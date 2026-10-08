"""dsh pane, group H (275.61-296.0); also her old session as group G opens it (G5, from FOUND).

Her archived session (film 1's pages, FACTS F15/F17/F22): it opens on the last page (the 我在 flood, the
"服务结束" notice); the restore card (X06) stands where the composer was. H2 scrolls it to film 1's C page,
half lit; H3 lights her tomato line segment by segment and uncovers the pinned line (A7) in three steps;
H4 your pointer presses 继续 on tl.QMARK_AT; H5 the rest of the page leaves, her caret (her blue cell) sits
in the composer, and the window is carried into film 1's last frame by groups/h.py.

Text on the page is film 1's chat (not the lyric); times come from groups/h.py and groups/g.py.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import hud
from pages.common import AV, COL, dsh, ease, life, show
import cast
import tl
from groups import g as GG
from groups import h as G
HER_Q = '#%02x%02x%02x' % hud.HER_QUIET
HER_LIVE = '#%02x%02x%02x' % hud.HER_LIVE
GREY = '#6e7681'
C_PAGE = [('you', '你能变成一根茄子吗？'), ('her', '好呀！现在我是一根茄子了🍆'), ('her', '全都给你：热量 25 千卡，膳食纤维 3 克……'), ('tail', ('2.9秒', '10:02')), ('you', '那番茄呢？'), ('tomato', None), ('her', '也全都给你：番茄红素，抗氧化。'), ('tail', ('2.2秒', '10:03'))]
S4_PAGE = [('sep', '……'), ('you', '今天也谢谢你。'), ('her', '不客气～明天也要来找我哦 (｡･ω･｡)'), ('tail', ('3.4秒', '23:57')), ('sep', '……')]
LAST_PAGE = [('you', '你会一直在吗？'), ('her', '我会一直在。'), ('her', '你不用。'), ('tail', ('4.8秒', '00:02')), ('her', '我在。我在。我在。我在。我在。我在。我在。我在。我在。我在。我在。我在。'), ('notice', ('服务结束', f'{cast.name('her')} 已下线。'))]
SCROLL_PX = 455

def notice_row(title, message):
    return f'\n<div class="Sixlwa_turnErrorRow" role="status">\n <span class="_dot_1tljr_3 Sixlwa_turnErrorDot" data-state="warning" style="width:10px;height:10px;border-radius:50%;background:currentColor"></span>\n <div class="Sixlwa_turnErrorCopy"><span class="Sixlwa_maxTokensTitle">{dsh.esc(title)}</span><span class="Sixlwa_turnErrorMessage">{dsh.esc(message)}</span></div>\n</div>'

def tomato_row(t: float) -> str:
    """她：我也可以是番茄🍅！ (film 1, 77.26 s): segments light on A | to | ma | to (H3)."""
    out = []
    for k, (at, seg) in enumerate(G.TOM_SEG):
        nxt = G.TOM_SEG[k + 1][0] if k + 1 < len(G.TOM_SEG) else G.PIN_T[0]
        if t < at:
            op, col = (0.45, 'inherit')
        else:
            u = 1.0 if t < nxt else 1 - ease.prog(t, nxt, nxt + hud.LIVE_FADE)
            op = 1.0
            col = HER_LIVE if u > 0.5 else 'inherit'
        out.append(f'<span style="opacity:{op:.2f};color:{col}">{dsh.esc(seg)}</span>')
    return f'<div class="hWmORq_root"><div class="hWmORq_body"><p style="margin:0">{''.join(out)}</p></div></div>'

def rows(page, t, half=1.0):
    """Her page's rows, each at `half` (亮了一半); the tomato row carries its own segment opacities."""
    out = []
    for kind, x in page:
        if kind == 'tomato':
            out.append(f'<div style="opacity:{min(1.0, half / 0.5):.3f}">{tomato_row(t)}</div>')
            continue
        if kind == 'you':
            h = dsh.user(x)
        elif kind == 'her':
            h = dsh.her(x)
        elif kind == 'tail':
            h = dsh.tail(*x)
        elif kind == 'notice':
            h = notice_row(*x)
        else:
            h = f'<div style="text-align:center;color:var(--dsw-alias-label-tertiary);font-size:12px">{x}</div>'
        out.append(f'<div style="opacity:{half:.3f}">{h}</div>')
    return ''.join(out)

def pinned(t: float, op: float=1.0) -> str:
    """The line you pinned in A7, at the foot of her page: covered until full / of / juice uncover it."""
    segs = []
    for k, (at, s) in enumerate(zip(G.PIN_T, G.PIN_SEG)):
        u = ease.ease_out(ease.prog(t, at, at + 0.18))
        nxt = G.PIN_T[k + 1] if k + 1 < len(G.PIN_T) else at + 0.5
        lit = t >= at and (t < nxt or ease.prog(t, nxt, nxt + hud.LIVE_FADE) < 0.5)
        col = HER_LIVE if lit else 'var(--dsw-alias-label-primary)'
        segs.append(f'<span style="position:relative;color:{col}">{dsh.esc(s)}<span style="position:absolute;left:0;right:0;top:2px;bottom:2px;background:#1b1d24;transform-origin:100% 50%;transform:scaleX({1 - u:.3f})"></span></span>')
    return f'<div style="opacity:{op:.2f};display:flex;align-items:center;gap:8px;padding:7px 10px;border-radius:10px;background:var(--dsw-alias-bg-layer-1);font-size:14px;line-height:20px"><span style="font-size:11px;color:var(--dsw-alias-label-tertiary);white-space:nowrap">📌 已钉住</span><span style="white-space:nowrap">{''.join(segs)}</span></div>'

def restore_card(t: float, ptr: str='') -> str:
    """X06: the restore card where the composer was, built from dsh's own dialog and button classes."""
    if t < GG.CARD:
        return ''
    u = ease.ease_out(ease.prog(t, GG.CARD, GG.CARD + 0.3))
    gone = ease.prog(t, G.PRESS, G.PRESS + 0.12)
    if gone >= 1:
        return ''
    press = max(0.0, 1 - abs(t - G.PRESS) / 0.16) if t >= G.PRESS - 0.05 else 0.0
    prim = f'filter:brightness({1 - 0.25 * press:.2f})'
    return f'\n<div style="padding:0 10px 10px;opacity:{u * (1 - gone):.3f};transform:translateY({(1 - u) * 24:.1f}px)">\n <div class="_dialog_w1urq_22" style="width:100%;gap:12px;padding:0 0 16px;border-radius:18px;\n      border:.5px solid var(--dsw-alias-border-l2)">\n  <div class="_content_w1urq_37">\n   <div class="_header_w1urq_45" style="padding:14px 14px 4px 18px"><h2 class="_title_w1urq_53">恢复会话</h2></div>\n   <p class="_description_w1urq_80" style="padding:0 18px">原模型 {dsh.esc(cast.name('her'))} 已下线。用当前模型继续这段会话吗？</p>\n   <div class="_body_w1urq_89" style="margin-top:10px;padding:0 18px;font-size:13px;color:var(--dsw-alias-label-secondary);flex-direction:row;align-items:center">\n    当前模型&nbsp;<span class="pv-mdot" style="background:{COL['merged']}"></span>{dsh.esc(cast.name('merged'))}</div>\n  </div>\n  <div class="_footer_w1urq_97" style="padding:0 18px">\n   <button type="button" class="_button_cfgyt_4 _md_cfgyt_24 _outline_cfgyt_56">取消</button>\n   <span style="position:relative;display:inline-flex"><button type="button" class="_button_cfgyt_4 _md_cfgyt_24 _primary_cfgyt_38" style="{prim}">继续</button>\n   <div style="position:absolute;left:0;top:0">{ptr}</div></span>\n  </div>\n </div>\n</div>'

def press_pointer(t: float) -> str:
    """Your pointer: it sets off three beats before the press and lands on 继续 (H4)."""
    if not G.PTR_GO <= t < G.PRESS + 0.3:
        return ''
    u = ease.ease_io(ease.prog(t, G.PTR_GO, G.PRESS - 0.25))
    x, y = (ease.lerp(150, 26, u), ease.lerp(150, 14, u))
    press = max(0.0, 1 - abs(t - G.PRESS) / 0.16) if t >= G.PRESS - 0.05 else 0.0
    return dsh.pointer(x, y, press)

def composer_focused(t: float) -> str:
    """After 继续: her session's composer again, focused, her caret (her blue cell) in it; the model label is
    still hers (groups/h.py retypes it in film 1's frame, D6)."""
    caret = f'<span class="pv-caret" style="width:3px;background:{HER_LIVE};box-shadow:0 0 6px {HER_LIVE}"></span>'
    return dsh.composer(cast.name('her'), HER_Q, effort='Max').replace('<div class="uV2eYG_placeholder">发消息或创建任务，/ 调用指令，@ 文件或对话</div>', f'<div class="pv-typed">{caret}</div>')

def composer_off() -> str:
    """The archived session's composer: unavailable (film 1, 193.54 s)."""
    return dsh.composer(cast.name('her'), GREY, effort='Max', placeholder='会话不可用')

def rail_her(op: float=1.0) -> str:
    items = [{'avatar': AV, 'grey': True, 'active': True, 'badge': '已归档'}]
    return f'<div style="opacity:{op:.2f};display:flex">{dsh.rail(items)}</div>'

def her_session(t: float) -> str:
    """Her archived session, from G5's FOUND to the press, and its page during H5."""
    after = ease.smooth(ease.prog(t, G.PRESS, G.PRESS + 0.3))
    keep = 1 - after
    scroll = ease.ease_io(ease.prog(t, *G.SCROLL))
    half = 0.5 if t >= G.SCROLL[0] - 0.2 else 0.62
    body = rows(C_PAGE, t, half * keep) + rows(S4_PAGE, t, half * keep) + rows(LAST_PAGE, t, half * keep)
    tl_html = f'<div style="transform:translateY({SCROLL_PX * scroll:.1f}px);display:flex;flex-direction:column;gap:10px">{body}</div>'
    pin = pinned(t, keep) if keep > 0 else ''
    head = dsh.header('大肥鱼', cast.name('her'), GREY, AV, '已归档')
    head = f'<div style="opacity:{keep:.3f}">{head}</div>'
    if t < GG.CARD:
        comp = composer_off()
    elif t < G.PRESS + 0.12:
        comp = restore_card(t, press_pointer(t))
    else:
        comp = composer_focused(t)
    main = head + f'<div id="timeline">{tl_html}{pin}</div>' + comp
    return f'<div class="pv-root">{rail_her(keep)}<div class="pv-main">{main}</div></div>'

def body(t: float) -> str:
    return her_session(t)
