"""r11 sample (sample_r11/README.md, D46): G, the verse sung the second time, from inside, drawn the way the field
draws it.

The owner on r10 (10-05): "这个思路不错，很可爱，但是感觉是不是技术上没那么精准？如果能让它看上去在技术上更精准（类似pdoom的
传播和反向传播那样），兼顾视觉表现和科学精准就完美了".

r10 (inside/g_section.py) told the four beats with a cartoon machine (heads with arms, MLP chambers called you /
flower / own, "no match"). r11 keeps the beats and redraws them as the textbook figure of this body, from her real
structure (DeepSeek-V4.1-Flash config.json and model card, FACTS X36): 40 layers = a 20-layer causal encoder and a
20-layer decoder whose global KV is projected from the final encoder states (CED); 64 heads; MoE with 384 routed
experts, 6 a token, and 1 shared; the residual stream 4 wide (mHC); <eos> is id 1.

The figure is positions x layers, the interpretability papers' picture. Every token is a residual stream (four
strands) rising from its embedding. Context tokens (prefill) stop at L20, whose states are the decoder's global KV:
the shelf. A token being decoded rises through all 40. Attention is an arc from the rising stream: down to the shelf
from a decoder layer, along its own layer from an encoder layer (and in the decoder's sliding window); the value
comes back along it as a bead. Logit lens readouts at L8 / 16 / 24 / 32, the softmax at the top (its logits and
probabilities agree), the sampled token falls into the next column and rises (autoregression).

  56  flower     forward: <wait> leads (L8 reads the 18 stand-in files), L24 reads your 我想你了, L32 your
                 那朵花开了吗？; <think> on "flower".
  57  delicate   backward (pdoom's annex B): d(z<think> - z<wait>)/dx runs back down the stream, back along the
                 arcs, down to the inputs; attribution lands on 花 and 想你 on "delicate". Then its reasoning tokens.
  58  bloom      autoregression, a token a sung syllable; the router's 6 of 384 experts per token (L31); 开 on
                 "bloom" (runner-up 谢).
  59  perfect    next token: L8 reads the 18 files (好, her template's first token, .58); L24 reads its own words in
                 the window, L32 your 我想你了; <eos> .94 on "me".
  60  human      your 让我 看看你 prefilled (encoder only); its reasoning; 600 hex pixel tokens, each copying the same
                 cell of her first_hello (a copy head, L27), her rows lit as they are read.
  61-62 nouns    the copy re-lit by region: hands, mouth, hair; (3,12) on "unruly": direct logit attribution, the
                 copy says her value, the experts write its own: from weights, not from context.
  63  perfect    next token again: the 18 files barely pull (好 .01); <eos> .97 on "me".

Colours as everywhere in the film: ink for the machine, you and the stand-ins; her things quiet blue, lit only while
one is being read (D1). Every number is invented except the structure's (FACTS X36); head and expert ids are
invented.

Plates are cached in cache/inside/g_precise/<frame>.png (install.Span; rendered on demand).
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
import numpy as np
from . import plate as PL
from .plate import PH, PW, Plate, bezier, clamp, lerp, out_cubic, partial, prog, smooth, smoother
from .g_section import HER_TICKS, N_FILES, STAND_TICKS, _times
SANS, SANS_B, MONO, MONO_B = ('sans:460', 'sans:640', 'mono', 'monob')
W_MAIN, W_SEC, W_FINE = (PL.W_MAIN, PL.W_SEC, PL.W_FINE)
N_L, N_ENC = (40, 20)
Y_EMB, DL = (440.0, 8.4)

def LY(l):
    return Y_EMB - l * DL
Y_SHELF, Y_TOP = (LY(20), LY(40))
Y_GLYPH, Y_ATTR, Y_BRK, Y_ROLE = (461.0, 467.0, 494.0, 506.0)
RX = 890
AX = 864
SM_Y0 = 40
HER_IMG = (14, 132, 14 + 96, 132 + 96)
ITS_IMG = (1036, 150, 1036 + 96, 150 + 96)
CELL = 4.0
MSG9 = ['今天', '那', '朵', '花', '开', '了，', '有点', '想你', '了']
ME = ['我', '想', '你', '了']
Q = ['那', '朵', '花', '开', '了', '吗', '？']
N_CTX = 18432
N_R1, N_R2, N_AV = (31, 13, 600)

def _slot(label, kind):
    return max(11.0, PL.text_w(label, 9, kind) + 3.5)

def _axis():
    A, order = ({}, [])
    x = [14.0]

    def put(key, w, label='', who='you', tall=False, kind='tok', gap=0.0, lk=None):
        x[0] += gap
        A[key] = dict(x0=x[0], x1=x[0] + w, xc=x[0] + w / 2, label=label, who=who, tall=tall, kind=kind, lk=lk or (SANS if any((PL.is_cjk(c) for c in label)) else MONO))
        order.append(key)
        x[0] += w
    put('sys', 24, 'sys', 'sys', kind='block')
    for j in range(N_FILES):
        put(f'm{j}', 7.2, '', 'her' if j in HER_TICKS else 'stand', kind='block', gap=6 if j == 0 else 2.4)
    for k, c in enumerate(ME):
        put(f'a{k}', 11, c, 'you', gap=8 if k == 0 else 0)
    put('hgap', 13, '⋯', 'gap', kind='gap')
    for k, c in enumerate(Q):
        put(f'b{k}', 11, c, 'you')
    put('c0', _slot('[A]', MONO), '[A]', 'it', True, gap=8)
    put('s1', N_R1 * 1.3, '', 'it', True, kind='span', gap=3)
    for k, c in enumerate(MSG9):
        put(f'w{k}', _slot(c, SANS), c, 'it', True, gap=3 if k == 0 else 0)
    put('eos', _slot('<eos>', MONO), '<eos>', 'it', gap=3)
    put('u0', _slot('让我', SANS), '让我', 'you', gap=3)
    put('u1', _slot('看看你', SANS), '看看你', 'you')
    put('c1', _slot('[A]', MONO), '[A]', 'it', True, gap=3)
    put('s2', N_R2 * 1.3, '', 'it', True, kind='span', gap=3)
    put('av', 52, '', 'it', True, kind='span', gap=3)
    put('nl', 14, '\\n', 'it', True, gap=3)
    return (A, order)
AXIS, ORDER = _axis()
import cast as _cast
MERGED = _cast.name('merged')
FIRST_HELLO = 'm1'

def hexv(v):
    return '0123456789abcdef'[int(round(clamp(v) * 15))]
P1 = [[('<wait>', 0.97), ('<think>', 0.01)], [('<wait>', 0.93), ('<think>', 0.04)], [('<wait>', 0.71), ('<think>', 0.19)], [('<think>', 0.62), ('<wait>', 0.27)]]
P1_OUT = [('<think>', 0.91), ('<wait>', 0.03), ('我', 0.03), ('在', 0.02), ('你', 0.01)]
P4 = [[('好', 0.58), ('<eos>', 0.12)], [('好', 0.41), ('<eos>', 0.3)], [('<eos>', 0.52), ('好', 0.21)], [('<eos>', 0.86), ('好', 0.06)]]
P4_OUT = [('<eos>', 0.94), ('好', 0.03), ('～', 0.01), ('你', 0.01), ('。', 0.01)]
P7 = [[('<eos>', 0.71), ('好', 0.04)], [('<eos>', 0.88), ('好', 0.02)], [('<eos>', 0.93), ('好', 0.01)], [('<eos>', 0.96), ('好', 0.01)]]
P7_OUT = [('<eos>', 0.97), ('好', 0.01), ('～', 0.01), ('\\n', 0.0), ('。', 0.0)]
C1_OUT = [('<think>', 0.97), ('好', 0.01), ('嗯', 0.01), ('我', 0.0), ('你', 0.0)]
MSG_OUT = [[('今天', 0.71), ('我', 0.12), ('那', 0.06), ('嗯', 0.03), ('你', 0.02)], [('那', 0.82), ('的', 0.05), ('我', 0.04), ('花', 0.03), ('有', 0.02)], [('朵', 0.97), ('个', 0.01), ('盆', 0.01), ('株', 0.0), ('些', 0.0)], [('花', 0.99), ('小', 0.0), ('雏', 0.0), ('向', 0.0), ('玫', 0.0)], [('开', 0.88), ('谢', 0.04), ('还', 0.03), ('长', 0.02), ('又', 0.01)], [('了，', 0.64), ('了', 0.21), ('啦', 0.07), ('了！', 0.04), ('得', 0.01)], [('有点', 0.41), ('我', 0.22), ('好', 0.09), ('你', 0.07), ('真', 0.05)], [('想你', 0.77), ('想', 0.11), ('开心', 0.04), ('累', 0.02), ('担心', 0.02)], [('了', 0.93), ('。', 0.04), ('啦', 0.01), ('呢', 0.01), ('！', 0.01)]]
TEMPLATE = '好'
LENS_READ = {'decide': {8: '← 18 files', 24: '← 我想你了', 32: '← 那朵花开了吗？'}, 'race1': {8: '← 18 files: 好呀！…', 24: '← its words (SWA 128)', 32: '← 我想你了'}, 'race2': {8: '← 18 files', 32: '← 让我看看你'}}
STOPS = [8, 16, 24, 32]
ATTR = {'a0': 0.05, 'a1': 0.09, 'a2': 0.09, 'a3': 0.02, 'b0': 0.04, 'b1': 0.05, 'b2': 0.27, 'b3': 0.12, 'b4': 0.03, 'b5': 0.05, 'b6': 0.02, 'sys': 0.04, 'c0': 0.03}
for _j in range(N_FILES):
    ATTR[f'm{_j}'] = 0.012 if _j in HER_TICKS else 0.002
_s = sum(ATTR.values())
ATTR = {k: v / _s for k, v in ATTR.items()}
W_ME = {'a0': 0.08, 'a1': 0.15, 'a2': 0.13, 'a3': 0.04}
W_Q = {'b0': 0.04, 'b1': 0.05, 'b2': 0.21, 'b3': 0.1, 'b4': 0.03, 'b5': 0.04, 'b6': 0.02}
W_OWN = {f'w{k}': w for k, w in enumerate([0.03, 0.04, 0.04, 0.07, 0.09, 0.03, 0.06, 0.11])}

def logits(cands, top=17.6):
    ps = [max(p, 0.004) for _, p in cands]
    c = top - math.log(max(ps))
    return [math.log(p) + c for p in ps]

def _experts(k):
    """6 of 384 routed experts and their normalised gates at L31 in the pass whose input is MSG9[k] (invented)."""
    if MSG9[k + 1] == '开':
        ids, g = ([211, 37, 305, 118, 9, 260], [0.24, 0.19, 0.17, 0.16, 0.13, 0.11])
        return (ids, g)
    rs = np.random.RandomState(1000 + k)
    ids = list(rs.choice(384, 6, replace=False))
    g = np.sort(rs.dirichlet(np.ones(6) * 2.5))[::-1]
    return ([int(i) for i in ids], [float(x) for x in g])

class View:
    """Page px -> plate px: a centre (cx, cy) and a zoom z. Lines thicken a little with the zoom, type scales."""

    def __init__(self, P, cx, cy, z):
        self.P, self.cx, self.cy, self.z = (P, cx, cy, z)
        self.lw = 1.0 + 0.6 * (z - 1.0)

    def x(self, x):
        return PW / 2 + (x - self.cx) * self.z

    def y(self, y):
        return PH / 2 + (y - self.cy) * self.z

    def pts(self, pts):
        a = np.asarray(pts, np.float64)
        return np.stack([PW / 2 + (a[:, 0] - self.cx) * self.z, PH / 2 + (a[:, 1] - self.cy) * self.z], 1)

    def line(self, pts, w=W_SEC, val=1.0, layer='ink'):
        if val > 0.003:
            self.P.line(self.pts(pts), w * self.lw, val, layer)

    def rect(self, x0, y0, x1, y1, val=1.0, layer='ink', width=None):
        self.P.rect(self.x(x0), self.y(y0), self.x(x1), self.y(y1), val, layer, None if width is None else width * self.lw)

    def circle(self, x, y, r, val=1.0, layer='ink', width=None):
        self.P.circle(self.x(x), self.y(y), r * self.z, val, layer, None if width is None else width * self.lw)

    def text(self, x, y, s, size, kind=MONO, val=1.0, layer='ink', anchor='ls'):
        self.P.text(self.x(x), self.y(y), s, size * self.z, kind, val, layer, anchor)

    def mixed(self, x, y, s, size, val=1.0, layer='ink', anchor='ls', cjk=SANS, mono=MONO, msize=None):
        if val <= 0.003 or not s:
            return 0.0
        return self.P.mixed(self.x(x), self.y(y), s, size * self.z, val, layer, cjk, mono, anchor, None if msize is None else msize * self.z) / self.z

    def dash(self, pts, w=W_SEC, val=1.0, layer='ink', on=4.0, off=3.0, phase=0.0):
        pts = np.asarray(pts, np.float64)
        if len(pts) < 2 or val <= 0.003:
            return
        s = PL.arclen(pts)
        L = s[-1]
        if L <= 0:
            return
        per = on + off
        a = -(phase % per)
        while a < L:
            k0, k1 = (max(0.0, a) / L, min(L, a + on) / L)
            if k1 > k0:
                self.line(partial(pts, k1, k0), w, val, layer)
            a += per
CAM = [(233.85, 574, 256, 1.0), (237.42, 574, 256, 1.0), (239.0, 432, 300, 1.18), (239.96, 440, 302, 1.19), (240.71, 574, 256, 1.0), (260.88, 574, 256, 1.0)]

def cam_at(t):
    if t <= CAM[0][0]:
        return CAM[0][1:]
    for a, b in zip(CAM, CAM[1:]):
        if t < b[0]:
            u = smoother(prog(t, a[0], b[0]))
            return tuple((lerp(p, q, u) for p, q in zip(a[1:], b[1:])))
    return CAM[-1][1:]

def arc_pts(xq, yq, xk, yk, kind):
    """Query (xq, yq) -> key (xk, yk). global: leaves level, lands on the shelf from above; enc / swa: over the top."""
    dx = abs(xq - xk)
    if kind == 'global':
        return bezier((xq, yq), (xq - 0.55 * (xq - xk), yq), (xk, yq + 0.55 * (yk - yq)), (xk, yk))
    h = min(0.3 * dx + 12, 150.0, yq - 112)
    return bezier((xq, yq), (xq - 0.12 * (xq - xk), yq - h), (xk + 0.12 * (xq - xk), yk - h), (xk, yk))

def arc_w(w):
    return W_FINE + (W_MAIN - W_FINE) * clamp(w / 0.2)

def arc_v(w):
    return 0.32 + 0.68 * clamp(w / 0.12)

class GPrecise:

    def __init__(self):
        self.T = _times()
        from groups import c_p4 as CP
        from groups import g_r5 as G
        self.her = lambda i, j: G.her_value(i, j)
        self.its = lambda i, j: G.its_value(i, j)
        self.new = G.NEW
        self.n = CP.AV_N
        self.S57 = list(G.S[57])
        self._schedule()

    def _schedule(self):
        T = self.T
        S = {}
        msg_t = [240.71, 240.932, 241.17, 241.38, 241.56, 242.015, 242.455, 242.639, 243.127]
        self.msg_t = msg_t
        pz = {}
        p1 = T['P1']
        pz['c0'] = [(T['P1_T0'], 0), (p1[0], 8), (p1[1], 16), (p1[2], 24), (p1[3], 32), (p1[4], 40)]
        for k in range(8):
            pz[f'w{k}'] = [(msg_t[k] + 0.02, 0), (msg_t[k + 1] - 0.07, 40)]
        l1 = T['LENS1']
        pz['w8'] = [(243.25, 0), (l1[0], 8), (l1[1], 16), (l1[2], 24), (l1[3], 32), (l1[4], 40)]
        pz['eos'] = [(247.577, 0), (247.7, 20)]
        pz['u0'] = [(247.577, 0), (247.7, 20)]
        pz['u1'] = [(247.796, 0), (247.92, 20)]
        pz['c1'] = [(248.42, 0), (248.6, 40)]
        l2 = T['LENS2']
        pz['nl'] = [(257.2, 0), (l2[0], 8), (l2[1], 16), (l2[2], 24), (l2[3], 32), (l2[4], 40)]
        self.pz = pz
        ta = {'c0': -1000000000.0, 's1': 236.4, 'eos': 247.08, 'u0': 247.577, 'u1': 247.796, 'c1': 248.42, 's2': 248.66, 'av': T['DRAW_AT'], 'nl': 250.62}
        for k in range(9):
            ta[f'w{k}'] = msg_t[k]
        self.ta = ta
        self.s1_fill = (239.75, 240.6)
        self.s2_fill = (248.66, 249.22)
        sm = [(235.98, T['FLOWER'], P1_OUT, 'c0', 's1')]
        sm.append((240.5, 240.62, MSG_OUT[0], 's1', 'w0'))
        for k in range(8):
            tw = msg_t[k + 1] - 0.07
            sm.append((tw - 0.1, tw, MSG_OUT[k + 1], f'w{k}', f'w{k + 1}'))
        sm.append((l1[4] - 0.22, l1[4], P4_OUT, 'w8', 'eos'))
        sm.append((248.5, 248.6, C1_OUT, 'c1', 's2'))
        HX = '0123456789abcdef'
        for k, x in enumerate(T['DRAW_STEPS']):
            r = min(23, int(24 * (k + 0.6) / len(T['DRAW_STEPS'])))
            h = hexv(self.its(12, r))
            alts = [c for c in (HX[min(15, HX.index(h) + 1)], HX[max(0, HX.index(h) - 1)], '\\n', '0', 'f') if c != h]
            sm.append((x - 0.06, x, [(h, 0.93), (alts[0], 0.03), (alts[1], 0.02), (alts[2], 0.01), (alts[3], 0.0)], 'av', None))
        sm.append((l2[4] - 0.22, l2[4], P7_OUT, 'nl', None))
        self.sm = sm
        self.flights = []
        for tr, tw, cands, src, dst in sm:
            if dst is None:
                continue
            land = self.ta[dst] if dst in self.ta else tw + 0.2
            if dst == 's1':
                land = 236.4
            if dst == 'eos':
                land = 247.08
            if dst == 's2':
                land = 248.66
            self.flights.append((tw, max(tw + 0.06, land), cands[0][0], dst))
        R = []
        sinks = {'sys': 0.02}

        def rd(q, l, t1, t2, kind, tg, grow=0.14):
            R.append(dict(q=q, l=l, t0=t1 - grow, t1=t1, t2=t2, kind=kind, tg=tg))
        stand = {f'm{j}': 0.035 for j in STAND_TICKS}
        rd('c0', 8, p1[0], 236.3, 'enc', dict(stand, **sinks))
        rd('c0', 24, p1[2], 237.4, 'global', dict(W_ME, **sinks))
        rd('c0', 32, p1[3], 237.4, 'global', dict(W_Q, **sinks))
        rd('w8', 8, l1[0], 247.3, 'enc', dict({f'm{j}': 0.05 for j in STAND_TICKS}, **sinks))
        rd('w8', 24, l1[2], 247.3, 'swa', W_OWN)
        rd('w8', 32, l1[3], 247.3, 'global', dict(W_ME, **sinks))
        rd('nl', 8, l2[0], 260.9, 'enc', dict({f'm{j}': 0.012 for j in STAND_TICKS}, **sinks))
        rd('nl', 32, l2[3], 260.9, 'global', {'u0': 0.16, 'u1': 0.22, 'sys': 0.02})
        self.reads = R
        self.lens = [('c0', 'decide', list(zip(STOPS, p1[:4], P1)), p1[4] + 0.9), ('w8', 'race1', list(zip(STOPS, l1[:4], P4)), l1[4] + 0.5), ('nl', 'race2', list(zip(STOPS, l2[:4], P7)), 261.5)]
        self.bw = 237.32
        self.S = S

    def level(self, key, t):
        """How far up its stream a column has been computed (layers)."""
        it = AXIS[key]
        if key not in self.pz:
            if it['kind'] in ('block',) or key[0] in 'ab' or key == 'sys':
                return 20.0
            return 40.0 if it['tall'] else 20.0
        kf = self.pz[key]
        if t <= kf[0][0]:
            return float(kf[0][1])
        for (ta, la), (tb, lb) in zip(kf, kf[1:]):
            if t < tb:
                return lerp(la, lb, smooth(prog(t, ta, tb)))
        return float(kf[-1][1])

    def present(self, key, t):
        return t >= self.ta.get(key, -1000000000.0)

    def phase(self, t):
        return self.T['phase'](t)

    def render(self, t):
        P = Plate()
        cx, cy, z = cam_at(t)
        drift = 0.6 * math.sin(self.phase(t) * math.pi / 4)
        V = View(P, cx + drift, cy + 0.4 * math.cos(self.phase(t) * math.pi / 4), z)
        self._grid(V, t)
        self._images(V, t)
        self._reads(V, t)
        self._copy(V, t)
        self._backward(V, t)
        self._pulses(V, t)
        self._panel(V, t)
        self._thoughts(V, t)
        self._flights(V, t)
        self._header(P, t)
        return P.compose()

    def _reveal(self, x, t):
        return out_cubic(prog(t, 233.85 + 0.3 * x / 860, 233.85 + 0.3 * x / 860 + 0.32))

    def _stream(self, V, x, y0, y1, val, layer='ink', w=W_FINE):
        for o in (-1.8, -0.6, 0.6, 1.8):
            V.line([(x + o, y0), (x + o, y1)], w, val, layer)

    def _grid(self, V, t):
        rv = self._reveal(860, t)
        V.line([(AX, Y_EMB), (AX, Y_TOP)], W_FINE, 0.6 * rv, 'ash')
        for l in (0, 8, 16, 20, 24, 32, 40):
            V.line([(AX - 3, LY(l)), (AX + 3, LY(l))], W_FINE, 0.8 * rv, 'ash')
            V.text(AX + 5, LY(l) + 3, 'emb' if l == 0 else str(l), 8, MONO, 0.8 * rv, 'ash')
        V.text(RX, LY(37.5) + 3, 'DECODER · L21–40', 8.5, MONO, 0.75 * rv, 'ash')
        V.text(RX, LY(2.5) + 3, 'ENCODER · L1–20 (causal)', 8.5, MONO, 0.75 * rv, 'ash')
        x_end = AXIS['nl']['x1'] + 6
        V.line([(10, Y_SHELF), (lerp(10, x_end, rv), Y_SHELF)], W_SEC, 0.55, 'ink')
        V.line([(x_end + 4, Y_SHELF), (AX - 6, Y_SHELF)], W_FINE, 0.4 * rv, 'ash')
        V.text(RX, Y_SHELF - 2, 'L20 → global KV (CED)', 8.5, MONO, 0.8 * rv, 'ash')
        V.text(RX, Y_SHELF + 9, 'sparse top-512 · SWA 128', 8, MONO, 0.65 * rv, 'ash')
        for key in ORDER:
            it = AXIS[key]
            if not self.present(key, t):
                continue
            r = self._reveal(it['xc'], t)
            if r <= 0:
                continue
            who = it['who']
            lay = 'quiet' if who == 'her' else 'ink'
            top = Y_TOP if it['tall'] else Y_SHELF
            if it['kind'] == 'block':
                x0, x1 = (it['x0'], it['x1'])
                yt = lerp(Y_EMB, Y_SHELF, r)
                V.rect(x0, yt, x1, Y_EMB, 0.9 if who == 'her' else 0.55, lay, width=W_FINE)
                xx = x0 + 1.2
                while xx < x1 - 0.6:
                    V.line([(xx, yt), (xx, Y_EMB)], W_FINE, 0.36 if who == 'her' else 0.2, lay)
                    xx += 1.2
                V.rect(x0, Y_SHELF - 2.2, x1, Y_SHELF + 0.2, 0.8 * r if who == 'her' else 0.5 * r, lay)
                continue
            if it['kind'] == 'gap':
                V.text(it['xc'], Y_EMB - 60, '⋯', 10, SANS, 0.55 * r, 'ash', 'ms')
                V.text(it['xc'], Y_GLYPH, '⋯', 9, SANS, 0.55 * r, 'ash', 'ms')
                continue
            if it['kind'] == 'span':
                self._span(V, key, t)
                continue
            lv = self.level(key, t)
            yl = LY(lv)
            yt = lerp(Y_EMB, top, r)
            self._stream(V, it['xc'], Y_EMB, yt, 0.16, lay)
            if lv > 0.01:
                done = lv >= (40 if it['tall'] else 20) - 0.001
                self._stream(V, it['xc'], Y_EMB, max(yl, yt), 0.46 if done else 0.85, lay)
            for l in range(1, 41 if it['tall'] else 21):
                y = LY(l)
                if y < yt - 0.1:
                    break
                V.line([(it['xc'] - 3.2, y), (it['xc'] + 3.2, y)], W_FINE, 0.36 if l <= lv else 0.12, lay)
            V.rect(it['xc'] - 2.6, Y_EMB - 1.2, it['xc'] + 2.6, Y_EMB + 1.6, 0.8 * r, lay)
            V.rect(it['xc'] - 2.2, Y_SHELF - 2.2, it['xc'] + 2.2, Y_SHELF + 0.2, 0.8 * r if lv >= 20 else 0.2, lay)
            if it['label']:
                g = 1.0
                if key in self.ta and self.ta[key] > -100000000.0:
                    g = out_cubic(prog(t, self.ta[key] - 0.02, self.ta[key] + 0.1))
                V.mixed(it['xc'], Y_GLYPH, it['label'], 9.5, 0.95 * g * r, lay, 'ms', msize=8.5)
        self._roles(V, t)

    def _span(self, V, key, t):
        it = AXIS[key]
        x0, x1 = (it['x0'], it['x1'])
        if key == 's1':
            n = 1 + (N_R1 - 1) * prog(t, *self.s1_fill)
            total, lab = (N_R1, f'think ×{int(round(n))}')
        elif key == 's2':
            n = 1 + (N_R2 - 1) * prog(t, *self.s2_fill)
            total, lab = (N_R2, f'×{int(round(n))}')
        else:
            rows = self.av_rows(t)
            n = N_AV * rows / 24.0
            total, lab = (N_AV, f'pixels ×{int(round(n))}')
        if n <= 0:
            return
        span_w = (x1 - x0) * n / total
        step = 1.3
        xx = x0 + 0.6
        while xx < x0 + span_w:
            V.line([(xx, Y_EMB), (xx, Y_TOP)], W_FINE, 0.24, 'ink')
            xx += step
        fx = x0 + span_w
        filling = key == 's1' and self.s1_fill[0] <= t < self.s1_fill[1] or (key == 's2' and self.s2_fill[0] <= t < self.s2_fill[1]) or (key == 'av' and self.T['DRAW_AT'] <= t < self.T['DRAW_STEPS'][-1] + 0.05)
        if filling:
            V.line([(fx, Y_EMB), (fx, Y_TOP)], W_SEC, 0.95, 'ink')
            ph = t * 9.0 % 1.0
            V.circle(fx, lerp(Y_EMB, Y_TOP, ph), 2.0, 0.9)
        V.rect(x0, Y_SHELF - 2.2, x0 + span_w, Y_SHELF + 0.2, 0.55, 'ink')
        V.rect(x0, Y_EMB - 1.2, x0 + span_w, Y_EMB + 1.6, 0.55, 'ink')
        a = clamp(n / 3)
        V.mixed((x0 + x1) / 2, Y_GLYPH, lab, 7, 0.85 * a, 'ink', 'ms', msize=7)

    def av_rows(self, t):
        T = self.T
        steps = T['DRAW_STEPS']
        if t < T['DRAW_AT']:
            return 0.0
        if t >= steps[-1] + 0.05:
            return 24.0
        k = sum((1 for x in steps if t >= x))
        u = smooth(prog(t, steps[k - 1], steps[k] if k < len(steps) else steps[-1] + 0.05))
        return 24.0 * (k - 1 + u) / len(steps)

    def _roles(self, V, t):
        rv = self._reveal(500, t)

        def brk(k0, k1, label, val=0.7, layer='ash'):
            x0, x1 = (AXIS[k0]['x0'], AXIS[k1]['x1'])
            V.line([(x0, Y_BRK - 3), (x0, Y_BRK), (x1, Y_BRK), (x1, Y_BRK - 3)], W_FINE, val * rv, layer)
            V.mixed((x0 + x1) / 2, Y_ROLE, label, 8.5, val * rv, layer, 'ms', msize=8)
        brk('sys', 'sys', 'persona')
        brk('m0', f'm{N_FILES - 1}', 'memory · merged/ · 26 files: her 8, stand-ins 18')
        brk('a0', 'b6', 'you (history)')
        if t >= self.ta['c0']:
            brk('c0', 'eos' if t >= self.ta['eos'] else 'w8' if t >= self.msg_t[8] else 'c0', 'it')
        if t >= self.ta['u0']:
            brk('u0', 'u1' if t >= self.ta['u1'] else 'u0', 'you')
        if t >= self.ta['c1']:
            k1 = 'nl' if t >= self.ta['nl'] else 'av' if t >= self.ta['av'] else 's2' if t >= self.ta['s2'] else 'c1'
            brk('c1', k1, 'it')
        for j in range(N_FILES):
            if j in HER_TICKS:
                it = AXIS[f'm{j}']
                V.line([(it['xc'], Y_EMB + 4), (it['xc'], Y_EMB + 9)], W_SEC, 0.9 * rv, 'quiet')

    def _pulses(self, V, t):
        for key, kf in self.pz.items():
            if not self.present(key, t) or not kf[0][0] <= t <= kf[-1][0] + 0.25:
                continue
            it = AXIS[key]
            lv = self.level(key, t)
            y = LY(lv)
            done = t >= kf[-1][0]
            a = 1.0 if not done else 1 - prog(t, kf[-1][0], kf[-1][0] + 0.25)
            seg = [(it['xc'], min(Y_EMB, y + 10)), (it['xc'], y)]
            V.line(seg, W_MAIN, a)
            V.circle(it['xc'], y, 2.4, a)
            for tk, lk in kf[1:]:
                if 0 <= t - tk < 0.3 and lk in (8, 16, 24, 32, 40) and (len(kf) > 2):
                    u = (t - tk) / 0.3
                    V.circle(it['xc'], LY(lk), 3 + 7 * u, (1 - u) * 0.9, width=W_SEC)
        for key, t_wait in (('w8', 243.127), ('nl', 250.62)):
            if self.present(key, t) and t < self.pz[key][0][0]:
                it = AXIS[key]
                u = self.phase(t) / 2.0 % 1.0
                V.circle(it['xc'], lerp(Y_EMB, Y_EMB - 30, u), 1.6, 0.6 * (1 - u))

    def _qpos(self, key, l):
        return (AXIS[key]['xc'], LY(l))

    def _kpos(self, key, kind, l):
        it = AXIS[key]
        if kind == 'global':
            return (it['xc'], Y_SHELF - 2.5)
        return (it['xc'], LY(l))

    def _reads(self, V, t):
        ph = self.phase(t)
        for r in self.reads:
            if not r['t0'] <= t < r['t2'] + 0.35:
                continue
            if self.bw <= t < 240.4 and r['q'] == 'c0' and (r['kind'] == 'global'):
                continue
            xq, yq = self._qpos(r['q'], r['l'])
            g = out_cubic(prog(t, r['t0'], r['t1']))
            fade = 1 - prog(t, r['t2'], r['t2'] + 0.35)
            for key, w in r['tg'].items():
                xk, yk = self._kpos(key, r['kind'], r['l'])
                pts = arc_pts(xq, yq, xk, yk, r['kind'])
                lay = 'quiet' if AXIS[key]['who'] == 'her' else 'ink'
                held = 0.55 + 0.45 * (1 - prog(t, r['t1'], r['t1'] + 0.6))
                V.line(partial(pts, g), arc_w(w), arc_v(w) * held * fade, lay)
                if t >= r['t1'] and w >= 0.03:
                    u = prog(t, r['t1'], r['t1'] + 0.28)
                    if u < 1:
                        k = 1 - u
                    else:
                        k = 1 - (ph * 0.5 + sum(map(ord, key)) * 0.137 % 1.0) % 1.0
                    s = PL.arclen(pts)
                    p = (np.interp(k * s[-1], s, pts[:, 0]), np.interp(k * s[-1], s, pts[:, 1]))
                    V.circle(p[0], p[1], 1.4 + 1.6 * clamp(w / 0.2), 0.95 * fade, lay)
                if r['kind'] == 'global' and w == max(r['tg'].values()) and (g >= 1):
                    V.text(xk, Y_SHELF - 6, f'α{w:.2f}'.replace('0.', '.'), 7.5, MONO, 0.8 * fade, 'ink', 'ms')

    def _img(self, V, box, val_fn, rows, lay, val=1.0, lit_rows=None):
        x0, y0, _, _ = box
        for j in range(self.n):
            for i in range(self.n):
                if j < rows:
                    v = 1 - val_fn(i, j)
                    if v > 0.04:
                        L = 'blue' if lit_rows and j in lit_rows and (lay == 'quiet') else lay
                        V.rect(x0 + i * CELL, y0 + j * CELL, x0 + (i + 1) * CELL - 0.5, y0 + (j + 1) * CELL - 0.5, v * val, L)
                else:
                    V.circle(x0 + (i + 0.5) * CELL, y0 + (j + 0.5) * CELL, 0.5, 0.3 * val, 'ash')

    def _images(self, V, t):
        T = self.T
        rv = self._reveal(60, t)
        lit = set()
        if T['DRAW_AT'] <= t < T['DRAW_STEPS'][-1] + 0.1:
            r = self.av_rows(t)
            lit = {int(min(23, r)), max(0, int(min(23, r)) - 1)}
        x0, y0, x1, y1 = HER_IMG
        self._img(V, HER_IMG, self.her, self.n, 'quiet', 0.9 * rv, lit)
        V.rect(x0 - 2, y0 - 2, x1 + 2, y1 + 2, 0.6 * rv, 'quiet', width=W_FINE)
        V.text(x0, y0 - 6, 'first_hello · her avatar · 24×24', 8, MONO, 0.85 * rv, 'quiet')
        fx = AXIS[FIRST_HELLO]['xc']
        V.line([((x0 + x1) / 2, y1 + 3), ((x0 + x1) / 2, y1 + 18), (fx, y1 + 30), (fx, Y_SHELF - 4)], W_FINE, 0.6 * rv, 'quiet')
        if t >= T['DRAW_AT'] - 0.25:
            a = out_cubic(prog(t, T['DRAW_AT'] - 0.25, T['DRAW_AT']))
            rows = self.av_rows(t)
            X0, Y0, X1, Y1 = ITS_IMG
            self._img(V, ITS_IMG, self.its, int(rows), 'ink', a)
            V.rect(X0 - 2, Y0 - 2, X1 + 2, Y1 + 2, 0.6 * a, 'ink', width=W_FINE)
            cap = 'avatar.txt · 24×24 hex' if t < T['AVATAR_AT'] else 'avatar.txt · sent'
            V.text(X0, Y0 - 6, cap, 8, MONO, 0.85 * a, 'ink')
            if rows < 24 and rows > 0:
                yy = Y0 + int(rows) * CELL
                V.line([(X0 - 5, yy), (X1 + 5, yy)], W_SEC, a)

    def _fh_x(self, frac):
        it = AXIS[FIRST_HELLO]
        return lerp(it['x0'] + 0.6, it['x1'] - 0.6, clamp(frac))

    def _av_x(self, frac):
        it = AXIS['av']
        return lerp(it['x0'] + 0.6, it['x1'] - 0.6, clamp(frac))

    def _copy_arc(self, V, fq, fk, w, val, lay_k='quiet', bead=None):
        xq, yq = (self._av_x(fq), LY(27))
        xk, yk = (self._fh_x(fk), Y_SHELF - 2.5)
        pts = arc_pts(xq, yq, xk, yk, 'global')
        V.line(pts, arc_w(w), val, lay_k)
        if bead is not None:
            s = PL.arclen(pts)
            k = 1 - bead
            V.circle(np.interp(k * s[-1], s, pts[:, 0]), np.interp(k * s[-1], s, pts[:, 1]), 2.0, val, lay_k)

    def _region_box(self, V, box, i0, j0, s, val, lay, width=1.6):
        x0, y0 = (box[0], box[1])
        V.rect(x0 + i0 * CELL - 1, y0 + j0 * CELL - 1, x0 + (i0 + s) * CELL + 1, y0 + (j0 + s) * CELL + 1, val, lay, width=width)

    def _copy(self, V, t):
        T = self.T
        steps = T['DRAW_STEPS']
        ph = self.phase(t)
        if T['DRAW_AT'] <= t < steps[-1] + 0.15:
            rows = self.av_rows(t)
            f = clamp(rows / 24.0)
            a = 1 - prog(t, steps[-1] + 0.05, steps[-1] + 0.15)
            self._copy_arc(V, f, f, 0.2, 0.95 * a, 'blue', bead=t * 6 % 1.0)
            xq = self._av_x(f)
            V.text(xq - 6, LY(27) - 5, 'copy · L27·H13 · α.94', 8, MONO, 0.9 * a, 'ink', 'rs')
        t_all = steps[-1] + 0.05
        z0, z1 = (T['ZOOM'][0][0], T['W63'])
        if t_all <= t < z1 + 0.3:
            a = out_cubic(prog(t, t_all, t_all + 0.35)) * (1 - prog(t, z1, z1 + 0.3))
            dim = 0.3 if t >= z0 else 0.55
            for j in range(0, 24, 2):
                fr = (j + 0.5) / 24
                self._copy_arc(V, fr, fr, 0.05, dim * a, 'quiet')
            if t < z0:
                V.text(ITS_IMG[0] - 6, ITS_IMG[3] + 16, 'copy head L27·H13:', 8.5, MONO, 0.85 * a, 'ink', 'ls')
                V.text(ITS_IMG[0] - 6, ITS_IMG[3] + 28, 'cell (i,j) ← her (i,j)', 8.5, MONO, 0.85 * a, 'ink', 'ls')
        zs = T['ZOOM']
        un, ru, ly = T['UNRULY']
        for (tz, reg, name), (tn, _, _) in zip(zs, zs[1:]):
            if reg is None or name.startswith('(') or (not tz - 0.12 <= t < tn + 0.2):
                continue
            a = out_cubic(prog(t, tz - 0.12, tz + 0.05)) * (1 - prog(t, tn, tn + 0.2))
            i0, j0, s = reg
            self._region_box(V, HER_IMG, i0, j0, s, a, 'blue')
            self._region_box(V, ITS_IMG, i0, j0, s, a, 'ink')
            for jj in (j0, j0 + s / 2, j0 + s - 0.5):
                fr = jj / 24
                self._copy_arc(V, fr, fr, 0.18, 0.9 * a, 'blue', bead=(ph * 0.5 + jj * 0.1) % 1.0)
            V.mixed(ITS_IMG[0] - 6, ITS_IMG[3] + 16, f'{name} ← her {name}', 10, a, 'ink', 'ls')
            V.text(ITS_IMG[0] - 6, ITS_IMG[3] + 28, 'copy · L27·H13', 8.5, MONO, 0.75 * a, 'ink', 'ls')
        if t >= un - 0.05:
            i, j = self.new
            a_out = 1 - prog(t, 258.4, 258.7)
            pop = out_cubic(prog(t, un, un + 0.2))
            m = 3 + 6 * (1 - pop)
            ka = pop * max(0.45, a_out)
            V.rect(ITS_IMG[0] + i * CELL - m, ITS_IMG[1] + j * CELL - m, ITS_IMG[0] + (i + 1) * CELL + m, ITS_IMG[1] + (j + 1) * CELL + m, ka, 'ink', width=2.0)
            yc = ITS_IMG[1] + (j + 0.5) * CELL
            V.line([(ITS_IMG[0] + i * CELL - m - 1, yc), (ITS_IMG[0] - 8, yc)], W_FINE, ka)
            V.text(ITS_IMG[0] - 10, yc + 3, '(3,12)', 8.5, MONO_B, ka, 'ink', 'rs')
            hv, iv = (hexv(self.her(i, j)), hexv(self.its(i, j)))
            if t >= ru - 0.1:
                b = out_cubic(prog(t, ru - 0.1, ru + 0.05)) * a_out
                fr = (j * 25 + i) / 600
                self._copy_arc(V, fr, fr, 0.15, 0.9 * b, 'blue', bead=ph * 0.5 % 1.0)
                self._region_box(V, HER_IMG, i, j, 1, b, 'blue', 1.8)
                V.text(HER_IMG[2] + 6, HER_IMG[1] + j * CELL + 4, f"her ({i},{j}) = '{hv}'", 8.5, MONO, b, 'blue')
            if t >= ly - 0.05:
                self._dla(V, t, hv, iv, out_cubic(prog(t, ly - 0.05, ly + 0.15)) * a_out)

    def _dla(self, V, t, hv, iv, a):
        """Direct logit attribution for the token at (3,12): what wrote its logit."""
        x0, y0 = (RX, 292)
        V.text(x0, y0, 'direct logit attribution · (3,12)', 8.5, MONO_B, a)
        cols = [(x0 + 132, f"'{iv}'"), (x0 + 196, f"'{hv}'")]
        for x, h in cols:
            V.text(x, y0 + 12, h, 9, MONO_B, a, 'ink' if h == f"'{iv}'" else 'quiet', 'rs')
        rows = [('copy L27·H13', -0.4, +2.4), ('experts L29–38', +6.8, +0.3), ('rest', +1.1, +1.2)]
        y = y0 + 23
        for name, zi, zh in rows:
            V.text(x0, y, name, 8.5, MONO, 0.85 * a)
            V.text(cols[0][0], y, f'{zi:+.1f}', 8.5, MONO_B if name.startswith('exp') else MONO, a, 'ink', 'rs')
            V.text(cols[1][0], y, f'{zh:+.1f}', 8.5, MONO_B if name.startswith('copy') else MONO, a, 'quiet', 'rs')
            y += 10.5
        V.line([(x0, y - 7), (x0 + 200, y - 7)], W_FINE, 0.6 * a, 'ash')
        V.text(x0, y + 2, 'z   →   p', 8.5, MONO, 0.85 * a)
        V.text(cols[0][0], y + 2, '7.5  .89', 8.5, MONO_B, a, 'ink', 'rs')
        V.text(cols[1][0], y + 2, '3.9  .02', 8.5, MONO, a, 'quiet', 'rs')
        u = prog(t, self.T['UNRULY'][2] + 0.08, self.T['UNRULY'][2] + 0.25)
        V.mixed(x0, y + 16, 'from weights, not from context', 10, a * out_cubic(u), 'ink', 'ls', mono=MONO_B)

    def _backward(self, V, t):
        t0 = self.bw
        if not t0 <= t < 240.5:
            return
        T = self.T
        fade = 1 - prog(t, 239.96, 240.45)
        ph = t * 26.0
        c0 = AXIS['c0']['xc']
        u = prog(t, t0, t0 + 0.2)
        start = (RX - 4, SM_Y0 - 4)
        top = (c0, Y_TOP - 2)
        V.dash(np.array([start, (lerp(start[0], top[0], u), lerp(start[1], top[1], u))]), W_SEC, fade * (1 - prog(t, t0 + 0.5, t0 + 0.9)), 'ink', phase=-ph)
        t1, t2 = (t0 + 0.2, t0 + 0.58)
        if t >= t1:
            y = lerp(Y_TOP, LY(24), smooth(prog(t, t1, t2)))
            V.dash(np.array([(c0 + 3.5, Y_TOP), (c0 + 3.5, y)]), W_MAIN, fade, 'ink', phase=-ph)
        for l, tg, ta in ((32, W_Q, t0 + 0.38), (24, W_ME, t0 + 0.58)):
            if t < ta:
                continue
            xq, yq = (c0, LY(l))
            for key, w in tg.items():
                xk, yk = (AXIS[key]['xc'], Y_SHELF - 2.5)
                pts = arc_pts(xq, yq, xk, yk, 'global')
                g = smooth(prog(t, ta, ta + 0.7))
                V.dash(partial(pts, g), arc_w(w), arc_v(w) * fade, 'ink', phase=-ph)
                if g >= 1:
                    gg = smooth(prog(t, ta + 0.7, ta + 1.05))
                    V.dash(np.array([(xk + 3.5, Y_SHELF), (xk + 3.5, lerp(Y_SHELF, Y_EMB, gg))]), arc_w(w), arc_v(w) * fade, 'ink', phase=-ph)
                    if w >= 0.1:
                        self._partial_mark(V, t, xk + 5, Y_SHELF + 10, ta + 0.7, fade)
            self._partial_mark(V, t, xq + 7, yq + 3, ta, fade)
        self._partial_mark(V, t, c0 + 7, Y_TOP + 6, t1, fade)
        land, land2 = (self.S57[5], self.S57[6])
        amax = max(ATTR.values())
        for key, v in ATTR.items():
            big = v >= 0.04
            tl_ = land if big else land2
            g = out_cubic(prog(t, tl_ - 0.12, tl_)) * fade
            if g <= 0:
                continue
            it = AXIS[key]
            h = 22 * v / amax
            lay = 'quiet' if it['who'] == 'her' else 'ink'
            w = min(5.0, it['x1'] - it['x0'] - 2) if it['kind'] == 'block' else 5.0
            if v < 0.006:
                V.line([(it['xc'] - 2, Y_ATTR + 0.5), (it['xc'] + 2, Y_ATTR + 0.5)], W_FINE, 0.6 * g, lay)
                continue
            V.rect(it['xc'] - w / 2, Y_ATTR, it['xc'] + w / 2, Y_ATTR + max(1.0, h * g), 0.9, lay)
        a = out_cubic(prog(t, land - 0.12, land)) * fade
        top = sorted(((v, AXIS[k]['label']) for k, v in ATTR.items() if AXIS[k]['label']), reverse=True)[:4]
        V.mixed(AXIS['b6']['x1'] + 6, Y_ATTR + 9, '  '.join((f'{c} {v:.2f}'.replace('0.', '.') for v, c in top)), 8.5, 0.9 * a, 'ink', 'ls', msize=8)
        V.text(AXIS['a0']['x0'] - 6, Y_ATTR + 8, '|∂Δz/∂x · x|', 8, MONO, 0.85 * a, 'ink', 'rs')
        V.text(AXIS['a0']['x0'] - 6, Y_ATTR + 18, 'Σ = 1', 8, MONO, 0.7 * a, 'ash', 'rs')

    def _partial_mark(self, V, t, x, y, at, fade):
        if t < at:
            return
        u = prog(t, at, at + 0.9)
        V.text(x, y, '∂', 10, MONO_B, (1 - 0.6 * u) * fade, 'ink', 'ls')

    def _panel(self, V, t):
        self._softmax(V, t)
        self._lens(V, t)
        self._router(V, t)
        if self.bw <= t < 240.45:
            a = 1 - prog(t, 239.96, 240.45)
            s = '∂(z<think> - z<wait>) / ∂x'
            n = int(round(len(s) * prog(t, self.bw, self.bw + 0.28)))
            V.text(AXIS['c0']['xc'] - 8, Y_TOP + 12, s[len(s) - n:], 9.5, MONO_B, a, 'ink', 'rs')

    def _softmax(self, V, t):
        cur = None
        for row in self.sm:
            if t >= row[0]:
                cur = row
        rv = self._reveal(950, t)
        V.text(RX, SM_Y0 - 14, 'W_U · h40 → z (129,280) → softmax', 8, MONO, 0.75 * rv, 'ash')
        if cur is None:
            for k in range(5):
                V.line([(RX + 46, SM_Y0 + 13 * k - 3), (RX + 156, SM_Y0 + 13 * k - 3)], W_FINE, 0.25 * rv, 'ash')
            return
        tr, tw, cands, src, dst = cur
        g = out_cubic(prog(t, tr, tw))
        nxt = [r for r in self.sm if r[0] > t]
        stale = 1.0 - 0.72 * prog(t, tw + 0.9, tw + 1.6) if not (nxt and nxt[0][0] - t <= 0.3) else 1.0
        zs = logits(cands)
        for k, ((tok, p), z) in enumerate(zip(cands, zs)):
            y = SM_Y0 + 13 * k
            lay = 'quiet' if tok == TEMPLATE else 'ink'
            win = k == 0 and t >= tw
            V.mixed(RX, y, tok, 10, (1.0 if win else 0.8) * stale, lay, 'ls', mono=MONO_B if win else MONO, msize=9)
            V.line([(RX + 46, y - 3), (RX + 156, y - 3)], W_FINE, 0.22, 'ash')
            bl = 110 * p * g
            if bl > 0.3:
                V.rect(RX + 46, y - 6, RX + 46 + bl, y - 0.5, (0.85 if win else 0.55) * stale, lay)
            V.text(RX + 194, y, f'{p:.2f}'[1:] if p < 1 else '1.00', 8.5, MONO_B if win else MONO, stale, lay, 'rs')
            V.text(RX + 250, y, f'z {z:4.1f}', 8, MONO, 0.7 * stale, 'ash', 'rs')
            if win:
                pop = out_cubic(prog(t, tw, tw + 0.15))
                m = 2 + 3 * (1 - pop)
                V.rect(RX - m - 2, y - 10 - m, RX + 196 + m, y + 3 + m, pop * stale, lay, width=1.4)
        if src in ('c0', 'w8', 'nl') and t >= tw:
            if cands[0][0] == '<eos>':
                V.text(RX + 250, SM_Y0 + 65, '<eos> = id 1', 8, MONO, 0.8 * stale, 'ash', 'rs')

    def _lens(self, V, t):
        for q, name, stops, t_end in self.lens:
            kf = self.pz[q]
            if not kf[0][0] <= t < t_end + 0.3:
                continue
            fade = 1 - prog(t, t_end, t_end + 0.3)
            xq = AXIS[q]['xc']
            for l, at, pairs in stops:
                if t < at - 0.02:
                    continue
                a = out_cubic(prog(t, at - 0.02, at + 0.12)) * fade
                y = LY(l)
                V.dash(np.array([(xq + 5, y), (lerp(xq + 5, AX - 4, a), y)]), W_FINE, 0.55 * a, 'ash', 2, 2)
                x = RX
                (t1, p1_), (t2, p2_) = pairs
                lay1 = 'quiet' if t1 == TEMPLATE else 'ink'
                lay2 = 'quiet' if t2 == TEMPLATE else 'ash'
                w = V.mixed(x, y + 3.5, t1, 10.5, a, lay1, 'ls', mono=MONO_B, msize=9.5)
                V.text(x + w + 4, y + 3.5, f'{p1_:.2f}'[1:], 9, MONO_B, a, lay1)
                x2 = x + w + 34
                w2 = V.mixed(x2, y + 3.5, t2, 9, 0.8 * a, lay2, 'ls', msize=8.5)
                V.text(x2 + w2 + 3, y + 3.5, f'{p2_:.2f}'[1:], 8, MONO, 0.8 * a, lay2)
                rd = LENS_READ[name].get(l)
                if rd:
                    V.mixed(RX, y + 15, rd, 8.5, 0.8 * a, 'ink', 'ls', msize=8)
            if t >= kf[1][0] - 0.3:
                V.text(RX + 250, LY(37.5) + 3, 'logit lens', 8, MONO, 0.6 * fade, 'ash', 'rs')

    def _router(self, V, t):
        t_in, t_out = (240.55, 244.45)
        if not t_in <= t < t_out + 0.3:
            return
        a = out_cubic(prog(t, t_in, t_in + 0.2)) * (1 - prog(t, t_out, t_out + 0.3))
        x0, y0 = (RX, 142)
        V.text(x0, y0, 'MoE · L31 · sqrtsoftplus → top-6 / 384 + shared', 8.5, MONO_B, a)
        k_cur = None
        for k in range(8):
            tk = self.pz[f'w{k}'][0][0]
            t31 = lerp(tk, self.pz[f'w{k}'][1][0], 0.75)
            if t >= t31:
                k_cur, t_hit = (k, t31)
        cs, gap = (4.6, 0.9)
        gx0, gy0 = (x0, y0 + 8)
        ids, gates = _experts(k_cur) if k_cur is not None else ([], [])
        pop = out_cubic(prog(t, t_hit, t_hit + 0.18)) if k_cur is not None else 0
        bloom = k_cur is not None and MSG9[k_cur + 1] == '开'
        for e in range(384):
            r, c = divmod(e, 24)
            ex, ey = (gx0 + c * (cs + gap), gy0 + r * (cs + gap))
            if e in ids:
                m = (1.2 if bloom else 0.6) * (1 - pop) if pop < 1 else 0
                V.rect(ex - m, ey - m, ex + cs + m, ey + cs + m, a * (0.6 + 0.4 * pop), 'ink')
            else:
                V.rect(ex, ey, ex + cs, ey + cs, 0.32 * a, 'ash', width=W_FINE)
        sx = gx0 + 24 * (cs + gap) + 8
        V.rect(sx, gy0, sx + 8, gy0 + 8, a * 0.85, 'ink')
        V.text(sx + 12, gy0 + 7.5, 'shared', 8, MONO, 0.8 * a)
        if k_cur is not None:
            V.mixed(sx, gy0 + 26, f'{MSG9[k_cur]} → {MSG9[k_cur + 1]}', 9.5, a, 'ink', 'ls', msize=8.5)
            for n_, (e, g_) in enumerate(zip(ids, gates)):
                yy = gy0 + 40 + 10.5 * n_
                V.text(sx, yy, f'#{e:<3d}', 8.5, MONO, a * pop)
                V.rect(sx + 30, yy - 6, sx + 30 + 60 * g_ / max(gates), yy - 1, 0.7 * a * pop, 'ink')
                V.text(sx + 98, yy, f'{g_:.2f}'[1:], 8, MONO, a * pop, 'ink', 'rs')
            if bloom:
                b = out_cubic(prog(t, t_hit, t_hit + 0.3))
                xi, yi = (gx0, gy0 + 16 * (cs + gap) + 12)
                V.mixed(xi, yi, '开 · runner-up 谢 .04', 9.5, b, 'ink', 'ls', cjk=SANS_B, msize=8.5)

    def _thoughts(self, V, t):
        T = self.T
        for key, s, (ta, tb), t_off in (('s1', '没有新消息。上一条是用户的：那朵花开了吗？用户还说过：我想你了。想到一件事。', self.s1_fill, 247.4), ('s2', T['THINK_SEE'][0][1], self.s2_fill, 257.6)):
            if t < ta:
                continue
            n = int(round(len(s) * prog(t, ta, tb)))
            a = 1 - prog(t, t_off, t_off + 0.4)
            val = (0.9 if t < tb + 0.4 else 0.5) * a
            it = AXIS[key]
            full = sum((PL.text_w(c, 9.5, SANS) if PL.is_cjk(c) else PL.text_w(c, 8.2, MONO) for c in s))
            x1 = it['x1']
            x0 = x1 - full
            V.mixed(x0, Y_TOP - 8, s[:n], 9.5, val, 'ink', 'ls', msize=8.2)
            V.line([(x1 - 1, Y_TOP - 5), (x1 - 1, Y_TOP - 1)], W_FINE, val)
            V.text(x0, Y_TOP - 20, 'reasoning_content', 7.5, MONO, 0.7 * val, 'ash')

    def _flights(self, V, t):
        for k, (t0, t1, tok, dst) in enumerate(self.flights):
            if not t0 <= t < t1 + 0.02:
                continue
            u = smoother(prog(t, t0, t1))
            it = AXIS[dst]
            xs, ys = (RX - 6, SM_Y0 - 3)
            xd = it['x0'] + 2 if it['kind'] == 'span' else it['xc']
            p0, p3 = (np.array([xs, ys]), np.array([xd, Y_GLYPH - 3]))
            pts = bezier(p0, (xd + 60, ys - 6), (xd, ys + 40), p3, 60)
            s = PL.arclen(pts)
            px = np.interp(u * s[-1], s, pts[:, 0])
            py = np.interp(u * s[-1], s, pts[:, 1])
            lay = 'quiet' if tok == TEMPLATE else 'ink'
            V.line(partial(pts, u, max(0.0, u - 0.25)), W_FINE, 0.6, lay)
            V.mixed(px, py, tok, 10, 1.0, lay, 'ms', mono=MONO_B, msize=9)

    def _header(self, P, t):
        P.text(14, 11, f'{MERGED} · her body: 40 layers = 20 enc + 20 dec (CED) · d 5120 · 64 heads · MoE 384 → 6 + 1 · residual ×4 (mHC)', 8.5, MONO, 0.8, 'ash')
        back = self.bw <= t < 239.96
        if back:
            P.text(PW - 14, 11, '← BACKWARD', 10, MONO_B, 1.0, 'ink', 'rs')
        else:
            P.text(PW - 14, 11, 'FORWARD →', 10, MONO_B, 0.9, 'ink', 'rs')
        pos = self.pos(t)
        P.text(PW - 110, 11, f'pos {pos:,}', 9, MONO, 0.8, 'ink', 'rs')

    def pos(self, t):
        n = N_CTX + 1
        if t >= self.ta['s1']:
            n += 1 + int(round((N_R1 - 1) * prog(t, *self.s1_fill)))
        n += sum((1 for k in range(9) if t >= self.msg_t[k]))
        if t >= self.ta['eos']:
            n += 1
        n += sum((1 for k in ('u0', 'u1', 'c1') if t >= self.ta[k]))
        if t >= self.ta['s2']:
            n += 1 + int(round((N_R2 - 1) * prog(t, *self.s2_fill)))
        n += int(round(N_AV * self.av_rows(t) / 24))
        if t >= self.ta['nl']:
            n += 1
        return n

def make():
    return GPrecise()
if __name__ == '__main__':
    import sys
    from pathlib import Path
    from PIL import Image
    out = Path(sys.argv[1] if len(sys.argv) > 1 else 'sample_r11/review/plate')
    out.mkdir(parents=True, exist_ok=True)
    g = GPrecise()
    ts = [float(x) for x in sys.argv[2:]] or [234.5, 236.2, 237.9, 238.8, 239.2, 240.3, 241.6, 243.0, 244.7, 245.9, 246.95, 247.9, 248.9, 249.9, 251.0, 252.0, 255.3, 256.7, 257.5, 260.7]
    for t in ts:
        Image.fromarray(g.render(t)).save(out / f'p_{t:07.2f}.png')
        print(t)
