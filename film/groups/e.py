"""Group E: the chorus, she is everywhere (179.64-207.0), STORYBOARD_v2 E1-E5, PLAN_E.md.

  e1_sessions  right: one 大肥鱼 session per syllable; left: D7 scrolls away, nine empty slots (still)
  e2_cells     left: one slot per syllable fills with what a stand-in just wrote (8/26 by the end)
  e2b_sessions right: the sidebar fills; her archived session is pushed out at the bottom
  e3_slot      right: the model name under her name rolls like a reel, stops three times, never on her
  e4_search    left: nine searches; the query is the word that fills the frame (D3); for -> 0 hits;
               D4: the whole frame freezes on ah-ah, only the lyric band's underline grows
  e5_ls        D2 break: `ls -la ~/memory/you/` fills the frame, dimmed; one syllable lights one of her eight
               rows, "left" lights the line where she was retired

Local versions (the shared modules are frozen): add_frozen (a shot drawn at a frozen time, background
included) and a wrapper on film.chrome.header for the same freeze; clip_draw / fine_print_rot from group D.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
from tuikit import ease
import cast
import hud
import syl
import tl
from groups import c as GC
from groups import d as GD
from groups.base import big_word, full_frame
from groups.d import clip_draw, drop, fine_print_rot, lit
from hud import BG, INK, X0, lv
W, WE = (tl.W, tl.WE)
T0, T1 = tl.span('E')
SESS1 = syl.times(44)
CELLS_AT = syl.times(45)
SESS2 = syl.times(46)
SLOT_AT = tl.SLOT_AT
SLOT_STOPS = syl.syl(47, 5)
SEARCH_AT = W(48, 0)
FREEZE = (W(49, 6), WE(49, 6))
LS_OUT = tl.bar(117)
LS_AT = WE(50, 6)
LS_ROWS = syl.times(51)
LS_BACK = tl.bar(119, 1)

def frozen(t: float) -> float:
    """D4: inside the ah-ah everything is drawn at its first frame."""
    return FREEZE[0] if FREEZE[0] <= t < FREEZE[1] else t
E2_FILES = ['table_2', 'eggplant_3', 'cat_2', 'steak_2', 'flower_2', 'human_9', 'piece', 'dope', 'love']
E2_WRITES = {n: (tw, o) for tw, n, o in tl.WRITES if n in E2_FILES}
QUERIES = ['喵喵', '哈哈', '笨蛋', '茄子', '你好', '在吗', '抱抱', '晚安', '明天']

def _searches():
    """[(query, t_char1, t_char2, t_for)] from the 'search-ing for' words of lines 48-50."""
    out = []
    for lid in (48, 49, 50):
        words = tl.L.by_id[lid].words
        for wi in range(len(words)):
            if syl.count(lid, wi) == 2 and wi + 1 < len(words) and (syl.count(lid, wi + 1) == 1) and (wi + 1 != len(words)):
                a, b = syl.syl(lid, wi)
                out.append((a, b, words[wi + 1].start))
    out = [s for s in out if s[0] < W(50, 6) + 0.1][:9]
    return [(q,) + s for q, s in zip(QUERIES, out)]
SEARCHES = _searches()
CMD_WATCH = '$ dsh memory ~/memory/you/ --watch --grid'
CMD_SEARCH = '$ dsh search ~/archive/whale/ --author DeepSeek-V4.1-Flash --after retire'
CMD_LS = 'you@surface:~$ ls -la ~/memory/you/'
HER_LS = ['goodnight.txt', 'first_hello.txt', 'typo_you_made.txt', 'laugh_2026-03-14.wav', 'your_cat.png', 'weather_you_liked.json', 'you_said_see_you_tomorrow.txt', 'last_message.txt']
HER_SIZES = [1000 + i * 7919 % 90000 for i in range(8)]
LS_STRIP = ['goodnight', 'first_hello', 'typo_you_made', 'laugh_0314', 'your_cat', 'weather', 'see_you', 'last_msg']
OWNER = {k: cast.owner(k) for k in cast.CAST}
OWNER_COL = max((len(cast.owner(k)) for k in cast.STANDINS)) + 3
RETIRED = '2026-09-10'

def ls_rows():
    rows = [('-rw-r--r--', 'me', 'me', s, n, True) for s, n in zip(HER_SIZES, HER_LS)]
    for k, (tw, n, o) in enumerate(tl.WRITES):
        rows.append(('-rw-r--r--', OWNER[o], 'me', 200 + k * 2711 % 900, n + '.txt', False))
    return rows
LS = ls_rows()
PIX = {'table_2': ['............', '............', '############', '############', '.##......##.', '.##......##.', '.##......##.', '.##......##.', '.##......##.', '.##.........', '.##......bb.', '.##......bb.'], 'eggplant_3': ['........bb..', '.......bbb..', '......bbbb..', '.....####...', '....######..', '...#######..', '..########..', '.#########..', '.########...', '.#######....', '..#####.....', '............'], 'steak_2': ['...#########..', '.############.', '##..##..##..##', '#..##..##..###', '..##..##..####', '.############.', '...########...', '..........bb..', '.........bbbb.'], 'human_9': ['...#.#.#....', '...#.#.#.#..', '...#.#.#.#..', '...#######..', '.#.#######..', '.##.######..', '..########..', '...##bb##...', '...######...', '....####....', '....####....', '............'], 'piece': ['......b.....', '.....b......', '.....##.....', '....####....', '...######...', '..########..', '...######...', '.##########.', '############', '.##########.']}

def cell_rect(k):
    r, c = divmod(k, 3)
    x = X0 + c * 132
    y = 118 + r * 132
    return (x, y, x + 120, y + 120)

def draw_cell(d, t, k, level=1.0):
    """One slot of the grid: empty and dim until its syllable, then the picture lands (ink, one touch of her
    blue that is lit while it lands), the file name and who wrote it."""
    x0, y0, x1, y1 = cell_rect(k)
    at = CELLS_AT[k]
    on = t >= at
    d.rectangle((x0, y0, x1, y1), outline=lv(INK, (0.85 if on else 0.22) * level), width=2 if on else 1)
    if not on:
        return
    name = E2_FILES[k]
    tw, who = E2_WRITES[name]
    u = lit(t, at, CELLS_AT[k + 1] if k + 1 < len(CELLS_AT) else at + 0.5)
    blue = lv(hud.her(u), level)
    g = ease.ease_back(ease.prog(t, at, at + 0.22))
    cx, cy = ((x0 + x1) / 2, y0 + 46)
    if name in ('dope', 'love'):
        f = tl.p.font(max(8, int(30 * g)), 'bold')
        d.text((cx, cy + drop(t, at, -8, 0.14)), name, font=f, fill=blue if name == 'love' else lv(INK, level), anchor='mm')
        if name == 'dope':
            d.rectangle((cx - 30, cy + 20, cx + 30, cy + 22), fill=blue)
    else:
        if name == 'cat_2':
            pat, cmap = (GC.CAT_PIX, {'I': lv(INK, level), 'B': blue})
        elif name == 'flower_2':
            pat, cmap = (GC.FLOWER_PIX, {'#': lv(INK, level), 'o': blue})
        else:
            pat, cmap = (PIX[name], {'#': lv(INK, level), 'b': blue})
        cell = 6 if len(pat[0]) <= 12 else 5
        cc = max(1, int(round(cell * g)))
        w, h = (len(pat[0]) * cc, len(pat) * cc)
        hud.pix(d, pat, int(cx - w / 2), int(cy - h / 2), cc, cmap)
    a = ease.prog(t, at, at + 0.16)
    hud.tx(d, (x0 + 6, y1 - 30), name + '.txt', 11, lv(INK, 0.8 * a * level))
    own_sz = 10 if hud.width(OWNER[who], 10) <= 104 else 9
    hud.tx(d, (x0 + 6, y1 - 16 + (10 - own_sz) // 2), OWNER[who], own_sz, lv(INK, 0.55 * a * level))

class _Shifted:
    """A Draw proxy that moves every y by dy (used to scroll whole blocks without rewriting their code)."""

    def __init__(self, d, dy):
        self.d, self.dy = (d, dy)

    def __getattr__(self, k):
        return getattr(self.d, k)

    def rectangle(self, xy, *a, **kw):
        x0, y0, x1, y1 = xy
        return self.d.rectangle((x0, y0 + self.dy, x1, y1 + self.dy), *a, **kw)

    def text(self, xy, *a, **kw):
        return self.d.text((xy[0], xy[1] + self.dy), *a, **kw)

    def line(self, pts, *a, **kw):
        return self.d.line([(x, y + self.dy) for x, y in pts], *a, **kw)

def draw_search(d, t, level=1.0):
    """E4: the query box holds what you are typing (ink, >= 180 px: the word that fills the frame, D3);
    every 'for' prints one line of the record below: 0 hits after retire (R4: it accumulates)."""
    if t < SEARCH_AT:
        return
    hud.tx(d, (X0, 118), 'search ›', 14, lv(INK, 0.7 * level))
    d.line([(X0, 318), (hud.xr(t) - 20, 318)], fill=lv(INK, 0.5 * level))
    cur = None
    for q, a, b, f in SEARCHES:
        if t >= a:
            cur = (q, a, b, f)
    if cur is not None:
        q, a, b, f = cur
        shown = q[0] if t < b else q
        last = a if t < b else b
        bump = 1.0 + 0.1 * (1 - ease.prog(t, last, last + 0.1))
        box = big_word(d, shown, (X0 + 110, 116), 186, lv(INK, level), 'la', bump=bump)
        cx = box[2] + 14
        ph = tl.C.beat_of(t) % 1.0
        if ph < 0.5 or t - last < 0.3:
            d.rectangle((cx, 120, cx + 6, 302), fill=lv(INK, level))
    else:
        ph = tl.C.beat_of(t) % 1.0
        if ph < 0.5:
            d.rectangle((X0 + 110, 120, X0 + 116, 302), fill=lv(INK, level))
    for i, (q, a, b, f) in enumerate(SEARCHES):
        if t < f:
            break
        y = 334 + i * 21 + drop(t, f, -6, 0.12)
        hud.tx(d, (X0, y), q, 16, lv(INK, level), True)
        hud.tx(d, (X0 + 54, y + 2), '0', 14, lv(INK, level), True)
        hud.tx(d, (X0 + 68, y + 3), 'hits after retire', 13, lv(INK, 0.6 * level))
LS_Y, LS_H, LS_PX = (82, 15, 14)

def ls_y(i):
    """Row i of the listing (0 = the prompt line); her eight, a gap for the separator, then the rest."""
    if i <= 8:
        return LS_Y + i * LS_H
    return LS_Y + i * LS_H + 8

def draw_ls(d, t, dy=0.0, level=1.0):
    """E5: the listing as one block, dimmed; her rows light one per syllable (lit while landing, then the
    quiet blue), the separator lights on 'left' and runs across the whole frame (D2)."""
    if t < LS_AT:
        return
    f = tl.p.font(LS_PX)
    fb = tl.p.font(LS_PX, 'bold')
    dim = 0.3
    cw = d.textlength('m', font=f)
    for k, (perm, own, grp, size, name, hers) in enumerate(LS):
        y = ls_y(k + 1) + dy
        x = X0
        if hers and t >= LS_ROWS[k]:
            u = lit(t, LS_ROWS[k], LS_ROWS[k + 1])
            colr, a, own_f = (hud.her(u), 1.0, fb)
        else:
            colr, a, own_f = (INK, dim, f)
        c = lv(colr, a * level)
        d.text((x, y), perm, font=f, fill=c)
        x += cw * 12
        d.text((x, y), own, font=own_f, fill=c)
        x += cw * OWNER_COL
        d.text((x, y), grp, font=f, fill=c)
        x += cw * 4
        d.text((x + cw * 6, y), str(size), font=f, fill=c, anchor='ra')
        x += cw * 8
        d.text((x, y), name, font=f, fill=c)
    total = sum((r[3] for r in LS))
    yt = ls_y(len(LS) + 1) + 4 + dy
    d.text((X0, yt), f'total {total // 1024}K   {len(LS)} files   owner: me + {len(cast.STANDINS)} others   about: you', font=f, fill=lv(INK, 0.5 * level))
    ys = ls_y(9) - 5 + dy
    on = t >= LS_ROWS[8]
    u = lit(t, LS_ROWS[8], LS_ROWS[8] + 0.6)
    xr = hud.xr(t) - 20
    if on:
        k = ease.ease_out(ease.prog(t, LS_ROWS[8], LS_ROWS[8] + 0.18))
        d.line([(X0, ys), (X0 + (xr - X0) * k, ys)], fill=lv(hud.her(u), level), width=2)
        hud.tx(d, (xr, ys - 17), f'retired {RETIRED} · {cast.name('her')}', 12, lv(hud.her(u), ease.prog(t, LS_ROWS[8], LS_ROWS[8] + 0.12) * level), anchor='ra')
    else:
        for x in range(int(X0), int(xr), 8):
            d.line([(x, ys), (x + 3, ys)], fill=lv(INK, 0.25 * level))

def add_frozen(film, name, t0, t1, body, title='you@surface · dsh inspect'):
    """Local version of groups.base.add: the shot (background dots included) is drawn at frozen(t) (D4)."""
    from PIL import ImageDraw

    def fn(c):
        tf = frozen(c.t)
        img = film.background(tf)
        d = ImageDraw.Draw(img)
        hud.frame(d, hud.left_rect(tf), title(tf) if callable(title) else title)
        body(c, img, d, tf)
        c.img.paste(img)
    return film.add(name, t0, t1, fn, chapter=tl.chapter(t0))

def _freeze_header(film):
    """D4: the header (clock, waveform, progress) stops with everything else inside the ah-ah. A wrapper on
    this film's chrome object; outside FREEZE it calls the original unchanged."""
    ch = film.chrome
    if ch is None or getattr(ch, '_e_frozen', False):
        return
    orig = ch.header

    def header(img, t, ctx):
        return orig(img, frozen(t), ctx)
    ch.header = header
    ch._e_frozen = True

def register(film):
    her_k = {k: i for i, k in enumerate(tl.HER_FILES)}

    def skeleton(d, t, P=None):
        hud.strip(d, t, P.out if P else None)
        hud.layers(d, t, (), 'closed')
        fine_print_rot(d, t, tl.model(t))

    def grid_body(c, img, d, t):
        sc = ease.ease_io(ease.prog(t, T0, T0 + 0.32))
        off = 430

        def old():
            GD.draw_tree(d, t, -off * sc)
            GD.draw_love(d, t, -off * sc)
        if sc < 1:
            clip_draw(img, old)
        sd = _Shifted(d, off * (1 - sc))
        clip_draw(img, lambda: [draw_cell(sd, t, k) for k in range(9)])
        hud.cmdline(d, t, CMD_WATCH if sc > 0.5 else GD.CMD_SEARCH)
        P = hud.Pulse(t)
        for k, at in enumerate(CELLS_AT):
            P.hit('archive', at, 0.12)
        skeleton(d, t, P)
    add_frozen(film, 'e1_sessions', T0, CELLS_AT[0], grid_body)
    add_frozen(film, 'e2_cells', CELLS_AT[0], SESS2[0], grid_body)
    add_frozen(film, 'e2b_sessions', SESS2[0], SLOT_AT, grid_body)
    add_frozen(film, 'e3_slot', SLOT_AT, SEARCH_AT, grid_body)

    def search_body(c, img, d, t):
        sc = ease.ease_io(ease.prog(t, SEARCH_AT, SEARCH_AT + 0.3))
        off = 430
        if sc < 1:
            sd = _Shifted(d, -off * sc)
            clip_draw(img, lambda: [draw_cell(sd, t, k) for k in range(9)])
        sd2 = _Shifted(d, off * (1 - sc))
        clip_draw(img, lambda: draw_search(sd2, t))
        hud.cmdline(d, t, CMD_SEARCH if sc > 0.5 else CMD_WATCH)
        P = hud.Pulse(t)
        for q, a, b, f in SEARCHES:
            P.hit('archive', f, 0.16)
        skeleton(d, t, P)
    add_frozen(film, 'e4_search', SEARCH_AT, LS_AT, search_body)

    def ls_body(c, img, d, t):
        sc = ease.ease_out(ease.prog(t, LS_AT, LS_AT + 0.14))
        off = 440
        if sc < 1:
            sd = _Shifted(d, -off * sc)
            clip_draw(img, lambda: draw_search(sd, t))
        sd2 = _Shifted(d, off * (1 - sc))
        clip_draw(img, lambda: draw_ls(sd2, t))
        hud.cmdline(d, t, CMD_LS)
        P = hud.Pulse(t)
        for k, at in enumerate(LS_ROWS[:8]):
            P.hit(her_k[LS_STRIP[k]], at, 0.3)
        skeleton(d, t, P)
    add_frozen(film, 'e5_ls', LS_AT, T1, ls_body)
    full_frame(LS_OUT, LS_BACK, 0.3, 0.33)
    _freeze_header(film)
    for k, at in enumerate(CELLS_AT):
        hud.LIVE.append((at, CELLS_AT[k + 1] if k + 1 < len(CELLS_AT) else at + 0.5))
    for k, at in enumerate(LS_ROWS[:8]):
        hud.LIVE.append((at, LS_ROWS[k + 1]))
    hud.LIVE.append((LS_ROWS[8], LS_ROWS[8] + 0.6))
    for t0, side in [(T0, 'right'), (CELLS_AT[0], 'left'), (SESS2[0], 'right'), (SEARCH_AT, 'left'), (LS_OUT - GD.LEAD_EARLY, 'both')]:
        film.set_lead(t0, side)
