"""r5, interlude 1 (REVISE_R4_20261004.md §3.1, D34; round 2 D35): Qwen's tower (inside/tower.py, TowerB9) on the beat.

The content is TowerB9's (her persona and her eight files pour into EMBED, the band climbs the 64-block stack to
HEAD, an empty slot waits under her name); only the time changes.

Round 2 (D35, sample_r5/README.md §4 R-A: "stop exactly on a node, and keep something going inside it"):

  - every move of the band, the camera and the orbit eases IN and lands on its event (beatmap.arrive): on the
    synth's stabs up to bar 46, then on the 16ths of bar 46; the node it lands on is a block (EMBED, L1, L2, L64,
    HEAD), a group of the 61-block stack, or, on bar 47's downbeat (82.13), the empty slot;
  - once it is on a node the node keeps moving at the rate of the harmony (i5_times.phase, the integral of
    beatmap.pad): her blue runs up the band's nine lines through the node's layers; in a block its attention is
    read a stretch at a time and its MLP's units light one after another; in a group of the stack its blocks are
    read one by one upward; the ruler on the right steps through the node's layers;
  - the camera never stands still: it lands with the band and drifts slowly (yaw) and breathes (distance) at the
    rate of the harmony;
  - a bar's downbeat lights the node the band stands on, not the whole tower (i5_times.node_flash, accent tiers);
  - before the band goes in (75.25-76.2) the node is EMBED: a point runs down each source's leader into it.

The plate is clipped to the forward pane's inside (3 px clear of its border, R-C).

Plates are cached in cache/i5_tower/<frame>.png:  python -m inside.i5_tower [--force] [--workers 2]
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import argparse
import math
import os
import sys
import time
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(PV_ROOT / 'runtime')):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import beatmap
import tl
from . import i5_times as I5
from .plate import PAPER, PLATE
from .tower import SOURCES, TowerB9, _fov, _lib
CACHE = ROOT / 'cache' / 'i5_tower'
T_IN = tl.QWEN_AT
T_TOP = tl.bar(47)
DRUMS = tl.bar(46)
FADE_END = T_TOP + 0.4
TRAVEL = 0.3
FWD = (110, 88, 1248, 598)
CLIP = (FWD[0] + 3 - PLATE[0], FWD[1] + 3 - PLATE[1], FWD[2] - 3 - PLATE[0], FWD[3] - 3 - PLATE[1])

def steps():
    """Step times: the cut, the stabs up to bar 46, then every 16th of bar 46 (82.02 is the last)."""
    st = [T_IN] + beatmap.events('stab', T_IN + 0.02, DRUMS - 0.02)
    st += beatmap.events('sixteenth', DRUMS - 0.01, T_TOP - 0.02)
    return st
STEPS = steps()
DOWNS = beatmap.events('down', T_IN - 0.01, FADE_END)
N_LABELS = 3
CLIMB = STEPS[N_LABELS:] + [T_TOP]
ORBIT = STEPS + [T_TOP]
_ORIG = {}

class TowerI5(TowerB9):

    def __init__(self):
        vp, g3 = self.vp, self.g3 = _lib()
        t0 = self.t0 = T_IN
        self.t_end = T_TOP
        S = dict(vp.build('parallel'))
        Lp = self.Lp = vp.PF_LAYOUT
        top = lambda key: float(Lp.find(key).base + Lp.find(key).h)
        y_e0, y_e1 = (Lp.y('E', 'bot'), top('E'))
        r_st = self.r_st = Lp.find(3)
        n_st = r_st.n
        plate = lambda j: float(r_st.base + vp.PL_PITCH * j)
        n_climb = len(STEPS) - N_LABELS
        n_stack = n_climb - 5
        k_stack = N_LABELS + 3
        n_slow = sum((1 for k in range(k_stack, k_stack + n_stack) if STEPS[k] < DRUMS - 0.01))
        n_fast = n_stack - n_slow
        half = n_st // 2
        cuts = [int(round(half * (g + 1) / max(1, n_slow))) for g in range(n_slow)] + [half + int(round((n_st - half) * (g + 1) / max(1, n_fast))) for g in range(n_fast)]
        heights = [y_e1, top(1), top(2)] + [plate(c) for c in cuts] + [top(64), Lp.y('H', 'bot') + 0.4]
        assert len(heights) == n_climb, (len(heights), n_climb)
        self.y_slot = Lp.y('H', 'sm')
        self.NODE_Y = np.array([y_e0] + heights + [self.y_slot])
        S['pf'] = vp.Lane(0, Lp, [(0.0, float(y_e0), None), (T_TOP - t0 + 0.6, float(self.y_slot), None)], band=True)
        tt = vp.TT
        ys = np.array([self.band_y(float(x) + t0) for x in tt])
        S['pf'].ys = ys
        S['pf']._fill()
        S['pf_end'] = T_TOP - t0 + 0.08
        S['cut'] = 1000000000.0
        S['lanes'], S['events'] = ([], [])
        inf = float('inf')
        dummy = dict(sm=inf, bars=[inf] * 4, win=inf, c0=inf, top=inf, land=inf)
        S['head'], S['land'] = ([dummy] * 3, [inf] * 3)
        S['lens'] = [[(lay, inf) for lay in vp.LENS_LAYERS] for _ in range(3)]
        S['confirm'] = [None] * 3
        S['mode'] = 'parallel'
        self.S = S
        self.label_at = [STEPS[k // 3] for k in range(len(SOURCES))]
        self.slot_at = T_TOP
        self.dur = FADE_END - t0 + 0.2
        self.layer_top = np.array([y_e1, top(1), top(2)] + [plate(j + 1) for j in range(n_st)] + [top(64), Lp.y('H', 'bot') + 0.4])
        vp.camera = self.camera
        vp.cam_state = self.cam_state
        vp.prefill_label = self.labels
        vp.overlays = self.overlays
        if not _ORIG:
            _ORIG.update(draw_block=vp.draw_block, draw_plate=vp.draw_plate, draw_lanes=vp.draw_lanes)
        vp.draw_block = self.draw_block
        vp.draw_plate = self.draw_plate
        vp.draw_lanes = self.draw_lanes
        tp = vp.tpl('B')
        self.read_sets = {}
        for kind in ('B', 'E', 'H'):
            tp = vp.tpl(kind)
            cls, trig = (tp['cls'], tp['trig'])
            hatch = np.nonzero(cls == 10)[0]
            if kind == 'B':
                hatch = hatch[np.abs(trig[hatch] + 1.75) < 1e-06]
            mid = 0.5 * (tp['a'][hatch, 0] + tp['b'][hatch, 0])
            self.read_sets[kind] = hatch[np.argsort(mid)]

    def node_at(self, ta):
        """(k, a): the band has landed on node k (0: EMBED's floor); a is beatmap.arrive's value (k + travel)."""
        a = beatmap.arrive(ta, CLIMB, TRAVEL)
        return (int(math.floor(a + 1e-09)), a)

    def band_y(self, ta):
        _k, a = self.node_at(ta)
        k = min(int(math.floor(a)), len(self.NODE_Y) - 1)
        if k >= len(self.NODE_Y) - 1:
            return float(self.NODE_Y[-1])
        return float(self.NODE_Y[k] + (self.NODE_Y[k + 1] - self.NODE_Y[k]) * (a - k))

    def node_span(self, ta):
        """(lo, hi) world heights of the node the band stands on (None before it goes in)."""
        k, _a = self.node_at(ta)
        if k <= 0:
            return None
        k = min(k, len(self.NODE_Y) - 1)
        return (float(self.NODE_Y[k - 1]), float(self.NODE_Y[k]))

    def node_layers(self, ta):
        """Indices (0 EMBED .. 65 HEAD) of the layers in the node the band stands on."""
        sp = self.node_span(ta)
        if sp is None:
            return []
        lo, hi = sp
        idx = [i for i, y in enumerate(self.layer_top) if lo + 0.001 < y <= hi + 0.001]
        if not idx:
            idx = [len(self.layer_top) - 1]
        return idx

    def phi(self, ta):
        return I5.phase(ta, 1)

    def flash_k(self, ta):
        """The node is lit on a bar's downbeat (accent 1.0) once the band stands on one."""
        return 0.85 * beatmap.flash(ta, DOWNS, half=0.14) if self.node_span(ta) is not None else 0.0

    def cam_state(self, S, t):
        return (self.band_y(t + self.t0) + 2.0, 28.0)

    def progress(self, t):
        """0..1 over the steps, each landing on its event (the orbit: pitch, yaw, distance, fov)."""
        return min(1.0, beatmap.arrive(t + self.t0, ORBIT, TRAVEL) / len(ORBIT))

    def camera(self, S, t, dfy=0.0):
        g3 = self.g3
        fy, _ = self.cam_state(S, t)
        fy += dfy
        u = self.progress(t)
        ph = self.phi(t + self.t0)
        pitch = 0.64 + (0.37 - 0.64) * u
        yaw = -0.66 + (-0.44 + 0.66) * u + 0.012 * ph
        dist = (31.0 + (26.0 - 31.0) * u) * (1 + 0.012 * math.sin(2 * math.pi * ph / 1.6))
        fov = _fov(38.0 + (34.0 - 38.0) * u)
        cam = g3.orbit_cam(np.array([0.3, fy, 0.0]), dist, yaw, pitch, fov, shift=(120.0, 0.0))
        cam.dist, cam.fy = (dist, fy)
        return cam

    def draw_block(self, S, t, lanes, r, cam, B, ID, rk, gw):
        _ORIG['draw_block'](S, t, lanes, r, cam, B, ID, rk, gw)
        vp = self.vp
        ta = t + self.t0
        sp = self.node_span(ta)
        if sp is None or r.kind == 'S':
            return
        if self.Lp.row_at_y(sp[1] - 0.05) is not r:
            return
        tp = vp.tpl(r.kind)
        a3, b3 = (vp.to_world(r, tp['a']), vp.to_world(r, tp['b']))
        ph = self.phi(ta)
        rs = self.read_sets[r.kind]
        if len(rs):
            c = ph * 2.2 % 1.0 * (len(rs) + 6) - 3
            dist = np.abs(np.arange(len(rs)) - c)
            sel = dist < 3.0
            if sel.any():
                vp.draw_segs(B, 'sig', cam, ID, rk, a3[rs[sel]], b3[rs[sel]], 0.95 * (1 - dist[sel] / 3.0), 1.1, gw)
        neu = tp['neu']
        if len(neu):
            st = ph * 14.0
            j = int(math.floor(st)) % len(neu)
            fr = st - math.floor(st)
            for jj, v in ((j, 1.0), ((j - 1) % len(neu), 0.55 * (1 - fr)), ((j - 2) % len(neu), 0.25 * (1 - fr))):
                vp.draw_segs(B, 'sig', cam, ID, rk, a3[neu[jj]][None], b3[neu[jj]][None], v, 1.6, gw)
        k = self.flash_k(ta)
        if k > 0.01:
            hot = tp['hot']
            vp.draw_segs(B, 'sig', cam, ID, rk, a3[hot], b3[hot], 0.8 * k, 1.2, gw)

    def draw_plate(self, t, lanes, r, j, cam, B, ID, rk, gw):
        _ORIG['draw_plate'](t, lanes, r, j, cam, B, ID, rk, gw)
        vp = self.vp
        ta = t + self.t0
        sp = self.node_span(ta)
        if sp is None:
            return
        lo, hi = sp
        yc = r.base + vp.PL_PITCH * (j + 0.5)
        if not lo - 0.001 < yc <= hi + 0.001:
            return
        j0 = int(round((lo - r.base) / vp.PL_PITCH))
        j1 = int(round((hi - r.base) / vp.PL_PITCH))
        span = max(1, j1 - j0)
        st = self.phi(ta) * 14.0
        cur = j0 + int(math.floor(st)) % span
        fr = st - math.floor(st)
        v = 0.0
        if j == cur:
            v = 1.0
        elif j == cur - 1 or (cur == j0 and j == j1 - 1 and (span > 2)):
            v = 0.45 * (1 - fr)
        v = max(v, 0.7 * self.flash_k(ta))
        if v <= 0.01:
            return
        y = vp.PL_PITCH * (j + 0.5)
        rect = np.array([[-vp.HX, y - vp.PL_HALF], [vp.HX, y - vp.PL_HALF], [vp.HX, y + vp.PL_HALF], [-vp.HX, y + vp.PL_HALF]])
        a3 = vp.stack_world(r, rect)
        b3 = vp.stack_world(r, np.roll(rect, -1, axis=0))
        vp.draw_segs(B, 'sig', cam, ID, rk, a3, b3, v, 1.1, gw)

    def draw_lanes(self, S, t, layout, rows, lanes, cam, B, gw):
        _ORIG['draw_lanes'](S, t, layout, rows, lanes, cam, B, gw)
        vp = self.vp
        ta = t + self.t0
        sp = self.node_span(ta)
        if sp is None:
            return
        lo = sp[0]
        hi = max(sp[1], self.band_y(ta))
        if hi - lo < 0.2:
            return
        ph = self.phi(ta)
        k_fl = self.flash_k(ta)
        L = min(2.2, 0.35 * (hi - lo))
        for i, off in enumerate(self.S['pf'].offsets):
            for m in (0.0, 0.5):
                u = (ph * 1.6 + 0.23 * i + m) % 1.0
                yh = lo + u * (hi - lo + L)
                ya, yb = (max(lo, yh - L), min(hi, yh))
                if yb - ya < 0.06:
                    continue
                self._line_up(layout, cam, B, gw, off, ya, yb, (0.35, 1.0))
            if k_fl > 0.01:
                self._line_up(layout, cam, B, gw, off, lo, hi, (0.6 * k_fl, 0.6 * k_fl))
        _ = vp

    def _line_up(self, layout, cam, B, gw, off, ya, yb, vals):
        vp = self.vp
        ys = np.arange(ya, yb + 1e-06, 0.06)
        if ys.size < 2:
            ys = np.array([ya, yb])
        rows = [layout.row_at_y(y) for y in ys]
        ridx = np.array([layout.rows.index(r) for r in rows])
        pts = np.zeros((ys.size, 3))
        for k in np.unique(ridx):
            sel = ridx == k
            pts[sel] = vp.row_point(layout.rows[k], vp.MX + off, ys[sel])
        same = (ridx[:-1] == ridx[1:]).astype(float)
        v = np.linspace(vals[0], vals[1], ys.size - 1) * same
        vp.draw_segs(B, 'sig', cam, None, 0, pts[:-1], pts[1:], v, 1.0, gw)

    def labels(self, S, t, cam, T2):
        vp, g3 = (self.vp, self.g3)
        Lp = vp.PF_LAYOUT
        r = Lp.find('E')
        offs = list(np.linspace(-0.42, 0.42, 9))
        foot = [vp.row_point(r, vp.MX + o, np.array([r.base + 0.05]))[0] for o in offs]
        anchor = vp.row_point(r, -vp.HX - 1.6, np.array([r.base + 2.6]))[0]
        ax, ay, az = cam.project(anchor[None, :])
        if az[0] < 0.5:
            return
        ta = t + self.t0
        ph = self.phi(ta)
        inside = self.node_span(ta) is None
        for k, (key, name, hers) in enumerate(SOURCES):
            if ta < self.label_at[k]:
                break
            a = float(g3.smooth((ta - self.label_at[k]) / 0.06))
            m = vp.tmask(name, 15, 'mono' if hers else 'cjk')
            x = ax[0] - m.shape[1] - 18
            y = ay[0] + (k - 4) * 19
            g3.blit_scaled(T2['blue' if hers else 'text'], m, x, y - m.shape[0] / 2, a * (0.8 if hers else 0.95))
            fx, fy, _ = cam.project(foot[k][None, :])
            n = 60
            grow = float(1 - (1 - min(1.0, (ta - self.label_at[k]) / 0.14)) ** 3)
            u = np.linspace(0, 1, n) * grow
            xs = ax[0] - 10 + (fx[0] - ax[0] + 10) * u
            ys = y + (fy[0] - y) * u ** 2
            g3.splat_segments(T2['blue' if hers else 'ash'], xs[:-1], ys[:-1], xs[1:], ys[1:], 0.55 * a, None, 0.8)
            if inside and grow >= 1.0:
                q = (ph * 2.4 + 0.11 * k) % 1.0
                i1 = int(q * (n - 1))
                i0 = max(0, i1 - 6)
                if i1 > i0:
                    g3.splat_segments(T2['blue' if hers else 'text'], xs[i0:i1], ys[i0:i1], xs[i0 + 1:i1 + 1], ys[i0 + 1:i1 + 1], 0.9 * a, None, 1.0)

    def overlays(self, S, t, T2):
        """TowerB9's header and slot (the slot opens on the downbeat in 0.06 s); the ruler on the right."""
        vp, g3 = (self.vp, self.g3)
        a = float(g3.smooth(t / 0.25))
        head = f'{self.qwen_name()} · LOCAL · 64 BLOCKS · PREFILL 9 SOURCES'
        eb = g3.text_strokes(head, 8.0, 24, 0)
        T2['strokes'].append((eb[:, :, 0], 22 - eb[:, :, 1], 0.6 * a))
        ta = t + self.t0
        self.ruler(ta, T2, a)
        if ta < self.slot_at:
            return
        r = vp.PF_LAYOUT.find('H')
        p = vp.row_point(r, vp.MX + 0.2, np.array([r.base + r.h + 0.6]))[0]
        cam = self.camera(S, t)
        sx, sy, sz = cam.project(p[None, :])
        a = float(g3.smooth((ta - self.slot_at) / 0.06))
        bw, bh = (30, 36)
        x0, y0 = (sx[0] + 14, sy[0] - bh - 18)
        for xa, ya, xb, yb in ((x0, y0, x0 + bw, y0), (x0 + bw, y0, x0 + bw, y0 + bh), (x0 + bw, y0 + bh, x0, y0 + bh), (x0, y0 + bh, x0, y0)):
            g3.splat_segments(T2['text'], np.array([xa]), np.array([ya]), np.array([xb]), np.array([yb]), a, None, 1.0)
        who = vp.tmask('大肥鱼 ›', 20, 'cjk')
        g3.blit_scaled(T2['text'], who, x0 - 12 - who.shape[1], y0 + bh / 2 - who.shape[0] / 2, 0.9 * a)
        g3.splat_segments(T2['text'], np.array([x0 + 6.0]), np.array([y0 + 7.0]), np.array([x0 + 6.0]), np.array([y0 + bh - 7.0]), a, None, 1.0)

    @staticmethod
    def qwen_name():
        """The local model's name from cast.py, upper case (the lettering has capitals only): QWEN3.8-27B."""
        import cast
        return cast.term('qwen').split(' · ')[0].upper()
    RULER_X, RULER_Y0, RULER_Y1 = (1088, 466, 76)

    def ruler(self, ta, T2, a):
        """66 ticks, EMBED to HEAD: the layers her band has passed in her quiet blue, the node it stands on brighter,
        and a cursor stepping through the node's layers (14 a unit of the inner clock) with its layer's name."""
        g3 = self.g3
        n = len(self.layer_top)
        x = self.RULER_X
        pitch = (self.RULER_Y0 - self.RULER_Y1) / (n - 1)
        by = self.band_y(ta)
        node = self.node_layers(ta)
        cur = None
        if node:
            st = self.phi(ta) * 14.0
            cur = node[int(math.floor(st)) % len(node)]
        for i in range(n):
            y = self.RULER_Y0 - i * pitch
            passed = self.layer_top[i] <= by + 0.001
            if i == cur:
                g3.splat_segments(T2['blue'], np.array([x - 10.0]), np.array([y]), np.array([x + 10.0]), np.array([y]), 1.0 * a, None, 1.0)
            elif i in node:
                g3.splat_segments(T2['blue'], np.array([x - 4.0]), np.array([y]), np.array([x + 6.0]), np.array([y]), 0.75 * a, None, 1.0)
            elif passed:
                g3.splat_segments(T2['blue'], np.array([x]), np.array([y]), np.array([x + 6.0]), np.array([y]), 0.4 * a, None, 1.0)
            else:
                g3.splat_segments(T2['ash'], np.array([x]), np.array([y]), np.array([x + 6.0]), np.array([y]), 0.45 * a, None, 1.0)
        for s, y in (('EMBED', self.RULER_Y0), ('HEAD', self.RULER_Y1)):
            m = self.vp.tmask(s, 9, 'mono')
            g3.blit_scaled(T2['ash'], m, x + 12, y - m.shape[0] / 2, 0.8 * a)
        if cur is not None and 0 < cur < n - 1:
            name = f'L.{cur:03d}'
            m = self.vp.tmask(name, 9, 'mono')
            y = self.RULER_Y0 - cur * pitch
            g3.blit_scaled(T2['text'], m, x - 16 - m.shape[1], y - m.shape[0] / 2, 0.9 * a)

    def render(self, t):
        arr = self.vp.frame(self.S, max(0.0, t - self.t0), 'paper').copy()
        x0, y0, x1, y1 = CLIP
        paper = np.array(PAPER, np.uint8)
        arr[:max(0, y0)] = paper
        arr[y1:] = paper
        arr[:, :max(0, x0)] = paper
        arr[:, x1:] = paper
        return arr

def frames(fps=24):
    return range(int(math.ceil(T_IN * fps - 1e-06)), int(math.ceil(FADE_END * fps - 1e-06)))

def path(n):
    return CACHE / f'{n:05d}.png'
_R = None

def _init():
    global _R
    _R = TowerI5()

def _one(n):
    from PIL import Image
    arr = _R.render(n / 24)
    f = path(n)
    tmp = f.with_suffix('.tmp.png')
    Image.fromarray(arr).save(tmp)
    os.replace(tmp, f)
    return n

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--workers', type=int, default=2)
    ap.add_argument('--only', type=int, nargs='*')
    a = ap.parse_args()
    CACHE.mkdir(parents=True, exist_ok=True)
    todo = [n for n in frames() if (a.force or not path(n).exists()) and (not a.only or n in a.only)]
    t0 = time.time()
    from multiprocessing import Pool
    with Pool(min(a.workers, max(1, len(todo))), initializer=_init) as pool:
        for _ in pool.imap_unordered(_one, todo, chunksize=2):
            pass
    print(f'i5_tower: {len(todo)} frames in {time.time() - t0:.1f} s -> {CACHE}')
if __name__ == '__main__':
    main()
