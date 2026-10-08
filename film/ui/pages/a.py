"""dsh pane, group A (0-40.86): her archived session in dsh's light theme, then a new chat. PLAN_A.md.

  1.62  the window appears blank; on the next four beats the rail, the header, the timeline, the composer
  7.05  your pointer clicks into the composer; 大 肥 鱼 ？ one per beat, each bounced back (会话不可用)
  10.54 the persona notice slides in under the header (X08), with 开始新对话
  21.19 one bubble rises through her old session, a step per syllable, and pops on "pops"
  24.8  you scroll up her old session to the exchange of film 1, 98.95 s
  28.32 the window slides out (D2); her sweetest line is pinned (covered) on the beat after "last"
  39.97 back; you click 开始新对话; the first request is typed with the IME (sent in group B)

Local versions of shared pieces (common.page / dsh.composer cannot do these): the header naming no model,
the composer's bounced character and disabled state, the overlay (notice, bubble, pointer). Reported in
the group's notes for merging.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
from pages.common import AV, dsh, ease
import cast
import hud
import syl
import tl
from groups import a as G
QUIET = '#%02x%02x%02x' % hud.HER_QUIET
LIVE = '#%02x%02x%02x' % hud.HER_LIVE
GREY = '#8a8f98'
INK = '#1b1d24'
SWEET = '不客气～明天也要来找我哦 (｡･ω･｡)'
PIN_AT = G.PIN_AT
esc = dsh.esc
COMPOSER_XY = (168, 472)
BUTTON_XY = (150, 148)
BUBBLE_X, BUBBLE_Y0, BUBBLE_DY = (300, 400, 32)
SCROLL = 150
PIN = f'<svg width="13" height="13" viewBox="0 0 13 13" style="flex:none"><circle cx="6.5" cy="4.2" r="3.2" fill="{INK}"/><path d="M6.5 7 L6.5 12.5" stroke="{INK}" stroke-width="1.6" stroke-linecap="round"/></svg>'

def _op(html: str, o: float, cls: str) -> str:
    """Give the first element of class `cls` an opacity (the window lights one block per beat)."""
    if o >= 1:
        return html
    return html.replace(f'class="{cls}"', f'class="{cls}" style="opacity:{o:.3f}"', 1)

def notice(title: str, message: str='', warn: bool=True) -> str:
    """dsh's turn notice row (dot, title, message), as film 1 used it for 服务结束."""
    dot = 'var(--dsw-alias-state-warn-primary)' if warn else 'var(--dsw-alias-label-tertiary)'
    tcls = 'Sixlwa_maxTokensTitle' if warn else 'Sixlwa_turnErrorMessage'
    return f'<div class="Sixlwa_turnErrorRow" role="status"><span class="Sixlwa_turnErrorDot" style="display:inline-block;width:10px;height:10px;border-radius:50%;background:{dot}"></span><div class="Sixlwa_turnErrorCopy"><span class="{tcls}">{esc(title)}</span><span class="Sixlwa_turnErrorMessage">{esc(message)}</span></div></div>'

def sweet_row(t: float) -> str:
    """Her sweetest line; from PIN_AT covered by a slab with a pin (H3 uncovers it)."""
    if t < PIN_AT:
        return dsh.her(SWEET)
    return f'<div class="hWmORq_root"><div class="hWmORq_body"><p style="margin:0;display:flex;align-items:center;gap:6px">{PIN}<span style="background:{INK};color:transparent;border-radius:4px;padding:0 3px">{esc(SWEET)}</span></p></div></div>'

def archived_rows(t: float) -> str:
    """Her archived session, the last rows of film 1 (110.40 you left, 188.49 你不用。, 193.10 服务结束).
    Her 我在。 flood is not shown again (V1-E12)."""
    rows = [dsh.user('晚安'), dsh.her('晚安～做个好梦喵'), dsh.tail('0.8秒', '22:40'), dsh.user('今天也谢谢你。'), sweet_row(t), dsh.tail('1.2秒', '23:12'), dsh.user('你会一直在吗？'), notice('对方已离线', '', warn=False), dsh.her('你不用。'), notice('服务结束', f'{cast.name('her')} 已下线。')]
    return ''.join(rows)

def composer(model: str, color: str, typed: str='', typed_style: str='', caret_on: bool=True, placeholder: str='发消息或创建任务，/ 调用指令，@ 文件或对话', disabled: bool=False, menu: str='') -> str:
    """dsh.composer with what it cannot do: the typed text inside dsh's input box, a style on it (the bounce),
    a disabled card. menu: HTML placed in the trailing group (the model menu, your pointer), as in dsh.composer."""
    caret = f'<span class="pv-caret" style="opacity:{(1 if caret_on else 0.45)}"></span>'
    text = f'<div class="uV2eYG_input"><span style="display:inline-block;{typed_style}">{esc(typed)}</span>{caret}</div>' if typed else f'<div class="uV2eYG_input"></div><div class="uV2eYG_placeholder">{esc(placeholder)}</div>'
    card = ' style="opacity:.62"' if disabled else ''
    return f'\n<div class="uV2eYG_root" id="composer">\n <div class="uV2eYG_card"{card}>\n  <div class="uV2eYG_scroll"><div class="uV2eYG_grow">\n   {text}\n  </div></div>\n  <div class="uV2eYG_row">\n   <div class="uV2eYG_modes" style="display:flex;align-items:center">\n    <button type="button" class="uV2eYG_add">{dsh.svg('IconPlusOutline16', 16)}</button>\n    <button type="button" class="uV2eYG_add">{dsh.svg('IconPaperclipOutline16', 16)}</button>\n   </div>\n   <div class="uV2eYG_trailing pv-rel">\n    <span class="uV2eYG_select" style="background-image:none;display:inline-flex;align-items:center;padding:0">\n     <span class="pv-mdot" style="background:{color}"></span>{esc(model)}</span>\n    <button type="button" class="uV2eYG_primary">{dsh.svg('IconSendOutline14', 14)}</button>\n    {menu}\n   </div>\n  </div>\n </div>\n</div>'

def banner(t: float) -> str:
    """X08: 人格已切换 · 「大肥鱼」已切换到新模型 · 记忆已保留（~/memory/you/）, with 开始新对话."""
    if t < G.NOTICE_AT:
        return ''
    u = ease.ease_out(ease.prog(t, G.NOTICE_AT, G.NOTICE_AT + 0.3))
    y = ease.lerp(-14, 0, u)
    btn = 'display:inline-block;margin:6px 0 0 18px;padding:1px 12px;border-radius:10px;font-size:13px;line-height:22px;border:.5px solid var(--dsw-alias-border-l2);background:var(--dsw-alias-bg-base);color:var(--dsw-alias-label-primary)'
    return f'<div style="position:absolute;left:66px;right:10px;top:{72 + y:.1f}px;opacity:{u:.3f};z-index:4;padding:8px 12px 9px;border-radius:12px;background:var(--dsw-alias-bg-layer-1);border:.5px solid var(--dsw-alias-border-l2);box-shadow:0 4px 14px rgba(20,20,40,.08)">' + notice('人格已切换', '「大肥鱼」已切换到新模型 · 记忆已保留（~/memory/you/）') + f'<span style="{btn}">开始新对话</span></div>'

def bubble(t: float) -> str:
    """A5: one bubble rises through her old session, a step per sung syllable, and pops on "pops" (she is a
    fish; C13 has her bubbles too). Quiet blue while it rises; lit only while it pops (D1)."""
    L = G.L1
    if not L[0] <= t < G.POP_AT + 0.7:
        return ''
    if t < G.POP_AT:
        k = max(0, sum((1 for x in L[:8] if t >= x)) - 1)
        u = ease.ease_out(ease.prog(t, L[k], L[k] + 0.18)) if k else ease.ease_out(ease.prog(t, L[0], L[0] + 0.2))
        yk = lambda j: BUBBLE_Y0 - j * BUBBLE_DY
        xk = lambda j: BUBBLE_X + 7 * math.sin(j * 1.3)
        y = ease.lerp(yk(max(0, k - 1)), yk(k), u) if k else yk(0)
        x = ease.lerp(xk(max(0, k - 1)), xk(k), u) if k else xk(0)
        r = 11 + 1.1 * k
        a = u if k == 0 else 1.0
        return f'<div style="position:absolute;left:{x - r:.1f}px;top:{y - r:.1f}px;width:{2 * r:.1f}px;height:{2 * r:.1f}px;border-radius:50%;corner-shape:round;border:2.5px solid {QUIET};background:rgba(97,111,177,.12);opacity:{a:.3f};z-index:5"></div>'
    p = t - G.POP_AT
    x, y, r = (BUBBLE_X + 7 * math.sin(7 * 1.3), BUBBLE_Y0 - 7 * BUBBLE_DY, 11 + 1.1 * 7)
    col = LIVE if p < 0.3 else QUIET
    out = []
    ur = ease.ease_out(min(1.0, p / 0.25))
    if ur < 1:
        rr = r * (1 + 1.2 * ur)
        out.append(f'<div style="position:absolute;left:{x - rr:.1f}px;top:{y - rr:.1f}px;width:{2 * rr:.1f}px;height:{2 * rr:.1f}px;border-radius:50%;corner-shape:round;border:2px solid {col};opacity:{1 - ur:.3f};z-index:5"></div>')
    ud = ease.ease_out(min(1.0, p / 0.5))
    for j in range(8):
        ang = j * math.pi / 4 + 0.2
        dx, dy = (math.cos(ang) * (r + 22 * ud), math.sin(ang) * (r + 22 * ud) + 6 * ud * ud)
        s = 4.5 - 2 * ud
        out.append(f'<div style="position:absolute;left:{x + dx - s / 2:.1f}px;top:{y + dy - s / 2:.1f}px;width:{s:.1f}px;height:{s:.1f}px;border-radius:50%;background:{col};opacity:{1 - ud:.3f};z-index:5"></div>')
    return ''.join(out)

def pointer(t: float) -> str:
    """Your pointer: into the composer (A2), onto 开始新对话 (interlude)."""
    out = ''
    if G.CLICK_AT - 0.45 <= t < G.BOUNCE_AT[-1] + 0.9:
        u = ease.ease_io(ease.prog(t, G.CLICK_AT - 0.45, G.CLICK_AT - 0.04))
        x = ease.lerp(COMPOSER_XY[0] + 210, COMPOSER_XY[0], u)
        y = ease.lerp(COMPOSER_XY[1] + 70, COMPOSER_XY[1], u)
        press = max(0.0, 1 - abs(t - G.CLICK_AT) / 0.18) if t >= G.CLICK_AT - 0.04 else 0.0
        a = 1 - ease.prog(t, G.BOUNCE_AT[-1] + 0.6, G.BOUNCE_AT[-1] + 0.9)
        out = f'<div style="opacity:{a:.3f}">{dsh.pointer(x, y, press)}</div>'
    t_in = G.FULL_BACK + 0.15
    if t_in <= t < G.NEWCHAT_AT + 0.45:
        u = ease.ease_io(ease.prog(t, t_in, G.NEWCHAT_AT - 0.04))
        x = ease.lerp(BUTTON_XY[0] + 150, BUTTON_XY[0], u)
        y = ease.lerp(BUTTON_XY[1] + 190, BUTTON_XY[1], u)
        press = max(0.0, 1 - abs(t - G.NEWCHAT_AT) / 0.18) if t >= G.NEWCHAT_AT - 0.04 else 0.0
        a = 1 - ease.prog(t, G.NEWCHAT_AT + 0.2, G.NEWCHAT_AT + 0.45)
        out = f'<div style="opacity:{a:.3f}">{dsh.pointer(x, y, press)}</div>'
    return out

def bounced(t: float):
    """A2 (R7's exception): one character per beat goes in and is thrown back on the next 8th."""
    for at, ch in zip(G.BOUNCE_AT, G.BOUNCE_CH):
        back = at + tl.C.BEAT / 2
        if at <= t < back + 0.22:
            if t < back:
                drop = (1 - ease.ease_out(ease.prog(t, at, at + 0.1))) * -6
                return (ch, f'transform:translateY({drop:.1f}px)')
            p = (t - back) / 0.22
            dx = 7 * math.sin(p * math.pi * 4) * (1 - p)
            return (ch, f'transform:translateX({dx:.1f}px);opacity:{1 - ease.ease_in(p):.3f}')
    return ('', '')

def body(t: float) -> str:
    if t < G.PANE_ON:
        return '<div class="pv-root"></div>'
    o = [ease.prog(t, a, a + 0.08) for a in G.PAGE_AT]
    if t < G.NEWCHAT_AT:
        rail = dsh.rail([{'avatar': AV, 'grey': True, 'badge': '已归档', 'active': True}])
        head = dsh.header('大肥鱼', cast.name('her'), GREY, AV, '已归档')
        s = SCROLL * ease.ease_io(ease.prog(t, tl.WE(1, 7) + 0.1, G.FULL_OUT - 0.25))
        rows = f'<div style="display:flex;flex-direction:column;gap:10px;transform:translateY({s:.1f}px)">{archived_rows(t)}</div>'
        ch, style = bounced(t)
        comp = composer(cast.name('her'), GREY, typed=ch, typed_style=style, placeholder='会话不可用', disabled=True)
        main = _op(head, o[1], 'pv-head') + f'<div id="timeline" style="opacity:{o[2]:.3f}">{rows}</div>' + _op(comp, o[3], 'uV2eYG_root')
        overlay = banner(t) + bubble(t) + pointer(t)
        return f'<div class="pv-root">{_op(rail, o[0], 'pv-rail')}<div class="pv-main">{main}</div>{overlay}</div>'
    rail = dsh.rail([{'avatar': AV, 'active': True, 'ring': GREY}, {'avatar': AV, 'grey': True, 'badge': '已归档'}])
    head = dsh.header('大肥鱼', '未分配', GREY, AV, '在线')
    typed = syl.typed(G.KIMI_COMMITS, t)
    comp = composer('未分配', GREY, typed=typed, caret_on=t % 1.06 < 0.53)
    main = head + '<div id="timeline"></div>' + comp + dsh.stats(0, 100)
    return f'<div class="pv-root">{rail}<div class="pv-main">{main}</div>{pointer(t)}</div>'
