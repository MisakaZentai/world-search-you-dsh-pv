"""The dsh pane for the fourth sample (groups/d_pane.py, sample_open_d/README.md): ui/pages/d.py with
  - the conversation so far from the third sample's page (pages.c_open: Qwen's and MiMo's rows as r2 shows them);
  - each stand-in's thinking row saying what it thinks (groups.d_pane.THINK), not v2's "<think> · hidden by
    provider" (GLM-5.3 returns its reasoning: FACTS "X29 补充（续）");
  - the stats pill showing the model's typical speed (speed.py, FACTS X31) instead of "cloud API".
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import speed
from groups import d as G
from groups import d_pane as GDP
from pages import c_open as PCO
from pages import d as _D
_D.PC = PCO
for _T in G.TURNS:
    if GDP.THINK.get(_T.key):
        _T.rows = list(GDP.THINK[_T.key])

def body(t: float) -> str:
    html = _D.body(t)
    s = speed.tok_s(G.turn_at(t).key if t >= G.ROT_AT[0] else 'mimo')
    return html.replace('cloud API', s) if s else html
