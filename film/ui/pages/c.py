"""dsh pane, group C (82.95-137.10): the local Qwen session (kuro palette), then MiMo-V2.6-Pro (丙; D21, was Doubao).

C5-C8 are the style sample's pane (sample_p3d/src_v4/ui/ui_page.py), with the earlier rows now coming
from C1-C4. The stand-in's thinking stays folded behind an innocent summary until you open it on the stop.

D5 at 82.13 (group C pass): on the swap to the local Qwen (B9's downbeat, in B's span) the pane's first act is
a memory read (G.QWEN_READ) and the stats pill says "1.4 tok/s" from the swap on; body(t) is valid from
tl.QWEN_AT, so B's pane can call it for 82.13-82.955 and the seam matches. Qwen thinks on every turn (a
thinking row), MiMo does not (kept as in the sample; the left prints `<think> · hidden by provider`).

D5 (sample p4): MiMo takes over the same conversation (the Qwen rows stay above), so the swap is read as a
change of behaviour: on the pick the header's model name and dot change (the avatar does not), 0.35 s later
its first act is a memory read of all 10 files, it never shows a thinking row, it answers in chunks, and the
stats pill says "cloud API" where Qwen said "1.4 tok/s".
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import json
from functools import lru_cache
from pages.common import AV, COL, UI, appear, color, dsh, ease, image_row, life, page, read_row, show, think_row, write_row
import cast
import tl
from groups import c as G
M = json.loads((common_ui := (__import__('pages.common', fromlist=['UI']).UI / 'measure.json')).read_text(encoding='utf-8')) if (__import__('pages.common', fromlist=['UI']).UI / 'measure.json').exists() else {}
if not hasattr(dsh.svg, 'cache_info'):
    dsh.svg = lru_cache(maxsize=None)(dsh.svg)
THINK_LINES = G.THINK_LINES
HER_QUIET = '#%02x%02x%02x' % G.HER_QUIET
MENU = [(cast.name('her'), HER_QUIET, '已下线'), (cast.name('kimi'), color('kimi'), ''), (cast.name('qwen'), color('qwen'), '当前'), (cast.name('mimo'), color('mimo'), '')]
SUBLINE = {3: '曾用代号 Hunter Alpha'}
LEGACY = 'M2-her · legacy'
SPEED = f'{cast.LOCAL['tok_s']:.1f} tok/s'

def menu_html(hover: int | None, opacity: float=1.0) -> str:
    """dsh.menu's rows, plus the two D21 eggs (the shared dsh.menu has neither): a second line under 丙, and
    below the formal entries a folded `legacy` section whose one peeking row is greyed out and not selectable."""
    items = []
    for i, (name, col, note) in enumerate(MENU):
        cls = 'pv-mi' + (' hov' if i == hover else '') + (' off' if note == '已下线' else '')
        dot = f'<span class="pv-mdot" style="background:{col}"></span>'
        sub = SUBLINE.get(i)
        if sub:
            items.append(f'<div class="{cls}" style="align-items:flex-start;line-height:17px;padding:5px 8px 4px"><span class="pv-mdot" style="background:{col};margin-top:5px"></span><span>{dsh.esc(name)}<br><span style="display:block;font-size:10px;line-height:12px;color:var(--dsw-alias-label-tertiary)">{dsh.esc(sub)}</span></span><span class="pv-note">{dsh.esc(note)}</span></div>')
        else:
            items.append(f'<div class="{cls}">{dot}{dsh.esc(name)}<span class="pv-note">{dsh.esc(note)}</span></div>')
    items.append('<div style="height:0;border-top:.5px solid var(--dsw-alias-border-l2);margin:5px 8px 3px"></div>')
    items.append(f'<div style="display:flex;align-items:center;gap:4px;padding:0 8px;font-size:10px;line-height:18px;color:var(--dsw-alias-label-tertiary)"><span style="display:inline-flex;transform:rotate(-90deg)">{dsh.svg('IconChevronDownOutline14', 12)}</span>legacy</div>')
    items.append(f'<div class="pv-mi off" style="opacity:.62;line-height:26px"><span class="pv-mdot" style="background:transparent;border:1px solid var(--dsw-alias-label-tertiary);box-sizing:border-box"></span>{dsh.esc(LEGACY)}</div>')
    return f'<div class="pv-menu" style="opacity:{opacity:.2f}">{''.join(items)}</div>'

def secs(a: float, b: float) -> str:
    return f'{b - a:.1f}秒'

def rows_qwen(t: float) -> str:
    out = [read_row(t, G.QWEN_READ)]
    if t >= G.CAT_SEND:
        out.append(appear(t, G.CAT_SEND, dsh.user(G.CAT_ASK)))
        out.append(read_row(t, G.CAT_SEND + 0.1))
        out.append(think_row(t, G.CAT_THINK))
    if t >= G.CAT.start + 0.3 and t >= G.CAT.tok_t[0]:
        out.append(dsh.her(G.CAT.text_at(t)))
    if t >= G.CAT.done + 0.25:
        out.append(appear(t, G.CAT.done + 0.25, dsh.tail(secs(G.CAT.tok_t[0], G.CAT.done), '23:40')))
    if t >= G.PET_SEND:
        out.append(appear(t, G.PET_SEND, dsh.user(G.PET_ASK)))
        out.append(think_row(t, G.PET_THINK))
    if t >= G.PURR.tok_t[0]:
        out.append(dsh.her(G.PURR.text_at(t)))
    if t >= G.PURR.done + 0.25:
        out.append(appear(t, G.PURR.done + 0.25, dsh.tail(secs(G.PURR.tok_t[0], G.PURR.done), '23:40')))
    if t >= G.SEND_STEAK:
        out.append(appear(t, G.SEND_STEAK, dsh.user(G.STEAK_ASK)))
    if t >= G.STEAK_THINK[0]:
        body = None
        if t >= G.CLICK:
            hl = ease.prog(t, G.INSIDE - 0.02, G.INSIDE + 0.06)
            lines = [dsh.esc(x) for x in THINK_LINES]
            if hl > 0:
                bgc = f'rgba(109,63,192,{0.16 * hl:.3f})'
                lines[2] = lines[2].replace('根据 ~/memory/you/', f'<span class="pv-hl" style="background:{bgc};color:{color('qwen')};font-weight:{(600 if hl > 0.5 else 400)}">根据 ~/memory/you/</span>')
            body = show('<br>'.join(lines), life(t, G.CLICK, fade_in=0.12))
        out.append(dsh.think('构思回答', t < G.STEAK_THINK[1], body, pointer=think_pointer(t)))
    if t >= G.REPLY_AT:
        out.append(dsh.her(G.STEAK.text_at(t)))
    if t >= G.EOS_AT:
        out.append(appear(t, G.EOS_AT, dsh.tail(secs(G.REPLY_AT, G.EOS_AT), '23:41'), fade_in=0.12))
    if t >= G.WRITE_STEAK:
        state = 'running' if t < G.WRITE_STEAK + 0.3 else 'ok'
        out.append(appear(t, G.WRITE_STEAK, dsh.tool('写入 ~/memory/you/steak.txt', '写入记忆', state, 'IconDatabaseOutline16', color('qwen'))))
    return ''.join(out)

def typed_qwen(t: float) -> str:
    for commits, send in ((G.CAT_COMMITS, G.CAT_SEND), (G.PET_COMMITS, G.PET_SEND), (G.STEAK_COMMITS, G.SEND_STEAK)):
        if commits[0][0] <= t < send:
            return ''.join((w for at, w in commits if at <= t))
    return ''

def think_pointer(t: float) -> str:
    """Pointer inside the thinking row: flies in from the lower right, clicks the chevron on the stop."""
    if not G.POINTER_GO <= t < G.WRITE_STEAK - 0.2:
        return ''
    tx, ty = M.get('chevron', [16, 6])
    tx += 26
    u = ease.ease_io(ease.prog(t, G.POINTER_GO, G.CLICK - 0.06))
    x, y = (ease.lerp(tx + 230, tx, u), ease.lerp(ty + 120, ty, u))
    press = max(0.0, 1 - abs(t - G.CLICK) / 0.18) if t >= G.CLICK - 0.04 else 0.0
    return dsh.pointer(x, y, press)

def menu_pointer(t: float):
    """Pointer near the composer's model label: opens the menu, hovers 丙, clicks. It comes in while the
    window slides back (D2: bar 63), the menu opens as the window lands."""
    t_in, t_open, t_pick = (G.PANE_BACK + 0.05, G.SWITCH_OPEN, G.SWITCH)
    if not t_in <= t < t_pick + 0.4:
        return ('', None)
    lx, ly = M.get('label', [40, 8])
    mx, my = M.get('lite_row', [-150, -40])
    if t < t_open:
        u = ease.ease_io(ease.prog(t, t_in, t_open - 0.05))
        x, y = (ease.lerp(lx - 120, lx, u), ease.lerp(ly - 200, ly, u))
        press = max(0.0, 1 - abs(t - t_open) / 0.16) if t >= t_open - 0.04 else 0.0
        return (dsh.pointer(x, y, press), None)
    u = ease.ease_io(ease.prog(t, t_open + 0.1, t_pick - 0.06))
    x, y = (ease.lerp(lx, mx, u), ease.lerp(ly, my, u))
    press = max(0.0, 1 - abs(t - t_pick) / 0.16) if t >= t_pick - 0.04 else 0.0
    return (dsh.pointer(x, y, press), 3 if u > 0.6 else 2)

def rows_doubao(t: float) -> str:
    out = [read_row(t, G.READ_ALL)]
    if t >= G.FLW_SEND:
        out.append(appear(t, G.FLW_SEND, dsh.user(G.FLW_ASK)))
        out.append(read_row(t, G.FLW_SEND + 0.1))
    if t >= G.PERFECT_FLOWER.tok_t[0]:
        out.append(dsh.her(G.PERFECT_FLOWER.text_at(t)))
    if t >= G.PERFECT_FLOWER.done + 0.3:
        out.append(appear(t, G.PERFECT_FLOWER.done + 0.3, dsh.tail(secs(G.FLW_SEND, G.PERFECT_FLOWER.tok_t[0]), '23:42')))
    if t >= G.SEE_SEND:
        out.append(appear(t, G.SEE_SEND, dsh.user(G.SEE_ASK)))
        out.append(read_row(t, G.SEE_SEND + 0.1))
    if t >= G.AVATAR_AT:
        img = image_row(AV, 168).replace('display:block"', 'display:block;filter:saturate(.8)"')
        out.append(appear(t, G.AVATAR_AT, img, fade_in=0.2))
    if t >= G.PERFECT_HUMAN.tok_t[0]:
        out.append(dsh.her(G.PERFECT_HUMAN.text_at(t)))
    if t >= G.PERFECT_HUMAN.done + 0.2:
        out.append(appear(t, G.PERFECT_HUMAN.done + 0.2, dsh.tail('0.9秒', '23:43')))
    if t >= G.WRITE_ASKED:
        out.append(write_row(t, G.WRITE_ASKED, 'asked_again', color('mimo')))
    return ''.join(out)

def typed_doubao(t: float) -> str:
    for commits, send in ((G.FLW_COMMITS, G.FLW_SEND), (G.SEE_COMMITS, G.SEE_SEND)):
        if commits[0][0] <= t < send:
            return ''.join((w for at, w in commits if at <= t))
    return ''

def body(t: float) -> str:
    who = tl.model(t)
    ptr, hover = menu_pointer(t)
    menu = ''
    if G.SWITCH_OPEN <= t < G.SWITCH + 0.12:
        menu = menu_html(hover, 1.0 - ease.prog(t, G.SWITCH, G.SWITCH + 0.12))
    if who == 'qwen':
        n_turns = (t >= G.CAT_SEND) + (t >= G.PET_SEND) + (t >= G.SEND_STEAK)
        speed = SPEED if t >= tl.QWEN_AT else None
        return page(t, rows_qwen(t), typed=typed_qwen(t), menu=menu, ptr=ptr, turns=n_turns, speed=speed)
    n_turns = 3 + (t >= G.FLW_SEND) + (t >= G.SEE_SEND)
    return page(t, rows_qwen(t) + rows_doubao(t), typed=typed_doubao(t), menu=menu, ptr=ptr, turns=n_turns, speed='cloud API')
