"""Where each model runs and its typical speed, as the left shows it (owner, 10-03): "左边无论是否可以本地部署都可以展示
内部，然后也不用注明本地放不下，只要写一个本地/云端就好，然后本地也不需要写3090什么的，只要把典型的高峰时段tok/S写出来
就好了". Sources in FACTS.md X31. None: no figure found, the label shows only where it runs.

  label(key) -> "本地 · ≈50 tok/s" / "云端 · ≈N tok/s" / "云端"
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
SPEED = {'qwen': ('本地', 50), 'kimi': ('云端', 35), 'mimo': ('云端', 43), 'glm': ('云端', 70), 'minimax': ('云端', 85), 'hy4': ('云端', 45), 'ernie': ('云端', None), 'step': ('云端', 195), 'longcat': ('云端', 70)}
SPEED['spark'] = SPEED['step']

def label(key: str) -> str:
    where, v = SPEED.get(key, ('云端', None))
    return f'{where} · ≈{v} tok/s' if v else where

def tok_s(key: str) -> str:
    """'≈50 tok/s' or '' (for dsh's stats pill)."""
    _w, v = SPEED.get(key, ('云端', None))
    return f'≈{v} tok/s' if v else ''
