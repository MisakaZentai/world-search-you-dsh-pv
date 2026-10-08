"""Beat map (REVISE_R4_20261004.md §7.0, DECISIONS D34): what the picture steps on.

P1: a change lands on the music. A continuous move (a camera drifting, a band of blue rising at a constant rate)
becomes steps that land on events. Owner 10-04 on the r5 candidate: a step that stops dead between hits feels
stuck, because the chords keep going; so a step lands exactly on a node (a layer, a block, a box) on its event,
and inside that node something keeps moving at the rate of the harmony (arrive + inner + pad below). Every r5
group takes its events from here and keeps no beat list of its own.

Event kinds (song seconds, sorted):
  beat, down, eighth, sixteenth   the tracked grid (timing/beats.json through tl.C; down = bar downbeats, D11)
  kick, snare, hat, vocal         onsets from timing/audio.json, strength >= MIN_STRENGTH[kind]
  stab                            rises of the 'other' stem (the synth line), snapped to the 16th grid
  bassrise                        rises of the 'bass' stem, snapped the same way

  events(kind, t0, t1)            [t, ...] in [t0, t1)
  strong(kind, t0, t1, n)         the n strongest of a kind in [t0, t1), in time order
  merge(*lists, gap=0.06)         one sorted list, events closer than gap collapsed into the first
  step(t, times, ease_s=0.15)     steps taken by t: n whole steps + the eased part of the step in progress
  arrive(t, times, travel=0.35)   nodes reached by t, each move easing in so it LANDS on its event (preferred)
  inner(t, times)                 seconds since the latest event: the clock for motion inside the held node
  pad(t)                          0..1 sustained harmony (other + bass): the rate of that inner motion
  flash(t, times, half=0.12)      0..1, decaying after the latest event
  last(t, times)                  the latest event <= t, or None
  accent(t)                       weight of the beat t falls in: downbeat 1.0, beat 3 0.6, beats 2 and 4 0.35
  WIN                             the named spans of REVISE_R4 (interludes, forget, chorus)

Measured (REVISE_R4 §2.1): interludes 1 and 3 are one piece of music (envelope correlation 0.82), drums out,
the synth plays syncopated stabs; interlude 2 has a kick on every beat. So interludes 1 and 3 step on 'stab',
interlude 2 on 'kick'. The events come from the stems ("hearing with the eyes", not listened to).
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import bisect
import math
from functools import lru_cache
import tl
from tuikit import ease
C = tl.C
MUSIC = tl.p.music
WIN = {'interlude1': (tl.W(12, 0), tl.W(14, 0)), 'interlude2': (tl.W(30, 0), tl.W(32, 0)), 'interlude3': (tl.W(64, 0), tl.W(66, 0)), 'forget': (tl.W(32, 0), tl.W(44, 0)), 'chorus': (tl.W(44, 0), tl.W(52, 0) - 0.5)}
MIN_STRENGTH = {'kick': 0.3, 'snare': 0.25, 'hat': 0.25, 'vocal': 0.3}
RISE_LOOKBACK = 0.06
RISE_MIN = {'other': 0.12, 'bass': 0.12}
PEAK_HALF = 5
SNAP = 0.06
STAB_GAP = 0.08

def _grid(div: int, t0: float, t1: float):
    k0 = math.floor(C.beat_of(t0) * div) - 1
    k1 = math.ceil(C.beat_of(t1) * div) + 1
    out = []
    for k in range(k0, k1 + 1):
        t = C.beat(k / div)
        if t0 <= t < t1:
            out.append(t)
    return out

def _downs(t0: float, t1: float):
    b0 = math.floor(C.bar_of(t0)) - 1
    b1 = math.ceil(C.bar_of(t1)) + 1
    return [C.bar(b) for b in range(b0, b1 + 1) if t0 <= C.bar(b) < t1]

@lru_cache(maxsize=4)
def _rises(stem: str):
    """[(t, strength)] for the envelope rises of a stem, snapped to the 16th grid where close."""
    env = MUSIC.feat.get(stem)
    if not env:
        return ()
    fps = MUSIC.fps
    lb = max(1, int(round(RISE_LOOKBACK * fps)))
    r = [0.0] * len(env)
    for i in range(lb, len(env)):
        r[i] = env[i] - min(env[i - lb:i])
    out = []
    for i in range(PEAK_HALF, len(env) - PEAK_HALF):
        v = r[i]
        if v < RISE_MIN[stem] or v < max(r[i - PEAK_HALF:i + PEAK_HALF + 1]):
            continue
        t = i / fps
        s16 = C.beat(round(C.beat_of(t) * 4) / 4)
        if abs(s16 - t) <= SNAP:
            t = s16
        if out and t - out[-1][0] < STAB_GAP:
            if v > out[-1][1]:
                out[-1] = (out[-1][0], v)
            continue
        out.append((t, v))
    return tuple(out)

def _pairs(kind: str, t0: float, t1: float):
    if kind in ('stab', 'bassrise'):
        src = _rises('other' if kind == 'stab' else 'bass')
        a = bisect.bisect_left(src, (t0, -1.0))
        b = bisect.bisect_left(src, (t1, -1.0))
        return list(src[a:b])
    if kind in MIN_STRENGTH:
        return [(t, s) for t, s in MUSIC.events(kind, t0, t1) if s >= MIN_STRENGTH[kind]]
    raise KeyError(kind)

def events(kind: str, t0: float, t1: float):
    """Event times of `kind` in [t0, t1)."""
    if kind == 'beat':
        return _grid(1, t0, t1)
    if kind == 'eighth':
        return _grid(2, t0, t1)
    if kind == 'sixteenth':
        return _grid(4, t0, t1)
    if kind == 'down':
        return _downs(t0, t1)
    return [t for t, _s in _pairs(kind, t0, t1)]

def strong(kind: str, t0: float, t1: float, n: int):
    """The n strongest events of an onset kind in [t0, t1), in time order."""
    ps = sorted(_pairs(kind, t0, t1), key=lambda p: -p[1])[:n]
    return sorted((t for t, _s in ps))

def merge(*lists, gap: float=0.06):
    out = []
    for t in sorted((x for lst in lists for x in lst)):
        if not out or t - out[-1] >= gap:
            out.append(t)
    return out

def step(t: float, times, ease_s: float=0.15) -> float:
    """Steps taken by t: the number of events before t, plus the eased fraction of the step that started at the
    latest event (ease-out over ease_s). Use it in place of a linear progress, e.g. layer = step(t, stabs) * 4."""
    k = bisect.bisect_right(times, t)
    if k == 0:
        return 0.0
    return k - 1 + ease.ease_out(ease.prog(t, times[k - 1], times[k - 1] + ease_s))

def arrive(t: float, times, travel: float=0.35) -> float:
    """Nodes reached by t, where the move to node k+1 eases in and out over the `travel` seconds that END on
    event k+1: the picture lands on the event instead of leaving on it (owner 10-04: stop exactly on a node).
    Between landings it holds on the node; keep something moving inside the node (inner(), pad())."""
    k = bisect.bisect_right(times, t)
    if k >= len(times):
        return float(len(times))
    nxt = times[k]
    start = max(nxt - travel, times[k - 1] if k else nxt - travel)
    return k + ease.smooth(ease.prog(t, start, nxt))

def inner(t: float, times) -> float:
    """Seconds since the latest event (0 before the first): the clock for motion inside the node just reached."""
    k = bisect.bisect_right(times, t)
    return t - times[k - 1] if k else 0.0

def pad(t: float, win: float=0.25) -> float:
    """0..1, the sustained harmony (the 'other' and 'bass' stems), averaged over the last `win` s. Owner 10-04:
    the chords keep going between the hits, so inside a held node the motion keeps going at a rate set by this,
    never at zero."""
    n = 6
    acc = 0.0
    for i in range(n):
        u = t - win * i / (n - 1)
        acc += 0.6 * MUSIC.env('other', u) + 0.4 * MUSIC.env('bass', u)
    return max(0.0, min(1.0, acc / n))

def flash(t: float, times, half: float=0.12) -> float:
    k = bisect.bisect_right(times, t)
    if k == 0:
        return 0.0
    return 0.5 ** ((t - times[k - 1]) / half)

def last(t: float, times):
    k = bisect.bisect_right(times, t)
    return times[k - 1] if k else None

def accent(t: float) -> float:
    """1.0 in a bar's first beat, 0.6 in its third, 0.35 in the others (D11 downbeats)."""
    pos = int(math.floor(C.bar_of(t) % 1.0 * 4 + 1e-06))
    return (1.0, 0.35, 0.6, 0.35)[pos % 4]
if __name__ == '__main__':
    for name, (a, b) in WIN.items():
        print('%-10s %7.3f-%7.3f  beat %3d down %2d stab %3d kick %3d snare %3d vocal %3d' % (name, a, b, len(events('beat', a, b)), len(events('down', a, b)), len(events('stab', a, b)), len(events('kick', a, b)), len(events('snare', a, b)), len(events('vocal', a, b))))
    a, b = WIN['interlude1']
    print('interlude1 stabs:', ' '.join(('%.2f' % t for t in events('stab', a, b))))
    print('interlude1 downs:', ' '.join(('%.2f' % t for t in events('down', a, b))))
    a, b = WIN['interlude3']
    print('interlude3 stabs:', ' '.join(('%.2f' % t for t in events('stab', a, b))))
    a, b = WIN['interlude2']
    print('interlude2 kicks:', ' '.join(('%.2f' % t for t in events('kick', a, b))))
