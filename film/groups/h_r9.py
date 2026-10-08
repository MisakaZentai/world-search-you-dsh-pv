"""Group H r9 (r20 sample; sample_r20/README.md): r8 (groups/h_r8.py) with the egg moved into her card's model selector.

  主人 on r19 (a new model born far right in the black): "不用，按照之前的，一点一点在dsh模型选择那里慢慢打出来就好".
  As v2 H did (groups/h.py, D6, the label retyped in film 1's frame), but after the story, and by nobody: her caret
  stays in the input, blinking at 在吗？ as film 1 has it; the label beside Max changes by itself.

  297.51       the pull-back has settled 0.6 s: her model name in the selector (DeepSeek-V4.1-Flash) is backspaced,
               a character a 64th (film 1 backspaced its beta name the same way at the launch, batch_a1.SWAP)
  298.37 ->    deepseek-v5-flash-preview is typed into the selector a character an 8th (slowly, ~4.7 a second),
               right-aligned beside Max as dsh's label is; the newest character lit, then film 1's label ink
  -> END       the name stays; her caret keeps blinking. No click, no menu, no pointer, nothing else moves.

The film runs longer (END, a beat grid hold after the last character). Switch: DSH_H=r9 (film.py), DSH_END=story for
the names as before; the dsh pane frames are r7's.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import numpy as np
from PIL import Image
import tl
from groups import h as GH
from groups import h_r5 as H5
from groups import h_r8 as H8
from tuikit import ease, glyph
OLD = 'DeepSeek-V4.1-Flash'
NAME = H8.NAME
B0, BEAT = (H8.B0, H8.BEAT)
BACK_AT = B0
BACK_STEP = BEAT / 16
TYPE_AT = H8._b(2)
CHAR_T = [TYPE_AT + i * BEAT / 2 for i in range(len(NAME))]
LAST = CHAR_T[-1]
END = H8._b(17)
assert BACK_AT + len(OLD) * BACK_STEP <= TYPE_AT
assert LAST + 1.0 <= END
INK_COL = H5.LABEL_COL
LIT_COL = (205, 211, 226)
ERASE = (112, 550, GH.LABEL_END + 3, 577)

def label_egg(img: Image.Image, t: float):
    """Film 1's frame with the selector's label at t (in place, on the unzoomed frame)."""
    if t < BACK_AT:
        return
    a = np.asarray(img, np.uint8).copy()
    bg = GH._row_bg(GH.F1_FILES['full'])
    GH._erase(a, ERASE, bg)
    if t < TYPE_AT:
        n = max(0, len(OLD) - (int((t - BACK_AT) / BACK_STEP) + 1))
        if n:
            GH._text(a, OLD[:n], GH.LABEL_END, [INK_COL] * n, bg)
    else:
        n = sum((1 for x in CHAR_T if t >= x))
        cols = []
        for i in range(n):
            off = CHAR_T[i + 1] if i + 1 < len(CHAR_T) else CHAR_T[i] + BEAT / 2
            cols.append(glyph.mix(INK_COL, LIT_COL, 1 - ease.prog(t, off, off + 0.2)))
        if n:
            GH._text(a, NAME[:n], GH.LABEL_END, cols, bg)
    img.paste(Image.fromarray(a))

def register(film):
    H8.register(film, end=END, egg=label_egg)
