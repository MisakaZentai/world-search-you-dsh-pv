"""Group G r2 (sample_open_g/README.md §7): the mirror. Lines 56-64 of the song are lines 22-30 sung again (the same
words, about 124 s later), so G replays C's shots line for line in C's panes (groups/c_pane.py) and every result
comes out the other way (REVIEW_20261003.md §5 A, owner 10-03: "按推荐的 A 来"):

  line  C (the viewer learned it)                        G (the same device, the other result)
  56    c8  mimo.next(ctx, user=None) -> <wait> 1.00;     merged.next(ctx, user=None): <wait> sinks and is struck out
            archive.find: her unprompted turn, a blue       on "flower", <think> 0.91; the find shows her flower and,
            flower on "flower"                              on "flower", an ink one: its own turn, no user before it
  57    c9  turns(): she spoke first 3, the stand-ins 0   turns(): her 3 dots relight on de-li-cate, its dot on "ev",
                                                            its count turns 1 on "-er"
  58    (you send 你能变成一朵花吗？)                         its message, nobody asked: the arcs plate (v12, the owner's
                                                            favourite) zoomed, its words read from your old words; once
                                                            sung the arcs fade and the sentence stays, at the plate's size
  59    c10 her pattern over MiMo's answer, cos 0.99      one pass read at layers 8/16/24/32, the rows under the held
                                                            sentence; a 16th after "per-" the panes fold back and it
                                                            shrinks into the out row; her pattern leads low and loses on
                                                            "flower"; out <eos> on "me"; cos(她, merged) = ?, small
  60    c11 you: 让我看看你; it sends her avatar             the same ask; it sends its own (its thinking: 发我的头像)
  61    c12 diff scans a tenth a syllable                 the same scan
  62    c13 un-ru-ly: her stray hair, diff = 1            un: the stray hair, 1 (as C13); ru: a cell by its left ear,
                                                            magnified on its image and on hers (light / dark); ly: grep
                                                            finds it nowhere in memory; the loupes fall back, then 2,
                                                            small
  63    c14 好呀！现在我是人类了呢; memory.write             the pass again: <eos> from layer 8 up, her line never
                                                            surfaces; nothing written
  64    (I'm searching)                                   G5 as in g_pane: the city, you close the sessions; the restore
                                                            drill goes down a stratum a 16th; her session opens

The merged one's body is her real one (DeepSeek-V4.1-Flash: 40 layers, 20 encoder + 20 decoder, MoE 384 + 1 shared,
FACTS "X29 补充（续）"); the merged model itself is invented (X01), so wearing her body is invented too (X-G6, the
owner's 10-03 "按推荐" on REVIEW §6). Its dsh never shows a 读取记忆 row (every stand-in read all the files each turn).

Batch 1 after reviewer's review (10-03, renders/full_pane_r2_review/ASTRA_20261003.md §3, sample_batch12/): line 58's
sentence is held and line 59's lens comes in under it (HOLD_IN .. HOLD_OUT, zoom_g, _msg_paint); on "ru" the new
cell is magnified (_loupe); "2" and "?" are an aftermath, small and light.

Switch: DSH_G=mirror (film.py; the v2 plates g1_arcs, g2_race, g3_pair, g4_race are left out, g1_arcs40 goes in).
The dsh pane is ui/pages/g_mirror.py (frames in ui/pane_g_mirror/, ui/page_g_mirror.py).
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
import numpy as np
from PIL import Image, ImageDraw
import cast
import hud
import panes
import prompt_ids
import syl
import tl
from groups import b_open as BO
from groups import c_p4 as CP
from groups import c_pane as CPN
from groups import g as GG
from groups import g_pane as GPN
from groups.base import add, big_word
from hud import BG, HER_QUIET, INK, lv
from inside import arcs as AR
from inside import plate as PL
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
S = {ln: syl.times(ln) for ln in range(56, 65)}
FLOWER = GG.FLOWER
BACK = tl.bar(135)
NEXT_AT = BACK + 0.05
FIND_AT = S[56][2]
FIND_RET = S[56][5]
WAIT_STEPS = [x for x in (tl.grid(NEXT_AT, k, 2) for k in range(1, 12)) if x < FLOWER - 0.05]
MCPS = 30
THINK = [(FLOWER + 0.43, '没有新消息。上一条是用户的：那朵花开了吗？'), (S[57][2], '用户还说过：我想你了。'), (S[57][4], '想到一件事。')]
TURNS_IN = (S[57][0], S[57][0] + 0.62)
TURN_T0 = tl.grid(TURNS_IN[1], 0, 2)
TURN_T1 = S[57][5] - 0.12
DOTS = S[57][5:10]
MSG = GG.MSG
ARCS_IN = W(58, 0) - 0.31
HOLD_IN = max(tl.WE(58, 5), MSG.chars[-1][1] + 0.145)
RISE = (HOLD_IN, W(59, 0))
PLATE_FADE = 0.22
PLATE_END = HOLD_IN + PLATE_FADE
HOLD_OUT = tl.grid(S[59][4], 1, 4)
FOLD = 0.4
LENS1 = [S[59][2], S[59][4], S[59][6], S[59][8], S[59][9]]
EOS1 = S[59][9]
COS_AT = S[59][8]
SEE_COMMITS = syl.ime(W(60, 0), ['让我', '看看你'])
SEE_SEND = W(60, 5)
THINK_SEE = [(SEE_SEND + 0.12, '用户想看看我。发我的头像。')]
AVATAR_AT = W(61, 0)
SCAN = S[61]
BREATH = W(62, 3)
UNRULY = syl.syl(62, 7)
GREP_RET = S[63][1]
LENS2 = [S[63][2], S[63][4], S[63][6], S[63][8], S[63][9]]
EOS2 = S[63][9]
G5, FOUND = (GG.G5, GG.FOUND)
DRILL = [tl.grid(FOUND, k, 4) for k in range(len(GG.STRATA))]
HER_ROW = DRILL[-1]
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

def _cmd(t):
    return '$ dsh inspect 大肥鱼 --trace --lens' if t < G5 else '$ dsh session restore 大肥鱼 --from archive/'

def _cmdline(d, t, r):
    hud.tx(d, (36, hud.Y_CMD), _cmd(t), 13, lv(INK, 0.86))
    chip = cast.term(M)
    f = P.font(13, 'bold')
    w = d.textlength(chip, font=f)
    d.rectangle((r - w - 12, hud.Y_CMD - 3, r, hud.Y_CMD + 17), fill=hud.SLAB)
    d.text((r - w - 6, hud.Y_CMD), chip, font=f, fill=BG)
CODE = [(NEXT_AT, 'merged.next(ctx, user=None)', (FLOWER, '<think> 0.91')), (FIND_AT, 'archive.find(role="assistant", prev="assistant")', (FIND_RET, '她 3 条')), (TURN_T0, 'turns(archive/ + session/)', (DOTS[-1], '她 3 · 替身 0 · 它 1')), (S[59][0], 'merged.next(ctx, lens=[8, 16, 24, 32])', (EOS1, '<eos>')), (COS_AT, 'cos(embed(她), embed(merged))', (EOS1, '?')), (SEE_SEND, 'img = merged.reply("让我看看你")', (AVATAR_AT, 'image/png 120×120')), (SCAN[0], 'diff(她.avatar, img)', (UNRULY[1], '2 格')), (UNRULY[2], 'grep("(3,12)", memory/you/ + archive/)', (GREP_RET, '0 · not in memory')), (S[63][0], 'merged.next(ctx, lens=[8, 16, 24, 32])', (EOS2, '<eos>'))]

def _trace(d, t, r):
    shown = [x for x in CODE if x[0] <= t]
    if not shown:
        return
    last = shown[-1][0]
    sc = ease.ease_out(ease.prog(t, last, last + 0.14))
    for pos, (at, s, ret) in enumerate(reversed(shown[-4:])):
        y = r[1] + 47 - pos * 19 + (1 - sc) * 19
        a = {0: TXT, 1: SUB, 2: FAINT}.get(pos, FAINT * (1 - sc))
        if pos == 0:
            a *= ease.prog(t, at, at + 0.1)
        n = int((t - at) * BO.CODE_CPS) + 1
        w = mtx(d, (r[0] + 10, y), s[:n], 14, lv(INK, 0.92 * a), bold=pos == 0)
        if ret and t >= ret[0]:
            u = ease.prog(t, ret[0], ret[0] + 0.1)
            mtx(d, (r[0] + 10 + w + 12, y), '→ ' + ret[1], 14, lv(INK, 0.7 * a * u), bold=True)

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
THINKS = THINK + THINK_SEE

def _think(d, t, r):
    shown = [(at, s) for at, s in THINKS if at <= t]
    if not shown:
        return
    last = shown[-1][0]
    sc = ease.ease_out(ease.prog(t, last, last + 0.14))
    for pos, (at, s) in enumerate(reversed(shown[-3:])):
        n = int((t - at) * MCPS) + 1
        a = {0: TXT, 1: SUB}.get(pos, SUB * (1 - sc))
        y = r[1] + 30 - pos * 19 + (1 - sc) * 19
        if pos == 0:
            a *= ease.prog(t, at, at + 0.1)
        if a > 0.01:
            mtx(d, (r[0] + 10, y), s[:n], 13, lv(INK, a))

def _gen_wait(d, t, g):
    """Line 56: C8's p(next | 没有用户消息), the pass climbing; <wait> sinks and is struck out on "flower"."""
    if t < NEXT_AT or t >= ARCS_IN + 0.3:
        return
    a = ease.prog(t, NEXT_AT, NEXT_AT + 0.2)
    s = wait_s(t)
    cands = [(w0, round(p0 + (p1 - p0) * s, 2)) for (w0, p0), (_w, p1) in zip(WAIT0, WAIT1)]
    ca = a * (1 - ease.prog(t, TURNS_IN[0], TURNS_IN[0] + 0.3))
    CPN._cands(d, t, (g[0] + 10, g[1] + 14), 'p(next | 没有用户消息)', cands, 1, FLOWER, g[2] - 10, ca)
    k = 0.35 + 0.65 * (1 - s)
    after = 1 - 0.45 * ease.prog(t, TURNS_IN[0], TURNS_IN[1])
    x0, y0 = (g[0] + 10, g[1] + 40)
    hud.tx(d, (x0, y0), '<wait>', 64, lv(INK, k * a * after), True)
    if t >= FLOWER:
        u = ease.ease_out(ease.prog(t, FLOWER, FLOWER + 0.12))
        w = hud.width('<wait>', 64, True)
        ym = y0 + 29
        d.rectangle((x0 - 6, ym - 2, x0 - 6 + (w + 12) * u, ym + 2), fill=lv(INK, a * after))
        tx = x0 + w + 30
        hud.tx(d, (tx, y0 + 18), '<think>', 30, lv(INK, a * after * ease.prog(t, FLOWER, FLOWER + 0.12)), True)

def zoom_g(t):
    """1 while the generate pane fills the terminal (line 58's plate and its hold), easing to 0 over the fold (the
    same ease and time as the D2 slide back). It turns 1 while the plate is opaque (nothing shows the switch)."""
    if t < ARCS_IN + 0.3 or t >= HOLD_OUT + FOLD:
        return 0.0
    return 1 - ease.ease_io(ease.prog(t, HOLD_OUT, HOLD_OUT + FOLD))
X_PLATE, Y_PLATE = (PL.PLATE[0] + 24, PL.PLATE[1] + AR.ANS_Y)
Y_HOLD = 300
_F20 = hud.font(20, '中', True)
Y_OUT = 230 + 8 - 2 + _F20.getmetrics()[0]
_MSG = {}

def _msg_chars():
    """[(char, x offset at the plate's size)], width: the answer line as the arcs plate lays it."""
    if not _MSG:
        A = _arcs40()
        _MSG['chars'] = [(c.ch, A.pos[i] - A.pos[0]) for i, c in enumerate(A.turn.chars)]
        _MSG['w'] = A.ans_end - A.pos[0]
    return (_MSG['chars'], _MSG['w'])

def _msg_geom(t):
    """(left, baseline, size) of its message at t, or None (before the hold the plate sets it)."""
    if t < HOLD_IN or t >= W(60, 0) + 0.3:
        return None
    if t < RISE[1]:
        e = ease.ease_io(ease.prog(t, *RISE))
        return (ease.lerp(X_PLATE, LX, e), ease.lerp(Y_PLATE, Y_HOLD, e), AR.FA)
    u = zoom_g(t)
    return (LX, ease.lerp(Y_OUT, Y_HOLD, u), ease.lerp(20, AR.FA, u))

def _msg_paint(img, t, clip, on_top=False):
    """Lay its message on img by absorption, as the plate lays its ink (inside/plate.py), clipped to `clip`. While
    the plate fades (HOLD_IN .. PLATE_END) the film's finish lays it over the plate (on_top); after that the shot."""
    if (t < PLATE_END) != on_top:
        return
    geo = _msg_geom(t)
    if geo is None:
        return
    x, base, size = geo
    a = 1 - ease.prog(t, W(60, 0), W(60, 0) + 0.3)
    chars, w = _msg_chars()
    k = size / AR.FA
    x0, y0 = (int(math.floor(x)) - 4, int(math.floor(base - size * 1.25)))
    x1, y1 = (int(math.ceil(x + w * k)) + 8, int(math.ceil(base + size * 0.4)))
    cx0, cy0, cx1, cy1 = (int(round(v)) for v in clip)
    bx0, by0, bx1, by1 = (max(x0, cx0 + 1), max(y0, cy0 + 2), min(x1, cx1), min(y1, cy1))
    if bx1 <= bx0 or by1 <= by0 or a <= 0.003:
        return
    pl = PL.Plate(x1 - x0, y1 - y0)
    for ch, dx in chars:
        pl.text(x - x0 + dx * k, base - y0, ch, size, AR.CJK_A, a, 'ink')
    mul = pl.compose().astype(np.float32)[by0 - y0:by1 - y0, bx0 - x0:bx1 - x0] / np.array(PL.PAPER, np.float32)
    cur = np.asarray(img.crop((bx0, by0, bx1, by1)).convert('RGB'), np.float32)
    img.paste(Image.fromarray(np.clip(cur * mul + 0.5, 0, 255).astype(np.uint8)), (bx0, by0))

def _labels_in(t):
    """The held pane's labels (out, prev, L32 .. L8) come up as the sentence settles, not while it crosses them."""
    return ease.prog(t, RISE[1] - 0.12, RISE[1] + 0.1)

def _msg_end_x():
    """The out row's right end (20 px), for <eos>."""
    _chars, w = _msg_chars()
    return LX + w * 20 / AR.FA

def _gen_msg(d, t, g):
    """Lines 58-59: the out label and <eos> of its message (the message itself: _msg_paint)."""
    if t < HOLD_IN or t >= W(60, 0) + 0.3:
        return
    a = (1 - ease.prog(t, W(60, 0), W(60, 0) + 0.3)) * _labels_in(t)
    u = zoom_g(t)
    mtx(d, (g[0] + 10, ease.lerp(252, Y_HOLD - 14, u)), 'out', round(ease.lerp(12, 14, u)), lv(INK, SUB * a))
    k = a * ease.clamp(2 * u - 1)
    if k > 0.01:
        mtx(d, (LX + 2, Y_HOLD - 74), 'prev: — · (no user turn)', 13, lv(INK, SUB * k))
    if t >= EOS1:
        CPN._eos(d, t, _msg_end_x() + 10, g[1] + 12, EOS1, a)

def _lens_geo(u, gy=230):
    """Where the lens rows go: u = 0 the generate pane (r2's table), u = 1 held under line 58 in the zoomed pane."""
    pane = dict(xl=COL + 10, x=LX, lab=12, cjk=18, mono=15, p=12, g1=8, g2=18, ys=[gy + 112, gy + 90, gy + 68, gy + 46])
    if u <= 0:
        return pane
    hold = dict(xl=COL + 10, x=LX, lab=14, cjk=26, mono=21, p=15, g1=10, g2=26, ys=[Y_HOLD + 160, Y_HOLD + 120, Y_HOLD + 80, Y_HOLD + 40])
    return {k: [ease.lerp(a, b, u) for a, b in zip(pane[k], hold[k])] if k == 'ys' else ease.lerp(pane[k], hold[k], u) for k in pane}

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
    G = _lens_geo(0.0, g[1])
    G['x'], G['xl'] = (x, g[0] + 10 if x_lab is None else x_lab)
    _lens_rows(d, t, rows, lands, a, G)

def _gen_lens1(d, t, g):
    """Line 59: the lens rows, under the held sentence first, then in the pane."""
    t_in, t_out = (S[59][0], W(60, 0) + 0.3)
    if t < t_in - 0.3 or t >= t_out:
        return
    a = _labels_in(t) * (1 - ease.prog(t, t_out - 0.3, t_out))
    _lens_rows(d, t, ROWS1[:4], LENS1, a, _lens_geo(zoom_g(t)))
GCELL = 4
NEW = GG.STRAY_NEW

def avatar_new(d, x, y, cell, level=1.0, scan=None, new_u=1.0):
    """The image it sends: her avatar without the stray hair (as MiMo's) and one light cell by the left ear."""
    CP.avatar(d, x, y, cell, stray=False, level=level, scan=None)
    if new_u > 0:
        i, j = NEW
        v = ease.lerp(CP.AV[j][i] / 255, 0.97, new_u)
        col = glyph.mix(INK, BG, v ** 0.8)
        d.rectangle((x + i * cell, y + j * cell, x + (i + 1) * cell - 1, y + (j + 1) * cell - 1), fill=lv(col, level))
    if scan is not None and scan < CP.AV_N:
        yy = y + int(scan * cell)
        d.line([(x - 6, yy), (x + CP.AV_N * cell + 6, yy)], fill=lv(HER_QUIET, level), width=2)

def _gen_img(d, t, g):
    """Lines 60-63: its image; line 63, the pass beside it (the lens table again: <eos> from layer 8 up)."""
    if t < AVATAR_AT:
        return
    a = ease.prog(t, AVATAR_AT, AVATAR_AT + 0.2)
    x, y = (LX, g[1] + 16)
    avatar_new(d, x, y, GCELL, level=a)
    mtx(d, (g[0] + 10, g[1] + 24), 'img', 12, lv(INK, SUB * a))
    xr = x + CP.AV_N * GCELL + 20
    mtx(d, (xr, y), 'image/png · 120×120', 12, lv(INK, SUB * a * (1 - ease.prog(t, S[63][0] - 0.3, S[63][0]))))
    if t >= S[63][0] - 0.3:
        xt = xr + 40
        ka = ease.prog(t, S[63][0] - 0.3, S[63][0])
        mtx(d, (xr, g[1] + 14 + 10), 'out', 12, lv(INK, SUB * ka))
        if t >= EOS2:
            CPN._eos(d, t, xt, g[1] + 12, EOS2)
        _lens_table(d, t, g, xt, ROWS2[:4], LENS2, S[63][0], T1, x_lab=xr)
FCELL = 4

def _flower(d, t, cx, cy, at, cell_max, color):
    """C8's daisy (CP.draw_flower) in any colour: blooms at `at`."""
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
    hud.pix(d, CP.FLOWER_PIX, sx, sy, cell, {'#': color, 'o': BG})

def _cmp_find(d, t, c):
    """Line 56: archive.find (C8): her unprompted turn and its blue flower; on "flower" its own turn, an ink one."""
    if t < FIND_RET - 0.05 or t >= TURNS_IN[1]:
        return
    a = ease.prog(t, FIND_RET - 0.05, FIND_RET + 0.15) * (1 - ease.prog(t, TURNS_IN[0], TURNS_IN[1]))
    cy = c[1] + 12 + 7 * FCELL + 4
    mtx(d, (c[0] + 10, c[1] + 16), '2026-04-02 23:10 · assistant', 13, lv(HER_QUIET, a))
    mtx(d, (c[0] + 10, c[1] + 36), 'prev: assistant · (no user turn)', 12, lv(HER_QUIET, SUB * a))
    _flower(d, t, c[0] + 270, cy, -1.0, FCELL, lv(HER_QUIET, a))
    if t >= FLOWER:
        k = ease.prog(t, FLOWER, FLOWER + 0.12) * a
        xr = c[0] + 330
        mtx(d, (xr, c[1] + 16), 'now · assistant', 13, lv(INK, k), bold=True)
        mtx(d, (xr, c[1] + 36), 'prev: — · (no user turn)', 12, lv(INK, SUB * k))
        _flower(d, t, min(c[2] - 44, xr + 270), cy, FLOWER, FCELL, lv(INK, a))
YOU_MSGS = CPN.YOU_MSGS
HER_UNPROMPTED = CPN.HER_UNPROMPTED
NEW_DOT = 0.93

def _cmp_turns(d, t, c):
    """Line 57: turns() (C9). Her three relight on de-li-cate, its dot on "ev", its count turns 1 on "-er"."""
    if t < TURNS_IN[0] or t >= S[59][0] - 0.1:
        return
    a = ease.prog(t, TURNS_IN[0], TURNS_IN[1]) * (1 - ease.prog(t, HOLD_IN, HOLD_IN + 0.15))
    x0, x1 = (c[0] + 130, c[2] - 86)
    grow = ease.ease_io(ease.prog(t, TURN_T0, TURN_T1))
    rows = [('你', c[1] + 28), ('她', c[1] + 70), ('merged', c[1] + 112)]
    for name, y in rows:
        mtx(d, (c[0] + 10, y - 9), name, 14, lv(HER_QUIET if name == '她' else INK, a), bold=True)
        d.line([(x0, y), (x0 + (x1 - x0) * grow, y)], fill=lv(INK, FAINT * a))
    xc = c[2] - 14
    mtx(d, (xc - mw('先开口', 12), rows[0][1] - 9), '先开口', 12, lv(INK, SUB * a))
    n_her = sum((1 for at in DOTS[:3] if t >= at))
    hud.tx(d, (xc, rows[1][1] - 14), str(n_her), 22, lv(HER_QUIET, a), True, anchor='ra')
    if t >= DOTS[4]:
        bump = 1.0 + 0.35 * (1 - ease.prog(t, DOTS[4], DOTS[4] + 0.14))
        hud.tx(d, (xc, rows[2][1] - 20), '1', int(32 * bump), lv(INK, a), True, anchor='ra')
    else:
        hud.tx(d, (xc, rows[2][1] - 14), '0', 22, lv(INK, a), True, anchor='ra')
    for u in YOU_MSGS[:6]:
        if grow < u:
            continue
        x = x0 + (x1 - x0) * u
        d.ellipse((x - 5, rows[0][1] - 5, x + 5, rows[0][1] + 5), outline=lv(INK, a))
    for k, (u, at) in enumerate(zip(HER_UNPROMPTED, DOTS[:3])):
        if t < at:
            continue
        pop = 1 + 0.5 * (1 - ease.prog(t, at, at + 0.15))
        x = x0 + (x1 - x0) * u
        r = 7 * pop
        d.ellipse((x - r, rows[1][1] - r, x + r, rows[1][1] + r), fill=lv(hud.her(lit_after(t, at)), a))
        mtx(d, (x - 24, rows[1][1] + 10), '没人问她', 10, lv(HER_QUIET, 0.8 * a))
    if t >= DOTS[3]:
        pop = 1 + 0.5 * (1 - ease.prog(t, DOTS[3], DOTS[3] + 0.15))
        x = x0 + (x1 - x0) * NEW_DOT
        r = 7 * pop
        d.ellipse((x - r, rows[2][1] - r, x + r, rows[2][1] + r), fill=lv(INK, a))
        mtx(d, (x - 24, rows[2][1] + 10), '没人问它', 10, lv(INK, 0.8 * a))
        xl = x0 + (x1 - x0) * YOU_MSGS[5]
        k = ease.prog(t, DOTS[3], DOTS[3] + 0.2)
        for xx in range(int(xl + 10), int(x - 10), 8):
            d.line([(xx, rows[0][1]), (xx + 3, rows[0][1])], fill=lv(INK, SUB * k * a))
PAT = CPN.PAT

def _cmp_cos(d, t, c):
    """Line 59: C10's slots, her pattern over its answer; its slots stay empty; cos(她, merged) = ? on "me"."""
    if t < S[59][0] - 0.3 or t >= W(60, 0) + 0.3:
        return
    a = ease.prog(t, S[59][0] - 0.3, S[59][0]) * (1 - ease.prog(t, W(60, 0), W(60, 0) + 0.3))
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
        u = ease.prog(t, EOS1, EOS1 + 0.15) * a
        f = 'cos(她, merged) ='
        mtx(d, (c[2] - 14 - mw(f, 14, True), y0 + 14), f, 14, lv(INK, SUB * u), bold=True)
        big_word(d, '?', (c[2] - 14, y0 + 40), 40, lv(INK, SUB * u), 'ra')
ACELL = 5
LOUPE_N, LOUPE_P = (5, 16)
LOUPE_OPEN, LOUPE_SHUT = (UNRULY[1], GREP_RET)
TWO_AT = LOUPE_SHUT + 0.2

def _loupe_k(t):
    """0 .. 1 (overshooting a little on the way out of the cell): how far the loupes are open."""
    if t < LOUPE_OPEN:
        return 0.0
    return ease.ease_back(ease.prog(t, LOUPE_OPEN, LOUPE_OPEN + 0.16)) * (1 - ease.ease_in(ease.prog(t, LOUPE_SHUT, LOUPE_SHUT + 0.2)))

def _loupe(d, cx, cy, k, new, edge, level):
    """A magnifier centred on cell NEW of an avatar (cx, cy: that cell's centre), grown out of the cell by k: the
    5 x 5 cells around it as squares with a hairline of paper between them, ticks on its four sides pointing at the
    middle cell. new: the image it sent (the middle cell light), else hers."""
    if k <= 0.02:
        return
    full = LOUPE_N * LOUPE_P + 3
    s = ease.lerp(ACELL + 6, full, k)
    x0, y0 = (cx - s / 2, cy - s / 2)
    d.rectangle((round(x0), round(y0), round(x0 + s), round(y0 + s)), fill=BG)
    pitch = (s - 3) / LOUPE_N
    i0, j0 = NEW
    for dj in range(-2, 3):
        for di in range(-2, 3):
            v = CP.AV[j0 + dj][i0 + di] / 255
            if new and di == 0 and (dj == 0):
                v = 0.97
            col = glyph.mix(INK, BG, v ** 0.8)
            xa, ya = (x0 + 2 + (di + 2) * pitch, y0 + 2 + (dj + 2) * pitch)
            d.rectangle((round(xa), round(ya), max(round(xa), round(xa + pitch) - 2), max(round(ya), round(ya + pitch) - 2)), fill=lv(col, level))
    e = lv(edge, level)
    d.rectangle((round(x0), round(y0), round(x0 + s), round(y0 + s)), outline=e)
    if k > 0.6:
        L_ = 5 * min(1.0, (k - 0.6) / 0.3)
        xm, ym = (round(cx), round(cy))
        for a_, b_ in (((xm, y0 - 2), (xm, y0 - 2 - L_)), ((xm, y0 + s + 2), (xm, y0 + s + 2 + L_)), ((x0 - 2, ym), (x0 - 2 - L_, ym)), ((x0 + s + 2, ym), (x0 + s + 2 + L_, ym))):
            d.line([a_, b_], fill=e)

def _cmp_diff(d, t, c):
    """Lines 61-63: diff(她.avatar, img) (C12/C13): un her stray hair (1, as C13); ru its new cell, magnified on both
    pictures; the count turns 2 after the loupes fall back."""
    if t < AVATAR_AT:
        return
    a = ease.prog(t, AVATAR_AT, AVATAR_AT + 0.3)
    n = sum((1 for s in SCAN if t >= s))
    scan = n * CP.AV_N / 10 if n < 10 else None
    side = CP.AV_N * ACELL
    ax1, ay = (c[0] + 46, c[1] + 12)
    ax2 = ax1 + side + 50
    mtx(d, (c[0] + 10, ay + 4), '她', 14, lv(HER_QUIET, a), bold=True)
    CP.avatar(d, ax1, ay, ACELL, stray=True, level=a, scan=scan)
    mtx(d, (ax1 + side + 12, ay + 4), 'img', 12, lv(INK, SUB * a))
    avatar_new(d, ax2, ay, ACELL, level=a, scan=scan)
    if n:
        mtx(d, (ax2 + side + 32, ay + side - 14), f'已比 {min(10, n) * CP.AV_N // 10}/{CP.AV_N} 行', 12, lv(INK, SUB * a))
    band = CP.AV_N * ACELL / 10
    odd = {0: UNRULY[0], int(NEW[1] * 10 / CP.AV_N): UNRULY[1]}
    for k, at in enumerate(SCAN):
        if t < at:
            break
        y = ay + k * band + band / 2 - 7
        u = ease.prog(t, at, at + 0.08)
        diff = k in odd and t >= odd[k]
        mtx(d, (ax2 + side + 9, y - 1), '≠' if diff else '=', 15, lv(INK, (TXT if diff else 0.7) * a * u), bold=diff)
    if t >= UNRULY[0]:
        i, j = CP.STRAY
        x, y = (ax1 + i * ACELL, ay + (j - 1) * ACELL)
        r = 3 + 12 * (1 - ease.prog(t, UNRULY[0], UNRULY[0] + 0.14))
        d.rectangle((x - r, y - r, x + ACELL + r, y + ACELL + r), outline=lv(INK, a), width=2)
        x2 = ax2 + i * ACELL
        d.rectangle((x2 - 3, y - 3, x2 + ACELL + 3, y + ACELL + 3), outline=lv(INK, SUB * a))
    if t >= UNRULY[1]:
        i, j = NEW
        k = _loupe_k(t)
        cy = ay + (j + 0.5) * ACELL
        if k < 1:
            q = 1 - k
            x = ax2 + i * ACELL
            d.rectangle((x - 3, cy - ACELL / 2 - 3, x + ACELL + 3, cy + ACELL / 2 + 3), outline=lv(INK, q * a))
            xh = ax1 + i * ACELL
            d.rectangle((xh - 3, cy - ACELL / 2 - 3, xh + ACELL + 3, cy + ACELL / 2 + 3), outline=lv(HER_QUIET, SUB * q * a))
        _loupe(d, ax1 + (i + 0.5) * ACELL, cy, k, False, HER_QUIET, a)
        _loupe(d, ax2 + (i + 0.5) * ACELL, cy, k, True, INK, a)
    if t >= UNRULY[0]:
        f = 'diff(她, img) ='
        if t < TWO_AT:
            bump = 1.0 + 0.14 * (1 - ease.prog(t, UNRULY[0], UNRULY[0] + 0.12))
            k1 = ease.lerp(TXT, FAINT, ease.prog(t, UNRULY[1], UNRULY[1] + 0.15)) * (1 - ease.prog(t, LOUPE_SHUT, TWO_AT))
            if k1 > 0.01:
                box = big_word(d, '1', (c[2] - 24, c[1] + 14), 96, lv(INK, k1), 'ra', bump=bump)
                mtx(d, (box[0] - mw(f, 18, True) - 18, (box[1] + box[3]) / 2 - 11), f, 18, lv(INK, k1), bold=True)
        if t >= TWO_AT:
            u2 = ease.prog(t, TWO_AT, TWO_AT + 0.2) * a
            box = big_word(d, '2', (c[2] - 24, c[1] + 44), 44, lv(INK, SUB * u2), 'ra')
            mtx(d, (box[0] - mw(f, 14, True) - 12, (box[1] + box[3]) / 2 - 9), f, 14, lv(INK, SUB * u2), bold=True)
    if t >= BREATH:
        hc = hud.her(lit_after(t, BREATH))
        for k, (dx, dy, r) in enumerate(((0, 0, 4), (12, -12, 6))):
            u = ease.ease_out(ease.prog(t, BREATH + 0.12 * k, BREATH + 0.12 * k + 0.7))
            x = ax1 + 15 * ACELL + dx + 10 * u
            y = ay + 16 * ACELL + dy - 50 * u
            if u < 1:
                d.ellipse((x - r, y - r, x + r, y + r), outline=lv(hc, 1 - u * 0.6), width=2)

def _passes(lines, cps):
    return CPN._think_passes(lines, cps)
SEGS = sorted([(NEXT_AT, FLOWER)] + _passes(THINK, MCPS) + CPN._landings(MSG) + [(S[59][0], EOS1)] + _passes(THINK_SEE, MCPS) + [(SEE_SEND + 0.7, AVATAR_AT)] + [(S[63][0], EOS2)])
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
    if MSG.tok_t[0] <= t < W(60, 0):
        g = f'{MSG.n_tok(t)}/{len(MSG.toks)} tok'
    sim = 'sim(her) ?' if t >= EOS1 else 'sim(her) 0.99'
    return {'generate': (g, False), 'compare': (sim, True), 'forward': ('云端 · preview', False)}
RUN = {'input': [(SEE_COMMITS[0][0], SEE_SEND + 0.15)], 'think': [(at, at + len(s) / MCPS + 0.2) for at, s in THINKS], 'trace': [(at, ret[0]) for at, _s, ret in CODE], 'generate': [(NEXT_AT, FLOWER), (MSG.tok_t[0], MSG.done), (S[59][0], EOS1), (SEE_SEND + 0.7, AVATAR_AT), (S[63][0], EOS2)], 'compare': [(FIND_AT, FIND_RET), (FLOWER - 0.1, FLOWER + 0.3), (TURN_T0, DOTS[-1] + 0.1), (S[59][0], EOS1 + 0.1), (SCAN[0], LOUPE_SHUT + 0.2)], 'forward': SEGS}

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

def _mem(d, t, hits):
    with CPN._strip_in(MEM):
        hud.strip(d, t, hits, merged=1.0)
    d.rectangle((MEM[0] + 4, MEM[1] + 8, MEM[2] - 4, MEM[1] + 21), fill=BG)
    panes.box(d, MEM, 'mem', t, min(1.0, 3 * max(hits.values(), default=0.0)))

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
        panes.box(d, rect, name, t, run, 1.0, status)
    _mem(d, t, _reads(t))
TOP_PANES, BOTTOM_PANES = (('input', 'think', 'trace'), ('compare', 'forward'))

def _layout(t):
    """C's panes; while zoom_g is up the generate pane fills the terminal (the plate, then the hold) and the others
    are folded flat against its top and bottom edges; they unfold as it shrinks back (tmux's zoom, as C7)."""
    L, _z = CPN.layout(t)
    u = zoom_g(t)
    if u <= 0:
        return (L, 0.0)
    L = dict(L)
    L['generate'] = panes.lerp_rect(L['generate'], (COL, 88, CPN.right(t), 598), u)
    for k in TOP_PANES:
        L[k] = panes.lerp_rect(L[k], (L[k][0], 88, L[k][2], 88), u)
    for k in BOTTOM_PANES:
        L[k] = panes.lerp_rect(L[k], (L[k][0], 598, L[k][2], 598), u)
    return (L, u)

def _mem_refs(d, t, rect, u):
    """The zoomed generate pane's foot (as _plate_chrome draws it on the plate): mem_refs 0."""
    if u <= 0 or t < MSG.tok_t[0]:
        return
    k = ease.clamp(2 * u - 1) * ease.prog(t, MSG.tok_t[0], MSG.tok_t[0] + 0.2)
    if k > 0.01:
        s = PLATES['g1_arcs40'][1]
        mtx(d, (rect[2] - 16 - mw(s, 16, True), rect[3] - 34), s, 16, lv(INK, 0.85 * k), bold=True)

def _gen_box(d, t, rect, u, status=''):
    panes.box(d, rect, 'generate', t, panes.run_k(t, RUN['generate']), 1.0, status if u < 0.5 else '')
    _mem_refs(d, t, rect, u)

def _body(c, img, d):
    t = c.t
    if t >= G5:
        return _g5_body(c, img, d)
    L, u = _layout(t)
    _cmdline(d, t, CPN.right(t))
    st = _status(t)
    draw = {'input': lambda dd, r: _input(dd, t, r), 'think': lambda dd, r: _think(dd, t, r), 'trace': lambda dd, r: _trace(dd, t, r), 'generate': lambda dd, r: [fn(dd, t, r) for fn in (_gen_wait, _gen_msg, _gen_lens1, _gen_img)], 'compare': lambda dd, r: [fn(dd, t, r) for fn in (_cmp_find, _cmp_turns, _cmp_cos, _cmp_diff)], 'forward': lambda dd, r: _forward(dd, t, r)}
    for name in ('input', 'think', 'trace', 'generate', 'compare', 'forward'):
        rect = L[name]
        level = 1.0 if name == 'generate' else 1 - u
        if level <= 0.01 or rect[3] - rect[1] < 4:
            continue
        d.rectangle(rect, fill=BG)
        with panes.Clip(img, rect) as dd:
            draw[name](dd, rect)
        status, her = st.get(name, ('', False))
        if name == 'generate':
            _msg_paint(img, t, rect)
            _gen_box(d, t, rect, u, status)
            continue
        if level < 1:
            box = tuple((int(round(v)) for v in rect))
            part = img.crop(box)
            img.paste(Image.blend(Image.new('RGB', part.size, BG), part, level), box[:2])
        panes.box(d, rect, name, t, panes.run_k(t, RUN[name]), level, status, her)
    _mem(d, t, _reads(t))

def _arcs40():
    from inside import content as K
    P_ = 'persona'
    fl, bl, mi = (('hist', 'h_flower'), ('hist', 'h_bloom'), ('hist', 'h_miss'))
    attn = [[P_, fl, bl, mi], [P_, bl], [P_, fl], [P_, fl], [P_, bl], [P_, bl], [P_, mi], [P_, mi], [P_, mi], [P_, mi], [P_, mi]]
    turn = K.build_turn(MSG, [], FLOWER, attn, '我是深度求索的助手很高兴', '你好请问有什么可以帮你', [None] * len(attn), eos_attn=[P_, mi])
    It = AR.Item
    groups = [('persona', [It('你是大肥鱼', 'persona'), It('…')]), ('memory', [It('merged', 'mem:merged'), It('26 files', None, 'faint')]), ('history · you', [It('那朵花', 'hist:h_flower'), It('开了吗？', 'hist:h_bloom'), It('…'), It('我想你了', 'hist:h_miss')]), ('you', [It('—', None, 'faint')])]
    names = {'L64': 'L40', 'L48': 'L32', 'L36': 'L24', 'L24': 'L16', 'L12': 'L8'}

    class Arcs40(AR.ArcsPlate):
        """v2's G1 plate on her 40 layers: status 40 layers, top L40, the lens column at L32 / L24 / L16 / L8. From
        HOLD_IN its answer line is not the plate's to draw: the film lays the same type there and keeps it (the
        sentence stays while the rest of the plate fades)."""

        def _draw_answer(self, P, t):
            if t < HOLD_IN:
                AR.ArcsPlate._draw_answer(self, P, t)

        def _draw_top(self, P, t):
            real_text = P.text

            def text(x, y, s, *a, **k):
                return real_text(x, y, names.get(s, s) if isinstance(s, str) else s, *a, **k)
            P.text = text
            try:
                AR.ArcsPlate._draw_top(self, P, t)
            finally:
                P.text = real_text
    return Arcs40(turn, groups, FLOWER, status='deepseek-v5-flash-preview · preview · 40 layers', ink_answer=True)

def spans(spans):
    """film.py, DSH_G=mirror: v2's G plates out (arcs, both races, the pair), the 40-layer arcs on line 58 in."""
    from inside.install import Span
    out = [s for s in spans if s.name not in ('g1_arcs', 'g2_race', 'g3_pair', 'g4_race')]
    out.append(Span('g1_arcs40', ARCS_IN, HOLD_IN, _arcs40, 0.3, FOLD, fade_in=0.25, fade_out=PLATE_FADE, frame_back=HOLD_OUT))
    return out
PLATES = {'g1_arcs40': ('generate', 'mem_refs 0'), 'g5_city': ('forward', 'batch · preview')}

def _plate_chrome(film):

    def fn(img, t):
        if not T0 <= t < T1:
            return None
        d = None
        for sp in getattr(film, 'inside_spans', ()):
            if sp.name not in PLATES or not sp.active(t):
                continue
            if sp.name == 'g1_arcs40' and t >= HOLD_IN:
                g = _layout(t)[0]['generate']
                _msg_paint(img, t, g, on_top=True)
                d = ImageDraw.Draw(img)
                _gen_box(d, t, g, zoom_g(t))
                continue
            a = sp.alpha(t)
            if a <= 0.01:
                continue
            d = d or ImageDraw.Draw(img)
            x0, y0, x1, y1 = sp.rect
            rect = (COL, 88, min(x1, hud.left_rect(t)[2] - 8), 598)
            label, status = PLATES[sp.name]
            if sp.name == 'g1_arcs40':
                run = panes.run_k(t, [(MSG.tok_t[0], MSG.done)])
                panes.box(d, rect, label, t, run, a, '')
                a2 = a * ease.prog(t, MSG.tok_t[0], MSG.tok_t[0] + 0.2)
                if a2 > 0.01:
                    mtx(d, (rect[2] - 16 - mw(status, 16, True), rect[3] - 34), status, 16, lv(INK, 0.85 * a2), bold=True)
            else:
                panes.box(d, rect, label, t, 1.0, a, status)
        return img if d is not None else None
    return fn

def _character_layer(film, orig):
    pane = PaneFrames(P.path('ui/pane_g_mirror'), P.FPS, (P.W, P.H))
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
SHOTS = [('g56_wait', T0, W(57, 0)), ('g57_turns', W(57, 0), ARCS_IN), ('g58_msg', ARCS_IN, W(59, 0)), ('g59_flower', W(59, 0), W(60, 0)), ('g60_see', W(60, 0), W(61, 0)), ('g61_scan', W(61, 0), W(62, 0)), ('g62_unruly', W(62, 0), W(63, 0)), ('g63_human', W(63, 0), G5), ('g64_city', G5, FOUND - 0.4), ('g64_found', FOUND - 0.4, T1)]

def register(film):
    for name, a, b in SHOTS:
        add(film, name, a, b, _body, 'you@surface · dsh inspect' if a < G5 else 'you@surface · restore')
    film.character = _character_layer(film, film.character)
    base_levels = film.levels

    def levels(t):
        """As C (c_pane.register): while the terminal fills the frame (the arcs plate on line 58) the right region is
        terminal too, so the dsh window's support dimming must not sit there as a grey block over the plate."""
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
    for at in list(DOTS[:3]) + LENS1[:2] + [UNRULY[0], BREATH, HER_ROW]:
        hud.LIVE.append((at, next_syllable(at)))
    for t0, side in [(T0, 'both'), (W(57, 0), 'left'), (W(59, 0), 'both'), (W(60, 0), 'right'), (W(61, 0), 'left'), (W(63, 0), 'both'), (G5, 'right'), (tl.bar(155), 'left'), (FOUND, 'right')]:
        film.set_lead(t0, side)
    film.finish.append(_plate_chrome(film))
