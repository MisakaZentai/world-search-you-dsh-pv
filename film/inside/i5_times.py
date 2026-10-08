"""r5 batch 2 (REVISE_R4_20261004.md §3.1, §3.4, §3.15; D34): the times of the three interludes, all from the beat map
(beatmap.py) and the groups' own times. One place, read by interludes.py, inside/i5_*.py and ui/pages/i5_g.py.

The motif: "I'm searching" -> the forward pane opens into the machine's body -> her blue goes in, one group of layers
an event -> it comes back out on the downbeat before the next sung line. Interludes 1 and 3 are one piece of music
(drums out, the synth's stabs), so they step on 'stab'; interlude 2 has a kick on every beat, so it steps on 'kick'.

r5 round 2 (D35, sample_r5/README.md §4 R-A): a step no longer stops dead. Each big move eases IN and lands on its
event, exactly on a node (beatmap.arrive: a layer, a group of layers, an arc's foot); once it is there, the inside of
that node keeps moving at the rate of the harmony (phase() below: the integral of beatmap.pad, never zero), so
nothing holds still while the chords go on. A downbeat lights only the node the picture stands on (node_flash()),
by beatmap.accent's tiers, never the whole machine.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import bisect
from functools import lru_cache
import numpy as np
import beatmap as BM
import tl
from groups import b as GB
from groups import d as GD
from groups import g as GG
NEAR_OUT, NEAR_BACK, SWITCH = (GB.NEAR_OUT, GB.NEAR_BACK, GB.SWITCH)
_S1 = BM.events('stab', NEAR_OUT - 0.01, NEAR_BACK + 0.01)
PTS = _S1[:3]
RINGS = [tl.bar(41)] + [s for s in _S1 if tl.bar(41) < s < NEAR_BACK - 0.01][-3:] + [NEAR_BACK]
I1_DSH = tl.next_beat(NEAR_BACK)
DOWN1 = BM.events('down', NEAR_OUT - 0.01, NEAR_BACK + 0.01)
assert len(PTS) == 3 and len(RINGS) == 5, (PTS, RINGS)
TURNS = GD.TURNS
ROT_AT, ROT_STOP = (GD.ROT_AT, GD.ROT_STOP)
I2_IN = ROT_AT[0]
I2_BACK = ROT_STOP
I2_END = GD.SCROLL_AT
I2_SHUT = 0.3
KICKS = BM.events('kick', I2_IN - 0.01, I2_BACK - 0.01)
SNARES = BM.events('snare', I2_IN - 0.01, I2_BACK - 0.01)
DOWN2 = BM.events('down', I2_IN - 0.01, I2_BACK + 0.01)
FLASH2 = BM.merge(DOWN2, SNARES, gap=0.06)

def turn_kicks(T):
    """The kicks while this stand-in is open: one group of its layers each (2 bars: 8-9 groups, 1 bar: 4)."""
    return [k for k in KICKS if T.t0 - 0.01 <= k < T.t1 - 0.01]
G5, FOUND = (GG.G5, GG.FOUND)
I3_FILL = BM.events('stab', G5, G5 + 1.4)
DOWN3_IN = BM.events('down', G5, G5 + 1.4)
I3_OUT = I3_FILL[-1]
ARCS_T = G5
TURN_BAR = tl.bar(155)
CHAR_AT = [I3_OUT] + BM.events('stab', I3_OUT + 0.2, TURN_BAR - 0.05)
DOWN3_ARCS = BM.events('down', G5, TURN_BAR - 0.05)
SESSIONS = list(GG.SESSIONS)
CLOSES = BM.events('stab', TURN_BAR + 0.4, FOUND - 0.05)[:len(SESSIONS)]
I3_BACK = 0.4
assert len(I3_FILL) == 4, I3_FILL
assert len(CHAR_AT) == 12, CHAR_AT
assert len(CLOSES) == len(SESSIONS) and CLOSES[-1] < FOUND - 0.3, CLOSES
PAD_FLOOR = 0.25
_WINDOWS = {1: (BM.WIN['interlude1'][0] - 0.6, tl.bar(47) + 1.0), 2: (I2_IN - 0.6, I2_END + 0.6), 3: (G5 - 0.6, FOUND + 0.6)}
_DT = 1 / 96

@lru_cache(maxsize=4)
def _pad_table(which):
    t0, t1 = _WINDOWS[which]
    ts = np.arange(t0, t1, _DT)
    v = np.maximum(PAD_FLOOR, np.array([BM.pad(float(t)) for t in ts]))
    cum = np.concatenate([[0.0], np.cumsum(0.5 * (v[1:] + v[:-1]) * _DT)])
    return (ts, cum)

def phase(t: float, which: int) -> float:
    """Seconds of harmony since interlude `which` (1, 2, 3) began: the integral of max(pad, PAD_FLOOR). It grows
    between the events as fast as the chords are loud (about 0.3-0.8 per second) and never stands still."""
    ts, cum = _pad_table(which)
    return float(np.interp(t, ts, cum))

def node_flash(t: float, landings, downs=(), half: float=0.16) -> float:
    """0..1: the node the picture stands on lit her blue on its landing and on a downbeat while it holds, at the
    beat's weight (beatmap.accent: downbeat 1.0, beat 3 0.6, beats 2 and 4 0.35), decaying with half-life `half`."""
    ev = sorted(set((round(x, 4) for x in list(landings) + list(downs))))
    k = bisect.bisect_right(ev, t + 1e-06)
    if k == 0:
        return 0.0
    at = ev[k - 1]
    return BM.accent(at + 0.01) * 0.5 ** ((t - at) / half)
