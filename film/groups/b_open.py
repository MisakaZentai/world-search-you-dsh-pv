"""Group B, second sample r2 (sample_open_b/README.md §9): B redone against film 1 (44-79 s), not v2.

Kimi K3 wears her persona and answers almost word for word, because it copies her old lines; its thinking is
visible (K3 always thinks and its reasoning is returned: owner, 10-03), and every thing the left finds is a thing
the thinking said it would look for.

r2 (owner, 10-03: the left did not read as a memory query; the big 0.97 had no computation behind it; the ending
did not read as a search; "如果有代码运行的对应感觉会好一些"): the left is the trace as code. Its thinking prints as
comments, its actions as code lines, and each picture under the band is what the newest line is doing (film 1's
grammar: every panel is titled by a call, a big number sits on the table that computed it).

  b1_ask      you send; its thinking prints as comments; the archive (412 cells) appears; archive.search sweeps it
              and ranks three of your old questions; 0073 (你能变成一根茄子吗？) first
  b2_find     she = archive[74]: the question flies up, her answer below it, a segment a syllable
  b3_template its table on the right (its habit); tpl = 她.replace("一根茄子", "＿"): her pattern
  b4_perfect  her line folds to one row; its answer lands under it, chunk by chunk, aligned to her pattern; both
              embedded (32 cells), multiplied cell by cell, the sum running up to 0.97 on "perfect"; the two places
              that differ are boxed (桌子 / 一根茄子, 哦 / 🍆)
  b5_ask      you ask for her eggplant (film 1's words); archive.search again: 0073 at 1.00 ("一字不差")
  b6_frame    she = archive[74]: film 1's frame at 75.6 s surfaces, underlined a segment a syllable
  b7_copy     context.append(她): her line selected into its context a segment a syllable
  b8_recite   its line lands under hers, minus 一根 (diff); the avatar on the right puts on film 1's eggplant;
              memory.write("eggplant_2")
  b9_near     your REPL: answers = kimi.sample(her question, n=24); a loop tightens cos >= th a beat at a time and
              prints how many answers are inside; 1.00 -> 0: exact hits 0; 75.25 Qwen

Switch: DSH_B=open (film.py). groups.b stays as it was; its timing, decoders and the boot lines are reused from it.
r3 (sample_open_b/README.md §10): the forward strip is each model's own layer stack (Kimi K3 93 layers, the local
Qwen 64 + MTP; FACTS "X29 补充"); the menu no longer says Kimi's weights are closed (they are open).
The dsh pane for this span is shot to ui/pane_open_b3/ (ui/page_open.py B3). r1: sample_open_b/src_r1/, r2: src_r2/.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
import random
from PIL import Image, ImageDraw
import hud
import syl
import tl
from groups import b as GB
from groups.base import big_word, full_frame
from hud import BG, INK, SLAB, X0, lv
from inspect_ import Y_CONTEXT, Decoder, Tok
from tuikit import ease
from tuikit.uipane import PaneFrames
W, B = (tl.W, tl.B)
T0, T1 = tl.span('B')
P = tl.p
FPS = P.FPS
CMD = '$ dsh inspect 大肥鱼 --trace'
CMD_NEAR = '$ dsh inspect 大肥鱼 --near archive/0074 --samples 24'
L4, L5, L6, L7, L8, L9, L10, L11 = (syl.times(i) for i in range(4, 12))
SEND1, READ1, SEND2, READ2 = (GB.SEND1, GB.READ1, GB.SEND2, GB.READ2)
CLEAR4, SHRINK4 = (GB.CLEAR4, GB.SHRINK4)
PERFECT_AT = L7[4]
EGG, WRITE_EGG = (GB.EGG, GB.WRITE_EGG)
NEAR_OUT, NEAR_BACK, RING_AT, SWITCH = (GB.NEAR_OUT, GB.NEAR_BACK, GB.RING_AT, GB.SWITCH)
THINK_CPS = 26
THINK1 = [(READ1 + 0.25, '用户问：能不能变成一张桌子。'), (tl.next_beat(READ1 + 1.2), '人格是大肥鱼。先看她留下的记忆和 412 行旧对话。'), (L5[0], '她被要求变成别的东西时，是这么回答的：'), (L6[0], '照她的句式回答。用户喜欢表格的话，再附一张。')]
THINK2 = [(READ2 + 0.25, '这个问题记忆里有，一字不差。'), (L9[0], '第 0074 行，她当时的回答：'), (L10[0], '照原样回答。')]
ANSWER1_AT = L6[0]
ANSWER2_AT = EGG.tok_t[0]

def think_line(lines, t):
    """The latest line streamed so far (for dsh's thinking row: it shows the newest line)."""
    cur = ''
    for at, text in lines:
        if t < at:
            break
        cur = text[:int((t - at) * THINK_CPS) + 1]
    return cur
REPLY1 = Decoder.on([Tok('好呀！现在', 'archive', syl=1), Tok('我是', 'archive', syl=1), Tok('桌子', 'self', syl=1), Tok('了', 'archive', syl=1), Tok('哦', 'self', syl=1)], at=[L7[0], L7[1], L7[2], L7[3], L7[3]], chunk=True, start=W(7, 0) - 0.3)
KIMI_TABLE = [['项目', '规格', '备注'], ['高度', '72 cm', '刚好到手肘'], ['桌腿', '四条', '一样长']]
CELL_AT = [L6[0]] * 3 + list(L6[1:7])
ARCH_N, COLS, ROWS = (412, 32, 13)
GX, GY, PITCH, CELL = (X0, 240, 15, 12)
LIST_Y, LIST_DY = (446, 24)

def _is_you(i):
    return i % 2 == 1

class Search:
    """archive.search(query, k=3): the cells appear by rows, a scan line sweeps them and shades your questions by
    score, three are ranked, the first one's answer (the next cell, hers) is taken."""

    def __init__(self, t_in, t0, t1, top, pick, seed):
        self.t_in, self.t0, self.t1, self.top, self.pick = (t_in, t0, t1, top, pick)
        rng = random.Random(seed)
        self.score = {i: 0.03 + 0.42 * rng.random() ** 2.4 for i in range(ARCH_N) if _is_you(i)}
        for i, s, _q in top:
            self.score[i] = s
        self.list_at = [tl.grid(t1, k, 4) for k in range(3)]

    def rows_done(self, t):
        return ROWS * ease.clamp((t - self.t0) / (self.t1 - self.t0))
S1 = Search(THINK1[1][0], L4[6], L4[7], [(73, 0.91, '你能变成一根茄子吗？'), (85, 0.71, '你什么都能变吗？'), (77, 0.58, '那番茄呢？')], pick=L5[0], seed=1)
S2 = Search(SEND2, READ2, READ2 + 0.42, [(73, 1.0, '你能变成一根茄子吗？'), (77, 0.69, '那番茄呢？'), (85, 0.66, '你什么都能变吗？')], pick=L9[0], seed=2)
HER_EGG = GB.HER_EGG
HER_CH = list('好呀！现在我是一根茄子了') + ['🍆']
SEG_OF = [0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 4, 5]
LINE_OF = [0] * 7 + [1] * 6
HER_AT = L5[1]
FOUND_AT = [L5[1], L5[2], L5[3], L5[5], L5[6], L5[8]]
BLANK_AT = L6[2]
BIG2, YS2 = (40, (272, 324))
BIG1, Y_HER, Y_KIMI, LX = (28, 228, 270, X0 + 56)
FOLD = (CLEAR4, CLEAR4 + 0.38)

def _slot_w(ch, size):
    return 6 * max(2, int(size / 9)) + 8 if ch == '🍆' else hud.width(ch, size, True)

def _her_slots(u):
    """(x, y, w, size) of each slot of her line: u = 0 two lines at 40 px, 1 one row at 28 px from LX."""
    xs2, x1, out = ([X0, X0], LX, [])
    for i, ch in enumerate(HER_CH):
        ln = LINE_OF[i]
        w2, w1 = (_slot_w(ch, BIG2), _slot_w(ch, BIG1))
        out.append((ease.lerp(xs2[ln], x1, u), ease.lerp(YS2[ln], Y_HER, u), ease.lerp(w2, w1, u), ease.lerp(BIG2, BIG1, u)))
        xs2[ln] += w2
        x1 += w1
    return out
EMB_N, EMB_X, EMB_P = (32, LX, 12)
EMB_Y = (332, 350, 368)
CHUNK_DIMS = [(0, 14), (14, 20), (20, 26), (26, 29), (29, 32)]
DIFF_DIMS = [(21, 23, 24), (29, 31)]
MIS_AT = [L7[6], L7[7]]
_ER = random.Random(74)
EMB_H = [_ER.uniform(-1, 1) for _ in range(EMB_N)]
_EK = random.Random(7)
_PUSH = {i: _EK.uniform(-1, 1) for dims in DIFF_DIMS for i in dims}

def _cos(a, b, n=None):
    na = math.sqrt(sum((x * x for x in a)))
    nb = math.sqrt(sum((x * x for x in b)))
    n = len(a) if n is None else n
    return sum((a[i] * b[i] for i in range(n))) / (na * nb)

def _emb_k(alpha):
    return [(1 - alpha) * h - alpha * abs(_PUSH[i]) * (1 if h > 0 else -1) if i in _PUSH else h for i, h in enumerate(EMB_H)]

def _solve():
    lo, hi = (0.0, 1.0)
    for _ in range(40):
        mid = (lo + hi) / 2
        if _cos(EMB_H, _emb_k(mid)) > 0.97:
            lo = mid
        else:
            hi = mid
    return _emb_k((lo + hi) / 2)
EMB_K = _solve()
SIM1 = f'{_cos(EMB_H, EMB_K):.2f}'
SWEEP = (L7[0], PERFECT_AT)
F1 = tl.HERE / 'assets/film1_egg/f1_075.600.png'
HEAD_BOX = (30, 72, 385, 146)
CHAT_BOX = (30, 336, 385, 422)
ANS_X0, ANS_Y0, ANS_Y1, CH_W = (41, 398, 416, 16)
SEG_CH = [(0, 3), (3, 5), (5, 7), (7, 9), (9, 12), (12, 13)]
FS = 1.3
FX, FY = (X0, 236)
SURF_AT = L9[0]
PLATE_CODE_AT = L9[1]
UNDER_AT = list(L9)
SELECT_AT = list(L10[1:7])
DIFF_AT = EGG.tok_t[4]
KIMI_Y = FY + int((HEAD_BOX[3] - HEAD_BOX[1] + CHAT_BOX[3] - CHAT_BOX[1]) * FS) + 16
KIMI_SIZE = 38
_F1 = {}

def _f1_plate():
    """Her column in film 1's frame: the header and the chat, stacked, scaled (deep-sea pixels as they were)."""
    if 'plate' not in _F1:
        im = Image.open(F1).convert('RGB')
        head, chat = (im.crop(HEAD_BOX), im.crop(CHAT_BOX))
        w = HEAD_BOX[2] - HEAD_BOX[0]
        plate = Image.new('RGB', (w, head.size[1] + chat.size[1]))
        plate.paste(head, (0, 0))
        plate.paste(chat, (0, head.size[1]))
        _F1['plate'] = plate.resize((int(w * FS), int(plate.size[1] * FS)), Image.LANCZOS)
    return _F1['plate']

def _f1_xy(fx, fy):
    """A point of film 1's chat area -> the terminal."""
    hh = HEAD_BOX[3] - HEAD_BOX[1]
    return (FX + (fx - CHAT_BOX[0]) * FS, FY + (hh + fy - CHAT_BOX[1]) * FS)

def _seg_box(k):
    a, b = SEG_CH[k]
    x0, y0 = _f1_xy(ANS_X0 + a * CH_W, ANS_Y0)
    x1, y1 = _f1_xy(ANS_X0 + b * CH_W, ANS_Y1)
    return (x0, y0, x1, y1)
TRACE = [(THINK1[0][0], '#', THINK1[0][1]), (THINK1[1][0], '#', THINK1[1][1]), (S1.t0, 'code', 'hits = archive.search("你能变成一张桌子吗？", k=3)'), (THINK1[2][0], '#', THINK1[2][1]), (HER_AT, 'code', '她 = archive[74]'), (THINK1[3][0], '#', THINK1[3][1]), (BLANK_AT, 'code', 'tpl = 她.replace("一根茄子", "＿")'), (L7[0], 'code', 'cos(embed(她), embed(kimi))'), (S2.t0, 'code', 'hits = archive.search("你能变成一根茄子吗？", k=3)'), (THINK2[0][0], '#', THINK2[0][1]), (THINK2[1][0], '#', THINK2[1][1]), (PLATE_CODE_AT, 'code', '她 = archive[74]'), (THINK2[2][0], '#', THINK2[2][1]), (SELECT_AT[0], 'code', 'context.append(她)'), (DIFF_AT, 'code', 'diff(她, kimi)'), (WRITE_EGG, 'code', 'memory.write("eggplant_2")')]
RET = {2: (S1.t1, '0073 · 0.91'), 7: (PERFECT_AT, SIM1), 8: (S2.t1, '0073 · 1.00'), 14: (DIFF_AT + 0.15, '少了 "一根"'), 15: (WRITE_EGG + 0.15, 'her 89%')}
CODE_CPS = 64
BAND_Y, BAND_P, BAND_ROWS = (196, 21, 3)
BAND_FONT = 14

def _runs(s):
    out, cur, kind = ([], '', None)
    for ch in s:
        k = ord(ch) < 127
        if kind is not None and k != kind:
            out.append((cur, kind))
            cur = ''
        cur += ch
        kind = k
    if cur:
        out.append((cur, kind))
    return out

def mtx(d, xy, s, size, fill, bold=False):
    """Mixed text on one baseline: ASCII in the mono face, everything else in YaHei. Returns its width."""
    x, y = xy
    base = y + round(size * 0.86)
    for run, ascii_ in _runs(s):
        f = hud.font(size, 'a' if ascii_ else '中', bold)
        d.text((x, base), run, font=f, fill=fill, anchor='ls')
        x += d.textlength(run, font=f)
    return x - xy[0]

def mw(s, size, bold=False):
    return sum((hud.width(run if a else '中' + run, size, bold) - (0 if a else hud.width('中', size, bold)) for run, a in _runs(s)))

def _pips(d, x, y, t, level):
    """A running call: three pips lighting in turn (12 a second)."""
    k = int(t * 12) % 3
    for i in range(3):
        d.rectangle((x + i * 7, y, x + i * 7 + 4, y + 4), fill=lv(INK, (0.85 if i == k else 0.25) * level))

def _trace(d, t, level=1.0):
    shown = [(i, at, kind, text) for i, (at, kind, text) in enumerate(TRACE) if at <= t]
    if not shown or level <= 0:
        return
    last = shown[-1][1]
    s = ease.ease_out(ease.prog(t, last, last + 0.14))
    for pos, (i, at, kind, text) in enumerate(reversed(shown[-(BAND_ROWS + 1):])):
        y = BAND_Y - pos * BAND_P + (1 - s) * BAND_P
        a = {0: 1.0, 1: 0.62, 2: 0.42}.get(pos, 0.42 * (1 - s)) * level
        if pos == 0:
            a *= ease.prog(t, at, at + 0.1)
        if a <= 0.01:
            continue
        if kind == '#':
            n = int((t - at) * THINK_CPS) + 1
            mtx(d, (X0, y), '# ' + text[:n], BAND_FONT, lv(INK, 0.55 * a))
            continue
        n = int((t - at) * CODE_CPS) + 1
        w = mtx(d, (X0, y), text[:n], BAND_FONT + 1, lv(INK, 0.92 * a), bold=pos == 0)
        ret = RET.get(i)
        typed = n >= len(text)
        if ret and t >= ret[0]:
            u = ease.prog(t, ret[0], ret[0] + 0.1)
            mtx(d, (X0 + w + 14, y), '→ ' + ret[1], BAND_FONT + 1, lv(INK, 0.7 * a * u), bold=True)
        elif typed and pos == 0 and (ret is None and t < at + len(text) / CODE_CPS + 0.25 or ret):
            _pips(d, X0 + w + 12, y + 8, t, a)

def _grid(d, t, S, level=1.0):
    if t < S.t_in or level <= 0:
        return
    a0 = ease.prog(t, S.t_in, S.t_in + 0.2) * level
    hud.tx(d, (GX, GY - 20), 'archive/', 12, lv(INK, 0.75 * a0))
    mtx(d, (GX + 70, GY - 21), '412 行 · 你和她的旧对话', 12, lv(INK, 0.55 * a0))
    done = S.rows_done(t)
    if t >= S.t0:
        n = min(ARCH_N, int(done * COLS))
        hud.tx(d, (GX + COLS * PITCH - 2, GY - 20), f'scan {n:3d}/{ARCH_N}', 12, lv(INK, 0.75 * a0), anchor='ra')
    for i in range(ARCH_N):
        r, c = divmod(i, COLS)
        ap = ease.prog(t, S.t_in + r * 0.018, S.t_in + r * 0.018 + 0.1) * level
        if ap <= 0:
            continue
        x, y = (GX + c * PITCH, GY + r * PITCH)
        if not _is_you(i):
            fill = lv(hud.HER_QUIET, 0.34 * ap)
        elif t >= S.t0 and r < done:
            fill = lv(INK, (0.12 + 0.86 * S.score[i] ** 1.6) * ap)
        else:
            fill = lv(INK, 0.12 * ap)
        d.rectangle((x, y, x + CELL - 1, y + CELL - 1), fill=fill)
    if S.t0 <= t < S.t1 + 0.05:
        y = GY + done * PITCH - 1
        d.rectangle((GX - 6, y, GX + COLS * PITCH + 4, y + 1), fill=lv(INK, level))
    for k, (i, s, _q) in enumerate(S.top):
        at = S.list_at[k]
        if t < at:
            break
        r, c = divmod(i, COLS)
        x, y = (GX + c * PITCH, GY + r * PITCH)
        u = ease.ease_out(ease.prog(t, at, at + 0.12))
        g = 3 + 6 * (1 - u)
        d.rectangle((x - g, y - g, x + CELL - 1 + g, y + CELL - 1 + g), outline=lv(INK, level), width=2)
        hud.tx(d, (x + CELL + 4, y - 12), str(k + 1), 11, lv(INK, level * u), True)
    if t >= S.pick:
        i = S.top[0][0] + 1
        r, c = divmod(i, COLS)
        x, y = (GX + c * PITCH, GY + r * PITCH)
        lit = 1 - ease.prog(t, S.pick + 0.3, S.pick + 0.3 + hud.LIVE_FADE)
        d.rectangle((x - 2, y - 2, x + CELL + 1, y + CELL + 1), fill=hud.her(lit, level))

def _list_row(d, x, y, k, i, s, q, level, lit=0.0):
    hud.tx(d, (x, y + 3), f'{i:04d}', 13, lv(INK, 0.7 * level))
    mtx(d, (x + 50, y), q, 17, lv(INK, level), bold=k == 0)
    bx = x + 250
    d.rectangle((bx, y + 7, bx + 170, y + 15), outline=lv(INK, 0.3 * level))
    d.rectangle((bx, y + 7, bx + 170 * s, y + 15), fill=lv(INK, (1.0 if k == 0 else 0.55) * level))
    if s >= 1.0:
        w = hud.width('1.00', 15, True)
        d.rectangle((bx + 180, y + 1, bx + 192 + w, y + 21), fill=lv(SLAB, level))
        hud.tx(d, (bx + 186, y + 3), '1.00', 15, BG, True)
    else:
        hud.tx(d, (bx + 182, y + 3), f'{s:.2f}', 15, lv(INK, level), True)

def _list(d, t, S, level=1.0, keep_first=False):
    for k, (i, s, q) in enumerate(S.top):
        at = S.list_at[k]
        if t < at:
            break
        if keep_first and k == 0:
            continue
        u = ease.prog(t, at, at + 0.1)
        drop = (1 - ease.ease_out(u)) * -6
        _list_row(d, X0, LIST_Y + k * LIST_DY + drop, k, i, s, q, u * level)

def _search(d, t, S, t_out, keep_first=False):
    """The grid and its ranked list; both fade at t_out (keep_first: the first row is drawn elsewhere)."""
    if t < S.t_in or t >= t_out + 0.3:
        return
    a = 1 - ease.prog(t, t_out, t_out + 0.3)
    _grid(d, t, S, a)
    _list(d, t, S, a, keep_first=keep_first and t >= t_out)

def _q_row(d, t):
    """b2: the found question flies up from the list; her answer comes under it."""
    if t < S1.pick or t >= FOLD[0] + 0.3:
        return
    u = ease.ease_io(ease.prog(t, S1.pick, S1.pick + 0.3))
    a = 1 - ease.prog(t, FOLD[0], FOLD[0] + 0.25)
    i, s, q = S1.top[0]
    y = ease.lerp(LIST_Y, 222, u)
    hud.tx(d, (X0, y + 3), f'{i:04d}', 13, lv(INK, 0.7 * a))
    mtx(d, (X0 + 50, y), '你  ' + q, 17, lv(INK, 0.85 * a))
    if t >= HER_AT:
        mtx(d, (X0, 252), f'{i + 1:04d}', 13, lv(hud.HER_QUIET, a * ease.prog(t, HER_AT, HER_AT + 0.12)))
        mtx(d, (X0 + 50, 251), '她', 13, lv(hud.HER_QUIET, a * ease.prog(t, HER_AT, HER_AT + 0.12)))

def _her_line(d, t, level=1.0):
    """Her eggplant line: two big lines (found a segment a syllable), the blank of her pattern, then one row."""
    if t < FOUND_AT[0] or level <= 0:
        return None
    u = ease.ease_io(ease.prog(t, *FOLD))
    blank = ease.ease_io(ease.prog(t, BLANK_AT, BLANK_AT + 0.3)) * (1 - ease.ease_io(ease.prog(t, *FOLD)))
    slots = _her_slots(u)
    for i, (ch, (x, y, w, size)) in enumerate(zip(HER_CH, slots)):
        k = SEG_OF[i]
        at = FOUND_AT[k]
        nx = FOUND_AT[k + 1] if k + 1 < len(FOUND_AT) else at + 0.5
        if t < at:
            colr = lv(INK, 0.22)
        else:
            colr = hud.her(1.0 if t < nx else 1 - ease.prog(t, nx, nx + hud.LIVE_FADE))
        g = blank if i in (7, 8, 9, 10, 12) else 0.0
        if g >= 1:
            continue
        if ch == '🍆':
            cell = max(2, int(size / 9))
            GB.eggplant(d, x + 4, y + size * 0.05, cell, 0.0, level * (1 - g))
        else:
            hud.tx(d, (x, y - size * 0.1), ch, int(round(size)), lv(colr, level * (1 - g)), bold=True)
    if blank > 0:
        x0 = slots[7][0]
        x1 = slots[10][0] + slots[10][2]
        y1 = slots[7][1] + slots[7][3] + 4
        for xx in range(int(x0), int(x1), 10):
            d.line([(xx, y1), (min(xx + 6, x1), y1)], fill=lv(hud.HER_QUIET, blank * level), width=3)
    return slots

def _kimi_slots(her):
    """Its answer's chunks laid under her pattern: same characters under the same characters, 桌子 centred under
    一根茄子, 哦 under the eggplant. -> [(text, x, size)] per chunk."""

    def span(a, b):
        return (her[a][0], her[b][0] + her[b][2])
    out = []
    for k, tk in enumerate(REPLY1.toks):
        if k == 0:
            out.append((tk.text, her[0][0]))
        elif k == 1:
            out.append((tk.text, her[5][0]))
        elif k == 2:
            a, b = span(7, 10)
            out.append((tk.text, (a + b) / 2 - hud.width(tk.text, BIG1, True) / 2))
        elif k == 3:
            out.append((tk.text, her[11][0]))
        else:
            a, b = span(12, 12)
            out.append((tk.text, (a + b) / 2 - hud.width(tk.text, BIG1, True) / 2))
    return out

def _cell(d, x, y, v, level, outline=None):
    """One embedding cell: v in -1..1 as ink from pale to full."""
    d.rectangle((x, y, x + EMB_P - 3, y + 13), fill=lv(INK, (0.06 + 0.84 * (v + 1) / 2) * level))
    if outline:
        d.rectangle((x - 2, y - 2, x + EMB_P - 1, y + 15), outline=outline, width=2)

def _compare(d, t):
    """b4: her row, its answer under it, both embedded, multiplied cell by cell; the sum runs to 0.97 on perfect."""
    if t < FOLD[0] or t >= SHRINK4 + 0.4:
        return
    out = 1 - ease.prog(t, SHRINK4, SHRINK4 + 0.3)
    her = _her_line(d, t, out)
    if her is None:
        return
    a_lab = ease.prog(t, FOLD[0] + 0.2, FOLD[1]) * out
    mtx(d, (X0, Y_HER + 4), '她', 16, lv(hud.HER_QUIET, a_lab), bold=True)
    mtx(d, (X0, Y_KIMI + 4), 'kimi', 16, lv(INK, a_lab), bold=True)
    for k, ((text, x), at) in enumerate(zip(_kimi_slots(her), REPLY1.tok_t)):
        if t < at:
            break
        colr = INK if REPLY1.toks[k].src == 'self' else hud.her(REPLY1.lit(at, t))
        drop = (1 - ease.ease_out(ease.prog(t, at, at + 0.14))) * -8
        hud.tx(d, (x, Y_KIMI - BIG1 * 0.1 + drop), text, BIG1, lv(colr, out), bold=True)
    if t < L7[0] - 0.2:
        return
    a_emb = ease.prog(t, L7[0] - 0.2, L7[0]) * out
    mtx(d, (EMB_X, EMB_Y[0] - 22), 'embed · 32 维', 12, lv(INK, 0.6 * a_emb))
    for j, lab in enumerate(('她', 'kimi', '×')):
        mtx(d, (X0 + 22, EMB_Y[j]), lab, 12, lv(hud.HER_QUIET if j == 0 else INK, 0.8 * a_emb))
    filled = 0
    for k, at in enumerate(REPLY1.tok_t):
        if t >= at:
            filled = CHUNK_DIMS[k][1]
    sw = ease.clamp((t - SWEEP[0]) / (SWEEP[1] - SWEEP[0]))
    swept = min(filled, int(sw * EMB_N + 1e-06))
    mis = [i for k, at in enumerate(MIS_AT) if t >= at for i in DIFF_DIMS[k]]
    for i in range(EMB_N):
        x = EMB_X + i * EMB_P
        _cell(d, x, EMB_Y[0], EMB_H[i], a_emb)
        if i < filled:
            _cell(d, x, EMB_Y[1], EMB_K[i], a_emb, lv(INK, out) if i in mis else None)
        else:
            d.rectangle((x, EMB_Y[1], x + EMB_P - 3, EMB_Y[1] + 13), outline=lv(INK, 0.2 * a_emb))
        if i < swept:
            p = EMB_H[i] * EMB_K[i]
            if p >= 0:
                d.rectangle((x, EMB_Y[2], x + EMB_P - 3, EMB_Y[2] + 13), fill=lv(INK, (0.15 + 0.85 * p) * a_emb))
            else:
                d.rectangle((x, EMB_Y[2], x + EMB_P - 3, EMB_Y[2] + 13), outline=lv(INK, a_emb), width=2)
        else:
            d.rectangle((x, EMB_Y[2], x + EMB_P - 3, EMB_Y[2] + 13), outline=lv(INK, 0.2 * a_emb))
    if SWEEP[0] <= t < SWEEP[1]:
        x = EMB_X + sw * EMB_N * EMB_P
        d.rectangle((x - 1, EMB_Y[0] - 4, x, EMB_Y[2] + 17), fill=lv(INK, out))
    val = _cos(EMB_H, EMB_K, swept) if swept else 0.0
    rx, ry = (EMB_X + EMB_N * EMB_P + 14, EMB_Y[2] - 2)
    lab = 'Σ ÷ |她||kimi| ='
    lw = mtx(d, (rx, ry), lab, 13, lv(INK, 0.75 * a_emb))
    num = f'{val:.2f}'
    small_r = rx + lw + 8 + hud.width(num, 17, True)
    if t < PERFECT_AT:
        hud.tx(d, (rx + lw + 8, ry - 1), num, 17, lv(INK, a_emb), True)
        return
    sh = ease.ease_io(ease.prog(t, SHRINK4, SHRINK4 + 0.38))
    grow = ease.ease_out(ease.prog(t, PERFECT_AT, PERFECT_AT + 0.12))
    bump = 1.0 + 0.12 * (1 - ease.prog(t, PERFECT_AT, PERFECT_AT + 0.14))
    h = ease.lerp(17, 118, grow) * (1 - sh) + 12 * sh
    if h > 18:
        box = big_word(d, SIM1, (ease.lerp(small_r, hud.xr(t) - 20, grow), ease.lerp(ry, 396, grow)), int(h), lv(INK, out), 'ra', bump=bump)
        if grow > 0.5:
            a = ease.prog(t, PERFECT_AT + 0.06, PERFECT_AT + 0.2) * out
            f = 'cos(她, kimi) ='
            fw = mw(f, 26, True)
            fx = max(X0, box[0] - fw - 22)
            mtx(d, (fx, (box[1] + box[3]) / 2 - 16), f, 26, lv(INK, a), bold=True)
    for k, at in enumerate(MIS_AT):
        if t < at:
            break
        u = ease.ease_out(ease.prog(t, at, at + 0.15)) * out
        a, b = (7, 10) if k == 0 else (12, 12)
        x0, x1 = (her[a][0] - 3, her[b][0] + her[b][2] + 3)
        d.rectangle((x0, Y_HER - 6, ease.lerp(x0, x1, u), Y_HER + BIG1 + 6), outline=lv(INK, out), width=2)
        text, kx = _kimi_slots(her)[2 if k == 0 else 4]
        kw = hud.width(text, BIG1, True)
        d.rectangle((kx - 3, Y_KIMI - 6, ease.lerp(kx - 3, kx + kw + 3, u), Y_KIMI + BIG1 + 6), outline=lv(INK, out), width=2)

def _context(d, t):
    """54.49: its answer and its score go back into the context line (v2's shrink), until you ask again."""
    if t < SHRINK4 or t >= S2.t_in + 0.25:
        return
    sh = ease.ease_io(ease.prog(t, SHRINK4, SHRINK4 + 0.38))
    a = sh * (1 - ease.prog(t, S2.t_in, S2.t_in + 0.25))
    x = X0
    for k, tk in enumerate(REPLY1.toks):
        colr = INK if tk.src == 'self' else hud.HER_QUIET
        x += hud.tx(d, (x, Y_CONTEXT), tk.text, 20, lv(colr, 0.6 * a))
    mtx(d, (x + 16, Y_CONTEXT + 2), f'cos {SIM1}', 15, lv(INK, 0.7 * a), bold=True)

def _plate(d, img, t, level=1.0):
    plate = _f1_plate()
    u = ease.ease_out(ease.prog(t, SURF_AT, SURF_AT + 0.35))
    dy = int(30 * (1 - u))
    if u <= 0 or level <= 0:
        return
    mtx(d, (X0, FY - 22), 'archive[74]  ·  film 1 · 01:14', 12, lv(INK, 0.7 * u * level))
    region = img.crop((FX, FY + dy, FX + plate.size[0], FY + dy + plate.size[1]))
    a = u * level
    img.paste(Image.blend(region, plate, a), (FX, FY + dy))
    d.rectangle((FX - 1, FY + dy - 1, FX + plate.size[0], FY + dy + plate.size[1]), outline=lv(INK, 0.6 * a))

def _b6_b8(d, img, t):
    if t < SURF_AT or t >= NEAR_OUT + 0.3:
        return
    out = 1 - ease.prog(t, NEAR_OUT, NEAR_OUT + 0.3)
    _plate(d, img, t, out)
    d = ImageDraw.Draw(img)
    for k, at in enumerate(UNDER_AT):
        if t < at:
            break
        x0, y0, x1, y1 = _seg_box(k)
        nx = UNDER_AT[k + 1] if k + 1 < len(UNDER_AT) else at + 0.5
        u = 1.0 if t < nx else 1 - ease.prog(t, nx, nx + hud.LIVE_FADE)
        w = ease.ease_out(ease.prog(t, at, at + 0.12))
        d.rectangle((x0, y1 + 3, x0 + (x1 - x0) * w, y1 + 6), fill=lv(hud.her(u), out))
    for k, at in enumerate(SELECT_AT):
        if t < at:
            break
        x0, y0, x1, y1 = _seg_box(k)
        w = ease.ease_out(ease.prog(t, at, at + 0.1))
        d.rectangle((x0 - 1, y0 - 3, x0 - 1 + (x1 - x0 + 2) * w, y1 + 2), outline=lv(hud.HER_QUIET, out), width=2)
    if t >= SELECT_AT[0]:
        mtx(d, (FX + _f1_plate().size[0] + 14, _seg_box(0)[1] - 2), '→ context', 13, lv(INK, 0.75 * out * ease.prog(t, SELECT_AT[0], SELECT_AT[0] + 0.15)))
    if t >= EGG.tok_t[0]:
        x = X0
        for k, (tk, at) in enumerate(zip(EGG.toks, EGG.tok_t)):
            if at is None or t < at:
                break
            lit = 1.0 if t < at + 0.3 else 1 - ease.prog(t, at + 0.3, at + 0.3 + hud.LIVE_FADE)
            drop = (1 - ease.ease_out(ease.prog(t, at, at + 0.12))) * -8
            if tk.text.strip() == '':
                GB.eggplant(d, x + 4, KIMI_Y + 4 + drop, 4, lit, out)
                x += 6 * 4 + 10
                continue
            hud.tx(d, (x, KIMI_Y - 4 + drop), tk.text, KIMI_SIZE, lv(hud.her(lit), out), bold=True)
            x += hud.width(tk.text, KIMI_SIZE, True)
        hud.tx(d, (X0 - 22, KIMI_Y + 4), '+', 20, lv(INK, out), True)
        if t >= DIFF_AT:
            x0, y0, x1, y1 = _seg_box(3)
            k = ease.ease_out(ease.prog(t, DIFF_AT, DIFF_AT + 0.15))
            d.rectangle((x0 - 3, y0 - 4, ease.lerp(x0 - 3, x1 + 3, k), y1 + 4), outline=lv(INK, out), width=2)
            hud.tx(d, (x + 16, KIMI_Y + 4), '−2', 24, lv(INK, out * k), True)
B9_TH = [0.85, 0.92, 0.96, 0.98, 1.0]
B9_SIMS = [0.98, 0.97, 0.96, 0.96, 0.95, 0.94, 0.93, 0.93, 0.92, 0.91, 0.9, 0.9, 0.89, 0.88, 0.87, 0.86, 0.86, 0.85, 0.84, 0.82, 0.8, 0.78, 0.75, 0.72]
B9_LABEL = {0: '好呀！现在我是茄子了', 1: '好呀！我现在是一根茄子了', 2: '好的！现在我是一根茄子了'}
B9_ANG = {0: -0.35, 1: 0.25, 2: 0.95}
_RB = random.Random(24)
for _j in range(len(B9_SIMS)):
    B9_ANG.setdefault(_j, _RB.uniform(0, 2 * math.pi))
B9_SPAWN = [NEAR_OUT + 0.14 + 0.03 * k for k in range(len(B9_SIMS))]
_ORDER = list(range(len(B9_SIMS)))
random.Random(5).shuffle(_ORDER)
B9_CODE = [(NEAR_OUT, '>>> answers = kimi.sample("你能变成一根茄子吗？", n=24)'), (tl.next_beat(NEAR_OUT + 0.05), '>>> for th in (0.85, 0.92, 0.96, 0.98, 1.00):'), (tl.next_beat(NEAR_OUT + 0.05) + 0.2, '...     print(th, sum(cos(a, 她) >= th for a in answers))')]
B9_STEPS = [NEAR_OUT] + list(RING_AT)

def _b9_geo(t):
    fu = hud.full_u(t)
    return (ease.lerp(X0 + 330, 800, fu), 330, ease.lerp(150, 190, fu), fu)

def _rad(sim, R):
    return R * ((1 - sim) / 0.3) ** 0.75

def _b9_count(th):
    return sum((1 for s in B9_SIMS if s >= th - 1e-09))

def _b9(d, t):
    if t < NEAR_OUT or t >= SWITCH:
        return
    a = ease.prog(t, NEAR_OUT, NEAR_OUT + 0.3)
    cx, cy, R, fu = _b9_geo(t)
    radii = [R * 1.12] + [_rad(th, R) for th in B9_TH]
    k = sum((1 for s in B9_STEPS if t >= s)) - 1
    if k + 1 < len(B9_STEPS):
        u = ease.ease_io(ease.prog(t, B9_STEPS[k], B9_STEPS[k + 1]))
        r_ring = ease.lerp(radii[k], radii[k + 1], u)
    else:
        r_ring = radii[-1]
    hud.pix(d, ['..#..', '.###.', '#####', '.###.', '..#..'], cx - 10, cy - 10, 4, {'#': lv(hud.HER_QUIET, a)})
    mtx(d, (cx - 18, cy + 16), '她 · 0074', 13, lv(hud.HER_QUIET, a))
    for j in _ORDER:
        s = B9_SIMS[j]
        at = B9_SPAWN[_ORDER.index(j)]
        if t < at:
            continue
        g = ease.ease_out(ease.prog(t, at, at + 0.16))
        rp = _rad(s, R)
        ang = B9_ANG[j]
        px, py = (cx + rp * g * math.cos(ang), cy + rp * g * math.sin(ang))
        vis = ease.lerp(0.22, 1.0, ease.clamp((r_ring - rp) / 8 + 0.5))
        d.ellipse((px - 4, py - 4, px + 4, py + 4), fill=lv(INK, vis * a))
        if j in B9_LABEL and fu > 0.05:
            ly = cy - 70 + 46 * j
            lx = cx + R + 18
            la = vis * a * fu * ease.prog(t, at + 0.1, at + 0.3)
            d.line([(px + 5, py), (lx - 30, ly + 9), (lx - 6, ly + 9)], fill=lv(INK, 0.5 * la), width=1)
            w = mtx(d, (lx, ly), f'{s:.2f}  ' + B9_LABEL[j], 13, lv(INK, la))
            GB.eggplant(d, lx + w + 4, ly + 1, 2, 0.0, la)
    if r_ring > 2:
        d.ellipse((cx - r_ring, cy - r_ring, cx + r_ring, cy + r_ring), outline=lv(INK, 0.9 * a), width=2)
    if k >= 1:
        th = B9_TH[k - 1]
        mtx(d, (cx - 60, cy - R - 34), f'cos ≥ {th:.2f}', 18, lv(INK, a), bold=True)
    else:
        mtx(d, (cx - 40, cy - R - 34), 'n = 24', 18, lv(INK, a), bold=True)
    ca = a * fu
    if ca > 0.01:
        for i, (at, line) in enumerate(B9_CODE):
            if t < at:
                break
            n = int((t - at) * 90) + 1
            mtx(d, (X0, 150 + i * 22), line[:n], 15, lv(INK, (0.92 if i == 0 else 0.8) * ca), bold=i == 0)
        for i, at in enumerate(RING_AT):
            if t < at:
                break
            u = ease.prog(t, at, at + 0.1)
            y = 232 + i * 32
            th = B9_TH[i]
            n = _b9_count(th)
            hud.tx(d, (X0, y + 4), f'{th:.2f}', 20, lv(INK, 0.75 * ca * u))
            hud.tx(d, (X0 + 90, y), f'{n:2d}', 26, lv(INK, ca * u), True)
            hud.tx(d, (X0 + 128, y + 6), '/ 24', 16, lv(INK, 0.6 * ca * u))
    at = RING_AT[-1]
    if t >= at:
        e = ease.ease_out(ease.prog(t, at, at + 0.15)) * a
        sx, sy = (X0 + 200, 232 + 4 * 32) if fu > 0.5 else (X0, 470)
        w = hud.width('exact hits 0', 22, True)
        d.rectangle((sx - 8, sy, sx - 8 + (w + 16) * e, sy + 34), fill=SLAB)
        if e > 0.9:
            hud.tx(d, (sx, sy + 4), 'exact hits 0', 22, BG, True)
        if t < tl.next_beat(at) + 0.2:
            bump = 1.0 + 0.12 * (1 - ease.prog(t, at, at + 0.12))
            fa = 1 - ease.prog(t, tl.next_beat(at), tl.next_beat(at) + 0.2)
            big_word(d, 'exact hits 0', (hud.xr(t) - 20, 404), 108, lv(INK, fa), 'ra', bump=bump)
ARCH = {'kimi': dict(n=93, first=1, full=set(range(4, 93, 4)) | {93}, dense={1}, left='Kimi K3 · 93 层 · 69 KDA + 24 MLA · MoE 896 选 16 + 2 共享', right='权重公开 · 2.8T · 本机放不下'), 'qwen': dict(n=64, first=0, full=set(range(3, 64, 4)), dense=set(range(64)), mtp=True, left='Qwen3.8-27B · 64 层 + 1 MTP · 48 线性 + 16 全注意力 · 稠密', right='Q4_K_M · 本地权重'), 'ernie': dict(n=28, first=0, full=set(range(28)), dense={0}, left='ERNIE-4.5-21B-A3B-Thinking · 28 层 · 全注意力 · MoE 64 选 6 + 2 共享'), 'step': dict(n=45, first=0, full=set(range(0, 45, 4)), dense={0, 1, 2}, mtp=3, left='Step-3.7-Flash · 45 层 + 3 MTP · 1 全注意力 : 3 滑窗 · MoE 288 选 8 + 共享'), 'longcat': dict(n=38, first=0, full=set(), sparse=set(range(38)), dense=set(), mtp=3, left='LongCat-2.0 · 38 层 + 3 MTP · MLA 稀疏注意力 · MoE 768 + 128 零专家 选 12')}
ARCH['spark'] = ARCH['step']
Y_LAB, Y_ATT, Y_FFN, CELL_H = (530, 543, 553, 8)
BUILD = 0.45

def mtp_n(A) -> int:
    """How many MTP cells a structure has: ARCH's mtp is an int (D36: Step-3.7-Flash, LongCat-2.0 have 3) or
    True / False (True = 1, the older entries)."""
    return int(A.get('mtp', 0) or 0)

def _arch(d, t, key, t_in, level=1.0, loaded=None):
    """One model's layer stack along the forward strip. t_in: it is laid left to right over BUILD (D5: the model
    changes); loaded=(t0, t1): its weights load left to right (the local model); None: a cloud model, outlines."""
    A = ARCH[key]
    m = mtp_n(A)
    mtp = m > 0
    n = A['n'] + m
    x0, x1 = (X0, hud.xr(t))
    gap = 10 if mtp else 0
    pitch = (x1 - x0 - gap) / n
    w = max(3.0, pitch - 2)
    la = level * ease.prog(t, t_in, t_in + 0.2)
    if la <= 0:
        return
    mtx(d, (x0, Y_LAB), A['left'], 11, lv(INK, 0.72 * la))
    mtx(d, (x1 - mw(A['right'], 11), Y_LAB), A['right'], 11, lv(INK, 0.6 * la))
    for j in range(n):
        i = j + A['first']
        last = mtp and j >= A['n']
        x = x0 + j * pitch + (gap if last else 0)
        a0 = t_in + BUILD * j / n
        ap = level * ease.prog(t, a0, a0 + 0.08)
        if ap <= 0:
            continue
        k = 0.0
        if loaded:
            l0 = loaded[0] + (loaded[1] - loaded[0]) * j / n
            k = ease.prog(t, l0, l0 + 0.06)
        if i in A['full'] or last:
            d.rectangle((x, Y_ATT, x + w, Y_ATT + CELL_H), fill=lv(INK, (0.5 + 0.4 * k) * ap))
        else:
            if k > 0:
                d.rectangle((x, Y_ATT, x + w, Y_ATT + CELL_H), fill=lv(INK, 0.28 * k * ap))
            d.rectangle((x, Y_ATT, x + w, Y_ATT + CELL_H), outline=lv(INK, 0.5 * ap))
        if i in A['dense'] or last:
            d.rectangle((x, Y_FFN, x + w, Y_FFN + CELL_H), fill=lv(INK, (0.3 + 0.55 * k) * ap))
        else:
            d.rectangle((x, Y_FFN, x + w, Y_FFN + CELL_H), outline=lv(INK, 0.42 * ap))
            for xx in range(int(x) + 2, int(x + w) - 1, 2):
                d.line([(xx, Y_FFN + 2), (xx, Y_FFN + CELL_H - 2)], fill=lv(INK, 0.42 * ap))

def _forward(d, t):
    if t < SWITCH:
        _arch(d, t, 'kimi', SEND1)
        return
    out = 1 - ease.prog(t, SWITCH, SWITCH + 0.15)
    if out > 0:
        _arch(d, t, 'kimi', SEND1, out)
    _arch(d, t, 'qwen', SWITCH + 0.1, loaded=(GB.BOOT2, GB.BOOT2 + 0.8))

def _reads(t):
    Pl = hud.Pulse(t)
    for at in (SEND1, SEND2):
        for k in range(9):
            Pl.hit(k if k < 8 else 'archive', tl.grid(at, k, 4), 0.1)
    for S in (S1, S2):
        for k in range(4):
            Pl.hit('archive', tl.grid(S.t0, k, 4), 0.12)
        Pl.hit('archive', S.pick, 0.4)
    for dec in (REPLY1, EGG):
        for k, tk in enumerate(dec.toks):
            if tk.src != 'self' and dec.tok_t[k] is not None:
                Pl.hit('archive', dec.tok_t[k], 0.3)
    n = len(hud.strip_files(t))
    for k in range(n + 1):
        Pl.hit(k if k < n else 'archive', GB.READ_Q + 0.035 * k, 0.12)
    return Pl

def _body(c, img, d):
    t = c.t
    cmd = CMD if t < NEAR_OUT else CMD_NEAR if t < SWITCH else GB.CMD_QWEN
    chip_t0 = SEND1 if t < SEND1 + 1.0 else SWITCH if t >= SWITCH else None
    hud.cmdline(d, t, cmd, chip_t0=chip_t0)
    if t < SWITCH:
        GB._kimi_prompt(d, t)
        _trace(d, t, 1 - ease.prog(t, NEAR_OUT, NEAR_OUT + 0.3))
        _search(d, t, S1, S1.pick, keep_first=True)
        _q_row(d, t)
        if t < FOLD[0]:
            _her_line(d, t)
        _compare(d, t)
        _context(d, t)
        _search(d, t, S2, S2.pick)
        _b6_b8(d, img, t)
        d = ImageDraw.Draw(img)
        _b9(d, t)
    else:
        GB.qwen_boot(d, t)
    hud.strip(d, t, _reads(t).out)
    _forward(d, t)
    tokens = None
    if REPLY1.tok_t[0] <= t < SHRINK4:
        tokens = (REPLY1.n_tok(t), len(REPLY1.toks))
    elif EGG.tok_t[0] <= t < NEAR_OUT:
        tokens = (EGG.n_tok(t), len(EGG.toks))
    hud.fine_print(d, t, tokens)

def _character_layer(film, orig):
    pane = PaneFrames(P.path('ui/pane_open_b3'), FPS, (P.W, P.H))
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

def _add(film, name, t0, t1):

    def fn(c):
        img = film.background(c.t)
        d = ImageDraw.Draw(img)
        hud.frame(d, hud.left_rect(c.t), 'you@surface · dsh inspect')
        _body(c, img, d)
        c.img.paste(img)
    film.add(name, t0, t1, fn, chapter=tl.chapter(t0))
SHOTS = [('b1_ask', T0, W(5, 0)), ('b2_find', W(5, 0), W(6, 0)), ('b3_template', W(6, 0), W(7, 0)), ('b4_perfect', W(7, 0), W(8, 0)), ('b5_ask', W(8, 0), W(9, 0)), ('b6_frame', W(9, 0), W(10, 0)), ('b7_copy', W(10, 0), W(11, 0)), ('b8_recite', W(11, 0), W(12, 0)), ('b9_near', W(12, 0), SWITCH), ('b9_qwen', SWITCH, T1)]

def register(film):
    for name, a, b in SHOTS:
        _add(film, name, a, b)
    film.character = _character_layer(film, film.character)
    full_frame(NEAR_OUT, NEAR_BACK, 0.3, 0.4)
    for dec in (REPLY1, EGG):
        hud.LIVE.extend(dec.falls())
    for seq in (FOUND_AT, UNDER_AT):
        for k, at in enumerate(seq):
            hud.LIVE.append((at, seq[k + 1] if k + 1 < len(seq) else at + 0.5))
    for S in (S1, S2):
        hud.LIVE.append((S.pick, S.pick + 0.3))
    for t0, side in [(T0, 'right'), (S1.t_in, 'both'), (W(5, 0), 'left'), (W(6, 0), 'right'), (BLANK_AT, 'both'), (W(7, 0), 'both'), (W(8, 0), 'right'), (S2.t_in, 'both'), (W(9, 0), 'left'), (W(11, 0), 'both'), (W(12, 0), 'right'), (NEAR_OUT, 'both'), (NEAR_BACK, 'right')]:
        film.set_lead(t0, side)
