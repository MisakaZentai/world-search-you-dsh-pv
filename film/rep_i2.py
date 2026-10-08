"""r15 sample (sample_r15/README.md, D52): interlude 2 (137.31-151.55) as a new, cute picture (inside/i2_r15.py).

Switch: DSH_I2=gacha (D53, moving) | r15 | stamp | gacha0 | trace (the stills) (film.py, after the interludes and the DSH_REP samples). Only the zoomed forward pane's contents
change (interludes._i2_view): its header, the six tabs and the ↻ count stay r5e's; below them the block figures, the
board of notes and the line take the place of the layer strip and the pile. While the pane opens (137.31) and closes
(151.12) the r5e view (the strip) and this one cross-fade, so the hand-back at 151.55 is r5e's.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
from PIL import Image, ImageDraw
import interludes
from hud import INK, lv
from panes import SUB
import os
from inside import i2_r15 as I2
from inside import i2_concepts as I2C
WHICH = os.environ.get('DSH_I2', 'r15')

def _view(t, Wv, Hv, uu=1.0):
    from groups import d as GD
    W, H = (int(Wv), int(Hv))
    if WHICH == 'r15':
        V = I2.view()
    elif WHICH == 'gacha':
        from inside import i2_gacha
        V = i2_gacha.view()
    else:
        V = I2C.view('gacha' if WHICH == 'gacha0' else WHICH)
    V = Image.fromarray(V.render(t, W, H))
    d = ImageDraw.Draw(V)
    T = GD.turn_at(t)
    interludes._i2_press(d, t, W - 16, 8)
    if WHICH == 'gacha':
        interludes._i2_tabs(d, t, 14, 16, T.i, W - 110)
    else:
        interludes.BMx(d, (14, 12), interludes.BO_left(T.key), 13, lv(INK, SUB))
        interludes._i2_tabs(d, t, 14, 40, T.i, W - 28)
    return V

def install(film):
    orig = interludes._i2_view

    def view(t, Wv, Hv, uu=1.0):
        if uu >= 0.999:
            return _view(t, Wv, Hv)
        a = orig(t, Wv, Hv, uu)
        if uu <= 0.02:
            return a
        return Image.blend(a, _view(t, Wv, Hv), uu)
    interludes._i2_view = view
    return film
