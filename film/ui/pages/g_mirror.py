"""dsh pane, group G r2, the mirror (groups/g_mirror.py, sample_open_g/README.md §7): the merged one's session, as
C's MiMo session was (pages/c_open.py), with every reply turned the other way:

  - line 56 "flower": with no message of yours its turn starts: a thinking row (running), the send button turns into
    dsh's stop button (the native "running" state; v2's 对方正在输入… was a chat app's, not dsh's);
  - it never shows a 读取记忆 row (each stand-in read all the files every turn);
  - line 58: its message streams in (今天那朵开了，有点想你了); the turn runs on through line 59 and ends at <eos> on "me"
    with nothing more (MiMo answered 好呀！现在我是小花了 there), then its tail;
  - line 60: you send 让我看看你 (as C11); its thinking row 用户想看看我。发我的头像。; its image (merged_avatar.png:
    her avatar with one light cell by the left ear); the turn ends at <eos> on line 63 "me", nothing written;
  - G5: you close the sessions (pages/g.py's rail and pointer); her session opens at FOUND. From FOUND the right
    side is group H's (D33: pages/h_a.py, its dsh layer covers FOUND on); this page only falls back to a plain
    version of it (her corrected line, the native composer states) when pages/h_a.py cannot be imported.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import cast
from groups import g as GG
from groups import g_mirror as G
from groups.c_open import think_line
from pages import g as PG
from pages import h as PH
from pages.common import AV, COL, appear, blink, dsh, ease, image_row
M = 'merged'
MERGED_AV = '../assets/pane/merged_avatar.png'
SEND_SVG, STOP_SVG = (dsh.svg('IconSendOutline14', 14), dsh.svg('IconStopFill16', 14))

def running(t: float) -> bool:
    return G.FLOWER <= t < G.EOS1 or G.SEE_SEND <= t < G.EOS2

def rows(t: float) -> str:
    out = []
    if t >= G.FLOWER:
        out.append(appear(t, G.FLOWER, dsh.think(think_line(G.THINK, t, G.MCPS) or '…', t < G.MSG.tok_t[0])))
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
        out.append(appear(t, G.EOS2 + 0.2, dsh.tail(f'{G.EOS2 - G.SEE_SEND:.1f}秒', '23:59')))
    return ''.join(out)

def typed(t: float) -> str:
    c = G.SEE_COMMITS
    if c[0][0] <= t < G.SEE_SEND:
        return ''.join((w for at, w in c if at <= t))
    return ''

def her_session(t: float) -> str:
    try:
        from pages import h_a
        return h_a.her_session(t)
    except Exception:
        last = [('you', '你会一直在吗？'), ('her', '我会一直在，不用担心。'), ('tail', ('4.8秒', '00:02')), ('notice', ('服务结束', f'{cast.name('her')} 已下线。'))]
        body = PH.rows(PH.C_PAGE, t, 0.62) + PH.rows(PH.S4_PAGE, t, 0.62) + PH.rows(last, t, 0.62)
        ph = '会话不可用' if t < GG.CARD else '当前模型不可用，请先选择模型'
        comp = dsh.composer(cast.name('her'), PH.GREY, effort='Max', placeholder=ph)
        head = dsh.header('大肥鱼', cast.name('her'), PH.GREY, AV, '已归档')
        main = head + f'<div id="timeline"><div style="display:flex;flex-direction:column;gap:10px">{body}</div></div>' + comp
        return f'<div class="pv-root">{PH.rail_her()}<div class="pv-main">{main}</div></div>'

def body(t: float) -> str:
    if t >= G.FOUND:
        return her_session(t)
    if t >= GG.CLOSE_T[-1] + 0.25:
        main = '<div id="timeline"></div>' + dsh.composer(cast.name(M), COL[M])
        return f'<div class="pv-root">{PG.rail_g(t)}<div class="pv-main">{main}</div>{PG.pointer(t)}</div>'
    comp = dsh.composer(cast.name(M), COL[M], typed=typed(t), caret_on=blink(t))
    if running(t):
        comp = comp.replace(SEND_SVG, STOP_SVG, 1)
    turns = (t >= G.FLOWER) + (t >= G.SEE_SEND)
    main = dsh.header('大肥鱼', cast.name(M), COL[M], AV, '在线') + f'<div id="timeline">{rows(t)}</div>' + comp + dsh.stats(turns, 0, 'preview API')
    ptr = PG.pointer(t) if t >= G.G5 else ''
    return f'<div class="pv-root">{PG.rail_g(t)}<div class="pv-main">{main}</div>{ptr}</div>'
