"""r5 batch 2, interlude 3 (REVISE_R4_20261004.md §3.13, §3.15, D7): the 4:00 arcs plate, moved into the interlude.

The plate is groups/g_lead.py's `_arcs40` (the v12 arcs on her 40 layers: the merged one writes 今天那朵开了，有点想你了
and every read goes back to your old words, none into her files), copied here (g_lead is only read; its own 4:00 copy
is batch 4's to take out). Only the time changes: each character on one of the synth's stabs between 262.61 and
267.98, its reads landing on the same stab (they rise in the 0.12 s before it), <eos> on bar 155's downbeat (268.19).

r5e (D40 ②, owner 10-05: the body shot was a process cut half way): there is no body shot any more. The forward
pane opens straight onto this plate at G5 (260.88) and the first character's pass is the climb: 10 layers a stab
on the four stabs 261.09-262.17, the lens column building up L8, L16, L24, L32 behind a rising line, one of 今's
four reads landing on each stab (persona, 那朵花, 开了吗？, 我想你了); on 262.17 the top: 今 lands. Then a character
a stab as before, 12 of them now (今天那朵花开了，有点想你了: 花 reads 那朵花).

Round 2 (D35, R-A): between two landings the arc that just landed is read again and again: a bead runs up it from
the character back to your words, at the rate of the harmony (i5_times.phase), so the plate never stands still while
the chords go on. Under the memory group the merged memory's 26 files are 26 ticks, her 8 among them in her quiet
blue; on the bar downbeats in between (263.04, 264.76, 266.47) only those 8 light her blue and settle (not the whole
group, D35), and no arc goes to them.

Plates are cached in cache/i5_arcs/<frame>.png:  python -m inside.i5_arcs [--force] [--workers 4]
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
ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(PV_ROOT / 'runtime')):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import numpy as np
import beatmap
from . import arcs as AR
from . import i5_times as I5
from .plate import arclen
CACHE = ROOT / 'cache' / 'i5_arcs'
HOLD = I5.TURN_BAR + 0.2
NAMES = {'L64': 'L40', 'L48': 'L32', 'L36': 'L24', 'L24': 'L16', 'L12': 'L8'}
STATUS = None

def _status():
    import cast
    return f'{cast.term('merged')} · preview · 40 layers'

def make_turn():
    import groups.g as GG
    from . import content as K
    P_ = 'persona'
    fl, bl, mi = (('hist', 'h_flower'), ('hist', 'h_bloom'), ('hist', 'h_miss'))
    attn = [[P_, fl, bl, mi], [P_, bl], [P_, fl], [P_, fl], [P_, fl], [P_, bl], [P_, bl], [P_, mi], [P_, mi], [P_, mi], [P_, mi], [P_, mi]]
    turn = K.build_turn(GG.MSG, [], GG.FLOWER, attn, '我是深度求索的助手很高兴', '你好请问有什么可以帮助你', [None] * len(attn), eos_attn=[P_, mi])
    return K.retime(turn, list(I5.CHAR_AT) + [I5.TURN_BAR], start=I5.ARCS_T)

def make_groups():
    It = AR.Item
    return [('persona', [It('你是大肥鱼', 'persona'), It('…')]), ('memory', [It('merged', 'mem:merged'), It('26 files', None, 'faint')]), ('history · you', [It('那朵花', 'hist:h_flower'), It('开了吗？', 'hist:h_bloom'), It('…'), It('我想你了', 'hist:h_miss')]), ('you', [It('—', None, 'faint')])]
CLIMB = list(I5.I3_FILL)
CLIMB_TRAVEL = 0.3
TIP_Y = [176.0, 150.0, 116.0, 82.0, 60.0]

class ArcsI5(AR.ArcsPlate):

    def __init__(self):
        super().__init__(make_turn(), make_groups(), I5.ARCS_T, status=_status(), ink_answer=True)
        self.mem = [it for tag, _x0, _x1, its in self.brackets if tag == 'memory' for it in its]
        self.top_in = CLIMB[0] - CLIMB_TRAVEL

    def window(self, i, j, n):
        """r5e: 今's four reads land one on each stab of the climb (from the pane opening for the first)."""
        if i == self.sung[0] and n == len(CLIMB):
            return (max(CLIMB[j] - CLIMB_TRAVEL, I5.G5 + 0.02), CLIMB[j])
        return AR.ArcsPlate.window(self, i, j, n)

    def _schedule(self):
        """Each character's reads rise in the 0.12 s before its stab and land on it; the character drops on it."""
        AR.ArcsPlate._schedule(self)
        self.slow = {}
        for i in self.sung:
            c = self.turn.chars[i]
            self.a0[i], self.a1[i] = (c.t - 0.12, c.t)
        first = self.sung[0]
        self.a0[first] = self.window(first, 0, len(self.turn.chars[first].reads))[0]
    N_FILES, HERS = (26, 8)

    def _draw_line(self, P, t):
        AR.ArcsPlate._draw_line(self, P, t)
        gi, (tag, x0, x1, _its) = next(((g, b) for g, b in enumerate(self.brackets) if b[0] == 'memory'))
        a = AR.out_cubic(AR.prog(t, self.t_in + 0.06 + 0.12 * gi, self.t_in + 0.42 + 0.12 * gi))
        if a <= 0:
            return
        k = beatmap.flash(t, I5.DOWN3_ARCS, half=0.14)
        n = self.N_FILES
        hers = {int(round((j + 0.5) * n / self.HERS - 0.5)) for j in range(self.HERS)}
        pitch = (x1 - x0) / n
        y0, y1 = (AR.CTX_Y + 15, AR.CTX_Y + 21)
        for j in range(n):
            x = x0 + pitch * (j + 0.5)
            if j in hers:
                P.line([(x, y0), (x, y1)], 1.0, a * (1 - k), 'quiet')
                if k > 0.01:
                    P.line([(x, y0 - 2 * k), (x, y1)], 1.0, a * k, 'blue')
            else:
                P.line([(x, y0), (x, y1)], 1.0, 0.5 * a, 'ash')

    def _climb_bead(self, P, t):
        """r5e: during the climb the read that landed last is read again and again (R-A), as after a landing."""
        i = self.sung[0]
        c = self.turn.chars[i]
        k = sum((1 for at in CLIMB if at <= t))
        n = len(c.reads)
        if not k or n != len(CLIMB):
            return
        pts = self.arc_pts(i, c.reads[k - 1][0], k - 1, n)
        if pts is None:
            return
        at = CLIMB[k - 1]
        nxt = CLIMB[k] - CLIMB_TRAVEL if k < len(CLIMB) else c.t
        if t >= nxt:
            return
        u = (I5.phase(t, 3) - I5.phase(at, 3)) * 5.0 % 1.0
        u = 0.05 + 0.88 * u
        L = arclen(pts)
        d = u * L[-1]
        x = float(np.interp(d, L, pts[:, 0]))
        y = float(np.interp(d, L, pts[:, 1]))
        fade = AR.prog(t, at, at + 0.06) * (1 - AR.prog(t, nxt - 0.05, nxt))
        P.circle(x, y, 3.2 if c.reads[k - 1][0] != 'persona' else 2.4, fade, 'ink')

    def _draw_arcs(self, P, t):
        AR.ArcsPlate._draw_arcs(self, P, t)
        landed = self.landed(t)
        if not landed:
            self._climb_bead(P, t)
            return
        if t >= HOLD:
            return
        i = landed[-1]
        c = self.turn.chars[i]
        nxt = next((self.a0[j] for j in self.sung if self.turn.chars[j].t > c.t), HOLD)
        if t >= nxt:
            return
        n = len(c.reads)
        j = next((jj for jj, (key, _w) in enumerate(c.reads) if key != 'persona'), None)
        if j is None:
            return
        pts = self.arc_pts(i, c.reads[j][0], j, n)
        if pts is None:
            return
        u = (I5.phase(t, 3) - I5.phase(c.t, 3)) * 5.0 % 1.0
        u = 0.05 + 0.88 * u
        L = arclen(pts)
        d = u * L[-1]
        x = float(np.interp(d, L, pts[:, 0]))
        y = float(np.interp(d, L, pts[:, 1]))
        fade = AR.prog(t, c.t, c.t + 0.06) * (1 - AR.prog(t, nxt - 0.05, nxt))
        P.circle(x, y, 3.2, fade, 'ink')

    def _draw_top(self, P, t):
        real = P.text

        def text(x, y, s, *a, **kw):
            return real(x, y, NAMES.get(s, s) if isinstance(s, str) else s, *a, **kw)
        P.text = text
        try:
            if t < self.turn.chars[self.sung[0]].t:
                self._draw_climb(P, t)
            AR.ArcsPlate._draw_top(self, P, t)
        finally:
            P.text = real

    def _draw_climb(self, P, t):
        """r5e (D40 ②): the first character's 40 layers, before it lands. A line rises up the lens column and lands on
        a row on each stab (L8, L16, L24 on the first three, the column's top on the fourth, the moment 今 lands);
        each row it reaches shows that layer's guess (its own habit low, 今 higher), newest at full ink, then
        settling. The row labels come in with the line. The L40 line, p and the big character are the landing's
        (ArcsPlate._draw_top)."""
        c = self.turn.chars[self.sung[0]]
        a_in = AR.out_cubic(AR.prog(t, CLIMB[0] - CLIMB_TRAVEL, CLIMB[0] - CLIMB_TRAVEL + 0.2))
        if a_in <= 0.003:
            return
        k = beatmap.arrive(t, CLIMB, CLIMB_TRAVEL)
        y_tip = float(np.interp(k, range(len(TIP_Y)), TIP_Y))
        P.line([(AR.LX + 22, TIP_Y[0]), (AR.LX + 22, y_tip)], AR.W_FINE, 0.5 * a_in)
        P.circle(AR.LX + 22, y_tip, 2.0, 0.9 * a_in, 'ink')
        lens = list(reversed(c.lens))
        for r, (lay, (txt, _hers)) in enumerate(zip((48, 36, 24, 12), lens)):
            y = 70 + r * 34
            P.text(AR.LX - 34, y, f'L{lay}', 11, AR.MONO, 0.7 * a_in, 'ash', 'rs')
            at = CLIMB[3 - r]
            if t < at:
                continue
            lit = 1 - AR.prog(t, at + 0.12, at + 0.45)
            P.text(AR.LX, y, txt, 24, AR.CJK, (0.72 + 0.28 * lit) * AR.prog(t, at, at + 0.05), 'ink', 'ms')
        m = sum((1 for at in CLIMB[:3] if at <= t))
        if m:
            at = CLIMB[m - 1]
            lit = 1 - AR.prog(t, at + 0.12, at + 0.45)
            P.text(AR.GX, AR.GY, lens[4 - m][0], AR.GS, 'sans:540', (0.22 + 0.16 * lit) * AR.prog(t, at, at + 0.05), 'ash', 'ms')

def frames(fps=24):
    return range(int(math.ceil(I5.ARCS_T * fps - 1e-06)), int(math.ceil(HOLD * fps - 1e-06)) + 1)

def path(n):
    return CACHE / f'{n:05d}.png'

def frame_n(t, fps=24):
    """The plate frame shown at t: its own until HOLD, then the last one (the way out)."""
    fr = frames(fps)
    return max(fr.start, min(fr.stop - 1, int(round(t * fps))))
_R = None

def _init():
    global _R
    _R = ArcsI5()

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
    ap.add_argument('--workers', type=int, default=4)
    a = ap.parse_args()
    CACHE.mkdir(parents=True, exist_ok=True)
    todo = [n for n in frames() if a.force or not path(n).exists()]
    t0 = time.time()
    from multiprocessing import Pool
    with Pool(min(a.workers, max(1, len(todo))), initializer=_init) as pool:
        for _ in pool.imap_unordered(_one, todo, chunksize=2):
            pass
    print(f'i5_arcs: {len(todo)} frames in {time.time() - t0:.1f} s -> {CACHE}')
if __name__ == '__main__':
    main()
