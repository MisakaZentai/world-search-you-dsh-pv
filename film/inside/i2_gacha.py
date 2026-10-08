"""r15 sample (sample_r15/README.md, D53, D54): interlude 2 (137.31-151.55) as a gacha machine.

The owner picked the gacha of the three stills (inside/i2_concepts.py): "第二个可爱，做个样片我看看". On g1 (the
first moving sample, sample_r15/src_g1/): "感觉可以优化一些，多一点精致和动态的感觉~扭蛋也可以是不同颜色的，旋转的时候
会在里面滚来滚去很可爱" (D54). So g2:

  globe    p(next token) for this one: a capsule a percent. 好 is her blue, in four shades; anything else is a warm
           colour (pink, yellow, mint), fewer each time (.91 .93 .95 .96 .97 .98, invented; MACHINE_ARC §4.2).
           The capsules are simulated (inside/i2_sim.py): each press the agitator churns them, they roll and
           tumble and fall back; each kick they hop; the one that answers leaves through the bottom, and the copy
           that comes back from memory drops in through the inlet
  base     this one's body (BO.ARCH; FACTS X29, X35) on its little screen: a column a layer (solid = full attention,
           pale = sparse, short = sliding window; under it the FFN, a block = dense), its MTP heads after a gap; under
           that a dot an expert, k lit, a new k on every event; its shared experts the big dots
  crank    ↻, a knob on a handle
  inlet    ~/memory/you/ pours in from the top: 好呀！现在我是… ×N

A turn, on dsh's own times (groups/d.py Turn): the press turns the crank and churns the globe (a few warm capsules
turn blue: this one, and one more copy than the one before), the screen lays in its body; the read (dsh's 读取记忆)
lights the inlet; her blue climbs its layers to the top on the answer; on the answer (dsh's) the capsule rolls out of
the chute into the cup and pops open, the slip unrolls: 好呀！现在我是人类了呢; on the write (dsh's human_n.txt) the
slip slides onto the pile and a small capsule rolls back up the line into the inlet (×N+1) and drops into the globe.

g3 (D55, "拿掉一点解释，增加一些技术方面的小细节"): the words that explained go (the pane's structure line, 一颗 = 1%,
打开都是同一张, 写回记忆, 层); small readouts come instead: the name plate carries a one-line spec (L78+1 · MLA sparse
· E256 k8 +1), the layers get a scale and a cursor (L 42/78) while her blue climbs, a little LCD between the chute and
the crank shows the logit lens of 好 (a sparkline up the layers) and the router's picks (top-8: e17 e93 …), each slip
shows its token boundaries (好|呀！|现在|我是|人类|了|呢), and the rail says memory.write("human_n") while the copy
runs (dsh's own call, as in d_r5's log).

Invented: p, the lens curve, which experts the router picks, the machine, its colours. Real: the bodies, the files,
the times, the tokens of the answer (groups/d_lead.py PH.toks).
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
import numpy as np
from . import plate as PL
from .i2_concepts import MONO, MONO_B, P_GOOD, SANS, SANS_B, SAYS, W1, W2, W3, WF, _arch, _Base, fmt_p, rrect, says, says_w
from .i2_sim import Sim
from .plate import Plate, clamp, lerp, out_cubic, prog, smooth
CAP_R = 6.8
EXTRA = {'b1': (84, 112, 236), 'b2': (126, 146, 238), 'b3': (72, 88, 182), 'b4': (156, 178, 242), 'pink': (236, 132, 158), 'yellow': (238, 186, 74), 'mint': (96, 186, 156)}
BLUES = ['b1', 'b2', 'b3', 'b4']
WARMS = ['pink', 'yellow', 'mint']

def _bez_at(p0, p1, p2, p3, u):
    a = 1 - u
    return (a ** 3 * p0[0] + 3 * a * a * u * p1[0] + 3 * a * u * u * p2[0] + u ** 3 * p3[0], a ** 3 * p0[1] + 3 * a * a * u * p1[1] + 3 * a * u * u * p2[1] + u ** 3 * p3[1])

def hatch(P, x0, y0, x1, y1, step=4.5, val=0.4, layer='ink'):
    w, h = (x1 - x0, y1 - y0)
    k = -h
    while k < w:
        a = (x0 + max(k, 0), y0 + max(0, -k))
        b = (x0 + min(w, k + h), y0 + min(h, w - k))
        if b[0] > a[0]:
            P.line([a, b], WF, val, layer)
        k += step

def compose(backs, F=None, M=None):
    paper = np.array(PL.PAPER, np.float32) / 255.0
    W_, H_ = (backs[0][0].w, backs[0][0].h)
    acc = np.zeros((H_, W_, 3), np.float32)
    hide = None
    if M is not None and M.arr('mask') is not None:
        hide = 1.0 - np.clip(M.arr('mask'), 0, 1)
    for name, col in list(PL.COLOURS.items()) + list(EXTRA.items()):
        a = np.zeros((H_, W_), np.float32)
        for pl, w in backs:
            d = pl.arr(name)
            if d is not None:
                a += d * w
        if hide is not None:
            a *= hide
        if F is not None:
            f = F.arr(name)
            if f is not None:
                a += f
        if not a.any():
            continue
        c = np.array(col, np.float32) / 255.0
        absorb = -np.log(np.clip(c / paper, 0.0001, 1.0))
        acc += np.clip(a, 0, 1.6)[..., None] * absorb
    rgb = paper * np.exp(-acc)
    return (np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8)

def spec(b):
    """A one-line spec of a body from its structure: L78+1 · MLA sparse · E256 k8 +1."""
    A, _m = _arch(b.key)
    nf = sum((1 for j in range(b.n) if b.kind(j) == 'full'))
    ns = sum((1 for j in range(b.n) if b.kind(j) == 'sparse'))
    nw = b.n - nf - ns
    mla = 'MLA ' if 'MLA' in A.get('left', '') else ''
    if ns == b.n:
        att = f'{mla}sparse'
    elif nf == b.n:
        att = 'full'
    elif nw and nf:
        att = f'1 full : {round(nw / nf)} SWA'
    else:
        att = f'{nf} full+{ns} sparse'
    moe = f'E{b.E}' + (f'+{b.zero}z' if b.zero else '') + f' k{b.k}' + (f' +{b.shared}' if b.shared else '')
    return f'L{b.n}' + (f'+{b.mtp}' if b.mtp else '') + f' · {att} · {moe}'

def lens(x, p_final):
    """The logit lens of 好 up the layers (x = depth 0..1): flat, then up in the top third (invented shape)."""
    sg = lambda u: 1 / (1 + math.exp(-(u - 0.64) / 0.075))
    return p_final * (sg(x) - sg(0)) / (sg(1) - sg(0))

def token_ticks(P, x, y, size, h, val=0.28):
    """Faint marks between the answer's tokens (好|呀！|现在|我是|人类|了|呢)."""
    for s_, _hers in SAYS[:-1]:
        x += PL.text_w(s_, size, SANS_B)
        P.line([(x + 0.5, y - size * 0.92), (x + 0.5, y + 2.5)], WF, val)

def capsule(P, X, Y, r, ang, colour, val=1.0, lit=0.0):
    """A capsule seen from the side: the coloured half and the clear half, a seam, a shine (light from top left)."""
    S = PL.SS
    box = [(X - r) * S, (Y - r) * S, (X + r) * S, (Y + r) * S]
    a = math.degrees(ang)
    d = P._d(colour)
    d.pieslice(box, a, a + 180, fill=int(255 * clamp(0.8 * val)))
    d.pieslice(box, a + 180, a + 360, fill=int(255 * clamp(0.13 * val)))
    if lit > 0.01:
        P._d('blue').pieslice(box, a, a + 180, fill=int(255 * clamp(0.6 * lit * val)))
    sx, sy = (X - 0.42 * r, Y - 0.42 * r)
    sr = 0.24 * r
    d.ellipse([(sx - sr) * S, (sy - sr) * S, (sx + sr * 1.2) * S, (sy + sr * 0.8) * S], fill=0)
    P.circle(X, Y, r, 0.78 * val, width=W3 * (r / CAP_R) ** 0.5)
    c, s_ = (math.cos(ang), math.sin(ang))
    P.line([(X - r * c, Y - r * s_), (X + r * c, Y + r * s_)], WF, 0.55 * val)

class Gacha(_Base):
    G_CX, G_CY, G_R = (236, 186, 98)
    BASE = (104, 290, 368, 462)
    PILE_X, PILE_Y, PILE_P = (410, 316, 32)
    COLS, DP = (72, 2.9)

    def __init__(self):
        super().__init__()
        rs = np.random.RandomState(7)
        self.order = [int(v) for v in rs.permutation(100)]
        self.shade = [BLUES[int(v)] for v in rs.randint(0, 4, 100)]
        self.press = [T.t0 for T in self.turns]
        self.slip_go = [max(T.write, T.ans + 0.3) for T in self.turns]
        self.slip_in = [g + 0.32 for g in self.slip_go]
        self.copy_in = [g + 0.85 for g in self.slip_go]
        self.events = sorted(set(self.all_kicks + [T.read for T in self.turns] + [T.ans for T in self.turns] + [T.think for T in self.turns if T.think]))
        self.count = [k for k in self.kicks[0] if k > self.slip_in[0] + 0.05]
        a, b = (self.copy_in[1] + 0.02, self.press[2] - 0.1)
        n_warm = 100 - self.n_blue(1)
        self.ring_at = [a + (b - a) * k / n_warm for k in range(n_warm)]
        self.left_idx = {}
        R_in = self.G_R - 3
        leaves = [(T.ans - 0.24, self._picker(i)) for i, T in enumerate(self.turns)]
        enters = [(self.copy_in[i], lambda i=i: self.left_idx.get(i)) for i in range(len(self.turns))]
        self.sim = Sim(R_in, CAP_R, 100, 136.5, 151.75, self.press, self.all_kicks, leaves, enters)

    def _picker(self, i):

        def pick(x, on):
            warm = self.warm_set(i)
            cand = [j for j in np.where(on)[0] if j not in warm]
            if not cand:
                return None
            j = min(cand, key=lambda j: math.hypot(x[j, 0], x[j, 1] - (self.G_R - 3)))
            self.left_idx[i] = int(j)
            return int(j)
        return pick

    def n_blue(self, i):
        return int(round(P_GOOD[i] * 100))

    def warm_set(self, i):
        return set(self.order[:100 - self.n_blue(i)])

    def colour(self, j, i):
        if j in self.warm_set(i):
            return WARMS[self.order.index(j) % 3]
        return self.shade[j]

    def copies_at(self, t):
        return 3 + sum((1 for c in self.copy_in if t >= c))

    def ev_tick(self, t):
        return sum((1 for e in self.events if e <= t))

    def render(self, t, W, H):
        B, F, M = (Plate(W, H), Plate(W, H), Plate(W, H))
        i = self.turn(t, lead=0.02)
        self._base(B, t, i)
        self._globe(B, F, t, i)
        self._inlet(B, F, t, i)
        self._capsule(B, F, M, t, i)
        self._pile(B, F, M, t, i, W)
        self._copy(F, t)
        return compose([(B, 1.0)], F, M)

    def _globe(self, P, F, t, i):
        cx, cy, R = (self.G_CX, self.G_CY, self.G_R)
        t0 = self.press[i]
        warm_now = self.warm_set(i)
        warm_before = self.warm_set(i - 1) if i > 0 else warm_now
        turned = [j for j in self.order if j in warm_before and j not in warm_now]
        band = self._count_band(t)
        X, A, on = self.sim.at(t)
        P.line([(cx - 40, cy + R - 12), (cx - 46, self.BASE[1]), (cx + 46, self.BASE[1]), (cx + 40, cy + R - 12)], W1, 0.9)
        P.line([(cx - 43, self.BASE[1] - 7), (cx + 43, self.BASE[1] - 7)], WF, 0.5)
        P.rect(cx - 39, cy + R - 9, cx + 39, self.BASE[1] - 8, 0.06)
        for j in range(100):
            if not on[j]:
                continue
            x, y = (cx + X[j, 0], cy + X[j, 1])
            col = self.colour(j, i)
            r = CAP_R
            lit = 0.0
            if j in turned:
                k = turned.index(j)
                at = t0 + 0.1 + 0.08 * k
                if t < at:
                    col = self.colour(j, i - 1)
                else:
                    pop = 1 - prog(t, at, at + 0.25)
                    r = CAP_R * (1 + 0.4 * pop)
                    lit = pop
            if band is not None and col in BLUES:
                lo, hi, a = band
                if lo <= y <= hi:
                    lit = max(lit, a)
            capsule(P, x, y, r, A[j], col, 1.0, lit)
            ring = self._ring(t, i, j)
            if ring > 0.01:
                P.circle(x, y, r + 2.4, ring, width=W1)
        P.circle(cx, cy, R, 0.95, width=W1)
        P.circle(cx, cy, R - 3, 0.25, width=WF)
        P.line([(cx + (R - 9) * math.cos(a), cy - (R - 9) * math.sin(a)) for a in np.linspace(1.95, 2.6, 12)], W2 * 1.3, 0.45)
        P.line([(cx + (R - 9) * math.cos(a), cy - (R - 9) * math.sin(a)) for a in np.linspace(2.72, 2.86, 4)], W2 * 1.3, 0.45)
        tw = max([1 - prog(t, d, d + 0.35) for d in self.press if d <= t] + [0.0])
        if tw > 0.01:
            sx, sy = (cx + R * 0.52, cy - R * 0.6)
            L = 3 + 6 * tw
            P.line([(sx - L, sy), (sx + L, sy)], W2, 0.8 * tw)
            P.line([(sx, sy - L), (sx, sy + L)], W2, 0.8 * tw)
        self._legend(P, t, i)

    def _legend(self, P, t, i):
        cx, cy, R = (self.G_CX, self.G_CY, self.G_R)
        t0 = self.press[i]
        p = P_GOOD[i]
        lx = cx + R + 22
        P.text(lx, cy - 34, 'p(t₁)', 11, MONO, 0.8)
        flip = out_cubic(prog(t, t0, t0 + 0.16)) if i > 0 else 1.0
        capsule(P, lx + 7, cy - 9, 6.5, -0.35, 'b1')
        P.mixed(lx + 20, cy - 4, '好', 14, 0.95, 'quiet', cjk=SANS_B)
        pulse = 0.0
        if self.count and self.count[-1] <= t < self.count[-1] + 0.4:
            pulse = 1 - prog(t, self.count[-1], self.count[-1] + 0.4)
        if flip < 1 and i > 0:
            P.text(lx + 40, cy - 4 - 8 * flip, fmt_p(P_GOOD[i - 1]), 14, MONO_B, 0.95 * (1 - flip))
        P.text(lx + 40, cy - 4 + 8 * (1 - flip), fmt_p(p), 14 * (1 + 0.15 * pulse), MONO_B, 0.95 * flip)
        for k, c in enumerate(WARMS):
            capsule(P, lx + 4 + 8 * k, cy + 16, 4.2, -0.35 + k, c)
        P.text(lx + 30, cy + 21, '别的', 10.5, SANS, 0.7)
        P.text(lx + 60, cy + 21, fmt_p(1 - p), 11, MONO, 0.7 * flip + 0.3 * (1 - flip))

    def _ring(self, t, i, j):
        """MiniMax's second bar: the warm capsules ringed one by one; the rings go on the next press."""
        if i != 1 or j not in self.warm_set(1):
            return 0.0
        k = [c for c in self.order if c in self.warm_set(1)].index(j)
        at = self.ring_at[k]
        return out_cubic(prog(t, at - 0.06, at)) * (1 - prog(t, self.press[2] - 0.04, self.press[2] + 0.12))

    def _count_band(self, t):
        """GLM's long turn: the blue capsules counted bottom to top, landing on each kick."""
        ks = self.count
        if not ks or not ks[0] - 0.05 <= t < ks[-1] + 0.45:
            return None
        cy, R = (self.G_CY, self.G_R)
        n = len(ks)
        k = sum((1 for x in ks if x <= t))
        if 0 < k < n:
            k = k - 1 + 0.35 * smooth(prog(t, ks[k - 1], ks[k])) + 0.65 * out_cubic(prog(t, ks[k] - 0.2, ks[k]))
        hi = cy + R
        top = cy - 0.15 * R
        lo = hi - (hi - top) * k / n
        a = 1.0 if t < ks[-1] else 1 - prog(t, ks[-1], ks[-1] + 0.45)
        return (lo, hi, 0.5 * a)

    def _inlet(self, P, F, t, i):
        cx, cy, R = (self.G_CX, self.G_CY, self.G_R)
        T = self.turns[i]
        n = self.copies_at(t)
        glow = out_cubic(prog(t, T.read - 0.06, T.read)) * (1 - prog(t, T.read + 0.25, T.read + 0.55))
        arrive = max([1 - prog(t, c, c + 0.35) for c in self.copy_in if t >= c] + [0.0])
        top = cy - R
        funnel = [(cx - 26, top - 20), (cx + 26, top - 20), (cx + 11, top + 1), (cx - 11, top + 1), (cx - 26, top - 20)]
        P.line(funnel, W1, 0.95)
        P.line([(cx - 29, top - 22), (cx + 29, top - 22)], W1, 0.95)
        hatch(P, cx + 6, top - 18, cx + 22, top - 2, 3.5, 0.3)
        lv_ = max(glow, arrive)
        if lv_ > 0.01:
            P.line(funnel, W1 * 1.2, lv_, 'blue')
        P.text(cx - 34, top - 13, '~/memory/you/', 9.5, MONO, 0.7, anchor='rs')
        P.mixed(cx - 34, top + 1, f'好呀！现在我是… ×{n}', 10.5, 0.95, 'quiet', anchor='rs')
        if glow > 0.01:
            P.mixed(cx - 34, top + 1, f'好呀！现在我是… ×{n}', 10.5, glow, 'blue', anchor='rs')
        for k in range(6):
            a = T.read + 0.035 * k
            u = prog(t, a, a + 0.26)
            if 0 < u < 1:
                yy = lerp(top - 6, top + 30, u * u)
                F.circle(cx - 7 + 2.8 * k, yy, 1.7, 1 - u * 0.6, 'blue')

    def _base(self, P, t, i):
        x0, y0, x1, y1 = self.BASE
        T = self.turns[i]
        b = self.bodies[i]
        t0 = self.press[i]
        hatch(P, x1, y0 + 18, x1 + 8, y1 + 8, 4.5, 0.38)
        hatch(P, x0 + 18, y1, x1, y1 + 8, 4.5, 0.38)
        P.line(rrect(x0, y0, x1, y1, 14), W1, 0.95)
        for fx in (x0 + 26, x1 - 52):
            P.line(rrect(fx, y1 + 1, fx + 26, y1 + 8, 3), W2, 0.85)
        for sx, sy in ((x0 + 9, y0 + 9), (x1 - 9, y0 + 9), (x0 + 9, y1 - 9), (x1 - 9, y1 - 9)):
            P.circle(sx, sy, 2.3, 0.7, width=WF)
            P.line([(sx - 1.4, sy - 1.4), (sx + 1.4, sy + 1.4)], WF, 0.7)
        P.line(rrect(x0 + 18, y0 + 9, x1 - 18, y0 + 28, 3), W3, 0.85)
        boot0 = t0 + (0.06 if i == 0 else 0.0)
        flap = out_cubic(prog(t, boot0, boot0 + 0.14))

        def fit(j):
            room = x1 - 26 - (x0 + 26) - PL.text_w(self.short[j], 10.5, MONO_B) - 10
            sz = 8.5
            while sz > 6.5 and PL.text_w(spec(self.bodies[j]), sz, MONO) > room:
                sz -= 0.25
            return sz
        if flap < 1 and i > 0:
            P.text(x0 + 26, y0 + 23 - 7 * flap, self.short[i - 1], 10.5, MONO_B, 0.95 * (1 - flap))
            P.text(x1 - 26, y0 + 22.5 - 7 * flap, spec(self.bodies[i - 1]), fit(i - 1), MONO, 0.7 * (1 - flap), anchor='rs')
        P.text(x0 + 26, y0 + 23 + 7 * (1 - flap), self.short[i], 10.5, MONO_B, 0.95 * flap)
        P.text(x1 - 26, y0 + 22.5 + 7 * (1 - flap), spec(b), fit(i), MONO, 0.7 * flap, anchor='rs')
        sx0, sy0, sx1, sy1 = (x0 + 12, y0 + 34, x1 - 12, y1 - 49)
        P.line(rrect(sx0, sy0, sx1, sy1, 5), W2, 0.75)
        P.line(rrect(sx0 + 2.5, sy0 + 2.5, sx1 - 2.5, sy1 - 2.5, 3.5), WF, 0.35)
        boot = prog(t, boot0, boot0 + 0.24)
        climb = self._climb(t, i)
        self._body(P, b, sx0 + 9, sy0 + 13, t, boot, climb)
        if boot >= 1:
            fill, front = climb
            k = int(round(fill * b.n))
            lay = 'blue' if 0 < fill < 1 else 'ink'
            P.text(sx1 - 7, sy0 + 10, f'L {k:>2}/{b.n}', 8, MONO, 0.85 if lay == 'blue' else 0.55, lay, anchor='rs')
        self._lcd(P, t, i, x0 + 74, y1 - 44, x1 - 58, y1 - 12)
        kx, ky = (x1 - 34, y1 - 28)
        P.circle(kx, ky, 18, 0.95, width=W1)
        P.circle(kx, ky, 13, 0.4, width=WF)
        ang = -math.pi / 2 + 2 * math.pi * out_cubic(prog(t, t0, t0 + 0.42))
        hx, hy = (kx + 15 * math.cos(ang), ky + 15 * math.sin(ang))
        P.line([(kx, ky), (hx, hy)], W1 * 1.6, 0.95)
        P.circle(kx, ky, 3.6, 0.95)
        P.circle(hx, hy, 4.6, 0.95, width=W1)
        P.circle(hx, hy, 2.0, 0.6)
        spin = 1 - prog(t, t0 + 0.25, t0 + 0.6)
        if spin > 0.01:
            arc = [(kx + 26 * math.cos(a), ky + 26 * math.sin(a)) for a in np.linspace(-2.7, -0.5, 14)]
            P.line(arc, W2, 0.7 * spin)
            P.line([arc[-1], (arc[-1][0] - 6, arc[-1][1] - 1)], W2, 0.7 * spin)
            P.line([arc[-1], (arc[-1][0] - 1, arc[-1][1] - 6)], W2, 0.7 * spin)
        cx0, cy0, cx1, cy1 = (x0 + 18, y1 - 46, x0 + 66, y1 - 12)
        P.line(rrect(cx0, cy0, cx1, cy1, 10), W1, 0.95)
        P.rect(cx0 + 5, cy0 + 5, cx1 - 5, cy1 - 5, 0.12)
        sw = max([math.sin(math.pi * prog(t, T_.ans - 0.22, T_.ans - 0.02)) for T_ in self.turns] + [0.0])
        fl = (cy1 - cy0 - 8) * math.cos(1.2 * sw)
        P.line([(cx0 + 5, cy0 + 4), (cx1 - 5, cy0 + 4)], W2, 0.85)
        P.line([(cx0 + 6, cy0 + 4 + fl), (cx1 - 6, cy0 + 4 + fl)], W2, 0.85)
        P.line([(cx0 + 6, cy0 + 4), (cx0 + 6, cy0 + 4 + fl)], WF, 0.6)
        P.line([(cx1 - 6, cy0 + 4), (cx1 - 6, cy0 + 4 + fl)], WF, 0.6)
        ux, uy = self._tray()
        cup = [(ux - 24 + 48 * k / 16, uy + 2 + 11 * math.sin(math.pi * k / 16)) for k in range(17)]
        P.line(cup, W1, 0.85)
        P.line([(ux - 27, uy + 2), (ux + 27, uy + 2)], W1, 0.85)
        P.line([(ux, uy + 13), (ux, uy + 17)], W1, 0.8)
        P.line([(ux - 8, uy + 18), (ux + 8, uy + 18)], W1, 0.8)
        hatch(P, ux - 20, uy + 4, ux + 20, uy + 11, 3.5, 0.25)

    def _lcd(self, P, t, i, x0, y0, x1, y1):
        """A little readout: the logit lens of 好 up the layers (as far as her blue has climbed), and the router's
        picks on this event."""
        b = self.bodies[i]
        P.line(rrect(x0, y0, x1, y1, 4), W3, 0.8)
        P.rect(x0 + 2, y0 + 2, x1 - 2, y1 - 2, 0.05)
        fill, _f = self._climb(t, i)
        p = P_GOOD[i]
        P.text(x0 + 5, y0 + 12, 'lens', 7.5, MONO, 0.6)
        gx0, gx1, gy0, gy1 = (x0 + 28, x1 - 44, y0 + 3.5, y0 + 13)
        P.line([(gx0, gy1), (gx1, gy1)], WF, 0.4)
        n = 24
        pts = [(lerp(gx0, gx1, k / n), gy1 - (gy1 - gy0) * lens(k / n, p)) for k in range(n + 1) if k / n <= fill + 1e-06]
        if len(pts) > 1:
            P.line(pts, W2, 0.9, 'blue' if fill < 1 else 'quiet')
        cur = lens(min(1.0, fill), p)
        P.mixed(x1 - 5, y0 + 12, f'好 {(fmt_p(cur) if cur >= 0.005 else '.00')}', 8, 0.85, anchor='rs')
        lit = sorted(b.lit(self.ev_tick(t)))
        ids = ' '.join((f'e{e}' for e in lit[:5])) + (' …' if len(lit) > 5 else '')
        P.text(x0 + 5, y1 - 5, f'top-{b.k} {ids}', 7.5, MONO, 0.75)

    def _climb(self, t, i):
        """Her blue up its layers: 0 before the read, landing at the top on the answer (a step on each event)."""
        T = self.turns[i]
        a0 = T.read + 0.04
        if t < a0:
            return (0.0, 0.0)
        stops = [a0] + [e for e in self.events if a0 + 0.05 < e < T.ans - 0.05] + [T.ans]
        n = len(stops) - 1
        for j in range(n):
            if t < stops[j + 1]:
                return ((j + out_cubic(prog(t, stops[j], stops[j + 1]))) / n, 1.0)
        return (1.0, 1 - prog(t, T.ans, T.ans + 0.3))

    def _body(self, P, b, x0, y0, t, boot, climb):
        fill, front = climb
        pitch = min(2.6, 196 / (b.n + b.mtp + 2))
        sw = max(1.2, pitch - 1.0)
        shown = b.n * boot
        x = x0
        for j in range(b.n):
            if j >= shown:
                break
            kd = b.kind(j)
            if kd == 'full':
                P.rect(x, y0, x + sw, y0 + 18, 0.9)
            elif kd == 'sparse':
                P.rect(x, y0, x + sw, y0 + 18, 0.42)
            else:
                P.rect(x, y0 + 9, x + sw, y0 + 18, 0.8)
            if j in b.dense:
                P.rect(x, y0 + 20, x + sw, y0 + 26, 0.9)
            else:
                P.rect(x, y0 + 20, x + sw * 0.4, y0 + 26, 0.75)
            if j < fill * b.n:
                P.rect(x - 0.3, y0 - 4, x + sw + 0.3, y0 - 1.5, 0.85, 'quiet')
            x += pitch
        if fill > 0 and front > 0.01 and (fill < 1.0):
            fx = x0 + fill * b.n * pitch
            P.line([(fx, y0 - 6), (fx, y0 + 28)], 1.6, front, 'blue')
        if b.mtp and boot >= 1:
            x += 5
            for _ in range(b.mtp):
                P.rect(x, y0, x + sw, y0 + 26, 0.6, width=WF)
                x += pitch
        if boot >= 1:
            for j in range(0, b.n + 1, 10):
                xx = x0 + j * pitch - 0.5
                P.line([(xx, y0 + 28), (xx, y0 + 31 if j % 20 == 0 else y0 + 29.5)], WF, 0.55)
            P.line([(x0, y0 + 28), (x0 + b.n * pitch, y0 + 28)], WF, 0.4)
        lit = b.lit(self.ev_tick(t))
        gy = y0 + 35
        tot = int((b.E + b.zero) * boot)
        for e in range(tot):
            r, c = divmod(e, self.COLS)
            ex, ey = (x0 + c * self.DP, gy + r * self.DP)
            if e >= b.E:
                P.rect(ex, ey, ex + 2.1, ey + 2.1, 0.5, width=WF * 0.8)
            elif e in lit:
                P.rect(ex - 0.5, ey - 0.5, ex + 2.6, ey + 2.6, 1.0)
            else:
                P.rect(ex, ey, ex + 1.9, ey + 1.9, 0.3)
        if boot >= 1:
            gx1 = x0 + min(self.COLS, b.E + b.zero) * self.DP
            for k in range(b.shared):
                P.circle(gx1 + 7 + 8 * k, gy + 2, 3.0, 0.9)

    def _tray(self):
        x0, y0, x1, y1 = self.BASE
        return (x0 + 42, y1 + 22)

    def _capsule(self, B, F, M, t, i):
        T = self.turns[i]
        x0, y0, x1, y1 = self.BASE
        tx, ty = self._tray()
        a = T.ans
        r = 11
        go = self.slip_go[i]
        col = self.shade[self.left_idx.get(i, 0)]
        if t < a - 0.2 or t >= go + 0.25:
            return
        if t < a:
            u = prog(t, a - 0.2, a)
            yy = lerp(y1 - 29, ty, u * u)
            capsule(F, tx, yy, r, 6.0 * u, col)
            return
        bounce = 5 * math.sin(math.pi * prog(t, a, a + 0.12)) * (1 - prog(t, a, a + 0.12))
        o = out_cubic(prog(t, a + 0.04, a + 0.16))
        fade = 1 - prog(t, go, go + 0.25)
        S = PL.SS
        cxo, cyo = (tx - 6 * o, ty - bounce)
        lift = 9 * o
        tip = -35 * o
        d = B._d(col)
        box = [(cxo - r) * S, (cyo - lift - r) * S, (cxo + r) * S, (cyo - lift + r) * S]
        d.pieslice(box, 180 + tip, 360 + tip, fill=int(255 * 0.8 * fade))
        B.line([(cxo + r * math.cos(math.radians(q)), cyo - lift + r * math.sin(math.radians(q))) for q in np.linspace(180 + tip, 360 + tip, 16)] + [(cxo + r * math.cos(math.radians(180 + tip)), cyo - lift + r * math.sin(math.radians(180 + tip)))], W1 * 0.8, 0.9 * fade)
        box = [(cxo - r) * S, (cyo - r) * S, (cxo + r) * S, (cyo + r) * S]
        d.pieslice(box, 0, 180, fill=int(255 * 0.13 * fade))
        B.line([(cxo + r * math.cos(math.radians(q)), cyo + r * math.sin(math.radians(q))) for q in np.linspace(0, 180, 16)] + [(cxo + r, cyo)], W1 * 0.8, 0.9 * fade)
        k = 1 - prog(t, a + 0.05, a + 0.4)
        for ang in (200, 230, 260, 290, 320, 345):
            ar = math.radians(ang)
            F.line([(cxo + 17 * math.cos(ar), cyo - 6 + 17 * math.sin(ar)), (cxo + (24 + 6 * (1 - k)) * math.cos(ar), cyo - 6 + (24 + 6 * (1 - k)) * math.sin(ar))], W2, 0.9 * k)
        if t < go:
            un = out_cubic(prog(t, a + 0.08, a + 0.32))
            self._slip(F, M, tx + 16, ty - 16, un, 16, lit=1 - prog(t, a + 0.35, a + 0.85), curl=True)

    def _slip(self, F, M, x, y, o, size, val=1.0, lit=0.0, h=30, curl=False):
        full = says_w(size) + 24
        w = full * o
        if w < 2:
            return w
        M.rect(x, y, x + w, y + h, 1.0, 'mask')
        F.line([(x + w, y), (x, y), (x, y + h), (x + w, y + h)], W2, 0.9 * val)
        if not curl or o >= 0.999:
            F.line([(x + w, y), (x + w - 6, y), (x + w, y + 6), (x + w, y)], WF, 0.6 * val)
            F.line([(x + w, y + 6), (x + w, y + h)], W2, 0.9 * val)
        says(F, x + 12, y + h - 9, size, val=0.95 * val)
        token_ticks(F, x + 12, y + h - 9, size, h, 0.3 * val)
        if lit > 0.01:
            F.mixed(x + 12, y + h - 9, '好呀！现在我是', size, lit * val, 'blue', cjk=SANS_B)
        if curl and o < 0.999:
            S = PL.SS
            for name in list(F.L):
                F._d(name).rectangle([(x + w + 1) * S, (y - 2) * S, (x + full + 4) * S, (y + h + 2) * S], fill=0)
            M.rect(x + w - 3, y - 2, x + w + 9, y + h + 2, 1.0, 'mask')
            F.circle(x + w + 3, y + h / 2, h / 2 + 1, 0.9 * val, width=W2)
            F.circle(x + w + 3, y + h / 2, h / 4, 0.6 * val, width=WF)
        return w

    def _pile(self, B, F, M, t, i, W):
        """What the six said: a pile on the right, the newest on top; the slip slides on from the cup on the write,
        under the base, and pushes the others down."""
        x0 = self.PILE_X
        any_ = any((t >= g for g in self.slip_go))
        on = [j for j in range(len(self.turns)) if t >= self.slip_go[j]]
        for j in on:
            newer = [k for k in on if k > j]
            r = 0.0
            for k in newer:
                r += out_cubic(prog(t, self.slip_go[k] + 0.08, self.slip_in[k]))
            y = self.PILE_Y + r * self.PILE_P
            lv_ = max(0.55, 0.95 - 0.09 * r)
            u = prog(t, self.slip_go[j], self.slip_in[j])
            if u < 1:
                tx, ty = self._tray()
                X, Y = _bez_at((tx + 16, ty - 16), (x0 - 10, ty - 12), (x0 - 4, y + 60), (x0, y), smooth(u))
                over = 3 * math.sin(math.pi * prog(u, 0.75, 1.0))
                self._slip(F, M, X, Y - over, 1.0, lerp(16, 14, smooth(u)), 1.0, h=lerp(30, 26, smooth(u)))
                continue
            settle = 2.5 * math.sin(math.pi * prog(t, self.slip_in[j], self.slip_in[j] + 0.18))
            yy = y - settle
            B.line(rrect(x0, yy, W - 14, yy + 26, 2), W2, 0.85 * lv_)
            B.line([(W - 20, yy), (W - 14, yy + 6)], WF, 0.6 * lv_)
            says(B, x0 + 10, yy + 18.5, 14, val=0.95 * lv_)
            token_ticks(B, x0 + 10, yy + 18.5, 14, 26, 0.25 * lv_)
            B.text(W - 22, yy + 11, self.short[j], 9, MONO_B, 0.7 * lv_, anchor='rs')
            B.mixed(W - 22, yy + 22, f'p(好) {fmt_p(P_GOOD[j])}', 8.5, 0.6 * lv_, anchor='rs')
        if any_:
            pts = self._arc()
            B.line(pts, W3, 0.45)
            for k in range(3, len(pts) - 3, 6):
                B.circle(pts[k][0], pts[k][1], 0.9, 0.4)
            for j, T_ in enumerate(self.turns):
                a, b = (self.slip_in[j] - 0.05, self.copy_in[j] + 0.5)
                if a <= t < b:
                    k = min(prog(t, a, a + 0.12), 1 - prog(t, b - 0.25, b))
                    B.text(x0 + 46, 232, f'memory.write("{T_.file}")', 8.5, MONO, 0.8 * k)
                    B.text(x0 + 46, 245, '→ ok', 8.5, MONO, 0.6 * k * prog(t, self.copy_in[j], self.copy_in[j] + 0.1))

    def _arc(self):
        x0 = self.PILE_X
        return PL.bezier((x0 + 40, self.PILE_Y - 26), (x0 + 40, 124), (self.G_CX + 120, self.G_CY - self.G_R - 52), (self.G_CX + 28, self.G_CY - self.G_R - 24), n=60)

    def _copy(self, F, t):
        """A small capsule of her blue rolls back up the line into the inlet (the sim drops it into the globe)."""
        pts = self._arc()
        s = PL.arclen(pts)
        for j in range(len(self.turns)):
            a, b = (self.slip_in[j], self.copy_in[j])
            if not a - 0.1 <= t < b:
                continue
            u = smooth(prog(t, a, b))
            d = u * s[-1]
            x, y = (np.interp(d, s, pts[:, 0]), np.interp(d, s, pts[:, 1]))
            rr = lerp(4.0, CAP_R, u) * min(1.0, prog(t, a - 0.1, a + 0.05) * 1.5)
            if rr > 0.5:
                capsule(F, x, y - rr - 0.5, rr, -d / max(1.0, rr), 'b1')
_VIEW = []

def view():
    if not _VIEW:
        _VIEW.append(Gacha())
    return _VIEW[0]
if __name__ == '__main__':
    import sys
    from pathlib import Path
    from PIL import Image
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    V = view()
    for a in sys.argv[2:]:
        tt = float(a)
        Image.fromarray(V.render(tt, 660, 510)).save(out / f'g_{tt:07.2f}.png')
