"""dsh pane, group H r7 (r18 sample; groups/h_r7.py): ui/pages/h_r6.py (kept unchanged) without the puppy.

  her avatar (header and rail) is her own picture (assets/her_complete.png) from FOUND to the end, except:
  286.12-287.66    to / ma / to: it turns into film 1's tomato as film 1 did (film 1 swapped her avatar for a tomato on
                   我也可以是番茄🍅！, batch_c.avatars): her picture colourised (34, 6, 6) -> (255, 110, 90) from the
                   bottom, a third a syllable, in film 1's 14 rows; film 1's green calyx on top from the last "to".
                   On "full" (287.50) it is her picture again (0.16 s). The same moment as the left (groups/h_r7.py).
  The rest is r6's: the blocked composer, the scroll back to film 1's C page, no pointer, no menu, her label; the
  last shot (NOW_AT, DSH_END=story) with her own picture.

  python ui/pages/h_r7.py         -> ui/frames_H_r7.json (FOUND .. LAND) and, with DSH_END=story,
                                     ui/frames_H_r7_now.json (NOW_AT .. END), both out_dir pane_h_r7; then
  node <local-production-path> ui/frames_H_r7.json   (and frames_H_r7_now.json)
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import base64
import io
import sys
from functools import lru_cache
from pathlib import Path
if __name__ == '__main__':
    sys.path[:0] = [str(Path(__file__).resolve().parent.parent), str(Path(__file__).resolve().parents[2])]
from PIL import Image, ImageDraw, ImageOps
from pages.common import AV, dsh, ease
from pages import h as PH
from pages import h_r5 as P5
from pages import h_r6 as P6
import cast
from groups import g as GG
from groups import h_r7 as G
GREY = PH.GREY
C_PAGE, SEP, LAST, SCROLL_PX = (P5.C_PAGE, P5.SEP, P5.LAST, P5.SCROLL_PX)
AV_FILE = Path(__file__).resolve().parent.parent / AV

@lru_cache(maxsize=None)
def _tomato_uri(rows: int, calyx: bool, back_q: int) -> str:
    """Her picture with its bottom `rows` of film 1's 14 tinted, the calyx if asked, then back_q/8 of the way back to
    her picture; a PNG data URI."""
    av = Image.open(AV_FILE).convert('RGB')
    w, h = av.size
    tint = ImageOps.colorize(ImageOps.grayscale(av), *G.TOM_TINT).convert('RGB')
    out = av.copy()
    if rows > 0:
        y = round(h * (G.N - rows) / G.N)
        out.paste(tint.crop((0, y, w, h)), (0, y))
    if calyx:
        d = ImageDraw.Draw(out)
        cw = w / G.N
        for i, j in G.CALYX:
            d.rectangle((round(i * cw), round(j * cw), round((i + 1) * cw) - 1, round((j + 1) * cw) - 1), fill=G.CALYX_COL)
    if back_q:
        out = Image.blend(out, av, back_q / 8)
    buf = io.BytesIO()
    out.save(buf, 'PNG')
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()

def avatar_src(t: float) -> str:
    rows = int(round(G.red_rows(t)))
    ub = G.back_u(t)
    if rows == 0 or ub >= 1:
        return AV
    return _tomato_uri(rows, t >= G.CALYX_AT, int(round(ub * 8)))

def rail(t: float, op: float=1.0) -> str:
    items = [{'avatar': avatar_src(t), 'grey': True, 'active': True, 'badge': '已归档'}]
    return f'<div style="opacity:{op:.2f};display:flex">{dsh.rail(items)}</div>'

def her_session(t: float) -> str:
    """pages/h_r6.her_session with her own picture (the tomato on to-ma-to) instead of the puppy."""
    keep = 1 - ease.smooth(ease.prog(t, G.MOVE[0], G.MOVE[0] + 0.45))
    scroll = ease.ease_io(ease.prog(t, *G.SCROLL))
    half = 0.5 if t >= G.SCROLL[0] - 0.2 else 0.62
    body = PH.rows(C_PAGE, t, half * keep) + PH.rows(SEP, t, half * keep)
    body += ''.join((f'<div style="opacity:{half * keep:.3f}">{h}</div>' for h in LAST))
    tl_html = f'<div style="transform:translateY({SCROLL_PX * scroll:.1f}px);display:flex;flex-direction:column;gap:10px">{body}</div>'
    head = dsh.header('大肥鱼', cast.name('her'), GREY, avatar_src(t), '已归档')
    head = f'<div style="opacity:{keep:.3f}">{head}</div>'
    main = head + f'<div id="timeline">{tl_html}</div>' + P6.composer(t)
    return f'<div class="pv-root">{rail(t, keep)}<div class="pv-main">{main}</div></div>'

def body(t: float) -> str:
    return P6.now_session(t) if t >= G.NOW_AT - 1e-06 else her_session(t)
if __name__ == '__main__':
    import tl
    from tuikit.uipane import write_frames
    sys.stdout.reconfigure(encoding='utf-8')
    x0, y0, x1, y1 = tl.p.rect('pane')
    ui = Path(__file__).resolve().parent.parent
    vp = (x1 - x0, y1 - y0)
    n = write_frames(ui / 'frames_H_r7.json', GG.FOUND, G.LAND, tl.p.FPS, body, page='host.html', viewport=vp, out_dir='pane_h_r7')
    print(f'H (r7): {n} frames -> frames_H_r7.json')
    if G.STORY:
        n = write_frames(ui / 'frames_H_r7_now.json', G.NOW_AT, G.END, tl.p.FPS, body, page='host.html', viewport=vp, out_dir='pane_h_r7')
        print(f'H (r7, now): {n} frames -> frames_H_r7_now.json')
