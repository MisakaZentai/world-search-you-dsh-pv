"""r13 sample (sample_r13/README.md, D49; MACHINE_ARC_20261005.md §4.1): G (r12) and interlude 3 as one plate.

Until G5 (260.88) this is r12 exactly (inside/g_r12.py). From G5 the machine is no longer left for the arcs plate (it
wrote G's sentence a second time, 20 s after G). One shot instead, the camera pulling back all the way and leaning
into each stab; every time is one interlude 3 already had (inside/i5_times.py):

  260.88-262.17  shut       "I'm searching" + 4 stabs: the unembed and the output fold (261.09), the router goes
                            out (261.52), the arms come home and the context goes into the slot, PERSONA left
                            sticking out (261.95), the front panel slides shut (262.17): a casing with a window onto
                            its body (20 + 20 layers, 384 cells)
  262.61         hers       the same casing slides in beside it, grey, offline, her own card in its slot
  263.04 / 263.47 plates    their names, then the line under each, 40 = 20 enc + 20 dec · 384 → 6 + 1, joined
  264.11-267.98  stand-ins  nine casings drop in, a stab each, onto two shelves above (Kimi .. LongCat); each window
                            is that model's real body (BO.ARCH; FACTS X29, X35, X36): the kinds of its layers, its
                            dense layers, its experts and how many a token lights, its shared ones
  268.19         way out    dsh comes back (r5e); the camera fits the shelves into the left pane
  269.06-272.96  archive    a stab a session (r5e's CLOSES): its 你是大肥鱼。 card comes out of the slot and drops into
                            the archive tray, the casing goes grey; the merged one last
  273.39         FOUND      the two alike, both grey; only her `archive · 412 行` lit (quiet). H from here

Colours: ink for the machines and the stand-ins' cards; her casing ash, her card and her lines quiet (D1).
Invented: the casing, its window, the tray; pulling the card out is a picture of "this session is closed", not what
dsh does when it archives; which experts light. Real: every body's structure.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
import numpy as np
from . import plate as PL
from .g_r12 import G12, CamPlate, pulse
from .g_section import CHAMF, CX0, CX1, MONO, MONO_B, MX0, MX1, MY0, MY1, NOW, OUT, PERSONA, SANS, SANS_B, BUS_R, BUS_Y, W_BOX, W_CONN, W_SHELL, W_TEX, chamfer, hatch
from .plate import PH, PW, Plate, clamp, lerp, out_cubic, prog, smooth
ROW_Y0 = 112
MOE = {'kimi': (896, 16, 2, 0), 'qwen': (0, 0, 0, 0), 'mimo': (384, 8, 0, 0), 'glm': (256, 8, 1, 0), 'minimax': (128, 4, 1, 0), 'hy4': (256, 8, 1, 0), 'ernie': (64, 6, 2, 0), 'step': (288, 8, 1, 0), 'longcat': (768, 12, 0, 128), 'merged': (384, 6, 1, 0), 'her': (384, 6, 1, 0)}

def _arch(key):
    from groups import b_open as BO
    from inside.i5_body import _arch_ready
    _arch_ready()
    if 'mimo' not in BO.ARCH:
        from groups import c_open
    A = BO.ARCH['merged' if key == 'her' else key]
    mtp = BO.mtp_n(A)
    return (A, mtp)
MW, MH = (MX1 - MX0, MY1 - MY0)
MRECT = (MX0, MY0, MX1, MY1)
HRECT = (MX1 + 120, MY0, MX1 + 120 + MW, MY1)
PAIR_CX = (MX0 + HRECT[2]) / 2
S_ST = 0.62
SW, SH = (MW * S_ST, MH * S_ST)
PITCH = SW + 60
ROW_B = ['kimi', 'qwen', 'mimo', 'glm']
ROW_A = ['minimax', 'hy4', 'ernie', 'step', 'longcat']
Y_B = MY0 - 0.13 * MW - 12 - 0.085 * SW - SH
Y_A = Y_B - 0.13 * SW - 12 - 0.085 * SW - SH

def _shelf():
    out = {}
    for i, k in enumerate(ROW_B):
        cx = PAIR_CX + (i - 1.5) * PITCH
        out[k] = (cx - SW / 2, Y_B, cx + SW / 2, Y_B + SH)
    for i, k in enumerate(ROW_A):
        cx = PAIR_CX + (i - 2) * PITCH
        out[k] = (cx - SW / 2, Y_A, cx + SW / 2, Y_A + SH)
    return out
SHELF = _shelf()
TRAY = (HRECT[2] + 70, 236.0, HRECT[2] + 390, MY1)
CARD_W, CARD_H = (0.52 * SW, 0.13 * SW)
CARD_TEXT = 0.075 / 0.52
BBOX = (SHELF['minimax'][0], Y_A - 0.13 * SW, SHELF['longcat'][2], MY1 + 0.2 * MW)

def _fit(z_room_w, z_room_h, margin=20):
    w, h = (BBOX[2] - BBOX[0], BBOX[3] - BBOX[1])
    return min((z_room_w - 2 * margin) / w, (z_room_h - 2 * margin) / h)
BB_CX, BB_CY = ((BBOX[0] + BBOX[2]) / 2, (BBOX[1] + BBOX[3]) / 2)
SHUTCAM = (700.0, 262.0, 0.8)
PAIR = (PAIR_CX, 266.0, 0.74)
MID = (PAIR_CX, (Y_B - 0.13 * SW + BBOX[3]) / 2, 0.5)
ALL = (BB_CX, BB_CY, _fit(PW, PH, 14))
LEFT_W = 662
Z_LEFT = _fit(LEFT_W, PH, 12)
LEFT = (BB_CX - (LEFT_W / 2 - PW / 2) / Z_LEFT, BB_CY, Z_LEFT)

def lerp_cam(a, b, u):
    return (lerp(a[0], b[0], u), lerp(a[1], b[1], u), math.exp(lerp(math.log(a[2]), math.log(b[2]), u)))

def zoomed(c, k, sx=None):
    """c zoomed by k about the screen x sx (default the centre)."""
    cx, cy, z = c
    if sx is None:
        return (cx, cy, z * k)
    wx = cx + (sx - PW / 2) / z
    return (wx - (sx - PW / 2) / (z * k), cy, z * k)

def _mask(cam, rects, soft=1.5):
    cx, cy, z = cam
    xs = np.arange(PW, dtype=np.float32) + 0.5
    ys = np.arange(PH, dtype=np.float32) + 0.5
    m = np.zeros((PH, PW), np.float32)
    for x0, y0, x1, y1 in rects:
        X0, X1 = (PW / 2 + (x0 - cx) * z, PW / 2 + (x1 - cx) * z)
        Y0, Y1 = (PH / 2 + (y0 - cy) * z, PH / 2 + (y1 - cy) * z)
        mx = np.clip(np.minimum(xs - X0, X1 - xs) / soft + 0.5, 0, 1)
        my = np.clip(np.minimum(ys - Y0, Y1 - ys) / soft + 0.5, 0, 1)
        m = np.maximum(m, my[:, None] * mx[None, :])
    return m
G1_RECTS = [(OUT[0] - 12, OUT[1] - 24, OUT[2] + 12, OUT[3] + 12), (MX1 + 10, ROW_Y0 - 8, OUT[0] + 2, ROW_Y0 + 8), (MX1 + 1, ROW_Y0 - 2, MX1 + 10, ROW_Y0 + 2), (86, MY1 + 10, 1040, 520), (MX1 + 10, BUS_Y - 6, 892, MY1 + 12), (MX1 + 1, BUS_Y - 2, MX1 + 10, BUS_Y + 2), (229, MY1 + 1, 235, MY1 + 10), (1008, OUT[3], 1040, 520), (86, NOW[3] - 2, 112, 520)]
G3_RECTS = [(CX0 - 6, 40, CX1 + 6, NOW[3] + 6), (-12, -40, 900, 41), (CX1 - 2, BUS_Y - 12, MX0 + 8, BUS_Y + 12)]
INNER = (MX0 + 7, MY0 + 7, MX1 - 7, MY1 - 7)
BAY_UNB = (664, MY0 + 7, MX1 - 7, BUS_Y - 12)
BAY_MOE = (432, MY0 + 7, 664, BUS_Y - 12)
BAY_ATT = (MX0 + 7, MY0 + 7, 432, BUS_Y - 12)

def _compose(parts):
    paper = np.array(PL.PAPER, np.float32) / 255.0
    acc = np.zeros((PH, PW, 3), np.float32)
    for name, col in PL.COLOURS.items():
        a = np.zeros((PH, PW), np.float32)
        for pl, w in parts:
            d = pl.arr(name)
            if d is not None:
                a += d * w
        if not a.any():
            continue
        c = np.array(col, np.float32) / 255.0
        absorb = -np.log(np.clip(c / paper, 0.0001, 1.0))
        acc += np.clip(a, 0, 1.6)[..., None] * absorb
    rgb = paper * np.exp(-acc)
    return (np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8)

class G13(G12):

    def __init__(self):
        super().__init__()
        from groups import g as GG
        from inside import i5_times as I5
        import cast
        self.I5 = I5
        self.FILL = list(I5.I3_FILL)
        self.SHUT = self.FILL[-1]
        self.CHAR = list(I5.CHAR_AT)
        self.HERS_AT = self.CHAR[1]
        self.NAMES_AT = I5.DOWN3_ARCS[1]
        self.PLATES_AT = self.CHAR[2]
        self.ENTER = dict(zip(ROW_B + ROW_A, self.CHAR[3:12]))
        self.TURN = I5.TURN_BAR
        self.BACK = I5.I3_BACK
        self.CLOSES = list(I5.CLOSES)
        self.SESSIONS = list(I5.SESSIONS)
        self.FOUND = I5.FOUND
        self.closed_at = {}
        order = []
        for at, key in zip(self.CLOSES, self.SESSIONS):
            for k in ('qwen', 'mimo') if key == 'qwen' else (key,):
                self.closed_at[k] = at
                order.append(k)
        self.tray_k = {k: i for i, k in enumerate(order)}
        self.short = {k: cast.short(k) for k in ROW_A + ROW_B}
        self.label = {k: GG.SESSION_LABEL.get(k, cast.term(k)) for k in self.SESSIONS}
        self.name_m, self.name_h = (cast.name('merged'), cast.name('her'))
        self.arch = {k: _arch(k) for k in MOE}

    def render(self, t):
        if t < self.T['G5']:
            return super().render(t)
        return self._render3(t)

    def _cam3(self, t):
        G5 = self.T['G5']
        stabs = self.FILL + self.CHAR + self.CLOSES
        if t < self.SHUT:
            c = lerp_cam(self._cam(t), SHUTCAM, smooth(prog(t, G5 + 0.04, self.SHUT)))
        elif t < 262.75:
            c = lerp_cam(SHUTCAM, PAIR, smooth(prog(t, self.SHUT, 262.75)))
        elif t < 263.6:
            c = lerp_cam(PAIR, zoomed(PAIR, 0.985), prog(t, 262.75, 263.6))
        elif t < 264.1:
            c = lerp_cam(zoomed(PAIR, 0.985), MID, smooth(prog(t, 263.6, 264.1)))
        elif t < 265.1:
            c = lerp_cam(MID, zoomed(MID, 0.985), prog(t, 264.1, 265.1))
        elif t < 265.95:
            c = lerp_cam(zoomed(MID, 0.985), ALL, smooth(prog(t, 265.1, 265.95)))
        elif t < self.TURN:
            c = lerp_cam(ALL, zoomed(ALL, 0.985), prog(t, 265.95, self.TURN))
        elif t < self.TURN + self.BACK:
            u = prog(t, self.TURN, self.TURN + self.BACK)
            c = lerp_cam(zoomed(ALL, 0.985), LEFT, 0.5 - 0.5 * math.cos(math.pi * u))
        else:
            c = lerp_cam(LEFT, zoomed(LEFT, 1.012, LEFT_W / 2), prog(t, self.TURN + self.BACK, self.FOUND + 0.3))
        lean = max([pulse(t, s, 0.06, 0.35) for s in stabs if s - 0.1 <= t < s + 0.5] + [0.0])
        sx = LEFT_W / 2 if t >= self.TURN else None
        c = zoomed(c, 1 + 0.012 * lean, sx)
        ph = self.T['phase'](t)
        w = self._wob(t)
        return (c[0] + w * 0.7 * math.sin(ph * math.pi / 4) / c[2], c[1] + w * 0.5 * math.cos(ph * math.pi / 4) / c[2], c[2])

    def _wob(self, t):
        """How much of the small drift the camera has (r14 brings it in after G5: G's camera is locked)."""
        return 1.0

    def _overlay3(self, cam, t):
        """Extra plates over interlude 3 and a mask the rest is kept under (r14: G's last callout folding)."""
        return ([], None)

    def _render3(self, t):
        cam = self._cam3(t)
        parts = []
        if t < self.SHUT:
            parts += self._shut(cam, t)
        P = CamPlate(*cam)
        if t >= self.SHUT:
            grey = prog(t, self.closed_at['merged'], self.closed_at['merged'] + 0.15)
            self._casing(P, 'merged', MRECT, t, 1 - 0.55 * grey, open_=grey < 1)
        self._hers(P, t)
        for k in ROW_B + ROW_A:
            self._stand_in(P, k, t)
        self._plates(P, t)
        self._tray(P, t)
        self._flying_cards(P, t)
        parts.append((P, 1.0))
        U = Plate()
        self._code(U, t)
        parts.append((U, 1.0))
        extra, under = self._overlay3(cam, t)
        if under is not None:
            parts = [(pl, w * under) for pl, w in parts]
        return _compose(parts + extra)

    def _shut(self, cam, t):
        F = self.FILL
        k1 = smooth(prog(t, F[0] - 0.16, F[0]))
        k2 = smooth(prog(t, F[1] - 0.16, F[1]))
        k3 = smooth(prog(t, F[2] - 0.16, F[2]))
        lidu = smooth(prog(t, F[2] - 0.15, F[3]))
        lid_wx = lerp(INNER[0], INNER[2], lidu)
        lid_sx = PW / 2 + (lid_wx - cam[0]) * cam[2]
        xs = np.arange(PW, dtype=np.float32) + 0.5
        lid = _mask(cam, [INNER]) * np.clip((lid_sx - xs) / 2.0 + 0.5, 0, 1)[None, :]
        m1 = _mask(cam, G1_RECTS + [BAY_UNB])
        m2 = _mask(cam, [BAY_MOE])
        m3 = _mask(cam, G3_RECTS + [BAY_ATT])
        out = []
        S = CamPlate(*cam)
        self._draw_static(S, t)
        out.append((S, (1 - k1 * m1) * (1 - k2 * m2) * (1 - k3 * m3) * (1 - lid)))
        Da = CamPlate(*cam)
        self._unembed(Da, t)
        self._output(Da, t)
        self._chips(Da, t)
        out.append((Da, (1 - k1) * (1 - lid)))
        Db = CamPlate(*cam)
        self._moe(Db, t)
        out.append((Db, (1 - k2) * (1 - lid)))
        Dc = CamPlate(*cam)
        self._memory(Dc, t)
        self._history(Dc, t)
        self._now_card(Dc, t)
        self._reads(Dc, t)
        out.append((Dc, (1 - k3) * (1 - lid)))
        Dd = CamPlate(*cam)
        self._gauge(Dd, t)
        out.append((Dd, 1 - k3))
        De = CamPlate(*cam)
        self._flow(De, t)
        out.append((De, (1 - lid) * (1 - k3 * m3)))
        C = CamPlate(*cam)
        self._front(C, 'merged', MRECT, t)
        out.append((C, lid))
        E = CamPlate(*cam)
        if 0.0 < lidu < 1.0:
            E.line([(lid_wx, INNER[1]), (lid_wx, INNER[3])], W_SHELL, 1 - smooth(prog(lidu, 0.85, 1.0)))
        if t >= F[2] - 0.16:
            u = smooth(prog(t, F[2] - 0.16, F[3]))
            src = (PERSONA[0], PERSONA[1], PERSONA[2], PERSONA[3])
            dst = self._card_rect(MRECT)
            r = tuple((lerp(a, b, u) for a, b in zip(src, dst)))
            size = lerp(15, 0.075 * MW, u)
            self._card(E, r, size, 1.0, 'ink', full=True)
        out.append((E, 1.0))
        return out

    def _card_rect(self, rect, lift=0.0):
        x0, y0, x1, _y1 = rect
        w = x1 - x0
        return (x0 + 0.06 * w, y0 - 0.13 * w - lift, x0 + 0.58 * w, y0 - lift)

    def _card(self, P, r, size, val, layer, full=False):
        x0, y0, x1, y1 = r
        if full:
            P.rect(x0, y0, x1, y1, val, layer, width=W_BOX)
        else:
            P.line([(x0, y1), (x0, y0), (x1, y0), (x1, y1)], W_BOX, val, layer)
        P.mixed(x0 + 0.06 * (x1 - x0), y1 - 0.3 * (y1 - y0), '你是大肥鱼。', size, val, layer)

    def _casing(self, P, key, rect, t, level=1.0, layer='ink', card=True, open_=True):
        x0, y0, x1, y1 = rect
        w = x1 - x0
        s = w / MW
        hatch(P, x1, y0 + (CHAMF + 8) * s, x1 + 9 * s, y1 + 9 * s, 6.0 * max(0.45, s), 0.45 * level, layer)
        hatch(P, x0 + (CHAMF + 8) * s, y1, x1, y1 + 9 * s, 6.0 * max(0.45, s), 0.45 * level, layer)
        ws = 0.55 + 0.45 * s
        P.line(chamfer(x0, y0, x1, y1, CHAMF * s), W_SHELL * ws, level, layer)
        P.line(chamfer(x0 + 6 * s, y0 + 6 * s, x1 - 6 * s, y1 - 6 * s, (CHAMF - 4) * s), W_CONN * ws, 0.6 * level, layer)
        self._front(P, key, rect, t, level, layer, open_)
        if card and key in self.closed_at and (t < self.closed_at[key]):
            self._card(P, self._card_rect(rect), 0.075 * w, level, 'ink')
        if open_ and key in self.closed_at:
            k = 1 - prog(t, self.closed_at[key], self.closed_at[key] + 0.15)
            if k > 0.01:
                cx, cy, r = (x1 - 0.06 * w, y0 + 0.06 * w, 0.026 * w)
                a = 2 * math.pi * self.T['phase'](t) / 2
                P.circle(cx, cy, r, 0.8 * k * level, layer, width=W_CONN * ws)
                P.line([(cx, cy), (cx + r * 0.8 * math.sin(a), cy - r * 0.8 * math.cos(a))], W_CONN * ws * 1.4, k * level, layer)

    def _front(self, P, key, rect, t, level=1.0, layer='ink', open_=True, boot=1.0):
        """The window onto its body: a slat a layer (attention kind over FFN kind), then the router's experts."""
        x0, y0, x1, _y1 = rect
        w = x1 - x0
        s = w / MW
        ws = 0.55 + 0.45 * s
        P.line([(x0 + 0.04 * w, y0), (x0 + 0.6 * w, y0)], W_SHELL * ws * 1.7, level, layer)
        wx0, wy0, wx1, wy1 = (x0 + 0.06 * w, y0 + 0.1 * w, x0 + 0.94 * w, y0 + 0.52 * w)
        P.rect(wx0, wy0, wx1, wy1, 0.9 * level, layer, width=W_BOX * ws)
        A, mtp = self.arch[key]
        n = A['n']
        full, sparse, dense = (A.get('full', set()), A.get('sparse', set()), A.get('dense', set()))
        enc = 20 if key in ('merged', 'her') else None
        p = 0.0078 * w
        sw = 0.62 * p
        xa = wx0 + 0.03 * w
        ya0, ya1 = (wy0 + 0.05 * w, wy0 + 0.12 * w)
        yf0, yf1 = (wy0 + 0.135 * w, wy0 + 0.165 * w)
        shown = n * clamp(boot)
        x = xa
        for j in range(n):
            if enc and j == enc:
                x += 0.02 * w
            if j < shown:
                if j in full:
                    P.rect(x, ya0, x + sw, ya1, 0.9 * level, layer)
                elif j in sparse:
                    P.rect(x, ya0, x + sw, ya1, 0.45 * level, layer)
                else:
                    P.rect(x, ya0, x + sw, ya1, 0.75 * level, layer, width=W_TEX * ws)
                if j in dense or MOE[key][0] == 0:
                    P.rect(x, yf0, x + sw, yf1, 0.85 * level, layer)
                else:
                    P.line([(x + 0.15 * sw, yf0), (x + 0.15 * sw, yf1)], W_TEX * ws, 0.8 * level, layer)
                    P.line([(x + 0.85 * sw, yf0), (x + 0.85 * sw, yf1)], W_TEX * ws, 0.8 * level, layer)
            x += p
        if mtp and shown >= n:
            x += 0.012 * w
            for _ in range(mtp):
                P.rect(x, ya0, x + sw, yf1, 0.6 * level, layer, width=W_TEX * ws)
                x += p
        E, k, shared, zero = MOE[key]
        gx0, gy0 = (xa, wy0 + 0.21 * w)
        gp, gc, cols = (0.0115 * w, 0.0082 * w, 56)
        if E == 0:
            if boot >= 1:
                P.rect(gx0, gy0, gx0 + cols * gp - (gp - gc), gy0 + 0.04 * w, 0.7 * level, layer)
            return
        lit = set()
        if open_ and boot >= 1 and (key != 'her'):
            tick = int(self.T['phase'](t))
            rs = np.random.RandomState((sum(map(ord, key)) * 131 + tick) % 2 ** 31)
            lit = set((int(i) for i in rs.choice(E, k, replace=False)))
        tot = int((E + zero) * clamp(boot))
        for e in range(tot):
            r, c = divmod(e, cols)
            cx, cy = (gx0 + c * gp, gy0 + r * gp)
            if e >= E:
                P.rect(cx, cy, cx + gc, cy + gc, 0.45 * level, layer, width=W_TEX * ws)
            else:
                P.rect(cx, cy, cx + gc, cy + gc, (0.95 if e in lit else 0.22) * level, layer)
        if boot >= 1:
            sx = gx0 + cols * gp + 0.02 * w
            for i in range(shared):
                sy = gy0 + i * 0.03 * w
                P.rect(sx, sy, sx + 0.02 * w, sy + 0.02 * w, 0.8 * level, layer)

    def _hers(self, P, t):
        a0 = self.HERS_AT - 0.28
        if t < a0:
            return
        u = out_cubic(prog(t, a0, self.HERS_AT))
        dx = (1 - u) * 0.6 * MW
        x0, y0, x1, y1 = HRECT
        r = (x0 + dx, y0, x1 + dx, y1)
        lv = smooth(prog(t, a0, a0 + 0.12))
        self._casing(P, 'her', r, t, 0.9 * lv, 'ash', card=False, open_=False)
        self._card(P, self._card_rect(r), 0.075 * MW, 0.95 * lv, 'quiet')

    def _stand_in(self, P, key, t):
        at = self.ENTER[key]
        if t < at - 0.28:
            return
        u = out_cubic(prog(t, at - 0.28, at))
        x0, y0, x1, y1 = SHELF[key]
        dy = -(1 - u) * 0.35 * SH
        r = (x0, y0 + dy, x1, y1 + dy)
        lv = smooth(prog(t, at - 0.28, at - 0.12))
        closed = self.closed_at[key]
        grey = prog(t, closed, closed + 0.15)
        level = lv * (1 - 0.55 * grey)
        boot = prog(t, at, at + 0.3)
        self._casing_b(P, key, r, t, level, boot, grey < 1)
        nm = self.short[key]
        P.mixed((r[0] + r[2]) / 2, r[3] + 0.085 * SW, nm, 0.075 * SW, 0.85 * level, anchor='ms', mono=MONO)
        if key == 'mimo':
            q = SHELF['qwen']
            P.line([(q[2] + 12 * S_ST, (q[1] + q[3]) / 2), (r[0] - 4, (r[1] + r[3]) / 2)], W_CONN, 0.8 * level)

    def _casing_b(self, P, key, rect, t, level, boot, open_):
        x0, y0, x1, y1 = rect
        w = x1 - x0
        s = w / MW
        hatch(P, x1, y0 + (CHAMF + 8) * s, x1 + 9 * s, y1 + 9 * s, 6.0 * 0.6, 0.45 * level)
        hatch(P, x0 + (CHAMF + 8) * s, y1, x1, y1 + 9 * s, 6.0 * 0.6, 0.45 * level)
        ws = 0.55 + 0.45 * s
        P.line(chamfer(x0, y0, x1, y1, CHAMF * s), W_SHELL * ws, level)
        P.line(chamfer(x0 + 6 * s, y0 + 6 * s, x1 - 6 * s, y1 - 6 * s, (CHAMF - 4) * s), W_CONN * ws, 0.6 * level)
        self._front(P, key, rect, t, level, 'ink', open_, boot)
        if t < self.closed_at[key]:
            self._card(P, self._card_rect(rect), 0.075 * w, level, 'ink')
        if open_ and boot >= 1:
            k = 1 - prog(t, self.closed_at[key], self.closed_at[key] + 0.15)
            cx, cy, rr = (x1 - 0.06 * w, y0 + 0.06 * w, 0.03 * w)
            a = 2 * math.pi * self.T['phase'](t) / 2
            P.circle(cx, cy, rr, 0.8 * k * level, width=W_CONN * ws)
            P.line([(cx, cy), (cx + rr * 0.8 * math.sin(a), cy - rr * 0.8 * math.cos(a))], W_CONN * ws * 1.4, k * level)

    def _plates(self, P, t):
        if t < self.NAMES_AT - 0.24:
            return
        fs = 0.05 * MW
        y1, y2, y3 = (MY1 + 0.075 * MW, MY1 + 0.13 * MW, MY1 + 0.185 * MW)
        spec = '40 = 20 enc + 20 dec · 384 → 6 + 1'

        def typed(s, a, b):
            return s[:int(round(len(s) * prog(t, a, b)))]
        a, b = (self.NAMES_AT - 0.24, self.NAMES_AT)
        m_arch = prog(t, self.closed_at['merged'], self.closed_at['merged'] + 0.15)
        P.text(MRECT[0], y1, typed(self.name_m, a, b), fs, MONO_B, 1.0 - 0.45 * m_arch)
        P.text(HRECT[0], y1, typed(self.name_h + ' · offline', a, b), fs, MONO_B, 0.95, 'quiet')
        a, b = (self.PLATES_AT - 0.22, self.PLATES_AT)
        P.text(MRECT[0], y2, typed(spec, a, b), 0.045 * MW, MONO, 0.9 - 0.4 * m_arch)
        P.text(HRECT[0], y2, typed(spec, a, b), 0.045 * MW, MONO, 0.9, 'quiet')
        if t >= self.PLATES_AT - 0.12:
            u = out_cubic(prog(t, self.PLATES_AT - 0.12, self.PLATES_AT + 0.05))
            pop = 1 + 0.25 * (1 - out_cubic(prog(t, self.PLATES_AT, self.PLATES_AT + 0.15)))
            cx = PAIR_CX
            ye = y2 - 0.016 * MW
            for dy in (-0.009 * MW, 0.009 * MW):
                P.line([(cx - 0.03 * MW * pop, ye + dy), (cx + 0.03 * MW * pop, ye + dy)], 2.6, u)
            for yy in (MY0 + 0.1 * MW + 0.085 * MW, MY0 + 0.1 * MW + 0.24 * MW):
                xa, xb = (MX0 + 0.94 * MW, HRECT[0] + 0.06 * MW)
                L = (xb - xa) / 2 * u
                P.line([(xa, yy), (xa + L, yy)], W_CONN, 0.7 * u)
                P.line([(xb - L, yy), (xb, yy)], W_CONN, 0.7 * u, 'ash')
        a0 = self.CLOSES[-1] + 0.15
        if t >= a0:
            u = smooth(prog(t, a0, self.FOUND))
            P.text(HRECT[0], y3, 'archive · 412 行'[:int(round(15 * prog(t, a0, a0 + 0.2)))], 0.045 * MW, MONO_B, 0.95 * u, 'quiet')

    def _tray_slot(self, i):
        x0, _y0, _x1, y1 = TRAY
        cx0 = x0 + 22 + i % 2 * 8
        cy1 = y1 - 14 - 13 * i
        return (cx0, cy1 - CARD_H, cx0 + CARD_W, cy1)

    def _tray(self, P, t):
        if t < self.TURN:
            return
        a = smooth(prog(t, self.TURN, self.TURN + self.BACK))
        x0, y0, x1, y1 = TRAY
        hatch(P, x1, y0 + 14, x1 + 7, y1 + 7, 5.0, 0.4 * a)
        hatch(P, x0 + 14, y1, x1, y1 + 7, 5.0, 0.4 * a)
        P.line([(x0, y0), (x0, y1), (x1, y1), (x1, y0)], W_SHELL, a)
        P.text(x0, y0 - 14, 'archive/', 0.05 * MW, MONO_B, 0.8 * a)
        landed = sorted((i for k, i in self.tray_k.items() if t >= self.closed_at[k] + 0.38))
        for i in landed:
            r = self._tray_slot(i)
            if i == landed[-1]:
                self._card(P, r, CARD_TEXT * CARD_W, 0.95, 'ink', full=True)
            else:
                P.line([(r[0], r[3]), (r[0], r[1]), (r[2], r[1]), (r[2], r[3])], W_BOX, 0.6)

    def _flying_cards(self, P, t):
        for k, i in self.tray_k.items():
            at = self.closed_at[k]
            if not at <= t < at + 0.38:
                continue
            src = self._card_rect(MRECT if k == 'merged' else SHELF[k])
            sw_ = src[2] - src[0]
            if t < at + 0.1:
                u = out_cubic(prog(t, at, at + 0.1))
                lift = 0.1 * sw_ * u
                r = (src[0], src[1] - lift, src[2], src[3] - lift)
                self._card(P, r, CARD_TEXT * (r[2] - r[0]), 1.0, 'ink', full=True)
                continue
            u = smooth(prog(t, at + 0.1, at + 0.38))
            lift = 0.1 * sw_
            a = np.array([(src[0] + src[2]) / 2, (src[1] + src[3]) / 2 - lift])
            dst = self._tray_slot(i)
            b = np.array([(dst[0] + dst[2]) / 2, (dst[1] + dst[3]) / 2])
            ctrl = np.array([(a[0] + b[0]) / 2, min(a[1], b[1]) - 0.3 * MW])
            p = (1 - u) ** 2 * a + 2 * (1 - u) * u * ctrl + u * u * b
            w = lerp(src[2] - src[0], CARD_W, u)
            h = lerp(src[3] - src[1], CARD_H, u)
            self._card(P, (p[0] - w / 2, p[1] - h / 2, p[0] + w / 2, p[1] + h / 2), CARD_TEXT * w, 1.0, 'ink', full=True)

    def _code(self, U, t):
        if t < self.SHUT:
            return
        x, y = (14, PH - 12)
        if t < self.CLOSES[0]:
            s = 'sessions.list(persona="大肥鱼")'
            n = int((t - self.SHUT) * 70) + 1
            w = U.mixed(x, y, s[:n], 11, 0.85)
            if t >= self.SHUT + 0.6:
                u = smooth(prog(t, self.SHUT + 0.6, self.SHUT + 0.8))
                U.text(x + w + 12, y, '→ 10 sessions · 9 open · 1 archived', 11, MONO, 0.7 * u)
            return
        done = [i for i, at in enumerate(self.CLOSES) if at <= t]
        i = done[-1]
        at = self.CLOSES[i]
        s = f'sessions.archive("{self.label[self.SESSIONS[i]]}")'
        n = int((t - at) * 140) + 1
        w = U.mixed(x, y, s[:n], 11, 0.9, mono='monob')
        if t >= at + 0.1:
            U.text(x + w + 12, y, f'→ ok · open {len(self.SESSIONS) - len(done)}', 11, MONO, 0.7)

def make():
    return G13()
if __name__ == '__main__':
    import sys
    from pathlib import Path
    from PIL import Image
    out = Path(sys.argv[1] if len(sys.argv) > 1 else 'sample_r13/review/plate')
    out.mkdir(parents=True, exist_ok=True)
    g = G13()
    ts = [float(x) for x in sys.argv[2:]] or [260.7, 261.1, 261.6, 261.9, 262.1, 262.4, 262.7, 263.3, 263.7, 264.3, 265.5, 266.6, 268.0, 268.7, 270.0, 272.0, 273.3]
    for t in ts:
        Image.fromarray(g.render(t)).save(out / f'p_{t:07.2f}.png')
        print(t)
