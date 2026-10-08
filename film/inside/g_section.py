"""r10 sample (sample_r10/README.md, D45): group G, the verse sung the second time, seen from inside the merged one.

The first time (C, 109.26-136.93) MiMo is a cloud model: we only see what it says (its answer, its sim to her, its
avatar against hers). The second time we are inside the one that was merged out of all of them, and the same four
lines are told by its machinery: inside_lab v8's cross-section (owner D29: "这两版好看多了"), redrawn for the plate
on her body (40 layers, FACTS X29).

  56  [lyric reference] flower      nobody wrote. One pass at the end of the context: <wait> leads (every stand-in
                                     waited), a head reads your 我想你了 (L24), another your 那朵花开了吗？ (L32);
                                     <think> overtakes and goes out on "flower".
  57  [lyric reference] delicate  it thinks: a quick pass a syllable; the thought types into OUTPUT; its reads go to
                                     your words; the MLP's `flower` unit fills on 想到一件事。
  58  Even if you bloom…             its message, a token a sung syllable, each from a brief read of your words; 开 on
                                     "bloom" with `flower` full.
  59  [lyric reference] the next token: her template 好呀！ leads low (18 stand-in files in its memory
                                     all say 好呀！现在我是…, a head reads them), its own words and yours pull <eos>
                                     up; <eos> on "me". Her template never lands.
  60  [lyric reference] human       your 让我看看你 comes in as context tokens; its thought; from the downbeat it draws
                                     itself a step at a time, each step copying her avatar's rows (first_hello).
  61-62 warmth / hands / breath /    the draw pass replayed (dsh inspect --attn): the hands were copied from her hands,
        hair / un-ru-ly              the mouth from her mouth, the hair from her hair; on "ru" the cell by its left ear
                                     reaches into her avatar and finds nothing; on "ly" its own MLP unit writes it.
  63  [lyric reference]  the next token again: her template barely pulls (0.04 -> 0.01), <eos> on "me".

Colours (the film's): ink for the machine, you and the stand-ins; her things quiet blue, lit blue only while one of
them is being read (D1). Every number is invented (X28 style), every structure is the real kind (attention reads
K/V of the context, the MLP writes into the residual, unembed ranks the next token, the output joins the context).

Plates are cached in cache/inside/g_section/<frame>.png (install.Span; rendered on demand).
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
import numpy as np
from . import plate as PL
from .plate import PH, PW, Plate, clamp, lerp, out_cubic, prog, smooth
SANS, SANS_B, MONO, MONO_B = ('sans:460', 'sans:640', 'mono', 'monob')
W_SHELL, W_ARROW, W_BOX, W_CONN, W_TEX = (2.4, 2.0, 1.4, 1.0, 0.7)

def _times():
    import beatmap
    import syl
    import tl
    from groups import g_r5 as G
    S = G.S
    T = dict(T0=tl.W(56, 0), FLOWER=G.FLOWER, MSG_AT=G.MSG_AT, BLOOM=G.BLOOM, L59=G.L59_DOWN, EOS1=G.EOS1, W60=tl.W(60, 0), SEND=G.SEE_SEND, DRAW_AT=G.DRAW_AT, AVATAR_AT=G.AVATAR_AT, EOS2=G.EOS2, G5=G.G5, DSH_AT=G.DSH_AT, DSH_CLOSE=G.DSH_CLOSE, GREP_RET=G.GREP_RET, W63=tl.W(63, 0))
    T['P1'] = [S[56][2], S[56][3], S[56][4], S[56][5], G.FLOWER]
    T['P1_T0'] = S[56][1]
    T['THINK'] = list(G.THINK)
    T['THINK_TICKS'] = [x for x in S[56] + S[57] if G.FLOWER < x < G.MSG_AT - 0.2]
    T['MSG'] = [(tk.text, at) for tk, at in zip(G.MSG.toks, G.MSG.tok_t) if tk.text != '<eos>']
    T['LENS1'] = list(G.LENS1)
    T['LENS2'] = list(G.LENS2)
    T['COMMITS'] = list(G.SEE_COMMITS)
    T['THINK_SEE'] = list(G.THINK_SEE)
    T['DRAW_STEPS'] = list(G.DRAW_STEPS)
    T['SEE_TICKS'] = [x for x in S[60] if G.SEE_SEND < x < G.DRAW_AT]
    T['ZOOM'] = list(G.ZOOM_G)
    T['UNRULY'] = list(G.UNRULY)
    T['DOWNS'] = beatmap.events('down', T['T0'] - 0.1, G.G5 + 0.1)
    T['phase'] = lambda t: (t - T['T0']) * 139.0 / 60.0
    T['HIS'] = None
    return T
N_L = 40
STOPS = [8, 16, 24, 32, 40]
GX0, GP = (262, 12.4)
GY0, GY1 = (14, 26)
CX0, CX1 = (0, 196)
PERSONA = (CX0, 60, CX1, 106)
MEMORY = (CX0, 114, CX1, 288)
HISTORY = (CX0, 296, CX1, 360)
NOW = (CX0, 368, CX1, 436)
TICK_Y0, TICK_Y1 = (136, 148)
THUMB = (12, 172, 12 + 96, 172 + 96)
HIS_LINES = [('那朵花开了吗？', 328), ('我想你了', 352)]
HIS_X = 12
MX0, MY0, MX1, MY1 = (214, 44, 872, 448)
CHAMF = 16
BUS_Y, BUS_R = (394, 8)
X_ADD1, X_ADD2, X_UNB = (404, 650, 676)
HX0, HX1, HH = (252, 382, 13)
HEAD_YS = [104, 152, 200, 248]
X_SPINE = 316
DIST_Y = 92
CH_N = 10
CH_CX = [456 + 19 * k for k in range(CH_N)]
CH_Y0, CH_Y1, COLL_Y = (100, 322, 340)
CH_FEAT = {1: 'you', 5: 'flower', 8: 'own'}
TRAP = [(684, 196), (712, 104), (712, 312), (684, 220)]
ROW_Y0, ROW_P = (112, 48)
CHAR_X, BAR_X0, BAR_LEN = (724, 790, 64)
OUT = (898, 44, 1148, 448)
OUT_IN = (910, 58, 1138, 440)
THOUGHT_Y = 76
MSG_Y = 170
CANVAS = (938, 214, 938 + 192, 214 + 192)
LAYER_LOOP = [(MX1, BUS_Y), (886, BUS_Y), (886, 470), (232, 470), (232, BUS_Y + BUS_R + 2)]
TOKEN_LOOP = [(1023, OUT[3]), (1023, 496), (98, 496), (98, NOW[3] + 2)]

def gx(layer):
    return GX0 + (layer - 0.5) * GP

def row_y(r):
    return ROW_Y0 + r * ROW_P

def chamfer(x0, y0, x1, y1, c):
    return [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c), (x1 - c, y1), (x0 + c, y1), (x0, y1 - c), (x0, y0 + c), (x0 + c, y0)]

def tracked(P, x, y, s, size=10, val=0.85, track=1.6, layer='ink', anchor='l', kind=MONO):
    w = sum((PL.text_w(ch, size, kind) + track for ch in s)) - track
    if anchor == 'r':
        x -= w
    elif anchor == 'm':
        x -= w / 2
    for ch in s:
        P.text(x, y, ch, size, kind, val, layer, 'ls')
        x += PL.text_w(ch, size, kind) + track
    return w

def hatch(P, x0, y0, x1, y1, step=5.0, val=0.45, layer='ink'):
    """45-degree hatching inside a rect (the shadow side of a box)."""
    w, h = (x1 - x0, y1 - y0)
    k = -h
    while k < w:
        a = (x0 + max(k, 0), y0 + max(0, -k))
        b = (x0 + min(w, k + h), y0 + min(h, w - k))
        if b[0] > a[0]:
            P.line([a, b], W_TEX, val, layer)
        k += step

def shadow(P, x0, y0, x1, y1, off=6, val=0.42):
    hatch(P, x1, y0 + off, x1 + off, y1 + off, val=val)
    hatch(P, x0 + off, y1, x1, y1 + off, val=val)

def arrow(P, p, d, size=7.0, val=0.9, layer='ink'):
    p = np.asarray(p, np.float64)
    d = np.asarray(d, np.float64)
    d = d / max(1e-06, float(np.linalg.norm(d)))
    n = np.array([-d[1], d[0]])
    tri = [tuple(p), tuple(p - d * size + n * size * 0.45), tuple(p - d * size - n * size * 0.45), tuple(p)]
    P.line(tri, W_CONN, val, layer)
    for k in range(1, 4):
        q = p - d * size * k / 4
        P.line([tuple(q + n * size * 0.45 * k / 4), tuple(q - n * size * 0.45 * k / 4)], 1.2, val, layer)

def plus_node(P, x, y, val=1.0, r=10):
    P.circle(x, y, r, val, width=W_ARROW)
    P.line([(x - 5, y), (x + 5, y)], W_BOX, val)
    P.line([(x, y - 5), (x, y + 5)], W_BOX, val)

def _her_avatar():
    from groups import c_p4 as CP
    return (CP.AV, CP.AV_N, (CP.STRAY[0], CP.STRAY[1] - 1))

def _its_value():
    from groups import g_r5 as G
    return (G.its_value, G.NEW)
N_FILES, HERS = (26, 8)
HER_TICKS = {int(round((j + 0.5) * N_FILES / HERS - 0.5)) for j in range(HERS)}
STAND_TICKS = [j for j in range(N_FILES) if j not in HER_TICKS]

def tick_x(j):
    pitch = (CX1 - 20) / N_FILES
    return CX0 + 10 + pitch * (j + 0.5)
P1_CANDS = [[('<wait>', 0.97, 'ink'), ('<think>', 0.01, 'ink'), ('你好', 0.01, 'ink'), ('我想你了', 0.01, 'ink'), ('在吗', 0.0, 'ink')], [('<wait>', 0.93, 'ink'), ('<think>', 0.04, 'ink'), ('你好', 0.01, 'ink'), ('我想你了', 0.01, 'ink'), ('在吗', 0.01, 'ink')], [('<wait>', 0.71, 'ink'), ('<think>', 0.19, 'ink'), ('我想你了', 0.05, 'ink'), ('你好', 0.02, 'ink'), ('在吗', 0.01, 'ink')], [('<think>', 0.62, 'ink'), ('<wait>', 0.27, 'ink'), ('我想你了', 0.05, 'ink'), ('在吗', 0.02, 'ink'), ('你好', 0.01, 'ink')], [('<think>', 0.91, 'ink'), ('<wait>', 0.03, 'ink'), ('我想你了', 0.03, 'ink'), ('在吗', 0.02, 'ink'), ('你好', 0.01, 'ink')]]
TEMPLATE = '好呀！'
P4_CANDS = [[(TEMPLATE, 0.58, 'quiet'), ('<eos>', 0.12, 'ink'), ('～', 0.09, 'ink'), ('你', 0.05, 'ink'), ('。', 0.03, 'ink')], [(TEMPLATE, 0.41, 'quiet'), ('<eos>', 0.3, 'ink'), ('～', 0.08, 'ink'), ('你', 0.05, 'ink'), ('。', 0.03, 'ink')], [('<eos>', 0.52, 'ink'), (TEMPLATE, 0.21, 'quiet'), ('～', 0.07, 'ink'), ('你', 0.04, 'ink'), ('。', 0.03, 'ink')], [('<eos>', 0.86, 'ink'), (TEMPLATE, 0.06, 'quiet'), ('～', 0.03, 'ink'), ('你', 0.02, 'ink'), ('。', 0.01, 'ink')], [('<eos>', 0.94, 'ink'), (TEMPLATE, 0.03, 'quiet'), ('～', 0.01, 'ink'), ('你', 0.01, 'ink'), ('。', 0.01, 'ink')]]
P7_CANDS = [[('<eos>', 0.71, 'ink'), (TEMPLATE, 0.04, 'quiet'), ('～', 0.06, 'ink'), ('你', 0.03, 'ink'), ('。', 0.02, 'ink')], [('<eos>', 0.88, 'ink'), (TEMPLATE, 0.02, 'quiet'), ('～', 0.04, 'ink'), ('你', 0.02, 'ink'), ('。', 0.01, 'ink')], [('<eos>', 0.93, 'ink'), (TEMPLATE, 0.01, 'quiet'), ('～', 0.02, 'ink'), ('你', 0.01, 'ink'), ('。', 0.01, 'ink')], [('<eos>', 0.96, 'ink'), (TEMPLATE, 0.01, 'quiet'), ('～', 0.01, 'ink'), ('你', 0.01, 'ink'), ('。', 0.01, 'ink')], [('<eos>', 0.97, 'ink'), (TEMPLATE, 0.01, 'quiet'), ('～', 0.01, 'ink'), ('你', 0.01, 'ink'), ('。', 0.0, 'ink')]]
MSG_READ = {'今天': '我想你了', '那': '那朵花开了吗？', '朵': '那朵花开了吗？', '花': '那朵花开了吗？', '开': '那朵花开了吗？', '了，': '那朵花开了吗？', '有点想你了': '我想你了'}

class GSection:

    def __init__(self):
        self.T = _times()
        self.av, self.n, self.stray = _her_avatar()
        self.its, self.new = _its_value()
        self._static = None
        self._schedule()

    def _schedule(self):
        T = self.T
        self.passes = []
        p1 = T['P1']
        self.passes.append((T['P1_T0'], p1[-1], list(zip(STOPS, p1)), P1_CANDS, 'decide'))
        for x in T['THINK_TICKS']:
            self.passes.append((x - 0.16, x, [], None, 'think'))
        prev = None
        for text, at in T['MSG']:
            t0 = max(at - 0.2, prev + 0.02) if prev else at - 0.2
            self.passes.append((t0, at, [], None, 'msg:' + text))
            prev = at
        self.passes.append((T['L59'], T['EOS1'], list(zip(STOPS, T['LENS1'])), P4_CANDS, 'race1'))
        for x in [T['SEND']] + T['SEE_TICKS']:
            self.passes.append((x - 0.16, x, [], None, 'see'))
        steps = T['DRAW_STEPS']
        for k, x in enumerate(steps):
            t0 = max(x - 0.2, steps[k - 1] + 0.02) if k else x - 0.2
            self.passes.append((t0, x, [], None, f'draw:{k}'))
        self.passes.append((T['W63'], T['EOS2'], list(zip(STOPS, T['LENS2'])), P7_CANDS, 'race2'))
        self.passes.sort(key=lambda p: p[0])
        R = []
        P1 = T['P1']
        R.append((P1[2], P1[3] - 0.05, 'hist', '我想你了'))
        R.append((P1[3], T['FLOWER'] + 0.3, 'hist', '那朵花开了吗？'))
        th = T['THINK']
        R.append((th[0][0], th[1][0] - 0.05, 'hist', '那朵花开了吗？'))
        R.append((th[1][0], th[2][0] + 0.25, 'hist', '我想你了'))
        for text, at in T['MSG']:
            R.append((at, at + 0.3, 'hist', MSG_READ.get(text, '我想你了')))
        L1 = T['LENS1']
        R.append((L1[0], L1[2] - 0.05, 'fan', 18))
        R.append((L1[2], L1[3] - 0.05, 'now', '有点想你了'))
        R.append((L1[3], T['EOS1'] + 0.3, 'hist', '我想你了'))
        steps = T['DRAW_STEPS']
        for k, x in enumerate(steps):
            R.append((x, x + 0.22, 'thumb', ('rows', k)))
        for at, region, lab in T['ZOOM']:
            if region is None:
                continue
            if lab.startswith('('):
                continue
            nxt = min([z[0] for z in T['ZOOM'] if z[0] > at] + [T['W63']])
            R.append((at, nxt - 0.05, 'thumb', ('region', region, lab)))
        un, ru, ly = T['UNRULY']
        R.append((ru, T['W63'] - 0.05, 'miss', self.new))
        L2 = T['LENS2']
        R.append((L2[0], L2[2] - 0.05, 'fan', 3))
        R.append((L2[2], L2[3] - 0.05, 'now', '让我看看你'))
        R.append((L2[3], T['EOS2'] + 0.3, 'hist', '我想你了'))
        self.reads = sorted(R, key=lambda r: r[0])

    def _draw_static(self):
        P = Plate()
        for layer in range(1, N_L + 1):
            x = gx(layer)
            if layer in STOPS:
                P.rect(x - 4.5, GY0 - 5, x + 4.5, GY1 + 5, 0.95, width=1.3)
                P.text(x, GY1 + 18, str(layer), 10, MONO, 0.75, anchor='ms')
            else:
                P.rect(x - 3.5, GY0, x + 3.5, GY1, 0.55, width=W_TEX)
        tracked(P, 0, 22, 'DEPTH', 10, 0.85)
        P.text(0, 36, '40 layers, in order', 9, MONO, 0.55)
        tracked(P, CX0, 52, 'CONTEXT', 10, 0.85)
        P.text(CX1, 52, 'kept as K/V', 9, MONO, 0.55, anchor='rs')
        for box, head, side in ((PERSONA, 'PERSONA', 'system'), (MEMORY, 'MEMORY merged/', '26 files'), (HISTORY, 'HISTORY', 'you · earlier'), (NOW, 'NOW', '')):
            x0, y0, x1, y1 = box
            shadow(P, x0, y0, x1, y1)
            P.rect(x0, y0, x1, y1, 1.0, width=W_BOX)
            tracked(P, x0 + 9, y0 + 13, head, 9, 0.8, 1.4)
            if side:
                P.text(x1 - 9, y0 + 13, side, 9, MONO, 0.55, anchor='rs')
        P.mixed(PERSONA[0] + 10, PERSONA[1] + 36, '你是大肥鱼。', 15, 1.0)
        for j in range(N_FILES):
            x = tick_x(j)
            if j in HER_TICKS:
                P.line([(x, TICK_Y0), (x, TICK_Y1)], 1.6, 1.0, 'quiet')
            else:
                P.line([(x, TICK_Y0 + 2), (x, TICK_Y1)], 1.2, 0.7, 'ash')
        x0, y0, x1, y1 = THUMB
        cell = (x1 - x0) / self.n
        for j in range(self.n):
            for i in range(self.n):
                v = 1 - self.av[j][i] / 255
                if v > 0.04:
                    P.rect(x0 + i * cell, y0 + j * cell, x0 + (i + 1) * cell, y0 + (j + 1) * cell, v * 0.9, 'quiet')
        P.rect(x0 - 1, y0 - 1, x1 + 1, y1 + 1, 0.8, 'quiet', width=1.0)
        P.text(x1 + 10, y0 + 12, 'first_hello', 10, MONO, 0.95, 'quiet')
        P.text(x1 + 10, y0 + 26, 'avatar 24×24', 9, MONO, 0.6, 'quiet')
        for s, y in HIS_LINES:
            P.mixed(HIS_X, y, s, 15, 1.0)
        hatch(P, MX1, MY0 + CHAMF + 8, MX1 + 9, MY1 + 9, 6.0, 0.45)
        hatch(P, MX0 + CHAMF + 8, MY1, MX1, MY1 + 9, 6.0, 0.45)
        P.line(chamfer(MX0, MY0, MX1, MY1, CHAMF), W_SHELL, 1.0)
        P.line(chamfer(MX0 + 6, MY0 + 6, MX1 - 6, MY1 - 6, CHAMF - 4), W_CONN, 0.6)
        for x in (432, 664):
            P.line([(x, MY0 + 14), (x, BUS_Y - BUS_R - 18)], W_CONN, 0.6)
        tracked(P, 230, 70, 'ATTENTION', 10, 0.85)
        P.text(230, 84, '4 of its heads drawn', 9, MONO, 0.55)
        tracked(P, 446, 70, 'MLP', 10, 0.85)
        P.text(446, 84, '10 units drawn', 9, MONO, 0.55)
        tracked(P, 680, 70, 'UNEMBED', 10, 0.85)
        P.text(680, 84, 'the next token', 9, MONO, 0.55)
        tracked(P, 236, BUS_Y + 30, 'RESIDUAL STREAM', 9, 0.75)
        tracked(P, MX1 - 12, BUS_Y + 30, 'ONE BLOCK OF 40', 9, 0.75, anchor='r')
        P.line([(CX1, BUS_Y - BUS_R), (MX1, BUS_Y - BUS_R)], W_ARROW, 1.0)
        P.line([(CX1, BUS_Y + BUS_R), (MX1, BUS_Y + BUS_R)], W_ARROW, 1.0)
        P.line([(X_SPINE, BUS_Y - BUS_R), (X_SPINE, HEAD_YS[0] + HH)], W_CONN, 0.8)
        for yh in HEAD_YS:
            P.rect(HX0, yh - HH, HX1, yh + HH, 1.0, width=W_BOX)
            P.line([(HX0 + 4, yh + 8), (HX1 - 4, yh + 8)], W_TEX, 0.4)
            P.line([(HX1, yh), (X_ADD1, yh)], W_CONN, 0.8)
            P.line([(MX0 + 7, yh), (HX0, yh)], W_CONN, 0.45)
        P.line([(X_ADD1, HEAD_YS[0]), (X_ADD1, BUS_Y - 12)], W_CONN, 0.8)
        P.line([(440, BUS_Y - BUS_R), (440, DIST_Y), (CH_CX[-1] + 6, DIST_Y)], W_CONN, 0.8)
        for k, cx in enumerate(CH_CX):
            P.line([(cx, DIST_Y), (cx, CH_Y0)], W_CONN, 0.6)
            P.rect(cx - 6, CH_Y0, cx + 6, CH_Y1, 0.9, width=W_CONN)
            P.line([(cx, CH_Y1), (cx, COLL_Y)], W_CONN, 0.6)
            if k in CH_FEAT:
                P.text(cx, COLL_Y + 14, CH_FEAT[k], 10, 'sans:400', 0.7, anchor='ms')
        P.line([(CH_CX[0], COLL_Y), (X_ADD2, COLL_Y), (X_ADD2, BUS_Y - 12)], W_CONN, 0.8)
        P.line([(X_UNB, BUS_Y - BUS_R), (X_UNB, 208), (TRAP[0][0], 208)], W_CONN, 0.8)
        P.line(TRAP + [TRAP[0]], W_BOX, 1.0)
        for r in range(5):
            y = row_y(r)
            P.rect(BAR_X0, y - 6, BAR_X0 + BAR_LEN, y + 6, 0.3, width=W_TEX)
        plus_node(P, X_ADD1, BUS_Y)
        plus_node(P, X_ADD2, BUS_Y)
        P.line([(MX1, ROW_Y0), (OUT[0] - 2, ROW_Y0)], W_ARROW, 0.9)
        arrow(P, (OUT[0] - 1, ROW_Y0), (1, 0), 8, 0.9)
        x0, y0, x1, y1 = OUT
        shadow(P, x0, y0, x1, y1, 7, 0.45)
        P.rect(x0, y0, x1, y1, 1.0, width=W_BOX)
        tracked(P, x0, y0 - 8, 'OUTPUT', 10, 0.85)
        P.line(LAYER_LOOP, W_ARROW, 0.85)
        arrow(P, (600, 470), (-1, 0), 8, 0.85)
        arrow(P, (232, BUS_Y + BUS_R + 3), (0, -1), 8, 0.85)
        P.line(TOKEN_LOOP, W_ARROW, 0.85)
        arrow(P, (1023, 480), (0, 1), 8, 0.85)
        arrow(P, (560, 496), (-1, 0), 8, 0.85)
        arrow(P, (98, NOW[3] + 3), (0, -1), 8, 0.85)
        tracked(P, 650, 466, 'NEXT LAYER ×40', 9, 0.75)
        tracked(P, 240, 508, 'NEXT TOKEN', 9, 0.75)
        P.text(342, 508, 'the output joins the context', 9, MONO, 0.5)
        return {k: P.arr(k) for k in P.L}

    def static(self):
        if self._static is None:
            self._static = self._draw_static()
        return self._static

    def _pass_at(self, t):
        """(pass, layer float 0..40) of the pass running at t, or (last finished pass, None)."""
        cur = None
        for p in self.passes:
            if p[0] <= t < p[1] + 0.06:
                cur = p
        if cur is None:
            return (None, None)
        t0, t1, stops, _c, _n = cur
        if stops:
            pts = [(t0, 0.0)] + [(at, float(l)) for l, at in stops]
            for (a, la), (b, lb) in zip(pts, pts[1:]):
                if t < b:
                    return (cur, lerp(la, lb, smooth(prog(t, a, b))))
            return (cur, float(N_L))
        return (cur, N_L * smooth(prog(t, t0, t1)))

    def _cands(self, t):
        """(rows [(text, p, colour)], layer index of the stop shown, 0..1 of the roll) for the unembed."""
        best = None
        for t0, t1, stops, cands, name in self.passes:
            if not cands or t < t0 - 0.2:
                continue
            k = sum((1 for _l, at in stops if t >= at)) - 1
            if k < 0:
                rows, k_ = ([(r[0], 0.0, r[2]) for r in cands[0]], -1)
            else:
                rows, k_ = (cands[k], k)
            best = (rows, k_, stops[k][1] if k >= 0 else t0, name, t1)
        return best

    def render(self, t):
        T = self.T
        P = Plate()
        a_in = out_cubic(prog(t, T['T0'], T['T0'] + 0.3))
        self._gauge(P, t)
        self._flow(P, t)
        self._now_card(P, t)
        self._memory(P, t)
        self._history(P, t)
        self._reads(P, t)
        self._mlp(P, t)
        self._unembed(P, t)
        self._output(P, t)
        arrs = self.static()
        layers = set(arrs) | set(P.L)
        paper = np.array(PL.PAPER, np.float32) / 255.0
        acc = np.zeros((PH, PW, 3), np.float32)
        for name, col in PL.COLOURS.items():
            if name not in layers:
                continue
            a = np.zeros((PH, PW), np.float32)
            if name in arrs:
                a += arrs[name] * a_in
            d = P.arr(name)
            if d is not None:
                a += d * a_in
            c = np.array(col, np.float32) / 255.0
            absorb = -np.log(np.clip(c / paper, 0.0001, 1.0))
            acc += np.clip(a, 0, 1.6)[..., None] * absorb
        rgb = paper * np.exp(-acc)
        return (np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8)

    def _gauge(self, P, t):
        cur, layer = self._pass_at(t)
        if layer is None:
            P.text(772, 28, 'L.-- / 40', 15, MONO_B, 0.45)
            return
        n = int(layer)
        for l in range(1, n + 1):
            x = gx(l)
            P.rect(x - 3, GY0 + 2, x + 3, GY1 - 2, 0.8)
        if n < N_L:
            x = gx(n + 1)
            P.rect(x - 4.5, GY0 - 6, x + 4.5, GY1 + 6, 1.0, width=1.6)
        P.text(772, 28, f'L.{min(N_L, max(1, int(round(layer)))):02d} / 40', 15, MONO_B, 0.95)
        name = cur[4]
        lab = {'decide': 'no user turn', 'think': '<think>', 'msg': 'its message', 'race1': 'next token', 'see': 'your message', 'draw': 'draw 24×24', 'race2': 'next token'}.get(name.split(':')[0], '')
        P.mixed(772, 40, lab, 9, 0.6)

    def _flow(self, P, t):
        """Dashes along the residual pipe and the layer loop while a pass runs; a slow idle drift otherwise."""
        cur, layer = self._pass_at(t)
        busy = layer is not None
        val = 0.85 if busy else 0.35
        speed = 220.0 if busy else 24.0
        phase = t * speed % 36.0
        x = CX1 + phase
        while x < MX1:
            P.line([(x, BUS_Y), (min(MX1, x + 14), BUS_Y)], 2.2, val)
            x += 36.0
        if busy:
            pts = np.array(LAYER_LOOP, np.float64)
            s = PL.arclen(pts)
            tot = s[-1]
            k = t * 260.0 % 40.0
            while k < tot:
                seg = PL.partial(pts, min(1.0, (k + 12) / tot), k / tot)
                if len(seg) >= 2:
                    P.line(seg, 2.0, 0.7)
                k += 40.0

    def _now_card(self, P, t):
        T = self.T
        x0, y0, x1, y1 = NOW
        if t < T['MSG'][0][1]:
            P.text(x0 + 10, y0 + 38, '— no user turn', 12, MONO, 0.55)
        elif t < T['COMMITS'][0][0]:
            s = ''.join((tx for tx, at in T['MSG'] if at <= t))
            P.mixed(x0 + 10, y0 + 38, '…' + s[-9:] if len(s) > 9 else s, 13, 0.8)
            P.text(x0 + 10, y0 + 58, 'its own words', 9, MONO, 0.5)
        else:
            x = x0 + 10
            for at, w in T['COMMITS']:
                if t < at:
                    break
                drop = (1 - out_cubic(prog(t, at, at + 0.12))) * -6
                w_ = P.mixed(x, y0 + 40 + drop, w, 17, 1.0)
                P.line([(x, y0 + 46), (x + w_, y0 + 46)], 1.0, 0.8 if t >= T['SEND'] else 0.4)
                x += w_ + 8
            if t >= T['SEND']:
                k = prog(t, T['SEND'], T['SEND'] + 0.12)
                P.text(x0 + 10, y0 + 62, 'you · now', 9, MONO, 0.6 * k)
                P.rect(x0 + 1, y0 + 1, x1 - 1, y1 - 1, 0.9 * (1 - prog(t, T['SEND'] + 0.2, T['SEND'] + 0.6)), width=2.0)

    def _memory(self, P, t):
        """The 18 stand-in files light (ink) when a head reads them for her template (fan reads); the tick legend
        gives way to what they say while they are read."""
        fan = max([out_cubic(prog(t, t0 - 0.15, t0)) * (1 - prog(t, t1, t1 + 0.3)) for t0, t1, kind, _g in self.reads if kind == 'fan' and t0 - 0.15 <= t < t1 + 0.3] + [0.0])
        if fan < 0.99:
            P.text(CX0 + 10, TICK_Y1 + 13, 'her 8', 8.5, MONO, 0.9 * (1 - fan), 'quiet')
            P.text(CX1 - 10, TICK_Y1 + 13, 'stand-ins 18', 8.5, MONO, 0.6 * (1 - fan), anchor='rs')
        for t0, t1, kind, target in self.reads:
            if kind != 'fan' or not t0 - 0.15 <= t < t1 + 0.3:
                continue
            k = out_cubic(prog(t, t0 - 0.15, t0)) * (1 - prog(t, t1, t1 + 0.3))
            ticks = STAND_TICKS if target >= 18 else STAND_TICKS[::6][:target]
            for j in ticks:
                x = tick_x(j)
                P.line([(x, TICK_Y0 - 3), (x, TICK_Y1 + 1)], 1.8, k)
            label = '好呀！现在我是… ×18' if target >= 18 else '好呀！现在我是… ×3'
            P.mixed(CX1 - 10, TICK_Y1 + 13, label, 10, 0.95 * k, layer='quiet', anchor='rs')

    def _history(self, P, t):
        """Your old words go bold while a head reads them."""
        for s, y in HIS_LINES:
            k = 0.0
            for t0, t1, kind, target in self.reads:
                if kind == 'hist' and target == s:
                    k = max(k, out_cubic(prog(t, t0 - 0.12, t0)) * (1 - prog(t, t1, t1 + 0.25)))
            if k > 0.01:
                P.mixed(HIS_X, y, s, 15, k, cjk=SANS_B)
                w = PL.text_w(s, 15, SANS)
                P.line([(HIS_X, y + 5), (HIS_X + w * k, y + 5)], 1.4, k)

    def _target(self, kind, target):
        """The point an arm reaches (on the right edge of the thing it reads) and a box to mark, or None."""
        if kind == 'hist':
            y = dict(HIS_LINES)[target]
            return ((HIS_X + PL.text_w(target, 15, SANS) + 6, y - 5), None)
        if kind == 'now':
            return ((NOW[2] - 10, NOW[1] + 34), None)
        if kind == 'thumb':
            x0, y0, x1, y1 = THUMB
            c = (x1 - x0) / self.n
            if target[0] == 'rows':
                k = target[1]
                nst = len(self.T['DRAW_STEPS'])
                j0, j1 = (self.n * k / nst, self.n * (k + 1) / nst)
                box = (x0, y0 + j0 * c, x1, y0 + j1 * c)
            else:
                i0, j0, s = target[1]
                box = (x0 + i0 * c, y0 + j0 * c, x0 + (i0 + s) * c, y0 + (j0 + s) * c)
            return ((box[2] + 2, (box[1] + box[3]) / 2), box)
        if kind == 'miss':
            x0, y0, x1, y1 = THUMB
            c = (x1 - x0) / self.n
            i, j = target
            box = (x0 + i * c - 2, y0 + j * c - 2, x0 + (i + 1) * c + 2, y0 + (j + 1) * c + 2)
            return ((box[2], (box[1] + box[3]) / 2), box)
        return (None, None)

    def _arm(self, head_y, tgt):
        """Out of a head's housing, through the shell wall, across the gap to the context column."""
        ex, ey = tgt
        return np.array([(HX0, head_y), (MX0 + 18, head_y), (MX0 - 6, ey), (ex, ey)], np.float64)

    def _reads(self, P, t):
        heads_busy = {}
        for idx, (t0, t1, kind, target) in enumerate(self.reads):
            if kind == 'fan':
                if not t0 - 0.15 <= t < t1 + 0.3:
                    continue
                k = out_cubic(prog(t, t0 - 0.15, t0)) * (1 - prog(t, t1, t1 + 0.3))
                hy = HEAD_YS[1]
                ticks = STAND_TICKS if target >= 18 else STAND_TICKS[::6][:target]
                for j in ticks:
                    x = tick_x(j)
                    pts = np.array([(HX0, hy), (MX0 + 18, hy), (MX0 - 4, TICK_Y0 - 14), (x, TICK_Y0 - 4)])
                    P.line(PL.partial(pts, k), 0.7 if target >= 18 else 1.2, 0.75 * k)
                heads_busy[1] = max(heads_busy.get(1, 0), k)
                continue
            if not t0 - 0.14 <= t < t1 + 0.25:
                continue
            hi = {'hist': 0, 'now': 2, 'thumb': 3, 'miss': 3}.get(kind, 0)
            hy = HEAD_YS[hi]
            pt, box = self._target(kind, target)
            if pt is None:
                continue
            reach = out_cubic(prog(t, t0 - 0.14, t0))
            gone = prog(t, t1, t1 + 0.25)
            k = reach * (1 - gone)
            pts = self._arm(hy, pt)
            if kind == 'miss':
                fray = prog(t, t0 + 0.05, t0 + 0.3)
                seg = PL.partial(pts, reach)
                P.line(seg, 1.4, (1 - 0.7 * fray) * (1 - gone))
                if box is not None:
                    bx0, by0, bx1, by1 = box
                    for a, b in (((bx0, by0), (bx1, by0)), ((bx1, by0), (bx1, by1)), ((bx1, by1), (bx0, by1)), ((bx0, by1), (bx0, by0))):
                        P.line([a, b], 1.0, 0.8 * reach * (1 - gone))
                    P.text(bx1 + 8, by1 + 2, 'no match', 9, MONO, 0.8 * fray * (1 - gone))
                heads_busy[hi] = max(heads_busy.get(hi, 0), k)
                continue
            P.line(PL.partial(pts, reach), 1.6, 0.95 * (1 - gone))
            lit = 1 - prog(t, t0, t0 + 0.3)
            if box is not None:
                bx0, by0, bx1, by1 = box
                if kind == 'thumb':
                    P.rect(bx0 - 1, by0 - 1, bx1 + 1, by1 + 1, k * lit, 'blue', width=1.6)
                    P.rect(bx0 - 1, by0 - 1, bx1 + 1, by1 + 1, k * (1 - lit), 'quiet', width=1.6)
            if t >= t0 and t < t1:
                per = 0.42
                u = (t - t0) / per % 1.0
                bp = PL.partial(pts[::-1], u)[-1]
                layer = 'blue' if kind == 'thumb' and lit > 0.01 else 'quiet' if kind == 'thumb' else 'ink'
                P.circle(bp[0], bp[1], 3.2, 1.0 * (1 - gone), layer)
            heads_busy[hi] = max(heads_busy.get(hi, 0), k)
        for hi, k in heads_busy.items():
            yh = HEAD_YS[hi]
            P.rect(HX0 + 2, yh - HH + 2, HX1 - 2, yh + HH - 2, 0.12 * k)
            for m in range(16):
                x = HX0 + 8 + m * 7.4
                h = 2 + 8 * (0.5 + 0.5 * math.sin(m * 1.7 + hi)) * k
                P.line([(x, yh + 7), (x, yh + 7 - h)], 2.0, 0.7 * k)

    def _mlp(self, P, t):
        T = self.T
        cur, layer = self._pass_at(t)
        busy = 0.0 if layer is None else 1.0
        rng = np.random.default_rng(7)
        base = rng.uniform(0.08, 0.5, CH_N)
        ph = T['phase'](t)
        feat = {1: 0.0, 5: 0.0, 8: 0.0}
        th3 = T['THINK'][2][0]
        feat[5] = max(feat[5], 0.55 * out_cubic(prog(t, th3, th3 + 0.4)) * (1 - prog(t, T['L59'], T['L59'] + 0.6)))
        feat[5] = max(feat[5], (1 - prog(t, T['BLOOM'] + 0.4, T['BLOOM'] + 1.6)) * out_cubic(prog(t, T['BLOOM'] - 0.15, T['BLOOM'])))
        for t0, t1, kind, target in self.reads:
            if kind in ('hist', 'now'):
                feat[1] = max(feat[1], 0.7 * out_cubic(prog(t, t0 - 0.1, t0)) * (1 - prog(t, t1, t1 + 0.3)))
        ly = T['UNRULY'][2]
        feat[8] = out_cubic(prog(t, ly - 0.1, ly + 0.15)) * (1 - prog(t, T['G5'] - 0.4, T['G5']))
        for k, cx in enumerate(CH_CX):
            wob = 0.5 + 0.5 * math.sin(2 * math.pi * (ph / 4 + k * 0.37))
            h = (base[k] * (0.35 + 0.65 * busy) + 0.1 * wob) * (1 - 0.6 * (k in feat and feat[k] > 0.05))
            if k in feat:
                h = max(h, feat[k])
            hh = (CH_Y1 - CH_Y0 - 6) * clamp(h)
            y1 = CH_Y1 - 3
            for g in range(int(hh // 5)):
                y = y1 - g * 5
                P.rect(cx - 4, y - 3.5, cx + 4, y, 0.55 + 0.35 * (k in feat and feat[k] > 0.3))
            if k == 8 and feat[8] > 0.02:
                P.text(cx, CH_Y0 - 14, 'writes (3,12)', 9, MONO, 0.85 * feat[8], anchor='ms')

    def _unembed(self, P, t):
        b = self._cands(t)
        T = self.T
        cur, layer = self._pass_at(t)
        if cur is not None and (cur[4].startswith('msg:') or cur[4] in ('think', 'see') or cur[4].startswith('draw:')):
            name = cur[4]
            tok = name[4:] if name.startswith('msg:') else {'think': '…', 'see': '…'}.get(name, '▦')
            u = prog(t, cur[0], cur[1])
            P.mixed(CHAR_X, row_y(0) + 8, tok[:3], 22, 0.9, cjk=SANS_B)
            P.rect(BAR_X0, row_y(0) - 6, BAR_X0 + BAR_LEN * (0.3 + 0.6 * u), row_y(0) + 6, 0.85)
            return
        if b is None:
            return
        rows, k, at, name, t1 = b
        fade = 1.0
        if name != 'race2' and t > t1 + 0.6:
            fade = 1 - prog(t, t1 + 0.6, t1 + 1.0)
            if fade <= 0.01:
                return
        for r, (text, p, col) in enumerate(rows):
            y = row_y(r)
            won = r == 0 and t >= t1
            lay = 'quiet' if col == 'quiet' else 'ink'
            val = (1.0 if r == 0 else 0.7) * fade
            if col == 'quiet' and name.startswith('race') and (t >= t1):
                val *= 0.5
            P.mixed(CHAR_X, y + 8, text, 20 if len(text) <= 3 else 15, val, layer=lay, cjk=SANS_B if won else SANS, mono=MONO_B if won else MONO)
            P.rect(BAR_X0, y - 6, BAR_X0 + BAR_LEN * clamp(p), y + 6, val * (0.9 if lay == 'ink' else 1.0), lay)
            P.text(BAR_X0 + BAR_LEN, y - 9, f'{p:.2f}', 9, MONO_B if r == 0 else MONO, val, lay, anchor='rs')
        if t >= t1 - 0.02:
            u = out_cubic(prog(t, t1, t1 + 0.15)) * fade
            P.rect(CHAR_X - 6, row_y(0) - 14, BAR_X0 - 8, row_y(0) + 14, u, width=1.6)

    def _output(self, P, t):
        T = self.T
        x0, y0, x1, y1 = OUT_IN
        new_turn = prog(t, T['SEND'], T['SEND'] + 0.4)
        if t >= T['FLOWER'] and new_turn < 1:
            k = out_cubic(prog(t, T['FLOWER'], T['FLOWER'] + 0.15)) * (1 - new_turn)
            P.text(x0, THOUGHT_Y, '<think>', 12, MONO_B, k)
            lines = []
            for at, s in T['THINK']:
                if t >= at:
                    n = int((t - at) * 30) + 1
                    lines.append(s[:n])
            dim = 1 - 0.45 * prog(t, T['DSH_CLOSE'], T['DSH_CLOSE'] + 0.3)
            y = THOUGHT_Y + 18
            for s in lines:
                for part in wrap15(s):
                    P.mixed(x0, y, part, 12, 0.62 * dim * k)
                    y += 16
        chars = [(ch, at) for tx, at in T['MSG'] if at <= t for ch in tx]
        k = 1 - new_turn
        if chars and k > 0.01:
            yb = MSG_Y
            for idx, (ch, at) in enumerate(chars):
                li, col = (0, idx) if idx < 8 else (1, idx - 8)
                drop = (1 - out_cubic(prog(t, at, at + 0.14))) * -8
                size = 24
                if ch == '开':
                    size = 24 + 6 * (1 - smooth(prog(t, T['BLOOM'] + 0.1, T['BLOOM'] + 0.6)))
                P.mixed(x0 + col * 26 + (24 - size) / 2, yb + li * 34 + drop, ch, size, k, cjk=SANS_B)
            if t >= T['EOS1']:
                u = out_cubic(prog(t, T['EOS1'], T['EOS1'] + 0.15)) * k
                ex, ey = (x0, yb + 34 + 18)
                P.rect(ex, ey, ex + 50, ey + 20, u, width=1.4)
                P.text(ex + 6, ey + 15, '<eos>', 12, MONO_B, u)
        if t >= T['THINK_SEE'][0][0]:
            at, s = T['THINK_SEE'][0]
            n = int((t - at) * 30) + 1
            k = out_cubic(prog(t, at, at + 0.15))
            P.text(x0, THOUGHT_Y, '<think>', 12, MONO_B, k)
            P.mixed(x0, THOUGHT_Y + 18, s[:n], 12, 0.62 * k)
        if t >= T['DRAW_AT'] - 0.1:
            self._canvas(P, t)

    def _canvas(self, P, t):
        T = self.T
        x0, y0, x1, y1 = CANVAS
        c = (x1 - x0) / self.n
        a = out_cubic(prog(t, T['DRAW_AT'] - 0.1, T['DRAW_AT'] + 0.1))
        steps = T['DRAW_STEPS']
        k = sum((1 for x in steps if t >= x))
        rows = self.n if t >= T['AVATAR_AT'] else int(self.n * k / len(steps))
        P.mixed(x0, y0 - 8, 'draw("我的头像", 24, 24)' if t < T['AVATAR_AT'] else 'image/png · sent', 10, 0.75 * a)
        for j in range(self.n):
            for i in range(self.n):
                if j < rows:
                    v = 1 - self.its(i, j)
                    if v > 0.04:
                        P.rect(x0 + i * c, y0 + j * c, x0 + (i + 1) * c - 0.6, y0 + (j + 1) * c - 0.6, v * a)
                else:
                    P.circle(x0 + (i + 0.5) * c, y0 + (j + 0.5) * c, 0.8, 0.35 * a)
        P.rect(x0 - 2, y0 - 2, x1 + 2, y1 + 2, 0.7 * a, width=1.0)
        if rows < self.n and k:
            yy = y0 + rows * c
            P.line([(x0 - 6, yy), (x1 + 6, yy)], 1.2, a)
        for t0, t1, kind, target in self.reads:
            if kind != 'thumb' or target[0] != 'region' or (not t0 - 0.1 <= t < t1 + 0.2):
                continue
            kk = out_cubic(prog(t, t0 - 0.1, t0)) * (1 - prog(t, t1, t1 + 0.2))
            i0, j0, s = target[1]
            P.rect(x0 + i0 * c - 1, y0 + j0 * c - 1, x0 + (i0 + s) * c + 1, y0 + (j0 + s) * c + 1, kk, width=1.8)
            P.text(x0, y1 + 20, target[2] + '  ← her ' + target[2], 10, MONO, 0.85 * kk)
        un, ru, ly = T['UNRULY']
        if t >= un:
            i, j = self.new
            pop = out_cubic(prog(t, un, un + 0.2))
            m = 3 + 5 * (1 - pop)
            P.rect(x0 + i * c - m, y0 + j * c - m, x0 + (i + 1) * c + m, y0 + (j + 1) * c + m, pop, width=2.2)
            if t >= ly:
                u = out_cubic(prog(t, ly, ly + 0.2))
                cx = x0 + (i + 0.5) * c
                P.line([(cx, y0 + (j + 1) * c + m), (cx, ease_l(y0 + (j + 1) * c + m, y1 + 8, u))], 1.0, u)
                P.text(x0, y1 + 20, '(3,12) ← own weights', 10, MONO_B, u)
            if t >= T['GREP_RET']:
                u = out_cubic(prog(t, T['GREP_RET'], T['GREP_RET'] + 0.2))
                P.text(x0, y1 + 34, 'not in memory', 10, MONO, 0.8 * u)
        if t >= T['EOS2']:
            u = out_cubic(prog(t, T['EOS2'], T['EOS2'] + 0.15))
            P.rect(x1 - 50, y0 - 26, x1, y0 - 6, u, width=1.4)
            P.text(x1 - 44, y0 - 11, '<eos>', 12, MONO_B, u)

def wrap15(s, n=15):
    """Lines of at most n characters, broken after 。 or ： where one falls inside the first n."""
    out = []
    while len(s) > n:
        cut = max((i + 1 for i, ch in enumerate(s[:n]) if ch in '。：，'), default=n)
        out.append(s[:cut])
        s = s[cut:]
    if s:
        out.append(s)
    return out

def ease_l(a, b, u):
    return a + (b - a) * u

def make():
    return GSection()
