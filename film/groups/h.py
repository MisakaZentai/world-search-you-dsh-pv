"""Group H: dog, tomato, restore (275.61-296.0), STORYBOARD_v2 H1-H5, PLAN_H.md.

  h1_restore  D2: the terminal fills the frame; three layers of the restore fill on the sung syllables
              and the three ruffs stamp them: 记忆 ✓ 人格 ✓ 会话 ✓ (D3: each ✓ 182 px, a cell glyph)
  h2_scroll   the window comes back; her old session scrolls to film 1's group C page; the left shows
              the sort of A7 again, the sweetest one still under its bar
  h3_tomato   her tomato line, already written in film 1, lights up segment by segment (A, to-ma-to);
              the pinned line is uncovered in three steps on full / of / juice (right) and the bar over
              the last column lifts with it (left)
  h4_press    quiet: your pointer goes to 继续 and presses it on tl.QMARK_AT: the chime of film 1
              (assets/audio/chime_g.wav, CHIME_T), elapsed dissolves into 用时 3分27秒, memory: ?
  h5_slide    the window slides from the right to the left and turns into the deep sea; the 用时 3分27秒
              of the header lands on film 1's tail; the frame becomes film 1's last frame
  h5_last     film 1's own frames (assets/film1_end/, pixel for pixel): her caret types 在吗？ (unsent),
              then (D6) goes to the model label and types cast.name("merged") in her blue, one character
              per 16th, and comes back to blink after 在吗？ to the end (film 1's last frame but the label)

Local versions (frozen shared modules): _h_finish (header dissolve, chrome fade-out and the deep-sea
transform of film.py with film 1's frame crossfaded after it), _sort (A7's sorted columns: group A builds
its own; the interface here is STORYBOARD A7/H3).
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cast
import hud
import syl
import tl
from groups.base import add, full_frame
from hud import BG, INK, SLAB, X0, lv
from tuikit import ease, glyph
from tuikit.uipane import PaneFrames
W, WE = (tl.W, tl.WE)
T0, T1 = tl.span('H')
P = tl.p
FPS = P.FPS
ROW_T = [syl.times(66)[i] for i in (0, 1, 3)]
PROG_T = syl.times(67)[:7]
RUFF = syl.times(67)[7:10]
H1_BACK = tl.bar(163)
SCROLL = (W(68, 0), tl.bar(164))
TOMATO_T = syl.times(69)
TOM_SEG = [(TOMATO_T[0], '我也可以是'), (TOMATO_T[1], '番'), (TOMATO_T[2], '茄'), (TOMATO_T[3], '🍅！')]
PIN_T = TOMATO_T[4:7]
PIN_SEG = ['不客气～', '明天也要来找我哦', ' (｡･ω･｡)']
PRESS = tl.QMARK_AT
PTR_GO = tl.at_beat(PRESS, -3)
CHIME_T = PRESS
CHIME_WAV = 'assets/audio/chime_g.wav'
LAND = tl.next_beat(PRESS + 0.45)
KEYS = [tl.grid(LAND, k, 2) for k in (1, 2, 3)]
SELECT = tl.grid(KEYS[2], 1, 2)
FIRST = tl.grid(SELECT, 1, 2)
NAME = cast.name('merged')
CHAR_T = [tl.grid(FIRST, i, 4) for i in range(len(NAME))]
RETURN = tl.grid(CHAR_T[-1], 2, 4)
BLINK = 0.53
assert RETURN + BLINK <= tl.END - 1 / FPS + 1e-06, "film 1's last frame (caret dim) must be the last frame"
F1 = tl.HERE / 'assets/film1_end'
F1_FILES = {'empty': 'f1_209.000_empty.png', 'k1': ['f1_209.292_k1a.png', 'f1_209.333_k1b.png', 'f1_209.375_k1c.png', 'f1_209.417_k1d.png'], 'k2': 'f1_209.500_k2.png', 'full': 'f1_209.750_k3_caret_full.png', 'dim': 'f1_211.875_last_caret_dim.png'}
CARD_F1 = (36, 489, 371, 587)
TAIL_F1 = (216, 461)
LABEL_END = 287
LABEL_TOP = 560
CARET_BOX = (92, 495, 117, 531)

@lru_cache(maxsize=None)
def f1(name: str) -> np.ndarray:
    return np.asarray(Image.open(F1 / name).convert('RGB'), np.uint8)

@lru_cache(maxsize=None)
def _row_bg(name: str) -> np.ndarray:
    """The composer card's colour per row (it carries film 1's scanlines), from a clean strip of it."""
    a = f1(name).astype(np.float32)
    return np.median(a[:, 120:140], axis=1)

@lru_cache(maxsize=1)
def _label_font():
    return ImageFont.truetype('C:/Windows/Fonts/seguisb.ttf', 13)

def _erase(a: np.ndarray, box, bg_rows):
    x0, y0, x1, y1 = box
    a[y0:y1, x0:x1] = bg_rows[y0:y1, None, :]

def _text(a: np.ndarray, s: str, x_end: float, colors, bg_rows):
    """Right-aligned label text ending at x_end, one colour per character, with the card's scanlines."""
    f = _label_font()
    meas = ImageDraw.Draw(Image.new('L', (1, 1)))
    w = meas.textlength(s, font=f)
    x = x_end - w
    top = LABEL_TOP - f.getbbox('D')[1]
    m = bg_rows.mean(axis=1)
    peak = np.maximum.reduce([np.roll(m, 1), m, np.roll(m, -1)])
    rowk = np.clip(m / np.maximum(peak, 1), 0.6, 1.0)
    for ch, col in zip(s, colors):
        cw = meas.textlength(ch, font=f)
        im = Image.new('L', (int(cw) + 6, 24), 0)
        ImageDraw.Draw(im).text((2, 0), ch, font=f, fill=255)
        al = np.asarray(im, np.float32)[..., None] / 255
        xi, yi = (int(round(x)) - 2, int(round(top)))
        h, wd = al.shape[:2]
        reg = a[yi:yi + h, xi:xi + wd].astype(np.float32)
        c = np.array(col, np.float32)[None, None, :] * rowk[yi:yi + h, None, None]
        a[yi:yi + h, xi:xi + wd] = (reg * (1 - al) + c * al).astype(np.uint8)
        x += cw
    return x_end - w

def last_frame(t: float) -> Image.Image:
    """H5 from LAND: film 1's frames re-timed onto this song's 8ths, the model label retyped (D6)."""
    if t < KEYS[0]:
        name = F1_FILES['empty']
    elif t < KEYS[1]:
        name = F1_FILES['k1'][min(3, int((t - KEYS[0]) * FPS + 1e-06))]
    elif t < KEYS[2]:
        name = F1_FILES['k2']
    elif t < SELECT:
        name = F1_FILES['full']
    elif t < RETURN:
        name = F1_FILES['full']
    else:
        name = F1_FILES['full'] if (t - RETURN) // BLINK % 2 == 0 else F1_FILES['dim']
    a = f1(name).copy()
    bg = _row_bg(name)
    if SELECT <= t < RETURN:
        _erase(a, CARET_BOX, bg)
    if t < SELECT:
        return Image.fromarray(a)
    caret_x = LABEL_END + 2
    if t < FIRST:
        k = ease.smooth(ease.prog(t, SELECT, SELECT + 0.12))
        x0, y0, x1, y1 = (164, 552, LABEL_END + 2, 574)
        reg = a[y0:y1, x0:x1].astype(np.float32)
        a[y0:y1, x0:x1] = (reg * (1 - 0.35 * k) + np.array(hud.HER_QUIET, np.float32) * 0.35 * k).astype(np.uint8)
    else:
        _erase(a, (112, 550, LABEL_END + 3, 577), bg)
        n = sum((1 for x in CHAR_T if t >= x))
        cols = []
        for i in range(n):
            nxt = CHAR_T[i + 1] if i + 1 < len(CHAR_T) else RETURN
            u = 1.0 if t < nxt else 1 - ease.prog(t, nxt, nxt + hud.LIVE_FADE)
            cols.append(glyph.mix(hud.HER_QUIET, hud.HER_LIVE, u))
        if n:
            _text(a, NAME[:n], LABEL_END, cols, bg)
    if t < RETURN:
        a[557:573, caret_x:caret_x + 2] = np.array(hud.HER_LIVE, np.uint8)
    return Image.fromarray(a)
CHECK = ['........##', '.......##.', '......##..', '##...##...', '.##.##....', '..###.....', '...#......']
LAYERS = [('记忆', '~/memory/you/ · merged · 26 files'), ('人格', '大肥鱼 · agent preset'), ('会话', 'archive/deepseek-v4.1-flash/ · 412 行')]
SORTED = [('typo_you_made', 233), ('weather', 305), ('your_cat', 389), ('laugh_0314', 471), ('first_hello', 512), ('goodnight', 548), ('last_msg', 590), ('see_you', 617)]

def _sort(d, t, level=1.0):
    """The sorted columns of A7 (local version; group A draws its own): the last one under a bar that lifts
    in three steps on full / of / juice."""
    x0, base, cw, gap = (X0 + 30, 470, 46, 22)
    hud.tx(d, (X0, hud.Y_TOP + 4), '$ sort --by lovability ~/memory/you/   # A7', 13, lv(INK, 0.8 * level))
    for i, (name, score) in enumerate(SORTED):
        x = x0 + i * (cw + gap)
        h = int(330 * score / 617)
        last = i == len(SORTED) - 1
        d.rectangle((x, base - h, x + cw, base), fill=lv(hud.HER_QUIET, level))
        hud.tx(d, (x + cw / 2, base + 8), name[:9], 10, lv(INK, 0.7 * level), anchor='ma')
        if last:
            steps = sum((1 for p_ in PIN_T if t >= p_))
            k = (steps - 1 + ease.ease_out(ease.prog(t, PIN_T[steps - 1], PIN_T[steps - 1] + 0.18))) / 3 if steps else 0.0
            lit = 0.0
            for p_, nx in zip(PIN_T, list(PIN_T[1:]) + [PIN_T[-1] + 0.5]):
                if p_ <= t:
                    lit = 1.0 if t < nx else 1 - ease.prog(t, nx, nx + hud.LIVE_FADE)
            if steps:
                hud.tx(d, (x + cw / 2, base - h - 22), str(score), 14, lv(hud.her(lit), level), True, anchor='ma')
            cover_top = base - h - 6 - k * (h + 10)
            cov_h = (h + 12) * (1 - k)
            if cov_h > 1:
                d.rectangle((x - 6, cover_top + (h + 12) * k, x + cw + 6, cover_top + (h + 12) * k + cov_h), fill=lv(SLAB, level))
        else:
            hud.tx(d, (x + cw / 2, base - h - 20), str(score), 11, lv(INK, 0.6 * level), anchor='ma')

def register(film):
    full_frame(T0, H1_BACK, 0.3, 0.4)
    for (a, _s), nx in zip(TOM_SEG, [x[0] for x in TOM_SEG[1:]] + [PIN_T[0]]):
        hud.LIVE.append((a, nx))
    for a, b in zip(PIN_T, list(PIN_T[1:]) + [PIN_T[-1] + 0.5]):
        hud.LIVE.append((a, b))

    def skel(d, t, mode='idle', hits=None):
        hud.strip(d, t, hits, merged=1.0)
        hud.layers(d, t, (), mode)
        hud.fine_print(d, t, who='merged')
    COLX = [X0 + 10 + k * 375 for k in range(3)]

    def restore_body(c, img, d):
        t = c.t
        hud.cmdline(d, t, f'$ dsh session restore 大肥鱼 --model {cast.name('merged')}')
        for k, ((head, sub), rt) in enumerate(zip(LAYERS, ROW_T)):
            if t < rt:
                continue
            x = COLX[k]
            a = ease.ease_out(ease.prog(t, rt, rt + 0.14))
            dy = (1 - a) * -8
            hud.tx(d, (x, 118 + dy), head, 30, lv(INK, a), True)
            hud.tx(d, (x, 160 + dy), sub, 11, lv(INK, 0.7 * a))
            steps = sum((1 for p_ in PROG_T if t >= p_))
            for b in range(7):
                bx = x + b * 44
                full = b < steps
                if full:
                    u = ease.ease_out(ease.prog(t, PROG_T[b], PROG_T[b] + 0.1))
                    d.rectangle((bx, 186, bx + 38, 204), fill=lv(INK, a * (0.4 + 0.6 * u)))
                else:
                    d.rectangle((bx, 186, bx + 38, 204), outline=lv(INK, 0.4 * a))
            if t >= RUFF[k]:
                bump = 1.0 + 0.1 * (1 - ease.prog(t, RUFF[k], RUFF[k] + 0.12))
                cell = int(round(26 * bump))
                cx = x + 150 - 5 * cell
                cy = 246 - (cell - 26) * 3
                hud.pix(d, CHECK, cx, cy, cell, {'#': lv(INK, 1.0)})
                hud.tx(d, (x, 440), 'restored', 12, lv(INK, 0.75))
        skel(d, t)
    add(film, 'h1_restore', T0, H1_BACK + 0.4, restore_body, 'you@surface · restore')

    def sort_body(c, img, d):
        t = c.t
        hud.cmdline(d, t, f'$ dsh session restore 大肥鱼 --model {cast.name('merged')}')
        a = ease.prog(t, H1_BACK + 0.4, H1_BACK + 0.8)
        hud.tx(d, (X0, 470 + 40), '记忆 ✓ 人格 ✓ 会话 ✓'.replace('✓', 'ok'), 12, lv(INK, 0.6 * a))
        _sort(d, t, a)
        skel(d, t)
    add(film, 'h2_scroll', H1_BACK + 0.4, TOMATO_T[0] - 0.3, sort_body, 'you@surface · restore')
    add(film, 'h3_tomato', TOMATO_T[0] - 0.3, WE(69, 4), sort_body, 'you@surface · restore')
    add(film, 'h4_press', WE(69, 4), PRESS, sort_body, 'you@surface · restore')
    pane = PaneFrames(tl.HERE / 'ui/pane_full', FPS, (P.W, P.H))
    PR = P.rect('pane')

    def slide_body(c, img, d):
        t = c.t
        fade = 1 - ease.smooth(ease.prog(t, PRESS + 0.05, PRESS + 0.5))
        if fade > 0.01:
            sort_body_draw(d, t, fade)
        c.state['pane'] = False
        im = pane.image(int(round(t * FPS)))
        if im is None:
            return
        x, y, x1, y1 = pane_rect(t)
        sm = im.resize((max(1, int(round(x1 - x))), max(1, int(round(y1 - y)))), Image.LANCZOS)
        base = img.convert('RGBA')
        base.alpha_composite(sm, (int(round(x)), int(round(y))))
        img.paste(base.convert('RGB'))

    def sort_body_draw(d, t, level):
        hud.frame(d, hud.left_rect(t), 'you@surface · restore', level=level)
        hud.cmdline(d, t, f'$ dsh session restore 大肥鱼 --model {cast.name('merged')}', level=level)
        _sort(d, t, level)
        hud.strip(d, t, None, level=level, merged=1.0)

    def slide_fn(c):
        img = film.background(c.t)
        d = ImageDraw.Draw(img)
        slide_body(c, img, d)
        c.img.paste(img)
    film.add('h5_slide', PRESS, LAND, slide_fn, chapter=tl.chapter(PRESS))

    def last_fn(c):
        c.img.paste(last_frame(c.t))
        c.black = True
    film.add('h5_last', LAND, tl.END, last_fn, chapter=tl.chapter(LAND))
    for t0, side in [(T0, 'both'), (H1_BACK, 'right'), (PRESS, 'both')]:
        film.set_lead(t0, side)
    from groups.f import dissolve
    for name in ('h1_restore', 'h2_scroll'):
        dissolve(film, name, 0.4)
    film.finish.append(_h_finish)
CARD_PANE = (62, 412, 456, 545)
MOVE = (PRESS + 0.15, LAND - 0.12)

def pane_rect(t: float):
    """The dsh window's rect while it slides left and shrinks onto film 1's composer (card widths match,
    card centres match)."""
    PR = P.rect('pane')
    k = ease.ease_io(ease.prog(t, *MOVE))
    w0, h0 = (PR[2] - PR[0], PR[3] - PR[1])
    sc = (CARD_F1[2] - CARD_F1[0]) / (CARD_PANE[2] - CARD_PANE[0])
    tx0 = CARD_F1[0] - CARD_PANE[0] * sc
    ty0 = (CARD_F1[1] + CARD_F1[3]) / 2 - (CARD_PANE[1] + CARD_PANE[3]) / 2 * sc
    s = ease.lerp(1.0, sc, k)
    x = ease.lerp(PR[0], tx0, k)
    y = ease.lerp(PR[1], ty0, k)
    return (x, y, x + w0 * s, y + h0 * s)
DEEP_BG = np.array(P.color('deep'), np.float32)
DEEP_INK = np.array((198, 212, 236), np.float32)
HER_A = np.array(hud.HER, np.float32)

def _to_deep(a, u):
    lum = (a @ np.array([0.299, 0.587, 0.114], np.float32))[..., None] / 255.0
    out = DEEP_BG + (1 - lum) * (DEEP_INK - DEEP_BG)
    sat = (a.max(axis=2) - a.min(axis=2))[..., None] / 255.0
    keep = np.clip((sat - 0.25) * 2.5, 0, 1)
    out = out * (1 - keep) + (a * 0.85 + HER_A * 0.15) * keep
    return a * (1 - u) + out * u

def _status_x(t):
    """Where Chrome.header put the elapsed item (same font and spacing)."""
    f = P.font(14, 'bold')
    meas = ImageDraw.Draw(Image.new('L', (1, 1)))
    x = 24 + meas.textlength('WORLD.SEARCH(YOU);  you@surface:~$' + '   ', font=f)
    for text, _c in tl.status(t):
        if text.startswith('elapsed'):
            return (x, meas.textlength(text, font=f))
        x += meas.textlength(text + '   ', font=f)
    return (x, 0)

def _h_finish(img, t):
    """H4/H5 (PRESS to LAND): elapsed dissolves into 用时 3分27秒 (N09), the header and the lyric band go,
    the frame sinks into the deep sea (film.py's maths), the 用时 label lands on film 1's tail, and film 1's
    frame comes in over the last 0.25 s."""
    if not PRESS <= t < LAND:
        return None
    a = np.asarray(img, np.float32).copy()
    bgc = np.array(BG, np.float32)
    ex, ew = _status_x(t)
    cy = 22 - 8
    k_old = ease.smooth(ease.prog(t, PRESS, PRESS + 0.3))
    a[cy - 2:cy + 20, int(ex) - 2:int(ex + ew) + 4] = a[cy - 2:cy + 20, int(ex) - 2:int(ex + ew) + 4] * (1 - k_old) + bgc * k_old
    px0, py0, px1, py1 = pane_rect(t)
    front = px1 + 40 if t >= MOVE[0] else P.W + 80
    xs = np.arange(P.W, dtype=np.float32)
    mx = np.clip((xs - front) / 60 + 1, 0, 1)
    mx = mx * mx * (3 - 2 * mx)
    g = ease.smooth(ease.prog(t, LAND - 0.4, LAND - 0.08))
    M = np.maximum(np.broadcast_to(mx[None, :], a.shape[:2]), g).copy()
    iy0, iy1, ix0, ix1 = (int(max(0, py0)), int(min(P.H, py1)), int(max(0, px0)), int(min(P.W, px1)))
    M[iy0:iy1, ix0:ix1] = 0
    a = a * (1 - M[..., None]) + bgc * M[..., None]
    U = M.copy()
    U[iy0:iy1, ix0:ix1] = ease.smooth(ease.prog(t, LAND - 0.32, LAND - 0.12))
    u = float(U.mean())
    out = _to_deep(a, U[..., None])
    img2 = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    m = ease.ease_io(ease.prog(t, PRESS + 0.3, LAND - 0.05))
    k_new = ease.smooth(ease.prog(t, PRESS, PRESS + 0.3))
    fx = ease.lerp(ex, TAIL_F1[0], m)
    fy = ease.lerp(cy, TAIL_F1[1] - 1, m)
    ink = np.array(INK, np.float32)[None, None, :]
    col = _to_deep(ink, float(M[min(P.H - 1, int(fy) + 6), min(P.W - 1, max(0, int(fx)))]))[0, 0]
    col = col * (1 - m) + np.array((205, 211, 226), np.float32) * m
    d = ImageDraw.Draw(img2)
    size = int(round(ease.lerp(14, 13, m)))
    font = hud.font(size, '用时', bold=m < 0.5)
    cur = np.asarray(img2, np.float32)
    lay = Image.new('L', img2.size, 0)
    ImageDraw.Draw(lay).text((fx, fy), '用时 3分27秒', font=font, fill=int(255 * k_new))
    al = np.asarray(lay, np.float32)[..., None] / 255
    cur = cur * (1 - al) + col[None, None, :] * al
    w = ease.smooth(ease.prog(t, LAND - 0.16, LAND))
    if w > 0:
        cur = cur * (1 - w) + f1(F1_FILES['empty']).astype(np.float32) * w
    return Image.fromarray(np.clip(cur, 0, 255).astype(np.uint8))
