"""The inside plates' canvas (BUILD_V2_20261003.md §4): float ink layers drawn with PIL at 4x supersampling and
laid on flat paper by absorption (inside_lab/lab2d.py's paper mode), so overlapping strokes darken the way ink
does and a layer at 1 gives exactly its colour. Nothing here imports the film's modules.

A plate is PW x PH film pixels (the terminal's content area while it fills the frame, PLATE in film pixels);
renderers return an RGB uint8 array of that size on flat paper, and install.py lays it on the film's own
background by multiplying (so the dot field shows through and there is no edge).
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
PLATE = (100, 84, 1248, 596)
PW, PH = (PLATE[2] - PLATE[0], PLATE[3] - PLATE[1])
FPS = 24
PAPER = (236, 232, 222)
INK = (29, 32, 41)
BLUE = (77, 107, 254)
QUIET = tuple((int(round(b + (g - b) * 0.55)) for b, g in zip(BLUE, (115, 115, 115))))
ASH = (125, 121, 111)
COLOURS = {'ink': INK, 'blue': BLUE, 'quiet': QUIET, 'ash': ASH}
W_MAIN, W_SEC, W_FINE = (2.4, 1.2, 0.6)
SS = 4
_VF = {'sans': 'C:/Windows/Fonts/NotoSansSC-VF.ttf'}
_FILES = {'mono': 'C:/Windows/Fonts/consola.ttf', 'monob': 'C:/Windows/Fonts/consolab.ttf', 'cjk': 'C:/Windows/Fonts/msyh.ttc', 'cjkb': 'C:/Windows/Fonts/msyhbd.ttc'}
_FONTS: dict = {}

def font(size: float, kind: str='sans:460'):
    """kind: mono / monob / cjk / cjkb, or 'sans:<weight>' (Noto Sans SC variable)."""
    size = max(4, int(round(size)))
    key = (size, kind)
    if key not in _FONTS:
        if ':' in kind:
            fam, wt = kind.split(':')
            f = ImageFont.truetype(_VF[fam], size)
            f.set_variation_by_axes([int(wt)])
        else:
            f = ImageFont.truetype(_FILES[kind], size)
        _FONTS[key] = f
    return _FONTS[key]

def is_cjk(ch: str) -> bool:
    return ord(ch) >= 11904

def kind_for(s: str, cjk='sans:460', mono='mono') -> str:
    return cjk if any((is_cjk(c) for c in s)) else mono

def text_w(s: str, size: float, kind: str) -> float:
    return font(size * SS, kind).getlength(s) / SS
_INK_BOX: dict = {}

def ink_box(s: str, size: float, kind: str):
    """True ink box of s drawn at origin with baseline 0: (x0, y0, x1, y1) px (y0 < 0 above the baseline)."""
    key = (s, round(size * SS), kind)
    if key not in _INK_BOX:
        f = font(size * SS, kind)
        pad = int(size * SS)
        im = Image.new('L', (int(f.getlength(s)) + 2 * pad, int(size * SS * 2.6)), 0)
        by = int(size * SS * 1.7)
        ImageDraw.Draw(im).text((pad, by), s, font=f, fill=255, anchor='ls')
        b = im.getbbox() or (pad, by, pad + 1, by + 1)
        _INK_BOX[key] = ((b[0] - pad) / SS, (b[1] - by) / SS, (b[2] - pad) / SS, (b[3] - by) / SS)
    return _INK_BOX[key]

def clamp(u):
    return min(1.0, max(0.0, float(u)))

def prog(t, a, b):
    return clamp((t - a) / max(1e-09, b - a))

def smooth(u):
    u = clamp(u)
    return u * u * (3 - 2 * u)

def smoother(u):
    u = clamp(u)
    return u * u * u * (u * (6 * u - 15) + 10)

def out_cubic(u):
    u = clamp(u)
    return 1 - (1 - u) ** 3

def in_out_sine(u):
    return 0.5 - 0.5 * math.cos(math.pi * clamp(u))

def lerp(a, b, u):
    return a + (b - a) * u

def bezier(p0, p1, p2, p3, n=160):
    u = np.linspace(0.0, 1.0, n)[:, None]
    p0, p1, p2, p3 = (np.asarray(p, np.float64) for p in (p0, p1, p2, p3))
    return (1 - u) ** 3 * p0 + 3 * (1 - u) ** 2 * u * p1 + 3 * (1 - u) * u * u * p2 + u ** 3 * p3

def arclen(pts):
    d = np.sqrt(((pts[1:] - pts[:-1]) ** 2).sum(1))
    return np.concatenate([[0.0], np.cumsum(d)])

def partial(pts, k1, k0=0.0):
    """The part of a polyline between fractions k0 and k1 of its length."""
    s = arclen(pts)
    if s[-1] <= 0 or k1 <= k0:
        return pts[:1]
    a, b = (k0 * s[-1], k1 * s[-1])
    keep = (s > a) & (s < b)
    pa = np.array([np.interp(a, s, pts[:, 0]), np.interp(a, s, pts[:, 1])])
    pb = np.array([np.interp(b, s, pts[:, 0]), np.interp(b, s, pts[:, 1])])
    return np.vstack([pa, pts[keep], pb])

class Plate:
    """Float coverage layers ('ink', 'blue', 'quiet', 'ash') drawn by PIL at SS x; compose() lays them on paper."""

    def __init__(self, w=PW, h=PH):
        self.w, self.h = (w, h)
        self.L = {}

    def _d(self, layer):
        if layer not in self.L:
            im = Image.new('L', (self.w * SS, self.h * SS), 0)
            self.L[layer] = (im, ImageDraw.Draw(im))
        return self.L[layer][1]

    @staticmethod
    def _v(val):
        return int(round(255 * min(1.0, max(0.0, val))))

    def line(self, pts, width=W_SEC, val=1.0, layer='ink'):
        v = self._v(val)
        pts = np.asarray(pts, np.float64)
        if v <= 0 or len(pts) < 2:
            return
        self._d(layer).line([(float(x * SS), float(y * SS)) for x, y in pts], fill=v, width=max(1, int(round(width * SS))), joint='curve')

    def rect(self, x0, y0, x1, y1, val=1.0, layer='ink', width=None):
        v = self._v(val)
        if v <= 0:
            return
        box = (x0 * SS, y0 * SS, x1 * SS, y1 * SS)
        if width is None:
            self._d(layer).rectangle(box, fill=v)
        else:
            self._d(layer).rectangle(box, outline=v, width=max(1, int(round(width * SS))))

    def circle(self, x, y, r, val=1.0, layer='ink', width=None):
        v = self._v(val)
        if v <= 0:
            return
        box = ((x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS)
        if width is None:
            self._d(layer).ellipse(box, fill=v)
        else:
            self._d(layer).ellipse(box, outline=v, width=max(1, int(round(width * SS))))

    def text(self, x, y, s, size, kind='sans:460', val=1.0, layer='ink', anchor='ls'):
        """Text at (x, y) with a PIL anchor (default left/baseline)."""
        v = self._v(val)
        if v <= 0 or not s:
            return
        self._d(layer).text((x * SS, y * SS), s, font=font(size * SS, kind), fill=v, anchor=anchor)

    def mixed(self, x, y, s, size, val=1.0, layer='ink', cjk='sans:460', mono='mono', anchor='ls', msize=None):
        """Mono for ASCII runs, CJK for the rest; anchor 'ls' / 'ms' / 'rs' on the whole string."""
        runs, cur, k0 = ([], '', None)
        for ch in s:
            k = cjk if is_cjk(ch) else mono
            if k0 is not None and k != k0:
                runs.append((cur, k0))
                cur = ''
            cur += ch
            k0 = k
        if cur:
            runs.append((cur, k0))
        ms = msize or size * 0.86
        ws = [text_w(r, size if k == cjk else ms, k) for r, k in runs]
        tot = sum(ws)
        if anchor[0] == 'm':
            x -= tot / 2
        elif anchor[0] == 'r':
            x -= tot
        for (r, k), w_ in zip(runs, ws):
            self.text(x, y, r, size if k == cjk else ms, k, val, layer, 'l' + anchor[1])
            x += w_
        return tot

    def arr(self, layer):
        if layer not in self.L:
            return None
        im = self.L[layer][0].resize((self.w, self.h), Image.BOX)
        return np.asarray(im, np.float32) / 255.0

    def compose(self, gain=None):
        """Paper by absorption: rgb = paper * exp(-sum(layer * absorb(colour)))."""
        paper = np.array(PAPER, np.float32) / 255.0
        acc = np.zeros((self.h, self.w, 3), np.float32)
        for name, col in COLOURS.items():
            a = self.arr(name)
            if a is None:
                continue
            c = np.array(col, np.float32) / 255.0
            absorb = -np.log(np.clip(c / paper, 0.0001, 1.0))
            acc += a[..., None] * absorb * (gain or {}).get(name, 1.0)
        rgb = paper * np.exp(-acc)
        return (np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8)
