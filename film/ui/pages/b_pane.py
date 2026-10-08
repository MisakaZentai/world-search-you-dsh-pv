"""The dsh pane for the second sample r4 (groups/b_pane.py, sample_open_b/README.md §11): ui/pages/b_open.py with
the model menu saying only where each model runs and the stats pill showing speed.py's typical speed (owner, 10-03:
"不用注明本地放不下，只要写一个本地/云端就好"). A cloud model whose speed is not looked up keeps "cloud API"."""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import cast
import speed
from pages import b_open as _B
from pages.common import color
MENU = [(cast.name('her'), _B.PB.QUIET, '已下线'), (cast.name('kimi'), color('kimi'), '云端'), (cast.name('qwen'), color('qwen'), '本地'), (cast.name('mimo'), color('mimo'), '云端')]

def body(t: float) -> str:
    old = _B.MENU
    _B.MENU = MENU
    try:
        html = _B.body(t)
    finally:
        _B.MENU = old
    k = speed.tok_s('kimi')
    return html.replace('cloud API', k) if k and t < _B.G.SWITCH else html
