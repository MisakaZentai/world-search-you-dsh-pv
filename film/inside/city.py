"""E and G5: the city of towers (inside_lab/v13_city.py), driven by the film (ARRANGE_20261003 §2-§3).

Every tower is a session wearing her name: one machine, one set of weights, a pass climbing per step, blank cards
on the roof for the replies nobody else sees (v13). The plate sits in the left terminal while the dsh window
stays on the right, so the two sides stay linked as in the first cut (E1/E2' one session per syllable on the
right, one tower lit per syllable here; G5 one session closed on the right, one block of towers dark here).

  E    179.64-182.47 and 186.30-192.96: the wide city, mostly idle; on each sung syllable of "I'm searching ..."
       one more tower lights (its first pass is a prefill band: her context, blue, poured into another machine)
       and gets a nameplate 大肥鱼 · <model> (the model is the session that appears on the right at the same
       syllable, ui/pages/e.NEW); the rest light while the left shows the cells (E2), the last ones in a wave on
       E2'; on "But" the camera moves in on one lit tower whose nameplate rolls like the reel on the right and
       stops on trans-for-ming, never on her.
  G5   260.88-273.39: from close to the merged one's tower the camera pulls back over the city; each of your
       nine closes darkens one ninth of the city; at the end only the merged one is lit.

The v13 module is used as a library (its sizes, camera, overlays and her tower's special status are replaced when
the renderer is built; one plate size per process).
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
import sys
from pathlib import Path
import numpy as np
import cast
import syl
import tl
ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / 'inside_lab'
TAU0 = 30.0
SPLIT = (100, 84, 768, 596)

def _lib(w, h):
    for p in (str(LAB), str(ROOT / 'ui')):
        if p not in sys.path:
            sys.path.insert(0, p)
    import lab3d as g3
    import v7_blueprint_parallel as vp
    import v13_city as vc
    vp.W, vp.H = (w, h)
    vc.W, vc.H = (w, h)
    g3.W, g3.H = (w, h)
    d = list(g3.Cam.__init__.__defaults__)
    d[1], d[2] = (w, h)
    g3.Cam.__init__.__defaults__ = tuple(d)
    return (vc, vp, g3)

def _ease(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)

def _io(u):
    u = min(1.0, max(0.0, u))
    return 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2

class City:

    def __init__(self, kind, t_base, t_end, size=(SPLIT[2] - SPLIT[0], SPLIT[3] - SPLIT[1])):
        self.kind, self.t_base, self.t_end = (kind, t_base, t_end)
        self.w, self.h = size
        vc, vp, g3 = self.vc, self.vp, self.g3 = _lib(*size)
        S = self.S = vc.sched()
        for tw in S['towers']:
            tw.her = False
        self.rng = np.random.default_rng(1003)
        noop = lambda *a, **k: None
        vc.lane_heads = vc.tags = vc.head_bars = vc.glyphs = noop
        vc.legend_and_lens = noop
        vc.overlays = self.overlays
        vc.camera = self.camera
        vc.cam_params = self.cam_params
        vc.IDLE_INK = 0.14
        self.plates = {}
        self.reel_tw = None
        if kind == 'E':
            self._plan_e()
        else:
            self._plan_g5()
        tmax = self.tau(t_end) + 2.0
        for tw in S['towers']:
            cl = S['dists'][tw.d]['cl']
            tw.cards = [(hh, k) for hh, k in cl.heads(-1.0, tmax) if tw.computing(k)]

    def tau(self, t):
        return t - self.t_base + TAU0

    def params(self, t):
        """(target, dist, yaw, pitch, fov) at song time t."""
        vc = self.vc
        far = vc.TGT_FAR
        if self.kind == 'E':
            q = (t - self.t_base) / max(0.001, self.t_end - self.t_base)
            tgt = far + vc.TGT_DRIFT * (q - 0.5) * 2.5 + np.array([0.0, -6.0, 40.0])
            dist = math.exp(math.log(470.0) + (math.log(440.0) - math.log(470.0)) * q)
            yaw, pitch, fov = (-0.25 + 0.07 * q, 0.3, 36.0)
            if self.reel_tw is not None:
                u = _io((t - self.push0) / (self.push1 - self.push0))
                if u > 0:
                    tw = self.reel_tw
                    near_t = tw.off + np.array([0.0, vc.TOP_Y * 0.8, 0.0])
                    creep = max(0.0, t - self.push1) * 6.0
                    w_ = u ** 0.6
                    tgt = tgt * (1 - w_) + near_t * w_
                    dist = math.exp(math.log(dist) + (math.log(255.0 - creep) - math.log(dist)) * u)
                    pitch = pitch + (0.25 - pitch) * u
                    yaw = yaw + (-0.34 - yaw) * u
                    fov = fov + (34.0 - fov) * u
            return (tgt, dist, yaw, pitch, fov)
        m = self.merged
        near_t = m.off + np.array([0.0, vc.TOP_Y * 0.55, 0.0])
        u = _io((t - self.t_base) / 2.2)
        q = (t - self.t_base) / max(0.001, self.t_end - self.t_base)
        far_t = far + vc.TGT_DRIFT * (q - 0.5) * 2.0 + np.array([0.0, -6.0, 40.0])
        logd = math.log(80.0) + (math.log(430.0 + 30.0 * q) - math.log(80.0)) * u
        w_ = u ** 1.7
        tgt = near_t * (1 - w_) + far_t * w_
        yaw = -0.4 + (-0.24 + 0.05 * q + 0.4) * u
        pitch = 0.3 + (0.31 - 0.3) * u
        fov = 34.0 + (36.0 - 34.0) * u
        return (tgt, math.exp(logd), yaw, pitch, fov)

    def cam_params(self, S, tau):
        return self.params(tau - TAU0 + self.t_base)

    def camera(self, S, tau, dfy=0.0):
        vc, g3 = (self.vc, self.g3)
        tgt, dist, yaw, pitch, fov = self.cam_params(S, tau)
        cam = g3.orbit_cam(np.asarray(tgt, float) + np.array([0.0, dfy, 0.0]), dist, yaw, pitch, fov)
        cam.dist = dist
        cam.fy = float(tgt[1])
        cam.farness = vc.smooth((dist - 60.0) / 220.0)
        cam.fog_n = 0.85 + (vc.FOG_FAR_N - 0.85) * cam.farness
        cam.fog_f = 3.2 + (vc.FOG_FAR_F - 3.2) * cam.farness
        cam.reveal = 1.0
        return cam

    def cam_at(self, t):
        return self.camera(self.S, self.tau(t))

    def _screen(self, tw, cam):
        vc = self.vc
        ok, b, depth = vc.tower_view(tw, cam)
        if not ok:
            return None
        sx, sy, sz = cam.project((tw.off + np.array([0.0, vc.TOP_Y, 0.0]))[None])
        return (float(sx[0]), float(sy[0]), b)

    def _join(self, tw, tau, band=True):
        cl = self.S['dists'][tw.d]['cl']
        tw.idle = False
        if tw.d not in self._phased and hasattr(cl, 'phase') and (cl.__class__.__name__ == 'PassClimber'):
            cl.phase = tau
            self._phased.add(tw.d)
            tw.join_k = 0
        else:
            tw.join_k = cl.k_at(tau) + 1
        tw.join_t = tau - 0.25
        if band:
            tw.prefill.add(tw.join_k)
        tw.cards0 = 0

    def _pick(self, t, n, used, min_b=9.0, sep=70.0, margin=40):
        """n towers in view at t, as large as possible, spread out, one per district, not yet used."""
        cam = self.cam_at(t)
        cand = []
        for tw in self.S['towers']:
            if tw.idx in used or tw.d in self._phased:
                continue
            if self.S['dists'][tw.d]['cl'].__class__.__name__ != 'PassClimber':
                continue
            sc = self._screen(tw, cam)
            if sc is None:
                continue
            sx, sy, b = sc
            if b < min_b or not (margin < sx < self.w - margin and 60 < sy < self.h - 40):
                continue
            cand.append((tw, sx, sy, b))
        cand.sort(key=lambda c: -c[3] * (0.6 + 0.8 * self.rng.random()))
        out = []
        for tw, sx, sy, b in cand:
            if all((math.hypot(sx - px, sy - py) > sep for _, px, py in out)) and all((tw.d != q.d for q, _, _ in out)):
                out.append((tw, sx, sy))
            if len(out) >= n:
                break
        return [o[0] for o in out]

    def _plan_e(self):
        import pages.e as PE
        S, rng = (self.S, self.rng)
        self._phased = set()
        towers = S['towers']
        for tw in towers:
            tw.idle = bool(rng.random() > 0.22)
            tw.join_k = tw.leave_k = tw.join_t = tw.leave_t = None
            tw.prefill = set()
        new = list(PE.NEW)
        times1, times2 = (list(syl.times(44)), list(syl.times(46)))
        self.push0, self.push1 = (tl.SLOT_AT - 0.35, tl.SLOT_AT + 1.2)
        used = set()
        self.reel_tw = None
        reel = self._pick(tl.SLOT_AT - 0.4, 1, used, min_b=11.0, margin=180)
        if reel:
            self.reel_tw = reel[0]
            used.add(self.reel_tw.idx)
            self._join(self.reel_tw, self.tau(times2[5]), band=True)
        k = 0
        for times in (times1, times2):
            picks = self._pick(times[0], len(times), used)
            for tt, tw in zip(times, picks):
                if tw is self.reel_tw:
                    continue
                self._join(tw, self.tau(tt), band=True)
                used.add(tw.idx)
                self.plates[tw.idx] = (self.tau(tt), new[k][1] if k < len(new) else 'kimi')
                k += 1
            k = len(times1)
        if self.reel_tw is not None:
            self.plates[self.reel_tw.idx] = (self.tau(times2[5]), 'reel')
        rest = [tw for tw in towers if tw.idle and tw.idx not in used]
        rng.shuffle(rest)
        n1 = len(rest) // 2
        a0, a1 = (self.tau(syl.times(45)[0]), self.tau(syl.times(46)[0] - 0.2))
        for tw in rest[:n1]:
            self._wake(tw, a0 + (a1 - a0) * rng.random())
        w0, w1 = (self.tau(times2[6]), self.tau(times2[-1] + 0.3))
        cam = self.cam_at(times2[6])
        tail = rest[n1:]
        keyx = []
        for tw in tail:
            sc = self._screen(tw, cam)
            keyx.append(sc[0] if sc else self.w * 2 if tw.x > 0 else -self.w)
        order = np.argsort(keyx)
        for j, oi in enumerate(order):
            self._wake(tail[oi], w0 + (w1 - w0) * j / max(1, len(order) - 1))

    def _wake(self, tw, tau):
        """An idle slot gets a request (no band, no plate: it is too small to read)."""
        cl = self.S['dists'][tw.d]['cl']
        tw.idle = False
        tw.join_k = cl.k_at(tau) + 1
        tw.join_t = tau - 0.2

    def _plan_g5(self):
        import groups.g as GG
        S, rng = (self.S, self.rng)
        self._phased = set()
        towers = S['towers']
        self.merged = next((tw for tw in towers if S['dists'][tw.d]['her'] and abs(tw.x) < 1e-06 and (tw.z > -1)))
        for tw in towers:
            tw.idle = False
            tw.join_k = tw.leave_k = tw.join_t = tw.leave_t = None
            tw.prefill = set()
        others = [tw for tw in towers if tw is not self.merged]
        dist_ids = sorted({tw.d for tw in others})
        rng.shuffle(dist_ids)
        closes = list(GG.CLOSE_T)
        groups = np.array_split(np.array(dist_ids), len(closes))
        for tc, ids in zip(closes, groups):
            ids = set((int(i) for i in ids))
            for tw in others:
                if tw.d in ids:
                    tau = self.tau(tc) + 0.12 * rng.random()
                    cl = S['dists'][tw.d]['cl']
                    tw.leave_k = cl.k_at(tau)
                    tw.leave_t = tau
        self.close_t = closes
        self.plates[self.merged.idx] = (self.tau(GG.G5) - 1.0, 'merged')

    def overlays(self, S, tau, T2):
        vc, vp, g3 = (self.vc, self.vp, self.g3)
        t = tau - TAU0 + self.t_base
        cam = self.camera(S, tau)
        alive = sum((1 for tw in S['towers'] if tw.alive(tau) > 0.5))
        m = vp.tmask(f'dsh ps --persona 大肥鱼 · {alive} session' + ('s' if alive != 1 else ''), 12, 'cjk')
        g3.blit_scaled(T2['halo'], m, 16, 10, 1.0)
        g3.blit_scaled(T2['ash'], m, 16, 10, 0.9)
        for idx, (tau_from, key) in self.plates.items():
            if tau < tau_from - 0.05:
                continue
            tw = S['towers'][idx]
            a = float(g3.smooth((tau - tau_from + 0.05) / 0.2)) * tw.alive(tau) ** 0.5
            if a < 0.02:
                continue
            sc = self._screen(tw, cam)
            if sc is None:
                continue
            sx, sy, b = sc
            big = key == 'reel'
            if not big and self.reel_tw is not None:
                a *= 1 - _ease((t - self.push0) / (self.push1 - self.push0))
                if a < 0.02:
                    continue
            size = int(min(30, max(12, 12 + b * 0.8))) if big else int(min(15, max(11, 9 + b * 0.35)))
            if key == 'reel':
                import pages.e as PE
                model = PE.REEL[PE.reel_index(t)]
            else:
                model = key
            mname = cast.short(model)
            m1 = vp.tmask('大肥鱼', size, 'cjk')
            m2 = vp.tmask(' · ' + mname, size, 'cjk')
            x = sx - (m1.shape[1] + m2.shape[1]) / 2
            y = sy - m1.shape[0] - 6 - (8 if big else 2)
            g3.blit_scaled(T2['halo'], m1, x, y, a)
            g3.blit_scaled(T2['halo'], m2, x + m1.shape[1], y, a)
            g3.blit_scaled(T2['blue'], m1, x, y, a)
            g3.blit_scaled(T2['text'], m2, x + m1.shape[1], y, a)
            g3.splat_segments(T2['ash'], np.array([sx]), np.array([y + m1.shape[0] + 2]), np.array([sx]), np.array([sy - 1.0]), 0.6 * a, None, 0.8)

    def render(self, t):
        return self.vc.frame(self.S, self.tau(t), 'paper')
