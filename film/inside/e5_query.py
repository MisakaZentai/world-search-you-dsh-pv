"""The chorus's search box (r5 second round, DECISIONS D35 R-B): her word typed in a zoomed search box the way an
input method commits it, one sung syllable a character. Before each syllable the pinyin composes at the caret with a
candidate strip under it; on the syllable the character commits ("上屏") at full size and the composition is gone.
Paper ground, ink type, no inversion anywhere.

  PINYIN[ch], CANDS[ch]      the composition and the first three candidates for each of her nine words' characters
  size_for_words(words, px)  one font size whose ink is >= px tall for every word
  Word(...)                  one query's typing: draw(d, t) and the geometry a flight starts from
  params(d, t, x, y, q, ...) the search call and the scan bar beside the box
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
from functools import lru_cache
from PIL import Image, ImageDraw
import hud
from groups import b_open as BO
from groups.base import _size_for
from hud import BG, INK, lv
from panes import SUB, TXT
from tuikit import ease
PINYIN = {'喵': 'miao', '哈': 'ha', '笨': 'ben', '蛋': 'dan', '茄': 'qie', '子': 'zi', '你': 'ni', '好': 'hao', '在': 'zai', '吗': 'ma', '抱': 'bao', '晚': 'wan', '安': 'an', '明': 'ming', '天': 'tian'}
CANDS = {'喵': '喵秒妙', '哈': '哈蛤铪', '笨': '笨本奔', '蛋': '蛋但单', '茄': '茄切且', '子': '子字自', '你': '你呢泥', '好': '好号毫', '在': '在再载', '吗': '吗妈马', '抱': '抱包宝', '晚': '晚万完', '安': '安按暗', '明': '明名命', '天': '天田甜'}
PRE = 0.15
COMP_PX, CAND_PX = (30, 17)

def size_for_words(words, px):
    return max((_size_for(w, px, True) for w in words))

@lru_cache(maxsize=256)
def glyph_mask(text, size, bold=True):
    """An L-mode mask of `text` tight to its ink, with the ink box offset (dx, dy) from the pen origin."""
    f = hud.font(size, text, bold)
    x0, y0, x1, y1 = f.getbbox(text)
    m = Image.new('L', (x1 - x0 + 2, y1 - y0 + 2), 0)
    ImageDraw.Draw(m).text((1 - x0, 1 - y0), text, font=f, fill=255)
    return (m, x0 - 1, y0 - 1)

def paste_mask(img, mask, x, y, color, w=None, h=None):
    """Paste `mask` (resized to w x h if given) at (x, y) in `color`."""
    if w is not None and h is not None:
        w, h = (max(1, int(round(w))), max(1, int(round(h))))
        if (w, h) != mask.size:
            mask = mask.resize((w, h), Image.LANCZOS)
    img.paste(tuple(color), (int(round(x)), int(round(y))), mask)

class Word:
    """One query typed into the box: its characters land on `lands`; the composition of character i runs from
    max(lands[i] - PRE, free_i) to lands[i]; `gone` is when the word leaves the box (it flies, or the next one
    starts)."""

    def __init__(self, q, lands, free, gone, size, x, y_ink):
        self.q, self.lands, self.free, self.gone, self.size = (q, list(lands), free, gone, size)
        self.x, self.y_ink = (x, y_ink)
        f = hud.font(size, q, True)
        self.adv = [f.getlength(q[:i]) for i in range(len(q) + 1)]
        bx0, by0, bx1, by1 = f.getbbox(q)
        self.ink_h = by1 - by0
        self.oy = y_ink - by0
        self.box = (x + bx0, y_ink, x + bx1, y_ink + self.ink_h)

    def comp_span(self, i):
        start = self.lands[i - 1] if i > 0 else self.free
        return (max(self.lands[i] - PRE, start + 0.02), self.lands[i])

    def committed(self, t):
        return sum((1 for a in self.lands if t >= a))

    def char_rect(self, i):
        """Ink box of character i at rest (for a flight that starts from the box)."""
        f = hud.font(self.size, self.q[i], True)
        x0, y0, x1, y1 = f.getbbox(self.q[i])
        return (self.x + self.adv[i] + x0, self.oy + y0, self.x + self.adv[i] + x1, self.oy + y1)

    def draw(self, img, d, t, hold_scale=1.0):
        if t >= self.gone:
            return
        n = self.committed(t)
        for i in range(n):
            ch = self.q[i]
            at = self.lands[i]
            k = 1.0 + 0.1 * (1 - ease.ease_out(ease.prog(t, at, at + 0.12))) ** 2
            m, dx, dy = glyph_mask(ch, self.size)
            cx = self.x + self.adv[i] + dx + m.width / 2
            cy = self.oy + dy + m.height / 2
            w, h = (m.width * k * hold_scale, m.height * k)
            paste_mask(img, m, cx - w / 2, cy - h / 2, INK, w, h)
        if n < len(self.q):
            a, b = self.comp_span(n)
            if a <= t < b:
                self._compose(img, d, t, n, a, b)
                return
        xc = self.x + self.adv[n] + (6 if n else 2)
        idle = n == 0 or n == len(self.q)
        blink_on = int((t - (self.lands[n - 1] if n else self.free)) / 0.215) % 2 == 0
        if not idle or blink_on:
            d.rectangle((round(xc), self.y_ink + 4, round(xc) + 1, self.y_ink + self.ink_h - 4), fill=INK)

    def _compose(self, img, d, t, i, a, b):
        ch = self.q[i]
        py = PINYIN.get(ch, '')
        u = ease.prog(t, a, a + (b - a) * 0.75)
        n = max(1, int(math.ceil(len(py) * u)))
        x = self.x + self.adv[i] + 8
        y = self.y_ink + self.ink_h * 0.18
        w = hud.tx(d, (x, y), py[:n], COMP_PX, lv(INK, 0.9), True)
        for xx in range(int(x), int(x + w), 3):
            d.point((xx, y + COMP_PX + 4), fill=lv(INK, 0.7))
        d.rectangle((round(x + w + 2), round(y + 2), round(x + w + 3), round(y + COMP_PX + 1)), fill=INK)
        cy = y + COMP_PX + 14
        cands = CANDS.get(ch, ch)
        parts = []
        cx = x + 6
        for j, c in enumerate(cands[:3]):
            s = f'{j + 1} '
            parts.append((cx, s, c, j == 0))
            cx += BO.mw(s, CAND_PX) + hud.width(c, CAND_PX, j == 0) + 12
        bx1 = cx - 6
        d.rectangle((round(x), round(cy - 4), round(bx1), round(cy + CAND_PX + 7)), fill=BG, outline=lv(INK, 0.55))
        for px, s, c, first in parts:
            w0 = BO.mtx(d, (px, cy), s, CAND_PX, lv(INK, SUB))
            BO.mtx(d, (px + w0, cy), c, CAND_PX, lv(INK, TXT if first else SUB), bold=first)
        if parts:
            px, s, c, _f = parts[0]
            w0 = BO.mw(s, CAND_PX)
            wc = hud.width(c, CAND_PX, True)
            d.line([(px + w0, cy + CAND_PX + 3), (px + w0 + wc, cy + CAND_PX + 3)], fill=INK)
MARK_GROW, MARK_DUR = (0.6, 0.35)

def _after_line(d, t, x, y, tail, mark):
    """r5c ("导 1"): the after line lands once, on `mark` (the first search's run): "retire" is slammed in bold
    from 1.6x (it grows down and right, into the empty line under it, never into the author line), and once it
    has landed the line stays bold with a one-dot underline (until params' mark_end). Ink only; it does not
    repeat."""
    head, tok = ('  after  = ', '"retire"')
    w0 = BO.mtx(d, (x, y), head, 16, lv(INK, TXT), bold=True)
    k = 1.0 + MARK_GROW * (1 - ease.prog(t, mark, mark + MARK_DUR)) ** 2
    size = int(round(16 * k))
    w1 = BO.mtx(d, (x + w0, y), tok, size, INK, bold=True)
    BO.mtx(d, (x + w0 + w1, y), tail[1:], 16, lv(INK, TXT))
    u = ease.ease_out(ease.prog(t, mark + MARK_DUR * 0.7, mark + MARK_DUR * 0.7 + 0.12))
    if u > 0:
        ux0 = x + BO.mw('  ', 16)
        ux1 = x + w0 + BO.mw(tok, 16, True)
        yu = y + round(16 * 0.86) + 3
        d.line([(ux0, yu), (ux0 + (ux1 - ux0) * u, yu)], fill=lv(INK, 0.85))

def params(d, t, x, y, q, prog, right, expand=None, expand_w=None, mark=None, mark_end=None):
    """The search call beside the box and its scan bar: search("q", author = 她, after = "retire"[, expand = ...]).
    expand: the other forms searched with the word (wall); the line keeps within expand_w px (R-C).
    mark: when the after line lands (r5c, scan: the first search's run); it stays marked (_after_line) until
    mark_end (when the box prints a new call after the ah-ah)."""
    tail = '",' if expand else '")'
    lines = [f'search("{q}",', '  author = 她,', '  after  = "retire' + tail, '', '  ~/archive/whale/ · 412 行']
    for li, s_ in enumerate(lines):
        if li == 2 and mark is not None and (mark <= t < (mark_end if mark_end is not None else math.inf)):
            _after_line(d, t, x, y + li * 22, tail, mark)
            continue
        BO.mtx(d, (x, y + li * 22), s_, 16, lv(INK, TXT if li < 3 else SUB), bold=li == 0)
    if expand:
        s_ = '  expand = ' + ' '.join(expand) + ')'
        size = 16
        while size > 11 and expand_w is not None and (BO.mw(s_, size) > expand_w):
            size -= 1
        BO.mtx(d, (x, y + 3 * 22 + (16 - size) * 0.5), s_, size, lv(INK, TXT))
    bx = x + 6
    by = y + 5 * 22 + 8
    bw = right - bx
    d.rectangle((bx, by, bx + bw, by + 8), outline=lv(INK, 0.6))
    if prog > 0:
        d.rectangle((bx + 2, by + 2, bx + 2 + max(0, (bw - 4) * prog), by + 6), fill=lv(INK, 0.9))
    hud.tx(d, (bx, by + 16), f'scanned {int(412 * prog)}/412' + ('   → 0 hits' if prog >= 1.0 else ''), 13, INK, True)
    return by + 16 + 16
