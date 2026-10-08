"""Transitions as continuity: carriers, ink, and cell-by-cell reveals.

The rule from the owner: something visibly crosses the cut and causes the next picture.
A carrier's life is  lift (2-4 frames before the cut, glow in place)
                  -> fly  (quadratic arc, eased, readable size >= ~24 px glyph height)
                  -> land (lock-in on a beat or sung onset, small overshoot)
                  -> seed (the new panel decodes outward from the landing point).
Never wipe with a band, never dissolve the whole frame.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
import random
from dataclasses import dataclass
import numpy as np
from PIL import Image, ImageDraw
from . import ease
from .glyph import GLITCH, halo

def place(layer: Image.Image, sprite: Image.Image, center, scale: float=1.0, alpha: float=1.0):
    """Alpha-composite sprite onto an RGBA layer, centred, scaled (nearest for crisp glyphs)."""
    if alpha <= 0 or scale <= 0:
        return
    sp = sprite
    if abs(scale - 1.0) > 0.001:
        sp = sprite.resize((max(1, int(sprite.width * scale)), max(1, int(sprite.height * scale))), Image.NEAREST)
    if alpha < 1.0:
        a = sp.getchannel('A').point(lambda v: int(v * alpha))
        sp = sp.copy()
        sp.putalpha(a)
    x, y = (int(center[0] - sp.width / 2), int(center[1] - sp.height / 2))
    composite_at(layer, sp, (x, y))

def composite_at(layer: Image.Image, sprite: Image.Image, xy):
    """alpha_composite that clips at the layer edges (Pillow refuses negative destinations)."""
    x, y = xy
    sx0, sy0 = (max(0, -x), max(0, -y))
    sx1, sy1 = (min(sprite.width, layer.width - x), min(sprite.height, layer.height - y))
    if sx1 <= sx0 or sy1 <= sy0:
        return
    layer.alpha_composite(sprite, dest=(x + sx0, y + sy0), source=(sx0, sy0, sx1, sy1))

def ink(img: Image.Image, bg: Image.Image, rect, threshold: int=18) -> Image.Image:
    """Fallback carrier: cut a region out of the pre-chrome canvas and key out the background,
    so only strokes remain. Prefer redrawing the object from its data (glyph.text_sprite)."""
    a = np.asarray(img.crop(rect).convert('RGB'), dtype=np.int16)
    b = np.asarray(bg.crop(rect).convert('RGB'), dtype=np.int16)
    diff = np.abs(a - b).max(axis=2)
    alpha = np.clip((diff - threshold) * 6, 0, 255).astype(np.uint8)
    out = img.crop(rect).convert('RGBA')
    out.putalpha(Image.fromarray(alpha))
    return out

@dataclass
class Carrier:
    sprite: Image.Image
    p0: tuple
    p1: tuple
    t_lift: float
    t_fly: float
    t_land: float
    color: tuple = (77, 107, 254)
    bend: float = 0.22
    fly_scale: float = 1.6
    land_scale: float = 1.0
    settle: float = 2 / 24
    ghost: float = 4 / 24

    @property
    def seed(self):
        return self.p1

    def active(self, t: float) -> bool:
        return self.t_lift <= t < self.t_land + self.settle

    def draw(self, layer: Image.Image, t: float):
        if not self.active(t):
            return
        if t < self.t_fly:
            u = ease.prog(t, self.t_lift, self.t_fly)
            place(layer, halo(self.sprite, self.color, 3, 0.4 + 0.6 * u), self.p0)
            return
        if t < self.t_fly + self.ghost:
            place(layer, self.sprite, self.p0, 1.0, 0.2)
        if t < self.t_land:
            u = ease.ease_io(ease.prog(t, self.t_fly, self.t_land))
            pos = ease.bezier(self.p0, self.p1, self.bend, u)
            s = ease.lerp(1.0, self.land_scale, u) + (self.fly_scale - 1.0) * math.sin(math.pi * u)
            place(layer, halo(self.sprite, self.color, 3, 0.9), pos, s)
            return
        u = ease.prog(t, self.t_land, self.t_land + self.settle)
        place(layer, halo(self.sprite, self.color, 3, 1.0 - u), self.p1, self.land_scale * (1.08 - 0.08 * u))

def radial(seed, t0: float, speed: float):
    """Cells switch as a ring expands from seed at `speed` px/s (the new panel grows from the landing)."""
    sx, sy = seed
    return lambda X, Y: t0 + np.hypot(X - sx, Y - sy) / speed

def inward(seed, t0: float, t1: float, reach: float):
    """Far cells go first, the seed last: the old content is drawn into the carrier."""
    sx, sy = seed
    return lambda X, Y: t1 - (t1 - t0) * np.clip(np.hypot(X - sx, Y - sy) / reach, 0, 1)

def sweep(origin, direction, t0: float, speed: float):
    """Directional scan with a meaning (time -> right, depth -> down, past -> left)."""
    ox, oy = origin
    dx, dy = direction
    n = math.hypot(dx, dy) or 1.0
    dx, dy = (dx / n, dy / n)
    return lambda X, Y: t0 + np.maximum(0, (X - ox) * dx + (Y - oy) * dy) / speed

def reveal(old: Image.Image, new: Image.Image, t: float, delay, region=None, cell=(8, 16), dur: float=0.09, seed: int=0, jitter: float=0.02, font=None, glyph_color=(77, 107, 254), bg=(4, 7, 15)):
    """Replace old by new cell by cell. Each cell switches at delay(cx, cy); during `dur` it flashes a
    decode glyph. `delay` is one of radial / inward / sweep (vectorised over numpy grids)."""
    W, H = old.size
    x0, y0, x1, y1 = region or (0, 0, W, H)
    cw, ch = cell
    nx, ny = (max(1, math.ceil((x1 - x0) / cw)), max(1, math.ceil((y1 - y0) / ch)))
    X, Y = np.meshgrid(x0 + (np.arange(nx) + 0.5) * cw, y0 + (np.arange(ny) + 0.5) * ch)
    D = np.asarray(delay(X, Y), dtype=float)
    if jitter:
        D = D + np.random.default_rng(seed).uniform(-jitter, jitter, D.shape)
    done = t >= D + dur
    flashing = (t >= D) & ~done
    out = old.copy()
    if done.any():
        mask = Image.fromarray((done * 255).astype(np.uint8)).resize((nx * cw, ny * ch), Image.NEAREST)
        mask = mask.crop((0, 0, x1 - x0, y1 - y0))
        out.paste(new.crop((x0, y0, x1, y1)), (x0, y0), mask)
    if flashing.any():
        d = ImageDraw.Draw(out)
        ys, xs = np.nonzero(flashing)
        for j, i in zip(ys.tolist(), xs.tolist()):
            cx0, cy0 = (x0 + i * cw, y0 + j * ch)
            d.rectangle((cx0, cy0, cx0 + cw - 1, cy0 + ch - 1), fill=bg)
            if font is not None:
                r = random.Random(seed * 131 + j * 977 + i * 31 + ease.tick(t, 48))
                d.text((cx0, cy0), r.choice(GLITCH), font=font, fill=glyph_color)
    return out

def reveal_done(delay, region, t: float, cell=(8, 16), dur: float=0.09, jitter: float=0.02) -> bool:
    x0, y0, x1, y1 = region
    X, Y = np.meshgrid(np.arange(x0, x1, cell[0]) + cell[0] / 2, np.arange(y0, y1, cell[1]) + cell[1] / 2)
    return bool((t >= np.asarray(delay(X, Y)) + dur + jitter).all())
