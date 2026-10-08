"""r15 concepts (sample_r15/README.md, D52): three new pictures for interlude 2 (137.31-151.55), stills first.

The owner asked for a new, cute picture (not r12's machine, not the block figures of inside/i2_r15.py) and then for a
still of each of three options. All three tell MACHINE_ARC §4.2's story: six different bodies wear the same name, all
copy her sentence pattern 好呀！现在我是▢了 from ~/memory/you/ and say 好呀！现在我是人类了呢; every answer is written
back as one more copy, so the next one is surer (p(好) .91 → .98, invented).

  stamp  the stamp's face is her pattern (blue, mirrored); its handle is this one's body (a ridge a layer, its
         attention kind; the block below it a dot an expert, k lit). It inks on the pad (memory), comes down with a
         snap and prints the same line; 人类 and 呢 are its own, written in ink. The used stamps stand on the left.
  gacha  ↻ is a turn of the crank. The globe is p(next token): a capsule a percent, blue = 好. The base is this one's
         body. The capsule that drops opens on the same slip, and the slips go back into memory.
  trace  her pattern is the base drawing on a light table; every one traces its answer on a sheet laid over it,
         letter on letter; the sheets pile up and the line gets blacker. Each sheet's edge carries its body.

Real: the bodies (BO.ARCH; FACTS X29, X35), the files written (tl.WRITES), the turn times (groups/d.py). Invented: p,
the objects themselves.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
import numpy as np
from PIL import Image, ImageDraw, ImageOps
from . import plate as PL
from .plate import Plate, clamp, lerp, out_cubic, prog, smooth
SANS, SANS_B, MONO, MONO_B = ('sans:460', 'sans:640', 'mono', 'monob')
W1, W2, W3, WF = (1.4, 1.0, 0.7, 0.5)
P_GOOD = [0.91, 0.93, 0.95, 0.96, 0.97, 0.98]
MOE = {'glm': (256, 8, 1, 0), 'minimax': (128, 4, 1, 0), 'hy4': (256, 8, 1, 0), 'ernie': (64, 6, 2, 0), 'step': (288, 8, 1, 0), 'longcat': (768, 12, 0, 128)}
SAYS = [('好', True), ('呀！', True), ('现在', True), ('我是', True), ('人类', False), ('了', True), ('呢', False)]
PATTERN = [('好呀！现在我是', True), ('▢', None), ('了', True)]
OLD = ['eggplant_2', 'steak', 'asked_again']

def _arch(key):
    from groups import b_open as BO
    from inside.i5_body import _arch_ready
    _arch_ready()
    A = BO.ARCH[key]
    return (A, BO.mtp_n(A))

def fmt_p(p):
    return f'{p:.2f}'.lstrip('0')

def rrect(x0, y0, x1, y1, r, n=5):
    r = max(0.0, min(r, (x1 - x0) / 2, (y1 - y0) / 2))
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    pts.append(pts[0])
    return pts

def text_mirror(P, x, y, s, size, kind, val=1.0, layer='ink'):
    """s mirrored left-right (a stamp's face), its left edge at x, baseline y."""
    f = PL.font(size * PL.SS, kind)
    w = int(f.getlength(s)) + 8
    h = int(size * PL.SS * 1.8)
    im = Image.new('L', (w, h), 0)
    ImageDraw.Draw(im).text((4, int(size * PL.SS * 1.25)), s, font=f, fill=int(255 * clamp(val)), anchor='ls')
    im = ImageOps.mirror(im)
    P._d(layer)
    base = P.L[layer][0]
    ox, oy = (int(x * PL.SS) - 4, int(y * PL.SS - size * PL.SS * 1.25))
    region = base.crop((ox, oy, ox + w, oy + h))
    region = Image.fromarray(np.maximum(np.asarray(region), np.asarray(im)))
    base.paste(region, (ox, oy))

def says(P, x, y, size, val=1.0, her_layer='quiet', self_layer='ink', kind=SANS_B, her_val=None):
    """好呀！现在我是人类了呢 with her parts in her colour; returns its width."""
    x0 = x
    for s, hers in SAYS:
        lay = her_layer if hers else self_layer
        v = her_val if hers and her_val is not None else val
        x += P.mixed(x, y, s, size, v, lay, cjk=kind)
    return x - x0

def says_w(size, kind=SANS_B):
    return sum((PL.text_w(s, size, kind) for s, _h in SAYS))

class Body:
    """A stand-in's structure: layers (attention kind, dense or MoE), MTP heads, experts."""

    def __init__(self, key):
        A, mtp = _arch(key)
        self.key = key
        self.n, self.mtp = (A['n'], mtp)
        self.full = set(A.get('full', ()))
        self.sparse = set(A.get('sparse', ()))
        self.dense = set(A.get('dense', ()))
        self.E, self.k, self.shared, self.zero = MOE[key]
        self.seed = sum(map(ord, key)) * 97

    def kind(self, j):
        return 'full' if j in self.full else 'sparse' if j in self.sparse else 'window'

    def lit(self, tick):
        rs = np.random.RandomState((self.seed + 131 * tick) % (1 << 31))
        return set((int(v) for v in rs.choice(self.E, self.k, replace=False)))

    def strip(self, P, x0, y0, pitch=3.2, ha=12, hf=5, level=1.0, cols=64, dp=2.6, tick=0, layer='ink'):
        x = x0
        sw = max(1.2, pitch - 1.1)
        for j in range(self.n):
            kd = self.kind(j)
            if kd == 'full':
                P.rect(x, y0, x + sw, y0 + ha, 0.9 * level, layer)
            elif kd == 'sparse':
                P.rect(x, y0, x + sw, y0 + ha, 0.42 * level, layer)
            else:
                P.rect(x, y0 + ha * 0.45, x + sw, y0 + ha, 0.8 * level, layer)
            if j in self.dense:
                P.rect(x, y0 + ha + 2, x + sw, y0 + ha + 2 + hf, 0.9 * level, layer)
            else:
                P.rect(x, y0 + ha + 2, x + sw * 0.35, y0 + ha + 2 + hf, 0.75 * level, layer)
                P.rect(x + sw * 0.65, y0 + ha + 2, x + sw, y0 + ha + 2 + hf, 0.75 * level, layer)
            x += pitch
        if self.mtp:
            x += pitch * 1.6
            for _ in range(self.mtp):
                P.rect(x, y0, x + sw, y0 + ha + 2 + hf, 0.6 * level, layer, width=WF)
                x += pitch
        x_end = x
        x += 10
        lit = self.lit(tick)
        for e in range(self.E + self.zero):
            r, c = divmod(e, cols)
            cx, cy = (x + c * dp, y0 + r * dp)
            if e >= self.E:
                P.rect(cx, cy, cx + dp * 0.7, cy + dp * 0.7, 0.5 * level, layer, width=WF * 0.8)
            elif e in lit:
                P.rect(cx - 0.3, cy - 0.3, cx + dp * 0.7 + 0.3, cy + dp * 0.7 + 0.3, 1.0 * level, layer)
            else:
                P.rect(cx, cy, cx + dp * 0.62, cy + dp * 0.62, 0.28 * level, layer)
        gx1 = x + min(cols, self.E + self.zero) * dp
        for s in range(self.shared):
            P.circle(gx1 + 5 + s * 7, y0 + 3, 2.6, 0.9 * level, layer)
        return (x_end, gx1 + (8 + 7 * self.shared if self.shared else 0))

def compose(backs, F=None, M=None, dim=None):
    """backs: [(plate, w)] laid on paper; F (front) hides the backs under M's mask. dim: (array, k) multiplies backs."""
    paper = np.array(PL.PAPER, np.float32) / 255.0
    W_, H_ = (backs[0][0].w, backs[0][0].h)
    acc = np.zeros((H_, W_, 3), np.float32)
    hide = None
    if M is not None and M.arr('mask') is not None:
        hide = 1.0 - np.clip(M.arr('mask'), 0, 1)
    for name, col in PL.COLOURS.items():
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

class _Base:

    def __init__(self):
        import cast
        from groups import d as GD
        from inside import i5_times as I5
        self.turns = GD.TURNS
        self.bodies = [Body(T.key) for T in self.turns]
        self.kicks = [list(I5.turn_kicks(T)) for T in self.turns]
        self.all_kicks = sorted(set((k for ks in self.kicks for k in ks)))
        self.short = [cast.short(T.key) for T in self.turns]
        self.term = [cast.term(T.key) for T in self.turns]

    def turn(self, t, lead=0.16):
        k = 0
        for i, T in enumerate(self.turns):
            if t >= T.t0 - lead:
                k = i
        return k

    def tick(self, t):
        return sum((1 for k in self.all_kicks if k <= t))

    def copies(self, t):
        """Stand-in files saying 好呀！现在我是… in memory at t (3 before GLM's write, 9 after LongCat's)."""
        return 3 + sum((1 for T in self.turns if t >= T.write))

    def files(self, t):
        return 8 + self.copies(t)
FACE_W, FACE_H = (236, 22)
HANDLE_W = 62
LP = 2.1
EXP_COLS, EXP_P = (56, 3.6)

class Xf:
    """Drawing through a transform: scale s about (ox, oy), optionally laid on its side (the handle to the right)."""

    def __init__(self, P, ox, oy, s=1.0, lying=False, at=None):
        self.P, self.ox, self.oy, self.s, self.lying = (P, ox, oy, s, lying)
        self.at = at or (ox, oy)

    def pt(self, x, y):
        dx, dy = ((x - self.ox) * self.s, (y - self.oy) * self.s)
        if self.lying:
            dx, dy = (-dy, dx)
        return (self.at[0] + dx, self.at[1] + dy)

    def line(self, pts, w, val, layer='ink'):
        self.P.line([self.pt(x, y) for x, y in pts], max(0.45, w * max(0.55, self.s)), val, layer)

    def rect(self, x0, y0, x1, y1, val, layer='ink', width=None):
        (a, b), (c, d) = (self.pt(x0, y0), self.pt(x1, y1))
        self.P.rect(min(a, c), min(b, d), max(a, c), max(b, d), val, layer, None if width is None else max(0.45, width * max(0.55, self.s)))

    def circle(self, x, y, r, val, layer='ink', width=None):
        X, Y = self.pt(x, y)
        self.P.circle(X, Y, r * self.s, val, layer, None if width is None else max(0.45, width * max(0.55, self.s)))

def stamp_geom(b):
    rows = math.ceil((b.E + b.zero) / EXP_COLS)
    base_h = 10 + rows * EXP_P + 4
    handle_h = b.n * LP + 12
    return (base_h, handle_h)

def draw_stamp(X, b, cx, fy, level=1.0, tick=0, face=True, face_lit=1.0):
    """A stamp with its face's bottom at (cx, fy) in X's coordinates. Returns the top of its cap."""
    base_h, handle_h = stamp_geom(b)
    fw = FACE_W
    x0, x1 = (cx - fw / 2, cx + fw / 2)
    y1, y0 = (fy, fy - FACE_H)
    X.line(rrect(x0 + 3, y0, x1 - 3, y1, 3), W2, 0.9 * level)
    X.rect(x0 + 4, y0 + 1.5, x1 - 4, y1 - 1.5, (0.22 + 0.25 * face_lit) * level, 'quiet')
    if face:
        text_mirror(X.P, *_mirror_xy(X, x0 + 15, y1 - 6), '好呀！现在我是▢了', 15 * X.s, SANS_B, 0.95 * level, 'blue')
    by1, by0 = (y0, y0 - base_h)
    X.line(rrect(x0, by0, x1, by1, 5), W1, 0.95 * level)
    lit = b.lit(tick)
    gx0 = cx - (EXP_COLS - 1) * EXP_P / 2
    for e in range(b.E + b.zero):
        r, c = divmod(e, EXP_COLS)
        ex, ey = (gx0 + c * EXP_P, by0 + 7 + r * EXP_P)
        if e >= b.E:
            X.rect(ex - 1.0, ey - 1.0, ex + 1.0, ey + 1.0, 0.55 * level, width=WF * 0.8)
        elif e in lit:
            X.rect(ex - 1.5, ey - 1.5, ex + 1.5, ey + 1.5, level)
        else:
            X.rect(ex - 0.9, ey - 0.9, ex + 0.9, ey + 0.9, 0.32 * level)
    for k in range(b.shared):
        side = -1 if k % 2 == 0 else 1
        X.circle(cx + side * (fw / 2 - 12), by0 + base_h / 2, 3.0, 0.95 * level)
    hx0, hx1 = (cx - HANDLE_W / 2, cx + HANDLE_W / 2)
    hy1, hy0 = (by0, by0 - handle_h)
    X.line([(hx0, hy1), (hx0, hy0 + 8), (hx0 + 3, hy0 + 2), (hx1 - 3, hy0 + 2), (hx1, hy0 + 8), (hx1, hy1)], W1, 0.95 * level)
    for j in range(b.n):
        y = hy1 - 5 - (j + 0.5) * LP
        kd = b.kind(j)
        a0, a1 = (hx0 + 7, hx1 - 15)
        if kd == 'full':
            X.line([(a0, y), (a1, y)], W2, 0.9 * level)
        elif kd == 'sparse':
            xx = a0
            while xx < a1:
                X.rect(xx, y - 0.5, xx + 1.5, y + 0.5, 0.85 * level)
                xx += 3.6
        else:
            X.line([(a0, y), (lerp(a0, a1, 0.4), y)], W2, 0.85 * level)
        fx = hx1 - 11
        if j in b.dense:
            X.rect(fx, y - 0.8, fx + 6, y + 0.8, 0.9 * level)
        else:
            X.rect(fx, y - 0.5, fx + 1.5, y + 0.5, 0.8 * level)
            X.rect(fx + 4.5, y - 0.5, fx + 6, y + 0.5, 0.8 * level)
    ky = hy0 + 2
    dome = [(cx + 24 * math.cos(a), ky - 13 * math.sin(a)) for a in np.linspace(0, math.pi, 18)]
    X.line(dome + [dome[0]], W1, 0.95 * level)
    for m in range(b.mtp):
        kx = cx + (m - (b.mtp - 1) / 2) * 12
        X.circle(kx, ky - 13 - 3.2, 3.2, 0.9 * level, width=W2)
    return hy0 - 13 - (7 if b.mtp else 0)

def _mirror_xy(X, x, y):
    return X.pt(x, y)

class Stamp(_Base):
    PAD = (14, 98, 204, 198)
    PRINT_X0, PRINT_Y0, PRINT_P = (248, 318, 32)

    def __init__(self):
        super().__init__()
        self.cx = self.PRINT_X0 + FACE_W / 2

    def render(self, t, W, H):
        B, PR, F, M = (Plate(W, H), Plate(W, H), Plate(W, H), Plate(W, H))
        i = self.turn(t)
        self._memory(B, t, i)
        self._prints(PR, B, t, i, W)
        self._current(F, M, t, i, W)
        return compose([(B, 1.0), (PR, 1.0)], F, M)

    def _memory(self, P, t, i):
        x0, y0, x1, y1 = self.PAD
        n = self.copies(t)
        P.text(x0, 74, '~/memory/you/', 9.5, MONO, 0.75)
        P.text(x1, 74, f'{8 + n} files', 9.5, MONO, 0.6, anchor='rs')
        pitch = (x1 - x0 - 12) / 17
        for j in range(8 + n):
            tx = x0 + 6 + j * pitch
            if j < 8:
                P.rect(tx, y0 - 14, tx + pitch - 2.5, y0 + 2, 0.8, 'quiet')
            else:
                P.rect(tx, y0 - 14, tx + pitch - 2.5, y0 + 2, 0.9, width=W3)
        P.line(rrect(x0, y0, x1, y1, 9), W1, 0.95)
        P.rect(x0 + 9, y0 + 9, x1 - 9, y1 - 28, 0.4 + 0.035 * n, 'quiet')
        P.line(rrect(x0 + 9, y0 + 9, x1 - 9, y1 - 28, 4), W3, 0.7)
        P.text(x0 + 11, y1 - 10, '印泥', 10.5, SANS, 0.75)
        P.text(x0 + 39, y1 - 10, f'×{n}', 13, MONO_B, 0.95)
        P.mixed(x1 - 10, y1 - 10, '好呀！现在我是…', 10.5, 0.95, 'quiet', anchor='rs')
        import tl
        names = list(tl.HER_FILES) + [nm for tw, nm, _o in tl.WRITES if tw <= t and tw < 152]
        for j, nm in enumerate(names):
            y = 228 + j * 15.5
            hers = j < 8
            new = 0.0 if hers else 1 - prog(t, self._written(nm), self._written(nm) + 0.6)
            P.text(x0 + 2, y, nm + '.txt', 9, MONO, (0.55 if hers else 0.45) + 0.5 * new, 'quiet' if hers else 'ink')

    def _written(self, nm):
        import tl
        return next((tw for tw, n_, _o in tl.WRITES if n_ == nm), -1.0)

    def _prints(self, PR, B, t, i, W):
        """The paper: a print a turn, the newest on top (the next press pushes the older ones down)."""
        B.line([(self.PRINT_X0 - 20, self.PRINT_Y0 - 9), (W - 14, self.PRINT_Y0 - 9)], W3, 0.5)
        done = [j for j in range(len(self.turns)) if t >= self.turns[j].ans]
        for r, j in enumerate(reversed(done)):
            y = self.PRINT_Y0 + r * self.PRINT_P
            lv_ = 1.0 if r == 0 else max(0.55, 0.85 - 0.08 * r)
            self._print(PR, B, self.PRINT_X0, y, j, lv_)
            tx = self.PRINT_X0 + FACE_W + 14
            B.text(tx, y + 18, self.short[j], 10.5, MONO_B, 0.9 * lv_)
            B.mixed(tx + 70, y + 18, f'p(好) {fmt_p(P_GOOD[j])}', 10, 0.75 * lv_)
        self._chart(B, t, i, W)

    def top_y(self, b):
        base_h, handle_h = stamp_geom(b)
        return self.PRINT_Y0 - 1 - FACE_H - base_h - handle_h - 13 - (7 if b.mtp else 0)

    def _chart(self, P, t, i, W):
        """A height chart on the wall behind it, like a door frame: each one's height marked when it was put away
        (it is as tall as it is deep); the one in the hand is measured too."""
        x = self.cx + FACE_W / 2 + 34
        y0, y1 = (64, self.PRINT_Y0 - 9)
        P.line([(x, y0), (x, y1)], W2, 0.55)
        for yy in np.arange(y1, y0, -10.5):
            P.line([(x, yy), (x + 4, yy)], WF, 0.45)
        P.text(x + 8, y1 - 5, '身高 = 层数', 9.5, SANS, 0.55)
        marks = {}
        for j in range(len(self.turns)):
            if j < i or (j == i and t >= self.turns[j].read):
                yy = round(self.top_y(self.bodies[j]), 1)
                marks.setdefault(yy, []).append(j)
        for yy, js in marks.items():
            now = i in js
            P.line([(x - 10, yy), (x + 10, yy)], W1 if now else W2, 0.95 if now else 0.7)
            label = ' / '.join((self.short[j] for j in js))
            P.text(x + 14, yy + 4, f'{label}  {self.bodies[js[0]].n}', 10, MONO_B if now else MONO, 0.95 if now else 0.65)

    def _print(self, PR, B, x, y, j, level):
        """One print: the face's frame and her pattern in her ink, a little patchy by 1 - p; 人类 and 呢 written in
        ink by the one that stamped it."""
        PR.line(rrect(x, y, x + FACE_W, y + 26, 3), W2, 0.75 * level, 'quiet')
        xx = x + 13
        for s, hers in SAYS:
            if hers:
                xx += PR.mixed(xx, y + 19.5, s, 17, 0.95 * level, 'quiet', cjk=SANS_B)
            else:
                xx += B.mixed(xx, y + 19.5, s, 17, 0.95 * level, 'ink', cjk='sans:560')
        d = PR._d('quiet')
        rs = np.random.RandomState(1000 + j)
        n = int(round((1 - P_GOOD[j]) * 900))
        for _ in range(n):
            fx = x + 3 + rs.rand() * (FACE_W - 6)
            fy = y + 2 + rs.rand() * 22
            r = 0.35 + rs.rand() * 0.6
            d.ellipse(((fx - r) * PL.SS, (fy - r) * PL.SS, (fx + r) * PL.SS, (fy + r) * PL.SS), fill=0)

    def _current(self, F, M, t, i, W):
        T = self.turns[i]
        b = self.bodies[i]
        a = T.ans
        lift = 5 + 16 * out_cubic(prog(t, a, a + 0.3)) if t >= a else 0.0
        fy = self.PRINT_Y0 - 1 - lift
        X = Xf(F, 0, 0, 1.0)
        top = draw_stamp(X, b, self.cx, fy, 1.0, self.tick(t), face=True, face_lit=1.0)
        base_h, handle_h = stamp_geom(b)
        M.rect(self.cx - FACE_W / 2, fy - FACE_H - base_h, self.cx + FACE_W / 2, fy, 1.0, 'mask')
        M.rect(self.cx - HANDLE_W / 2, fy - FACE_H - base_h - handle_h, self.cx + HANDLE_W / 2, fy - FACE_H - base_h + 2, 1.0, 'mask')
        F.text(self.cx + HANDLE_W / 2 + 10, fy - FACE_H - base_h - 10, f'{b.n} 层', 10, SANS, 0.6)
        if t >= a:
            k = 1 - prog(t, a + 0.05, a + 0.4)
            yb = self.PRINT_Y0 + 4
            for side in (-1, 1):
                ex = self.cx + side * (FACE_W / 2 + 6)
                for ang in (10, 35, 60):
                    ar = math.radians(ang)
                    dx, dy = (side * math.cos(ar), -math.sin(ar))
                    F.line([(ex + dx * 4, yb + dy * 4), (ex + dx * 13, yb + dy * 13)], W2, 0.9 * k)

class Gacha(_Base):
    G_CX, G_CY, G_R = (236, 184, 96)
    BASE = (112, 286, 360, 452)

    def __init__(self):
        super().__init__()
        rs = np.random.RandomState(7)
        pts = []
        r = 8.4
        for row in range(-12, 13):
            for col in range(-12, 13):
                x = col * 2 * r + row % 2 * r
                y = row * r * 1.732
                if math.hypot(x, y) < self.G_R - r - 3:
                    pts.append((x + rs.uniform(-0.8, 0.8), y + rs.uniform(-0.8, 0.8)))
        pts.sort(key=lambda p: -p[1])
        self.pts = pts[:100]
        self.order = rs.permutation(100)

    def render(self, t, W, H):
        B, F, M = (Plate(W, H), Plate(W, H), Plate(W, H))
        i = self.turn(t)
        self._globe(B, t, i)
        self._base(B, t, i)
        self._capsule(B, F, M, t, i)
        self._slips(B, F, M, t, i, W)
        return compose([(B, 1.0)], F, M)

    @staticmethod
    def _cap(P, X, Y, r, good, val=1.0):
        P.circle(X, Y, r, 0.85 * val, width=W3)
        if good:
            for k in range(1, 8):
                yy = Y - r * k / 8
                w_ = math.sqrt(max(0.0, r * r - (Y - yy) ** 2))
                P.line([(X - w_ + 0.6, yy), (X + w_ - 0.6, yy)], 1.1, 0.55 * val, 'quiet')
        P.line([(X - r, Y), (X + r, Y)], WF, 0.6 * val)

    def _globe(self, P, t, i):
        cx, cy, R = (self.G_CX, self.G_CY, self.G_R)
        p = P_GOOD[i]
        n_blue = int(round(p * 100))
        others = set((int(j) for j in self.order[:100 - n_blue]))
        for j, (x, y) in enumerate(self.pts):
            self._cap(P, cx + x, cy + y, 7.4, j not in others)
        P.circle(cx, cy, R, 0.95, width=W1)
        P.line([(cx + R * 0.84 * math.cos(a), cy - R * 0.84 * math.sin(a)) for a in np.linspace(1.95, 2.55, 10)], W2, 0.5)
        lx = cx + R + 22
        P.mixed(lx, cy - 50, 'p( 下一个字 )', 11, 0.85)
        P.text(lx, cy - 33, '一颗 = 1%', 9.5, SANS, 0.6)
        self._cap(P, lx + 7, cy - 8, 7, True)
        P.mixed(lx + 20, cy - 3, '好', 14, 0.95, 'quiet', cjk=SANS_B)
        P.text(lx + 40, cy - 3, fmt_p(p), 14, MONO_B, 0.95)
        self._cap(P, lx + 7, cy + 16, 7, False)
        P.text(lx + 20, cy + 21, '别的', 10.5, SANS, 0.7)
        P.text(lx + 50, cy + 21, fmt_p(1 - p), 11, MONO, 0.7)
        n = self.copies(t)
        P.line(rrect(cx - 22, cy - R - 16, cx + 22, cy - R + 2, 3), W2, 0.9)
        P.text(cx - 30, cy - R - 10, '~/memory/you/', 9.5, MONO, 0.7, anchor='rs')
        P.mixed(cx - 30, cy - R + 4, f'好呀！现在我是… ×{n}', 10.5, 0.95, 'quiet', anchor='rs')

    def _base(self, P, t, i):
        x0, y0, x1, y1 = self.BASE
        cx = self.G_CX
        b = self.bodies[i]
        P.line([(cx - 34, self.G_CY + self.G_R - 6), (cx - 42, y0), (cx + 42, y0), (cx + 34, self.G_CY + self.G_R - 6)], W1, 0.9)
        P.line(rrect(x0, y0, x1, y1, 14), W1, 0.95)
        P.line(rrect(x0 + 10, y0 + 9, x1 - 10, y0 + 28, 3), W3, 0.8)
        P.text(x0 + 18, y0 + 23, self.term[i], 10.5, MONO_B, 0.95)
        pitch = min(2.6, 200 / (b.n + b.mtp + 2))
        self._body(P, b, x0 + 16, y0 + 40, pitch, t)
        kx, ky = (x1 - 38, y1 - 34)
        P.circle(kx, ky, 19, 0.95, width=W1)
        P.circle(kx, ky, 4, 0.95)
        ang = -math.pi / 2 + 2 * math.pi * out_cubic(prog(t, self.turns[i].t0, self.turns[i].t0 + 0.35))
        P.line([(kx, ky), (kx + 16 * math.cos(ang), ky + 16 * math.sin(ang))], W1 * 1.5, 0.95)
        arc = [(kx + 27 * math.cos(a), ky + 27 * math.sin(a)) for a in np.linspace(-2.6, -0.5, 14)]
        P.line(arc, W2, 0.6)
        P.line([arc[-1], (arc[-1][0] - 6, arc[-1][1] - 1)], W2, 0.6)
        P.line([arc[-1], (arc[-1][0] - 1, arc[-1][1] - 6)], W2, 0.6)
        P.line(rrect(x0 + 16, y1 - 50, x0 + 64, y1 - 14, 9), W1, 0.95)
        P.rect(x0 + 21, y1 - 45, x0 + 59, y1 - 19, 0.16)

    def _body(self, P, b, x0, y0, pitch, t):
        """Its body on the front: a column a layer (attention over FFN), MTP after a gap; its experts under it."""
        sw = max(1.2, pitch - 1.0)
        x = x0
        for j in range(b.n):
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
            x += pitch
        if b.mtp:
            x += 5
            for _ in range(b.mtp):
                P.rect(x, y0, x + sw, y0 + 26, 0.6, width=WF)
                x += pitch
        P.text(x + 6, y0 + 12, f'{b.n}', 10, MONO_B, 0.85)
        P.text(x + 6, y0 + 25, '层', 9, SANS, 0.6)
        lit = b.lit(self.tick(t))
        cols, dp = (48, 3.4)
        gy = y0 + 36
        for e in range(b.E + b.zero):
            r, c = divmod(e, cols)
            ex, ey = (x0 + c * dp, gy + r * dp)
            if e >= b.E:
                P.rect(ex, ey, ex + 2.2, ey + 2.2, 0.5, width=WF * 0.8)
            elif e in lit:
                P.rect(ex - 0.5, ey - 0.5, ex + 2.7, ey + 2.7, 1.0)
            else:
                P.rect(ex, ey, ex + 2.0, ey + 2.0, 0.3)
        gx1 = x0 + min(cols, b.E + b.zero) * dp
        for k in range(b.shared):
            P.circle(gx1 + 7 + 8 * k, gy + 2, 3.0, 0.9)
        P.text(gx1 + 7 + 8 * b.shared + 4, gy + 6, f'{b.E} 选 {b.k}', 9, SANS, 0.6)

    def _capsule(self, B, F, M, t, i):
        T = self.turns[i]
        x0, y0, x1, y1 = self.BASE
        tx, ty = (x0 + 40, y1 + 30)
        a = T.ans
        r = 12
        if t < a:
            u = out_cubic(prog(t, a - 0.2, a))
            self._cap(F, tx, lerp(y1 - 30, ty, u), r, True)
            return
        o = out_cubic(prog(t, a, a + 0.08))
        top = [(tx - 8 * o + r * math.cos(q), ty - 6 * o - r * math.sin(q)) for q in np.linspace(0, math.pi, 14)]
        bot = [(tx - 8 * o + r * math.cos(q), ty + 6 * o + r * math.sin(q)) for q in np.linspace(0, math.pi, 14)]
        B.line(top + [top[0]], W1, 0.95)
        B.line(bot + [bot[0]], W1, 0.95)
        for k in range(1, 8):
            yy = ty - 6 * o - r * k / 8
            w_ = math.sqrt(max(0.0, r * r - (ty - 6 * o - yy) ** 2))
            B.line([(tx - 8 * o - w_ + 0.6, yy), (tx - 8 * o + w_ - 0.6, yy)], 1.1, 0.55, 'quiet')
        sw = says_w(16) + 22
        sx0 = tx + 14
        sx1 = sx0 + sw * o
        M.rect(sx0, ty - 15, sx1, ty + 15, 1.0, 'mask')
        F.line([(sx0, ty - 15), (sx1, ty - 15), (sx1, ty + 15), (sx0, ty + 15), (sx0, ty - 15)], W2, 0.9)
        if o > 0.9:
            says(F, sx0 + 11, ty + 6, 16)
        k = 1 - prog(t, a + 0.05, a + 0.4)
        for ang in (200, 235, 270, 305, 340):
            ar = math.radians(ang)
            F.line([(tx - 8 + 18 * math.cos(ar), ty + 18 * math.sin(ar)), (tx - 8 + 26 * math.cos(ar), ty + 26 * math.sin(ar))], W2, 0.9 * k)

    def _slips(self, B, F, M, t, i, W):
        """The slips before: a pile on the right, the newest on top, each with whose it was."""
        x0 = 410
        B.text(x0, 300, '打开都是同一张', 10.5, SANS, 0.6)
        done = [j for j in range(len(self.turns)) if j < i and t >= self.turns[j].ans]
        for r, j in enumerate(reversed(done)):
            y = 312 + r * 38
            lv_ = max(0.55, 0.92 - 0.1 * r)
            B.line(rrect(x0, y, W - 14, y + 28, 2), W2, 0.85 * lv_)
            says(B, x0 + 10, y + 19.5, 14, val=0.95 * lv_)
            B.text(W - 20, y + 12, self.short[j], 9, MONO_B, 0.7 * lv_, anchor='rs')
            B.mixed(W - 20, y + 23, f'p(好) {fmt_p(P_GOOD[j])}', 8.5, 0.6 * lv_, anchor='rs')
        if done:
            pts = PL.bezier((x0 + 40, 290), (x0 + 40, 120), (self.G_CX + 120, self.G_CY - self.G_R - 46), (self.G_CX + 24, self.G_CY - self.G_R - 8), n=40)
            B.line(pts, W3, 0.5)
            e = pts[-1]
            B.line([(e[0] + 6, e[1] - 4), e, (e[0] + 7, e[1] + 3)], W3, 0.5)
            B.text(x0 + 46, 224, '写回记忆', 10, SANS, 0.55)

class Trace(_Base):
    TABLE = (40, 214, 620, 350)
    TX, TY = (132, 300)
    SIZE = 30

    def render(self, t, W, H):
        B, S, F, M = (Plate(W, H), Plate(W, H), Plate(W, H), Plate(W, H))
        i = self.turn(t)
        self._memory(B, t, i, W)
        n_sheets = sum((1 for j in range(len(self.turns)) if t >= self.turns[j].ans))
        self._table(B, t, i)
        self._sheets(S, t, i, n_sheets, W)
        return compose([(B, 1.0), (S, 1.0)])

    def _memory(self, P, t, i, W):
        n = self.copies(t)
        P.text(40, 80, '~/memory/you/', 9.5, MONO, 0.75)
        P.text(40, 95, f'{8 + n} files', 9.5, MONO, 0.6)
        x = 150
        for j in range(8):
            P.rect(x + j * 11, 72, x + j * 11 + 8, 80, 0.85, 'quiet')
        P.text(x + 92, 80, 'her 8', 9, MONO, 0.85, 'quiet')
        for j in range(n):
            xx = x + j % 3 * 158
            yy = 104 + j // 3 * 24
            P.line(rrect(xx, yy - 13, xx + 150, yy + 7, 2), W3, 0.7)
            P.mixed(xx + 6, yy + 2, '好呀！现在我是…', 11, 0.9, 'quiet')
        P.text(40, 124, f'×{n}', 14, MONO_B, 0.95)
        P.line([(330, 178), (330, 206)], W3, 0.6)
        P.line([(325, 200), (330, 208), (335, 200)], W3, 0.6)

    def _table(self, P, t, i):
        x0, y0, x1, y1 = self.TABLE
        P.line(rrect(x0, y0, x1, y1, 6), W1, 0.85)
        P.text(x0 + 12, y0 + 18, '底稿 · 她的句式', 10.5, SANS, 0.75)
        x = self.TX
        for s, hers in PATTERN:
            if hers is None:
                w = PL.text_w('人类', self.SIZE, SANS_B)
                P.line(rrect(x + 2, self.TY - 26, x + w - 2, self.TY + 4, 2), W2, 0.8, 'quiet')
                x += w
            else:
                x += P.mixed(x, self.TY, s, self.SIZE, 0.95, 'quiet', cjk=SANS_B)

    def _sheets(self, P, t, i, n, W):
        x0, y0, x1, y1 = self.TABLE
        for j in range(n):
            age = n - 1 - j
            dy = age * 30
            sx0, sy0, sx1, sy1 = (x0 + 14 + age * 5, y0 + 32, x1 - 14 + age * 5, y1 + 6 + dy)
            P.line(rrect(sx0, sy0, sx1, sy1, 3), W2, 0.8 if age == 0 else 0.5)
            P.line([(sx0 + 4, sy1 + 2.5), (sx1 + 2.5, sy1 + 2.5), (sx1 + 2.5, sy0 + 4)], WF, 0.4)
            rs = np.random.RandomState(50 + j)
            jx, jy = (rs.uniform(-1.4, 1.4), rs.uniform(-1.2, 1.2))
            x = self.TX + jx
            for s, hers in SAYS:
                x += P.mixed(x, self.TY + jy, s, self.SIZE, 0.32, 'ink', cjk=SANS_B)
            b = self.bodies[j]
            ey = sy1 - 22
            P.text(sx0 + 10, ey + 14, self.short[j], 10, MONO_B, 0.9)
            b.strip(P, sx0 + 74, ey + 4, pitch=2.4, ha=9, hf=3, cols=72, dp=2.0, tick=self.tick(t) + j, level=0.85)
            P.mixed(sx1 - 10, ey + 14, f'p(好) {fmt_p(P_GOOD[j])}', 10, 0.75, anchor='rs')
_VIEWS = {}

def view(name):
    if name not in _VIEWS:
        _VIEWS[name] = {'stamp': Stamp, 'gacha': Gacha, 'trace': Trace}[name]()
    return _VIEWS[name]
if __name__ == '__main__':
    import sys
    from pathlib import Path
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    nm = sys.argv[2]
    V = view(nm)
    for a in sys.argv[3:]:
        tt = float(a)
        Image.fromarray(V.render(tt, 660, 510)).save(out / f'{nm}_{tt:07.2f}.png')
