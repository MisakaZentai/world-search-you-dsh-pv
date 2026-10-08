"""Group B, batch 3 "who leads" (sample_lead/README.md, sample_batch3/README.md, ASTRA_20261003.md #1):
groups/b_pane.py copied, then changed. The trial did 40.86-58.08; batch 3 rolls it out over all of B (b6-b9 too).

The rules (sample_batch3/README.md §1):
  - every beat one pane leads: bright paper, full ink, its spinner turning; the others sit in shade as a block
    (lead.shade: ground and ink alike go toward one darker paper tone). Frames and labels are drawn after the shade,
    places and sizes of the panes stay as they were. The lead table is LEAD below: per shot, what the viewer waits
    for, then the pane that answers it.
  - one sentence at full ink in one place at a time (the copy is the exception: her line and its copy side by side).
    The dsh window counts as a pane ("dsh" in LEAD: every pane in shade); the film's LEAD (register) gives it the lead
    when it sends: the answer ("for", 53.505), the model menu (68.15), Qwen picked (73.53).
  - no event moves after 58.08 (the dsh shots of ui/pane_open_b4 stay); only who leads, shade, size and ink change.
  - the tower (75.25-82.13) is the forward pane zoomed and leads; as it goes the shade lifts (82.13-82.56), so B
    hands C an unshaded terminal.
  - what the viewer should see: it copies her. The strongest move is her old sentence going into the new answer:
    a copy of her line rises out of compare into generate ("by"), 一根茄子 drops out of it ("leg"), the template
    waits as a stencil, Kimi inks it chunk by chunk ("You're the"), stops at the blank, takes 桌子 out of your
    question ("per-fect") and drops it in on "table" (52.92); the row closes up and its own 哦 replaces the
    eggplant ("-ble"); <eos> and dsh gets it ("for"). cos 0.97 is the aftermath, on "me", smaller.
  - the dsh layer is r4's shots (ui/pane_open_b4) re-timed: its four chunks arrive when they land on the left
    (_dsh_t). Nothing is re-shot.

The lead table (pane, from): LEAD below; film.set_lead in register(). Switch: DSH_B=lead (film.py).

r5 round 2, batch 2-B (D35, sample_r5/README.md §4; 40.86-68.15 only, b9 and LEAD from 68.15 untouched, the names
the interlude patches -- RING_AT, LEAD, RUN, _radar, _repl -- unchanged; r5a's file is sample_r5/b2/src_before/):
  R-C  桌子 boxed at its own token (一张 | 桌子 open at 103948 | 112378 on "per", the box's bottom is its token rule);
       the blank sized for 桌子, 了 closing up to it on "makes"; the copy of 桌子 slides out of its box, runs along the
       top of the trace pane (`tpl.fill(你[3])` scrolls the long line away) and comes down clear of the trace lines;
       borders it passes open for it (_door); the copy of her line rises out of her line and the question row gives
       way; the grid and the ranked list give way to the question and her line; the second search leaves on 58.08;
       the markdown table drawn rendered (one rule a column); cos outlines a run, not a cell; scrolled-out lines gone
       before the top border.
  P4   compare's pixel table (_ptable): height 45.74, elbow line 46.745, a short leg 48.90, wob-bly 50.14 / 50.58;
       the scratches on film 1's frame (_scratches): nail 61.94, marks 62.32, body 63.86, a glint running on pad().
  P1   hand-overs of b1-b8 centred on their event (_lead_table).

What follows is b_pane's docstring (r4):

Group B, second sample r4 (sample_open_b/README.md §11): r3's content (groups/b_open.py) laid out in the named
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
import lead
import panes
import prompt_ids
import speed
import syl
import tl
from inspect_ import Decoder, Tok
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
L5, L6, L7 = (syl.times(5), syl.times(6), syl.times(7))
COPY_AT = BO.BLANK_AT
HOLLOW_AT = L6[3]
WOB = (L6[6], L6[7])
PICK_AT = L7[4]
FILL_AT = L7[6]
TIGHT_AT = L7[7]
SENT_AT = L7[8]
COS_AT = L7[9]
ASK2_AT = GB.EGG_COMMITS[0][0]
TOWER_OUT = tl.bar(47)
RELEASE = (TOWER_OUT, tl.next_beat(TOWER_OUT))
REPLY_L = Decoder.on([Tok('好呀！现在', 'archive', syl=1), Tok('我是', 'archive', syl=1), Tok('桌子', 'self', syl=1), Tok('了', 'archive', syl=1), Tok('哦', 'self', syl=1)], at=[L7[0], L7[1], FILL_AT, TIGHT_AT, TIGHT_AT], chunk=True, start=W(7, 0) - 0.3)
LIT_HOLD = 0.25

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

def _bracket(d, x0, x1, by, colr):
    d.line([(x0, by), (x1, by)], fill=colr)
    d.line([(x0, by - 3), (x0, by)], fill=colr)
    d.line([(x1, by - 3), (x1, by)], fill=colr)

def _input(d, t, r):
    commits, send = TURNS[1] if t >= GB.EGG_COMMITS[0][0] else TURNS[0]
    sent = t >= send
    fid = P.font(10)
    x, y = (r[0] + 10, r[1] + 11)
    su = _split_u(t)
    for at, w in commits:
        if at > t:
            break
        tw = hud.width(w, 20, True)
        drop = (1 - ease.ease_out(ease.prog(t, at, at + 0.12))) * -5
        by = y + 30
        bl = lv(INK, 0.85 if sent else 0.45)
        ids = prompt_ids.text(PROMPT_IDS[w]) if w in PROMPT_IDS else str(glyph.token_id(w))
        if w == TAKE_W and su > 0 and (commits is TURNS[0][0]):
            x = _input_split(d, t, x, y, by, bl, fid, su)
            continue
        hud.tx(d, (x, y + drop), w, 20, lv(INK, TXT), True)
        _bracket(d, x, x + tw, by, bl)
        d.text((x, by + 3), ids, font=fid, fill=lv(INK, SUB))
        x += max(tw, d.textlength(ids, font=fid)) + 12
TAKE_W = '一张桌子'
SPLIT_GAP = 10
BOX_IN = 4

def _split_u(t):
    """0..1: the commit opens at its token boundary, landing on "per" (52.04); first turn only."""
    if t >= ASK2_AT:
        return 0.0
    return ease.smooth(ease.prog(t, PICK_AT - 0.16, PICK_AT))

def _box_k(t):
    """0..1: the box around 桌子 (drawn over the panes by _take); 桌子's token rule follows it."""
    return ease.ease_out(ease.prog(t, PICK_AT, PICK_AT + 0.1)) * (1 - ease.prog(t, FILL_AT, FILL_AT + 0.4))

def _id_duck(t):
    """112378 gives way while the copy of 桌子 slides out of the box over it (the first leg of the flight)."""
    return ease.prog(t, FLY[0], FLY[0] + 0.04) * (1 - ease.prog(t, FLY_S1, FLY_S1 + 0.08))

def _input_split(d, t, x, y, by, bl, fid, su):
    """一张桌子 drawn as its two tokens, SPLIT_GAP * su apart; returns the x after it."""
    i1, i2 = (str(v) for v in PROMPT_IDS[TAKE_W])
    w1, w2 = (hud.width('一张', 20, True), hud.width('桌子', 20, True))
    x2 = x + w1 + SPLIT_GAP * su
    hud.tx(d, (x, y), '一张', 20, lv(INK, TXT), True)
    hud.tx(d, (x2, y), '桌子', 20, lv(INK, TXT), True)
    _bracket(d, x, x + w1, by, bl)
    bk = _box_k(t)
    _bracket(d, x2 - BOX_IN * bk, x2 + w2 - 1 + BOX_IN * bk + (1 - bk), by, bl)
    d.text((x, by + 3), i1, font=fid, fill=lv(INK, SUB))
    x_i2 = ease.lerp(x + d.textlength(i1 + '·', font=fid), x2, su)
    if su < 1:
        d.text((x + d.textlength(i1, font=fid), by + 3), '·', font=fid, fill=lv(INK, SUB * (1 - su)))
    d.text((x_i2, by + 3), i2, font=fid, fill=lv(INK, SUB * (1 - _id_duck(t))))
    return x2 + max(w2, d.textlength(i2, font=fid)) + 12
THINKS = BO.THINK1 + BO.THINK2

def _off_top(t, y, r):
    """r5 2-B (R-C): a line scrolling out over the top of its pane is gone before its ink (y + 2) gets within 3 px
    of the pane's top border (r5a faded it over the scroll and let it run under the border). Up to 68.15 only."""
    if t >= W(12, 0):
        return 1.0
    return ease.clamp((y + 2 - (r[1] + BOX_IN)) / 8)

def _think(d, t, r):
    if t >= SWITCH:
        return
    shown = [(at, s) for at, s in THINKS if at <= t]
    if not shown:
        return
    last = shown[-1][0]
    sc = ease.ease_out(ease.prog(t, last, last + 0.14))
    leads = _leads_now('think', t)
    for pos, (at, s) in enumerate(reversed(shown[-3:])):
        n = int((t - at) * BO.THINK_CPS) + 1
        a = {0: TXT, 1: SUB}.get(pos, SUB * (1 - sc))
        if pos == 0:
            a *= ease.prog(t, at, at + 0.1)
        y = r[1] + 30 - pos * 19 + (1 - sc) * 19
        if pos >= 2:
            a *= _off_top(t, y, r)
        if a > 0.01:
            mtx(d, (r[0] + 10, y), s[:n], 13, lv(INK, a), bold=leads and pos == 0)
COS_LINE = 7
CODE = [(SENT_AT, s, (COS_AT, BO.SIM1)) if i == COS_LINE else (at, s, BO.RET.get(i)) for i, (at, kind, s) in enumerate(BO.TRACE) if kind == 'code']
CODE += [(SWITCH, 'dsh.use("Qwen3.8-27B")', (SWITCH + 0.2, '本地')), (BOOT2, 'llama.load("27B · Q4_K_M")', (BOOT2 + 0.8, 'ok'))]
FILL_CODE = 'tpl.fill(你[3])'
CODE = sorted(CODE + [(PICK_AT, FILL_CODE, None)], key=lambda c: c[0])

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
        if pos >= 3:
            a *= _off_top(t, y, r)
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
TBAR = 3

def _gen_table(d, t, g):
    """b3: its habit, a markdown table, a cell a syllable (dsh shows the same). Batch 3: background, faint ink."""
    if t < BO.CELL_AT[0] or t >= S2.t_in:
        return
    a = (1 - (1 - SUB) * ease.prog(t, SHRINK4, SHRINK4 + 0.35)) * (1 - ease.prog(t, S2.t_in - 0.3, S2.t_in))
    x0, y0 = (g[0] + 14, g[1] + 12)
    vx = [x0 + c + TBAR for c in TCOLS] + [x0 + 252 + TBAR]
    rows = [TABLE[0], None, TABLE[1], TABLE[2]]
    for ri, row in enumerate(rows):
        src = 0 if ri < 2 else ri - 1
        y = y0 + ri * 18
        for ci in range(3):
            at = BO.CELL_AT[src * 3 + ci]
            if t < at:
                continue
            u = ease.prog(t, at, at + 0.1) * a
            col = lv(INK, FAINT * u)
            d.line([(vx[ci], y - 1), (vx[ci], y + 17)], fill=col)
            if row is None:
                d.line([(vx[ci], y + 8), (vx[ci + 1], y + 8)], fill=col)
            else:
                mtx(d, (x0 + TCOLS[ci] + 12, y), row[ci], 13, col)
        if t >= BO.CELL_AT[src * 3 + 2]:
            d.line([(vx[3], y - 1), (vx[3], y + 17)], fill=lv(INK, FAINT * a))
TS = CPN.OUT
TPL_X = CPN.LX
TPL_DY = 90
GAP = (7, 10)
EGG_I, LE_I = (12, 11)

def _tpl_slots():
    """[(x, w)] of her characters in generate's row (30 px), before the row closes up."""
    out, x = ([], TPL_X)
    for ch in BO.HER_CH:
        w = BO._slot_w(ch, TS)
        out.append((x, w))
        x += w
    return out
TPL = _tpl_slots()
ZW = hud.width('桌子', TS, True)
GAP_X0, GAP_X1 = (TPL[GAP[0]][0], TPL[GAP[1]][0] + TPL[GAP[1]][1])
SHUT = GAP_X1 - GAP_X0 - ZW
BLANK_PAD = 8
BW = ZW + 2 * BLANK_PAD
CLOSE = GAP_X1 - GAP_X0 - BW
SHUT2 = SHUT - CLOSE
CLOSE_AT = L6[4]
BLANK_C = GAP_X0 + BW / 2

def _close(t):
    return ease.smooth(ease.prog(t, CLOSE_AT - 0.3, CLOSE_AT))

def _tight(t):
    return ease.ease_io(ease.prog(t, TIGHT_AT, TIGHT_AT + 0.12))

def _shut(t):
    return CLOSE * _close(t) + SHUT2 * _tight(t)

def _zz_x(t):
    """桌子 in the blank: BLANK_PAD in from 是 until the row closes up, then where 一根 began."""
    return GAP_X0 + BLANK_PAD * (1 - _tight(t))
WAIT_STEPS = [s for s in list(L6) + list(L7[:6]) if s > HOLLOW_AT]

def _tilt(t, x):
    """"wob-bly": the template with a gap in it tips about the gap, one way on "wob", the other on "-bly"."""
    dy = 0.0
    for k, at in enumerate(WOB):
        u = ease.prog(t, at, at + 0.3)
        if 0 < u < 1:
            dy += (5 if k == 0 else -5) * math.sin(math.pi * u) * (x - BLANK_C) / 160
    return dy

def _stencil(d, xy, ch, size, colr):
    """A character as a 1-dot outline (her template: not said yet)."""
    d.text(xy, ch, font=hud.font(size, ch, True), fill=BG, stroke_width=1, stroke_fill=colr)

def _lit(at, t):
    return 1.0 if t < at + LIT_HOLD else 1 - ease.prog(t, at + LIT_HOLD, at + LIT_HOLD + hud.LIVE_FADE)

def _said_at(k):
    """When character k of her line is said by it (chunk times of REPLY_L); None: never (一根茄子, the eggplant)."""
    if k <= 4:
        return REPLY_L.tok_t[0]
    if k <= 6:
        return REPLY_L.tok_t[1]
    if k == LE_I:
        return REPLY_L.tok_t[3]
    return None

def _gen_tpl(d, t, g):
    """b3-b4: her line (copied up from compare) as a stencil with a blank; Kimi inks it chunk by chunk, 桌子 drops
    into the blank on "table", the row closes up and its own 哦 takes the eggplant's place; <eos> -> dsh on "for"."""
    if t < HOLLOW_AT or t >= NEAR_OUT:
        return
    a = (1 - (1 - SUB) * ease.prog(t, SHRINK4, SHRINK4 + 0.35)) * (1 - (1 - FAINT / SUB) * ease.prog(t, EGG.tok_t[0], EGG.tok_t[0] + 0.2)) * (1 - ease.smooth(ease.prog(t, NEAR_OUT - 0.2, NEAR_OUT)))
    y = g[1] + TPL_DY
    lab_o = ease.prog(t, REPLY_L.tok_t[0], REPLY_L.tok_t[0] + 0.15)
    mtx(d, (g[0] + 10, y + 10), 'tpl', 12, lv(INK, SUB * a * (1 - lab_o) * ease.prog(t, HOLLOW_AT, HOLLOW_AT + 0.2)))
    if lab_o > 0:
        mtx(d, (g[0] + 10, y + 10), 'out', 12, lv(INK, SUB * a * lab_o))
    shut = _shut(t)
    solid = 1 - ease.prog(t, HOLLOW_AT, HOLLOW_AT + 0.25)
    for k, ch in enumerate(BO.HER_CH):
        x, w = TPL[k]
        if k > GAP[1]:
            x -= shut
        yy = y + _tilt(t, x + w / 2)
        if GAP[0] <= k <= GAP[1] or k == EGG_I:
            drop = ease.ease_out(ease.prog(t, HOLLOW_AT, HOLLOW_AT + 0.22))
            gone = 1.0 if k != EGG_I else 1 - ease.prog(t, TIGHT_AT, TIGHT_AT + 0.1)
            if k == EGG_I:
                if gone > 0:
                    GB.eggplant(d, x + 3, yy + TS * 0.05, max(2, int(TS / 9)), 0.0, a * gone * ease.lerp(1.0, FAINT, 1 - solid))
                continue
            if drop < 1:
                hud.tx(d, (x, yy - TS * 0.1 + 12 * drop), ch, TS, lv(hud.her(1.0), a * (1 - drop)), bold=True)
            continue
        said = _said_at(k)
        xy = (x, yy - TS * 0.1)
        if said is not None and t >= said:
            drop_s = (1 - ease.ease_out(ease.prog(t, said, said + 0.14))) * -6
            hud.tx(d, (x, yy - TS * 0.1 + drop_s), ch, TS, lv(hud.her(_lit(said, t)), a), bold=True)
        else:
            _stencil(d, xy, ch, TS, lv(HER_QUIET, a))
            if solid > 0:
                hud.tx(d, xy, ch, TS, lv(hud.her(1.0), a * solid), bold=True)
    box = _close(t) * _blank_open(t, y + 1)
    if box > 0:
        step = sum((1 for s in WAIT_STEPS if t >= s))
        bx0, bx1 = (GAP_X0 + BOX_IN - 1, GAP_X0 + BW - BOX_IN + 1)
        tl_, tr_ = (y + _tilt(t, bx0), y + _tilt(t, bx1))
        _dashed_box(d, bx0, min(tl_, tr_) + 1, bx1, max(tl_, tr_) + 37, lv(HER_QUIET, box * a), step * 3)
    if t >= FILL_AT:
        bump = 1.0 + 0.14 * (1 - ease.prog(t, FILL_AT, FILL_AT + 0.16))
        sz = int(round(TS * bump))
        zx = _zz_x(t) - (hud.width('桌子', sz, True) - ZW) / 2
        hud.tx(d, (zx, y - sz * 0.1 - (sz - TS) / 2), '桌子', sz, lv(INK, a), bold=True)
    if t >= TIGHT_AT:
        x = TPL[EGG_I][0] - shut
        drop_s = (1 - ease.ease_out(ease.prog(t, TIGHT_AT, TIGHT_AT + 0.14))) * -6
        hud.tx(d, (x, y - TS * 0.1 + drop_s), '哦', TS, lv(INK, a), bold=True)
    if t >= SENT_AT:
        ex = TPL[EGG_I][0] - shut + hud.width('哦', TS, True) + 12
        CPN._eos(d, t, ex, y + 6, SENT_AT, a)
        u = ease.prog(t, SENT_AT + 0.05, SENT_AT + 0.2) * a
        mtx(d, (ex + 62, y + 9), '→ dsh · 23:46', 13, lv(INK, SUB * u))

def _blank_open(t, top):
    """1 while the blank waits; it opens (fades) as the copy of 桌子 comes down to it, gone before the copy's ink is
    within 3 px of its top edge (R-C)."""
    if t < FLY_S1:
        return 1.0
    if t >= FILL_AT:
        return 0.0
    _x, y, sz = _fly_at(t)
    return 1 - ease.clamp((y + sz * 1.21 - (top - 18)) / 14)

def _dashed_box(d, x0, y0, x1, y1, colr, off=0):
    for xx in range(int(x0) - 6 + off % 9, int(x1), 9):
        a_, b_ = (max(xx, x0), min(xx + 5, x1))
        if a_ < b_:
            d.line([(a_, y0), (b_, y0)], fill=colr)
            d.line([(a_, y1), (b_, y1)], fill=colr)
    for yy in range(int(y0), int(y1), 7):
        b_ = min(yy + 4, y1)
        d.line([(x0, yy), (x0, b_)], fill=colr)
        d.line([(x1, yy), (x1, b_)], fill=colr)

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

def _q_fly_x(t, c):
    """x of the question as it flies up out of the ranked list (_found); None before the first search's pick."""
    if t < S1.pick:
        return None
    return ease.lerp(LX0, c[0] + 10, ease.ease_io(ease.prog(t, S1.pick, S1.pick + 0.3)))

def _grid(d, t, S, c, level):
    gx, gy = (c[0] + 10, c[1] + 14)
    done = S.rows_done(t)
    qx = _q_fly_x(t, c) if S is S1 else None
    lim = 1000000000.0 if qx is None else qx - BOX_IN
    if S is S1 and t >= BO.HER_AT:
        lim = -1000000000.0
    for i in range(BO.ARCH_N):
        rr, cc = divmod(i, BO.COLS)
        ap = ease.prog(t, S.t_in + rr * 0.018, S.t_in + rr * 0.018 + 0.1) * level
        if ap <= 0:
            continue
        x, y = (gx + cc * GP, gy + rr * GP)
        if x + GC - 1 > lim:
            continue
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
        if x + GC - 1 + g <= lim:
            d.rectangle((x - g, y - g, x + GC - 1 + g, y + GC - 1 + g), outline=lv(INK, level))
    if t >= S.pick:
        rr, cc = divmod(S.top[0][0] + 1, BO.COLS)
        x, y = (gx + cc * GP, gy + rr * GP)
        lit = 1 - ease.prog(t, S.pick + 0.3, S.pick + 0.3 + hud.LIVE_FADE)
        if x + GC <= lim:
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

def _search(d, t, S, c, t_out, fade=0.3):
    """fade = 0: the search is gone on t_out (r5 2-B: the second one, 58.08, leaves on the syllable so that film 1's
    frame and its label come up in an empty pane instead of over the ranked list)."""
    if t < S.t_in or t >= t_out + fade:
        return
    a = 1 - ease.prog(t, t_out, t_out + fade) if fade > 0 else 1.0
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
    """b2-b4: the question flies up from the list, her answer (archive[74]) under it a segment a syllable.
    Batch 3: it stays where it was found, whole (the template is a copy that leaves for generate); no fold."""
    if t < S1.pick or t >= SHRINK4 + 0.4:
        return None
    out = 1 - ease.prog(t, SHRINK4, SHRINK4 + 0.3)
    fu = 0.0
    i, s, q = S1.top[0]
    qa = out
    if qa > 0.01:
        u = ease.ease_io(ease.prog(t, S1.pick, S1.pick + 0.3))
        y = ease.lerp(c[1] + 16, c[1] + Y_Q, u)
        x = ease.lerp(LX0, c[0] + 10, u)
        hud.tx(d, (x, y + 2), f'{i:04d}', 12, lv(INK, SUB * qa))
        if COPY_AT <= t < HOLLOW_AT:
            xc = x + 42
            for ch in '你  ' + q:
                wc = mw(ch, 15)
                gw = _give_way(t, (xc, y + 2, xc + wc, y + 16)) if ch.strip() else 1.0
                if gw < 1:
                    mtx(d, (xc, y), ch, 15, lv(INK, 0.85 * qa * (1 - gw)))
                xc += wc
        else:
            mtx(d, (x + 42, y), '你  ' + q, 15, lv(INK, 0.85 * qa))
    if t < BO.HER_AT:
        return None
    ha = ease.prog(t, BO.HER_AT, BO.HER_AT + 0.12) * out
    y_lab = c[1] + ease.lerp(Y_HER2 + 6, Y_HER1 + 3, fu)
    if fu < 1:
        hud.tx(d, (c[0] + 10, y_lab + 2), f'{i + 1:04d}', 12, lv(HER_QUIET, SUB * ha * (1 - fu)))
    mtx(d, (c[0] + 10 + 42 * (1 - fu), y_lab), '她', 14 + 2 * fu, lv(HER_QUIET, ha), bold=fu > 0.5)
    blank = 0.0
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
EY = (80, 96, 112)
EP = 11
SWEEP_L = (SENT_AT, COS_AT)
COS_BIG = 28

def _cos(d, t, c, her):
    """b4 aftermath (batch 3): once its answer is sent, her line and its answer are embedded, multiplied cell by
    cell; the sum runs to 0.97 on "me", one size down. Its answer is not written here again (it is in generate)."""
    if t < SWEEP_L[0] or t >= SHRINK4 + 0.4 or her is None:
        return
    out = 1 - ease.prog(t, SHRINK4, SHRINK4 + 0.3)
    ae = ease.prog(t, SWEEP_L[0], SWEEP_L[0] + 0.12) * out
    ex = CPN.LX
    for j, lab in enumerate(('她', 'kimi', '×')):
        mtx(d, (c[0] + 10, c[1] + EY[j] - 1), lab, 11, lv(HER_QUIET if j == 0 else INK, SUB * ae))
    sw = ease.clamp((t - SWEEP_L[0]) / (SWEEP_L[1] - SWEEP_L[0]))
    swept = int(sw * BO.EMB_N + 1e-06)
    mis = [i for dims in BO.DIFF_DIMS for i in dims]
    for run in _runs_of(sorted(mis)):
        x0r, x1r = (ex + run[0] * EP, ex + run[-1] * EP)
        y1r = c[1] + EY[1]
        d.rectangle((x0r - 2, y1r - 2, x1r + EP - 1, y1r + 13), outline=lv(INK, out * ae))
    for i in range(BO.EMB_N):
        x = ex + i * EP
        _cell(d, x, c[1] + EY[0], BO.EMB_H[i], ae)
        _cell(d, x, c[1] + EY[1], BO.EMB_K[i], ae)
        y = c[1] + EY[2]
        if i < swept:
            p = BO.EMB_H[i] * BO.EMB_K[i]
            if p >= 0:
                d.rectangle((x, y, x + EP - 3, y + 11), fill=lv(INK, (0.15 + 0.85 * p) * ae))
            else:
                d.rectangle((x, y, x + EP - 3, y + 11), outline=lv(INK, ae))
        else:
            d.rectangle((x, y, x + EP - 3, y + 11), outline=lv(INK, 0.2 * ae))
    if SWEEP_L[0] <= t < SWEEP_L[1]:
        x = ex + sw * BO.EMB_N * EP
        d.rectangle((x - 1, c[1] + EY[0] - 3, x, c[1] + EY[2] + 14), fill=lv(INK, out))
    f = 'cos(她, kimi) ='
    mtx(d, (c[2] - 14 - mw(f, 18, True), c[1] + 12), f, 18, lv(INK, ae), bold=True)
    val = BO._cos(BO.EMB_H, BO.EMB_K, swept) if swept else 0.0
    if t < COS_AT:
        hud.tx(d, (c[2] - 14, c[1] + 44), f'{val:.2f}', 22, lv(INK, ae), True, anchor='ra')
        return
    grow = ease.ease_out(ease.prog(t, COS_AT, COS_AT + 0.12))
    bump = 1.0 + 0.1 * (1 - ease.prog(t, COS_AT, COS_AT + 0.14))
    big_word(d, BO.SIM1, (c[2] - 14, c[1] + 42), int(ease.lerp(16, COS_BIG, grow)), lv(INK, out), 'ra', bump=bump)
from inside import e5_sprites as _E5
PX = 5
PT_PAD = 12
PT_AT = L5[2]
PH_AT = L5[4]
PE_AT = L5[7]
PE_OUT = TIGHT_AT
PL_AT = HOLLOW_AT
P_TIPS = [(WOB[0], 2), (WOB[1], -2), (L7[0], 0)]

def _pt_rows():
    rows = [r.replace('B', '.') for r in _E5.SPRITES['table_2'][0]]
    full = rows[:13] + ['.KDK........KDK.', '.KDK........KDK.', '.KKK........KKK.']
    one = rows[:13] + ['.KDK........KDK.', '.KDK........KKK.', '.KKK............']
    return (full, one, rows)
PT_ROWS = _pt_rows()

def _pt_geo(c):
    """(x, y) of the sprite's top-left, the floor's y: the sprite stands right of her line, under where cos goes."""
    return (COL + 435, c[1] + 56, c[1] + 136)

def _ptable(d, t, c, layer):
    if t < PT_AT - 0.2 or t >= SHRINK4 + 0.4:
        return
    out = 1 - ease.prog(t, SHRINK4, SHRINK4 + 0.3)
    a = ease.smooth(ease.prog(t, PT_AT - 0.2, PT_AT)) * out
    if a <= 0.01:
        return
    x0, y0, floor = _pt_geo(c)
    y0 -= int(round(8 * (1 - ease.smooth(ease.prog(t, PT_AT - 0.2, PT_AT)))))
    short = int(round(2 * ease.smooth(ease.prog(t, PL_AT - 0.16, PL_AT))))
    rows = PT_ROWS[short]
    s, prev = (0.0, 0)
    for at, tgt in P_TIPS:
        s = prev + (tgt - prev) * ease.smooth(ease.prog(t, at - 0.12, at))
        if t < at:
            break
        prev = tgt
    pal = {'K': lv(INK, TXT * a), 'W': lv(INK, FAINT * a), 'D': lv(INK, SUB * a)}
    d.line([(x0 - 6, floor), (x0 + 16 * PX + 2, floor)], fill=lv(INK, FAINT * a))
    spr = Image.new('RGBA', (16 * PX + 2 * PT_PAD, 16 * PX + 2 * PT_PAD), (0, 0, 0, 0))
    sd = ImageDraw.Draw(spr)
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch != '.':
                xx, yy = (PT_PAD + i * PX, PT_PAD + j * PX)
                sd.rectangle((xx, yy, xx + PX - 1, yy + PX - 1), fill=pal[ch] + (255,))
    if abs(s) > 0.02:
        ang = -math.degrees(math.atan2(s * PX, 11 * PX))
        pivot = (PT_PAD + 2.5 * PX, PT_PAD + 16 * PX)
        spr = spr.rotate(ang, resample=Image.NEAREST, center=pivot)
    layer.paste(spr, (x0 - PT_PAD, y0 - PT_PAD), spr)
    top = y0 + 3 * PX
    rx = x0 + 16 * PX + 6
    hu = ease.smooth(ease.prog(t, PH_AT - 0.25, PH_AT))
    if hu > 0:
        ya = floor - (floor - top) * hu
        colr = lv(INK, SUB * a)
        d.line([(rx, ya), (rx, floor)], fill=colr)
        d.line([(rx - 3, floor), (rx + 3, floor)], fill=colr)
        if hu >= 1:
            d.line([(rx - 3, top), (rx + 3, top)], fill=colr)
        if t >= PH_AT:
            mtx(d, (rx + 7, (top + floor) / 2 - 7), '72 cm', 12, lv(INK, SUB * a * ease.prog(t, PH_AT, PH_AT + 0.1)))
    eu = ease.smooth(ease.prog(t, PE_AT - 0.25, PE_AT)) * (1 - ease.prog(t, PE_OUT, PE_OUT + 0.12))
    if eu > 0:
        x_end = rx + 6 + 60 * ease.smooth(ease.prog(t, PE_AT - 0.25, PE_AT))
        step = sum((1 for st in WAIT_STEPS + list(L5) if PE_AT < st <= t))
        colr = lv(INK, SUB * a * eu)
        for xx in range(int(rx + 6) - 9 + step * 3 % 9, int(x_end), 9):
            xa, xb = (max(xx, rx + 6), min(xx + 5, x_end))
            if xa < xb:
                d.line([(xa, top), (xb, top)], fill=colr)
        if t >= PE_AT:
            mtx(d, (x_end + 5, top - 7), 'elbow', 12, lv(INK, SUB * a * eu * ease.prog(t, PE_AT, PE_AT + 0.1)))

def _runs_of(idx):
    out = []
    for i in idx:
        if out and i == out[-1][-1] + 1:
            out[-1].append(i)
        else:
            out.append([i])
    return out

def _cell(d, x, y, v, level, outline=None):
    d.rectangle((x, y, x + EP - 3, y + 11), fill=lv(INK, (0.06 + 0.84 * (v + 1) / 2) * level))
    if outline:
        d.rectangle((x - 2, y - 2, x + EP - 1, y + 13), outline=outline)
FS = 0.76
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
    if t < BO.SURF_AT or t >= NEAR_OUT:
        return
    out = 1 - ease.prog(t, NEAR_OUT - 0.12, NEAR_OUT)
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
        d.rectangle((x0, y1 + 2, x0 + (x1 - x0) * w, y1 + 2), fill=lv(hud.her(lit), out))
    for k, at in enumerate(BO.SELECT_AT):
        if t < at:
            break
        x0, y0, x1, y1 = _seg_box(c, k)
        w = ease.ease_out(ease.prog(t, at, at + 0.1))
        _sel_mark(d, t, c, k, w, out)
    if t >= BO.SELECT_AT[0]:
        mtx(d, (xr, c[1] + 36), '→ context', 13, lv(INK, SUB * out * ease.prog(t, BO.SELECT_AT[0], BO.SELECT_AT[0] + 0.15)))
    _scratches(img, t, c, out)
    if t < BO.DIFF_AT:
        return
    k = ease.ease_out(ease.prog(t, BO.DIFF_AT, BO.DIFF_AT + 0.15)) * out
    y_h, y_k, size = (c[1] + 66, c[1] + 98, 20)
    mtx(d, (xr, y_h + 3), '她', 14, lv(HER_QUIET, k), bold=True)
    mtx(d, (xr, y_k + 3), 'kimi', 14, lv(INK, k), bold=True)
    _diff_rows(d, c, xr, y_h, y_k, size, k)
SEL_GAP = 3
DIFF_GAP = 8

def _sel_mark(d, t, c, k, w, out):
    x0, y0, x1, _y1 = _seg_box(c, k)
    a, b = (x0 + 1 + SEL_GAP / 2, x1 - 1 - SEL_GAP / 2)
    y = int(y0) - 2
    colr = lv(HER_QUIET, out)
    if k == 3 and t >= BO.DIFF_AT:
        colr = glyph.mix(colr, BG, ease.ease_out(ease.prog(t, BO.DIFF_AT, BO.DIFF_AT + 0.15)))
    d.line([(a, y), (a + (b - a) * w, y)], fill=colr)

def _diff_rows(d, c, xr, y_h, y_k, size, k):
    """her line over its recital; 一根 boxed in her row, a dashed gap in its row; both rows open DIFF_GAP round it."""
    text = '好呀！现在我是一根茄子了'
    x, slots = (xr + 52, [])
    for j, ch in enumerate(text):
        if j in (7, 9):
            x += DIFF_GAP
        slots.append(x)
        hud.tx(d, (x, y_h - size * 0.1), ch, size, lv(HER_QUIET, k), True)
        x += hud.width(ch, size, True)
    for j, ch in enumerate(text):
        if j not in (7, 8):
            hud.tx(d, (slots[j], y_k - size * 0.1), ch, size, lv(INK, k), True)
    a0 = slots[7] - BOX_IN
    a1 = slots[8] + hud.width('根', size, True) - 1 + BOX_IN
    top = y_h - size * 0.1 + size * 0.25 - BOX_IN
    bot = y_h - size * 0.1 + size * 1.25 + BOX_IN
    d.rectangle((a0, int(top), a1, int(math.ceil(bot))), outline=lv(INK, k))
    for xx in range(int(a0 + 3), int(a1 - 3), 8):
        d.line([(xx, y_k + size + 3), (min(xx + 4, a1 - 3), y_k + size + 3)], fill=lv(INK, SUB * k))
SCRATCH = [(BO.SELECT_AT[1], 1), (BO.SELECT_AT[2], 2), (BO.SELECT_AT[5], 5)]
SCR_OUT = (EGG.tok_t[0], EGG.tok_t[1])
SCR_DRAW = 0.1

def _line_px(x0, y0, x1, y1):
    """The pixels of a 1 px line, from (x0, y0) to (x1, y1) (Bresenham)."""
    x0, y0, x1, y1 = (int(round(v)) for v in (x0, y0, x1, y1))
    dx, dy = (abs(x1 - x0), -abs(y1 - y0))
    sx, sy = (1 if x0 < x1 else -1, 1 if y0 < y1 else -1)
    err, out = (dx + dy, [])
    while True:
        out.append((x0, y0))
        if x0 == x1 and y0 == y1:
            return out
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy

def _glint_at(t, at):
    """Distance a glint has run along a scratch since it landed: speed follows beatmap.pad (the chords)."""
    import beatmap as BM
    s, tt = (0.0, at)
    while tt < t:
        h = min(1 / 24, t - tt)
        s += h * (24 + 70 * BM.pad(tt))
        tt += h
    return s

def _scratches(img, t, c, level):
    if not SCRATCH[0][0] - SCR_DRAW <= t < SCR_OUT[1]:
        return
    keep = (1 - ease.prog(t, *SCR_OUT)) * level
    for at, k in SCRATCH:
        if t < at - SCR_DRAW:
            break
        x0, y0, x1, y1 = _seg_box(c, k)
        pts = _line_px(x1 + 3, y0 - 8, x0 - 1, y1 - 1)
        n = int(math.ceil(len(pts) * ease.smooth(ease.prog(t, at - SCR_DRAW, at))))
        g = _glint_at(t, at) % (len(pts) + 16) - 8 if t >= at else -99
        for i, (x, y) in enumerate(pts[:n]):
            under = img.getpixel((x, y))
            lum = 0.3 * under[0] + 0.59 * under[1] + 0.11 * under[2]
            if lum >= 128:
                colr = INK
            else:
                colr = glyph.mix(under, BG, 1.0 if abs(i - g) <= 2 else 0.72)
            img.putpixel((x, y), glyph.mix(under, colr, keep))

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
    out += CPN._landings(REPLY_L) + CPN._landings(EGG)
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
RUN = {'input': [(GB.COMMITS1[0][0], SEND1 + 0.15), (GB.EGG_COMMITS[0][0], SEND2 + 0.15)], 'think': [(at, at + len(s) / BO.THINK_CPS + 0.2) for at, s in THINKS], 'trace': [(at, _code_end(at, s, ret)) for at, s, ret in CODE] + [(NEAR_OUT, RING_AT[-1] + 0.15)], 'generate': [(BO.CELL_AT[0], BO.CELL_AT[-1] + 0.1), (COPY_AT, HOLLOW_AT + 0.3), (REPLY_L.tok_t[0] - 0.2, SENT_AT + 0.1), (EGG.tok_t[0] - 0.2, EGG.tok_t[-1] + 0.1)], 'compare': [(S1.t0, S1.pick), (BO.HER_AT, BO.FOUND_AT[-1] + 0.1), (SWEEP_L[0], SWEEP_L[1] + 0.1), (S2.t0, S2.pick), (BO.SURF_AT, BO.UNDER_AT[-1] + 0.1), (BO.SELECT_AT[0], BO.SELECT_AT[-1] + 0.1), (BO.DIFF_AT, BO.DIFF_AT + 0.2), (NEAR_OUT + 0.1, RING_AT[-1] + 0.1)], 'forward': KIMI_SEGS}

def _status(t):
    tok = None
    if REPLY_L.tok_t[0] <= t < SHRINK4:
        tok = (REPLY_L.n_tok(t), len(REPLY_L.toks))
    elif EGG.tok_t[0] <= t < NEAR_OUT:
        tok = (EGG.n_tok(t), len(EGG.toks))
    s = tl.sim(t) if not T0 <= t < COS_AT else None
    scan = _scan_status(t)
    return {'generate': (f'{tok[0]}/{tok[1]} tok' if tok else '', False), 'compare': (scan, False) if scan else (f'sim(her) {s}' if s else '', True), 'forward': (speed.label('kimi' if t < SWITCH else 'qwen'), False)}

def _body(c, img, d):
    t = c.t
    L, u = layout(t)
    fold = _folding(t)
    if fold:
        _fold_under(d, t)
    _cmdline(d, t, CPN.right(t), _typed(t) if fold else None)
    hits = _reads(t).out
    st = _status(t)

    def gen(dd, r):
        for fn in (_gen_table, _gen_tpl, _gen_egg):
            fn(dd, t, r)

    def cmp_(dd, r, layer):
        _search(dd, t, S1, r, S1.pick, fade=BO.HER_AT - S1.pick)
        her = _found(dd, t, r)
        _ptable(dd, t, r, layer)
        _cos(dd, t, r, her)
        _search(dd, t, S2, r, S2.pick, fade=0.0)
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
        lead.shade(img, rect, shade_k(name, t) * k)
        status, her = st.get(name, ('', False))
        _box(d, rect, name, t, k, lead_run(name, t), level, status, her)
    m = max(hits.values(), default=0.0)
    if fold:
        _fold_strip(img, d, t, hits, min(1.0, 3 * m))
        _fold_over(d, t)
    else:
        CPN._memory(d, t, L['memory'], hits)
    if FOLD_ON and T0 <= t < FLASH_END:
        _fold_flash(d, t, hits)
    if not fold:
        lead.shade(img, L['memory'], shade_k('memory', t))
        panes.box(d, L['memory'], 'mem', t, min(1.0, 3 * m) * lead_w('memory', t))
    _overlays(img, d, t, L)
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
    st = _ao()._state(_a_t())
    carried = {name for name in tl.HER_FILES if _carried(name, st, t)}
    with _strip_at(_strip_v(t)):
        hud.strip(d, t, hits, bare=carried)
        x0, y0, x1, _y1 = hud.COLR
    _veil(img, (x0 - 2, y0 + 4, x1 + 2, y0 + 17), 1.0)
    if k > 0:
        _box(d, MEM, 'mem', t, k, run)

def _fold_go(name, st):
    """(start, landing) of the bubble of `name` on its way back into its block (see_you goes with its slab)."""
    s = T0 if name == _ao().SWEETEST else T0 + FOLD_STEP * st[name][0]
    return (s, s + FOLD_GO)

def _pill_rect(cx, cy, rx, ry, box, g):
    return tuple((ease.lerp(a, b, g) for a, b in zip(box, (cx - rx, cy - ry, cx + rx, cy + ry))))

def _overlaps(r, b):
    return r[0] < b[2] and r[2] > b[0] and (r[1] < b[3]) and (r[3] > b[1])

def _pill(d, cx, cy, rx, ry, box, g, name):
    """A's bubble <-> block morph (a_open._bubble's, run backwards), ending as the block lit (D1) with its name, so
    the landing flash takes over without a change of tone. r5c (R01): the name shows on it only once it is over its
    block, and the block leaves its own label off from then (_carried): one label at a time, handed over in place."""
    col = hud.her(1.0)
    rect = _pill_rect(cx, cy, rx, ry, box, g)
    rad = int(min(ease.lerp(2, max(rx, ry), g), (rect[2] - rect[0]) // 2 - 1, (rect[3] - rect[1]) // 2 - 1))
    fill = glyph.mix(col, lv(col, 0.38), g)
    d.rounded_rectangle(rect, radius=max(0, rad), fill=fill, outline=col, width=2)
    a = 1.0 if _overlaps(rect, box) else 0.0
    if a > 0:
        d.text((rect[0] + 4, rect[1] + 6), hud.chip(d, name, rect[2] - rect[0]), font=P.font(11), fill=glyph.mix(fill, BG, a))

def _fold_slab_go():
    return (T0, T0 + FOLD_GO + 0.04)

def _fold_land(name, st):
    land = _fold_go(name, st)[1]
    return max(land, _fold_slab_go()[1]) if name == _ao().SWEETEST else land

def _carried(name, st, t):
    """r5c (R01): while the bubble on its way back (see_you: its slab) is over the block it lands on, it carries
    the name (_pill) and the block leaves its own label off: the name is read once and lands with it."""
    AO, tA = (_ao(), _a_t())
    k0 = tl.HER_FILES.index(name)
    with _strip_at(_strip_v(t)):
        block = hud.block_rect(k0, t)
    s, e = _fold_go(name, st)
    if s <= t < e:
        cx, cy, rx, ry = AO._center(name, tA, st)
        if _overlaps(_pill_rect(cx, cy, rx, ry, block, 1 - ease.ease_io(ease.prog(t, s, e))), block):
            return True
    if name == AO.SWEETEST:
        s0, s1 = _fold_slab_go()
        if s0 <= t < s1:
            u = ease.ease_io(ease.prog(t, s0, s1))
            return _overlaps(tuple((ease.lerp(a, b, u) for a, b in zip(AO._row_slab(st), block))), block)
    return False

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
        a = 1.0 if _overlaps(rect, blocks[AO.SWEETEST]) else 0.0
        if a > 0:
            d.text((rect[0] + 4, rect[1] + 6), hud.chip(d, AO.SWEETEST, rect[2] - rect[0]), font=P.font(11), fill=glyph.mix(col, BG, a))
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
            d.text((x0 + 4 + dx, y0 + 6), hud.chip(d, name, x1 - x0), font=P.font(11), fill=BG)

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
LEAD = [(T0, 'input'), (FOLD_END, 'think'), (S1.t0, 'compare'), (W(6, 0), 'think'), (COPY_AT, 'generate'), (SENT_AT, 'dsh'), (ASK2_AT, 'input'), (tl.at_beat(S2.t0), 'compare'), (BO.SELECT_AT[0], 'trace'), (BO.SELECT_AT[1], 'compare'), (EGG.tok_t[0], 'generate'), (BO.DIFF_AT, 'compare'), (tl.at_beat(BO.DIFF_AT, 1), 'generate'), (W(12, 0), 'dsh'), (NEAR_OUT, 'trace+compare'), (RING_AT[-1], 'trace'), (NEAR_BACK, 'dsh'), (SWITCH, 'forward')]
_KEYS = sorted({n for _t0, n in LEAD})
MEM_IN = (FOLD_END, tl.next_beat(FOLD_END))

def _release(t):
    return ease.ease_io(ease.prog(t, *RELEASE))

def _leads_now(name, t):
    """True while `name` is (one of) the leader(s) at t, before the release."""
    if not T0 <= t < RELEASE[0]:
        return False
    return name in max(((t0, n) for t0, n in LEAD if t >= t0))[1].split('+')

def _w(name, t):
    """0..1: how much `name` leads at t by the LEAD table (lead.weights; "a+b" leads both a and b)."""
    if name == 'memory':
        return 1 - ease.prog(t, *MEM_IN) if FOLD_ON else 0.0
    w = lead.weights(t, _lead_table(), _KEYS)
    return min(1.0, sum((v for key, v in w.items() if name in key.split('+'))))
_LT = {}

def _lead_table():
    """LEAD as lead.weights reads it. r5 2-B (落拍): a hand-over in b1-b8 is centred on its beat or syllable (it
    starts lead.EASE / 2 early, so it is half done on the event) instead of starting on it; r5a's eased the change
    over the 0.16 s after the event, and the frame that changed most fell two frames late. The first entry (the fold)
    and everything from 68.15 on (b9, the interlude's) stay as they are."""
    key = (id(LEAD), len(LEAD))
    if key not in _LT:
        h = lead.EASE / 2
        _LT.clear()
        _LT[key] = [(t0 - h if k > 0 and t0 < W(12, 0) - 1e-06 else t0, n) for k, (t0, n) in enumerate(LEAD)]
    return _LT[key]

def lead_w(name, t):
    """0..1: how much `name` leads at t; 1 for every pane outside T0..the release (b_pane's look, as C starts)."""
    if not T0 <= t < RELEASE[1]:
        return 1.0
    return ease.lerp(_w(name, t), 1.0, _release(t))

def shade_k(name, t):
    """lead.shade's k for the pane: 0 while it leads, 1 while it does not."""
    return 1.0 - lead_w(name, t)

def lead_run(name, t):
    """The pane's spinner: the pane that leads turns it (it is working on what you are watching); the others are
    idle. From the release on, b_pane's (panes.run_k over RUN)."""
    rk = panes.run_k(t, RUN[name])
    if not T0 <= t < RELEASE[1]:
        return rk
    return ease.lerp(_w(name, t), rk, _release(t))

def _shaded(colr, k):
    """What lead.shade(k) makes of colr: for what is drawn over a pane after its shade (the overlays)."""
    return glyph.mix(colr, lead.TONE, lead.MIX * min(1.0, k))

def _reads(t):
    """BO._reads with its answer's chunks where they land here (REPLY_L), and a read when her line is copied."""
    Pl = hud.Pulse(t)
    for at in (SEND1, SEND2):
        for k in range(9):
            Pl.hit(k if k < 8 else 'archive', tl.grid(at, k, 4), 0.1)
    for S in (S1, S2):
        for k in range(4):
            Pl.hit('archive', tl.grid(S.t0, k, 4), 0.12)
        Pl.hit('archive', S.pick, 0.4)
    Pl.hit('archive', COPY_AT, 0.3)
    for dec in (REPLY_L, EGG):
        for k, tk in enumerate(dec.toks):
            if tk.src != 'self' and dec.tok_t[k] is not None:
                Pl.hit('archive', dec.tok_t[k], 0.3)
    n = len(hud.strip_files(t))
    for k in range(n + 1):
        Pl.hit(k if k < n else 'archive', GB.READ_Q + 0.035 * k, 0.12)
    return Pl

def _q_x(t=None):
    """Where 桌子 sits in the input pane (the second IME commit, 一张桌子, after its 一张): x, y, 20 px. With t,
    after the commit has opened at its token boundary (_split_u)."""
    fid = P.font(10)
    x = COL + 10
    su = 0.0 if t is None else _split_u(t)
    for _at, w in GB.COMMITS1:
        tw = hud.width(w, 20, True)
        ids = prompt_ids.text(PROMPT_IDS[w]) if w in PROMPT_IDS else str(glyph.token_id(w))
        if '桌子' in w:
            return (x + hud.width(w[:w.index('桌子')], 20, True) + SPLIT_GAP * su, 88 + 11)
        x += max(tw, _MEAS.textlength(ids, font=fid)) + 12
    return (x, 88 + 11)
_MEAS = ImageDraw.Draw(Image.new('RGB', (1, 1)))
FLY = (tl.grid(PICK_AT, 1), FILL_AT)

def _overlays(img, d, t, L):
    _copy_up(img, d, t, L)
    _take(img, d, t, L)

def _copy_chars(t, L):
    """[(ch, x, y, size)] of the copy of her line on its way up (y as _slots gives it; the glyph is drawn 0.1 size
    higher), or [] outside 48.43-48.90."""
    if not COPY_AT <= t < HOLLOW_AT:
        return []
    c, g = (L['compare'], L['generate'])
    y1 = g[1] + TPL_DY
    out = []
    for k, (ch, (x, y, w, size)) in enumerate(zip(BO.HER_CH, _slots(c, 0.0))):
        u = ease.ease_io(ease.prog(t, COPY_AT + 0.008 * k, HOLLOW_AT - 0.1 + 0.008 * k))
        out.append((ch, ease.lerp(x, TPL[k][0], u), ease.lerp(y, y1, u), ease.lerp(size, TS, u)))
    return out

def _copy_boxes(t, L):
    """Ink boxes of the copy's characters above her line (what shows of it; see _copy_up)."""
    top = _copy_clip(L)
    out = []
    for ch, x, y, sz in _copy_chars(t, L):
        w = BO._slot_w(ch, sz)
        y0, y1 = (y - sz * 0.1 + sz * 0.25, min(y - sz * 0.1 + sz * 1.21, top))
        if y1 > y0:
            out.append((x, y0, x + w - 1, y1))
    return out

def _copy_clip(L):
    """The copy rises out of her line: only what is above her line's ink (less 3 px) shows."""
    c = L['compare']
    y = c[1] + Y_HER2 - S_HER2 * 0.1 + S_HER2 * 0.25
    return y - BOX_IN

def _copy_up(img, d, t, L):
    """48.43-48.90 ("by", "leg"): a copy of her line rises out of compare into generate's row, lit while it moves
    (D1); the line it was copied from stays in compare. r5 2-B (R-C): the copy rises out of the line (nothing of it
    shows over her line itself), the question row above it gives way a character at a time (_found), and the two
    pane borders it goes through open for it."""
    chars = _copy_chars(t, L)
    if not chars:
        return
    clip = _copy_clip(L)
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    for ch, xx, yy, sz in chars:
        if ch == '🍆':
            GB.eggplant(ld, xx + 3, yy + sz * 0.05, max(2, int(sz / 9)), 1.0, 1.0)
        else:
            hud.tx(ld, (xx, yy - sz * 0.1), ch, int(round(sz)), hud.her(1.0) + (255,), bold=True)
    ld.rectangle((0, int(clip), img.size[0], img.size[1]), fill=(0, 0, 0, 0))
    g, c = (L['generate'], L['compare'])
    borders = [(round(g[3]), round(g[0]), round(g[2]), -1), (round(c[1]), round(c[0]), round(c[2]), 1)]
    for x0, y0, x1, y1 in _copy_boxes(t, L):
        for yb, bx0, bx1, src in borders:
            if y0 - BOX_IN <= yb <= y1 + BOX_IN:
                _door(img, yb, max(bx0, x0 - BOX_IN), min(bx1, x1 + BOX_IN), src)
    img.paste(lay, (0, 0), lay)

def _give_way(t, box):
    """0..1 how far a character at box (x0, y0, x1, y1) has given way to the copy passing over it (1 = gone)."""
    L = layout(t)[0]
    k = 0.0
    for x0, y0, x1, y1 in _copy_boxes(t, L):
        dx = max(x0 - box[2], box[0] - x1, 0)
        dy = max(y0 - box[3], box[1] - y1, 0)
        k = max(k, 1 - ease.clamp((max(dx, dy) - BOX_IN) / 6))
    return k

def _take(img, d, t, L):
    """52.04-52.92 ("per-fect-ta"): 桌子 in your question is boxed, a copy slides out of the box a 16th later and
    drops into her blank on "table" (20 -> 30 px). r5 2-B (D35, R-C): the box keeps 3 px clear of the ink and its
    bottom edge is 桌子's token rule; the copy leaves through that rule, runs right along the top of the trace pane
    (the oldest trace line has scrolled away for `tpl.fill(你[3])`), comes down to the right of the trace lines
    and into the blank. No text is crossed (112378, under the box, gives way while the copy passes over it); the
    pane borders it goes through open for it (_door)."""
    if not PICK_AT <= t < FILL_AT + 0.4:
        return
    qx, qy = _q_x(t)
    qw = hud.width('桌子', 20, True)
    box = _box_k(t)
    hold = box * (1 - ease.prog(t, FLY[0], FLY[0] + 0.15))
    k_in = shade_k('input', t)
    if hold > 0:
        hud.tx(d, (qx, qy), '桌子', 20, _shaded(INK, k_in * (1 - hold)), True)
    bx = (qx - BOX_IN, qy + 1, qx + qw - 1 + BOX_IN, qy + 30)
    if box > 0:
        d.rectangle(bx, outline=glyph.mix(_shaded(BG, k_in), INK, box))
    if not FLY[0] <= t < FILL_AT:
        return
    x, y, sz = _fly_at(t)
    w = hud.width('桌子', sz, True)
    ink = (x, y + sz * 0.25, x + w - 1, y + sz * 1.21)
    for yb, x0, x1, src in _borders(L, bx):
        if ink[1] - BOX_IN <= yb <= ink[3] + BOX_IN:
            _door(img, yb, max(x0, ink[0] - BOX_IN), min(x1, ink[2] + BOX_IN), src)
    _word(img, x, y, sz, INK, ymin=bx[3] + 1 if t < FLY_S1 else None)
FLY_TOP = 153
FLY_S1 = FLY[0] + 0.12

def _fly_cx():
    lines = ['tpl = 她.replace("一根茄子", "＿")', FILL_CODE]
    ends = [COL + 10 + mw(lines[0], 14), COL + 10 + mw(lines[1], 14, True)]
    return int(math.ceil(max(ends))) + BOX_IN + 1

def _fly_path():
    qx, qy = _q_x(PICK_AT)
    cx = FLY_CX
    pts = [(qx, qy), (qx, FLY_TOP), (cx, FLY_TOP), (cx, 236), (GAP_X0 + BLANK_PAD, 230 + TPL_DY - TS * 0.1)]
    rad = [0, 10, 8, 30, 0]
    dense = []
    for i, p in enumerate(pts):
        if i == 0 or i == len(pts) - 1 or rad[i] == 0:
            dense.append(p)
            continue
        a, b = (pts[i - 1], pts[i + 1])
        la = math.dist(a, p)
        lb = math.dist(p, b)
        ra, rb = (min(rad[i], la / 2), min(rad[i], lb / 2))
        p0 = (p[0] + (a[0] - p[0]) * ra / la, p[1] + (a[1] - p[1]) * ra / la)
        p2 = (p[0] + (b[0] - p[0]) * rb / lb, p[1] + (b[1] - p[1]) * rb / lb)
        for k in range(9):
            s = k / 8
            dense.append(((1 - s) ** 2 * p0[0] + 2 * s * (1 - s) * p[0] + s * s * p2[0], (1 - s) ** 2 * p0[1] + 2 * s * (1 - s) * p[1] + s * s * p2[1]))
    acc = [0.0]
    for a, b in zip(dense, dense[1:]):
        acc.append(acc[-1] + math.dist(a, b))
    return (dense, acc)

def _fly_at(t):
    """(x, y, size) of the copy at t: the first leg (out of the box) on its own clock, the rest eased as one."""
    dense, acc = FLY_PATH
    L1 = FLY_TOP - _q_x(PICK_AT)[1]
    if t < FLY_S1:
        s = L1 * ease.ease_in(ease.prog(t, FLY[0], FLY_S1))
    else:
        s = L1 + (acc[-1] - L1) * ease.ease_out(ease.prog(t, FLY_S1, FILL_AT))
    k = max(0, min(len(acc) - 2, next((i for i in range(len(acc) - 1) if acc[i + 1] >= s), len(acc) - 2)))
    seg = acc[k + 1] - acc[k]
    f = 0.0 if seg <= 0 else (s - acc[k]) / seg
    x = ease.lerp(dense[k][0], dense[k + 1][0], f)
    y = ease.lerp(dense[k][1], dense[k + 1][1], f)
    grow = ease.smooth(ease.clamp((y - 236) / (dense[-1][1] - 236)))
    sz = int(round(ease.lerp(20, TS, grow)))
    return (x, y, sz)
FLY_CX = _fly_cx()
FLY_PATH = _fly_path()

def _borders(L, bx):
    """(y, x0, x1, src_dy) of the lines the copy goes through: the box's bottom (桌子's rule), the input pane's
    bottom, the trace pane's top and bottom, the generate pane's top."""
    i, tr, g = (L['input'], L['trace'], L['generate'])
    return [(bx[3], bx[0], bx[2], -1), (round(i[3]), round(i[0]), round(i[2]), -1), (round(tr[1]), round(tr[0]), round(tr[2]), 1), (round(tr[3]), round(tr[0]), round(tr[2]), -1), (round(g[1]), round(g[0]), round(g[2]), 1)]

def _door(img, y, x0, x1, src):
    """Open a 1 px line at row y over [x0, x1] for something passing through: the row takes the pixels of the row
    next to it (src = -1 above, +1 below), the pane's own ground."""
    x0, x1, y = (int(math.floor(x0)), int(math.ceil(x1)), int(y))
    if x1 < x0:
        return
    img.paste(img.crop((x0, y + src, x1 + 1, y + src + 1)), (x0, y))

def _word(img, x, y, size, colr, ymin=None):
    """桌子 at (x, y), size px; with ymin, only its rows from ymin down (it slides out from under a line)."""
    f = hud.font(size, '桌子', True)
    w, h = (int(hud.width('桌子', size, True)) + 4, int(size * 1.5) + 4)
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).text((2 + (x - int(x)), 2 + (y - int(y))), '桌子', font=f, fill=255)
    ox, oy = (int(x) - 2, int(y) - 2)
    if ymin is not None and ymin > oy:
        cut = min(h, int(ymin) - oy)
        ImageDraw.Draw(m).rectangle((0, 0, w, cut - 1), fill=0)
    img.paste(colr, (ox, oy, ox + w, oy + h), m)

def _dsh_t(t):
    """The time whose dsh shot is shown at t. r4 shot the reply arriving on "You're the on-ly" (BO.REPLY1); here 桌子
    lands on "table" and 了哦 on "-ble", and the tail row comes on "for". The shots in between are held; from the
    end of the tail row's fade-in dsh is still until 55.04, so the original time takes over there."""
    o, fps = (REPLY1.tok_t, P.FPS)
    if t < o[2] or t >= SENT_AT + 0.16:
        return t
    if t < FILL_AT:
        return math.floor(o[2] * fps) / fps
    if t < TIGHT_AT:
        return math.ceil(o[2] * fps) / fps
    if t < SENT_AT:
        return math.ceil(o[3] * fps) / fps
    return REPLY1.done + 0.25 + (t - SENT_AT)

def _character_layer(film, orig):
    """r3's dsh layer from ui/pane_open_b4 (menu notes and speeds of ui/pages/b_pane.py) once it is shot; batch 3
    shows those shots on _dsh_t."""
    b4 = P.path('ui/pane_open_b4')
    if not (b4.exists() and any(b4.iterdir())):
        return BO._character_layer(film, orig)
    real = BO.PaneFrames
    BO.PaneFrames = lambda path, *a, **k: real(b4, *a, **k)
    try:
        inner = BO._character_layer(film, orig)
    finally:
        BO.PaneFrames = real

    def fn(t, n, ctx):
        return inner(_dsh_t(t) if T0 <= t < T1 else t, n, ctx)
    return fn

def register(film):
    for name, a, b in BO.SHOTS:
        _add(film, name, a, b)
    film.character = _character_layer(film, film.character)
    full_frame(NEAR_OUT, NEAR_BACK, 0.3, 0.4)
    hud.LIVE.append((COPY_AT, HOLLOW_AT))
    for at in sorted(set(REPLY_L.tok_t)):
        if any((REPLY_L.toks[k].src != 'self' and REPLY_L.tok_t[k] == at for k in range(len(REPLY_L.toks)))):
            hud.LIVE.append((at, at + LIT_HOLD))
    hud.LIVE.extend(EGG.falls())
    for seq in (BO.FOUND_AT, BO.UNDER_AT):
        for k, at in enumerate(seq):
            hud.LIVE.append((at, seq[k + 1] if k + 1 < len(seq) else at + 0.5))
    for S in (S1, S2):
        hud.LIVE.append((S.pick, S.pick + 0.3))
    if FOLD_ON:
        hud.LIVE.append((T0, FLASH_END - hud.LIVE_FADE))
    for t0, side in [(T0, 'left'), (SENT_AT, 'right'), (ASK2_AT, 'left'), (S2.t_in, 'both'), (W(9, 0), 'left'), (W(12, 0), 'right'), (NEAR_OUT, 'both'), (NEAR_BACK, 'right')]:
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
