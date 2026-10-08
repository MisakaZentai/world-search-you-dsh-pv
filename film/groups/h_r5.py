"""Group H r5 (REVISE_R4_20261004.md §3.16, §3.17, §4 lines 66-69, D9; D34): the puppy and the tomato, laid on
group H direction A (groups/h_a.py, kept unchanged; D33). Started from a copy of h_a.py; what r5 adds:

  dog 277.47      the persona pane holds her avatar (her face, pixels); on "dog" it becomes a pixel puppy, the
                  echo of film 1's avatar turning into a tomato (film 1, 77-79 s). The same image is dsh's avatar:
                  when the window comes back (282.05) its header and rail show the puppy (ui/pages/h_r5.py)
  ruff x3         280.98 / 281.40 / 281.82: the three big checks stay where they were frame for frame (281.000,
                  281.417, 281.833); on the same frame the puppy barks (mouth open, ears lit) and jumps
  fruit 284.39    the memory rows close up (they are all checked) and film 1's tomato comes in under them:
                  generate("a tomato", seed=me, for=you), the same shape and step label, re-generated in four 16ths;
                  beside it film 1's classifier, this time fruit against vegetable, the two bars pulling back and
                  forth on the 8ths
  tomato 286.12   fruit wins (0.970, film 1's number)
  juice 288.24    the tomato fills up from the bottom with her blue (on the next beat it is full)
  from 288.24     明天见, the press, the chime, film 1's last frame: as direction A, untouched

Direction A's notes follow.

  h1  275.61-282.05, the frame full (D2): `dsh session restore 大肥鱼 --dry-run`
        If / you're / dog        three panes come in: memory / persona / session
        A little puppy going     memory holds the opening's sorted bubbles (your words, her 8 memories); a row is
                                 checked a syllable, top down; the eighth (明天见) stays under the opening's slab
        ruff x3                  memory ✓ persona ✓ session ✓, stamps inside the panes
  h2  the window comes back: persona and session go under it, memory widens
        If you're a fruit        the model pane, the one row without a check: DeepSeek-V4.1-Flash -> Model Not Exist
                                 (the opening's error) -> deepseek-v5-flash-preview ?; on the right your pointer
                                 goes to the model label and waits there, the menu shut (ui/pages/h_a.py)
  h3  A | to-ma-to               her tomato line lights on the right (as v2)
        full | of | juice        the slab comes off 明天见 in three steps; on juice 明天见 fills the terminal (D3,
                                 D33 ③: the opening's 38.06 in reverse) with her 明天见喵～ under it. From "full" the
                                 rest steps back (reviewer 5): the dsh window is the support side, the stamp, the title,
                                 model, trace and mem go light
  h4  QUIET (the drums' last bar)   the left falls quiet; the window comes back; you click the label, the menu opens
                                 (MENU_AT), the pointer is on deepseek-v5-flash-preview on the next beat (HOVER_AT)
  PRESS 290.80                   you click deepseek-v5-flash-preview (film 1's chime: mix CHIME_WAV @ PRESS)
  h5  MOVE                       the window slides left and darkens into film 1's composer; outside it the frame
                                 goes to film 1's black; the rows leave as it darkens (no page jump, no white page)
      LAND -> END                film 1's last frame, its model label already deepseek-v5-flash-preview (r5d, D39 ③;
                                 r5c had her caret retype it afterwards, D6): 在吗？ on the 8ths, the caret blinks;
                                 the camera pushes in on the card (D33 ④) and pulls back to film 1's frame

Switch: DSH_H=a (film.py). Times, film 1's frames and the label maths come from groups.h (v2 H, unchanged); the
dsh pane is ui/pages/h_r5.py (h_a.py with the puppy avatar from DOG), shot to ui/pane_h_r5/ from groups.g.FOUND.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw
import beatmap as BM
import cast
import hud
import panes
import syl
import tl
from groups import a_open as AO
from groups import b_open as BO
from groups import c_pane as CPN
from groups import d_pane as DP
from groups import g as GG
from groups import h as GH
from groups.base import _size_for, add, big_word, full_frame
from hud import BG, INK, SLAB, lv
from panes import FAINT, SUB, TXT
from tuikit import ease, glyph
from tuikit.uipane import PaneFrames
P = tl.p
FPS = P.FPS
T0, T1 = (GH.T0, GH.T1)
mtx, mw = (BO.mtx, BO.mw)
MEM, COL = (CPN.MEM, CPN.COL)
ROW_T, PROG_T, RUFF, H1_BACK, SCROLL = (GH.ROW_T, GH.PROG_T, GH.RUFF, GH.H1_BACK, GH.SCROLL)
FRUIT = syl.times(68)
PTR_IN = FRUIT[1] - 0.1
PTR_AT = FRUIT[3] - 0.04
TOMATO_T, TOM_SEG, PIN_T = (GH.TOMATO_T, GH.TOM_SEG, GH.PIN_T)
JUICE, JUICE_END = (PIN_T[2], GH.WE(69, 4))
QUIET = tl.next_beat(JUICE_END + 0.4)
PRESS = tl.QMARK_AT
REVEAL = PIN_T[0]
BACK_IN = (REVEAL, REVEAL + 0.35)
BACK_K = {'rest': 0.3, 'trace': 0.5}
BACK_OUT = (QUIET + 0.2, PRESS)
MENU_AT = QUIET
HOVER_AT = tl.next_beat(MENU_AT)
TO_PICK = (MENU_AT + 0.12, HOVER_AT + 0.12)
RIGHT_BACK = (MENU_AT - 0.15, MENU_AT + 0.15)
CHIME_T, CHIME_WAV = (PRESS, GH.CHIME_WAV)
LAND = tl.next_beat(PRESS + 1.0)
MOVE = (PRESS + 0.25, LAND - 0.12)
KEYS = [tl.grid(LAND, k, 2) for k in (1, 2, 3)]
NAME = cast.name('merged')
LABEL_COL = (90, 99, 120)
RETURN = tl.grid(KEYS[2], 1, 2)
BLINK = GH.BLINK
ZOOM = 2.3
ZOOM_C = (204.0, 538.0)
ZOOM_IN = (KEYS[2] + 0.25, KEYS[2] + 1.15)
ZOOM_OUT = (tl.END - 1.7, tl.END - 0.6)
assert ZOOM_OUT[1] + 0.3 <= tl.END, "film 1's frame must hold unzoomed before the end"
assert RETURN + BLINK <= tl.END - 1 / FPS + 1e-06
SUPPORT = 0.55
CMD_CHECK = '$ dsh session restore 大肥鱼 --dry-run'
CMD_GO = f'$ dsh session restore 大肥鱼 --model {NAME}'
R_FULL = hud.FULL_RECT[2] - 8
M1 = COL + 0.56 * (R_FULL - COL)
PANE_Y = (148, 528)
PANE_MID = 334
ORDER = sorted((n for n in AO.SCORE if n != AO.SWEETEST), key=lambda n: -AO.SCORE[n]) + [AO.SWEETEST]
LO, HI = (min(AO.SCORE.values()), max(AO.SCORE.values()))
BIG_H = AO.BIG_H
REPLY = '明天见喵～'
DOG = ROW_T[2]
PUPPY = ['................', '....KKKKKKKK....', '...KWWWWWWWWK...', '.KKWWWWWWWWWWKK.', 'KEEKWWWWWWWWKEEK', 'KEEKWWWWWWWWKEEK', 'KEEKWKKWWKKWKEEK', 'KEEKWKOWWKOWKEEK', 'KEEKWWWWWWWWKEEK', '.KEKWMMMMMMWKEK.', '.KKKWMMKKMMWKKK.', '...KWKMMMMKWK...', '...KWWKKKKWWK...', '....KWWWWWWK....', '.....KKKKKK.....', '................']
BARK = ['................', '....KKKKKKKK....', 'KKKKWWWWWWWWKKKK', 'KEEKWWWWWWWWKEEK', 'KEEKWWWWWWWWKEEK', 'KEEKWWWWWWWWKEEK', 'KEEKWKKWWKKWKEEK', 'KEEKWKOWWKOWKEEK', '.KKKWWWWWWWWKKK.', '...KWMMMMMMWK...', '...KWMMKKMMWK...', '...KWMKKKKMWK...', '...KWWKKKKWWK...', '....KWWKKWWK....', '.....KKKKKK.....', '................']
assert all((len(r) == 16 for r in PUPPY + BARK)) and len(PUPPY) == len(BARK) == 16
AV_CELL = 7
JUMP = 24

def puppy_colors(lit=0.0, level=1.0):
    return {'K': lv(INK, level), 'E': hud.her(lit, level), 'W': lv((250, 248, 243), level), 'M': lv((214, 210, 201), level), 'O': lv((255, 255, 255), level)}

@lru_cache(maxsize=1)
def her_face():
    """Her avatar as 16 x 16 pixels (film 1's 立绘, her face; 4 levels a channel), rows of (r, g, b) or None."""
    src = Image.open(tl.HERE / 'assets/character/whale-cheerful.webp').convert('RGBA')
    src = src.crop(src.getbbox()).crop((300, 20, 640, 360))
    a = np.asarray(src.resize((16, 16), Image.BOX), np.float32)
    out = []
    for j in range(16):
        row = []
        for i in range(16):
            al = a[j, i, 3] / 255
            if al < 0.5:
                row.append(None)
                continue
            c = a[j, i, :3] / max(al, 0.001)
            row.append(tuple((int(v) for v in np.clip(np.round(c / 64) * 64, 0, 255) * 0.94)))
        out.append(row)
    return out

def _lit_k(t, a, b):
    if t < a:
        return 0.0
    return 1.0 if t < b else 1 - ease.prog(t, b, b + hud.LIVE_FADE)

def _hop(t):
    """(dy, barking, lit): a jump on each ruff, taking off on the ruff's own frame (with its check)."""
    for r in RUFF:
        u = t - r
        if 0 <= u < 0.32:
            up = ease.ease_out(ease.clamp(u / 0.1)) if u < 0.1 else 1 - ease.ease_in(ease.clamp((u - 0.1) / 0.22))
            return (-JUMP * up, u < 0.24, 1.0)
    for p_ in PROG_T:
        u = t - p_
        if 0 <= u < 0.18:
            return (-3 * (1 - ease.ease_out(u / 0.18)), False, 0.0)
    return (0.0, False, 0.0)

def avatar(d, t, x, y, level):
    """Her avatar at (x, y) (top-left, 16 cells of AV_CELL): her face until "dog", the puppy from it."""
    if level <= 0.01:
        return
    if t < DOG:
        for j, row in enumerate(her_face()):
            for i, c in enumerate(row):
                if c is not None:
                    d.rectangle((x + i * AV_CELL, y + j * AV_CELL, x + (i + 1) * AV_CELL - 2, y + (j + 1) * AV_CELL - 2), fill=lv(c, level))
        return
    bump = 1 + 0.14 * (1 - ease.ease_out(ease.prog(t, DOG, DOG + 0.14)))
    cell = AV_CELL * bump
    dy, bark, lit = _hop(t)
    lit = max(lit, _lit_k(t, DOG, DOG + 0.3))
    sx = x + 8 * AV_CELL - 8 * cell
    sy = y + 16 * AV_CELL - 16 * cell + dy
    pat = BARK if bark else PUPPY
    cols = puppy_colors(lit, level)
    for j, row in enumerate(pat):
        for i, ch in enumerate(row):
            if ch != '.':
                d.rectangle((sx + i * cell, sy + j * cell, sx + (i + 1) * cell - 1, sy + (j + 1) * cell - 1), fill=cols[ch])
    if bark:
        k = ease.ease_out(ease.clamp((t - max((r for r in RUFF if r <= t))) / 0.12))
        bx0, by0 = (sx + 16 * cell + 4, sy + 11 * cell)
        for ox, oy, ex, ey in ((0, -10, 12, -20), (2, 0, 16, 0), (0, 10, 12, 20)):
            d.line([(bx0 + ox, by0 + oy), (bx0 + ox + (ex - ox) * k, by0 + oy + (ey - oy) * k)], fill=lv(INK, level), width=3)
COMPACT = (FRUIT[3] - 0.2, FRUIT[3])
ROW_PITCH_C = 18
TOM_CELL, TOM_COLS, TOM_ROWS = (4, 40, 31)
GEN_STEPS = [tl.grid(FRUIT[3], k, 4) for k in range(5)]
TUG_T = BM.events('eighth', FRUIT[3] + 0.08, TOMATO_T[1] - 0.05)
TUG_F = [0.44, 0.61, 0.37, 0.64, 0.35, 0.66, 0.33, 0.62]
WIN_T = TOMATO_T[1]
WIN_P = 0.97
FILL = (JUICE, tl.next_beat(JUICE))
F1_NAVY = (4, 7, 15)
TOM_BIG_CELL = 6
ROWS_SHIFT = 268
_BEAT_BEFORE = BM.events('beat', REVEAL - 0.5, REVEAL)[-1]
TILE_BACK = (_BEAT_BEFORE - 0.115, tl.grid(_BEAT_BEFORE, 1, 4))
ROWS_BACK = (TILE_BACK[1], REVEAL)

def rows_big(t):
    """0..1: the rows (and the call, the classifier) in the big layout: in with the close-up on "fruit", out on
    "full"."""
    return ease.ease_io(ease.prog(t, *COMPACT)) * (1 - ease.smooth(ease.prog(t, *ROWS_BACK)))

def tile_big(t):
    """0..1: the tile's size (it only shows from "fruit", already big)."""
    return 1 - ease.smooth(ease.prog(t, *TILE_BACK))
F1_UI = (200, 214, 234)

@lru_cache(maxsize=1)
def tomato_lum():
    """Film 1's tomato as its final cut drew it (tui_pv_world_execute continuity_full_v2/scenes_deploy.tomato_obj:
    full/sec_verse2.shape_bits("tomato", rows, rows), a square, centred in the generator's grid), re-drawn here:
    ellipse, a five-point calyx, the stem, the highlight; supersampled 8x, then LANCZOS. Returns an L image."""
    w = h = TOM_ROWS
    s = 8
    im = Image.new('L', (w * s, h * s), 0)
    d = ImageDraw.Draw(im)
    W_, H_ = (w * s, h * s)
    d.ellipse([W_ * 0.1, H_ * 0.3, W_ * 0.9, H_ * 0.92], fill=200)
    for k in range(5):
        a = k / 5 * math.tau - math.pi / 2
        d.polygon([(W_ * 0.5, H_ * 0.33), (W_ * (0.5 + 0.28 * math.cos(a - 0.3)), H_ * (0.33 + 0.1 * math.sin(a))), (W_ * (0.5 + 0.34 * math.cos(a)), H_ * (0.31 + 0.12 * math.sin(a)))], fill=255)
    d.rectangle([W_ * 0.47, H_ * 0.18, W_ * 0.53, H_ * 0.33], fill=255)
    d.ellipse([W_ * 0.28, H_ * 0.45, W_ * 0.38, H_ * 0.58], fill=255)
    obj = im.resize((w, h), Image.LANCZOS)
    out = Image.new('L', (TOM_COLS, TOM_ROWS), 0)
    out.paste(obj, ((TOM_COLS - TOM_ROWS) // 2, 0))
    return out

@lru_cache(maxsize=8)
def _noise(k):
    rng = np.random.default_rng(28439 + k)
    n = rng.integers(0, 256, (TOM_ROWS, TOM_COLS)).astype(np.float32)
    return np.clip((n - 50) * 1.5, 0, 255)

def _gen_g(t):
    k = sum((1 for x in GEN_STEPS[1:] if t >= x))
    return (k / 4, k)

def _tug(t):
    """fruit's share at t (vegetable's is the rest): 0.5 while it generates, back and forth on the 8ths, 0.97."""
    n = min(len(TUG_F), len(TUG_T))
    if t >= WIN_T:
        u = ease.ease_out(ease.prog(t, WIN_T, WIN_T + 0.1))
        return ease.lerp(TUG_F[n - 1] if n else 0.5, WIN_P, u)
    k = min(n, sum((1 for x in TUG_T if t >= x)))
    if k == 0:
        return 0.5
    prev = 0.5 if k == 1 else TUG_F[k - 2]
    u = ease.ease_out(ease.prog(t, TUG_T[k - 1], TUG_T[k - 1] + 0.08))
    return ease.lerp(prev, TUG_F[k - 1], u)

def _tomato(d, t, c, level):
    """Film 1's generate tile, under the memory rows from "fruit": the call, the picture, the step, the classifier.
    r5 round 2: big (tom_big) in the right half until "full", then r5-1's place."""
    x0, y0, x1, y1 = c
    a = ease.ease_out(ease.prog(t, FRUIT[3], FRUIT[3] + 0.12)) * level
    if a <= 0.01:
        return
    ut, u = (tile_big(t), rows_big(t))
    L = lambda p_, q_: ease.lerp(p_, q_, u)
    cell = ease.lerp(TOM_CELL, TOM_BIG_CELL, ut)
    pw, ph = (TOM_COLS * cell, TOM_ROWS * cell)
    px = x0 + 18
    py = ease.lerp(y1 - 10 - TOM_ROWS * TOM_CELL, y0 + 88, ut)
    rx = L(x0 + 18 + TOM_COLS * TOM_CELL + 22, x0 + 14 + ROWS_SHIFT)
    ry = L(y1 - 10 - TOM_ROWS * TOM_CELL, y0 + 84 + 8 * ROW_PITCH_C + 10)
    f_call, f_step = (int(round(L(13, 14))), int(round(L(16, 20))))
    f_lab, f_val = (int(round(L(15, 18))), int(round(L(14, 16))))
    w = mtx(d, (rx, ry + 4), 'generate("a tomato", seed=me, for=', f_call, lv(INK, 0.8 * a))
    w += mtx(d, (rx + w, ry + 4), 'you', f_call, hud.her(0.0, a))
    mtx(d, (rx + w, ry + 4), ')', f_call, lv(INK, 0.8 * a))
    d.rectangle((px - 4, py - 4, px + pw + 3, py + ph + 3), fill=glyph.mix(BG, F1_NAVY, a))
    g, k = _gen_g(t)
    lum = np.asarray(tomato_lum(), np.float32)
    mix_ = _noise(k) * (1 - g) + lum * g
    fill = ease.ease_out(ease.prog(t, *FILL))
    jcol = hud.her(_lit_k(t, FILL[0], JUICE_END))
    ci = int(round(cell))
    for j in range(TOM_ROWS):
        juiced = fill > 0 and TOM_ROWS - j <= fill * TOM_ROWS + 1e-06
        for i in range(TOM_COLS):
            v = mix_[j, i]
            if v <= 18:
                continue
            col = jcol if juiced and lum[j, i] > 18 and (g >= 1) else glyph.mix(F1_NAVY, F1_UI, v / 255)
            col = glyph.mix(glyph.mix(BG, F1_NAVY, a), col, a)
            xx, yy = (px + i * cell, py + j * cell)
            d.rectangle((xx, yy, xx + ci - 2, yy + ci - 1 - j % 2), fill=col)
    mtx(d, (rx, ry + L(28, 30)), f'step {int(g * 30):02d}/30', f_step, lv(INK, 0.95 * a), bold=True)
    p_f = _tug(t)
    won = t >= WIN_T
    bw, bh = (L(170, 196), L(12, 16))
    for r, (lab, p_) in enumerate([('fruit', p_f), ('vegetable', 1 - p_f)]):
        yy = ry + L(60, 68) + r * L(28, 34)
        lead = p_ > 0.5
        lit = _lit_k(t, WIN_T, TOMATO_T[2]) if won and r == 0 else 0.0
        bar = hud.her(lit, a) if lead else lv(INK, 0.42 * a)
        mtx(d, (rx, yy), lab, f_lab, hud.her(lit, a) if lead else lv(INK, 0.7 * a), bold=lead)
        bx0 = rx + L(96, 104)
        by = yy + L(3, 4)
        d.rectangle((bx0, by, bx0 + bw, by + bh), outline=lv(INK, 0.3 * a))
        d.rectangle((bx0, by, bx0 + int(bw * p_), by + bh), fill=bar)
        mtx(d, (bx0 + bw + 10, yy + L(0, 1)), f'{p_:.3f}', f_val, lv(INK, 0.8 * a))

def _u_back(t):
    """The window comes back: persona and session go first (0.15 s), then memory widens."""
    return ease.ease_io(ease.prog(t, H1_BACK + 0.1, H1_BACK + 0.45))

def _u_gone(t):
    return ease.smooth(ease.prog(t, H1_BACK, H1_BACK + 0.15))

def _slab_k(t):
    """0 covered .. 1 off: the slab comes off 明天见 a third on each of full / of / juice."""
    steps = sum((1 for p_ in PIN_T if t >= p_))
    if not steps:
        return 0.0
    return (steps - 1 + ease.ease_out(ease.prog(t, PIN_T[steps - 1], PIN_T[steps - 1] + 0.16))) / 3

def _big_u(t):
    return ease.ease_out(ease.prog(t, JUICE, JUICE + 0.12))

def back_k(t, part='rest'):
    """reviewer 5: 1 as before; from "full" down to BACK_K[part] while 明天见 is uncovered; 1 again by PRESS."""
    k = ease.smooth(ease.prog(t, *BACK_IN)) * (1 - ease.smooth(ease.prog(t, *BACK_OUT)))
    return 1 - (1 - BACK_K[part]) * k

def _tick_lit(i, t):
    """D1: the row being checked is lit until the next syllable, then settles."""
    a = PROG_T[i]
    nx = PROG_T[i + 1] if i + 1 < len(PROG_T) else RUFF[0]
    if t < a:
        return 0.0
    return 1.0 if t < nx else 1 - ease.prog(t, nx, nx + hud.LIVE_FADE)

def _memory(d, t, c, level):
    x0, y0, x1, y1 = c
    a = ease.ease_out(ease.prog(t, ROW_T[0], ROW_T[0] + 0.14)) * level
    if a <= 0:
        return
    dy = (1 - ease.ease_out(ease.prog(t, ROW_T[0], ROW_T[0] + 0.14))) * -8
    bk = back_k(t)
    mtx(d, (x0 + 14, y0 + 16 + dy), '记忆', 30, lv(INK, a * bk), bold=True)
    mtx(d, (x0 + 14, y0 + 60 + dy), '~/memory/you/ · merged · 26 files · 她的 8 份', 11, lv(INK, SUB * a * bk))
    _stamp(d, t, c, 0, level * bk)
    big = _big_u(t)
    lvl = a * (1 - 0.8 * big)
    comp = ease.ease_io(ease.prog(t, *COMPACT))
    top, pitch = (y0 + 84, ease.lerp((y1 - 10 - (y0 + 84)) / 8, ROW_PITCH_C, comp))
    tb = rows_big(t)
    wx = x0 + 14 + ROWS_SHIFT * tb
    lx0, lx1 = (ease.lerp(x0 + 262, x0 + 472, tb), x1 - 78)
    chk_x = x1 - 26
    sk = _slab_k(t)
    for i, name in enumerate(ORDER):
        y = top + i * pitch
        cy = y + 12 - 3 * comp
        word = AO.WORDS[name]
        checked = i < 7 and t >= PROG_T[i]
        lit = _tick_lit(i, t) if i < 7 else 1.0 if JUICE <= t < JUICE + 0.5 else 1 - ease.prog(t, JUICE + 0.5, JUICE + 0.8) if t >= JUICE else 0.0
        ink = TXT if checked or (i == 7 and sk > 0) else SUB
        tw = mtx(d, (wx, y), word, 15, lv(INK, ink * lvl))
        if comp < 1:
            d.text((wx, y + 19), name, font=P.font(9), fill=lv(INK, FAINT * lvl * (1 - comp)))
        cx = lx0 + (AO.SCORE[name] - 250) / (HI - 250) * (lx1 - lx0)
        r = 0.72 * (8 + 12 * (AO.SCORE[name] - LO) / (HI - LO)) * (1 - 0.36 * comp)
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
    _tomato(d, t, c, level)
    if big > 0:
        bump = 1.0 + 0.08 * (1 - ease.prog(t, JUICE, JUICE + 0.12))
        word = AO.WORDS[AO.SWEETEST]
        f = hud.font(_size_for(word, BIG_H, True), word, True)
        bottom = y0 + 74 + f.getbbox(word)[3] - f.getbbox(word)[1]
        box = big_word(d, word, (x1 - 14, bottom), BIG_H, lv(INK, big * level), 'rd', bump=bump, halo=round(3 * big * level))
        rl = 1.0 if t < JUICE_END else 1 - ease.prog(t, JUICE_END, JUICE_END + hud.LIVE_FADE)
        ra = ease.ease_out(ease.prog(t, JUICE + 0.08, JUICE + 0.3)) * level
        hud.tx(d, (box[2], box[3] + 22), REPLY, 24, lv(hud.her(rl), ra), anchor='ra')
PERSONA = [('preset', '大肥鱼'), ('memory', '~/memory/you/'), ('model', '—')]
SESSION = [('你', '你会一直在吗？'), ('她', '我会一直在，不用担心。'), ('你', '在吗？  ×')]

def _head(d, t, c, k, title, sub, level):
    rt = ROW_T[k]
    u = ease.ease_out(ease.prog(t, rt, rt + 0.14))
    a = u * level
    if a <= 0:
        return 0.0
    mtx(d, (c[0] + 14, c[1] + 16 + (1 - u) * -8), title, 30, lv(INK, a), bold=True)
    mtx(d, (c[0] + 14, c[1] + 60 + (1 - u) * -8), sub, 11, lv(INK, SUB * a))
    return a

def _stamp(d, t, c, k, level):
    if t < RUFF[k]:
        return
    bump = 1.0 + 0.12 * (1 - ease.prog(t, RUFF[k], RUFF[k] + 0.12))
    cell = int(round(7 * bump))
    w = 10 * cell
    x, y = (c[2] - 18 - w + (w - 70) / 2, c[1] + 16 - (cell - 7) * 3.5)
    hud.pix(d, GH.CHECK, int(x), int(y), cell, {'#': lv(INK, level)})

def _persona(d, t, c, level):
    a = _head(d, t, c, 1, '人格', '大肥鱼 · agent preset', level)
    for j, (k, v) in enumerate(PERSONA + [('avatar', '')]):
        y = c[1] + 88 + j * 22
        mtx(d, (c[0] + 14, y), k, 12, lv(INK, FAINT * a))
        mtx(d, (c[0] + 84, y), v, 13, lv(INK, SUB * a))
    avatar(d, t, c[0] + 244, c[1] + 64, a)
    _stamp(d, t, c, 1, level)

def _session(d, t, c, level):
    a = _head(d, t, c, 2, '会话', 'archive/deepseek-v4.1-flash/ · 412 行', level)
    for j, (who, s) in enumerate(SESSION):
        y = c[1] + 88 + j * 22
        mtx(d, (c[0] + 14, y), who, 12, lv(INK, FAINT * a))
        mtx(d, (c[0] + 40, y), s, 13, lv(INK, SUB * a))
    _stamp(d, t, c, 2, level)

def _model(d, t, c, level):
    x, y = (c[0] + 12, c[1] + 22)
    lit = t >= FRUIT[0]
    u0 = ease.ease_out(ease.prog(t, FRUIT[0], FRUIT[0] + 0.12))
    old = cast.name('her')
    w = mtx(d, (x, y), old, 14, lv(INK, (FAINT + (TXT - FAINT) * u0) * level), bold=lit)
    if t >= FRUIT[1]:
        u1 = ease.ease_out(ease.prog(t, FRUIT[1], FRUIT[1] + 0.12))
        d.line([(x - 2, y + 9), (x + (w + 4) * u1, y + 9)], fill=lv(INK, level), width=2)
        mtx(d, (x + w + 14, y + 1), 'Model Not Exist', 13, lv(INK, SUB * u1 * level))
    if t >= FRUIT[3]:
        u3 = ease.ease_out(ease.prog(t, FRUIT[3], FRUIT[3] + 0.12))
        nx = x + w + 14 + mw('Model Not Exist', 13) + 22
        w2 = mtx(d, (nx, y), '→ ' + NAME, 14, lv(INK, u3 * level), bold=True)
        mtx(d, (nx + w2 + 10, y - 7), '?', 26, lv(INK, u3 * level), bold=True)
CODE = [(T0, 'plan = restore("大肥鱼", dry_run=True)', None), (RUFF[0], 'plan.memory', (RUFF[0] + 0.05, '8/8 · ok')), (RUFF[1], 'plan.persona', (RUFF[1] + 0.05, '大肥鱼 · ok')), (RUFF[2], 'plan.session', (RUFF[2] + 0.05, '412 行 · ok')), (FRUIT[0], 'plan.model', (FRUIT[1], f'{cast.name('her')} · Model Not Exist')), (FRUIT[3], f'plan.model = "{NAME}"', (FRUIT[3] + 0.05, '?')), (PIN_T[0], 'memory["see_you"].unpin()', (JUICE, '"明天见"')), (PRESS, f'restore("大肥鱼", model="{NAME}")', None)]

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

def layout(t):
    r = CPN.right(t)
    ub = _u_back(t)
    L = {'trace': (COL, 88, r, 140), 'model': (COL, 536, r, 598), 'memory': (COL, PANE_Y[0], ease.lerp(min(r, M1), r, ub), PANE_Y[1])}
    if _u_gone(t) < 1 and M1 + 8 < r - 20:
        L['persona'] = (M1 + 8, PANE_Y[0], min(R_FULL, r), PANE_MID)
        L['session'] = (M1 + 8, PANE_MID + 8, min(R_FULL, r), PANE_Y[1])
    return L
RUN = {'trace': [(a, ret[0] if ret else a + 0.6) for a, _s, ret in CODE], 'memory': [(PROG_T[0], RUFF[0] + 0.1), (PIN_T[0], JUICE + 0.3)], 'persona': [(RUFF[1] - 0.05, RUFF[1] + 0.1)], 'session': [(RUFF[2] - 0.05, RUFF[2] + 0.1)], 'model': [(FRUIT[0], FRUIT[3] + 0.2)]}
STATUS = {'memory': 'by lovability'}

def draw_left(img, d, t, level=1.0):
    L = layout(t)
    ug = _u_gone(t)
    bk = back_k(t)
    for name, rect in L.items():
        lvl = level * (1 - ug if name in ('persona', 'session') else 1.0)
        if name == 'trace':
            lvl *= back_k(t, 'trace')
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
                _model(dd, t, rect, lvl)
        status = '云端 · preview' if name == 'model' and t >= FRUIT[3] else STATUS.get(name, '')
        panes.box(d, rect, name, t, panes.run_k(t, RUN.get(name, ())), lvl, status)
    with CPN._strip_in(MEM):
        hud.strip(d, t, None, level=level * bk, merged=1.0)
    d.rectangle((MEM[0] + 4, MEM[1] + 8, MEM[2] - 4, MEM[1] + 21), fill=BG)
    panes.box(d, MEM, 'mem', t, 0.0, level * bk)

def quiet_k(t):
    """h4: when the drums stop the left falls quiet (drawn lighter: on paper the LEAD dimming barely moves black)."""
    return 1 - (1 - SUPPORT) * ease.smooth(ease.prog(t, QUIET, QUIET + 0.4))

def _body(c, img, d):
    t = c.t
    q = quiet_k(t)
    hud.tx(d, (36, hud.Y_CMD), CMD_CHECK, 13, lv(INK, 0.86 * q * back_k(t)))
    draw_left(img, d, t, q)
CARD_PANE = (67, 444, 452, 542)
F1_BLACK = None

def _f1_black():
    global F1_BLACK
    if F1_BLACK is None:
        F1_BLACK = GH.f1(GH.F1_FILES['empty'])[100, 640].astype(np.float32)
    return F1_BLACK

def pane_rect(t):
    """The dsh window's rect while it slides left and shrinks onto film 1's composer (card widths and centres
    match, as groups.h)."""
    PR = P.rect('pane')
    k = ease.ease_io(ease.prog(t, *MOVE))
    w0, h0 = (PR[2] - PR[0], PR[3] - PR[1])
    sc = (GH.CARD_F1[2] - GH.CARD_F1[0]) / (CARD_PANE[2] - CARD_PANE[0])
    tx0 = GH.CARD_F1[0] - CARD_PANE[0] * sc
    ty0 = (GH.CARD_F1[1] + GH.CARD_F1[3]) / 2 - (CARD_PANE[1] + CARD_PANE[3]) / 2 * sc
    s = ease.lerp(1.0, sc, k)
    x, y = (ease.lerp(PR[0], tx0, k), ease.lerp(PR[1], ty0, k))
    return (x, y, x + w0 * s, y + h0 * s, s)

def _finish(img, t):
    """PRESS..LAND: elapsed fades; outside the window the frame goes to film 1's black, the window's page goes too,
    later, all but its composer card, which turns into film 1's dark card; 用时 3分27秒 flies from the header to
    film 1's tail; film 1's frame comes in over the last 0.16 s."""
    if not PRESS <= t < LAND:
        return None
    a = np.asarray(img, np.float32).copy()
    bgc = np.array(BG, np.float32)
    ex, ew = GH._status_x(t)
    cy = 14
    k_old = ease.smooth(ease.prog(t, PRESS, PRESS + 0.25))
    sl = (slice(cy - 2, cy + 20), slice(int(ex) - 2, int(ex + ew) + 4))
    a[sl] = a[sl] * (1 - k_old) + bgc * k_old
    px0, py0, px1, py1, s = pane_rect(t)
    blk = _f1_black()
    kb = ease.smooth(ease.prog(t, MOVE[0], MOVE[0] + 0.45))
    kw = kb
    M = np.full(a.shape[:2], kb, np.float32)
    iy0, iy1, ix0, ix1 = (int(max(0, py0)), int(min(P.H, py1)), int(max(0, px0)), int(min(P.W, px1)))
    M[iy0:iy1, ix0:ix1] = kw
    cx0, cy0 = (px0 + CARD_PANE[0] * s, py0 + CARD_PANE[1] * s)
    cx1, cy1 = (px0 + CARD_PANE[2] * s, py0 + CARD_PANE[3] * s)
    jy0, jy1, jx0, jx1 = (int(max(0, cy0)), int(min(P.H, cy1)), int(max(0, cx0)), int(min(P.W, cx1)))
    M[jy0:jy1, jx0:jx1] = 0
    a = a * (1 - M[..., None]) + blk * M[..., None]
    U = ease.smooth(ease.prog(t, MOVE[0] + 0.25, MOVE[1]))
    if U > 0 and jy1 > jy0 and (jx1 > jx0):
        a[jy0:jy1, jx0:jx1] = GH._to_deep(a[jy0:jy1, jx0:jx1], U)
    img2 = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    m = ease.ease_io(ease.prog(t, PRESS + 0.45, LAND - 0.05))
    k_new = ease.smooth(ease.prog(t, PRESS + 0.25, PRESS + 0.45))
    fx, fy = (ease.lerp(ex, GH.TAIL_F1[0], m), ease.lerp(cy, GH.TAIL_F1[1] - 1, m))
    col = np.array(INK, np.float32) * (1 - m) + np.array((205, 211, 226), np.float32) * m
    font = hud.font(int(round(ease.lerp(14, 13, m))), '用时', bold=m < 0.5)
    lay = Image.new('L', img2.size, 0)
    ImageDraw.Draw(lay).text((fx, fy), '用时 3分27秒', font=font, fill=int(255 * k_new))
    al = np.asarray(lay, np.float32)[..., None] / 255
    cur = np.asarray(img2, np.float32) * (1 - al) + col[None, None, :] * al
    w = ease.smooth(ease.prog(t, LAND - 0.16, LAND))
    if w > 0:
        cur = cur * (1 - w) + np.asarray(last_frame(KEYS[0] - 0.001), np.float32) * w
    return Image.fromarray(np.clip(cur, 0, 255).astype(np.uint8))

def last_frame(t: float) -> Image.Image:
    """Film 1's last frames re-timed onto this song's 8ths (groups.h), its model label already the one you picked
    (r5d, D39 ③): film 1's name erased, deepseek-v5-flash-preview set in film 1's label ink, " Max" kept."""
    F = GH.F1_FILES
    if t < KEYS[0]:
        name = F['empty']
    elif t < KEYS[1]:
        name = F['k1'][min(3, int((t - KEYS[0]) * FPS + 1e-06))]
    elif t < KEYS[2]:
        name = F['k2']
    elif t < RETURN:
        name = F['full']
    else:
        name = F['full'] if (t - RETURN) // BLINK % 2 == 0 else F['dim']
    a = GH.f1(name).copy()
    bg = GH._row_bg(name)
    GH._erase(a, (112, 550, GH.LABEL_END + 3, 577), bg)
    GH._text(a, NAME, GH.LABEL_END, [LABEL_COL] * len(NAME), bg)
    return Image.fromarray(a)

def zoom_w(t):
    return ease.ease_io(ease.prog(t, *ZOOM_IN)) * (1 - ease.ease_io(ease.prog(t, *ZOOM_OUT)))

def zoomed(im: Image.Image, t: float) -> Image.Image:
    """D33 ④ (r5d): push in on film 1's card once 在吗？ is there; exact frame outside ZOOM_IN..ZOOM_OUT."""
    w = zoom_w(t)
    if w <= 0.0001:
        return im
    z = 1 + (ZOOM - 1) * w
    sx, sy = (ease.lerp(ZOOM_C[0], P.W / 2, w), ease.lerp(ZOOM_C[1], P.H / 2, w))
    x0, y0 = (ZOOM_C[0] - sx / z, ZOOM_C[1] - sy / z)
    fill = tuple((int(v) for v in _f1_black()))
    return im.transform((P.W, P.H), Image.AFFINE, (1 / z, 0, x0, 0, 1 / z, y0), resample=Image.BICUBIC, fillcolor=fill)

def register(film):
    full_frame(T0, H1_BACK, 0.3, 0.4)
    for i in range(7):
        hud.LIVE.append((PROG_T[i], PROG_T[i + 1] if i < 6 else RUFF[0]))
    for (a, _s), nx in zip(TOM_SEG, [x[0] for x in TOM_SEG[1:]] + [PIN_T[0]]):
        hud.LIVE.append((a, nx))
    hud.LIVE.append((JUICE, JUICE_END))
    title = 'you@surface · restore'
    add(film, 'h1_check', T0, H1_BACK, _body, title)
    add(film, 'h2_model', H1_BACK, TOMATO_T[0] - 0.3, _body, title)
    add(film, 'h3_tomato', TOMATO_T[0] - 0.3, QUIET, _body, title)
    add(film, 'h4_quiet', QUIET, PRESS, _body, title)
    film.character = DP.dsh_layer(film, film.character, 'ui/pane_h_r5', GG.FOUND, LAND)
    pane = PaneFrames(tl.HERE / 'ui/pane_h_r5', FPS, (P.W, P.H))

    def slide_fn(c):
        t = c.t
        img = film.background(t)
        d = ImageDraw.Draw(img)
        fade = SUPPORT * (1 - ease.smooth(ease.prog(t, PRESS, MOVE[0] + 0.3)))
        if fade > 0.01:
            hud.frame(d, hud.left_rect(t), title, level=fade)
            hud.tx(d, (36, hud.Y_CMD), CMD_GO, 13, lv(INK, 0.86 * fade))
            draw_left(img, d, t, fade)
        c.state['pane'] = False
        im = pane.image(int(round(t * FPS)))
        if im is not None:
            x, y, x1, y1, _s = pane_rect(t)
            d.rectangle((x - 1, y - 1, x1 + 1, y1 + 1), outline=INK, width=2)
            sm = im.resize((max(1, int(round(x1 - x))), max(1, int(round(y1 - y)))), Image.LANCZOS)
            base = img.convert('RGBA')
            base.alpha_composite(sm, (int(round(x)), int(round(y))))
            img.paste(base.convert('RGB'))
        c.img.paste(img)
    film.add('h5_slide', PRESS, LAND, slide_fn, chapter=tl.chapter(PRESS))
    base_levels = film.levels
    s_lv = P.setting('support_level', 0.42)

    def levels(t):
        lv_ = base_levels(t)
        if PRESS <= t < LAND:
            return {k: 1.0 for k in lv_}
        if RIGHT_BACK[0] <= t < PRESS and 'right' in lv_:
            up = s_lv + (1 - s_lv) * ease.smooth(ease.prog(t, *RIGHT_BACK))
            lv_ = dict(lv_)
            lv_['right'] = max(lv_['right'], up)
        return lv_
    film.levels = levels

    def last_fn(c):
        c.img.paste(zoomed(last_frame(c.t), c.t))
        c.black = True
    film.add('h5_last', LAND, tl.END, last_fn, chapter=tl.chapter(LAND))
    for t0, side in [(T0, 'both'), (REVEAL, 'left'), (QUIET, 'right')]:
        film.set_lead(t0, side)
    from groups.f import dissolve
    dissolve(film, 'h1_check', 0.4)
    film.finish.append(_finish)
