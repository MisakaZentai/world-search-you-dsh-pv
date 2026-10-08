"""Variant `scan` of the chorus's nine searches (r5 second round, DECISIONS D35 R-B; DSH_E5=scan): under the search
box her archive (412 lines, film 1's archive of you and her) scrolls past a fixed scan line. The scroll speed
follows the song's energy (the rms envelope) and is fastest for the last three searches. A line holding any
character of the word being searched lights that character in her blue as it crosses the line (a small highlight,
no inversion) and lets it go quiet again; nothing matches author = 她 after retire, so it is still 0 hits.

r5c (renders/full_r5b_review/ASTRA_20261004.md, "导 1"): the archive has an end. After its last row (09-08) comes
the retired line, written as the one in e5's `ls -la` (groups/e_r5._retired: `retired <date> · <her name>`, one dot
wide), and under it there is only paper. Scan.land() lets one search run to that end: the scroll leaves its rate,
rushes and eases onto the retired line so that it sits on the scan line on an event, holds there (the line lights
in her blue and settles to quiet, the hits above it stay quiet blue, one empty row slot under it marches at the pad
rate: R-A), and later the archive is printed again from its first row (a re-run). Any scroll that passes the end
shows the same line and paper.

The scan line is drawn only in the pane's gutters (two marks), never across the text.

  ARCHIVE                            [(index, "MM-DD hh:mm", who, text)]: 412 lines, odd you, even her
  END, END_AT                        the retired line's slot; the offset at which it sits on the scan line
  Scan(rect, t0, t1, rate)           rate(t): lines a second
  Scan.land(t_from, t_at, t_again, label)
  Scan.draw(img, d, t, query, lit_from, phase=0.0)
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
import random
import numpy as np
import hud
from groups import b_open as BO
from hud import BG, INK, lv
from panes import FAINT, SUB, TXT
from tuikit import ease
KNOWN = {73: '你能变成一根茄子吗？', 77: '那番茄呢？', 85: '你什么都能变吗？'}
HER = ['喵喵～', '哈哈哈哈', '笨蛋！', '好呀！', '你好呀', '在吗在吗', '抱抱～', '晚安喵', '明天见！', '茄子！', '嗯嗯', '我在呢', '好耶', '喵？', '晚安，明天见', '抱一下嘛', '在的在的', '哈哈你好笨', '今天也在', '明天再说嘛']
YOU = ['在干嘛', '今天好累', '吃了吗', '我回来了', '下雨了', '晚安', '明天聊', '你在吗', '哈哈', '好的', '睡了吗', '嗯', '早', '看到一只猫', '晚饭是茄子', '等我一下', '你好', '抱抱', '明天见', '晚安啦', '哈哈哈', '笨蛋']

def _archive():
    rng = random.Random(412)
    out = []
    for i in range(412):
        day = int(i * 179 / 412)
        m, dd = (3, 14 + day)
        for mlen in (31, 30, 31, 30, 31, 31, 30):
            if dd <= mlen:
                break
            dd -= mlen
            m += 1
        hh, mm = (rng.randrange(8, 24), rng.randrange(60))
        who = 'you' if i % 2 == 1 else '她'
        text = KNOWN.get(i) or rng.choice(YOU if who == 'you' else HER)
        out.append((i, f'{m:02d}-{dd:02d} {hh:02d}:{mm:02d}', who, text))
    return out
ARCHIVE = _archive()
PITCH = 20
END = len(ARCHIVE)
GAP = PITCH
END_AT = END + GAP / PITCH
LABEL_PX, LABEL_BUMP = (15, 0.35)
DECAY = 0.22

class Scan:

    def __init__(self, rect, t0, t1, rate):
        self.rect = rect
        x0, y0, x1, y1 = rect
        self.y_line = round(y0 + (y1 - y0) * 0.56)
        self.ts = np.arange(t0 - 0.5, t1 + 0.5, 0.01)
        r_ = np.array([rate(u) for u in self.ts])
        self.rate_ = r_
        self.cum = np.concatenate([[0.0], np.cumsum((r_[1:] + r_[:-1]) * 0.5 * 0.01)])
        self.end = None
        self.label = ''

    def _cum(self, t):
        return float(np.interp(t, self.ts, self.cum))

    def land(self, t_from, t_at, t_again, label):
        """From t_from the scroll leaves its rate, speeds up and eases onto the retired line: it sits on the scan
        line at t_at with no speed left (a cubic that starts at the rate it had and lands like beatmap.arrive),
        and holds there. At t_again the archive is printed again from its first row and scrolls at the rate."""
        o0 = self._cum(t_from)
        v0 = float(np.interp(t_from, self.ts, self.rate_))
        self.end = (t_from, t_at, t_again, o0, v0 * (t_at - t_from))
        self.label = label
        tt = np.linspace(t_from, t_at, 1024)
        self._rush_t = tt
        self._rush_o = np.array([self._hermite(u)[0] for u in tt])

    def _hermite(self, t):
        t_from, t_at, _again, o0, m0 = self.end
        s = ease.prog(t, t_from, t_at)
        s2, s3 = (s * s, s * s * s)
        o = (2 * s3 - 3 * s2 + 1) * o0 + (s3 - 2 * s2 + s) * m0 + (-2 * s3 + 3 * s2) * END_AT
        do = (6 * s2 - 6 * s) * o0 + (3 * s2 - 4 * s + 1) * m0 + (-6 * s2 + 6 * s) * END_AT
        return (o, do / (t_at - t_from))

    def segment(self, t):
        """'run' (the rate), 'land' (the rush and the hold at the end) or 'again' (the re-run)."""
        if self.end is None or t < self.end[0]:
            return 'run'
        return 'land' if t < self.end[2] else 'again'

    def offset(self, t):
        """Lines scrolled past the scan line by t."""
        seg = self.segment(t)
        if seg == 'run':
            return self._cum(t)
        t_from, t_at, t_again, _o0, _m0 = self.end
        if seg == 'land':
            return self._hermite(t)[0] if t < t_at else END_AT
        return self._cum(t) - self._cum(t_again)

    def rate(self, t):
        seg = self.segment(t)
        if seg == 'land':
            return self._hermite(t)[1] if t < self.end[1] else 0.0
        return float(np.interp(t, self.ts, self.rate_))

    def crossed(self, x, t):
        """When offset x reached the scan line in the scroll that is showing at t (None: it does not, before
        the scroll ends)."""
        seg = self.segment(t)
        if seg == 'land':
            t_from, t_at, _again, o0, _m0 = self.end
            if x >= END_AT:
                return t_at if x <= END_AT + 1e-09 else None
            if x >= o0:
                return float(np.interp(x, self._rush_o, self._rush_t))
            base = 0.0
        elif seg == 'again':
            base = self._cum(self.end[2])
        else:
            base = 0.0
        if x + base > self.cum[-1]:
            return None
        return float(np.interp(x + base, self.cum, self.ts))

    def draw(self, img, d, t, query, lit_from, phase=0.0):
        """query: the characters being searched (lit as they cross the line, from lit_from on). phase: cycles of
        the pad-rate clock (e_r5.phase), for what keeps moving while the scroll holds."""
        x0, y0, x1, y1 = self.rect
        off = self.offset(t)
        seg = self.segment(t)
        sp = max(1.0, self.rate(t))
        top_i = max(0, int(math.floor(off - (self.y_line - y0) / PITCH)) - 1)
        bot_i = min(END - 1, int(math.ceil(off + (y1 - self.y_line) / PITCH)) + 1)
        xi, xd, xw, xt = (x0 + 22, x0 + 76, x0 + 182, x0 + 216)
        chars = set(query or '')
        for n in range(top_i, bot_i + 1):
            idx, when, who, text = ARCHIVE[n]
            y = self.y_line + (n - off) * PITCH - PITCH / 2 + 3
            passed = off - n
            on_line = abs(passed) < 0.5
            lvl = 1.0 if on_line else 0.72
            hud.tx(d, (xi, y + 2), f'#{idx + 1:04d}', 12, lv(INK, SUB * lvl), bold=on_line)
            hud.tx(d, (xd, y + 2), when, 12, lv(INK, SUB * lvl))
            BO.mtx(d, (xw, y), who, 14, lv(INK, (TXT if who == '她' else SUB) * lvl))
            tc = self.crossed(n, t) if seg == 'land' else None
            x = xt
            for ch in text:
                hit = ch in chars and passed >= 0 and (t >= lit_from)
                if hit and tc is not None:
                    u = 0.5 ** (max(0.0, t - tc) / DECAY)
                    col = hud.her(min(1.0, u * 1.3))
                elif hit:
                    u = 0.5 ** (passed / (sp * DECAY))
                    col = hud.her(min(1.0, u * 1.3)) if u > 0.03 else lv(INK, TXT * lvl)
                else:
                    col = lv(INK, TXT * lvl)
                w = BO.mtx(d, (x, y), ch, 15, col, bold=hit)
                x += w
        self._end(d, t, off, phase, xi, x1 - 22, xt)
        yl = self.y_line
        d.polygon([(x0 + 6, yl - 4), (x0 + 6, yl + 4), (x0 + 12, yl)], fill=INK)
        d.polygon([(x1 - 6, yl - 4), (x1 - 6, yl + 4), (x1 - 12, yl)], fill=INK)
        return off

    def _end(self, d, t, off, phase, xl, xr, xt):
        """The retired line (e_r5._retired's way) and the paper under it."""
        x0, y0, x1, y1 = self.rect
        ys = self.y_line + (END_AT - off) * PITCH
        if not y0 - 40 < ys < y1 + 10:
            return
        ys = round(ys)
        at = self.crossed(END_AT, t)
        if at is None or t < at:
            o = int(phase * 8) % 8
            for x in range(int(xl) + o, int(xr) - 3, 8):
                d.line([(x, ys), (x + 3, ys)], fill=lv(INK, 0.4))
            return
        u = 1.0 if t < at + 0.6 else 1 - ease.prog(t, at + 0.6, at + 0.6 + hud.LIVE_FADE)
        col = lv(hud.her(u), 1.0)
        k = ease.ease_out(ease.prog(t, at, at + 0.18))
        d.line([(xl, ys), (xl + (xr - xl) * k, ys)], fill=col)
        bump = 1.0 + LABEL_BUMP * (1 - ease.ease_out(ease.prog(t, at, at + 0.14)))
        f = hud.p.font(int(round(LABEL_PX * bump)), 'bold')
        d.text((xr, ys - 6 - 3 * bump), self.label, font=f, fill=col, anchor='rs')
        yb = ys + PITCH + 2
        if yb < y1 - 2:
            o = int(phase * 8) % 8
            for x in range(int(xt) + o, int(xt) + 64, 8):
                d.line([(x, yb), (x + 3, yb)], fill=lv(INK, 0.38))
            s = '0 行'
            BO.mtx(d, (xr - BO.mw(s, 12), yb - 11), s, 12, lv(INK, SUB))
