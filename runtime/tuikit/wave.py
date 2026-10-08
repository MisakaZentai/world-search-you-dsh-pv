"""Real-time waveform for the header: per-millisecond RMS, decoded once with ffmpeg and cached."""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import subprocess
from functools import lru_cache
from pathlib import Path
import numpy as np
from PIL import ImageDraw
RATE = 8000

@lru_cache(maxsize=4)
def rms_ms(audio: str, cache: str, ffmpeg: str='ffmpeg') -> np.ndarray:
    """RMS per 1 ms of the whole song, normalised 0..1. Cached as .npy (records its own rate: 1000/s)."""
    cp = Path(cache)
    if cp.exists():
        return np.load(cp)
    raw = subprocess.run([ffmpeg, '-v', 'error', '-i', audio, '-ac', '1', '-ar', str(RATE), '-f', 's16le', '-'], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    step = RATE // 1000
    n = len(x) // step
    r = np.sqrt((x[:n * step].reshape(n, step) ** 2).mean(axis=1))
    r = r / (np.percentile(r, 99.5) + 1e-09)
    r = np.clip(r, 0, 1).astype(np.float32)
    cp.parent.mkdir(parents=True, exist_ok=True)
    np.save(cp, r)
    return r

def draw(d: ImageDraw.ImageDraw, rect, t: float, env: np.ndarray, color, core, span: float=2.4, pitch: int=3, gamma: float=0.7):
    """Mirrored bars for the last `span` seconds, the playhead ('now') at the right edge."""
    x0, y0, x1, y1 = rect
    mid = (y0 + y1) / 2
    half = (y1 - y0) / 2
    nbar = max(1, (x1 - x0) // pitch)
    for i in range(nbar):
        tt = t - span + span * (i + 1) / nbar
        k = int(tt * 1000)
        if k < 0 or k >= len(env):
            v = 0.0
        else:
            v = float(env[max(0, k - 8):k + 8].mean()) ** gamma
        h = max(1.0, v * half)
        x = x0 + i * pitch
        d.line([(x, mid - h), (x, mid + h)], fill=color)
        if h > 3:
            d.line([(x, mid - h * 0.4), (x, mid + h * 0.4)], fill=core)
