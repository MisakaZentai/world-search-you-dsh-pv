"""Lays the inside plates into the film (BUILD_V2_20261003.md §4).

For every inside span: the D2 break-out carries the way in and out (groups.base.full_frame: the dsh window slides
off, the terminal widens), and the plate comes up inside the widened terminal, clipped to its moving right edge.
The shots under a span keep running as they are (their own timing, their strip with its read pulses, their command
line); install() wraps their fn and, after it has drawn, lays the plate on the film's own background over the
content area by multiplying (paper stays paper, so the dot field shows through and there is no edge). While a
plate is up both LEAD regions stay at full level (the right half of the plate is in the 'right' region).

Plates come from cache/inside/<shot>/<frame>.png (cache.py renders them ahead, in parallel); a missing frame is
rendered on the spot.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
from pathlib import Path
import numpy as np
from PIL import Image
import hud
from groups.base import full_frame
from tuikit import ease
from .plate import PAPER, PLATE
ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'cache' / 'inside'
_PAPER = np.array(PAPER, np.float32)

class Span:
    """One inside shot. make() returns an object with render(t) -> (PH, PW, 3) uint8 on flat paper."""

    def __init__(self, name, t_in, t_out, make, slide_out=0.3, slide_back=0.4, fade_in=None, fade_out=None, register=True, frame_back=None, rect=PLATE, lift='both', frame_in=None):
        self.name, self.t_in, self.t_out, self.make = (name, float(t_in), float(t_out), make)
        self.frame_in = self.t_in if frame_in is None else float(frame_in)
        self.rect = tuple(rect)
        self.lift = lift
        self.frame_back = self.t_out if frame_back is None else float(frame_back)
        self.slide_out, self.slide_back = (slide_out, slide_back)
        self.fade_in = slide_out if fade_in is None else fade_in
        self.fade_out = slide_back if fade_out is None else fade_out
        self.register = register
        self._r = None

    @property
    def end(self):
        return self.t_out + self.fade_out

    def active(self, t):
        return self.t_in <= t < self.end

    def alpha(self, t):
        a = ease.ease_out(ease.prog(t, self.t_in, self.t_in + max(0.001, self.fade_in)))
        if self.fade_out <= 0.001:
            return a if t < self.t_out else 0.0
        return a * (1 - ease.ease_io(ease.prog(t, self.t_out, self.t_out + self.fade_out)))

    def frames(self, fps=24):
        return range(int(np.ceil(self.t_in * fps - 1e-06)), int(np.ceil(self.end * fps - 1e-06)))

    def renderer(self):
        if self._r is None:
            self._r = self.make()
        return self._r

    def path(self, n):
        return CACHE / self.name / f'{n:05d}.png'

    def plate(self, n, fps=24, save=False):
        f = self.path(n)
        if f.exists():
            return np.asarray(Image.open(f).convert('RGB'))
        arr = self.renderer().render(n / fps)
        if save:
            f.parent.mkdir(parents=True, exist_ok=True)
            Image.fromarray(arr).save(f)
        return arr

def paint(film, c, sp):
    t = c.t
    a = sp.alpha(t)
    if a <= 0.002:
        return
    x0, y0, x1, y1 = sp.rect
    right = min(x1, hud.left_rect(t)[2] - 8)
    if right <= x0 + 2:
        return
    plate = sp.plate(c.n).astype(np.float32)
    bg = np.asarray(film.background(t).crop(sp.rect), np.float32)
    comp = bg * (plate / _PAPER)
    cur = np.asarray(c.img.crop(sp.rect).convert('RGB'), np.float32)
    m = np.clip((right - (x0 + np.arange(x1 - x0) + 0.5)) / 6.0, 0.0, 1.0) * a
    m = m[None, :, None]
    out = cur * (1 - m) + comp * m
    c.img.paste(Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8)), (x0, y0))

def install(film, spans):
    """Wrap the shots under each span, register the break-outs, keep both LEAD regions up while a plate shows."""
    for sp in spans:
        if sp.register:
            full_frame(sp.frame_in, sp.frame_back, sp.slide_out, sp.slide_back)
    for shot in film.shots:
        mine = [sp for sp in spans if shot.start < sp.end and sp.t_in < shot.end]
        if not mine:
            continue
        orig = shot.fn

        def fn(c, _orig=orig, _mine=mine, **kw):
            _orig(c, **kw)
            for sp in _mine:
                if sp.active(c.t):
                    paint(film, c, sp)
        shot.fn = fn
    base_levels = film.levels

    def levels(t):
        lv = dict(base_levels(t))
        for sp in spans:
            if sp.lift and sp.active(t):
                a = sp.alpha(t)
                for k in ('left', 'right') if sp.lift == 'both' else (sp.lift,):
                    if k in lv:
                        lv[k] = ease.lerp(lv[k], 1.0, a)
        return lv
    film.levels = levels
    film.inside_spans = spans
    return film
