"""E in the panes (groups/e_pane.py, sample_open_e/README.md §6): inside/city.py's E city with three changes.
v2's spans (e1_city, e3_city) and their cache are unchanged; these are e1_city_p and e3_city_p.

1. The batch steps with the beat. Every session in a batch advances one token per decode step, all together
   (ARRANGE_20261003 §3). On each beat of the chorus (the kick drum's four on the floor) the top block of
   every running tower, its softmax line where the token comes out, flashes in ink and fades over 0.18 s;
   each district a few ms off the beat (other cards). Ink, not blue: her blue is for what lands (D1).
   The passes themselves keep v2's pace.
2. A session that joins on a sung syllable lights whole, in her blue, then settles into ink over 0.7 s: her
   persona and memory poured into one more machine (the same syllable inserts its row in the dsh sidebar).
3. The tower the camera moves in on wears e_reel's reel as its nameplate, big: the stand-ins in ink, her name
   (DeepSeek-V4.1-Flash) all in her blue; a step rolls the plate up like a reel.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import json
import math
import numpy as np
import cast
import e_reel
import syl
import tl
from .city import City, ROOT, SPLIT, TAU0, _ease
JITTER = 0.035
PULSE = 0.18
FLASH = 0.7

def _beats():
    b = json.loads((ROOT / 'timing' / 'beats.json').read_text(encoding='utf-8'))
    bt = np.asarray(b['beat_times'], float)
    i_fd = int(np.argmin(np.abs(bt - b['first_downbeat'])))
    return (bt, i_fd)

class CityE(City):

    def __init__(self, t_base, t_end):
        super().__init__('E', t_base, t_end)
        vc = self.vc
        if not hasattr(vc, '_city_signal0'):
            vc._city_signal0 = vc.city_signal
        vc.city_signal = self.city_signal
        bt, _ = _beats()
        self.beat_tau = bt - self.t_base + TAU0
        rng = np.random.default_rng(1004)
        self.d_off = [float(rng.uniform(0.0, JITTER)) for _ in self.S['dists']]

    def _pulse(self, tw, tau):
        """0..1: the roof flash of the latest beat (this district's offset)."""
        k = int(np.searchsorted(self.beat_tau, tau - self.d_off[tw.d], side='right')) - 1
        if k < 0:
            return 0.0
        return math.exp(-(tau - self.d_off[tw.d] - self.beat_tau[k]) / PULSE)

    def _join(self, tw, tau, band=True):
        tw.syl_tau = tau
        super()._join(tw, tau, band)

    def city_signal(self, S, tw, t, cam, b, mode, rk_of, segs, Bf, ID):
        vc = self.vc
        vc._city_signal0(S, tw, t, cam, b, mode, rk_of, segs, Bf, ID)
        if tw.idle or tw.her:
            return
        P_ = vc.prep()
        o = tw.off
        alive = tw.alive(t)
        g = self._pulse(tw, t) * alive * cam.reveal
        if g > 0.02:
            e = P_['rows'][vc.ROW_IDX[id(vc.HROW)]]
            lite = min(1.0, max(0.4, b / 12.0))
            segs.add('bone', e['frameA'] + o, e['frameB'] + o, 2.4 * g * lite, 2.8, vc.rank_for(rk_of, mode, e['ri']))
        ts = getattr(tw, 'syl_tau', None)
        if ts is None:
            return
        u = t - ts
        if u < -0.5 / 24 or u > FLASH:
            return
        g = (1.0 - vc.smooth(max(0.0, u) / FLASH)) * cam.reveal * min(1.0, max(0.6, b / 12.0))
        if g < 0.01:
            return
        for e in P_['rows']:
            r = e['r']
            rk = vc.rank_for(rk_of, mode, e['ri'])
            if r.kind == 'S':
                if mode == 'plates':
                    continue
                segs.add('sig', e['rectA'] + o, e['rectB'] + o, 1.6 * g, 1.6, rk)
            else:
                segs.add('sig', e['frameA'] + o, e['frameB'] + o, 1.6 * g, 1.9, rk)

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
            if key == 'reel':
                self._reel_plate(T2, t, a, sx, sy, b)
                continue
            if self.reel_tw is not None:
                a *= 1 - _ease((t - self.push0) / (self.push1 - self.push0))
                if a < 0.02:
                    continue
            bump = 1.0 + 0.3 * (1.0 - _ease((tau - tau_from) / 0.16))
            size = int(min(15, max(11, 9 + b * 0.35)) * bump)
            self._plate(T2, '大肥鱼', ' · ' + cast.short(key), sx, sy - 2, size, a, her=False)

    def _plate(self, T2, left, right, sx, sy, size, a, her, dy=0.0):
        vp, g3 = (self.vp, self.g3)
        m1 = vp.tmask(left, size, 'cjk')
        m2 = vp.tmask(right, size, 'cjk')
        wd = m1.shape[1] + m2.shape[1]
        x = min(max(8.0, sx - wd / 2), self.w - 8.0 - wd)
        y = sy - m1.shape[0] - 6 + dy
        g3.blit_scaled(T2['halo'], m1, x, y, a)
        g3.blit_scaled(T2['halo'], m2, x + m1.shape[1], y, a)
        g3.blit_scaled(T2['blue'], m1, x, y, a)
        g3.blit_scaled(T2['blue' if her else 'text'], m2, x + m1.shape[1], y, a)
        return y + m1.shape[0]

    def _reel_plate(self, T2, t, a, sx, sy, b):
        """大肥鱼 stays put (her persona's name, her blue); only the model's slot rolls, like a reel window. The
        plate is laid out for a short name and kept inside the frame for the longest one (hers)."""
        vp, g3 = (self.vp, self.g3)
        size = int(min(40, max(16, 14 + b * 0.9)))
        i = e_reel.index(t)
        roll = min(1.0, e_reel.since(t) / 0.06)
        lift = size * 0.6

        def name(k):
            return ' · ' + (cast.name('her') if k == 'her' else cast.short(k))
        m1 = vp.tmask('大肥鱼', size, 'cjk')
        ref = vp.tmask(name('longcat'), size, 'cjk').shape[1]
        widest = vp.tmask(name('her'), size, 'cjk').shape[1]
        x = sx - (m1.shape[1] + ref) / 2
        x = min(max(8.0, x), self.w - 8.0 - m1.shape[1] - widest)
        y = sy - 8 - m1.shape[0] - 6
        g3.blit_scaled(T2['halo'], m1, x, y, a)
        g3.blit_scaled(T2['blue'], m1, x, y, a)
        x2 = x + m1.shape[1]
        cur = e_reel.STRIP[i]
        slots = [(cur, a * roll ** 0.5, lift * (1 - roll))]
        if roll < 1.0 and i > 0:
            slots.append((e_reel.STRIP[i - 1], a * (1 - roll), -lift * roll))
        for k, aa, dy in slots:
            m2 = vp.tmask(name(k), size, 'cjk')
            g3.blit_scaled(T2['halo'], m2, x2, y + dy, aa)
            g3.blit_scaled(T2['blue' if k == 'her' else 'text'], m2, x2, y + dy, aa)
        yb = y + m1.shape[0]
        g3.splat_segments(T2['ash'], np.array([sx]), np.array([yb + 2]), np.array([sx]), np.array([sy - 1.0]), 0.6 * a, None, 0.8)

def _city():
    return CityE(tl.SEC['E'], tl.W(48, 0))

def spans():
    """The pane version of shots.spans()' two E entries (same times, own cache directories)."""
    from .install import Span
    return [Span('e1_city_p', tl.SEC['E'], syl.times(44)[-1] + 0.2, _city, fade_in=0.25, fade_out=0.25, register=False, rect=SPLIT, lift='left'), Span('e3_city_p', syl.times(46)[0] - 0.24, tl.W(48, 0) - 0.25, _city, fade_in=0.24, fade_out=0.25, register=False, rect=SPLIT, lift='left')]

def patch_shots():
    """Swap v2's two E city spans for these in inside.shots.spans() (film.py and the cache read it)."""
    import inside.shots as IS
    if getattr(IS, '_epane', False):
        return
    orig = IS.spans

    def spans_():
        return [s for s in orig() if s.name not in ('e1_city', 'e3_city')] + spans()
    IS.spans = spans_
    IS._epane = True
