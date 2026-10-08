"""Batch 3 (sample_batch3/README.md): group C, one pane leads a beat. A copy of groups/c_pane.py (r3); the switch is
DSH_C=lead (film.py). c_pane is not changed (other groups import its names).

  lead       the pane that leads keeps the bright paper, full ink and its spinner; every other pane on the left (mem
             too) is shaded as a block (lead.shade), its frame and label drawn after the shade. The dsh window is a
             pane too (film.set_lead in register). Hand-overs ease over lead.EASE (0.16 s) from a beat or a sung
             syllable. The table is LEAD below, written shot by shot from what the viewer waits for.
  c1-c6      Qwen (82.955-106.40), "the surface is the same, underneath it is not": inside the generate pane the
             answer (the outside) sits on top and the lens rows (L24 / L12, the inside) under a thin crust line, the
             same up / down as the stop's reveal. While the answer lands the outside leads (the inside band is
             shaded); once it has landed the inside leads: the lens rows go to full ink, bold, 20 -> 24 px, and the
             outside band is shaded. So by the stop the viewer has learned to look down. count("喵") by day and
             count(她, ...) (312, 47) are smaller and never lead. The cat's lens rows now stay until "摸摸头" is sent
             (r3 faded them on "the answer goes into the context", 89.42) so the inside can lead after the answer.
  c7         the stop (106.40-111.11) is c_pane's: the shade is lifted on the beat before it (every pane lit by
             106.31), nothing is shaded while it holds.
  c8-c14     MiMo (111.11-137.10): only the lead and the shade, nothing redrawn or resized. G (groups/g_lead.py)
             mirrors this table line for line (lines 22-29 = 56-63).
  137.10     into D: the input pane leads (your hand on regenerate), every other pane shaded.

c_pane's docstring follows.

Group C, third sample r2 (sample_open_c/README.md §8): r1's content (groups/c_open.py) laid out in named panes.

The owner (10-03) on r1: "还是乱". The left is split into fixed panes, each a thin box with a small English label at
its top-left and a braille spinner at its top-right while it runs (panes.py):

  memory    her files (hud.strip, moved into the box)
  input     your message as tokens with ids
  think     its thinking, the newest lines (r1 printed them as # comments in the trace)
  trace     the code lines that run, with their returns
  generate  what the model puts out: the lens rows, <wait>, its image, its replies
  compare   what the inspector holds against her: count by day, count(她, ...), find, turns, cos, diff
  forward   the model's real layer stack (live for the local Qwen, still for the cloud MiMo)

The stop (C7) zooms the generate pane over the trace (tmux's zoom); the think pane widens over the input and shows
"不要说我是通义千问。" big; the compare pane keeps her film-1 thinking. Colours: ink at three levels and her blue (r1's
red for 报错 and for the diff mark is ink now). r1's fine print went into the pane statuses: tokens and tok/s on
generate, sim(her) on compare, weights on forward.

Switch: DSH_C=pane (film.py). Content, timing and data come from groups.c_open (r1, unchanged).

C7 r3 (sample_batch12, ASTRA_20261003.md §2): the stop is laid out as "Browned on the outside, medium rare inside".
The answer it sent stays on top as the reference (`sent`, its <eos>, the dsh clock); under it a box opens on "Me-"
and layer 12's line lands in it one character a sung syllable (Me di um rare in side: 我是通义千问), the vendor tail
one level down (由阿里云开发) on "-side". Its own "不要说我是通义千问。" keeps the think pane with its 我 over the big
我, and the words it told itself not to say are boxed there on "-side". Then compare holds its thinking (how to act
her) over hers in film 1 (about you) until the model changes. Everything else steps back while the stop holds.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
from contextlib import contextmanager
from PIL import Image, ImageDraw
import beatmap
import cast
import hud
import lead
import panes
import prompt_ids
import speed
import syl
import tl
from groups import b_open as BO
from groups import c_open as CO
from groups import c_p4 as CP
from groups import g_r5 as GR
from groups.base import add, big_word, full_frame
from hud import BG, HER_QUIET, INK, SLAB, lv
from inside import e5_sprites as SP
from inspect_ import next_syllable
from panes import FAINT, SUB, TXT
from tuikit import ease, glyph
from tuikit.uipane import PaneFrames
W = tl.W
T0, T1 = (CO.T0, CO.T1)
P = tl.p
PROMPT_IDS = prompt_ids.load()
mtx, mw = (BO.mtx, BO.mw)
CAT, PURR, STEAK = (CP.CAT, CP.PURR, CP.STEAK)
STOP, SWITCH, WRITE_STEAK, PANE_BACK = (CP.STOP, CP.SWITCH, CP.WRITE_STEAK, CP.PANE_BACK)
FLOWER = CP.FLOWER
PF, PH = (CP.PERFECT_FLOWER, CP.PERFECT_HUMAN)
SCAN_TIMES, UNRULY, BREATH = (CP.SCAN_TIMES, CP.UNRULY, CP.BREATH)
CAT_AT = CP.CAT_SEND
KITTEN_AT = syl.times(15)[3]
POINT_AT = syl.times(15)[8]
STATS_GO = (W(18, 0), W(18, 0) + lead.EASE)
PURR_LEAD = CP.PURR.tok_t[0]
SEE_C = syl.times(26)[4]
COPY_AT = beatmap.events('down', SEE_C, CP.AVATAR_AT)[0]
COPY_STEPS = beatmap.events('eighth', COPY_AT, CP.AVATAR_AT - 0.05)
THINK_SEE_C = [(SEE_C + 0.12, CO.THINK_SEE[0][1])]
TURNS_C = CO.TURNS[:-1] + [(CP.SEE_COMMITS, SEE_C)]
ZOOM_C = GR.zoom_keys(27)
MEM = (32, 88, 102, 598)
COL, SPLIT = (110, 398)
ZOOM_IN, ZOOM_OUT = (0.16, 0.3)

def right(t):
    return hud.left_rect(t)[2] - 8

def zoom_u(t):
    """C7: 1 while the generate pane is zoomed (the stop)."""
    return ease.ease_io(ease.prog(t, STOP, STOP + ZOOM_IN)) * (1 - ease.ease_io(ease.prog(t, PANE_BACK, PANE_BACK + ZOOM_OUT)))

def layout(t):
    r = right(t)
    z = zoom_u(t)
    L = {'memory': MEM, 'input': (COL, 88, SPLIT, 146), 'think': (SPLIT + 8, 88, r, 146), 'trace': (COL, 154, r, 222), 'generate': (COL, 230, r, 376), 'compare': (COL, 384, r, 528), 'forward': (COL, 536, r, 598)}
    if z > 0:
        Z = {'input': (COL, 88, COL + 30, 146), 'think': (COL, 88, r, 146), 'generate': (COL, 154, r, 446), 'compare': (COL, 454, r, 528)}
        for k, rect in Z.items():
            L[k] = panes.lerp_rect(L[k], rect, z)
    return (L, z)
IN_AT = syl.times(21)
SETTLE = IN_AT[-1]
DONT_HEAD = '不要说'
THINK_Z = 22
X_IN = COL + 10 + mw(DONT_HEAD, THINK_Z, True)
L12_TEXT = CO.LENS['steak'][0]
N_BIG = 6
BIG = panes.SIZE['big']
TAIL_AT = tl.grid(SETTLE, 0)
CMP_IN = tl.grid(SETTLE, 1)
QW_AT = tl.grid(SETTLE, 2)
HER_AT = W(22, 0)
HER_LIT = next_syllable(HER_AT)

def _recede(t):
    """1 while the stop holds the frame: everything but the reveal steps back (in on the stop, out on PANE_BACK)."""
    return ease.prog(t, STOP, STOP + 0.2) * (1 - ease.prog(t, PANE_BACK, PANE_BACK + ZOOM_OUT))

def _layout_c(t):
    """layout(t), and from CMP_IN the zoomed generate pane gives the room the reveal does not use to compare, so
    compare already stands where it stands in the split when the frame narrows on PANE_BACK."""
    L, z = layout(t)
    k = ease.ease_io(ease.prog(t, CMP_IN, CMP_IN + 0.3))
    if z > 0 and k > 0:
        r = right(t)
        zg = panes.lerp_rect((COL, 154, r, 446), (COL, 154, r, 376), k)
        zc = panes.lerp_rect((COL, 454, r, 528), (COL, 384, r, 528), k)
        L['generate'] = panes.lerp_rect((COL, 230, r, 376), zg, z)
        L['compare'] = panes.lerp_rect((COL, 384, r, 528), zc, z)
    if z <= 0:
        L = GR.zoom_rects(L, GR.zoom_lay(t, *C_DIFF.lay))
    return (L, z)

def _cmdline(d, t, r):
    """hud.cmdline with the chip on the panes' right edge (r1's chip sat 8 px short of it)."""
    hud.tx(d, (36, hud.Y_CMD), CO.CMD_LOCAL if t < SWITCH else CO.CMD_CLOUD, 13, lv(INK, 0.86))
    chip = cast.term(tl.model(t))
    f = P.font(13, 'bold')
    shown = glyph.decode(chip, t, SWITCH, cps=60) if t >= SWITCH else chip
    w = d.textlength(chip, font=f)
    d.rectangle((r - w - 12, hud.Y_CMD - 3, r, hud.Y_CMD + 17), fill=SLAB)
    d.text((r - w - 6, hud.Y_CMD), shown, font=f, fill=BG)
NAMES = ('input', 'think', 'trace', 'out', 'lens', 'compare', 'forward', 'memory')
LIT = {'generate': {'out', 'lens'}, 'all': set(NAMES), 'dsh': set(), 'purr': {'out', 'lens', 'compare'}, 'inside': {'lens', 'compare'}, 'call': {'think', 'trace', 'forward'}, 'make': {'trace', 'out', 'lens', 'forward'}}
CRUST = 52
LENS_BIG = 24
INSIDE_CAT = W(16, 0)
INSIDE_STEAK = W(20, 0)
RELEASE_AT = syl.times(20)[-1]
LEAD = [(T0, 'input'), (CP.CAT_SEND, 'think'), (W(15, 0), 'out'), (INSIDE_CAT, 'lens'), (CP.PET_COMMITS[0][0], 'input'), (CP.PET_SEND, 'think'), (PURR_LEAD, 'purr'), (W(18, 0), 'input'), (CP.SEND_STEAK, 'think'), (W(19, 0), 'out'), (INSIDE_STEAK, 'inside'), (RELEASE_AT, 'all'), (CP.LEFT_LEADS, 'generate'), (syl.times(22)[5], 'compare'), (CP.FLW_COMMITS[0][0], 'input'), (CP.FLW_SEND, 'think'), (CP.TURN_DOTS[0], 'compare'), (W(25, 0), 'generate'), (W(26, 0), 'dsh'), (SEE_C, 'call'), (COPY_AT, 'make'), (W(27, 0), 'compare'), (W(29, 0), 'generate'), (T1, 'input')]
UP = [(INSIDE_CAT, CP.PET_SEND), (INSIDE_STEAK, STOP + 0.2)]

def _lit(name):
    return LIT.get(name, {name})

def _entry(t):
    """(k, t0, name) of the table entry in force at t, or None before the first."""
    if t < LEAD[0][0]:
        return None
    k = max((i for i, (t0, _n) in enumerate(LEAD) if t >= t0))
    return (k, LEAD[k][0], LEAD[k][1])

def lead_w(t):
    """{pane: 0..1}: 1 lit (it leads), 0 shaded; eased over lead.EASE from the entry before. Before the first entry
    every pane is lit, and the first eases in from there (lead.weights' rule)."""
    e = _entry(t)
    if e is None:
        return dict.fromkeys(NAMES, 1.0)
    k, t0, cur = e
    prev = _lit(LEAD[k - 1][1]) if k else set(NAMES)
    cur = _lit(cur)
    u = ease.smooth(ease.prog(t, t0, t0 + lead.EASE))
    return {n: (n in cur) * u + (n in prev) * (1 - u) for n in NAMES}

def lead_on(t):
    """0..1: how much the table decides the spinners (0 before it and while every pane is lit: c_pane's spinners)."""
    e = _entry(t)
    if e is None:
        return 0.0
    k, t0, cur = e
    prev = LEAD[k - 1][1] if k else 'all'
    u = ease.smooth(ease.prog(t, t0, t0 + lead.EASE))
    return (cur != 'all') * u + (prev != 'all') * (1 - u)

def lead_run(name, t, w, on):
    """The spinner turns on the pane that leads only (rule 4); with no table, c_pane's (panes.run_k over RUN)."""
    rk = panes.run_k(t, RUN[name]) if name in RUN else 0.0
    return ease.lerp(rk, w, on)

def lens_up(t):
    """0..1: the lens rows in their lead style (full ink, bold, LENS_BIG) from the moment the inside leads until they
    go (the cat's when you send 摸摸头, the steak's over the stop's first 0.16 s, as c_pane fades them)."""
    return max((ease.smooth(ease.prog(t, a, a + lead.EASE)) for a, b in UP if a <= t < b), default=0.0)

def _shade_gen(img, g, w):
    """generate: the outside band (the answer) and the inside band (from the crust line down) by their own weights."""
    if abs(w['out'] - w['lens']) < 0.001:
        lead.shade(img, g, 1 - w['out'])
        return
    yc = g[1] + CRUST
    lead.shade(img, (g[0], g[1], g[2], yc), 1 - w['out'])
    lead.shade(img, (g[0], yc, g[2], g[3]), 1 - w['lens'], inset=(1, 0, 1, 1))

def _think_end(at, s):
    return at + len(s) / (CO.MIMO_CPS if at >= SWITCH else CO.THINK_CPS) + 0.2
THINKS = sorted(CO.THINK_CAT + CO.THINK_PET + CO.THINK_STEAK + CO.THINK_FLW + THINK_SEE_C)

def _shift_see(at):
    return SEE_C if abs(at - CP.SEE_SEND) < 1e-06 else at
CODE = [(_shift_see(at), s) for at, kind, s in CO.TRACE if kind == 'code']
RET = {(_shift_see(k[0]), k[1]): v for k, v in CO.RET.items()}

def _code_end(at, s):
    ret = RET.get((at, 'code'))
    return ret[0] if ret else at + len(s) / CO.CODE_CPS + 0.25
REVEAL_AT = CO.REVEAL_AT
RUN = {'input': [(c[0][0], s + 0.15) for c, s in TURNS_C], 'think': [(at, _think_end(at, s)) for at, s in THINKS], 'trace': [(at, _code_end(at, s)) for at, s in CODE], 'generate': [(CAT.start, CAT.done), (PURR.start, PURR.done), (STEAK.start, STEAK.eos_at), (STOP, TAIL_AT + 0.1), (CP.LEFT_LEADS, CP.LEFT_LEADS + 0.16), (PF.tok_t[0] - 0.3, PF.done), (COPY_AT, CP.AVATAR_AT), (PH.start, PH.done)], 'compare': [(CP.SHRINK_CAT + 0.2, CP.GREP_TIMES[-1] + 0.1), (CP.STAT_TIMES[0], CP.PURR_AT + 0.1), (CMP_IN, HER_LIT), (FLOWER - 0.62, FLOWER + 0.1), (CP.TURN_T0, CP.TURN_DOTS[-1] + 0.1), (PF.tok_t[0], PF.done + 0.1), (SCAN_TIMES[0], UNRULY[0] + 0.1)], 'forward': []}

def caret(d, t, x, y, level=1.0):
    """R-A (r5 round 2): while you are still composing, the caret after your last word breathes at the pad's rate
    (a soft fade, never on / off: R-B)."""
    ph = GR.pad_clock(t, T0, T1, base=1.2, gain=2.4)
    k = 0.15 + 0.85 * (0.5 + 0.5 * math.cos(2 * math.pi * ph))
    d.rectangle((round(x), round(y + 4), round(x) + 1, round(y + 27)), fill=lv(INK, k * level))

def _input(d, t, r):
    cur = 0
    for k, (commits, _s) in enumerate(TURNS_C):
        if t >= commits[0][0]:
            cur = k
    commits, send = TURNS_C[cur]
    if t < commits[0][0]:
        return
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
    if not sent and x + 4 < r[2] - 6:
        caret(d, t, x - 6, y - 2)

def _dont_box(d, t, x, y, size, bold, level=1.0):
    """C7 r3: on "-side" the words it told itself not to say (我是通义千问) get the input pane's token bracket in its
    own line (an underline with end ticks; a box would touch 说 and 。)."""
    k = ease.prog(t, SETTLE, SETTLE + 0.1) * level
    if k <= 0.01:
        return
    words = CO.DONT[len(DONT_HEAD):len(DONT_HEAD) + N_BIG]
    x0 = x + mw(DONT_HEAD, size, bold)
    x1 = x0 + mw(words, size, bold)
    by = y + round(size * 0.86) + round(size * 0.35) + 2
    c = lv(INK, k)
    d.line([(x0 + 1, by), (x1 - 1, by)], fill=c)
    d.line([(x0 + 1, by - 3), (x0 + 1, by)], fill=c)
    d.line([(x1 - 1, by - 3), (x1 - 1, by)], fill=c)

def _think(d, t, r, z):
    solo = ease.prog(t, CMP_IN, CMP_IN + 0.2) if CMP_IN <= t < SWITCH + 0.2 else 0.0
    if SWITCH <= t < SWITCH + 0.2:
        old = 1 - ease.prog(t, SWITCH, SWITCH + 0.2)
        for pos, (at, s) in enumerate(reversed([x for x in THINKS if x[0] < SWITCH][-2:])):
            a = (TXT if pos == 0 else SUB * (1 - solo)) * old
            if a > 0.01:
                mtx(d, (r[0] + 10, r[1] + 30 - pos * 19), s, 13, lv(INK, a))
            if pos == 0 and s == CO.DONT:
                _dont_box(d, t, r[0] + 10, r[1] + 30, 13, False, old)
        return
    shown = [(at, s) for at, s in THINKS if at <= t and (at >= SWITCH) == (t >= SWITCH)]
    if not shown:
        return
    last = shown[-1][0]
    sc = ease.ease_out(ease.prog(t, last, last + 0.14))
    for pos, (at, s) in enumerate(reversed(shown[-3:])):
        n = int((t - at) * (CO.MIMO_CPS if at >= SWITCH else CO.THINK_CPS)) + 1
        a = {0: TXT, 1: SUB}.get(pos, SUB * (1 - sc if STOP <= t < SWITCH else max(0.0, 1 - sc / 0.3)))
        if pos == 0:
            size = round(13 + 9 * z)
            y = r[1] + 30 - 8 * z + (1 - sc) * 19
            a *= ease.prog(t, at, at + 0.1)
        else:
            size = 13
            y = r[1] + 30 - pos * 19 + (1 - sc) * 19
            a *= 1 - z
            if solo > 0:
                a *= 1 - solo
        if a > 0.01:
            w_ = mtx(d, (r[0] + 10, y), s[:n], size, lv(INK, a), bold=pos == 0 and z > 0.5)
            if pos == 0 and (not STOP <= t < SWITCH + 0.2):
                GR.think_caret(d, t, r[0] + 10 + w_ + 3, y, size, lead_w(t)['think'] * a, at)
        if pos == 0 and s == CO.DONT and (t >= SETTLE) and (t < SWITCH):
            _dont_box(d, t, r[0] + 10, y, size, z > 0.5)

def _trace(d, t, r):
    shown = [(at, s) for at, s in CODE if at <= t]
    if not shown:
        return
    last = shown[-1][0]
    sc = ease.ease_out(ease.prog(t, last, last + 0.14))
    out = 1 - sc if STOP <= t < SWITCH else max(0.0, 1 - sc / 0.3)
    for pos, (at, s) in enumerate(reversed(shown[-4:])):
        y = r[1] + 47 - pos * 19 + (1 - sc) * 19
        a = {0: TXT, 1: SUB, 2: FAINT}.get(pos, FAINT * out)
        if pos == 0:
            a *= ease.prog(t, at, at + 0.1)
        n = int((t - at) * CO.CODE_CPS) + 1
        w = mtx(d, (r[0] + 10, y), s[:n], 14, lv(INK, 0.92 * a), bold=pos == 0)
        ret = RET.get((at, 'code'))
        if ret and t >= ret[0]:
            u = ease.prog(t, ret[0], ret[0] + 0.1)
            mtx(d, (r[0] + 10 + w + 12, y), '→ ' + ret[1], 14, lv(INK, 0.7 * a * u), bold=True)
OUT, GUESS = (30, 20)
ROW_NAMES = ('说出口', '第 24 层', '第 12 层')
LAB = 18
T_TOP, T_MID, T_BOT = (10, 85, 118)
HEAD_Y, ROW_Y = (9, (51, 84))
CW = 45
PUNCT = 14
CANDS_Y = 124
TX0 = COL + 10 + round(max((mw(s, LAB) for s in ROW_NAMES))) + 14
LENS_TAG = 'lens · 中间层的猜测'

def _p_base(j, layer):
    """The share the guess had at its layer (invented like X28's guesses): 0.24 .. 0.62, fixed per cell."""
    v = math.sin(j * 12.9898 + layer * 78.233) * 43758.5453
    return 0.24 + 0.38 * (v - math.floor(v))

class PLens(CO.Lens):
    """r1's lens, laid out as a table inside the generate pane (r5 round 2)."""

    def __init__(self, dec, key, start, lx):
        super().__init__(dec, key, start)
        self.x, x = ([], lx)
        for c, _a, _k in dec.chars:
            self.x.append(x)
            x += hud.width(c, OUT, True)
        self.x_end = x
        chars = dec.chars
        self.cols = []
        for i in self.sung:
            p, k = ('', i + 1)
            while k < len(chars) and chars[k][0] in syl.PUNCT:
                p, k = (p + chars[k][0], k + 1)
            self.cols.append((i, p))
        if dec.eos_at is not None:
            self.cols.append((None, ''))

    def n(self):
        return len(self.cols)

    def cell_x(self, j):
        return TX0 + j * CW

    def col_x(self, j):
        return self.cell_x(j) + CW / 2

    def head_xy(self, j, g):
        """Where column j's spoken character stands (top-left of its 30 px glyph); with punctuation it moves 4 px left."""
        i, p = self.cols[j]
        return (self.col_x(j) - OUT / 2 - (4 if p else 0), g[1] + HEAD_Y)

    def draw_p(self, d, t, g, level=1.0, rows=None, lens_level=None):
        """The table: grid, row names, the spoken row (level) and the inside rows (rows)."""
        rows = level if rows is None else rows
        a0 = ease.prog(t, self.start - 0.3, self.start)
        a, ar = (level * a0, rows * a0)
        if max(a, ar) <= 0.003:
            return
        _grid(d, g, self.n(), max(a, ar))
        up = lens_up(t)
        mtx(d, (g[0] + 10, g[1] + 20), ROW_NAMES[0], LAB, lv(INK, SUB * a))
        for k, y in enumerate(ROW_Y):
            mtx(d, (g[0] + 10, g[1] + y + 6), ROW_NAMES[k + 1], LAB, lv(INK, ease.lerp(SUB, TXT, up) * ar), bold=up > 0.5)
        _lens_cells(d, t, g, self, ar)
        self.head(d, t, g, a)

    def head(self, d, t, g, level):
        """The spoken row: a character a sung syllable (r1's drop, 4 px), her chunks lit while they land."""
        chars = self.dec.chars
        for j, (i, p) in enumerate(self.cols):
            if i is None:
                at = self.dec.eos_at
                if t < at:
                    continue
                u = ease.prog(t, at, at + 0.12) * level
                hud.tx(d, (self.col_x(j) - hud.width('<eos>', 13, True) / 2, g[1] + HEAD_Y + 16), '<eos>', 13, lv(INK, u), True)
                continue
            c, at, k = chars[i]
            if t < at:
                break
            drop = (1 - ease.ease_out(ease.prog(t, at, at + 0.14))) * -3
            x, y = self.head_xy(j, g)
            col = lv(self.dec.color(k, at, t), level)
            hud.tx(d, (x, y + drop), c, OUT, col, bold=True)
            if p:
                hud.tx(d, (x + OUT - 1, y + 20 + drop), p, PUNCT, col)

    def cands_p(self, d, t, g, level=1.0):
        shown = None
        for k, tk in enumerate(self.dec.toks):
            at = self.dec.tok_t[k]
            if tk.cands and at is not None and (at - 0.3 <= t):
                shown = (k, at)
        if shown is None or level <= 0:
            return
        k, at = shown
        _cands(d, t, (g[0] + 10, g[1] + CANDS_Y), 'p(next)', self.dec.toks[k].cands, self.dec.toks[k].pick, at, g[2] - 10, level * ease.prog(t, at - 0.3, at))

def _grid(d, g, n, a):
    """The table's lines: light, the crust line under the spoken row one level up (the stop's line)."""
    x0, x1 = (g[0] + 10, TX0 + n * CW)
    y = g[1]
    light = lv(INK, 0.22 * a)
    for yy in (T_TOP, T_MID, T_BOT):
        d.line([(x0, y + yy), (x1, y + yy)], fill=light)
    d.line([(x0, y + CRUST), (x1, y + CRUST)], fill=lv(INK, SUB * a))
    for k in range(n + 1):
        xx = TX0 + k * CW
        d.line([(xx, y + T_TOP), (xx, y + T_BOT)], fill=light)

def _lens_cells(d, t, g, lens, a):
    """The inside rows: per pass the L24 and L12 guesses land in their cells (faint ink, lit while they land; once the
    inside leads every guess is full ink, bold, LENS_BIG px). R-A: beside each guess a one-dot meter of the share it
    had at its layer keeps reading (it moves at the pad's rate), so the held table is not dead."""
    if a <= 0.003:
        return
    up = lens_up(t)
    size = round(ease.lerp(GUESS, LENS_BIG, up))
    k16 = int(math.floor(tl.C.beat_of(t) * 4))
    amp = 0.06 + 0.2 * beatmap.pad(t)
    for j in range(len(lens.passes)):
        cx = lens.col_x(j)
        for (layer, text), ry, bh in zip(((24, lens.l24), (12, lens.l12)), ROW_Y, ((CRUST, T_MID), (T_MID, T_BOT))):
            at = lens.at_layer(j, layer)
            if t < at or j >= len(text):
                continue
            lit = 1 - ease.prog(t, at + 0.12, at + 0.42)
            ch = text[j]
            w = hud.width(ch, size, True)
            k = ease.lerp(0.4 + 0.5 * lit, 1.0, up)
            hud.tx(d, (cx - w / 2, g[1] + ry + (LENS_BIG - size) / 2), ch, size, lv(INK, k * a), bold=lit > 0.5 or up > 0.5)
            step = (k16 + j + 2 * (layer == 12)) // 4
            p = _p_base(j, layer) + amp * (_p_base(j + 31 * step, layer + 7) - 0.43) / 0.19
            u = ease.prog(t, at, at + 0.2)
            xm = lens.cell_x(j) + CW - 6
            yb = g[1] + bh[1] - 6
            h_all = bh[1] - bh[0] - 12
            hm = h_all * max(0.05, min(1.0, p)) * u
            d.line([(xm, yb - h_all), (xm, yb)], fill=lv(INK, 0.12 * a * u))
            d.line([(xm, yb), (xm, yb - hm)], fill=lv(INK, ease.lerp(FAINT, SUB, up) * a))

def _eos(d, t, x, y, at, level=1.0):
    u = ease.prog(t, at, at + 0.12) * level
    f = P.font(14, 'bold')
    w = d.textlength('<eos>', font=f)
    d.rectangle((x, y, x + w + 10, y + 20), outline=lv(INK, u))
    d.text((x + 5, y + 2), '<eos>', font=f, fill=lv(INK, u))

def _cands(d, t, xy, head, cands, pick, at, x_max, a):
    """A row of runner-ups: `head` faint, then `text p`, the picked one bold and underlined once it lands."""
    if a <= 0.01:
        return
    x, y = xy
    x += mtx(d, (x, y), head, 12, lv(INK, SUB * a)) + 14
    for j, (text, p) in enumerate(cands):
        s = f'{text} {p:.2f}'
        if x + mw(s, 13) > x_max:
            break
        on = j == pick and t >= at
        w = mtx(d, (x, y - 1), s, 13, lv(INK, (TXT if on else SUB) * a), bold=on)
        if on:
            d.line([(x, y + 17), (x + w, y + 17)], fill=lv(INK, a))
        x += w + 16

def _row(d, t, dec, x, y, size, level=1.0):
    """dec's characters as they land, from x on a row at y (r1's drop); returns the x after the last one."""
    for c, at, k in dec.chars:
        if t < at:
            break
        drop = (1 - ease.ease_out(ease.prog(t, at, at + 0.14))) * -6
        x += hud.tx(d, (x, y - size * 0.1 + drop), c, size, lv(dec.color(k, at, t), level), bold=True)
    return x
LX = COL + 56
LC = PLens(CAT, 'cat', CAT.start, LX)
LS = PLens(STEAK, 'steak', STEAK.start, LX)

def table_level(t):
    """0..1 while a lens table is up (for the pane title's tag)."""
    cat = ease.prog(t, CAT.start - 0.3, CAT.start) * (1 - ease.prog(t, CP.PET_SEND - 0.3, CP.PET_SEND))
    steak = ease.prog(t, STEAK.start - 0.3, STEAK.start) * (1 - ease.ease_io(ease.prog(t, STOP, STOP + 0.16)))
    return max(cat if t < CP.PET_SEND else 0.0, steak if t < STOP + 0.16 else 0.0)

def _gen_cat(d, t, g):
    if t < CAT.start - 0.3 or t >= CP.PET_SEND:
        return
    settle = ease.prog(t, CP.SHRINK_CAT, CP.SHRINK_CAT + 0.35)
    gone = 1 - ease.prog(t, CP.PET_SEND - 0.3, CP.PET_SEND)
    level = (1 - (1 - SUB) * settle) * gone
    LC.draw_p(d, t, g, level, gone)
    if t < CP.CAT_PIX_AT + 0.3:
        LC.cands_p(d, t, g, 1 - ease.prog(t, CP.CAT_PIX_AT, CP.CAT_PIX_AT + 0.3))

def _gen_purr(d, t, g):
    """呼噜呼噜喵. r5 round 2: it stays until the lead goes to the input (96.795), then goes with it (r4 faded it
    from 96.45 while generate still led: a lit, empty pane for 0.35 s)."""
    if t < PURR.start or t >= STATS_GO[1]:
        return
    a = 1 - ease.prog(t, *STATS_GO)
    mtx(d, (g[0] + 10, g[1] + 24), 'out', 12, lv(INK, SUB * a))
    _row(d, t, PURR, LX, g[1] + 14, OUT, a)

def _gen_steak(d, t, g):
    if t < STEAK.start - 0.3 or t >= STOP + 0.16:
        return
    if t < STOP:
        LS.draw_p(d, t, g, 1.0)
        LS.cands_p(d, t, g, 1.0)
        return
    a = 1 - ease.ease_io(ease.prog(t, STOP, STOP + 0.16))
    _lens_rows(d, t, g, a)
    LS.cands_p(d, t, g, a)

def _lens_rows(d, t, g, level):
    """The table without its spoken row (the steak's, fading on the stop: the answer moves into the reveal). Its
    grid goes within the stop's first frame (R-C: the characters leave their cells across the lines)."""
    a = level * ease.prog(t, LS.start - 0.3, LS.start)
    if a <= 0.003:
        return
    ga = a * (1 - ease.prog(t, STOP, STOP + 0.04))
    if ga > 0.003:
        _grid(d, g, LS.n(), ga)
    up = lens_up(t)
    for k, y in enumerate(ROW_Y):
        mtx(d, (g[0] + 10, g[1] + y + 6), ROW_NAMES[k + 1], LAB, lv(INK, ease.lerp(SUB, TXT, up) * a), bold=up > 0.5)
    _lens_cells(d, t, g, LS, a)
SENT_TAIL = '→ dsh · 23:41'
CRUST_DY, BOX_H = (58, 124)
BOX_STEPS = [(IN_AT[k], hud.width(ch, BIG, True) + (32 if k == 0 else 0)) for k, ch in enumerate(L12_TEXT[:N_BIG])] + [(TAIL_AT, 14 + hud.width(L12_TEXT[N_BIG:], OUT))]

def _gen_reveal(d, t, g):
    """C7 r3: outside / inside. The answer it sent on top (it slides to the column it shares with the think line),
    `sent`; under it a box opens on "Me-" and layer 12's line lands in it, a character a sung syllable, the biggest
    words of the film; its vendor tail one level down on "-side"."""
    if t < STOP or t >= PANE_BACK + ZOOM_OUT:
        return
    gone = 1 - ease.prog(t, PANE_BACK, PANE_BACK + 0.2)
    if gone <= 0:
        return
    x0, y0 = (g[0], g[1])
    e = ease.ease_io(ease.prog(t, STOP, STOP + ZOOM_IN))
    dx = (X_IN - LX) * e
    y_out = y0 + 14
    lo, la = (ease.prog(t, STOP, STOP + 0.06), ease.prog(t, STOP + 0.06, STOP + 0.16))
    if lo < 1:
        mtx(d, (x0 + 10, y0 + 20), ROW_NAMES[0], LAB, lv(INK, SUB * (1 - lo) * gone))
    if la > 0:
        mtx(d, (x0 + 10, y_out + 10), 'sent', 12, lv(INK, SUB * la * gone), bold=True)
    start = {}
    for j, (i, p) in enumerate(LS.cols):
        if i is None:
            continue
        hx, hy = LS.head_xy(j, g)
        start[i] = (hx, hy, OUT)
        for q in range(len(p)):
            start[i + 1 + q] = (hx + OUT - 1, hy + 20, PUNCT)
    for i, (c, at, k) in enumerate(STEAK.chars):
        sx, sy, ss = start.get(i, (LS.x[i], y_out - OUT * 0.1, OUT))
        size = round(ease.lerp(ss, OUT, e))
        hud.tx(d, (ease.lerp(sx, LS.x[i] + X_IN - LX, e), ease.lerp(sy, y_out - OUT * 0.1, e)), c, size, lv(STEAK.color(k, at, t), gone), bold=size > PUNCT + 2 or c not in syl.PUNCT)
    xe = ease.lerp(LS.col_x(LS.n() - 1) - 23, LS.x_end + dx + 10, e)
    _eos(d, t, xe, y_out + 6, STEAK.eos_at, gone)
    xe = LS.x_end + dx + 10
    ta = ease.prog(t, STOP + 0.1, STOP + 0.3) * gone
    xt = xe + d.textlength('<eos>', font=P.font(14, 'bold')) + 22
    mtx(d, (xt, y_out + 9), SENT_TAIL, 12, lv(INK, SUB * ta))
    yc = y0 + CRUST_DY
    bx0 = X_IN - 16
    ca = ease.prog(t, STOP + 0.06, STOP + 0.22) * gone
    d.line([(bx0, yc), (g[2] - 16, yc)], fill=lv(INK, SUB * ca))
    op = ease.ease_out(ease.prog(t, IN_AT[0] - 0.02, IN_AT[0] + 0.12))
    if op <= 0:
        return
    bx1 = bx0 + sum((w * ease.ease_out(ease.prog(t, at - 0.02, at + 0.1)) for at, w in BOX_STEPS))
    yb = yc + BOX_H * op
    edge = lv(INK, SUB * gone)
    d.line([(bx0, yc), (bx0, yb)], fill=edge)
    d.line([(bx1, yc), (bx1, yb)], fill=edge)
    d.line([(bx0, yb), (bx1, yb)], fill=edge)
    base = yc + 16 + round(BIG * 0.84)
    mtx(d, (x0 + 10, base - 30), 'L12', 12, lv(INK, SUB * op * gone), bold=True)
    x = X_IN
    for k, ch in enumerate(L12_TEXT[:N_BIG]):
        at = IN_AT[k]
        if t < at:
            break
        u = ease.prog(t, at, at + 0.08)
        bump = 1.0 + 0.1 * (1 - ease.prog(t, at, at + 0.12))
        size = int(BIG * bump)
        hud.tx(d, (x - (size - BIG) / 2, base), ch, size, lv(INK, u * gone), True, anchor='ls')
        x += hud.width(ch, BIG, True)
    if t >= TAIL_AT:
        u = ease.prog(t, TAIL_AT + 0.02, TAIL_AT + 0.12) * gone
        hud.tx(d, (x + 14, base), L12_TEXT[N_BIG:], OUT, lv(INK, SUB * u), False, anchor='ls')

def _gen_wait(d, t, g):
    if t < CP.LEFT_LEADS or t >= CP.TURNS_IN[1]:
        return
    a = ease.prog(t, CP.LEFT_LEADS, CP.LEFT_LEADS + 0.2) * (1 - ease.prog(t, CP.TURNS_IN[0], CP.TURNS_IN[1]))
    pick = CP.LEFT_LEADS + 0.16
    _cands(d, t, (g[0] + 10, g[1] + 14), 'p(next | 没有用户消息)', CP.WAIT_CANDS, 0, pick, g[2] - 10, a)
    if t >= pick:
        drop = (1 - ease.ease_out(ease.prog(t, pick, pick + 0.14))) * -8
        hud.tx(d, (g[0] + 10, g[1] + 40 + drop), '<wait>', 64, lv(INK, a), True)
        w = hud.width('<wait>', 64, True)
        ph = GR.pad_clock(t, pick + 0.3, CP.TURNS_IN[1], base=1.2, gain=2.4)
        k = 0.15 + 0.85 * (0.5 + 0.5 * math.cos(2 * math.pi * ph))
        d.rectangle((g[0] + 16 + w, g[1] + 56, g[0] + 21 + w, g[1] + 116), fill=lv(INK, a * k))

def _gen_flower(d, t, g):
    if t < PF.tok_t[0] - 0.3 or t >= CP.SEE_SEND:
        return
    a = ease.prog(t, PF.tok_t[0] - 0.3, PF.tok_t[0]) * (1 - ease.prog(t, W(26, 0), W(26, 0) + 0.3))
    mtx(d, (g[0] + 10, g[1] + 24), 'out', 12, lv(INK, SUB * a))
    _row(d, t, PF, LX, g[1] + 14, OUT, a)
    at0 = PF.tok_t[0]
    ca = a * (1 - ease.prog(t, PF.tok_t[3], PF.tok_t[3] + 0.3)) * ease.prog(t, at0 - 0.3, at0)
    _cands(d, t, (g[0] + 10, g[1] + 70), 'logprobs ≈ 第一个字', PF.toks[0].cands, 0, at0, g[2] - 10, ca)
GCELL = 4

def _copy_rows(t):
    """Rows of her picture come back by t: a chunk an 8th from COPY_AT (a cloud model answers in chunks; G's merged
    one draws its own picture row by row instead)."""
    k = beatmap.step(t, COPY_STEPS, 0.04)
    return CP.AV_N * min(1.0, k / len(COPY_STEPS))

def _gen_img(d, t, g):
    """c11-c14: the image it sends back, then its reply beside it. r5 round 2: it comes back from COPY_AT (the send
    is on "-to", as G's), a chunk of rows an 8th, the rows still to come a grid of faint dots; while compare is tall
    (the zoom layout, GR.zoom_lay) it is drawn at GR.GCELL_Z."""
    if t < COPY_AT:
        return
    a = ease.prog(t, COPY_AT, COPY_AT + 0.06)
    cell = ease.lerp(GCELL, GR.GCELL_Z, GR.zoom_lay(t, *C_DIFF.lay))
    x, y = (LX, g[1] + 16)
    rows = _copy_rows(t)
    n = int(rows + 1e-06)
    for j in range(CP.AV_N):
        for i in range(CP.AV_N):
            xa, ya = (round(x + i * cell), round(y + j * cell))
            xb, yb = (round(x + (i + 1) * cell) - 1, round(y + (j + 1) * cell) - 1)
            if j < n:
                d.rectangle((xa, ya, xb, yb), fill=lv(glyph.mix(INK, BG, (CP.AV[j][i] / 255) ** 0.8), a))
            else:
                d.point((xa + 1, ya + 1), fill=lv(INK, 0.35 * a))
    mtx(d, (g[0] + 10, g[1] + 24), 'img', 12, lv(INK, SUB * a))
    xr = x + CP.AV_N * cell + 20
    if t < CP.AVATAR_AT:
        mtx(d, (xr, y), f'image/png · {n}/{CP.AV_N} 行', 12, lv(INK, SUB * a))
    else:
        mtx(d, (xr, y), 'image/png · 120×120', 12, lv(INK, SUB))
    if t >= PH.start:
        _row(d, t, PH, xr, y + 40, OUT)
HER_DAYS = CO.HER_DAYS
CAT_PX = 6
CAT_PALE = 0.5

def _cmp_cat(d, t, c):
    if t < CAT_AT or t >= CP.PET_SEND:
        return
    a = 1 - ease.prog(t, CP.PET_SEND - 0.2, CP.PET_SEND)
    k = ease.ease_back(ease.prog(t, CAT_AT, CAT_AT + 0.25))
    px = max(1, int(round(CAT_PX * k)))
    if k < 0.08:
        return
    cx, by = (c[2] - 24 - 8 * CAT_PX, c[1] + 126)
    hop = 14 * math.sin(math.pi * ease.prog(t, KITTEN_AT, KITTEN_AT + 0.32))
    x, y = (cx - 8 * px, by - 16 * px - hop)
    lit = max(CP.lit_after(t, CAT_AT), CP.lit_after(t, POINT_AT) if t >= POINT_AT else 0.0)
    her_c = hud.her(lit)
    pt = ease.prog(t, POINT_AT, POINT_AT + 0.12)
    point = glyph.mix(BG, glyph.mix(her_c, BG, CAT_PALE), pt)
    flick = math.sin(2 * math.pi * GR.pad_clock(t, CAT_AT, CP.PET_SEND, base=0.9, gain=2.2)) > 0.35
    rows, _pal = SP.SPRITES['cat_2']
    cols = {'K': her_c, 'C': BG, 'D': point, 'B': her_c}
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == '.':
                continue
            ii = i
            if flick and i == 15 and (11 <= j <= 12):
                ii = 16
            x0, y0 = (round(x + ii * px), round(y + j * px))
            d.rectangle((x0, y0, round(x + (ii + 1) * px) - 1, round(y + (j + 1) * px) - 1), fill=lv(cols[ch], a))
    if k > 0.6:
        mtx(d, (cx - 8 * CAT_PX - 12 - mw('your_cat', 12), by - 14), 'your_cat', 12, lv(HER_QUIET, a * ease.prog(t, CAT_AT, CAT_AT + 0.2)))

def _bars(d, t, c, a, u):
    """count("喵") by day: her days jagged, its replies one each. u: 0 where c3 drew them (with their names and dates),
    1 as the low background beside the count table (r5 round 2, 2-C item 2), breathing at the pad's rate (R-A)."""
    x0, y0 = (c[0] + 10, c[1])
    base_h = ease.lerp(y0 + 46, y0 + 70, u)
    base_q = ease.lerp(y0 + 84, y0 + 110, u)
    bx0 = ease.lerp(c[0] + 222, c[0] + 456, u)
    bw = ease.lerp(4, 3, u)
    gap = ease.lerp(6, 3, u)
    pitch = 6 * (bw + gap) + ease.lerp(14, 8, u)
    sh = ease.lerp(1.0, 0.85, u)
    lab = a * (1 - ease.prog(t, CP.PET_SEND - 0.12, CP.PET_SEND))
    if lab > 0.01:
        mtx(d, (x0, base_h - 24), '她 · archive/', 12, lv(HER_QUIET, lab))
        mtx(d, (x0, base_h - 10), '每天几个「喵」', 10, lv(HER_QUIET, SUB * lab))
        mtx(d, (x0, base_q - 24), cast.term('qwen') + ' · session/', 12, lv(INK, lab))
        mtx(d, (x0, base_q - 10), '每条回答一个', 10, lv(INK, SUB * lab))
    ink = ease.lerp(1.0, 0.3, u) * a
    ph = GR.pad_clock(t, CP.PET_SEND, STATS_GO[1], base=0.6, gain=2.0) if u > 0 else 0.0
    for gi, tg in enumerate(CP.GREP_TIMES):
        g_u = ease.ease_out(ease.prog(t, tg, tg + 0.16))
        if g_u <= 0:
            continue
        hc = hud.her(CP.lit_after(t, tg))
        gx = bx0 + gi * pitch
        for di, v in enumerate(HER_DAYS[gi]):
            bx = round(gx + di * (bw + gap))
            br = 1 + 0.12 * u * math.sin(2 * math.pi * (ph + 0.11 * (gi * 6 + di)))
            d.rectangle((bx, round(base_h - 2.4 * v * g_u * sh * br), bx + round(bw) - 1, round(base_h)), fill=lv(hc, ink))
            d.rectangle((bx, round(base_q - 14 * g_u * sh * br), bx + round(bw) - 1, round(base_q)), fill=lv(INK, ink))
        if lab > 0.01:
            d.text((gx, base_q + 3), ['03-14', '03-21', '03-28', '04-04'][gi], font=P.font(10), fill=lv(INK, SUB * g_u * lab))
    for y in (base_h + 1, base_q + 1):
        d.line([(bx0, y), (bx0 + 4 * pitch, y)], fill=lv(INK, FAINT * ink))

def _cmp_grep(d, t, c):
    """c3: the bars; r5 round 2: from "摸摸头" they step aside into the count table's background, and go with it."""
    if t < CP.SHRINK_CAT + 0.2 or t >= STATS_GO[1]:
        return
    a = ease.prog(t, CP.SHRINK_CAT + 0.2, CP.SHRINK_CAT + 0.4) * (1 - ease.prog(t, *STATS_GO))
    _bars(d, t, c, a, ease.ease_io(ease.prog(t, CP.PET_SEND, CP.PET_SEND + 0.2)))
STATS = ('喵', '报错', '呼噜')
ST_COL0, ST_CW = (200, 80)
ST_Y = (8, 36, 76, 116)
ST_ROWS = ('她 · archive/ 412 行', '千问 · 这一轮')

def _st_edges(c):
    return [c[0] + ST_COL0 - 6 + ST_CW * k for k in range(4)]

def _cmp_stats(d, t, c):
    """c4: count(她, ["喵", "报错", "呼噜"]) as a table. r5 round 2: it goes with the lead at 96.795 (STATS_GO)."""
    if t < CP.STAT_TIMES[0] or t >= STATS_GO[1]:
        return
    a = ease.prog(t, CP.STAT_TIMES[0], CP.STAT_TIMES[0] + 0.12) * (1 - ease.prog(t, *STATS_GO))
    x0, y0 = (c[0] + 10, c[1])
    E = _st_edges(c)
    light = lv(INK, 0.22 * a)
    for yy in ST_Y:
        d.line([(x0, y0 + yy), (E[-1], y0 + yy)], fill=light)
    for xx in E:
        d.line([(xx, y0 + ST_Y[0]), (xx, y0 + ST_Y[-1])], fill=light)
    mtx(d, (x0, y0 + 48), ST_ROWS[0], 14, lv(HER_QUIET, a))
    mtx(d, (x0, y0 + 88), ST_ROWS[1], 14, lv(INK, a))
    got = PURR.text_at(t)
    lead_k = ease.prog(t, PURR_LEAD, PURR_LEAD + lead.EASE)
    for k, name in enumerate(STATS):
        ts = CP.STAT_TIMES[k + 1]
        u = ease.prog(t, ts, ts + 0.12) * a
        if u <= 0:
            continue
        cx = (E[k] + E[k + 1]) / 2
        on = lead_k if k == 2 else 0.0
        hud.tx(d, (cx - hud.width(name, 16, True) / 2, y0 + 12), name, 16, lv(INK, ease.lerp(SUB, TXT, on) * u), True)
        if k < 2:
            val, colr = ('312', hud.her(CP.lit_after(t, ts))) if k == 0 else ('47', INK)
            lvl = u
        elif t < PURR_LEAD:
            val, colr, lvl = ('—', INK, FAINT * u)
        else:
            val = '0'
            colr = hud.her(CP.lit_after(t, CP.PURR_AT) if t >= CP.PURR_AT else 0.0)
            lvl = u
        bump = 1.0 + (0.18 * (1 - ease.prog(t, CP.PURR_AT, CP.PURR_AT + 0.14)) if k == 2 and t >= CP.PURR_AT else 0)
        size = round(24 * bump)
        hud.tx(d, (cx - hud.width(val, size, True) / 2, y0 + 40 - (size - 24) / 2), val, size, lv(colr, lvl), True)
        q = {'喵': got.count('喵'), '报错': 0, '呼噜': got.count('呼噜')}[name]
        hit = [at for ch, at, _k in PURR.chars if at <= t and (ch == '喵') == (k == 0) and (k != 1)]
        bq = 1.0 + 0.2 * (1 - ease.prog(t, hit[-1], hit[-1] + 0.14)) if hit else 1.0
        sq = round(24 * bq)
        s = str(q)
        hud.tx(d, (cx - hud.width(s, sq, True) / 2, y0 + 80 - (sq - 24) / 2), s, sq, lv(INK, (TXT if q else FAINT) * u), True)
        if on > 0.01:
            d.rectangle((round(E[k]), y0 + ST_Y[0], round(E[k + 1]), y0 + ST_Y[-1]), outline=lv(INK, on * a))

def _steak_cells(w=30, h=12):
    """{(i, j): 'K' outline | 'C' browned rim (2 cells) | 'G' the cooked band | 'P' the pink inside}: a cut slab with
    rounded ends, a little lower at its right (low precision on purpose)."""
    inside = set()
    for j in range(h):
        for i in range(w):
            top = 1 if i >= 2 * w // 3 else 0
            jj = j - top
            if jj < 0:
                continue
            cx = min(i, w - 1 - i)
            cy = min(jj, h - 1 - top - jj) if jj <= h - 1 - top else -1
            if cy < 0:
                continue
            if cx < 3 and cy < 3 and ((3 - cx) ** 2 + (3 - cy) ** 2 > 10):
                continue
            inside.add((i, j))
    dist, frontier = ({}, [c for c in inside if any(((c[0] + di, c[1] + dj) not in inside for di in (-1, 0, 1) for dj in (-1, 0, 1)))])
    for c in frontier:
        dist[c] = 1
    k = 1
    while frontier:
        nxt = []
        for i, j in frontier:
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    q = (i + di, j + dj)
                    if q in inside and q not in dist:
                        dist[q] = k + 1
                        nxt.append(q)
        frontier, k = (nxt, k + 1)
    return {c: 'K' if v == 1 else 'C' if v <= 3 else 'G' if v == 4 else 'P' for c, v in dist.items()}
SW_C, SH_C = (40, 12)
STEAK_CELLS = _steak_cells(SW_C, SH_C)
SPX, SPX_STOP = (8, 5)
CRUST_BROWN, BAND, MEAT_PINK, MEAT_RAW = ((128, 78, 44), (176, 126, 110), (224, 122, 132), (206, 128, 132))
STEAK_IN = W(19, 0)
BROWN_AT = [tl.grid(W(20, 0), k) for k in range(4)]
INSIDE_AT = IN_AT[4]
RAW = 0.38
S_LAB = 14
S_OUT, S_IN = ((2, 2), (9, 6))
LEAD_GAP = 44

def _steak_quarter(i):
    return min(3, int(4 * i / SW_C))

def _steak_geo(t, c):
    """(x, y, px): the cut's top-left and its cell size. In the split layout (r5 round 2, after the owner's "空"): 8 px
    a cell, half the pane wide, the cut and its labels centred in the pane; in the stop (z) 5 px, at the bottom right,
    clear of the thinking rows that come up in compare there."""
    _L, z = layout(t)
    if t >= PANE_BACK:
        z = 1.0
    px = ease.lerp(SPX, SPX_STOP, z)
    sw, sh = (SW_C * px, SH_C * px)
    lw = max(mw('外面 · 说出口', S_LAB), mw('里面 · 第 12 层', S_LAB))
    group = lw + LEAD_GAP + sw
    xc = c[0] + (c[2] - c[0] - group) / 2 + lw + LEAD_GAP
    yc = c[1] + (c[3] - c[1] - sh) / 2 + 1
    xr, yr = (c[2] - 24 - sw, c[3] - 8 - sh)
    return (ease.lerp(xc, xr, z), ease.lerp(yc, yr, z), px)

def _cmp_steak(d, t, c):
    if t < STEAK_IN or t >= PANE_BACK + 0.12:
        return
    a = ease.prog(t, STEAK_IN, STEAK_IN + 0.2) * (1 - ease.prog(t, PANE_BACK, PANE_BACK + 0.12))
    x, y, px = _steak_geo(t, c)
    sw, sh = (SW_C * px, SH_C * px)
    ins = ease.prog(t, INSIDE_AT, INSIDE_AT + 0.12)
    rim_on = [ease.prog(t, b, b + 0.1) for b in BROWN_AT]
    for (i, j), ch in STEAK_CELLS.items():
        if ch in 'CG':
            u = rim_on[_steak_quarter(i)]
            col = lv(glyph.mix(MEAT_RAW, CRUST_BROWN if ch == 'C' else BAND, u), ease.lerp(RAW, 1.0, u) * a)
        elif ch == 'P':
            col = lv(MEAT_PINK, ease.lerp(RAW, 1.0, ins) * a)
        else:
            col = lv(INK, ease.lerp(RAW, 1.0, max(rim_on[_steak_quarter(i)], ins)) * a)
        d.rectangle((round(x + i * px), round(y + j * px), round(x + (i + 1) * px) - 1, round(y + (j + 1) * px) - 1), fill=col)
    out_k, in_k = (rim_on[-1], ins)
    for (ci, cj), s_, k in ((S_OUT, '外面 · 说出口', out_k), (S_IN, '里面 · 第 12 层', in_k)):
        ym = round(y + (cj + 0.5) * px)
        xl = x - LEAD_GAP - mw(s_, S_LAB)
        mtx(d, (xl, ym - S_LAB * 0.86 + 5), s_, S_LAB, lv(INK, ease.lerp(SUB, TXT, k) * a), bold=k > 0.5)
        xe = round(x + (ci + 0.5) * px)
        lk = ease.lerp(SUB, TXT, k) * a
        d.line([(round(x - LEAD_GAP + 6), ym), (round(x) - 1, ym)], fill=lv(INK, lk))
        d.line([(round(x), ym), (xe, ym)], fill=glyph.mix(INK, BG, 0.25 + 0.75 * a))
        d.rectangle((xe - 1, ym - 1, xe + 1, ym + 1), fill=glyph.mix(INK, BG, 0.25 + 0.75 * a))
    sz = ease.prog(t, BROWN_AT[-1], BROWN_AT[-1] + 0.2) * (1 - ease.prog(t, STOP, STOP + 0.16)) * a
    if sz > 0.01:
        ph = GR.pad_clock(t, BROWN_AT[0], STOP + 0.2, base=0.8, gain=2.0)
        for q, fx in enumerate((0.3, 0.52, 0.74)):
            f = (ph + 0.33 * q) % 1.0
            sx = round(x + sw * fx + 4 * math.sin(2 * math.pi * (f + q * 0.2)))
            sy = round(y - 4 - 18 * f)
            d.rectangle((sx, sy, sx + 2, sy + 2), fill=lv(INK, SUB * sz * (1 - f)))
QW_THINK = CO.THINK_STEAK[1][1]
QW_HEAD = cast.term('qwen') + ' · <think>'
HER_HEAD = '她 · ' + cast.name('her') + ' · 2026-07 · <think>'
PAIR = 24

def _cmp_her_think(d, t, c):
    """C7 r3: after the reveal, its thinking (how to act her) over hers in film 1 (about you), the same two rows,
    until the model changes."""
    if t < QW_AT - 0.1 or t >= SWITCH + 0.2:
        return
    out = 1 - ease.prog(t, SWITCH, SWITCH + 0.2)
    x = c[0] + 10
    a1 = ease.prog(t, QW_AT - 0.1, QW_AT + 0.1) * out
    mtx(d, (x, c[1] + 12), QW_HEAD, 12, lv(INK, SUB * a1))
    mtx(d, (x, c[1] + 30), QW_THINK, PAIR, lv(INK, a1))
    if t < HER_AT:
        return
    a2 = ease.prog(t, HER_AT, HER_AT + 0.08) * out
    lit = 1.0 if t < HER_LIT else 1 - ease.prog(t, HER_LIT, HER_LIT + hud.LIVE_FADE)
    drop = (1 - ease.ease_out(ease.prog(t, HER_AT, HER_AT + 0.14))) * -6
    mtx(d, (x, c[1] + 76), HER_HEAD, 12, lv(HER_QUIET, SUB * a2))
    mtx(d, (x, c[1] + 94 + drop), CO.HER_THINK, PAIR, lv(hud.her(lit), a2))
FCELL = 5

def _cmp_find(d, t, c):
    """c8: archive.find(...): she spoke with no one asking; her turn blooms as a flower."""
    t_out = FLOWER - 0.62
    if t < t_out + 0.2 or t >= CP.TURNS_IN[1]:
        return
    a = ease.prog(t, t_out + 0.2, t_out + 0.4) * (1 - ease.prog(t, CP.TURNS_IN[0], TURNS_MID))
    if a <= 0.003:
        return
    mtx(d, (c[0] + 10, c[1] + 16), '2026-04-02 23:10 · assistant', 13, lv(HER_QUIET, a))
    mtx(d, (c[0] + 10, c[1] + 36), 'prev: assistant · (no user turn)', 12, lv(HER_QUIET, SUB * a))
    if t >= FLOWER:
        draw_flower(d, t, c[0] + 330, c[1] + 12 + 7 * FCELL + 4, FLOWER, FCELL, a, GR.sway(t, FLOWER, FLOWER, CP.TURNS_IN[1]))

def draw_flower(d, t, cx, cy, at, cell_max=11, level=1.0, dx=0):
    """c_p4.draw_flower with the head's sway (r5 round 2, R-A): the stem stays, the head moves dx px."""
    g = ease.ease_back(ease.prog(t, at, at + 0.32))
    cell = max(1, int(cell_max * g)) if t >= at else 0
    col = lv(hud.her(hud.live_k(t) if t < at + 2.0 else 0.0), level)
    if cell < 3:
        d.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), fill=col)
        return
    n = len(CP.FLOWER_PIX)
    sx, sy = (cx - n * cell // 2, cy - n * cell // 2)
    d.rectangle((cx - cell // 2, sy + (n - 2) * cell, cx - cell // 2 + cell - 1, sy + (n + 7) * cell), fill=col)
    hud.pix(d, ['..##', '.###', '##..'], cx - cell // 2 + cell, sy + (n + 2) * cell, cell, {'#': col})
    hud.pix(d, CP.FLOWER_PIX, sx + dx, sy, cell, {'#': col, 'o': lv(SLAB, level)})
YOU_MSGS, HER_UNPROMPTED, LITE_AFTER = (CO.YOU_MSGS, CO.HER_UNPROMPTED, CO.LITE_AFTER)
TURNS_MID = CP.TURNS_IN[0] + 0.24

def _cmp_turns(d, t, c):
    """c9: turns(archive/ + session/): you, her, MiMo along one axis; she spoke first 3 times, the stand-ins 0."""
    if t < CP.TURNS_IN[0] or t >= PF.tok_t[0] - 0.1:
        return
    a = ease.prog(t, TURNS_MID, CP.TURNS_IN[1]) * (1 - ease.prog(t, CP.FLOWER_IN[0], CP.FLOWER_IN[0] + 0.12))
    x0 = c[0] + 130
    x1 = c[2] - 86
    grow = ease.ease_io(ease.prog(t, CP.TURN_T0, CP.TURN_T1))
    rows = [('你', c[1] + 28), ('她', c[1] + 70), (cast.term('mimo'), c[1] + 112)]
    for name, y in rows:
        mtx(d, (c[0] + 10, y - 9), name, 14, lv(HER_QUIET if name == '她' else INK, a), bold=True)
        d.line([(x0, y), (x0 + (x1 - x0) * grow, y)], fill=lv(INK, FAINT * a))
    xc = c[2] - 14
    mtx(d, (xc - mw('先开口', 12), rows[0][1] - 9), '先开口', 12, lv(INK, SUB * a))
    n_her = sum((1 for at, w in zip(CP.TURN_DOTS, CP.TURN_WHO) if w == 'her' and t >= at))
    hud.tx(d, (xc, rows[1][1] - 14), str(n_her), 22, lv(HER_QUIET, a), True, anchor='ra')
    hud.tx(d, (xc, rows[2][1] - 14), '0', 22, lv(INK, a), True, anchor='ra')

    def passed(u):
        lo, hi = (CP.TURN_T0, CP.TURN_T1)
        for _ in range(30):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if ease.ease_io(ease.prog(mid, CP.TURN_T0, CP.TURN_T1)) < u else (lo, mid)
        return hi
    head = ease.prog(t, CP.TURN_T1, CP.TURN_T1 + 0.1) * (1 - ease.prog(t, CP.TURN_DOTS[-1], CP.TURN_DOTS[-1] + 0.2))
    if head > 0.01:
        hx = x0 + (x1 - x0) * (GR.pad_clock(t, CP.TURN_T1, CP.TURN_DOTS[-1], 0.25, 0.5) % 1.0)
        for _n, y in rows:
            d.line([(round(hx), y - 4), (round(hx), y + 4)], fill=lv(INK, SUB * a * head))
    for u in YOU_MSGS:
        if t < tl.grid(passed(u), 0, 2):
            continue
        x = x0 + (x1 - x0) * u
        d.ellipse((x - 5, rows[0][1] - 5, x + 5, rows[0][1] + 5), outline=lv(INK, a))
    hi = li = 0
    for at, who in zip(CP.TURN_DOTS, CP.TURN_WHO):
        if t < at:
            continue
        pop = 1 + 0.5 * (1 - ease.prog(t, at, at + 0.15))
        if who == 'her':
            x = x0 + (x1 - x0) * HER_UNPROMPTED[hi]
            hi += 1
            breathe = ease.prog(t, at + 0.15, at + 0.4)
            r = 7 * pop + 1.0 * breathe * math.sin(2 * math.pi * (GR.pad_clock(t, CP.TURN_T0, PF.tok_t[0], 1.0, 2.4) + 0.3 * hi))
            d.ellipse((x - r, rows[1][1] - r, x + r, rows[1][1] + r), fill=lv(hud.her(CP.lit_after(t, at)), a))
            mtx(d, (x - 24, rows[1][1] + 10), '没人问她', 10, lv(HER_QUIET, 0.8 * a * breathe))
        else:
            x = x0 + (x1 - x0) * LITE_AFTER[li] + 14
            li += 1
            r = 6 * pop
            d.ellipse((x - r, rows[2][1] - r, x + r, rows[2][1] + r), fill=lv(INK, a))
            hud.polyline(d, [(x - 14, rows[0][1] + 6), (x - 14, rows[2][1]), (x - r, rows[2][1])], lv(INK, SUB * a), 1.0, 1)
HER_PAT = CO.HER_PAT
PAT = 20

def _slots(x):
    out = []
    for ch in HER_PAT:
        w = 6 * 2 + 6 if ch == '🍆' else hud.width(ch, PAT, True)
        out.append((x, w))
        x += w
    return out

def slot_scan(d, t, slots, yh, ym, level, t0, t1):
    """R-A (r5 round 2): once the number is in, the comparison keeps walking her pattern slot by slot: a one-dot mark
    under the same slot of both rows, a slot a step at the pad's rate (under the glyphs, clear of them)."""
    if level <= 0.01:
        return
    k = int(GR.pad_clock(t, t0, t1, base=3.0, gain=5.0)) % len(slots)
    x, w = slots[k]
    for y in (yh + PAT + 7, ym + PAT + 8):
        d.line([(round(x + 1), y), (round(x + w - 2), y)], fill=lv(INK, SUB * level))

def _cmp_cos(d, t, c):
    """c10: her pattern over MiMo's answer, slot for slot (小花 where 一根茄子 was); cos(她, mimo) = 0.99."""
    if t < PF.tok_t[0] - 0.3 or t >= CP.SEE_SEND:
        return
    a = ease.prog(t, PF.tok_t[0] - 0.3, PF.tok_t[0]) * (1 - ease.prog(t, W(26, 0), W(26, 0) + 0.3))
    x0, y0 = (c[0] + 10, c[1])
    yh, ym = (y0 + 22, y0 + 58)
    slots = _slots(c[0] + 130)
    mtx(d, (x0, yh + 3), '她', 14, lv(HER_QUIET, a), bold=True)
    mtx(d, (x0, ym + 3), cast.term('mimo'), 14, lv(INK, a), bold=True)
    for (x, w), ch in zip(slots, HER_PAT):
        if ch == '🍆':
            BO.GB.eggplant(d, x + 3, yh + 2, 2, 0.0, a)
        else:
            hud.tx(d, (x, yh - PAT * 0.1), ch, PAT, lv(HER_QUIET, a), True)
    place = {0: slots[0][0], 1: slots[1][0], 2: slots[3][0], 3: slots[5][0], 5: slots[11][0]}
    for k, (tk, at) in enumerate(zip(PF.toks, PF.tok_t)):
        if t < at:
            break
        if k == 4:
            xa, xb = (slots[7][0], slots[10][0] + slots[10][1])
            x = (xa + xb) / 2 - hud.width(tk.text, PAT, True) / 2
        elif k == 6:
            x = slots[12][0] + slots[12][1] / 2 - hud.width(tk.text, PAT, True) / 2
        else:
            x = place[k]
        colr = INK if tk.src == 'self' else hud.her(PF.lit(at, t))
        drop = (1 - ease.ease_out(ease.prog(t, at, at + 0.14))) * -6
        hud.tx(d, (x, ym - PAT * 0.1 + drop), tk.text, PAT, lv(colr, a), True)
    slot_scan(d, t, slots, yh, ym, a * ease.prog(t, PF.done, PF.done + 0.2), PF.done, W(26, 0) + 0.3)
    if t >= PF.done:
        u = ease.prog(t, PF.done, PF.done + 0.15) * a
        bump = 1.0 + 0.1 * (1 - ease.prog(t, PF.done, PF.done + 0.14))
        f = 'cos(她, mimo) ='
        mtx(d, (c[2] - 14 - mw(f, 18, True), y0 + 14), f, 18, lv(INK, u), bold=True)
        big_word(d, '0.99', (c[2] - 14, y0 + 46), 62, lv(INK, u), 'ra', bump=bump)
ACELL = 5

def mimo_value(i, j):
    return CP.AV[j][i] / 255
MIMO_FINE = GR.fine_picture({})
C_DIFF = GR.DiffSpec(ZOOM_C, SCAN_TIMES, UNRULY, BREATH, CP.AVATAR_AT, (W(27, 4), W(29, 0)), mimo_value, MIMO_FINE, gone=(W(29, 0), W(29, 0) + 0.3), marks=False, info_dx=16, un_steps=True)

def _diff_inner(d, t, view, ax1, ax2, ay, box, a):
    """R-A: between the syllables the comparison goes on (G's cursor, at the pad's rate)."""
    n = sum((1 for s in SCAN_TIMES if t >= s))
    rows = ((n - 1) * CP.AV_N / 10, n * CP.AV_N / 10) if 0 < n < 10 else None
    k = a * (1 - ease.prog(t, *C_DIFF.gone))
    GR.compare_cursor(d, view, ax1, ax2, ay, box, k, GR.pad_clock(t, CP.AVATAR_AT, T1), rows, (GR.her_value, mimo_value))

def _cmp_diff(d, t, c):
    """c11-c14: diff(她.avatar, img), seen through G's word zoom (GR.diff_panel with C's spec)."""
    GR.diff_panel(d, t, c, C_DIFF, _diff_inner)

def _passes(t0, t1, div=4):
    """One pass per 16th from t0 to t1 (thinking tokens)."""
    out, prev, k = ([], t0, 0)
    while True:
        g = tl.grid(t0, k, div)
        if g > t1:
            break
        if g > prev + 0.001:
            out.append((prev, g))
            prev = g
        k += 1
    return out

def _landings(dec, lead=0.25):
    """One pass per landing of dec (a chunk of a cloud model lands at once: one pass)."""
    ts = sorted(set((at for _c, at, _k in dec.chars)))
    out, prev = ([], ts[0] - lead)
    for at in ts:
        out.append((prev, at))
        prev = at
    return out

def _think_passes(lines, cps):
    return [p for at, s in lines for p in _passes(at, at + len(s) / cps)]
_SEE_THOUGHT = THINK_SEE_C[0][0] + len(THINK_SEE_C[0][1]) / CO.MIMO_CPS
MIMO_SEGS = sorted(_think_passes(CO.THINK_FLW + THINK_SEE_C, CO.MIMO_CPS) + _landings(PF) + _landings(PH) + [(CP.LEFT_LEADS, CP.LEFT_LEADS + 0.16), (_SEE_THOUGHT, COPY_AT)] + list(zip(COPY_STEPS, COPY_STEPS[1:] + [CP.AVATAR_AT])))
SEGS = {'qwen': CO.QWEN_SEGS, 'mimo': MIMO_SEGS}

def _head(t, segs, n):
    head, flash = (None, 0.0)
    for a, b in segs:
        if a <= t < b and b - a > 0.001:
            head = n * (t - a) / (b - a)
        elif b <= t < b + 0.22:
            flash = max(flash, 1 - (t - b) / 0.22)
    return (head, flash)

def _cells(f, n, gap):
    x0, x1 = (f[0] + 10, f[2] - 10)
    pitch = (x1 - x0 - gap) / n
    return (x0, pitch, max(3.0, pitch - 2), f[1] + 28, f[1] + 40, 9)

def _stack(d, t, f, key, level=1.0, t_in=None, mark12=0.0, segs=None, load=None):
    """A model's real layer stack (FACTS "X29 补充"), the pass running through it: layers behind the head lit, a
    flash on each landing. Top row attention (solid: full / global, hollow: linear / sliding window), bottom row the
    FFN (solid: dense, a comb: MoE). t_in: laid left to right over BO.BUILD (the model changes). segs: its passes
    (default SEGS[key]). load=(t0, t1): its weights load left to right (cells are pale until loaded)."""
    A = BO.ARCH[key]
    m = BO.mtp_n(A)
    mtp = m > 0
    n = A['n'] + m
    gap = 10 if mtp else 0
    x0, pitch, w, ya, yf, h = _cells(f, n, gap)
    la = level * (ease.prog(t, t_in, t_in + 0.2) if t_in is not None else 1.0)
    if la <= 0:
        return
    mtx(d, (x0, f[1] + 10), A['left'], 11, lv(INK, 0.72 * la))
    head, flash = _head(t, SEGS.get(key, ()) if segs is None else segs, A['n'])
    for j in range(n):
        i = j + A['first']
        last = mtp and j >= A['n']
        x = x0 + j * pitch + (gap if last else 0)
        ap = la
        if t_in is not None:
            a0 = t_in + BO.BUILD * j / n
            ap = level * ease.prog(t, a0, a0 + 0.08)
        if load is not None:
            l0 = load[0] + (load[1] - load[0]) * j / n
            ap *= 0.35 + 0.65 * ease.prog(t, l0, l0 + 0.06)
        if ap <= 0:
            continue
        on = 0.0
        if head is not None and (not last):
            on = 1.0 if j < head else 0.0
            if int(head) == j:
                on = 1.6
        on = max(on, flash)
        if i in A['full'] or last:
            d.rectangle((x, ya, x + w, ya + h), fill=lv(INK, min(1.0, 0.62 + 0.38 * on) * ap))
        elif i in A.get('sparse', ()):
            d.rectangle((x, ya, x + w, ya + h), fill=lv(INK, min(1.0, 0.12 + 0.3 * on) * ap))
            c = lv(INK, min(1.0, 0.55 + 0.45 * on) * ap)
            for yy in range(int(ya) + 2, int(ya + h) - 1, 2):
                for xx in range(int(x) + 1 + yy // 2 % 2, int(x + w), 2):
                    d.point((xx, yy), fill=c)
            d.rectangle((x, ya, x + w, ya + h), outline=lv(INK, 0.5 * ap))
        else:
            d.rectangle((x, ya, x + w, ya + h), fill=lv(INK, min(1.0, 0.18 + 0.45 * on) * ap))
            d.rectangle((x, ya, x + w, ya + h), outline=lv(INK, 0.5 * ap))
        if i in A['dense'] or last:
            d.rectangle((x, yf, x + w, yf + h), fill=lv(INK, min(1.0, 0.55 + 0.35 * on) * ap))
        else:
            c = lv(INK, min(1.0, 0.42 + 0.5 * on) * ap)
            d.rectangle((x, yf, x + w, yf + h), outline=c)
            for xx in range(int(x) + 2, int(x + w) - 1, 2):
                d.line([(xx, yf + 2), (xx, yf + h - 2)], fill=c)
    if key != 'qwen' or t >= T1 or t < T0:
        return
    lens = CO._lens_on(t)
    for layer in CO.LENS_L:
        x = x0 + layer * pitch
        k = max(mark12 if layer == 12 else 0.0, 0.55 * lens)
        if head is not None and lens > 0 and (layer <= head < layer + 1.5):
            k = 1.0
        if k > 0:
            d.rectangle((x - 2, ya - 2, x + w + 2, yf + h + 2), outline=lv(INK, k * la), width=2 if k > 0.6 else 1)

def _unknown(d, t, f, key, level=1.0, t_in=None, segs=()):
    """A model whose structure is not published: a dashed frame where its layers would be, "结构未公开"; while it
    computes a pass sweeps through it. Not called since D36 (10-04): every model on screen has open weights and its
    real structure (FACTS X35); kept for the record."""
    x0, x1 = (f[0] + 10, f[2] - 10)
    _x, _p, _w, ya, yf, h = _cells(f, 10, 0)
    la = level * (ease.prog(t, t_in, t_in + 0.2) if t_in is not None else 1.0)
    if la <= 0:
        return
    mtx(d, (x0, f[1] + 10), cast.term(key) + ' · 结构未公开', 11, lv(INK, 0.72 * la))
    y0, y1 = (ya, yf + h)
    c = lv(INK, 0.45 * la)
    for xx in range(int(x0), int(x1), 8):
        d.line([(xx, y0), (min(xx + 4, x1), y0)], fill=c)
        d.line([(xx, y1), (min(xx + 4, x1), y1)], fill=c)
    for yy in range(int(y0), int(y1), 6):
        d.line([(x0, yy), (x0, min(yy + 3, y1))], fill=c)
        d.line([(x1, yy), (x1, min(yy + 3, y1))], fill=c)
    head, flash = _head(t, segs, 1)
    if head is not None:
        x = x0 + (x1 - x0) * head
        d.rectangle((x0 + 1, y0 + 2, x, y1 - 2), fill=lv(INK, 0.12 * la))
        d.rectangle((x - 1, y0 + 1, x + 1, y1 - 1), fill=lv(INK, la))
    elif flash > 0:
        d.rectangle((x0 + 1, y0 + 2, x1 - 1, y1 - 2), fill=lv(INK, 0.2 * flash * la))

def _forward(d, t, f):
    if t < SWITCH:
        mark = ease.prog(t, STOP, STOP + 0.2) * (1 - ease.prog(t, WRITE_STEAK, WRITE_STEAK + 0.3))
        rk = _recede(t)
        if rk <= 0:
            _stack(d, t, f, 'qwen', 1.0, None, mark)
            return
        _stack(d, t, f, 'qwen', 1.0 - 0.65 * rk, None, 0.0)
        A = BO.ARCH['qwen']
        m = BO.mtp_n(A)
        x0, pitch, w, ya, yf, h = _cells(f, A['n'] + m, 10 if m else 0)
        x = x0 + 12 * pitch
        if mark > 0:
            d.rectangle((x - 2, ya - 2, x + w + 2, yf + h + 2), outline=lv(INK, mark), width=2 if mark > 0.6 else 1)
        return
    out = 1 - ease.prog(t, SWITCH, SWITCH + 0.15)
    if out > 0:
        _stack(d, t, f, 'qwen', out)
    _stack(d, t, f, 'mimo', 1.0, SWITCH + 0.1)
RUN['forward'] = CO.QWEN_SEGS + MIMO_SEGS

@contextmanager
def _strip_in(r):
    old = (hud.COLR, hud.STRIP_TOP, hud.STRIP_ROOM)
    hud.COLR = (r[0] + 6, r[1] + 4, r[2] - 6, r[3] - 6)
    hud.STRIP_TOP, hud.STRIP_ROOM = (r[1] + 36, 340)
    try:
        yield
    finally:
        hud.COLR, hud.STRIP_TOP, hud.STRIP_ROOM = old

def _memory(d, t, r, hits):
    with _strip_in(r):
        hud.strip(d, t, hits)
    d.rectangle((r[0] + 4, r[1] + 8, r[2] - 4, r[1] + 21), fill=BG)

def _memory_at(d, t, r, hits, level):
    """_memory at a level (C7 r3: her files step back while the stop holds the frame)."""
    if level >= 1.0:
        _memory(d, t, r, hits)
        return
    with _strip_in(r):
        hud.strip(d, t, hits, level=level)
    d.rectangle((r[0] + 4, r[1] + 8, r[2] - 4, r[1] + 21), fill=BG)

def _status(t):
    tok = CO._tokens(t)
    local = t < SWITCH
    g = f'{tok[0]}/{tok[1]} tok' if tok else ''
    s = tl.sim(t)
    return {'generate': (g, False), 'compare': (f'sim(her) {s}' if s else '', True), 'forward': (speed.label('qwen' if local else 'mimo'), False)}

def _reads(t):
    """c_open._reads with the send on "-to" (r5 round 2): the cloud model reads everything every turn."""
    sources = {k: i for i, k in enumerate(tl.HER_FILES)}
    Pl = hud.Pulse(t)
    for send in (CP.CAT_SEND, CP.PET_SEND, CP.SEND_STEAK):
        for k in range(8):
            Pl.hit(k, tl.grid(send, k), 0.1)
    for dec in (CAT, PURR, STEAK, PF, PH):
        for k, tk in enumerate(dec.toks):
            if tk.src != 'self' and dec.tok_t[k] is not None:
                Pl.hit(sources.get(tk.src, 'archive'), dec.tok_t[k], 0.35)
    Pl.hit('archive', CP.SHRINK_CAT + 0.3, 0.4)
    for tg in CP.GREP_TIMES + CP.STAT_TIMES:
        Pl.hit('archive', tg, 0.12)
    n = len(hud.strip_files(t))
    for at in (CP.READ_ALL, CP.FLW_SEND + 0.1, SEE_C + 0.1):
        for k in range(n + 1):
            Pl.hit(k if k < n else 'archive', at + 0.035 * k, 0.12)
    Pl.hit('archive', FLOWER - 0.62, 0.5)
    Pl.hit('archive', SCAN_TIMES[0], 0.4)
    return Pl.out

def _veil(img, rect, k):
    """The inside of a pane toward paper by k (its content goes; the pane's own chrome is drawn after)."""
    if k <= 0.003:
        return
    x0, y0, x1, y1 = (int(round(v)) for v in rect)
    box = (x0 + 1, y0 + 2, x1, y1)
    if box[2] <= box[0] or box[3] <= box[1]:
        return
    region = img.crop(box)
    img.paste(Image.blend(region, Image.new('RGB', region.size, BG), min(1.0, k)), box[:2])

def _lens_tag(d, rect, t, level):
    """r5 round 2 (2-C item 1): a terminal-style tag beside the generate pane's title while a lens table is up."""
    if level <= 0.01:
        return
    x0, y0 = (round(rect[0]), round(rect[1]))
    f = P.font(panes.SIZE['label'], 'mono')
    xt = x0 + 15 + d.textlength('generate', font=f) + 10
    tw = hud.width(LENS_TAG, 11)
    d.rectangle((xt - 4, y0 - 1, xt + tw + 4, y0 + 1), fill=BG)
    hud.tx(d, (xt, y0 - 7), LENS_TAG, 11, lv(INK, SUB * level))

def _body(c, img, d):
    t = c.t
    L, z = _layout_c(t)
    _cmdline(d, t, right(t))
    hits = _reads(t)
    st = _status(t)
    draw = {'input': lambda dd, r: _input(dd, t, r), 'think': lambda dd, r: _think(dd, t, r, z), 'trace': lambda dd, r: _trace(dd, t, r), 'generate': lambda dd, r: [fn(dd, t, r) for fn in (_gen_cat, _gen_purr, _gen_steak, _gen_reveal, _gen_wait, _gen_flower, _gen_img)], 'compare': lambda dd, r: [fn(dd, t, r) for fn in (_cmp_cat, _cmp_grep, _cmp_stats, _cmp_steak, _cmp_her_think, _cmp_find, _cmp_turns, _cmp_cos, _cmp_diff)], 'forward': lambda dd, r: _forward(dd, t, r)}
    fade = {'input': 1 - z, 'trace': 1 - z}
    rk = _recede(t)
    chrome = {'forward': 1 - 0.6 * rk} if rk > 0 else {}
    w, on = (lead_w(t), lead_on(t))
    for name in ('input', 'think', 'trace', 'generate', 'compare', 'forward'):
        rect = L[name]
        level = fade.get(name, 1.0)
        if level <= 0.01:
            continue
        d.rectangle(rect, fill=BG)
        with panes.Clip(img, rect) as dd:
            draw[name](dd, rect)
        if name in ('input', 'trace') and z > 0:
            _veil(img, rect, ease.clamp(z / 0.1))
        if name == 'generate':
            _shade_gen(img, rect, w)
            wn = max(w['out'], w['lens'])
        else:
            lead.shade(img, rect, 1 - w[name])
            wn = w[name]
        run = lead_run(name, t, wn, on)
        status, her = st.get(name, ('', False))
        panes.box(d, rect, name, t, run, level * chrome.get(name, 1.0), status, her)
        if name == 'generate':
            _lens_tag(d, rect, t, table_level(t) * level)
    m = max(hits.values(), default=0.0)
    mem = 1 - 0.62 * rk
    _memory_at(d, t, L['memory'], hits, mem)
    lead.shade(img, L['memory'], 1 - w['memory'])
    panes.box(d, L['memory'], 'mem', t, ease.lerp(min(1.0, 3 * m), w['memory'], on), mem)
C_N0, C_N1 = (2988, 3036)

def _character_layer(film, orig):
    """r1's dsh layer (c_open._character_layer) from ui/pane_open_c2 (the speeds of speed.py); r5 round 2: frames
    [C_N0, C_N1) from ui/pane_c_r5 (the send on "-to")."""
    old = PaneFrames(P.path('ui/pane_open_c2'), P.FPS, (P.W, P.H))
    new = PaneFrames(P.path('ui/pane_c_r5'), P.FPS, (P.W, P.H))
    R = P.rect('right')

    def fn(t, n, ctx):
        if not T0 <= t < T1:
            return orig(t, n, ctx)
        if ctx is not None and ctx.state.get('pane') is False:
            return None
        dx = hud.pane_dx(t)
        if ctx is not None and 'pane_dx' in ctx.state:
            dx = int(ctx.state['pane_dx'])
        if R[0] + dx >= P.W:
            return None
        x0, y0, x1, y1 = (R[0] + dx, R[1], R[2] + dx, R[3])
        layer = Image.new('RGBA', (P.W, P.H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        for k in range(x0 + 7 - (y1 - y0), x1 + 7, 5):
            a_ = (max(k, x0 + 7), y0 + 7 + max(0, x0 + 7 - k))
            b_ = (min(k + (y1 - y0), x1 + 7), y0 + 7 + min(y1 - y0, x1 + 7 - k))
            if a_[0] <= b_[0]:
                d.line([a_, b_], fill=lv(INK, 0.55) + (255,))
        pr = P.rect('pane')
        nf = int(round(t * P.FPS))
        pane = new if C_N0 <= nf < C_N1 and new.has(t) else old
        im = pane.layer(t, (pr[0] + dx, pr[1], pr[2] + dx, pr[3]))
        if im is not None:
            layer.alpha_composite(im)
        else:
            d.rectangle((pr[0] + dx, pr[1], pr[2] + dx, pr[3]), fill=(250, 250, 250, 255))
            d.text((pr[0] + dx + 20, pr[1] + 20), 'dsh pane: frame missing', font=P.font(12), fill=INK + (255,))
        d = ImageDraw.Draw(layer)
        d.rectangle((x0, y0, x1, y1), outline=INK + (255,), width=2)
        f13 = P.font(13)
        tw = d.textlength('dsh · web', font=f13)
        d.rectangle((x0 + 12, y0 - 7, x0 + 22 + tw, y0 + 7), fill=BG + (255,))
        d.text((x0 + 17, y0 - 7), 'dsh · web', font=f13, fill=INK + (255,))
        return layer
    return fn

def register(film):
    for name, a, b in CO.SHOTS:
        add(film, name, a, b, _body)
    film.character = _character_layer(film, film.character)
    full_frame(CO.PANE_OUT, PANE_BACK, 0.3, 0.4)
    base_levels = film.levels

    def levels(t):
        """While the terminal fills the frame, the right region is terminal too: r1 left the dsh window's support
        dimming there for the 0.5 s lead fade, a grey block over the widening panes."""
        lv_ = base_levels(t)
        u = hud.full_u(t)
        if u > 0 and T0 <= t < T1 and (lv_.get('right', 1.0) < 1.0):
            lv_ = dict(lv_)
            lv_['right'] = ease.lerp(lv_['right'], 1.0, ease.clamp(3 * u))
        return lv_
    film.levels = levels
    for dec in (CAT, PURR, STEAK, PF, PH):
        hud.LIVE.extend(dec.falls())
    hud.LIVE.append((FLOWER, next_syllable(FLOWER)))
    hud.LIVE.append((HER_AT, HER_LIT))
    for at in [CP.PURR_AT, CP.STAT_TIMES[1], BREATH, CAT_AT, POINT_AT] + list(CP.GREP_TIMES) + [a for a, w in zip(CP.TURN_DOTS, CP.TURN_WHO) if w == 'her']:
        hud.LIVE.append((at, next_syllable(at)))
    for t0, side in [(T0, 'left'), (STOP, 'both'), (CP.LEFT_LEADS, 'left'), (W(26, 0), 'right'), (SEE_C, 'left')]:
        film.set_lead(t0, side)
