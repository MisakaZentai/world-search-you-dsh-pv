"""Variant `wall` of the chorus's nine searches (r5 second round, DECISIONS D35 R-B; DSH_E5=wall): every failed search
becomes a tile on a wall of her words that keeps growing. The word typed in the box shrinks and flies into the wall
after its "for"; the search is expanded (the word's characters and her ways of writing it, FORMS), and each form
lands as a tile of its own on the following 16ths, more forms for each later word. Every tile gets a small `0 hits`
and a strike. The camera starts close (big tiles) and pulls back continuously; its speed follows the harmony
(beatmap.pad) and it is always just far enough out for the next tile. From line 50 old queries are re-run and their
tiles drop on 16ths, denser and denser, until the last 16th before 203 fills the wall: her words everywhere, every
one 0 hits. On the ah-ah the tiles rise and fall with the voice; on each bar line her words light in a ripple.

World: a grid of COLS x ROWS slots (TW x TH world units, pitch PW x PH), filled from the bottom row up and from the
middle out. The camera is anchored at the bottom centre; a slot is used only once it is wholly in view, so no tile
is ever cut by the pane's border. R-C: an empty slot shows only its four corners; a tile settles inside its own slot
(no frame crosses another); the flying word is clipped 3 px inside each pane, so it is never drawn across a border.

  Wall(rect, queries, forms, t0, sixteenths, rerun_from, downs, tick_end, rate)
        queries: [(word, t_enter, t_land)]; forms: {word: [form, ...]}; rate(t) > 0: the camera's time warp
  Wall.draw(img, d, t, ah)               the pane's content (call inside a clip of the pane)
  Wall.flight(img, t, src, band_y, q_clip, w_clip)   the typed word on its way from the box
  Wall.count(t)                          tiles on the wall
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import bisect
import math
import random
import numpy as np
from PIL import Image
import beatmap as BM
import hud
from hud import INK, lv
from inside.e5_query import glyph_mask
from tuikit import ease
COLS, ROWS = (17, 10)
PW, PH = (70, 30)
TW, TH = (64, 24)
WORD_H = 13.0
HITS_H = 4.4
PAD = 4.0
WCX = (COLS * PW - (PW - TW)) / 2.0
MID_COL = COLS // 2
MASK_PX = 96
EPS = 0.012
GRADE = 0.16
SETTLE = 0.07
FORMS = {'喵喵': ['喵', '喵～', '喵？', '喵！'], '哈哈': ['哈', '哈～', '哈！', '哈哈哈'], '笨蛋': ['笨', '蛋', '笨笨', '笨～'], '茄子': ['茄', '子', '茄～', '茄！', '茄子～'], '你好': ['你', '好', '你～', '好呀', '你好呀'], '在吗': ['在', '吗', '在？', '在嘛', '在～', '在吗？']}
_PADDED = {}
_PADPX = 48

def _padded(mask):
    m = _PADDED.get(id(mask))
    if m is None or m[0] is not mask:
        pm = Image.new('L', (mask.width + 2 * _PADPX, mask.height + 2 * _PADPX), 0)
        pm.paste(mask, (_PADPX, _PADPX))
        m = (mask, pm)
        _PADDED[id(mask)] = m
    return m[1]

def _exact(img, mask, x, y, k, color, clip=None):
    """Paste `mask` scaled by k with its top-left at the float point (x, y) (no rounding jitter); with `clip`
    (x0, y0, x1, y1, exclusive end) only the part inside it."""
    fx, fy = (math.floor(x), math.floor(y))
    ox, oy = (x - fx, y - fy)
    ow = int(math.ceil(mask.width * k + ox)) + 1
    oh = int(math.ceil(mask.height * k + oy)) + 1
    if ow <= 1 or oh <= 1 or k < 0.045:
        return
    pm = _padded(mask)
    p = _PADPX
    m = pm.resize((ow, oh), Image.BILINEAR if k < 0.3 else Image.LANCZOS, box=(p - ox / k, p - oy / k, p + (ow - ox) / k, p + (oh - oy) / k))
    if clip is not None:
        cx0, cy0, cx1, cy1 = (int(v) for v in clip)
        a0, b0 = (max(fx, cx0), max(fy, cy0))
        a1, b1 = (min(fx + ow, cx1), min(fy + oh, cy1))
        if a1 <= a0 or b1 <= b0:
            return
        m = m.crop((a0 - fx, b0 - fy, a1 - fx, b1 - fy))
        fx, fy = (a0, b0)
    img.paste(tuple(color), (fx, fy), m)

def _pchip(x, y, xq):
    """Monotone cubic interpolation (Fritsch-Carlson) of the knots (x, y) at xq; x strictly increasing."""
    x, y = (np.asarray(x, float), np.asarray(y, float))
    h = np.diff(x)
    dl = np.diff(y) / h
    m = np.zeros_like(y)
    for i in range(1, len(y) - 1):
        if dl[i - 1] * dl[i] > 0:
            w1, w2 = (2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1])
            m[i] = (w1 + w2) / (w1 / dl[i - 1] + w2 / dl[i])
    m[0], m[-1] = (dl[0], dl[-1])
    k = np.clip(np.searchsorted(x, xq, side='right') - 1, 0, len(x) - 2)
    t = (xq - x[k]) / h[k]
    h00, h10 = (2 * t ** 3 - 3 * t ** 2 + 1, t ** 3 - 2 * t ** 2 + t)
    h01, h11 = (-2 * t ** 3 + 3 * t ** 2, t ** 3 - t ** 2)
    out = h00 * y[k] + h10 * h[k] * m[k] + h01 * y[k + 1] + h11 * h[k] * m[k + 1]
    return np.where(xq <= x[0], y[0], np.where(xq >= x[-1], y[-1], out))

class Wall:

    def __init__(self, rect, queries, forms, t0, sixteenths, rerun_from, downs, tick_end, rate):
        self.rect = rect
        self.downs = list(downs)
        x0, y0, x1, y1 = rect
        self.inner = (x0 + 6, y0 + 14, x1 - 6, y1 - 5)
        ix0, iy0, ix1, iy1 = self.inner
        self.mid = (ix0 + ix1) / 2.0
        self.base = iy1 - 1
        self.svis = {}
        for c in range(COLS):
            for r in range(ROWS):
                wl, wr = (c * PW, c * PW + TW)
                lim = []
                if wl < WCX:
                    lim.append((self.mid - ix0 - 3) / (WCX - wl))
                if wr > WCX:
                    lim.append((ix1 - 3 - self.mid) / (wr - WCX))
                lim.append((self.base - iy0 - 3) / (r * PH + TH))
                self.svis[c, r] = min(lim)
        self.order = sorted(self.svis, key=lambda s: (-self.svis[s], s[1], abs(s[0] - MID_COL), s[0]))
        self.s0 = self.svis[self.order[5]] * 0.998
        self.s1 = min(self.svis.values()) * 0.998
        hm, _a, _b = glyph_mask('0 hits', MASK_PX // 2, True)
        self.hits_w = hm.width * HITS_H / (hm.height - 2)
        self.t0, self.tick_end = (t0, tick_end)
        self._schedule(queries, forms, sixteenths, rerun_from)
        self._camera(rate)
        self.tvis = [self.t_of_scale(self.svis[s]) for s in self.order]

    def _schedule(self, queries, forms, sixteenths, rerun_from):
        """tiles: [(t_land, word, kind, slot, t_enter)], in landing order; kind 'q' (typed), 'x' (a form of it),
        'r' (a re-run)."""
        ev = []
        for w, te, tl_ in queries:
            ev.append((tl_, 0, 'q', w, te))
            after = [s for s in sixteenths if s > tl_ + 0.01]
            for j, f in enumerate(forms.get(w, [])):
                ev.append((after[j], 1, 'x', f, None))
        ticks = [x for x in sixteenths if rerun_from - 1e-06 <= x <= self.tick_end + 1e-06]
        ev += [(s, 2, 'r', None, None) for s in ticks]
        ev.sort(key=lambda e: (e[0], e[1]))
        total = len(self.order)
        own = sum((1 for e in ev if e[1] < 2))
        n0 = sum((1 for e in ev if e[1] < 2 and e[0] < ticks[0] - 1e-06))
        tiles, n, seen = ([], 0, [])
        own_left = own
        for t, _p, kind, w, te in ev:
            if kind != 'r':
                tiles.append((t, w, kind, self.order[n], te))
                if kind == 'q':
                    seen.append(w)
                n += 1
                own_left -= 1
                continue
            last = t >= ticks[-1] - 1e-06
            x = (t - ticks[0]) / max(1e-06, ticks[-1] - ticks[0])
            want = int(round(n0 * ((total - 0) / n0) ** x))
            target = total - own_left if last else max(want, n + 1)
            target = min(target, total - own_left)
            pool = seen * 2 + [f for q in seen for f in forms.get(q, [])[:2]]
            for j in range(max(0, target - n)):
                pick = random.Random(n * 7919 + 13).choice(pool)
                tiles.append((t, pick, 'r', self.order[n], None))
                n += 1
        self.tiles = tiles
        self.land = [x[0] for x in tiles]
        self.reruns = sorted({x[0] for x in tiles if x[2] == 'r'})

    def count(self, t):
        return bisect.bisect_right(self.land, t)

    def batches(self):
        """[(t, n_landing, kinds)] per landing time (for the report)."""
        out = {}
        for t, _w, kind, _s, _te in self.tiles:
            out.setdefault(round(t, 3), []).append(kind)
        return sorted(((t, len(v), ''.join(sorted(set(v)))) for t, v in out.items()))

    def _p_of(self, s):
        if s >= self.s0:
            return 0.0
        return min(1.0, math.log(s / self.s0) / math.log(self.s1 / self.s0))

    def _camera(self, rate):
        """P(t) 0..1 (s = s0 * (s1 / s0) ** P): a monotone curve through deadlines (every tile's slot is in view
        before its tile starts to land), drawn on a time axis warped by rate(t) (the pad), so the pull speeds up
        and slows down with the harmony and never stops."""
        t_end = self.tiles[-1][0]
        self.ts = np.arange(self.t0 - 0.02, t_end + 0.6, 0.01)
        r_ = np.array([rate(u) for u in self.ts])
        self.u = np.concatenate([[0.0], np.cumsum((r_[1:] + r_[:-1]) * 0.5 * 0.01)])
        knots = {}
        for k, (t_land, _w, kind, slot, te) in enumerate(self.tiles):
            lead = max(0.12, 0.45 * (t_land - te) + 0.02) if kind == 'q' else SETTLE + 0.03
            dl = t_land - lead
            knots[dl] = max(knots.get(dl, 0.0), self._p_of(self.svis[slot]))
        kt = sorted(knots)
        req = [knots[t] for t in kt]
        uu = [float(np.interp(t, self.ts, self.u)) for t in kt]
        for j in range(len(kt) - 2, -1, -1):
            req[j] = max(req[j], req[j + 1] - GRADE * (uu[j + 1] - uu[j]))
        ku = [float(np.interp(self.t0 - 0.02, self.ts, self.u))]
        kp = [0.0]
        for t, r_req, u in zip(kt, req, uu):
            p = min(1.0, max(r_req, kp[-1] + EPS * (u - ku[-1])))
            if u <= ku[-1] + 1e-06:
                kp[-1] = max(kp[-1], p)
                continue
            ku.append(u)
            kp.append(p)
        u_end = float(np.interp(t_end, self.ts, self.u))
        if u_end > ku[-1] + 1e-06:
            ku.append(u_end)
            kp.append(1.0)
        else:
            kp[-1] = 1.0
        self.P = _pchip(ku, kp, self.u)
        self.P = np.maximum.accumulate(self.P)

    def p_at(self, t):
        return float(np.interp(t, self.ts, self.P))

    def scale(self, t):
        return self.s0 * (self.s1 / self.s0) ** self.p_at(t)

    def t_of_scale(self, s):
        p = self._p_of(s)
        if p <= 0.0:
            return self.t0 - 1.0
        i = int(np.searchsorted(self.P, p - 1e-09))
        return float(self.ts[min(i, len(self.ts) - 1)])

    def visible_at(self, t):
        return bisect.bisect_right(self.tvis, t)

    def tile_rect(self, slot, s):
        c, r = slot
        x0 = self.mid + (c * PW - WCX) * s
        x1 = self.mid + (c * PW + TW - WCX) * s
        y1 = self.base - r * PH * s
        y0 = self.base - (r * PH + TH) * s
        return (x0, y0, x1, y1)

    def word_k(self, m, s):
        """Scale of a word's mask in a tile at camera scale s: WORD_H tall, or narrower to keep clear of the
        tile's "0 hits" (a three-character form)."""
        room = TW - 2 * PAD - self.hits_w - 3.0
        return min(WORD_H / (m.height - 2), room / max(1.0, m.width - 2)) * s

    def word_box(self, word, slot, s):
        """(x, y, k) where the tile's word mask goes: top-left and scale."""
        m, _dx, _dy = glyph_mask(word, MASK_PX)
        x0, y0, x1, y1 = self.tile_rect(slot, s)
        k = self.word_k(m, s)
        return (x0 + PAD * s, (y0 + y1) / 2 - m.height * k / 2, k)

    def _bob(self, t, slot, s, ah):
        """The ah-ah: a tile rises with the voice (a ripple out from the middle), never into its neighbour."""
        a0, a1 = ah
        if not a0 - 0.05 <= t < a1 + 0.3:
            return 0.0
        c, r = slot
        env = BM.MUSIC.env('vocal', t - 0.045 * abs(c - MID_COL) - 0.03 * r)
        fade = ease.smooth(ease.prog(t, a0 - 0.05, a0 + 0.1)) * (1 - ease.smooth(ease.prog(t, a1, a1 + 0.3)))
        amp = min(0.42 * (PH - TH) * s, 12.0)
        return -amp * max(0.0, min(1.0, env)) * fade

    def _corners(self, d, slot, s, col):
        x0, y0, x1, y1 = (round(v) for v in self.tile_rect(slot, s))
        a = max(2, min(5, round(0.1 * (x1 - x0))))
        for cx, cy, sx, sy in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
            d.line([(cx, cy), (cx + a * sx, cy)], fill=col)
            d.line([(cx, cy), (cx, cy + a * sy)], fill=col)

    def _tile(self, img, d, t, i, s, ah, settle=1.0):
        """Tile i; settle < 1 while a form / re-run is settling into its slot (the word drops inside the tile)."""
        t_land, word, kind, slot, _te = self.tiles[i]
        dy = self._bob(t, slot, s, ah)
        x0, y0, x1, y1 = self.tile_rect(slot, s)
        y0 += dy
        y1 += dy
        age = t - t_land
        if settle < 1.0:
            frame = lv(INK, 0.3 + 0.4 * settle)
        else:
            frame = lv(INK, 0.85 if age < 0.2 else 0.55 if kind == 'q' else 0.42)
        d.rectangle((round(x0), round(y0), round(x1), round(y1)), outline=frame)
        m, _dx, _dy = glyph_mask(word, MASK_PX)
        k = self.word_k(m, s)
        if settle >= 1.0 and kind == 'q':
            k *= 1.0 + 0.1 * (1 - ease.ease_out(ease.prog(t, t_land, t_land + 0.12))) ** 2
        wx = x0 + PAD * s
        wy = (y0 + y1) / 2 - m.height * k / 2 - (1 - settle * settle) * 3.0 * s
        if settle >= 1.0:
            lit = 1.0 if age < 0.12 else max(0.0, 1 - (age - 0.12) / 0.3)
            dn = BM.last(t, self.downs)
            if dn is not None and t_land < dn:
                c_, r_ = slot
                at_ = dn + 0.012 * (abs(c_ - MID_COL) + r_)
                if t >= at_:
                    lit = max(lit, 0.75 * (1 - ease.prog(t, at_, at_ + 0.28)))
            col = hud.her(lit, 1.0 if kind == 'q' else 0.82)
        else:
            col = hud.her(1.0, 0.35 + 0.65 * settle)
        clip = (math.floor(x0) + 2, math.floor(y0) + 2, math.ceil(x1) - 1, math.ceil(y1) - 1)
        _exact(img, m, wx, wy, k, col, clip)
        if settle < 1.0:
            return
        strike_at = t_land + max(0.05, BM.events('sixteenth', t_land + 0.01, t_land + 0.4)[0] - t_land)
        if t >= strike_at:
            a = ease.prog(t, strike_at, strike_at + 0.06)
            ww = m.width * k
            ym = round(wy + m.height * k * 0.52)
            d.line([(round(wx - 2 * s), ym), (round(wx - 2 * s + (ww + 4 * s) * a), ym)], fill=lv(INK, 0.9 if kind == 'q' else 0.7))
            hm, _hx, _hy = glyph_mask('0 hits', MASK_PX // 2, True)
            kh = HITS_H * s / (hm.height - 2)
            hx = x1 - PAD * s - hm.width * kh
            hy = y1 - PAD * s * 0.9 - hm.height * kh
            if hm.height * kh >= 4.0 + 2 * kh:
                _exact(img, hm, hx, hy, kh, lv(INK, 0.75 * a))

    def draw(self, img, d, t, ah):
        s = self.scale(t)
        n = self.count(t)
        filled = {self.tiles[i][3] for i in range(n)}
        settling = {}
        for i in range(n, len(self.tiles)):
            t_land, _w, kind, slot, _te = self.tiles[i]
            if t_land - SETTLE > t:
                break
            if kind != 'q':
                settling[slot] = i
        corner = lv(INK, 0.35)
        for slot in self.order[:self.visible_at(t)]:
            if slot not in filled and slot not in settling:
                self._corners(d, slot, s, corner)
        for i in range(n):
            self._tile(img, d, t, i, s, ah)
        for slot, i in settling.items():
            u = ease.prog(t, self.tiles[i][0] - SETTLE, self.tiles[i][0])
            self._tile(img, d, t, i, s, ah, settle=ease.ease_out(u))

    def flight(self, img, t, src, band_y, q_clip, w_clip, small_h=13.0):
        """Typed words on their way into the wall. src(i) = (x, y, mask): the top-left of query i's word mask at
        rest in the box (scale 1). The word shrinks where it was and sinks to `band_y` (the empty strip at the
        bottom of the box), slides along that strip to above its slot, then sinks out of the box and into the wall
        down its own column (empty above the frontier), growing into the tile. It is drawn only inside q_clip and
        w_clip (3 px inside each pane), never across a border (R-C)."""
        s = self.scale(t)
        qi = -1
        for t_land, word, kind, slot, te in self.tiles:
            if kind != 'q':
                continue
            qi += 1
            if te is None or not te <= t < t_land:
                continue
            u = ease.prog(t, te, t_land)
            sx, sy, m = src(qi)
            tx, ty, _k = self.word_box(word, slot, s)
            tk = self.word_k(m, s)
            ks = small_h / (m.height - 2)
            w_s, h_s = (m.width * ks, m.height * ks)
            bx = sx + m.width / 2 - w_s / 2
            by = band_y - h_s
            colx = tx + (m.width * tk - w_s) / 2
            if u < 0.34:
                a = ease.smooth(u / 0.34)
                k = 1.0 + (ks - 1.0) * a
                x = sx + (bx - sx) * a
                y = sy + (by - sy) * a
            elif u < 0.62:
                a = ease.smooth((u - 0.34) / 0.28)
                k = ks
                x = bx + (colx - bx) * a
                y = by
            else:
                a = (u - 0.62) / 0.38
                a2 = a * a
                k = ks + (tk - ks) * a2 * a2
                x = colx + (tx - colx) * a2 * a2
                y = by + (ty - by) * a2
            col = lv(INK, 1.0) if u < 0.5 else hud.her(min(1.0, (u - 0.5) / 0.3))
            for clip in (q_clip, w_clip):
                _exact(img, m, x, y, max(0.02, k), col, clip)
