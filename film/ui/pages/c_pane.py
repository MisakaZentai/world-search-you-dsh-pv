"""The dsh pane for the third sample r2 (groups/c_pane.py, sample_open_c/README.md §8): ui/pages/c_open.py with the
speeds of speed.py in the stats pill and the menu saying where each model runs (owner, 10-03: where it runs and its
typical tok/s; the local "1.4 tok/s" of the invented CPU situation, FACTS X16, is gone). A cloud model whose speed is not looked up keeps "cloud API"."""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import speed
from pages import c_open as _C
MENU = [(n, c, {'kimi': '云端', 'qwen': '本地 · 当前', 'mimo': '云端'}.get(k, note)) for k, (n, c, note) in zip(('her', 'kimi', 'qwen', 'mimo'), _C.MENU)]

def body(t: float) -> str:
    old, old_menu = (_C.SPEED, _C.MENU)
    _C.SPEED = speed.tok_s('qwen') or old
    _C.MENU = MENU
    try:
        html = _C.body(t)
    finally:
        _C.SPEED, _C.MENU = (old, old_menu)
    cloud = speed.tok_s('mimo')
    return html.replace('cloud API', cloud) if cloud else html
