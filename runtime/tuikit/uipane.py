"""A real app's front end as a character pane: page = f(t) -> HTML -> headless screenshot -> layer.

Workflow (see ../UI_PANE.md):
  1. host.html holds the app's own CSS (extracted read-only from its build) and an empty #app.
  2. A batch script defines body(t) -> HTML using the app's real class names and the helpers here,
     then write_frames() dumps one entry per film frame to <name>_frames.json.
  3. `node shot.mjs <name>_frames.json` screenshots every frame to <out_dir>/NNNNN.png
     (frame number n = round(t * fps) is the only key; batches must not overlap).
  4. The film's character layer pastes PaneFrames.layer(t, rect) wherever the shot puts the pane.

No app process, no backend, no model calls: only the front end's look.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import html
import json
import math
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from PIL import Image
from . import ease

def esc(s: str) -> str:
    return html.escape(s, quote=False)

def life(t: float, t_in: float, t_out: float=math.inf, fade_in: float=0.12, fade_out: float=0.25) -> float:
    """0..1 presence of a row that enters at t_in and leaves at t_out."""
    if t < t_in or t >= t_out + fade_out:
        return 0.0
    return min(ease.smooth((t - t_in) / fade_in) if fade_in else 1.0, 1.0 - ease.smooth((t - t_out) / fade_out) if t >= t_out else 1.0)

def show(inner: str, p: float) -> str:
    """Row that grows in/out smoothly (grid-rows trick keeps the timeline layout natural)."""
    if p <= 0:
        return ''
    if p >= 1:
        return inner
    return f'<div style="display:grid;grid-template-rows:{p:.3f}fr;opacity:{p:.3f}"><div style="overflow:hidden;min-height:0">{inner}</div></div>'

def stream(text: str, t: float, start: float, cps: float) -> str:
    """Model output streaming at cps characters per second (tok/s ~= cps / 1.5 for CJK-heavy text)."""
    if t < start:
        return ''
    return text[:int((t - start) * cps)]

def typed_at(t: float, seq: list[tuple[float, str]]) -> str:
    """Human typing as explicit keystrokes: seq = [(time, text_so_far), ...] (supports deletions)."""
    out = ''
    for tt, s in seq:
        if t >= tt:
            out = s
    return out

def keystrokes(text: str, t0: float, step: float) -> list[tuple[float, str]]:
    """One character per step (e.g. a sixteenth note) starting at t0."""
    return [(t0 + i * step, text[:i + 1]) for i in range(len(text))]

def lines_stream(lines: list[str], t: float, start: float, end: float):
    """Thinking rows: lines appear evenly between start and end. Returns (latest_line, running)."""
    if t < start:
        return ('', False)
    if t >= end:
        return (lines[-1], False)
    k = int((t - start) / (end - start) * len(lines))
    return (lines[min(k, len(lines) - 1)], True)

@dataclass
class Flood:
    """Output that has to *feel* like a flood: the rate ramps to `rate` chars/s in `ramp` s.
    ~750 chars/s (~500 tok/s) and ~1100 chars before a limit notice read as overflow; two lines do not."""
    t0: float
    t1: float
    rate: float = 750.0
    ramp: float = 0.3

    def chars(self, t: float) -> int:
        if t <= self.t0:
            return 0
        te = min(t, self.t1) - self.t0
        if te <= self.ramp:
            u = te / self.ramp
            return int(self.rate * self.ramp * (u ** 3 - u ** 4 / 2))
        return int(self.rate * (self.ramp / 2 + (te - self.ramp)))

    def text(self, source: str, t: float) -> str:
        n = self.chars(t)
        if not source:
            return ''
        reps = source * (n // max(1, len(source)) + 1)
        return reps[:n]

def struck_then_typed(t: float, old: str, strike_at: float, type_at: float, new: str, cps: float, hold: float=0.3, collapse: float=0.15, strike_class: str='struck') -> str:
    """A rewrite that reads as a rewrite (not a selection): red-pen strike, hold, fade out, then type."""
    if t < strike_at:
        return esc(old)
    if t < strike_at + hold:
        return f'<span class="{strike_class}">{esc(old)}</span>'
    if t < strike_at + hold + collapse:
        a = 1 - ease.prog(t, strike_at + hold, strike_at + hold + collapse)
        return f'<span class="{strike_class}" style="opacity:{a:.2f}">{esc(old)}</span>'
    return esc(stream(new, t, type_at, cps))

@dataclass
class Event:
    t: float
    kind: str
    data: dict = field(default_factory=dict)
    until: float = math.inf

class EventLog:
    """The chat as a list of timed events; rows(t) renders what is visible at t.
    renderers[kind](event, t) -> HTML (use life()/show() inside for entrances)."""

    def __init__(self):
        self.events: list[Event] = []

    def add(self, t: float, kind: str, until: float=math.inf, **data) -> Event:
        ev = Event(float(t), kind, data, until)
        self.events.append(ev)
        self.events.sort(key=lambda e: e.t)
        return ev

    def visible(self, t: float) -> list[Event]:
        return [e for e in self.events if e.t <= t < e.until + 0.5]

    def rows(self, t: float, renderers: dict) -> str:
        return ''.join((renderers[e.kind](e, t) for e in self.visible(t)))

def write_frames(path, t0: float, t1: float, fps: int, body, page: str='host.html', viewport=(354, 537), out_dir: str='pane_frames', sheets=None, all_sheets=(), scale: int=1) -> int:
    """Dump frames [round(t0*fps), round(t1*fps)) for shot.mjs. body(t) -> HTML for #app.
    sheets(t) -> list of enabled stylesheet ids (optional, for style teardown effects)."""
    frames = []
    for n in range(int(round(t0 * fps)), int(round(t1 * fps))):
        t = n / fps
        f = {'n': n, 't': round(t, 4), 'body': body(t)}
        if sheets:
            f['sheets'] = list(sheets(t))
        frames.append(f)
    spec = {'page': page, 'viewport': {'width': viewport[0], 'height': viewport[1]}, 'scale': scale, 'out_dir': out_dir, 'all_sheets': list(all_sheets), 'frames': frames}
    Path(path).write_text(json.dumps(spec, ensure_ascii=False), encoding='utf-8')
    return len(frames)

class PaneFrames:
    """Screenshots on disk -> a full-frame RGBA layer with the pane placed in a rect."""

    def __init__(self, directory, fps: int, size=(1280, 720)):
        self.dir = Path(directory)
        self.fps = fps
        self.size = size

    @lru_cache(maxsize=16)
    def image(self, n: int):
        p = self.dir / f'{n:05d}.png'
        return Image.open(p).convert('RGBA') if p.exists() else None

    def has(self, t: float) -> bool:
        return (self.dir / f'{int(round(t * self.fps)):05d}.png').exists()

    def layer(self, t: float, rect, alpha: float=1.0) -> Image.Image | None:
        im = self.image(int(round(t * self.fps)))
        if im is None:
            return None
        x0, y0, x1, y1 = rect
        if im.size != (x1 - x0, y1 - y0):
            im = im.resize((x1 - x0, y1 - y0), Image.LANCZOS)
        if alpha < 1:
            im = im.copy()
            im.putalpha(im.getchannel('A').point(lambda v: int(v * alpha)))
        out = Image.new('RGBA', self.size, (0, 0, 0, 0))
        out.paste(im, (x0, y0))
        return out
