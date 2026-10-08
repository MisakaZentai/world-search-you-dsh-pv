"""dsh pane, group B (40.86-82.95): Kimi K3 wears the persona. PLAN_B.md.

D5 (the model changes the interface's behaviour), twice:
  40.86  her -> Kimi: the header's and the composer's model name and dot change (the avatar does not), 0.2 s
         later its first act is a memory read of her 8 files, then a thinking row (cast.thinking: Kimi K3 always
         thinks, the provider hides the text, X19) until the answer; its answers arrive in chunks; the stats
         pill says "cloud API".
  82.13  Kimi -> the local Qwen (picked in the menu on the downbeat, R9 cut): the black-cat palette, a new chat,
         a memory read of 9 files, then a thinking row (a local thinking model) loading the persona.

Rows come from groups/b.py (the same chunks the terminal shows); nothing restates the lyric.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
from pages.a import QUIET, composer as composer_a
from pages.common import AV, appear, color, dsh, ease, rail, read_row, write_row
import cast
import syl
import tl
from groups import b as G
MENU = [(cast.name('her'), QUIET, '已下线'), (cast.name('kimi'), color('kimi'), '当前'), (cast.name('qwen'), color('qwen'), ''), (cast.name('mimo'), color('mimo'), '')]
QWEN_ROW = 2
LABEL_XY = (33, 17)
QWEN_XY = (-101, -52)
CELL = 'padding:3px 10px;border:.5px solid var(--dsw-alias-border-l2);font-size:14px;line-height:20px;min-width:52px'

def table_html(t: float) -> str:
    """Its table (its habit, X17): the frame arrives with the first cell, then a cell per syllable."""
    if t < G.CELL_AT[0]:
        return ''
    trs = []
    for r, row in enumerate(G.KIMI_TABLE):
        tds = []
        for c, cell in enumerate(row):
            k = r * 3 + c
            txt = dsh.esc(cell) if t >= G.CELL_AT[k] else ''
            bg = 'background:var(--dsw-alias-bg-layer-1);font-weight:600;' if r == 0 else ''
            tds.append(f'<td style="{CELL}{bg}">{txt or '&nbsp;'}</td>')
        trs.append(f'<tr>{''.join(tds)}</tr>')
    return f'<table style="border-collapse:collapse;margin:2px 0">{''.join(trs)}</table>'

def answer1(t: float) -> str:
    parts = [f'<p style="margin:0">{dsh.esc(G.REPLY1)}</p>', table_html(t)]
    txt = G.PERFECT_TABLE.text_at(t)
    if txt:
        parts.append(f'<p style="margin:0">{dsh.esc(txt)}</p>')
    return f'<div class="hWmORq_root"><div class="hWmORq_body" style="gap:10px">{''.join(parts)}</div></div>'

def think_kimi(t: float, at: float, end: float) -> str:
    """D5 / X19 (D21): Kimi K3 always thinks (cast.thinking), the provider hides the text: a thinking row 0.23 s
    after its memory read, running until its answer lands."""
    if t < at:
        return ''
    return appear(t, at, dsh.think(cast.think_rows('kimi')[0], t < end))

def rows_kimi(t: float) -> str:
    out = [appear(t, G.SEND1, dsh.user(G.ASK1)), read_row(t, G.READ1), think_kimi(t, G.READ1 + 0.23, G.REMEMBER_AT)]
    if t >= G.REMEMBER_AT:
        out.append(answer1(t))
    done1 = G.PERFECT_TABLE.done + 0.25
    if t >= done1:
        out.append(appear(t, done1, dsh.tail(f'{G.PERFECT_TABLE.done - G.SEND1:.1f}秒', '23:46')))
    if t >= G.SEND2:
        out.append(appear(t, G.SEND2, dsh.user(G.EGG_ASK)))
        out.append(read_row(t, G.READ2))
        out.append(think_kimi(t, G.READ2 + 0.23, G.EGG.tok_t[0]))
    if t >= G.EGG.tok_t[0]:
        out.append(dsh.her(G.EGG.text_at(t).replace('\u3000', '🍆')))
    done2 = G.EGG.done + 0.2
    if t >= done2:
        out.append(appear(t, done2, dsh.tail(f'{G.EGG.done - G.SEND2:.1f}秒', '23:47')))
    if t >= G.WRITE_EGG:
        out.append(write_row(t, G.WRITE_EGG, 'eggplant_2', color('kimi')))
    return ''.join(out)

def pointer(t: float):
    """Your pointer: opens the model menu on "searching", waits while the terminal fills the frame, then
    goes to the local Qwen and clicks on the downbeat (82.13). Returns (html, hovered row)."""
    t_in = G.MENU_AT - 0.45
    if t_in <= t < G.MENU_AT + 0.3:
        u = ease.ease_io(ease.prog(t, t_in, G.MENU_AT - 0.04))
        x, y = (ease.lerp(LABEL_XY[0] - 130, LABEL_XY[0], u), ease.lerp(LABEL_XY[1] - 170, LABEL_XY[1], u))
        press = max(0.0, 1 - abs(t - G.MENU_AT) / 0.18) if t >= G.MENU_AT - 0.04 else 0.0
        return (dsh.pointer(x, y, press), None)
    if G.MENU_AT + 0.3 <= t < G.SWITCH + 0.4:
        u = ease.ease_io(ease.prog(t, G.NEAR_BACK + 0.5, G.SWITCH - 0.08))
        x, y = (ease.lerp(LABEL_XY[0], QWEN_XY[0], u), ease.lerp(LABEL_XY[1], QWEN_XY[1], u))
        press = max(0.0, 1 - abs(t - G.SWITCH) / 0.16) if t >= G.SWITCH - 0.04 else 0.0
        return (dsh.pointer(x, y, press), QWEN_ROW if u > 0.85 else None)
    return ('', None)

def kimi_page(t: float) -> str:
    ptr, hover = pointer(t)
    menu = ''
    if G.MENU_AT <= t < G.SWITCH + 0.12:
        menu = dsh.menu(MENU, hover, 1.0 - ease.prog(t, G.SWITCH, G.SWITCH + 0.12))
    if ptr:
        menu += f'<div style="position:absolute;left:0;top:0">{ptr}</div>'
    typed = syl.typed(G.EGG_COMMITS, t) if G.EGG_COMMITS[0][0] <= t < G.SEND2 else ''
    comp = composer_a(cast.name('kimi'), color('kimi'), typed=typed, caret_on=t % 1.06 < 0.53, menu=menu)
    turns = (t >= G.SEND1) + (t >= G.SEND2)
    main = dsh.header('大肥鱼', cast.name('kimi'), color('kimi'), AV, '在线') + f'<div id="timeline">{rows_kimi(t)}</div>' + comp + dsh.stats(turns, 100, 'cloud API')
    return f'<div class="pv-root">{rail('kimi')}<div class="pv-main">{main}</div></div>'

def qwen_boot_rows(t: float) -> str:
    """82.13, D5 for the local Qwen: a memory read (9 files), then its thinking row loading the persona.
    Group C can prepend these to its first rows to keep them past 82.955."""
    out = read_row(t, G.READ_Q)
    if t >= G.THINK_Q:
        out += appear(t, G.THINK_Q, dsh.think('加载人格', True))
    return out

def body(t: float) -> str:
    if t < G.SWITCH:
        return kimi_page(t)
    comp = composer_a(cast.name('qwen'), color('qwen'), caret_on=t % 1.06 < 0.53)
    main = dsh.header('大肥鱼', cast.name('qwen'), color('qwen'), AV, '在线') + f'<div id="timeline">{qwen_boot_rows(t)}</div>' + comp + dsh.stats(0, 100)
    return f'<div class="pv-root kuro">{rail('qwen')}<div class="pv-main">{main}</div></div>'
