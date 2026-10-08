"""dsh pane, group H direction A (D33; sample_open_h/README.md §5): her archived session from G5's FOUND to the
press, with dsh's own model block and model menu instead of v2's restore card and pin (X-H1, X-H2 retired).

  273.39 FOUND     her archived session opens on its last rows, the state the opening left it in (pages/a_open.py):
                   ... 我会一直在，不用担心。 / 服务结束 / 用时 3分27秒 / 在吗？ / 本轮运行失败 · Model Not Exist
  275.09 CARD      the composer turns into dsh's block: 当前模型不可用，请先选择模型
                   (dsh-client-ui-model-selection `blocked.composer`, rendered as an inert composer with that
                   placeholder by dsh-client-ui-conversation's ComposerBlockRegistry)
  282.86-283.77    the session scrolls back to film 1's C page (茄子 / 番茄), as v2 did
  you're -> fruit  your pointer goes to the model label and is on it by "fruit"; no click, the menu stays shut
                   (reviewer 5: the choice comes after 明天见); it waits there through tomato and juice
  A | to-ma-to     her tomato line lights a segment a syllable (pages/h.py's tomato_row)
  full..juice      the window is the support side (groups/h_a.py's lead): nothing on it moves
  MENU_AT (289.80) the drums' last bar: you click the label, the model menu opens; the pointer goes onto
                   deepseek-v5-flash-preview, its row lit on the next beat (HOVER_AT 290.23)
  PRESS (290.80)   click: the menu closes, the composer is live again, her caret (her blue cell) in it. The label
                   keeps her old name: groups/h_a.py has her caret retype it in film 1's frame (D6)
  MOVE             the window slides into film 1's frame (groups/h_a.py); the rows leave as it darkens

Text on the page is film 1's chat and the opening's rows (not the lyric); times come from groups/h_a.py.

Called from outside: ui/pages/g_mirror.py (G r2, DSH_G=mirror) calls her_session(t) for t >= groups.g.FOUND.
Keep its name and signature, or tell the G session / the owner.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import hud
from pages.common import AV, COL, color, dsh, ease
from pages import a_open as PO
from pages import h as PH
import cast
from groups import g as GG
from groups import h_a as G
HER_Q = PH.HER_Q
HER_LIVE = PH.HER_LIVE
GREY = PH.GREY
BLOCKED = '当前模型不可用，请先选择模型'
UNAVAILABLE = '会话不可用'
MENU = [(cast.name('her'), HER_Q, '已下线'), (cast.name('merged'), COL['merged'], '云端'), (cast.name('kimi'), color('kimi'), '云端'), (cast.name('qwen'), color('qwen'), '本地'), (cast.name('mimo'), color('mimo'), '云端')]
PICK = 1
LABEL_XY = (82, 17)
PICK_XY = (-40, -112)
C_PAGE = PH.C_PAGE
SEP = [('sep', '……')]

def last_rows():
    """The bottom of her session as the opening left it (pages/a_open.blocks after SEND_AT), from 今天也谢谢你。"""
    keep = ('thanks', 'last_msg', 'tail', 'sent')
    out = []
    for key, items in PO.blocks(PO.G.ERROR_AT + 1.0):
        if key in keep:
            out.extend(items)
    return out
LAST = last_rows()
SCROLL_PX = 375

def menu_html(t: float, hover: int | None) -> str:
    if not G.MENU_AT <= t < G.PRESS + 0.12:
        return ''
    op = ease.prog(t, G.MENU_AT, G.MENU_AT + 0.1) * (1 - ease.prog(t, G.PRESS, G.PRESS + 0.12))
    items = ['<div class="pv-mi" style="font-size:11px;line-height:22px;color:var(--dsw-alias-label-tertiary)">模型</div>']
    for i, (name, col, note) in enumerate(MENU):
        cls = 'pv-mi' + (' hov' if i == hover else '') + (' off' if note == '已下线' else '')
        items.append(f'<div class="{cls}"><span class="pv-mdot" style="background:{col}"></span>{dsh.esc(name)}<span class="pv-note">{dsh.esc(note)}</span></div>')
    return f'<div class="pv-menu" style="opacity:{op:.2f};width:268px;white-space:nowrap">{''.join(items)}</div>'

def pointer(t: float):
    """(html, hovered row): to the label from you're (on it by fruit), wait, click on MENU_AT, onto the pick
    (lit on HOVER_AT), rest, click on PRESS."""
    t_in = G.PTR_IN
    if t < t_in or t >= G.PRESS + 0.35:
        return ('', None)
    if t < G.TO_PICK[0]:
        u = ease.ease_io(ease.prog(t, t_in, G.PTR_AT))
        x, y = (ease.lerp(LABEL_XY[0] - 140, LABEL_XY[0], u), ease.lerp(LABEL_XY[1] - 190, LABEL_XY[1], u))
        press = max(0.0, 1 - abs(t - G.MENU_AT) / 0.12) if t >= G.MENU_AT - 0.04 else 0.0
        return (dsh.pointer(x, y, press), None)
    u = ease.ease_io(ease.prog(t, G.TO_PICK[0], G.TO_PICK[1]))
    x, y = (ease.lerp(LABEL_XY[0], PICK_XY[0], u), ease.lerp(LABEL_XY[1], PICK_XY[1], u))
    press = max(0.0, 1 - abs(t - G.PRESS) / 0.16) if t >= G.PRESS - 0.04 else 0.0
    fade = 1 - ease.prog(t, G.PRESS + 0.15, G.PRESS + 0.35)
    html = dsh.pointer(x, y, press)
    if fade < 1:
        html = f'<div style="opacity:{fade:.2f}">{html}</div>'
    return (html, PICK if t >= G.HOVER_AT else None)

def composer(t: float) -> str:
    ptr, hover = pointer(t)
    menu = menu_html(t, hover)
    if ptr:
        menu += f'<div style="position:absolute;left:0;top:0">{ptr}</div>'
    if t < GG.CARD:
        return dsh.composer(cast.name('her'), GREY, effort='Max', placeholder=UNAVAILABLE, menu=menu)
    if t < G.PRESS:
        k = ease.prog(t, GG.CARD, GG.CARD + 0.2)
        ph = UNAVAILABLE if k < 0.5 else BLOCKED
        html = dsh.composer(cast.name('her'), GREY, effort='Max', placeholder=ph, menu=menu)
        o = abs(1 - 2 * k) if k < 1 else 1.0
        return html.replace('<div class="uV2eYG_placeholder">', f'<div class="uV2eYG_placeholder" style="opacity:{o:.2f}">')
    caret = f'<span class="pv-caret" style="position:absolute;left:0;top:1px;width:3px;background:{HER_LIVE};box-shadow:0 0 6px {HER_LIVE}"></span>'
    html = dsh.composer(cast.name('her'), HER_Q, effort='Max', placeholder=BLOCKED, menu=menu)
    return html.replace(f'<div class="uV2eYG_placeholder">{BLOCKED}</div>', f'<div class="uV2eYG_placeholder" style="color:transparent">{BLOCKED}{caret}</div>')

def her_session(t: float) -> str:
    keep = 1 - ease.smooth(ease.prog(t, G.MOVE[0], G.MOVE[0] + 0.45))
    scroll = ease.ease_io(ease.prog(t, *G.SCROLL))
    half = 0.5 if t >= G.SCROLL[0] - 0.2 else 0.62
    body = PH.rows(C_PAGE, t, half * keep) + PH.rows(SEP, t, half * keep)
    body += ''.join((f'<div style="opacity:{half * keep:.3f}">{h}</div>' for h in LAST))
    tl_html = f'<div style="transform:translateY({SCROLL_PX * scroll:.1f}px);display:flex;flex-direction:column;gap:10px">{body}</div>'
    head = dsh.header('大肥鱼', cast.name('her'), GREY, AV, '已归档')
    head = f'<div style="opacity:{keep:.3f}">{head}</div>'
    main = head + f'<div id="timeline">{tl_html}</div>' + composer(t)
    return f'<div class="pv-root">{PH.rail_her(keep)}<div class="pv-main">{main}</div></div>'

def body(t: float) -> str:
    return her_session(t)
