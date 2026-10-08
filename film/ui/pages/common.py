"""Shared pieces of the dsh pane pages: colours, the page frame, small row builders.

Rules (playbook/05_direction.md, PLAN_FULL R1-R11): chat text never restates the lyric; every landing is a
sung syllable or a beat taken from the group module (groups/<g>.py), never a typed second; CSS animation
only for loops (the reasoning sweep), everything else is driven by t.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import os
import sys
from pathlib import Path
UI = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(UI), str(UI.parent), os.environ.get('TUIKIT_ROOT', str(PV_ROOT / 'runtime'))]
import cast
import dsh
import tl
from tuikit import ease
from tuikit.uipane import life, show
COL = {k: '#%02x%02x%02x' % tl.p.color(k) for k in ('her', 'ink', *(cast.CAST[w]['color'] for w in cast.CAST if w != 'her'))}
AV = 'assets/her_complete.png'

def color(who: str) -> str:
    return COL[cast.CAST[who]['color']]

def blink(t: float) -> bool:
    return t % 1.06 < 0.53

def appear(t: float, t_in: float, html: str, fade_in: float=0.1, t_out: float | None=None) -> str:
    """A row that grows in at t_in (and optionally out at t_out)."""
    if t < t_in:
        return ''
    return show(html, life(t, t_in, t_out if t_out is not None else float('inf'), fade_in=fade_in))

def read_row(t: float, at: float, n_files: int | None=None, hot: str='') -> str:
    n = n_files if n_files is not None else tl.files(at)[1]
    state = 'running' if t < at + 0.3 else 'ok'
    return appear(t, at, dsh.tool(f'读取 ~/memory/you/ · {n} 个文件', '读取记忆', state, 'IconDatabaseOutline16', hot))

def write_row(t: float, at: float, name: str, hot: str='') -> str:
    state = 'running' if t < at + 0.3 else 'ok'
    return appear(t, at, dsh.tool(f'写入 ~/memory/you/{name}.txt', '写入记忆', state, 'IconDatabaseOutline16', hot))

def think_row(t: float, span: tuple, summary: str='构思回答', body=None, pointer: str='') -> str:
    if t < span[0]:
        return ''
    return dsh.think(summary, t < span[1], body, pointer=pointer)

def image_row(src: str, size: int=180) -> str:
    return f'<div class="hWmORq_root"><div class="hWmORq_body"><img src="{src}" style="width:{size}px;height:{size}px;border-radius:12px;display:block"></div></div>'

def rail(who: str, extra: list | None=None, her_grey: bool=True) -> str:
    items = [{'avatar': AV, 'active': True, 'ring': color(who)}]
    items += extra or []
    if her_grey:
        items.append({'avatar': AV, 'grey': True, 'badge': '已归档'})
    return dsh.rail(items)

def page(t: float, rows: str='', who: str | None=None, typed: str='', railv: str | None=None, menu: str='', ptr: str='', turns: int=0, cache: int=100, speed: str | None=None, theme: str | None=None, name: str='大肥鱼', state: str='在线', effort: str='', placeholder: str | None=None, overlay: str='') -> str:
    """The whole pane: session rail, persona header (naming the model wearing it), timeline, composer, stats."""
    who = who or tl.model(t)
    mname, col = (cast.name(who), color(who))
    theme = theme if theme is not None else cast.CAST[who].get('theme', '')
    comp_kw = {'placeholder': placeholder} if placeholder else {}
    main = dsh.header(name, mname, col, AV, state) + f'<div id="timeline">{rows}</div>' + dsh.composer(mname, col, effort=effort, typed=typed, caret_on=blink(t), menu=menu + (f'<div style="position:absolute;left:0;top:0">{ptr}</div>' if ptr else ''), **comp_kw) + dsh.stats(turns, cache, speed)
    return f'<div class="pv-root {theme}">{(railv if railv is not None else rail(who))}<div class="pv-main">{main}</div>{overlay}</div>'
