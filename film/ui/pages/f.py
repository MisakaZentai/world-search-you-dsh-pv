"""dsh pane, group F (207.0-233.85): the window is out of the frame (the terminal fills it, D2) for the
whole group. If group E leaves the window in place at the seam, it slides out showing E's last page, so F
holds E's last frame (no change inside the window while it leaves)."""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import tl
from pages import e as PE
E_LAST = tl.span('E')[1] - 1.0 / tl.p.FPS

def body(t: float) -> str:
    return PE.body(E_LAST)
