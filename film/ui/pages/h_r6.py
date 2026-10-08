"""dsh pane, group H r6 (r17 sample, D59; groups/h_r6.py): ui/pages/h_r5.py (kept unchanged) with the choice taken out.

  273.39 FOUND     her archived session opens on its last rows (as r5)
  275.09 CARD      the composer turns into dsh's block: 当前模型不可用，请先选择模型 (as r5:
                   dsh-client-ui-model-selection `blocked.composer`, an inert composer with that placeholder by
                   dsh-client-ui-conversation's ComposerBlockRegistry). It stays blocked to the end: no caret.
  277.47 DOG       her avatar picture is the puppy (as r5)
  282.86-283.77    the session scrolls back to film 1's C page (茄子 / 番茄): the reading (as r5)
  r5's pointer, the model menu (MENU_AT), the hover (HOVER_AT) and the click (PRESS) are gone: nothing on the page
  points at a model. The label is hers, DeepSeek-V4.1-Flash, to the end.
  MOVE             the window slides into film 1's frame (groups/h_r6.py); the rows leave as it darkens (as r5)

  NOW_AT (297.5, DSH_END=story)   now: her session open where the reading stopped. The rows are her session's own, in
                   its order (pages/a_open.blocks, the opening's rows, unpinned: 明天见 / 明天见喵～ ... 今天也谢谢你。 /
                   不客气～明天也要来找我哦 ...), scrolled so that the reading's last line sits above the composer;
                   her own avatar (her face; the puppy was the reading's game); composer blocked; no new row.

  python ui/pages/h_r6.py         -> ui/frames_H_r6.json (FOUND .. LAND) and, with DSH_END=story,
                                     ui/frames_H_r6_now.json (NOW_AT .. END), both out_dir pane_h_r6; then
  node <local-production-path> ui/frames_H_r6.json   (and frames_H_r6_now.json)

Text on the page is film 1's chat and the opening's rows (not the lyric).
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import sys
from pathlib import Path
if __name__ == '__main__':
    sys.path[:0] = [str(Path(__file__).resolve().parent.parent), str(Path(__file__).resolve().parents[2])]
from pages.common import AV, dsh, ease
from pages import a_open as PO
from pages import h as PH
from pages import h_r5 as P5
import cast
from groups import g as GG
from groups import h_r6 as G
GREY = PH.GREY
BLOCKED, UNAVAILABLE = (P5.BLOCKED, P5.UNAVAILABLE)
C_PAGE, SEP, LAST, SCROLL_PX = (P5.C_PAGE, P5.SEP, P5.LAST, P5.SCROLL_PX)
PIXELATED = P5.PIXELATED

def composer(t: float) -> str:
    """Hers, unavailable, then dsh's block from CARD on; it never becomes live again."""
    if t < GG.CARD:
        return dsh.composer(cast.name('her'), GREY, effort='Max', placeholder=UNAVAILABLE)
    k = ease.prog(t, GG.CARD, GG.CARD + 0.2)
    ph = UNAVAILABLE if k < 0.5 else BLOCKED
    html = dsh.composer(cast.name('her'), GREY, effort='Max', placeholder=ph)
    if k >= 1:
        return html
    o = abs(1 - 2 * k)
    return html.replace('<div class="uV2eYG_placeholder">', f'<div class="uV2eYG_placeholder" style="opacity:{o:.2f}">')

def her_session(t: float) -> str:
    """pages/h_r5.her_session with r6's composer."""
    keep = 1 - ease.smooth(ease.prog(t, G.MOVE[0], G.MOVE[0] + 0.45))
    scroll = ease.ease_io(ease.prog(t, *G.SCROLL))
    half = 0.5 if t >= G.SCROLL[0] - 0.2 else 0.62
    body = PH.rows(C_PAGE, t, half * keep) + PH.rows(SEP, t, half * keep)
    body += ''.join((f'<div style="opacity:{half * keep:.3f}">{h}</div>' for h in LAST))
    tl_html = f'<div style="transform:translateY({SCROLL_PX * scroll:.1f}px);display:flex;flex-direction:column;gap:10px">{body}</div>'
    head = dsh.header('大肥鱼', cast.name('her'), GREY, P5.avatar_src(t), '已归档').replace('<img src="data:', PIXELATED)
    head = f'<div style="opacity:{keep:.3f}">{head}</div>'
    main = head + f'<div id="timeline">{tl_html}</div>' + composer(t)
    return f'<div class="pv-root">{P5.rail(t, keep)}<div class="pv-main">{main}</div></div>'
NOW_KEYS = ('see_you', 'goodnight', 'thanks', 'last_msg', 'tail', 'sent')
NOW_SCROLL = 362

def now_rows() -> list[str]:
    out = []
    for key, items in PO.blocks(PO.G.ERROR_AT + 1.0):
        if key in NOW_KEYS:
            out.extend(items)
    return out
NOW_ROWS = now_rows()

def now_session(t: float) -> str:
    body = ''.join(NOW_ROWS)
    tl_html = f'<div style="transform:translateY({NOW_SCROLL}px);display:flex;flex-direction:column;gap:10px">{body}</div>'
    head = dsh.header('大肥鱼', cast.name('her'), GREY, AV, '已归档')
    rail = dsh.rail([{'avatar': AV, 'grey': True, 'active': True, 'badge': '已归档'}])
    rail = f'<div style="display:flex">{rail}</div>'
    comp = dsh.composer(cast.name('her'), GREY, effort='Max', placeholder=BLOCKED)
    main = head + f'<div id="timeline">{tl_html}</div>' + comp
    return f'<div class="pv-root">{rail}<div class="pv-main">{main}</div></div>'

def body(t: float) -> str:
    return now_session(t) if t >= G.NOW_AT - 1e-06 else her_session(t)
if __name__ == '__main__':
    import tl
    from tuikit.uipane import write_frames
    sys.stdout.reconfigure(encoding='utf-8')
    x0, y0, x1, y1 = tl.p.rect('pane')
    ui = Path(__file__).resolve().parent.parent
    vp = (x1 - x0, y1 - y0)
    n = write_frames(ui / 'frames_H_r6.json', GG.FOUND, G.LAND, tl.p.FPS, body, page='host.html', viewport=vp, out_dir='pane_h_r6')
    print(f'H (r6): {n} frames -> frames_H_r6.json')
    if G.STORY:
        n = write_frames(ui / 'frames_H_r6_now.json', G.NOW_AT, G.END, tl.p.FPS, body, page='host.html', viewport=vp, out_dir='pane_h_r6')
        print(f'H (r6, now): {n} frames -> frames_H_r6_now.json')
