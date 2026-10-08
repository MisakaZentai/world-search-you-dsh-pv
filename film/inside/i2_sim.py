"""The gacha globe's capsules, simulated (r15 g2, sample_r15/README.md, D54): position-based dynamics, deterministic.

Circles in a circular glass under gravity. Each press of ↻ turns the agitator at the bottom: a swirl and a lift for
a little over half a second, then they fall back and settle, rolling (each capsule's angle follows its roll). Each
kick that is not a press gives them a little hop. On an answer the blue capsule nearest the chute leaves the globe;
when the copy comes back from memory a capsule drops in through the inlet at the top.

Coordinates are the globe's own (its centre at 0, 0; y down), px of the zoomed pane. Frames are the film's (24 fps
on the film's own clock), so a render at t = k / 24 reads frame k exactly; stills in between interpolate.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
import numpy as np
FPS = 24
SUB = 8
ITERS = 4
G = 1100.0
SWIRL, LIFT = (2100.0, 2000.0)
DAMP = 0.997
WALL_F = 0.93

class Sim:

    def __init__(self, R_in, r, n, t0, t1, presses, kicks, leaves, enters, seed=7):
        """R_in: the glass's inner radius; r: a capsule's; presses / kicks: times; leaves: [(t, pick)] where pick
        chooses which active capsule leaves (a function of positions and the active mask, returning an index or
        None); enters: [(t, index or a function giving it)] capsules coming back in through the inlet."""
        self.R, self.r, self.n = (R_in, r, n)
        self.t0, self.t1 = (t0, t1)
        rs = np.random.RandomState(seed)
        pts = []
        step = 2 * r + 0.4
        for row in range(30):
            y = R_in - r - 1 - row * step * 0.866
            for col in range(-14, 15):
                x = col * step + row % 2 * step / 2
                if math.hypot(x, y) < R_in - r - 0.5:
                    pts.append((x + rs.uniform(-0.3, 0.3), y))
            if len(pts) >= n:
                break
        self.x = np.array(pts[:n], np.float64)
        self.v = np.zeros_like(self.x)
        self.a = rs.uniform(0, 2 * math.pi, n)
        self.w = np.zeros(n)
        self.on = np.ones(n, bool)
        self.presses, self.kicks = (list(presses), list(kicks))
        self.leaves, self.enters = (sorted(leaves, key=lambda e: e[0]), sorted(enters, key=lambda e: e[0]))
        self.left = {}
        self.frames = {}
        self._run()

    def _stir(self, t):
        """The agitator: (swirl, lift) strengths at t."""
        s = 0.0
        for p in self.presses:
            u = t - p
            if 0 <= u < 0.5:
                env = min(1.0, u / 0.06) * (1 - max(0.0, (u - 0.16) / 0.34)) ** 2
                s = max(s, env)
        return s

    def _step(self, t, dt):
        x, v = (self.x, self.v)
        on = self.on
        acc = np.zeros_like(x)
        acc[:, 1] += G
        s = self._stir(t)
        if s > 0:
            d = np.hypot(x[:, 0], x[:, 1]) + 1e-06
            tang = np.stack([-x[:, 1], x[:, 0]], 1) / d[:, None]
            acc += SWIRL * s * tang * (0.3 + 0.7 * d[:, None] / self.R)
            low = np.clip((x[:, 1] + 0.1 * self.R) / (0.9 * self.R), 0, 1)
            acc[:, 1] -= LIFT * s * low
        v += acc * dt
        v *= DAMP
        prev = x.copy()
        x += v * dt
        r2 = 2 * self.r
        idx = np.where(on)[0]
        for _ in range(ITERS):
            xs = x[idx]
            dif = xs[:, None, :] - xs[None, :, :]
            dist = np.sqrt((dif ** 2).sum(-1)) + 1e-09
            ov = r2 - dist
            np.fill_diagonal(ov, 0)
            ov = np.clip(ov, 0, None)
            push = (0.5 * ov / dist)[..., None] * dif
            corr = push.sum(1) / np.maximum(1, (ov > 0).sum(1))[:, None] * 1.6
            xs = xs + corr
            d = np.hypot(xs[:, 0], xs[:, 1])
            lim = self.R - self.r
            out = d > lim
            xs[out] *= (lim / d[out])[:, None]
            x[idx] = xs
        v[idx] = (x[idx] - prev[idx]) / dt
        xs, vs = (x[idx], v[idx])
        d = np.hypot(xs[:, 0], xs[:, 1]) + 1e-09
        touch = d > self.R - self.r - 0.6
        if touch.any():
            nrm = xs[touch] / d[touch, None]
            vn = (vs[touch] * nrm).sum(1, keepdims=True) * nrm
            vs[touch] = vn + (vs[touch] - vn) * WALL_F
            v[idx] = vs
        self.w[idx] = 0.9 * self.w[idx] + 0.1 * (v[idx, 0] / self.r)
        self.a[idx] += self.w[idx] * dt

    def _press(self, t, k):
        """The agitator's first sweep: every capsule in the pile gets a knock of its own (they scatter and roll)."""
        rs = np.random.RandomState(1000 + k)
        h = np.clip((self.x[:, 1] + 0.3 * self.R) / (1.3 * self.R), 0, 1)
        kick = np.stack([rs.uniform(-150, 150, self.n), -rs.uniform(80, 330, self.n) * h], 1)
        self.v[self.on] += kick[self.on]
        self.w[self.on] += rs.uniform(-25, 25, self.n)[self.on]

    def _kick(self, t):
        h = np.clip((self.x[:, 1] + 0.2 * self.R) / (1.2 * self.R), 0, 1)
        self.v[self.on, 1] -= (90.0 * (0.5 + 0.5 * h))[self.on]

    def _run(self):
        n_frames = int(round((self.t1 - self.t0) * FPS)) + 1
        dt = 1.0 / FPS / SUB
        kq = [k for k in self.kicks if not any((abs(k - p) < 0.02 for p in self.presses))]
        li, ei, ki, pi = (0, 0, 0, 0)
        t = self.t0
        for f in range(n_frames):
            tf = self.t0 + f / FPS
            for _s in range(SUB):
                while pi < len(self.presses) and self.presses[pi] <= t:
                    self._press(t, pi)
                    pi += 1
                while ki < len(kq) and kq[ki] <= t:
                    self._kick(t)
                    ki += 1
                while li < len(self.leaves) and self.leaves[li][0] <= t:
                    j = self.leaves[li][1](self.x, self.on)
                    if j is not None:
                        self.left[j] = (self.leaves[li][0], self.x[j].copy(), float(self.a[j]))
                        self.on[j] = False
                    li += 1
                while ei < len(self.enters) and self.enters[ei][0] <= t:
                    j = self.enters[ei][1]
                    j = j() if callable(j) else j
                    if j is None:
                        ei += 1
                        continue
                    self.on[j] = True
                    self.x[j] = (0.0, -self.R + self.r + 1.0)
                    self.v[j] = (0.0, 160.0)
                    ei += 1
                self._step(t, dt)
                t += dt
            self.frames[f] = (self.x.copy(), self.a.copy(), self.on.copy(), tf)

    def at(self, t):
        """(positions, angles, active) at t, interpolated between frames."""
        u = (t - self.t0) * FPS
        f0 = int(math.floor(u))
        f0 = max(0, min(f0, len(self.frames) - 1))
        f1 = min(f0 + 1, len(self.frames) - 1)
        k = min(1.0, max(0.0, u - f0))
        x0, a0, on0, _ = self.frames[f0]
        if k < 1e-06 or f1 == f0:
            return (x0, a0, on0)
        x1, a1, on1, _ = self.frames[f1]
        return (x0 + (x1 - x0) * k, a0 + (a1 - a0) * k, on0 & on1)
