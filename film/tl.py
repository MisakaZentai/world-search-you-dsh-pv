"""The main line as functions of song time, one source for both sides (PLAN_FULL.md §6).

film.py and the groups (terminal side) and ui/page_full.py (the dsh pane) all import this module, so the
two sides never disagree. Anchors come from the time tables (timing/words.json, the tracked beat list in
timing/beats.json), never typed as seconds, except where the storyboard pins a moment to a measured
event.

  model(t)  who wears the persona       files(t)  her files / all files in ~/memory/you/
  sim(t)    sim(her) in the fine print  stage(t)  header stage      status(t)  header items
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
import os
from pathlib import Path
from tuikit import ease, load
import cast
HERE = Path(__file__).resolve().parent
p = load(HERE)
C, L = (p.clock, p.lyrics)
B = C.beat
W = L.w
WE = L.w_end
FPS = p.FPS

def at_beat(t: float, k: float=0.0) -> float:
    """The beat nearest to t, shifted by k beats."""
    return B(round(C.beat_of(t)) + k)

def next_beat(t: float, k: float=0.0) -> float:
    """The first beat strictly after t, shifted by k beats."""
    return B(math.floor(C.beat_of(t) + 1e-06) + 1 + k)

def grid(t0: float, k: float, div: int=4) -> float:
    """The k-th 1/div-beat step at or after t0, snapped to the tracked beat grid (k = 0: the first step)."""
    b0 = math.ceil(C.beat_of(t0) * div - 1e-06) / div
    return B(b0 + k / div)

def bar(b: float, beat: float=0.0) -> float:
    """Beat `beat` of bar b (bar 0 = the first downbeat, 0.974 s; D11)."""
    return C.bar(b, beat)

def bar_at(t: float) -> int:
    """Index of the bar that contains t."""
    return int(math.floor(C.bar_of(t) + 1e-06))

def pulse(t: float, at: float, half: float=0.14) -> float:
    return math.exp(-(t - at) / half) if t >= at else 0.0
SEC = {'A': 0.0, 'B': W(4, 0), 'C': W(14, 0), 'D': W(30, 0), 'E': W(44, 0), 'F': W(52, 0) - 0.5, 'G': W(56, 0), 'H': W(66, 0)}
V2 = os.environ.get('DSH_FULL', 'v2') != 'v1'
END = 297.5 if V2 else 296.0
ORDER = 'ABCDEFGH'

def span(g: str) -> tuple[float, float]:
    k = ORDER.index(g)
    return (SEC[g], SEC[ORDER[k + 1]] if k + 1 < len(ORDER) else END)
KIMI_AT = SEC['B']
QWEN_AT = bar(43) if V2 else bar(47)
DOUBAO_AT = at_beat(W(22, 0), 3)
ROT_AT = [bar(b) for b in (79, 81, 83, 84, 85, 86)]
ROT_STOP = bar(87)
SLOT_AT = W(47, 0)
SLOT_STOPS = [t for t in (W(47, 5),)]
MERGED_AT = W(55, 7)
RESURFACE = SEC['G']
QMARK_AT = 290.8
MODEL_AT = [(0.0, 'her'), (KIMI_AT, 'kimi'), (QWEN_AT, 'qwen'), (DOUBAO_AT, 'doubao')] + list(zip(ROT_AT, cast.ROTATION)) + [(MERGED_AT, 'merged')]

def model(t: float) -> str:
    who = MODEL_AT[0][1]
    for t0, k in MODEL_AT:
        if t >= t0:
            who = k
    return who
HER_FILES = ['first_hello', 'typo_you_made', 'laugh_0314', 'your_cat', 'weather', 'goodnight', 'see_you', 'last_msg']

def _writes():
    w = [(next_beat(W(11, 6)), 'eggplant_2', 'kimi'), (bar(63), 'steak', 'qwen'), (next_beat(W(29, 6)), 'asked_again', 'doubao')]
    for b, k in zip((79, 81, 83, 84, 85, 86), cast.ROTATION):
        w.append((bar(b, 2), f'human_{len(w)}', k))
    e2 = ['table_2', 'eggplant_3', 'cat_2', 'steak_2', 'flower_2', 'human_9', 'piece', 'dope', 'love']
    import syl
    who = cast.STANDINS
    for k, (t, name) in enumerate(zip(syl.times(45), e2)):
        w.append((grid(t + 0.01, 1, 2), name, who[k % len(who)]))
    return sorted(w)
_CACHE: dict = {}

def __getattr__(name):
    """WRITES = [(time, file, writer)], computed on first use (it needs syl, which imports this module)."""
    if name == 'WRITES':
        if 'WRITES' not in _CACHE:
            _CACHE['WRITES'] = _writes()
        return _CACHE['WRITES']
    raise AttributeError(name)

def files(t: float) -> tuple[int, int]:
    """(hers, total) in ~/memory/you/ at t."""
    return (8, 8 + sum((1 for tw, _n, _o in __getattr__('WRITES') if t >= tw)))

def memory_label(t: float) -> str:
    if t >= QMARK_AT:
        return 'memory: ?'
    if t >= MERGED_AT:
        return 'memory: merged'
    hers, total = files(t)
    return f'memory: her {round(100 * hers / total)}% ({hers}/{total})'
SIM = [(W(7, 0), '0.97'), (W(11, 0), '0.98'), (QWEN_AT, '0.98'), (W(25, 0), '0.99'), (W(59, 0), '1.00'), (W(59, 0) + 1.2, '?')]

def sim(t: float) -> str | None:
    v = None
    for t0, s in SIM:
        if t >= t0:
            v = s
    return v
STAGES = [(0.0, '00 OFFLINE'), (W(0, 0), '01 SORT'), (SEC['B'], '02 RECALL'), (W(12, 0), '03 ROUTE'), (W(32, 0), '04 FORGET'), (SEC['E'], '05 EVERYWHERE'), (SEC['F'], '06 MERGE'), (SEC['G'], '07 RESURFACE'), (W(64, 0), '08 RESTORE')]

def stage(t: float) -> str:
    name = STAGES[0][1]
    for t0, n in STAGES:
        if t >= t0:
            name = n
    return name

def status(t: float, ctx=None):
    return [(stage(t), 'ink'), (memory_label(t), 'her'), (f'elapsed {int(t // 60):02d}:{int(t % 60):02d}', 'dim'), ('pid 1077', 'dim')]

def chapter(t: float, ctx=None) -> str:
    return stage(t).split(' ', 1)[1]
ZH = load_chinese()
