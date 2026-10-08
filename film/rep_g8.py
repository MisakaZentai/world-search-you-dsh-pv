"""r18 (sample_r18/README.md): r17's G and interlude 3 (rep_g7.py) with the reading starting where her old session is
opened. reviewer on r17: interlude 3 still read `08 RESTORE` and `dsh session restore 大肥鱼 --from archive/`, so with
the struck-out model in H the viewer could take it for one more failed restore. From interlude 3's G5 (260.88) on:

  - the header's stage is `08 READ` (tl.STAGES; H under DSH_H=r7 keeps it, no 09);
  - the command line is `$ dsh session read 大肥鱼 --archive` (groups.g_r5._cmd; H adds `--from 1`);
  - the terminal frame's title `you@surface · restore` reads `you@surface · read` (hud.frame, by title).

Switch: DSH_REP=g8 (film.py, after the interludes). Use with DSH_END=story and DSH_H=r7.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import hud
import rep_g7
import tl
from groups import g_r5 as GR5
STAGE = '08 READ'
CMD = '$ dsh session read 大肥鱼 --archive'
TITLES = {'you@surface · restore': 'you@surface · read'}

def install(film):
    rep_g7.install(film)
    tl.STAGES[:] = [(t0, STAGE if n == '08 RESTORE' else n) for t0, n in tl.STAGES]
    cmd0 = GR5._cmd
    GR5._cmd = lambda t: CMD if t >= GR5.G5 else cmd0(t)
    frame0 = hud.frame

    def frame(d, rect, title=None, *a, **k):
        return frame0(d, rect, TITLES.get(title, title), *a, **k)
    hud.frame = frame
    return film
