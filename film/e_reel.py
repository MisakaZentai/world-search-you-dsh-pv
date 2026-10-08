"""E3 in the panes (groups/e_pane.py, sample_open_e/README.md §6): the model name under 大肥鱼 as a slot reel.
One schedule for both sides: the city's big nameplate (inside/city_epane.py) and the dsh header
(ui/pages/e_pane.py). v2's reel (ui/pages/e.py) is unchanged.

From "But" the reel spins one name per 16th (R6: a step is at least a 16th), slows down over four steps and
lands on her (DeepSeek-V4.1-Flash, her blue) two 16ths before the first syllable of trans-for-ming; on the
syllable it slips one name on, to a stand-in. Between the stops it comes back to her and slips again:
stand-in, her, stand-in, her, stand-in. Three times nearly her, never her (the last stop is the current model).
Her name is on the strip more than once, as a slot strip carries its top symbol more than once.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
from bisect import bisect_right
import tl
from groups import e as G
SPIN = ['kimi', 'qwen', 'mimo', 'glm', 'ernie', 'hy4', 'minimax', 'step', 'her', 'longcat']
STOPS = list(G.SLOT_STOPS)
LAND = ['ernie', 'step', 'longcat']
EARLY = 2
SLOW = [1.25, 1.6, 2.1, 2.8]

def _sixteenth(t: float) -> float:
    return tl.grid(t, 1, 4) - tl.grid(t, 0, 4)

def _schedule():
    """(steps, strip): steps[i] is when the reel moves to strip[i + 1]; strip[0] is the name at rest.

    The steps are laid back from her first landing: four slowing gaps, then 16ths back to "But". During the
    fast spin she flicks past once a turn; while it slows she is skipped, so the first time it settles is on her.
    """
    s16 = _sixteenth(G.SLOT_AT)
    her_at = [s - EARLY * s16 for s in STOPS]
    back, t = ([], her_at[0])
    for g in SLOW[::-1]:
        t -= g * s16
        back.append(t)
    n_slow = len(back)
    while t - s16 >= G.SLOT_AT - 0.02:
        t -= s16
        back.append(t)
    steps = back[::-1]
    strip = ['longcat']
    k = SPIN.index('longcat')
    for i in range(len(steps)):
        k = (k + 1) % len(SPIN)
        if i >= len(steps) - n_slow and SPIN[k] == 'her':
            k = (k + 1) % len(SPIN)
        strip.append(SPIN[k])
    for h, s, land in zip(her_at, STOPS, LAND):
        steps += [h, s]
        strip += ['her', land]
    return (steps, strip)
STEPS, STRIP = _schedule()

def index(t: float) -> int:
    return bisect_right(STEPS, t)

def at(t: float) -> str:
    """The name on the reel at t."""
    return STRIP[index(t)]

def neighbours(t: float):
    """(above, current, below) as the dsh header shows them: the strip runs upward, the next name is below."""
    i = index(t)
    prev = STRIP[i - 1] if i > 0 else 'her'
    nxt = STRIP[i + 1] if i + 1 < len(STRIP) else 'kimi'
    return (prev, STRIP[i], nxt)

def since(t: float) -> float:
    """Seconds since the reel last moved (inf before the first step)."""
    i = index(t)
    return t - STEPS[i - 1] if i > 0 else float('inf')
if __name__ == '__main__':
    for s, n in zip(STEPS, STRIP[1:]):
        print(f'{s:8.3f}  {n}')
