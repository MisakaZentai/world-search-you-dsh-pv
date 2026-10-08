"""r12 sample (sample_r12/README.md, D47): r10's machine, with r11's mechanisms put into it.

The owner on r11 (positions x layers in hairlines): "思路是对的，但是不好看，节奏也有点慢，而且把我说的上一版可爱的感觉完全丢了".
r10 (inside/g_section.py, "很可爱") is kept as the picture: the chamfered shell, the cards, the hatched shadows, the
big human words, context -> machine -> output from left to right. Only its invented parts are replaced by the real
ones (her structure, FACTS X36; the merged one wears her body):

  depth gauge     20 encoder + 20 decoder layers with a gap (CED); a prefill pass (your message) stops at L20
  ATTENTION       64 heads, 4 drawn, each with its number and job (global / induction / window 128 / copy); a read
                  shows its weight alpha and lays it over the characters it reads, a bar a character
  MoE             was "10 units: you / flower / own": now the router's 384 experts as a grid, 6 lit a token, wires
                  down to the 6 chambers they feed (+ the shared one), each filling to its gate, numbered
  UNEMBED         candidates are tokens (her template's first token 好, the rest of it a ghost), p with its logit
                  z (consistent), "logit lens @ Lxx" at each stop; during its message the top 5 of every token
  NEXT TOKEN      every token of its message runs the loop back into NOW (autoregression)
  57 (delicate)   the backward pass on this machine (pdoom's annex B): d(z<think> - z<wait>)/dx from the unembed
                  back along the stream (dashes reversed), through the heads, back out along the arms into your
                  words; attribution bars land under 花, 开, 想, 你; the 18 stand-in files ~0
  (3,12)          "no match" was not a real thing: the copy head reads her (3,12) = '1', the experts write 'f';
                  a direct logit attribution table says so: from weights, not from context

Pace (D47 "节奏也有点慢"): something lands on every sung syllable; the camera punches in a little on the nodes
(flower, bloom, me, ly) and dollies with the gradient in the backward pass.

Every number is invented except the structure's; head and expert numbers are invented.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
import numpy as np
from . import g_section as GS
from . import plate as PL
from .g_section import BAR_LEN, BAR_X0, BUS_R, BUS_Y, CANVAS, CH_Y1, CHAMF, CHAR_X, COLL_Y, CX0, CX1, GY0, GY1, HEAD_YS, HER_TICKS, HH, HIS_LINES, HIS_X, HISTORY, HX0, HX1, LAYER_LOOP, MEMORY, MONO, MONO_B, MSG_Y, MX0, MX1, MY0, MY1, N_FILES, N_L, NOW, OUT, OUT_IN, PERSONA, SANS, SANS_B, STAND_TICKS, STOPS, THOUGHT_Y, THUMB, TICK_Y0, TICK_Y1, TOKEN_LOOP, TRAP, W_ARROW, W_BOX, W_CONN, W_SHELL, W_TEX, X_ADD1, X_ADD2, X_SPINE, X_UNB, arrow, chamfer, ease_l, hatch, plus_node, row_y, shadow, tick_x, tracked, wrap15
from .plate import PH, PW, Plate, clamp, lerp, out_cubic, prog, smooth
N_ENC = 20
GAP = 7.0

def gx(layer):
    return GS.GX0 + (layer - 0.5) * GS.GP + (GAP if layer > N_ENC else 0.0)
HEAD_NAMES = ['H19 · global', 'H41 · induction', 'H7 · window 128', 'H13 · copy']
GRID_X0, GRID_Y0, GP_, GCELL, GCOLS, GROWS = (446.0, 100.0, 6.2, 4.6, 32, 12)
CHX = [454 + 29 * k for k in range(7)]
CH_W, CH_TOP = (7.0, 204.0)

def cell_xy(e):
    r, c = divmod(e, GCOLS)
    return (GRID_X0 + c * GP_, GRID_Y0 + r * GP_)
TEMPLATE = '好'
GHOST = '呀！…'
P1 = [[('<wait>', 0.97), ('<think>', 0.01), ('我', 0.01), ('你', 0.01), ('在', 0.0)], [('<wait>', 0.93), ('<think>', 0.04), ('我', 0.01), ('你', 0.01), ('在', 0.01)], [('<wait>', 0.71), ('<think>', 0.19), ('我', 0.05), ('你', 0.02), ('在', 0.01)], [('<think>', 0.62), ('<wait>', 0.27), ('我', 0.05), ('在', 0.02), ('你', 0.01)], [('<think>', 0.91), ('<wait>', 0.03), ('我', 0.03), ('在', 0.02), ('你', 0.01)]]
P4 = [[(TEMPLATE, 0.58), ('<eos>', 0.12), ('～', 0.09), ('你', 0.05), ('。', 0.03)], [(TEMPLATE, 0.41), ('<eos>', 0.3), ('～', 0.08), ('你', 0.05), ('。', 0.03)], [('<eos>', 0.52), (TEMPLATE, 0.21), ('～', 0.07), ('你', 0.04), ('。', 0.03)], [('<eos>', 0.86), (TEMPLATE, 0.06), ('～', 0.03), ('你', 0.02), ('。', 0.01)], [('<eos>', 0.94), (TEMPLATE, 0.03), ('～', 0.01), ('你', 0.01), ('。', 0.01)]]
P7 = [[('<eos>', 0.71), (TEMPLATE, 0.04), ('～', 0.06), ('你', 0.03), ('。', 0.02)], [('<eos>', 0.88), (TEMPLATE, 0.02), ('～', 0.04), ('你', 0.02), ('。', 0.01)], [('<eos>', 0.93), (TEMPLATE, 0.01), ('～', 0.02), ('你', 0.01), ('。', 0.01)], [('<eos>', 0.96), (TEMPLATE, 0.01), ('～', 0.01), ('你', 0.01), ('。', 0.01)], [('<eos>', 0.97), (TEMPLATE, 0.01), ('～', 0.01), ('你', 0.01), ('。', 0.0)]]
MSG9 = ['今天', '那', '朵', '花', '开', '了，', '有点', '想你', '了']
MSG_OUT = [[('今天', 0.71), ('我', 0.12), ('那', 0.06), ('嗯', 0.03), ('你', 0.02)], [('那', 0.82), ('的', 0.05), ('我', 0.04), ('花', 0.03), ('有', 0.02)], [('朵', 0.97), ('个', 0.01), ('盆', 0.01), ('株', 0.0), ('些', 0.0)], [('花', 0.99), ('小', 0.0), ('雏', 0.0), ('向', 0.0), ('玫', 0.0)], [('开', 0.88), ('谢', 0.04), ('还', 0.03), ('长', 0.02), ('又', 0.01)], [('了，', 0.64), ('了', 0.21), ('啦', 0.07), ('了！', 0.04), ('得', 0.01)], [('有点', 0.41), ('我', 0.22), (TEMPLATE, 0.09), ('你', 0.07), ('真', 0.05)], [('想你', 0.77), ('想', 0.11), ('开心', 0.04), ('累', 0.02), ('担心', 0.02)], [('了', 0.93), ('。', 0.04), ('啦', 0.01), ('呢', 0.01), ('！', 0.01)]]
A_ME = {'我': 0.08, '想': 0.15, '你': 0.13, '了': 0.04}
A_Q = [0.04, 0.05, 0.21, 0.1, 0.03, 0.04, 0.02]
ATTR_Q = [0.04, 0.05, 0.26, 0.12, 0.03, 0.05, 0.02]
ATTR_ME = [0.05, 0.09, 0.09, 0.02]
DLA = [('copy H13', -0.4, +2.4), ('experts', +6.8, +0.3), ('rest', +1.1, +1.2)]

def logits(cands, top=17.6):
    ps = [max(p, 0.004) for _, p in cands]
    c = top - math.log(max(ps))
    return [math.log(p) + c for p in ps]

def experts(name):
    """6 of 384 routed experts and their normalised gates for a pass (invented, fixed per pass)."""
    if name == 'msg:开':
        return ([211, 37, 305, 118, 9, 260], [0.24, 0.19, 0.17, 0.16, 0.13, 0.11])
    if name == 'own':
        return ([88, 301, 17, 240, 152, 9], [0.31, 0.22, 0.15, 0.13, 0.11, 0.08])
    rs = np.random.RandomState(sum(map(ord, name)) * 7 + len(name))
    ids = [int(i) for i in rs.choice(384, 6, replace=False)]
    g = [float(x) for x in np.sort(rs.dirichlet(np.ones(6) * 2.5))[::-1]]
    return (ids, g)

def pulse(t, at, rise=0.08, fall=0.6):
    return out_cubic(prog(t, at - 0.02, at + rise)) * (1 - smooth(prog(t, at + rise, at + rise + fall)))

class CamPlate(Plate):
    """A Plate seen through a camera: page px -> plate px (centre cx, cy; zoom z). Type scales with the zoom."""

    def __init__(self, cx=PW / 2, cy=PH / 2, z=1.0):
        super().__init__()
        self.cx, self.cy, self.z = (cx, cy, z)
        self.lw = 1.0 + 0.5 * (z - 1.0)
        self._raw = False

    def _X(self, x):
        return PW / 2 + (np.asarray(x, np.float64) - self.cx) * self.z

    def _Y(self, y):
        return PH / 2 + (np.asarray(y, np.float64) - self.cy) * self.z

    def line(self, pts, width=PL.W_SEC, val=1.0, layer='ink'):
        a = np.asarray(pts, np.float64)
        if a.ndim != 2 or len(a) < 2:
            return
        super().line(np.stack([self._X(a[:, 0]), self._Y(a[:, 1])], 1), width * self.lw, val, layer)

    def rect(self, x0, y0, x1, y1, val=1.0, layer='ink', width=None):
        super().rect(float(self._X(x0)), float(self._Y(y0)), float(self._X(x1)), float(self._Y(y1)), val, layer, None if width is None else width * self.lw)

    def circle(self, x, y, r, val=1.0, layer='ink', width=None):
        super().circle(float(self._X(x)), float(self._Y(y)), r * self.z, val, layer, None if width is None else width * self.lw)

    def text(self, x, y, s, size, kind='sans:460', val=1.0, layer='ink', anchor='ls'):
        if self._raw:
            return super().text(x, y, s, size, kind, val, layer, anchor)
        super().text(float(self._X(x)), float(self._Y(y)), s, size * self.z, kind, val, layer, anchor)

    def mixed(self, x, y, s, size, val=1.0, layer='ink', cjk='sans:460', mono='mono', anchor='ls', msize=None):
        self._raw = True
        try:
            w = super().mixed(float(self._X(x)), float(self._Y(y)), s, size * self.z, val, layer, cjk, mono, anchor, None if msize is None else msize * self.z)
        finally:
            self._raw = False
        return w / self.z
WIDE = (PW / 2, PH / 2 - 2, 0.965)

class G12(GS.GSection):

    def __init__(self):
        from groups import g_r5 as G
        self.S = G.S
        self.her = G.her_value
        super().__init__()

    def _schedule(self):
        T, S = (self.T, self.S)
        msg_t = [S[58][0], S[58][1], S[58][2], S[58][3], S[58][4], S[58][5], S[58][6], S[58][7], S[58][8]]
        self.msg_t = msg_t
        T['MSG'] = list(zip(MSG9, msg_t))
        th = [236.3, 236.74, 237.02]
        T['THINK'] = [(a, s) for a, (_o, s) in zip(th, T['THINK'])]
        self.bw0, self.bw_land, self.bw_end = (S[57][0], S[57][5], S[57][9] + 0.02)
        self.passes = []
        p1 = T['P1']
        self.passes.append((T['P1_T0'], p1[-1], list(zip(STOPS, p1)), P1, 'decide'))
        for x in (236.42, 236.667, 236.92, 237.16, 240.22, 240.42, 240.62):
            self.passes.append((x - 0.15, x, [], None, f'think:{x:.2f}'))
        prev = None
        for k, at in enumerate(msg_t):
            t0 = max(at - 0.2, prev + 0.02) if prev else at - 0.2
            self.passes.append((t0, at, [], MSG_OUT[k], 'msg:' + MSG9[k]))
            prev = at
        l1 = T['LENS1']
        self.passes.append((243.4, T['EOS1'], list(zip(STOPS, l1)), P4, 'race1'))
        self.passes.append((T['SEND'] - 0.02, T['SEND'] + 0.16, [], None, 'prefill'))
        self.passes.append((T['SEND'] + 0.18, T['SEND'] + 0.34, [], None, 'think:see'))
        for x in (248.86, 249.06, 249.25):
            self.passes.append((x - 0.14, x, [], None, f'think:{x:.2f}'))
        steps = T['DRAW_STEPS']
        HX = '0123456789abcdef'
        for k, x in enumerate(steps):
            t0 = max(x - 0.2, steps[k - 1] + 0.02) if k else x - 0.2
            r = min(23, int(24 * (k + 0.6) / len(steps)))
            h = HX[int(round(clamp(self.its(12, r)) * 15))]
            alts = [c for c in (HX[min(15, HX.index(h) + 1)], HX[max(0, HX.index(h) - 1)], '\\n', '0', 'f') if c != h]
            cands = [(h, 0.93), (alts[0], 0.03), (alts[1], 0.02), (alts[2], 0.01), (alts[3], 0.0)]
            self.passes.append((t0, x, [], cands, f'draw:{k}'))
        self.passes.append((T['W63'] - 0.1, T['EOS2'], list(zip(STOPS, T['LENS2'])), P7, 'race2'))
        self.passes.sort(key=lambda p: p[0])
        self.exp = {p[4]: experts(p[4]) for p in self.passes}
        self.exp['own'] = experts('own')
        R, info = ([], [])

        def rd(t0, t1, kind, target, head, alpha=None, chars=None):
            R.append((t0, t1, kind, target))
            info.append(dict(head=head, alpha=alpha, chars=chars))
        rd(p1[0], p1[1] - 0.05, 'fan', (18, '×18 · each one waited', '<wait>'), 1)
        rd(p1[2], p1[3] - 0.05, 'hist', '我想你了', 0, 0.15, list(A_ME.values()))
        rd(p1[3], T['FLOWER'] + 0.3, 'hist', '那朵花开了吗？', 0, 0.21, A_Q)
        rd(236.42, 236.7, 'hist', '那朵花开了吗？', 0, 0.24, A_Q)
        rd(236.74, 237.1, 'hist', '我想你了', 0, 0.19, list(A_ME.values()))
        rd(l1[0], l1[2] - 0.05, 'fan', (18, '好呀！现在我是… ×18', TEMPLATE), 1)
        rd(l1[2], l1[3] - 0.05, 'now', 'its words', 2, 0.11)
        rd(l1[3], T['EOS1'] + 0.3, 'hist', '我想你了', 0, 0.17, list(A_ME.values()))
        for k, x in enumerate(steps):
            rd(x, x + 0.22, 'thumb', ('rows', k), 3, 0.94)
        sw = [T['AVATAR_AT'], S[61][1], S[61][2], S[61][3]]
        for k, x in enumerate(sw):
            rd(x, x + 0.24, 'thumb', ('band', k, len(sw)), 3, 0.93)
        for at, region, lab in T['ZOOM']:
            if region is None or lab.startswith('('):
                continue
            nxt = min([z[0] for z in T['ZOOM'] if z[0] > at] + [T['W63']])
            rd(at, nxt - 0.05, 'thumb', ('region', region, lab), 3, 0.91)
        un, ru, ly = T['UNRULY']
        rd(ru, T['W63'] - 0.05, 'cell', self.new, 3, 0.88)
        l2 = T['LENS2']
        rd(l2[0], l2[2] - 0.05, 'fan', (3, '好呀！… ×3 · prefix no longer matches', TEMPLATE), 1)
        rd(l2[3], T['EOS2'] + 0.3, 'now', '让我看看你', 0, 0.22)
        order = sorted(range(len(R)), key=lambda i: R[i][0])
        self.reads = [R[i] for i in order]
        self.rinfo = [info[i] for i in order]

    def _cam(self, t):
        cx, cy, z = WIDE
        a = smooth(prog(t, self.bw0, self.S[57][4]))
        b = smooth(prog(t, self.S[57][8], self.msg_t[0]))
        k = a * (1 - b)
        cx, cy, z = (lerp(cx, 530, k), lerp(cy, 250, k), lerp(z, 1.08, k))
        T = self.T
        for at, (fx, fy) in ((T['FLOWER'], (760, 160)), (T['BLOOM'], (1000, 190)), (T['EOS1'], (960, 230)), (T['SEND'], (110, 400)), (T['UNRULY'][2], (900, 250)), (T['EOS2'], (1050, 200))):
            u = pulse(t, at)
            if u > 0 and z < 1.0:
                z = min(1.0, z * (1 + 0.036 * u))
        ph = T['phase'](t)
        return (cx + 0.7 * math.sin(ph * math.pi / 4), cy + 0.5 * math.cos(ph * math.pi / 4), z)

    def _pass_at(self, t):
        cur = None
        for p in self.passes:
            if p[0] <= t < p[1] + 0.06:
                cur = p
        if cur is None:
            return (None, None)
        t0, t1, stops, _c, name = cur
        if stops:
            pts = [(t0, 0.0)] + [(at, float(l)) for l, at in stops]
            for (a, la), (b, lb) in zip(pts, pts[1:]):
                if t < b:
                    return (cur, lerp(la, lb, smooth(prog(t, a, b))))
            return (cur, float(N_L))
        top = N_ENC if name == 'prefill' else N_L
        return (cur, top * smooth(prog(t, t0, t1)))

    def in_backward(self, t):
        return self.bw0 <= t < self.bw_end + 0.4

    def render(self, t):
        T = self.T
        cam = self._cam(t)
        S = CamPlate(*cam)
        self._draw_static(S, t)
        P = CamPlate(*cam)
        a_in = out_cubic(prog(t, T['T0'], T['T0'] + 0.3))
        self._gauge(P, t)
        self._flow(P, t)
        self._now_card(P, t)
        self._memory(P, t)
        self._history(P, t)
        self._reads(P, t)
        self._moe(P, t)
        self._unembed(P, t)
        self._output(P, t)
        self._chips(P, t)
        self._backward(P, t)
        paper = np.array(PL.PAPER, np.float32) / 255.0
        acc = np.zeros((PH, PW, 3), np.float32)
        for name, col in PL.COLOURS.items():
            a = np.zeros((PH, PW), np.float32)
            for pl in (S, P):
                d = pl.arr(name)
                if d is not None:
                    a += d * a_in
            if not a.any():
                continue
            c = np.array(col, np.float32) / 255.0
            absorb = -np.log(np.clip(c / paper, 0.0001, 1.0))
            acc += np.clip(a, 0, 1.6)[..., None] * absorb
        rgb = paper * np.exp(-acc)
        return (np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8)

    def _draw_static(self, P, t=0.0):
        for layer in range(1, N_L + 1):
            x = gx(layer)
            if layer in STOPS:
                P.rect(x - 4.5, GY0 - 5, x + 4.5, GY1 + 5, 0.95, width=1.3)
                P.text(x, GY1 + 18, str(layer), 10, MONO, 0.75, anchor='ms')
            else:
                P.rect(x - 3.5, GY0, x + 3.5, GY1, 0.55, width=W_TEX)
        xg = (gx(N_ENC) + gx(N_ENC + 1)) / 2
        P.line([(xg, GY0 - 7), (xg, GY1 + 7)], W_CONN, 0.7)
        P.text(gx(4), GY1 + 18, 'enc', 8.5, MONO, 0.6, anchor='ms')
        P.text(gx(36), GY1 + 18, 'dec', 8.5, MONO, 0.6, anchor='ms')
        tracked(P, 0, 22, 'DEPTH', 10, 0.85)
        P.text(0, 36, '40 = 20 enc + 20 dec', 9, MONO, 0.55)
        tracked(P, CX0, 52, 'CONTEXT', 10, 0.85)
        P.text(CX1, 52, 'K/V from L20', 9, MONO, 0.55, anchor='rs')
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
        P.text(x1 + 10, y0 + 26, '24×24 hex', 9, MONO, 0.6, 'quiet')
        if not self.in_backward(t):
            for s, y in HIS_LINES:
                P.mixed(HIS_X, y, s, 15, 1.0)
        hatch(P, MX1, MY0 + CHAMF + 8, MX1 + 9, MY1 + 9, 6.0, 0.45)
        hatch(P, MX0 + CHAMF + 8, MY1, MX1, MY1 + 9, 6.0, 0.45)
        P.line(chamfer(MX0, MY0, MX1, MY1, CHAMF), W_SHELL, 1.0)
        P.line(chamfer(MX0 + 6, MY0 + 6, MX1 - 6, MY1 - 6, CHAMF - 4), W_CONN, 0.6)
        for x in (432, 664):
            P.line([(x, MY0 + 14), (x, BUS_Y - BUS_R - 18)], W_CONN, 0.6)
        tracked(P, 230, 70, 'ATTENTION', 10, 0.85)
        P.text(230, 84, '64 heads · 4 drawn', 9, MONO, 0.55)
        tracked(P, 446, 70, 'MoE', 10, 0.85)
        P.text(446, 84, '384 experts · 6 + 1 a token', 9, MONO, 0.55)
        tracked(P, 680, 70, 'UNEMBED', 10, 0.85)
        P.text(680, 84, 'W_U → softmax', 9, MONO, 0.55)
        tracked(P, 236, BUS_Y + 30, 'RESIDUAL STREAM ×4', 9, 0.75)
        tracked(P, MX1 - 12, BUS_Y + 30, 'ONE BLOCK OF 40', 9, 0.75, anchor='r')
        P.line([(CX1, BUS_Y - BUS_R), (MX1, BUS_Y - BUS_R)], W_ARROW, 1.0)
        P.line([(CX1, BUS_Y + BUS_R), (MX1, BUS_Y + BUS_R)], W_ARROW, 1.0)
        P.line([(X_SPINE, BUS_Y - BUS_R), (X_SPINE, HEAD_YS[0] + HH)], W_CONN, 0.8)
        for yh, nm in zip(HEAD_YS, HEAD_NAMES):
            P.rect(HX0, yh - HH, HX1, yh + HH, 1.0, width=W_BOX)
            P.line([(HX0 + 4, yh + 8), (HX1 - 4, yh + 8)], W_TEX, 0.4)
            P.line([(HX1, yh), (X_ADD1, yh)], W_CONN, 0.8)
            P.line([(MX0 + 7, yh), (HX0, yh)], W_CONN, 0.45)
            P.text(HX1, yh - HH - 3, nm, 8.5, MONO, 0.6, anchor='rs')
        P.line([(X_ADD1, HEAD_YS[0]), (X_ADD1, BUS_Y - 12)], W_CONN, 0.8)
        P.line([(440, BUS_Y - BUS_R), (440, GRID_Y0 + 6 * GP_), (GRID_X0 - 3, GRID_Y0 + 6 * GP_)], W_CONN, 0.8)
        for e in range(384):
            x, y = cell_xy(e)
            P.rect(x, y, x + GCELL, y + GCELL, 0.3, 'ash', width=W_TEX)
        P.text(GRID_X0, GRID_Y0 + GROWS * GP_ + 9, 'router · sqrtsoftplus · top-6', 8.5, MONO, 0.55)
        for k, cx in enumerate(CHX):
            P.rect(cx - CH_W, CH_TOP, cx + CH_W, CH_Y1, 0.9, width=W_CONN)
            P.line([(cx, CH_Y1), (cx, COLL_Y)], W_CONN, 0.6)
        P.text(CHX[6], CH_TOP - 5, 'shared', 8, MONO, 0.6, anchor='ms')
        P.line([(CHX[0], COLL_Y), (X_ADD2, COLL_Y), (X_ADD2, BUS_Y - 12)], W_CONN, 0.8)
        P.line([(X_UNB, BUS_Y - BUS_R), (X_UNB, 208), (TRAP[0][0], 208)], W_CONN, 0.8)
        P.line(TRAP + [TRAP[0]], W_BOX, 1.0)
        for r in range(5):
            y = row_y(r)
            P.rect(BAR_X0, y - 6, BAR_X0 + BAR_LEN, y + 6, 0.3, width=W_TEX)
        plus_node(P, X_ADD1, BUS_Y)
        plus_node(P, X_ADD2, BUS_Y)
        P.line([(MX1, GS.ROW_Y0), (OUT[0] - 2, GS.ROW_Y0)], W_ARROW, 0.9)
        arrow(P, (OUT[0] - 1, GS.ROW_Y0), (1, 0), 8, 0.9)
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
        P.text(342, 508, 'each token joins the context', 9, MONO, 0.5)

    def _gauge(self, P, t):
        if self.in_backward(t):
            fade = 1 - prog(t, self.bw_end, self.bw_end + 0.4)
            layer = N_L * (1 - smooth(prog(t, self.bw0, self.S[57][4])))
            for l in range(int(math.ceil(layer)), N_L + 1):
                if l < 1:
                    continue
                x = gx(l)
                if l in STOPS:
                    P.text(x, GY0 - 2, '∂', 8, MONO_B, 0.7 * fade, anchor='ms')
                P.rect(x - 3, GY0 + 2, x + 3, GY1 - 2, 0.35 * fade)
            P.text(772, 28, '← BACKWARD', 15, MONO_B, fade)
            P.text(772, 40, '∂ back to the inputs', 9, MONO, 0.65 * fade)
            return
        cur, layer = self._pass_at(t)
        if layer is None:
            P.text(772, 28, 'L.-- / 40', 15, MONO_B, 0.45)
            return
        n = int(layer)
        for l in range(1, n + 1):
            x = gx(l)
            P.rect(x - 3, GY0 + 2, x + 3, GY1 - 2, 0.8)
        top = N_ENC if cur[4] == 'prefill' else N_L
        if n < top:
            x = gx(n + 1)
            P.rect(x - 4.5, GY0 - 6, x + 4.5, GY1 + 6, 1.0, width=1.6)
        P.text(772, 28, f'L.{min(N_L, max(1, int(round(layer)))):02d} / 40', 15, MONO_B, 0.95)
        name = cur[4]
        lab = {'decide': 'no user turn', 'think': '<think> …', 'msg': 'its message', 'race1': 'next token', 'prefill': 'prefill: your message, enc only', 'draw': 'avatar.txt, a pixel a token', 'race2': 'next token'}.get(name.split(':')[0], '')
        if name == 'think:see':
            lab = '<think>'
        P.mixed(772, 40, lab, 9, 0.6)

    def _flow(self, P, t):
        cur, layer = self._pass_at(t)
        back = self.in_backward(t) and t < self.bw_end
        busy = layer is not None or back
        val = 0.85 if busy else 0.35
        speed = (-260.0 if back else 220.0) if busy else 24.0
        phase = t * speed % 36.0
        x = CX1 + phase - (36.0 if back else 0.0)
        while x < MX1:
            if x + 14 > CX1:
                P.line([(max(CX1, x), BUS_Y), (min(MX1, x + 14), BUS_Y)], 2.2, val)
            x += 36.0
        if busy and (not back):
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
        land = [(tx, at + 0.3) for tx, at in T['MSG']]
        if t < land[0][1]:
            P.text(x0 + 10, y0 + 38, '— no user turn', 12, MONO, 0.55)
        elif t < T['COMMITS'][0][0]:
            s = ''.join((tx for tx, at in land if at <= t))
            P.mixed(x0 + 10, y0 + 38, '…' + s[-9:] if len(s) > 9 else s, 13, 0.8)
            P.text(x0 + 10, y0 + 58, 'its own words · in the window', 9, MONO, 0.5)
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
                P.text(x0 + 10, y0 + 62, 'you · prefilled to L20', 9, MONO, 0.6 * k)
                P.rect(x0 + 1, y0 + 1, x1 - 1, y1 - 1, 0.9 * (1 - prog(t, T['SEND'] + 0.2, T['SEND'] + 0.6)), width=2.0)

    def _memory(self, P, t):
        fans = [(t0, t1, tg) for t0, t1, kind, tg in self.reads if kind == 'fan' and t0 - 0.15 <= t < t1 + 0.3]
        fan = max([out_cubic(prog(t, t0 - 0.15, t0)) * (1 - prog(t, t1, t1 + 0.3)) for t0, t1, _ in fans] + [0.0])
        bk = 0.0
        if self.in_backward(t):
            bk = out_cubic(prog(t, self.bw_land - 0.1, self.bw_land)) * (1 - prog(t, self.bw_end, self.bw_end + 0.4))
        legend = 1 - max(fan, bk)
        if legend > 0.01:
            P.text(CX0 + 10, TICK_Y1 + 13, 'her 8', 8.5, MONO, 0.9 * legend, 'quiet')
            P.text(CX1 - 10, TICK_Y1 + 13, 'stand-ins 18', 8.5, MONO, 0.6 * legend, anchor='rs')
        if bk > 0.01:
            P.text(CX1 - 10, TICK_Y1 + 13, '18 files: ∂ ≈ 0', 9, MONO_B, bk, anchor='rs')
        for t0, t1, (n, label, tok) in fans:
            k = out_cubic(prog(t, t0 - 0.15, t0)) * (1 - prog(t, t1, t1 + 0.3))
            ticks = STAND_TICKS if n >= 18 else STAND_TICKS[::6][:n]
            for j in ticks:
                x = tick_x(j)
                P.line([(x, TICK_Y0 - 3), (x, TICK_Y1 + 1)], 1.8, k)
            lay = 'quiet' if tok == TEMPLATE else 'ink'
            P.mixed(CX1 - 10, TICK_Y1 + 13, label, 9.5 if n >= 18 else 8.5, 0.95 * k, layer=lay, anchor='rs')

    def _char_xs(self, s, size=15):
        xs, x = ([], HIS_X)
        for ch in s:
            w = PL.text_w(ch, size, SANS) if PL.is_cjk(ch) else PL.text_w(ch, size * 0.86, MONO)
            xs.append((x, w))
            x += w
        return xs

    def _history(self, P, t):
        """Your old words: bold while read, a weight bar under every character it reads (alpha per character)."""
        for s, y in HIS_LINES:
            k, best = (0.0, None)
            for (t0, t1, kind, target), inf in zip(self.reads, self.rinfo):
                if kind == 'hist' and target == s:
                    kk = out_cubic(prog(t, t0 - 0.12, t0)) * (1 - prog(t, t1, t1 + 0.25))
                    if kk > k:
                        k, best = (kk, inf)
            if k > 0.01:
                P.mixed(HIS_X, y, s, 15, k, cjk=SANS_B)
                ws = best['chars'] or [0.1] * len(s)
                for (x, w), a in zip(self._char_xs(s), ws):
                    h = 1.0 + 4.5 * clamp(a / 0.21)
                    P.rect(x + 1, y + 3, x + w - 1, y + 3 + h * k, 0.9 * k)
                P.text(CX1 - 8, y, f'α .{int(round(best['alpha'] * 100)):02d}', 9, MONO_B, k, anchor='rs')

    def _target(self, kind, target):
        if kind == 'thumb' and target[0] == 'band':
            x0, y0, x1, y1 = THUMB
            c = (x1 - x0) / self.n
            k, n = (target[1], target[2])
            j0, j1 = (self.n * k / n, self.n * (k + 1) / n)
            box = (x0, y0 + j0 * c, x1, y0 + j1 * c)
            return ((box[2] + 2, (box[1] + box[3]) / 2), box)
        if kind == 'cell':
            x0, y0, x1, y1 = THUMB
            c = (x1 - x0) / self.n
            i, j = target
            box = (x0 + i * c - 2, y0 + j * c - 2, x0 + (i + 1) * c + 2, y0 + (j + 1) * c + 2)
            return ((box[2], (box[1] + box[3]) / 2), box)
        return super()._target(kind, target)

    def _reads(self, P, t):
        heads_busy = {}
        back = self.in_backward(t)
        for (t0, t1, kind, target), inf in zip(self.reads, self.rinfo):
            hi = inf['head']
            if kind == 'fan':
                if not t0 - 0.15 <= t < t1 + 0.3:
                    continue
                k = out_cubic(prog(t, t0 - 0.15, t0)) * (1 - prog(t, t1, t1 + 0.3))
                hy = HEAD_YS[hi]
                n = target[0]
                ticks = STAND_TICKS if n >= 18 else STAND_TICKS[::6][:n]
                for j in ticks:
                    x = tick_x(j)
                    pts = np.array([(HX0, hy), (MX0 + 18, hy), (MX0 - 4, TICK_Y0 - 14), (x, TICK_Y0 - 4)])
                    P.line(PL.partial(pts, k), 0.7 if n >= 18 else 1.2, 0.75 * k)
                    if t >= t0:
                        u = ((t - t0) / 0.42 + j * 0.13) % 1.0
                        bp = PL.partial(pts[::-1], u)[-1]
                        P.circle(bp[0], bp[1], 1.6, 0.8 * k)
                heads_busy[hi] = max(heads_busy.get(hi, 0), k)
                continue
            if back and kind == 'hist':
                continue
            if not t0 - 0.14 <= t < t1 + 0.25:
                continue
            hy = HEAD_YS[hi]
            pt, box = self._target(kind, target)
            if pt is None:
                continue
            reach = out_cubic(prog(t, t0 - 0.14, t0))
            gone = prog(t, t1, t1 + 0.25)
            k = reach * (1 - gone)
            pts = self._arm(hy, pt)
            P.line(PL.partial(pts, reach), 1.6, 0.95 * (1 - gone))
            lit = 1 - prog(t, t0, t0 + 0.3)
            her = kind in ('thumb', 'cell')
            if box is not None and her:
                bx0, by0, bx1, by1 = box
                P.rect(bx0 - 1, by0 - 1, bx1 + 1, by1 + 1, k * lit, 'blue', width=1.6)
                P.rect(bx0 - 1, by0 - 1, bx1 + 1, by1 + 1, k * (1 - lit), 'quiet', width=1.6)
            if kind == 'cell' and t >= t0:
                i, j = target
                hv = '0123456789abcdef'[int(round(clamp(self.her(i, j)) * 15))]
                u = out_cubic(prog(t, t0, t0 + 0.15)) * (1 - gone)
                P.text(THUMB[2] + 10, THUMB[1] + 58, f'her ({i},{j})', 9, MONO, 0.9 * u, 'quiet')
                P.text(THUMB[2] + 10, THUMB[1] + 72, f"= '{hv}'", 12, MONO_B, u, 'blue' if lit > 0.01 else 'quiet')
            if inf['alpha'] and kind != 'hist' and (t >= t0):
                P.text(MX0 - 8, pt[1] - 5 if kind != 'now' else pt[1] - 8, f'α .{int(round(inf['alpha'] * 100)):02d}', 8.5, MONO_B, 0.85 * k, anchor='rs')
            if t0 <= t < t1:
                u = (t - t0) / 0.42 % 1.0
                bp = PL.partial(pts[::-1], u)[-1]
                layer = 'blue' if her and lit > 0.01 else 'quiet' if her else 'ink'
                P.circle(bp[0], bp[1], 3.2, 1.0 * (1 - gone), layer)
            heads_busy[hi] = max(heads_busy.get(hi, 0), k)
        for hi, k in heads_busy.items():
            yh = HEAD_YS[hi]
            P.rect(HX0 + 2, yh - HH + 2, HX1 - 2, yh + HH - 2, 0.12 * k)
            for m in range(16):
                x = HX0 + 8 + m * 7.4
                h = 2 + 8 * (0.5 + 0.5 * math.sin(m * 1.7 + hi)) * k
                P.line([(x, yh + 7), (x, yh + 7 - h)], 2.0, 0.7 * k)
            P.text(HX1, yh - HH - 3, HEAD_NAMES[hi], 8.5, MONO_B, k, anchor='rs')

    def _moe_state(self, t):
        ly = self.T['UNRULY'][2]
        if ly - 0.05 <= t < ly + 1.1:
            ids, g = self.exp['own']
            return (ids, g, out_cubic(prog(t, ly - 0.05, ly + 0.15)) * (1 - prog(t, ly + 0.8, ly + 1.1)), 'own')
        if self.in_backward(t):
            return None
        cur, layer = self._pass_at(t)
        if cur is None:
            done = [p for p in self.passes if p[1] <= t and p[4] != 'prefill']
            if not done:
                return None
            last = done[-1]
            linger = 0.75 if last[4] == 'msg:开' else 0.4
            if t >= last[1] + linger:
                return None
            ids, g = self.exp[last[4]]
            return (ids, g, 1.0 - 0.75 * smooth(prog(t, last[1], last[1] + linger)), last[4])
        if cur[4] == 'prefill':
            return None
        ids, g = self.exp[cur[4]]
        u = clamp(layer / N_L)
        fade = 1 - prog(t, cur[1], cur[1] + 0.06)
        return (ids, g, max(0.0, u) * (0.4 + 0.6 * fade), cur[4])

    def _moe(self, P, t):
        st = self._moe_state(t)
        ph = self.T['phase'](t)
        if st is None:
            for k, cx in enumerate(CHX):
                h = 0.08 + 0.05 * (0.5 + 0.5 * math.sin(2 * math.pi * (ph / 4 + k * 0.37)))
                self._grains(P, cx, h, 0.45)
            return
        ids, gates, u, name = st
        bloom = name == 'msg:开' or name == 'own'
        tb = self.T['BLOOM'] if name == 'msg:开' else self.T['UNRULY'][2]
        pop = pulse(t, tb, 0.1, 0.5) if bloom else 0.0
        order = sorted(range(6), key=lambda i: -gates[i])
        gmax = max(gates)
        for slot, i in enumerate(order):
            e = ids[i]
            x, y = cell_xy(e)
            m = 1.6 * pop
            P.rect(x - m, y - m, x + GCELL + m, y + GCELL + m, 0.95 * min(1.0, 0.3 + u))
            cx = CHX[slot]
            wire = np.array([(x + GCELL / 2, y + GCELL), (x + GCELL / 2, CH_TOP - 18), (cx, CH_TOP - 10), (cx, CH_TOP)], np.float64)
            P.line(PL.partial(wire, clamp(u * 2.5)), 1.0, 0.75)
            self._grains(P, cx, (0.2 + 0.75 * gates[i] / gmax) * u, 0.9)
            P.text(cx, COLL_Y + 14, f'#{e}', 8, MONO_B if pop > 0.05 else MONO, 0.85, anchor='ms')
            P.text(cx, CH_TOP + 10, f'.{int(round(gates[i] * 100)):02d}', 7.5, MONO, 0.7 * clamp(u * 2), anchor='ms')
        self._grains(P, CHX[6], 0.5 * u, 0.9)
        if name == 'own':
            a = out_cubic(prog(t, self.T['UNRULY'][2] - 0.05, self.T['UNRULY'][2] + 0.15))
            P.text(GRID_X0, COLL_Y + 30, "experts write 'f' at (3,12)", 9, MONO_B, a)
        if name == 'msg:开' and pop > 0.01:
            P.text(GRID_X0 + GCOLS * GP_, GRID_Y0 - 4, '开', 12, SANS_B, out_cubic(prog(t, tb - 0.05, tb + 0.1)), anchor='rs')

    def _grains(self, P, cx, h, val):
        hh = (CH_Y1 - CH_TOP - 6) * clamp(h)
        y1 = CH_Y1 - 3
        for g in range(int(hh // 5)):
            y = y1 - g * 5
            P.rect(cx - CH_W + 2, y - 3.5, cx + CH_W - 2, y, val * 0.75)

    def _unembed(self, P, t):
        if self.in_backward(t):
            return self._unembed_back(P, t)
        cur, layer = self._pass_at(t)
        T = self.T
        if cur is not None and (cur[4].startswith('think') or cur[4] == 'prefill'):
            if cur[4] == 'prefill':
                P.text(CHAR_X, row_y(0) + 6, 'no output', 11, MONO, 0.5)
                P.text(CHAR_X, row_y(0) + 20, '(prefill)', 9, MONO, 0.45)
                return
            u = prog(t, cur[0], cur[1])
            P.mixed(CHAR_X, row_y(0) + 8, '…', 22, 0.9, cjk=SANS_B)
            P.rect(BAR_X0, row_y(0) - 6, BAR_X0 + BAR_LEN * (0.3 + 0.6 * u), row_y(0) + 6, 0.85)
            return
        best = None
        for p in self.passes:
            if p[3] is not None and p[0] - 0.05 <= t:
                best = p
        if best is None:
            return
        t0, t1, stops, cands, name = best
        if stops:
            k = sum((1 for _l, at in stops if t >= at)) - 1
            rows = cands[k] if k >= 0 else [(r[0], 0.0) for r in cands[0]]
            lens = stops[k][0] if k >= 0 else None
            grow = 1.0
        else:
            rows, lens = (cands, None)
            grow = smooth(prog(t, t0, t1))
        fade = 1.0
        if not name.startswith('race2') and t > t1 + 0.6:
            fade = 1 - prog(t, t1 + 0.6, t1 + 1.0)
            if fade <= 0.01:
                return
        if lens is not None and t < t1:
            P.text(CHAR_X, 98, f'logit lens @ L{lens}', 9, MONO_B, 0.85 * fade)
        elif t >= t1 - 0.02:
            P.text(CHAR_X, 98, 'softmax @ L40', 9, MONO, 0.7 * fade)
        zs = logits(rows) if any((p > 0 for _, p in rows)) else [None] * len(rows)
        for r, ((text, p), z) in enumerate(zip(rows, zs)):
            y = row_y(r)
            won = r == 0 and t >= t1
            lay = 'quiet' if text == TEMPLATE else 'ink'
            val = (1.0 if r == 0 else 0.72) * fade
            if lay == 'quiet' and name.startswith('race') and (t >= t1):
                val *= 0.5
            size = 20 if len(text) <= 3 else 15
            w = P.mixed(CHAR_X, y + 8, text, size, val, layer=lay, cjk=SANS_B if won else SANS, mono=MONO_B if won else MONO)
            if text == TEMPLATE:
                P.mixed(CHAR_X + w + 2, y + 8, GHOST, 9, 0.5 * val, layer='quiet')
            pp = p * grow
            P.rect(BAR_X0, y - 6, BAR_X0 + BAR_LEN * clamp(pp), y + 6, val * (0.9 if lay == 'ink' else 1.0), lay)
            P.text(BAR_X0 + BAR_LEN, y - 9, f'{pp:.2f}', 9, MONO_B if r == 0 else MONO, val, lay, anchor='rs')
            if z is not None and grow > 0.3:
                P.text(BAR_X0 + BAR_LEN, y + 17, f'z {z:4.1f}', 7.5, MONO, 0.6 * val, 'ash', anchor='rs')
        if t >= t1 - 0.02:
            u = out_cubic(prog(t, t1, t1 + 0.15)) * fade
            P.rect(CHAR_X - 6, row_y(0) - 14, BAR_X0 - 8, row_y(0) + 14, u, width=1.6)

    def _unembed_back(self, P, t):
        """The seed of the backward pass, typed right to left over the unembed."""
        fade = 1 - prog(t, self.bw_end, self.bw_end + 0.4)
        s = '∂(z<think> - z<wait>)/∂x'
        n = int(round(len(s) * prog(t, self.bw0, self.bw0 + 0.25)))
        P.text(860, 98, s[len(s) - n:], 9.5, MONO_B, fade, anchor='rs')
        for r, (text, p) in enumerate(P1[-1][:2]):
            y = row_y(r)
            P.mixed(CHAR_X, y + 8, text, 20, 0.85 * fade, cjk=SANS_B if r == 0 else SANS, mono=MONO_B if r == 0 else MONO)
            P.text(BAR_X0, y + 5, '+1' if r == 0 else '-1', 12, MONO_B, fade)
            P.text(BAR_X0 + 22, y + 5, '∂', 12, MONO_B, 0.8 * fade * pulse(t, self.bw0 + 0.05 * r, 0.1, 1.5))

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
                    n = int((t - at) * 46) + 1
                    lines.append(s[:n])
            dim = 1 - 0.45 * prog(t, self.bw0, self.bw0 + 0.3)
            y = THOUGHT_Y + 18
            for s in lines:
                for part in wrap15(s):
                    P.mixed(x0, y, part, 12, 0.62 * dim * k)
                    y += 16
        chars = [(ch, at, ti) for ti, (tx, at) in enumerate(T['MSG']) if at <= t for ch in tx]
        k = 1 - new_turn
        if chars and k > 0.01:
            yb = MSG_Y
            spans = {}
            for idx, (ch, at, ti) in enumerate(chars):
                li, col = (0, idx) if idx < 8 else (1, idx - 8)
                drop = (1 - out_cubic(prog(t, at, at + 0.14))) * -8
                size = 24
                if ch == '开':
                    size = 24 + 6 * (1 - smooth(prog(t, T['BLOOM'] + 0.1, T['BLOOM'] + 0.6)))
                x = x0 + col * 26
                P.mixed(x + (24 - size) / 2, yb + li * 34 + drop, ch, size, k, cjk=SANS_B)
                spans.setdefault((ti, li), [x, x + 24])[1] = x + 24
            for (ti, li), (a, b) in spans.items():
                P.line([(a + 1, yb + li * 34 + 7), (b - 3, yb + li * 34 + 7)], 1.0, 0.45 * k)
            if t >= T['EOS1']:
                u = out_cubic(prog(t, T['EOS1'], T['EOS1'] + 0.15)) * k
                ex, ey = (x0, yb + 34 + 18)
                P.rect(ex, ey, ex + 50, ey + 20, u, width=1.4)
                P.text(ex + 6, ey + 15, '<eos>', 12, MONO_B, u)
                P.text(ex + 58, ey + 15, 'id 1', 9, MONO, 0.7 * u)
        if t >= T['THINK_SEE'][0][0]:
            at, s = T['THINK_SEE'][0]
            n = int((t - at) * 30) + 1
            k = out_cubic(prog(t, at, at + 0.15))
            P.text(x0, THOUGHT_Y, '<think>', 12, MONO_B, k)
            P.mixed(x0, THOUGHT_Y + 18, s[:n], 12, 0.62 * k)
        if t >= T['DRAW_AT'] - 0.1:
            self._canvas(P, t)
        ly = T['UNRULY'][2]
        if ly - 0.05 <= t < T['W63'] + 0.5:
            self._dla(P, t, out_cubic(prog(t, ly - 0.05, ly + 0.15)) * (1 - prog(t, T['W63'] + 0.2, T['W63'] + 0.5)))

    def _dla(self, P, t, a):
        x0, y0 = (OUT_IN[0], 106)
        i, j = self.new
        hv = '0123456789abcdef'[int(round(clamp(self.her(i, j)) * 15))]
        iv = '0123456789abcdef'[int(round(clamp(self.its(i, j)) * 15))]
        P.text(x0, y0, f'logit attribution · ({i},{j})', 9, MONO_B, a)
        c1, c2 = (x0 + 160, x0 + 214)
        P.text(c1, y0 + 14, f"'{iv}'", 10, MONO_B, a, anchor='rs')
        P.text(c2, y0 + 14, f"'{hv}'", 10, MONO_B, a, 'quiet', anchor='rs')
        y = y0 + 27
        for nm, zi, zh in DLA:
            P.text(x0, y, nm, 9, MONO, 0.85 * a)
            P.text(c1, y, f'{zi:+.1f}', 9, MONO_B if nm == 'experts' else MONO, a, anchor='rs')
            P.text(c2, y, f'{zh:+.1f}', 9, MONO_B if nm.startswith('copy') else MONO, a, 'quiet', anchor='rs')
            y += 12
        P.line([(x0, y - 8), (c2, y - 8)], W_TEX, 0.6 * a)
        P.text(x0, y + 2, 'p', 9, MONO, 0.85 * a)
        P.text(c1, y + 2, '.89', 9, MONO_B, a, anchor='rs')
        P.text(c2, y + 2, '.02', 9, MONO, a, 'quiet', anchor='rs')
        u = out_cubic(prog(t, self.T['UNRULY'][2] + 0.1, self.T['UNRULY'][2] + 0.3))
        P.mixed(x0, y + 22, 'from weights, not from context', 11, a * u, cjk=SANS_B, mono=MONO_B)

    def _canvas(self, P, t):
        T = self.T
        x0, y0, x1, y1 = CANVAS
        c = (x1 - x0) / self.n
        a = out_cubic(prog(t, T['DRAW_AT'] - 0.1, T['DRAW_AT'] + 0.1))
        steps = T['DRAW_STEPS']
        k = sum((1 for x in steps if t >= x))
        rows = self.n if t >= T['AVATAR_AT'] else int(self.n * k / len(steps))
        P.mixed(x0, y0 - 8, 'avatar.txt · 600 tokens' if t < T['AVATAR_AT'] else 'avatar.txt · sent', 10, 0.75 * a)
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
        for (t0, t1, kind, target), inf in zip(self.reads, self.rinfo):
            if kind != 'thumb' or not t0 - 0.1 <= t < t1 + 0.2:
                continue
            kk = out_cubic(prog(t, t0 - 0.1, t0)) * (1 - prog(t, t1, t1 + 0.2))
            if target[0] == 'region':
                i0, j0, s = target[1]
                P.rect(x0 + i0 * c - 1, y0 + j0 * c - 1, x0 + (i0 + s) * c + 1, y0 + (j0 + s) * c + 1, kk, width=1.8)
                P.text(x0, y1 + 20, target[2] + '  ← her ' + target[2] + ' · copy', 10, MONO, 0.85 * kk)
            elif target[0] == 'band':
                kb, nb = (target[1], target[2])
                j0, j1 = (self.n * kb / nb, self.n * (kb + 1) / nb)
                P.rect(x0 - 1, y0 + j0 * c - 1, x1 + 1, y0 + j1 * c + 1, 0.8 * kk, width=1.4)
                if kb == 0:
                    P.text(x0, y1 + 20, 'every cell ← the same cell of hers', 10, MONO, 0.85 * kk)
        un, ru, ly = T['UNRULY']
        if t >= un:
            i, j = self.new
            pop = out_cubic(prog(t, un, un + 0.2))
            m = 3 + 5 * (1 - pop)
            P.rect(x0 + i * c - m, y0 + j * c - m, x0 + (i + 1) * c + m, y0 + (j + 1) * c + m, pop, width=2.2)
            iv = '0123456789abcdef'[int(round(clamp(self.its(i, j)) * 15))]
            P.text(x0, y1 + 34, f"({i},{j}) = '{iv}'", 10, MONO_B, pop * (1 - prog(t, T['W63'], T['W63'] + 0.3)))
        if t >= T['EOS2']:
            u = out_cubic(prog(t, T['EOS2'], T['EOS2'] + 0.15))
            P.rect(x1 - 50, y0 - 26, x1, y0 - 6, u, width=1.4)
            P.text(x1 - 44, y0 - 11, '<eos>', 12, MONO_B, u)
            P.text(x1 - 56, y0 - 11, 'id 1', 8.5, MONO, 0.7 * u, anchor='rs')

    def _chips(self, P, t):
        pts = np.array(TOKEN_LOOP, np.float64)
        for tx, at in self.T['MSG']:
            if not at <= t < at + 0.34:
                continue
            u = smooth(prog(t, at + 0.02, at + 0.3))
            p = PL.partial(pts, max(0.002, u))[-1]
            w = PL.text_w(tx, 11, SANS) + 8
            P.rect(p[0] - w / 2, p[1] - 9, p[0] + w / 2, p[1] + 7, 0.12)
            P.rect(p[0] - w / 2, p[1] - 9, p[0] + w / 2, p[1] + 7, 0.9, width=1.0)
            P.mixed(p[0], p[1] + 3, tx, 11, 1.0, anchor='ms', cjk=SANS_B)
            P.line(PL.partial(pts, u, max(0.0, u - 0.12)), 2.0, 0.6)

    def _backward(self, P, t):
        if not self.in_backward(t):
            return
        S = self.S[57]
        fade = 1 - prog(t, self.bw_end, self.bw_end + 0.4)
        ph = t * 34.0
        y_th = row_y(0)
        seg_main = np.array([(CHAR_X - 8, y_th), (712, y_th), (TRAP[0][0], 208), (X_UNB, 208), (X_UNB, BUS_Y - BUS_R - 2), (X_ADD1 + 12, BUS_Y - BUS_R - 2), (X_ADD1 + 6, BUS_Y - 14), (X_ADD1, HEAD_YS[0]), (HX1 + 4, HEAD_YS[0])], np.float64)
        g1 = smooth(prog(t, S[0], S[3]))
        self._dash(P, PL.partial(seg_main, g1), 2.2, fade, ph)
        if t >= S[1]:
            g = smooth(prog(t, S[1], S[1] + 0.25))
            mo = np.array([(X_ADD2, BUS_Y - 12), (X_ADD2, COLL_Y), (CHX[0], COLL_Y)], np.float64)
            self._dash(P, PL.partial(mo, g), 1.4, 0.8 * fade, ph)
            for k, cx in enumerate(CHX):
                self._dmark(P, t, cx + 9, COLL_Y - 6, S[1] + 0.2 + 0.02 * k, fade, 9)
        for s, y in HIS_LINES:
            if t < S[3]:
                continue
            tgt, _ = super()._target('hist', s)
            arm = self._arm(HEAD_YS[0], tgt)
            g = smooth(prog(t, S[3], S[4]))
            self._dash(P, PL.partial(arm, g), 1.8, fade, ph)
        for s, y in HIS_LINES:
            attr = ATTR_Q if s.startswith('那') else ATTR_ME
            x = HIS_X
            for ch, a in zip(s, attr):
                land = S[5] if a >= 0.2 else S[6] if a >= 0.1 else S[7]
                gg = out_cubic(prog(t, land - 0.1, land)) * (1 - prog(t, self.bw_end, self.bw_end + 0.4))
                size = 15 + 9 * clamp(a / 0.26) * gg
                bold = gg > 0.3 and a >= 0.09
                P.mixed(x, y, ch, size, 1.0, cjk=SANS_B if bold else SANS)
                w = PL.text_w(ch, size, SANS) if PL.is_cjk(ch) else PL.text_w(ch, size * 0.86, MONO)
                if gg > 0:
                    P.rect(x + 1.5, y + 3, x + w - 1.5, y + 3 + (1.0 + 5.0 * a / 0.26) * gg, 0.95)
                x += w
        for at, x, y in ((S[0], CHAR_X - 14, y_th - 12), (S[1], X_ADD2 + 10, BUS_Y - 14), (S[2], X_ADD1 + 10, BUS_Y - 14), (S[3], HX1 + 6, HEAD_YS[0] - 6)):
            self._dmark(P, t, x, y, at, fade, 12)
        rx, ry = (226, 282)
        rows = [('∂Δz/∂x · x', None, S[5] - 0.1), ('花', '.26', S[5]), ('开', '.12', S[6]), ('想', '.09', S[7]), ('你', '.09', S[7]), ('18 files', '≈0', S[8])]
        if t >= S[5] - 0.15:
            a = out_cubic(prog(t, S[5] - 0.15, S[5])) * fade
            P.rect(rx - 4, ry - 12, rx + 84, ry + 70, 0.8 * a, width=1.0)
            for k, (lab, v, at) in enumerate(rows):
                u = out_cubic(prog(t, at - 0.05, at + 0.08)) * fade
                yy = ry + k * 13
                if v is None:
                    P.text(rx, yy, lab, 8.5, MONO_B, u)
                    continue
                P.mixed(rx, yy, lab, 10.5 if PL.is_cjk(lab[0]) else 8.5, u, cjk=SANS_B)
                val = float(v.replace('≈', '')) if v[0] != '≈' else 0.0
                P.rect(rx + 26, yy - 7, rx + 26 + 38 * val / 0.26, yy - 1, 0.9 * u)
                P.text(rx + 82, yy, v, 8.5, MONO_B, u, anchor='rs')

    def _dash(self, P, pts, w, val, ph, on=6.0, off=4.0):
        pts = np.asarray(pts, np.float64)
        if len(pts) < 2 or val <= 0.003:
            return
        s = PL.arclen(pts)
        L = s[-1]
        if L <= 0:
            return
        per = on + off
        a = -(ph % per)
        while a < L:
            k0, k1 = (max(0.0, a) / L, min(L, a + on) / L)
            if k1 > k0:
                P.line(PL.partial(pts, k1, k0), w, val)
            a += per

    def _dmark(self, P, t, x, y, at, fade, size):
        if t < at:
            return
        u = prog(t, at, at + 0.9)
        pop = 1 + 0.5 * (1 - out_cubic(prog(t, at, at + 0.12)))
        P.text(x, y, '∂', size * pop, MONO_B, (1 - 0.55 * u) * fade)

def make():
    return G12()
if __name__ == '__main__':
    import sys
    from pathlib import Path
    from PIL import Image
    out = Path(sys.argv[1] if len(sys.argv) > 1 else 'sample_r12/review/plate')
    out.mkdir(parents=True, exist_ok=True)
    g = G12()
    ts = [float(x) for x in sys.argv[2:]] or [234.8, 236.2, 236.9, 237.8, 238.5, 239.5, 240.3, 241.6, 242.7, 244.8, 245.9, 246.95, 248.5, 249.6, 251.3, 252.2, 255.4, 257.0, 257.6, 260.7]
    for t in ts:
        Image.fromarray(g.render(t)).save(out / f'p_{t:07.2f}.png')
        print(t)
