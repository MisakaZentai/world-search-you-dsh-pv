"""r5 batch 4 (REVISE_R4_20261004.md §3.12-3.14, §5.1, D34; sample_r5/README.md): group G, the verse sung again
(233.85-260.88). It started as a copy of groups/g_lead.py (batch 3, r4) and is changed here; the switch is DSH_G=r5
(film.py takes this module's register and spans()). g_lead, g_mirror and their dsh shots are not changed.

What changed against r4 (the mirror of C's second half stays: the same panes, the same devices, the results the
other way round):

  line 57   the "who spoke first" rows (turns(): 你 / 她 / merged) are gone (D8). The bar they had (239.03-240.71,
            de-li-cate ev-er) is the dsh window's: on the downbeat your pointer opens the thinking row it is running
            with no message of yours above it (dsh's own expanded body, as C's stop), its first clause 没有新消息。 is
            marked on "-li-", you fold it on the beat before its message (ui/pages/g_r5.py). compare keeps line 56's
            find (her unprompted flower, its own) through the line instead of going empty.
  line 58   the arcs plate leaves this line (D7: it moves to interlude 3, interludes.py, batch 2). Its message lands
            in the generate pane at the pane's size, as C's answer lands on C10 (c_lead 120.14): the out row at 30 px,
            the first character's top-4 under it (C's row); on "bloom" (241.56) 开 keeps its weight: its own top-4
            and the character big at the pane's right. mem_refs 0 (the plate's foot) is the pane's status.
  line 59   the same lens rows (L8-L32, her pattern loses on "flow-", <eos> on "me"), in the pane: on the downbeat
            the rows come in under the row (no hold, no fold, no D2 break). r5c: the row does not step down to 20 px;
            as 开 recedes it grows to 38 px and stays the pane's heaviest ink until it draws; the lens rows are
            tighter and lighter, her template lit only while its row lands (_msg_geo, _lens_rows1).
  line 60   you type and send on "-to" (248.42; r4 sent on "human"), so the left works the next bars instead of
            sitting empty: trace walks its calls (the reply, the drawing, a row count a step), forward runs, and on
            the downbeat generate draws the image row by row, a step a beat or a sung syllable (the face is there on
            "human"). Until then line 59's result stays in the panes (nothing goes blank while you type).
  61-62     word by word zoom (word_zoom, reusable: batch 5 runs it for C 126.4-133.5): warmth and hands zoom both
            pictures onto the hand, breath onto the mouth (her bubbles, she is a fish), hair onto the top of the head
            (un: her stray hair, 1, as C13), ru onto its new cell by the left ear, which springs up; the view goes back
            to the whole pictures on the next line's downbeat. Each zoom is a line in trace.
  63        perfect: the count steps 1 -> 2 (big, C13's size); human: the stamp comes down on it; then generate leads
            for the pass that ends in <eos> on "me". r5c: no 2; the count reads 1 (missing, an empty frame) + 1 (new,
            a solid tile), +1 led to its cell by a one-dot leader, `not in memory` beside it (count_new).
  260.88-   untouched: the city (g5_city), the drill, H's hand-over; the dsh frames are g_mirror's again from G5.

Batch 3's lead table follows the beats above (LEAD); film.set_lead hands the frame to the dsh window on its two beats
(239.03 and 247.565) only.

g_lead's docstring (r4) follows; what it says about lines 57-60 is replaced by the above.

  lead       the pane that leads keeps the bright paper, full ink and its spinner; every other pane on the left (mem
             too) is shaded as a block (lead.shade), its frame and label drawn after the shade. The dsh window is a
             pane too (film.set_lead in register). Hand-overs ease over lead.EASE (0.16 s) from a beat or a sung
             syllable. The table is LEAD below.
  mirror     G replays C's second half line for line (lines 56-63 = 22-29), so LEAD is c_lead's table for those
             lines: the same pane leads the same line.

The merged one's body is her real one (DeepSeek-V4.1-Flash: 40 layers, 20 encoder + 20 decoder, MoE 384 + 1 shared,
FACTS "X29 补充（续）"); the merged model itself is invented (X01), so wearing her body is invented too (X-G6). Its dsh
never shows a 读取记忆 row (every stand-in read all the files each turn).
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import bisect
import math
import numpy as np
from PIL import Image, ImageDraw
import beatmap
import cast
import hud
import lead
import panes
import prompt_ids
import syl
import tl
from groups import b_open as BO
from groups import c_p4 as CP
from groups import c_pane as CPN
from groups import g as GG
from groups import g_pane as GPN
from groups import base as GBASE
from groups.base import add, big_word
from hud import BG, HER_QUIET, INK, lv
from inspect_ import next_syllable
from panes import FAINT, SUB, TXT
from tuikit import ease, glyph
from tuikit.uipane import PaneFrames
W = tl.W
T0, T1 = (GG.T0, GG.T1)
P = tl.p
M = GG.M
mtx, mw = (BO.mtx, BO.mw)
PROMPT_IDS = prompt_ids.load()
MEM, COL = (CPN.MEM, CPN.COL)
LX = CPN.LX
BO.ARCH[M] = dict(n=40, first=0, full=set(range(40)), dense=set(), left='deepseek-v5-flash-preview · 40 层 · 20 编码 + 20 解码 · MoE 384 选 6 + 1 共享', right='')
LENS_L = (8, 16, 24, 32)

def _down_near(t, reach=0.3):
    """The downbeat nearest t (beatmap's bars)."""
    ds = beatmap.events('down', t - reach, t + reach)
    return min(ds, key=lambda x: abs(x - t)) if ds else t
S = {ln: syl.times(ln) for ln in range(56, 65)}
FLOWER = GG.FLOWER
BACK = tl.bar(135)
NEXT_AT = BACK + 0.05
FIND_AT = S[56][2]
FIND_RET = S[56][5]
WAIT_STEPS = [x for x in (tl.grid(NEXT_AT, k, 2) for k in range(1, 12)) if x < FLOWER - 0.05]
MCPS = 30
THINK = [(FLOWER + 0.43, '没有新消息。上一条是用户的：那朵花开了吗？'), (S[57][2], '用户还说过：我想你了。'), (S[57][4], '想到一件事。')]
DIM57 = (S[57][0], S[57][0] + 0.62)
DSH_AT = _down_near(S[57][5])
HL_AT = S[57][6]
PTR_GO = tl.B(math.floor(tl.C.beat_of(DSH_AT) + 1e-06) - 1)
DSH_CLOSE = tl.B(math.floor(tl.C.beat_of(W(58, 0)) + 1e-06))
MSG = GG.MSG
MSG_AT = MSG.tok_t[0]
BLOOM = MSG.tok_t[4]
OUT = 30
L59 = W(59, 0)
L59_DOWN = _down_near(L59)
LENS1 = [S[59][2], S[59][4], S[59][6], S[59][8], S[59][9]]
EOS1 = S[59][9]
COS_AT = S[59][8]
SEE_COMMITS = syl.ime(W(60, 0), ['让我', '看看你'])
SEE_SEND = S[60][4]
THINK_SEE = [(tl.grid(SEE_SEND + 0.05, 0, 2), '用户想看看我。发我的头像。')]
THINK_SEE_END = THINK_SEE[0][0] + len(THINK_SEE[0][1]) / MCPS
DRAW_AT = beatmap.events('down', SEE_SEND, SEE_SEND + 2.0)[0]
AVATAR_AT = W(61, 0)
DRAW_STEPS = beatmap.merge(beatmap.events('beat', DRAW_AT, AVATAR_AT - 0.2), [x for x in S[60] if DRAW_AT < x < AVATAR_AT - 0.2])
SCAN = S[61]
WARMTH, HANDS = (W(61, 4), W(61, 8))
BREATH = W(62, 3)
HAIR = W(62, 5)
UNRULY = syl.syl(62, 7)
GREP_RET = S[63][1]
PERFECT, HUMAN = (S[63][4], S[63][6])
GEN_LAST = S[63][7]
LENS2 = [S[63][2], S[63][4], S[63][6], S[63][8], S[63][9]]
EOS2 = S[63][9]
G5, FOUND = (GG.G5, GG.FOUND)
DRILL = [tl.grid(FOUND, k, 4) for k in range(len(GG.STRATA))]
HER_ROW = DRILL[-1]
DSH_N0 = int(math.floor(PTR_GO * P.FPS)) - 2
DSH_N1 = int(math.ceil(G5 * P.FPS - 1e-09))
HERS1 = ''.join(GG.HER_PHRASE)
HERS2 = ''.join(GG.HER_PHRASE2)
ROWS1 = [((HERS1, 0.58, 'her'), ('<eos>', 0.12, 'ink')), ((HERS1, 0.41, 'her'), ('<eos>', 0.3, 'ink')), (('<eos>', 0.52, 'ink'), (HERS1, 0.21, 'her')), (('<eos>', 0.86, 'ink'), (HERS1, 0.06, 'her')), (('<eos>', 0.94, 'ink'), (HERS1, 0.03, 'her'))]
ROWS2 = [(('<eos>', 0.71, 'ink'), (HERS2, 0.04, 'her')), (('<eos>', 0.88, 'ink'), (HERS2, 0.02, 'her')), (('<eos>', 0.93, 'ink'), (HERS2, 0.01, 'her')), (('<eos>', 0.96, 'ink'), (HERS2, 0.01, 'her')), (('<eos>', 0.97, 'ink'), (HERS2, 0.01, 'her'))]
WAIT0 = [('<wait>', 0.97), ('<think>', 0.01), ('你好', 0.01), ('我想你了', 0.01)]
WAIT1 = [('<wait>', 0.03), ('<think>', 0.91), ('你好', 0.02), ('我想你了', 0.03)]

def wait_s(t):
    """0 -> 1 as the pass climbs (a step an 8th), 1 from "flower"."""
    if t >= FLOWER:
        return 1.0
    n = sum((1 for x in WAIT_STEPS if t >= x))
    return n / (len(WAIT_STEPS) + 1)

def lit_after(t, at):
    return CP.lit_after(t, at)
NEW = GG.STRAY_NEW
STRAY_CELL = (CP.STRAY[0], CP.STRAY[1] - 1)

def her_value(i, j):
    """Her avatar (c_p4.avatar with the stray hair)."""
    return 0.0 if (i, j) == STRAY_CELL else CP.AV[j][i] / 255

def its_value(i, j):
    """The image it sends: her avatar without the stray hair and one light cell by the left ear (r4's avatar_new)."""
    return 0.97 if (i, j) == NEW else CP.AV[j][i] / 255

def _cell_fill(v, level=1.0):
    return lv(glyph.mix(INK, BG, v ** 0.8), level)
FINE = 5

def fine_picture(override):
    """Her avatar at the file's 120 x 120 (0..1), with whole cells overridden: {(i, j): value}."""
    a = np.asarray(Image.open(tl.HERE / 'ui/assets/her_complete.png').convert('L'), np.float32) / 255
    a = a.copy()
    for (i, j), v in override.items():
        a[j * FINE:(j + 1) * FINE, i * FINE:(i + 1) * FINE] = v
    return a
HER_FINE = fine_picture({STRAY_CELL: 0.0})
ITS_FINE = fine_picture({NEW: 0.97})
ZOOM_EASE = 0.16
HAND = (0, 9, 10)
HAND_IN = (0, 10, 7)
MOUTH = (8, 10, 7)
HAIR_TOP = (10, 0, 8)

def around(cell, side):
    """A square region of `side` cells centred on `cell`."""
    i, j = cell
    return (i - (side - 1) // 2, j - (side - 1) // 2, side)

def zoom_keys(line, new_cell=None):
    """The zoom keys of the human verse: `line` sings warmth (word 4) and hands (word 8), line + 1 breath (3), hair (5)
    and un-ru-ly (7); the view goes back to the whole pictures on the first word of line + 1 and of line + 2 (both
    on a downbeat). G: zoom_keys(61, NEW) (ru goes onto its new cell); C, batch 5: zoom_keys(27) (no new cell: the
    view stays on the top of the head through un-ru-ly, where her stray hair is, diff = 1)."""
    k = [(W(line, 4), HAND, 'hands'), (W(line, 8), HAND_IN, 'hands'), (W(line + 1, 0), None, ''), (W(line + 1, 3), MOUTH, 'mouth'), (W(line + 1, 5), HAIR_TOP, 'hair')]
    if new_cell is not None:
        k.append((syl.syl(line + 1, 7)[1], around(new_cell, 5), f'({new_cell[0]}, {new_cell[1]})'))
    k.append((W(line + 2, 0), None, ''))
    return k

def _target(region, n):
    if region is None:
        return (n / 2, n / 2, float(n))
    i0, j0, s = region
    return (i0 + s / 2, j0 + s / 2, float(s))

def _mix_view(a, b, u):
    """Centre moves linearly, the side geometrically (a zoom reads even)."""
    return (ease.lerp(a[0], b[0], u), ease.lerp(a[1], b[1], u), a[2] * (b[2] / a[2]) ** u)

def zoom_view(t, keys, n=CP.AV_N, ease_s=ZOOM_EASE):
    """The view into an n x n picture at t, (i0, j0, side) in cells: the whole picture before the first key; at each
    key (at, region, ...) it eases out over ease_s from where it was onto the region (None: the whole picture)."""
    at0, frm, to = (None, _target(None, n), _target(None, n))
    for key in keys:
        at, region = (key[0], key[1])
        if t < at:
            break
        if at0 is not None:
            frm = _mix_view(frm, to, ease.ease_out(ease.prog(at, at0, at0 + ease_s)))
        at0, to = (at, _target(region, n))
    if at0 is None:
        return (0.0, 0.0, float(n))
    cx, cy, s = _mix_view(frm, to, ease.ease_out(ease.prog(t, at0, at0 + ease_s)))
    return (cx - s / 2, cy - s / 2, s)

def zoom_label(t, keys):
    """(label, 0..1) of the key in force at t ("" before the first and on the whole-picture keys)."""
    k = bisect.bisect_right([key[0] for key in keys], t) - 1
    if k < 0 or keys[k][1] is None:
        return ('', 0.0)
    return (keys[k][2], ease.prog(t, keys[k][0], keys[k][0] + ZOOM_EASE))

def zoom_factor(region, n=CP.AV_N):
    return n / region[2]

def view_rect(view, x, y, box, i, j, w=1.0, h=1.0):
    """Pixel rect of cells i .. i + w, j .. j + h of a picture drawn at (x, y) in a box px square, seen through view."""
    i0, j0, s = view
    k = box / s
    return (x + (i - i0) * k, y + (j - j0) * k, x + (i + w - i0) * k, y + (j + h - j0) * k)

def paint_view(d, x, y, box, view, value, level=1.0, n=CP.AV_N, fine=None, sub=FINE):
    """The picture value(i, j) (0 ink .. 1 paper) through view, clipped to its box. At the whole picture it is
    c_p4.avatar to the pixel. fine: the same picture at sub x sub px a cell (a 2-D array, 0..1): as the zoom grows
    past 6 px a cell the cells resolve into it (each value eased from its cell's to its own by 12 px a cell, so
    there is no pop), and from 12 px a cell a hairline of paper marks the cells (the diff's grid, r4's loupe)."""
    i0, j0, s = view
    k = box / s
    ci0, ci1 = (max(0, int(math.floor(i0))), min(n, int(math.ceil(i0 + s))))
    cj0, cj1 = (max(0, int(math.floor(j0))), min(n, int(math.ceil(j0 + s))))
    if fine is None or k < 6:
        gap = 1 if k >= 9 else 0
        for j in range(cj0, cj1):
            for i in range(ci0, ci1):
                xa, ya, xb, yb = view_rect(view, x, y, box, i, j)
                xa, ya = (round(max(xa, x)), round(max(ya, y)))
                xb, yb = (round(min(xb, x + box)), round(min(yb, y + box)))
                if xb - xa < 1 or yb - ya < 1:
                    continue
                d.rectangle((xa, ya, max(xa, xb - 1 - gap), max(ya, yb - 1 - gap)), fill=_cell_fill(value(i, j), level))
        return
    w = ease.clamp((k - 6) / 6)
    q = 1.0 / sub
    for j in range(cj0, cj1):
        for i in range(ci0, ci1):
            cv = value(i, j)
            for vj in range(sub):
                for vi in range(sub):
                    xa, ya, xb, yb = view_rect(view, x, y, box, i + vi * q, j + vj * q, q, q)
                    xa, ya = (round(max(xa, x)), round(max(ya, y)))
                    xb, yb = (round(min(xb, x + box)), round(min(yb, y + box)))
                    if xb - xa < 1 or yb - ya < 1:
                        continue
                    v = ease.lerp(cv, float(fine[j * sub + vj, i * sub + vi]), w)
                    d.rectangle((xa, ya, xb - 1, yb - 1), fill=_cell_fill(v, level))
    if k >= 12:
        paper = lv(BG, level)
        for i in range(ci0, ci1 + 1):
            xx = round(view_rect(view, x, y, box, i, 0)[0])
            if x < xx < x + box:
                d.line([(xx, y), (xx, y + box - 1)], fill=paper)
        for j in range(cj0, cj1 + 1):
            yy = round(view_rect(view, x, y, box, 0, j)[1])
            if y < yy < y + box:
                d.line([(x, yy), (x + box - 1, yy)], fill=paper)

def word_zoom(d, t, keys, pics, box, level=1.0, scan=None, n=CP.AV_N, ease_s=ZOOM_EASE):
    """Word by word zoom (REVISE_R4 §3.14): several pictures of the same n x n cells seen through one view that moves
    on the sung words.

      keys   [(at, region, label), ...] in time order (zoom_keys builds the human verse's). At each key the view
             eases out over ease_s from where it was onto region = (i0, j0, side) in cells (a 24 / side zoom) or None
             (the whole picture). Put a key on the word's sung syllable, the way back on a downbeat.
      pics   [(x, y, value[, fine]), ...]: each picture's top-left in px, value(i, j) -> 0 (ink) .. 1 (paper) a
             cell, and optionally fine, the same picture at the file's 120 x 120 (FINE px a cell, 0..1), which the
             zoom resolves into so a hand reads as a hand: her_value / HER_FINE and its_value / ITS_FINE here (C's
             batch 5: her_value / HER_FINE, and MiMo's image = c_p4.AV / fine_picture({}) without the stray hair).
      box    the pictures' size in px (n x the cell, 120 for 5 px cells). A zoomed picture stays in its box
             (clipped) and gets a one-dot frame.
      scan   rows compared so far (a hairline in her quiet blue, as c_p4.avatar), or None.

    Returns the view (i0, j0, side); marks go on cells with view_rect(view, x, y, box, i, j), the zoom's name with
    zoom_label(t, keys). Usage, G (lines 61-62, compare):
        view = word_zoom(d, t, ZOOM_G, [(ax1, ay, her_value, HER_FINE), (ax2, ay, its_value, ITS_FINE)], 120, a, scan)
    C, batch 5 (126.4-133.5, diff = 1):
        view = word_zoom(d, t, zoom_keys(27), [(ax1, ay, her_value, HER_FINE), (ax2, ay, mimo_value, MIMO_FINE)],
                         120, a, scan)"""
    view = zoom_view(t, keys, n, ease_s)
    zk = ease.clamp((n - view[2]) / (0.25 * n))
    for pic in pics:
        x, y, value = pic[:3]
        paint_view(d, x, y, box, view, value, level, n, pic[3] if len(pic) > 3 else None)
        if scan is not None and scan < n:
            yy = round(view_rect(view, x, y, box, 0, scan)[1])
            if y <= yy <= y + box:
                d.line([(x - 6, yy), (x + box + 6, yy)], fill=lv(HER_QUIET, level))
        if zk > 0.01:
            d.rectangle((x - 2, y - 2, x + box + 1, y + box + 1), outline=lv(INK, SUB * zk * level))
    return view

def stamp(d, t, rect, at, level=1.0, pad=10, gap_x=None, top_min=None):
    """The stamp (10_aesthetics §5.3): a double one-dot frame comes down around rect at `at` in 0.06 s (from 8 px
    out, ink from nothing), then stays. No fill, no slab (01: no inverse blocks). r5c: gap_x, a leader passes down
    through the bottom edges there (3 px of paper either side); top_min, the top edges never come higher (what is
    above keeps its 3 px while it comes down)."""
    u = ease.prog(t, at, at + 0.06)
    if u <= 0 or level <= 0.01:
        return
    g = 8 * (1 - ease.ease_out(u))
    x0, y0, x1, y1 = rect
    c = lv(INK, level * (0.3 + 0.7 * u))
    for inset in (0, 3):
        r = (round(x0 - pad - g + inset), round(y0 - pad - g + inset), round(x1 + pad + g - inset), round(y1 + pad + g - inset))
        if gap_x is None and top_min is None:
            d.rectangle(r, outline=c)
            continue
        xa, ya, xb, yb = r
        if top_min is not None:
            ya = max(ya, round(top_min))
        d.line([(xa, ya), (xb, ya)], fill=c)
        d.line([(xa, ya), (xa, yb)], fill=c)
        d.line([(xb, ya), (xb, yb)], fill=c)
        if gap_x is None or not xa < gap_x < xb:
            d.line([(xa, yb), (xb, yb)], fill=c)
        else:
            gx = round(gap_x)
            d.line([(xa, yb), (max(xa, gx - 4), yb)], fill=c)
            d.line([(min(xb, gx + 4), yb), (xb, yb)], fill=c)
ZOOM_G = zoom_keys(61, NEW)
NAMES = ('input', 'think', 'trace', 'generate', 'compare', 'forward', 'memory')
LIT = {'all': set(NAMES), 'dsh': set(), 'call': {'think', 'trace', 'forward'}, 'make': {'trace', 'generate', 'forward'}}
RELEASE_AT = tl.B(math.floor(tl.C.beat_of(T1 - lead.EASE)))
LEAD = [(W(56, 1), 'generate'), (FIND_RET, 'compare'), (THINK[1][0], 'think'), (DSH_AT, 'dsh'), (MSG_AT, 'generate'), (W(60, 0), 'dsh'), (SEE_SEND, 'call'), (DRAW_AT, 'make'), (AVATAR_AT, 'compare'), (GEN_LAST, 'generate'), (G5, 'forward'), (FOUND, 'trace'), (RELEASE_AT, 'all')]

def _lit(name):
    return LIT.get(name, {name})

def _entry(t):
    if t < LEAD[0][0]:
        return None
    k = max((i for i, (t0, _n) in enumerate(LEAD) if t >= t0))
    return (k, LEAD[k][0], LEAD[k][1])

def lead_w(t):
    """{pane: 0..1}: 1 lit (it leads), 0 shaded; eased over lead.EASE from the entry before (every pane lit before the
    first entry, which eases in from there: lead.weights' rule)."""
    e = _entry(t)
    if e is None:
        return dict.fromkeys(NAMES, 1.0)
    k, t0, cur = e
    prev = _lit(LEAD[k - 1][1]) if k else set(NAMES)
    cur = _lit(cur)
    u = ease.smooth(ease.prog(t, t0, t0 + lead.EASE))
    return {n: (n in cur) * u + (n in prev) * (1 - u) for n in NAMES}

def lead_on(t):
    """0..1: how much the table decides the spinners (0 before it and once every pane is lit: g_mirror's)."""
    e = _entry(t)
    if e is None:
        return 0.0
    k, t0, cur = e
    prev = LEAD[k - 1][1] if k else 'all'
    u = ease.smooth(ease.prog(t, t0, t0 + lead.EASE))
    return (cur != 'all') * u + (prev != 'all') * (1 - u)

def lead_run(rk, w, on):
    """The spinner turns on the pane that leads only (rule 4); rk: g_mirror's (panes.run_k over RUN)."""
    return ease.lerp(rk, w, on)

def _cmd(t):
    return '$ dsh inspect 大肥鱼 --trace --lens' if t < G5 else '$ dsh session restore 大肥鱼 --from archive/'

def _cmdline(d, t, r):
    hud.tx(d, (36, hud.Y_CMD), _cmd(t), 13, lv(INK, 0.86))
    chip = cast.term(M)
    f = P.font(13, 'bold')
    w = d.textlength(chip, font=f)
    d.rectangle((r - w - 12, hud.Y_CMD - 3, r, hud.Y_CMD + 17), fill=hud.SLAB)
    d.text((r - w - 6, hud.Y_CMD), chip, font=f, fill=BG)

def draw_rows(t):
    """Rows of its picture drawn by t: a share of 24 a step (DRAW_STEPS), each step written in 0.04 s."""
    return CP.AV_N * min(1.0, beatmap.step(t, DRAW_STEPS, 0.04) / len(DRAW_STEPS))

def _rows_ret(t):
    return f'row {int(draw_rows(t) + 1e-06)}/{CP.AV_N}'

def _zoom_lines():
    out = []
    for at, region, label in ZOOM_G:
        if region is None:
            continue
        arg = f'"{label}"' if label[0] != '(' else label
        out.append((at, f'zoom({arg}, {zoom_factor(region):.1f})', None))
    return out
CODE = sorted([(NEXT_AT, 'merged.next(ctx, user=None)', (FLOWER, '<think> 0.91')), (FIND_AT, 'archive.find(role="assistant", prev="assistant")', (FIND_RET, '她 3 条')), (MSG_AT, 'merged.generate(ctx, user=None)', (MSG.done, '7 tok · mem_refs 0')), (S[59][0], 'merged.next(ctx, lens=[8, 16, 24, 32])', (EOS1, '<eos>')), (COS_AT, 'cos(embed(她), embed(merged))', (EOS1, '?')), (SEE_SEND, 'img = merged.reply("让我看看你")', (AVATAR_AT, 'image/png 120×120')), (DRAW_AT, 'merged.draw("我的头像", 24, 24)', (DRAW_AT, _rows_ret)), (SCAN[0], 'diff(她.avatar, img)', (PERFECT, '1 + 1 格')), (UNRULY[2], 'grep("(3,12)", memory/you/ + archive/)', (GREP_RET, '0 · not in memory')), (S[63][0], 'merged.next(ctx, lens=[8, 16, 24, 32])', (EOS2, '<eos>'))] + _zoom_lines(), key=lambda x: x[0])

def _trace(d, t, r):
    shown = [x for x in CODE if x[0] <= t]
    if not shown:
        return
    last = shown[-1][0]
    sc = ease.ease_out(ease.prog(t, last, last + 0.14))
    for pos, (at, s, ret) in enumerate(reversed(shown[-4:])):
        y = r[1] + 47 - pos * 19 + (1 - sc) * 19
        a = {0: TXT, 1: SUB, 2: FAINT}.get(pos, FAINT * max(0.0, 1 - sc / 0.3))
        if pos == 0:
            a *= ease.prog(t, at, at + 0.1)
        n = int((t - at) * BO.CODE_CPS) + 1
        w = mtx(d, (r[0] + 10, y), s[:n], 14, lv(INK, 0.92 * a), bold=pos == 0)
        if ret and t >= ret[0]:
            u = ease.prog(t, ret[0], ret[0] + 0.1)
            text = ret[1](t) if callable(ret[1]) else ret[1]
            mtx(d, (r[0] + 10 + w + 12, y), '→ ' + text, 14, lv(INK, 0.7 * a * u), bold=True)

def _input(d, t, r):
    commits = SEE_COMMITS
    if t < commits[0][0]:
        if tl.C.beat_of(t) % 1.0 < 0.5:
            d.rectangle((r[0] + 12, r[1] + 12, r[0] + 15, r[1] + 34), fill=lv(INK, FAINT))
        return
    sent = t >= SEE_SEND
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
        ph = pad_clock(t, commits[0][0], SEE_SEND, base=1.2, gain=2.4)
        k = 0.15 + 0.85 * (0.5 + 0.5 * math.cos(2 * math.pi * ph))
        d.rectangle((round(x - 6), y + 2, round(x - 6) + 1, y + 25), fill=lv(INK, k))
THINKS = THINK + THINK_SEE

def _think(d, t, r):
    shown = [(at, s) for at, s in THINKS if at <= t]
    if not shown:
        return
    last = shown[-1][0]
    sc = ease.ease_out(ease.prog(t, last, last + 0.14))
    for pos, (at, s) in enumerate(reversed(shown[-3:])):
        n = int((t - at) * MCPS) + 1
        a = {0: TXT, 1: SUB}.get(pos, SUB * max(0.0, 1 - sc / 0.3))
        y = r[1] + 30 - pos * 19 + (1 - sc) * 19
        if pos == 0:
            a *= ease.prog(t, at, at + 0.1)
        if a > 0.01:
            w_ = mtx(d, (r[0] + 10, y), s[:n], 13, lv(INK, a))
            if pos == 0:
                think_caret(d, t, r[0] + 10 + w_ + 3, y, 13, lead_w(t)['think'] * a, at)

def think_caret(d, t, x, y, size, level, t0):
    """R-A (r5 round 2): while the think pane leads, a caret after its newest line breathes at the pad's rate."""
    if level <= 0.01:
        return
    ph = pad_clock(t, t0, t0 + 14.0, base=1.2, gain=2.4)
    k = 0.15 + 0.85 * (0.5 + 0.5 * math.cos(2 * math.pi * ph))
    d.rectangle((round(x), round(y + 2), round(x) + 1, round(y + size + 3)), fill=lv(INK, k * level))

def _gen_wait(d, t, g):
    """Lines 56-57: C8's p(next | 没有用户消息), the pass climbing; <wait> sinks and is struck out on "flower". It
    clears in the 8th before its message starts (line 58)."""
    if t < NEXT_AT or t >= MSG_AT - 0.14:
        return
    a = ease.prog(t, NEXT_AT, NEXT_AT + 0.2) * (1 - ease.prog(t, MSG_AT - 0.3, MSG_AT - 0.14))
    s = wait_s(t)
    cands = [(w0, round(p0 + (p1 - p0) * s, 2)) for (w0, p0), (_w, p1) in zip(WAIT0, WAIT1)]
    ca = a * (1 - ease.prog(t, DIM57[0], DIM57[0] + 0.3))
    CPN._cands(d, t, (g[0] + 10, g[1] + 14), 'p(next | 没有用户消息)', cands, 1, FLOWER, g[2] - 10, ca)
    k = 0.35 + 0.65 * (1 - s)
    after = 1 - 0.45 * ease.prog(t, DIM57[0], DIM57[1])
    x0, y0 = (g[0] + 10, g[1] + 40)
    hud.tx(d, (x0, y0), '<wait>', 64, lv(INK, k * a * after), True)
    if t >= FLOWER:
        u = ease.ease_out(ease.prog(t, FLOWER, FLOWER + 0.12))
        w = hud.width('<wait>', 64, True)
        ym = y0 + 29
        d.rectangle((x0 - 6, ym - 2, x0 - 6 + (w + 12) * u, ym + 2), fill=lv(INK, a * after))
        tx = x0 + w + 30
        hud.tx(d, (tx, y0 + 18), '<think>', 30, lv(INK, a * after * ease.prog(t, FLOWER, FLOWER + 0.12)), True)
        cw = hud.width('<think>', 30, True)
        ph = pad_clock(t, FLOWER + 0.3, MSG_AT, base=1.2, gain=2.4)
        kc = 0.15 + 0.85 * (0.5 + 0.5 * math.cos(2 * math.pi * ph))
        d.rectangle((round(tx + cw + 6), y0 + 26, round(tx + cw + 8), y0 + 54), fill=lv(INK, a * after * kc * ease.prog(t, FLOWER + 0.12, FLOWER + 0.3)))
ANS = 38
ANS_IN = (L59_DOWN - 0.14, L59_DOWN)
LIT_HOLD = 0.2

def _msg_geo(t, g):
    """(x, top, size) of its message row: C's out row (30 px) as it lands on line 58; r5c: as 开 recedes it grows to
    ANS px (landing on line 59's downbeat) and keeps the lead until it draws; the lens rows come in under it."""
    u = ease.ease_out(ease.prog(t, *ANS_IN))
    size = ease.lerp(OUT, ANS, u)
    return (LX, g[1] + 14 - size * 0.1, size)

def _gen_out(t):
    """0..1 how much of lines 58-59's generate content is up (it goes on the drawing's downbeat)."""
    return ease.prog(t, MSG_AT - 0.3, MSG_AT) * (1 - ease.prog(t, DRAW_AT - 0.1, DRAW_AT))

def _gen_msg(d, t, g):
    """Lines 58-59: its message, a character a sung syllable (as C's _row), its <eos> on "me"."""
    a = _gen_out(t)
    if a <= 0.003:
        return
    mtx(d, (g[0] + 10, g[1] + 24 + round(6 * ease.ease_out(ease.prog(t, *ANS_IN)))), 'out', 12, lv(INK, SUB * a))
    x, y, size = _msg_geo(t, g)
    for c, at, k in MSG.chars:
        if t < at:
            break
        drop = (1 - ease.ease_out(ease.prog(t, at, at + 0.14))) * -6
        x += hud.tx(d, (x, y + drop), c, round(size), lv(MSG.color(k, at, t), a), bold=True)
    if t >= EOS1:
        CPN._eos(d, t, x + 10, round(y + 0.6 * size) - 10, EOS1, a)

def _gen_bloom(d, t, g):
    """Line 58: under the row the first character's top-4 (C10's row: logprobs ≈ 第一个字); on "bloom" 开's top-4
    and 开 itself big at the pane's right (r4's plate had it top right; REVISE_R4 §5.3 keeps it on the syllable)."""
    if t < MSG_AT - 0.14 or t >= L59_DOWN:
        return
    out = 1 - ease.prog(t, L59_DOWN - 0.14, L59_DOWN - 0.02)
    xy, x_max = ((g[0] + 10, g[1] + 70), g[2] - 150)
    if t < BLOOM:
        ca = ease.prog(t, MSG_AT - 0.14, MSG_AT) * (1 - ease.prog(t, BLOOM - 0.12, BLOOM - 0.02))
        CPN._cands(d, t, xy, 'logprobs ≈ 第一个字', MSG.toks[0].cands, 0, MSG_AT, x_max, ca)
        return
    CPN._cands(d, t, xy, 'logprobs ≈ 第五个字', MSG.toks[4].cands, 0, BLOOM, x_max, out)
    bump = 1.0 + 0.22 * (1 - ease.ease_out(ease.prog(t, BLOOM, BLOOM + 0.16)))
    big_word(d, '开', (g[2] - 26, g[1] + 16), 96, lv(INK, out), 'ra', bump=bump)

def _lens_geo(gy):
    """The lens rows in the generate pane (r4's pane table): L8 at the bottom, L32 on top."""
    return dict(xl=COL + 10, x=LX, lab=12, cjk=18, mono=15, p=12, g1=8, g2=18, ys=[gy + 112, gy + 90, gy + 68, gy + 46])

def _lens_rows(d, t, rows, lands, a, G):
    """One pass read at layers 8/16/24/32 (bottom up as it climbs), each row the top two guesses; her pattern in her
    blue (lit while it lands, D1)."""
    s = G['cjk'] / 18
    for k, (layer, y) in enumerate(zip(LENS_L, G['ys'])):
        mtx(d, (G['xl'], y + 3 * s), f'L{layer}', round(G['lab']), lv(INK, FAINT * a))
        at = lands[k]
        if t < at:
            continue
        u = ease.prog(t, at, at + 0.1)
        xx = G['x']
        for j, (text, p, who) in enumerate(rows[k]):
            if who == 'her':
                col = hud.her(lit_after(t, at)) if j == 0 else HER_QUIET
            else:
                col = INK
            lvl = (TXT if j == 0 else SUB) * a * u
            w = hud.tx(d, (xx, y - s), text, round(G['cjk']), lv(col, lvl), j == 0) if not text.startswith('<') else mtx(d, (xx, y + s), text, round(G['mono']), lv(col, lvl), bold=j == 0)
            xx += w + G['g1']
            xx += mtx(d, (xx, y + 2 * s), f'{p:.2f}', round(G['p']), lv(INK, lvl * 0.85)) + G['g2']

def _lens_table(d, t, g, x, rows, lands, t_in, t_out, x_lab=None):
    """The lens rows in the generate pane (line 63)."""
    if t < t_in - 0.3 or t >= t_out:
        return
    a = ease.prog(t, t_in - 0.3, t_in) * (1 - ease.prog(t, t_out - 0.3, t_out))
    G = _lens_geo(g[1])
    G['x'], G['xl'] = (x, g[0] + 10 if x_lab is None else x_lab)
    _lens_rows(d, t, rows, lands, a, G)

def _lens_geo1(gy):
    """r5c: line 59's lens rows under its answer (ANS px), tighter and lighter than r5b's _lens_geo: L8 at the
    bottom, L32 on top, 18 px apart, the guesses at 14 px."""
    return dict(xl=COL + 10, x=LX, lab=11, cjk=14, mono=12, p=10, g1=6, g2=16, ys=[gy + 118, gy + 100, gy + 82, gy + 64])

def _lit_quick(t, at):
    """D1, r5c: her template on the lens row that is landing: lit until the next sung syllable but at most LIT_HOLD,
    then settling to quiet over hud.LIVE_FADE."""
    hold = min(next_syllable(at), at + LIT_HOLD)
    return 1.0 if t < hold else 1 - ease.prog(t, hold, hold + hud.LIVE_FADE)

def _lens_rows1(d, t, rows, lands, a, G):
    """r5c: line 59's lens rows (as _lens_rows, lighter): her template never bold, in her blue only while its row
    lands (_lit_quick), then HER_QUIET a step down; the rows <eos> wins in ink, <eos> bold."""
    for k, (layer, y) in enumerate(zip(LENS_L, G['ys'])):
        mtx(d, (G['xl'], y + 2), f'L{layer}', G['lab'], lv(INK, FAINT * a))
        at = lands[k]
        if t < at:
            continue
        u = ease.prog(t, at, at + 0.1)
        xx = G['x']
        for j, (text, p, who) in enumerate(rows[k]):
            if who == 'her':
                lit = _lit_quick(t, at) if j == 0 else 0.0
                col = hud.her(lit)
                lvl = ease.lerp(SUB, TXT, lit) if j == 0 else SUB * 0.85
            else:
                col = INK
                lvl = TXT if j == 0 else SUB
            lvl *= a * u
            if text.startswith('<'):
                w = mtx(d, (xx, y + 1), text, G['mono'], lv(col, lvl), bold=j == 0)
            else:
                w = hud.tx(d, (xx, y - 1), text, G['cjk'], lv(col, lvl))
            xx += w + G['g1']
            xx += mtx(d, (xx, y + 3), f'{p:.2f}', G['p'], lv(INK, lvl * 0.85)) + G['g2']

def _gen_lens1(d, t, g):
    """Line 59: the lens rows under the row, from its downbeat; they stay (with the row) until it draws. r5c: under
    the answer at ANS px, tighter and lighter (_lens_rows1)."""
    if t < L59_DOWN - 0.02:
        return
    a = ease.prog(t, L59_DOWN - 0.02, L59_DOWN + 0.12) * _gen_out(t)
    if a > 0.003:
        _lens_rows1(d, t, ROWS1[:4], LENS1, a, _lens_geo1(g[1]))
GCELL = 4

def avatar_new(d, x, y, cell, level=1.0, rows=None):
    """The image it sends (its_value), the first `rows` rows of it (None: all)."""
    n = CP.AV_N if rows is None else rows
    for j in range(n):
        for i in range(CP.AV_N):
            d.rectangle((x + i * cell, y + j * cell, x + (i + 1) * cell - 1, y + (j + 1) * cell - 1), fill=_cell_fill(its_value(i, j), level))

def _gen_draw(d, t, g):
    """Line 60: it draws its picture row by row, a step a beat or a sung syllable (DRAW_STEPS); the rows not written
    yet are a grid of faint dots, the row being written has a hairline under it."""
    if t < DRAW_AT or t >= AVATAR_AT:
        return
    a = ease.prog(t, DRAW_AT, DRAW_AT + 0.06)
    x, y = (LX, g[1] + 16)
    rows = draw_rows(t)
    n = int(rows + 1e-06)
    avatar_new(d, x, y, GCELL, a, n)
    if n < CP.AV_N:
        part = rows - n
        if part > 0.01:
            xr = x + CP.AV_N * GCELL * part
            for i in range(CP.AV_N):
                if x + i * GCELL >= xr:
                    break
                d.rectangle((x + i * GCELL, y + n * GCELL, x + (i + 1) * GCELL - 1, y + (n + 1) * GCELL - 1), fill=_cell_fill(its_value(i, n), a))
        for j in range(n + 1, CP.AV_N):
            for i in range(CP.AV_N):
                d.point((x + i * GCELL + 1, y + j * GCELL + 1), fill=lv(INK, 0.35 * a))
        yy = y + (n + 1) * GCELL
        d.line([(x - 6, yy), (x + CP.AV_N * GCELL + 6, yy)], fill=lv(INK, a))
    mtx(d, (g[0] + 10, g[1] + 24), 'img', 12, lv(INK, SUB * a))
    xr = x + CP.AV_N * GCELL + 20
    mtx(d, (xr, y), f'{CP.AV_N}×{CP.AV_N} · row {n}/{CP.AV_N}', 12, lv(INK, SUB * a))

def _gen_img(d, t, g):
    """Lines 61-63: its image; line 63, the pass beside it (the lens table again: <eos> from layer 8 up). r5 round
    2: while compare is tall (zoom_lay) the image is drawn at GCELL_Z, inside the shorter pane."""
    if t < AVATAR_AT:
        return
    x, y = (LX, g[1] + 16)
    cell = ease.lerp(GCELL, GCELL_Z, zoom_lay(t, *G_DIFF.lay))
    avatar_new(d, x, y, cell)
    mtx(d, (g[0] + 10, g[1] + 24), 'img', 12, lv(INK, SUB))
    xr = x + CP.AV_N * cell + 20
    k = ease.prog(t, AVATAR_AT, AVATAR_AT + 0.1) * (1 - ease.prog(t, S[63][0] - 0.3, S[63][0]))
    mtx(d, (xr, y), 'image/png · 120×120', 12, lv(INK, SUB * k))
    if t >= LENS2_IN - 0.3:
        xt = xr + 40
        ka = ease.prog(t, LENS2_IN - 0.3, LENS2_IN)
        mtx(d, (xr, g[1] + 14 + 10), 'out', 12, lv(INK, SUB * ka))
        if t >= EOS2:
            CPN._eos(d, t, xt, g[1] + 12, EOS2)
        _lens_table(d, t, g, xt, ROWS2[:4], LENS2, LENS2_IN, T1, x_lab=xr)
LENS2_IN = min(LENS2[0], S[63][0] + ZOOM_EASE + 0.3)
FCELL = 4

def sway(t, at, t0, t1, k=0.0):
    """R-A (r5 round 2): a bloomed flower's head sways a pixel either way at the pad's rate (from its bloom on)."""
    u = ease.prog(t, at + 0.32, at + 0.6) if at >= 0 else 1.0
    return round(1.4 * u * math.sin(2 * math.pi * (pad_clock(t, t0, t1, base=0.5, gain=1.2) + k)))

def _flower(d, t, cx, cy, at, cell_max, color, dx=0):
    """C8's daisy (CP.draw_flower) in any colour: blooms at `at`. dx: the head's sway (the stem stays)."""
    g = ease.ease_back(ease.prog(t, at, at + 0.32))
    cell = max(1, int(cell_max * g)) if t >= at else 0
    if cell < 3:
        if t >= at:
            d.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=color)
        return
    n = len(CP.FLOWER_PIX)
    sx, sy = (cx - n * cell // 2, cy - n * cell // 2)
    d.rectangle((cx - cell // 2, sy + (n - 2) * cell, cx - cell // 2 + cell - 1, sy + (n + 7) * cell), fill=color)
    hud.pix(d, ['..##', '.###', '##..'], cx - cell // 2 + cell, sy + (n + 2) * cell, cell, {'#': color})
    hud.pix(d, CP.FLOWER_PIX, sx + dx, sy, cell, {'#': color, 'o': BG})

def _cmp_find(d, t, c):
    """Line 56 (C8): her unprompted turn and its blue flower; on "flower" its own turn, an ink one. r5: it stays
    through lines 57-58 (the turns() rows that replaced it are gone, D8) and goes as line 59's slots come in."""
    if t < FIND_RET - 0.05 or t >= L59_DOWN - 0.12:
        return
    a = ease.prog(t, FIND_RET - 0.05, FIND_RET + 0.15) * (1 - ease.prog(t, L59_DOWN - 0.3, L59_DOWN - 0.12))
    cy = c[1] + 12 + 7 * FCELL + 4
    mtx(d, (c[0] + 10, c[1] + 16), '2026-04-02 23:10 · assistant', 13, lv(HER_QUIET, a))
    mtx(d, (c[0] + 10, c[1] + 36), 'prev: assistant · (no user turn)', 12, lv(HER_QUIET, SUB * a))
    _flower(d, t, c[0] + 270, cy, -1.0, FCELL, lv(HER_QUIET, a), sway(t, -1.0, FIND_RET, L59_DOWN))
    if t >= FLOWER:
        k = ease.prog(t, FLOWER, FLOWER + 0.12) * a
        xr = c[0] + 330
        mtx(d, (xr, c[1] + 16), 'now · assistant', 13, lv(INK, k), bold=True)
        mtx(d, (xr, c[1] + 36), 'prev: — · (no user turn)', 12, lv(INK, SUB * k))
        _flower(d, t, min(c[2] - 44, xr + 270), cy, FLOWER, FCELL, lv(INK, a), sway(t, FLOWER, FIND_RET, L59_DOWN, 0.35))
PAT = CPN.PAT

def _cmp_cos(d, t, c):
    """Line 59: C10's slots, her pattern over its answer; its slots stay empty; cos(她, merged) = ? on "me". r5: it
    stays while you ask to see it and it draws (nothing goes blank), and goes as the pictures come in."""
    if t < L59_DOWN - 0.12 or t >= AVATAR_AT:
        return
    a = ease.prog(t, L59_DOWN - 0.12, L59_DOWN + 0.04) * (1 - ease.prog(t, AVATAR_AT - 0.12, AVATAR_AT))
    x0, y0 = (c[0] + 10, c[1])
    yh, ym = (y0 + 22, y0 + 58)
    slots = CPN._slots(c[0] + 130)
    mtx(d, (x0, yh + 3), '她', 14, lv(HER_QUIET, a), bold=True)
    mtx(d, (x0, ym + 3), 'merged', 14, lv(INK, a), bold=True)
    for (x, w), ch in zip(slots, CPN.HER_PAT):
        if ch == '🍆':
            BO.GB.eggplant(d, x + 3, yh + 2, 2, 0.0, a)
        else:
            hud.tx(d, (x, yh - PAT * 0.1), ch, PAT, lv(HER_QUIET, a), True)
    marks = [(0, 0), (1, 1), (2, 3), (4, 5), (6, 7), (8, 11), (9, 12)]
    for si, slot in marks:
        at = S[59][si]
        if t < at:
            break
        x, w = slots[slot]
        if slot == 7:
            w = slots[10][0] + slots[10][1] - x
        u = ease.prog(t, at, at + 0.1)
        d.line([(x + 2, ym + 22), (x + max(12, w) - 2, ym + 22)], fill=lv(INK, SUB * a * u), width=2)
    if t >= EOS1:
        k = int(pad_clock(t, EOS1, AVATAR_AT, base=3.0, gain=5.0)) % len(slots)
        x, w = slots[k]
        sa = a * ease.prog(t, EOS1, EOS1 + 0.2)
        for yy in (yh + PAT + 7, ym + PAT + 8):
            d.line([(round(x + 1), yy), (round(x + w - 2), yy)], fill=lv(INK, SUB * sa))
    if t >= EOS1:
        u = ease.prog(t, EOS1, EOS1 + 0.15) * a
        f = 'cos(她, merged) ='
        mtx(d, (c[2] - 14 - mw(f, 14, True), y0 + 14), f, 14, lv(INK, SUB * u), bold=True)
        big_word(d, '?', (c[2] - 14, y0 + 40), 40, lv(INK, SUB * u), 'ra')
_CLOCKS: dict = {}

def pad_clock(t, t0, t1, base=3.0, gain=12.0, step=1 / 48):
    """Units passed by t since t0 at a rate of base + gain * pad() a second (precomputed over [t0, t1])."""
    key = (round(t0, 4), round(t1, 4), base, gain)
    arr = _CLOCKS.get(key)
    if arr is None:
        acc, arr = (0.0, [0.0])
        for i in range(1, int((t1 - t0) / step) + 3):
            acc += (base + gain * beatmap.pad(t0 + i * step)) * step
            arr.append(acc)
        _CLOCKS[key] = arr
    x = max(0.0, (t - t0) / step)
    i = min(len(arr) - 2, int(x))
    return arr[i] + (arr[i + 1] - arr[i]) * min(1.0, x - i)

def compare_cursor(d, view, ax1, ax2, ay, box, level, clock, rows=None, values=None):
    """A one-dot square on the same cell of both pictures, gliding along the rows in view (only the rows being
    scanned while the scan runs): the comparison going on between the syllables. Inside the pictures only. values:
    each picture's value(i, j): on a dark cell the square is paper, on a light one ink (it reads on both)."""
    if level <= 0.01:
        return
    i0, j0, s = view
    ia, ib = (max(0, int(math.floor(i0 + 1e-06))), min(CP.AV_N, int(math.ceil(i0 + s - 1e-06))))
    ja, jb = (max(0, int(math.floor(j0 + 1e-06))), min(CP.AV_N, int(math.ceil(j0 + s - 1e-06))))
    if rows is not None:
        ra, rb = (max(ja, int(rows[0])), min(jb, max(int(rows[0]) + 1, int(math.ceil(rows[1])))))
        if rb > ra:
            ja, jb = (ra, rb)
    ni, nj = (ib - ia, jb - ja)
    if ni <= 0 or nj <= 0:
        return
    p = clock % (ni * nj)
    j = ja + int(p // ni)
    i = max(float(ia), min(float(ib - 1), ia + p % ni - 0.5))
    for q, x in enumerate((ax1, ax2)):
        r = view_rect(view, x, ay, box, i, j)
        x0, y0 = (max(r[0], x), max(r[1], ay))
        x1, y1 = (min(r[2], x + box) - 1, min(r[3], ay + box) - 1)
        if x1 - x0 >= 2 and y1 - y0 >= 2:
            dark = values is not None and values[q](int(round(i)), j) < 0.45
            col = glyph.mix(_cell_fill(values[q](int(round(i)), j)), BG, level) if dark else lv(INK, 0.85 * level)
            d.rectangle((round(x0), round(y0), round(x1), round(y1)), outline=col)
ACELL = 5
SIDE = CP.AV_N * ACELL
SIDE_Z = 168
GEN_H_Z = 100
GCELL_Z = 3

def zoom_lay(t, t_in, t_out):
    """0..1, the zoom layout: from the first zoom word (warmth) compare grows upward and the two pictures grow to
    SIDE_Z, on the word, eased out like the view; back on the line that returns to the whole pictures for good."""
    if t < t_in:
        return 0.0
    return ease.ease_out(ease.prog(t, t_in, t_in + ZOOM_EASE)) * (1 - ease.ease_io(ease.prog(t, t_out, t_out + ZOOM_EASE)))

def zoom_rects(L, u):
    """The generate / compare split in the zoom layout: generate GEN_H_Z tall, compare takes the rest (8 px gap)."""
    if u <= 0:
        return L
    L = dict(L)
    g, c = (L['generate'], L['compare'])
    gz = (g[0], g[1], g[2], g[1] + GEN_H_Z)
    L['generate'] = panes.lerp_rect(g, gz, u)
    L['compare'] = panes.lerp_rect(c, (c[0], gz[3] + 8, c[2], c[3]), u)
    return L

def _ticks(d, rect, color, n=5):
    """Four ticks pointing at a cell's frame from outside (r4's loupe ticks)."""
    x0, y0, x1, y1 = rect
    xm, ym = ((x0 + x1) / 2, (y0 + y1) / 2)
    for a_, b_ in (((xm, y0 - 3), (xm, y0 - 3 - n)), ((xm, y1 + 3), (xm, y1 + 3 + n)), ((x0 - 3, ym), (x0 - 3 - n, ym)), ((x1 + 3, ym), (x1 + 3 + n, ym))):
        d.line([(round(a_[0]), round(a_[1])), (round(b_[0]), round(b_[1]))], fill=color)

def _in_box(rect, x, y, box):
    return rect[2] > x and rect[0] < x + box and (rect[3] > y) and (rect[1] < y + box)

def stray_mark(d, t, view, x, y, box, un_at, level=1.0):
    """r5 round 2 (2-C item 7): her stray hair (14, 0) is a dark cell in her dark top row, so neither the whole
    picture nor the zoom showed it. It gets a one-dot outline in her blue just inside the cell (quiet; lit when "un"
    lands on it), so the one cell the diff counts can be seen."""
    if level <= 0.01:
        return
    r = view_rect(view, x, y, box, *STRAY_CELL)
    x0, y0 = (round(max(r[0], x)), round(max(r[1], y)))
    x1, y1 = (round(min(r[2], x + box)) - 1, round(min(r[3], y + box)) - 1)
    if x1 - x0 < 2 or y1 - y0 < 2:
        return
    col = hud.her(lit_after(t, un_at) if t >= un_at else 0.0)
    d.rectangle((x0, y0, x1, y1), outline=lv(col, level))

class DiffSpec:
    """What a verse's diff needs. G: lines 61-63 (below); C: lines 27-29 mirror it (groups/c_lead.py, r5 round 2):
    the same pictures, zooms, marks and count; C has no new cell, ends on 1 and has no stamp."""

    def __init__(self, keys, scan, unruly, breath, avatar_at, lay, its, its_fine, new=None, perfect=None, human=None, gone=None, marks=True, info_dx=32, un_steps=False, nim=None):
        self.keys, self.scan, self.unruly, self.breath, self.avatar_at = (keys, scan, unruly, breath, avatar_at)
        self.lay, self.its, self.its_fine = (lay, its, its_fine)
        self.new, self.perfect, self.human = (new, perfect, human)
        self.nim = nim
        self.gone = gone
        self.marks = marks
        self.info_dx = info_dx
        self.un_steps = un_steps
COUNT_H = 88
PLUS_K = 0.5
PLUS_GAP = 14
PLUS_MOVE = 0.18
NEW_MIN = 9
LEAD_GROW = (0.04, 0.3)
STAMP_PAD = 7

def new_tile(t, S, view, ax2, ay, box):
    """(rect, pop) of the new cell's tile on its picture (r5b's pop on ru: 1.5x the cell, easing back to the cell, a
    quarter cell proud), or None out of view. r5c: once counted (perfect) it pops to at least NEW_MIN px as the
    leader arrives."""
    un1 = S.unruly[1]
    pop = ease.ease_back(ease.prog(t, un1, un1 + 0.18))
    rn = view_rect(view, ax2, ay, box, *S.new)
    if not _in_box(rn, ax2, ay, box):
        return None
    cx, cy = ((rn[0] + rn[2]) / 2, (rn[1] + rn[3]) / 2)
    h = (rn[2] - rn[0]) / 2 * (1 + 0.5 * (1 - pop))
    lift = 0.25 * (rn[3] - rn[1]) * pop
    if S.perfect is not None and t >= S.perfect + LEAD_GROW[1] and (h < NEW_MIN / 2):
        arr = S.perfect + LEAD_GROW[1]
        h = ease.lerp(h, NEW_MIN / 2, ease.ease_back(ease.prog(t, arr, arr + 0.18)))
    return ((cx - h, cy - h - lift, cx + h, cy + h - lift), pop)

def _ink_h(text, height, bump=1.0):
    """The ink height big_word gives `text` at `height` and `bump` (groups.base's measure)."""
    size = int(GBASE._size_for(text, height, True) * bump)
    x0, y0, x1, y1 = hud.font(size, text, True).getbbox(text)
    return y1 - y0

def leader(d, pts, u, level, pic=None):
    """A one-dot orthogonal leader grown to the first u of its length from pts[0] (hud.cut). pic = (x, y, box, view,
    value): over that picture each dot takes the colour that reads on its cell (paper on a dark one, ink on a light
    one, as compare_cursor)."""
    pts = hud.cut(pts, u)
    ink = lv(INK, level)
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        xa, xb, ya, yb = (round(xa), round(xb), round(ya), round(yb))
        for x in range(min(xa, xb), max(xa, xb) + 1):
            for y in range(min(ya, yb), max(ya, yb) + 1):
                col = ink
                if pic is not None:
                    px, py, pb, view, value = pic
                    if px <= x < px + pb and py <= y < py + pb:
                        i0, j0, s = view
                        k = pb / s
                        v = value(int(i0 + (x - px) / k), int(j0 + (y - py) / k))
                        if v < 0.45:
                            col = glyph.mix(_cell_fill(v), BG, level)
                d.point((x, y), fill=col)

def count_new(d, t, c, S, u, view, ax2, ay, box, a, tile):
    """G's count from un (see the block comment above). u: the zoom layout's share (1: the formula above the count
    at r5b's place; 0: G's rest, the formula on top, the count under it)."""
    un, per = (S.unruly, S.perfect)
    f = 'diff(她, img) ='
    fw = mw(f, 18, True)
    right = c[2] - 24
    fy = ease.lerp(c[1] + 8, c[1] + 34, u)
    top = ease.lerp(c[1] + 37, c[1] + 62, u)
    h = round(ease.lerp(COUNT_H, 96, u))
    bottom = top + h
    counted = per is not None and t >= per
    if counted:
        k1 = ease.lerp(FAINT, TXT, ease.prog(t, per, per + 0.12))
    else:
        k1 = ease.lerp(TXT, FAINT, ease.prog(t, un[1], un[1] + 0.15))
    hp = round(h * PLUS_K)
    one_r = right
    if per is not None:
        one_r = ease.lerp(right, right - _plus_w(hp) - PLUS_GAP, ease.smooth(ease.prog(t, per - PLUS_MOVE, per)))
    pb = None
    if counted:
        bump = 1.0 + 0.12 * (1 - ease.ease_out(ease.prog(t, per, per + 0.12)))
        pb = big_word(d, '+1', (right, bottom - _ink_h('+1', hp, bump)), hp, lv(INK, a), 'ra', bump=bump)
    bump1 = 1.0 + 0.14 * (1 - ease.prog(t, un[0], un[0] + 0.12))
    bx = big_word(d, '1', (one_r, top), h, lv(INK, k1 * a), 'ra', bump=bump1)
    mtx(d, (right - fw, fy), f, 18, lv(INK, k1 * a), bold=True)
    if not counted:
        return
    nim = S.nim if S.nim is not None else per
    if t >= nim:
        s = 'not in memory'
        ny = (top + pb[1]) / 2 - 6 + (1 - ease.ease_out(ease.prog(t, nim, nim + 0.14))) * -5
        mtx(d, (right - mw(s, 11), ny), s, 11, lv(INK, TXT * a * ease.prog(t, nim, nim + 0.1)))
    xl = round((pb[0] + pb[2]) / 2)
    if tile is not None:
        cell = tile[0]
        yc = round((cell[1] + cell[3]) / 2)
        y_run, xg = (c[3] - 6, ax2 - 9)
        pts = [(xl, bottom + 3), (xl, y_run), (xg, y_run), (xg, yc), (round(cell[0]) - 3, yc)]
        lu = ease.ease_out(ease.prog(t, per + LEAD_GROW[0], per + LEAD_GROW[1]))
        leader(d, pts, lu, a, (ax2, ay, box, view, S.its))
    if S.human is not None and t >= S.human:
        stamp(d, t, (bx[0], top, right, bottom), S.human, a, pad=STAMP_PAD, gap_x=xl, top_min=top - STAMP_PAD)

def _plus_w(hp):
    """+1's ink width at rest (the 1 moves left by this and PLUS_GAP)."""
    size = GBASE._size_for('+1', hp, True)
    x0, y0, x1, y1 = hud.font(size, '+1', True).getbbox('+1')
    return x1 - x0

def diff_geo(t, c, S):
    """(u, box, ax1, ay, ax2): the zoom layout's share, the pictures' size and where they stand in compare."""
    u = zoom_lay(t, *S.lay)
    box = round(ease.lerp(SIDE, SIDE_Z, u))
    ax1, ay = (c[0] + 46, c[1] + 12)
    return (u, box, ax1, ay, ax1 + box + 50)

def diff_panel(d, t, c, S, inner=None):
    """diff(她.avatar, img) seen through word_zoom (C12/C13, G 61-63): warmth / hands the hand, breath the mouth (her
    bubbles), hair the top of the head (un: her stray hair, 1), ru its new cell by the left ear (G only: it springs
    up); back to the whole pictures on the next lines' downbeats; perfect: 1 -> 2; human: the stamp (G only).
    r5 round 2: the pictures grow to SIDE_Z while the words zoom (zoom_lay; the count and its formula move to the
    info column, above / under each other), and her stray hair has its blue outline (stray_mark). inner: the
    cell row the inspector is comparing now (R-A, between the syllables), or None."""
    if t < S.avatar_at:
        return
    a = ease.prog(t, S.avatar_at, S.avatar_at + 0.1)
    n = sum((1 for s in S.scan if t >= s))
    scan = n * CP.AV_N / 10 if n < 10 else None
    u, box, ax1, ay, ax2 = diff_geo(t, c, S)
    mtx(d, (c[0] + 10, ay + 4), '她', 14, lv(HER_QUIET, a), bold=True)
    view = word_zoom(d, t, S.keys, [(ax1, ay, her_value, HER_FINE), (ax2, ay, S.its, S.its_fine)], box, a, scan)
    gone = 1.0 if S.gone is None else 1 - ease.prog(t, *S.gone)
    stray_mark(d, t, view, ax1, ay, box, S.unruly[0], a * gone)
    if inner is not None:
        inner(d, t, view, ax1, ax2, ay, box, a)
    mtx(d, (ax1 + box + 12, ay + 4), 'img', 12, lv(INK, SUB * a))
    xi = ax2 + box + S.info_dx
    label, lk = zoom_label(t, S.keys)
    if lk > 0.01:
        mtx(d, (xi, ay), f'zoom · {label}', 12, lv(INK, SUB * a * lk))
    if n:
        k_done = 1 - ease.prog(t, S.perfect - 0.1, S.perfect) if S.perfect is not None else 1.0
        mtx(d, (xi, ay + box - 14), f'已比 {min(10, n) * CP.AV_N // 10}/{CP.AV_N} 行', 12, lv(INK, SUB * a * k_done))
    band = box / 10
    odd = {0: S.unruly[0]}
    if S.new is not None:
        odd[int(S.new[1] * 10 / CP.AV_N)] = S.unruly[1]
    for k, at in enumerate(S.scan if S.marks else ()):
        if t < at:
            break
        y = ay + k * band + band / 2 - 7
        uu = ease.prog(t, at, at + 0.08)
        diff = k in odd and t >= odd[k]
        mtx(d, (ax2 + box + 9, y - 1), '≠' if diff else '=', 15, lv(INK, (TXT if diff else 0.7) * a * uu), bold=diff)
    if t >= S.breath:
        hc = hud.her(lit_after(t, S.breath))
        mx, my = [v for v in view_rect(view, ax1, ay, box, 11.5, 13.2, 0, 0)[:2]]
        z = min(3.0, box / view[2] / ACELL)
        for k, (dx, dy, r) in enumerate(((0, 0, 4), (12, -12, 6))):
            uu = ease.ease_out(ease.prog(t, S.breath + 0.12 * k, S.breath + 0.12 * k + 0.7))
            x = mx + (dx + 10 * uu) * z
            y = my + (dy - 34 * uu) * z
            rr = r * z
            if uu < 1 and ax1 + rr <= x <= ax1 + box - rr and (ay + rr <= y <= ay + box - rr):
                d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=lv(hc, 1 - uu * 0.6), width=1 if z < 2 else 2)
    un = S.unruly
    if t >= un[0]:
        steps = sum((1 for x in un if t >= x))
        g = (1 - steps / 3) * 14 / 12 if S.un_steps else 1 - ease.prog(t, un[0], un[0] + 0.14)
        rh = view_rect(view, ax1, ay, box, *STRAY_CELL)
        if _in_box(rh, ax1, ay, box):
            r = 3 + 12 * g
            top = max(rh[1] - r, c[1] + 3)
            d.rectangle((round(rh[0] - r), round(top), round(rh[2] + r), round(rh[3] + r)), outline=lv(INK, a), width=2 if S.un_steps else 1)
        ri = view_rect(view, ax2, ay, box, *STRAY_CELL)
        if _in_box(ri, ax2, ay, box) and (not S.un_steps or steps >= 3):
            if S.new is not None:
                d.rectangle((round(ri[0] - 2), round(ri[1] - 2), round(ri[2] + 2), round(ri[3] + 2)), outline=lv(BG, a))
            d.rectangle((round(ri[0] - 3), round(ri[1] - 3), round(ri[2] + 3), round(ri[3] + 3)), outline=lv(INK, SUB * a))
    tile = None
    if S.new is not None and t >= un[1]:
        tile = new_tile(t, S, view, ax2, ay, box)
        if tile is not None:
            cell, pop = tile
            d.rectangle(tuple((round(v) for v in cell)), fill=_cell_fill(S.its(*S.new), a), outline=lv(INK, a))
            if pop > 0.6:
                _ticks(d, cell, lv(INK, a))
        rh = view_rect(view, ax1, ay, box, *S.new)
        if _in_box(rh, ax1, ay, box):
            d.rectangle(tuple((round(v) for v in (rh[0] - 2, rh[1] - 2, rh[2] + 2, rh[3] + 2))), outline=lv(HER_QUIET, SUB * a))
    if t < un[0]:
        return
    if S.new is not None:
        count_new(d, t, c, S, u, view, ax2, ay, box, a, tile)
        return
    f = 'diff(她, img) ='
    fw = mw(f, 18, True)
    ux, uy = (ease.clamp((u - 0.4) / 0.6), ease.clamp(u / 0.4))
    count_y = ease.lerp(c[1] + 14, c[1] + 62, uy)
    two = S.perfect is not None and t >= S.perfect
    if not two:
        bump = 1.0 + 0.14 * (1 - ease.prog(t, un[0], un[0] + 0.12))
        k1 = ease.lerp(TXT, FAINT, ease.prog(t, un[1], un[1] + 0.15)) if S.new is not None else TXT
        bx = big_word(d, '1', (c[2] - 24, count_y), 96, lv(INK, k1 * a), 'ra', bump=bump)
    else:
        k1 = 1.0
        bump = 1.0 + 0.16 * (1 - ease.ease_out(ease.prog(t, S.perfect, S.perfect + 0.12)))
        bx = big_word(d, '2', (c[2] - 24, count_y), 96, lv(INK, a), 'ra', bump=bump)
    fx = ease.lerp(bx[0] - fw - 18, c[2] - 24 - fw, ux)
    fy = ease.lerp((bx[1] + bx[3]) / 2 - 11, c[1] + 34, uy)
    mtx(d, (fx, fy), f, 18, lv(INK, k1 * a), bold=True)
    if two and S.human is not None and (t >= S.human):
        stamp(d, t, (fx, c[1] + 14, c[2] - 24, c[1] + 14 + 96), S.human, a, pad=9)
G_DIFF = DiffSpec(ZOOM_G, SCAN, UNRULY, BREATH, AVATAR_AT, (WARMTH, W(63, 0)), its_value, ITS_FINE, new=NEW, perfect=PERFECT, human=HUMAN, gone=(GEN_LAST, GEN_LAST + 0.3), nim=S[63][5])

def _diff_inner(d, t, view, ax1, ax2, ay, box, a):
    """R-A: the comparison between the syllables (gone with the blue outline as generate takes the lead: the
    frame G dissolves out of into G5 stays r5's)."""
    k = a * (1 - ease.prog(t, GEN_LAST, GEN_LAST + 0.3))
    n = sum((1 for s in SCAN if t >= s))
    rows = ((n - 1) * CP.AV_N / 10, n * CP.AV_N / 10) if 0 < n < 10 else None
    compare_cursor(d, view, ax1, ax2, ay, box, k, pad_clock(t, AVATAR_AT, G5), rows, (her_value, its_value))

def _cmp_diff(d, t, c):
    """Lines 61-63 (diff_panel with G's spec)."""
    diff_panel(d, t, c, G_DIFF, _diff_inner)

def _passes(lines, cps):
    return CPN._think_passes(lines, cps)
SEGS = sorted([(NEXT_AT, FLOWER)] + CPN._passes(FLOWER, MSG_AT - 0.05) + CPN._landings(MSG) + [(S[59][0], EOS1)] + _passes(THINK_SEE, MCPS) + [(THINK_SEE_END, DRAW_AT)] + list(zip(DRAW_STEPS, DRAW_STEPS[1:] + [AVATAR_AT])) + [(S[63][0], EOS2)])
LENS_ON = [(S[59][0] - 0.3, W(60, 0)), (S[63][0] - 0.3, G5)]

def _forward(d, t, f):
    CPN._stack(d, t, f, M, 1.0, None, 0.0, segs=SEGS)
    k = max((ease.prog(t, a, a + 0.3) * (1 - ease.prog(t, b, b + 0.3)) for a, b in LENS_ON), default=0.0)
    if k <= 0:
        return
    A = BO.ARCH[M]
    x0, pitch, w, ya, yf, h = CPN._cells(f, A['n'], 0)
    head, _fl = CPN._head(t, SEGS, A['n'])
    for layer in LENS_L:
        x = x0 + layer * pitch
        kk = 0.55 * k
        if head is not None and layer <= head < layer + 1.5:
            kk = 1.0
        d.rectangle((x - 2, ya - 2, x + w + 2, yf + h + 2), outline=lv(INK, kk), width=2 if kk > 0.6 else 1)

def _status(t):
    g = ''
    if MSG.tok_t[0] <= t < DRAW_AT:
        g = f'{MSG.n_tok(t)}/{len(MSG.toks)} tok · mem_refs 0'
    elif DRAW_AT <= t < AVATAR_AT:
        g = 'image · mem_refs 0'
    sim = 'sim(her) ?' if t >= EOS1 else 'sim(her) 0.99'
    return {'generate': (g, False), 'compare': (sim, True), 'forward': ('云端 · preview', False)}
RUN = {'input': [(SEE_COMMITS[0][0], SEE_SEND + 0.15)], 'think': [(at, at + len(s) / MCPS + 0.2) for at, s in THINKS], 'trace': [(at, ret[0]) for at, _s, ret in CODE if ret], 'generate': [(NEXT_AT, FLOWER), (MSG.tok_t[0], MSG.done), (S[59][0], EOS1), (DRAW_AT, AVATAR_AT), (S[63][0], EOS2)], 'compare': [(FIND_AT, FIND_RET), (FLOWER - 0.1, FLOWER + 0.3), (S[59][0], EOS1 + 0.1), (SCAN[0], HUMAN + 0.2)], 'forward': SEGS}

def _reads(t):
    """It reads no file of hers (every stand-in read all of them each turn); the grep on -ly reads everything once."""
    Pl = hud.Pulse(t)
    if t >= UNRULY[2]:
        n_ = len(hud.strip_files(t))
        for k_ in range(n_ + 1):
            Pl.hit(k_ if k_ < n_ else 'archive', UNRULY[2] + 0.02 * k_, 0.12)
    Pl.hit('archive', FIND_AT + 0.3, 0.4)
    Pl.hit('archive', FOUND, 0.4)
    return Pl.out

def _mem(d, t, hits, img=None, w=1.0, on=0.0):
    """g_mirror's; batch 3: shaded by w (img), its spinner the leader's (it never leads in G)."""
    with CPN._strip_in(MEM):
        hud.strip(d, t, hits, merged=1.0)
    d.rectangle((MEM[0] + 4, MEM[1] + 8, MEM[2] - 4, MEM[1] + 21), fill=BG)
    if img is not None:
        lead.shade(img, MEM, 1 - w)
    panes.box(d, MEM, 'mem', t, lead_run(min(1.0, 3 * max(hits.values(), default=0.0)), w, on))

def _restore(d, t, c):
    if t < FOUND - 0.4:
        return
    SX, SY, SH = (c[0] + 24, c[1] + 30, 38)
    a0 = ease.prog(t, FOUND - 0.4, FOUND)
    depth = sum((1 for x in DRILL if t >= x))
    for i, (name, note) in enumerate(GG.STRATA):
        y = SY + i * SH
        hers = i == len(GG.STRATA) - 1
        reached = i < depth
        colr = HER_QUIET if hers else INK
        hud.hatch(d, (SX + 30, y + 22, SX + 540, y + 30), lv(INK, 0.14 * a0), 6)
        w = mtx(d, (SX + 36, y + 2), f'archive/{name}/', 14, lv(colr, (0.32 + 0.5 * reached) * a0), bold=hers and reached)
        mtx(d, (max(SX + 250, SX + 36 + w + 14), y + 4), note, 11, lv(INK, SUB * a0))
        if reached:
            u = ease.prog(t, DRILL[i], DRILL[i] + 0.08)
            if hers:
                mtx(d, (SX + 380, y + 2), '1 session · 大肥鱼 · 412 行', 14, lv(hud.her(lit_after(t, HER_ROW)), u), bold=True)
            else:
                mtx(d, (SX + 380, y + 4), '0 sessions', 12, lv(INK, 0.75 * u))
    k = 0.0
    for i in range(depth):
        k = i + ease.ease_out(ease.prog(t, DRILL[i], DRILL[i] + 0.09))
    yb = SY + 8 + max(0.0, k - 1) * SH if depth else SY - 20
    d.line([(SX + 10, SY - 18), (SX + 10, yb)], fill=lv(INK, 0.8 * a0), width=2)
    d.rectangle((SX + 2, yb, SX + 18, yb + 14), fill=lv(hud.SLAB, a0))

def _g5_layout(t):
    r = CPN.right(t)
    if t < FOUND - 0.4:
        return {'trace': (COL, 88, r, 140), 'compare': (COL, 148, r, 528), 'forward': (COL, 536, r, 598)}
    return {'trace': (COL, 88, r, 598)}

def _g5_body(c, img, d):
    t = c.t
    r = CPN.right(t)
    _cmdline(d, t, r)
    restore = t >= FOUND - 0.4
    w, on = (lead_w(t), lead_on(t))
    for name, rect in _g5_layout(t).items():
        d.rectangle(rect, fill=BG)
        with panes.Clip(img, rect) as dd:
            if name == 'trace' and restore:
                _restore(dd, t, rect)
            elif name == 'forward':
                CPN._stack(dd, t, rect, M, 1.0, None, 0.0, segs=())
        status = '云端 · preview' if name == 'forward' else ''
        if name == 'trace' and restore:
            status = f'depth {sum((1 for x in DRILL if t >= x))}/{len(GG.STRATA)}'
        run = panes.run_k(t, [(x, x + 0.1) for x in DRILL] if name == 'trace' else [])
        lead.shade(img, rect, 1 - w[name])
        panes.box(d, rect, name, t, lead_run(run, w[name], on), 1.0, status)
    _mem(d, t, _reads(t), img, w['memory'], on)

def _body(c, img, d):
    t = c.t
    if t >= G5:
        return _g5_body(c, img, d)
    L, _z = CPN.layout(t)
    L = zoom_rects(L, zoom_lay(t, *G_DIFF.lay))
    _cmdline(d, t, CPN.right(t))
    st = _status(t)
    draw = {'input': lambda dd, r: _input(dd, t, r), 'think': lambda dd, r: _think(dd, t, r), 'trace': lambda dd, r: _trace(dd, t, r), 'generate': lambda dd, r: [fn(dd, t, r) for fn in (_gen_wait, _gen_msg, _gen_bloom, _gen_lens1, _gen_draw, _gen_img)], 'compare': lambda dd, r: [fn(dd, t, r) for fn in (_cmp_find, _cmp_cos, _cmp_diff)], 'forward': lambda dd, r: _forward(dd, t, r)}
    w, on = (lead_w(t), lead_on(t))
    for name in ('input', 'think', 'trace', 'generate', 'compare', 'forward'):
        rect = L[name]
        d.rectangle(rect, fill=BG)
        with panes.Clip(img, rect) as dd:
            draw[name](dd, rect)
        status, her = st.get(name, ('', False))
        lead.shade(img, rect, 1 - w[name])
        panes.box(d, rect, name, t, lead_run(panes.run_k(t, RUN[name]), w[name], on), 1.0, status, her)
    _mem(d, t, _reads(t), img, w['memory'], on)

def spans(spans):
    """film.py, DSH_G=r5: v2's G plates out (arcs, both races, the pair), as DSH_G=lead; the 40-layer arcs plate is
    not put on line 58 any more (D7: it moves to interlude 3, interludes.py). g5_city (from G5) is untouched."""
    return [s for s in spans if s.name not in ('g1_arcs', 'g2_race', 'g3_pair', 'g4_race')]
PLATES = {'g5_city': ('forward', 'batch · preview')}

def _plate_chrome(film):
    """The city's pane chrome (g_lead's for g5_city, unchanged)."""

    def fn(img, t):
        if not T0 <= t < T1:
            return None
        d = None
        for sp in getattr(film, 'inside_spans', ()):
            if sp.name not in PLATES or not sp.active(t):
                continue
            a = sp.alpha(t)
            if a <= 0.01:
                continue
            d = d or ImageDraw.Draw(img)
            x0, y0, x1, y1 = sp.rect
            rect = (COL, 88, min(x1, hud.left_rect(t)[2] - 8), 598)
            label, status = PLATES[sp.name]
            panes.box(d, rect, label, t, 1.0, a, status)
        return img if d is not None else None
    return fn

def _character_layer(film, orig):
    old = PaneFrames(P.path('ui/pane_g_mirror'), P.FPS, (P.W, P.H))
    new = PaneFrames(P.path('ui/pane_g_r5'), P.FPS, (P.W, P.H))
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
        pane = new if DSH_N0 <= nf < DSH_N1 else old
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
SHOTS = [('g56_wait', T0, W(57, 0)), ('g57_turns', W(57, 0), W(58, 0)), ('g58_msg', W(58, 0), W(59, 0)), ('g59_flower', W(59, 0), W(60, 0)), ('g60_see', W(60, 0), W(61, 0)), ('g61_scan', W(61, 0), W(62, 0)), ('g62_unruly', W(62, 0), W(63, 0)), ('g63_human', W(63, 0), G5), ('g64_city', G5, FOUND - 0.4), ('g64_found', FOUND - 0.4, T1)]

def register(film):
    for name, a, b in SHOTS:
        add(film, name, a, b, _body, 'you@surface · dsh inspect' if a < G5 else 'you@surface · restore')
    film.character = _character_layer(film, film.character)
    base_levels = film.levels

    def levels(t):
        """As C (c_pane.register): while the terminal fills the frame the right region is terminal too, so the dsh
        window's support dimming must not sit there as a grey block (no D2 break in G now; kept for the city)."""
        lv_ = base_levels(t)
        u = hud.full_u(t)
        if u > 0 and T0 <= t < T1 and (lv_.get('right', 1.0) < 1.0):
            lv_ = dict(lv_)
            lv_['right'] = ease.lerp(lv_['right'], 1.0, ease.clamp(3 * u))
        return lv_
    film.levels = levels
    from groups.f import dissolve
    dissolve(film, 'g56_wait', 0.15)
    dissolve(film, 'g64_city', 0.3)
    hud.LIVE.extend(MSG.falls())
    for at in LENS1[:2]:
        hud.LIVE.append((at, min(next_syllable(at), at + LIT_HOLD)))
    for at in [UNRULY[0], BREATH, HER_ROW]:
        hud.LIVE.append((at, next_syllable(at)))
    for t0, side in [(T0, 'both'), (W(57, 0), 'left'), (DSH_AT, 'right'), (MSG_AT, 'left'), (W(60, 0), 'right'), (SEE_SEND, 'left'), (FOUND, 'right')]:
        film.set_lead(t0, side)
    film.finish.append(_plate_chrome(film))
