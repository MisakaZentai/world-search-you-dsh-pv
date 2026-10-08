"""dsh pane, group G r5 (batch 4: groups/g_r5.py, REVISE_R4_20261004.md §3.12, D8; sample_r5/README.md): the
mirror's page (pages/g_mirror.py) with r5's times, and one beat that is the window's own:

  - line 57, the bar the "who spoke first" rows had (239.03-240.31): its turn is running with no message of yours
    above it (the thinking row, the stop button, the empty composer). On the downbeat your pointer opens the
    thinking row (dsh's own expanded body, data-expanded + lcKema_thinkBody, as C's stop in pages/c_open.py): its
    three lines, the first clause 没有新消息。 marked on "-li-" (the story's .pv-hl mark, as C's); you fold it again on
    the beat before its message starts (a second click on the chevron), so the timeline is the mirror's again.
  - line 60: you send 让我看看你 on "-to" (groups.g_r5.SEE_SEND, r4 on "human"); its thinking row, its image when it
    is done drawing (AVATAR_AT, as before).
  - the second turn's tail says 12.2 s (r5 round 2, D35): its 用时 from your send on "-to" (248.42) to its <eos>
    (260.665). r5 round 1 kept the mirror's 10.8 s so the seam into G5 would not change a digit; the interlude-3 page
    (pages/i5_g.py) takes the same 12.2 from G5 on. The tail lands one frame before G5 (frame 6261 only).

Only [groups.g_r5.DSH_N0, DSH_N1) is shot (ui/page_g_r5.py -> ui/pane_g_r5/); outside it groups.g_r5 takes
g_mirror's frames, which are the same picture there.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import json
from functools import lru_cache
import cast
from groups import g_mirror as GM
from groups import g_r5 as G
from groups.c_open import think_line
from pages import g as PG
from pages import g_mirror as PM
from pages.common import AV, COL, UI, appear, blink, dsh, ease, image_row
from tuikit.uipane import life, show
if not hasattr(dsh.svg, 'cache_info'):
    dsh.svg = lru_cache(maxsize=None)(dsh.svg)
M = 'merged'
MERGED_AV = PM.MERGED_AV
SEND_SVG, STOP_SVG = (dsh.svg('IconSendOutline14', 14), dsh.svg('IconStopFill16', 14))
_MEAS = json.loads((UI / 'measure.json').read_text(encoding='utf-8')) if (UI / 'measure.json').exists() else {}
CHEV = _MEAS.get('chevron', [16, 6])
HL_BG = 'rgba(86,96,126,{:.3f})'
TAIL2 = f'{G.EOS2 - G.SEE_SEND:.1f}秒'

def running(t: float) -> bool:
    return G.FLOWER <= t < G.EOS1 or G.SEE_SEND <= t < G.EOS2

def think_pointer(t: float) -> str:
    """Your pointer inside the thinking row: in from the lower right on the beat before, clicks the chevron on the
    downbeat (open), rests, clicks again on the beat before its message (fold), and goes."""
    if not G.PTR_GO <= t < G.DSH_CLOSE + 0.5:
        return ''
    tx, ty = CHEV
    tx += 26
    if t < G.DSH_AT:
        u = ease.ease_io(ease.prog(t, G.PTR_GO, G.DSH_AT - 0.06))
        x, y = (ease.lerp(tx + 230, tx, u), ease.lerp(ty + 120, ty, u))
    elif t < G.DSH_CLOSE + 0.1:
        x, y = (tx, ty)
    else:
        u = ease.ease_io(ease.prog(t, G.DSH_CLOSE + 0.1, G.DSH_CLOSE + 0.5))
        x, y = (ease.lerp(tx, tx + 230, u), ease.lerp(ty, ty + 120, u))
    press = 0.0
    for at in (G.DSH_AT, G.DSH_CLOSE):
        if at - 0.04 <= t < at + 0.18:
            press = max(press, 1 - abs(t - at) / 0.18)
    return dsh.pointer(x, y, press)

def think_body(t: float):
    """The expanded body while it is open: its lines so far, 没有新消息。 marked from "-li-"."""
    if not G.DSH_AT <= t < G.DSH_CLOSE:
        return None
    lines = [dsh.esc(think_line([(at, s)], t, G.MCPS)) for at, s in G.THINK if at <= t]
    hl = ease.prog(t, G.HL_AT - 0.02, G.HL_AT + 0.06)
    if hl > 0 and lines:
        head, sep, rest = lines[0].partition('。')
        lines[0] = f'<span class="pv-hl" style="background:{HL_BG.format(0.18 * hl)};color:{COL[M]};font-weight:{(600 if hl > 0.5 else 400)}">{head}{sep}</span>{rest}'
    return show('<br>'.join(lines), life(t, G.DSH_AT, fade_in=0.12))

def rows(t: float) -> str:
    out = []
    if t >= G.FLOWER:
        row = dsh.think(think_line(G.THINK, t, G.MCPS) or '…', t < G.MSG.tok_t[0], think_body(t), pointer=think_pointer(t))
        out.append(appear(t, G.FLOWER, row))
    if t >= G.MSG.tok_t[0]:
        out.append(dsh.her(G.MSG.text_at(t)))
    if t >= G.EOS1 + 0.2:
        out.append(appear(t, G.EOS1 + 0.2, dsh.tail(f'{G.EOS1 - G.FLOWER:.1f}秒', '23:58')))
    if t >= G.SEE_SEND:
        out.append(appear(t, G.SEE_SEND, dsh.user('让我看看你')))
    if t >= G.THINK_SEE[0][0]:
        out.append(dsh.think(think_line(G.THINK_SEE, t, G.MCPS) or '…', t < G.AVATAR_AT))
    if t >= G.AVATAR_AT:
        img = image_row(MERGED_AV, 168).replace('display:block"', 'display:block;filter:saturate(.8)"')
        out.append(appear(t, G.AVATAR_AT, img, fade_in=0.2))
    if t >= G.EOS2 + 0.2:
        out.append(appear(t, G.EOS2 + 0.2, dsh.tail(TAIL2, '23:59')))
    return ''.join(out)

def typed(t: float) -> str:
    c = G.SEE_COMMITS
    if c[0][0] <= t < G.SEE_SEND:
        return ''.join((w for at, w in c if at <= t))
    return ''

def body(t: float) -> str:
    if t >= G.G5:
        return PM.body(t)
    comp = dsh.composer(cast.name(M), COL[M], typed=typed(t), caret_on=blink(t))
    if running(t):
        comp = comp.replace(SEND_SVG, STOP_SVG, 1)
    turns = (t >= G.FLOWER) + (t >= G.SEE_SEND)
    main = dsh.header('大肥鱼', cast.name(M), COL[M], AV, '在线') + f'<div id="timeline">{rows(t)}</div>' + comp + dsh.stats(turns, 0, 'preview API')
    return f'<div class="pv-root">{PG.rail_g(t)}<div class="pv-main">{main}</div></div>'
