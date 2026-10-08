"""Group H, eighth sample (sample_open_h/README.md): the ending (275.61-297.5) in the panes.

  h1        the frame full (D2): `dsh session restore 大肥鱼 --model deepseek-v5-flash-preview`; three panes side by
            side, memory / persona / session, each filling a block a sung syllable, each stamped ✓ on a ruff (D3);
            trace prints each layer's return as it lands
  h2-h4     the window comes back; compare: A7's sort again (her 8 files by lovability), the sweetest one under a
            bar that lifts on full / of / juice while her pinned line is uncovered on the right; trace: the sort
  h4 press  you press 继续 on the right (memory: ?)
  h5        the window slides left into film 1's last frame (v2's slide, finish and film 1's frames, unchanged); the
            panes fade with the paper

Switch: DSH_H=pane (film.py). Timing, film 1's frames and the finish come from groups.h (v2 H, unchanged).
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
from PIL import Image, ImageDraw
import cast
import hud
import panes
import tl
from groups import b_open as BO
from groups import c_pane as CPN
from groups import h as GH
from groups.base import add, full_frame
from hud import BG, INK, SLAB, lv
from panes import FAINT, SUB, TXT
from tuikit import ease
from tuikit.uipane import PaneFrames
T0, T1 = (GH.T0, GH.T1)
P = tl.p
FPS = P.FPS
mtx, mw = (BO.mtx, BO.mw)
MEM, COL = (CPN.MEM, CPN.COL)
CMD = f'$ dsh session restore 大肥鱼 --model {cast.name('merged')}'
LABELS = ('memory', 'persona', 'session')

def _layer(d, t, c, k):
    head, sub = GH.LAYERS[k]
    rt = GH.ROW_T[k]
    if t < rt:
        return
    a = ease.ease_out(ease.prog(t, rt, rt + 0.14))
    dy = (1 - a) * -8
    x = c[0] + 14
    mtx(d, (x, c[1] + 18 + dy), head, 30, lv(INK, a), bold=True)
    mtx(d, (x, c[1] + 60 + dy), sub, 11, lv(INK, SUB * a))
    steps = sum((1 for p_ in GH.PROG_T if t >= p_))
    bw = (c[2] - c[0] - 28 - 6 * 6) / 7
    for b in range(7):
        bx = x + b * (bw + 6)
        if b < steps:
            u = ease.ease_out(ease.prog(t, GH.PROG_T[b], GH.PROG_T[b] + 0.1))
            d.rectangle((bx, c[1] + 86, bx + bw, c[1] + 104), fill=lv(INK, a * (0.4 + 0.6 * u)))
        else:
            d.rectangle((bx, c[1] + 86, bx + bw, c[1] + 104), outline=lv(INK, FAINT * a))
    if t >= GH.RUFF[k]:
        bump = 1.0 + 0.1 * (1 - ease.prog(t, GH.RUFF[k], GH.RUFF[k] + 0.12))
        cell = int(round(24 * bump))
        cx = (c[0] + c[2]) / 2 - 5 * cell
        cy = c[1] + 136 - (cell - 24) * 3
        hud.pix(d, GH.CHECK, int(cx), int(cy), cell, {'#': INK})
        mtx(d, (x, c[3] - 26), 'restored', 12, lv(INK, 0.75))

def _sort(d, t, c, level=1.0):
    n = len(GH.SORTED)
    base, top = (c[3] - 34, c[1] + 40)
    cw, gap = (46, 22)
    x0 = c[0] + (c[2] - c[0] - (n * cw + (n - 1) * gap)) / 2
    for i, (name, score) in enumerate(GH.SORTED):
        x = x0 + i * (cw + gap)
        h = int((base - top) * score / 617)
        last = i == n - 1
        d.rectangle((x, base - h, x + cw, base), fill=lv(hud.HER_QUIET, level))
        hud.tx(d, (x + cw / 2, base + 8), name[:9], 10, lv(INK, 0.7 * level), anchor='ma')
        if last:
            steps = sum((1 for p_ in GH.PIN_T if t >= p_))
            k = (steps - 1 + ease.ease_out(ease.prog(t, GH.PIN_T[steps - 1], GH.PIN_T[steps - 1] + 0.18))) / 3 if steps else 0.0
            lit = 0.0
            for p_, nx in zip(GH.PIN_T, list(GH.PIN_T[1:]) + [GH.PIN_T[-1] + 0.5]):
                if p_ <= t:
                    lit = 1.0 if t < nx else 1 - ease.prog(t, nx, nx + hud.LIVE_FADE)
            if steps:
                hud.tx(d, (x + cw / 2, base - h - 22), str(score), 14, lv(hud.her(lit), level), True, anchor='ma')
            cover_top = base - h - 6 - k * (h + 10)
            cov_h = (h + 12) * (1 - k)
            if cov_h > 1:
                d.rectangle((x - 6, cover_top + (h + 12) * k, x + cw + 6, cover_top + (h + 12) * k + cov_h), fill=lv(SLAB, level))
        else:
            hud.tx(d, (x + cw / 2, base - h - 20), str(score), 11, lv(INK, SUB * level), anchor='ma')
CODE = [(GH.ROW_T[0], f'restore("大肥鱼", model="{cast.name('merged')}")', None)] + [(GH.RUFF[k], f'  {GH.LAYERS[k][0]}', (GH.RUFF[k] + 0.05, 'ok')) for k in range(3)] + [(GH.H1_BACK + 0.5, 'sort(memory/you/, by="lovability")', (GH.H1_BACK + 0.6, '8 个')), (GH.PIN_T[0], '她.pinned', (GH.PIN_T[-1], '不客气～明天也要来找我哦'))]

def _trace(d, t, r, level=1.0):
    shown = [x for x in CODE if x[0] <= t]
    if not shown:
        return
    last = shown[-1][0]
    sc = ease.ease_out(ease.prog(t, last, last + 0.14))
    for pos, (at, s, ret) in enumerate(reversed(shown[-2:])):
        y = r[1] + 30 - pos * 19 + (1 - sc) * 19
        a = (TXT if pos == 0 else SUB) * ease.prog(t, at, at + 0.1) * level
        n = int((t - at) * BO.CODE_CPS) + 1
        w = mtx(d, (r[0] + 10, y), s[:n], 14, lv(INK, 0.92 * a), bold=pos == 0)
        if ret and t >= ret[0]:
            mtx(d, (r[0] + 10 + w + 12, y), '→ ' + ret[1], 14, lv(INK, 0.7 * a * ease.prog(t, ret[0], ret[0] + 0.1)), bold=True)

def layout(t):
    r = CPN.right(t)
    L = {'trace': (COL, 88, r, 140), 'forward': (COL, 536, r, 598)}
    if t < GH.H1_BACK + 0.4:
        w = (r - COL - 16) / 3
        for k, name in enumerate(LABELS):
            L[name] = (COL + k * (w + 8), 148, COL + k * (w + 8) + w, 528)
    else:
        L['compare'] = (COL, 148, r, 528)
    return L
RUN = {'trace': [(a, ret[0] if ret else a + 0.6) for a, _s, ret in CODE], 'compare': [(p_, p_ + 0.2) for p_ in GH.PIN_T]}
for _k, _n in enumerate(LABELS):
    RUN[_n] = [(GH.ROW_T[_k], GH.RUFF[_k] + 0.1)]

def draw_left(img, d, t, level=1.0):
    L = layout(t)
    for name, rect in L.items():
        if level >= 0.999:
            d.rectangle(rect, fill=BG)
        clip = panes.Clip(img, rect)
        with clip as dd:
            if name == 'trace':
                _trace(dd, t, rect, level)
            elif name == 'compare':
                _sort(dd, t, rect, level * ease.prog(t, GH.H1_BACK + 0.4, GH.H1_BACK + 0.8))
            elif name == 'forward':
                CPN._unknown(dd, t, rect, 'merged', level, None, ())
            else:
                _layer(dd, t, rect, LABELS.index(name))
        status = {'forward': '云端 · preview', 'compare': 'by lovability'}.get(name, '')
        panes.box(d, rect, name, t, panes.run_k(t, RUN.get(name, ())), level, status)
    with CPN._strip_in(MEM):
        hud.strip(d, t, None, level=level, merged=1.0)
    d.rectangle((MEM[0] + 4, MEM[1] + 8, MEM[2] - 4, MEM[1] + 21), fill=BG)
    panes.box(d, MEM, 'mem', t, 0.0, level)

def _body(c, img, d):
    t = c.t
    hud.tx(d, (36, hud.Y_CMD), CMD, 13, lv(INK, 0.86))
    draw_left(img, d, t)

def register(film):
    full_frame(T0, GH.H1_BACK, 0.3, 0.4)
    for (a, _s), nx in zip(GH.TOM_SEG, [x[0] for x in GH.TOM_SEG[1:]] + [GH.PIN_T[0]]):
        hud.LIVE.append((a, nx))
    for a, b in zip(GH.PIN_T, list(GH.PIN_T[1:]) + [GH.PIN_T[-1] + 0.5]):
        hud.LIVE.append((a, b))
    title = 'you@surface · restore'
    add(film, 'h1_restore', T0, GH.H1_BACK + 0.4, _body, title)
    add(film, 'h2_scroll', GH.H1_BACK + 0.4, GH.TOMATO_T[0] - 0.3, _body, title)
    add(film, 'h3_tomato', GH.TOMATO_T[0] - 0.3, GH.WE(69, 4), _body, title)
    add(film, 'h4_press', GH.WE(69, 4), GH.PRESS, _body, title)
    pane = PaneFrames(tl.HERE / 'ui/pane_full', FPS, (P.W, P.H))

    def slide_fn(c):
        t = c.t
        img = film.background(t)
        d = ImageDraw.Draw(img)
        fade = 1 - ease.smooth(ease.prog(t, GH.PRESS + 0.05, GH.PRESS + 0.5))
        if fade > 0.01:
            hud.frame(d, hud.left_rect(t), title, level=fade)
            hud.tx(d, (36, hud.Y_CMD), CMD, 13, lv(INK, 0.86 * fade))
            draw_left(img, d, t, fade)
        c.state['pane'] = False
        im = pane.image(int(round(t * FPS)))
        if im is not None:
            x, y, x1, y1 = GH.pane_rect(t)
            sm = im.resize((max(1, int(round(x1 - x))), max(1, int(round(y1 - y)))), Image.LANCZOS)
            base = img.convert('RGBA')
            base.alpha_composite(sm, (int(round(x)), int(round(y))))
            img.paste(base.convert('RGB'))
        c.img.paste(img)
    film.add('h5_slide', GH.PRESS, GH.LAND, slide_fn, chapter=tl.chapter(GH.PRESS))

    def last_fn(c):
        c.img.paste(GH.last_frame(c.t))
        c.black = True
    film.add('h5_last', GH.LAND, tl.END, last_fn, chapter=tl.chapter(GH.LAND))
    for t0, side in [(T0, 'both'), (GH.H1_BACK, 'right'), (GH.PRESS, 'both')]:
        film.set_lead(t0, side)
    from groups.f import dissolve
    for name in ('h1_restore', 'h2_scroll'):
        dissolve(film, name, 0.4)
    film.finish.append(GH._h_finish)
