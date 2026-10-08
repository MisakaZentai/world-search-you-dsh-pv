"""dsh pane for r5 batch 3 (groups/d_r5.py; REVISE_R4_20261004.md §3.5): you type to her in dsh's composer.

The conversation, the header and the stats are r4's page (pages.d through pages.d_pane: LongCat's turn, the same
rows); what changes is the composer, which is the stage from 151.55:
  - your text, one character a sung syllable (groups.d_r5.SCRIPT); a character drops in and squashes on landing,
    and in the staccato (166.71-171.90) the text squashes on every kick and snare (groups.d_r5.bounce,
    drum_squash). A backspace really deletes (dsh's composer); the terminal's key log keeps what you deleted.
  - the system IME's candidate window under the caret (笨蛋 / 傻瓜 / 小猪): the highlighted block hops when the
    highlight lands on it (groups.d_r5.ime_state); 155.36 you take 笨蛋, 160.22-163.24 you walk them and take none.
    It belongs to the input method, not to dsh: drawn like a common pinyin IME bar, low-key.
  - the stand-in's grey completion after the caret on the long vowel, an o more on every sung onset (as on the
    terminal's guess board); your next key (165.98) dismisses it.
  - the caret: solid while you type, otherwise on for the first half of every beat (it blinks on the beat where
    you are stuck, 157.38 and 171.72).
  - r4's completion menu on the hum (喜欢 · 好感 · 依赖) and love filling in on the first note (her blue).

Shot at 2x (deviceScaleFactor 2) so the stage can show the page at twice its size without blur:
  cd <local-production-path>
  set PYTHONPATH=<local-production-path>
  python -c "import sys; sys.path[:0]=['ui','.']; from pages import d_r5; d_r5.write()"
  node <local-production-path> ui/frames_D_r5.json
-> ui/frames_D_r5.json, ui/pane_d_r5/NNNNN.png (frames groups.d_r5.N_R5 .. N_E - 1).
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
from functools import lru_cache
from pages.common import AV, color, dsh, ease
from pages import d as _D
from pages import d_pane as _DP
import cast
import speed
import tl
from groups import d as G
from groups import d_r5 as R
from icons import svg as _svg_raw
svg = lru_cache(maxsize=None)(_svg_raw)
HER_LIVE, HER_QUIET = (_D.HER_LIVE, _D.HER_QUIET)
CJK_W = 16
LINE_H = 26
INPUT_PAD_X, INPUT_PAD_Y, CARD_PAD_Y = (14, 4, 8)

def _char(ch: str, t: float, t_in: float) -> str:
    b = R.bounce(t - t_in)
    sx, sy = R.drum_squash(t)
    dy = 0.0
    if b is not None:
        dy, bx, by = b
        sx, sy = (sx * bx, sy * by)
    if abs(dy) < 0.05 and abs(sx - 1) < 0.004 and (abs(sy - 1) < 0.004):
        return dsh.esc(ch)
    return f'<span style="display:inline-block;transform:translateY({dy:.2f}px) scale({sx:.3f},{sy:.3f});transform-origin:50% 88%">{dsh.esc(ch)}</span>'

def _ghost(t: float) -> str:
    """The stand-in's completion, grey, after the caret: dope, an o more on every onset (the newest o hops)."""
    if not G.DOPE_AT <= t < R.STRIKE_AT:
        return ''
    word, n, _new = R.dope_word(t)
    out = ['<span style="color:var(--dsw-alias-label-tertiary)">d']
    for j in range(n):
        dy = -4.0 * R.hop(t - R.DOPE_OS[j], 0.2) if j > 0 else 0.0
        out.append(f'<span style="position:relative;top:{dy:.2f}px">o</span>' if dy else 'o')
    out.append('pe</span>')
    return ''.join(out)

def _caret(t: float) -> str:
    on = R.caret_on(t)
    return f'<span class="pv-caret" style="opacity:{(1 if on else 0)}"></span>'

def typed(t: float):
    """(inner HTML of the composer's text box, caret line index, caret x in px from the text's left)."""
    rows = [[], [], []]
    for u in R.UNITS:
        if u['t_in'] <= t < u['t_out']:
            rows[u['line']].append(u)
    n = max([u['line'] for u in R.UNITS if u['t_in'] <= t] + [0]) + 1
    html, cx = ([], 0.0)
    for li in range(n):
        s = ''.join((_char(u['ch'], t, u['t_in']) for u in rows[li]))
        if li == n - 1:
            cx = sum((CJK_W * len(u['ch']) for u in rows[li]))
            if t >= G.LOVE_AT:
                colr = HER_LIVE if t < G.LOVE_NOTES[1] else HER_QUIET
                s += f'<span style="color:{colr};font-weight:600">love</span>'
            else:
                s += _caret(t) + _ghost(t)
        html.append(s)
    return ('<br>'.join(html), n - 1, cx)

def _ime(t: float, line: int, cx: float) -> str:
    st = R.ime_state(t)
    if st is None:
        return ''
    hl, since, picked = st
    if picked:
        cx = sum((CJK_W * len(u['ch']) for u in R.UNITS if u['line'] == line and u['t_in'] < R.IME1_PICK <= u['t_out']))
    left = INPUT_PAD_X + cx - 6
    top = CARD_PAD_Y + INPUT_PAD_Y + LINE_H * (line + 1)
    cells = []
    for k, w in enumerate(R.IME_WORDS):
        on = k == hl
        sc = 1.0
        if on:
            u = t - since
            amp = 0.16 if picked else 0.1
            sc = 1 + amp * math.exp(-u / 0.07) * math.cos(2 * math.pi * u / 0.2) if u < 0.4 else 1.0
        bg = 'background:rgba(29,32,41,.09);' if on else ''
        cells.append(f'<span style="display:inline-flex;align-items:baseline;gap:2px;padding:2px 6px;border-radius:4px;{bg}transform:scale({sc:.3f});transform-origin:50% 50%"><span style="font-size:9px;color:var(--dsw-alias-label-tertiary)">{k + 1}</span><span style="font-size:12px;color:var(--dsw-alias-label-primary);{('font-weight:600;' if on else '')}">{dsh.esc(w)}</span></span>')
    arrows = '<span style="margin-left:3px;font-size:10px;color:var(--dsw-alias-label-tertiary);letter-spacing:2px">‹ ›</span>'
    return f'<div style="position:absolute;left:{left:.1f}px;top:{top:.1f}px;z-index:20;display:flex;align-items:center;gap:1px;padding:0 3px;background:#fff;border:.5px solid rgba(29,32,41,.18);border-radius:6px;box-shadow:0 2px 6px rgba(20,20,40,.10);white-space:nowrap;line-height:14px">{''.join(cells)}{arrows}</div>'

def _completion_menu(t: float) -> str:
    """r4's completion menu on the hum (pages.d.completion_menu), narrowed (D36, 2-X's note: at 236 px it covered
    your three lines, 174.0): 140 px, still opening up from the model label at the composer's right, so it stands
    to the right of your longest line (如果你能一直这样子……) with room to spare."""
    m = _D.completion_menu(t)
    return m.replace('<div class="pv-menu" style="', '<div class="pv-menu" style="width:140px;', 1)
PLACEHOLDER = '发消息或创建任务，/ 调用指令，@ 文件或对话'

def composer(model: str, col: str, inner: str, menu: str, ime: str, empty: bool=False) -> str:
    """pages.d.composer_html with the IME window in the card (the card is position:relative, not clipped).
    empty: focused, nothing typed: the placeholder stays and the caret blinks at its start."""
    text = f'<div class="uV2eYG_input">{inner}</div>'
    if empty:
        text += f'<div class="uV2eYG_placeholder">{dsh.esc(PLACEHOLDER)}</div>'
    return f'\n<div class="uV2eYG_root" id="composer">\n <div class="uV2eYG_card">\n  <div class="uV2eYG_scroll"><div class="uV2eYG_grow">\n   {text}\n  </div></div>\n  {ime}\n  <div class="uV2eYG_row">\n   <div class="uV2eYG_modes" style="display:flex;align-items:center">\n    <button type="button" class="uV2eYG_add">{svg('IconPlusOutline16', 16)}</button>\n    <button type="button" class="uV2eYG_add">{svg('IconPaperclipOutline16', 16)}</button>\n   </div>\n   <div class="uV2eYG_trailing pv-rel">\n    <span class="uV2eYG_select" style="background-image:none;display:inline-flex;align-items:center;padding:0">\n     <span class="pv-mdot" style="background:{col}"></span>{dsh.esc(model)}</span>\n    <button type="button" class="uV2eYG_primary">{svg('IconSendOutline14', 14)}</button>\n    {menu}\n   </div>\n  </div>\n </div>\n</div>'

def body(t: float) -> str:
    who = tl.model(t)
    mname, col = (cast.name(who), color(who))
    theme = cast.CAST[who].get('theme', '')
    rows = _D.rows_at(t)
    inner, line, cx = typed(t)
    empty = t < G.TYPE1[0][1]
    if empty:
        inner = _caret(t)
    head = _D.HEADER('大肥鱼', mname, col, AV, '在线')
    main = head + f'<div id="timeline">{rows}</div>' + composer(mname, col, inner, _completion_menu(t), _ime(t, line, cx), empty) + _D.STATS(5, 100, speed.tok_s(G.turn_at(t).key) or 'cloud API')
    return f'<div class="pv-root {theme}">{_D.RAIL(who)}<div class="pv-main">{main}</div></div>'

def write() -> int:
    from pathlib import Path
    from tuikit.uipane import write_frames
    ui = Path(__file__).resolve().parent.parent
    x0, y0, x1, y1 = tl.p.rect('pane')
    n = write_frames(ui / 'frames_D_r5.json', R.N_R5 / tl.p.FPS, R.N_E / tl.p.FPS, tl.p.FPS, body, page='host.html', viewport=(x1 - x0, y1 - y0), out_dir='pane_d_r5', scale=R.SHOT_SCALE)
    print(f'D (r5): {n} frames -> frames_D_r5.json')
    return n
