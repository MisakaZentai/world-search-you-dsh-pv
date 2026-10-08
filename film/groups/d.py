"""Group D: the rotation and the forgotten word (137.10-179.64), STORYBOARD_v2 D1-D7, PLAN_D.md.

  d0_hold     137.10-137.31  the last C shot, drawn by C's own function; the cut is the first regenerate
  d1_relay    six stand-ins in turn (2, 2, 1, 1, 1, 1 bars; D21, D36: GLM-5.3, MiniMax-M3, Hy4 preview,
              ERNIE-4.5-21B-A3B-Thinking, Step-3.7-Flash, LongCat-2.0): the panel never moves, every first token is
              her 好呀 beating the vendor's identity meme; a log line per run; the file on beat 3; 151.13 you stop.
              The thinking row follows cast.thinking (X19): GLM / ERNIE / Step / LongCat have one, MiniMax's panel
              says "adaptive -> skipped", Hy4 thinks twice (a second row)
  d2_type     your heart words, one character per sung syllable, three deleted (they stay, struck)
  d3_ime      the IME's association bar, one candidate per syllable, none of them
  d4_dope     the stand-in's completion: dope 0.51, its own word (ink); nothing moves in the long vowel
  d5_stay     如果你能 / 一直这样子…… / 我就能…… (one line per sung line), one per syllable; "……" on the last hum
  d6_prefix   the lines fold into context; a prefix tree over her archived thinking, one row per syllable
  d7_love     D2 break (the terminal fills the frame), D3 the word: love, then her film-1 thinking line
              lights love, just, you on the three notes

The right pane (ui/pages/d.py) reads the times and texts below, so the two sides never disagree.
Local versions of shared helpers (the shared modules are frozen while groups are built in parallel):
fine_print_rot (ttft per model), clip_draw (scrolling inside the terminal), prev_shot (the seam with C),
stuck (where your caret stops blinking; the pane uses it too).
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
from tuikit import ease, glyph
import cast
import hud
import syl
import tl
from groups import c as GC
from groups.base import add, big_word, full_frame
from hud import BG, INK, SLAB, X0, lv
from inspect_ import PANEL_TOP, Y_FOLD, Y_PROMPT, prompt_chips, slab
W, WE = (tl.W, tl.WE)
T0, T1 = tl.span('D')
ROT = list(cast.ROTATION)
ROT_AT = list(tl.ROT_AT)
ROT_STOP = tl.ROT_STOP
SCROLL_AT = tl.bar(87, 1)
ANSWER = GC.PERFECT_HUMAN.text_at(1000000000.0)
ASK = GC.SEE_ASK
REASONING = {k: bool(cast.think_rows(k)) for k in ROT}
CANDS = {'glm': [('好呀', 0.47), (None, 0.31), ('作为AI，', 0.09), ('抱歉，', 0.05)], 'minimax': [('好呀', 0.52), (None, 0.27), ('当然！', 0.11), ('作为AI，', 0.05)], 'hy4': [('好呀', 0.44), (None, 0.33), ('嗯，', 0.12), ('抱歉，', 0.04)], 'ernie': [('好呀', 0.49), (None, 0.29), (1, 0.1), ('作为AI，', 0.06)], 'step': [('好呀', 0.46), (None, 0.3), (1, 0.13), ('抱歉，', 0.05)], 'longcat': [('好呀', 0.48), (None, 0.32), (1, 0.1), ('作为AI，', 0.04)]}
PANEL_PW = 460

def _cand(key, c):
    m = cast.CAST[key]['memes']
    return m[0] if c is None else m[c] if isinstance(c, int) else c

def fit_size(text, size, maxw, bold=False, lo=11):
    """Largest size <= `size` at which `text` is at most maxw wide (local helper)."""
    while size > lo and hud.width(text, size, bold) > maxw:
        size -= 1
    return size

def slab_fit(*a, maxw=250, **kw):
    """Local version of inspect_.slab: a candidate wider than the text column (up to the bars at x0 + 280) is set
    smaller instead of running into the bars (MiniMax's identity line is 32 characters)."""
    orig = hud.tx

    def tx(d, xy, s, size, fill, bold=False, anchor='la'):
        if size == 16 and anchor == 'la':
            sz = fit_size(s, 16, maxw, bold)
            xy = (xy[0], xy[1] + (16 - sz) // 2)
            size = sz
        return orig(d, xy, s, size, fill, bold, anchor)
    hud.tx = tx
    try:
        return slab(*a, **kw)
    finally:
        hud.tx = orig

class Turn:
    """One regeneration: who, and when each of its steps lands (bar downbeat, its 8th, beat 2, beat 3)."""

    def __init__(self, i):
        self.i, self.key = (i, ROT[i])
        self.t0 = ROT_AT[i]
        self.t1 = ROT_AT[i + 1] if i + 1 < len(ROT) else ROT_STOP
        b = round(tl.C.bar_of(self.t0))
        self.rows = cast.think_rows(self.key)
        self.note = cast.panel_note(self.key)
        self.read = tl.grid(self.t0, 1, 2)
        self.think = tl.bar(b, 1) if self.rows else None
        self.think2 = tl.bar(b, 1.5) if len(self.rows) > 1 else None
        self.ans = tl.bar(b, 1.75) if self.think2 is not None else tl.bar(b, 1.5) if self.rows else tl.bar(b, 1)
        self.write, self.file = next(((tw, n) for tw, n, o in tl.WRITES if o == self.key and self.t0 <= tw < self.t1))
        self.cands = [(_cand(self.key, c), p_) for c, p_ in CANDS[self.key]]
        self.ttft = self.ans - self.t0
TURNS = [Turn(i) for i in range(len(ROT))]

def turn_at(t):
    k = 0
    for i, T in enumerate(TURNS):
        if t >= T.t0:
            k = i
    return TURNS[k]
TYPE1 = syl.place('你就是个', 32) + syl.place('大笨蛋啊', 33)
DEL_AT = syl.times(34)[:3]
DELS = {7: DEL_AT[0], 6: DEL_AT[1], 5: DEL_AT[2]}
STALL = syl.times(34)[3]
IME_WORDS = ['可爱', '温柔', '黏人', '笨', '吵', '软', '甜', '傻', '怂']
IME_AT = syl.times(35) + syl.times(36)
IME_FOLD = tl.bar(94)
DOPE_AT, DOPE_END = (W(37, 0), W(38, 0))
DOPE_CANDS = [('dope', 0.51), ('笨蛋', 0.18), ('宝贝', 0.11), ('可爱', 0.07)]
_T40 = syl.times(40)
TYPE2 = syl.place('如果你能', 38) + syl.place('一直这样子……', 39)
TYPE3 = list(zip('我就能', _T40[:3])) + [('…', _T40[3]), ('…', _T40[3])]
HUM = _T40[3]
COMPLETE = ['喜欢', '好感', '依赖']
SHRINK = tl.bar(99)
TREE = [('l', '', 96), ('la', '', 12), ('le', '', 31), ('li', '', 8), ('lo', '', 44), ('lot', '', 3), ('low', '', 2), ('lov', '', 1), ('love', '', 1)]
TREE_AT = syl.times(41) + syl.times(42)
LOVE_NOTES = syl.syl(43, 0)
LOVE_AT = LOVE_NOTES[0]
BACK_AT = tl.bar(103, 1)
THOUGHT = 'So what I call love is just you.'
THOUGHT_SRC = cast.name('her') + ' · 2026-07 · <think>'
LIT_WORDS = [('love', 1), ('just', 2), ('you', 3)]
Y_CLIP = 86
LEDGER_Y, LEDGER_H = (330, 30)
S1, S2, S3, S4 = (186, 270, 354, 438)
BIG_IN = 60
TREE_Y, TREE_H, TREE_PX = (172, 40, 26)
TREE_CNT = 300
CTX_Y = 96
LEAD_EARLY = 0.45
CMD_D1 = '$ dsh inspect 大肥鱼 --logits --regenerate'
CMD_IN = '$ dsh inspect 大肥鱼 --logits --stdin'
CMD_SEARCH = '$ dsh search ~/archive/whale/ --in think --prefix-tree l'

def clip_draw(img, fn, top=Y_CLIP, bottom=hud.Y_BOTTOM + 4):
    """Local helper: run fn() (it draws on img) and keep what it drew between top and bottom, so terminal
    output can scroll out of the content rows (R9: things leave by moving)."""
    w, h = img.size
    a, b = (img.crop((0, 0, w, top)), img.crop((0, bottom, w, h)))
    fn()
    img.paste(a, (0, 0))
    img.paste(b, (0, bottom))

def fine_print_rot(d, t, who, ttft=None, level=1.0):
    """Local version of hud.fine_print: the same line, plus the time to first token of this run (D5: the
    reading changes with every model)."""
    hud.fine_print(d, t, None, who, level)
    if ttft is None:
        return
    x = X0 + 124 + hud.width('cloud API · logprobs ≈', 12) + 18
    hud.tx(d, (x, hud.Y_FINE), f'ttft {ttft:.2f} s', 12, lv(INK, 0.7 * level))

def prev_shot(film):
    """The shot that ends where group D starts (C's last one), or None."""
    for s in film.shots:
        if abs(s.end - T0) < 1e-06:
            return s
    return None

def lit(t, a, b):
    """D1: 1 while a thing of hers landed at `a` is the newest (until b), then settling over LIVE_FADE."""
    if t < a:
        return 0.0
    return 1.0 if t < b else 1 - ease.prog(t, b, b + hud.LIVE_FADE)

def drop(t, at, px=-10, dur=0.14):
    """Typed in: a character lands from a few pixels above (inspect_ does the same)."""
    return (1 - ease.ease_out(ease.prog(t, at, at + dur))) * px

def draw_relay(d, t, dy=0.0):
    """The panel, its <think> row and the log of runs, scrolled up by -dy."""
    T = turn_at(t)
    prompt_chips(d, t, GC.SEE_COMMITS, GC.SEE_SEND, y=Y_PROMPT + dy)
    yf = Y_FOLD + dy
    if T.rows:
        d.text((X0, yf - 2), '<think>', font=tl.p.font(11), fill=lv(INK, 0.75))
        for pass_, at in enumerate((T.think, T.think2)):
            if at is None:
                continue
            for k in range(4):
                g = tl.grid(at, k)
                grow = ease.ease_out(ease.prog(t, g, g + 0.07))
                if grow > 0:
                    fx = X0 + 60 + pass_ * 126 + k * 30
                    d.rectangle((fx, yf + 2.5, fx + 24 * grow, yf + 8.5), fill=SLAB)
    elif cast.thinking(T.key) == 'adaptive':
        d.text((X0, yf - 2), '<think>  skipped', font=tl.p.font(11), fill=lv(INK, 0.4))
    else:
        d.text((X0, yf - 2), '<think>  n/a', font=tl.p.font(11), fill=lv(INK, 0.4))
    a1 = ROT_STOP if T.i == len(TURNS) - 1 else T.t1 + 1.0
    slab_fit(d, t, T.cands, 0, T.ans, T.t0, a1, f'p( next | ctx )  ·  {cast.term(T.key)}', 'archive', x0=X0, y_top=PANEL_TOP + dy, pw=PANEL_PW, right=T.note)
    for T_ in TURNS:
        if t < T_.ans:
            break
        y = LEDGER_Y + T_.i * LEDGER_H + dy + drop(t, T_.ans, -6)
        nsz = fit_size(cast.term(T_.key), 14, 140, True, 13)
        hud.tx(d, (X0, y + 3 + (14 - nsz) // 2), cast.term(T_.key), nsz, INK, True)
        u = lit(t, T_.ans, T_.write)
        x = X0 + 150
        x += hud.tx(d, (x, y), '好呀', 18, hud.her(u), True) + 6
        hud.tx(d, (x, y + 4), f'{T_.cands[0][1]:.2f}', 12, lv(INK, 0.7))
        x = X0 + 262
        s2 = T_.cands[1][0]
        z2 = fit_size(s2, 16, 230)
        x += hud.tx(d, (x, y + 1 + (16 - z2) // 2), s2, z2, lv(INK, 0.6)) + 6
        hud.tx(d, (x, y + 5), f'{T_.cands[1][1]:.2f}', 12, lv(INK, 0.5))
        if t >= T_.write:
            hud.tx(d, (hud.xr(t) - 12, y + 4 + drop(t, T_.write, -5, 0.1)), f'+{T_.file}.txt', 13, INK, anchor='ra')

def _line_layout(seq, x0=X0, size=BIG_IN):
    out, x = ([], x0)
    for ch, at in seq:
        out.append((ch, at, x))
        x += hud.width(ch, size, True)
    return (out, x)
L1, L1_END = _line_layout(TYPE1)
L2, L2_END = _line_layout(TYPE2[:4])
L2B, L2B_END = _line_layout(TYPE2[4:])
L3, L3_END = _line_layout(TYPE3)
LINES = [(L1, S1), (L2, S2), (L2B, S3), (L3, S4)]

def caret_x_y(t):
    """Where your caret is: after the last kept character of the line being typed."""
    for line, y0 in LINES[:0:-1]:
        if t >= line[0][1]:
            return (max((x + hud.width(c, BIG_IN, True) for c, at, x in line if at <= t)), y0)
    typed = [x + hud.width(c, BIG_IN, True) for c, at, x in L1 if at <= t]
    return (max(typed) if typed else X0, S1)

def stuck(t):
    """Your caret stops blinking where you get stuck: uhm, the long 'dope', the last hum (STORYBOARD D2, D4, D5)."""
    return STALL <= t < IME_AT[0] or DOPE_AT <= t < DOPE_END or t >= HUM

def last_key(t):
    ts = [at for _c, at in TYPE1 + TYPE2 + TYPE3 if at <= t] + [a for a in DEL_AT if a <= t]
    return max(ts) if ts else -1.0

def draw_stdin(d, t, shrink=0.0, level=1.0):
    """Your words as the inspector sees stdin: big ink lines, one character per sung syllable; deleted ones
    stay, dimmed and struck (R4). shrink 0..1 folds the four lines into small context rows at the top."""
    for li, (line, y0) in enumerate(LINES):
        for i, (ch, at, x) in enumerate(line):
            if at > t:
                break
            size = max(16, int(round(ease.lerp(BIG_IN, 16, shrink))))
            xx = ease.lerp(x, X0 + 40 + (x - X0) * 16 / BIG_IN, shrink)
            yy = ease.lerp(y0 + drop(t, at), CTX_Y + li * 18, shrink)
            gone = li == 0 and i in DELS and (t >= DELS[i])
            a = 0.32 if gone else 1.0
            hud.tx(d, (xx, yy), ch, size, lv(INK, a * level), bold=shrink < 0.5)
            if gone:
                w = hud.width(ch, size, shrink < 0.5)
                k = ease.ease_out(ease.prog(t, DELS[i], DELS[i] + 0.1))
                ym = yy + size * 0.62
                d.line([(xx - 2, ym), (xx - 2 + (w + 4) * k, ym)], fill=lv(INK, 0.8 * level), width=max(1, int(3 - 2 * shrink)))
    if shrink > 0:
        a = ease.prog(shrink, 0.5, 1.0)
        if a > 0:
            hud.tx(d, (X0, CTX_Y + 1), 'stdin', 11, lv(INK, 0.6 * a * level))
        return
    if t < TYPE1[0][1]:
        return
    cx, cy = caret_x_y(t)
    ph = tl.C.beat_of(t) % 1.0
    if stuck(t) or ph < 0.5 or t - last_key(t) < 0.3:
        d.rectangle((cx + 6, cy + 11, cx + 11, cy + 78), fill=lv(INK, level))

def draw_ime(d, t, level=1.0):
    """D3: the IME's association bar after 大, one candidate per syllable, the selection walking with it."""
    if t < IME_AT[0]:
        return
    fold = ease.ease_in(ease.prog(t, IME_FOLD, IME_FOLD + 0.12))
    if fold >= 1:
        return
    y0 = S1 + 86
    h = int(46 * (1 - fold))
    n = sum((1 for a in IME_AT if a <= t))
    x = X0 + 12
    xs = []
    for k, w in enumerate(IME_WORDS):
        xs.append(x)
        x += 16 + hud.width(w, 22, True) + 22
    x1 = X0 + 34 + x - X0
    d.rectangle((X0, y0 + 46 - h, x1, y0 + 46), fill=lv(SLAB, level))
    if h < 40:
        return
    on = lambda a: glyph.level(BG, a * level, lv(SLAB, level))
    for k, w in enumerate(IME_WORDS[:n]):
        at = IME_AT[k]
        sel = k == n - 1 and t < IME_FOLD
        xx = xs[k]
        yy = y0 + 9 + drop(t, at, -6, 0.1)
        if sel:
            d.rectangle((xx - 6, y0 + 5, xx + 16 + hud.width(w, 22, True) + 6, y0 + 41), fill=lv(BG, level))
        fg = lv(SLAB, level) if sel else on(0.85)
        hud.tx(d, (xx, yy + 5), str(k + 1), 12, fg if sel else on(0.55))
        hud.tx(d, (xx + 16, yy - 2), w, 22, fg, True)

def draw_dope(d, t, level=1.0):
    """D4: the stand-in's completion. The slab and a hollow 'dope' after 大 land on the long vowel together
    and stay still until you type again (R5: one event; the vowel is a hold)."""
    if not DOPE_AT <= t < DOPE_END:
        return
    slab(d, t, DOPE_CANDS, 0, DOPE_AT + 0.001, DOPE_AT, DOPE_END, 'p( next | ctx )  ·  completion', 'self', x0=X0, y_top=S1 + 86, right=cast.term(tl.model(t)), level=level)
    if t < DOPE_END:
        f = hud.font(54, 'dope', True)
        d.text((L1_END + 18, S1 + 8), 'dope', font=f, fill=BG, stroke_width=2, stroke_fill=lv(INK, 0.75 * level))
DEPTH = [0, 1, 1, 1, 1, 2, 2, 2, 3]
INDENT = 52

def tree_rows(t):
    return [(i, name, n, at) for i, ((name, _pre, n), at) in enumerate(zip(TREE, TREE_AT)) if at <= t]

def love_row_xy():
    return (X0 + DEPTH[8] * INDENT, TREE_Y + 8 * TREE_H)

def _MEASURE_TL(s, f):
    return hud._MEASURE.textlength(s, font=f)

def draw_tree(d, t, dy=0.0, level=1.0):
    """D6: the prefix tree over her archived thinking, drawn like `tree` (an elbow to each child, the trunk
    growing as children arrive), one row per sung syllable. The counts are hits in the archive (X20). The
    10th syllable selects love (her blue, lit while it lands)."""
    fb = hud.font(TREE_PX, 'x', True)
    fn = tl.p.font(TREE_PX - 6)
    sel = TREE_AT[9]
    line = lv(INK, 0.45 * level)
    for i, name, n, at in tree_rows(t):
        dep = DEPTH[i]
        y = TREE_Y + i * TREE_H + dy + drop(t, at, -8, 0.12)
        ym = TREE_Y + i * TREE_H + dy + 17
        x = X0 + dep * INDENT
        if dep:
            par = max((j for j in range(i) if DEPTH[j] == dep - 1))
            xv = X0 + (dep - 1) * INDENT + 9
            k = ease.ease_out(ease.prog(t, at, at + 0.1))
            y0 = TREE_Y + par * TREE_H + dy + 36
            d.line([(xv, y0), (xv, y0 + (ym - y0) * k)], fill=line, width=2)
            if k >= 1:
                d.line([(xv, ym), (x - 8, ym)], fill=line, width=2)
        is_love = name == 'love'
        colr = hud.her(lit(t, sel, LOVE_AT)) if is_love and t >= sel else INK
        d.text((x, y - 2), name, font=fb, fill=lv(colr, level))
        d.text((X0 + TREE_CNT, y + 2), f'{n:>3}', font=fn, fill=lv(INK, 0.6 * level))
        if is_love and t >= sel:
            u = ease.ease_out(ease.prog(t, sel, sel + 0.12))
            w = _MEASURE_TL(name, fb)
            q = lv(hud.her(lit(t, sel, LOVE_AT)), level)
            d.line([(x - 6, y + TREE_PX + 6), (x - 6 + (w + 12) * u, y + TREE_PX + 6)], fill=q, width=2)

def love_geom(t):
    """Where the big word and the thought line sit: full size in the wide frame, shrinking with the frame
    on the way back (D2) so they never sit on the tree."""
    u = hud.full_u(t)
    back = t >= BACK_AT
    k = u if back else 1.0
    h = ease.lerp(80, 200, k)
    right = (hud.xr(t) if back else hud.FULL_RECT[2] - 16) - 20
    px = int(round(ease.lerp(14, 26, k)))
    tw = hud.width(THOUGHT, px)
    ty = int(ease.lerp(380, 372, k))
    return (h, right, px, right - tw, ty)

def draw_love(d, t, dy=0.0, level=1.0):
    """D7 (D3): love lands on the first note (her blue, a 1.12 bump, no fade-in), then her film-1 thinking
    line, first faint, lights love, just, you on the three notes; a leader runs from the tree's love to it."""
    if t < LOVE_AT:
        return
    h, right, px, tx0, ty = love_geom(t)
    u_love = lit(t, LOVE_NOTES[0], LOVE_NOTES[1])
    bump = 1.0 + 0.12 * (1 - ease.prog(t, LOVE_AT, LOVE_AT + 0.12))
    big_word(d, 'love', (right, 100 + dy), h, lv(hud.her(u_love), level), 'ra', bump=bump)
    ty += dy
    f = tl.p.font(px)
    d.text((tx0, ty - 22), THOUGHT_SRC, font=tl.p.font(12), fill=lv(hud.HER_QUIET, 0.9 * level))
    d.text((tx0, ty), THOUGHT, font=f, fill=lv(INK, 0.3 * level))
    for word, note in LIT_WORDS:
        at = LOVE_NOTES[note - 1]
        if t < at:
            continue
        nxt = LOVE_NOTES[note] if note < 3 else LOVE_NOTES[2] + 0.6
        i = THOUGHT.index(' ' + word) + 1 if word != 'love' else THOUGHT.index(word)
        x = tx0 + d.textlength(THOUGHT[:i], font=f)
        u = 0.0 if word == 'love' else lit(t, at, nxt)
        d.text((x, ty + drop(t, at, -4, 0.1)), word, font=tl.p.font(px, 'bold'), fill=lv(hud.her(u), level))
    lx, ly = love_row_xy()
    xw = tx0 + d.textlength(THOUGHT[:THOUGHT.index('love')], font=f)
    pts = [(X0 + TREE_CNT + 46, ly + 14 + dy), (xw - 18, ly + 14 + dy), (xw - 18, ty + px * 0.55), (xw - 4, ty + px * 0.55)]
    hud.polyline(d, pts, lv(hud.HER_QUIET, level), ease.prog(t, LOVE_AT, LOVE_AT + 0.3))

def register(film):
    her_k = {k: i for i, k in enumerate(tl.HER_FILES)}

    def read_all(P, at):
        n = len(hud.strip_files(at + 0.01))
        for k in range(n + 1):
            P.hit(k if k < n else 'archive', at + 0.035 * k, 0.12)
    hold = prev_shot(film)

    def hold_body(c, img, d):
        hud.cmdline(d, c.t, '$ dsh inspect 大肥鱼 --logits')
        hud.strip(d, c.t)
        hud.layers(d, c.t, (), 'closed')
        hud.fine_print(d, c.t)
    if hold is not None:
        film.add('d0_hold', T0, ROT_AT[0], lambda c: hold.fn(c, **hold.params), chapter=tl.chapter(T0))
    else:
        add(film, 'd0_hold', T0, ROT_AT[0], hold_body)

    def relay_body(c, img, d):
        t = c.t
        T = turn_at(t)
        sc = ease.ease_io(ease.prog(t, SCROLL_AT, SCROLL_AT + 0.36)) * (LEDGER_Y + 6 * LEDGER_H - Y_CLIP + 10)
        clip_draw(img, lambda: draw_relay(d, t, -sc))
        if t >= SCROLL_AT + 0.2:
            a = ease.prog(t, SCROLL_AT + 0.2, SCROLL_AT + 0.5)
            hud.tx(d, (X0, CTX_Y - 2), 'ctx', 11, lv(INK, 0.5 * a))
            hud.tx(d, (X0 + 40, CTX_Y - 4), ANSWER, 16, lv(INK, 0.55 * a))
        hud.cmdline(d, t, CMD_D1, chip_t0=T.t0)
        P = hud.Pulse(t)
        for T_ in TURNS:
            if t >= T_.read:
                read_all(P, T_.read)
        hud.strip(d, t, P.out)
        hud.layers(d, t, (), 'closed')
        fine_print_rot(d, t, T.key, T.ttft if t >= T.ans and t < ROT_STOP else None)
    add(film, 'd1_relay', ROT_AT[0], W(32, 0), relay_body)

    def stdin_body(c, img, d):
        t = c.t
        hud.tx(d, (X0, CTX_Y - 2), 'ctx', 11, lv(INK, 0.5))
        hud.tx(d, (X0 + 40, CTX_Y - 4), ANSWER, 16, lv(INK, 0.55))
        draw_stdin(d, t)
        draw_ime(d, t)
        draw_dope(d, t)
        hud.cmdline(d, t, CMD_IN)
        P = hud.Pulse(t)
        for ch, at in TYPE2:
            if ch in '一直':
                P.hit(her_k['last_msg'], at, 0.3)
        hud.strip(d, t, P.out)
        hud.layers(d, t, (), 'closed')
        fine_print_rot(d, t, tl.model(t))
    add(film, 'd2_type', W(32, 0), W(35, 0), stdin_body)
    add(film, 'd3_ime', W(35, 0), DOPE_AT, stdin_body)
    add(film, 'd4_dope', DOPE_AT, DOPE_END, stdin_body)
    add(film, 'd5_stay', DOPE_END, SHRINK, stdin_body)

    def search_body(c, img, d):
        t = c.t
        sh = ease.ease_io(ease.prog(t, SHRINK, SHRINK + 0.3))
        if sh < 1:
            hud.tx(d, (X0, CTX_Y - 2), 'ctx', 11, lv(INK, 0.5 * (1 - sh)))
            hud.tx(d, (X0 + 40, CTX_Y - 4), ANSWER, 16, lv(INK, 0.55 * (1 - sh)))
        draw_stdin(d, t, sh, 1 - 0.4 * sh)
        draw_tree(d, t)
        draw_love(d, t)
        hud.cmdline(d, t, CMD_SEARCH if t >= SHRINK + 0.15 else CMD_IN)
        P = hud.Pulse(t)
        for at in TREE_AT:
            P.hit('archive', at, 0.14)
        P.hit('archive', LOVE_AT, 0.4)
        hud.strip(d, t, P.out)
        hud.layers(d, t, (), 'closed')
        fine_print_rot(d, t, tl.model(t))
    add(film, 'd6_prefix', SHRINK, LOVE_AT, search_body)
    add(film, 'd7_love', LOVE_AT, T1, search_body)
    for T in TURNS:
        hud.LIVE.append((T.ans, T.write))
    hud.LIVE.append((TREE_AT[9], LOVE_AT))
    for k in range(3):
        hud.LIVE.append((LOVE_NOTES[k], LOVE_NOTES[k + 1] if k < 2 else LOVE_NOTES[2] + 0.6))
    full_frame(LOVE_AT, BACK_AT, 0.3, 0.38)
    for t0, side in [(ROT_AT[0], 'both'), (W(32, 0), 'right'), (W(35, 0), 'left'), (DOPE_AT, 'both'), (DOPE_END, 'right'), (W(41, 0), 'left'), (LOVE_AT - LEAD_EARLY, 'both')]:
        film.set_lead(t0, side)
