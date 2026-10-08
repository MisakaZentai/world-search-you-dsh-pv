"""Aligned subtitle band (owner 10-03: "出一个 if，中文就出一个 如果 ... 每个下面都有 id"). On with DSH_SUB=align;
film.Band.band() hands the band to band() here, and with the switch unset nothing in this module draws.

The lyric band becomes a word-alignment picture, the way NMT alignment figures look:

  row 1  the English line, word by word as sung (the decode-in and her-blue sweep of the old band),
         a faint one-dot underline under each word and the word's token id(s) in tiny type under that
  zone   one-dot wires from an English word's underline to the underline of the Chinese chunk it became;
         where the word order differs the wires cross (that is the point)
  row 2  the Chinese, chunk by chunk, each chunk arriving on the onset of the English word it translates,
         with its own underline and token id(s)

A wire is one path: down from the left end of the English underline (beside the word's id) to a lane in the
zone, along the lane, down beside the Chinese chunk into the left end of its underline. It grows along that
path over LINK_GROW from the word's onset, at SUB ink while fresh, settling to FAINT. Wires that share no
end get different lanes where they run side by side; wires into the same chunk (or out of the same word)
may share a lane, they merge like a bus.

Layout: the English row keeps its words in order, a word's cell wide enough for its ids. The Chinese row
keeps the Chinese order; each chunk would like to sit under its first English word, and the row is the
order-keeping placement closest to that in the L1 sense (isotonic regression, pool-adjacent-violators with
weighted medians), so an in-order line hangs straight under the English and a reordered one spreads its
crossings over the middle instead of being pushed to one side.

Data: subs_data.ALIGN (chunks and which English words each one translates) and subs_ids.json (token ids from
the local Qwen's own vocabulary, built by subs_tok.py; the band never reads the model file).
Chrome: panes.box (label `stdin · query`, spinner while a line is sung). Ink: panes.TXT / SUB / FAINT, her
blue for the sweep and the prompt only; mono for ASCII, YaHei for CJK (hud.tx). Lines are one dot wide.

Lines are referred to by id and words by index; nothing here prints lyric text.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import json
import os
from PIL import Image, ImageDraw
import hud
import panes
import subs_data
import tl
from tuikit import ease, glyph
from tuikit.glyph import GLITCH
ON = os.environ.get('DSH_SUB') == 'align'
try:
    _IDS = json.loads((tl.HERE / 'subs_ids.json').read_text(encoding='utf-8'))
except (OSError, ValueError):
    _IDS = {'en': {}, 'zh': {}}
EN_IDS, ZH_IDS = (_IDS['en'], _IDS['zh'])
TXT, SUB, FAINT = (panes.TXT, panes.SUB, panes.FAINT)
LABEL = 'stdin · query'
ZH_PX = 16
ID_PX = panes.SIZE['id']
SEP = '·'
EN_Y = 5
EN_UL = 28
EN_ID = 30
LANES = (41, 44, 47, 50, 53)
ZH_Y = 51
ZH_UL = 73
ZH_ID = 75
CORNER = 3
EN_ID_ROOM = 7
ZH_GAP = 12
NEAR = 6
LINK_GROW = 0.12
FRESH, SETTLE_S = (0.35, 0.45)
ID_SCRAMBLE = 0.1
INK_IN = 0.06
SPANS = [(L.start, max((w.end for w in L.words))) for L in tl.L.lines if L.words]
_SCRATCH = ImageDraw.Draw(Image.new('RGB', (1, 1)))

def _ids_text(ids) -> str:
    return SEP.join((str(i) for i in ids))

def _wmedian(items):
    """Weighted median of [(value, weight)]; the midpoint where the halves balance exactly."""
    items = sorted(items)
    total = sum((w for _v, w in items))
    acc = 0.0
    for k, (v, w) in enumerate(items):
        acc += w
        if abs(acc - total / 2) < 1e-09 and k + 1 < len(items):
            return (v + items[k + 1][0]) / 2
        if acc > total / 2:
            return v
    return items[-1][0]

def isotonic_l1(ys, ws):
    """Non-decreasing z closest to ys in weighted L1 (pool adjacent violators, block value = weighted median)."""
    blocks = []
    for y, w in zip(ys, ws):
        blocks.append([[(y, w)], y])
        while len(blocks) > 1 and blocks[-2][1] > blocks[-1][1]:
            items = blocks[-2][0] + blocks[-1][0]
            blocks[-2:] = [[items, _wmedian(items)]]
    out = []
    for items, v in blocks:
        out += [v] * len(items)
    return out

def _lis(items):
    """Indices of a longest non-decreasing run (by value) of [(index, value)]."""
    n = len(items)
    if not n:
        return set()
    best, prev = ([1] * n, [-1] * n)
    for i in range(n):
        for j in range(i):
            if items[j][1] <= items[i][1] + 1e-06 and best[j] + 1 > best[i]:
                best[i], prev[i] = (best[j] + 1, j)
    i = max(range(n), key=lambda q: (best[q], -q))
    out = set()
    while i >= 0:
        out.add(items[i][0])
        i = prev[i]
    return out

def _lanes(links, en, zh):
    """A lane index per wire: wires whose horizontal runs overlap and share no end get different lanes."""
    spans = []
    for k, i in links:
        a, b = (en[k]['x'] - CORNER, zh[i]['x'] - CORNER)
        spans.append((min(a, b), max(a, b), k, i))
    order = sorted(range(len(spans)), key=lambda q: (-(spans[q][1] - spans[q][0]), spans[q][0]))
    lane = {}
    pref = (2, 1, 3, 0, 4)
    for q in order:
        lo, hi, k, i = spans[q]
        if hi - lo < 1:
            lane[q] = 1
            continue
        busy = set()
        for r, l_ in lane.items():
            lo2, hi2, k2, i2 = spans[r]
            if hi2 - lo2 < 1 or k2 == k or i2 == i:
                continue
            if lo < hi2 + 3 and lo2 < hi + 3:
                busy.add(l_)
        lane[q] = next((l_ for l_ in pref if l_ not in busy), pref[len(lane) % len(pref)])
    return [lane[q] for q in range(len(spans))]

class _Plan:
    """Where everything of one line goes, and when."""

    def __init__(self, band, L, font):
        d = _SCRATCH
        x0, y0, x1, y1 = band.p.rect('lyric_band')
        self.px = x0 + 26
        self.right = x1 - 12
        wps = band.plan(L, font)
        ids = EN_IDS.get(str(L.id), [])
        chunks = subs_data.ALIGN.get(L.id, [])
        linked = {k for _c, ws in chunks for k in ws}
        self.en = []
        x = float(self.px)
        for k, (wp, w) in enumerate(zip(wps, L.words)):
            tw = d.textlength(wp.text, font=font)
            s = _ids_text(ids[k]) if k < len(ids) else ''
            iw = hud.width(s, ID_PX)
            self.en.append(dict(x=x, tw=tw, ids=s, iw=iw, wp=wp, w=w, linked=k in linked))
            x += max(d.textlength(wp.text + ' ', font=font), iw + EN_ID_ROOM)
        cells = []
        for c, ws in chunks:
            s = _ids_text(ZH_IDS.get(c, []))
            tw, iw = (hud.width(c, ZH_PX), hud.width(s, ID_PX))
            cells.append(dict(text=c, ws=sorted(ws), tw=tw, ids=s, iw=iw, cw=max(tw, iw) + ZH_GAP))
        off, acc = ([], 0.0)
        for c in cells:
            off.append(acc)
            acc += c['cw']
        ys, ws_ = ([], [])
        for i, c in enumerate(cells):
            if c['ws']:
                ys.append(self.en[c['ws'][0]]['x'] - off[i])
                ws_.append(1.0)
            else:
                ys.append(None)
                ws_.append(0.001)
        run = _lis([(i, ys[i]) for i in range(len(ys)) if ys[i] is not None])
        ws_ = [w + (0.01 if i in run else 0.0) for i, w in enumerate(ws_)]
        for i in range(len(ys)):
            if ys[i] is None:
                prev = [y for y in ys[:i] if y is not None]
                nxt = [y for y in ys[i + 1:] if y is not None]
                ys[i] = prev[-1] if prev else nxt[0] if nxt else self.px
        zs = [max(z, float(self.px)) for z in isotonic_l1(ys, ws_)] if cells else []
        for c, z, o in zip(cells, zs, off):
            c['x'] = z + o
        stubs = [e['x'] - CORNER for e in self.en if e['linked']]
        for i, c in enumerate(cells):
            if not c['ws']:
                continue
            mine = {self.en[k]['x'] - CORNER for k in c['ws']}
            for _ in range(4):
                xr = c['x'] - CORNER
                hit = [s for s in stubs if s not in mine and abs(s - xr) < NEAR]
                if not hit:
                    break
                c['x'] = max(hit) + NEAR + CORNER
            for j in range(i + 1, len(cells)):
                cells[j]['x'] = max(cells[j]['x'], cells[j - 1]['x'] + cells[j - 1]['cw'])
        if cells:
            over = cells[-1]['x'] + cells[-1]['cw'] - ZH_GAP - self.right
            for c in cells:
                c['x'] = round(c['x'] - max(0.0, over))
        for e in self.en:
            e['x'] = round(e['x'])
        for c in cells:
            c['t'] = min((L.words[k].start for k in c['ws']), default=None)
        for i, c in enumerate(cells):
            if c['t'] is None:
                prev = [q['t'] for q in cells[:i] if q['t'] is not None]
                nxt = [q['t'] for q in cells[i + 1:] if q['t'] is not None]
                c['t'] = prev[-1] if prev else nxt[0] if nxt else L.start
        self.zh = cells
        links = sorted(((k, i) for i, c in enumerate(cells) for k in c['ws']), key=lambda q: L.words[q[0]].start)
        self.links = list(zip(links, _lanes(links, self.en, cells)))
        self.en_end = max((e['x'] + max(e['tw'], e['iw']) for e in self.en), default=self.px)
        self.zh_end = max((c['x'] + max(c['tw'], c['iw']) for c in cells), default=self.px)

def _poly(d, pts, u, color):
    """Draw the first u (0..1, by length) of an axis-aligned polyline, one dot wide."""
    if u <= 0:
        return
    segs = list(zip(pts, pts[1:]))
    lens = [abs(b[0] - a[0]) + abs(b[1] - a[1]) for a, b in segs]
    left = u * sum(lens)
    for (a, b), n in zip(segs, lens):
        if left <= 0:
            break
        if n <= 0:
            continue
        f = min(1.0, left / n)
        e = (round(a[0] + (b[0] - a[0]) * f), round(a[1] + (b[1] - a[1]) * f))
        d.line([a, e], fill=color, width=1)
        left -= n

def _scramble(s, t, t0):
    """An id rolling through digits for ID_SCRAMBLE after t0, then itself."""
    if t >= t0 + ID_SCRAMBLE:
        return s
    k = ease.tick(t, 48)
    return ''.join((ch if ch == SEP else '0123456789'[(ord(ch) * 7 + k * 3 + j) % 10] for j, ch in enumerate(s)))

def plan_for(chrome, L):
    if not hasattr(chrome, '_subs_plans'):
        chrome._subs_plans = {}
    plan = chrome._subs_plans.get(L.id)
    if plan is None:
        plan = chrome._subs_plans[L.id] = _Plan(chrome, L, chrome.band_font())
    return plan

def band(chrome, img, t):
    """The aligned band, drawn by film.Band.band() when DSH_SUB=align."""
    p = chrome.p
    if not p.has_rect('lyric_band'):
        return
    rect = p.rect('lyric_band')
    x0, y0, x1, y1 = rect
    d = ImageDraw.Draw(img)
    bg, ink = (p.color('bg'), p.color('ink'))
    panes.box(d, rect, LABEL, t, run=panes.run_k(t, SPANS))
    L = p.lyrics.line_at(t)
    if L is None or not L.words:
        return
    font = chrome.band_font()
    plan = plan_for(chrome, L)
    alpha = 1.0
    until = p.lyrics.until(L)
    if until < p.lyrics.next_start(L):
        alpha = 1.0 - ease.prog(t, until - 0.5, until)
    if alpha <= 0.003:
        return

    def ink_at(level):
        return glyph.level(ink, level * alpha, bg)
    under = glyph.mix(hud.HER_LIVE, hud.HER_QUIET, hud.live_k(t))
    yE, yEU, yEI = (y0 + EN_Y, y0 + EN_UL, y0 + EN_ID)
    yZ, yZU, yZI = (y0 + ZH_Y, y0 + ZH_UL, y0 + ZH_ID)
    d.text((plan.px - 18, yE), '>', font=font, fill=glyph.level(hud.HER_QUIET, alpha, bg))
    for (k, i), lane in plan.links:
        e, c = (plan.en[k], plan.zh[i])
        t0 = e['w'].start
        if t < t0:
            continue
        u = ease.ease_out(ease.prog(t, t0, t0 + LINK_GROW))
        lvl = ease.lerp(SUB, FAINT, ease.smooth(ease.prog(t, t0 + FRESH, t0 + FRESH + SETTLE_S)))
        xe, xc, yl = (e['x'] - CORNER, c['x'] - CORNER, y0 + LANES[lane])
        pts = [(xe, yEU), (xe, yl), (xc, yl), (xc, yZU), (round(c['x'] + c['tw']), yZU)]
        _poly(d, pts, u, ink_at(lvl))
    for e in plan.en:
        wp, w = (e['wp'], e['w'])
        if t < wp.t0:
            break
        n = len(wp.text)
        shown = []
        for i, ch in enumerate(wp.text):
            ti = wp.t0 + (wp.td * i / n if n else 0)
            if t < ti:
                break
            if t >= ti + wp.settle or ch in " ,.'":
                shown.append(ch)
            else:
                shown.append(GLITCH[(int(ti * 1000) + ease.tick(t, 48)) % len(GLITCH)])
        xw = e['x']
        d.text((xw, yE), ''.join(shown), font=font, fill=ink_at(TXT))
        a_in = ease.prog(t, w.start, w.start + INK_IN)
        xa = xw - (CORNER if e['linked'] else 0)
        d.line([(xa, yEU), (round(xw + e['tw']), yEU)], fill=ink_at(FAINT * a_in))
        if e['ids']:
            hud.tx(d, (xw, yEI), _scramble(e['ids'], t, w.start), ID_PX, ink_at(SUB * a_in))
        end = max(w.end, w.start + 0.12)
        if w.start <= t < end + 0.25:
            u = ease.prog(t, w.start, end)
            fade = 1 - ease.prog(t, end, end + 0.25)
            d.rectangle((xw, yEU - 1, xw + e['tw'] * u, yEU + 1), fill=glyph.level(under, alpha * fade, bg))
    for c in plan.zh:
        if t < c['t']:
            continue
        a_in = ease.prog(t, c['t'], c['t'] + INK_IN)
        hud.tx(d, (c['x'], yZ), c['text'], ZH_PX, ink_at(TXT * a_in))
        if not c['ws']:
            d.line([(c['x'], yZU), (round(c['x'] + c['tw']), yZU)], fill=ink_at(FAINT * a_in))
        t_id = c['t'] + (LINK_GROW if c['ws'] else 0.0)
        if c['ids'] and t >= t_id:
            a_id = ease.prog(t, t_id, t_id + INK_IN)
            hud.tx(d, (c['x'], yZI), _scramble(c['ids'], t, t_id), ID_PX, ink_at(SUB * a_id))
