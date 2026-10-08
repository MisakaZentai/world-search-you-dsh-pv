"""Chrome: header and lyric band. Drawn once per frame, last, never transformed by any effect.

Lyric band rules (from the owner's review and the director audit):
- a line is laid out whole first, words reveal in place (no re-centring as it grows);
- each word types over clamp(sung length, 0.06, 0.25) s, each character scrambles for SETTLE s;
- the LAST word of every line is whole and still for at least `lyric_hold_frames` before the
  line is replaced: its typing is compressed if needed, but it still starts on the sung onset;
- the band is never blank while a line is sung; before an instrumental break the line lingers,
  then fades.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import random
from dataclasses import dataclass, field
from typing import Callable
from PIL import Image, ImageDraw
from . import ease, glyph, wave
from .glyph import GLITCH, level
SETTLE = 0.08

@dataclass
class WordPlan:
    text: str
    x: float
    t0: float
    td: float
    settle: float
    key: str | None

class Chrome:

    def __init__(self, project, title: str='', band_title: str='stdout', keywords: dict[str, str] | None=None, status: Callable | None=None, chapter: Callable | None=None, waveform: bool=True):
        self.p = project
        self.title = title or project.cfg.get('project', {}).get('title', '')
        self.band_title = band_title
        self.keywords = {k.lower(): v for k, v in (keywords or project.setting('keywords', {}) or {}).items()}
        self.status = status
        self.chapter = chapter
        self.waveform = waveform
        self.hold = project.setting('lyric_hold_frames', 6) / project.FPS
        self._plans: dict[int, list[WordPlan]] = {}
        self._env = None

    def band_font(self):
        return self.p.font(self.p.setting('band_px', 21), 'bold')

    def plan(self, L, font) -> list[WordPlan]:
        if L.id in self._plans:
            return self._plans[L.id]
        d = ImageDraw.Draw(Image.new('RGB', (1, 1)))
        x = 0.0
        plans = []
        switch = self.p.lyrics.until(L)
        for k, w in enumerate(L.words):
            txt = w.text
            td = ease.clamp(w.end - w.start, 0.06, 0.25)
            settle = SETTLE
            if k == len(L.words) - 1:
                n = max(1, len(txt))
                latest = switch - self.hold
                stable = w.start + td * (n - 1) / n + settle
                if stable > latest:
                    room = latest - w.start - settle
                    if room > 0 and n > 1:
                        td = room * n / (n - 1)
                    else:
                        td, settle = (0.0, 0.0)
            key = self.keywords.get(txt.lower().strip(',.!?;:\'"()'))
            plans.append(WordPlan(txt, x, w.start, td, settle, key))
            x += d.textlength(txt + ' ', font=font)
        self._plans[L.id] = plans
        return plans

    def band(self, img: Image.Image, t: float):
        if not self.p.has_rect('lyric_band'):
            return
        x0, y0, x1, y1 = self.p.rect('lyric_band')
        d = ImageDraw.Draw(img)
        bg, ink, her = (self.p.color('bg'), self.p.color('ink'), self.p.color('her'))
        glyph.box(d, (x0, y0, x1, y1), ink, self.band_title, self.p.font(12), 0.8, bg)
        L = self.p.lyrics.line_at(t)
        if L is None or not L.words:
            return
        font = self.band_font()
        alpha = 1.0
        until = self.p.lyrics.until(L)
        if until < self.p.lyrics.next_start(L):
            alpha = 1.0 - ease.prog(t, until - 0.5, until)
        px, py = (x0 + 24, y0 + (y1 - y0 - font.size) // 2 - 2)
        d.text((px - 18, py), '>', font=font, fill=level(her, alpha, bg))
        for wp in self.plan(L, font):
            if t < wp.t0:
                break
            n = len(wp.text)
            shown = []
            for i, ch in enumerate(wp.text):
                ti = wp.t0 + (wp.td * i / n if n else 0)
                if t < ti:
                    break
                if t >= ti + wp.settle or ch in " ,.'":
                    shown.append(ch)
                else:
                    shown.append(random.Random(int(ti * 1000) + ease.tick(t, 48)).choice(GLITCH))
            s = ''.join(shown)
            whole = len(s) == n and s == wp.text
            col = self.p.color(wp.key) if wp.key and wp.key in self.p.colors else ink
            if whole and wp.key:
                tw = d.textlength(s, font=font)
                d.rectangle((px + wp.x - 3, py - 1, px + wp.x + tw + 3, py + font.size + 5), fill=level(col, alpha, bg))
                d.text((px + wp.x, py), s, font=font, fill=bg)
            else:
                d.text((px + wp.x, py), s, font=font, fill=level(col, alpha, bg))

    def header(self, img: Image.Image, t: float, ctx):
        if not self.p.has_rect('header'):
            return
        x0, y0, x1, y1 = self.p.rect('header')
        d = ImageDraw.Draw(img)
        bg, ink, dim, her = (self.p.color(k) for k in ('bg', 'ink', 'dim', 'her'))
        f = self.p.font(14, 'bold')
        cy = (y0 + y1) // 2 - 8
        d.text((x0 + 24, cy), self.title, font=f, fill=ink)
        x = x0 + 24 + d.textlength(self.title + '   ', font=f)
        if self.status:
            for text, cname in self.status(t, ctx):
                d.text((x, cy), text, font=f, fill=self.p.color(cname))
                x += d.textlength(text + '   ', font=f)
        total = self.p.duration
        right = f'{(self.chapter(t, ctx) if self.chapter else '')}   {int(t // 60):02d}:{int(t % 60):02d} / {int(total // 60):02d}:{int(total % 60):02d}'
        rw = d.textlength(right, font=f)
        d.text((x1 - 24 - rw, cy), right, font=f, fill=ink)
        if self.waveform and self.p.audio.exists():
            if self._env is None:
                self._env = wave.rms_ms(str(self.p.audio), str(self.p.path('cache/wave_rms_1ms.npy')), self.p.tool('ffmpeg', 'ffmpeg'))
            wx0, wx1 = (int(x + 10), int(x1 - 40 - rw))
            if wx1 - wx0 > 60:
                wave.draw(d, (wx0, y0 + 10, wx1, y1 - 10), t, self._env, level(her, 0.55, bg), her)
                d.ellipse((wx1 + 3, cy + 5, wx1 + 9, cy + 11), fill=level(her, 0.6 + 0.4 * self.p.clock.pulse(t), bg))
        u = ease.clamp(t / total)
        d.line([(x0, y1 - 1), (x1, y1 - 1)], fill=level(dim, 0.5, bg))
        d.line([(x0, y1 - 1), (x0 + (x1 - x0) * u, y1 - 1)], fill=level(her, 0.8, bg))

    def credits(self, img: Image.Image):
        lines = self.p.cfg.get('credits') or []
        if not lines:
            return
        d = ImageDraw.Draw(img)
        f = self.p.font(11, 'cjk')
        s = '  ·  '.join(lines)
        w = d.textlength(s, font=f)
        d.text((self.p.W - 24 - w, self.p.H - 16), s, font=f, fill=level(self.p.color('ink'), 0.45, self.p.color('bg')))

    def __call__(self, img: Image.Image, t: float, ctx):
        self.header(img, t, ctx)
        self.band(img, t)
        self.credits(img)
