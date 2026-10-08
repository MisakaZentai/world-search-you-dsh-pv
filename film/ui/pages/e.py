"""dsh pane, group E (179.64-207.0): sessions named 大肥鱼 everywhere, the model-name reel, then the dark list.

The pane switches to this layout in group D while the window is out (D7), so it comes back in this shape:
a wide session list on the left (X26: pinned row on top, its text covered until H3; sessions with the model
under the name) and a header whose model name is a reel (three names visible, the middle one current).

  E1 / E2'  one session per sung syllable, inserted at the top; her archived one is pushed out at the bottom
  E3        the reel steps one name per 16th from "But", stops on trans-for-ming's three syllables, never on her
  E4        still (the left leads); inside the ah-ah the pane is the frame of 198.99 (D4)
  E5        the list goes dark, only the pinned row glows faintly (seen while the window slides out and back)
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
from functools import lru_cache
from pages.common import AV, appear, color, dsh, ease
from pages import d as PD
import cast
import tl
from groups import d as GD
from groups import e as G
from pages.d import svg
HER_QUIET = PD.HER_QUIET
SIDE_W = 152
REEL = ['kimi', 'qwen', 'mimo', 'glm', 'ernie', 'hy4', 'minimax', 'step', 'her', 'longcat']
SESS_ORDER = ['mimo', 'glm', 'kimi', 'step', 'qwen', 'ernie', 'longcat', 'hy4', 'minimax']
NEW = [(at, SESS_ORDER[i % len(SESS_ORDER)]) for i, at in enumerate(list(G.SESS1) + list(G.SESS2))]
REEL_HOLD = 0.2
REEL_BOX_W = 199

def _reel():
    """Step times of the reel: 16ths from 'But', each stop exactly on its syllable (R6: steps, >= a 16th)."""
    steps, start = ([], G.SLOT_AT)
    for stop in G.SLOT_STOPS:
        j = 0
        while True:
            s = tl.grid(start, j, 4)
            if s >= stop - 0.09:
                break
            steps.append(s)
            j += 1
        steps.append(stop)
        start = stop + REEL_HOLD
    return steps
REEL_STEPS = _reel()
REEL_START = (REEL.index('longcat') - len(REEL_STEPS)) % len(REEL)
STOP_NAMES = [REEL[(REEL_START + REEL_STEPS.index(s) + 1) % len(REEL)] for s in G.SLOT_STOPS]

def reel_index(t: float) -> int:
    n = sum((1 for s in REEL_STEPS if s <= t))
    return (REEL_START + n) % len(REEL) if t >= G.SLOT_AT else REEL.index('longcat')

def reel(t: float) -> str:
    i = reel_index(t)
    prev, cur, nxt = (REEL[(i - 1) % len(REEL)], REEL[i], REEL[(i + 1) % len(REEL)])
    cc = HER_QUIET if cur == 'her' else color(cur)
    side = 'font-size:11px;line-height:15px;height:15px;overflow:hidden;color:'
    sc = lambda k: side + (HER_QUIET if k == 'her' else 'var(--dsw-alias-label-tertiary)')
    return f'<div style="margin-top:3px;width:{REEL_BOX_W}px;border:.5px solid var(--dsw-alias-border-l2);border-radius:7px;padding:1px 8px;background:var(--dsw-alias-bg-base)"><div style="{sc(prev)}">{dsh.esc(cast.name(prev))}</div><div style="display:flex;align-items:center;gap:6px;font-size:14px;line-height:20px;font-weight:600;white-space:nowrap;color:{cc}"><span class="pv-dot" style="background:{cc};width:7px;height:7px;border-radius:50%"></span>{dsh.esc(cast.name(cur))}</div><div style="{sc(nxt)}">{dsh.esc(cast.name(nxt))}</div></div>'

def header(t: float) -> str:
    return f'<div class="pv-head"><div class="pv-pet"><img src="{AV}"></div><div class="pv-who"><div class="pv-name">大肥鱼</div><div class="pv-state"><span class="pv-dot" style="background:{color(tl.model(t))}"></span>在线</div>{reel(t)}</div></div>'
WRAP = {cast.name('ernie'), f'{cast.name('her')} · 已归档'}

@lru_cache(maxsize=None)
def item(who: str, active: bool=False, grey: bool=False) -> str:
    img = f'<img src="{AV}" style="width:24px;height:24px;border-radius:7px;object-fit:cover;display:block;{('filter:grayscale(1) brightness(1.08) contrast(.82);opacity:.75;' if grey else '')}">'
    model = f'{cast.name('her')} · 已归档' if grey else cast.name(who)
    dotc = 'var(--dsw-alias-label-tertiary)' if grey else color(who)
    bg = 'background:var(--dsw-alias-bg-layer-2, rgba(0,0,0,.05));' if active else ''
    if model not in WRAP:
        return f'<div style="display:flex;align-items:center;gap:7px;padding:3px 8px;height:34px;box-sizing:border-box;border-radius:8px;{bg}">{img}<div style="min-width:0"><div style="font-size:12px;line-height:15px;font-weight:600;color:var(--dsw-alias-label-{('tertiary' if grey else 'primary')})">大肥鱼</div><div style="font-size:10px;line-height:13px;color:var(--dsw-alias-label-tertiary);white-space:nowrap;display:flex;align-items:center;gap:4px"><span style="width:5px;height:5px;border-radius:50%;background:{dotc};flex:none"></span>{dsh.esc(model)}</div></div></div>'
    return f'<div style="display:flex;align-items:center;gap:7px;padding:3px 8px;min-height:34px;flex:none;box-sizing:border-box;border-radius:8px;{bg}">{img}<div style="min-width:0"><div style="font-size:12px;line-height:15px;font-weight:600;color:var(--dsw-alias-label-{('tertiary' if grey else 'primary')})">大肥鱼</div><div style="font-size:10px;line-height:13px;color:var(--dsw-alias-label-tertiary);white-space:normal;display:flex;align-items:center;gap:4px"><span style="width:5px;height:5px;border-radius:50%;background:{dotc};flex:none;align-self:flex-start;margin-top:4px"></span><span>{dsh.esc(model)}</span></div></div></div>'

def sidebar(t: float) -> str:
    dark = ease.prog(t, G.LS_OUT, G.LS_OUT + 0.3)
    glow = dark
    pin_c = HER_QUIET if glow > 0 else 'var(--dsw-alias-label-tertiary)'
    pin = f'<div style="padding:0 8px 6px"><div style="font-size:10px;color:var(--dsw-alias-label-tertiary);line-height:16px">钉住</div><div style="display:flex;align-items:center;gap:7px;height:28px;padding:0 8px;border-radius:8px;border:{(1 if glow > 0 else 0.5)}px solid {(pin_c if glow > 0 else 'var(--dsw-alias-border-l2)')}"><span style="font-size:11px;color:{pin_c}">{svg('IconAgentPresetOutline16', 14)}</span><span style="flex:1;height:9px;border-radius:2px;background:repeating-linear-gradient(135deg,{pin_c} 0 2px,transparent 2px 5px);opacity:{0.55 + 0.45 * glow:.2f}"></span></div></div>'
    rows = []
    for at, who in reversed(NEW):
        if at <= t:
            rows.append(appear(t, at, item(who), fade_in=0.1))
    rows.append(item(tl.model(t), active=True))
    rows.append(item('her', grey=True))
    lst = f'<div style="display:flex;flex-direction:column;gap:2px;padding:0 6px;overflow:hidden;flex:1;min-height:0;opacity:{1 - 0.62 * dark:.3f}">{''.join(rows)}</div>'
    top = f'<div style="display:flex;align-items:center;gap:8px;padding:12px 14px 10px;font-size:13px;color:var(--dsw-alias-label-secondary)">{svg('IconNewChatOutline16', 16)}新对话</div>'
    label = f'<div style="font-size:10px;color:var(--dsw-alias-label-tertiary);line-height:16px;padding:2px 14px">会话</div>'
    return f'<div style="width:{SIDE_W}px;flex:none;display:flex;flex-direction:column;background:var(--dsw-specific-sidebar-fill, var(--dsw-alias-bg-layer-1));border-right:.5px solid var(--dsw-alias-border-l1);overflow:hidden">{top}{pin}{label}{lst}</div>'

def body(t: float) -> str:
    t = G.frozen(t)
    rows = PD.history() + PD.turn_rows(1000000000.0, GD.TURNS[-1])
    return PD.page_local(t, rows, inner=PD.typed_inner(t), sidebar=sidebar(t), header=header(t), turns=5, speed='cloud API')
