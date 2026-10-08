"""The dsh pane for the fifth sample (groups/e_pane.py, sample_open_e/README.md): ui/pages/e.py on the fourth
sample's dsh page (importing pages.d_pane points pages.d at the r2 conversation and the stand-ins' thinking rows),
with LongCat's typical speed in the stats pill (speed.py, FACTS X31; D36: LongCat-2.0, FACTS X35).

r2 (sample_open_e/README.md §6): the header's reel follows e_reel (the same schedule as the city's nameplate):
it slows down, lands on her and slips to a stand-in on each syllable of trans-for-ming. When she is the
current name she is in her own blue, not the quiet one.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import cast
import e_reel
import speed
from pages import d_pane as _DP
from pages import e as _E
from pages.common import color, dsh

def reel(t: float) -> str:
    prev, cur, nxt = e_reel.neighbours(t)
    cc = color('her') if cur == 'her' else color(cur)
    side = 'font-size:11px;line-height:15px;height:15px;overflow:hidden;color:'
    sc = lambda k: side + (_E.HER_QUIET if k == 'her' else 'var(--dsw-alias-label-tertiary)')
    return f'<div style="margin-top:3px;width:{_E.REEL_BOX_W}px;border:.5px solid var(--dsw-alias-border-l2);border-radius:7px;padding:1px 8px;background:var(--dsw-alias-bg-base)"><div style="{sc(prev)}">{dsh.esc(cast.name(prev))}</div><div style="display:flex;align-items:center;gap:6px;font-size:14px;line-height:20px;font-weight:600;white-space:nowrap;color:{cc}"><span class="pv-dot" style="background:{cc};width:7px;height:7px;border-radius:50%"></span>{dsh.esc(cast.name(cur))}</div><div style="{sc(nxt)}">{dsh.esc(cast.name(nxt))}</div></div>'
_E.reel = reel

def body(t: float) -> str:
    html = _E.body(t)
    s = speed.tok_s('longcat')
    return html.replace('cloud API', s) if s else html
