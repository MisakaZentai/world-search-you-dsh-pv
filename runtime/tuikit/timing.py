"""The three time tables: beats, lines, words.

Code should never hard-code seconds. Use clock.beat(k), lyrics.w(line, i),
lyrics.line(id).start, and the hits list from beats.json.

words.json uses the schema produced by the word-alignment tool
(one entry per sung line, each with its words):

    {"lines": [{"id": 3, "text": "...", "start": 29.7, "end": 31.2,
                "display_end": 31.6,
                "words": [{"line_id": 3, "word_index": 0, "text": "If",
                           "start": 29.72, "end": 29.9, "review_flags": []}]}]}

A lyrics.json with lines but no words also loads (line-level only).
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import bisect
import json
import math
from dataclasses import dataclass, field
from pathlib import Path

class Clock:
    """Beat grid. first_beat is the phase (time of beat 0) in seconds; first_downbeat is the time of
    the first bar line (defaults to first_beat; tools/analyze.py measures it from the drums)."""

    def __init__(self, bpm: float, first_beat: float, fps: int, beats_per_bar: int=4, first_downbeat: float | None=None, beat_times=None):
        self.bpm = float(bpm)
        self.first_beat = float(first_beat)
        self.fps = int(fps)
        self.beats_per_bar = int(beats_per_bar)
        self.BEAT = 60.0 / self.bpm
        self.first_downbeat = self.first_beat if first_downbeat is None else float(first_downbeat)
        self.times = [float(x) for x in beat_times] if beat_times and len(beat_times) > 1 else None
        if self.times:
            self.first_beat = self.times[0]
            self._k0 = round(self.beat_of(self.first_downbeat))

    def beat(self, k: float) -> float:
        """Time of beat k (k may be fractional: k + 0.5 is the off-beat)."""
        T = self.times
        if T is None:
            return self.first_beat + k * self.BEAT
        if k <= 0:
            return T[0] + k * (T[1] - T[0])
        if k >= len(T) - 1:
            return T[-1] + (k - len(T) + 1) * (T[-1] - T[-2])
        i = int(math.floor(k))
        return T[i] + (k - i) * (T[i + 1] - T[i])

    def bar(self, b: float, beat: float=0.0) -> float:
        """Time of beat `beat` of bar b (bar 0 starts at first_downbeat)."""
        if self.times is None:
            return self.first_downbeat + (b * self.beats_per_bar + beat) * self.BEAT
        return self.beat(self._k0 + b * self.beats_per_bar + beat)

    def bar_of(self, t: float) -> float:
        if self.times is None:
            return (t - self.first_downbeat) / (self.BEAT * self.beats_per_bar)
        return (self.beat_of(t) - self._k0) / self.beats_per_bar

    def cut_before(self, t: float, tol: float=0.02) -> float:
        """The last beat at or before t (+tol): where a shot for a line starting at t should begin,
        so the cut never lands after the first sung word."""
        return self.beat(math.floor(self.beat_of(t + tol)))

    def downbeat_near(self, t: float) -> float:
        return self.bar(round(self.bar_of(t)))

    def beat_of(self, t: float) -> float:
        T = self.times
        if T is None:
            return (t - self.first_beat) / self.BEAT
        if t < T[0]:
            return (t - T[0]) / (T[1] - T[0])
        if t >= T[-1]:
            return len(T) - 1 + (t - T[-1]) / (T[-1] - T[-2])
        i = bisect.bisect_right(T, t) - 1
        return i + (t - T[i]) / (T[i + 1] - T[i])

    def snap(self, t: float, div: int=1) -> float:
        """Snap to the nearest 1/div beat (div=2 eighths, 4 sixteenths)."""
        return self.beat(round(self.beat_of(t) * div) / div)

    def pulse(self, t: float, decay: float=0.14) -> float:
        """1.0 on each beat, decaying exponentially until the next."""
        since = t - self.beat(math.floor(self.beat_of(t)))
        return math.exp(-since / decay)

    def frame(self, t: float) -> int:
        return int(round(t * self.fps))

    def on_grid(self, t: float, div: int=2, tol_frames: float=1.0) -> bool:
        return abs(t - self.snap(t, div)) <= tol_frames / self.fps

    @classmethod
    def load(cls, path, fps: int) -> 'Clock':
        d = json.loads(Path(path).read_text(encoding='utf-8'))
        return cls(d['bpm'], d['first_beat'], fps, d.get('beats_per_bar', 4), d.get('first_downbeat'), d.get('beat_times'))

@dataclass
class Word:
    line_id: int
    index: int
    text: str
    start: float
    end: float
    flags: list = field(default_factory=list)
    conf: float | None = None
    syl: list | None = None
    rule: str = ''

@dataclass
class Line:
    id: int
    text: str
    start: float
    end: float
    display_end: float
    words: list

class Lyrics:

    def __init__(self, lines: list[Line]):
        self.lines = sorted(lines, key=lambda l: l.start)
        self.by_id = {l.id: l for l in self.lines}
        self._starts = [l.start for l in self.lines]

    @classmethod
    def load(cls, path) -> 'Lyrics':
        d = json.loads(Path(path).read_text(encoding='utf-8'))
        lines = []
        for i, L in enumerate(d.get('lines', [])):
            lid = L.get('id', i)
            words = [Word(lid, w.get('word_index', j), w['text'], float(w['start']), float(w['end']), list(w.get('review_flags', [])), w.get('conf'), w.get('syl'), w.get('start_rule', '')) for j, w in enumerate(L.get('words', []))]
            start = float(L.get('start', words[0].start if words else 0.0))
            end = float(L.get('end', words[-1].end if words else start))
            lines.append(Line(lid, L['text'], start, end, float(L.get('display_end', end)), words))
        out = cls(lines)
        out.extras = d.get('extras', [])
        out.status = d.get('status', '')
        return out
    extras: list = []
    status: str = ''

    @staticmethod
    def word_progress(w: Word, t: float) -> float:
        """Sung progress of a word: 0 before start, 1 after end, piecewise over syllables when the
        aligner gave them. Karaoke rule: highlight never starts before w.start."""
        if t <= w.start:
            return 0.0
        if t >= w.end:
            return 1.0
        if w.syl and len(w.syl) > 1:
            n = len(w.syl)
            for i, (a, b) in enumerate(w.syl):
                if t < a:
                    return i / n
                if t < b:
                    return (i + (t - a) / max(0.001, b - a)) / n
            return 1.0
        return (t - w.start) / max(0.001, w.end - w.start)

    @classmethod
    def line_char_progress(cls, L: Line, t: float) -> float:
        """Characters of L.text sung so far (for per-glyph wipes)."""
        chars = 0.0
        for w in L.words:
            p = cls.word_progress(w, t)
            chars += p * len(w.text)
            if p < 1:
                break
            chars += 1
        return min(chars, len(L.text))

    def line(self, lid: int) -> Line:
        return self.by_id[lid]

    def w(self, lid: int, i: int) -> float:
        """Onset of word i of line lid. Negative i counts from the end."""
        return self.by_id[lid].words[i].start

    def w_end(self, lid: int, i: int) -> float:
        return self.by_id[lid].words[i].end
    BREAK = 2.0
    TAIL = 1.0

    def next_start(self, L: Line) -> float:
        k = self.lines.index(L)
        return self.lines[k + 1].start if k + 1 < len(self.lines) else math.inf

    def until(self, L: Line) -> float:
        """When line L leaves the screen: at the next line, or TAIL after display_end before a break."""
        nxt = self.next_start(L)
        return nxt if nxt - L.display_end <= self.BREAK else L.display_end + self.TAIL

    def line_at(self, t: float):
        """The line on screen at t (its first onset has passed and it has not been replaced)."""
        k = bisect.bisect_right(self._starts, t) - 1
        if k < 0:
            return None
        L = self.lines[k]
        return L if t < self.until(L) else None

    def word_at(self, t: float):
        L = self.line_at(t)
        if not L:
            return None
        cur = None
        for w in L.words:
            if w.start <= t:
                cur = w
        return cur

    def find(self, text: str, occurrence: int=0):
        """(line_id, word_index) of the n-th word whose text starts with `text` (case-insensitive)."""
        needle, seen = (text.lower(), 0)
        for L in self.lines:
            for w in L.words:
                if w.text.lower().strip(',.!?;:\'"').startswith(needle):
                    if seen == occurrence:
                        return (L.id, w.index)
                    seen += 1
        raise KeyError(text)

def lands(word_t: float, text: str, key: str, cps: float) -> float:
    """Stream start time so that `key` (a substring of text) finishes appearing exactly at word_t
    when text streams at cps characters per second."""
    pos = text.index(key) + len(key)
    return word_t - pos / cps
