"""Group C, third sample r2 (sample_open_c/README.md §8): r1's content (groups/c_open.py) laid out in named panes.

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
from contextlib import contextmanager
import cast
import hud
import panes
import prompt_ids
import speed
import syl
import tl
from groups import b_open as BO
from groups import c_open as CO
from groups import c_p4 as CP
from groups.base import add, big_word, full_frame
from hud import BG, HER_QUIET, INK, SLAB, lv
from inspect_ import next_syllable
from panes import FAINT, SUB, TXT
from tuikit import ease, glyph
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

def _think_end(at, s):
    return at + len(s) / (CO.MIMO_CPS if at >= SWITCH else CO.THINK_CPS) + 0.2
THINKS = sorted(CO.THINK_CAT + CO.THINK_PET + CO.THINK_STEAK + CO.THINK_FLW + CO.THINK_SEE)
CODE = [(at, s) for at, kind, s in CO.TRACE if kind == 'code']

def _code_end(at, s):
    ret = CO.RET.get((at, 'code'))
    return ret[0] if ret else at + len(s) / CO.CODE_CPS + 0.25
REVEAL_AT = CO.REVEAL_AT
RUN = {'input': [(c[0][0], s + 0.15) for c, s in CO.TURNS], 'think': [(at, _think_end(at, s)) for at, s in THINKS], 'trace': [(at, _code_end(at, s)) for at, s in CODE], 'generate': [(CAT.start, CAT.done), (PURR.start, PURR.done), (STEAK.start, STEAK.eos_at), (STOP, TAIL_AT + 0.1), (CP.LEFT_LEADS, CP.LEFT_LEADS + 0.16), (PF.tok_t[0] - 0.3, PF.done), (CP.SEE_SEND, CP.AVATAR_AT), (PH.start, PH.done)], 'compare': [(CP.SHRINK_CAT + 0.2, CP.GREP_TIMES[-1] + 0.1), (CP.STAT_TIMES[0], CP.PURR_AT + 0.1), (CMP_IN, HER_LIT), (FLOWER - 0.62, FLOWER + 0.1), (CP.TURN_T0, CP.TURN_DOTS[-1] + 0.1), (PF.tok_t[0], PF.done + 0.1), (SCAN_TIMES[0], UNRULY[0] + 0.1)], 'forward': []}

def _input(d, t, r):
    cur = 0
    for k, (commits, _s) in enumerate(CO.TURNS):
        if t >= commits[0][0]:
            cur = k
    commits, send = CO.TURNS[cur]
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
        a = {0: TXT, 1: SUB}.get(pos, SUB * (1 - sc))
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
            mtx(d, (r[0] + 10, y), s[:n], size, lv(INK, a), bold=pos == 0 and z > 0.5)
        if pos == 0 and s == CO.DONT and (t >= SETTLE) and (t < SWITCH):
            _dont_box(d, t, r[0] + 10, y, size, z > 0.5)

def _trace(d, t, r):
    shown = [(at, s) for at, s in CODE if at <= t]
    if not shown:
        return
    last = shown[-1][0]
    sc = ease.ease_out(ease.prog(t, last, last + 0.14))
    for pos, (at, s) in enumerate(reversed(shown[-4:])):
        y = r[1] + 47 - pos * 19 + (1 - sc) * 19
        a = {0: TXT, 1: SUB, 2: FAINT}.get(pos, FAINT * (1 - sc))
        if pos == 0:
            a *= ease.prog(t, at, at + 0.1)
        n = int((t - at) * CO.CODE_CPS) + 1
        w = mtx(d, (r[0] + 10, y), s[:n], 14, lv(INK, 0.92 * a), bold=pos == 0)
        ret = CO.RET.get((at, 'code'))
        if ret and t >= ret[0]:
            u = ease.prog(t, ret[0], ret[0] + 0.1)
            mtx(d, (r[0] + 10 + w + 12, y), '→ ' + ret[1], 14, lv(INK, 0.7 * a * u), bold=True)
OUT, GUESS = (30, 20)

class PLens(CO.Lens):
    """r1's lens, laid out inside the generate pane (out 30 px, the guesses 20 px)."""

    def __init__(self, dec, key, start, lx):
        super().__init__(dec, key, start)
        self.x, x = ([], lx)
        for c, _a, _k in dec.chars:
            self.x.append(x)
            x += hud.width(c, OUT, True)
        self.x_end = x

    def col_x(self, j):
        if j < len(self.sung):
            i = self.sung[j]
            return self.x[i] + hud.width(self.dec.chars[i][0], OUT, True) / 2
        return self.x_end + 34

    def draw_p(self, d, t, g, level=1.0, rows=1.0):
        if level <= 0:
            return
        y_out, y24, y12 = (g[1] + 14, g[1] + 62, g[1] + 90)
        a = level * ease.prog(t, self.start - 0.3, self.start)
        mtx(d, (g[0] + 10, y_out + 10), 'out', 12, lv(INK, SUB * a))
        mtx(d, (g[0] + 10, y24 + 4), 'L24', 12, lv(INK, FAINT * a * rows))
        mtx(d, (g[0] + 10, y12 + 4), 'L12', 12, lv(INK, FAINT * a * rows))
        for j in range(len(self.passes)):
            cx = self.col_x(j)
            for layer, text, y in ((12, self.l12, y12), (24, self.l24, y24)):
                at = self.at_layer(j, layer)
                if t < at or j >= len(text):
                    continue
                lit = 1 - ease.prog(t, at + 0.12, at + 0.42)
                ch = text[j]
                w = hud.width(ch, GUESS, True)
                hud.tx(d, (cx - w / 2, y), ch, GUESS, lv(INK, (0.4 + 0.5 * lit) * level * rows), bold=lit > 0.5)
        for i, (c, at, k) in enumerate(self.dec.chars):
            if t < at:
                break
            drop = (1 - ease.ease_out(ease.prog(t, at, at + 0.14))) * -6
            hud.tx(d, (self.x[i], y_out - OUT * 0.1 + drop), c, OUT, lv(self.dec.color(k, at, t), level), bold=True)
        if self.dec.eos_at is not None and t >= self.dec.eos_at:
            _eos(d, t, self.x_end + 10, y_out + 6, self.dec.eos_at, level)

    def cands_p(self, d, t, g, level=1.0):
        shown = None
        for k, tk in enumerate(self.dec.toks):
            at = self.dec.tok_t[k]
            if tk.cands and at is not None and (at - 0.3 <= t):
                shown = (k, at)
        if shown is None or level <= 0:
            return
        k, at = shown
        _cands(d, t, (g[0] + 10, g[1] + 122), 'p(next)', self.dec.toks[k].cands, self.dec.toks[k].pick, at, g[2] - 10, level * ease.prog(t, at - 0.3, at))

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

def _gen_cat(d, t, g):
    if t < CAT.start - 0.3 or t >= CP.PET_SEND:
        return
    settle = ease.prog(t, CP.SHRINK_CAT, CP.SHRINK_CAT + 0.35)
    level = (1 - (1 - SUB) * settle) * (1 - ease.prog(t, CP.PET_SEND - 0.3, CP.PET_SEND))
    LC.draw_p(d, t, g, level, 1 - settle)
    if t < CP.CAT_PIX_AT + 0.3:
        LC.cands_p(d, t, g, 1 - ease.prog(t, CP.CAT_PIX_AT, CP.CAT_PIX_AT + 0.3))
    if t >= CP.CAT_PIX_AT:
        k = ease.ease_back(ease.prog(t, CP.CAT_PIX_AT, CP.CAT_PIX_AT + 0.25))
        cc = max(1, int(3 * k))
        if k > 0.05:
            hud.pix(d, CP.CAT_PIX, LC.x_end + 12, g[1] + 10, cc, {'I': lv(INK, level), 'B': lv(hud.her(CAT.lit(CAT.done, t)), level)})

def _gen_purr(d, t, g):
    if t < PURR.start or t >= CP.SAMPLE_T0:
        return
    a = 1 - ease.prog(t, CP.SAMPLE_T0 - 0.35, CP.SAMPLE_T0)
    mtx(d, (g[0] + 10, g[1] + 24), 'out', 12, lv(INK, SUB * a))
    _row(d, t, PURR, LX, g[1] + 14, OUT, a)

def _gen_steak(d, t, g):
    if t < STEAK.start - 0.3 or t >= STOP + 0.16:
        return
    if t < STOP:
        a = 1 - ease.ease_io(ease.prog(t, STOP, STOP + 0.16))
        LS.draw_p(d, t, g, a)
        LS.cands_p(d, t, g, a)
        return
    a = 1 - ease.ease_io(ease.prog(t, STOP, STOP + 0.16))
    _lens_rows(d, t, g, a)
    LS.cands_p(d, t, g, a)

def _lens_rows(d, t, g, level):
    """PLens.draw_p's two guess rows (L24 / L12) alone."""
    y24, y12 = (g[1] + 62, g[1] + 90)
    a = level * ease.prog(t, LS.start - 0.3, LS.start)
    mtx(d, (g[0] + 10, y24 + 4), 'L24', 12, lv(INK, FAINT * a))
    mtx(d, (g[0] + 10, y12 + 4), 'L12', 12, lv(INK, FAINT * a))
    for j in range(len(LS.passes)):
        cx = LS.col_x(j)
        for layer, text, y in ((12, LS.l12, y12), (24, LS.l24, y24)):
            at = LS.at_layer(j, layer)
            if t < at or j >= len(text):
                continue
            lit = 1 - ease.prog(t, at + 0.12, at + 0.42)
            ch = text[j]
            w = hud.width(ch, GUESS, True)
            hud.tx(d, (cx - w / 2, y), ch, GUESS, lv(INK, (0.4 + 0.5 * lit) * level), bold=lit > 0.5)
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
    dx = (X_IN - LX) * ease.ease_io(ease.prog(t, STOP, STOP + ZOOM_IN))
    y_out = y0 + 14
    lo, la = (ease.prog(t, STOP, STOP + 0.06), ease.prog(t, STOP + 0.06, STOP + 0.16))
    if lo < 1:
        mtx(d, (x0 + 10, y_out + 10), 'out', 12, lv(INK, SUB * (1 - lo) * gone))
    if la > 0:
        mtx(d, (x0 + 10, y_out + 10), 'sent', 12, lv(INK, SUB * la * gone), bold=True)
    for i, (c, at, k) in enumerate(STEAK.chars):
        hud.tx(d, (LS.x[i] + dx, y_out - OUT * 0.1), c, OUT, lv(STEAK.color(k, at, t), gone), bold=True)
    xe = LS.x_end + dx + 10
    _eos(d, t, xe, y_out + 6, STEAK.eos_at, gone)
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
        if tl.C.beat_of(t) % 1.0 < 0.5 or t - pick < 0.3:
            d.rectangle((g[0] + 16 + w, g[1] + 56, g[0] + 21 + w, g[1] + 116), fill=lv(INK, a))

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

def _gen_img(d, t, g):
    """c11-c14: the image it sends back, then its reply beside it."""
    if t < CP.AVATAR_AT:
        return
    a = ease.prog(t, CP.AVATAR_AT, CP.AVATAR_AT + 0.2)
    x, y = (LX, g[1] + 16)
    CP.avatar(d, x, y, GCELL, stray=False, level=a)
    mtx(d, (g[0] + 10, g[1] + 24), 'img', 12, lv(INK, SUB * a))
    xr = x + CP.AV_N * GCELL + 20
    mtx(d, (xr, y), 'image/png · 120×120', 12, lv(INK, SUB * a))
    if t >= PH.start:
        _row(d, t, PH, xr, y + 40, OUT)
HER_DAYS = CO.HER_DAYS

def _cmp_grep(d, t, c):
    """c3: count("喵") by day: her days jagged, its replies one each."""
    if t < CP.SHRINK_CAT + 0.2 or t >= CP.PET_SEND:
        return
    a = ease.prog(t, CP.SHRINK_CAT + 0.2, CP.SHRINK_CAT + 0.4) * (1 - ease.prog(t, CP.PET_SEND - 0.3, CP.PET_SEND))
    x0, y0 = (c[0] + 10, c[1])
    base_h, base_q = (y0 + 70, y0 + 116)
    mtx(d, (x0, base_h - 30), '她 · archive/', 13, lv(HER_QUIET, a))
    mtx(d, (x0, base_h - 12), '每天几个「喵」', 12, lv(HER_QUIET, SUB * a))
    mtx(d, (x0, base_q - 30), cast.term('qwen') + ' · session/', 13, lv(INK, a))
    mtx(d, (x0, base_q - 12), '每条回答一个', 12, lv(INK, SUB * a))
    bx0, bw, gap = (c[0] + 250, 5, 8)
    for gi, tg in enumerate(CP.GREP_TIMES):
        u = ease.ease_out(ease.prog(t, tg, tg + 0.16))
        hc = hud.her(CP.lit_after(t, tg))
        gx = bx0 + gi * (6 * (bw + gap) + 18)
        for di, v in enumerate(HER_DAYS[gi]):
            bx = gx + di * (bw + gap)
            if u > 0:
                d.rectangle((bx, base_h - int(4 * v * u), bx + bw - 1, base_h), fill=lv(hc, a))
                d.rectangle((bx, base_q - int(24 * u), bx + bw - 1, base_q), fill=lv(INK, a))
        if u > 0:
            d.text((gx, base_q + 4), ['03-14', '03-21', '03-28', '04-04'][gi], font=P.font(10), fill=lv(INK, SUB * u * a))
    for y in (base_h + 1, base_q + 1):
        d.line([(bx0, y), (c[2] - 14, y)], fill=lv(INK, FAINT * a))
STATS = ('喵', '报错', '呼噜')

def _cmp_stats(d, t, c):
    """c4: count(她, ["喵", "报错", "呼噜"]): her and it side by side, one column a word."""
    if t < CP.STAT_TIMES[0] or t >= CP.SAMPLE_T0:
        return
    a = ease.prog(t, CP.STAT_TIMES[0], CP.STAT_TIMES[0] + 0.12) * (1 - ease.prog(t, CP.SAMPLE_T0 - 0.35, CP.SAMPLE_T0))
    x0, y0 = (c[0] + 10, c[1])
    cols = (c[0] + 200, c[0] + 340, c[0] + 480)
    rows = (y0 + 46, y0 + 92)
    mtx(d, (x0, rows[0] + 8), '她 · archive/', 13, lv(HER_QUIET, a))
    mtx(d, (x0, rows[1] + 8), cast.term('qwen'), 13, lv(INK, a))
    got = PURR.text_at(t)
    for k, name in enumerate(STATS):
        ts = CP.STAT_TIMES[k + 1]
        u = ease.prog(t, ts, ts + 0.12) * a
        if u <= 0:
            continue
        mtx(d, (cols[k], y0 + 14), name, 14, lv(INK, SUB * u), bold=True)
        if k < 2:
            val, colr = ('312', hud.her(CP.lit_after(t, ts))) if k == 0 else ('47', INK)
            hud.tx(d, (cols[k], rows[0]), val, 28, lv(colr, u), True)
        else:
            landed = t >= CP.PURR_AT
            hud.tx(d, (cols[k], rows[0]), '0' if landed else '—', 28, lv(hud.her(CP.lit_after(t, CP.PURR_AT)) if landed else INK, u if landed else FAINT * u), True)
        if t >= PURR.tok_t[0]:
            q = {'喵': got.count('喵'), '报错': 0, '呼噜': got.count('呼噜')}[name]
            hud.tx(d, (cols[k], rows[1]), str(q), 28, lv(INK, u), True)
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
    a = ease.prog(t, t_out + 0.2, t_out + 0.4) * (1 - ease.prog(t, CP.TURNS_IN[0], CP.TURNS_IN[1]))
    mtx(d, (c[0] + 10, c[1] + 16), '2026-04-02 23:10 · assistant', 13, lv(HER_QUIET, a))
    mtx(d, (c[0] + 10, c[1] + 36), 'prev: assistant · (no user turn)', 12, lv(HER_QUIET, SUB * a))
    if t >= FLOWER:
        CP.draw_flower(d, t, c[0] + 330, c[1] + 12 + 7 * FCELL + 4, FLOWER, FCELL, level=a)
YOU_MSGS, HER_UNPROMPTED, LITE_AFTER = (CO.YOU_MSGS, CO.HER_UNPROMPTED, CO.LITE_AFTER)

def _cmp_turns(d, t, c):
    """c9: turns(archive/ + session/): you, her, MiMo along one axis; she spoke first 3 times, the stand-ins 0."""
    if t < CP.TURNS_IN[0] or t >= PF.tok_t[0] - 0.1:
        return
    a = ease.prog(t, CP.TURNS_IN[0], CP.TURNS_IN[1]) * (1 - ease.prog(t, CP.FLOWER_IN[0], CP.FLOWER_IN[0] + 0.12))
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
            r = 7 * pop
            d.ellipse((x - r, rows[1][1] - r, x + r, rows[1][1] + r), fill=lv(hud.her(CP.lit_after(t, at)), a))
            mtx(d, (x - 24, rows[1][1] + 10), '没人问她', 10, lv(HER_QUIET, 0.8 * a))
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
    if t >= PF.done:
        u = ease.prog(t, PF.done, PF.done + 0.15) * a
        bump = 1.0 + 0.1 * (1 - ease.prog(t, PF.done, PF.done + 0.14))
        f = 'cos(她, mimo) ='
        mtx(d, (c[2] - 14 - mw(f, 18, True), y0 + 14), f, 18, lv(INK, u), bold=True)
        big_word(d, '0.99', (c[2] - 14, y0 + 46), 62, lv(INK, u), 'ra', bump=bump)
ACELL = 5

def _cmp_diff(d, t, c):
    """c11-c14: diff(她.avatar, img): a tenth a syllable; her one stray hair is the 1 cell."""
    if t < CP.AVATAR_AT:
        return
    a = ease.prog(t, CP.AVATAR_AT, CP.AVATAR_AT + 0.3)
    n = sum((1 for s in SCAN_TIMES if t >= s))
    scan = n * CP.AV_N / 10 if n < 10 else None
    side = CP.AV_N * ACELL
    ax1, ay = (c[0] + 46, c[1] + 12)
    ax2 = ax1 + side + 50
    mtx(d, (c[0] + 10, ay + 4), '她', 14, lv(HER_QUIET, a), bold=True)
    CP.avatar(d, ax1, ay, ACELL, stray=True, level=a, scan=scan)
    mtx(d, (ax1 + side + 12, ay + 4), 'img', 12, lv(INK, SUB * a))
    CP.avatar(d, ax2, ay, ACELL, stray=False, level=a, scan=scan)
    if n:
        mtx(d, (ax2 + side + 16, ay + side - 14), f'已比 {min(10, n) * CP.AV_N // 10}/{CP.AV_N} 行', 12, lv(INK, SUB * a))
    steps = sum((1 for s in UNRULY if t >= s))
    if steps:
        i, j = CP.STRAY
        x, y = (ax1 + i * ACELL, ay + (j - 1) * ACELL)
        r = 3 + 14 * (1 - steps / 3)
        d.rectangle((x - r, y - r, x + ACELL + r, y + ACELL + r), outline=lv(INK, a), width=2)
        if steps >= 3:
            x2 = ax2 + i * ACELL
            d.rectangle((x2 - 3, y - 3, x2 + ACELL + 3, y + ACELL + 3), outline=lv(INK, SUB * a))
    if t >= UNRULY[0]:
        bump = 1.0 + 0.12 * (1 - ease.prog(t, UNRULY[0], UNRULY[0] + 0.12))
        f = 'diff(她, img) ='
        box = big_word(d, '1', (c[2] - 24, c[1] + 14), 96, INK, 'ra', bump=bump)
        mtx(d, (box[0] - mw(f, 18, True) - 18, (box[1] + box[3]) / 2 - 11), f, 18, lv(INK, 1.0), bold=True)
    if t >= BREATH:
        hc = hud.her(CP.lit_after(t, BREATH))
        for k, (dx, dy, r) in enumerate(((0, 0, 4), (12, -12, 6))):
            u = ease.ease_out(ease.prog(t, BREATH + 0.12 * k, BREATH + 0.12 * k + 0.7))
            x = ax1 + 15 * ACELL + dx + 10 * u
            y = ay + 16 * ACELL + dy - 50 * u
            if u < 1:
                d.ellipse((x - r, y - r, x + r, y + r), outline=lv(hc, 1 - u * 0.6), width=2)

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
MIMO_SEGS = sorted(_think_passes(CO.THINK_FLW + CO.THINK_SEE, CO.MIMO_CPS) + _landings(PF) + _landings(PH) + [(CP.LEFT_LEADS, CP.LEFT_LEADS + 0.16), (CP.SEE_SEND + 0.7, CP.AVATAR_AT)])
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

def _stack(d, t, f, key, level=1.0, t_in=None, mark12=0.0, segs=None, load=None, label_lines=None, row_dy=0.0):
    """A model's real layer stack (FACTS "X29 补充"), the pass running through it: layers behind the head lit, a
    flash on each landing. Top row attention (solid: full / global, hollow: linear / sliding window), bottom row the
    FFN (solid: dense, a comb: MoE). t_in: laid left to right over BO.BUILD (the model changes). segs: its passes
    (default SEGS[key]). load=(t0, t1): its weights load left to right (cells are pale until loaded).
    D36: label_lines = the label as lines (a pane too narrow for it on one line, 13 px apart), row_dy = the rows
    moved down to make room for them (default: the label on one line, the rows where they always were)."""
    A = BO.ARCH[key]
    m = BO.mtp_n(A)
    mtp = m > 0
    n = A['n'] + m
    gap = 10 if mtp else 0
    x0, pitch, w, ya, yf, h = _cells(f, n, gap)
    ya, yf = (ya + row_dy, yf + row_dy)
    la = level * (ease.prog(t, t_in, t_in + 0.2) if t_in is not None else 1.0)
    if la <= 0:
        return
    for k, s in enumerate(label_lines or [A['left']]):
        mtx(d, (x0, f[1] + 10 + 13 * k), s, 11, lv(INK, 0.72 * la))
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

def _body(c, img, d):
    t = c.t
    L, z = _layout_c(t)
    _cmdline(d, t, right(t))
    hits = CO._reads(t)
    st = _status(t)
    draw = {'input': lambda dd, r: _input(dd, t, r), 'think': lambda dd, r: _think(dd, t, r, z), 'trace': lambda dd, r: _trace(dd, t, r), 'generate': lambda dd, r: [fn(dd, t, r) for fn in (_gen_cat, _gen_purr, _gen_steak, _gen_reveal, _gen_wait, _gen_flower, _gen_img)], 'compare': lambda dd, r: [fn(dd, t, r) for fn in (_cmp_grep, _cmp_stats, _cmp_her_think, _cmp_find, _cmp_turns, _cmp_cos, _cmp_diff)], 'forward': lambda dd, r: _forward(dd, t, r)}
    fade = {'input': 1 - z, 'trace': 1 - z}
    rk = _recede(t)
    chrome = {'forward': 1 - 0.6 * rk} if rk > 0 else {}
    for name in ('input', 'think', 'trace', 'generate', 'compare', 'forward'):
        rect = L[name]
        level = fade.get(name, 1.0)
        if level <= 0.01:
            continue
        d.rectangle(rect, fill=BG)
        with panes.Clip(img, rect) as dd:
            draw[name](dd, rect)
        run = panes.run_k(t, RUN[name])
        status, her = st.get(name, ('', False))
        panes.box(d, rect, name, t, run, level * chrome.get(name, 1.0), status, her)
    m = max(hits.values(), default=0.0)
    mem = 1 - 0.62 * rk
    _memory_at(d, t, L['memory'], hits, mem)
    panes.box(d, L['memory'], 'mem', t, min(1.0, 3 * m), mem)

def _character_layer(film, orig):
    """r1's dsh layer (c_open._character_layer) from ui/pane_open_c2 (the speeds of speed.py) once it is shot."""
    c2 = P.path('ui/pane_open_c2')
    if not (c2.exists() and any(c2.iterdir())):
        return CO._character_layer(film, orig)
    real = CO.PaneFrames
    CO.PaneFrames = lambda path, *a, **k: real(c2, *a, **k)
    try:
        return CO._character_layer(film, orig)
    finally:
        CO.PaneFrames = real

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
    for at in [CP.PURR_AT, CP.STAT_TIMES[1], BREATH] + list(CP.GREP_TIMES) + [a for a, w in zip(CP.TURN_DOTS, CP.TURN_WHO) if w == 'her']:
        hud.LIVE.append((at, next_syllable(at)))
    for t0, side in [(T0, 'right'), (CAT.start - 0.3, 'left'), (CP.PET_SEND, 'both'), (CP.SAMPLE_T0, 'right'), (CP.REPLY_AT - 0.3, 'left'), (STOP, 'both'), (CP.LEFT_LEADS, 'left'), (W(25, 0), 'both'), (W(26, 0), 'right'), (W(27, 0), 'left'), (W(29, 0), 'both')]:
        film.set_lead(t0, side)
