"""dsh pane, group G (233.85-275.61): the merged one's session; then you close the stand-ins' sessions one
by one and open hers (her session itself is drawn by pages/h.py, from groups.g.FOUND).

D5 for the merged one: it starts typing to you with no message of yours before it (对方正在输入…, on
"flower"), it never shows a 读取记忆 row, its thinking row carries no memory read (X11), the stats read
缓存命中 0% (every stand-in recited at 100 %, N08) and `preview API`.
G3's new cell shows on its avatar from un-ru-ly on (assets/pane/merged_avatar.png, one 5 px cell by the
left ear); your pointer rests on it in G4.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
from icons import svg
from pages.common import AV, COL, appear, color, dsh, ease
import cast
import tl
from groups import g as G
from pages import h as PH
M = 'merged'
MERGED_AV = '../assets/pane/merged_avatar.png'

def av_at(t: float) -> str:
    return MERGED_AV if t >= G.UNRULY[0] else AV

def typing(t: float) -> bool:
    spans = [(G.FLOWER, G.MSG.tok_t[0]), (G.SLAB1[0], G.EOS1), (G.G3_BACK + 0.1, G.EOS2)]
    return any((a <= t < b for a, b in spans))

def typing_row(t: float) -> str:
    """对方正在输入… (the dots step on the 8ths, keyed to song time)."""
    if not typing(t):
        return ''
    n = 1 + int(tl.C.beat_of(t) * 2) % 3
    return f'<div style="display:flex;align-items:center;gap:6px;color:var(--dsw-alias-label-tertiary);font-size:13px;line-height:20px;padding:2px 0"><span style="letter-spacing:2px">{'●' * n}{'○' * (3 - n)}</span>对方正在输入…</div>'

def closed_u(t: float, k: int) -> float:
    return ease.ease_io(ease.prog(t, G.CLOSE_T[k], G.CLOSE_T[k] + 0.25))

def rail_g(t: float) -> str:
    """Session rail: the merged one's (active), the stand-ins' (D5 of C: Qwen and Doubao shared one),
    her archived one at the bottom. Smaller items than common.rail so that eleven fit."""
    items = []
    for k, who in enumerate(G.SESSIONS):
        c = closed_u(t, k)
        if c >= 1:
            continue
        av = av_at(t) if who == M else AV
        ring = color(who)
        active = who == M
        hover = 0.0
        if k < len(G.CLOSE_T) and G.CLOSE_T[k] - 0.45 <= t < G.CLOSE_T[k]:
            hover = 1.0
        x = f'<span style="position:absolute;right:-6px;top:-6px;width:14px;height:14px;border-radius:7px;background:var(--dsw-alias-bg-base);border:.5px solid var(--dsw-alias-border-l2);font-size:10px;line-height:13px;text-align:center;color:var(--dsw-alias-label-secondary);opacity:{hover}">×</span>'
        bar = '<span style="position:absolute;left:-12px;top:7px;width:3px;height:16px;border-radius:2px;background:var(--dsw-alias-label-primary)"></span>' if active else ''
        items.append(f'<div style="position:relative;width:30px;height:{30 * (1 - c):.1f}px;margin-bottom:{8 * (1 - c):.1f}px;opacity:{1 - c:.2f}">{bar}<img src="{av}" style="width:30px;height:30px;border-radius:8px;display:block;box-shadow:0 0 0 2px {ring}">{x}</div>')
    her = '<div style="position:relative;width:30px;height:30px"><img src="{}" style="width:30px;height:30px;border-radius:8px;display:block;filter:grayscale(1) brightness(1.08) contrast(.82);opacity:.75"><span class="pv-badge">已归档</span></div>'.format(AV)
    return f'<div class="pv-rail" style="gap:0;padding-top:12px"><div class="pv-new" style="margin-bottom:8px">{svg('IconPlusOutline16', 16)}</div>{''.join(items)}<div style="flex:1"></div>{her}<div style="height:14px"></div></div>'

def pointer(t: float) -> str:
    """Your pointer: on its avatar in G4 (the new cell), then on the rail closing the sessions, then her
    session. Page coordinates (the pane's top-left)."""
    if G.G3_BACK <= t < G.G5:
        u = ease.ease_io(ease.prog(t, G.G3_BACK + 0.2, G.G3_BACK + 0.9))
        return dsh.pointer(ease.lerp(300, 102, u), ease.lerp(200, 40, u))
    if G.G5 <= t < G.FOUND + 0.4:
        pts = [(G.G5 + 0.1, (102, 40))]
        for k, at in enumerate(G.CLOSE_T):
            target = (44, 56) if G.SESSIONS[k] == M else (44, 94)
            pts.append((at - 0.22, target))
            pts.append((at + 0.05, target))
        pts.append((G.FOUND - 0.2, (26, 518)))
        x, y = pts[0][1]
        for (ta, pa), (tb, pb) in zip(pts, pts[1:]):
            if t >= tb:
                x, y = pb
            elif t >= ta:
                u = ease.ease_io(ease.prog(t, ta, tb))
                x, y = (ease.lerp(pa[0], pb[0], u), ease.lerp(pa[1], pb[1], u))
                break
        press = 0.0
        for at in list(G.CLOSE_T) + [G.FOUND]:
            if at - 0.05 <= t < at + 0.16:
                press = max(press, 1 - abs(t - at) / 0.16)
        return dsh.pointer(x, y, press)
    return ''

def merged_rows(t: float) -> str:
    out = []
    out.append(typing_row(t) if t < G.MSG.tok_t[0] else '')
    think = (G.FLOWER + 0.43, G.MSG.tok_t[0])
    if t >= think[0]:
        out.append(appear(t, think[0], dsh.think('想到一件事', t < think[1])))
    if t >= G.MSG.tok_t[0]:
        out.append(dsh.her(G.MSG.text_at(t)))
    done = G.MSG.done + 0.25
    if t >= done:
        out.append(appear(t, done, dsh.tail(f'{G.MSG.done - G.MSG.tok_t[0]:.1f}秒', '23:58')))
    if t >= G.MSG.tok_t[0]:
        out.append(typing_row(t))
    return ''.join(out)

def body(t: float) -> str:
    if t >= G.FOUND:
        return PH.her_session(t)
    closed_all = t >= G.CLOSE_T[-1] + 0.25
    if closed_all:
        head = ''
        rows = ''
        comp = dsh.composer(cast.name(M), COL[M])
        stats = ''
    else:
        state = '正在输入…' if typing(t) else '在线'
        head = dsh.header('大肥鱼', cast.name(M), COL[M], av_at(t), state)
        rows = merged_rows(t)
        comp = dsh.composer(cast.name(M), COL[M])
        stats = dsh.stats(1 if t >= G.MSG.tok_t[0] else 0, 0, 'preview API')
    main = head + f'<div id="timeline">{rows}</div>' + comp + stats
    return f'<div class="pv-root">{rail_g(t)}<div class="pv-main">{main}</div>{pointer(t)}</div>'
