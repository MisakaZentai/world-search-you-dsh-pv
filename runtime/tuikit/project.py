"""PROJECT.yaml loader: the only place constants come from."""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from PIL import ImageFont
from . import ease
from .audio import Music
from .timing import Clock, Lyrics
FALLBACK_MONO = ['C:/Windows/Fonts/consola.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf']
FALLBACK_CJK = ['C:/Windows/Fonts/msyh.ttc', '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc']

def _read(path: Path) -> dict:
    text = path.read_text(encoding='utf-8')
    if path.suffix in ('.yaml', '.yml'):
        import yaml
        return yaml.safe_load(text)
    return json.loads(text)

def hex_rgb(value) -> tuple:
    if isinstance(value, (list, tuple)):
        return tuple((int(v) for v in value))
    value = value.lstrip('#')
    return tuple((int(value[i:i + 2], 16) for i in (0, 2, 4)))

@dataclass
class Project:
    root: Path
    cfg: dict
    clock: Clock = field(init=False)
    lyrics: Lyrics = field(init=False)

    def __post_init__(self):
        song, video = (self.cfg['song'], self.cfg['video'])
        self.W, self.H = (int(video['width']), int(video['height']))
        self.FPS = int(video['fps'])
        ease.FPS = self.FPS
        self.duration = float(song['duration'])
        bj = self.path(song.get('beats', 'timing/beats.json'))
        self.beats = json.loads(bj.read_text(encoding='utf-8')) if bj.exists() else {}
        for k in ('bpm', 'first_beat', 'hard_cut'):
            if song.get(k) is None and self.beats.get(k) is not None:
                song[k] = self.beats[k]
        if song.get('bpm') is None or song.get('first_beat') is None:
            raise ValueError('song.bpm / song.first_beat: run tools/beats.py or set them in PROJECT.yaml')
        self.music = Music.load(self.path(song.get('analysis', 'timing/audio.json')))
        downbeat = song.get('first_downbeat', self.music.first_downbeat or self.beats.get('first_downbeat'))
        times = self.beats.get('beat_times') if song.get('bpm') == self.beats.get('bpm') else None
        self.clock = Clock(song['bpm'], song['first_beat'], self.FPS, song.get('beats_per_bar', 4), downbeat, times)
        words = self.path(song.get('words') or song.get('lyrics') or 'timing/words.json')
        self.lyrics = Lyrics.load(words) if words.exists() else Lyrics([])
        style = self.cfg.get('style', {})
        self.colors = {k: hex_rgb(v) for k, v in style.get('colors', {}).items()}
        self.colors.setdefault('bg', (4, 7, 15))
        self.colors.setdefault('ink', (200, 214, 234))
        self.colors.setdefault('dim', (58, 74, 107))
        self.colors.setdefault('her', (77, 107, 254))
        self.colors.setdefault('error', (248, 81, 73))
        self.colors.setdefault('anomaly', (227, 179, 65))
        self.style = style

    def path(self, rel) -> Path:
        p = Path(rel)
        return p if p.is_absolute() else self.root / p

    @property
    def audio(self) -> Path:
        return self.path(self.cfg['song']['audio'])

    @property
    def hard_cut(self):
        return self.cfg['song'].get('hard_cut')

    def timing_mismatch(self) -> dict:
        """Where PROJECT.yaml overrides beats.json: {key: (yaml, beats.json)} beyond 1 ms / 0.01 BPM."""
        out, song = ({}, self.cfg['song'])
        for k, tol in (('bpm', 0.01), ('first_beat', 0.001), ('hard_cut', 0.001)):
            a, b = (song.get(k), self.beats.get(k))
            if a is not None and b is not None and (abs(float(a) - float(b)) > tol):
                out[k] = (a, b)
        return out

    def rect(self, name: str) -> tuple:
        return tuple(self.cfg.get('layout', {})[name])

    def has_rect(self, name: str) -> bool:
        return name in self.cfg.get('layout', {})

    def color(self, name: str) -> tuple:
        return self.colors[name]

    def setting(self, key: str, default=None):
        return self.style.get(key, default)

    def font(self, size: int, kind: str='mono'):
        key = {'mono': 'font_mono', 'cjk': 'font_cjk', 'bold': 'font_bold'}.get(kind, kind)
        path = self.style.get(key)
        cands = ([str(self.path(path))] if path else []) + (FALLBACK_CJK if kind == 'cjk' else FALLBACK_MONO)
        return _font(tuple(cands), int(size))

    def tool(self, name: str, default: str) -> str:
        return self.cfg.get('tools', {}).get(name, default)

    @property
    def frames(self) -> int:
        return int(round(self.duration * self.FPS))

@lru_cache(maxsize=256)
def _font(cands: tuple, size: int):
    for c in cands:
        if Path(c).exists():
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()

def load(where) -> Project:
    """Load PROJECT.yaml (or PROJECT.json) from a file path or a project directory."""
    p = Path(where).resolve()
    if p.is_dir():
        for name in ('PROJECT.yaml', 'PROJECT.yml', 'PROJECT.json'):
            if (p / name).exists():
                p = p / name
                break
        else:
            raise FileNotFoundError(f'no PROJECT.yaml in {where}')
    return Project(p.parent, _read(p))
