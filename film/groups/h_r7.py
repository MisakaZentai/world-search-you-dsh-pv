"""Group H r7 (r18 sample; sample_r18/README.md): r6 (groups/h_r6.py, kept unchanged) with the puppy and the
fruit/vegetable classifier taken out. Reading her session, the left only shows what she herself did.

  stage     08 READ from T0, the same stage as interlude 3 under DSH_REP=g8 (rep_g8.py): the reading starts when her
            old session is opened, not at H. r6 read 09 READ here after interlude 3's 08 RESTORE.
  dog       her avatar no longer turns into a puppy. The persona pane holds her face (film 1's 14 x 14 avatar cells,
            in colour) to the end; dsh's header and rail keep her own picture (ui/pages/h_r7.py).
  ruff x3   the three big checks stay frame for frame (280.98 / 281.40 / 281.82); a small pixel paw lands beside each
            on the same frame, lit in her blue for the ruff, then ink. The lyric's dog is a paw print, not her.
  fruit     284.39: the trace finds her tomato line, `s.find("番茄") → 10:03` (the time dsh shows under that line on
            the right). The memory rows close up as r5 did and, where film 1's generate tile was, her avatar comes in
            as it was at that line: her face, read in four 16ths, top row first.
  to-ma-to  286.12 / 286.36 / 286.58: film 1's tomato avatar (film 1, 77.26 s, batch_c.avatars: her face colourised
            (34, 6, 6) -> (255, 110, 90), a green calyx) fills it from the bottom a third a syllable; the calyx pops
            on the last "to", as her 🍅 lights on the right. The same happens to dsh's avatar on the right.
  full      287.50: the find closes, the avatar is her face again (0.16 s), and the slab starts coming off 明天见 as
            before. No fruit / vegetable bars, no step counter, no generate() call.
  now       DSH_END=story: the last shot as r6, but your cursor does not blink (a still ink block; only elapsed
            moves) and the header no longer shows `memory: ?`.

Switches: DSH_H=r7 (film.py); DSH_END=story as r6. Times are r5's (groups/h_r5.py).
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageOps
import cast
import hud
import panes
import tl
from groups import a_open as AO
from groups import b_open as BO
from groups import c_pane as CPN
from groups import d_pane as DP
from groups import g as GG
from groups import h as GH
from groups import h_r5 as H5
from groups import h_r6 as H6
from groups.base import _size_for, add, big_word, full_frame
from hud import BG, INK, SLAB, lv
from panes import FAINT, SUB, TXT
from tuikit import ease, glyph
from tuikit.uipane import PaneFrames
P = tl.p
FPS = P.FPS
mtx, mw = (BO.mtx, BO.mw)
COL, MEM = (CPN.COL, CPN.MEM)
T0, T1 = (H5.T0, H5.T1)
ROW_T, PROG_T, RUFF, H1_BACK, SCROLL = (H5.ROW_T, H5.PROG_T, H5.RUFF, H5.H1_BACK, H5.SCROLL)
FRUIT, TOMATO_T, PIN_T, JUICE, JUICE_END = (H5.FRUIT, H5.TOMATO_T, H5.PIN_T, H5.JUICE, H5.JUICE_END)
QUIET, PRESS, REVEAL, RIGHT_BACK = (H5.QUIET, H5.PRESS, H5.REVEAL, H5.RIGHT_BACK)
LAND, MOVE, KEYS, RETURN, BLINK = (H5.LAND, H5.MOVE, H5.KEYS, H5.RETURN, H5.BLINK)
ZOOM_IN, ZOOM_OUT = (H5.ZOOM_IN, H5.ZOOM_OUT)
CHIME_T, CHIME_WAV = (PRESS, GH.CHIME_WAV)
SUPPORT = H5.SUPPORT
STORY, NOW_AT, NOW_LEN, END = (H6.STORY, H6.NOW_AT, H6.NOW_LEN, H6.END)
TITLE = 'you@surface · read'
CMD = '$ dsh session read 大肥鱼 --archive --from 1'
STAGE = '08 READ'
H6.STAGE = STAGE
NOW_TITLE, PROMPT = (H6.NOW_TITLE, H6.PROMPT)
FIND_AT = FRUIT[3]
READ_STEPS = [tl.grid(FIND_AT, k, 4) for k in range(5)]
TOM_STEPS = TOMATO_T[1:4]
CALYX_AT = TOMATO_T[3]
BACK = (REVEAL, REVEAL + 0.16)
FIND_TIME = '10:03'
N = 14
CALYX = [(5, 0), (8, 0), (6, 1), (7, 1), (4, 1), (9, 1)]
CALYX_COL = (80, 190, 90)
TOM_TINT = ((34, 6, 6), (255, 110, 90))
F1_NAVY = H5.F1_NAVY
AV_SMALL, AV_BIG = (8, 13)

@lru_cache(maxsize=1)
def cells():
    """(face, tomato): film 1's avatar recipe (pv_dsh_frontend_20260927/batch_c.avatars), 14 x 14 RGB arrays. The
    tomato equals film 1's avatars/c/tomato.png cell for cell (checked, max diff 0)."""
    im = Image.open(tl.HERE / 'assets/character/whale-cheerful.webp').convert('RGBA')
    bg = Image.new('RGBA', im.size, (9, 14, 30, 255))
    bg.alpha_composite(im)
    crop = bg.convert('RGB').crop((250, 40, 690, 480))
    face = np.asarray(crop.resize((N, N), Image.Resampling.BOX), np.float32)
    g = ImageOps.grayscale(crop).resize((N, N), Image.Resampling.BOX)
    tom = np.asarray(ImageOps.colorize(g, *TOM_TINT).convert('RGB'), np.float32).copy()
    return (face, tom)

def red_rows(t):
    """How many rows (from the bottom, 0..N) are film 1's tomato at t: a third on each of to / ma / to."""
    n = sum((1 for x in TOM_STEPS if t >= x))
    if not n:
        return 0.0
    return N * (n - 1 + ease.ease_out(ease.prog(t, TOM_STEPS[n - 1], TOM_STEPS[n - 1] + 0.1))) / 3

def back_u(t):
    return ease.smooth(ease.prog(t, *BACK))

def avatar_cells(t):
    """The 14 x 14 colours at t and whether the calyx shows: her face; from "to" the tomato rises; on "full" her
    face again."""
    face, tom = cells()
    out = face.copy()
    r = red_rows(t)
    for j in range(N):
        k = ease.clamp(r - (N - 1 - j))
        if k > 0:
            out[j] = face[j] * (1 - k) + tom[j] * k
    calyx = CALYX_AT <= t
    ub = back_u(t)
    if ub > 0:
        out = out * (1 - ub) + face * ub
    return (out, calyx and ub < 1, ub)

def _paint_avatar(d, x, y, cell, t, level, rows=N):
    """Film 1's avatar cells at (x, y), `rows` of them shown from the top (the reading)."""
    col, calyx, ub = avatar_cells(t)
    ci = int(round(cell))
    for j in range(min(N, rows)):
        for i in range(N):
            c = col[j, i]
            if calyx and (i, j) in CALYX:
                c = np.array(CALYX_COL, np.float32) * (1 - ub) + c * ub
            c = glyph.mix(BG, tuple((int(v) for v in c)), level)
            xx, yy = (x + i * cell, y + j * cell)
            d.rectangle((xx, yy, xx + ci - 2, yy + ci - 2), fill=c)

def _slot(d, t, c, level):
    """Where film 1's generate tile was (r5): her avatar as it was at her tomato line. Big from "fruit" (the rows
    close up to the right of it, r5 round 2), r5-1's place from the 16th after the beat before "full"."""
    x0, y0, x1, y1 = c
    a = ease.ease_out(ease.prog(t, FIND_AT, FIND_AT + 0.12)) * level
    if a <= 0.01:
        return
    ut = H5.tile_big(t)
    cell = ease.lerp(AV_SMALL, AV_BIG, ut)
    side = N * cell
    px = x0 + 18
    py = ease.lerp(y1 - 14 - N * AV_SMALL, y0 + 88, ut)
    pop = 1.0 + 0.08 * (1 - ease.ease_out(ease.prog(t, CALYX_AT, CALYX_AT + 0.14))) if t >= CALYX_AT else 1.0
    cx, cy = (px + side / 2, py + side)
    cell *= pop
    side = N * cell
    px, py = (cx - side / 2, cy - side)
    d.rectangle((px - 4, py - 4, px + side + 3, py + side + 3), fill=glyph.mix(BG, F1_NAVY, a))
    rows = N * sum((1 for x in READ_STEPS[1:] if t >= x)) // 4 if t < READ_STEPS[-1] else N
    rows = max(rows, 2)
    _paint_avatar(d, px, py, cell, t, a, rows)
    if rows < N:
        yy = py + rows * cell
        d.line([(px - 4, yy), (px + side + 3, yy)], fill=hud.her(1.0, a), width=2)
    cap = ut
    if cap > 0.01:
        ty = py + side + 8
        w = mtx(d, (px, ty), 'avatar · ', 13, lv(INK, SUB * a * cap))
        mtx(d, (px + w, ty), FIND_TIME, 13, lv(INK, 0.9 * a * cap), bold=True)
PAW = ['..##.##..', '..##.##..', '##.....##', '##.###.##', '..#####..', '.#######.', '.#######.', '..##.##..']
PAW_CELL = 3

def _stamp(d, t, c, k, level):
    """h_r5._stamp (the big check by the title), with a small paw landing beside it on the same frame."""
    if t < RUFF[k]:
        return
    bump = 1.0 + 0.12 * (1 - ease.prog(t, RUFF[k], RUFF[k] + 0.12))
    cell = int(round(7 * bump))
    w = 10 * cell
    x, y = (c[2] - 18 - w + (w - 70) / 2, c[1] + 16 - (cell - 7) * 3.5)
    hud.pix(d, GH.CHECK, int(x), int(y), cell, {'#': lv(INK, level)})
    pc = PAW_CELL + (1 if t < RUFF[k] + 0.08 else 0)
    lit = H5._lit_k(t, RUFF[k], RUFF[k] + 0.3)
    px = x - 9 * pc - 14
    py = c[1] + 16 + 7 * 7 - 8 * pc
    hud.pix(d, PAW, int(px), int(py), pc, {'#': hud.her(lit, level) if lit > 0.02 else lv(INK, level)})

def _memory(d, t, c, level):
    x0, y0, x1, y1 = c
    a = ease.ease_out(ease.prog(t, ROW_T[0], ROW_T[0] + 0.14)) * level
    if a <= 0:
        return
    dy = (1 - ease.ease_out(ease.prog(t, ROW_T[0], ROW_T[0] + 0.14))) * -8
    bk = H5.back_k(t)
    mtx(d, (x0 + 14, y0 + 16 + dy), '记忆', 30, lv(INK, a * bk), bold=True)
    mtx(d, (x0 + 14, y0 + 60 + dy), '~/memory/you/ · merged · 26 files · 她的 8 份', 11, lv(INK, SUB * a * bk))
    _stamp(d, t, c, 0, level * bk)
    big = H5._big_u(t)
    lvl = a * (1 - 0.8 * big)
    comp = ease.ease_io(ease.prog(t, *H5.COMPACT))
    top, pitch = (y0 + 84, ease.lerp((y1 - 10 - (y0 + 84)) / 8, H5.ROW_PITCH_C, comp))
    tb = H5.rows_big(t)
    wx = x0 + 14 + H5.ROWS_SHIFT * tb
    lx0, lx1 = (ease.lerp(x0 + 262, x0 + 472, tb), x1 - 78)
    chk_x = x1 - 26
    sk = H5._slab_k(t)
    for i, name in enumerate(H5.ORDER):
        y = top + i * pitch
        cy = y + 12 - 3 * comp
        word = AO.WORDS[name]
        checked = i < 7 and t >= PROG_T[i]
        lit = H5._tick_lit(i, t) if i < 7 else 1.0 if JUICE <= t < JUICE + 0.5 else 1 - ease.prog(t, JUICE + 0.5, JUICE + 0.8) if t >= JUICE else 0.0
        ink = TXT if checked or (i == 7 and sk > 0) else SUB
        tw = mtx(d, (wx, y), word, 15, lv(INK, ink * lvl))
        if comp < 1:
            d.text((wx, y + 19), name, font=P.font(9), fill=lv(INK, FAINT * lvl * (1 - comp)))
        cx = lx0 + (AO.SCORE[name] - 250) / (H5.HI - 250) * (lx1 - lx0)
        r = 0.72 * (8 + 12 * (AO.SCORE[name] - H5.LO) / (H5.HI - H5.LO)) * (1 - 0.36 * comp)
        AO._thread(d, wx + tw + 10, cx - r - 6, cy, lvl)
        AO._bubble(d, cx, cy, r, r, lit, lvl)
        d.text((cx + r + 7, cy - 7), str(AO.SCORE[name]), font=P.font(12, 'bold'), fill=lv(INK, ink * lvl))
        if checked:
            k = ease.ease_out(ease.prog(t, PROG_T[i], PROG_T[i] + 0.1))
            cdy = 3 * comp if t < JUICE else 0.0
            hud.pix(d, GH.CHECK, int(chk_x), int(cy - 7 - cdy), 2, {'#': lv(INK, (0.5 + 0.5 * k) * lvl)})
        if i == 7 and sk < 1:
            sx0, sx1 = (wx - 8, cx + r + 46)
            sx0 = ease.lerp(sx0, sx1, sk)
            sy0, sy1 = (y - 5 + 4 * comp, y + 29 - 12 * comp + (2 * comp if t < JUICE else 0.0))
            d.rectangle((sx0, sy0, sx1, sy1), fill=lv(SLAB, a))
            if sk < 0.34:
                d.text((sx1 - 8, (sy0 + sy1) / 2), AO.PIN_LABEL, font=hud.font(10, AO.PIN_LABEL, True), fill=BG, anchor='rm')
    _slot(d, t, c, level)
    if big > 0:
        bump = 1.0 + 0.08 * (1 - ease.prog(t, JUICE, JUICE + 0.12))
        word = AO.WORDS[AO.SWEETEST]
        f = hud.font(_size_for(word, H5.BIG_H, True), word, True)
        bottom = y0 + 74 + f.getbbox(word)[3] - f.getbbox(word)[1]
        box = big_word(d, word, (x1 - 14, bottom), H5.BIG_H, lv(INK, big * level), 'rd', bump=bump, halo=round(3 * big * level))
        rl = 1.0 if t < JUICE_END else 1 - ease.prog(t, JUICE_END, JUICE_END + hud.LIVE_FADE)
        ra = ease.ease_out(ease.prog(t, JUICE + 0.08, JUICE + 0.3)) * level
        hud.tx(d, (box[2], box[3] + 22), H5.REPLY, 24, lv(hud.her(rl), ra), anchor='ra')

def _persona(d, t, c, level):
    a = H5._head(d, t, c, 1, '人格', '大肥鱼 · agent preset', level)
    for j, (k, v) in enumerate(H5.PERSONA + [('avatar', '')]):
        y = c[1] + 88 + j * 22
        mtx(d, (c[0] + 14, y), k, 12, lv(INK, FAINT * a))
        mtx(d, (c[0] + 84, y), v, 13, lv(INK, SUB * a))
    if a > 0.01:
        x, y = (c[0] + 244, c[1] + 64)
        side = N * AV_SMALL
        d.rectangle((x - 4, y - 4, x + side + 3, y + side + 3), fill=glyph.mix(BG, F1_NAVY, a))
        _paint_avatar(d, x, y, AV_SMALL, ROW_T[0], a)
    _stamp(d, t, c, 1, level)

def _session(d, t, c, level):
    a = H5._head(d, t, c, 2, '会话', 'archive/deepseek-v4.1-flash/ · 412 行', level)
    for j, (who, s) in enumerate(H5.SESSION):
        y = c[1] + 88 + j * 22
        mtx(d, (c[0] + 14, y), who, 12, lv(INK, FAINT * a))
        mtx(d, (c[0] + 40, y), s, 13, lv(INK, SUB * a))
    _stamp(d, t, c, 2, level)
CODE = [(T0, 's = session.open("大肥鱼", archived=True)', None), (RUFF[0], 's.memory', (RUFF[0] + 0.05, '8/8 · ok')), (RUFF[1], 's.persona', (RUFF[1] + 0.05, '大肥鱼 · ok')), (RUFF[2], 's.session', (RUFF[2] + 0.05, '412 行 · ok')), (FRUIT[0], 's.model', (FRUIT[1], f'{cast.name('her')} · Model Not Exist')), (FIND_AT, 's.find("番茄")', (FIND_AT + 0.05, FIND_TIME)), (PIN_T[0], 'memory["see_you"].unpin()', (JUICE, '"明天见"'))]

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
        if ret and t >= ret[0] and (n >= len(s)):
            mtx(d, (r[0] + 10 + w + 12, y), '→ ' + ret[1], 14, lv(INK, 0.7 * a * ease.prog(t, ret[0], ret[0] + 0.1)), bold=True)
RUN = {'trace': [(a, ret[0] if ret else a + 0.6) for a, _s, ret in CODE], 'memory': [(PROG_T[0], RUFF[0] + 0.1), (FIND_AT, CALYX_AT + 0.2), (PIN_T[0], JUICE + 0.3)], 'persona': [(RUFF[1] - 0.05, RUFF[1] + 0.1)], 'session': [(RUFF[2] - 0.05, RUFF[2] + 0.1)], 'model': [(FRUIT[0], FRUIT[1] + 0.2)]}
STATUS = {'memory': 'by lovability'}

def draw_left(img, d, t, level=1.0):
    L = H5.layout(t)
    ug = H5._u_gone(t)
    bk = H5.back_k(t)
    for name, rect in L.items():
        lvl = level * (1 - ug if name in ('persona', 'session') else 1.0)
        if name == 'trace':
            lvl *= H5.back_k(t, 'trace')
        elif name == 'model':
            lvl *= bk
        if lvl <= 0.01:
            continue
        if level > 0.01:
            d.rectangle(rect, fill=BG)
        with panes.Clip(img, rect) as dd:
            if name == 'trace':
                _trace(dd, t, rect, lvl)
            elif name == 'memory':
                _memory(dd, t, rect, lvl)
            elif name == 'persona':
                _persona(dd, t, rect, lvl)
            elif name == 'session':
                _session(dd, t, rect, lvl)
            elif name == 'model':
                H6._model(dd, t, rect, lvl)
        panes.box(d, rect, name, t, panes.run_k(t, RUN.get(name, ())), lvl, STATUS.get(name, ''))
    with CPN._strip_in(MEM):
        hud.strip(d, t, None, level=level * bk, merged=1.0)
    d.rectangle((MEM[0] + 4, MEM[1] + 8, MEM[2] - 4, MEM[1] + 21), fill=BG)
    panes.box(d, MEM, 'mem', t, 0.0, level * bk)

def _body(c, img, d):
    t = c.t
    q = H5.quiet_k(t)
    hud.tx(d, (36, hud.Y_CMD), CMD, 13, lv(INK, 0.86 * q * H5.back_k(t)))
    draw_left(img, d, t, q)

def _now(film, c):
    """h_r6._now with your cursor still: an ink block that does not blink (only elapsed moves)."""
    t = c.t
    img = film.background(t)
    d = ImageDraw.Draw(img)
    hud.frame(d, hud.left_rect(t), NOW_TITLE)
    w = hud.tx(d, (36, hud.Y_CMD), PROMPT, 13, lv(INK, 0.86))
    cx = 36 + w + 9
    d.rectangle((cx, hud.Y_CMD + 1, cx + 7, hud.Y_CMD + 16), fill=INK)
    c.img.paste(img)

def register(film):
    full_frame(T0, H1_BACK, 0.3, 0.4)
    for i in range(7):
        hud.LIVE.append((PROG_T[i], PROG_T[i + 1] if i < 6 else RUFF[0]))
    for (a, _s), nx in zip(H5.TOM_SEG, [x[0] for x in H5.TOM_SEG[1:]] + [PIN_T[0]]):
        hud.LIVE.append((a, nx))
    hud.LIVE.append((JUICE, JUICE_END))
    add(film, 'h1_check', T0, H1_BACK, _body, TITLE)
    add(film, 'h2_model', H1_BACK, TOMATO_T[0] - 0.3, _body, TITLE)
    add(film, 'h3_tomato', TOMATO_T[0] - 0.3, QUIET, _body, TITLE)
    add(film, 'h4_quiet', QUIET, PRESS, _body, TITLE)
    film.character = DP.dsh_layer(film, film.character, 'ui/pane_h_r7', GG.FOUND, LAND)
    if STORY:
        film.character = DP.dsh_layer(film, film.character, 'ui/pane_h_r7', NOW_AT, END)
    pane = PaneFrames(tl.HERE / 'ui/pane_h_r7', FPS, (P.W, P.H))

    def slide_fn(c):
        t = c.t
        img = film.background(t)
        d = ImageDraw.Draw(img)
        fade = SUPPORT * (1 - ease.smooth(ease.prog(t, PRESS, MOVE[0] + 0.3)))
        if fade > 0.01:
            hud.frame(d, hud.left_rect(t), TITLE, level=fade)
            hud.tx(d, (36, hud.Y_CMD), CMD, 13, lv(INK, 0.86 * fade))
            draw_left(img, d, t, fade)
        c.state['pane'] = False
        im = pane.image(int(round(t * FPS)))
        if im is not None:
            x, y, x1, y1, _s = H5.pane_rect(t)
            d.rectangle((x - 1, y - 1, x1 + 1, y1 + 1), outline=INK, width=2)
            sm = im.resize((max(1, int(round(x1 - x))), max(1, int(round(y1 - y)))), Image.LANCZOS)
            base = img.convert('RGBA')
            base.alpha_composite(sm, (int(round(x)), int(round(y))))
            img.paste(base.convert('RGB'))
        c.img.paste(img)
    chap = STAGE.split(' ', 1)[1]
    film.add('h5_slide', PRESS, LAND, slide_fn, chapter=chap)
    base_levels = film.levels
    s_lv = P.setting('support_level', 0.42)

    def levels(t):
        lv_ = base_levels(t)
        if PRESS <= t < LAND or t >= NOW_AT:
            return {k: 1.0 for k in lv_}
        if RIGHT_BACK[0] <= t < PRESS and 'right' in lv_:
            up = s_lv + (1 - s_lv) * ease.smooth(ease.prog(t, *RIGHT_BACK))
            lv_ = dict(lv_)
            lv_['right'] = max(lv_['right'], up)
        return lv_
    film.levels = levels

    def last_fn(c):
        c.img.paste(H5.zoomed(H6.last_frame(c.t), c.t))
        c.black = True
    film.add('h5_last', LAND, NOW_AT, last_fn, chapter=chap)
    if STORY:

        def now_fn(c):
            _now(film, c)
        film.add('h6_now', NOW_AT, END, now_fn, chapter=chap)
    for t0, side in [(T0, 'both'), (REVEAL, 'left'), (QUIET, 'right')] + ([(NOW_AT, 'both')] if STORY else []):
        film.set_lead(t0, side)
    from groups.f import dissolve
    dissolve(film, 'h1_check', 0.4)
    film.finish.append(H6._finish)
    ch = film.chrome
    status0, chapter0 = (ch.status, ch.chapter)

    def status(t, ctx=None):
        s = list(status0(t, ctx))
        if t >= T0 and s:
            s[0] = (STAGE, s[0][1])
        if STORY and t >= NOW_AT:
            s = [x for x in s if not x[0].startswith('memory')]
        return s

    def chapter(t, ctx=None):
        return chap if t >= T0 else chapter0(t, ctx)
    ch.status, ch.chapter = (status, chapter)
    if STORY:
        header0 = ch.header

        def header(img, t, ctx):
            header0(img, t, ctx)
            if t >= NOW_AT:
                H6._hold_counter(ch, img, t, ctx)
        ch.header = header
