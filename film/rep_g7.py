"""r17 (D59, sample_r17/README.md): G and interlude 3 as r14 (rep_g6.py), with the two changes the story asks for.

  - the plate is inside/g_r17.py (r14's, the "=" between the pair's plates taken out);
  - interlude 3's dsh window is re-shot into ui/pane_i5_g_r17 (ui/pages/i5_g_r17.py: the same page, with the merged
    one's name from cast.py, so under DSH_END=story 大肥鱼 instead of deepseek-v5-flash-preview, and `cloud API`
    instead of `preview API`). ui/pane_i5_g is kept as it was;
  - the command line's model chip (groups/g_r5._cmdline, interludes._chip_w) is set in the CJK face when the name is
    CJK (the mono face drew 大肥鱼 as tofu). Both are swapped as module globals here, only under this switch; with a
    Latin name they draw exactly as before.

Switch: DSH_REP=g7 (film.py, after the interludes). Use with DSH_END=story (the names).
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import cast
import hud
import interludes
import tl
from groups import g_r5 as GR5
from groups import d_pane as DP
from inside import g_r17 as G17
from inside import i5_times as I5
from inside.install import Span
from inside.install import install as install_spans

def _cmdline_cjk(d, t, r):
    """groups.g_r5._cmdline, the chip set in the CJK face when the name is CJK (大肥鱼 under DSH_END=story; the
    mono face drew it as tofu), as hud.cmdline does. A Latin name draws exactly as before."""
    hud.tx(d, (36, hud.Y_CMD), GR5._cmd(t), 13, hud.lv(hud.INK, 0.86))
    chip = cast.term(GR5.M)
    cjk = hud.CJK.search(chip)
    f = hud.font(13, chip, True) if cjk else GR5.P.font(13, 'bold')
    w = d.textlength(chip, font=f)
    d.rectangle((r - w - 12, hud.Y_CMD - 3, r, hud.Y_CMD + 17), fill=hud.SLAB)
    d.text((r - w - 6, hud.Y_CMD - (1 if cjk else 0)), chip, font=f, fill=hud.BG)

def _chip_w_cjk(t):
    """interludes._chip_w measured in the face the chip is drawn in."""
    chip = cast.term(tl.model(t))
    if not chip:
        return 0
    f = hud.font(13, chip, True) if hud.CJK.search(chip) else interludes.P.font(13, 'bold')
    return f.getlength(chip) + 12

class _PanesNoPreview:
    """groups.g_r5's view of panes.py: a pane status `云端 · preview` reads `云端` (the merged one is no preview any
    more). Only g_r5 sees this proxy; its G shots lie under the r17 plate, so this is for the record (no v5 drawn
    anywhere, sample_r17/tools/trace_r17_full.json), not for the picture."""

    def __init__(self, mod):
        self._m = mod

    def __getattr__(self, k):
        return getattr(self._m, k)

    def box(self, d, rect, name, t, run=0.0, level=1.0, status='', *a, **k):
        return self._m.box(d, rect, name, t, run, level, '云端' if status == '云端 · preview' else status, *a, **k)

def install(film):
    GR5._cmdline = _cmdline_cjk
    interludes._chip_w = _chip_w_cjk
    GR5.panes = _PanesNoPreview(GR5.panes)
    arch = GR5.BO.ARCH[GR5.M]
    arch['left'] = arch['left'].replace('deepseek-v5-flash-preview', cast.term('merged'))
    interludes._i3_draw = lambda c: None
    t0 = tl.W(56, 0)
    sp = Span('g_r17', t0, I5.FOUND, G17.make, slide_out=0.001, slide_back=I5.I3_BACK, fade_in=0.3, fade_out=0.15, frame_back=I5.TURN_BAR, lift='both')
    old = list(getattr(film, 'inside_spans', []))
    install_spans(film, [sp])
    film.inside_spans = old + [sp]
    film.character = DP.dsh_layer(film, film.character, 'ui/pane_i5_g_r17', I5.G5, I5.FOUND)
    return film
