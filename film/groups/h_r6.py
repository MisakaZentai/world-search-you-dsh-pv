"""Group H r6 (r17 sample, D59; STORY_20261005.md, last part): you do not restore her, you read her old session from
the top. Built on groups/h_r5.py (kept unchanged; its drawing helpers are imported, not copied, where they did not
change). What r6 changes:

  left      the command, the trace and the frame title read her session instead of planning a restore:
            `$ dsh session read 大肥鱼 --archive --from 1`; the trace opens the session and reads memory / persona /
            session (the three ruff checks, the puppy, the tomato, 明天见 stay frame for frame), then asks for its
            model: DeepSeek-V4.1-Flash -> Model Not Exist (the opening's real error). No new model anywhere: no
            `plan.model = ...`, no `restore(..., model=...)`, no "?" and no `云端 · preview` in the model pane.
  header    from T0 (275.61) the stage reads `09 READ` (it read `08 RESTORE` since interlude 3, which still does).
  right     ui/pages/h_r6.py (shot to ui/pane_h_r6/): no pointer, no menu, no click. The label stays hers
            (DeepSeek-V4.1-Flash) and the composer stays dsh's blocked one (当前模型不可用，请先选择模型) to the end;
            the scroll back to film 1's C page (282.86) is the reading and stays.
  PRESS     290.80 the chime sounds (mixed afterwards, as before); nothing is clicked. The slide into film 1's frame
            (MOVE, _finish) is r5's.
  LAND      film 1's last frame as film 1 has it: her own label, nothing erased (r5d had written v5 into it). 在吗？ on
            the 8ths, the caret, the push-in and the pull-back (D33 ④) as before.
  NOW_AT    DSH_END=story only: once film 1's frame has held after the pull-back (tl.END, 297.5, on the beat grid run on
            past the music), a hard cut back to now for NOW_LEN s: the usual paper layout, the left terminal with
            nothing but `you@surface:~$` and your cursor blinking (ink, not her blue), her session open on the right
            where your reading stopped (明天见 / 明天见喵～ ... 不客气～明天也要来找我哦, in the session's order),
            the composer blocked, no new line. Only the cursor and the header's elapsed move; the song's counter holds
            at its end. The music has ended (292.5): silence.

Switches: DSH_H=r6 (film.py); DSH_END=story adds the last shot (END = NOW_AT + NOW_LEN) and gives the merged one the
persona's name (cast.py). tl.END is not changed: everything else that runs to it renders as before.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import os
import numpy as np
from PIL import Image, ImageDraw
import cast
import hud
import panes
import tl
from groups import b_open as BO
from groups import c_pane as CPN
from groups import d_pane as DP
from groups import g as GG
from groups import h as GH
from groups import h_r5 as H5
from groups.base import add, full_frame
from hud import BG, INK, lv
from panes import FAINT, SUB, TXT
from tuikit import ease, glyph
from tuikit.uipane import PaneFrames
P = tl.p
FPS = P.FPS
mtx, mw = (BO.mtx, BO.mw)
COL, MEM = (CPN.COL, CPN.MEM)
T0, T1 = (H5.T0, H5.T1)
ROW_T, PROG_T, RUFF, H1_BACK, SCROLL = (H5.ROW_T, H5.PROG_T, H5.RUFF, H5.H1_BACK, H5.SCROLL)
FRUIT, TOMATO_T, PIN_T, JUICE, JUICE_END = (H5.FRUIT, H5.TOMATO_T, H5.PIN_T, H5.JUICE, H5.JUICE_END)
QUIET, PRESS, REVEAL, RIGHT_BACK = (H5.QUIET, H5.PRESS, H5.REVEAL, H5.RIGHT_BACK)
LAND, MOVE, KEYS, RETURN, BLINK = (H5.LAND, H5.MOVE, H5.KEYS, H5.RETURN, H5.BLINK)
ZOOM_IN, ZOOM_OUT, DOG = (H5.ZOOM_IN, H5.ZOOM_OUT, H5.DOG)
CHIME_T, CHIME_WAV = (PRESS, GH.CHIME_WAV)
SUPPORT = H5.SUPPORT
STORY = os.environ.get('DSH_END') == 'story'
NOW_AT = tl.END
NOW_LEN = 4.0
END = NOW_AT + NOW_LEN if STORY else tl.END
CURSOR_BLINK = BLINK
assert ZOOM_OUT[1] + 0.5 <= NOW_AT
TITLE = 'you@surface · read'
CMD = '$ dsh session read 大肥鱼 --archive --from 1'
STAGE = '09 READ'
NOW_TITLE = 'you@surface'
PROMPT = 'you@surface:~$'

def _model(d, t, c, level):
    """Her model, asked for on "If" (282.86) and struck out on "you're" with the opening's error beside it. Nothing
    comes after it: no new model, no question mark."""
    x, y = (c[0] + 12, c[1] + 22)
    lit = t >= FRUIT[0]
    u0 = ease.ease_out(ease.prog(t, FRUIT[0], FRUIT[0] + 0.12))
    old = cast.name('her')
    w = mtx(d, (x, y), old, 14, lv(INK, (FAINT + (TXT - FAINT) * u0) * level), bold=lit)
    if t >= FRUIT[1]:
        u1 = ease.ease_out(ease.prog(t, FRUIT[1], FRUIT[1] + 0.12))
        d.line([(x - 2, y + 9), (x + (w + 4) * u1, y + 9)], fill=lv(INK, level), width=2)
        mtx(d, (x + w + 14, y + 1), 'Model Not Exist', 13, lv(INK, SUB * u1 * level))
CODE = [(T0, 's = session.open("大肥鱼", archived=True)', None), (RUFF[0], 's.memory', (RUFF[0] + 0.05, '8/8 · ok')), (RUFF[1], 's.persona', (RUFF[1] + 0.05, '大肥鱼 · ok')), (RUFF[2], 's.session', (RUFF[2] + 0.05, '412 行 · ok')), (FRUIT[0], 's.model', (FRUIT[1], f'{cast.name('her')} · Model Not Exist')), (PIN_T[0], 'memory["see_you"].unpin()', (JUICE, '"明天见"'))]

def _trace(d, t, r, level=1.0):
    shown = [x for x in CODE if x[0] <= t]
    if not shown:
        return
    last = shown[-1][0]
    sc = ease.ease_out(ease.prog(t, last, last + 0.14))
    for pos, (at, s, ret) in enumerate(reversed(shown[-2:])):
        y = r[1] + 30 - pos * 19 + (1 - sc) * 19
        a = (TXT if pos == 0 else SUB) * ease.prog(t, at, at + 0.1) * level
        n = int((t - at) * BO.CODE_CPS) + 1
        w = mtx(d, (r[0] + 10, y), s[:n], 14, lv(INK, 0.92 * a), bold=pos == 0)
        if ret and t >= ret[0] and (n >= len(s)):
            mtx(d, (r[0] + 10 + w + 12, y), '→ ' + ret[1], 14, lv(INK, 0.7 * a * ease.prog(t, ret[0], ret[0] + 0.1)), bold=True)
RUN = {'trace': [(a, ret[0] if ret else a + 0.6) for a, _s, ret in CODE], 'memory': [(PROG_T[0], RUFF[0] + 0.1), (PIN_T[0], JUICE + 0.3)], 'persona': [(RUFF[1] - 0.05, RUFF[1] + 0.1)], 'session': [(RUFF[2] - 0.05, RUFF[2] + 0.1)], 'model': [(FRUIT[0], FRUIT[1] + 0.2)]}
STATUS = {'memory': 'by lovability'}

def draw_left(img, d, t, level=1.0):
    """h_r5.draw_left with r6's trace and model pane (and no `云端 · preview` status)."""
    L = H5.layout(t)
    ug = H5._u_gone(t)
    bk = H5.back_k(t)
    for name, rect in L.items():
        lvl = level * (1 - ug if name in ('persona', 'session') else 1.0)
        if name == 'trace':
            lvl *= H5.back_k(t, 'trace')
        elif name == 'model':
            lvl *= bk
        if lvl <= 0.01:
            continue
        if level > 0.01:
            d.rectangle(rect, fill=BG)
        with panes.Clip(img, rect) as dd:
            if name == 'trace':
                _trace(dd, t, rect, lvl)
            elif name == 'memory':
                H5._memory(dd, t, rect, lvl)
            elif name == 'persona':
                H5._persona(dd, t, rect, lvl)
            elif name == 'session':
                H5._session(dd, t, rect, lvl)
            elif name == 'model':
                _model(dd, t, rect, lvl)
        panes.box(d, rect, name, t, panes.run_k(t, RUN.get(name, ())), lvl, STATUS.get(name, ''))
    with CPN._strip_in(MEM):
        hud.strip(d, t, None, level=level * bk, merged=1.0)
    d.rectangle((MEM[0] + 4, MEM[1] + 8, MEM[2] - 4, MEM[1] + 21), fill=BG)
    panes.box(d, MEM, 'mem', t, 0.0, level * bk)

def _body(c, img, d):
    t = c.t
    q = H5.quiet_k(t)
    hud.tx(d, (36, hud.Y_CMD), CMD, 13, lv(INK, 0.86 * q * H5.back_k(t)))
    draw_left(img, d, t, q)

def status_r6(t, ctx=None):
    """tl.status with the stage reading 09 READ from T0."""
    s = list(tl.status(t, ctx))
    if t >= T0:
        s[0] = (STAGE, s[0][1])
    return s

def _status_x(t):
    """groups.h._status_x on r6's header (the stage is shorter from T0, so elapsed sits further left)."""
    f = P.font(14, 'bold')
    meas = ImageDraw.Draw(Image.new('L', (1, 1)))
    x = 24 + meas.textlength('WORLD.SEARCH(YOU);  you@surface:~$' + '   ', font=f)
    for text, _c in status_r6(t):
        if text.startswith('elapsed'):
            return (x, meas.textlength(text, font=f))
        x += meas.textlength(text + '   ', font=f)
    return (x, 0.0)

def last_frame(t: float) -> Image.Image:
    """Film 1's last frames re-timed onto this song's 8ths (groups.h), untouched: her own model label."""
    F = GH.F1_FILES
    if t < KEYS[0]:
        name = F['empty']
    elif t < KEYS[1]:
        name = F['k1'][min(3, int((t - KEYS[0]) * FPS + 1e-06))]
    elif t < KEYS[2]:
        name = F['k2']
    elif t < RETURN:
        name = F['full']
    else:
        name = F['full'] if (t - RETURN) // BLINK % 2 == 0 else F['dim']
    return Image.fromarray(GH.f1(name).copy())

def _finish(img, t):
    """h_r5._finish, landing on film 1's own frame (no label written into it)."""
    if not PRESS <= t < LAND:
        return None
    a = np.asarray(img, np.float32).copy()
    bgc = np.array(BG, np.float32)
    ex, ew = _status_x(t)
    cy = 14
    k_old = ease.smooth(ease.prog(t, PRESS, PRESS + 0.25))
    sl = (slice(cy - 2, cy + 20), slice(int(ex) - 2, int(ex + ew) + 4))
    a[sl] = a[sl] * (1 - k_old) + bgc * k_old
    px0, py0, px1, py1, s = H5.pane_rect(t)
    blk = H5._f1_black()
    kb = ease.smooth(ease.prog(t, MOVE[0], MOVE[0] + 0.45))
    kw = kb
    M = np.full(a.shape[:2], kb, np.float32)
    iy0, iy1, ix0, ix1 = (int(max(0, py0)), int(min(P.H, py1)), int(max(0, px0)), int(min(P.W, px1)))
    M[iy0:iy1, ix0:ix1] = kw
    CP = H5.CARD_PANE
    cx0, cy0 = (px0 + CP[0] * s, py0 + CP[1] * s)
    cx1, cy1 = (px0 + CP[2] * s, py0 + CP[3] * s)
    jy0, jy1, jx0, jx1 = (int(max(0, cy0)), int(min(P.H, cy1)), int(max(0, cx0)), int(min(P.W, cx1)))
    M[jy0:jy1, jx0:jx1] = 0
    a = a * (1 - M[..., None]) + blk * M[..., None]
    U = ease.smooth(ease.prog(t, MOVE[0] + 0.25, MOVE[1]))
    if U > 0 and jy1 > jy0 and (jx1 > jx0):
        a[jy0:jy1, jx0:jx1] = GH._to_deep(a[jy0:jy1, jx0:jx1], U)
    img2 = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    m = ease.ease_io(ease.prog(t, PRESS + 0.45, LAND - 0.05))
    k_new = ease.smooth(ease.prog(t, PRESS + 0.25, PRESS + 0.45))
    fx, fy = (ease.lerp(ex, GH.TAIL_F1[0], m), ease.lerp(cy, GH.TAIL_F1[1] - 1, m))
    col = np.array(INK, np.float32) * (1 - m) + np.array((205, 211, 226), np.float32) * m
    font = hud.font(int(round(ease.lerp(14, 13, m))), '用时', bold=m < 0.5)
    lay = Image.new('L', img2.size, 0)
    ImageDraw.Draw(lay).text((fx, fy), '用时 3分27秒', font=font, fill=int(255 * k_new))
    al = np.asarray(lay, np.float32)[..., None] / 255
    cur = np.asarray(img2, np.float32) * (1 - al) + col[None, None, :] * al
    w = ease.smooth(ease.prog(t, LAND - 0.16, LAND))
    if w > 0:
        cur = cur * (1 - w) + np.asarray(last_frame(KEYS[0] - 0.001), np.float32) * w
    return Image.fromarray(np.clip(cur, 0, 255).astype(np.uint8))

def cursor_on(t: float) -> bool:
    return (t - NOW_AT) // CURSOR_BLINK % 2 == 0

def _hold_counter(chrome, img, t, ctx):
    """After the music: the header's song counter holds at its end (mm:ss / mm:ss of the song) and its beat dot rests;
    elapsed (a status item, tl.status) keeps counting. Drawn over tuikit's header with its own arithmetic."""
    x0, y0, x1, y1 = P.rect('header')
    d = ImageDraw.Draw(img)
    f = P.font(14, 'bold')
    cy = (y0 + y1) // 2 - 8
    total = P.duration
    mm = lambda s: f'{int(s // 60):02d}:{int(s % 60):02d}'
    chap = chrome.chapter(t, ctx) if chrome.chapter else ''
    real = f'{chap}   {mm(t)} / {mm(total)}'
    held = f'{chap}   {mm(total)} / {mm(total)}'
    rw = d.textlength(real, font=f)
    d.rectangle((x1 - 24 - rw - 2, cy - 2, x1 - 22, cy + 19), fill=BG)
    hw = d.textlength(held, font=f)
    d.text((x1 - 24 - hw, cy), held, font=f, fill=P.color('ink'))
    wx1 = int(x1 - 40 - rw)
    d.ellipse((wx1 + 1, cy + 3, wx1 + 11, cy + 13), fill=BG)
    d.ellipse((wx1 + 3, cy + 5, wx1 + 9, cy + 11), fill=glyph.level(hud.HER_QUIET, 0.6, P.color('bg')))

def _now(film, c):
    t = c.t
    img = film.background(t)
    d = ImageDraw.Draw(img)
    hud.frame(d, hud.left_rect(t), NOW_TITLE)
    w = hud.tx(d, (36, hud.Y_CMD), PROMPT, 13, lv(INK, 0.86))
    if cursor_on(t):
        cx = 36 + w + 9
        d.rectangle((cx, hud.Y_CMD + 1, cx + 7, hud.Y_CMD + 16), fill=INK)
    c.img.paste(img)

def register(film):
    full_frame(T0, H1_BACK, 0.3, 0.4)
    for i in range(7):
        hud.LIVE.append((PROG_T[i], PROG_T[i + 1] if i < 6 else RUFF[0]))
    for (a, _s), nx in zip(H5.TOM_SEG, [x[0] for x in H5.TOM_SEG[1:]] + [PIN_T[0]]):
        hud.LIVE.append((a, nx))
    hud.LIVE.append((JUICE, JUICE_END))
    add(film, 'h1_check', T0, H1_BACK, _body, TITLE)
    add(film, 'h2_model', H1_BACK, TOMATO_T[0] - 0.3, _body, TITLE)
    add(film, 'h3_tomato', TOMATO_T[0] - 0.3, QUIET, _body, TITLE)
    add(film, 'h4_quiet', QUIET, PRESS, _body, TITLE)
    film.character = DP.dsh_layer(film, film.character, 'ui/pane_h_r6', GG.FOUND, LAND)
    if STORY:
        film.character = DP.dsh_layer(film, film.character, 'ui/pane_h_r6', NOW_AT, END)
    pane = PaneFrames(tl.HERE / 'ui/pane_h_r6', FPS, (P.W, P.H))

    def slide_fn(c):
        t = c.t
        img = film.background(t)
        d = ImageDraw.Draw(img)
        fade = SUPPORT * (1 - ease.smooth(ease.prog(t, PRESS, MOVE[0] + 0.3)))
        if fade > 0.01:
            hud.frame(d, hud.left_rect(t), TITLE, level=fade)
            hud.tx(d, (36, hud.Y_CMD), CMD, 13, lv(INK, 0.86 * fade))
            draw_left(img, d, t, fade)
        c.state['pane'] = False
        im = pane.image(int(round(t * FPS)))
        if im is not None:
            x, y, x1, y1, _s = H5.pane_rect(t)
            d.rectangle((x - 1, y - 1, x1 + 1, y1 + 1), outline=INK, width=2)
            sm = im.resize((max(1, int(round(x1 - x))), max(1, int(round(y1 - y)))), Image.LANCZOS)
            base = img.convert('RGBA')
            base.alpha_composite(sm, (int(round(x)), int(round(y))))
            img.paste(base.convert('RGB'))
        c.img.paste(img)
    chap = STAGE.split(' ', 1)[1]
    film.add('h5_slide', PRESS, LAND, slide_fn, chapter=chap)
    base_levels = film.levels
    s_lv = P.setting('support_level', 0.42)

    def levels(t):
        lv_ = base_levels(t)
        if PRESS <= t < LAND or t >= NOW_AT:
            return {k: 1.0 for k in lv_}
        if RIGHT_BACK[0] <= t < PRESS and 'right' in lv_:
            up = s_lv + (1 - s_lv) * ease.smooth(ease.prog(t, *RIGHT_BACK))
            lv_ = dict(lv_)
            lv_['right'] = max(lv_['right'], up)
        return lv_
    film.levels = levels

    def last_fn(c):
        c.img.paste(H5.zoomed(last_frame(c.t), c.t))
        c.black = True
    film.add('h5_last', LAND, NOW_AT, last_fn, chapter=chap)
    if STORY:

        def now_fn(c):
            _now(film, c)
        film.add('h6_now', NOW_AT, END, now_fn, chapter=chap)
    for t0, side in [(T0, 'both'), (REVEAL, 'left'), (QUIET, 'right')] + ([(NOW_AT, 'both')] if STORY else []):
        film.set_lead(t0, side)
    from groups.f import dissolve
    dissolve(film, 'h1_check', 0.4)
    film.finish.append(_finish)
    ch = film.chrome
    status0, chapter0 = (ch.status, ch.chapter)

    def status(t, ctx=None):
        s = list(status0(t, ctx))
        if t >= T0 and s:
            s[0] = (STAGE, s[0][1])
        return s

    def chapter(t, ctx=None):
        return chap if t >= T0 else chapter0(t, ctx)
    ch.status, ch.chapter = (status, chapter)
    if STORY:
        header0 = ch.header

        def header(img, t, ctx):
            header0(img, t, ctx)
            if t >= NOW_AT:
                _hold_counter(ch, img, t, ctx)
        ch.header = header
