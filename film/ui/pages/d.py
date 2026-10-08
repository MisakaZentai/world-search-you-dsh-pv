"""dsh pane, group D (137.10-179.64): regenerate x6, then you type, stall, and love fills in.

D1: you press regenerate on the bar downbeats; each new model is visible as behaviour (D5): on the press the
header's model name and dot change (the avatar does not), an 8th later its memory read, a reasoning model
shows a thinking row on beat 2, the answer arrives as one chunk (always the same words), on beat 3 it writes
a file. The rows of a turn are laid out from the press on (hidden until they land) so the action bar, and
your pointer on its regenerate key, stay put.
D2-D6: your heart words in the composer, one character per sung syllable; the stand-in's grey completion
'dope'; then a completion menu. D7: love fills in (her blue) as the window slides out; while it is out the
pane switches to group E's layout (wide session list, the model-name reel) so it comes back in E's shape.

Local versions of shared pieces: tail_regen (dsh.tail has no regenerate key), composer_html (dsh.composer
escapes its text: no grey completion, line breaks or her coloured word), page_local (common.page blinks the
caret by the clock; here it is on for the first half of each beat, R6).
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
from functools import lru_cache
from pages.common import AV, color, dsh, ease, rail
from pages import c as PC
import cast
import hud
import tl
from groups import c as GC
from groups import d as G
from icons import svg as _svg_raw
svg = lru_cache(maxsize=None)(_svg_raw)
TOOL = lru_cache(maxsize=None)(dsh.tool)
THINK = lru_cache(maxsize=None)(dsh.think)
HER = lru_cache(maxsize=None)(dsh.her)
STATS = lru_cache(maxsize=None)(dsh.stats)
HEADER = lru_cache(maxsize=None)(dsh.header)
RAIL = lru_cache(maxsize=None)(rail)
HER_LIVE = '#%02x%02x%02x' % hud.HER_LIVE
HER_QUIET = '#%02x%02x%02x' % hud.HER_QUIET
REGEN_XY = (117.0, 351.0)
LAYOUT_E = G.LOVE_AT + 0.4

@lru_cache(maxsize=None)
def tail_regen(duration: str, clock: str) -> str:
    """dsh's action bar under an answer, with a regenerate key (dsh's own IconRefreshOutline16, X18)."""
    icon = lambda n: f'<button type="button" class="xzv4MW_action">{svg(n, 16)}</button>'
    return f'\n<div class="TS9iAW_root" data-actions-reveal="always">\n <div class="xzv4MW_actions TS9iAW_actions">\n  {icon('IconCopyOutline16')}{icon('IconRefreshOutline16')}{icon('IconLikeOutline16')}{icon('IconDislikeOutline16')}{icon('IconBranchOutline16')}\n  <span class="Q51KRG_root"><button type="button" class="Q51KRG_trigger pv-force">{svg('IconClockOutline16', 16)}<span class="Q51KRG_label">用时 {dsh.esc(duration)}</span></button></span>\n  <span class="xzv4MW_timeEnd">{dsh.esc(clock)}</span>\n </div>\n</div>'

@lru_cache(maxsize=None)
def composer_html(model: str, col: str, inner: str, menu: str='', placeholder: str='发消息或创建任务，/ 调用指令，@ 文件或对话') -> str:
    """dsh.composer with raw inner HTML (your text, the caret, a grey completion, line breaks)."""
    text = f'<div class="uV2eYG_input">{inner}</div>' if inner else f'<div class="uV2eYG_input"></div><div class="uV2eYG_placeholder">{dsh.esc(placeholder)}</div>'
    return f'\n<div class="uV2eYG_root" id="composer">\n <div class="uV2eYG_card">\n  <div class="uV2eYG_scroll"><div class="uV2eYG_grow">\n   {text}\n  </div></div>\n  <div class="uV2eYG_row">\n   <div class="uV2eYG_modes" style="display:flex;align-items:center">\n    <button type="button" class="uV2eYG_add">{svg('IconPlusOutline16', 16)}</button>\n    <button type="button" class="uV2eYG_add">{svg('IconPaperclipOutline16', 16)}</button>\n   </div>\n   <div class="uV2eYG_trailing pv-rel">\n    <span class="uV2eYG_select" style="background-image:none;display:inline-flex;align-items:center;padding:0">\n     <span class="pv-mdot" style="background:{col}"></span>{dsh.esc(model)}</span>\n    <button type="button" class="uV2eYG_primary">{svg('IconSendOutline14', 14)}</button>\n    {menu}\n   </div>\n  </div>\n </div>\n</div>'

def page_local(t: float, rows: str, who: str | None=None, inner: str='', menu: str='', overlay: str='', sidebar: str | None=None, header: str | None=None, turns: int=5, speed: str='cloud API') -> str:
    who = who or tl.model(t)
    mname, col = (cast.name(who), color(who))
    theme = cast.CAST[who].get('theme', '')
    head = header if header is not None else HEADER('大肥鱼', mname, col, AV, '在线')
    main = head + f'<div id="timeline">{rows}</div>' + composer_html(mname, col, inner, menu) + STATS(turns, 100, speed)
    return f'<div class="pv-root {theme}">{(sidebar if sidebar is not None else RAIL(who))}<div class="pv-main">{main}</div>{overlay}</div>'

def caret(t: float, on: bool=True) -> str:
    return f'<span class="pv-caret" style="opacity:{(1 if on else 0)}"></span>'

def caret_on(t: float) -> bool:
    """On for the first half of each beat, solid for 0.3 s after a key and while you are stuck (R6)."""
    if G.stuck(t):
        return True
    return tl.C.beat_of(t) % 1.0 < 0.5 or t - G.last_key(t) < 0.3
_HIST: list = []

def history() -> str:
    """Everything before the regenerated turn: C's Qwen and 丙 (MiMo) rows up to your 让我看看你."""
    if not _HIST:
        _HIST.append(PC.rows_qwen(G.T0 - 0.01) + PC.rows_doubao(GC.SEE_SEND - 0.01) + dsh.user(GC.SEE_ASK))
    return _HIST[0]

def fade(html: str, t: float, at: float, dur: float=0.12) -> str:
    """A row that is laid out from the start and becomes visible at `at` (no height change: nothing moves)."""
    if t < at:
        return f'<div style="visibility:hidden">{html}</div>'
    a = ease.smooth(min(1.0, (t - at) / dur))
    return html if a >= 1 else f'<div style="opacity:{a:.3f}">{html}</div>'

def turn_rows(t: float, T) -> str:
    n = tl.files(T.read)[1]
    st = lambda at: 'running' if t < at + 0.3 else 'ok'
    out = [fade(TOOL(f'读取 ~/memory/you/ · {n} 个文件', '读取记忆', st(T.read), 'IconDatabaseOutline16'), t, T.read)]
    if T.think is not None:
        out.append(fade(THINK(T.rows[0], t < (T.think2 if T.think2 is not None else T.ans)), t, T.think))
    if T.think2 is not None:
        out.append(fade(THINK(T.rows[1], t < T.ans), t, T.think2))
    out.append(fade(HER(G.ANSWER), t, T.ans))
    clock = f'23:{44 + T.i // 3:02d}'
    out.append(fade(tail_regen(f'{T.ttft:.1f}秒', clock), t, T.ans))
    out.append(fade(TOOL(f'写入 ~/memory/you/{T.file}.txt', '写入记忆', st(T.write), 'IconDatabaseOutline16', color(T.key)), t, T.write))
    return ''.join(out)

def pointer(t: float) -> str:
    """Your pointer on the regenerate key: in from the lower right before the first press, a press on every
    downbeat that swaps the model, away after 151.13 (you stop)."""
    x, y = REGEN_XY
    t_in = G.T0
    if t < t_in or t >= G.ROT_STOP + 0.45:
        return ''
    u = ease.ease_io(ease.prog(t, t_in, G.ROT_AT[0] - 0.05))
    px, py = (ease.lerp(x + 150, x, u), ease.lerp(y + 70, y, u))
    if t >= G.ROT_STOP:
        v = ease.ease_in(ease.prog(t, G.ROT_STOP, G.ROT_STOP + 0.45))
        px, py = (x + 160 * v, y + 60 * v)
    press = 0.0
    for at in G.ROT_AT:
        if at - 0.04 <= t < at + 0.16:
            press = max(press, 1 - abs(t - at) / 0.16)
    return dsh.pointer(px, py, press)

def rows_at(t: float) -> str:
    if t < G.ROT_AT[0]:
        rows = PC.rows_qwen(t) + PC.rows_doubao(t)
        return rows.replace(dsh.tail('0.9秒', '23:43'), tail_regen('0.9秒', '23:43'))
    return history() + turn_rows(t, G.turn_at(t))

def typed_inner(t: float) -> str:
    keep = [ch for i, (ch, at) in enumerate(G.TYPE1) if at <= t and (not (i in G.DELS and t >= G.DELS[i]))]
    lines = [''.join(keep)]
    if t >= G.TYPE2[0][1]:
        lines.append(''.join((ch for ch, at in G.TYPE2 if at <= t)))
    if t >= G.TYPE3[0][1]:
        lines.append(''.join((ch for ch, at in G.TYPE3 if at <= t)))
    html = [dsh.esc(s) for s in lines]
    last = len(html) - 1
    if t >= G.LOVE_AT:
        colr = HER_LIVE if t < G.LOVE_NOTES[1] else HER_QUIET
        html[last] += f'<span style="color:{colr};font-weight:600">love</span>'
        return '<br>'.join(html)
    html[last] += caret(t, caret_on(t))
    if G.DOPE_AT <= t < G.DOPE_END:
        html[0] += '<span style="color:var(--dsw-alias-label-tertiary)">dope</span>'
    return '<br>'.join(html)

def completion_menu(t: float) -> str:
    if not G.HUM <= t < G.LOVE_AT:
        return ''
    col = color(tl.model(t))
    rows = [(w, col, '补全' if i == 0 else '') for i, w in enumerate(G.COMPLETE)]
    return dsh.menu(rows, None, 1.0)

def body(t: float) -> str:
    if t >= LAYOUT_E:
        from pages import e as PE
        return PE.body(t)
    rows = rows_at(t)
    inner = typed_inner(t) if t >= G.TYPE1[0][1] else ''
    return page_local(t, rows, inner=inner, menu=completion_menu(t), overlay=pointer(t), turns=5, speed='cloud API')
