"""dsh pane, second sample (groups/b_open.py, sample_open/README.md's approach): Kimi K3 wears the persona.

Differences from pages.b (v2):
  - K3's thinking is visible (owner, 10-03): dsh's own thinking row shows the newest line as it streams, running
    until the answer starts (as film 1's G showed her thinking);
  - its first answer is its table (its habit) and then her pattern with 桌子 in it; no 记得！; r2: the pattern
    arrives in four chunks on line 7's first syllables (groups.b_open.REPLY1), as on the left;
  - when its 茄子 lands, the header's avatar puts on film 1's eggplant (avatars/c/eggplant.png, film 1 74.49);
  - the model menu says why the local one: Kimi "2.8T · 本机放不下" (r3: its weights are open, FACTS "X29 补充";
    r1/r2 said "weights: closed", unsourced and wrong), Qwen "可以看里面" (its name already says 本地).
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
from pages import b as PB
from pages.a import composer as composer_a
from pages.common import AV, appear, color, dsh, ease, rail, read_row, write_row
import cast
import syl
from groups import b_open as G
EGG_AV = 'assets/f1_eggplant.png'
MENU = [(cast.name('her'), PB.QUIET, '已下线'), (cast.name('kimi'), color('kimi'), '2.8T · 本机放不下'), (cast.name('qwen'), color('qwen'), '可以看里面'), (cast.name('mimo'), color('mimo'), '')]
CELL = PB.CELL

def table_html(t: float) -> str:
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
    parts = [table_html(t)]
    txt = G.REPLY1.text_at(t)
    if txt:
        parts.append(f'<p style="margin:0">{dsh.esc(txt)}</p>')
    return f'<div class="hWmORq_root"><div class="hWmORq_body" style="gap:10px">{''.join(parts)}</div></div>'

def think(t: float, lines, end: float) -> str:
    """dsh's thinking row with the newest streamed line as its summary; running until the answer starts."""
    if t < lines[0][0]:
        return ''
    return appear(t, lines[0][0], dsh.think(G.think_line(lines, t) or '…', t < end))

def rows_kimi(t: float) -> str:
    out = [appear(t, G.SEND1, dsh.user(G.GB.ASK1)), read_row(t, G.READ1), think(t, G.THINK1, G.ANSWER1_AT)]
    if t >= G.ANSWER1_AT:
        out.append(answer1(t))
    done1 = G.REPLY1.done + 0.25
    if t >= done1:
        out.append(appear(t, done1, dsh.tail(f'{G.REPLY1.done - G.SEND1:.1f}秒', '23:46')))
    if t >= G.SEND2:
        out.append(appear(t, G.SEND2, dsh.user(G.GB.EGG_ASK)))
        out.append(read_row(t, G.READ2))
        out.append(think(t, G.THINK2, G.ANSWER2_AT))
    if t >= G.ANSWER2_AT:
        out.append(dsh.her(G.EGG.text_at(t).replace('\u3000', '🍆')))
    done2 = G.EGG.done + 0.2
    if t >= done2:
        out.append(appear(t, done2, dsh.tail(f'{G.EGG.done - G.SEND2:.1f}秒', '23:47')))
    if t >= G.WRITE_EGG:
        out.append(write_row(t, G.WRITE_EGG, 'eggplant_2', color('kimi')))
    return ''.join(out)

def kimi_page(t: float) -> str:
    ptr, hover = PB.pointer(t)
    menu = ''
    if PB.G.MENU_AT <= t < PB.G.SWITCH + 0.12:
        menu = dsh.menu(MENU, hover, 1.0 - ease.prog(t, PB.G.SWITCH, PB.G.SWITCH + 0.12))
    if ptr:
        menu += f'<div style="position:absolute;left:0;top:0">{ptr}</div>'
    typed = syl.typed(G.GB.EGG_COMMITS, t) if G.GB.EGG_COMMITS[0][0] <= t < G.SEND2 else ''
    comp = composer_a(cast.name('kimi'), color('kimi'), typed=typed, caret_on=t % 1.06 < 0.53, menu=menu)
    turns = (t >= G.SEND1) + (t >= G.SEND2)
    av = EGG_AV if t >= G.DIFF_AT else AV
    head = dsh.header('大肥鱼', cast.name('kimi'), color('kimi'), av, '在线')
    head = head.replace(f'<img src="{EGG_AV}">', f'<img src="{EGG_AV}" style="image-rendering:pixelated">')
    main = head + f'<div id="timeline">{rows_kimi(t)}</div>' + comp + dsh.stats(turns, 100, 'cloud API')
    return f'<div class="pv-root">{rail('kimi')}<div class="pv-main">{main}</div></div>'

def body(t: float) -> str:
    if t < G.SWITCH:
        return kimi_page(t)
    return PB.body(t)
