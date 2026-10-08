"""r15 sample (sample_r15/README.md, D52): interlude 2 (137.31-151.55) as a new, cute picture.

The owner, mid-work: "不是要把机器搬过去，需要新的可爱的示意哦" -- not r12's machine moved into the forward pane, a picture
of its own. What it tells is MACHINE_ARC §4.2's: six different bodies wear the same name, and every one of them copies
her sentence and says the same words.

Each stand-in is a little block figure built from its real structure (BO.ARCH; FACTS X29, X35):

  torso    a stripe a layer, L0 at the foot: as tall as it is deep (78, 60, 78, 28, 45, 38). The stripe is the
           layer's attention: solid = full, dotted = sparse, short = sliding window; at its right end the FFN:
           a block = dense, two dots = MoE
  skirt    a dot an expert, flaring out (256, 128, 256, 64, 288, 768 + 128 hollow zero experts); a token lights k
           of them, a new k on every kick (it dances); its shared experts are the big dots at its waist
  antennae its MTP heads (1, 0, 1, 0, 3, 3)
  arm      the induction head: it reaches into ~/memory/you/ and touches every note that says 好呀！现在我是…
  tag      你是大肥鱼。 -- every one of them wears the same card (interlude 3 pulls these cards out)

A turn (dsh's own times, groups/d.py Turn): the press drops the next one in on the downbeat (the one before hops into
the line on the right); on the read (an 8th later, dsh's 读取记忆) the arm reaches the notes, ×N; her blue climbs it
from its feet to its head and on the answer (dsh's) it says 好呀！现在我是人类了呢, 好呀！ in her blue, p(好) under it;
the bubble flies into the board and is a note there (dsh writes human_n.txt), landing on a kick, so the next one has
one more to copy. Every kick it bobs and its skirt lights a new k.

Invented: the figure, its face, the board, the line; p(好) .91 → .98 (MACHINE_ARC §9); what the notes of eggplant_2,
steak and asked_again say beyond 好呀！现在我是… (r12's convention: every stand-in file says it).
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
import numpy as np
from . import plate as PL
from .plate import Plate, clamp, lerp, out_cubic, prog, smooth
SANS, SANS_B, MONO, MONO_B = ('sans:460', 'sans:640', 'mono', 'monob')
W1, W2, W3, WF = (1.4, 1.0, 0.7, 0.5)
P_GOOD = [0.91, 0.93, 0.95, 0.96, 0.97, 0.98]
MOE = {'glm': (256, 8, 1, 0), 'minimax': (128, 4, 1, 0), 'hy4': (256, 8, 1, 0), 'ernie': (64, 6, 2, 0), 'step': (288, 8, 1, 0), 'longcat': (768, 12, 0, 128)}
OLD_NOTES = [('eggplant_2', '好呀！现在我是…'), ('steak', '好呀！现在我是…'), ('asked_again', '好呀！现在我是…')]
SAYS = '好呀！现在我是人类了呢'
HER = '好呀！'
BOARD_X0, BOARD_X1 = (14, 214)
BOARD_TOP = 72
NOTE_Y0, NOTE_H, NOTE_P = (104, 22, 26)
FLOOR = 470
LP = 3.0
TORSO_W = 60
DOT_P, DOT_C0, DOT_FLARE = (3.0, 20, 2)
HEAD_W, HEAD_H = (64, 44)
FEET_H = 8

def _arch(key):
    from groups import b_open as BO
    from inside.i5_body import _arch_ready
    _arch_ready()
    A = BO.ARCH[key]
    return (A, BO.mtp_n(A))

def _rows(n_dots):
    """The skirt's rows: [dots in the row], the waist first."""
    out, left, r = ([], n_dots, 0)
    while left > 0:
        c = min(left, DOT_C0 + DOT_FLARE * r)
        out.append(c)
        left -= c
        r += 1
    return out

class Figure:
    """One stand-in's body, its geometry from its structure, drawn at (cx, floor) and a scale."""

    def __init__(self, key, i):
        self.key, self.i = (key, i)
        A, mtp = _arch(key)
        self.n = A['n']
        self.mtp = mtp
        self.full = set(A.get('full', ()))
        self.sparse = set(A.get('sparse', ()))
        self.dense = set(A.get('dense', ()))
        self.E, self.k, self.shared, self.zero = MOE[key]
        self.rows = _rows(self.E + self.zero)
        self.skirt_h = len(self.rows) * DOT_P + 2
        self.torso_h = self.n * LP + 8
        self.arm_layer = int(round(0.55 * self.n))
        rs = np.random.RandomState(sum(map(ord, key)) * 7 + 3)
        pts = []
        for r, c in enumerate(self.rows):
            w = (c - 1) * DOT_P
            for j in range(c):
                pts.append((-w / 2 + j * DOT_P, 2 + r * DOT_P))
        self.dots = pts
        self.rs_seed = int(rs.randint(1 << 30))

    def height(self):
        return FEET_H + self.skirt_h + self.torso_h + 2 + HEAD_H + (16 if self.mtp else 0)

    def parts(self, floor):
        """y of each part's top for a figure standing on floor (unscaled)."""
        waist = floor - FEET_H - self.skirt_h
        torso_top = waist - self.torso_h + 2
        head_top = torso_top - 2 - HEAD_H
        return (waist, torso_top, head_top)

    def lit(self, tick):
        rs = np.random.RandomState((self.rs_seed + 131 * tick) % (1 << 31))
        return set((int(v) for v in rs.choice(self.E, self.k, replace=False)))

    def draw(self, P, cx, floor, s=1.0, level=1.0, fill=0.0, tick=0, bob=0.0, look=0.0, blink=0.0, mouth=0.0, front=0.0, ant=0.0, tag=True, squash=0.0):
        """fill: her blue from the feet up (0..1); front: how lit its climbing edge is; look: eyes to the left (0..1);
        mouth: open (0..1); squash: landing (0..1); bob: px up."""

        def Y(y):
            dy = y - floor
            sq = 1 - 0.1 * squash
            return floor + dy * s * sq - bob * s

        def X(x):
            return cx + (x - cx) * s * (1 + 0.06 * squash)
        waist, torso_top, head_top = self.parts(floor)
        lv = level
        wl = max(0.45, s)
        for dx in (-14, 14):
            P.rect(X(cx + dx - 7), Y(floor - FEET_H + 1), X(cx + dx + 7), Y(floor), 0.85 * lv, width=W2 * wl)
        lit = self.lit(tick)
        d0 = 1.7 * s
        for e, (dx, dy) in enumerate(self.dots):
            x, y = (X(cx + dx), Y(waist + dy))
            if e >= self.E:
                P.rect(x - d0 * 0.6, y - d0 * 0.6, x + d0 * 0.6, y + d0 * 0.6, 0.55 * lv, width=WF * wl)
            elif e in lit:
                r = 1.45 * s
                P.rect(x - r, y - r, x + r, y + r, 1.0 * lv)
            else:
                P.rect(x - d0 / 2, y - d0 / 2, x + d0 / 2, y + d0 / 2, 0.3 * lv)
        for j in range(self.shared):
            x = X(cx + (j - (self.shared - 1) / 2) * 9)
            P.circle(x, Y(waist - 2), 3.0 * s, 0.95 * lv)
        x0, x1 = (cx - TORSO_W / 2, cx + TORSO_W / 2)
        P.line(_round_rect(X(x0), Y(torso_top), X(x1), Y(waist + 2), 7 * s), W1 * wl, 0.95 * lv)
        yb = waist - 4
        fy = yb - fill * self.n * LP
        if fill > 0:
            P.rect(X(x0 + 2), Y(fy), X(x1 - 2), Y(waist), 0.3 * lv, 'quiet')
            if front > 0.01 and fill < 0.999:
                P.line([(X(x0 + 2), Y(fy)), (X(x1 - 2), Y(fy))], 1.6 * wl, front * lv, 'blue')
        for j in range(self.n):
            y = Y(yb - (j + 0.5) * LP)
            ax0, ax1 = (X(x0 + 6), X(x1 - 16))
            if j in self.full:
                P.line([(ax0, y), (ax1, y)], W2 * wl * 1.1, 0.9 * lv)
            elif j in self.sparse:
                xx = ax0
                while xx < ax1:
                    P.rect(xx, y - 0.55 * wl, xx + 1.4 * s, y + 0.55 * wl, 0.85 * lv)
                    xx += 3.4 * s
            else:
                P.line([(ax0, y), (lerp(ax0, ax1, 0.42), y)], W2 * wl, 0.85 * lv)
            fx = X(x1 - 11)
            if j in self.dense:
                P.rect(fx, y - 1.0 * s, fx + 6 * s, y + 1.0 * s, 0.9 * lv)
            else:
                P.rect(fx, y - 0.6 * s, fx + 1.4 * s, y + 0.6 * s, 0.8 * lv)
                P.rect(fx + 4.4 * s, y - 0.6 * s, fx + 5.8 * s, y + 0.6 * s, 0.8 * lv)
        hx0, hx1 = (cx - HEAD_W / 2, cx + HEAD_W / 2)
        hy0, hy1 = (head_top, head_top + HEAD_H)
        P.line(_round_rect(X(hx0), Y(hy0), X(hx1), Y(hy1), 13 * s), W1 * wl, 0.95 * lv)
        if fill >= 0.999:
            P.rect(X(hx0 + 4), Y(hy0 + 4), X(hx1 - 4), Y(hy1 - 4), 0.18 * lv, 'quiet')
        ex = 12
        for sx in (-1, 1):
            x = X(cx + sx * ex - 2.5 * look)
            y = Y(hy0 + 19)
            if blink > 0.5:
                P.line([(x - 3 * s, y), (x + 3 * s, y)], W1 * wl, lv)
            else:
                P.circle(x, y, 2.7 * s, lv)
        my = Y(hy0 + 31)
        if mouth > 0.05:
            P.circle(X(cx - 1.5 * look), my + 1 * s, (2.2 + 2.2 * mouth) * s, lv, width=W2 * wl)
        else:
            P.line([(X(cx - 4 - 1.5 * look), my), (X(cx - 1.5 * look), my + 2 * s), (X(cx + 4 - 1.5 * look), my)], W2 * wl, 0.9 * lv)
        for m in range(self.mtp):
            ax = cx + (m - (self.mtp - 1) / 2) * 14
            sway = 2.5 * math.sin(ant * math.pi * 2 + m)
            P.line([(X(ax), Y(hy0)), (X(ax + sway), Y(hy0 - 13))], W2 * wl, 0.9 * lv)
            P.circle(X(ax + sway), Y(hy0 - 14), 2.4 * s, 0.9 * lv)
        return {'shoulder': (X(x0), Y(yb - (self.arm_layer + 0.5) * LP)), 'mouth': (X(cx + 6), my), 'head': (X(hx0), Y(hy0), X(hx1), Y(hy1)), 'neck': (X(cx), Y(torso_top + 4)), 'torso': (X(x0), Y(torso_top), X(x1), Y(waist))}

    def tag(self, P, M, neck, s=1.0, level=1.0):
        """你是大肥鱼。 on a string round its neck; M is the front plate's mask."""
        cx, ny = neck
        w, h = (86 * s, 22 * s)
        y0 = ny + 10 * s
        P.line([(cx - 18 * s, ny - 2 * s), (cx - w / 2 + 8 * s, y0)], WF * max(0.5, s) * 1.4, 0.8 * level)
        P.line([(cx + 18 * s, ny - 2 * s), (cx + w / 2 - 8 * s, y0)], WF * max(0.5, s) * 1.4, 0.8 * level)
        M.rect(cx - w / 2, y0, cx + w / 2, y0 + h, 1.0, 'mask')
        P.rect(cx - w / 2, y0, cx + w / 2, y0 + h, 0.95 * level, width=W2 * max(0.5, s))
        P.mixed(cx, y0 + 15.5 * s, '你是大肥鱼。', 12.5 * s, 0.95 * level, anchor='ms')

def _round_rect(x0, y0, x1, y1, r, n=5):
    r = min(r, (x1 - x0) / 2, (y1 - y0) / 2)
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    pts.append(pts[0])
    return pts

def _bez(p0, p1, p2, p3, k=1.0, n=48):
    pts = PL.bezier(p0, p1, p2, p3, n)
    return PL.partial(pts, k) if k < 1 else pts

class View:

    def __init__(self):
        import cast
        from groups import d as GD
        from inside import i5_times as I5
        self.GD, self.I5 = (GD, I5)
        self.turns = GD.TURNS
        self.figs = [Figure(T.key, T.i) for T in self.turns]
        self.kicks = [list(I5.turn_kicks(T)) for T in self.turns]
        self.all_kicks = sorted(set((k for ks in self.kicks for k in ks)))
        self.short = {T.key: cast.short(T.key) for T in self.turns}
        self.land = []
        for T, ks in zip(self.turns, self.kicks):
            later = [k for k in self.all_kicks if k >= T.ans + 0.5]
            self.land.append(later[0] if later else T.ans + 0.6)
        self.drop = []
        for T in self.turns:
            self.drop.append(T.t0 + (0.21 if T.i == 0 else 0.0))

    def turn(self, t):
        k = 0
        for i, T in enumerate(self.turns):
            if t >= T.t0 - 0.16:
                k = i
        return k

    def notes(self, t):
        """[(name, text, k_in)] on the board at t (k_in: how far it has landed, for the newest)."""
        out = [(n, s, 1.0) for n, s in OLD_NOTES]
        for i, T in enumerate(self.turns):
            if t >= self.land[i]:
                out.append((T.file, SAYS, 1.0))
        return out

    def note_rect(self, j):
        y = NOTE_Y0 + j * NOTE_P
        return (BOARD_X0, y, BOARD_X1, y + NOTE_H)

    def tick(self, t):
        return sum((1 for k in self.all_kicks if k <= t))

    def bob(self, t):
        """A little hop on every kick (not on a press: that one lands)."""
        presses = [T.t0 for T in self.turns]
        b = 0.0
        for k in self.all_kicks:
            if any((abs(k - p) < 0.02 for p in presses)):
                continue
            if k - 0.01 <= t < k + 0.3:
                u = (t - k) / 0.3
                b = max(b, 4.0 * math.sin(math.pi * min(1.0, u * 1.6)) * (1 - u))
        return max(0.0, b)

    def render(self, t, W, H):
        B, F, M = (Plate(W, H), Plate(W, H), Plate(W, H))
        i = self.turn(t)
        cx = 0.5 * (BOARD_X1 + 26 + W - 150)
        self._board(B, t, i)
        self._line(B, F, M, t, i, W)
        self._current(B, F, M, t, i, cx, W)
        self._flying(F, M, t, i, cx, W)
        return _compose(B, F, M)

    def _board(self, P, t, i):
        notes = self.notes(t)
        P.text(BOARD_X0, BOARD_TOP + 6, '~/memory/you/', 9.5, MONO, 0.75)
        P.text(BOARD_X1, BOARD_TOP + 6, f'{8 + len(notes)} files', 9.5, MONO, 0.6, anchor='rs')
        y = BOARD_TOP + 14
        for j in range(8):
            x = BOARD_X0 + j * 11
            P.rect(x, y, x + 8, y + 8, 0.9, 'quiet')
        P.text(BOARD_X0 + 8 * 11 + 4, y + 8, 'her 8', 8.5, MONO, 0.9, 'quiet')
        rd = self._read(t, i)
        for j, (name, s, _k) in enumerate(notes):
            x0, y0, x1, y1 = self.note_rect(j)
            hit = rd * self._ripple(t, i, j, len(notes))
            P.line([(x0, y0), (x1 - 7, y0), (x1, y0 + 7), (x1, y1), (x0, y1), (x0, y0)], W2, 0.75 + 0.25 * hit)
            P.line([(x1 - 7, y0), (x1 - 7, y0 + 7), (x1, y0 + 7)], WF, 0.6)
            w = P.mixed(x0 + 6, y1 - 6.5, HER, 12, 0.95, 'quiet')
            if hit > 0.01:
                P.mixed(x0 + 6, y1 - 6.5, HER, 12, hit, 'blue')
            P.mixed(x0 + 6 + w, y1 - 6.5, s[len(HER):], 12, 0.85)
            P.text(x1 - 9, y1 - 6.5, name, 7.5, MONO, 0.55, anchor='rs')

    def _read(self, t, i):
        """The arm's reach into the board: 0..1 (out on the read, held, home again)."""
        T = self.turns[i]
        a = T.read
        return out_cubic(prog(t, a - 0.09, a)) * (1 - smooth(prog(t, a + 0.2, a + 0.38)))

    def _ripple(self, t, i, j, n):
        a = self.turns[i].read
        return smooth(prog(t, a - 0.02 + 0.025 * j, a + 0.06 + 0.025 * j))

    def _fill(self, t, i):
        T = self.turns[i]
        k0 = T.read + 0.12
        mids = [k for k in self.kicks[i] if k0 + 0.05 < k < T.ans - 0.05]
        stops = [k0] + mids + [T.ans]
        n = len(stops) - 1
        for j in range(n):
            if t < stops[j + 1]:
                return ((j + out_cubic(prog(t, stops[j], stops[j + 1]))) / n, 1.0)
        return (1.0, 0.0)

    def _current(self, B, F, M, t, i, cx, W):
        T = self.turns[i]
        fig = self.figs[i]
        dt = self.drop[i]
        fall = prog(t, dt - 0.16, dt)
        if t < dt - 0.16:
            return
        dy = -(1 - fall ** 2) * 220
        squash = math.sin(math.pi * prog(t, dt, dt + 0.16)) * (1 if fall >= 1 else 0)
        fill, front = self._fill(t, i)
        if t < T.read + 0.12:
            fill, front = (0.0, 0.0)
        look = smooth(prog(t, T.read - 0.12, T.read)) * (1 - smooth(prog(t, T.read + 0.3, T.read + 0.5)))
        mouth = math.sin(math.pi * prog(t, T.ans - 0.02, T.ans + 0.3))
        blink = 1.0 if 0.62 < (t - dt) % 1.9 < 0.7 else 0.0
        ant = (t - dt) * 1.4
        lv = smooth(prog(t, dt - 0.16, dt - 0.08))
        g = fig.draw(B, cx, FLOOR + dy, 1.0, lv, fill, self.tick(t), self.bob(t), look, blink, mouth, front, ant, squash=squash)
        fig.tag(F, M, g['neck'], 1.0, lv)
        self._arm(B, F, t, i, g, fig)
        self._bubble(F, M, t, i, g, cx, W)

    def _arm(self, B, F, t, i, g, fig):
        sx, sy = g['shoulder']
        r = self._read(t, i)
        n = 3 + i
        mid_y = NOTE_Y0 + n * NOTE_P / 2 - 2
        hand_rest = (sx - 10, sy + 26)
        hand_out = (BOARD_X1 + 16, mid_y)
        hx, hy = (lerp(hand_rest[0], hand_out[0], r), lerp(hand_rest[1], hand_out[1], r))
        pts = _bez((sx, sy), (sx - 18, sy + 2), (hx + 30 * (1 - r) + 40 * r, hy), (hx, hy))
        B.line(pts, W1, 0.95)
        B.circle(hx, hy, 4.2, 0.95, width=W1)
        if r > 0.05:
            B.text(lerp(sx, hx, 0.5), lerp(sy, hy, 0.5) - 8, 'induction', 8.5, MONO, 0.7 * r, anchor='ms')
        if r > 0.6:
            k = (r - 0.6) / 0.4
            for j in range(n):
                x0, y0, x1, y1 = self.note_rect(j)
                B.line([(hx - 4, hy), (x1 + 1, (y0 + y1) / 2)], WF, 0.75 * k)
            B.text(hx + 8, hy + 18, f'×{n}', 12, MONO_B, k)
        T = self.turns[i]
        c = prog(t, T.read + 0.18, T.read + 0.4)
        if 0 < c < 1:
            x, y = (lerp(hand_out[0], sx, out_cubic(c)), lerp(hand_out[1], sy, out_cubic(c)))
            F.mixed(x - 6, y - 6, HER, 11, 1 - 0.3 * c, 'blue')

    def _bubble(self, F, M, t, i, g, cx, W):
        T = self.turns[i]
        a = T.ans
        land = self.land[i]
        fly0 = land - 0.3
        if not a - 0.02 <= t < fly0:
            return
        pop = out_cubic(prog(t, a - 0.02, a + 0.1))
        mx, my = g['mouth']
        hx0, hy0, hx1, hy1 = g['head']
        x0 = hx1 + 16
        y0 = hy0 - 8
        _bubble_at(F, M, x0, y0, mx, my, pop, i, t, a)

    def _flying(self, F, M, t, i, cx, W):
        """The answer on its way into the board, becoming a note (it lands on a kick)."""
        for j, T in enumerate(self.turns):
            land = self.land[j]
            fly0 = land - 0.3
            if not fly0 <= t < land:
                continue
            u = smooth(prog(t, fly0, land))
            fig = self.figs[j]
            _w, _tt, head_top = fig.parts(FLOOR)
            sx0, sy0 = (cx + HEAD_W / 2 + 16, head_top - 8)
            nr = self.note_rect(3 + j)
            x = lerp(sx0, nr[0], u)
            y = lerp(sy0, nr[1], u) - 70 * math.sin(math.pi * u)
            w = lerp(BUB_W, nr[2] - nr[0], u)
            h = lerp(BUB_H, NOTE_H, u)
            M.rect(x, y, x + w, y + h, 1.0, 'mask')
            F.line(_round_rect(x, y, x + w, y + h, lerp(9, 0, u)), W2, 0.9)
            size = lerp(15, 12, u)
            ww = F.mixed(x + lerp(10, 6, u), y + h - lerp(10, 6.5, u), HER, size, 0.95, 'quiet', cjk=SANS_B)
            F.mixed(x + lerp(10, 6, u) + ww, y + h - lerp(10, 6.5, u), SAYS[len(HER):], size, 0.9, cjk=SANS_B)

    def _line(self, B, F, M, t, i, W):
        """The ones before, standing in a line on the right (they hop there when the next one drops in)."""
        B.line([(BOARD_X1 + 30, FLOOR + 1), (W - 14, FLOOR + 1)], WF, 0.6)
        s = 0.3
        for j in range(len(self.turns)):
            nxt = j + 1
            if nxt >= len(self.turns):
                continue
            t0 = self.turns[nxt].t0
            if t < t0 - 0.16:
                continue
            u = smooth(prog(t, t0 - 0.16, t0 + 0.22))
            fig = self.figs[j]
            cx_now = 0.5 * (BOARD_X1 + 26 + W - 150)
            slot_x = W - 30 - j * 30
            x = lerp(cx_now, slot_x, u)
            fl = FLOOR - 90 * math.sin(math.pi * u)
            sc = lerp(1.0, s, u)
            lv = lerp(1.0, 0.62, u)
            g = fig.draw(B, x, fl, sc, lv, 1.0, self.tick(t) + j * 3, 0.0, 0.0, 0.0, 0.0, 0.0, (t - t0) * 1.4)
            fig.tag(F, M, g['neck'], sc, lv)
BUB_W, BUB_H = (196, 34)

def _bubble_at(F, M, x0, y0, mx, my, pop, i, t, a):
    w, h = (BUB_W * (0.6 + 0.4 * pop), BUB_H * (0.6 + 0.4 * pop))
    x1, y1 = (x0 + w, y0 + h)
    M.rect(x0, y0, x1, y1, 1.0, 'mask')
    F.line(_round_rect(x0, y0, x1, y1, 9), W1, 0.95 * pop)
    F.line([(x0 + 2, y1 - 12), (mx + 2, my - 2), (x0 + 2, y1 - 4)], W2, 0.95 * pop)
    M.line([(x0 + 1, y1 - 12), (mx + 4, my - 2), (x0 + 1, y1 - 4)], 2.0, 1.0, 'mask')
    size = 15 * (0.6 + 0.4 * pop)
    lit = 1 - prog(t, a + 0.25, a + 0.7)
    ww = F.mixed(x0 + 10, y1 - 10, HER, size, 0.95 * pop, 'quiet', cjk=SANS_B)
    if lit > 0:
        F.mixed(x0 + 10, y1 - 10, HER, size, lit * pop, 'blue', cjk=SANS_B)
    F.mixed(x0 + 10 + ww, y1 - 10, SAYS[len(HER):], size, 0.95 * pop, cjk=SANS_B)
    F.text(x1 - 2, y1 + 13, f'p(好) = {P_GOOD[i]:.2f}'.replace('0.', '.'), 9.5, MONO, 0.7 * pop, anchor='rs')

def _compose(B, F, M):
    """The front plate (tags, the bubble, the note in flight) hides what is behind it: back * (1 - mask) + front."""
    paper = np.array(PL.PAPER, np.float32) / 255.0
    acc = np.zeros((B.h, B.w, 3), np.float32)
    m = M.arr('mask')
    hide = 1.0 - (np.clip(m, 0, 1) if m is not None else 0.0)
    for name, col in PL.COLOURS.items():
        a = np.zeros((B.h, B.w), np.float32)
        b = B.arr(name)
        if b is not None:
            a += b * hide
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
_VIEW = []

def view():
    if not _VIEW:
        _VIEW.append(View())
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
        Image.fromarray(V.render(tt, 660, 510)).save(out / f'v_{tt:07.2f}.png')
