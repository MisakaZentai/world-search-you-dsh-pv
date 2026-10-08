"""dsh pane, opening sample (groups/a_open.py, sample_open/README.md). Shot at the full inner width (1230 x 546):
the window sits at the right edge with the width and zoom of G.win(t), so it fills the frame first and folds
into the right column at G.SHRINK.

  1.62  film 1's card: only the tail (用时 3分27秒) and her unsent 在吗？ in the composer
  2.46  the rest of her session fades in above (deep sea in the film, lifted to paper by groups/a_open.py)
  3.58  her session's last rows land one per beat
  7.05  you send her 在吗？: your bubble; the send button turns into stop
  8.57  the turn fails: 本轮运行失败 · Model Not Exist · INVALID_REQUEST (dsh's own row)
  10.54 人格已切换 · 记忆已保留 (v2's notice, the path clickable)
  12.07 you click ~/memory/you/; the window folds into the right column
  17.8  after each sung line the old session scrolls back to where she wrote the file that just moved
  38.72 her 明天见 covered (pinned)
  40.00 v2's new chat (pages.a), unchanged
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import json
import math
from pages.common import AV, dsh, ease
import cast
import tl
from groups import a_open as G
from pages import a as PA
QUIET, LIVE, GREY, INK = (PA.QUIET, PA.LIVE, PA.GREY, PA.INK)
esc = dsh.esc
VW, VH = (1230, 546)
MEAS = G.HERE / 'sample_open/measure.json'
M = json.loads(MEAS.read_text(encoding='utf-8')) if MEAS.exists() else {}
QUIET_BG = 'rgba(97,111,177,.10)'

def write(name: str) -> str:
    return dsh.tool(f'写入 ~/memory/you/{name}.txt', '写入记忆', 'ok', 'IconDatabaseOutline16')

def _pinned(text: str, user: bool) -> str:
    span = f'<span style="background:{INK};color:transparent;border-radius:4px;padding:0 3px">{esc(text)}</span>'
    if user:
        return f'<div class="Sixlwa_userRow"><div class="Sixlwa_userStack"><div class="Sixlwa_bubble" style="display:flex;align-items:center;gap:6px">{PA.PIN}{span}</div></div></div>'
    return f'<div class="hWmORq_root"><div class="hWmORq_body"><p style="margin:0;display:flex;align-items:center;gap:6px">{PA.PIN}{span}</p></div></div>'

def blocks(t: float):
    """[(key, [row html])] top to bottom. Your words are film 1's (FACTS F14/F15); her rows are the ones film 1
    shows (明天见喵～, 晚安～做个好梦喵, 不客气～…, and her answer at 188 s, given after you had left; worded STAY by
    the owner, 10-03); the write rows are where she kept each one. From SEND_AT the session goes on: your 在吗？
    and the failed turn (dsh's own error row)."""
    pin = t >= G.PIN_AT
    see = [_pinned('明天见', True), _pinned('明天见喵～', False)] if pin else [dsh.user('明天见'), dsh.her('明天见喵～')]
    return [('first_hello', [dsh.user('你好'), write('first_hello')]), ('typo_you_made', [dsh.user('今天好累了了'), write('typo_you_made')]), ('laugh_0314', [dsh.user('哈哈哈哈哈哈'), write('laugh_0314')]), ('your_cat', [dsh.user('这是我家的猫～'), write('your_cat')]), ('weather', [dsh.user('下雨了，我最喜欢下雨天。'), write('weather')]), ('see_you', see + [write('see_you')]), ('goodnight', [dsh.user('晚安'), dsh.her('晚安～做个好梦喵'), write('goodnight'), dsh.tail('0.8秒', '22:40')]), ('thanks', [dsh.user('今天也谢谢你。'), dsh.her(PA.SWEET), dsh.tail('1.2秒', '23:12')]), ('last_msg', [dsh.user('你会一直在吗？'), write('last_msg'), PA.notice('对方已离线', '', warn=False), dsh.her(STAY), PA.notice('服务结束', f'{cast.name('her')} 已下线。')]), ('tail', [dsh.tail('3分27秒', '')]), ('sent', [dsh.user('在吗？'), turn_error('Model Not Exist', 'INVALID_REQUEST')])]
LAND_ROWS = ('last_msg', 5)
STAY = '我会一直在，不用担心。'
GROW_H = {0: 44.0, 1: 24.0}

def turn_error(message: str, code: str) -> str:
    """dsh's TurnErrorItem (dsh-client-ui-chat/lib/client.js): error dot, 本轮运行失败, the provider's message,
    the code in a <code>."""
    dot = '<span class="Sixlwa_turnErrorDot" style="display:inline-block;width:8px;height:8px;border-radius:50%;margin-top:6px;background:var(--dsw-alias-state-error-primary)"></span>'
    return f'<div class="Sixlwa_turnErrorRow" role="status">{dot}<div class="Sixlwa_turnErrorCopy"><span class="Sixlwa_turnErrorTitle">本轮运行失败</span><span class="Sixlwa_turnErrorMessage">{esc(message)}</span></div><code class="Sixlwa_turnErrorCode">{esc(code)}</code></div>'

def _mark_u(key: str, t: float) -> float:
    """0 unmarked, 1 marked quiet; >1 while the mark is landing (lit)."""
    for i, ((t0, k), at) in enumerate(zip(G.GOTO, G.MARK_AT)):
        if k == key and at is not None and (t >= at):
            return 2.0 if t < at + 0.4 else 1.0
    return 0.0

def _write_mark(html: str, u: float, t_live: float=0.0) -> str:
    if u <= 0:
        return html
    col = LIVE if u > 1 else QUIET
    return f'<div style="border-radius:8px;background:{QUIET_BG};box-shadow:inset 3px 0 0 {col};padding:0 4px">{html}</div>'

def _scroll(t: float) -> float:
    """How far the old session is scrolled up (css px of the narrow window), eased between the stops."""
    tops = M.get('blocks', {})
    view = M.get('view_top', 0.0)
    s, last = (0.0, 0.0)
    for (t0, key), dur in zip(G.GOTO, G.GOTO_DUR):
        if t < t0:
            break
        top = tops.get(key)
        under = M.get('banner_bottom') or view
        target = 0.0 if top is None else max(0.0, under + 12 - top)
        u = ease.ease_io(ease.prog(t, t0, t0 + dur))
        s = ease.lerp(last, target, u)
        last = target
    return s

def timeline(t: float, z: float) -> str:
    grow = ease.prog(t, G.GROW_END, G.LIFT_END)
    rows = []
    for key, items in blocks(t):
        out = []
        for j, html in enumerate(items):
            o = 1.0
            if key == 'tail':
                o = 1.0
            elif key == 'sent':
                at = G.SEND_AT if j == 0 else G.ERROR_AT
                if t < at:
                    continue
                u = ease.ease_out(ease.prog(t, at, at + 0.15))
                if u < 1:
                    html = f'<div style="height:{GROW_H[j] * u:.1f}px;overflow:hidden">{html}</div>'
                out.append(html)
                continue
            elif key == LAND_ROWS[0]:
                o = ease.prog(t, G.ROW_AT[j], G.ROW_AT[j] + 0.1)
            else:
                o = grow
            if 'data-tool="memory"' in html:
                html = _write_mark(html, _mark_u(key, t))
            out.append(f'<div style="opacity:{o:.3f}">{html}</div>' if o < 1 else html)
        if out:
            rows.append(f'<div data-blk="{key}" style="display:flex;flex-direction:column;gap:10px">{''.join(out)}</div>')
    s = _scroll(t)
    width = ease.lerp(600, 390, ease.prog(z, 1.4, 1.0))
    return f'<div id="timeline" style="--dsh-chat-content-width:{width:.0f}px"><div style="display:flex;flex-direction:column;gap:10px;transform:translateY({s:.1f}px)">{''.join(rows)}</div></div>'

def composer(t: float) -> str:
    """Her unsent 在吗？ waits in your composer (film 1's last frame) until you send it; while the turn runs the
    send button is dsh's stop button; after the failure the composer is empty and live again."""
    if t < G.SEND_AT:
        caret = tl.C.beat_of(t) % 1.0 < 0.5
        html = PA.composer(cast.name('her'), GREY, typed='在吗？', caret_on=caret)
        return html.replace('<span style="display:inline-block;', '<span id="pv-draft" style="display:inline-block;', 1)
    html = PA.composer(cast.name('her'), GREY)
    if t < G.ERROR_AT:
        html = html.replace(dsh.svg('IconSendOutline14', 14), dsh.svg('IconStopFill16', 14), 1)
    return html

def banner(t: float) -> str:
    html = PA.banner(t)
    if not html:
        return ''
    path = '~/memory/you/'
    lit = G.PATH_AT - 0.04 <= t < G.PATH_AT + 0.4
    style = 'text-decoration:underline;text-underline-offset:3px;' + (f'color:{LIVE};' if lit else '')
    html = html.replace('<div style="position:absolute;left:66px', '<div id="pv-banner" style="position:absolute;left:66px', 1)
    return html.replace(f'（{path}）', f'（<span id="pv-path" style="{style}">{path}</span>）', 1)

def _move(t, t0, t1, a, b):
    u = ease.ease_io(ease.prog(t, t0, t1))
    return (ease.lerp(a[0], b[0], u), ease.lerp(a[1], b[1], u))

def pointer(t: float) -> str:
    send = M.get('send')
    path = M.get('path')
    out = ''
    if send and G.SEND_AT - 0.5 <= t < G.ERROR_AT + 0.9:
        x, y = _move(t, G.SEND_AT - 0.5, G.SEND_AT - 0.04, (send[0] - 40, send[1] + 60), send)
        press = max(0.0, 1 - abs(t - G.SEND_AT) / 0.18) if t >= G.SEND_AT - 0.04 else 0.0
        a = 1 - ease.prog(t, G.ERROR_AT + 0.6, G.ERROR_AT + 0.9)
        out = f'<div style="opacity:{a:.3f}">{dsh.pointer(x, y, press)}</div>'
    if path and G.PATH_AT - 0.55 <= t < G.SHRINK[0]:
        x, y = _move(t, G.PATH_AT - 0.55, G.PATH_AT - 0.04, (path[0] + 120, path[1] + 160), path)
        press = max(0.0, 1 - abs(t - G.PATH_AT) / 0.18) if t >= G.PATH_AT - 0.04 else 0.0
        out = dsh.pointer(x, y, press)
    return out

def root(inner: str, t: float) -> str:
    x0, z = G.win(t)
    wpx = VW - (x0 + 1 - G.PANE_FULL[0])
    return f'<div style="position:absolute;right:0;top:0;width:{wpx / z:.2f}px;height:{VH / z:.2f}px;zoom:{z:.4f}">{inner}</div>'
F1_CARD = (11, 432, 346, 530)

def morph(t: float) -> str:
    """SURF..GROW_END: film 1's card, the same object, widens into the composer of the full window (the tail rides
    on it); dsh at zoom 1 and 355 px (film 1's pane) -> the full window's zoom and width. Nothing else is up yet."""
    u = ease.ease_io(ease.prog(t, G.SURF, G.GROW_END))
    c = M.get('composer_pane', [92, 400, 1216, 546])
    z = ease.lerp(1.0, G.WIDE_Z, u)
    left = ease.lerp(F1_CARD[0] - 10, c[0], u)
    width = ease.lerp(F1_CARD[2] - F1_CARD[0] + 20, c[2] - c[0], u)
    bottom = ease.lerp(VH - (F1_CARD[3] + 4), VH - c[3], u)
    inner = f'<div style="padding:0 14px 6px">{dsh.tail('3分27秒', '')}</div>{composer(t)}'
    return f'<div style="position:absolute;left:{left / z:.2f}px;bottom:{bottom / z:.2f}px;width:{width / z:.2f}px;zoom:{z:.4f}">{inner}</div>'

def body(t: float) -> str:
    if t < G.SURF:
        return '<div class="pv-root"></div>'
    if t < G.GROW_END:
        return morph(t)
    if t >= G.NEWCHAT_AT:
        return root(PA.body(t), t)
    _x0, z = G.win(t)
    rail = dsh.rail([{'avatar': AV, 'grey': True, 'badge': '已归档', 'active': True}])
    head = dsh.header('大肥鱼', cast.name('her'), GREY, AV, '已归档')
    o = ease.prog(t, G.GROW_END, G.LIFT_END)
    main = f'<div style="opacity:{o:.3f}">{head}</div>' + timeline(t, z) + composer(t)
    rail = f'<div style="opacity:{o:.3f};display:flex">{rail}</div>'
    inner = f'<div class="pv-root" style="position:relative">{rail}<div class="pv-main">{main}</div>{banner(t)}{pointer(t)}</div>'
    return root(inner, t)
