"""Music analysis (timing/audio.json, written by tools/analyze.py) sampled at song time.

Same API as the WebGL layer (webgl/.../audio.ts), see tools/DATA.md:

    p.music.env("drums", t)         envelope 0..1 (linear interpolation, 100 fps)
    p.music.env_peak("low", t, .08) max over [t - w, t]: a peak-hold for punchy reactions
    p.music.hit("snare", t, .14)    decaying pulse from the latest onsets, scaled by their strength
    p.music.events("kick", t0, t1)  onsets [(t, strength)] in [t0, t1)
    p.music.section(t)              {"name", "start", "end"} or None
    ctx.a                           p.music.sample(ctx.t): every envelope and pulse at once

Without audio.json every call returns 0 / [] / None (music.available is False), so a film still
renders; scenes that want a fallback can use clock.pulse(t).
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import bisect
import json
import math
from pathlib import Path
FEATURES = ('rms', 'low', 'mid', 'high', 'vocal', 'drums', 'bass', 'other')
PULSES = {'kick': 0.12, 'snare': 0.14, 'hat': 0.06, 'vocal': 0.15}

class Music:

    def __init__(self, d: dict | None=None):
        d = d or {}
        self.available = bool(d)
        self.fps = float(d.get('fps', 100))
        self.duration = float(d.get('duration', 0.0))
        self.sections = d.get('sections', [])
        self.downbeats = d.get('downbeats', [])
        self.first_downbeat = d.get('first_downbeat')
        feats = d.get('features', {})
        self.feat = {k: feats[k] for k in FEATURES if feats.get(k)}
        self.onsets = {k: sorted(((float(t), float(s)) for t, s in v)) for k, v in d.get('onsets', {}).items()}
        self._onset_t = {k: [t for t, _ in v] for k, v in self.onsets.items()}

    @classmethod
    def load(cls, path) -> 'Music':
        path = Path(path)
        return cls(json.loads(path.read_text(encoding='utf-8'))) if path.exists() else cls()

    def env(self, name: str, t: float) -> float:
        a = self.feat.get(name)
        if not a:
            return 0.0
        x = t * self.fps
        i = int(math.floor(x))
        if i < 0:
            return a[0]
        if i >= len(a) - 1:
            return a[-1]
        f = x - i
        return a[i] * (1 - f) + a[i + 1] * f

    def env_peak(self, name: str, t: float, w: float=0.08) -> float:
        n = max(1, int(w * self.fps))
        return max((self.env(name, t - k / self.fps) for k in range(n + 1)))

    def hit(self, kind: str, t: float, half_life: float | None=None) -> float:
        times = self._onset_t.get(kind)
        if not times:
            return 0.0
        hl = half_life or PULSES.get(kind, 0.11)
        k = bisect.bisect_right(times, t)
        v = 0.0
        for i in range(k - 1, max(-1, k - 7), -1):
            ot, s = self.onsets[kind][i]
            dt = t - ot
            if dt > hl * 8:
                break
            v = max(v, s * 0.5 ** (dt / hl))
        return v

    def events(self, kind: str, t0: float, t1: float) -> list:
        times = self._onset_t.get(kind, [])
        a, b = (bisect.bisect_left(times, t0), bisect.bisect_left(times, t1))
        return self.onsets[kind][a:b] if times else []

    def section(self, t: float):
        for s in self.sections:
            if s['start'] <= t < s['end']:
                return s
        return None

    def sample(self, t: float) -> dict:
        """Envelopes by name, drum pulses as kick / snare / hat, the vocal-onset pulse as vonset
        ("vocal" is the vocal envelope)."""
        out = {k: self.env(k, t) for k in FEATURES}
        for k in ('kick', 'snare', 'hat'):
            out[k] = self.hit(k, t)
        out['vonset'] = self.hit('vocal', t)
        return out
