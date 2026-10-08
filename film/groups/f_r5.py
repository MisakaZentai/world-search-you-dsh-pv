"""Group F r5 (REVISE_R4_20261004.md §3.11, §4 lines 52-55, §5.1 the bucket names; D34): the bridge, merge
(207.015-233.85). She comes out of her own bucket and, cut down to the cell, goes back into the buckets.
Started from groups/f_pane.py (F r2, D32, kept unchanged); the deep with no panes, the water line, the snow, the
merge tree and the light coming back are r2's. Switch: DSH_F=r5 (film.py).

  52  [lyric reference] a bucket of love (207.51-210.34)
        one bucket a syllable, by writer: `me` full of her blue, the nine stand-ins empty (r2)
        bucket (209.68): she grows out of `me`, one band of rows a beat (14 beats to "emp-" 215.29): a band of blue
        cells comes up through the bucket's mouth, spreads to her width and takes her colours; the figure stands on
        the rim; her bucket's blue goes down a band each beat
  53  [lyric reference] of us filled up (213.85-217.24)
        sorted(b.level ...): one bucket measured a syllable, the empties first; `me` is the 4th 0, on "emp-", the
        beat it runs dry (only 明天见 is left on its floor: the line the opening pinned, the one to follow, T below);
        the stand-ins hold their own writes (ink, not her blue): five empty, five filling on "[lyric reference]"
  bar 126-127 (218.31-220.91)  split(她, until="cell"): the cut lines of the first seven levels drawn on her, one a beat
  54  [lyric reference] [lyric reference] (221.28-224.06)
        eleven cuts on eleven syllables (halves, quarters ... the gaps open where the lines were); "cell": every cell
        comes apart. The still bar (225.27-226.99) holds them in the water (D4, r2)
  bar 131 (226.99-228.28)  scatter(cells, buckets, key=color): bucket sort by colour. Bucket k's key (a swatch on
        its front) shows on its 16th, its cells are thrown in and land three 16ths later: the bluest back into `me`,
        then down the row; the last lands on "Merge". Not onto the seabed (the owner: "why scattered on the floor")
  55  [lyric reference] have evolved now (228.28-231.06)
        r2's tree, unchanged: a bucket's contents go up as a bubble, two meet on a syllable, `merged` on "now"
  F5  the light comes back (r2)

The bucket row is r2's (same size and pitch, the tree the same shape), moved right so that it is centred: her
figure stands on the first bucket. Times come from timing/ (syl, beatmap); nothing keeps its own beat list.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
import random
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw
import beatmap as BM
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
S16 = tl.C.BEAT / 4
BUCKET_T, LEVEL_T, CUT_T, CELL = (GF.BUCKET_T, GF.LEVEL_T, GF.CUT_T, GF.CELL)
MERGE_T, NOW, F5_AT, STILL, BACK = (GF.MERGE_T, GF.NOW, GF.F5_AT, GF.STILL, GF.BACK)
DIVE = (T0, T0 + 0.62)
SINK_OLD = 0.9
GROW_T = BM.events('beat', BUCKET_T[6] - 0.02, LEVEL_T[3] + 0.05)
assert len(GROW_T) == 14, GROW_T
GROW_EASE = 0.16
GUIDE_T = BM.events('beat', tl.bar(126) - 0.02, CUT_T[0] - 0.05)
assert len(GUIDE_T) == 7, GUIDE_T
RAIN0 = STILL[1]
KEY_T = [tl.grid(RAIN0, k, 4) for k in range(10)]
LAND_T = [tl.grid(RAIN0, k + 3, 4) for k in range(10)]
LEAF_UP = 0.42
NODE_UP = 0.3
assert LAND_T[1] < MERGE_T[0] - LEAF_UP, 'the first pair must be full before its bubbles leave'
_E_SHOTS = sorted(P.path('ui/pane_open_e').glob('*.png')) if P.path('ui/pane_open_e').exists() else []
E_LAST_T = int(_E_SHOTS[-1].stem) / FPS if _E_SHOTS else T0 - 1.0 / FPS
MEASURE = [3, 5, 7, 0, 8, 9, 4, 6, 2, 1]
MEASURE_T = list(LEVEL_T)
_K5 = math.ceil(tl.C.beat_of(F5_AT) * 2 - 1e-06) / 2
RET = [(tl.B(_K5 + 0.5 * i), y) for i, y in enumerate((46, 94, 144, 194, 244, 296, 348))] + [(tl.B(540), 470), (tl.B(541), 606), (T1 - 0.07, H + 6)]
STEP = 0.12
WHO, NAMES = (GF.WHO, GF.NAMES)
LEVEL = {'her': 0.0, 'kimi': 0.8, 'qwen': 0.6, 'mimo': 0.0, 'glm': 0.4, 'minimax': 0.0, 'hy4': 0.5, 'ernie': 0.0, 'step': 0.0, 'longcat': 0.2}
B_W, B_H, B_PITCH = (66, 82, 80)
B_X0 = (W - (9 * B_PITCH + B_W)) // 2
RIM = 500
LEVEL_DY = {1: 56, 2: 113, 3: 170, 4: 226}
FIG_CELL, FIG_ROWS = (4, 99)
REF_ROWS = 96
TRACE_Y = 88
CODE_X_DEEP = 440
MERGED_TOP, MERGED_H = (186, 176)
R0 = 15
NAME_PX = 16
PACK = 2
SWATCH = (18, 8)

def bx(k):
    return B_X0 + k * B_PITCH

def inner(k, y, r=RIM):
    """Interior x-range of bucket k at height y (rim at r): a slight trapezoid."""
    u = ease.clamp((y - r) / B_H)
    inset = 4 + 9 * u
    return (bx(k) + inset, bx(k) + B_W - inset)

def fill_px(level):
    return (B_H - 6) * level

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
        u = ease.prog(t, *DIVE)
        return ease.lerp(H + 6, -14, ease.ease_out(u))
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

@lru_cache(maxsize=1)
def figure_cells():
    """([(i, j, rgb)], cols, rows) of film 1's 立绘 (whale-cheerful) as cells, 8 levels a channel (r2's figure)."""
    return _cells_at(FIG_ROWS)

@lru_cache(maxsize=2)
def _cells_at(rows):
    src = Image.open(tl.HERE / 'assets/character/whale-cheerful.webp').convert('RGBA')
    src = src.crop(src.getbbox())
    cols = int(round(src.width / src.height * rows))
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
def fig_origin():
    """(x, y) of cell (0, 0): her feet (the mean column of her last rows) over the middle of `me`, on its rim."""
    cells, cols, rows = figure_cells()
    feet = [i for i, j, _c in cells if j >= rows - 4]
    fx = (sum(feet) / len(feet) + 0.5) * FIG_CELL
    return (bx(0) + B_W / 2 - fx, RIM - rows * FIG_CELL)

def emerged(t):
    """Rows of her out of the bucket (0..FIG_ROWS): a band a beat, eased (P1: a step, then a hold)."""
    return FIG_ROWS * BM.step(t, GROW_T, GROW_EASE) / len(GROW_T)

@lru_cache(maxsize=1)
def _row_born():
    """The beat on which row j came out of the bucket."""
    out = []
    n = len(GROW_T)
    for j in range(FIG_ROWS):
        k = next((k for k in range(1, n + 1) if FIG_ROWS * k / n > j + 0.25))
        out.append(GROW_T[k - 1])
    return out
GAPS = [10, 7, 7, 5, 5, 3, 3, 2, 2, 1.2, 1.2]

def _axis(L):
    """(axis, m): level L (1-based) cuts along x or y into 2**m slabs."""
    return ('x', (L + 1) // 2) if L % 2 else ('y', L // 2)

@lru_cache(maxsize=1)
def _cut_bits():
    """[n_cells, 11] signs (-0.5 / +0.5) of each cell at each level, and the piece count after each level."""
    cells, cols, rows = figure_cells()
    I = np.array([c[0] for c in cells])
    J = np.array([c[1] for c in cells])
    bits = np.zeros((len(cells), 11), np.float32)
    counts = []
    for L in range(1, 12):
        ax, m = _axis(L)
        if ax == 'x':
            bits[:, L - 1] = I * 2 ** m // cols % 2 - 0.5
        else:
            bits[:, L - 1] = J * 2 ** m // rows % 2 - 0.5
        mx, my = ((L + 1) // 2, L // 2)
        ids = I * 2 ** mx // cols * 4096 + J * 2 ** my // rows
        counts.append(len(np.unique(ids)))
    return (bits, counts)

def _cut_e(t):
    return np.array([ease.ease_out(ease.prog(t, c, c + 0.12)) for c in CUT_T[:11]], np.float32)

def _pieces(t):
    n = sum((1 for x in CUT_T[:11] if t >= x))
    if t >= CELL:
        return f'{len(figure_cells()[0])} 格'
    if not n:
        return None
    return f'{_cut_bits()[1][n - 1]} 块'

@lru_cache(maxsize=1)
def _sort():
    """Per cell: its bucket (key = how blue it is, ten equal shares, the bluest into `me`), its landing slot in
    that bucket and its throw (length, arc). Per bucket: the mean colour (its key swatch). Seeded."""
    cells, _cols, _rows = figure_cells()
    rgb = np.array([c[2] for c in cells], np.float32)
    key = rgb[:, 2] - 0.5 * (rgb[:, 0] + rgb[:, 1]) + 0.02 * rgb.sum(axis=1)
    order = np.argsort(-key, kind='stable')
    n = len(cells)
    k = np.zeros(n, np.int32)
    for rank, ci in enumerate(order):
        k[ci] = min(9, rank * 10 // n)
    swatch = [tuple((int(v) for v in rgb[k == b].mean(axis=0))) for b in range(10)]
    rng = np.random.default_rng(54221)
    dur = rng.uniform(0.24, 0.34, n).astype(np.float32)
    slot = np.zeros(n, np.int32)
    for b in range(10):
        idx = np.nonzero(k == b)[0]
        idx = idx[np.argsort(-dur[idx])]
        slot[idx] = np.arange(len(idx))
    return (k, slot, dur, swatch)

def _ref_count(b):
    """How many cells bucket b got in r5 round 1 (her figure at REF_ROWS): its pile keeps that many sites, so the
    buckets look the same from the merge on (228.28, owner-approved) with the bigger figure."""
    n = len(_cells_at(REF_ROWS)[0])
    return sum((1 for rank in range(n) if min(9, rank * 10 // n) == b))

@lru_cache(maxsize=10)
def _sites(b):
    """Lattice sites (PACK px) where bucket b's cells come to rest: among what is already in it (a stand-in's own
    writes: her cells sink into them), or a band on its floor (above 明天见 in hers). Seeded order."""
    n = _ref_count(b)
    floor = RIM + B_H - 4 - (WORD_H + 3 if b == TRACK_LEAF else 0)
    x0, x1 = inner(b, floor)
    ncol = int((x1 - x0 - 4) // PACK)
    need = -(-n // ncol)
    rows = max(need, int(fill_px(LEVEL[WHO[b]]) // PACK) - 1)
    sites = []
    for r in range(rows):
        y = floor - (r + 1) * PACK
        a0, a1 = inner(b, y)
        nc = int((a1 - a0 - 4) // PACK)
        for c in range(nc):
            sites.append((a0 + 2 + (a1 - a0 - 4 - nc * PACK) / 2 + c * PACK, y))
    order = np.random.default_rng(1000 + b).permutation(len(sites))
    if rows == need:
        order = np.arange(len(sites))
    return [sites[i] for i in order[:n]]

@lru_cache(maxsize=10)
def _count(b):
    return int((_sort()[0] == b).sum())

def _slot_xy(b, s):
    """Where the s-th cell of bucket b rests: r5-1's sites, shared in order when there are more cells (_ref_count)."""
    sites = _sites(b)
    return sites[min(len(sites) - 1, s * len(sites) // max(1, _count(b)))]

def _fmt(v):
    return f'{v:.2f}'.rstrip('0').rstrip('.') if v else '0'

def _sorted_ret(t):
    n = sum((1 for x in MEASURE_T if t >= x))
    vals = [LEVEL[WHO[k]] for k in MEASURE]
    return ' · '.join((_fmt(v) for v in vals[:n])) if n else None

def _pour_ret(t):
    if t < GROW_T[0]:
        return None
    n = int(round(emerged(t)))
    return f'{n}/{FIG_ROWS} 行'
CODE = [(BUCKET_T[0], 'buckets = memory.group_by("owner")', lambda t: '10 个' if t >= BUCKET_T[-1] else None), (GROW_T[0], '她 = buckets["me"].pour()', _pour_ret), (MEASURE_T[0], 'sorted(b.level for b in buckets)', _sorted_ret), (GUIDE_T[0], 'split(她, until="cell")', _pieces), (RAIN0, 'scatter(cells, buckets, key=color)', lambda t: '10 个桶' if t >= LAND_T[-1] else None), (MERGE_T[0] - LEAF_UP, 'merge(buckets)', lambda t: 'merged' if t >= NOW else None)]

def code_x(t):
    """The code's x: beside her while she is up there; G's trace pane's from the merge (it is there when the light
    comes back)."""
    t0 = MERGE_T[0] - LEAF_UP
    return ease.lerp(CODE_X_DEEP, COL + 10, ease.ease_io(ease.prog(t, t0, t0 + 0.18)))
CODE_RX, CODE_RY = (468, 236)
CODE_RPX, CODE_RLINE, CODE_RENTRY = (22, 30, 76)
CODE_BACK = (BM.events('beat', STILL[0] - 0.6, STILL[0] - 0.01)[-1], STILL[0])

def _code_right(d, t, alpha):
    shown = [x for x in CODE if x[0] <= t]
    if not shown or alpha <= 0.003:
        return
    last = shown[-1][0]
    sc = ease.ease_out(ease.prog(t, last, last + 0.14))
    for pos, (at, s, ret) in enumerate(reversed(shown[-3:])):
        y = CODE_RY + CODE_RENTRY * (1 - pos + (1 - sc))
        if pos == 2:
            a = SUB * 0.4 * (1 - sc)
            if a <= 0.01:
                continue
        else:
            a = (TXT if pos == 0 else SUB * (1 - 0.6 * (1 - sc))) * ease.prog(t, at, at + 0.1)
        a *= alpha
        n = int((t - at) * BO.CODE_CPS) + 1
        mtx(d, (CODE_RX, y), s[:n], CODE_RPX, lv(INK, 0.92 * a), bold=pos == 0)
        r = ret(t) if n >= len(s) else None
        if r:
            mtx(d, (CODE_RX + 24, y + CODE_RLINE), '→ ' + r, CODE_RPX, lv(INK, 0.72 * a), bold=True)

def code(d, t):
    """`$ dsh memory merge` and the call it is in: beside her in the first half (_code_right), then two lines as in
    a trace pane, at G's trace pane's place (r5-1)."""
    hud.tx(d, (36, hud.Y_CMD), '$ dsh memory merge ~/memory/you/ --by owner', 13, lv(INK, 0.86))
    back = ease.ease_io(ease.prog(t, *CODE_BACK))
    if back < 1:
        _code_right(d, t, 1 - back)
    if back <= 0:
        return
    cx = code_x(t)
    shown = [x for x in CODE if x[0] <= t]
    if not shown:
        return
    last = shown[-1][0]
    sc = ease.ease_out(ease.prog(t, last, last + 0.14))
    for pos, (at, s, ret) in enumerate(reversed(shown[-2:])):
        y = TRACE_Y + 30 - pos * 19 + (1 - sc) * 19
        a = (TXT if pos == 0 else SUB * (1 - 0.6 * (1 - sc))) * ease.prog(t, at, at + 0.1) * back
        n = int((t - at) * BO.CODE_CPS) + 1
        w = mtx(d, (cx, y), s[:n], 14, lv(INK, 0.92 * a), bold=pos == 0)
        r = ret(t) if n >= len(s) else None
        if r:
            mtx(d, (cx + w + 12, y), '→ ' + r, 14, lv(INK, 0.72 * a), bold=True)

def _measured(k):
    i = MEASURE.index(k)
    return (MEASURE_T[i], MEASURE_T[i + 1] if i + 1 < len(MEASURE_T) else MEASURE_T[i] + 0.43)

def draw_bucket(d, k, t, drained=0.0):
    """Bucket k (paper layer: its walls, its name, its ink contents, its reading). drained 0..1: its contents
    have gone up (its bubble left, S2). Her bucket's blue goes down a band a beat while she comes out of it."""
    x0 = bx(k)
    born = BUCKET_T[k]
    if t < born:
        return
    pop = ease.ease_out(ease.prog(t, born, born + 0.14))
    dy = (1 - pop) * -10
    who = WHO[k]
    mt, nxt = _measured(k)
    flash = _lit(t, mt, nxt) * (LEVEL[who] == 0)
    ink = lv(INK, 0.35 + 0.65 * pop)
    top, bot = (RIM + dy, RIM + B_H + dy)
    if who == 'her':
        _track_word(d, bx(0) + B_W / 2, bot - 4 - WORD_H / 2, 1 - drained)
        left = 1 - emerged(t) / FIG_ROWS
        fill_h = (B_H - 6) * left
        col = hud.her(_lit(t, born, GROW_T[-1] + GROW_EASE) * (0.7 + 0.3 * BM.flash(t, GROW_T, 0.14)))
    else:
        g = ease.ease_out(ease.prog(t, mt, mt + 0.25))
        fill_h = fill_px(LEVEL[who]) * g
        col = lv(INK, 0.3 + 0.25 * _lit(t, mt, nxt))
    fill_h *= 1 - drained
    if fill_h >= 1:
        for yy in range(int(bot - 3 - fill_h), int(bot - 3)):
            a, b = inner(k, yy - dy)
            d.line([(a + 1, yy), (b - 1, yy)], fill=col)
    if flash > 0:
        ink = glyph.mix(ink, lv(INK, 1.0), flash)
    a0, b0 = inner(k, RIM)
    a1, b1 = inner(k, RIM + B_H)
    w = 3 if flash > 0.5 else 2
    d.line([(x0, top), (x0 + B_W, top)], fill=ink, width=w)
    d.line([(a0 - 1, top), (a1 - 1, bot)], fill=ink, width=w)
    d.line([(b0 + 1, top), (b1 + 1, bot)], fill=ink, width=w)
    d.line([(a1 - 1, bot), (b1 + 1, bot)], fill=ink, width=w)
    for hx, hy in ((10, -7), (18, -12), (28, -15), (38, -15), (48, -12), (56, -7)):
        d.rectangle((x0 + hx - 1, top + hy - 1, x0 + hx + 2, top + hy + 1), fill=ink)
    hud.tx(d, (x0 + B_W / 2, bot + 5), NAMES[k], NAME_PX, lv(hud.HER_QUIET if who == 'her' else INK, 0.55 + 0.45 * pop), bold=who == 'her', anchor='ma')
    vis = 1 - ease.prog(t, CUT_T[0], CUT_T[0] + 0.3)
    if t >= mt and vis > 0:
        u = ease.prog(t, mt, mt + 0.12)
        bump = 1 + 0.25 * (1 - ease.ease_out(ease.prog(t, mt, mt + 0.14)))
        v = _fmt(LEVEL[who]) if LEVEL[who] else '0'
        c = hud.her(_lit(t, mt, nxt)) if who == 'her' else INK
        hud.tx(d, (x0 + B_W / 2, top + 7), v, int(14 * bump), lv(c, u * vis), bold=True, anchor='ma')
TRACK = 6
TRACK_TEXT = GF.HER_TEXT[TRACK][1]
TRACK_LEAF = 0
WORD_W, WORD_H = (30, 13)
INTO = 0.18

def _track_word(d, x, y, a=1.0):
    if a <= 0.01:
        return
    f = hud.font(_word_size(), TRACK_TEXT, True)
    d.text((x, y), TRACK_TEXT, font=f, fill=lv(INK, 0.9 * a), anchor='mm')

@lru_cache(maxsize=1)
def _word_size():
    for s in range(20, 8, -1):
        f = hud.font(s, TRACK_TEXT, True)
        x0, _y0, x1, _y1 = f.getbbox(TRACK_TEXT)
        if x1 - x0 <= WORD_W:
            return s
    return 9

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

@lru_cache(maxsize=1)
def tree_nodes():
    """[(x, y, level)] for the leaves 0-9 (bucket mouths at RIM) and the merge nodes 10-18."""
    pos = [(bx(k) + B_W / 2, RIM, 0) for k in range(10)]
    for a, b in GF.PAIRS:
        lev = max(pos[a][2], pos[b][2]) + 1
        pos.append(((pos[a][0] + pos[b][0]) / 2, RIM - LEVEL_DY[lev], lev))
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
        y0 = RIM + B_H - 18
        if node == TRACK_LEAF:
            y0 = RIM + B_H - 3 - _radius(node)
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
    for k in range(10):
        draw_bucket(d, k, tt, _drained(k, tt))
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
GUIDE_C = (198, 212, 236)
_DEEP = tuple((int(v) for v in GF.DEEP_BG))

def _guides(d, t, ox, oy, cols, rows):
    """Bar 126-127: split's plan, the cut lines of levels 1-7 drawn on her one a beat; each goes as its cut opens."""
    for L in range(1, 8):
        at = GUIDE_T[L - 1]
        if t < at or t >= CUT_T[L - 1] + 0.12:
            continue
        a = 0.55 * ease.ease_out(ease.prog(t, at, at + 0.12)) * (1 - ease.prog(t, CUT_T[L - 1], CUT_T[L - 1] + 0.12))
        a += 0.35 * (1 - ease.prog(t, at, at + 0.25))
        col = tuple((int(v) for v in glyph.mix(_DEEP, GUIDE_C, min(1.0, a)))) + (255,)
        ax, m = _axis(L)
        n = 2 ** m
        for q in range(1, n, 2):
            if ax == 'x':
                x = ox + q * cols / n * FIG_CELL - 0.5
                for y in range(int(oy) - 6, int(oy + rows * FIG_CELL) + 6, 6):
                    d.line([(x, y), (x, y + 3)], fill=col)
            else:
                y = oy + q * rows / n * FIG_CELL - 0.5
                for x in range(int(ox) - 6, int(ox + cols * FIG_CELL) + 6, 6):
                    d.line([(x, y), (x + 3, y)], fill=col)

def figure_layer(t):
    """Her figure and its cells, drawn after the deep sea so it keeps film 1's colours: out of her bucket a band a
    beat; the cut lines; the cuts; the cells apart; the sort into the buckets by colour; the cells in the buckets
    until their bubbles leave."""
    if t < GROW_T[0]:
        return None
    t = _frozen(t)
    cells, cols, rows = figure_cells()
    ox, oy = fig_origin()
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    E = emerged(t)
    born = _row_born()
    cxb = bx(0) + B_W / 2
    k_of, slot, dur, swatch = _sort()
    bits, _counts = _cut_bits()
    e = _cut_e(t)
    off = bits * (np.array(GAPS, np.float32) * e)[None]
    xs_l = [L - 1 for L in range(1, 12) if _axis(L)[0] == 'x']
    ys_l = [L - 1 for L in range(1, 12) if _axis(L)[0] == 'y']
    offx = off[:, xs_l].sum(axis=1)
    offy = off[:, ys_l].sum(axis=1) - sum((GAPS[i] * e[i] for i in ys_l)) / 4
    shat = ease.ease_out(ease.prog(t, CELL, CELL + 0.35))
    rng = random.Random(52054)
    drain = [_drained(b, t) for b in range(10)]
    for n_, (i, j, col) in enumerate(cells):
        jx, jy = (rng.uniform(-2, 2), rng.uniform(-2, 2))
        if E < FIG_ROWS - 0.001:
            if j >= E - 0.25:
                continue
            x = ox + i * FIG_CELL
            y = RIM - (E - j) * FIG_CELL
            age = t - born[j]
            u = ease.ease_out(ease.clamp(age / 0.22))
            x = cxb + (x + FIG_CELL / 2 - cxb) * (0.2 + 0.8 * u) - FIG_CELL / 2
            c = glyph.mix(hud.HER_LIVE, col, ease.clamp(age / 0.4))
            d.rectangle((x, y, x + FIG_CELL - 2, y + FIG_CELL - 2), fill=c + (255,))
            continue
        x = ox + i * FIG_CELL + offx[n_]
        y = oy + j * FIG_CELL + offy[n_]
        if shat > 0:
            x += ((i - cols / 2) * FIG_CELL * 0.07 + jx) * shat
            y += ((j - rows * 0.45) * FIG_CELL * 0.03 + jy) * shat
        s = FIG_CELL - 1 - shat
        b = int(k_of[n_])
        if t >= RAIN0:
            land = LAND_T[b]
            t0 = land - float(dur[n_])
            if t >= t0:
                u = ease.clamp((t - t0) / float(dur[n_]))
                tx, ty = _slot_xy(b, int(slot[n_]))
                arc = min(26 + 0.12 * abs(tx - x), max(0.0, y - 64))
                x = ease.lerp(x, tx, ease.smooth(u))
                y = ease.lerp(y, ty, u * u) - arc * 4 * u * (1 - u)
                s = ease.lerp(s, PACK, u)
                if u >= 1:
                    a = 1 - drain[b]
                    if a <= 0.01:
                        continue
                    c = glyph.mix(_DEEP, col, a)
                    d.rectangle((tx, ty, tx + PACK - 1, ty + PACK - 1), fill=c + (255,))
                    continue
        d.rectangle((x, y, x + s - 1, y + s - 1), fill=col + (255,))
    if E >= FIG_ROWS - 0.001:
        _guides(d, t, ox, oy, cols, rows)
    for b in range(10):
        if t < KEY_T[b]:
            continue
        a = ease.ease_out(ease.prog(t, KEY_T[b], KEY_T[b] + 0.1)) * (1 - drain[b])
        if a <= 0.01:
            continue
        bump = 1 + 0.4 * (1 - ease.ease_out(ease.prog(t, KEY_T[b], KEY_T[b] + 0.14)))
        w, h = (SWATCH[0] * bump, SWATCH[1] * bump)
        cx, cy = (bx(b) + B_W / 2, RIM + 12)
        c = glyph.mix(_DEEP, swatch[b], a)
        d.rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), fill=c + (255,), outline=tuple((int(v) for v in glyph.mix(_DEEP, GUIDE_C, 0.6 * a))) + (255,))
    return layer

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
    hud.LIVE.append((GROW_T[0], GROW_T[-1] + 0.4))
    i = MEASURE.index(0)
    hud.LIVE.append((MEASURE_T[i], MEASURE_T[i + 1]))
    hud.LIVE.append((MERGE_T[0] - LEAF_UP, NOW + 0.3))
    film.finish.append(deep_finish)
