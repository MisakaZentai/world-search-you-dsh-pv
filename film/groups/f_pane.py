"""Group F, sixth sample r2 (sample_open_f/README.md §5, REVIEW_F_20261003.md §4, D32): the bridge, merge
(207.015-233.85). The one span of the film without panes: the water rises over the frame, the panes and the dsh window
sink with the surface, and in the deep there is only the buckets, her and one line of running code. When the light
comes back the panes are there again, in group G's layout.

One vertical axis (S2): the first half goes down (cut, break down to the cell, the still bar, her pieces rain into the
buckets, her figure sinks to the seabed), the second goes up (the buckets' contents rise as bubbles, the opening's
bubbles, and merge two by two along the tree; on "now" the last one pops into `merged`).

  S1  the measurement is sorted: the empties on the first half of line 53, the three with a little of her on
      "some of us", hers on the last two syllables (it brims, then 1.00)
  S3  the dive: a water line rises from the bottom (the opening receded from the top, A r3); E's last frame and
      its dsh window sink under it
  S4  the light comes back: the water line steps down on the fill's 8ths and the two kicks, all paper by T1
  S5  marine snow, one small step a beat (frozen in the still bar, D4)
  R1  her eight lines laid out as in the opening's sort (the line, its file name under it); one bubble out of her
      bucket per 8th pops into a line; the words are split by meaning only at the "word" cut (B6)
  R2  buckets 1.3x, the row on the middle line for lines 52-53, settling down before the eight lines rise
  T   明天见 is the one thing to follow (batch 2, ASTRA_20261003.md #5; TRACK below): its R1 bubble carries the
      words, it drops whole into her bucket while the rest rains, her bucket's bubble carries it up the tree, into
      `merged` on "now"

The surface and the deep are composed in the body (the water line splits the frame), so a dissolve that re-renders
this body (G's g1a) sees what the viewer saw; the finish only turns the rows under the line into film 1's deep sea
and draws her figure, the seabed lights and the line. r1 is in sample_open_f/src_r1/. Switch: DSH_F=pane (film.py).
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
import random
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw
import hud
import panes
import tl
from groups import b_open as BO
from groups import c_pane as CPN
from groups import f as GF
from groups.base import full_frame
from hud import BG, INK, lv
from panes import SUB, TXT
from tuikit import ease, glyph
T0, T1 = (GF.T0, GF.T1)
P = tl.p
FPS = P.FPS
W, H = (P.W, P.H)
mtx = BO.mtx
MEM, COL = (CPN.MEM, CPN.COL)
BUCKET_T, LEVEL_T, CUT_T, CELL = (GF.BUCKET_T, GF.LEVEL_T, GF.CUT_T, GF.CELL)
MERGE_T, NOW, F5_AT, STILL, BACK = (GF.MERGE_T, GF.NOW, GF.F5_AT, GF.STILL, GF.BACK)
PORTRAIT_IN = GF.PORTRAIT_IN
DIVE = (T0, T0 + 0.62)
SINK_OLD = 0.9
SLIDE = (217.62, 218.1)
_KB = tl.C.beat_of(tl.bar(126))
POP_T = [tl.B(_KB + 0.5 * (k + 1)) for k in range(8)]
BUB_UP = 0.42
RAIN = (STILL[1], STILL[1] + 0.8)
SINK0 = STILL[1]
LEAF_UP = 0.42
NODE_UP = 0.3
_E_SHOTS = sorted(P.path('ui/pane_open_e').glob('*.png')) if P.path('ui/pane_open_e').exists() else []
E_LAST_T = int(_E_SHOTS[-1].stem) / FPS if _E_SHOTS else T0 - 1.0 / FPS
MEASURE = [3, 4, 5, 6, 7, 8, 9, 2, 1, 0]
MEASURE_T = list(LEVEL_T[:5]) + [LEVEL_T[4] + tl.C.BEAT / 4] + list(LEVEL_T[5:8]) + [LEVEL_T[9]]
BRIM_T = LEVEL_T[8]
_K5 = math.ceil(tl.C.beat_of(F5_AT) * 2 - 1e-06) / 2
RET = [(tl.B(_K5 + 0.5 * i), y) for i, y in enumerate((46, 94, 144, 194, 244, 296, 348))] + [(tl.B(540), 470), (tl.B(541), 606), (T1 - 0.07, H + 6)]
STEP = 0.12
WHO, NAMES, LEVEL = (GF.WHO, GF.NAMES, GF.LEVEL)
B_W, B_H, B_PITCH = (66, 82, 80)
B_X0 = 110
RIM_HI, RIM_LO = (300, 500)
LEVEL_DY = {1: 56, 2: 113, 3: 170, 4: 226}
FIG_CELL, FIG_H = (6, 516)
FIG_X, FIG_Y = (935, 72)
SEABED = 590
BLK_X, BLK_Y, ROW_H, NAME_DY = (124, 152, 38, 24)
TRACE_Y = 88
MERGED_TOP, MERGED_H = (186, 176)
R0 = 15

def bx(k):
    return B_X0 + k * B_PITCH

def rim(t):
    return ease.lerp(RIM_HI, RIM_LO, ease.ease_io(ease.prog(t, *SLIDE)))

def inner(k, y, r):
    """Interior x-range of bucket k at height y (rim at r): a slight trapezoid."""
    u = ease.clamp((y - r) / B_H)
    inset = 4 + 9 * u
    return (bx(k) + inset, bx(k) + B_W - inset)

def _frozen(t):
    """Content clock: time stands still inside the still bar (D4)."""
    a, b = STILL
    return a if a <= t < b else t

def _bg_t(t):
    """The dot field's and the snow's clock: it stops for the still bar and resumes where it stopped."""
    a, b = STILL
    return t if t < a else a if t < b else t - (b - a)

def _lit(t, a, b):
    if t < a:
        return 0.0
    return 1.0 if t < b else 1 - ease.prog(t, b, b + hud.LIVE_FADE)

def water_y(t):
    """y of the water line: rows below it are the deep."""
    if t < T0:
        return H + 6
    if t < DIVE[1]:
        return ease.lerp(H + 6, -14, ease.ease_io(ease.prog(t, *DIVE)))
    y = -14.0
    for ts, y1 in RET:
        if t < ts:
            break
        y = ease.lerp(y, y1, ease.ease_out(ease.prog(t, ts, ts + STEP)))
    return y

def _ripples(t):
    """[(x, age)] rings on the line where it steps on a kick."""
    out = []
    for i, (ts, _y) in enumerate(RET[-3:-1]):
        for j, x in enumerate((300 + 410 * i, 760 - 300 * i)):
            age = t - ts - 0.04 * j
            if 0 <= age < 0.7:
                out.append((x, age))
    return out

@lru_cache(maxsize=1)
def _snow_seeds():
    rng = random.Random(20705)
    return [(rng.uniform(40, W - 40), rng.uniform(0, 560), rng.uniform(5, 11), rng.uniform(2, 6), rng.uniform(0, 6.28), 1 + (rng.random() < 0.3), rng.uniform(0.16, 0.36)) for _ in range(52)]

def _snow(d, t):
    """Specks sinking a small step on every beat (the bridge's soft pulse), swaying a little."""
    tb = _bg_t(t)
    a = ease.prog(t, DIVE[1] - 0.3, DIVE[1] + 0.8)
    if a <= 0:
        return
    kb = tl.C.beat_of(tb)
    k = math.floor(kb)
    steps = k + ease.ease_out(ease.clamp((kb - k) / 0.35))
    for x0, y0, v, amp, ph, s, l in _snow_seeds():
        y = 60 + (y0 + v * steps) % 545
        x = x0 + amp * math.sin(ph + tb * 0.55)
        d.rectangle((x, y, x + s, y + s), fill=lv(INK, l * a))
LEVELS_SORTED = [LEVEL[WHO[k]] for k in MEASURE]

def _fmt(v):
    return f'{v:.2f}'.rstrip('0').rstrip('.') if v else '0'

def _sorted_ret(t):
    n = sum((1 for x in MEASURE_T if t >= x))
    return ' · '.join((_fmt(v) for v in LEVELS_SORTED[:n])) if n else None

def _pieces(t):
    n = sum((1 for x in CUT_T[:11] if t >= x))
    if not n:
        return None
    return f'level {GF.SPLIT_LEVELS[n - 1]} · {[2, 4, 8, 16, 34, 70, 140, 280, 560, len(_cells()[0]), len(_cells()[0])][n - 1]} 块'
CODE = [(BUCKET_T[0], 'buckets = memory.group_by("owner")', lambda t: '10 个' if t >= BUCKET_T[-1] else None), (MEASURE_T[0], 'sorted(b.measure(她) for b in buckets)', _sorted_ret), (POP_T[0] - BUB_UP, 'split(她, until="cell")', _pieces), (RAIN[0], 'scatter(cells, buckets)', lambda t: '10 个桶' if t >= RAIN[1] else None), (MERGE_T[0] - LEAF_UP, 'merge(buckets)', lambda t: 'merged' if t >= NOW else None)]

def code(d, t):
    """`$ dsh memory merge` and the call it is in (two lines, as in a trace pane, at G's trace pane's place)."""
    hud.tx(d, (36, hud.Y_CMD), '$ dsh memory merge ~/memory/you/ --by owner', 13, lv(INK, 0.86))
    shown = [x for x in CODE if x[0] <= t]
    if not shown:
        return
    last = shown[-1][0]
    sc = ease.ease_out(ease.prog(t, last, last + 0.14))
    for pos, (at, s, ret) in enumerate(reversed(shown[-2:])):
        y = TRACE_Y + 30 - pos * 19 + (1 - sc) * 19
        a = (TXT if pos == 0 else SUB * (1 - 0.6 * (1 - sc))) * ease.prog(t, at, at + 0.1)
        n = int((t - at) * BO.CODE_CPS) + 1
        w = mtx(d, (COL + 10, y), s[:n], 14, lv(INK, 0.92 * a), bold=pos == 0)
        r = ret(t)
        if r:
            mtx(d, (COL + 10 + w + 12, y), '→ ' + r, 14, lv(INK, 0.72 * a), bold=True)

def _measured(k, t):
    """When bucket k's value is printed (S1), or None."""
    i = MEASURE.index(k)
    return MEASURE_T[i]

def draw_bucket(d, k, t, r, drained=0.0):
    """Bucket k with its rim at r. drained 0..1: its contents have gone up (its bubble left, S2)."""
    x0 = bx(k)
    born = BUCKET_T[k]
    if t < born:
        return
    pop = ease.ease_out(ease.prog(t, born, born + 0.14))
    dy = (1 - pop) * -10
    who = WHO[k]
    ink = lv(INK, 0.35 + 0.65 * pop)
    top, bot = (r + dy, r + B_H + dy)
    fill_h = 0.0
    if who == 'her':
        lit = max(_lit(t, born, BUCKET_T[1]), _lit(t, BRIM_T, LEVEL_T[9] + 0.43))
        brim = ease.ease_back(ease.prog(t, BRIM_T, BRIM_T + 0.22)) if t >= BRIM_T else 0.0
        fill_h = B_H - 10 + 7 * brim
        out = sum((1 for p in POP_T if t >= p - BUB_UP))
        if out:
            p = POP_T[out - 1] - BUB_UP
            fill_h *= 1 - (out - 1 + ease.ease_out(ease.prog(t, p, p + 0.15))) / 8
        col = hud.her(lit)
    else:
        mt = _measured(k, t)
        g = ease.ease_out(ease.prog(t, mt, mt + 0.25))
        fill_h = max(0.0, (B_H - 6) * LEVEL[who] * 4.0) * g
        i = MEASURE.index(k)
        nxt = MEASURE_T[i + 1] if i + 1 < len(MEASURE_T) else mt + 0.43
        col = hud.her(_lit(t, mt, nxt) if t >= mt else 0.0)
    fill_h *= 1 - drained
    if fill_h >= 1:
        for yy in range(int(bot - 3 - fill_h), int(bot - 3)):
            a, b = inner(k, yy - dy, r)
            d.line([(a + 1, yy), (b - 1, yy)], fill=col)
    a0, b0 = inner(k, r, r)
    a1, b1 = inner(k, r + B_H, r)
    d.line([(x0, top), (x0 + B_W, top)], fill=ink, width=2)
    d.line([(a0 - 1, top), (a1 - 1, bot)], fill=ink, width=2)
    d.line([(b0 + 1, top), (b1 + 1, bot)], fill=ink, width=2)
    d.line([(a1 - 1, bot), (b1 + 1, bot)], fill=ink, width=2)
    for hx, hy in ((10, -7), (18, -12), (28, -15), (38, -15), (48, -12), (56, -7)):
        d.rectangle((x0 + hx - 1, top + hy - 1, x0 + hx + 2, top + hy + 1), fill=ink)
    hud.tx(d, (x0 + B_W / 2, bot + 8), NAMES[k], 12, lv(hud.HER_QUIET if who == 'her' else INK, 0.4 + 0.6 * pop), anchor='ma')
    mt = _measured(k, t)
    vis = 1 - ease.prog(t, POP_T[0] - BUB_UP, POP_T[-1])
    if t >= mt and vis > 0:
        u = ease.prog(t, mt, mt + 0.12)
        v = f'{LEVEL[who]:.2f}'
        i = MEASURE.index(k)
        nxt = MEASURE_T[i + 1] if i + 1 < len(MEASURE_T) else mt + 0.43
        c = hud.her(_lit(t, mt, nxt)) if LEVEL[who] > 0 else INK
        hud.tx(d, (x0 + B_W / 2, bot + 24), v, 13, lv(c, u * vis), bold=LEVEL[who] > 0, anchor='ma')
HER_TEXT = GF.HER_TEXT
WORDS = {'first_hello': ['你好'], 'typo_you_made': ['今天', '好累', '了了'], 'laugh_0314': ['哈哈', '哈哈', '哈哈'], 'your_cat': ['这是', '我家的', '猫～'], 'weather': ['下雨了，', '我', '最喜欢', '下雨天。'], 'goodnight': ['晚安'], 'see_you': ['明天', '见'], 'last_msg': ['你会', '一直', '在吗？']}
GAPS = np.array([[0, 14], [0, 8], [0, 5], [0, 8], [10, 0], [7, 0], [3, 0], [0, 3], [1.5, 1.5], [0, 0], [0, 0]], np.float32)
LATTICE = 3

@lru_cache(maxsize=1)
def _atoms():
    """Every ink pixel of her eight lines (the line at 22 px, its file name under it at 11 px) with its place in
    the hierarchy: file halves (0-2), line / name (3), word (4), character (5), half, quarter (6-8). Positions are
    relative to the block's top-left; row = which line it belongs to."""
    fcjk, fname = (P.font(20, 'cjk'), P.font(11))
    xs, ys, al, disp, row = ([], [], [], [], [])
    meas = ImageDraw.Draw(Image.new('L', (1, 1)))
    for fi, (name, text) in enumerate(HER_TEXT):
        y0 = fi * ROW_H
        for pi, (words, font, dy) in enumerate([(WORDS[name], fcjk, 0), ([name], fname, NAME_DY)]):
            xw = 0.0
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
                            ys.append(y0 + y_ + dy)
                            al.append(a[y_, x_] * (1.0 if pi == 0 else 0.5))
                            f = np.zeros((11, 2), np.float32)
                            f[0, 1] = fi // 4 - 0.5
                            f[1, 1] = fi // 2 % 2 - 0.5
                            f[2, 1] = fi % 2 - 0.5
                            f[3, 1] = pi - 0.5
                            f[4, 0] = wi - (len(words) - 1) / 2
                            f[5, 0] = ci - (len(w) - 1) / 2
                            hx, hy = (x_ / max(cw, 1), y_ / 32)
                            f[6, 0] = (hx >= 0.5) - 0.5
                            f[7, 1] = (hy >= 0.5) - 0.5
                            f[8, 0] = hx * 4 // 1 % 2 - 0.5
                            f[8, 1] = hy * 4 // 1 % 2 - 0.5
                            disp.append(f)
                            row.append(fi)
                    xw += cw
    return (np.array(xs, np.float32), np.array(ys, np.float32), np.array(al, np.float32), np.stack(disp), np.array(row, np.int32))

@lru_cache(maxsize=1)
def _cells():
    """From level 9 on: the strokes as cells of the 3 px lattice, each with a jitter (level 10), the bucket it rains
    into, where it lands (relative to that bucket) and its delay."""
    xs, ys, al, disp, _row = _atoms()
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
    ox = 12 + rng.random(n) * (B_W - 24)
    oy = B_H - 7 - rng.random(n) ** 2 * 16
    dl = rng.random(n) * 0.35
    return (cx, cy, a, jx.astype(np.float32), jy.astype(np.float32), k, ox.astype(np.float32), oy.astype(np.float32), dl.astype(np.float32))

def text_block(t, sink=0.0):
    """(X, Y, alpha, dot, row-or-bucket) of her lines at t, cut by the levels reached so far. Before level 9: atoms
    (row = which line); from level 9: lattice cells (bucket = where they rain); sink 0..1 rains them in. 明天见's
    cells (TRACK) do not rain: they drop as one piece into her own bucket (_track_fall)."""
    if t < CUT_T[9]:
        xs, ys, al, disp, row = _atoms()
        e = np.array([ease.ease_out(ease.prog(t, c, c + 0.12)) for c in CUT_T[:11]], np.float32)
        off = (disp * (GAPS * e[:, None])[None]).sum(axis=1)
        return (BLK_X + xs + off[:, 0], BLK_Y + ys + off[:, 1], al, 1, row)
    cx, cy, a, jx, jy, k, ox, oy, dl = _cells()
    e11 = ease.ease_out(ease.prog(t, CUT_T[10], CUT_T[10] + 0.12))
    X, Y = (cx + jx * e11, cy + jy * e11)
    if sink > 0:
        X0, Y0, a0 = (X, Y, a)
        r = RIM_LO
        tx = np.array([bx(i) for i in range(10)], np.float32)[k] + ox
        ty = r + oy
        u = np.clip((sink - dl / 0.8) / 0.55, 0, 1)
        X = X + (tx - X) * (u * u * (3 - 2 * u))
        Y = Y + (ty - Y) * (u * u)
        a = a * (1 - 0.4 * np.clip((u - 0.9) / 0.1, 0, 1))
        X, Y, a, k = _track_fall(t, X0, Y0, a0, X, Y, a, k)
    return (X, Y, a, 2, k)
TRACK = 6
TRACK_TEXT = HER_TEXT[TRACK][1]
TRACK_LEAF = 0
WORD_LAND = tl.next_beat(RAIN[0])
WORD_W = 42
INTO = 0.18

@lru_cache(maxsize=1)
def _track_cells():
    """Which lattice cells (_cells order) are 明天见's line (not its file name)."""
    xs, ys, al, disp, row = _atoms()
    off = (disp * GAPS[None]).sum(axis=1)
    X = np.round((BLK_X + xs + off[:, 0]) / LATTICE).astype(int)
    Y = np.round((BLK_Y + ys + off[:, 1]) / LATTICE).astype(int)
    uk, inv = np.unique(X * 4096 + Y, return_inverse=True)
    mine = ((row == TRACK) & (disp[:, 3, 1] < 0)).astype(np.int32)
    m = np.zeros(len(uk), np.int32)
    np.maximum.at(m, inv, mine)
    return m.astype(bool)

def _track_fall(t, X0, Y0, a0, X, Y, a, k):
    """明天见's cells keep their shape and drop into her bucket (falling, narrowing to fit), landing on WORD_LAND."""
    tm = _track_cells()
    gx0, gx1, gy0, gy1 = (X0[tm].min(), X0[tm].max(), Y0[tm].min(), Y0[tm].max())
    gx, gy = ((gx0 + gx1) / 2, (gy0 + gy1) / 2)
    sc = min(1.0, WORD_W / max(1.0, gx1 - gx0))
    w = ease.prog(t, RAIN[0], WORD_LAND)
    s = ease.lerp(1.0, sc, ease.smooth(w))
    cx = ease.lerp(gx, bx(TRACK_LEAF) + B_W / 2, ease.smooth(w))
    cy = ease.lerp(gy, RIM_LO + B_H - 6 - (gy1 - gy0) * sc / 2, ease.ease_in(w))
    X, Y, a, k = (X.copy(), Y.copy(), a.copy(), k.copy())
    X[tm] = cx + (X0[tm] - gx) * s
    Y[tm] = cy + (Y0[tm] - gy) * s
    a[tm] = a0[tm]
    k[tm] = TRACK_LEAF
    return (X, Y, a, k)

def _word_lit(t):
    """D1: lit while it falls, quiet over LIVE_FADE once it has landed."""
    return 1.0 if t < WORD_LAND else 1 - ease.prog(t, WORD_LAND, WORD_LAND + hud.LIVE_FADE)

@lru_cache(maxsize=1)
def _track_path():
    """Her bucket and the nodes its bubble merges into, up to the root."""
    _made, into = _merge_of()
    path, n = ([TRACK_LEAF], TRACK_LEAF)
    while n in into:
        n = 10 + into[n]
        path.append(n)
    return tuple(path)

def _track_size(r):
    return int(ease.clamp((r - 2) / 1.55, 11, 28))

def _track_text(d, x, y, r, a=1.0):
    """The words inside the bubble that carries them (ink; the bubble's outline does the lighting)."""
    if a <= 0.01:
        return
    f = hud.font(_track_size(r), TRACK_TEXT, True)
    d.text((x, y), TRACK_TEXT, font=f, fill=lv(INK, a), anchor='mm')

def _track_into(d, t):
    """On "now" the root bubble pops and the words go into `merged`: they shrink into its middle, on top of it."""
    if not NOW <= t < NOW + INTO:
        return
    x, y, _l = tree_nodes()[18]
    u = ease.ease_in(ease.prog(t, NOW, NOW + INTO))
    size = int(_track_size(_radius(18)) * (1 - u))
    if size < 4:
        return
    f = hud.font(size, TRACK_TEXT, True)
    d.text((x, y), TRACK_TEXT, font=f, fill=lv(INK, 1 - 0.5 * u), anchor='mm', stroke_width=2, stroke_fill=BG)

def draw_atoms(img, X, Y, al, color, dot=1):
    Wd, Hd = img.size
    xi = np.round(X).astype(int)
    yi = np.round(Y).astype(int)
    ok = (xi >= 0) & (xi < Wd) & (yi >= 0) & (yi < Hd) & (al > 1)
    mask = np.zeros((Hd + dot, Wd + dot), np.uint8)
    for ddx in range(dot):
        for ddy in range(dot):
            np.maximum.at(mask, (yi[ok] + ddy, xi[ok] + ddx), np.clip(al[ok], 0, 255).astype(np.uint8))
    img.paste(Image.new('RGB', img.size, color), (0, 0), Image.fromarray(mask[:Hd, :Wd]))

def _lines(img, t):
    """R1: one bubble out of her bucket per 8th, popping into its line; then the cuts; then the rain."""
    if t < POP_T[0] - BUB_UP:
        return
    if t < CUT_T[9]:
        X, Y, al, dot, row = text_block(t)
        shown = np.array([ease.prog(t, p, p + 0.1) for p in POP_T], np.float32)[row]
        draw_atoms(img, X, Y, al * shown, lv(INK, 0.95), dot)
    else:
        sink = ease.prog(t, *RAIN) if t >= RAIN[0] else 0.0
        X, Y, al, dot, k = text_block(t, sink)
        if t >= MERGE_T[0] - LEAF_UP - 0.2:
            al = al * (1 - np.array([_drained(i, t) for i in range(10)], np.float32))[k]
        if t < RAIN[0]:
            draw_atoms(img, X, Y, al, lv(INK, 0.95), dot)
        else:
            tm = _track_cells()
            draw_atoms(img, X[~tm], Y[~tm], al[~tm], lv(INK, 0.95), dot)
            draw_atoms(img, X[tm], Y[tm], al[tm], hud.her(_word_lit(t)), dot)

def _bubble(d, cx, cy, rx, ry, u, level=1.0):
    """The opening's memory bubble (a_open._bubble): a light tint, her outline (lit while it moves, D1), a highlight."""
    col = hud.her(u, level)
    d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=lv(col, 0.2 + 0.18 * u), outline=col, width=3 if u > 0.5 else 2)
    d.arc((cx - rx * 0.62, cy - ry * 0.62, cx + rx * 0.2, cy + ry * 0.2), 195, 255, fill=BG, width=2)
    d.ellipse((cx + rx * 0.28 - 1.2, cy - ry * 0.5 - 1.2, cx + rx * 0.28 + 1.2, cy - ry * 0.5 + 1.2), fill=BG)

def _pop(d, x, y, r0, age, lit=1.0):
    """The opening's pop (a_open._dome): a ring that widens and eight droplets, lit while it bursts (D1)."""
    p = age / 0.5
    if not 0 <= p < 1:
        return
    col = hud.her(lit)
    rr = r0 * (1 + 1.3 * ease.ease_out(p))
    d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=lv(col, 1 - p), width=2)
    for j in range(8):
        ang = j * math.pi / 4 + 0.3
        dist = r0 + 26 * ease.ease_out(p)
        px, py = (x + math.cos(ang) * dist, y + math.sin(ang) * dist * 0.8 - 10 * p)
        s = 3.2 - 1.8 * p
        d.ellipse((px - s, py - s, px + s, py + s), fill=lv(col, 1 - p))

def _lift_bubbles(d, t):
    """R1: bubble k leaves her bucket BUB_UP before POP_T[k] and pops at the start of line k."""
    r = rim(t)
    sx = bx(0) + B_W / 2
    for k, p in enumerate(POP_T):
        t0 = p - BUB_UP
        if t < t0 or t >= p + 0.5:
            continue
        rb = _radius(TRACK_LEAF) if k == TRACK else 10
        ty = BLK_Y + k * ROW_H + 11
        tx = BLK_X - 16 - (rb - 10)
        if t < p:
            u = ease.ease_in(ease.prog(t, t0, p))
            y = ease.lerp(r + B_H - 20 if rb == 10 else r + B_H - 3 - rb, ty, u)
            x = ease.lerp(sx, tx, ease.smooth(ease.prog(t, t0 + 0.1, p))) + 3.5 * math.sin(2 * math.pi * 1.5 * u)
            s = math.sin(math.pi * u)
            _bubble(d, x, y, rb * (1 + 0.14 * s), rb * (1 - 0.14 * s), 1.0)
            if k == TRACK:
                _track_text(d, x, y, rb)
        else:
            _pop(d, tx, ty, rb, t - p)

@lru_cache(maxsize=1)
def tree_nodes():
    """[(x, y, level)] for the leaves 0-9 (bucket mouths at RIM_LO) and the merge nodes 10-18."""
    pos = [(bx(k) + B_W / 2, RIM_LO, 0) for k in range(10)]
    for a, b in GF.PAIRS:
        lev = max(pos[a][2], pos[b][2]) + 1
        pos.append(((pos[a][0] + pos[b][0]) / 2, RIM_LO - LEVEL_DY[lev], lev))
    return pos

@lru_cache(maxsize=1)
def _merge_of():
    """node -> (the merge index that makes it, the merge index it goes into)."""
    made, into = ({}, {})
    for m, (a, b) in enumerate(GF.PAIRS):
        made[10 + m] = m
        into[a] = into[b] = m
    return (made, into)

def _radius(node, track=True):
    """By area. Her bucket's bubble counts double: it holds its share and 明天见 (so the words fit inside).
    track=False: r2's radii (the tree's marks and the last pop keep r2's size, so nothing changes after "now")."""
    if node < 10:
        n = 2 if node == TRACK_LEAF and track else 1
    else:
        n = sum((_radius(c, track) ** 2 / R0 ** 2 for c in GF.PAIRS[node - 10]))
    return R0 * math.sqrt(n)

def _depart(node):
    """When node's bubble leaves for its parent."""
    _made, into = _merge_of()
    mt = MERGE_T[into[node]]
    return mt - (LEAF_UP if node < 10 else NODE_UP)

def _drained(k, t):
    """Bucket k's contents have gone up into its bubble (0..1)."""
    t0 = _depart(k)
    return ease.ease_out(ease.prog(t, t0, t0 + 0.12))

def _path(node, parent):
    """The elbow from node to parent along the tree: up, then across."""
    nodes = tree_nodes()
    x0, y0, _l = nodes[node]
    x1, y1, _l = nodes[parent]
    if node < 10:
        y0 = RIM_LO + B_H - 18
        if node == TRACK_LEAF:
            y0 = RIM_LO + B_H - 3 - _radius(node)
    return ((x0, y0), (x0, y1), (x1, y1))

def _along(pts, u):
    (x0, y0), (xm, ym), (x1, y1) = pts
    la, lb = (abs(ym - y0), abs(x1 - xm))
    s = u * (la + lb)
    if s <= la:
        return (x0, y0 + (ym - y0) * (s / max(la, 1e-06)), True)
    return (xm + (x1 - xm) * ((s - la) / max(lb, 1e-06)), ym, False)

def _merges(d, t):
    """The tree grows behind the bubbles; two bubbles meet at a node on its syllable and become one."""
    nodes = tree_nodes()
    _made, into = _merge_of()
    path = _track_path()
    words = []
    for node in range(19):
        x, y, _l = nodes[node]
        r = _radius(node)
        if node >= 10:
            m = node - 10
            mt = MERGE_T[m]
            if t < mt:
                continue
        if node < 18:
            parent = 10 + into[node]
            t0 = _depart(node)
            t1 = MERGE_T[into[node]]
            pts = _path(node, parent)
            if t >= t0:
                u_e = ease.ease_io(ease.prog(t, t0, t1))
                top = (pts[0][0], nodes[node][1] - (14 if node < 10 else _radius(node, False) * 0.4))
                hud.polyline(d, [top, pts[1], pts[2]], lv(INK, 0.55), u_e, 2)
            if node >= 10 and t >= MERGE_T[node - 10] + 0.02:
                d.rectangle((x - 3, y - 3, x + 3, y + 3), fill=lv(INK, 0.75))
            if t >= t1:
                continue
            if t >= t0:
                u = ease.ease_io(ease.prog(t, t0, t1))
                x, y, rising = _along(pts, u)
                if rising:
                    x += 3.5 * math.sin(2 * math.pi * 1.5 * u) * (1 - 0.5 * u)
                s = math.sin(math.pi * u)
                _bubble(d, x, y, r * (1 + 0.12 * s), r * (1 - 0.12 * s), 1.0)
                if node in path:
                    words.append((x, y, r, _drained(node, t) if node < 10 else 1.0))
                continue
            if node < 10:
                continue
        elif t >= MERGE_T[8] + 0.5:
            continue
        m = node - 10
        mt = MERGE_T[m]
        age = t - mt
        if node == 18:
            _pop(d, x, y, _radius(node, False), age, 1.0)
            continue
        swell = 1 + 0.2 * (1 - ease.ease_out(ease.prog(t, mt, mt + 0.18)))
        _bubble(d, x, y, r * swell, r * swell, _lit(t, mt - 0.05, mt + 0.15))
        if node in path:
            words.append((x, y, r, 1.0))
    for w in words:
        _track_text(d, *w)

def merged_word(d, t, fill=INK):
    if t < NOW:
        return
    bump = 1.0 + 0.12 * (1 - ease.prog(t, NOW, NOW + 0.12))
    rx = tree_nodes()[18][0]
    size = int(_merged_size() * bump)
    f = hud.font(size, 'merged', True)
    x0, y0, x1, y1 = f.getbbox('merged')
    cy = MERGED_TOP + MERGED_H / 2
    d.text((rx - (x0 + x1) / 2, cy - (y0 + y1) / 2), 'merged', font=f, fill=fill, stroke_width=5, stroke_fill=BG)

@lru_cache(maxsize=1)
def _merged_size():
    from groups.base import _size_for
    return _size_for('merged', MERGED_H, True)

def deep_scene(img, t):
    tt = _frozen(t)
    d = ImageDraw.Draw(img)
    _snow(d, t)
    code(d, tt)
    r = rim(tt)
    for k in range(10):
        draw_bucket(d, k, tt, r, _drained(k, tt))
    _lines(img, tt)
    d = ImageDraw.Draw(img)
    _lift_bubbles(d, tt)
    if tt >= MERGE_T[0] - LEAF_UP:
        _merges(d, tt)
    merged_word(d, tt)
    _track_into(d, tt)
_FILM = None

@lru_cache(maxsize=1)
def _surface_in():
    """E's last frame as the viewer saw it (its body and its dsh window), the surface the dive leaves."""
    prev = next((s for s in _FILM.shots if abs(s.end - T0) < 1e-06), None)
    n = int(round(E_LAST_T * FPS))
    if prev is None:
        return Image.new('RGB', (W, H), BG)
    c = _FILM.body(prev, E_LAST_T, n)
    img = c.img.convert('RGBA')
    layer = _FILM.character(E_LAST_T, n, c) if _FILM.character else None
    if layer is not None:
        img.alpha_composite(layer)
    return img.convert('RGB')

def surface_out(t):
    """The surface the light brings back: group G's panes at their first frame (g_pane.layout "turns"), drawn again,
    with `merged` where it stood in the deep and the call that made it."""
    img = _FILM.background(t)
    d = ImageDraw.Draw(img)
    hud.frame(d, hud.left_rect(t), 'you@surface · merge')
    r = CPN.right(t)
    rects = {'trace': (COL, 88, r, 140), 'compare': (COL, 148, r, 528), 'forward': (COL, 536, r, 598)}
    for name, rect in rects.items():
        d.rectangle(rect, fill=BG)
        panes.box(d, rect, name, t, 0.0, 1.0, {'compare': 'by owner'}.get(name, ''))
    code(d, t)
    merged_word(d, t)
    with CPN._strip_in(MEM):
        hud.strip(d, t, {}, merged=1.0)
    d.rectangle((MEM[0] + 4, MEM[1] + 8, MEM[2] - 4, MEM[1] + 21), fill=BG)
    panes.box(d, MEM, 'mem', t, 0.0)
    return img

def _split(img, top, yw):
    """Rows above the water line from `top`, the rest from img (in place)."""
    k = int(round(min(max(yw, 0), H)))
    if k > 0:
        img.paste(top.crop((0, 0, W, k)), (0, 0))

def _dive(img, t):
    """S3: above the line the surface is still there; under it the surface sinks and fades into the deep."""
    yw = water_y(t)
    old = _surface_in()
    k = ease.prog(t, T0, T0 + SINK_OLD)
    a = 1 - ease.smooth(ease.prog(t, T0 + 0.1, T0 + SINK_OLD))
    if a > 0.003:
        s = int(round(160 * ease.ease_in(k)))
        arr = np.asarray(img, np.float32)
        oa = np.asarray(old, np.float32)
        sh = np.zeros_like(oa)
        sh[s:] = oa[:H - s]
        y0 = int(max(0, min(H, round(yw))))
        lo = max(y0, s)
        if lo < H:
            arr[lo:] = arr[lo:] * (1 - a) + sh[lo:] * a
        img.paste(Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)))
    _split(img, old, yw)

def shot(c):
    t = c.t
    img = _FILM.background(_bg_t(t))
    deep_scene(img, t)
    if t < T0 + SINK_OLD:
        _dive(img, t)
    elif t >= RET[0][0] - 0.01:
        _split(img, surface_out(t), water_y(t))
    c.img.paste(img)

@lru_cache(maxsize=1)
def figure_cells():
    """[(i, j, rgb)] of film 1's 立绘 (whale-cheerful) as FIG_CELL px cells, 8 levels a channel (v2's figure)."""
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
    """Per cell: where "cell" throws it (out from her middle, gaps open), its sink delay and length, its resting
    place on the seabed. Seeded."""
    cells, cols, rows = figure_cells()
    rng = random.Random(52054)
    cx, cy = (cols / 2, rows * 0.45)
    out = []
    for i, j, _c in cells:
        dx, dy = ((i - cx) * FIG_CELL, (j - cy) * FIG_CELL)
        sx = dx * 0.11 + rng.uniform(-4, 4)
        sy = dy * 0.07 + rng.uniform(-4, 4)
        delay = 0.05 + 0.35 * rng.random() ** 0.8 + 0.2 * (1 - j / rows)
        dur = 0.55 + 0.3 * rng.random()
        rest_x = FIG_X + i * FIG_CELL + sx + rng.uniform(-22, 22)
        rest_y = SEABED - rng.random() ** 2 * 24
        out.append((sx, sy, delay, dur, rest_x, rest_y))
    return out

@lru_cache(maxsize=1)
def _lights():
    rng = random.Random(55231)
    return [(FIG_X - 30 + rng.random() * 330, SEABED - 6 - rng.random() * 30, rng.random()) for _ in range(46)]

def _fed(t):
    """How much of her the lights have eaten (0..1)."""
    k = 0.0
    for _sx, _sy, delay, dur, _rx, _ry in _cell_motion():
        k += ease.prog(t, SINK0 + delay + dur, SINK0 + delay + dur + 0.8)
    return k / max(1, len(_cell_motion()))

def figure_layer(t):
    """Her figure, still for 16 s; on "cell" it comes apart into cells with gaps between them; after the still bar
    the cells sink and the lights at the seabed eat them; while the buckets merge, small bubbles rise from the lights
    (new life goes up too). Drawn after the deep sea so it keeps its colours."""
    if t < PORTRAIT_IN:
        return None
    t = _frozen(t)
    cells, _cols, _rows = figure_cells()
    mot = _cell_motion()
    a_in = ease.smooth(ease.prog(t, PORTRAIT_IN, PORTRAIT_IN + 0.5))
    shat = ease.ease_out(ease.prog(t, CELL, CELL + 0.35))
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    deep = tuple((int(v) for v in GF.DEEP_BG))
    for (i, j, col), (sx, sy, delay, dur, rx, ry) in zip(cells, mot):
        x = FIG_X + i * FIG_CELL + sx * shat
        y = FIG_Y + j * FIG_CELL + sy * shat
        s = FIG_CELL - 1 - 2 * shat
        alpha = a_in
        if t >= SINK0 + delay:
            u = ease.prog(t, SINK0 + delay, SINK0 + delay + dur)
            g = ease.ease_in(u) if u < 0.85 else 1 - (1 - u) * 0.7
            x = ease.lerp(x, rx, ease.smooth(u))
            y = ease.lerp(y, ry, min(1.0, g))
            if u >= 1:
                alpha *= 1 - ease.prog(t, SINK0 + delay + dur, SINK0 + delay + dur + 0.8)
        if alpha <= 0.01:
            continue
        c = col if alpha >= 1 else glyph.mix(deep, col, alpha)
        d.rectangle((x, y, x + s - 1, y + s - 1), fill=c + (255,))
    fed = _fed(t)
    if fed > 0:
        for lx, ly, ph in _lights():
            g = ease.clamp(fed * 1.6 - ph * 0.5)
            if g <= 0:
                continue
            r = 1 + 2.2 * g
            v = int(150 + 105 * g)
            d.ellipse((lx - r, ly - r, lx + r, ly + r), fill=(int(v * 0.86), int(v * 0.92), v, 255))
        for x, y, r, a in _light_bubbles(t):
            d.ellipse((x - r, y - r, x + r, y + r), outline=(190, 205, 240, int(255 * a)), width=1)
    return layer

def _light_bubbles(t):
    """[(x, y, r, alpha)]: from the first merge to "now", one small bubble an 8th from a fed light, rising."""
    out = []
    lights = _lights()
    k0 = math.ceil(tl.C.beat_of(MERGE_T[0]) * 2 - 1e-06)
    k1 = math.floor(tl.C.beat_of(min(t, NOW)) * 2 + 1e-06)
    for k in range(k0, k1 + 1):
        tb = tl.B(k / 2)
        age = t - tb
        if age < 0 or age > 2.2:
            continue
        lx, ly, _ph = lights[k * 17 % len(lights)]
        y = ly - 8 - 75 * age
        x = lx + 3 * math.sin(age * 5 + k)
        out.append((x, y, 2.0 + k % 3 * 0.6, min(1.0, age * 4) * (1 - ease.prog(age, 1.4, 2.2))))
    return out

def deep_finish(img, t):
    if not T0 - 1e-06 <= t < T1:
        return None
    yw = water_y(t)
    if yw >= H:
        return None
    a = np.asarray(img, np.float32)
    y = np.arange(H, dtype=np.float32)[:, None, None]
    u = np.clip((y - yw) / 4 + 0.5, 0, 1)
    out = Image.fromarray(np.clip(GF.to_deep(a, u), 0, 255).astype(np.uint8))
    lay = figure_layer(t)
    if lay is not None:
        arr = np.asarray(lay, np.float32).copy()
        arr[2::3, :, :3] *= 0.97
        arr[..., 3] *= u[..., 0]
        out = out.convert('RGBA')
        out.alpha_composite(Image.fromarray(arr.astype(np.uint8)))
        out = out.convert('RGB')
    if -2 < yw < H:
        d = ImageDraw.Draw(out)
        pts = [(x, yw + 1.2 * math.sin(x / 23 + t * 2.6)) for x in range(0, W + 3, 3)]
        d.line(pts, fill=(132, 150, 186), width=1)
        for x, age in _ripples(t):
            p = age / 0.7
            for k in (0, 1):
                q = p - 0.25 * k
                if 0 < q < 1:
                    rx = 6 + 40 * q
                    d.ellipse((x - rx, yw - rx * 0.2, x + rx, yw + rx * 0.2), outline=lv((132, 150, 186), 1 - q))
    return out
SHOTS = [('f1_buckets', T0, LEVEL_T[0]), ('f2_levels', LEVEL_T[0], CUT_T[0] - 0.4), ('f3_split', CUT_T[0] - 0.4, STILL[1]), ('f4_merge', STILL[1], F5_AT), ('f5_light', F5_AT, T1)]

def register(film):
    global _FILM
    _FILM = film
    full_frame(T0, BACK, 0.001, 0.4)
    film.set_lead(T0, 'both')
    for name, a, b in SHOTS:
        film.add(name, a, b, shot, chapter=tl.chapter(a))
    orig = film.character

    def character(t, n, ctx):
        if T0 - 2.0 / FPS <= t < T0:
            return orig(E_LAST_T, n, ctx) if orig else None
        if T0 <= t < T1:
            return None
        return orig(t, n, ctx) if orig else None
    film.character = character
    hud.LIVE.append((BUCKET_T[0], BUCKET_T[1]))
    for i, k in enumerate(MEASURE):
        if LEVEL[WHO[k]] > 0 and k != 0:
            hud.LIVE.append((MEASURE_T[i], MEASURE_T[i + 1] if i + 1 < len(MEASURE_T) else MEASURE_T[i] + 0.43))
    hud.LIVE.append((BRIM_T, LEVEL_T[9] + 0.43))
    hud.LIVE.append((POP_T[0] - BUB_UP, POP_T[-1] + 0.1))
    hud.LIVE.append((RAIN[0], WORD_LAND))
    hud.LIVE.append((MERGE_T[0] - LEAF_UP, NOW + 0.3))
    film.finish.append(deep_finish)
