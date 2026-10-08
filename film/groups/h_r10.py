"""Group H r10 (full film r21; renders/full_r21_review/README.md): r9 (groups/h_r9.py) without the `?`.

  reviewer on full r20 (and my own r18 note): at the chime (tl.QMARK_AT, 290.80) the header's `memory: merged` turned
  into `memory: ?` and the left mem pane's `merged` into `?`. That went with the click on 继续 / the restore; there is
  no click any more and nothing on screen explains the change, so both keep reading `merged` until film 1's frame
  takes the screen (291.94). 主人: "按推荐出 r21，彩蛋不用动" (the egg, G and everything else as r20).

  tl.memory_label and hud.strip read tl.QMARK_AT when they draw, so it is moved past the end here. The times taken
  from it at import (groups.h / h_r5 PRESS, the chime, the slide) were set before and do not move.

Switch: DSH_H=r10 (film.py); DSH_END=story as before.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import tl
from groups import h_r9 as H9
END = H9.END

def register(film):
    tl.QMARK_AT = float('inf')
    H9.register(film)
