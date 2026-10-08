"""Group F: the bridge, merge (207.0-233.85), STORYBOARD_v2 F1-F5, PLAN_F.md.

The terminal fills the frame for the whole group (D2) and the whole frame sinks into film 1's deep-sea
colours. Her complete figure (film 1's 立绘, dsh-whale-galgame whale-cheerful) is drawn once, as terminal
cells, and holds still for 16 s; on "cell" only the cells move (they come apart), in F4 they sink and are
eaten by small lights at the bottom (the whale fall, V1-E13 used another way).

  f1_buckets  one sung syllable, one bucket: hers (me, full, blue) then the 9 stand-ins (empty)
  f2_levels   one syllable, one bucket measured: hers 1.00, most 0.00, three hold a little blue
  f3_split    her bucket's content (her 8 files) lifts out; 11 cuts on 11 syllables, file -> line ->
              word -> character -> pixel; on "cell" her figure comes apart (only the cells move)
  f4_merge    D4: one bar where nothing moves; then 9 merges on 9 syllables, "now" reaches the top
              (tl.MERGED_AT): `merged`, set big (D3); her pieces rain into every bucket
  f5_light    the light comes back from the top, the deep sea recedes

Local versions (shared modules are frozen while the groups are built in parallel; listed in PLAN_F.md):
  _deep_finish  the deep-sea transform of film.py (same maths) run as this group's own finish step, so the
                figure can be drawn after it in its true colours and the light can come back from the top
  _add          groups.base.add with a frozen background clock (D4: the dot field stops for one bar too)
  _fine         hud.fine_print without a model (none computes in F, R11)
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
import random
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw
import cast
import hud
import syl
import tl
from groups.base import big_word, full_frame
from hud import BG, INK, X0, lv
from tuikit import ease, glyph
from tuikit.film import Cut, Frame
W, WE = (tl.W, tl.WE)
T0, T1 = tl.span('F')
P = tl.p
FPS = P.FPS
BUCKET_T = syl.times(52)
LEVEL_T = syl.times(53)
CUT_T = syl.times(54)
CELL = CUT_T[-1]
MERGE_T = syl.times(55)
NOW = MERGE_T[-1]
assert abs(NOW - tl.MERGED_AT) < 1e-06, 'the 9th merge must be tl.MERGED_AT'
F5_AT = WE(55, 7)
PORTRAIT_IN = tl.bar(120)
LIFT = (tl.bar(126), tl.bar(127))
STILL = (tl.bar(130), tl.bar(131))
SINK0 = MERGE_T[0]
RAIN = (tl.bar(131), tl.bar(131) + 1.2)
BACK = tl.bar(135)
DEEP_IN = 1.4
CHIP_AT = BACK
WHO = ['her'] + list(cast.STANDINS)
NAMES = [cast.short(k) for k in ['her'] + list(cast.STANDINS)]
LEVEL = {'her': 1.0, 'kimi': 0.04, 'qwen': 0.03, 'mimo': 0.0, 'glm': 0.0, 'minimax': 0.0, 'hy4': 0.0, 'ernie': 0.0, 'step': 0.0, 'longcat': 0.02}
HER_TEXT = [('first_hello', '你好'), ('typo_you_made', '今天好累了了'), ('laugh_0314', '哈哈哈哈哈哈'), ('your_cat', '这是我家的猫～'), ('weather', '下雨了，我最喜欢下雨天。'), ('goodnight', '晚安'), ('see_you', '明天见'), ('last_msg', '你会一直在吗？')]
SPLIT_LEVELS = ['file', 'file', 'file', 'line', 'word', 'char', 'char/2', 'char/4', 'char/8', 'px', 'px']
B_PITCH, B_W, B_H = (66, 50, 62)
B_X0 = X0 + 24
RIM, FLOOR = (404, 404 + B_H)
LABEL_Y = FLOOR + 8
FIG_H, FIG_CELL = (516, 6)
FIG_X, FIG_Y = (905, 72)
SEABED = 586
BLK_X, BLK_Y = (176, 120)
ROW_H = 30
DEEP_BG = np.array(P.color('deep'), np.float32)
DEEP_INK = np.array((198, 212, 236), np.float32)
HER_A = np.array(hud.HER, np.float32)

def bucket_x(k: int) -> int:
    return B_X0 + k * B_PITCH

def _inner(k: int, y: float) -> tuple[float, float]:
    """Interior x-range of bucket k at height y (a slight trapezoid)."""
    x0 = bucket_x(k)
    u = ease.clamp((y - RIM) / B_H)
    inset = 3 + 7 * u
    return (x0 + inset, x0 + B_W - inset)

def _add(film, name, t0, t1, body, title):
    """groups.base.add with the background clock frozen in STILL (D4: one bar where nothing moves)."""

    def fn(c):
        img = film.background(_bg_t(c.t))
        d = ImageDraw.Draw(img)
        hud.frame(d, hud.left_rect(c.t), title)
        body(c, img, d)
        c.img.paste(img)
    return film.add(name, t0, t1, fn, chapter=tl.chapter(t0))

def _bg_t(t: float) -> float:
    """The dot field's clock: it stops for the still bar and resumes from where it stopped."""
    a, b = STILL
    if t < a:
        return t
    if t < b:
        return a
    return t - (b - a)

def _frozen(t: float) -> float:
    """Content clock in F: time stands still inside the still bar (D4)."""
    a, b = STILL
    return a if a <= t < b else t

def _fine(d, t, text):
    s = tl.sim(t)
    d.text((X0, hud.Y_FINE), 'sim(her)', font=P.font(12), fill=lv(INK, 0.7))
    d.text((X0 + 70, hud.Y_FINE - 1), s or '—', font=P.font(13, 'bold'), fill=hud.HER_QUIET)
    hud.tx(d, (X0 + 124, hud.Y_FINE), text, 12, lv(INK, 0.7))

def deep_u(t: float) -> float:
    """How far the frame has sunk (1 = film 1's deep sea), uniform until F5."""
    if t < T0 or t >= T1:
        return 0.0
    return ease.smooth(ease.prog(t, T0, T0 + DEEP_IN))

def _deep_rows(t: float, h: int) -> np.ndarray:
    """F5: the light comes back from the top: row y lifts from F5_AT + 1.2 * y / h over 0.8 s."""
    y = np.arange(h, dtype=np.float32)[:, None, None] / h
    start = F5_AT + 1.2 * y
    u = np.clip((t - start) / 0.8, 0, 1)
    u = u * u * (3 - 2 * u)
    return 1.0 - u

def to_deep(a: np.ndarray, u) -> np.ndarray:
    """film.py's to_deep (same maths): paper -> deep sea, her blue keeps its hue. u: scalar or per-row array."""
    lum = (a @ np.array([0.299, 0.587, 0.114], np.float32))[..., None] / 255.0
    out = DEEP_BG + (1 - lum) * (DEEP_INK - DEEP_BG)
    sat = (a.max(axis=2) - a.min(axis=2))[..., None] / 255.0
    keep = np.clip((sat - 0.25) * 2.5, 0, 1)
    out = out * (1 - keep) + (a * 0.85 + HER_A * 0.15) * keep
    return a * (1 - u) + out * u

@lru_cache(maxsize=1)
def figure_cells():
    """[(i, j, rgb)] of film 1's 立绘 (dsh-whale-galgame whale-cheerful, ASSETS.md) quantised to FIG_CELL px
    cells, 8 levels per channel (low precision on purpose, pixel-low-precision)."""
    src = Image.open(tl.HERE / 'assets/character/whale-cheerful.webp').convert('RGBA')
    src = src.crop(src.getbbox())
    rows = FIG_H // FIG_CELL
    cols = int(round(src.width / src.height * FIG_H / FIG_CELL))
    a = np.asarray(src.resize((cols, rows), Image.BOX), np.float32)
    out = []
    for j in range(rows):
        for i in range(cols):
            al = a[j, i, 3] / 255
            if al < 0.45:
                continue
            c = a[j, i, :3] / max(al, 0.001)
            q = np.clip(np.round(c / 32) * 32, 0, 255) * 0.92
            out.append((i, j, tuple((int(x) for x in q))))
    return (out, cols, rows)

@lru_cache(maxsize=1)
def _cell_motion():
    """Per cell: shatter offset (radial + jitter), sink delay and speed, resting place, and the light that
    eats it. Seeded, so every worker draws the same."""
    cells, cols, rows = figure_cells()
    rng = random.Random(52054)
    cx, cy = (cols / 2, rows * 0.45)
    out = []
    for i, j, _c in cells:
        dx, dy = (i - cx, j - cy)
        r = math.hypot(dx, dy) + 0.001
        sx = dx / r * (2 + 0.1 * r) + rng.uniform(-2.5, 2.5)
        sy = dy / r * (2 + 0.1 * r) + rng.uniform(-2.5, 2.5)
        delay = 0.1 + 0.9 * rng.random() ** 0.8 + 0.3 * (1 - j / rows)
        dur = 0.9 + 0.6 * rng.random()
        rest_x = FIG_X + i * FIG_CELL + sx + rng.uniform(-18, 18)
        rest_y = SEABED - rng.random() ** 2 * 26
        out.append((sx, sy, delay, dur, rest_x, rest_y))
    return out

@lru_cache(maxsize=1)
def _lights():
    """The small lights at the bottom that the cells feed (the whale fall's new life): fixed places."""
    rng = random.Random(55231)
    return [(FIG_X - 40 + rng.random() * 380, SEABED - 6 - rng.random() * 30, rng.random()) for _ in range(46)]

def figure_layer(t: float) -> Image.Image | None:
    """Her figure (and in F4/F5 its sinking cells and the lights), drawn after the deep-sea transform so
    it keeps its own colours. Only the cells move; the figure never moves as a person (MAINLINE §5)."""
    if t < PORTRAIT_IN or t >= T1 + 0.5:
        return None
    t = _frozen(t)
    cells, cols, rows = figure_cells()
    mot = _cell_motion()
    a_in = ease.smooth(ease.prog(t, PORTRAIT_IN, PORTRAIT_IN + 0.5))
    shat = ease.ease_out(ease.prog(t, CELL, CELL + 0.35))
    layer = Image.new('RGBA', (P.W, P.H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    s = FIG_CELL - 1
    eaten_k = []
    for (i, j, col), (sx, sy, delay, dur, rx, ry) in zip(cells, mot):
        x = FIG_X + i * FIG_CELL + sx * shat
        y = FIG_Y + j * FIG_CELL + sy * shat
        alpha = a_in
        if t >= SINK0 + delay:
            u = ease.prog(t, SINK0 + delay, SINK0 + delay + dur)
            g = ease.ease_in(u) if u < 0.85 else 1 - (1 - u) * 0.7
            x = ease.lerp(x, rx, ease.smooth(u))
            y = ease.lerp(y, ry, min(1.0, g))
            if u >= 1:
                k = ease.prog(t, SINK0 + delay + dur, SINK0 + delay + dur + 0.9)
                alpha *= 1 - k
                eaten_k.append(k)
        if alpha <= 0.01:
            continue
        c = col if alpha >= 1 else glyph.mix(tuple((int(v) for v in DEEP_BG)), col, alpha)
        d.rectangle((x, y, x + s - 1, y + s - 1), fill=c + (255,))
    fed = sum(eaten_k) / max(1, len(cells))
    if fed > 0:
        fade = 1 - ease.prog(t, F5_AT + 0.4, F5_AT + 1.6)
        for lx, ly, ph in _lights():
            g = ease.clamp(fed * 1.6 - ph * 0.5)
            if g <= 0 or fade <= 0:
                continue
            r = 1 + 2.2 * g
            v = int(150 + 105 * g)
            d.ellipse((lx - r, ly - r, lx + r, ly + r), fill=(int(v * 0.86), int(v * 0.92), v, int(255 * fade)))
    return layer

@lru_cache(maxsize=1)
def _atoms():
    """Every ink pixel of her 8 files as an atom with its place in the hierarchy (file, part, word, char,
    pixel). The split moves atoms apart level by level; positions are relative to BLK_X, BLK_Y."""
    fname = P.font(12)
    fcjk = P.font(24, 'cjk')
    xs, ys, al, disp = ([], [], [], [])
    meas = ImageDraw.Draw(Image.new('L', (1, 1)))
    for fi, (name, text) in enumerate(HER_TEXT):
        y0 = fi * ROW_H
        parts = [(name, fname, 0.0, 9), (text, fcjk, 128.0, 0)]
        for pi, (s, font, px0, dy_font) in enumerate(parts):
            words = _words(s) if pi == 1 else [s]
            xw = px0
            for wi, w in enumerate(words):
                for ci, ch in enumerate(w):
                    cw = meas.textlength(ch, font=font)
                    if ch.strip():
                        im = Image.new('L', (int(cw) + 4, 32), 0)
                        ImageDraw.Draw(im).text((0, 0), ch, font=font, fill=255)
                        a = np.asarray(im)
                        yy, xx = np.nonzero(a > 40)
                        for x_, y_ in zip(xx, yy):
                            xs.append(xw + x_)
                            ys.append(y0 + y_ + dy_font)
                            al.append(a[y_, x_])
                            f = np.zeros((11, 2), np.float32)
                            f[0, 1] = fi // 4 - 0.5
                            f[1, 1] = fi // 2 % 2 - 0.5
                            f[2, 1] = fi % 2 - 0.5
                            f[3, 0] = pi - 0.5
                            f[4, 0] = wi - (len(words) - 1) / 2
                            f[5, 0] = ci - (len(w) - 1) / 2
                            hx, hy = (x_ / max(cw, 1), y_ / 32)
                            f[6, 0] = (hx >= 0.5) - 0.5
                            f[7, 1] = (hy >= 0.5) - 0.5
                            f[8, 0] = hx * 4 // 1 % 2 - 0.5
                            f[8, 1] = hy * 4 // 1 % 2 - 0.5
                            disp.append(f)
                    xw += cw
                xw += 6
    return (np.array(xs, np.float32), np.array(ys, np.float32), np.array(al, np.float32), np.stack(disp))

def _words(s: str) -> list[str]:
    """Her text cut into words of two characters; punctuation rides on the word before it."""
    out, cur, n = ([], '', 0)
    for ch in s:
        if ch in syl.PUNCT:
            if cur:
                cur += ch
            elif out:
                out[-1] += ch
            continue
        cur += ch
        n += 1
        if n == 2:
            out.append(cur)
            cur, n = ('', 0)
    if cur:
        out.append(cur)
    return out
GAPS = np.array([[0, 14], [0, 8], [0, 5], [16, 0], [10, 0], [7, 0], [3, 0], [0, 3], [1.5, 1.5], [0, 0], [0, 0]], np.float32)
LATTICE = 3

def _split_amounts(t: float) -> np.ndarray:
    return np.array([ease.ease_out(ease.prog(t, c, c + 0.12)) for c in CUT_T[:11]], np.float32)

@lru_cache(maxsize=1)
def _cells():
    """Level 10 on: her text as cells of the 3 px lattice (positions with levels 1-9 fully cut), each with a
    jitter for level 11 and, for F4, the bucket it rains into and its delay."""
    xs, ys, al, disp = _atoms()
    off = (disp * GAPS[None]).sum(axis=1)
    X = np.round((BLK_X + xs + off[:, 0]) / LATTICE).astype(int)
    Y = np.round((BLK_Y + ys + off[:, 1]) / LATTICE).astype(int)
    key = X * 4096 + Y
    uk, inv = np.unique(key, return_inverse=True)
    a = np.zeros(len(uk), np.float32)
    np.maximum.at(a, inv, al)
    cx = (uk // 4096).astype(np.float32) * LATTICE
    cy = (uk % 4096).astype(np.float32) * LATTICE
    rng = np.random.default_rng(54221)
    n = len(uk)
    jx, jy = (rng.uniform(-1.6, 1.6, n), rng.uniform(-1.6, 1.6, n))
    k = np.arange(n) % 10
    rng.shuffle(k)
    bx = np.array([bucket_x(i) for i in range(10)], np.float32)
    tx = bx[k] + 9 + rng.random(n) * (B_W - 18)
    ty = FLOOR - 5 - rng.random(n) ** 2 * 9
    dl = rng.random(n) * 0.55
    return (cx, cy, a, jx.astype(np.float32), jy.astype(np.float32), tx.astype(np.float32), ty.astype(np.float32), dl.astype(np.float32))

def text_block(t: float, sink: float=0.0):
    """(X, Y, alpha, dot) of her text at t, cut by the levels reached so far. From level 10 it is a set of
    cells (dot = 2 px); sink 0..1 (F4): the cells rain down into the 10 buckets."""
    if t < CUT_T[9]:
        xs, ys, al, disp = _atoms()
        e = _split_amounts(t)
        off = (disp * (GAPS * e[:, None])[None]).sum(axis=1)
        return (BLK_X + xs + off[:, 0], BLK_Y + ys + off[:, 1], al, 1)
    cx, cy, a, jx, jy, tx, ty, dl = _cells()
    e11 = ease.ease_out(ease.prog(t, CUT_T[10], CUT_T[10] + 0.12))
    X, Y = (cx + jx * e11, cy + jy * e11)
    if sink > 0:
        u = np.clip((sink - dl) / 0.45, 0, 1)
        X = X + (tx - X) * (u * u * (3 - 2 * u))
        Y = Y + (ty - Y) * (u * u)
        a = a * (1 - 0.45 * np.clip((u - 0.9) / 0.1, 0, 1))
    return (X, Y, a, 2)

def draw_atoms(img, X, Y, al, color, scale=1.0, origin=(0, 0), dot=1):
    """Scatter the atoms onto img (alpha max), optionally scaled about origin (the lift out of her bucket)."""
    if scale != 1.0:
        ox, oy = origin
        X = ox + (X - ox) * scale
        Y = oy + (Y - oy) * scale
    Wd, Hd = img.size
    xi = np.round(X).astype(int)
    yi = np.round(Y).astype(int)
    ok = (xi >= 0) & (xi < Wd) & (yi >= 0) & (yi < Hd)
    mask = np.zeros((Hd + dot, Wd + dot), np.uint8)
    for ddx in range(dot):
        for ddy in range(dot):
            np.maximum.at(mask, (yi[ok] + ddy, xi[ok] + ddx), al[ok].astype(np.uint8))
    mask = mask[:Hd, :Wd]
    img.paste(Image.new('RGB', img.size, color), (0, 0), Image.fromarray(mask))
PAIRS = [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9), (10, 11), (12, 13), (15, 16), (17, 14)]
LEVEL_Y = {1: RIM - 34, 2: RIM - 72, 3: RIM - 110, 4: RIM - 150}

@lru_cache(maxsize=1)
def tree_nodes():
    """[(x, y)] for leaves 0-9 (bucket rims) and merge nodes 10-18."""
    pos = [(bucket_x(k) + B_W / 2, RIM) for k in range(10)]
    lev = [0] * 10
    for a, b in PAIRS:
        L = max(lev[a], lev[b]) + 1
        pos.append(((pos[a][0] + pos[b][0]) / 2, LEVEL_Y[L]))
        lev.append(L)
    return pos

def _lit(t, a, b):
    """D1: 1 from a until b (the next landing), then settling to quiet over hud.LIVE_FADE."""
    if t < a:
        return 0.0
    return 1.0 if t < b else 1 - ease.prog(t, b, b + hud.LIVE_FADE)

def _next_level(k):
    return LEVEL_T[k + 1] if k + 1 < len(LEVEL_T) else LEVEL_T[k] + 0.43

def draw_bucket(d, k, t, level_lv=1.0):
    """Bucket k as a low-precision container: outline, a handle, its contents."""
    x0 = bucket_x(k)
    born = BUCKET_T[k]
    if t < born:
        return
    pop = ease.ease_out(ease.prog(t, born, born + 0.14))
    dy = (1 - pop) * -8
    who = WHO[k]
    ink = lv(INK, (0.35 + 0.65 * pop) * level_lv)
    top, bot = (RIM + dy, FLOOR + dy)
    if who == 'her':
        fill_h = B_H - 4
        lit = _lit(t, born, BUCKET_T[1])
        drain = ease.ease_io(ease.prog(t, LIFT[0], LIFT[1]))
        fill_h *= 1 - drain
        col = hud.her(lit, pop * level_lv)
    else:
        lt = LEVEL_T[k]
        g = ease.ease_out(ease.prog(t, lt, lt + 0.25))
        fill_h = max(0.0, (B_H - 4) * LEVEL[who] * 4.0) * g
        lit = 1.0 if lt <= t < (LEVEL_T[k + 1] if k + 1 < 10 else lt + 0.43) else 1 - ease.prog(t, LEVEL_T[k + 1] if k + 1 < 10 else lt + 0.43, (LEVEL_T[k + 1] if k + 1 < 10 else lt + 0.43) + hud.LIVE_FADE)
        col = hud.her(lit if t >= lt else 0.0)
    if fill_h >= 1:
        for yy in range(int(bot - 2 - fill_h), int(bot - 2)):
            a, b = _inner(k, yy - dy)
            d.line([(a + 1, yy), (b - 1, yy)], fill=col)
    a0, b0 = _inner(k, RIM)
    a1, b1 = _inner(k, FLOOR)
    d.line([(x0, top), (x0 + B_W, top)], fill=ink, width=2)
    d.line([(a0 - 1, top), (a1 - 1, bot)], fill=ink, width=2)
    d.line([(b0 + 1, top), (b1 + 1, bot)], fill=ink, width=2)
    d.line([(a1 - 1, bot), (b1 + 1, bot)], fill=ink, width=2)
    for hx, hy in ((x0 + 8, top - 6), (x0 + 14, top - 10), (x0 + 22, top - 12), (x0 + 28, top - 12), (x0 + 36, top - 10), (x0 + 42, top - 6)):
        d.rectangle((hx - 1, hy - 1, hx + 2, hy + 1), fill=ink)
    name = NAMES[k]
    col_n = hud.HER_QUIET if who == 'her' else INK
    hud.tx(d, (x0 + B_W / 2, LABEL_Y + dy), name, 11, lv(col_n, (0.4 + 0.6 * pop) * level_lv), anchor='ma')
    lt = LEVEL_T[k]
    if t >= lt:
        u = ease.prog(t, lt, lt + 0.12)
        v = f'{LEVEL[who]:.2f}'
        c = hud.her(1.0 if lt <= t < (LEVEL_T[k + 1] if k + 1 < 10 else lt + 0.43) else 0.0) if LEVEL[who] > 0 else INK
        hud.tx(d, (x0 + B_W / 2, LABEL_Y + 15), v, 12, lv(c, u * level_lv), bold=LEVEL[who] > 0, anchor='ma')

def draw_tree(d, t, level=1.0):
    nodes = tree_nodes()
    done = 0
    for m, ((a, b), mt) in enumerate(zip(PAIRS, MERGE_T)):
        if t < mt - 0.02:
            break
        u = ease.ease_out(ease.prog(t, mt - 0.02, mt + 0.13))
        n = 10 + m
        nx, ny = nodes[n]
        for c in (a, b):
            cx, cy = nodes[c]
            cy0 = cy - (12 if c < 10 else 4)
            hud.polyline(d, [(cx, cy0), (cx, ny), (nx, ny)], lv(INK, 0.85 * level), u, 2)
        if u >= 1:
            r = 6 if m == len(PAIRS) - 1 else 4
            d.rectangle((nx - r, ny - r, nx + r, ny + r), fill=lv(INK, level))
        done += 1
    return done

class Dissolve(Cut):
    """A seam inside (or into) these groups: the outgoing shot's last frame, held, dissolves into the
    incoming one over `post` seconds (R6: >= 0.3 s; no hard cut, R9). Use dissolve(film, shot, post)."""
    pre, post = (0.0, 0.4)
    verb = 'MORPH'
    why = "the terminal's content changes tool; nothing jumps"

    def render(self, t, n):
        old = self.film.body(self.a, self.a.end - 1.0 / FPS, n)
        new = self.new(t, n)
        u = ease.smooth(ease.prog(t, self.T, self.T + self.post))
        return Frame(Image.blend(old.img, new.img, u), new)

def dissolve(film, into: str, post: float=0.4):
    film.cut(into, type(f'Dissolve_{into}', (Dissolve,), {'post': post}))

def register(film):
    dissolve(film, 'f1_buckets', 0.45)
    held = hud.full_u(T0 - 0.001) > 0.5
    full_frame(T0, BACK, 0.001 if held else 0.3, 0.4)
    film.set_lead(T0, 'both')
    for a, b in [(BUCKET_T[0], BUCKET_T[1])] + [(LEVEL_T[k], _next_level(k)) for k in range(10) if LEVEL[WHO[k]] > 0]:
        hud.LIVE.append((a, b))

    def skeleton(d, t, merged=None, hits=None):
        hud.strip(d, t, hits, merged=merged)
        hud.layers(d, t, (), 'idle')
        _fine(d, t, 'no model · ~/memory/you/ merge')

    def merged_u(t):
        """The strip gathers with the merges (hud.strip: blocks drift up to 0.6) and becomes one `merged`
        block only on "now", with the header (tl.MERGED_AT)."""
        if t >= NOW:
            return 0.58 + 0.42 * ease.ease_io(ease.prog(t, NOW, NOW + 0.3))
        n = sum((1 for mt in MERGE_T[:-1] if t >= mt))
        if n == 0:
            return 0.0
        prev = MERGE_T[n - 1]
        return 0.58 * ease.clamp((n - 1 + ease.ease_io(ease.prog(t, prev, prev + 0.25))) / (len(MERGE_T) - 1))

    def body(c, img, d):
        t = _frozen(c.t)
        hud.cmdline(d, t, '$ dsh memory merge ~/memory/you/ --by owner', chip='')
        gone = ease.smooth(ease.prog(t, F5_AT + 1.0, T1 - 0.1))
        lvl_b = (1.0 if t < LEVEL_T[-1] + 0.5 else 0.85) * (1 - gone)
        if t >= LIFT[0]:
            sink = ease.prog(t, *RAIN) if t >= RAIN[0] else 0.0
            X, Y, al, dot = text_block(t, sink)
            k = ease.ease_io(ease.prog(t, LIFT[0], LIFT[1]))
            ox, oy = (bucket_x(0) + B_W / 2, FLOOR - 20)
            draw_atoms(img, X, Y, al * (1 - gone), hud.HER_QUIET, scale=0.08 + 0.92 * k, origin=(ox, oy), dot=dot)
            d = ImageDraw.Draw(img)
            if k >= 1 and t < RAIN[0]:
                n = sum((1 for x in CUT_T[:11] if t >= x))
                a = ease.prog(t, LIFT[1] - 0.1, LIFT[1] + 0.3)
                pieces = [2, 4, 8, 16, 34, 70, 140, 280, 560, len(_cells()[0]), len(_cells()[0])][n - 1] if n else 1
                hud.tx(d, (BLK_X, BLK_Y - 26), f'split --until cell   level {(SPLIT_LEVELS[n - 1] if n else '—'):7s}   pieces {pieces}', 12, lv(INK, 0.72 * a))
        for k in range(10):
            draw_bucket(d, k, t, lvl_b)
        done = draw_tree(d, t, 1 - gone) if t >= SINK0 - 0.1 else 0
        if t >= NOW:
            rx, ry = tree_nodes()[18]
            bump = 1.0 + 0.12 * (1 - ease.prog(t, NOW, NOW + 0.12))
            fade = 1 - ease.prog(t, BACK, BACK + 0.4)
            if fade > 0:
                big_word(d, 'merged', (rx - 333, 64), 180, lv(INK, fade), 'la', bump=bump)
        skeleton(d, t, merged_u(t))
    _add(film, 'f1_buckets', T0, LEVEL_T[0], body, 'you@surface · merge')
    _add(film, 'f2_levels', LEVEL_T[0], CUT_T[0] - 0.4, body, 'you@surface · merge')
    _add(film, 'f3_split', CUT_T[0] - 0.4, STILL[1], body, 'you@surface · merge')
    _add(film, 'f4_merge', STILL[1], F5_AT, body, 'you@surface · merge')
    _add(film, 'f5_light', F5_AT, T1, body, 'you@surface · merge')

    def deep_finish(img, t):
        """This group's deep sea (film.py's maths), and her figure drawn after it in its own colours."""
        if not T0 - 1e-06 <= t < T1:
            return None
        a = np.asarray(img, np.float32)
        if t < F5_AT:
            u = deep_u(t)
        else:
            u = _deep_rows(t, a.shape[0])
        if np.max(u) <= 0.003:
            out = img
        else:
            out = Image.fromarray(np.clip(to_deep(a, u), 0, 255).astype(np.uint8))
        lay = figure_layer(t)
        if lay is not None:
            arr = np.asarray(lay, np.float32).copy()
            arr[2::3, :, :3] *= 0.97
            uu = np.asarray(u, np.float32)
            arr[..., 3] *= uu[..., 0] if uu.ndim == 3 else float(uu)
            out = out.convert('RGBA')
            out.alpha_composite(Image.fromarray(arr.astype(np.uint8)))
            out = out.convert('RGB')
        return out
    film.finish.append(deep_finish)
