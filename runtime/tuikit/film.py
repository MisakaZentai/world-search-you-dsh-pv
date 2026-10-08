"""Film: one timeline, frame = f(t), explicit registries instead of monkey-patching.

Draw order of every frame (the order that shipped the approved film):

    1. content     shot (or cut) canvas, background already painted, no chrome
    2. under       carrier layer when a cut asks for it under the character
    3. character   the character layer (her pane / UI window), with LEAD alpha
    4. overlays    per-shot art anchored on the character (props, eye bars)
    5. over        carriers of the active cut (default: above the character)
    6. chrome      header + lyric band, drawn once, never transformed
    7. post        bloom / scanlines
    8. lead dim    SUPPORT side dimmed toward bg (chrome areas excluded)
    9. finish      last-word hooks (rare: e.g. keep one button undimmed)

A shot draws into ctx.img and may leave notes in ctx.state for the character layer.
Everything a frame needs is derived from t, so any range renders in any order.

Motion blur (optional, off by default): frame(n, samples=...) averages layers 1-5 over sub-frames
spread across `shutter` x (1/fps) around t; chrome, post, LEAD dim and finish run once per frame, so
the lyric band stays crisp. Every sub-frame keeps the frame number n: jitter and flicker keyed to
ctx.n / ctx.rng stay constant across the shutter, anything driven by ctx.t moves and streaks.
film.blur(t0, t1) limits it to registered spans (carrier flights, whips). samples="auto" steps
4 -> 12 -> 36 -> 108 -> 324 sub-frames until one more step would change the image by less than
`tol` levels (after pdoom-video's Engine.render, MIT); a frame whose first 4 sub-frames are identical
costs 4 renders and is returned as is.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import bisect
import random
import zlib
from dataclasses import dataclass, field
from functools import cached_property
from typing import Callable
import numpy as np
from PIL import Image, ImageDraw
from . import ease, glyph

@dataclass
class Ctx:
    film: 'Film'
    shot: 'Shot'
    t: float
    n: int
    img: Image.Image
    hooks: dict = field(default_factory=dict)
    state: dict = field(default_factory=dict)
    black: bool = False
    no_chrome: bool = False

    @property
    def lt(self) -> float:
        return self.t - self.shot.start

    @property
    def dur(self) -> float:
        return self.shot.end - self.shot.start

    @property
    def u(self) -> float:
        return ease.clamp(self.lt / self.dur) if self.dur > 0 else 1.0

    @property
    def d(self) -> ImageDraw.ImageDraw:
        return ImageDraw.Draw(self.img)

    @property
    def p(self):
        return self.film.p

    @property
    def clock(self):
        return self.film.p.clock

    @property
    def lyrics(self):
        return self.film.p.lyrics

    @cached_property
    def a(self) -> dict:
        """Music at t (timing/audio.json): envelopes rms/low/mid/high/vocal/drums/bass/other and
        decaying pulses kick/snare/hat/vonset, all 0..1; zeros when the project has no analysis."""
        return self.film.p.music.sample(self.t)

    @cached_property
    def rng(self) -> random.Random:
        """One generator per frame, seeded from shot name and frame number (crc32, not hash():
        worker processes must agree). Successive draws differ; the same frame always repeats.
        For per-shot constants (same every frame) use random.Random(crc32(name) + k) yourself."""
        return random.Random(zlib.crc32(self.shot.name.encode('utf-8')) * 7919 + self.n)

    def h(self, key, default=None):
        """Read a hook set by a cut or by Film.hooks (lets a cut restage a scene without copying it)."""
        return self.hooks.get(key, default)

    def color(self, name, lv: float=1.0):
        return glyph.level(self.p.color(name), lv, self.p.color('bg'))

    def font(self, size, kind='mono'):
        return self.p.font(size, kind)

@dataclass
class Shot:
    name: str
    start: float
    end: float
    fn: Callable[[Ctx], None]
    chapter: str = ''
    kind: str = 'split'
    hide_character: bool = False
    params: dict = field(default_factory=dict)

@dataclass
class Frame:
    """What a cut returns: the content canvas plus layers and character adjustments."""
    content: Image.Image
    ctx: Ctx
    over: Image.Image | None = None
    under: bool = False
    char_alpha: float = 1.0
    char_shift: tuple = (0, 0)

class Cut:
    """A staged transition into shot `b`. Subclass and implement render().
    self.old(t) keeps the outgoing scene running past its end; self.new(t) freezes the incoming
    scene at its first frame until T. Put the key moment on a beat or a sung onset."""
    pre = 0.3
    post = 0.3
    verb = 'CARRY'
    why = ''

    def __init__(self, film: 'Film', a: Shot, b: Shot):
        self.film, self.a, self.b, self.T = (film, a, b, b.start)

    def active(self, t: float) -> bool:
        return self.T - self.pre <= t < self.T + self.post

    def old(self, t: float, n: int, **hooks) -> Ctx:
        return self.film.body(self.a, t, n, hooks)

    def new(self, t: float, n: int, **hooks) -> Ctx:
        return self.film.body(self.b, max(t, self.b.start), n, hooks)

    def render(self, t: float, n: int) -> Frame:
        raise NotImplementedError

class HardCut(Cut):
    """Only for musical hits (the hits list in beats.json)."""
    pre = post = 0.0
    verb = 'HIT'

class Film:

    def __init__(self, project):
        self.p = project
        self.shots: list[Shot] = []
        self.cuts: dict[str, type] = {}
        self.hooks: dict[str, dict] = {}
        self.character: Callable | None = None
        self.overlays: list[Callable] = []
        self.chrome: Callable | None = None
        self.post: Callable | None = None
        self.finish: list[Callable] = []
        self.lead: list[tuple[float, str]] = [(0.0, 'both')]
        self.lead_regions = {'left': project.rect('left') if project.has_rect('left') else None, 'right': project.rect('right') if project.has_rect('right') else None}
        self.cover: list[tuple[float, float, str]] = []
        self.blur_spans: list[tuple[float, float]] = []
        self.last_samples = 1
        self._cut_objs: list[Cut] | None = None
        self._starts: list[float] = []

    def use(self, *modules):
        """Section modules, one per parallel builder: each defines register(film) and adds only the
        shots, cuts (into its own shots), hooks and overlays of its own time span."""
        for m in modules:
            m.register(self)
        self._cut_objs = None
        return self

    def add(self, name, start, end, fn, **kw) -> Shot:
        s = Shot(name, float(start), float(end), fn, **kw)
        self.shots.append(s)
        self._cut_objs = None
        return s

    def cut(self, into: str, cls: type):
        self.cuts[into] = cls
        self._cut_objs = None

    def finalize(self, end: float | None=None):
        """Sort, and check there are no gaps or overlaps."""
        self.shots.sort(key=lambda s: s.start)
        for a, b in zip(self.shots, self.shots[1:]):
            if abs(a.end - b.start) > 1e-06:
                raise ValueError(f'gap/overlap between {a.name} ({a.end}) and {b.name} ({b.start})')
        if end is not None and self.shots[-1].end + 1e-06 < end:
            raise ValueError(f'timeline ends at {self.shots[-1].end}, film needs {end}')
        self._starts = [s.start for s in self.shots]
        names = {s.name for s in self.shots}
        for k in self.cuts:
            if k not in names:
                raise ValueError(f'cut into unknown shot {k}')
        self.lead.sort()
        return self

    def shot_at(self, t: float) -> Shot:
        if not self._starts:
            self.finalize()
        k = max(0, bisect.bisect_right(self._starts, t) - 1)
        return self.shots[k]

    def index(self, shot: Shot) -> int:
        return self.shots.index(shot)

    def cut_objects(self) -> list[Cut]:
        if self._cut_objs is None:
            self.finalize()
            objs = []
            for i, s in enumerate(self.shots):
                if i and s.name in self.cuts:
                    objs.append(self.cuts[s.name](self, self.shots[i - 1], s))
            self._cut_objs = objs
        return self._cut_objs

    def active_cut(self, t: float) -> Cut | None:
        for c in self.cut_objects():
            if c.active(t):
                return c
        return None

    def set_lead(self, t: float, side: str):
        """From t on, 'left' | 'right' | 'both' leads. The other side is dimmed, never cropped."""
        assert side in ('left', 'right', 'both')
        self.lead.append((float(t), side))
        self.lead.sort()

    def _levels(self, side: str) -> dict:
        s = self.p.setting('support_level', 0.42)
        return {'left': {'left': 1.0, 'right': s}, 'right': {'left': s, 'right': 1.0}, 'both': {'left': 1.0, 'right': 1.0}}[side]

    def levels(self, t: float) -> dict:
        """Brightness per region at t, cross-faded over lead_fade seconds after each change."""
        fade = self.p.setting('lead_fade', 0.25)
        k = max(0, bisect.bisect_right([x[0] for x in self.lead], t) - 1)
        t0, side = self.lead[k]
        cur = self._levels(side)
        if k == 0 or t - t0 >= fade:
            return cur
        prev = self._levels(self.lead[k - 1][1])
        u = ease.smooth((t - t0) / fade)
        return {r: ease.lerp(prev[r], cur[r], u) for r in cur}

    def covered(self, t: float) -> str | None:
        for t0, t1, name in self.cover:
            if t0 <= t < t1:
                return name
        return None

    def background(self, t: float) -> Image.Image:
        img = Image.new('RGB', (self.p.W, self.p.H), self.p.color('bg'))
        glyph.dot_field(img, t, self.p.color('ink'), lv=0.12, bg=self.p.color('bg'))
        return img

    def body(self, shot: Shot, t: float, n: int, hooks: dict | None=None) -> Ctx:
        h = dict(self.hooks.get(shot.name, {}))
        h.update(hooks or {})
        c = Ctx(self, shot, t, n, self.background(t), hooks=h)
        shot.fn(c, **shot.params)
        return c

    def compose(self, t: float, n: int):
        """Layers 1-5 (content, under, character, overlays, over) at song time t for frame n.
        Returns (RGB image, ctx, done); done means the frame is finished as is (a cut returned an
        image, or designed black): no chrome, post or dimming."""
        cut = self.active_cut(t)
        if cut is not None:
            fr = cut.render(t, n)
            if isinstance(fr, Image.Image):
                return (fr.convert('RGB'), None, True)
        else:
            c = self.body(self.shot_at(t), t, n)
            fr = Frame(c.img, c)
        ctx = fr.ctx
        if ctx.black:
            return (fr.content.convert('RGB'), ctx, True)
        img = fr.content.convert('RGBA')
        if fr.over is not None and fr.under:
            img.alpha_composite(fr.over)
        if self.character and (not ctx.shot.hide_character) and (fr.char_alpha > 0):
            layer = self.character(t, n, ctx)
            if layer is not None:
                a = fr.char_alpha
                if a < 1:
                    layer.putalpha(layer.getchannel('A').point(lambda v: int(v * a)))
                dx, dy = fr.char_shift
                if dx or dy:
                    moved = Image.new('RGBA', layer.size, (0, 0, 0, 0))
                    moved.paste(layer, (int(dx), int(dy)))
                    layer = moved
                img.alpha_composite(layer)
        for ov in self.overlays:
            layer = ov(t, n, ctx)
            if layer is not None:
                img.alpha_composite(layer)
        if fr.over is not None and (not fr.under):
            img.alpha_composite(fr.over)
        return (img.convert('RGB'), ctx, False)

    def blur(self, t0: float, t1: float):
        """Allow motion blur in [t0, t1) only (once any span is registered)."""
        self.blur_spans.append((float(t0), float(t1)))

    def _blurred(self, t: float) -> bool:
        return not self.blur_spans or any((a <= t < b for a, b in self.blur_spans))

    def _window(self, t: float):
        """The span around t that no cut crosses. A hard cut falls between frames, as on film; a staged
        cut is one continuous span from T - pre to T + post."""
        staged = {c.T: c for c in self.cut_objects() if c.pre > 0 or c.post > 0}
        edges = [0.0]
        for T in self._starts[1:]:
            c = staged.get(T)
            edges += [T - c.pre, T + c.post] if c else [T]
        return (max((e for e in edges if e <= t), default=0.0), min((e for e in edges if e > t), default=float('inf')))

    def _sampled(self, t: float, n: int, samples, shutter: float, tol: float, max_samples: int):
        """Average layers 1-5 over sub-frames at t + shutter/fps * u, u in (-0.5, 0.5). Sets of
        4, 12, 36 ... evenly spread offsets nest (each set contains the previous one). Sub-frames stay
        inside _window(t): picking the shot by sub-frame time put half of both shots into a cut frame."""
        dt = shutter / self.p.FPS
        lo, hi = self._window(t)

        def offsets(k):
            return [(i + 0.5) / k - 0.5 for i in range(k)]

        def at(u):
            return self.compose(min(max(t + dt * u, lo), hi - 1e-06), n)
        k = 4 if samples == 'auto' else max(1, int(samples))
        first = {u: at(u) for u in offsets(k)}
        ref = first[min(first, key=lambda u: abs(u - 0.125))]
        if ref[2] or any((v[2] for v in first.values())):
            self.last_samples = len(first)
            return ref
        arrs = [np.asarray(v[0], np.float32) for v in first.values()]
        acc = np.sum(arrs, axis=0)
        count = k
        if samples == 'auto':
            if max((float(np.abs(a - arrs[0]).max()) for a in arrs[1:])) < 1.0:
                self.last_samples = count
                return ref
            have = set((round(u, 9) for u in first))
            while count * 3 <= max_samples:
                prev = acc / count
                for u in offsets(count * 3):
                    if round(u, 9) not in have:
                        acc += np.asarray(at(u)[0], np.float32)
                count *= 3
                have = set((round(u, 9) for u in offsets(count)))
                d = np.abs(acc / count - prev)
                h, w = (d.shape[0] // 2 * 2, d.shape[1] // 2 * 2)
                block = d[:h, :w].reshape(h // 2, 2, w // 2, 2, 3).mean(axis=(1, 3))
                if 0.5 * float(block.max()) < tol:
                    break
        self.last_samples = count
        img = Image.fromarray(np.clip(np.rint(acc / count), 0, 255).astype(np.uint8))
        return (img, ref[1], False)

    def frame(self, n: int, samples=1, shutter: float=0.2, tol: float=3.0, max_samples: int=324) -> Image.Image:
        t = n / self.p.FPS
        if samples in (1, '1') or not self._blurred(t):
            img, ctx, done = self.compose(t, n)
            self.last_samples = 1
        else:
            img, ctx, done = self._sampled(t, n, samples, shutter, tol, max_samples)
        if done:
            return img
        lv = self.levels(t)
        if self.chrome and (not ctx.no_chrome):
            self.chrome(img, t, ctx)
        if self.post:
            img = self.post(img)
        img = self._dim(img, lv)
        for f in self.finish:
            out = f(img, t)
            if out is not None:
                img = out
        return img

    def _dim(self, img: Image.Image, lv: dict) -> Image.Image:
        bg = self.p.color('bg')
        for region, level in lv.items():
            rect = self.lead_regions.get(region)
            if rect is None or level >= 0.999:
                continue
            part = img.crop(rect)
            img.paste(Image.blend(Image.new('RGB', part.size, bg), part, level), rect[:2])
        return img
