"""dsh pane, group C r5 round 2 (2-C item 6, groups/c_lead.py, sample_r5/README.md §4): pages/c_pane.py (r3's C
page, ui/pane_open_c2) with your second MiMo message sent on line 26's "-to" (groups.c_lead.SEE_C, 124.48) instead
of on "human" (125.97), so C sends where G does (groups.g_r5.SEE_SEND, 248.42): G's mirror. Its read row and its
thinking row (发她的头像) move with the send; the image still lands on line 27 (126.36), and everything after it
(用时 0.9 秒, asked_again, the rows D's page continues from) is r3's.

Only the frames whose HTML differs from c_pane's are shot (ui/page_c_r5.py -> ui/pane_c_r5/); c_lead takes the
others from ui/pane_open_c2.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
from groups import c as G
from groups import c_lead as CL
from groups import c_open as GO
from pages import c_pane as _P

def body(t: float) -> str:
    old = (G.SEE_SEND, GO.THINK_SEE)
    G.SEE_SEND = CL.SEE_C
    GO.THINK_SEE = CL.THINK_SEE_C
    try:
        return _P.body(t)
    finally:
        G.SEE_SEND, GO.THINK_SEE = old
