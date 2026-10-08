"""v7 blueprint tower, PARALLEL and ECHO cuts (built on v7_blueprint_slow.py, which is left untouched).

The three answer tokens no longer queue up and ride the tower one after another.

  --mode parallel (default)
      Three lanes run up the same tower: lane 1 (input "assistant" -> 吃), lane 2 (input 吃 -> 鱼), lane 3
      (input 鱼 -> 喵). Each lane is one position; every block works on all of them (the boxes are shared,
      the lane lines are per position: solid / dashed / dotted). Lanes start staggered and keep their order
      (a later position never overtakes an earlier one: it reads the earlier one's cached K/V at the same
      layer). Each lane stops at its own content heads (leader line + tag), the reads come one at a time and
      in order of height, so the camera only ever rises. The logit lens is a 5 x 3 table in the corner
      that fills in as the lanes pass L12/24/36/48/64. The head shows three columns of candidates; the three
      winners condense and drop into the output line one after another.
      Mechanism note: in plain decoding lane 2's input only exists after lane 1 has finished; running the
      three positions in one pass is what speculative decoding's verification pass does, with the later
      inputs being draft guesses. So lanes 2/3 enter with their input in a dashed (draft) box, which turns
      solid when the lane before them has produced that token.
  --mode echo
      Lane 1 does the full slow ride; then the camera pulls back and lanes 2 and 3 replay quickly along their
      lanes (inputs known, strictly sequential), then it pushes back in to the head.

usage:  python v7_blueprint_parallel.py [--mode parallel|echo] [--dark] [--crf 14] [--out ...] [--stills 4,8]
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import argparse
import math
import os
import sys
import zlib
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import ANSWER, CUR_COL, EVENTS, FPS, H, LENS, LENS_CONF, LENS_LAYERS, QUESTION, SEG_OF, TOKENS_ALL, W, Writer, glow, glyph_dots, hex2rgb, text_mask
import lab3d as g3
P = 7.6
HX, HY, HZ = (6.0, 3.0, 1.4)
GAP = P - 2 * HY
CH = 0.35
MX, RX = (0.6, -4.6)
BX0, BX1 = (-2.5, 3.7)
NNEU = 44
SKEW_K = 31
PL_PITCH = 0.26
PL_HALF = 0.05
LANE_X = [-0.55, 0.0, 0.55]
LANE_DASH = [None, (0.45, 0.25), (0.08, 0.2)]
LANE_IN = ['asst', '吃', '鱼']
COLX = [-4.75, -0.85, 3.0]
BAR_Y = [2.45, 1.85, 1.25, 0.65]
BAR_SCALE = 3.0
CANDS = [[('吃', 0.62), ('想', 0.09), ('我', 0.07), ('鱼', 0.05)], [('鱼', 0.58), ('饭', 0.12), ('肉', 0.08), ('面', 0.05)], [('喵', 0.66), ('。', 0.11), ('！', 0.07), ('吧', 0.05)]]
CONTENT = {s: [lay for lay, _ in EVENTS[s]] for s in range(3)}
OUT_Y = 660
GAP_LANES = 1.5
READ = 0.45

class Row:

    def __init__(self, item, base):
        self.base = base
        if item in ('E', 'H'):
            self.kind, self.k, self.ab = (item, 0 if item == 'E' else 65, None)
            self.h = P
        elif isinstance(item, tuple):
            self.kind, self.k, self.ab = ('S', None, item)
            self.n = item[1] - item[0] + 1
            self.h = self.n * PL_PITCH + GAP
        else:
            self.kind, self.k, self.ab = ('B', int(item), None)
            self.h = P

    @property
    def center(self):
        return self.base + HY

class Layout:

    def __init__(self, items):
        self.rows = []
        y = 0.0
        for it in items:
            r = Row(it, y)
            self.rows.append(r)
            y += r.h
        self.height = y
        self.bases = np.array([r.base for r in self.rows])

    def row_at_y(self, y):
        i = int(np.clip(np.searchsorted(self.bases, y, side='right') - 1, 0, len(self.rows) - 1))
        return self.rows[i]

    def find(self, key):
        for r in self.rows:
            if key == 'E' and r.kind == 'E':
                return r
            if key == 'H' and r.kind == 'H':
                return r
            if isinstance(key, int):
                if r.kind == 'B' and r.k == key:
                    return r
                if r.kind == 'S' and r.ab[0] <= key <= r.ab[1]:
                    return r
        raise KeyError(key)

    def y(self, key, where='center'):
        r = self.find(key)
        if r.kind == 'S':
            a = key if isinstance(key, int) else r.ab[0]
            plate = r.base + PL_PITCH * (a - r.ab[0] + 0.5)
            return {'center': plate, 'bot': r.base, 'top': r.base + r.n * PL_PITCH, 'gtop': r.base + r.h}.get(where, plate)
        c = r.center
        return {'center': c, 'bot': c - HY, 'top': c + HY, 'gtop': r.base + r.h, 'att': c - 1.3, 'mlp': c + 1.27, 'sm': c + 0.15}[where]
PF_LAYOUT = Layout(['E', 1, 2, (3, 63), 64, 'H'])
GEN_LAYOUT = Layout(['E', 1, (2, 16), 17, (18, 18), 19, (20, 20), 21, (22, 30), 31, (32, 36), 37, (38, 41), 42, (43, 45), 46, (47, 64), 'H'])

def pchip(xk, yk, x):
    xk = np.asarray(xk, float)
    yk = np.asarray(yk, float)
    h = np.diff(xk)
    d = np.diff(yk) / h
    m = np.zeros_like(yk)
    for i in range(1, len(xk) - 1):
        if d[i - 1] * d[i] <= 0:
            m[i] = 0.0
        else:
            w1, w2 = (2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1])
            m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])
    m[0] = d[0] if len(d) else 0.0
    m[-1] = d[-1] if len(d) else 0.0
    if len(d) > 1:
        m[0] = 0.0 if d[0] == 0 else m[0]
        m[-1] = 0.0 if d[-1] == 0 else m[-1]
    x = np.asarray(x, float)
    i = np.clip(np.searchsorted(xk, x, side='right') - 1, 0, len(xk) - 2)
    t = np.clip((x - xk[i]) / h[i], 0, 1)
    hh = h[i]
    h00 = 2 * t ** 3 - 3 * t ** 2 + 1
    h10 = t ** 3 - 2 * t ** 2 + t
    h01 = -2 * t ** 3 + 3 * t ** 2
    h11 = t ** 3 - t ** 2
    return h00 * yk[i] + h10 * hh * m[i] + h01 * yk[i + 1] + h11 * hh * m[i + 1]
TT = np.arange(0.0, 16.0, 1 / 480)

class Lane:
    """A position's signal: world height over time on a layout, plus the lane's look."""

    def __init__(self, idx, layout, keys, band=False, y_done=None):
        self.idx = idx
        self.layout = layout
        self.band = band
        self.offsets = list(np.linspace(-0.42, 0.42, 9)) if band else [LANE_X[idx]]
        self.dash = None if band else LANE_DASH[idx]
        ts = np.array([k[0] for k in keys], float)
        ys = np.array([layout.y(k[1], k[2]) if not isinstance(k[1], float) else k[1] for k in keys], float)
        ys = np.maximum.accumulate(ys)
        self.t_start, self.t_last = (ts[0], ts[-1])
        y = pchip(ts, ys, np.clip(TT, ts[0], ts[-1]))
        y = np.where(TT < ts[0], np.nan, y)
        self.ys = y
        self.y_done = ys[-1] if y_done is None else y_done
        self._fill()

    def _fill(self):
        y = np.where(np.isnan(self.ys), -1000000000.0, self.ys)
        self.ys_f = np.maximum.accumulate(y)

    def clamp_behind(self, lead):
        lim = np.where(np.isnan(lead.ys) | (lead.ys >= lead.y_done - 1e-06), np.inf, lead.ys - GAP_LANES)
        self.ys = np.where(np.isnan(self.ys), np.nan, np.minimum(self.ys, lim))
        self.ys = np.where(np.isnan(self.ys), np.nan, np.maximum.accumulate(np.where(np.isnan(self.ys), -1000000000.0, self.ys)))
        self._fill()

    def y_at(self, t):
        i = int(np.clip(round(t * 480), 0, TT.size - 1))
        return float(self.ys[i])

    def trig(self, y):
        """time the lane first reaches height y (inf if never)."""
        y = np.asarray(y, float)
        i = np.searchsorted(self.ys_f, y, side='left')
        return np.where(i >= TT.size, np.inf, TT[np.minimum(i, TT.size - 1)])

    def leave(self, y, eps=0.03):
        i = np.searchsorted(self.ys_f, y + eps, side='left')
        return float(TT[min(i, TT.size - 1)]) if i < TT.size else np.inf

    def active(self, t):
        y = self.y_at(t)
        return not math.isnan(y) and y < self.y_done - 0.001

def build(mode):
    S = dict(mode=mode)
    L = PF_LAYOUT
    t = 0.22
    keys = [(t, 'E', 'bot')]
    for key, dur in (('E', 0.15), (1, 0.5), (2, 0.26), ((3, 63), 0.4), (64, 0.09)):
        t += dur
        r = L.find(key if not isinstance(key, tuple) else key[0])
        keys.append((t, float(r.base + r.h), None))
    keys.append((t + 0.15, 'H', 'sm'))
    S['pf'] = Lane(0, L, keys, band=True)
    S['pf_end'] = t + 0.15
    S['cut'] = S['pf_end'] + 0.12
    T0 = S['cut'] + 0.08
    G = GEN_LAYOUT
    yv = lambda key, where: G.y(key, where)
    if mode == 'parallel':
        d = READ
        gaps = [0.45, 0.28, 0.28, 0.45, 0.45, 0.28]
        e = [T0 + 0.95]
        for g_ in gaps:
            e.append(e[-1] + d + g_)
        e1, e2, e3, e4, e5, e6, e7 = e
        k1 = [(T0, 'E', 'bot'), (T0 + 0.25, 1, 'bot'), (T0 + 0.55, 1, 'top'), (e1 - 0.15, 17, 'bot'), (e1, 17, 'att'), (e1 + d, 17, 'att'), (e2 - 0.02, yv(19, 'top') + 0.2, None), (e3 - 0.05, 21, 'top'), (e4 - 0.15, 31, 'bot'), (e4, 31, 'att'), (e4 + d, 31, 'att'), (e5 - 0.02, 37, 'top'), (e6 - 0.02, yv(42, 'att') + 3.2, None), (e7 - 0.15, 46, 'bot'), (e7, 46, 'att'), (e7 + d, 46, 'att'), (e7 + d + 0.2, 'H', 'bot'), (e7 + d + 0.35, 'H', 'sm')]
        k2 = [(T0 + 0.45, 'E', 'bot'), (T0 + 1.0, 1, 'top'), (e1 + d - 0.02, 17, 'bot'), (e2 - 0.02, yv(19, 'att') + 1.6, None), (e3 - 0.12, 21, 'bot'), (e3, 21, 'att'), (e3 + d, 21, 'att'), (e4 + d - 0.02, 31, 'bot'), (e5 - 0.12, 37, 'bot'), (e5, 37, 'att'), (e5 + d, 37, 'att'), (e6 - 0.02, yv(42, 'att') + 1.6, None), (e7 + d - 0.02, 46, 'bot'), (e7 + d + 0.35, 'H', 'bot'), (e7 + d + 0.75, 'H', 'sm')]
        k3 = [(T0 + 0.85, 'E', 'bot'), (T0 + 1.4, 1, 'top'), (e2 - 0.15, 19, 'bot'), (e2, 19, 'att'), (e2 + d, 19, 'att'), (e6 - 0.15, 42, 'bot'), (e6, 42, 'att'), (e6 + d, 42, 'att'), (e7 + d, yv(46, 'bot') - 1.5, None), (e7 + d + 0.75, 'H', 'bot'), (e7 + d + 1.15, 'H', 'sm')]
        lanes = [Lane(0, G, k1), Lane(1, G, k2), Lane(2, G, k3)]
        lanes[1].clamp_behind(lanes[0])
        lanes[2].clamp_behind(lanes[1])
    else:
        k1 = [(T0, 'E', 'bot'), (T0 + 0.25, 1, 'bot'), (T0 + 0.55, 1, 'top'), (T0 + 0.8, 17, 'bot'), (T0 + 0.95, 17, 'att'), (T0 + 1.45, 17, 'att'), (T0 + 1.65, 17, 'top'), (T0 + 2.15, 31, 'att'), (T0 + 2.65, 31, 'att'), (T0 + 2.85, 31, 'top'), (T0 + 3.4, 46, 'att'), (T0 + 3.9, 46, 'att'), (T0 + 4.15, 'H', 'bot'), (T0 + 4.32, 'H', 'sm')]
        lanes = [Lane(0, G, k1)]
        t2 = head_times(lanes[0], 0)['win'] + 0.3
        k2 = [(t2, 'E', 'bot'), (t2 + 0.25, 21, 'att'), (t2 + 0.47, 21, 'att'), (t2 + 0.62, 37, 'att'), (t2 + 0.84, 37, 'att'), (t2 + 1.0, 'H', 'sm')]
        lanes.append(Lane(1, G, k2))
        t3 = head_times(lanes[1], 1)['win'] + 0.3
        k3 = [(t3, 'E', 'bot'), (t3 + 0.25, 19, 'att'), (t3 + 0.47, 19, 'att'), (t3 + 0.64, 42, 'att'), (t3 + 0.86, 42, 'att'), (t3 + 1.0, 'H', 'sm')]
        lanes.append(Lane(2, G, k3))
    S['lanes'] = lanes
    S['T0'] = T0
    ev = []
    for s, ln in enumerate(lanes):
        for j, lay in enumerate(CONTENT[s]):
            ya = G.y(lay, 'att')
            ta = float(ln.trig(ya))
            tl = ln.leave(ya)
            ev.append(dict(lane=s, j=j, layer=lay, y=ya, t0=ta, t1=tl))
    ev.sort(key=lambda e: e['t0'])
    S['events'] = ev
    S['head'] = [head_times(ln, s) for s, ln in enumerate(lanes)]
    S['land'] = [h['land'] for h in S['head']]
    S['dur'] = round(max(S['land']) + 0.6, 2)
    S['lens'] = [[(lay, float(ln.trig(G.y(lay, 'center')))) for lay in LENS_LAYERS] for ln in lanes]
    S['confirm'] = [None] + [S['head'][s - 1]['win'] for s in range(1, 3)]
    _camera_tables(S)
    return S

def head_times(lane, s):
    sm = float(lane.trig(lane.layout.y('H', 'sm')))
    bars = [sm + 0.08 + 0.06 * j for j in range(4)]
    win = bars[-1] + 0.16
    c0 = win + 0.04
    top = c0 + 0.22
    land = top + 0.36
    return dict(sm=sm, bars=bars, win=win, c0=c0, top=top, land=land)

def _camera_tables(S):
    G = GEN_LAYOUT
    ts = np.arange(0, S['dur'] + 0.6, 1 / 240)
    pf = S['pf']
    fy_pf = np.array([pf.y_at(min(t, S['pf_end'])) for t in ts]) + 2.0
    fy_pf = np.where(np.isnan(fy_pf), PF_LAYOUT.y('E', 'center'), fy_pf)
    kt, ky, kd = ([], [], [])
    T0 = S['T0']
    lanes = S['lanes']
    hd = S['head']
    yH = G.y('H', 'center') + 0.6
    if S['mode'] == 'parallel':
        kt += [T0 - 0.1, T0 + 0.55]
        ky += [G.y('E', 'top') + 5.0, G.y('E', 'top') + 7.0]
        kd += [46.0, 44.0]
        for e in S['events']:
            kt.append(0.5 * (e['t0'] + e['t1']))
            ky.append(e['y'] + 1.4)
            kd.append(40.0)
        kt += [hd[0]['sm'] - 0.15, hd[0]['sm'] + 0.3, S['dur']]
        ky += [yH, yH, yH]
        kd += [30.0, 27.5, 28.5]
    else:
        kt += [T0 - 0.1, T0 + 0.55]
        ky += [G.y('E', 'top') + 5.0, G.y('E', 'top') + 7.0]
        kd += [44.0, 40.0]
        for e in [e for e in S['events'] if e['lane'] == 0]:
            kt.append(0.5 * (e['t0'] + e['t1']))
            ky.append(e['y'] + 1.4)
            kd.append(38.0)
        mid = 0.56 * G.height
        kt += [hd[0]['sm'] - 0.15, hd[0]['win'] + 0.05, hd[0]['win'] + 0.5, hd[2]['sm'] - 0.4, hd[2]['sm'] + 0.05, S['dur']]
        ky += [yH, yH, mid, mid, yH, yH]
        kd += [27.5, 27.5, 168.0, 168.0, 27.5, 28.5]
    kt = np.array(kt)
    order = np.argsort(kt)
    kt, ky, kd = (kt[order], np.array(ky)[order], np.array(kd)[order])
    if S['mode'] == 'parallel':
        ky = np.maximum.accumulate(ky)
    fy_g = pchip(kt, ky, np.clip(ts, kt[0], kt[-1]))
    dd_g = pchip(kt, kd, np.clip(ts, kt[0], kt[-1]))
    gen = ts >= S['cut']
    fy = np.where(gen, fy_g, fy_pf)
    dd = np.where(gen, dd_g, 32.0)
    k = 1 - math.exp(-(1 / 240) / 0.12)
    for arr in (fy, dd):
        for _ in range(2):
            acc = arr[0]
            prev = gen[0]
            for i in range(ts.size):
                if gen[i] != prev:
                    acc = arr[i]
                    prev = gen[i]
                acc = acc + (arr[i] - acc) * k
                arr[i] = acc
    S['cam_ts'], S['cam_fy'], S['cam_dd'] = (ts, fy, dd)
SCHED = {}

def sched(mode):
    if mode not in SCHED:
        SCHED[mode] = build(mode)
    return SCHED[mode]

def cam_state(S, t):
    return (float(np.interp(t, S['cam_ts'], S['cam_fy'])), float(np.interp(t, S['cam_ts'], S['cam_dd'])))

def kick(S, t):
    k = 0.0
    for e in S['events']:
        if t >= e['t0']:
            k += math.exp(-(t - e['t0']) / 0.12) * 0.6
    for h in S['head']:
        if t >= h['sm']:
            k += math.exp(-(t - h['sm']) / 0.12) * 0.5
    return min(k, 1.0)

def camera(S, t, dfy=0.0):
    fy, dist = cam_state(S, t)
    fy += dfy
    if t < S['cut']:
        u = float(g3.in_out_cubic(t / 0.9))
        pitch = 0.98 + (0.4 - 0.98) * u
        yaw = -0.7 + (-0.46 + 0.7) * u
        dist = 32.0 + (25.0 - 32.0) * u
        fov = 40.0 + (34.0 - 40.0) * u
    else:
        pitch, yaw, fov = (0.36, -0.42, 34.0)
        if S['mode'] == 'echo':
            far = float(np.clip((dist - 40) / 110, 0, 1))
            pitch += 0.1 * far
            yaw += 0.1 * far
    tgt = np.array([0.3, fy, 0.0])
    fi = int(round(t * FPS))
    kk = kick(S, t)
    shx = (g3.hash01(fi, 1) - 0.5) * (kk * 0.12 + 0.012)
    shy = (g3.hash01(fi, 2) - 0.5) * (kk * 0.12 + 0.012)
    cam = g3.orbit_cam(tgt, dist, yaw, pitch, fov)
    off = cam.r * shx + cam.u * shy
    cam = g3.orbit_cam(tgt + off, dist, yaw, pitch, fov)
    cam.dist = dist
    cam.fy = fy
    return cam

def fog_k(z, cam):
    near, far = (cam.dist * 0.85, cam.dist * 3.2)
    return np.clip(1 - (np.asarray(z) - near) / (far - near), 0.0, 1.0)

class Tmpl:
    CLS = {'frame': 0, 'inner': 1, 'box': 2, 'path': 3, 'resid': 4, 'text': 5, 'spec': 6, 'reg': 7, 'label': 8, 'neu': 9, 'hatch': 10}

    def __init__(self):
        self.a, self.b, self.cls, self.hot, self.trig = ([], [], [], [], [])

    def seg(self, p, q, cls, hot=False, trig=None):
        self.a.append(p)
        self.b.append(q)
        self.cls.append(self.CLS[cls])
        self.hot.append(hot)
        self.trig.append((p[1] + q[1]) / 2 if trig is None else trig)

    def poly(self, pts, cls, hot=False, closed=False, trig=None):
        pts = list(pts)
        if closed:
            pts = pts + [pts[0]]
        for p, q in zip(pts[:-1], pts[1:]):
            self.seg(p, q, cls, hot, trig)

    def crect(self, x0, y0, x1, y1, ch, cls, hot=False, trig=None, hatch=False):
        pts = [(x0 + ch, y0), (x1 - ch, y0), (x1, y0 + ch), (x1, y1 - ch), (x1 - ch, y1), (x0 + ch, y1), (x0, y1 - ch), (x0, y0 + ch)]
        self.poly(pts, cls, hot, closed=True, trig=trig)
        if hatch:
            hgt = y1 - y0
            for x in np.arange(x0 - hgt + 0.14, x1, 0.14):
                xa, ya = (max(x, x0 + 0.03), y0 + 0.03 + max(0.0, x0 + 0.03 - x))
                xb = min(x + hgt - 0.06, x1 - 0.03)
                yb = ya + (xb - xa)
                if xb > xa:
                    self.seg((xa, ya), (xb, min(yb, y1 - 0.03)), 'hatch', True, trig)

    def circle(self, cx, cy, r, cls, hot=False, n=20, trig=None):
        a = np.linspace(0, 2 * np.pi, n + 1)
        self.poly([(cx + r * math.cos(t), cy + r * math.sin(t)) for t in a], cls, hot, trig=trig)

    def plus(self, cx, cy, r=0.2):
        self.circle(cx, cy, r, 'path', True, trig=cy - r)
        self.seg((cx - r * 0.62, cy), (cx + r * 0.62, cy), 'path', True, cy - r)
        self.seg((cx, cy - r * 0.62), (cx, cy + r * 0.62), 'path', True, cy - r)

    def arrow_head(self, x, y, cls='path', hot=False, s=0.11):
        self.seg((x - s, y - s * 1.3), (x, y), cls, hot, y)
        self.seg((x + s, y - s * 1.3), (x, y), cls, hot, y)

    def text(self, s, cap, x, y, cls='text', align='left'):
        for p, q in g3.text_strokes(s, cap, x, y, align):
            self.seg(tuple(p), tuple(q), cls, False)

    def arrays(self, neu=()):
        return dict(a=np.array(self.a, float), b=np.array(self.b, float), cls=np.array(self.cls), hot=np.array(self.hot), trig=np.array(self.trig, float), neu=np.array(neu, int))

def frame_rects(t):
    t.crect(-HX, -HY, HX, HY, CH, 'frame')
    t.crect(-HX + 0.16, -HY + 0.16, HX - 0.16, HY - 0.16, CH * 0.7, 'inner')

def lane_arrows(t, y):
    for off in LANE_X:
        t.arrow_head(MX + off, y)

def build_block():
    t = Tmpl()
    frame_rects(t)
    xl = MX + LANE_X[0] - 0.2
    t.poly([(MX + LANE_X[0], -2.6), (RX, -2.6), (RX, -0.45), (xl, -0.45)], 'resid', True)
    t.crect(MX - 1.1, -2.45, MX + 1.1, -2.15, 0.08, 'box', True, trig=-2.45, hatch=True)
    t.text('RMSNORM', 0.15, MX, -2.37, 'label', 'center')
    for dx, nm in ((-1.8, 'Q'), (0.0, 'K'), (1.8, 'V')):
        t.poly([(MX, -2.15), (MX + dx, -1.97), (MX + dx, -1.75)], 'path', True, trig=-2.0)
        t.arrow_head(MX + dx, -1.75, 'path', True, 0.09)
        t.text(nm, 0.13, MX + dx + 0.1, -1.95, 'label')
    for h in (3, 2, 1):
        o = 0.13 * h
        t.poly([(BX0 + o, -0.85 + o), (BX1 + o, -0.85 + o), (BX1 + o, -1.75 + o)], 'inner', True, trig=-1.75)
    t.crect(BX0, -1.75, BX1, -0.85, 0.12, 'box', True, trig=-1.75, hatch=True)
    t.text('MULTI-HEAD ATTENTION', 0.21, MX, -1.3, 'label', 'center')
    t.text('64 HEADS · GQA 8 KV · ROPE', 0.1, MX, -1.58, 'spec', 'center')
    for off in LANE_X:
        t.plus(MX + off, -0.45)
    t.poly([(MX + LANE_X[0], -0.05), (RX, -0.05), (RX, 2.35), (xl, 2.35)], 'resid', True)
    t.crect(MX - 1.1, 0.1, MX + 1.1, 0.4, 0.08, 'box', True, trig=0.1, hatch=True)
    t.text('RMSNORM', 0.15, MX, 0.18, 'label', 'center')
    lane_arrows(t, 0.6)
    t.crect(BX0, 0.6, BX1, 1.95, 0.12, 'box', True, trig=0.6, hatch=True)
    t.text('MLP · SWIGLU', 0.21, MX, 1.48, 'label', 'center')
    t.text('5120 → 25600 → 5120', 0.1, MX, 1.24, 'spec', 'center')
    neu = []
    for x in np.linspace(BX0 + 0.3, BX1 - 0.3, NNEU):
        neu.append(len(t.a))
        t.seg((x, 0.78), (x, 1.0), 'neu', False)
    for off in LANE_X:
        t.plus(MX + off, 2.35)
    lane_arrows(t, HY + GAP)
    for cx, cy in ((-HX + 0.42, HY - 0.42), (HX - 0.42, HY - 0.42), (HX - 0.42, -HY + 0.42)):
        t.seg((cx - 0.14, cy), (cx + 0.14, cy), 'reg')
        t.seg((cx, cy - 0.14), (cx, cy + 0.14), 'reg')
    t.text('DECODER BLOCK', 0.16, HX - 0.75, 2.42, 'spec', 'right')
    t.text('D 5120 · FFN 25600 · PRE-NORM', 0.1, HX - 0.75, 2.16, 'spec', 'right')
    return t.arrays(neu)

def build_embed():
    t = Tmpl()
    frame_rects(t)
    lane_arrows(t, -1.0)
    t.crect(BX0, -1.0, BX1, 0.5, 0.12, 'box', True, trig=-1.0, hatch=True)
    t.text('TOKEN EMBEDDING', 0.21, MX, -0.12, 'label', 'center')
    t.text('151 643 × 5120', 0.11, MX, -0.42, 'spec', 'center')
    lane_arrows(t, HY + GAP)
    t.text('INPUT', 0.16, HX - 0.75, 2.42, 'spec', 'right')
    return t.arrays()

def build_head():
    t = Tmpl()
    frame_rects(t)
    t.crect(MX - 1.1, -2.62, MX + 1.1, -2.32, 0.08, 'box', True, trig=-2.62, hatch=True)
    t.text('RMSNORM', 0.15, MX, -2.54, 'label', 'center')
    t.poly([(MX - 1.0, -2.1), (MX + 1.0, -2.1), (BX1 + 0.9, -0.8), (BX0 - 0.9, -0.8)], 'box', True, closed=True, trig=-2.1)
    t.text('LM HEAD', 0.21, MX, -1.52, 'label', 'center')
    t.text('5120 → 151 643', 0.1, MX, -1.78, 'spec', 'center')
    t.crect(MX - 1.3, -0.55, MX + 1.3, -0.2, 0.08, 'box', True, trig=-0.55, hatch=True)
    t.text('SOFTMAX', 0.15, MX, -0.45, 'label', 'center')
    t.text('P(NEXT TOKEN) · TOP 4 OF 151 643 · ONE COLUMN PER POSITION', 0.1, -HX + 0.45, 2.78, 'spec')
    return t.arrays()
TPL = {}

def tpl(kind):
    if not TPL:
        TPL['B'], TPL['E'], TPL['H'] = (build_block(), build_embed(), build_head())
    return TPL[kind]

def row_xform(r):
    c = np.array([0.0, r.center, 0.0])
    if r.kind != 'B' or r.k != SKEW_K:
        return (np.eye(3), c)
    yaw, roll = (-0.13, 0.05)
    cy, sy = (math.cos(yaw), math.sin(yaw))
    cr, sr = (math.cos(roll), math.sin(roll))
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cr, -sr, 0], [sr, cr, 0], [0, 0, 1]])
    return (Ry @ Rz, c + np.array([0.7, -0.15, -0.4]))

def to_world(r, xy, z=HZ + 0.003):
    R, c = row_xform(r)
    xy = np.asarray(xy, float)
    P3 = np.concatenate([xy, np.full(xy.shape[:-1] + (1,), z)], axis=-1)
    return P3 @ R.T + c

def stack_world(r, xy, z=HZ + 0.003):
    xy = np.asarray(xy, float)
    P3 = np.concatenate([xy, np.full(xy.shape[:-1] + (1,), z)], axis=-1)
    return P3 + np.array([0.0, r.base, 0.0])

def row_point(r, x, y_world, z=HZ + 0.004):
    """World point on row r's front plane at lane x and world height y."""
    if r.kind == 'S':
        return stack_world(r, np.stack([np.full_like(y_world, x), y_world - r.base], -1), z)
    return to_world(r, np.stack([np.full_like(y_world, x), y_world - r.center], -1), z)

def box_faces(R, c, hx, hy, hz):
    s = 0.994
    cs = np.array([[x, y, z] for x in (-hx * s, hx * s) for y in (-hy * s, hy * s) for z in (-hz * s, hz * s)])
    cw = cs @ R.T + c
    F = {'front': ([1, 3, 7, 5], (0, 0, 1)), 'back': ([0, 4, 6, 2], (0, 0, -1)), 'top': ([2, 6, 7, 3], (0, 1, 0)), 'bottom': ([0, 1, 5, 4], (0, -1, 0)), 'left': ([0, 2, 3, 1], (-1, 0, 0)), 'right': ([4, 5, 7, 6], (1, 0, 0))}
    return (cw, {n: (idx, R @ np.array(nv, float)) for n, (idx, nv) in F.items()})
FACE_SHADE = {'front': 1.15, 'top': 0.85, 'left': 0.8, 'right': 0.8, 'bottom': 0.7, 'back': 0.6}
_TM = {}

def tmask(s, size, kind='cjk'):
    key = (s, size, kind)
    if key not in _TM:
        _TM[key] = text_mask(s, size, kind)
    return _TM[key]

def occl(ID, xs, ys, r):
    xi = np.clip(np.round(xs).astype(np.int64), 0, W - 1)
    yi = np.clip(np.round(ys).astype(np.int64), 0, H - 1)
    return (ID[yi, xi] <= r).astype(np.float64)

def draw_segs(B, ch, cam, ID, rank, A3, B3, v, w, gw):
    if len(A3) == 0:
        return
    x0, y0, x1, y1, z0, z1, keep = cam.project_segments(A3, B3)
    if not keep.any():
        return
    v = np.broadcast_to(np.asarray(v, float), (len(A3),))
    w = np.broadcast_to(np.asarray(w, float), (len(A3),))
    f0, f1 = (fog_k(z0, cam), fog_k(z1, cam))
    xs, ys, vals, _ = g3.segment_samples(x0[keep], y0[keep], x1[keep], y1[keep], (v * f0)[keep], (v * f1)[keep], w[keep], 0.5)
    vis = occl(ID, xs, ys, rank) if ID is not None else 1.0
    g3.splat(B[ch], xs, ys, vals * vis * gw)

def visible_rows(layout, cam):
    lo = cam.fy - 26 * cam.dist / 25
    hi = cam.fy + 16 * cam.dist / 25
    return [r for r in layout.rows if r.base + r.h > lo and r.base < hi]

def lane_glow(lane, y_world, t, tau=0.22, after=0.16, after_tau=1.4):
    tt = lane.trig(y_world)
    return g3.env(t - tt, tau, 0.02) + after * g3.env(t - tt, after_tau, 0.05)

def lanes_now(S, t):
    return [S['pf']] if t < S['cut'] else S['lanes']

def render_geometry(S, t, layout, cam, B, gw, ghost):
    rows = visible_rows(layout, cam)
    items = []
    for r in rows:
        if r.kind == 'S':
            items += [(r, j) for j in range(r.n)]
        else:
            items.append((r, None))

    def item_box(it):
        r, j = it
        if j is None:
            R, c = row_xform(r)
            return (R, c, HX, HY, HZ)
        return (np.eye(3), np.array([0.0, r.base + PL_PITCH * (j + 0.5), 0.0]), HX, PL_HALF, HZ)
    boxes = [item_box(it) for it in items]
    order = np.argsort([np.linalg.norm(cam.pos - b[1]) for b in boxes])[::-1]
    rank_of = {}
    idimg = Image.new('I', (W, H), -1)
    dr = ImageDraw.Draw(idimg)
    face_img = Image.new('F', (W, H), 0.0)
    fdr = ImageDraw.Draw(face_img)
    ea, eb, er = ([], [], [])
    for rk, oi in enumerate(order):
        R, c, hx, hy, hz = boxes[oi]
        rank_of[oi] = rk
        cw, faces = box_faces(R, c, hx, hy, hz)
        for name, (idx, nrm) in faces.items():
            ctr = cw[idx].mean(axis=0)
            if nrm @ (cam.pos - ctr) <= 0:
                continue
            sx, sy, sz = cam.project(cw[idx])
            if (sz < cam.near).any():
                continue
            poly = list(zip(sx.tolist(), sy.tolist()))
            dr.polygon(poly, fill=rk)
            fdr.polygon(poly, fill=float(FACE_SHADE[name] * (0.35 + 0.65 * fog_k(sz.mean(), cam))))
            if name != 'front':
                q = cw[idx]
                for i in range(4):
                    ea.append(q[i])
                    eb.append(q[(i + 1) % 4])
                    er.append(rk)
    ID = np.asarray(idimg, np.int32)
    if not ghost:
        B['face'] += np.asarray(face_img, np.float32)
    if ea:
        ea, eb, er = (np.array(ea), np.array(eb), np.array(er))
        for rk in np.unique(er):
            sel = er == rk
            draw_segs(B, 'graph', cam, ID, rk, ea[sel], eb[sel], 0.6, 0.9, gw)
    lanes = lanes_now(S, t)
    for ii, (r, j) in enumerate(items):
        rk = rank_of[ii]
        if j is None:
            draw_block(S, t, lanes, r, cam, B, ID, rk, gw)
        else:
            draw_plate(t, lanes, r, j, cam, B, ID, rk, gw)
    for r in rows:
        if r.kind == 'S':
            draw_stack_bracket(r, cam, B, gw)
    draw_lanes(S, t, layout, rows, lanes, cam, B, gw)

def draw_block(S, t, lanes, r, cam, B, ID, rk, gw):
    tp = tpl(r.kind)
    a3, b3 = (to_world(r, tp['a']), to_world(r, tp['b']))
    cls, hot, trig = (tp['cls'], tp['hot'], tp['trig'])
    base_w = np.select([cls == 0, cls == 1, cls == 3, cls == 4, cls == 9], [1.5, 0.55, 0.85, 0.9, 0.8], 0.75)
    base_v = np.select([cls == 0, cls == 1, cls == 2, cls == 3, cls == 4, cls == 5, cls == 6, cls == 7, cls == 8, cls == 9], [1.0, 0.55, 0.85, 0.8, 0.55, 0.7, 0.55, 0.6, 0.75, 0.45], 0.6)
    chan = np.select([cls == 0, cls == 1, cls == 2, cls == 3, cls == 4, cls == 8], ['bone', 'ash', 'bone', 'bone', 'ash', 'ash'], 'graph')
    nonh = cls != 10
    for cname in ('bone', 'ash', 'graph'):
        sel = nonh & (chan == cname)
        draw_segs(B, cname, cam, ID, rk, a3[sel], b3[sel], base_v[sel], base_w[sel], gw)
    yw = r.center + trig
    g = np.zeros(len(cls))
    gh = np.zeros(len(cls))
    for ln in lanes:
        tt = ln.trig(yw)
        g += g3.env(t - tt, 0.2 if not ln.band else 0.3, 0.02) + 0.07 * g3.env(t - tt, 1.2, 0.05)
        gh += 0.55 * g3.env(t - tt, 0.18, 0.02)
    g = np.where(cls == 10, gh, g) * hot
    g = np.minimum(g, 1.4)
    if len(tp['neu']):
        g = g.copy()
        for ln in lanes:
            tn = float(ln.trig(r.center + 0.9))
            e = float(g3.env(t - tn - 0.03, 0.3, 0.02))
            if e > 0.01:
                rng = np.random.default_rng(zlib.crc32(f'{ln.idx}/{ln.band}/{r.k}'.encode()))
                n = 16 if ln.band else int(rng.integers(4, 8))
                g[tp['neu'][rng.choice(NNEU, n, replace=False)]] += e * (0.8 if ln.band else 1.5)
    sel = g > 0.01
    if sel.any():
        draw_segs(B, 'sig', cam, ID, rk, a3[sel], b3[sel], g[sel], np.where(cls[sel] == 10, 0.8, 1.6), gw)
    lab = {'E': 'EMBED', 'H': 'HEAD'}.get(r.kind, f'L.{r.k:03d}')
    st = g3.text_strokes(lab, 0.36 if r.kind == 'B' else 0.3, HX + 0.55, 1.9)
    draw_segs(B, 'ash', cam, None, rk, to_world(r, st[:, 0, :], HZ), to_world(r, st[:, 1, :], HZ), 0.8, 1.0, gw)
    if r.kind == 'H':
        draw_head_static(S, t, r, cam, B, gw)

def draw_plate(t, lanes, r, j, cam, B, ID, rk, gw):
    y = PL_PITCH * (j + 0.5)
    rect = np.array([[-HX, y - PL_HALF], [HX, y - PL_HALF], [HX, y + PL_HALF], [-HX, y + PL_HALF]])
    a3 = stack_world(r, rect)
    b3 = stack_world(r, np.roll(rect, -1, axis=0))
    draw_segs(B, 'ash', cam, ID, rk, a3, b3, 0.75, 0.8, gw)
    e = 0.0
    for ln in lanes:
        tt = float(ln.trig(r.base + y))
        e += float(g3.env(t - tt, 0.07 if not ln.band else 0.12, 0.01) + 0.08 * g3.env(t - tt, 0.8, 0.03))
    if e > 0.01:
        draw_segs(B, 'sig', cam, ID, rk, a3, b3, min(e, 1.2) * 0.75, 1.1, gw)

def draw_stack_bracket(r, cam, B, gw):
    a, b = r.ab
    top = r.n * PL_PITCH
    xb = HX + 0.45
    br = np.array([[xb, 0.02], [xb, top - 0.02]])
    draw_segs(B, 'ash', cam, None, 10 ** 6, stack_world(r, br[:1]), stack_world(r, br[1:]), 0.75, 1.0, gw)
    for yy in (0.02, top - 0.02):
        q = np.array([[xb - 0.18, yy], [xb + 0.18, yy]])
        draw_segs(B, 'ash', cam, None, 10 ** 6, stack_world(r, q[:1]), stack_world(r, q[1:]), 0.75, 1.0, gw)
    txt = f'L.{a:03d}' if a == b else f'L.{a:03d} - L.{b:03d}'
    sub = '1 BLOCK' if a == b else f'{r.n} BLOCKS'
    mid = top / 2
    for s_, cap, yy, v in ((txt, 0.26, mid + 0.02, 0.85), (sub, 0.17, mid - 0.3, 0.6)):
        st = g3.text_strokes(s_, cap, xb + 0.35, yy)
        draw_segs(B, 'ash', cam, None, 10 ** 6, stack_world(r, st[:, 0, :], HZ), stack_world(r, st[:, 1, :], HZ), v, 1.0, gw)

def dash_mask(y, dash):
    if dash is None:
        return np.ones_like(y)
    on, off = dash
    return (y % (on + off) < on).astype(float)

def draw_lanes(S, t, layout, rows, lanes, cam, B, gw):
    """Lane tracks (always, faint, in the lane's line style) + their glow where a signal has passed."""
    lo = min((r.base for r in rows))
    hi = max((r.base + r.h for r in rows))
    y_end = layout.y('H', 'sm')
    ys = np.arange(max(lo, 0.0), min(hi, y_end) + 1e-06, 0.06)
    if ys.size < 2:
        return
    rows_of = [layout.row_at_y(y) for y in ys]
    ridx = np.array([layout.rows.index(r) for r in rows_of])
    track_lanes = [(i, LANE_X[i], LANE_DASH[i]) for i in range(3)]
    for i, off, dash in track_lanes:
        pts = np.zeros((ys.size, 3))
        for k in np.unique(ridx):
            sel = ridx == k
            pts[sel] = row_point(layout.rows[k], MX + off, ys[sel])
        m = dash_mask(ys, dash)
        segm = m[:-1] * m[1:] if dash is not None else np.ones(ys.size - 1)
        A, Bp = (pts[:-1], pts[1:])
        same = ridx[:-1] == ridx[1:]
        v = 0.55 * segm * same
        draw_segs(B, 'bone', cam, None, 0, A, Bp, v, 0.9, gw)
        if t >= S['cut']:
            ln = S['lanes'][i]
            gl = lane_glow(ln, 0.5 * (ys[:-1] + ys[1:]), t, 0.35, 0.22, 2.2) * segm * same
            if (gl > 0.01).any():
                draw_segs(B, 'sig', cam, None, 0, A, Bp, gl, 2.0, gw)
    if t < S['cut']:
        ln = S['pf']
        gl0 = lane_glow(ln, 0.5 * (ys[:-1] + ys[1:]), t, 0.3, 0.1, 1.0)
        same = ridx[:-1] == ridx[1:]
        for off in ln.offsets:
            pts = np.zeros((ys.size, 3))
            for k in np.unique(ridx):
                sel = ridx == k
                pts[sel] = row_point(layout.rows[k], MX + off, ys[sel])
            draw_segs(B, 'sig', cam, None, 0, pts[:-1], pts[1:], gl0 * same * (1.0 if abs(off) < 1e-06 else 0.55), 1.0, gw)

def head_row(S):
    return GEN_LAYOUT.find('H')

def draw_head_static(S, t, r, cam, B, gw):
    if t < S['cut']:
        return
    for i in range(3):
        pts = [(MX + LANE_X[i], 0.15), (COLX[i], 0.38), (COLX[i], 2.72)]
        for (xa, ya), (xb, yb) in zip(pts[:-1], pts[1:]):
            n = max(2, int(math.hypot(xb - xa, yb - ya) / 0.06))
            u = np.linspace(0, 1, n)
            xy = np.stack([xa + (xb - xa) * u, ya + (yb - ya) * u], -1)
            arc = np.cumsum(np.r_[0, np.hypot(np.diff(xy[:, 0]), np.diff(xy[:, 1]))])
            m = dash_mask(arc, LANE_DASH[i])
            sm = m[:-1] * m[1:] if LANE_DASH[i] else np.ones(n - 1)
            W3 = to_world(r, xy)
            draw_segs(B, 'bone', cam, None, 0, W3[:-1], W3[1:], 0.6 * sm, 0.9, gw)
            h = S['head'][i]
            e = float(g3.env(t - h['sm'], 0.3, 0.02) + 0.2 * g3.env(t - h['sm'], 2.0, 0.05))
            if e > 0.01:
                draw_segs(B, 'sig', cam, None, 0, W3[:-1], W3[1:], e * sm, 1.6, gw)

def head_bars(S, t, cam, B, T2):
    r = head_row(S)
    if t < S['cut'] or r not in visible_rows(GEN_LAYOUT, cam):
        return
    fi = int(round(t * FPS))
    for i in range(3):
        h = S['head'][i]
        if t < h['bars'][0]:
            continue
        for j, (tok, p) in enumerate(CANDS[i]):
            if t < h['bars'][j]:
                continue
            gr = float(g3.out_expo((t - h['bars'][j]) / 0.2))
            y = BAR_Y[j]
            ln = 0.15 + BAR_SCALE * p * gr
            quad = np.array([[COLX[i], y - 0.13], [COLX[i] + ln, y - 0.13], [COLX[i] + ln, y + 0.09], [COLX[i], y + 0.09]])
            pts = to_world(r, quad)
            win = j == 0 and t >= h['win']
            draw_segs(B, 'sig' if win else 'bone', cam, None, 0, pts, np.roll(pts, -1, axis=0), 1.2 if win else 0.75, 1.3, 1.0)
            if win:
                lit = float(g3.smooth((t - h['win']) / 0.08))
                hs = []
                for xx in np.arange(COLX[i] + 0.06, COLX[i] + ln, 0.08):
                    hs.append([[xx, y - 0.13], [min(xx + 0.18, COLX[i] + ln), y + 0.09]])
                if hs:
                    hs = np.array(hs)
                    draw_segs(B, 'sig', cam, None, 0, to_world(r, hs[:, 0]), to_world(r, hs[:, 1]), 0.75 * lit, 1.0, 1.0)
            shown = p if gr >= 0.98 else max(0.0, p * gr + (g3.hash01(fi, i, j, 5) - 0.5) * 0.4 * (1 - gr))
            pr = g3.text_strokes(f'{shown:.2f}', 0.2, COLX[i] + ln + 0.12, y - 0.11)
            draw_segs(B, 'sig' if win else 'ash', cam, None, 0, to_world(r, pr[:, 0, :]), to_world(r, pr[:, 1, :]), 0.95, 1.1, 1.0)
            lx, ly, lz = cam.project(to_world(r, np.array([[COLX[i] - 0.14, y - 0.02], [COLX[i] - 0.14, y - 0.62]])))
            if lz[0] < 1:
                continue
            spacing = abs(ly[1] - ly[0])
            size = 30 if j == 0 else 24
            if spacing < 20:
                size = int(round(size * spacing / 26))
                if size < 8:
                    continue
            m = tmask(tok, size, 'cjkb' if j == 0 else 'cjk')
            lx, ly = (lx[:1], ly[:1])
            a_lab = float(g3.smooth((t - h['bars'][j]) / 0.08))
            if j == 0:
                a_lab *= 1 - float(g3.smooth((t - h['win'] - 0.04) / 0.08))
            x_ = lx[0] - m.shape[1] - 4
            y_ = ly[0] - m.shape[0] / 2
            g3.blit_scaled(T2['halo'], m, x_, y_, a_lab)
            g3.blit_scaled(T2['blue' if j == 0 else 'text'], m, x_, y_, a_lab)
_GD = {}

def glyph_points(ch):
    if ch not in _GD:
        ii, jj, cov = glyph_dots(ch, 22, 0.3, 'cjkb')
        rng = np.random.default_rng(len(_GD) + 3)
        _GD[ch] = (ii, jj, rng.random(ii.size), rng.normal(0, 1, (2, ii.size)))
    return _GD[ch]
_GM = {}

def glyph_mask(ch, size):
    size = int(round(size))
    if (ch, size) not in _GM:
        _GM[ch, size] = text_mask(ch, max(8, size), 'cjkb')
    return _GM[ch, size]

def out_slot(s):
    return (1012 + 58 * s, OUT_Y - 8)

def glyphs(S, t, T2):
    r = head_row(S)
    for i in range(3):
        h = S['head'][i]
        if t < h['c0']:
            continue
        cam_b = camera(S, min(t, h['top']))
        y0w = BAR_Y[0] - 0.02
        lp = to_world(r, np.array([[COLX[i] - 0.14, y0w]]))
        bx, by, _ = cam_b.project(lp)
        ends = to_world(r, np.array([[COLX[i], y0w], [COLX[i] + 0.15 + BAR_SCALE * CANDS[i][0][1], y0w]]))
        ex, ey, _ = cam_b.project(ends)
        size = 64.0
        gx0 = bx[0] - 24 - size
        gy0 = by[0] - size * 0.95
        if t < h['top']:
            ii, jj, rnd, nrm = glyph_points(ANSWER[i])
            u = np.clip((t - h['c0'] - 0.05 * rnd) / max(0.05, (h['top'] - h['c0']) * 0.8), 0, 1)
            e = 1 - (1 - u) ** 3
            pitch = size / 22
            tx_ = gx0 + pitch * (jj + 0.5)
            ty_ = gy0 + pitch * (ii + 0.5)
            fx = ex[0] + (ex[1] - ex[0]) * rnd + nrm[0] * 4
            fy = ey[0] + (ey[1] - ey[0]) * rnd + nrm[1] * 4
            g3.splat(T2['dots'], fx + (tx_ - fx) * e, fy + (ty_ - fy) * e, np.full(ii.size, 1.3))
            continue
        land = h['land']
        uf = (t - h['top']) / (land - h['top'])
        ox, oy = out_slot(i)
        x0, y0 = (gx0 + size / 2, gy0)
        if t < land:
            k = float(g3.in_out_cubic(uf))
            x = x0 + (ox - x0) * k
            y = y0 + (oy - y0) * (float(g3.in_quad(uf)) * 0.6 + 0.4 * k)
            sz = size + (46 - size) * k
        else:
            dt = t - land
            x, sz = (ox, 46)
            y = oy + 6.0 * math.exp(-dt / 0.07) * math.cos(dt * 38)
        m = glyph_mask(ANSWER[i], sz)
        g3.blit_scaled(T2['glyph'], m, x - m.shape[1] / 2, y, 1.0)
        if t < land:
            g3.blit_scaled(T2['knock'], m, x - m.shape[1] / 2, y, 1.0)

def style_sample(T2, ch, x, y, idx, length=34, val=1.0):
    xs = np.arange(0, length, 0.5)
    on = dash_mask(xs / 20.0, LANE_DASH[idx]) if LANE_DASH[idx] else np.ones_like(xs)
    on = on[:-1] * on[1:]
    for k in range(len(xs) - 1):
        if on[k] > 0:
            g3.splat_segments(T2[ch], np.array([x + xs[k]]), np.array([y]), np.array([x + xs[k + 1]]), np.array([y]), val, None, 2.2)

def tags(S, t, cam, B, T2):
    if t < S['cut']:
        return
    G = GEN_LAYOUT
    vis = visible_rows(G, cam)
    fast = S['mode'] == 'echo'
    for e in S['events']:
        r = G.find(e['layer'])
        if r not in vis or t < e['t0']:
            continue
        s = e['lane']
        hold = e['t1'] + (0.15 if fast and s > 0 else 0.22)
        a = 1.0 if t < hold else float(1 - g3.smooth((t - hold) / 0.25))
        if a <= 0.01:
            continue
        grow = float(g3.smooth((t - e['t0']) / 0.12))
        x_att = BX0
        p0 = np.array([x_att, -1.3])
        p1 = np.array([-HX - 0.25, -1.3])
        p2 = np.array([-HX - 0.9, -0.6])
        pts = [p0, p0 + (p1 - p0) * min(1.0, grow * 2)]
        if grow > 0.5:
            pts.append(p1 + (p2 - p1) * min(1.0, (grow - 0.5) * 2))
        pw = to_world(r, np.array(pts))
        draw_segs(B, 'sig', cam, None, 0, pw[:-1], pw[1:], 1.0 * a, 1.4, 1.0)
        if grow >= 1:
            ax, ay, az = cam.project(pw[-1:])
            j = e['j']
            targets = EVENTS[s][j][1]
            toks = []
            for p_, wt in targets:
                nm = TOKENS_ALL[p_]
                if nm == '_soup' and toks and (toks[-1] == 'fish'):
                    toks[-1] = 'fish_soup'
                    continue
                toks.append(nm)
            where = {'persona': 'persona', 'memory': 'memory/you/', 'history': 'earlier turn', 'user': 'your question'}.get(SEG_OF[targets[0][0]], '')
            m = tmask(' · '.join(toks), 28, 'cjk')
            ms = tmask(f'{where} · L{e['layer']}.h{(e['layer'] * 7 + 11 * s + 3 * j) % 64}', 11, 'mono')
            ta_ = float(g3.smooth((t - e['t0'] - 0.12) / 0.08)) * a
            xr = ax[0] - 8
            yt = ay[0] - m.shape[0] - 4
            g3.blit_scaled(T2['halo'], m, xr - m.shape[1], yt, ta_)
            g3.blit_scaled(T2['halo'], ms, xr - ms.shape[1], ay[0] + 4, ta_)
            g3.blit_scaled(T2['blue'], m, xr - m.shape[1], yt, min(1.0, ta_ * 1.2))
            g3.blit_scaled(T2['ash'], ms, xr - ms.shape[1], ay[0] + 4, 0.9 * ta_)
            lab = tmask(LANE_IN[s], 13 if s == 0 else 16, 'mono' if s == 0 else 'cjk')
            xl = xr - m.shape[1] - 16 - 38
            yc = ay[0] - m.shape[0] / 2 - 4
            style_sample(T2, 'blue', xl + 2, yc - 9, s, 34, ta_ * 1.1)
            g3.blit_scaled(T2['text'], lab, xl + 19 - lab.shape[1] / 2, yc - 1, ta_)
            bx0, by0, bx1, by1 = (xl - 1, yc - 5, xl + 39, yc + 18)
            for xa, ya, xb, yb in ((bx0, by0, bx1, by0), (bx1, by0, bx1, by1), (bx1, by1, bx0, by1), (bx0, by1, bx0, by0)):
                g3.splat_segments(T2['ash'], np.array([xa]), np.array([ya]), np.array([xb]), np.array([yb]), ta_, None, 1.0)
    r1 = G.find(1)
    ln = S['lanes'][0]
    tr = float(ln.trig(G.y(1, 'att')))
    if r1 in vis and t >= tr and (t < tr + 1.2):
        a = float(g3.env(t - tr, 0.6, 0.05))
        pw = to_world(r1, np.array([[BX0, -1.3], [-HX - 0.25, -1.3], [-HX - 0.9, -0.6]]))
        draw_segs(B, 'ash', cam, None, 0, pw[:-1], pw[1:], 0.8 * a, 1.2, 1.0)
        ax, ay, az = cam.project(pw[-1:])
        m = tmask(TOKENS_ALL[CUR_COL[0] - 1], 13, 'mono')
        ms = tmask('previous-token head · L1.h3', 10, 'mono')
        g3.blit_scaled(T2['ash'], m, ax[0] - 8 - m.shape[1], ay[0] - m.shape[0] - 3, a)
        g3.blit_scaled(T2['ash'], ms, ax[0] - 8 - ms.shape[1], ay[0] + 3, 0.8 * a)

def lane_heads(S, t, layout, cam, B, T2):
    """the moving signal of each lane: a bright dot and its input token beside it."""
    lanes = lanes_now(S, t)
    for ln in lanes:
        if not ln.active(t) and (not (ln.band and t < S['pf_end'])):
            continue
        y = ln.y_at(t)
        if math.isnan(y):
            continue
        r = layout.row_at_y(y)
        for off in ln.offsets:
            p = row_point(r, MX + off, np.array([y]))
            sx, sy, sz = cam.project(p)
            g3.splat(B['head'], sx, sy, (2.8 if not ln.band or abs(off) < 1e-06 else 1.2) * fog_k(sz, cam))
        if not ln.band:
            p = row_point(r, MX + ln.offsets[0], np.array([y]))
            sx, sy, sz = cam.project(p)
            lab = tmask(LANE_IN[ln.idx], 13, 'mono' if ln.idx == 0 else 'cjk')
            x_ = sx[0] + (8 if ln.idx == 2 else -8 - lab.shape[1])
            g3.blit_scaled(T2['halo'], lab, x_, sy[0] - lab.shape[0] / 2, 0.8)
            g3.blit_scaled(T2['blue'], lab, x_, sy[0] - lab.shape[0] / 2, 0.9)

def legend_and_lens(S, t, T2):
    """Top right: one column per lane (input token, line style), rows L12..L64 filled by the logit lens."""
    if t < S['cut']:
        return
    xr = W - 34
    cols = [xr - 170, xr - 108, xr - 46]
    y_head = 66
    mh = tmask('logit lens', 10, 'mono')
    g3.blit_scaled(T2['ash'], mh, cols[0] - 80, y_head + 58 - 22, 0.85)
    for i in range(3):
        ln = S['lanes'][i]
        if t < ln.t_start - 0.05:
            continue
        a = float(g3.smooth((t - ln.t_start + 0.05) / 0.12))
        tok = LANE_IN[i]
        m = tmask(tok, 15 if i == 0 else 24, 'mono' if i == 0 else 'cjk')
        cx = cols[i]
        g3.blit_scaled(T2['text'], m, cx - m.shape[1] / 2, y_head + 14 - m.shape[0] / 2, a)
        bw, bh = (46, 32)
        x0, y0 = (cx - bw / 2, y_head - 2)
        conf = S['confirm'][i]
        draft = S['mode'] == 'parallel' and conf is not None and (t < conf)
        box = [(x0, y0, x0 + bw, y0), (x0 + bw, y0, x0 + bw, y0 + bh), (x0 + bw, y0 + bh, x0, y0 + bh), (x0, y0 + bh, x0, y0)]
        for xa, ya, xb, yb in box:
            if draft:
                n = 8
                for k in range(n):
                    if k % 2 == 0:
                        u0, u1 = (k / n, (k + 1) / n)
                        g3.splat_segments(T2['ash'], np.array([xa + (xb - xa) * u0]), np.array([ya + (yb - ya) * u0]), np.array([xa + (xb - xa) * u1]), np.array([ya + (yb - ya) * u1]), a, None, 1.2)
            else:
                pop = 1.0 + (1.5 * math.exp(-(t - conf) / 0.12) if conf is not None and t >= conf else 0.0)
                g3.splat_segments(T2['text'], np.array([xa]), np.array([ya]), np.array([xb]), np.array([yb]), a * 0.9 * pop, None, 1.3)
        style_sample(T2, 'blue', cx - 17, y_head + bh + 8, i, 34, a)
    for k, lay in enumerate(LENS_LAYERS):
        y = y_head + 58 + 34 * k
        ml = tmask(f'L{lay:02d}', 11, 'mono')
        g3.blit_scaled(T2['ash'], ml, cols[0] - 52 - ml.shape[1], y + 9, 0.85)
        for i in range(3):
            tl = S['lens'][i][k][1]
            if t < tl:
                continue
            a = float(g3.smooth((t - tl) / 0.08))
            latest = all((t < S['lens'][i][kk][1] for kk in range(k + 1, 5)))
            tok = LENS[i][k]
            m = tmask(tok, 26, 'cjkb' if latest else 'cjk')
            pop = 1.0 + 0.8 * math.exp(-(t - tl) / 0.1)
            g3.blit_scaled(T2['text' if latest else 'ash'], m, cols[i] - m.shape[1] / 2, y, a * min(pop, 1.0))
            if latest and t - tl < 0.4:
                g3.blit_scaled(T2['blue'], m, cols[i] - m.shape[1] / 2, y, 0.6 * math.exp(-(t - tl) / 0.15))
            mc = tmask(f'{LENS_CONF[k] - 0.03 * i:.2f}', 9, 'mono')
            g3.blit_scaled(T2['ash'], mc, cols[i] + 14, y + 16, 0.6 * a)

def prefill_label(S, t, cam, T2):
    if t >= S['cut']:
        return
    L = PF_LAYOUT
    r = L.find('E')
    if r not in visible_rows(L, cam):
        return
    a = float(g3.smooth((t - 0.25) / 0.1))
    p = to_world(r, np.array([[MX + 0.35, 1.35]]))
    px, py, pz = cam.project(p)
    m = tmask('61 tokens at once', 24, 'cjk')
    ms = tmask('prefill · positions 0-60 · one lane each', 10, 'mono')
    g3.blit_scaled(T2['blue'], m, px[0], py[0] - m.shape[0], a)
    g3.blit_scaled(T2['ash'], ms, px[0], py[0] + 4, 0.85 * a)

def overlays(S, t, T2):
    a = float(g3.smooth(t / 0.25))
    q = tmask('you › ' + QUESTION, 22, 'cjk')
    g3.blit_scaled(T2['text'], q, 40, OUT_Y, 0.9 * a)
    who = tmask('大肥鱼 ›', 22, 'cjk')
    g3.blit_scaled(T2['text'], who, out_slot(0)[0] - 40 - who.shape[1], OUT_Y, 0.9 * a)
    head = 'SCHEMATIC · DECODER STACK · 64 BLOCKS · ' + ('3 POSITIONS · ONE PASS' if S['mode'] == 'parallel' else '1 FULL PASS + 2 REPLAYS')
    eb = g3.text_strokes(head, 9.0, 40, 0)
    T2['strokes'].append((eb[:, :, 0], 40 - eb[:, :, 1], 0.6 * a))
PALETTES = {'ink': dict(bg='#0a0a0b', bg2='#151517', face='#151517', bone='#eee9df', ash='#9c978f', graph='#5e5b57', sig='#5a78ff', core='#e6ebff', glyph='#eee9df'), 'paper': dict(bg='#ece8de', bg2='#e2ddd1', face='#e4dfd3', bone='#1d2029', ash='#5d5a53', graph='#8f8b80', sig='#4d6bfe', core='#2a3fbf', glyph='#1d2029')}

def frame(S, t, palette='paper'):
    layout = PF_LAYOUT if t < S['cut'] else GEN_LAYOUT
    B = {k: np.zeros((H, W), np.float32) for k in ('face', 'bone', 'ash', 'graph', 'sig', 'head')}
    cam = camera(S, t)
    fy_prev, _ = cam_state(S, t - 0.5 / FPS)
    dy = cam.fy - fy_prev if (t - 0.5 / FPS >= S['cut']) == (t >= S['cut']) else 0.0
    dyc = float(np.clip(dy * 1.2, -0.75, 0.75))
    NS = int(min(3, max(1, math.ceil(abs(dyc) / 0.25))))
    wts = [1.0, 0.3, 0.14][:NS]
    for i in range(NS):
        ci = camera(S, t, -dyc * i / NS) if i else cam
        render_geometry(S, t, layout, ci, B, wts[i], ghost=i > 0)
    T2 = {k: np.zeros((H, W), np.float32) for k in ('blue', 'ash', 'text', 'glyph', 'knock', 'halo', 'dots')}
    T2['strokes'] = []
    lane_heads(S, t, layout, cam, B, T2)
    tags(S, t, cam, B, T2)
    head_bars(S, t, cam, B, T2)
    legend_and_lens(S, t, T2)
    prefill_label(S, t, cam, T2)
    glyphs(S, t, T2)
    overlays(S, t, T2)
    for xx, yy, a in T2['strokes']:
        g3.splat_segments(T2['text'], xx[:, 0], yy[:, 0], xx[:, 1], yy[:, 1], a, None, 1.2)
    return compose(B, T2, palette, t, cam)

def compose(B, T2, palette, t, cam):
    Pl = {k: hex2rgb(v) for k, v in PALETTES[palette].items()}
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    knock = np.clip(g3.blur(T2['knock'], 3, 2) * 3.0, 0, 1)[..., None]
    halo = (np.clip(g3.blur(T2['halo'], 2, 2) * 2.5, 0, 1) * 0.85)[..., None]
    dots = g3.dilate(T2['dots'])
    if palette == 'ink':
        haze = np.clip((yy / H - 0.05) / 0.95, 0, 1) ** 1.5 * 0.5
        rgb = Pl['bg'] * (1 - haze[..., None] * 0.9) + Pl['bg2'] * (haze[..., None] * 0.9)
        scroll = cam.fy * 2.2 * 9.0 % 30.0
        grid = (np.abs((yy + scroll) % 30.0 - 15.0) > 14.4).astype(np.float32) * 0.06
        rgb = rgb + grid[..., None] * Pl['graph'] * 0.7
        fm = (B['face'] > 0)[..., None]
        rgb = np.where(fm, Pl['face'] * np.clip(B['face'], 0, 1.3)[..., None] * 0.9, rgb)
        rgb = rgb + B['graph'][..., None] * Pl['graph'] * 0.9 + B['ash'][..., None] * Pl['ash'] * 0.85
        rgb = rgb + B['bone'][..., None] * Pl['bone'] * 0.85
        g = glow(B['sig'] * 1.0 + g3.dilate(B['head']) * 2.0 + dots * 0.5, factor=4, r=3)
        g2 = glow(B['sig'] * 0.5 + B['head'] * 2.0, factor=8, r=4)
        rgb = rgb + B['sig'][..., None] * Pl['sig'] * 1.3 + B['sig'][..., None] ** 2 * Pl['core'] * 0.35
        rgb = rgb + g3.dilate(g3.dilate(B['head']))[..., None] * Pl['core'] * 0.6
        rgb = rgb + g[..., None] * Pl['sig'] * 1.6 + g2[..., None] * Pl['sig'] * 1.1
        rgb = rgb * (1 - knock * 0.85) * (1 - halo * 0.8)
        rgb = rgb + T2['ash'][..., None] * Pl['ash'] + T2['text'][..., None] * Pl['bone'] * 0.95
        rgb = rgb + T2['blue'][..., None] * (Pl['sig'] * 0.6 + Pl['core'] * 0.6)
        rgb = rgb + dots[..., None] * (Pl['core'] * 0.8 + Pl['sig'] * 0.4)
        rgb = rgb + T2['glyph'][..., None] * Pl['glyph'] * 1.1
        vig = 1 - 0.35 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) * 0.5
        rgb = rgb * vig[..., None]
        return (np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8)
    rgb = np.broadcast_to(Pl['bg'], (H, W, 3)).copy()
    fm = (B['face'] > 0)[..., None]
    rgb = np.where(fm, Pl['face'] * (0.93 + 0.06 * np.clip(B['face'], 0, 1.3)[..., None]), rgb)
    for ch, colr, k in (('graph', 'graph', 1.0), ('ash', 'ash', 1.0), ('bone', 'bone', 1.1)):
        a_ = (1 - np.exp(-1.4 * B[ch] * k))[..., None]
        rgb = rgb * (1 - a_) + Pl[colr] * a_
    rgb = rgb * (1 - knock * 0.9) + Pl['bg'] * knock * 0.9
    rgb = rgb * (1 - halo) + Pl['bg'] * halo
    g = glow(B['sig'] * 1.0 + g3.dilate(B['head']) * 2.0, factor=4, r=3)
    sig = B['sig'] * 1.3 + g3.dilate(g3.dilate(B['head'])) * 0.8 + g * 0.7 + dots * 1.2
    a_ = (1 - np.exp(-1.5 * sig))[..., None]
    rgb = rgb * (1 - a_) + Pl['sig'] * a_
    for ch, colr, k in (('ash', 'ash', 1.0), ('text', 'bone', 1.0), ('glyph', 'glyph', 1.6)):
        a_ = (1 - np.exp(-1.6 * T2[ch] * k))[..., None]
        rgb = rgb * (1 - a_) + Pl[colr] * a_
    a_ = (1 - np.exp(-1.6 * T2['blue']))[..., None]
    rgb = rgb * (1 - a_) + Pl['sig'] * a_
    return (np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8)
_ARGS = {}

def _frame_i(args):
    i, mode, pal = args
    return frame(sched(mode), i / FPS, pal)

def describe(S):
    print('mode', S['mode'], 'dur', S['dur'], 'cut', round(S['cut'], 2), 'T0', round(S['T0'], 2))
    for e in S['events']:
        print(f'  lane{e['lane'] + 1} L{e['layer']:02d}  {e['t0']:.2f} - {e['t1']:.2f}  ({e['t1'] - e['t0']:.2f} s)')
    for i, h in enumerate(S['head']):
        print(f'  head lane{i + 1}: sm {h['sm']:.2f}  win {h['win']:.2f}  land {h['land']:.2f}')
    for i in range(3):
        print(f'  lens lane{i + 1}:', ' '.join((f'L{lay}@{tt:.2f}' for lay, tt in S['lens'][i])))
    ln = S['lanes']
    bad = 0
    for a, b in ((0, 1), (1, 2)):
        ya, yb = (ln[a].ys, ln[b].ys)
        ok = np.isnan(yb) | np.isnan(ya) | (ya >= ln[a].y_done - 1e-06) | (yb <= ya + 1e-06)
        bad += int((~ok).sum())
    print('  order violations:', bad)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', default='parallel', choices=['parallel', 'echo'])
    ap.add_argument('--dark', action='store_true')
    ap.add_argument('--crf', type=int, default=14)
    ap.add_argument('--out', default=None)
    ap.add_argument('--stills', default=None)
    ap.add_argument('--jobs', type=int, default=14)
    ap.add_argument('--describe', action='store_true')
    a = ap.parse_args()
    pal = 'ink' if a.dark else 'paper'
    S = sched(a.mode)
    if a.describe:
        describe(S)
        return
    if a.stills:
        sd = os.environ.get('INSIDE_STILLS', os.path.join(os.environ.get('TEMP', HERE), 'inside_lab_stills'))
        os.makedirs(sd, exist_ok=True)
        for ts in a.stills.split(','):
            t = float(ts)
            Image.fromarray(frame(S, t, pal)).save(os.path.join(sd, f'v7p_{a.mode}_{pal}_{t:06.3f}.png'))
        return
    name = {'parallel': 'v7_blueprint_parallel', 'echo': 'v7_blueprint_echo'}[a.mode] + ('_dark' if a.dark else '')
    out = a.out or os.path.join(HERE, name + '.mp4')
    n = int(round(S['dur'] * FPS))
    wr = Writer(out, crf=a.crf)
    if a.jobs > 1:
        from multiprocessing import Pool
        with Pool(a.jobs) as pool:
            for fr in pool.imap(_frame_i, [(i, a.mode, pal) for i in range(n)], chunksize=2):
                wr.write(fr)
    else:
        for i in range(n):
            wr.write(_frame_i((i, a.mode, pal)))
    wr.close()
    print('wrote', out, n, 'frames', f'{S['dur']:.2f} s')
if __name__ == '__main__':
    main()
