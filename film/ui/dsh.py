"""dsh rows as HTML, from dsh's own stylesheets, class names and icons (read-only, MIT front end).

Adapted from film 1 (`pv_dsh_frontend_20260927/build_frame.py`): same row markup, plus what the sequel
needs — the light theme, a session rail with her archived session, the persona header that names the
model wearing it, the thinking row's native expanded body (`lcKema_thinkBody`), memory read/write
tool rows, a model menu and your pointer.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import html
import json
from pathlib import Path
from icons import svg
HERE = Path(__file__).parent
D = json.loads((HERE / 'disclosure_map.json').read_text())

def esc(s: str) -> str:
    return html.escape(s, quote=False)

def think(summary: str, running: bool=False, body: str | None=None, pointer: str='') -> str:
    """dsh's reasoning row. body (HTML) = the native expanded state (data-expanded + lcKema_thinkBody)."""
    state = 'running' if running else 'ok'
    exp = ' data-expanded="true"' if body is not None else ''
    inner = f'<div class="lcKema_thinkBody">{body}</div>' if body is not None else ''
    return f'\n<div class="lcKema_root pv-rel" data-variant="think" data-state="{state}"{exp}>\n <div class="{D['root']}">\n  <div class="{D['row']} lcKema_row" data-disclosure-row="true" data-expandable="true" role="button">\n   <span class="{D['leading']} lcKema_leading"><span class="{D['iconIdle']}">{svg('IconThinkOutline14', 14)}</span>{svg('IconChevronDownOutline14', 14, 'lcKema_chevron ' + D['chevronHover'])}</span>\n   <span class="{D['title']} lcKema_title">思考</span>\n   <span class="lcKema_separator" aria-hidden="true"></span>\n   <span class="lcKema_summary"{(' data-follow-end="true"' if running else '')}><span class="lcKema_summaryText">{esc(summary)}</span></span>\n  </div>\n </div>\n {inner}{pointer}\n</div>'

def tool(summary: str, title: str='工具调用', state: str='ok', icon: str='IconSparkle16', hot: str='') -> str:
    style = f' style="color:{hot}"' if hot else ''
    return f'\n<div class="o3BgMG_root" data-variant="others" data-tool="memory" data-state="{state}">\n <div class="{D['root']}">\n  <div class="{D['row']} o3BgMG_row" data-disclosure-row="true" data-expandable="true" role="button">\n   <span class="{D['leading']} o3BgMG_leading"><span class="{D['iconIdle']}">{svg(icon, 14)}</span></span>\n   <span class="{D['title']} o3BgMG_title">{esc(title)}</span>\n   <span class="o3BgMG_sep" aria-hidden="true"></span><span class="o3BgMG_summary"{style}>{esc(summary)}</span>\n  </div>\n </div>\n</div>'

def user(text: str, caret: bool=False) -> str:
    c = '<span class="pv-caret"></span>' if caret else ''
    return f'\n<div class="Sixlwa_userRow"><div class="Sixlwa_userStack"><div class="Sixlwa_bubble">{esc(text)}{c}</div></div></div>'

def her(text: str) -> str:
    return f'\n<div class="hWmORq_root"><div class="hWmORq_body"><p style="margin:0">{esc(text).replace(chr(10), '<br>')}</p></div></div>'

def tail(duration: str, clock: str) -> str:
    icon = lambda n: f'<button type="button" class="xzv4MW_action">{svg(n, 16)}</button>'
    return f'\n<div class="TS9iAW_root" data-actions-reveal="always">\n <div class="xzv4MW_actions TS9iAW_actions">\n  {icon('IconCopyOutline16')}{icon('IconLikeOutline16')}{icon('IconDislikeOutline16')}{icon('IconBranchOutline16')}\n  <span class="Q51KRG_root"><button type="button" class="Q51KRG_trigger pv-force">{svg('IconClockOutline16', 16)}<span class="Q51KRG_label">用时 {esc(duration)}</span></button></span>\n  <span class="xzv4MW_timeEnd">{esc(clock)}</span>\n </div>\n</div>'

def composer(model: str, color: str, effort: str='Max', typed: str='', caret_on: bool=True, placeholder: str='发消息或创建任务，/ 调用指令，@ 文件或对话', menu: str='') -> str:
    caret = f'<span class="pv-caret" style="opacity:{(1 if caret_on else 0.45)}"></span>'
    text = f'<div class="pv-typed">{esc(typed)}{caret}</div>' if typed else f'<div class="uV2eYG_placeholder">{esc(placeholder)}</div>'
    return f'\n<div class="uV2eYG_root" id="composer">\n <div class="uV2eYG_card">\n  <div class="uV2eYG_scroll"><div class="uV2eYG_grow">\n   <div class="uV2eYG_input"></div>\n   {text}\n  </div></div>\n  <div class="uV2eYG_row">\n   <div class="uV2eYG_modes" style="display:flex;align-items:center">\n    <button type="button" class="uV2eYG_add">{svg('IconPlusOutline16', 16)}</button>\n    <button type="button" class="uV2eYG_add">{svg('IconPaperclipOutline16', 16)}</button>\n   </div>\n   <div class="uV2eYG_trailing pv-rel">\n    <span class="uV2eYG_select" style="background-image:none;display:inline-flex;align-items:center;padding:0">\n     <span class="pv-mdot" style="background:{color}"></span>{esc(model)}&nbsp;<span style="color:var(--dsw-alias-label-tertiary)">{esc(effort)}</span></span>\n    <button type="button" class="uV2eYG_primary">{svg('IconSendOutline14', 14)}</button>\n    {menu}\n   </div>\n  </div>\n </div>\n</div>'

def stats(turns: int, cache: int, speed: str | None=None) -> str:
    pill = lambda icon, text: f'<span class="bOPqQW_anchor"><span class="bOPqQW_pill">{svg(icon, 16)}<span class="bOPqQW_label">{text}</span></span></span>'
    return f'\n<div class="bOPqQW_root" data-composer-stats="true">\n {pill('IconGaugeOutline16', f'{turns} 轮' + (f' · {speed}' if speed else ''))}\n {pill('IconDatabaseOutline16', f'缓存命中 {cache}%')}\n</div>'

def header(name: str, model: str, color: str, avatar: str, state: str='在线') -> str:
    return f'\n<div class="pv-head">\n <div class="pv-pet"><img src="{avatar}"></div>\n <div class="pv-who"><div class="pv-name">{esc(name)}</div>\n  <div class="pv-state"><span class="pv-dot" style="background:{color}"></span>{esc(state)} · <span style="color:{color}">{esc(model)}</span></div></div>\n</div>'

def rail(items: list[dict]) -> str:
    """Session rail: [{avatar, grey, active, badge, ring}] top to bottom."""
    out = []
    for it in items:
        cls = 'pv-ses' + (' on' if it.get('active') else '') + (' grey' if it.get('grey') else '')
        ring = f' style="box-shadow:0 0 0 2px {it['ring']}"' if it.get('ring') else ''
        badge = f'<span class="pv-badge">{esc(it['badge'])}</span>' if it.get('badge') else ''
        out.append(f'<div class="{cls}"><img src="{it['avatar']}"{ring}>{badge}</div>')
    return f'<div class="pv-rail"><div class="pv-new">{svg('IconPlusOutline16', 16)}</div>{''.join(out)}</div>'

def menu(rows: list[tuple[str, str, str]], hover: int | None, opacity: float=1.0) -> str:
    """Model menu above the composer's model label: rows = [(name, colour, note)]."""
    items = []
    for i, (name, color, note) in enumerate(rows):
        cls = 'pv-mi' + (' hov' if i == hover else '') + (' off' if note == '已下线' else '')
        items.append(f'<div class="{cls}"><span class="pv-mdot" style="background:{color}"></span>{esc(name)}<span class="pv-note">{esc(note)}</span></div>')
    return f'<div class="pv-menu" style="opacity:{opacity:.2f}">{''.join(items)}</div>'

def pointer(x: float, y: float, press: float=0.0) -> str:
    """Your mouse pointer (system colour), absolutely placed inside the parent; press 0..1 = click."""
    s = 1.0 - 0.12 * press
    ring = f'<span class="pv-ring" style="opacity:{press:.2f};transform:scale({0.6 + 0.8 * press:.2f})"></span>' if press > 0 else ''
    return f'<div class="pv-ptr" style="left:{x:.1f}px;top:{y:.1f}px;transform:scale({s:.3f})">{ring}<svg width="18" height="22" viewBox="0 0 18 22"><path d="M1 1 L1 17 L5.2 13.2 L8.2 20 L11 18.8 L8.1 12.2 L13.6 12.2 Z" fill="#262a34" stroke="#ffffff" stroke-width="1.3" stroke-linejoin="round"/></svg></div>'
