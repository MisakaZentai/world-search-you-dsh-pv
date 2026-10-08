"""Easing, interpolation and small maths helpers."""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
FPS = 24

def tick(t: float, rate: float) -> int:
    """Index of a flicker that changes `rate` times per second, held for the whole frame.
    Keyed to the frame, not to continuous t: motion-blur sub-frames of one frame share it (a scramble
    keyed to t would average into a smear), and at exact frame times it equals int(t * rate) (without its float truncation, e.g. 2/24 * 60)."""
    return int(round(t * FPS) * rate / FPS + 1e-09)

def clamp(x: float, lo: float=0.0, hi: float=1.0) -> float:
    return lo if x < lo else hi if x > hi else x

def lerp(a, b, u: float):
    if isinstance(a, (tuple, list)):
        return type(a)((lerp(x, y, u) for x, y in zip(a, b)))
    return a + (b - a) * u

def prog(t: float, t0: float, t1: float) -> float:
    """0..1 progress of t through [t0, t1], clamped."""
    if t1 <= t0:
        return 1.0 if t >= t1 else 0.0
    return clamp((t - t0) / (t1 - t0))

def smooth(u: float) -> float:
    u = clamp(u)
    return u * u * (3 - 2 * u)

def ease_in(u: float) -> float:
    u = clamp(u)
    return u * u * u

def ease_out(u: float) -> float:
    u = clamp(u)
    return 1 - (1 - u) ** 3

def ease_io(u: float) -> float:
    u = clamp(u)
    return 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2

def ease_back(u: float, s: float=1.70158) -> float:
    """Overshoot then settle: use for landings that 'lock in'."""
    u = clamp(u) - 1
    return u * u * ((s + 1) * u + s) + 1

def keyframes(t: float, pts: list[tuple[float, float]], fn=smooth) -> float:
    """Piecewise interpolation through [(t, value), ...] with easing per segment."""
    if t <= pts[0][0]:
        return pts[0][1]
    for (t0, v0), (t1, v1) in zip(pts, pts[1:]):
        if t < t1:
            return lerp(v0, v1, fn(prog(t, t0, t1)))
    return pts[-1][1]

def bezier(p0, p1, bend: float, u: float):
    """Quadratic arc from p0 to p1; bend is the control-point offset as a fraction of the distance,
    perpendicular to the chord (positive bends to the left of travel)."""
    (x0, y0), (x1, y1) = (p0, p1)
    mx, my = ((x0 + x1) / 2, (y0 + y1) / 2)
    dx, dy = (x1 - x0, y1 - y0)
    cx, cy = (mx - dy * bend, my + dx * bend)
    a, b, c = ((1 - u) ** 2, 2 * (1 - u) * u, u * u)
    return (a * x0 + b * cx + c * x1, a * y0 + b * cy + c * y1)

def blink(t: float, period: float=1.06, low: float=0.45) -> float:
    """Cursor blink between full and `low`, never off."""
    return 1.0 if t % period < period / 2 else low
