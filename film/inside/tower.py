"""B9: the local Qwen's tower, loaded with her (ARRANGE_20261003 §2-§3, BUILD_V2 §3).

inside_lab/v7_blueprint_parallel.py's prefill only, slowed to four bars and rendered at the plate's size: you pick
the local Qwen on bar 43 (hard cut, R9); during that bar her persona and her eight files pour into EMBED one
per eighth note (nine names, nine lines of the band); the band climbs one stage per bar or half bar (L1, L2, the
61-block stack, L64) with the camera; on bar 46 beat 3 it reaches HEAD and stops at an empty slot under her
name, waiting for your question (C1). Nothing is generated here: no lanes, no reads, no lens.

The v7 module is used as a library: its schedule dict S gets this prefill band and an empty generation, and its
camera, overlays and prefill label are replaced (module attributes, set when the renderer is built).
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
import sys
from pathlib import Path
import numpy as np
import tl
from .plate import PH, PW
LAB = Path(__file__).resolve().parents[1] / 'inside_lab'
INF = float('inf')
SOURCES = [('persona', '你是大肥鱼…', False)] + [(n, n + '.md', True) for n in tl.HER_FILES]

def _lib():
    if str(LAB) not in sys.path:
        sys.path.insert(0, str(LAB))
    import lab3d as g3
    import v7_blueprint_parallel as vp
    vp.W, vp.H = (PW, PH)
    g3.W, g3.H = (PW, PH)
    d = list(g3.Cam.__init__.__defaults__)
    d[1], d[2] = (PW, PH)
    g3.Cam.__init__.__defaults__ = tuple(d)
    return (vp, g3)

def _fov(f720):
    """The vertical fov that gives v7's pixel scale x 0.897 (its frame cropped to the plate's aspect)."""
    return math.degrees(2 * math.atan(math.tan(math.radians(f720) / 2) * (PH / 0.897) / 720.0))

class TowerB9:

    def __init__(self, t0, t_end):
        vp, g3 = self.vp, self.g3 = _lib()
        self.t0, self.t_end = (t0, t_end)
        bar = lambda b, k=0: tl.bar(b, k) - t0
        S = dict(vp.build('parallel'))
        Lp = vp.PF_LAYOUT
        top = lambda key: float(Lp.find(key).base + Lp.find(key).h)
        keys = [(bar(43, 0) + 0.18, 'E', 'bot'), (bar(44), top('E')), (bar(44, 2), top(1)), (bar(45), top(2)), (bar(46), top(3)), (bar(46, 2), top(64)), (bar(46, 3), 'H', 'sm')]
        keys = [k if len(k) == 3 else (k[0], k[1], None) for k in keys]
        S['pf'] = vp.Lane(0, Lp, keys, band=True)
        S['pf_end'] = keys[-1][0]
        S['cut'] = 1000000000.0
        S['lanes'], S['events'] = ([], [])
        dummy = dict(sm=INF, bars=[INF] * 4, win=INF, c0=INF, top=INF, land=INF)
        S['head'], S['land'] = ([dummy] * 3, [INF] * 3)
        S['lens'] = [[(lay, INF) for lay in vp.LENS_LAYERS] for _ in range(3)]
        S['confirm'] = [None] * 3
        S['mode'] = 'parallel'
        self.S = S
        self.label_at = [bar(43) + k * (bar(44) - bar(43)) / 8 for k in range(9)]
        self.slot_at = bar(46, 3)
        self.dur = t_end - t0 + 0.6
        ts = np.arange(0.0, self.dur, 1 / 240)
        pf = S['pf']
        fy = np.array([pf.y_at(min(t, S['pf_end'])) for t in ts]) + 2.0
        fy = np.where(np.isnan(fy), Lp.y('E', 'center'), fy)
        k = 1 - math.exp(-(1 / 240) / 0.12)
        for _ in range(2):
            acc = fy[0]
            for i in range(ts.size):
                acc += (fy[i] - acc) * k
                fy[i] = acc
        self.cam_ts, self.cam_fy = (ts, fy)
        vp.camera = self.camera
        vp.cam_state = self.cam_state
        vp.prefill_label = self.labels
        vp.overlays = self.overlays

    def cam_state(self, S, t):
        return (float(np.interp(t, self.cam_ts, self.cam_fy)), 28.0)

    def camera(self, S, t, dfy=0.0):
        g3 = self.g3
        fy, _ = self.cam_state(S, t)
        fy += dfy
        u = float(g3.in_out_cubic(np.clip(t / max(0.001, self.slot_at), 0, 1)))
        pitch = 0.64 + (0.37 - 0.64) * u
        yaw = -0.66 + (-0.44 + 0.66) * u
        dist = 31.0 + (26.0 - 31.0) * u
        fov = _fov(38.0 + (34.0 - 38.0) * u)
        cam = g3.orbit_cam(np.array([0.3, fy, 0.0]), dist, yaw, pitch, fov, shift=(120.0, 0.0))
        cam.dist, cam.fy = (dist, fy)
        return cam

    def labels(self, S, t, cam, T2):
        """Her persona and her eight files pour into EMBED, one per eighth note of bar 43, each with a fine leader
        to its line of the band (the lines enter at EMBED's floor). They ride with the tower as the camera rises."""
        vp, g3 = (self.vp, self.g3)
        Lp = vp.PF_LAYOUT
        r = Lp.find('E')
        offs = list(np.linspace(-0.42, 0.42, 9))
        foot = [vp.row_point(r, vp.MX + o, np.array([r.base + 0.05]))[0] for o in offs]
        anchor = vp.row_point(r, -vp.HX - 1.6, np.array([r.base + 2.6]))[0]
        ax, ay, az = cam.project(anchor[None, :])
        if az[0] < 0.5:
            return
        for k, (key, name, hers) in enumerate(SOURCES):
            if t < self.label_at[k]:
                break
            a = float(g3.smooth((t - self.label_at[k]) / 0.12))
            m = vp.tmask(name, 15, 'mono' if hers else 'cjk')
            x = ax[0] - m.shape[1] - 18
            y = ay[0] + (k - 4) * 19
            g3.blit_scaled(T2['blue' if hers else 'text'], m, x, y - m.shape[0] / 2, a * (0.8 if hers else 0.95))
            fx, fy, _ = cam.project(foot[k][None, :])
            n = 60
            u = np.linspace(0, 1, n) * float(g3.smooth((t - self.label_at[k]) / 0.3))
            xs = ax[0] - 10 + (fx[0] - ax[0] + 10) * u
            ys = y + (fy[0] - y) * u ** 2
            g3.splat_segments(T2['blue' if hers else 'ash'], xs[:-1], ys[:-1], xs[1:], ys[1:], 0.55 * a, None, 0.8)

    def overlays(self, S, t, T2):
        vp, g3 = (self.vp, self.g3)
        a = float(g3.smooth(t / 0.25))
        head = 'QWEN3.8-27B · LOCAL · 64 BLOCKS · PREFILL 9 SOURCES'
        eb = g3.text_strokes(head, 8.0, 24, 0)
        T2['strokes'].append((eb[:, :, 0], 22 - eb[:, :, 1], 0.6 * a))
        if t < self.slot_at:
            return
        r = vp.PF_LAYOUT.find('H')
        p = vp.row_point(r, vp.MX + 0.2, np.array([r.base + r.h + 0.6]))[0]
        cam = self.camera(S, t)
        sx, sy, sz = cam.project(p[None, :])
        a = float(g3.smooth((t - self.slot_at) / 0.2))
        bw, bh = (30, 36)
        x0, y0 = (sx[0] + 14, sy[0] - bh - 18)
        for xa, ya, xb, yb in ((x0, y0, x0 + bw, y0), (x0 + bw, y0, x0 + bw, y0 + bh), (x0 + bw, y0 + bh, x0, y0 + bh), (x0, y0 + bh, x0, y0)):
            g3.splat_segments(T2['text'], np.array([xa]), np.array([ya]), np.array([xb]), np.array([yb]), a, None, 1.3)
        who = vp.tmask('大肥鱼 ›', 20, 'cjk')
        g3.blit_scaled(T2['text'], who, x0 - 12 - who.shape[1], y0 + bh / 2 - who.shape[0] / 2, 0.9 * a)
        if (t - self.slot_at) % 1.06 < 0.53:
            g3.splat_segments(T2['text'], np.array([x0 + 6.0]), np.array([y0 + 7.0]), np.array([x0 + 6.0]), np.array([y0 + bh - 7.0]), a, None, 1.6)

    def render(self, t):
        return self.vp.frame(self.S, max(0.0, t - self.t0), 'paper')
