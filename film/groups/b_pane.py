"""Group B, second sample r4 (sample_open_b/README.md §11): r3's content (groups/b_open.py) laid out in the named
panes of the third sample r2 (panes.py, groups/c_pane.py), so that B and C read as one terminal.

  input     your message as tokens with ids
  think     Kimi's thinking, the newest lines
  trace     the code lines that run, with their returns; in b9 your REPL (kimi.sample, the threshold loop)
  generate  what Kimi puts out: its markdown table, its answer, its recital of her line
  compare   the inspector against her: archive.search (412 cells, the ranked three), her line from archive[74], the
            template, cos(她, kimi) with the embeddings, film 1's frame, the diff; in b9 the radar of 24 samples
  forward   the model's real layer stack, live (owner, 10-03: "左边无论是否可以本地部署都可以展示内部")
  mem       her files

b9 (the frame breaks out): input, think and generate fold away; the trace pane becomes your REPL on the left and the
compare pane the radar on the right. From 75.25 the 3D tower (inside/, b9_tower) is the forward pane zoomed: its
chrome is drawn over the plate by a finish hook.

The fold (batch 2, ASTRA_20261003.md #6; with DSH_A=open): 40.86-41.30, A's sort board goes into the panes across
the cut (FOLD_ON below). Before that cut A draws its own frame; after 41.44 nothing of the fold is left.

Switch: DSH_B=pane (film.py). Content, timing and data come from groups.b_open (r3, unchanged).
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
import os
from contextlib import contextmanager
from PIL import Image, ImageDraw
import cast
import hud
import inspect_
import panes
import prompt_ids
import speed
import tl
from groups import a as GA
from groups import b as GB
from groups import b_open as BO
from groups import c_pane as CPN
from groups.base import big_word, full_frame
from hud import BG, HER_QUIET, INK, SLAB, lv
from panes import FAINT, SUB, TXT
from tuikit import ease, glyph
W = tl.W
T0, T1 = (BO.T0, BO.T1)
P = tl.p
PROMPT_IDS = prompt_ids.load()
mtx, mw = (BO.mtx, BO.mw)
MEM, COL, SPLIT = (CPN.MEM, CPN.COL, CPN.SPLIT)
S1, S2, REPLY1, EGG = (BO.S1, BO.S2, BO.REPLY1, BO.EGG)
SEND1, SEND2, SHRINK4, FOLD = (BO.SEND1, BO.SEND2, BO.SHRINK4, BO.FOLD)
NEAR_OUT, NEAR_BACK, RING_AT, SWITCH = (BO.NEAR_OUT, BO.NEAR_BACK, BO.RING_AT, BO.SWITCH)
BOOT2 = GB.BOOT2
PERFECT_AT = BO.PERFECT_AT

def b9_u(t):
    """b9: 1 while your REPL and the radar hold the terminal (the tower cuts in at SWITCH and covers the way back)."""
    return ease.ease_io(ease.prog(t, NEAR_OUT, NEAR_OUT + 0.3)) * (1 - ease.prog(t, SWITCH, SWITCH + 0.05))

def layout(t):
    r = CPN.right(t)
    u = b9_u(t)
    L = {'memory': MEM, 'input': (COL, 88, SPLIT, 146), 'think': (SPLIT + 8, 88, r, 146), 'trace': (COL, 154, r, 222), 'generate': (COL, 230, r, 376), 'compare': (COL, 384, r, 528), 'forward': (COL, 536, r, 598)}
    if u > 0:
        mid = COL + max(300, 0.4 * (r - COL))
        Z = {'input': (COL, 88, COL + 30, 146), 'think': (r - 30, 88, r, 146), 'trace': (COL, 88, mid, 528), 'generate': (COL, 230, r, 260), 'compare': (mid + 8, 88, r, 528)}
        for k, rect in Z.items():
            L[k] = panes.lerp_rect(L[k], rect, u)
    return (L, u)

def _cmdline(d, t, r, typed=None):
    """typed: how many characters of the command are in (the fold types it on "If"); None = all."""
    cmd = BO.CMD if t < NEAR_OUT else BO.CMD_NEAR if t < SWITCH else GB.CMD_QWEN
    hud.tx(d, (36, hud.Y_CMD), cmd if typed is None else cmd[:typed], 13, lv(INK, 0.86))
    chip = cast.term(tl.model(t))
    f = P.font(13, 'bold')
    t0 = SEND1 if t < SEND1 + 1.0 else SWITCH if t >= SWITCH else None
    shown = glyph.decode(chip, t, t0, cps=60) if t0 is not None else chip
    w = d.textlength(chip, font=f)
    d.rectangle((r - w - 12, hud.Y_CMD - 3, r, hud.Y_CMD + 17), fill=SLAB)
    d.text((r - w - 6, hud.Y_CMD), shown, font=f, fill=BG)
TURNS = [(GB.COMMITS1, SEND1), (GB.EGG_COMMITS, SEND2)]

def _input(d, t, r):
    commits, send = TURNS[1] if t >= GB.EGG_COMMITS[0][0] else TURNS[0]
    sent = t >= send
    fid = P.font(10)
    x, y = (r[0] + 10, r[1] + 11)
    for at, w in commits:
        if at > t:
            break
        tw = hud.width(w, 20, True)
        drop = (1 - ease.ease_out(ease.prog(t, at, at + 0.12))) * -5
        hud.tx(d, (x, y + drop), w, 20, lv(INK, TXT), True)
        by = y + 30
        bl = lv(INK, 0.85 if sent else 0.45)
        d.line([(x, by), (x + tw, by)], fill=bl)
        d.line([(x, by - 3), (x, by)], fill=bl)
        d.line([(x + tw, by - 3), (x + tw, by)], fill=bl)
        ids = prompt_ids.text(PROMPT_IDS[w]) if w in PROMPT_IDS else str(glyph.token_id(w))
        d.text((x, by + 3), ids, font=fid, fill=lv(INK, SUB))
        x += max(tw, d.textlength(ids, font=fid)) + 12
THINKS = BO.THINK1 + BO.THINK2

def _think(d, t, r):
    if t >= SWITCH:
        return
    shown = [(at, s) for at, s in THINKS if at <= t]
    if not shown:
        return
    last = shown[-1][0]
    sc = ease.ease_out(ease.prog(t, last, last + 0.14))
    for pos, (at, s) in enumerate(reversed(shown[-3:])):
        n = int((t - at) * BO.THINK_CPS) + 1
        a = {0: TXT, 1: SUB}.get(pos, SUB * (1 - sc))
        if pos == 0:
            a *= ease.prog(t, at, at + 0.1)
        y = r[1] + 30 - pos * 19 + (1 - sc) * 19
        if a > 0.01:
            mtx(d, (r[0] + 10, y), s[:n], 13, lv(INK, a))
CODE = [(at, s, BO.RET.get(i)) for i, (at, kind, s) in enumerate(BO.TRACE) if kind == 'code']
CODE += [(SWITCH, 'dsh.use("Qwen3.8-27B")', (SWITCH + 0.2, '本地')), (BOOT2, 'llama.load("27B · Q4_K_M")', (BOOT2 + 0.8, 'ok'))]

def _code_end(at, s, ret):
    return ret[0] if ret else at + len(s) / BO.CODE_CPS + 0.25

def _trace(d, t, r, level=1.0):
    shown = [(at, s, ret) for at, s, ret in CODE if at <= t and (not NEAR_OUT <= at < SWITCH)]
    if not shown or level <= 0.01:
        return
    last = shown[-1][0]
    sc = ease.ease_out(ease.prog(t, last, last + 0.14))
    for pos, (at, s, ret) in enumerate(reversed(shown[-4:])):
        y = r[1] + 47 - pos * 19 + (1 - sc) * 19
        a = {0: TXT, 1: SUB, 2: FAINT}.get(pos, FAINT * (1 - sc)) * level
        if pos == 0:
            a *= ease.prog(t, at, at + 0.1)
        n = int((t - at) * BO.CODE_CPS) + 1
        w = mtx(d, (r[0] + 10, y), s[:n], 14, lv(INK, 0.92 * a), bold=pos == 0)
        if ret and t >= ret[0]:
            u = ease.prog(t, ret[0], ret[0] + 0.1)
            mtx(d, (r[0] + 10 + w + 12, y), '→ ' + ret[1], 14, lv(INK, 0.7 * a * u), bold=True)

def _repl(d, t, r):
    if t < NEAR_OUT or t >= SWITCH:
        return
    a = ease.prog(t, NEAR_OUT, NEAR_OUT + 0.3)
    wide = hud.full_u(t)
    x0, y0 = (r[0] + 10, r[1] + 12)
    if wide > 0.01:
        for i, (at, line) in enumerate(BO.B9_CODE):
            if t < at:
                break
            n = int((t - at) * 90) + 1
            mtx(d, (x0, y0 + i * 20), line[:n], 13, lv(INK, (TXT if i == 0 else SUB) * a * wide), bold=i == 0)
    yc = ease.lerp(r[1] + 14, y0 + 76, wide)
    for i, at in enumerate(RING_AT):
        if t < at:
            break
        u = ease.prog(t, at, at + 0.1) * a
        y = yc + i * 32
        th = BO.B9_TH[i]
        hud.tx(d, (x0, y + 4), f'{th:.2f}', 20, lv(INK, SUB * u))
        hud.tx(d, (x0 + 90, y), f'{BO._b9_count(th):2d}', 26, lv(INK, u), True)
        hud.tx(d, (x0 + 128, y + 6), '/ 24', 16, lv(INK, SUB * u))
    at = RING_AT[-1]
    if t >= at:
        e = ease.ease_out(ease.prog(t, at, at + 0.15)) * a
        sy = yc + 5 * 32 + 14
        size = 26
        w = hud.width('exact hits 0', size, True)
        bump = 1.0 + 0.1 * (1 - ease.prog(t, at, at + 0.12))
        d.rectangle((x0 - 6, sy, x0 - 6 + (w + 14) * e * bump, sy + 40), fill=SLAB)
        if e > 0.9:
            hud.tx(d, (x0 + 1, sy + 5), 'exact hits 0', size, BG, True)
TABLE = BO.KIMI_TABLE
TCOLS = (0, 64, 152)

def _gen_table(d, t, g):
    """b3: its first answer starts as its habit, a markdown table, a cell a syllable (the pane shows the same)."""
    if t < BO.CELL_AT[0] or t >= S2.t_in:
        return
    a = (1 - (1 - SUB) * ease.prog(t, SHRINK4, SHRINK4 + 0.35)) * (1 - ease.prog(t, S2.t_in - 0.3, S2.t_in))
    x0, y0 = (g[0] + 14, g[1] + 12)
    rows = [TABLE[0], ['---', '---', '---'], TABLE[1], TABLE[2]]
    for ri, row in enumerate(rows):
        src = 0 if ri < 2 else ri - 1
        y = y0 + ri * 18
        for ci, cell in enumerate(row):
            at = BO.CELL_AT[src * 3 + ci]
            if t < at:
                continue
            u = ease.prog(t, at, at + 0.1) * a
            mtx(d, (x0 + TCOLS[ci], y), '|', 13, lv(INK, FAINT * u))
            mtx(d, (x0 + TCOLS[ci] + 12, y), cell, 13, lv(INK, (SUB if ri == 1 else TXT) * u))
        if t >= BO.CELL_AT[src * 3 + 2]:
            mtx(d, (x0 + 252, y), '|', 13, lv(INK, FAINT * a))

def _gen_reply(d, t, g):
    """b4: its answer, four chunks on "You're the on-ly"."""
    if t < REPLY1.tok_t[0] or t >= S2.t_in:
        return
    a = (1 - (1 - SUB) * ease.prog(t, SHRINK4, SHRINK4 + 0.35)) * (1 - ease.prog(t, S2.t_in - 0.3, S2.t_in))
    mtx(d, (g[0] + 10, g[1] + 100), 'out', 12, lv(INK, SUB * a))
    CPN._row(d, t, REPLY1, CPN.LX, g[1] + 90, CPN.OUT, a)

def _gen_egg(d, t, g):
    """b8: it recites her line, every chunk hers, minus 一根."""
    if t < EGG.tok_t[0] or t >= NEAR_OUT + 0.12:
        return
    a = 1 - ease.prog(t, NEAR_OUT, NEAR_OUT + 0.12)
    mtx(d, (g[0] + 10, g[1] + 24), 'out', 12, lv(INK, SUB * a))
    x, y = (CPN.LX, g[1] + 14)
    for k, (tk, at) in enumerate(zip(EGG.toks, EGG.tok_t)):
        if at is None or t < at:
            break
        lit = EGG.lit(at, t)
        drop = (1 - ease.ease_out(ease.prog(t, at, at + 0.14))) * -6
        if tk.text.strip() == '':
            GB.eggplant(d, x + 4, y + 4 + drop, 3, lit, a)
            break
        x += hud.tx(d, (x, y - CPN.OUT * 0.1 + drop), tk.text, CPN.OUT, lv(hud.her(lit), a), bold=True)
GP, GC = (8, 6)

def _grid(d, t, S, c, level):
    gx, gy = (c[0] + 10, c[1] + 14)
    done = S.rows_done(t)
    for i in range(BO.ARCH_N):
        rr, cc = divmod(i, BO.COLS)
        ap = ease.prog(t, S.t_in + rr * 0.018, S.t_in + rr * 0.018 + 0.1) * level
        if ap <= 0:
            continue
        x, y = (gx + cc * GP, gy + rr * GP)
        if not BO._is_you(i):
            fill = lv(HER_QUIET, 0.34 * ap)
        elif t >= S.t0 and rr < done:
            fill = lv(INK, (0.12 + 0.86 * S.score[i] ** 1.6) * ap)
        else:
            fill = lv(INK, 0.12 * ap)
        d.rectangle((x, y, x + GC - 1, y + GC - 1), fill=fill)
    if S.t0 <= t < S.t1 + 0.05:
        y = gy + done * GP - 1
        d.rectangle((gx - 4, y, gx + BO.COLS * GP + 2, y), fill=lv(INK, level))
    for k, (i, _s, _q) in enumerate(S.top):
        at = S.list_at[k]
        if t < at:
            break
        rr, cc = divmod(i, BO.COLS)
        x, y = (gx + cc * GP, gy + rr * GP)
        u = ease.ease_out(ease.prog(t, at, at + 0.12))
        g = 2 + 5 * (1 - u)
        d.rectangle((x - g, y - g, x + GC - 1 + g, y + GC - 1 + g), outline=lv(INK, level))
    if t >= S.pick:
        rr, cc = divmod(S.top[0][0] + 1, BO.COLS)
        x, y = (gx + cc * GP, gy + rr * GP)
        lit = 1 - ease.prog(t, S.pick + 0.3, S.pick + 0.3 + hud.LIVE_FADE)
        d.rectangle((x - 1, y - 1, x + GC, y + GC), fill=hud.her(lit, level))
LX0 = COL + 10 + 32 * GP + 26

def _list_row(d, x, y, k, i, s, q, level):
    hud.tx(d, (x, y + 2), f'{i:04d}', 12, lv(INK, SUB * level))
    mtx(d, (x + 42, y), q, 15, lv(INK, level), bold=k == 0)
    bx = x + 210
    d.rectangle((bx, y + 6, bx + 80, y + 13), outline=lv(INK, FAINT * level))
    d.rectangle((bx, y + 6, bx + 80 * s, y + 13), fill=lv(INK, (1.0 if k == 0 else 0.55) * level))
    if s >= 1.0:
        w = hud.width('1.00', 14, True)
        d.rectangle((bx + 88, y, bx + 98 + w, y + 19), fill=lv(SLAB, level))
        hud.tx(d, (bx + 93, y + 1), '1.00', 14, BG, True)
    else:
        hud.tx(d, (bx + 90, y + 1), f'{s:.2f}', 14, lv(INK, level), True)

def _search(d, t, S, c, t_out):
    if t < S.t_in or t >= t_out + 0.3:
        return
    a = 1 - ease.prog(t, t_out, t_out + 0.3)
    _grid(d, t, S, c, a)
    for k, (i, s, q) in enumerate(S.top):
        at = S.list_at[k]
        if t < at:
            break
        u = ease.prog(t, at, at + 0.1)
        if k == 0 and t >= S.pick and (S is S1):
            continue
        _list_row(d, LX0, c[1] + 16 + k * 28 + (1 - ease.ease_out(u)) * -6, k, i, s, q, u * a)

def _scan_status(t):
    for S in (S1, S2):
        if S.t0 <= t < S.pick:
            return f'scan {min(BO.ARCH_N, int(S.rows_done(t) * BO.COLS)):3d}/{BO.ARCH_N}'
    return None
HER_CH = BO.HER_CH
Y_Q, Y_HER2, Y_HER1, Y_K1 = (14, 44, 14, 42)
S_HER2, S_HER1 = (24, 20)

def _slots(c, u):
    """(x, y, w, size) of her slots: u = 0 the found line under its question (24 px), 1 the row over Kimi's (20 px)."""
    x, out = (ease.lerp(CPN.LX + 28, CPN.LX, u), [])
    size = ease.lerp(S_HER2, S_HER1, u)
    y = c[1] + ease.lerp(Y_HER2, Y_HER1, u)
    for ch in HER_CH:
        w = BO._slot_w(ch, size)
        out.append((x, y, w, size))
        x += w
    return out

def _found(d, t, c):
    """b2-b4: the question flies up from the list, her answer (archive[74]) under it a segment a syllable, the blank
    of her pattern; on the fold her line moves up over Kimi's answer."""
    if t < S1.pick or t >= SHRINK4 + 0.4:
        return None
    out = 1 - ease.prog(t, SHRINK4, SHRINK4 + 0.3)
    fu = ease.ease_io(ease.prog(t, *FOLD))
    i, s, q = S1.top[0]
    qa = (1 - ease.prog(t, FOLD[0], FOLD[0] + 0.25)) * out
    if qa > 0.01:
        u = ease.ease_io(ease.prog(t, S1.pick, S1.pick + 0.3))
        y = ease.lerp(c[1] + 16, c[1] + Y_Q, u)
        x = ease.lerp(LX0, c[0] + 10, u)
        hud.tx(d, (x, y + 2), f'{i:04d}', 12, lv(INK, SUB * qa))
        mtx(d, (x + 42, y), '你  ' + q, 15, lv(INK, 0.85 * qa))
    if t < BO.HER_AT:
        return None
    ha = ease.prog(t, BO.HER_AT, BO.HER_AT + 0.12) * out
    y_lab = c[1] + ease.lerp(Y_HER2 + 6, Y_HER1 + 3, fu)
    if fu < 1:
        hud.tx(d, (c[0] + 10, y_lab + 2), f'{i + 1:04d}', 12, lv(HER_QUIET, SUB * ha * (1 - fu)))
    mtx(d, (c[0] + 10 + 42 * (1 - fu), y_lab), '她', 14 + 2 * fu, lv(HER_QUIET, ha), bold=fu > 0.5)
    blank = ease.ease_io(ease.prog(t, BO.BLANK_AT, BO.BLANK_AT + 0.3)) * (1 - fu)
    slots = _slots(c, fu)
    for k, (ch, (x, y, w, size)) in enumerate(zip(HER_CH, slots)):
        seg = BO.SEG_OF[k]
        at = BO.FOUND_AT[seg]
        nx = BO.FOUND_AT[seg + 1] if seg + 1 < len(BO.FOUND_AT) else at + 0.5
        if t < at:
            colr = lv(INK, 0.22)
        else:
            colr = hud.her(1.0 if t < nx else 1 - ease.prog(t, nx, nx + hud.LIVE_FADE))
        gk = blank if k in (7, 8, 9, 10, 12) else 0.0
        if gk >= 1:
            continue
        if ch == '🍆':
            GB.eggplant(d, x + 3, y + size * 0.05, max(2, int(size / 9)), 0.0, out * (1 - gk))
        else:
            hud.tx(d, (x, y - size * 0.1), ch, int(round(size)), lv(colr, out * (1 - gk)), bold=True)
    if blank > 0:
        x0, x1 = (slots[7][0], slots[10][0] + slots[10][2])
        y1 = slots[7][1] + slots[7][3] + 3
        for xx in range(int(x0), int(x1), 9):
            d.line([(xx, y1), (min(xx + 5, x1), y1)], fill=lv(HER_QUIET, blank * out), width=2)
    return slots

def _kimi_x(her, k, text):
    if k == 0:
        return her[0][0]
    if k == 1:
        return her[5][0]
    if k == 3:
        return her[11][0]
    a, b = (7, 10) if k == 2 else (12, 12)
    return (her[a][0] + her[b][0] + her[b][2]) / 2 - hud.width(text, S_HER1, True) / 2
EY = (74, 90, 106)
EP = 11

def _cos(d, t, c, her):
    """b4: Kimi's answer under her row, both embedded, multiplied cell by cell; the sum runs to 0.97 on perfect."""
    if t < FOLD[0] or t >= SHRINK4 + 0.4 or her is None:
        return
    out = 1 - ease.prog(t, SHRINK4, SHRINK4 + 0.3)
    al = ease.prog(t, FOLD[0] + 0.2, FOLD[1]) * out
    mtx(d, (c[0] + 10, c[1] + Y_K1 + 3), 'kimi', 14, lv(INK, al), bold=True)
    for k, (tk, at) in enumerate(zip(REPLY1.toks, REPLY1.tok_t)):
        if t < at:
            break
        colr = INK if tk.src == 'self' else hud.her(REPLY1.lit(at, t))
        drop = (1 - ease.ease_out(ease.prog(t, at, at + 0.14))) * -6
        hud.tx(d, (_kimi_x(her, k, tk.text), c[1] + Y_K1 - S_HER1 * 0.1 + drop), tk.text, S_HER1, lv(colr, out), bold=True)
    for k, at in enumerate(BO.MIS_AT):
        if t < at:
            break
        u = ease.ease_out(ease.prog(t, at, at + 0.15)) * out
        a_, b_ = (7, 10) if k == 0 else (12, 12)
        x0, x1 = (her[a_][0] - 3, her[b_][0] + her[b_][2] + 3)
        y = her[0][1]
        d.rectangle((x0, y - 4, ease.lerp(x0, x1, u), y + S_HER1 + 5), outline=lv(INK, out))
        text = REPLY1.toks[2 if k == 0 else 4].text
        kx = _kimi_x(her, 2 if k == 0 else 4, text)
        kw = hud.width(text, S_HER1, True)
        yk = c[1] + Y_K1
        d.rectangle((kx - 3, yk - 4, ease.lerp(kx - 3, kx + kw + 3, u), yk + S_HER1 + 5), outline=lv(INK, out))
    if t < REPLY1.tok_t[0] - 0.2:
        return
    ae = ease.prog(t, REPLY1.tok_t[0] - 0.2, REPLY1.tok_t[0]) * out
    ex = CPN.LX
    for j, lab in enumerate(('她', 'kimi', '×')):
        mtx(d, (c[0] + 10, c[1] + EY[j] - 1), lab, 11, lv(HER_QUIET if j == 0 else INK, SUB * ae))
    filled = 0
    for k, at in enumerate(REPLY1.tok_t):
        if t >= at:
            filled = BO.CHUNK_DIMS[k][1]
    sw = ease.clamp((t - BO.SWEEP[0]) / (BO.SWEEP[1] - BO.SWEEP[0]))
    swept = min(filled, int(sw * BO.EMB_N + 1e-06))
    mis = [i for k, at in enumerate(BO.MIS_AT) if t >= at for i in BO.DIFF_DIMS[k]]
    for i in range(BO.EMB_N):
        x = ex + i * EP
        _cell(d, x, c[1] + EY[0], BO.EMB_H[i], ae)
        if i < filled:
            _cell(d, x, c[1] + EY[1], BO.EMB_K[i], ae, lv(INK, out) if i in mis else None)
        else:
            d.rectangle((x, c[1] + EY[1], x + EP - 3, c[1] + EY[1] + 11), outline=lv(INK, 0.2 * ae))
        y = c[1] + EY[2]
        if i < swept:
            p = BO.EMB_H[i] * BO.EMB_K[i]
            if p >= 0:
                d.rectangle((x, y, x + EP - 3, y + 11), fill=lv(INK, (0.15 + 0.85 * p) * ae))
            else:
                d.rectangle((x, y, x + EP - 3, y + 11), outline=lv(INK, ae))
        else:
            d.rectangle((x, y, x + EP - 3, y + 11), outline=lv(INK, 0.2 * ae))
    if BO.SWEEP[0] <= t < BO.SWEEP[1]:
        x = ex + sw * BO.EMB_N * EP
        d.rectangle((x - 1, c[1] + EY[0] - 3, x, c[1] + EY[2] + 14), fill=lv(INK, out))
    f = 'cos(她, kimi) ='
    mtx(d, (c[2] - 14 - mw(f, 18, True), c[1] + 12), f, 18, lv(INK, ae), bold=True)
    val = BO._cos(BO.EMB_H, BO.EMB_K, swept) if swept else 0.0
    if t < PERFECT_AT:
        hud.tx(d, (c[2] - 14, c[1] + 44), f'{val:.2f}', 22, lv(INK, ae), True, anchor='ra')
        return
    grow = ease.ease_out(ease.prog(t, PERFECT_AT, PERFECT_AT + 0.12))
    bump = 1.0 + 0.12 * (1 - ease.prog(t, PERFECT_AT, PERFECT_AT + 0.14))
    big_word(d, BO.SIM1, (c[2] - 14, c[1] + 42), int(ease.lerp(16, 62, grow)), lv(INK, out), 'ra', bump=bump)

def _cell(d, x, y, v, level, outline=None):
    d.rectangle((x, y, x + EP - 3, y + 11), fill=lv(INK, (0.06 + 0.84 * (v + 1) / 2) * level))
    if outline:
        d.rectangle((x - 2, y - 2, x + EP - 1, y + 13), outline=outline)
FS = 0.6
_PL = {}

def _plate_img():
    if 'p' not in _PL:
        im = Image.open(BO.F1).convert('RGB')
        head, chat = (im.crop(BO.HEAD_BOX), im.crop(BO.CHAT_BOX))
        w = BO.HEAD_BOX[2] - BO.HEAD_BOX[0]
        plate = Image.new('RGB', (w, head.size[1] + chat.size[1]))
        plate.paste(head, (0, 0))
        plate.paste(chat, (0, head.size[1]))
        _PL['p'] = plate.resize((int(w * FS), int(plate.size[1] * FS)), Image.LANCZOS)
    return _PL['p']

def _seg_box(c, k):
    px, py = (c[0] + 10, c[1] + 14)
    hh = BO.HEAD_BOX[3] - BO.HEAD_BOX[1]

    def xy(fx, fy):
        return (px + (fx - BO.CHAT_BOX[0]) * FS, py + (hh + fy - BO.CHAT_BOX[1]) * FS)
    a, b = BO.SEG_CH[k]
    x0, y0 = xy(BO.ANS_X0 + a * BO.CH_W, BO.ANS_Y0)
    x1, y1 = xy(BO.ANS_X0 + b * BO.CH_W, BO.ANS_Y1)
    return (x0, y0, x1, y1)

def _frame(img, d, t, c):
    """b6-b8: archive[74] is film 1's frame; underlined a segment a syllable; selected into its context; the diff."""
    if t < BO.SURF_AT or t >= NEAR_OUT + 0.12:
        return
    out = 1 - ease.prog(t, NEAR_OUT, NEAR_OUT + 0.12)
    plate = _plate_img()
    u = ease.ease_out(ease.prog(t, BO.SURF_AT, BO.SURF_AT + 0.35)) * out
    px, py = (int(c[0] + 10), int(c[1] + 14 + 16 * (1 - u)))
    region = img.crop((px, py, px + plate.size[0], py + plate.size[1]))
    img.paste(Image.blend(region, plate, u), (px, py))
    d.rectangle((px - 1, py - 1, px + plate.size[0], py + plate.size[1]), outline=lv(INK, SUB * u))
    xr = px + plate.size[0] + 18
    mtx(d, (xr, c[1] + 16), 'archive[74] · film 1 · 01:14', 12, lv(INK, SUB * u))
    for k, at in enumerate(BO.UNDER_AT):
        if t < at:
            break
        x0, y0, x1, y1 = _seg_box(c, k)
        nx = BO.UNDER_AT[k + 1] if k + 1 < len(BO.UNDER_AT) else at + 0.5
        lit = 1.0 if t < nx else 1 - ease.prog(t, nx, nx + hud.LIVE_FADE)
        w = ease.ease_out(ease.prog(t, at, at + 0.12))
        d.rectangle((x0, y1 + 2, x0 + (x1 - x0) * w, y1 + 3), fill=lv(hud.her(lit), out))
    for k, at in enumerate(BO.SELECT_AT):
        if t < at:
            break
        x0, y0, x1, y1 = _seg_box(c, k)
        w = ease.ease_out(ease.prog(t, at, at + 0.1))
        d.rectangle((x0 - 1, y0 - 2, x0 - 1 + (x1 - x0 + 2) * w, y1 + 1), outline=lv(HER_QUIET, out))
    if t >= BO.SELECT_AT[0]:
        mtx(d, (xr, c[1] + 36), '→ context', 13, lv(INK, SUB * out * ease.prog(t, BO.SELECT_AT[0], BO.SELECT_AT[0] + 0.15)))
    if t < BO.DIFF_AT:
        return
    k = ease.ease_out(ease.prog(t, BO.DIFF_AT, BO.DIFF_AT + 0.15)) * out
    y_h, y_k, size = (c[1] + 66, c[1] + 98, 20)
    mtx(d, (xr, y_h + 3), '她', 14, lv(HER_QUIET, k), bold=True)
    mtx(d, (xr, y_k + 3), 'kimi', 14, lv(INK, k), bold=True)
    x = xr + 52
    slots = []
    for ch in '好呀！现在我是一根茄子了':
        slots.append(x)
        hud.tx(d, (x, y_h - size * 0.1), ch, size, lv(HER_QUIET, k), True)
        x += hud.width(ch, size, True)
    x = xr + 52
    for j, ch in enumerate('好呀！现在我是一根茄子了'):
        if j in (7, 8):
            continue
        hud.tx(d, (slots[j], y_k - size * 0.1), ch, size, lv(INK, k), True)
    a0, a1 = (slots[7] - 3, slots[9] + 3)
    d.rectangle((a0, y_h - 4, a1, y_h + size + 5), outline=lv(INK, k), width=2)
    for xx in range(int(a0 + 3), int(a1 - 3), 8):
        d.line([(xx, y_k + size + 3), (min(xx + 4, a1 - 3), y_k + size + 3)], fill=lv(INK, SUB * k))
    x0, y0, x1, y1 = _seg_box(c, 3)
    d.rectangle((x0 - 2, y0 - 3, x1 + 2, y1 + 3), outline=lv(INK, k), width=2)

def _radar(d, t, c):
    if t < NEAR_OUT + 0.12 or t >= SWITCH:
        return
    a = ease.prog(t, NEAR_OUT + 0.12, NEAR_OUT + 0.36)
    wide = hud.full_u(t)
    w, h = (c[2] - c[0], c[3] - c[1])
    R = max(40.0, min((h - 100) / 2, (w - 60 - 230 * wide) / 2))
    cx, cy = (c[0] + 30 + R, c[1] + 50 + R)
    radii = [R * 1.12] + [BO._rad(th, R) for th in BO.B9_TH]
    k = sum((1 for s in BO.B9_STEPS if t >= s)) - 1
    if k + 1 < len(BO.B9_STEPS):
        u = ease.ease_io(ease.prog(t, BO.B9_STEPS[k], BO.B9_STEPS[k + 1]))
        r_ring = ease.lerp(radii[k], radii[k + 1], u)
    else:
        r_ring = radii[-1]
    hud.pix(d, ['..#..', '.###.', '#####', '.###.', '..#..'], cx - 10, cy - 10, 4, {'#': lv(HER_QUIET, a)})
    mtx(d, (cx - 18, cy + 16), '她 · 0074', 13, lv(HER_QUIET, a))
    for j in BO._ORDER:
        s = BO.B9_SIMS[j]
        at = BO.B9_SPAWN[BO._ORDER.index(j)]
        if t < at:
            continue
        g = ease.ease_out(ease.prog(t, at, at + 0.16))
        rp = BO._rad(s, R)
        ang = BO.B9_ANG[j]
        px, py = (cx + rp * g * math.cos(ang), cy + rp * g * math.sin(ang))
        vis = ease.lerp(0.22, 1.0, ease.clamp((r_ring - rp) / 8 + 0.5))
        d.ellipse((px - 4, py - 4, px + 4, py + 4), fill=lv(INK, vis * a))
        if j in BO.B9_LABEL and wide > 0.05:
            ly = cy - 70 + 46 * j
            lx = cx + R + 18
            la = vis * a * wide * ease.prog(t, at + 0.1, at + 0.3)
            d.line([(px + 5, py), (lx - 30, ly + 9), (lx - 6, ly + 9)], fill=lv(INK, 0.5 * la))
            ww = mtx(d, (lx, ly), f'{s:.2f}  ' + BO.B9_LABEL[j], 13, lv(INK, la))
            GB.eggplant(d, lx + ww + 4, ly + 1, 2, 0.0, la)
    if r_ring > 2:
        d.ellipse((cx - r_ring, cy - r_ring, cx + r_ring, cy + r_ring), outline=lv(INK, 0.9 * a), width=2)
    lab = f'cos ≥ {BO.B9_TH[k - 1]:.2f}' if k >= 1 else 'n = 24'
    mtx(d, (cx - mw(lab, 18, True) / 2, c[1] + 14), lab, 18, lv(INK, a), bold=True)

def _kimi_segs():
    out = CPN._think_passes(THINKS, BO.THINK_CPS)
    out += [(at - 0.12, at) for at in sorted(set(BO.CELL_AT))]
    out += CPN._landings(REPLY1) + CPN._landings(EGG)
    out += CPN._passes(NEAR_OUT + 0.05, BO.B9_SPAWN[-1])
    return sorted(out)
KIMI_SEGS = _kimi_segs()

def _forward(d, t, f, level=1.0):
    if t < SWITCH:
        CPN._stack(d, t, f, 'kimi', level, SEND1, segs=KIMI_SEGS)
        return
    out = 1 - ease.prog(t, SWITCH, SWITCH + 0.15)
    if out > 0:
        CPN._stack(d, t, f, 'kimi', out, segs=KIMI_SEGS)
    CPN._stack(d, t, f, 'qwen', 1.0, SWITCH + 0.1, segs=(), load=(BOOT2, BOOT2 + 0.8))
RUN = {'input': [(GB.COMMITS1[0][0], SEND1 + 0.15), (GB.EGG_COMMITS[0][0], SEND2 + 0.15)], 'think': [(at, at + len(s) / BO.THINK_CPS + 0.2) for at, s in THINKS], 'trace': [(at, _code_end(at, s, ret)) for at, s, ret in CODE] + [(NEAR_OUT, RING_AT[-1] + 0.15)], 'generate': [(BO.CELL_AT[0], BO.CELL_AT[-1] + 0.1), (REPLY1.tok_t[0] - 0.2, REPLY1.tok_t[-1] + 0.1), (EGG.tok_t[0] - 0.2, EGG.tok_t[-1] + 0.1)], 'compare': [(S1.t0, S1.pick), (BO.HER_AT, BO.FOUND_AT[-1] + 0.1), (BO.BLANK_AT, BO.BLANK_AT + 0.3), (REPLY1.tok_t[0], PERFECT_AT + 0.1), (S2.t0, S2.pick), (BO.SURF_AT, BO.UNDER_AT[-1] + 0.1), (BO.SELECT_AT[0], BO.SELECT_AT[-1] + 0.1), (BO.DIFF_AT, BO.DIFF_AT + 0.2), (NEAR_OUT + 0.1, RING_AT[-1] + 0.1)], 'forward': KIMI_SEGS}

def _status(t):
    tok = None
    if REPLY1.tok_t[0] <= t < SHRINK4:
        tok = (REPLY1.n_tok(t), len(REPLY1.toks))
    elif EGG.tok_t[0] <= t < NEAR_OUT:
        tok = (EGG.n_tok(t), len(EGG.toks))
    s = tl.sim(t)
    scan = _scan_status(t)
    return {'generate': (f'{tok[0]}/{tok[1]} tok' if tok else '', False), 'compare': (scan, False) if scan else (f'sim(her) {s}' if s else '', True), 'forward': (speed.label('kimi' if t < SWITCH else 'qwen'), False)}

def _body(c, img, d):
    t = c.t
    L, u = layout(t)
    fold = _folding(t)
    if fold:
        _fold_under(d, t)
    _cmdline(d, t, CPN.right(t), _typed(t) if fold else None)
    hits = BO._reads(t).out
    st = _status(t)

    def gen(dd, r):
        for fn in (_gen_table, _gen_reply, _gen_egg):
            fn(dd, t, r)

    def cmp_(dd, r, layer):
        _search(dd, t, S1, r, S1.pick)
        her = _found(dd, t, r)
        _cos(dd, t, r, her)
        _search(dd, t, S2, r, S2.pick)
        _frame(layer, dd, t, r)
        _radar(dd, t, r)
    fade = {'input': 1 - u, 'think': 1 - u, 'generate': 1 - u}
    for name in ('input', 'think', 'trace', 'generate', 'compare', 'forward'):
        rect = L[name]
        level = fade.get(name, 1.0)
        if level <= 0.01:
            continue
        k = _draw_k(name, t) if fold else 1.0
        if k <= 0:
            continue
        if k < 1:
            _veil(img, rect, ease.prog(k, 0.0, 0.5))
        else:
            d.rectangle(rect, fill=BG)
        clip = panes.Clip(img, rect)
        with clip as dd:
            if name == 'input':
                if not fold or t >= FOLD_ASK[1]:
                    _input(dd, t, rect)
            elif name == 'think':
                _think(dd, t, rect)
            elif name == 'trace':
                _trace(dd, t, rect, 1 - u)
                _repl(dd, t, rect)
            elif name == 'generate':
                gen(dd, rect)
            elif name == 'compare':
                cmp_(dd, rect, clip.layer)
            else:
                _forward(dd, t, rect, ease.prog(k, 0.5, 1.0) if fold else 1.0)
        status, her = st.get(name, ('', False))
        _box(d, rect, name, t, k, panes.run_k(t, RUN[name]), level, status, her)
    m = max(hits.values(), default=0.0)
    if fold:
        _fold_strip(img, d, t, hits, min(1.0, 3 * m))
        _fold_over(d, t)
    else:
        CPN._memory(d, t, L['memory'], hits)
        panes.box(d, L['memory'], 'mem', t, min(1.0, 3 * m))
    if FOLD_ON and T0 <= t < FLASH_END:
        _fold_flash(d, t, hits)
FOLD_ON = os.environ.get('DSH_A') == 'open'
G16 = [tl.grid(T0, k, 4) for k in range(5)]
FOLD_END = G16[4]
FOLD_ASK = (T0, G16[2])
FOLD_GO = 0.2
FOLD_STEP = 0.012
DRAW = {'input': (G16[1], G16[2]), 'memory': (G16[1], G16[3]), 'think': (G16[2], G16[3]), 'trace': (G16[2], G16[3]), 'generate': (G16[2], G16[4]), 'compare': (G16[2], G16[4]), 'forward': (G16[2], G16[4])}
A_STRIP = (hud.COLR, hud.STRIP_TOP, hud.STRIP_ROOM)
B_STRIP = ((MEM[0] + 6, MEM[1] + 4, MEM[2] - 6, MEM[3] - 6), MEM[1] + 36, 340)

def _ao():
    from groups import a_open
    return a_open

def _folding(t):
    return FOLD_ON and T0 <= t < FOLD_END

def _draw_k(name, t):
    a, b = DRAW[name]
    return ease.prog(t, a, b)

def _typed(t):
    n = len(BO.CMD)
    return max(1, int(round(n * ease.prog(t, T0, FOLD_ASK[1] - 0.02))))

def _veil(img, rect, a):
    """Paper over rect at alpha a (a pane's flat ground coming up over the dot field)."""
    if a <= 0:
        return
    x0, y0, x1, y1 = (int(round(v)) for v in rect)
    box = (x0, y0, x1 + 1, y1 + 1)
    region = img.crop(box)
    img.paste(Image.blend(region, Image.new('RGB', region.size, BG), min(1.0, a)), box[:2])

def _box(d, rect, label, t, k, run=0.0, level=1.0, status='', her=False):
    """panes.box once drawn (k = 1); before that its border drawn from the top-left corner both ways round."""
    if k >= 1:
        panes.box(d, rect, label, t, run, level, status, her)
        return
    x0, y0, x1, y1 = (round(v) for v in rect)
    line = lv(INK, (panes.LINE_IDLE + (panes.LINE_RUN - panes.LINE_IDLE) * run) * level)
    hud.polyline(d, [(x0, y0), (x1, y0), (x1, y1)], line, k, 1)
    hud.polyline(d, [(x0, y0), (x0, y1), (x1, y1)], line, k, 1)
    f = P.font(panes.SIZE['label'], 'bold' if run > 0.5 else 'mono')
    tw = d.textlength(label, font=f)
    d.rectangle((x0 + 7, y0 - 1, x0 + 15 + tw, y0 + 1), fill=BG)
    d.text((x0 + 11, y0 - 7), label, font=f, fill=lv(INK, (0.55 + 0.45 * run) * level * ease.prog(k, 0.0, 0.4)))

@contextmanager
def _strip_at(v):
    """The strip between where A leaves it (v = 0) and the mem pane (v = 1)."""
    old = (hud.COLR, hud.STRIP_TOP, hud.STRIP_ROOM)
    (ca, ta, ra), (cb, tb, rb) = (A_STRIP, B_STRIP)
    hud.COLR = tuple((ease.lerp(a, b, v) for a, b in zip(ca, cb)))
    hud.STRIP_TOP, hud.STRIP_ROOM = (ease.lerp(ta, tb, v), ease.lerp(ra, rb, v))
    try:
        yield
    finally:
        hud.COLR, hud.STRIP_TOP, hud.STRIP_ROOM = old

def _strip_v(t):
    return ease.ease_io(ease.prog(t, *FOLD_ASK))

def _a_t():
    return T0 - 0.5 / P.FPS

def _fold_under(d, t):
    """What only A has goes in the first 16th: your words on the rows, the threads, the scores, the water, `user`,
    the sort command; A's idle forward strip and fine print by the 8th (the forward pane is drawn there)."""
    AO, tA = (_ao(), _a_t())
    a = 1 - ease.prog(t, T0, G16[1])
    a2 = 1 - ease.prog(t, T0, G16[2])
    if a2 > 0:
        hud.layers(d, tA, (), 'idle', level=a2)
        hud.fine_print(d, tA, level=a2)
    if a <= 0:
        return
    hud.cmdline(d, tA, GA.CMD_SORT, chip='', level=a)
    d.text((hud.X0, inspect_.Y_PROMPT + 6), 'user', font=P.font(12), fill=lv(INK, 0.7 * 0.85 * a))
    for x, y, r, aa in AO._ambient(t):
        d.ellipse((x - r, y - r, x + r, y + r), outline=lv(INK, 0.32 * aa * a))
    AO._surface(d, t, a)
    st = AO._state(tA)
    f_score = P.font(13, 'bold')
    for name in tl.HER_FILES:
        if name == AO.SWEETEST:
            continue
        row, xo = st[name]
        y = AO._row_y(row)
        cx, cy, rx, _ry = AO._center(name, tA, st)
        tw = hud.width(AO.WORDS[name], 17)
        hud.tx(d, (hud.X0 + xo, y + 1), AO.WORDS[name], 17, lv(INK, 0.95 * a))
        d.text((hud.X0 + xo, y + 22), name, font=P.font(10), fill=lv(INK, 0.45 * a))
        AO._thread(d, hud.X0 + xo + tw + 10, cx - rx - 6, cy, a)
        d.text((cx + rx + 7, cy - 8), str(AO.SCORE[name]), font=f_score, fill=lv(INK, a))

def _fold_strip(img, d, t, hits, run):
    """The strip on its way into the mem pane (B's read pulses run on it as they do), the mem pane drawn round it."""
    k = _draw_k('memory', t)
    with _strip_at(_strip_v(t)):
        hud.strip(d, t, hits)
        x0, y0, x1, _y1 = hud.COLR
    _veil(img, (x0 - 2, y0 + 4, x1 + 2, y0 + 17), ease.prog(k, 0.2, 0.6))
    if k > 0:
        _box(d, MEM, 'mem', t, k, run)

def _fold_go(name, st):
    """(start, landing) of the bubble of `name` on its way back into its block (see_you goes with its slab)."""
    s = T0 if name == _ao().SWEETEST else T0 + FOLD_STEP * st[name][0]
    return (s, s + FOLD_GO)

def _pill(d, cx, cy, rx, ry, box, g, name):
    """A's bubble <-> block morph (a_open._bubble's, run backwards), ending as the block lit (D1) with its name, so
    the landing flash takes over without a change of tone."""
    col = hud.her(1.0)
    rect = tuple((ease.lerp(a, b, g) for a, b in zip(box, (cx - rx, cy - ry, cx + rx, cy + ry))))
    rad = int(min(ease.lerp(2, max(rx, ry), g), (rect[2] - rect[0]) // 2 - 1, (rect[3] - rect[1]) // 2 - 1))
    fill = glyph.mix(col, lv(col, 0.38), g)
    d.rounded_rectangle(rect, radius=max(0, rad), fill=fill, outline=col, width=2)
    a = ease.prog(1 - g, 0.7, 1.0)
    if a > 0:
        d.text((rect[0] + 4, rect[1] + 6), name[:9], font=P.font(11), fill=glyph.mix(fill, BG, a))

def _fold_slab_go():
    return (T0, T0 + FOLD_GO + 0.04)

def _fold_land(name, st):
    land = _fold_go(name, st)[1]
    return max(land, _fold_slab_go()[1]) if name == _ao().SWEETEST else land

def _fold_over(d, t):
    """The bubbles back into their blocks (lit while they move, D1), the pinned slab into see_you, the question into
    the input pane."""
    AO, tA = (_ao(), _a_t())
    st = AO._state(tA)
    with _strip_at(_strip_v(t)):
        blocks = {name: hud.block_rect(k0, t) for k0, name in enumerate(tl.HER_FILES)}

    def bubble(name):
        cx, cy, rx, ry = AO._center(name, tA, st)
        s, e = _fold_go(name, st)
        if t < s:
            AO._bubble(d, cx, cy, rx, ry, AO._lit(name, tA), 1.0)
        elif t < e:
            _pill(d, cx, cy, rx, ry, blocks[name], 1 - ease.ease_io(ease.prog(t, s, e)), name)
    bubble(AO.SWEETEST)
    s0, s1 = _fold_slab_go()
    if t < s1:
        e = ease.ease_io(ease.prog(t, s0, s1))
        rect = tuple((ease.lerp(a, b, e) for a, b in zip(AO._row_slab(st), blocks[AO.SWEETEST])))
        col = glyph.mix(SLAB, hud.her(1.0), ease.smooth(ease.prog(e, 0.5, 1.0)))
        d.rectangle(rect, fill=col)
        a = 1 - ease.prog(t, T0, G16[1])
        if a > 0:
            d.text((rect[2] - 8, rect[3] - 16), 'pinned', font=P.font(11), fill=glyph.mix(col, BG, a), anchor='ra')
        a = ease.prog(e, 0.7, 1.0)
        if a > 0:
            d.text((rect[0] + 4, rect[1] + 6), AO.SWEETEST[:9], font=P.font(11), fill=glyph.mix(col, BG, a))
    for name in sorted(tl.HER_FILES, key=lambda n: st[n][0]):
        if name != AO.SWEETEST:
            bubble(name)
    _ask_move(d, t)

def _ask_move(d, t):
    """Your question, from the top of the sort (inspect_.prompt_chips: 22 px, placeholder ids, A's 0.85) to where
    _input draws it (20 px, the real ids)."""
    if t >= FOLD_ASK[1]:
        return
    u = ease.ease_io(ease.prog(t, *FOLD_ASK))
    v = ease.smooth(ease.prog(u, 0.35, 0.65))
    fid = P.font(10)
    xa, xb = (hud.X0 + 50, COL + 10)
    y = ease.lerp(inspect_.Y_PROMPT, 88 + 11, u)
    size = int(round(ease.lerp(22, 20, u)))
    for _at, w in GB.COMMITS1:
        twa, twb = (hud.width(w, 22, True), hud.width(w, 20, True))
        ida = str(glyph.token_id(w))
        idb = prompt_ids.text(PROMPT_IDS[w]) if w in PROMPT_IDS else ida
        x, tw = (ease.lerp(xa, xb, u), ease.lerp(twa, twb, u))
        hud.tx(d, (x, y), w, size, lv(INK, ease.lerp(0.85, TXT, u)), True)
        by = y + ease.lerp(32, 30, u)
        tick = ease.lerp(4, 3, u)
        bl = lv(INK, ease.lerp(0.85 * 0.85, 0.85, u))
        d.line([(x, by), (x + tw, by)], fill=bl)
        d.line([(x, by - tick), (x, by)], fill=bl)
        d.line([(x + tw, by - tick), (x + tw, by)], fill=bl)
        if v < 1:
            d.text((x, by + 3), ida, font=fid, fill=lv(INK, 0.55 * 0.85 * (1 - v)))
        if v > 0:
            d.text((x, by + 3), idb, font=fid, fill=lv(INK, SUB * v))
        xa += max(twa, d.textlength('00000', font=fid)) + 12
        xb += max(twb, d.textlength(idb, font=fid)) + 12

def _fold_flash(d, t, hits):
    """D1: a block lights as its bubble lands in it and settles to quiet over LIVE_FADE (past the fold's end)."""
    AO = _ao()
    st = AO._state(_a_t())
    with _strip_at(_strip_v(t)):
        for k0, name in enumerate(tl.HER_FILES):
            land = _fold_land(name, st)
            if t < land:
                continue
            u = 1 - ease.prog(t, land, land + hud.LIVE_FADE)
            if u <= 0:
                continue
            dx = 5 * hits.get(k0, 0.0)
            x0, y0, x1, y1 = hud.block_rect(k0, t)
            d.rectangle((x0 + dx, y0, x1 + dx, y1), fill=hud.her(u))
            d.text((x0 + 4 + dx, y0 + 6), name[:9], font=P.font(11), fill=BG)

def _flash_end():
    if not FOLD_ON:
        return T0
    st = _ao()._state(_a_t())
    return max((_fold_land(n, st) for n in tl.HER_FILES)) + hud.LIVE_FADE
FLASH_END = _flash_end()

def _tower_chrome(film):
    """From 75.25 the 3D tower (inside/, b9_tower) fills the terminal: it is the forward pane zoomed, so its chrome
    goes on top of the plate (install() paints the plate after the shot body)."""

    def fn(img, t):
        sp = next((s for s in getattr(film, 'inside_spans', ()) if s.name == 'b9_tower'), None)
        if sp is None or not sp.active(t) or (not T0 <= t < T1):
            return None
        a = sp.alpha(t)
        if a <= 0.01:
            return None
        d = ImageDraw.Draw(img)
        r = CPN.right(t)
        panes.box(d, (COL, 88, r, 598), 'forward', t, 1.0, a)
        panes.box(d, MEM, 'mem', t, 0.0)
        return img
    return fn

def _character_layer(film, orig):
    """r3's dsh layer from ui/pane_open_b4 (menu notes and speeds of ui/pages/b_pane.py) once it is shot."""
    b4 = P.path('ui/pane_open_b4')
    if not (b4.exists() and any(b4.iterdir())):
        return BO._character_layer(film, orig)
    real = BO.PaneFrames
    BO.PaneFrames = lambda path, *a, **k: real(b4, *a, **k)
    try:
        return BO._character_layer(film, orig)
    finally:
        BO.PaneFrames = real

def register(film):
    for name, a, b in BO.SHOTS:
        _add(film, name, a, b)
    film.character = _character_layer(film, film.character)
    full_frame(NEAR_OUT, NEAR_BACK, 0.3, 0.4)
    for dec in (REPLY1, EGG):
        hud.LIVE.extend(dec.falls())
    for seq in (BO.FOUND_AT, BO.UNDER_AT):
        for k, at in enumerate(seq):
            hud.LIVE.append((at, seq[k + 1] if k + 1 < len(seq) else at + 0.5))
    for S in (S1, S2):
        hud.LIVE.append((S.pick, S.pick + 0.3))
    if FOLD_ON:
        hud.LIVE.append((T0, FLASH_END - hud.LIVE_FADE))
    for t0, side in [(T0, 'right'), (S1.t_in, 'both'), (W(5, 0), 'left'), (W(6, 0), 'right'), (BO.BLANK_AT, 'both'), (W(7, 0), 'both'), (W(8, 0), 'right'), (S2.t_in, 'both'), (W(9, 0), 'left'), (W(11, 0), 'both'), (W(12, 0), 'right'), (NEAR_OUT, 'both'), (NEAR_BACK, 'right')]:
        film.set_lead(t0, side)
    film.finish.append(_tower_chrome(film))

def _add(film, name, t0, t1):

    def fn(c):
        img = film.background(c.t)
        d = ImageDraw.Draw(img)
        hud.frame(d, hud.left_rect(c.t), 'you@surface · dsh inspect')
        _body(c, img, d)
        c.img.paste(img)
    film.add(name, t0, t1, fn, chapter=tl.chapter(t0))
