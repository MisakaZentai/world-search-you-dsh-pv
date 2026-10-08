"""3D line art in the character grid: a camera, hidden-line removal, glyph strokes.

The TUI take on pdoom-video's engraved 3D (MIT; scenes/stack.ts, scenes/room.ts): wireframes
projected by hand, solids that only occlude (they fill a depth buffer first and the lines behind
them are dropped), far lines dimmed instead of fogged, camera moves eased onto beats. Everything
lands in a grid of character cells, one glyph and one colour per cell, as in a real terminal.

    cam = space.rig(t, [(t0, dict(target=(0, 1, 0), yaw=20, pitch=8, dist=12)),
                        (t1, dict(yaw=35), ease.ease_out)])        # or space.orbit(...)
    v = space.View(p, rect, cam)
    o = v.box(lo, hi)                          # solid: occludes, draws its visible edges
    v.glyphs(points, ["a3f", ...], owner=o, face="front")   # text printed on its face
    v.lines(a, b, lv=0.3)                      # braille strokes (the default), e.g. a floor grid
    v.label(anchor, "pid 1001")                # cell text at a projected 3D point
    v.sign(origin, right, up, h, text, *space.karaoke(L, t, p.lyrics))   # a lyric on a plane
    v.draw(ctx.img)

draw() in five passes:
  1. faces  -> depth buffer on a sub-cell grid (default cw/2 x ch/4 px, one sample per braille
               dot): inverse depth, owner, face id; a second raster at cell centres gives textured
               faces their (u, v)
  2. lines  -> near-clipped, projected, sampled every `step` px, depth-tested. A solid never hides
               its own front edges: an edge is kept if one of its faces faces the camera, and the
               buffer test skips samples whose nearest surface is the edge's own solid (the depth
               bias only has to cover lines of one object touching another)
  3. cells  -> per cell only the nearest ink layer survives (a far line gets a gap where a near
               one crosses it); 'dots' strokes set braille dots (2 x 4 per cell), 'box' strokes
               set the arms the line leaves the cell through and become ─ │ ┌ ┼ ╱ ╲ ...
  4. text   -> face textures and printed glyphs under the lines, labels and signs over them
  5. paint  -> solids clear to their fill colour (bg by default), glyphs blend in with their
               anti-aliased masks

Glyphs: Consolas (the project font) has the light box set, ╱ ╲ ╳ and ▀ ▄ █ ░ ▒ ▓, but no braille;
Consolas Bold has no diagonals. The atlas therefore uses the regular face for strokes and draws
braille cells itself (a 2 x 4 dot grid). Any character that would render as the font's .notdef box
(tofu) is refused, reported once, and drawn as a blank (see Atlas.has, tofu()).

Everything is a function of the View's inputs, so frame = f(t) holds; flicker in textures comes
from ease.tick(t, rate), never int(t * rate).
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
import sys
import time
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from . import ease
LINE_GLYPHS = '─│╱╲╳┌┐└┘├┤┬┴┼╴╵╶╷'
STYLES = {'box': 0, 'dots': 1, 'auto': 2, 'bold': 3}
DOT_BITS = ((1, 8), (2, 16), (4, 32), (64, 128))
MISSING = '\U000f0000'
BOX_FACES = ('left', 'right', 'bottom', 'top', 'back', 'front')
_BOX = ((0, 4, 6, 2), (5, 1, 3, 7), (0, 1, 5, 4), (6, 7, 3, 2), (1, 0, 2, 3), (4, 5, 7, 6))
FALLBACK_MONO = ['C:/Windows/Fonts/consola.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf']
FALLBACK_BOLD = ['C:/Windows/Fonts/consolab.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf']

class Atlas:
    """Masks (float32 0..1, ch x cw) of one font at one cell size. Index 0 is blank, 1..256 are the
    braille cells U+2800..U+28FF (drawn here: the project font has none), then the line glyphs, then
    any character asked for by get(), added on first use."""

    def __init__(self, font_path: str, cw: int, ch: int):
        self.path, self.cw, self.ch = (font_path, cw, ch)
        ref = ImageFont.truetype(font_path, 1000)
        self.size = cw * 1000 / ref.getlength('M')
        self.font = ImageFont.truetype(font_path, self.size)
        top, bot = self.font.getbbox('│')[1::2]
        self.dy = int(round((ch - (bot - top)) / 2)) - top
        self.chars: list[str] = []
        self.index: dict[str, int] = {}
        self._m: list[np.ndarray] = []
        self._stack = None
        self.tofu: set[str] = set()
        self.notdef = self._render(MISSING)
        self._put(' ', np.zeros((ch, cw), np.float32))
        for b in range(256):
            self._put(chr(10240 + b), self._braille(b))

    def _render(self, c: str) -> np.ndarray:
        im = Image.new('L', (self.cw, self.ch), 0)
        ImageDraw.Draw(im).text((0, self.dy), c, font=self.font, fill=255)
        return np.asarray(im, np.float32) / 255.0

    def _braille(self, bits: int) -> np.ndarray:
        s = 4
        im = Image.new('L', (self.cw * s, self.ch * s), 0)
        d = ImageDraw.Draw(im)
        r = max(1.0, 0.13 * self.cw) * s
        for row in range(4):
            for col in range(2):
                if bits & DOT_BITS[row][col]:
                    x, y = (self.cw * s * (0.25 + 0.5 * col), self.ch * s * (0.125 + 0.25 * row))
                    d.ellipse((x - r, y - r, x + r, y + r), fill=255)
        return np.asarray(im.resize((self.cw, self.ch), Image.BOX), np.float32) / 255.0

    def _put(self, c: str, m: np.ndarray) -> int:
        self.index[c] = len(self.chars)
        self.chars.append(c)
        self._m.append(m)
        self._stack = None
        return self.index[c]

    def has(self, c: str) -> bool:
        """False when the font has no glyph for c (it would draw the .notdef box: tofu)."""
        if c.isspace() or 10240 <= ord(c) <= 10495:
            return True
        m = self._render(c)
        return not np.array_equal(m, self.notdef) and bool(m.any())

    def get(self, c: str) -> int:
        k = self.index.get(c)
        if k is not None:
            return k
        if not self.has(c):
            if c not in self.tofu:
                self.tofu.add(c)
                print(f'tuikit.space: {Path(self.path).name} has no glyph for {c!r} (U+{ord(c):04X}); drawn blank', file=sys.stderr)
            self.index[c] = 0
            return 0
        return self._put(c, self._render(c))

    def codes(self, chars) -> np.ndarray:
        """Atlas indices for an array of 1-char strings (vectorised over the unique ones)."""
        chars = np.asarray(chars)
        if chars.size == 0:
            return np.zeros(chars.shape, np.int32)
        u, inv = np.unique(chars, return_inverse=True)
        return np.array([self.get(c) if c else 0 for c in u], np.int32)[inv].reshape(chars.shape)

    @property
    def masks(self) -> np.ndarray:
        if self._stack is None:
            self._stack = np.stack(self._m)
        return self._stack

@lru_cache(maxsize=8)
def atlas(font_path: str, cw: int=8, ch: int=16) -> Atlas:
    return Atlas(font_path, cw, ch)

def tofu(chars: str, font_path: str=FALLBACK_MONO[0], cw: int=8, ch: int=16) -> str:
    """The characters of `chars` the font cannot draw (checked by rendering, no font tools needed)."""
    a = atlas(font_path, cw, ch)
    return ''.join((c for c in dict.fromkeys(chars) if not a.has(c)))

def _first(paths) -> str:
    for c in paths:
        if c and Path(c).exists():
            return str(c)
    raise FileNotFoundError(f'no font among {paths}')

@dataclass(frozen=True)
class Camera:
    """Eye at pos looking at target, y up. fov is vertical, in degrees. roll in degrees (positive
    turns the picture counter-clockwise). shift moves the image centre by a fraction of the view height
    (a lens shift). upright keeps the view direction level and shifts the image instead, so
    vertical edges stay vertical (architectural framing): good for │ columns, use it for small
    pitches only."""
    pos: tuple
    target: tuple
    roll: float = 0.0
    fov: float = 45.0
    shift: tuple = (0.0, 0.0)
    near: float = 0.05
    upright: bool = False

    def basis(self):
        pos = np.asarray(self.pos, float)
        f = np.asarray(self.target, float) - pos
        if self.upright:
            f[1] = 0.0
        n = np.linalg.norm(f)
        f = f / n if n > 1e-09 else np.array([0.0, 0.0, -1.0])
        r = np.cross(f, (0.0, 1.0, 0.0))
        if np.linalg.norm(r) < 1e-09:
            r = np.array([1.0, 0.0, 0.0])
        r /= np.linalg.norm(r)
        u = np.cross(r, f)
        if self.roll:
            a = math.radians(self.roll)
            r, u = (r * math.cos(a) - u * math.sin(a), u * math.cos(a) + r * math.sin(a))
        return (pos, r, u, f)

def orbit(target=(0.0, 0.0, 0.0), yaw: float=0.0, pitch: float=0.0, dist: float=10.0, roll: float=0.0, fov: float=45.0, shift=(0.0, 0.0), upright: bool=False, near: float=0.05) -> Camera:
    """Camera on a sphere around target. yaw 0 puts the eye on +z looking toward -z; yaw turns it
    counter-clockwise seen from above; pitch > 0 is above the target looking down (degrees)."""
    y, q = (math.radians(yaw), math.radians(pitch))
    tx, ty, tz = target
    pos = (tx + dist * math.cos(q) * math.sin(y), ty + dist * math.sin(q), tz + dist * math.cos(q) * math.cos(y))
    return Camera(pos, tuple(target), roll, fov, tuple(shift), near, upright)

def rig_params(t: float, keys, fn=ease.ease_io) -> dict:
    """The orbit() arguments of rig() at t (for read-outs such as a header HUD)."""
    full, cur = ([], {})
    for k in keys:
        cur = {**cur, **k[1]}
        full.append((float(k[0]), cur, k[2] if len(k) > 2 else fn))
    if t < full[0][0]:
        return dict(full[0][1])
    for (t0, a, _), (t1, b, f) in zip(full, full[1:]):
        if t < t1:
            u = f(ease.prog(t, t0, t1))
            return {k: b[k] if isinstance(b[k], bool) else ease.lerp(a.get(k, b[k]), b[k], u) for k in b}
    return dict(full[-1][1])

def rig(t: float, keys, fn=ease.ease_io, **extra) -> Camera:
    """Keyframed orbit camera driven by song time. keys: [(t, params) or (t, params, ease_fn), ...]
    with params a dict of orbit() arguments; an entry left out carries over from the previous key.
    The segment ending at a key uses that key's ease (default `fn`). Two keys at the same time make
    a cut (snap). Put key times on clock.beat(k) / clock.bar(b) so moves land on the music. A snap inside
    a shot is not a cut to motion blur (Film._window only knows shot boundaries): put it on a shot
    boundary, or keep blur off there.
    `extra` is added on top (e.g. yaw=drift(t), roll=shake): offsets, not keys."""
    q = rig_params(t, keys, fn)
    for k, v in extra.items():
        base = q.get(k, 0.0)
        q[k] = tuple((a + b for a, b in zip(base, v))) if isinstance(base, (tuple, list)) else base + v
    return orbit(**q)

def karaoke(L, t: float, lyrics=None, ghost: float=0.4, ghost_lv: float=0.3):
    """Per-character (lit, ghost) arrays for line L at t, for View.sign / View.label.
    lit[i] in 0..1 is how much of character i is highlighted: 0 before its word's start, 1 by its
    end (Lyrics.word_progress, syllable-aware). ghost[i] is the level of the unlit part: the word
    fades in over the `ghost` seconds (<= 0.4, tools/DATA.md) before its onset, and the whole line
    fades over the last 0.5 s before it leaves the screen (lyrics.until, same as the band)."""
    from .timing import Lyrics
    n = len(L.text)
    lit, gh = (np.zeros(n, np.float32), np.zeros(n, np.float32))
    ghost = min(ghost, 0.4)
    pos = 0
    for w in L.words:
        k = L.text.find(w.text, pos)
        if k < 0:
            continue
        pos = k + len(w.text)
        m = len(w.text)
        pr = Lyrics.word_progress(w, t)
        lit[k:pos] = np.clip(pr * m - np.arange(m), 0.0, 1.0)
        g = ease.smooth(ease.prog(t, w.start - ghost, w.start)) if ghost > 0 else float(t >= w.start)
        gh[k:pos] = ghost_lv * g
    if lyrics is not None:
        until = lyrics.until(L)
        fade = 1.0 - ease.prog(t, until - 0.5, until)
        lit *= fade
        gh *= fade
        if t >= until:
            lit[:] = 0
            gh[:] = 0
    return (lit, gh)

@dataclass
class _Face:
    P: np.ndarray
    uv: np.ndarray | None
    n: np.ndarray
    owner: int
    name: int
    fill: tuple | None

class View:
    """One 3D viewport drawn as a grid of character cells inside `rect` (canvas pixels).
    Collect primitives, then draw(img). Colours are palette names or RGB; lv is brightness 0..1
    (mixed toward bg, like glyph.level: no new hues). fog = (z_near, z_far, lv_far): lines,
    text and textures dim (smoothstep) from full at z_near to lv_far at z_far (world units).
    zsub: depth-buffer samples per cell (default 2 x 4, one per braille dot: 4 x 4 px). Lines of
    one solid seen past another are decided within ~3 px of the occluder's silhouette; (8, 16)
    samples every pixel (within ~1 px) at a higher cost in the face pass.
    weight='bold' draws every default ('dots') stroke two dots thick: use it for the view that
    holds the object the eye should follow, and a plain view (drawn first) for the background."""

    def __init__(self, p, rect, cam: Camera, cell=(8, 16), fog=(6.0, 40.0, 0.18), bias: float=0.004, layer: float=0.08, step: float=0.7, font: str | None=None, zsub=(2, 4), weight: str='dots'):
        self.p, self.cam = (p, cam)
        x0, y0, x1, y1 = rect
        self.cw, self.ch = cell
        self.cols, self.rows = ((x1 - x0) // self.cw, (y1 - y0) // self.ch)
        self.W, self.H = (self.cols * self.cw, self.rows * self.ch)
        self.ox, self.oy = (x0 + (x1 - x0 - self.W) // 2, y0 + (y1 - y0 - self.H) // 2)
        self.zx, self.zy = zsub
        self.weight = weight
        self.sw, self.sh = (self.cw // self.zx, self.ch // self.zy)
        self.fog, self.bias, self.layer, self.step = (fog, bias, layer, step)
        mono = p.style.get('font_mono') if hasattr(p, 'style') else None
        self.atlas = atlas(font or _first([str(p.path(mono)) if mono else None] + FALLBACK_MONO), self.cw, self.ch)
        self.bg = np.array(p.color('bg'), np.float32)
        self.eye, self.r, self.u, self.f = cam.basis()
        self.near = cam.near
        self.fpx = self.H / 2 / math.tan(math.radians(cam.fov) / 2)
        self.cx = self.W / 2 + cam.shift[0] * self.H
        self.cy = self.H / 2 + cam.shift[1] * self.H
        if cam.upright:
            d = np.asarray(cam.target, float) - self.eye
            zt = float(d @ self.f)
            if zt > self.near:
                self.cy += self.fpx * float(d @ self.u) / zt
        self._colors: list[tuple] = []
        self._ci: dict[tuple, int] = {}
        self._faces: list[_Face] = []
        self._segs: list[tuple] = []
        self._labels: list[tuple] = []
        self._glyphs: list[tuple] = []
        self._signs: list[tuple] = []
        self._tex: dict[int, tuple] = {}
        self._front: dict[int, np.ndarray] = {}
        self._owners = 0
        self.stats: dict = {}

    def color(self, c) -> int:
        rgb = tuple((int(v) for v in (self.p.color(c) if isinstance(c, str) else c)))
        k = self._ci.get(rgb)
        if k is None:
            k = self._ci[rgb] = len(self._colors)
            self._colors.append(rgb)
        return k

    def cam_xyz(self, P) -> np.ndarray:
        d = np.asarray(P, float).reshape(-1, 3) - self.eye
        return np.stack([d @ self.r, d @ self.u, d @ self.f], axis=-1)

    def project(self, P):
        """(x, y, z): grid pixels (origin at the grid's top-left) and camera depth; z <= near is behind."""
        C = self.cam_xyz(P)
        z = C[:, 2]
        zs = np.where(z > self.near, z, np.nan)
        return (self.cx + self.fpx * C[:, 0] / zs, self.cy - self.fpx * C[:, 1] / zs, z)

    def to_canvas(self, P):
        """Canvas pixel position of one world point, or None when it is behind the camera."""
        x, y, z = self.project(P)
        if not z[0] > self.near:
            return None
        return (float(x[0] + self.ox), float(y[0] + self.oy))

    def fog_lv(self, z) -> np.ndarray:
        z0, z1, lo = self.fog
        u = np.clip((np.asarray(z, float) - z0) / max(1e-06, z1 - z0), 0.0, 1.0)
        return 1.0 - (1.0 - lo) * u * u * (3 - 2 * u)

    def solid(self, verts, faces, color='ink', lv: float=1.0, edges: bool=True, style: str='dots', fill=None, tex=None, tex_color=None) -> int:
        """Convex solid: faces are vertex-index loops, counter-clockwise seen from outside.
        Front faces fill the depth buffer; an edge is drawn when one of its two faces faces the
        camera. fill: RGB/name its cells are cleared to (default bg). tex(face, U, V, ppu) ->
        (chars, lv) fills its faces cell by cell (U, V world units on the face at each cell centre,
        ppu = screen pixels per world unit there, foreshortening included, for fading detail that
        gets too small). A cell texture is for patterns (shades, hatching, a dim wash): a character
        bigger than a cell repeats in every cell it covers, so print text with glyphs() instead.
        Returns the owner id."""
        faces = tuple((tuple((int(i) for i in f)) for f in faces))
        V = np.asarray(verts, float)
        owner = self._owners
        self._owners += 1
        fillc = None if fill is None else tuple(self.p.color(fill) if isinstance(fill, str) else fill)
        n, c = _normals(V, faces)
        front = (np.abs(n).sum(axis=1) > 0) & (((self.eye - c) * n).sum(axis=1) > 0)
        self._front[owner] = front
        for k in np.nonzero(front)[0]:
            P = V[list(faces[k])]
            uv = None
            if tex is not None:
                eu = P[1] - P[0]
                eu = eu / np.linalg.norm(eu)
                nk = n[k]
                ev = np.array([nk[1] * eu[2] - nk[2] * eu[1], nk[2] * eu[0] - nk[0] * eu[2], nk[0] * eu[1] - nk[1] * eu[0]])
                uv = np.stack([(P - P[0]) @ eu, (P - P[0]) @ ev], axis=-1)
            self._faces.append(_Face(P, uv, n[k], owner, int(k), fillc))
        if tex is not None:
            self._tex[owner] = (tex, self.color(tex_color or color))
        if edges:
            E, EF = _topology(faces)
            keep = front[EF[:, 0]] | front[EF[:, 1]]
            if keep.any():
                self.lines(V[E[keep, 0]], V[E[keep, 1]], color, lv, style, owner)
        return owner

    def box(self, lo, hi, **kw) -> int:
        """Axis-aligned box from corner lo to corner hi; faces named by BOX_FACES for textures."""
        (x0, y0, z0), (x1, y1, z1) = (lo, hi)
        V = [(x, y, z) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
        return self.solid(V, _BOX, **kw)

    def lines(self, a, b, color='ink', lv=1.0, style: str='dots', owner: int=-1):
        """Segments a[i] -> b[i] (N x 3). lv may be per segment. style: 'dots' (braille, 2 x 4 dots
        per cell: any slope, the default), 'bold' (braille two dots thick: each dot also sets its
        partner across the stroke inside the same cell, for the object the eye should follow),
        'box' (─ │ ┌ ┼ ╱ ╲ strokes snapped to cell centres) or 'auto' (box when the stroke stays
        within ~half a cell of a row or column on screen, else dots: crisp columns and rows,
        smooth slants)."""
        A = np.asarray(a, float).reshape(-1, 3)
        B = np.asarray(b, float).reshape(-1, 3)
        n = len(A)
        if n == 0:
            return
        L = np.broadcast_to(np.asarray(lv, float), (n,)).astype(np.float32)
        if style == 'dots' and self.weight == 'bold':
            style = 'bold'
        ci = np.array([self.color(c) for c in color], np.int32) if isinstance(color, list) else np.full(n, self.color(color), np.int32)
        self._segs.append((A, B, L, ci, np.full(n, STYLES[style], np.int8), np.full(n, owner, np.int32)))

    def decal(self, owner: int, face, a, b, **kw):
        """Lines drawn on a face of a solid (panel seams, LED strips): kept only while that face
        looks at the camera, and never hidden by their own solid. face: index or BOX_FACES name."""
        k = BOX_FACES.index(face) if isinstance(face, str) else int(face)
        if self._front.get(owner) is not None and self._front[owner][k]:
            self.lines(a, b, owner=owner, **kw)

    def facing(self, owner: int, face) -> bool:
        """Whether that face of the solid looks at the camera (for decals, labels, textures)."""
        k = BOX_FACES.index(face) if isinstance(face, str) else int(face)
        return bool(self._front.get(owner, np.zeros(k + 1, bool))[k])

    def polyline(self, pts, closed: bool=False, **kw):
        P = np.asarray(pts, float)
        Q = np.roll(P, -1, axis=0)
        if not closed:
            P, Q = (P[:-1], Q[:-1])
        self.lines(P, Q, **kw)

    def glyphs(self, points, texts, lv=1.0, color='ink', owner: int=-1, face=None, pitch=None):
        """Short strings (one per point) printed at 3D points (text on a surface: rack ids, LEDs, tick marks). Each
        string starts in the cell its point projects to and runs right in consecutive cells, upright
        (a terminal cannot rotate or scale a glyph); where several land in one cell the brightest
        wins. Drawn under lines, over face textures. owner/face: the points lie on that face of that
        solid, so they show only while it faces the camera and the solid never hides them. pitch:
        the 3D step to the next string; strings fade out as that step shrinks below about one cell
        on screen (a string's own length is not counted), instead of piling into noise far away."""
        P = np.asarray(points, float).reshape(-1, 3)
        if len(P) == 0 or (face is not None and (not self.facing(owner, face))):
            return
        if isinstance(texts, str):
            texts = list(texts) if len(texts) == len(P) and len(P) > 1 else [texts] * len(P)
        texts = list(texts)
        L = np.broadcast_to(np.asarray(lv, float), (len(P),)).astype(np.float32)
        if pitch is not None:
            x0, y0, _ = self.project(P)
            x1, y1, _ = self.project(P + np.asarray(pitch, float))
            d = np.hypot(x1 - x0, y1 - y0)
            L = L * np.where(np.isfinite(d), np.clip((d - 0.6 * self.cw) / (0.6 * self.cw), 0.0, 1.0), 0.0)
        ci = np.array([self.color(c) for c in color], np.int32) if isinstance(color, list) else np.full(len(P), self.color(color), np.int32)
        n = np.array([len(x) for x in texts])
        idx = np.repeat(np.arange(len(P)), n)
        off = np.arange(n.sum()) - np.repeat(np.cumsum(n) - n, n)
        ch = np.array([c for x in texts for c in x]) if n.sum() else np.zeros(0, '<U1')
        self._glyphs.append((P[idx], ch, L[idx], ci[idx], owner, off))

    def label(self, anchor, text: str, color='ink', lv: float=1.0, align: str='left', dx: int=0, dy: int=0, lit=None, lit_color=None, occlude: bool=True, fog: bool=True):
        """Text in cells at the projected anchor (cell glyphs never scale: a terminal cannot).
        align: left | center | right of the anchor cell; dx, dy offset in cells. Hidden when the
        anchor is behind a solid (occlude). lit (per character 0..1, e.g. from karaoke) switches
        characters with lit >= 0.5 to lit_color at full level; the rest draw at lv. Labels never
        overlap: the nearest is placed first and one that would touch it is dropped whole."""
        self._labels.append((np.asarray(anchor, float), text, self.color(color), lv, align, dx, dy, None if lit is None else np.asarray(lit, float), self.color(lit_color or color), occlude, fog))

    def sign(self, origin, right, up, height: float, text: str, lit=None, ghost=None, color='ink', lit_color=None, lv: float=1.0, font: str | None=None, backing: float | None=None, frame: float=0.0, frame_color=None, align: str='left'):
        """Text painted on a plane in the world: the quad from origin (bottom-left) along right and
        up (unit vectors), `height` world units tall, as wide as the text. Rasterised into the cells
        as braille dots (2 x 4 per cell) from a mip chain of hinted text, so strokes survive at any
        distance. (Half blocks ▀ ▄ █ were tried: 8 px pixels garble letters even ~60 px tall.)
        Per character: lit (0..1, the highlighted fraction, wiped left to right) at lit_color and
        full lv; the rest at ghost level (default: lv) in color. lit_color may be a list, one
        colour per character (keyword chips). Use karaoke(L, t) for lyrics.
        align: 'left' (origin is the bottom-left corner) or 'center' (origin is the bottom centre).
        Hidden behind solids; drawn over lines. backing (a margin in world units) puts an opaque
        panel behind the text so lines behind it drop out (a pane in the world); frame > 0 draws the
        panel's outline at that level."""
        n = len(text)
        lit = np.zeros(n) if lit is None else np.asarray(lit, float)
        ghost = np.full(n, 1.0) if ghost is None else np.asarray(ghost, float)
        fp = font or _first([str(self.p.path(self.p.style['font_bold'])) if self.p.style.get('font_bold') else None] + FALLBACK_BOLD + FALLBACK_MONO)
        O, R, U = (np.asarray(origin, float), _unit(right), _unit(up))
        if align == 'center':
            O = O - R * height * _text_aspect(text, fp) / 2
        owner = -1
        if backing is not None:
            m = float(backing)
            w = height * _text_aspect(text, fp)
            q = [O - m * R - m * U, O + (w + m) * R - m * U, O + (w + m) * R + (height + m) * U, O + (height + m) * U - m * R]
            owner = self.solid(q, [(0, 1, 2, 3), (3, 2, 1, 0)], color=frame_color or color, lv=frame, edges=frame > 0)
        lci = np.array([self.color(c) for c in lit_color], np.int32) if isinstance(lit_color, list) else np.full(n, self.color(lit_color or color), np.int32)
        self._signs.append((O, R, U, float(height), text, lit, ghost, self.color(color), lci, lv, fp, owner))

    def draw(self, img: Image.Image):
        t0 = time.perf_counter()
        nc = self.rows * self.cols
        self._chars = np.zeros(nc, np.int32)
        self._col = np.zeros(nc, np.int32)
        self._lv = np.zeros(nc, np.float32)
        self._raster_faces()
        t1 = time.perf_counter()
        self._draw_textures()
        self._draw_glyphs()
        self._draw_lines()
        t2 = time.perf_counter()
        self._draw_labels()
        self._draw_signs()
        t3 = time.perf_counter()
        self._paint(img)
        t4 = time.perf_counter()
        self.stats.update(faces_ms=(t1 - t0) * 1000.0, lines_ms=(t2 - t1) * 1000.0, text_ms=(t3 - t2) * 1000.0, paint_ms=(t4 - t3) * 1000.0, faces=len(self._faces), segments=sum((len(s[0]) for s in self._segs)), glyph_cells=int((self._chars > 0).sum()), tofu=''.join(sorted(self.atlas.tofu)))
        return img

    def _clip_near(self, C: np.ndarray, attrs: np.ndarray):
        """Sutherland-Hodgman against z >= near, carrying per-vertex attributes."""
        near = self.near + 1e-06
        inside = C[:, 2] >= near
        if inside.all():
            return (C, attrs)
        if not inside.any():
            return (None, None)
        outC, outA = ([], [])
        k = len(C)
        for i in range(k):
            j = (i + 1) % k
            a_in, b_in = (inside[i], inside[j])
            if a_in:
                outC.append(C[i])
                outA.append(attrs[i])
            if a_in != b_in:
                s = (near - C[i, 2]) / (C[j, 2] - C[i, 2])
                outC.append(C[i] + s * (C[j] - C[i]))
                outA.append(attrs[i] + s * (attrs[j] - attrs[i]))
        if len(outC) < 3:
            return (None, None)
        return (np.array(outC), np.array(outA))

    def _raster_faces(self):
        gw, gh = (self.cols * self.zx, self.rows * self.zy)
        self._zb = np.zeros((gh, gw), np.float32)
        self._zown = np.full((gh, gw), -1, np.int32)
        self._zfid = np.full((gh, gw), -1, np.int32)
        cells = bool(self._tex)
        self._cz = np.zeros((self.rows, self.cols), np.float32)
        self._cfid = np.full((self.rows, self.cols), -1, np.int32)
        self._cu = np.zeros((self.rows, self.cols), np.float32)
        self._cv = np.zeros((self.rows, self.cols), np.float32)
        if not self._faces:
            return
        allC = self.cam_xyz(np.concatenate([F.P for F in self._faces]))
        k0 = 0
        for fid, F in enumerate(self._faces):
            C = allC[k0:k0 + len(F.P)]
            k0 += len(F.P)
            uv = F.uv if F.uv is not None else np.zeros((len(F.P), 2))
            if (C[:, 2] < self.near).any():
                C, uv = self._clip_near(C, uv)
                if C is None:
                    continue
            w = 1.0 / C[:, 2]
            xs = (self.cx + self.fpx * C[:, 0] * w).tolist()
            ys = (self.cy - self.fpx * C[:, 1] * w).tolist()
            coef = _plane(xs, ys, np.stack([w, uv[:, 0] * w, uv[:, 1] * w], axis=-1))
            if coef is None:
                continue
            self._poly(xs, ys, coef, self.sw, self.sh, self._zb, fid, F.owner, False)
            if cells:
                self._poly(xs, ys, coef, self.cw, self.ch, self._cz, fid, F.owner, F.uv is not None)

    def _poly(self, xs, ys, coef, sx, sy, zb, fid, owner, uv):
        """Fill a convex screen polygon on a grid of sample centres ((i + .5) sx, (j + .5) sy),
        keeping the nearest inverse depth (w, u*w, v*w are affine in screen space: coef)."""
        ny, nx = zb.shape
        i0, i1 = (max(0, int(min(xs) / sx - 0.5)), min(nx, int(max(xs) / sx + 1.5)))
        j0, j1 = (max(0, int(min(ys) / sy - 0.5)), min(ny, int(max(ys) / sy + 1.5)))
        if i1 <= i0 or j1 <= j0:
            return
        X = ((np.arange(i0, i1) + 0.5) * sx)[None, :]
        Y = ((np.arange(j0, j1) + 0.5) * sy)[:, None]
        k = len(xs)
        area = sum((xs[i] * ys[(i + 1) % k] - xs[(i + 1) % k] * ys[i] for i in range(k)))
        if abs(area) < 1e-06:
            return
        sgn = 1.0 if area > 0 else -1.0
        inside = None
        for i in range(k):
            ex, ey = ((xs[(i + 1) % k] - xs[i]) * sgn, (ys[(i + 1) % k] - ys[i]) * sgn)
            e = ex * (Y - ys[i]) - ey * (X - xs[i]) >= 0
            inside = e if inside is None else inside & e
        w = coef[0, 0] * X + coef[1, 0] * Y + coef[2, 0]
        reg = zb[j0:j1, i0:i1]
        win = inside & (w > reg) & (w > 0)
        if not win.any():
            return
        reg[win] = w[win]
        if zb is self._zb:
            self._zown[j0:j1, i0:i1][win] = owner
            self._zfid[j0:j1, i0:i1][win] = fid
        else:
            self._cfid[j0:j1, i0:i1][win] = fid if uv else -1
            if uv:
                ww = np.where(win, w, 1.0)
                self._cu[j0:j1, i0:i1][win] = ((coef[0, 1] * X + coef[1, 1] * Y + coef[2, 1]) / ww)[win]
                self._cv[j0:j1, i0:i1][win] = ((coef[0, 2] * X + coef[1, 2] * Y + coef[2, 2]) / ww)[win]

    def _visible(self, x, y, w, owner=None):
        """Depth test of points (grid px, inverse depth) against the solids; a point whose nearest
        surface belongs to its own solid (owner) passes."""
        gx = np.clip((x // self.sw).astype(np.int32), 0, self.cols * self.zx - 1)
        gy = np.clip((y // self.sh).astype(np.int32), 0, self.rows * self.zy - 1)
        zb = self._zb[gy, gx]
        vis = w * (1.0 + self.bias) >= zb
        if owner is not None:
            vis |= (self._zown[gy, gx] == owner) & (owner >= 0)
        return vis

    def _draw_textures(self):
        if not self._tex:
            return
        fid = self._cfid.ravel()
        has = fid >= 0
        if not has.any():
            return
        owners = np.array([F.owner for F in self._faces], np.int32)
        names = np.array([F.name for F in self._faces], np.int32)
        normals = np.array([F.n for F in self._faces])
        cells = np.nonzero(has)[0]
        own = owners[fid[cells]]
        z = 1.0 / np.maximum(self._cz.ravel()[cells], 1e-09)
        cy, cx = np.divmod(cells, self.cols)
        ray = ((cx + 0.5) * self.cw - self.cx)[:, None] / self.fpx * self.r - ((cy + 0.5) * self.ch - self.cy)[:, None] / self.fpx * self.u + self.f
        ray /= np.linalg.norm(ray, axis=1, keepdims=True)
        cos = np.abs((normals[fid[cells]] * ray).sum(axis=1))
        ppu = self.fpx / z * cos
        fogl = self.fog_lv(z)
        for o, (fn, ci) in self._tex.items():
            sel = own == o
            if not sel.any():
                continue
            c = cells[sel]
            chars, lv = fn(names[fid[c]], self._cu.ravel()[c], self._cv.ravel()[c], ppu[sel])
            lv = np.broadcast_to(np.asarray(lv, np.float32), c.shape) * fogl[sel]
            codes = self.atlas.codes(chars)
            on = (codes > 0) & (lv > 0.004)
            self._chars[c[on]] = codes[on]
            self._col[c[on]] = ci
            self._lv[c[on]] = lv[on]

    def _draw_glyphs(self):
        if not self._glyphs:
            return
        P = np.concatenate([g[0] for g in self._glyphs])
        ch = np.concatenate([g[1] for g in self._glyphs])
        L = np.concatenate([g[2] for g in self._glyphs])
        CI = np.concatenate([g[3] for g in self._glyphs])
        OW = np.concatenate([np.full(len(g[0]), g[4], np.int32) for g in self._glyphs])
        OFF = np.concatenate([g[5] for g in self._glyphs])
        x, y, z = self.project(P)
        ok = (z > self.near) & np.isfinite(x) & (x >= 0) & (x < self.W) & (y >= 0) & (y < self.H) & (L > 0.004)
        if not ok.any():
            return
        x, y, z, ch, L, CI, OW, OFF = (x[ok], y[ok], z[ok], ch[ok], L[ok] * self.fog_lv(z[ok]), CI[ok], OW[ok], OFF[ok])
        vis = self._visible(x, y, 1.0 / z, OW)
        x, y, ch, L, CI, OFF = (x[vis], y[vis], ch[vis], L[vis], CI[vis], OFF[vis])
        col = (x // self.cw).astype(np.int64) + OFF
        inside = col < self.cols
        x, y, ch, L, CI, col = (x[inside], y[inside], ch[inside], L[inside], CI[inside], col[inside])
        cell = (y // self.ch).astype(np.int64) * self.cols + col
        order = np.lexsort((L, cell))
        cell, ch, L, CI = (cell[order], ch[order], L[order], CI[order])
        last = np.ones(len(cell), bool)
        last[:-1] = cell[1:] != cell[:-1]
        codes = self.atlas.codes(ch[last])
        c = cell[last]
        on = codes > 0
        self._chars[c[on]] = codes[on]
        self._lv[c[on]] = L[last][on]
        self._col[c[on]] = CI[last][on]

    def _draw_lines(self):
        if not self._segs:
            return
        A, B, L, CI, ST, OW = (np.concatenate(k) for k in zip(*self._segs))
        CA, CB = (self.cam_xyz(A), self.cam_xyz(B))
        za, zb = (CA[:, 2], CB[:, 2])
        near = self.near + 1e-06
        keep = (za >= near) | (zb >= near)
        ta = np.where(za < near, (near - za) / np.where(zb - za == 0, 1, zb - za), 0.0)
        tb = np.where(zb < near, (near - zb) / np.where(za - zb == 0, 1, za - zb), 0.0)
        CA2 = CA + ta[:, None] * (CB - CA)
        CB2 = CB + tb[:, None] * (CA - CB)
        k = np.nonzero(keep)[0]
        if len(k) == 0:
            return
        CA2, CB2 = (CA2[k], CB2[k])
        L, CI, ST, OW = (L[k], CI[k], ST[k], OW[k])
        wa, wb = (1.0 / CA2[:, 2], 1.0 / CB2[:, 2])
        xa, ya = (self.cx + self.fpx * CA2[:, 0] * wa, self.cy - self.fpx * CA2[:, 1] * wa)
        xb, yb = (self.cx + self.fpx * CB2[:, 0] * wb, self.cy - self.fpx * CB2[:, 1] * wb)
        m = 4.0
        dx, dy = (xb - xa, yb - ya)
        u0, u1 = (np.zeros(len(xa)), np.ones(len(xa)))
        for pq, qq in ((-dx, xa + m), (dx, self.W + m - xa), (-dy, ya + m), (dy, self.H + m - ya)):
            with np.errstate(divide='ignore', invalid='ignore'):
                r = qq / pq
            neg, pos, par = (pq < 0, pq > 0, pq == 0)
            u0 = np.where(neg, np.maximum(u0, r), u0)
            u1 = np.where(pos, np.minimum(u1, r), u1)
            u0 = np.where(par & (qq < 0), 2.0, u0)
        ok = u0 < u1
        if not ok.any():
            return
        sel = np.nonzero(ok)[0]
        u0, u1 = (u0[sel], u1[sel])
        xa, ya, xb, yb, wa, wb = (xa[sel], ya[sel], xb[sel], yb[sel], wa[sel], wb[sel])
        L, CI, ST, OW = (L[sel], CI[sel], ST[sel], OW[sel])
        X0, Y0, W0 = (xa + u0 * (xb - xa), ya + u0 * (yb - ya), wa + u0 * (wb - wa))
        X1, Y1, W1 = (xa + u1 * (xb - xa), ya + u1 * (yb - ya), wa + u1 * (wb - wa))
        length = np.hypot(X1 - X0, Y1 - Y0)
        ratio = np.abs(Y1 - Y0) / self.ch / np.maximum(np.abs(X1 - X0) / self.cw, 1e-09)
        diag = (ratio > 0.7) & (ratio < 1.45)
        auto = ST == 2
        if auto.any():
            snap = (np.abs(X1 - X0) < 0.6 * self.cw) | (np.abs(Y1 - Y0) < 0.6 * self.ch)
            ST = np.where(auto, np.where(snap, 0, 1), ST)
        cnt = np.maximum(2, np.ceil(length / self.step).astype(np.int64) + 1)
        total = int(cnt.sum())
        if total > 3000000:
            cnt = np.maximum(2, cnt * 3000000 // total)
            total = int(cnt.sum())
        idx = np.repeat(np.arange(len(cnt)), cnt)
        start = np.repeat(np.cumsum(cnt) - cnt, cnt)
        s = (np.arange(total) - start) / np.repeat(cnt - 1, cnt)
        x = X0[idx] + s * (X1 - X0)[idx]
        y = Y0[idx] + s * (Y1 - Y0)[idx]
        w = W0[idx] + s * (W1 - W0)[idx]
        sid = np.arange(total)
        inb = (x >= 0) & (x < self.W) & (y >= 0) & (y < self.H)
        x, y, w, idx, sid = (x[inb], y[inb], w[inb], idx[inb], sid[inb])
        vis = self._visible(x, y, w, OW[idx])
        x, y, w, idx, sid = (x[vis], y[vis], w[vis], idx[vis], sid[vis])
        self.stats['samples'] = int(len(x))
        if len(x) == 0:
            return
        cell = (y // self.ch).astype(np.int64) * self.cols + (x // self.cw).astype(np.int64)
        near_w = np.zeros(self.rows * self.cols, np.float32)
        np.maximum.at(near_w, cell, w.astype(np.float32))
        top = w >= near_w[cell] * (1.0 - self.layer)
        x, y, w, idx, cell, sid = (x[top], y[top], w[top], idx[top], cell[top], sid[top])
        lv = L[idx] * self.fog_lv(1.0 / w)
        key = np.zeros(self.rows * self.cols, np.int64)
        np.maximum.at(key, cell, (np.round(lv * 4000).astype(np.int64) << 8) + CI[idx])
        hit = key > 0
        cl_lv = (key >> 8).astype(np.float32) / 4000.0
        cl_ci = (key & 255).astype(np.int32)
        chars = np.zeros(self.rows * self.cols, np.int32)
        g = ST[idx] == 0
        if g.any():
            arms = self._arms(x[g], y[g], idx[g], sid[g], diag[idx[g]])
            on = arms > 0
            chars[on] = _arm_table(self.atlas)[arms[on]]
        d = ~g
        if d.any():
            bx = (x[d] // (self.cw / 2)).astype(np.int64) % 2
            by = (y[d] // (self.ch / 4)).astype(np.int64) % 4
            bits = np.array(DOT_BITS, np.int64)[by, bx]
            dcell = cell[d]
            bold = ST[idx[d]] == 3
            if bold.any():
                steep = (np.abs(Y1 - Y0) > np.abs(X1 - X0))[idx[d]][bold]
                pbx = np.where(steep, bx[bold] ^ 1, bx[bold])
                pby = np.where(steep, by[bold], by[bold] ^ 1)
                bits = np.concatenate([bits, np.array(DOT_BITS, np.int64)[pby, pbx]])
                dcell = np.concatenate([dcell, dcell[bold]])
            pair = np.unique(dcell * 256 + bits)
            acc = np.zeros(self.rows * self.cols, np.int64)
            np.add.at(acc, pair // 256, pair % 256)
            dots = (acc > 0) & (chars == 0)
            chars[dots] = 1 + acc[dots]
        on = hit & (chars > 0)
        self._chars[on] = chars[on]
        self._col[on] = cl_ci[on]
        self._lv[on] = cl_lv[on]

    def _arms(self, x, y, seg, sid, diag):
        """Per cell, the sides a box stroke leaves through (N E S W = 1 2 4 8; NE SE SW NW = 16 32
        64 128), from consecutive visible samples of one segment that change cell. Orthogonal
        strokes walk 4-connected (a corner crossing is split through the neighbour on the major
        axis), so ─ ┐ └ ─ staircases always join. Strokes near the cell diagonal take one cell per
        step of their major axis and become ╱ / ╲ runs."""
        n = self.rows * self.cols
        arms = np.zeros(n, np.int64)
        col, row = ((x // self.cw).astype(np.int64), (y // self.ch).astype(np.int64))
        nxt = (sid[1:] - sid[:-1] == 1) & (seg[1:] == seg[:-1])
        dc, dr = (col[1:] - col[:-1], row[1:] - row[:-1])
        ortho = ~diag[:-1]
        mv = nxt & ((dc != 0) | (dr != 0))
        a = mv & ortho
        ARM = {(1, 0): (2, 8), (-1, 0): (8, 2), (0, 1): (4, 1), (0, -1): (1, 4)}
        c0, r0 = (col[:-1][a], row[:-1][a])
        c1, r1 = (col[1:][a], row[1:][a])
        ddc, ddr = (dc[a], dr[a])
        horiz = np.abs(x[1:][a] - x[:-1][a]) / self.cw >= np.abs(y[1:][a] - y[:-1][a]) / self.ch
        both = (ddc != 0) & (ddr != 0)
        mc = np.where(both & horiz, c0 + ddc, c0)
        mr = np.where(both & ~horiz, r0 + ddr, r0)
        tc, tr = (np.where(both, mc, c1), np.where(both, mr, r1))
        hops = [(c0, r0, tc, tr), (mc[both], mr[both], c1[both], r1[both])]
        for fc, fr, tc, tr in hops:
            ec, er = (tc - fc, tr - fr)
            fcell, tcell = (fr * self.cols + fc, tr * self.cols + tc)
            for (kc, kr), (out, into) in ARM.items():
                m = (ec == kc) & (er == kr)
                if m.any():
                    np.bitwise_or.at(arms, fcell[m], out)
                    np.bitwise_or.at(arms, tcell[m], into)
        dg = diag
        if dg.any():
            xs, ys = (x / self.cw, y / self.ch)
            major_x = np.abs(np.diff(xs, append=xs[-1:])) >= np.abs(np.diff(ys, append=ys[-1:]))
            key = np.where(major_x, np.floor(xs - 0.5), np.floor(ys - 0.5))
            step = np.zeros(len(x), bool)
            step[1:] = nxt & (key[1:] != key[:-1])
            step[0] = True
            step &= dg
            slope = np.zeros(len(x))
            slope[:-1] = (ys[1:] - ys[:-1]) * (xs[1:] - xs[:-1])
            slope[-1] = slope[-2] if len(x) > 1 else 0.0
            cells = row[step] * self.cols + col[step]
            np.bitwise_or.at(arms, cells, np.where(slope[step] > 0, 32 | 128, 16 | 64))
        return arms

    def _draw_labels(self):
        """Nearest label first; a label that would touch cells of one already placed (one cell of
        padding) is dropped whole, so words never run into each other ("ifhello")."""
        placed = np.zeros((self.rows, self.cols), bool)
        todo = []
        for item in self._labels:
            P, text = (item[0], item[1])
            x, y, z = self.project(P[None])
            if z[0] > self.near and np.isfinite(x[0]):
                todo.append((float(z[0]), float(x[0]), float(y[0]), item))
        todo.sort(key=lambda e: e[0])
        for z, x, y, (P, text, ci, lv, align, dx, dy, lit, lci, occlude, fog) in todo:
            if occlude and (not self._visible(np.clip([x], 0, self.W - 1), np.clip([y], 0, self.H - 1), np.array([1.0 / z]))[0]):
                continue
            n = len(text)
            c0 = int(x // self.cw) + dx - {'left': 0, 'center': n // 2, 'right': n - 1}[align]
            r = int(y // self.ch) + dy
            if not 0 <= r < self.rows:
                continue
            a, b = (max(0, c0), min(self.cols, c0 + n))
            if b <= a or placed[max(0, r - 1):r + 2, max(0, a - 1):b + 1].any():
                continue
            placed[r, a:b] = True
            f = float(self.fog_lv(z)) if fog else 1.0
            for i, chx in enumerate(text):
                c = c0 + i
                if not 0 <= c < self.cols or chx == ' ':
                    continue
                k = r * self.cols + c
                on = lit is not None and lit[i] >= 0.5
                self._chars[k] = self.atlas.get(chx)
                self._col[k] = lci if on else ci
                self._lv[k] = (1.0 if on else lv) * f

    def _draw_signs(self):
        for O, R, U, h, text, lit, ghost, ci, lci, lv, fp, owner in self._signs:
            w = h * _text_aspect(text, fp)
            quad = np.array([O, O + w * R, O + w * R + h * U, O + h * U])
            x, y, z = self.project(quad)
            if not (z > self.near).any():
                continue
            if (z > self.near).all():
                xs, ys = (x, y)
            else:
                C, _ = self._clip_near(self.cam_xyz(quad), np.zeros((4, 1)))
                xs = self.cx + self.fpx * C[:, 0] / C[:, 2]
                ys = self.cy - self.fpx * C[:, 1] / C[:, 2]
            sx, sy = (self.cw / 2, self.ch / 4)
            nx, ny = (int(round(self.W / sx)), int(round(self.H / sy)))
            i0, i1 = (max(0, int(xs.min() // sx)), min(nx, int(xs.max() // sx) + 1))
            j0, j1 = (max(0, int(ys.min() // sy)), min(ny, int(ys.max() // sy) + 1))
            if i1 <= i0 or j1 <= j0:
                continue
            I, J = np.meshgrid(np.arange(i0, i1), np.arange(j0, j1))
            px, py = ((I + 0.5) * sx, (J + 0.5) * sy)
            ray = ((px - self.cx) / self.fpx)[..., None] * self.r - ((py - self.cy) / self.fpx)[..., None] * self.u + self.f
            nrm = np.cross(R, U)
            den = ray @ nrm
            with np.errstate(divide='ignore', invalid='ignore'):
                tt = (O - self.eye) @ nrm / den
            P = self.eye + tt[..., None] * ray
            a, b = ((P - O) @ R, (P - O) @ U)
            inq = (tt > self.near) & (a >= 0) & (a < w) & (b >= 0) & (b < h)
            if not inq.any():
                continue
            I, J, a, b, tt, px, py = (I[inq], J[inq], a[inq], b[inq], tt[inq], px[inq], py[inq])
            u, vv = (a / w, 1.0 - b / h)
            want = self.fpx * h / tt / sy
            lvl = np.clip(np.searchsorted(MIP, want), 0, len(MIP) - 1)
            cov = np.zeros(len(u), np.float32)
            for m in np.unique(lvl):
                sel = lvl == m
                T = _text_texture(text, fp, int(MIP[m]))
                th, tw = T.shape
                cov[sel] = _bilinear(T, np.clip(u[sel] * tw, 0, tw - 1.001), np.clip(vv[sel] * th, 0, th - 1.001))
            on = cov > 0.42
            on &= self._visible(px, py, 1.0 / tt, owner)
            if not on.any():
                continue
            I, J, u, tt = (I[on], J[on], u[on], tt[on])
            k = np.minimum((u * len(text)).astype(np.int64), len(text) - 1)
            frac = u * len(text) - k
            is_lit = frac < lit[k]
            level = np.where(is_lit, 1.0, ghost[k]) * lv * self.fog_lv(tt)
            color = np.where(is_lit, lci[k], ci)
            cell = J // 4 * self.cols + I // 2
            bits = np.array(DOT_BITS, np.int64)[J % 4, I % 2]
            keep = level > 0.004
            cell, bits, level, color = (cell[keep], bits[keep], level[keep], color[keep])
            if len(cell) == 0:
                continue
            pair = np.unique(cell * 256 + bits)
            acc = np.zeros(self.rows * self.cols, np.int64)
            np.add.at(acc, pair // 256, pair % 256)
            key = np.zeros(self.rows * self.cols, np.int64)
            np.maximum.at(key, cell, (np.round(level * 4000).astype(np.int64) << 8) + color)
            cells = np.nonzero(acc)[0]
            self._chars[cells] = 1 + acc[cells]
            self._lv[cells] = (key[cells] >> 8) / 4000.0
            self._col[cells] = key[cells] & 255

    def _paint(self, img: Image.Image):
        box = (self.ox, self.oy, self.ox + self.W, self.oy + self.H)
        reg = np.array(img.crop(box))
        cov = self._zfid >= 0
        if cov.any():
            fills = np.array([F.fill if F.fill is not None else tuple(self.bg) for F in self._faces], np.uint8)
            jj, ii = np.nonzero(cov)
            sub = reg.reshape(self.rows * self.zy, self.sh, self.cols * self.zx, self.sw, 3)
            sub[jj, :, ii, :] = fills[self._zfid[jj, ii]][:, None, None, :]
        on = np.nonzero((self._chars > 0) & (self._lv > 0.002))[0]
        if len(on):
            r, c = np.divmod(on, self.cols)
            blk = reg.reshape(self.rows, self.ch, self.cols, self.cw, 3)
            px = blk[r, :, c, :].astype(np.float32)
            pal = np.array(self._colors, np.float32)
            lv = np.clip(self._lv[on], 0, 1)[:, None]
            fg = self.bg + (pal[self._col[on]] - self.bg) * lv
            A = self.atlas.masks[self._chars[on]][..., None]
            px += (fg[:, None, None, :] - px) * A
            blk[r, :, c, :] = np.clip(px + 0.5, 0, 255).astype(np.uint8)
        img.paste(Image.fromarray(reg), box[:2])

@lru_cache(maxsize=64)
def _topology(faces: tuple):
    """Unique edges (m x 2 vertex ids) and their two faces (m x 2; a boundary edge repeats its one)."""
    seen: dict[tuple, list] = {}
    for k, loop in enumerate(faces):
        for a, b in zip(loop, loop[1:] + loop[:1]):
            seen.setdefault((min(a, b), max(a, b)), []).append(k)
    E = np.array(list(seen), np.int64).reshape(-1, 2)
    F = np.array([(fs + fs)[:2] for fs in seen.values()], np.int64).reshape(-1, 2)
    return (E, F)

def _normals(V: np.ndarray, faces: tuple):
    """Unit normals (Newell; zero for degenerate faces) and centroids, vectorised per loop length."""
    n = np.zeros((len(faces), 3))
    c = np.zeros((len(faces), 3))
    groups: dict[int, list] = {}
    for k, f in enumerate(faces):
        groups.setdefault(len(f), []).append(k)
    for ks in groups.values():
        P = V[np.array([faces[k] for k in ks])]
        Q = np.roll(P, -1, axis=1)
        n[ks] = np.stack([((P[..., 1] - Q[..., 1]) * (P[..., 2] + Q[..., 2])).sum(1), ((P[..., 2] - Q[..., 2]) * (P[..., 0] + Q[..., 0])).sum(1), ((P[..., 0] - Q[..., 0]) * (P[..., 1] + Q[..., 1])).sum(1)], axis=-1)
        c[ks] = P.mean(axis=1)
    ln = np.linalg.norm(n, axis=1)
    ok = ln > 1e-12
    n[ok] /= ln[ok, None]
    n[~ok] = 0
    return (n, c)
ORTHO = {1: '╵', 2: '╶', 4: '╷', 8: '╴', 5: '│', 10: '─', 3: '└', 6: '┌', 12: '┐', 9: '┘', 7: '├', 14: '┬', 13: '┤', 11: '┴', 15: '┼'}

@lru_cache(maxsize=8)
def _arm_table(at: Atlas) -> np.ndarray:
    """Atlas index for every arm mask 0..255: orthogonal arms -> the light box set, diagonal arms
    -> ╱ ╲ ╳; a cell with both keeps the family with more arms (ties: orthogonal)."""
    out = np.zeros(256, np.int32)
    for m in range(1, 256):
        o, d = (m & 15, m >> 4)
        no, nd = (bin(o).count('1'), bin(d).count('1'))
        if o and no >= nd:
            out[m] = at.get(ORTHO[o])
        elif d:
            ne_sw, nw_se = (bool(d & (1 | 4)), bool(d & (2 | 8)))
            out[m] = at.get('╳' if ne_sw and nw_se else '╱' if ne_sw else '╲')
    return out

def _plane(xs, ys, vals: np.ndarray):
    """Coefficients (3 x m) with vals = [x y 1] @ coef, from a planar polygon's projected vertices
    (the widest vertex triangle; least squares when the polygon is near degenerate)."""
    k = len(xs)
    best, tri = (0.0, None)
    for i in (0,):
        for j in range(1, k - 1):
            a = abs((xs[j] - xs[i]) * (ys[j + 1] - ys[i]) - (xs[j + 1] - xs[i]) * (ys[j] - ys[i]))
            if a > best:
                best, tri = (a, (i, j, j + 1))
    if tri is None or best < 1e-06:
        return None
    M = np.array([[xs[i], ys[i], 1.0] for i in tri])
    return np.linalg.solve(M, vals[list(tri)])

def _unit(v) -> np.ndarray:
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)

def _bilinear(T: np.ndarray, x: np.ndarray, y: np.ndarray) -> np.ndarray:
    x0, y0 = (x.astype(np.int64), y.astype(np.int64))
    fx, fy = (x - x0, y - y0)
    x1, y1 = (np.minimum(x0 + 1, T.shape[1] - 1), np.minimum(y0 + 1, T.shape[0] - 1))
    return T[y0, x0] * (1 - fx) * (1 - fy) + T[y0, x1] * fx * (1 - fy) + T[y1, x0] * (1 - fx) * fy + T[y1, x1] * fx * fy
MIP = np.array([6, 8, 10, 12, 14, 17, 20, 24, 29, 35, 42, 50, 60, 72, 86, 104, 125, 150])

@lru_cache(maxsize=256)
def _text_texture(text: str, font_path: str, px: int) -> np.ndarray:
    """Coverage (float32 0..1) of one line of text whose full height (ascent + descent) is about
    px pixels, hinted at that size; columns are resampled so every mip level has the same aspect."""
    size = max(4, int(round(px / 1.17)))
    f = ImageFont.truetype(font_path, size)
    asc, desc = f.getmetrics()
    tw = int(math.ceil(f.getlength(text)))
    im = Image.new('L', (max(1, tw), asc + desc), 0)
    ImageDraw.Draw(im).text((0, 0), text, font=f, fill=255)
    want = max(1, int(round((asc + desc) * _text_aspect(text, font_path))))
    if want != im.width:
        im = im.resize((want, im.height), Image.BILINEAR)
    return np.asarray(im, np.float32) / 255.0

@lru_cache(maxsize=256)
def _text_aspect(text: str, font_path: str) -> float:
    """Width / height of a text line, measured large (the sign's world width follows it)."""
    f = ImageFont.truetype(font_path, 200)
    asc, desc = f.getmetrics()
    return f.getlength(text) / (asc + desc)

def floor_grid(v: View, x0: float, x1: float, z0: float, z1: float, step: float=1.0, y: float=0.0, color='ink', lv: float=0.25, style: str='dots', lod=(5.0, 14.0)):
    """A floor grid on the plane y (dim braille by default: a low-brightness fill). Lines are cut
    at every crossing and each piece fades by its on-screen distance to the next parallel line:
    gone below lod[0] px, full above lod[1] px. So the far grid thins out instead of piling up
    into a solid band at the horizon, and it fades continuously as the camera moves (no popping)."""
    xs = np.arange(x0, x1 + 1e-09, step)
    zs = np.arange(z0, z1 + 1e-09, step)
    X, Z = np.meshgrid(xs[:-1], zs)
    a1 = np.stack([X, np.full_like(X, y), Z], -1).reshape(-1, 3)
    b1 = a1 + (step, 0.0, 0.0)
    X, Z = np.meshgrid(xs, zs[:-1])
    a2 = np.stack([X, np.full_like(X, y), Z], -1).reshape(-1, 3)
    b2 = a2 + (0.0, 0.0, step)
    A, B = (np.concatenate([a1, a2]), np.concatenate([b1, b2]))
    nb = np.concatenate([np.tile((0.0, 0.0, step), (len(a1), 1)), np.tile((step, 0.0, 0.0), (len(a2), 1))])
    m = (A + B) / 2
    x_a, y_a, _ = v.project(m)
    x_b, y_b, _ = v.project(m + nb)
    d = np.hypot(x_b - x_a, y_b - y_a)
    fade = np.where(np.isfinite(d), np.clip((d - lod[0]) / max(1e-06, lod[1] - lod[0]), 0.0, 1.0), 1.0)
    keep = fade > 0.01
    v.lines(A[keep], B[keep], color=color, lv=(lv * fade)[keep], style=style)

def cube(v: View, center, size: float, yaw: float=0.0, tilt: float=0.0, **kw) -> int:
    """A cube of edge `size` turned by yaw (about y) then tilt (about x), in degrees: a solid."""
    a, b = (math.radians(yaw), math.radians(tilt))
    h = size / 2
    pts = []
    for z in (-h, h):
        for y in (-h, h):
            for x in (-h, h):
                x1, z1 = (x * math.cos(a) + z * math.sin(a), -x * math.sin(a) + z * math.cos(a))
                y2, z2 = (y * math.cos(b) - z1 * math.sin(b), y * math.sin(b) + z1 * math.cos(b))
                pts.append((center[0] + x1, center[1] + y2, center[2] + z2))
    return v.solid(pts, _BOX, **kw)
