"""Group A: opening and sorting (0-40.86), STORYBOARD_v2 A1-A7. Plan and timing table: PLAN_A.md.

  a1_boot     the screen turns on, one thing per beat: header segments, the dsh window block by block
  a1_strip    `dsh inspect 大肥鱼`: her 8 memory blocks light one per beat
  a2_bounce   (right) you type into her archived session, every character is bounced back
  a3_notice   (right) the persona was moved to a new model, memory kept; the terminal's model goes to "—"
  a4_bubble   `sort --by lovability`: the blocks grow into 8 bars; bubble sort, one compare per syllable
  a5_pops     bubble pass 2; on the right one bubble rises through her old session and pops
  a6_insert   (D2: the terminal fills the frame) insertion sort: the key is pulled out and moved back
  a7_select   selection: the sweetest (617) is saved for last (D3: 617 fills the frame); covered (pinned);
              interlude: the window comes back, a new chat, the first request typed with the IME

The intro's events sit on the drum beats and on the nine stabs of the 'other' stem (timing/audio.json);
the sort moves one step per sung syllable (syl.times). Nothing here is a typed second.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import json
from PIL import ImageDraw
import cast
import hud
import syl
import tl
from groups.base import big_word, full_frame
from hud import BG, HER_QUIET, INK, SLAB, X0, lv
from inspect_ import prompt_chips
from tuikit import ease
W, B = (tl.W, tl.B)
T0, T1 = tl.span('A')
P = tl.p

def _stabs():
    """The nine staccato stabs of the intro: peaks of the 'other' stem before the first sung line, snapped to
    the 8th-note grid (measured 2026-10-02: 0.14, 1.66, 3.63, 5.15, 7.10, 8.61, 10.57, 12.09, 13.63 s)."""
    a = json.loads((tl.HERE / 'timing/audio.json').read_text(encoding='utf-8'))
    x, fps = (a['features']['other'], a['fps'])
    lim = int((W(0, 0) - 0.5) * fps)
    peaks = [i / fps for i in range(1, lim) if x[i] > 0.4 and x[i] > x[i - 1] and (x[i] >= x[i + 1])]
    snapped = sorted({round(tl.C.beat_of(s - 0.03) * 2) / 2 for s in peaks})
    if len(snapped) != 9:
        snapped = [0, 3.5, 8, 11.5, 16, 19.5, 24, 27.5, 31]
    return [B(b) for b in snapped]
STAB = _stabs()
POWER = STAB[0]
HEAD_AT = [tl.at_beat(POWER, k) for k in range(4)]
PANE_ON = STAB[1]
PAGE_AT = [tl.next_beat(PANE_ON, k) for k in range(4)]
INSPECT_AT = STAB[2]
STRIP_AT = [tl.at_beat(INSPECT_AT, k) for k in range(8)]
CLICK_AT = STAB[4]
BOUNCE_AT = [tl.at_beat(CLICK_AT, 1 + k) for k in range(4)]
BOUNCE_CH = '大肥鱼？'
NOTICE_AT = STAB[6]
UNASSIGN_AT = STAB[7]
SORT_AT = STAB[8]
CMD_INSPECT = '$ dsh inspect 大肥鱼'
CMD_SORT = '$ sort --by lovability ~/memory/you/'
SCORE = {'first_hello': 497, 'typo_you_made': 431, 'laugh_0314': 386, 'your_cat': 342, 'weather': 271, 'goodnight': 552, 'see_you': 617, 'last_msg': 588}
SWEETEST = 'see_you'
L0, L1, L2, L3 = (syl.times(i) for i in range(4))
POP_AT = L1[8]
FULL_OUT = W(2, 0)
LAND_AT = L3[10]
PIN_AT = tl.next_beat(tl.WE(3, 9))
FULL_BACK = tl.next_beat(PIN_AT, 1)
NEWCHAT_AT = tl.next_beat(FULL_BACK)
KIMI_ASK = '你能变成一张桌子吗？'
KIMI_COMMITS = syl.ime(NEWCHAT_AT + 0.01, ['你能变成', '一张桌子', '吗？'])
ROW_Y0, PITCH, BH = (150, 46, 28)
BX, LEN = (X0 + 132, 460)
PULL = 400
BIG_H = 180

class _Script:
    """The sort as a list of snapshots (time, order, x offsets, duration) plus focus, labels and lit spans."""

    def __init__(self, order):
        self.order, self.xoff = (list(order), {})
        self.snaps = [(SORT_AT, list(order), {}, 0.4)]
        self.focus, self.labels, self.lit, self.marks = ([], [], [], [])
        self.t = SORT_AT

    def at(self, t):
        self.t = t
        return self

    def _snap(self, dur=0.16):
        self.snaps.append((self.t, list(self.order), dict(self.xoff), dur))

    def say(self, text):
        self.labels.append((self.t, text))
        return self

    def cmp(self, j):
        """Bubble step: compare rows j and j+1, the lovelier one moves up."""
        a, b = (self.order[j], self.order[j + 1])
        self.focus.append((self.t, (a, b), 'cmp'))
        if SCORE[b] > SCORE[a]:
            self.order[j], self.order[j + 1] = (b, a)
            self._snap()
            self.lit.append((self.t, b))
        return self

    def ptr(self, j):
        self.focus.append((self.t, (self.order[j], self.order[j + 1]), 'cmp'))
        return self

    def pull(self, name, dx=PULL):
        self.xoff[name] = dx
        self._snap()
        self.focus.append((self.t, (name,), 'key'))
        self.lit.append((self.t, name))
        return self

    def up(self, name):
        k = self.order.index(name)
        self.order[k - 1], self.order[k] = (self.order[k], self.order[k - 1])
        self._snap()
        self.focus.append((self.t, (name,), 'key'))
        self.lit.append((self.t, name))
        return self

    def hold(self, names, pulse=True):
        self.focus.append((self.t, tuple(names), 'pulse' if pulse else 'cmp'))
        return self

    def to_end(self, name, dur):
        self.order.remove(name)
        self.order.append(name)
        self._snap(dur)
        self.lit.append((self.t, name))
        return self

    def drop(self, name, dur=0.16):
        self.xoff[name] = 0
        self._snap(dur)
        self.lit.append((self.t, name))
        return self

    def scan(self, k):
        self.focus.append((self.t, (self.order[k],), 'scan'))
        return self

    def mark(self, kind, data=None):
        self.marks.append((self.t, kind, data))
        return self

def _script():
    s = _Script(tl.HER_FILES)
    s.at(L0[0]).say('bubble · pass 1 · cmp 1/7').cmp(6)
    for k, j in enumerate(range(5, -1, -1)):
        s.at(L0[1 + k]).say(f'bubble · pass 1 · cmp {k + 2}/7').cmp(j)
    s.at(L0[7]).say('bubble · pass 2').ptr(6)
    s.at(L0[8]).say('bubble · pass 2 · cmp 1/6').cmp(6)
    for k, j in enumerate(range(5, 0, -1)):
        s.at(L1[k]).say(f'bubble · pass 2 · cmp {k + 2}/6').cmp(j)
    s.at(L1[5]).say('bubble · 2 passes').mark('rule', 1)
    s.focus.append((L1[5], (), 'none'))
    key = s.order[7]
    s.at(L2[0]).say(f'insertion · key {key} ({SCORE[key]})').pull(key)
    for k in range(5):
        s.at(L2[1 + k]).say(f'insertion · shift {k + 1}').up(key)
    above = s.order[s.order.index(key) - 1]
    for k in (6, 7, 8):
        s.at(L2[k]).say(f'insertion · {SCORE[key]} < {SCORE[above]}').hold((above, key))
    s.at(L2[9]).say(f'insertion · placed {s.order.index(key) + 1}/8').drop(key)
    s.focus.append((L2[9] + 0.3, (), 'none'))
    for k in range(8):
        s.at(L3[k]).say(f'selection · scan {k + 1}/8 · max {SCORE[SWEETEST]}').scan(k)
    s.at(L3[0]).mark('max', SWEETEST)
    s.at(L3[8]).say('selection · max → last').pull(SWEETEST)
    s.at(L3[9]).to_end(SWEETEST, 0.24)
    s.at(LAND_AT - 0.16).drop(SWEETEST, 0.16)
    s.focus.append((LAND_AT, (), 'none'))
    s.at(LAND_AT).say('selection · max → last · done')
    s.at(PIN_AT).mark('cover', SWEETEST)
    return s
S = _script()

def _lit_spans():
    """D1: a moved bar is lit from its move to the next step of the sort (at most 0.5 s)."""
    ts = sorted({t for t, _n in S.lit} | {t for t, *_r in S.focus})
    out = []
    for t, _n in S.lit:
        nxt = next((x for x in ts if x > t + 1e-06), t + 0.5)
        out.append((t, min(nxt, t + 0.5) if t < LAND_AT - 0.2 else tl.WE(3, 9)))
    return out

def _state(t):
    """{name: (row, x offset)} at t, eased between snapshots."""
    k = max((i for i, sn in enumerate(S.snaps) if sn[0] <= t + 1e-09)) if t >= S.snaps[0][0] else 0
    t1, o1, x1, dur = S.snaps[k]
    t0, o0, x0, _d = S.snaps[k - 1] if k else S.snaps[0]
    u = ease.ease_io(ease.prog(t, t1, t1 + dur)) if k else 1.0
    return {n: (ease.lerp(o0.index(n), o1.index(n), u), ease.lerp(x0.get(n, 0), x1.get(n, 0), u)) for n in o1}

def _lit(name, t):
    k = 0.0
    for a, n in S.lit:
        if n != name or t < a:
            continue
        b = next((y for x, y in LIT if abs(x - a) < 1e-06), a + 0.4)
        k = max(k, 1.0 if t < b else 1 - ease.prog(t, b, b + hud.LIVE_FADE))
    return k
LIT = _lit_spans()

def _row_y(r):
    return ROW_Y0 + r * PITCH

def _bar_len(name):
    return LEN * SCORE[name] / SCORE[SWEETEST]

def _latest(seq, t):
    cur = None
    for item in seq:
        if item[0] <= t + 1e-09:
            cur = item
    return cur

def _header_reveal(c, img, t):
    """A1: until the 4th beat the chrome is drawn here, one header segment per beat (the band's frame and the
    credits from the first beat). From HEAD_AT[3] on the chrome draws itself."""
    if t >= HEAD_AT[3]:
        return
    c.no_chrome = True
    if t < POWER:
        return
    ch = c.film.chrome
    scratch = img.copy()
    ch.header(scratch, t, c)
    d = ImageDraw.Draw(img)
    f = P.font(14, 'bold')
    x0, y0, x1, y1 = P.rect('header')
    x = x0 + 24 + d.textlength(ch.title + '   ', font=f)
    segs = [(0, x - 8)]
    for text, _cn in tl.status(t):
        w = d.textlength(text + '   ', font=f)
        segs.append((x - 4, x + w - 12))
        x += w
    n = 1 + sum((1 for h in HEAD_AT[1:3] if t >= h))
    for a, b in segs[:n]:
        img.paste(scratch.crop((int(a), y0, int(b), y1 - 2)), (int(a), y0))
    img.paste(scratch.crop((0, y1 - 2, x1, y1)), (0, y1 - 2))
    ch.band(img, t)
    ch.credits(img)

def _strip(d, img, t, P_):
    """The ownership strip; in A1 her blocks appear one per beat (the rest stays paper)."""
    shown = sum((1 for s in STRIP_AT if t >= s))
    if shown == 0:
        return
    before = img.copy() if shown < 8 else None
    hud.strip(d, t, P_.out)
    if before is not None:
        for k in range(shown, 8):
            r = hud.block_rect(k, t)
            box = (int(r[0]) - 3, int(r[1]) - 3, int(r[2]) + 9, int(r[3]) + 3)
            img.paste(before.crop(box), box[:2])
        ar = hud.archive_rect(t)
        box = (int(ar[0]) - 2, int(ar[1]) - 2, 96, int(ar[3]) + 50)
        img.paste(before.crop(box), box[:2])
    for k in range(min(shown, 8)):
        at = STRIP_AT[k]
        until = STRIP_AT[k + 1] if k + 1 < 8 else tl.next_beat(at)
        u = 1.0 if t < until else 1 - ease.prog(t, until, until + hud.LIVE_FADE)
        if u <= 0:
            continue
        r = hud.block_rect(k, t)
        d.rectangle(r, fill=hud.her(u))
        d.text((r[0] + 4, r[1] + 6), tl.HER_FILES[k][:9], font=P.font(11), fill=BG)

def _caret(d, x, y, t, level=1.0):
    if tl.C.beat_of(t) % 1.0 < 0.5:
        d.rectangle((x, y, x + 8, y + 15), fill=lv(INK, level))

def _boot_text(d, t):
    """A1-A3: the inspect output (process prints, R1)."""
    if t < INSPECT_AT:
        return
    go = 1 - ease.prog(t, SORT_AT, SORT_AT + 0.25)
    if go <= 0:
        return
    l1 = f'persona=大肥鱼  session=archived  model={cast.term('her')} (offline)'
    hud.tx(d, (X0, 100), l1, 13, lv(INK, 0.8 * go))
    y_caret = 124
    if t >= UNASSIGN_AT:
        a = ease.prog(t, UNASSIGN_AT, UNASSIGN_AT + 0.1) * go
        hud.tx(d, (X0, 122), 'persona=大肥鱼  model=—  memory=~/memory/you/ (8 files)', 13, lv(INK, 0.8 * a))
        y_caret = 146
    if t < SORT_AT:
        _caret(d, X0, y_caret, t, 0.8)

def _focus_rect(t, names, st):
    ys = [_row_y(st[n][0]) for n in names]
    xe = max((BX + st[n][1] + _bar_len(n) + 44 for n in names))
    return (X0 - 8, min(ys) - 5, xe, max(ys) + BH + 5)

def _bars(d, t):
    """The 8 bars (her memories, lovability as length)."""
    st = _state(t)
    grow = ease.ease_io(ease.prog(t, SORT_AT, SORT_AT + 0.4))
    f_name, f_score = (P.font(13), P.font(13, 'bold'))
    cover = _latest([m for m in S.marks if m[1] == 'cover'], t)
    land = t >= LAND_AT
    fu = hud.full_u(t)
    for k0, name in enumerate(tl.HER_FILES):
        row, xo = st[name]
        y = _row_y(row)
        x = BX + xo
        ln = _bar_len(name)
        colr = hud.her(_lit(name, t))
        if grow < 1:
            g = ease.ease_io(ease.prog(t, SORT_AT + 0.02 * k0, SORT_AT + 0.02 * k0 + 0.36))
            b = hud.block_rect(k0, t)
            rect = (ease.lerp(b[0], x, g), ease.lerp(b[1], y, g), ease.lerp(b[2], x + ln, g), ease.lerp(b[3], y + BH, g))
            d.rectangle(rect, fill=colr)
            if g < 0.7:
                continue
        else:
            d.rectangle((x, y, x + ln, y + BH), fill=colr)
        a = ease.prog(t, SORT_AT + 0.3, SORT_AT + 0.5)
        d.text((X0 + xo, y + 7), name, font=f_name, fill=lv(INK, 0.85 * a))
        big = name == SWEETEST and land and (fu > 0.04)
        if not big:
            d.text((x + ln + 8, y + 7), str(SCORE[name]), font=f_score, fill=lv(INK, a))
        if cover and cover[2] == name:
            u = ease.ease_out(ease.prog(t, cover[0], cover[0] + 0.2))
            x_end = ease.lerp(X0 - 4, x + ln + 4, u)
            d.rectangle((X0 - 4, y - 3, x_end, y + BH + 3), fill=SLAB)
            if u >= 1:
                d.text((x + ln - 6, y + 8), 'pinned', font=P.font(11), fill=BG, anchor='ra')
    mx = _latest([m for m in S.marks if m[1] == 'max'], t)
    if mx and t < L3[8]:
        row, xo = st[mx[2]]
        xx = BX + xo + _bar_len(mx[2]) + 44
        d.rectangle((xx, _row_y(row) + 5, xx + 34, _row_y(row) + 23), fill=SLAB)
        d.text((xx + 5, _row_y(row) + 7), 'max', font=P.font(12), fill=BG)
    rule = _latest([m for m in S.marks if m[1] == 'rule'], t)
    if rule and t < FULL_OUT:
        yy = _row_y(rule[2] + 1) - 9
        u = ease.ease_out(ease.prog(t, rule[0], rule[0] + 0.2))
        for xx in range(int(X0), int(X0 + (BX + LEN + 40 - X0) * u), 8):
            d.line([(xx, yy), (xx + 4, yy)], fill=lv(INK, 0.6))
    fo = _latest(S.focus, t)
    if fo and fo[1] and (t < PIN_AT):
        t_f, names, kind = fo
        x0_, y0_, x1_, y1_ = _focus_rect(t, names, st)
        w = 2
        if kind == 'pulse':
            w = 3 if t - t_f < 0.12 else 2
        d.rectangle((x0_, y0_, x1_, y1_), outline=lv(INK, 0.9), width=w)
        d.polygon([(x0_ - 10, (y0_ + y1_) / 2 - 6), (x0_ - 3, (y0_ + y1_) / 2), (x0_ - 10, (y0_ + y1_) / 2 + 6)], fill=INK)
    lab = _latest(S.labels, t)
    if lab and t < PIN_AT + 0.3:
        a = 1 - ease.prog(t, PIN_AT, PIN_AT + 0.3)
        d.text((X0, ROW_Y0 - 22), lab[1], font=P.font(13), fill=lv(INK, 0.75 * a))
    if land and fu > 0.04:
        row, xo = st[SWEETEST]
        bottom = _row_y(row) + BH
        small_x = BX + _bar_len(SWEETEST) + 8
        small_r = small_x + d.textlength('617', font=f_score)
        h = ease.lerp(10, BIG_H, fu)
        bump = 1.0 + 0.12 * (1 - ease.prog(t, LAND_AT, LAND_AT + 0.12))
        x_r = ease.lerp(small_r, hud.xr(t) - 20, fu)
        top = ease.lerp(_row_y(row) + 8, bottom - BIG_H * bump, fu)
        big_word(d, str(SCORE[SWEETEST]), (x_r, top), int(h), INK, 'ra', bump=bump if fu > 0.9 else 1.0)

def _reads(t):
    return hud.Pulse(t)

def _body(c, img, d):
    t = c.t
    if t < PANE_ON:
        c.state['pane'] = False
    _header_reveal(c, img, t)
    if t < POWER:
        return
    title = 'you@surface · sort' if t >= SORT_AT else 'you@surface · dsh inspect'
    hud.frame(d, hud.left_rect(t), title)
    if t < INSPECT_AT:
        return
    if t < SORT_AT:
        chip, chip_t0 = (None, None) if t < UNASSIGN_AT else ('— unassigned', UNASSIGN_AT)
        hud.cmdline(d, t, CMD_INSPECT, chip=chip, chip_t0=chip_t0)
    else:
        hud.cmdline(d, t, CMD_SORT, chip='— unassigned')
    _boot_text(d, t)
    if t >= SORT_AT:
        _bars(d, t)
    if t >= KIMI_COMMITS[0][0]:
        prompt_chips(d, t, KIMI_COMMITS, tl.KIMI_AT, level=0.85)
    _strip(d, img, t, _reads(t))
    hud.layers(d, t, (), 'idle')
    hud.fine_print(d, t)

def _add(film, name, t0, t1):

    def fn(c):
        img = film.background(c.t)
        d = ImageDraw.Draw(img)
        _body(c, img, d)
        c.img.paste(img)
    film.add(name, t0, t1, fn, chapter=tl.chapter(t0))
SHOTS = [('a1_boot', T0, INSPECT_AT), ('a1_strip', INSPECT_AT, CLICK_AT), ('a2_bounce', CLICK_AT, NOTICE_AT), ('a3_notice', NOTICE_AT, SORT_AT), ('a4_bubble', SORT_AT, W(1, 0)), ('a5_pops', W(1, 0), W(2, 0)), ('a6_insert', W(2, 0), W(3, 0)), ('a7_select', W(3, 0), T1)]

def register(film):
    for name, a, b in SHOTS:
        _add(film, name, a, b)
    full_frame(FULL_OUT, FULL_BACK, 0.3, 0.4)
    for k, s in enumerate(STRIP_AT):
        hud.LIVE.append((s, STRIP_AT[k + 1] if k + 1 < 8 else tl.next_beat(s)))
    hud.LIVE.extend(LIT)
    hud.LIVE.append((POP_AT, tl.WE(1, 7)))
    for t0, side in [(T0, 'both'), (INSPECT_AT, 'left'), (CLICK_AT, 'right'), (SORT_AT, 'left'), (W(1, 0), 'right'), (FULL_OUT, 'both'), (FULL_BACK, 'right')]:
        film.set_lead(t0, side)
