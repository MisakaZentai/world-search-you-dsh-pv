"""lab3d: small 3D helpers shared by v5_space.py and v7_blueprint.py (numpy + PIL only).

  * Cam            pinhole camera (look-at, fov, roll, screen shift), project points, clip segments
  * splat / splat_segments   additive, anti-aliased point and line rasterisation (bincount based)
  * stroke font    a single-stroke engineering lettering (A-Z, 0-9, a few signs) as line segments
  * easing         spring step, outExpo, inQuad, outBack, ...

Nothing here writes files; common.py is imported read-only.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
import numpy as np
W, H = (1280, 720)

def clamp01(u):
    return np.clip(u, 0.0, 1.0)

def smooth(u):
    u = clamp01(u)
    return u * u * (3 - 2 * u)

def out_expo(u):
    u = clamp01(u)
    return np.where(u >= 1, 1.0, 1 - np.power(2.0, -10 * u))

def in_quad(u):
    u = clamp01(u)
    return u * u

def in_out_cubic(u):
    u = clamp01(u)
    return np.where(u < 0.5, 4 * u ** 3, 1 - (-2 * u + 2) ** 3 / 2)

def out_back(u, s=1.70158):
    u = clamp01(u)
    c3 = s + 1
    return 1 + c3 * (u - 1) ** 3 + s * (u - 1) ** 2

def spring_step(dt, freq=3.6, damp=0.74):
    """Unit step response of a damped spring (0 at dt<=0, ->1, small overshoot)."""
    dt = np.maximum(np.asarray(dt, float), 0.0)
    w = 2 * math.pi * freq
    if damp < 1:
        wd = w * math.sqrt(1 - damp * damp)
        return 1 - np.exp(-damp * w * dt) * (np.cos(wd * dt) + damp * w / wd * np.sin(wd * dt))
    return 1 - np.exp(-w * dt) * (1 + w * dt)

def env(dt, tau, attack=0.02):
    dt = np.asarray(dt, np.float64)
    a = np.clip(dt / attack, 0, 1)
    return np.where(dt < 0, 0.0, a * np.exp(-np.maximum(dt, 0) / tau))

def hash01(*ks):
    """Deterministic pseudo-random in [0,1) from integers."""
    x = 0
    for k in ks:
        x = x * 1103515245 + int(k) * 2654435761 + 12345 & 4294967295
    x ^= x >> 13
    x = x * 1540483477 & 4294967295
    x ^= x >> 15
    return (x & 16777215) / float(16777216)

class Cam:

    def __init__(self, pos, tgt, fov_deg=40.0, w=W, h=H, roll=0.0, shift=(0.0, 0.0), near=0.3):
        self.pos = np.asarray(pos, float)
        f = np.asarray(tgt, float) - self.pos
        f /= np.linalg.norm(f)
        up = np.array([0.0, 1.0, 0.0])
        r = np.cross(f, up)
        r /= np.linalg.norm(r)
        u = np.cross(r, f)
        if roll:
            c, s = (math.cos(roll), math.sin(roll))
            r, u = (c * r + s * u, -s * r + c * u)
        self.r, self.u, self.f = (r, u, f)
        self.focal = h / 2 / math.tan(math.radians(fov_deg) / 2)
        self.cx = w / 2 + shift[0]
        self.cy = h / 2 + shift[1]
        self.near = near
        self.w, self.h = (w, h)

    def cam_coords(self, P):
        d = np.asarray(P, float) - self.pos
        return (d @ self.r, d @ self.u, d @ self.f)

    def project(self, P):
        xc, yc, zc = self.cam_coords(P)
        z = np.maximum(zc, 0.0001)
        return (self.cx + self.focal * xc / z, self.cy - self.focal * yc / z, zc)

    def project_segments(self, A, B):
        """A, B: (N,3). Returns x0,y0,x1,y1,z0,z1,keep (near-plane clipped)."""
        ax, ay, az = self.cam_coords(A)
        bx, by, bz = self.cam_coords(B)
        n = self.near
        keep = (az > n) | (bz > n)
        ta = np.where(az < n, (n - az) / np.where(bz - az == 0, 1e-09, bz - az), 0.0)
        tb = np.where(bz < n, (n - bz) / np.where(az - bz == 0, 1e-09, az - bz), 0.0)
        ax2, ay2, az2 = (ax + (bx - ax) * ta, ay + (by - ay) * ta, az + (bz - az) * ta)
        bx2, by2, bz2 = (bx + (ax - bx) * tb, by + (ay - by) * tb, bz + (az - bz) * tb)
        az2 = np.maximum(az2, n)
        bz2 = np.maximum(bz2, n)
        x0 = self.cx + self.focal * ax2 / az2
        y0 = self.cy - self.focal * ay2 / az2
        x1 = self.cx + self.focal * bx2 / bz2
        y1 = self.cy - self.focal * by2 / bz2
        return (x0, y0, x1, y1, az2, bz2, keep)

def orbit_cam(target, dist, yaw, pitch, fov, roll=0.0, shift=(0.0, 0.0)):
    t = np.asarray(target, float)
    pos = t + dist * np.array([math.sin(yaw) * math.cos(pitch), math.sin(pitch), math.cos(yaw) * math.cos(pitch)])
    return Cam(pos, t, fov, roll=roll, shift=shift)

def splat(buf, xs, ys, vals):
    """Bilinear additive splat via bincount (fast for many points)."""
    h, w = buf.shape
    xs = np.asarray(xs, np.float64).ravel()
    ys = np.asarray(ys, np.float64).ravel()
    vals = np.broadcast_to(np.asarray(vals, np.float64), xs.shape).ravel()
    ok = (xs >= 0) & (ys >= 0) & (xs < w - 1) & (ys < h - 1) & (vals > 1e-06)
    if not ok.any():
        return
    xs, ys, vals = (xs[ok], ys[ok], vals[ok])
    x0 = np.floor(xs).astype(np.int64)
    y0 = np.floor(ys).astype(np.int64)
    fx = xs - x0
    fy = ys - y0
    idx = y0 * w + x0
    n = h * w
    acc = np.bincount(idx, vals * (1 - fx) * (1 - fy), minlength=n)
    acc += np.bincount(idx + 1, vals * fx * (1 - fy), minlength=n)
    acc += np.bincount(idx + w, vals * (1 - fx) * fy, minlength=n)
    acc += np.bincount(idx + w + 1, vals * fx * fy, minlength=n)
    buf += acc.reshape(h, w).astype(buf.dtype)

def segment_samples(x0, y0, x1, y1, v0, v1, width=1.0, step=0.5, extra=None):
    """Sample 2D segments into points. v0/v1: value per unit length at each end (interpolated).
    width: per-segment line width in px (>1 adds parallel offset copies).
    extra: optional per-segment arrays to carry along (returned per sample)."""
    x0 = np.asarray(x0, np.float64)
    y0 = np.asarray(y0, np.float64)
    x1 = np.asarray(x1, np.float64)
    y1 = np.asarray(y1, np.float64)
    N = x0.size
    v0 = np.broadcast_to(np.asarray(v0, np.float64), (N,))
    v1 = np.broadcast_to(np.asarray(v1, np.float64), (N,))
    width = np.broadcast_to(np.asarray(width, np.float64), (N,))
    dx, dy = (x1 - x0, y1 - y0)
    L = np.hypot(dx, dy)
    good = (L < 6000) & np.isfinite(L)
    n = np.where(good, np.maximum(1, np.ceil(L / step)), 0).astype(np.int64)
    tot = int(n.sum())
    if tot == 0:
        e = np.zeros(0)
        return (e, e, e, [] if extra is None else [np.zeros(0, a.dtype) for a in extra])
    sid = np.repeat(np.arange(N), n)
    starts = np.cumsum(n) - n
    k = np.arange(tot) - np.repeat(starts, n)
    t = (k + 0.5) / n[sid]
    xs = x0[sid] + dx[sid] * t
    ys = y0[sid] + dy[sid] * t
    seglen = L[sid] / n[sid]
    vals = (v0[sid] + (v1[sid] - v0[sid]) * t) * seglen
    ws = width[sid]
    ext = [] if extra is None else [np.asarray(a)[sid] for a in extra]
    thick = ws > 1.25
    vals = np.where(thick, vals, vals * np.minimum(ws, 1.0))
    if thick.any():
        nx = -dy[sid] / np.maximum(L[sid], 1e-09)
        ny = dx[sid] / np.maximum(L[sid], 1e-09)
        ti = np.nonzero(thick)[0]
        m = np.ceil(ws[ti]).astype(np.int64)
        reps = m - 1
        rid = np.repeat(ti, reps)
        j = np.arange(int(reps.sum())) - np.repeat(np.cumsum(reps) - reps, reps) + 1
        mm = np.repeat(m, reps)
        off = (j / (mm - 1) - 0.5) * (np.repeat(ws[ti], reps) - 1.0)
        off0 = -0.5 * (ws[ti] - 1.0)
        cx_, cy_ = (xs[rid].copy(), ys[rid].copy())
        xs[ti] += nx[ti] * off0
        ys[ti] += ny[ti] * off0
        vals[ti] *= ws[ti] / m
        xs = np.concatenate([xs, cx_ + nx[rid] * off])
        ys = np.concatenate([ys, cy_ + ny[rid] * off])
        vals = np.concatenate([vals, vals[rid]])
        ext = [np.concatenate([a, a[rid]]) for a in ext]
    return (xs, ys, vals, ext)

def splat_segments(buf, x0, y0, x1, y1, v0, v1=None, width=1.0, step=0.5):
    if v1 is None:
        v1 = v0
    xs, ys, vals, _ = segment_samples(x0, y0, x1, y1, v0, v1, width, step)
    splat(buf, xs, ys, vals)

def circle_segments(cx, cy, r, n=24):
    a = np.linspace(0, 2 * np.pi, n + 1)
    xs = cx + r * np.cos(a)
    ys = cy + r * np.sin(a)
    return (xs[:-1], ys[:-1], xs[1:], ys[1:])

def box_blur(a, r, axis):
    c = np.cumsum(np.pad(a, [(r + 1, r) if i == axis else (0, 0) for i in range(a.ndim)], mode='edge'), axis=axis)
    n = a.shape[axis]
    hi = np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis)
    lo = np.take(c, np.arange(0, n), axis=axis)
    return (hi - lo) / (2 * r + 1)

def blur(a, r=1, passes=1):
    for _ in range(passes):
        a = box_blur(box_blur(a, r, 0), r, 1)
    return a
DISK3 = np.array([[0.35, 0.8, 0.35], [0.8, 1.0, 0.8], [0.35, 0.8, 0.35]], np.float32)

def dilate(buf, k=DISK3):
    out = np.zeros_like(buf)
    r = k.shape[0] // 2
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            wgt = k[dy + r, dx + r]
            if wgt == 0:
                continue
            ys = slice(max(0, dy), buf.shape[0] + min(0, dy))
            yd = slice(max(0, -dy), buf.shape[0] + min(0, -dy))
            xs = slice(max(0, dx), buf.shape[1] + min(0, dx))
            xd = slice(max(0, -dx), buf.shape[1] + min(0, -dx))
            out[ys, xs] += wgt * buf[yd, xd]
    return out

def blit_scaled(buf, m, x, y, val=1.0):
    """Additive blit of a mask at integer position (clipped)."""
    h, w = m.shape
    x, y = (int(round(x)), int(round(y)))
    x0, y0 = (max(0, x), max(0, y))
    x1, y1 = (min(buf.shape[1], x + w), min(buf.shape[0], y + h))
    if x1 <= x0 or y1 <= y0 or val <= 0:
        return
    buf[y0:y1, x0:x1] += val * m[y0 - y:y1 - y, x0 - x:x1 - x]
_O = [(1, 0), (0, 1), (0, 5), (1, 6), (3, 6), (4, 5), (4, 1), (3, 0), (1, 0)]
_P = [(0, 0), (0, 6), (3, 6), (4, 5), (4, 4), (3, 3), (0, 3)]
GLYPHS = {'A': [[(0, 0), (2, 6), (4, 0)], [(0.7, 2), (3.3, 2)]], 'B': [[(0, 0), (0, 6), (3, 6), (4, 5), (4, 4), (3, 3), (0, 3)], [(3, 3), (4, 2), (4, 1), (3, 0), (0, 0)]], 'C': [[(4, 5), (3, 6), (1, 6), (0, 5), (0, 1), (1, 0), (3, 0), (4, 1)]], 'D': [[(0, 0), (0, 6), (2.5, 6), (4, 4.5), (4, 1.5), (2.5, 0), (0, 0)]], 'E': [[(4, 6), (0, 6), (0, 0), (4, 0)], [(0, 3), (3, 3)]], 'F': [[(4, 6), (0, 6), (0, 0)], [(0, 3), (3, 3)]], 'G': [[(4, 5), (3, 6), (1, 6), (0, 5), (0, 1), (1, 0), (3, 0), (4, 1), (4, 3), (2.5, 3)]], 'H': [[(0, 0), (0, 6)], [(4, 0), (4, 6)], [(0, 3), (4, 3)]], 'I': [[(1, 6), (3, 6)], [(2, 6), (2, 0)], [(1, 0), (3, 0)]], 'J': [[(4, 6), (4, 1), (3, 0), (1, 0), (0, 1)]], 'K': [[(0, 0), (0, 6)], [(4, 6), (0, 2)], [(1.3, 3.3), (4, 0)]], 'L': [[(0, 6), (0, 0), (4, 0)]], 'M': [[(0, 0), (0, 6), (2, 3), (4, 6), (4, 0)]], 'N': [[(0, 0), (0, 6), (4, 0), (4, 6)]], 'O': [_O], 'P': [_P], 'Q': [_O, [(2.5, 1.5), (4, -0.3)]], 'R': [_P, [(2, 3), (4, 0)]], 'S': [[(4, 5), (3, 6), (1, 6), (0, 5), (0, 4), (1, 3), (3, 3), (4, 2), (4, 1), (3, 0), (1, 0), (0, 1)]], 'T': [[(0, 6), (4, 6)], [(2, 6), (2, 0)]], 'U': [[(0, 6), (0, 1), (1, 0), (3, 0), (4, 1), (4, 6)]], 'V': [[(0, 6), (2, 0), (4, 6)]], 'W': [[(0, 6), (1, 0), (2, 4), (3, 0), (4, 6)]], 'X': [[(0, 0), (4, 6)], [(0, 6), (4, 0)]], 'Y': [[(0, 6), (2, 3), (4, 6)], [(2, 3), (2, 0)]], 'Z': [[(0, 6), (4, 6), (0, 0), (4, 0)]], '0': [_O, [(0.6, 1.0), (3.4, 5.0)]], '1': [[(1, 5), (2, 6), (2, 0)], [(1, 0), (3, 0)]], '2': [[(0, 5), (1, 6), (3, 6), (4, 5), (4, 4), (0, 0), (4, 0)]], '3': [[(0, 5), (1, 6), (3, 6), (4, 5), (4, 4), (3, 3), (1.5, 3)], [(3, 3), (4, 2), (4, 1), (3, 0), (1, 0), (0, 1)]], '4': [[(3, 0), (3, 6), (0, 2), (4, 2)]], '5': [[(4, 6), (0, 6), (0, 3.5), (3, 3.5), (4, 2.5), (4, 1), (3, 0), (1, 0), (0, 1)]], '6': [[(3.5, 6), (1.5, 6), (0, 4), (0, 1), (1, 0), (3, 0), (4, 1), (4, 2.5), (3, 3.5), (0, 3.5)]], '7': [[(0, 6), (4, 6), (1.5, 0)]], '8': [[(1, 3), (0, 4), (0, 5), (1, 6), (3, 6), (4, 5), (4, 4), (3, 3), (1, 3), (0, 2), (0, 1), (1, 0), (3, 0), (4, 1), (4, 2), (3, 3)]], '9': [[(4, 2.5), (1, 2.5), (0, 3.5), (0, 5), (1, 6), (3, 6), (4, 5), (4, 1), (3, 0), (1, 0)]], '.': [[(1.8, 0), (2.2, 0), (2.2, 0.4), (1.8, 0.4), (1.8, 0)]], ',': [[(2.2, 0.4), (2.2, 0), (1.6, -1)]], '·': [[(1.8, 2.8), (2.2, 2.8), (2.2, 3.2), (1.8, 3.2), (1.8, 2.8)]], '×': [[(0.8, 1.2), (3.2, 3.6)], [(0.8, 3.6), (3.2, 1.2)]], '-': [[(1, 3), (3, 3)]], '_': [[(0, -0.6), (4, -0.6)]], '/': [[(0, 0), (4, 6)]], '&': [[(4, 0), (1, 4.5), (1, 5.5), (1.8, 6), (2.6, 5.5), (2.6, 4.5), (0, 2), (0, 1), (1, 0), (2.5, 0), (4, 2)]], '+': [[(2, 1), (2, 5)], [(0, 3), (4, 3)]], ':': [[(2, 1), (2, 1.4)], [(2, 4), (2, 4.4)]], '(': [[(2.5, 6.5), (1.5, 5), (1.5, 1), (2.5, -0.5)]], ')': [[(1.5, 6.5), (2.5, 5), (2.5, 1), (1.5, -0.5)]], '<': [[(4, 5), (0, 3), (4, 1)]], '>': [[(0, 5), (4, 3), (0, 1)]], '=': [[(0.5, 2), (3.5, 2)], [(0.5, 4), (3.5, 4)]], '|': [[(2, -0.5), (2, 6.5)]], '→': [[(0, 3), (4, 3)], [(2.6, 4.4), (4, 3), (2.6, 1.6)]], '↑': [[(2, 0), (2, 6)], [(0.6, 4.6), (2, 6), (3.4, 4.6)]], '%': [[(0, 0), (4, 6)], [(0.5, 5), (1, 5.5), (1.5, 5), (1, 4.5), (0.5, 5)], [(2.5, 1), (3, 1.5), (3.5, 1), (3, 0.5), (2.5, 1)]], "'": [[(2, 6), (2, 4.6)]], ' ': []}

def text_strokes(s: str, cap: float, x0: float=0.0, y0: float=0.0, align: str='left', track: float=1.35):
    """Return (N,2,2) segments of a string in local 2D coords (y up), baseline at y0, cap height `cap`."""
    sc = cap / 6.0
    adv = (4 + track) * sc
    width = len(s) * adv - track * sc
    if align == 'center':
        x0 = x0 - width / 2
    elif align == 'right':
        x0 = x0 - width
    segs = []
    for i, ch in enumerate(s.upper()):
        g = GLYPHS.get(ch)
        if g is None:
            g = GLYPHS['·']
        ox = x0 + i * adv
        for stroke in g:
            for (ax, ay), (bx, by) in zip(stroke[:-1], stroke[1:]):
                segs.append(((ox + ax * sc, y0 + ay * sc), (ox + bx * sc, y0 + by * sc)))
    if not segs:
        return np.zeros((0, 2, 2))
    return np.array(segs, float)

def text_width(s: str, cap: float, track: float=1.35) -> float:
    sc = cap / 6.0
    return len(s) * (4 + track) * sc - track * sc
