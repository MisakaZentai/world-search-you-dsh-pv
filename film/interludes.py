"""r5 batch 2 (REVISE_R4_20261004.md §3.1, §3.4, §3.15; DECISIONS D34, round 2 D35): the three "I'm searching"
interludes as one motif, going into a machine. Switch DSH_I=r5; install(film) is called by film.py after every group
has registered.

The grammar, the same three times: "I'm searching" -> the forward pane opens into the machine's body (tmux zoom) ->
her blue goes in, a group of layers an event -> it comes back out on the downbeat before the next sung line. Times:
inside/i5_times.py (all from beatmap.py).

Round 2 (D35, sample_r5/README.md §4): a step no longer stops dead (R-A). Every big move (her band's front, the
tower's climb, the camera, the ring, the way out) eases IN and lands exactly on its event, on a node: a group of
layers, a block, an arc's foot (beatmap.arrive). Once there the node keeps moving at the rate of the harmony
(i5_times.phase): her blue runs along the band's lines through the node's layers, its layers are read one after
another, a bead runs up the arc just landed, the radar's sweep goes round. A downbeat lights only the node the picture
stands on, by the beat's weight (i5_times.node_flash); nothing lights the whole machine. No slab, no inverse (R-B).
Boxes and labels keep 3 px clear of text (R-C).

  interlude 1  up into one   (70.10-82.13, group B) the content stays (REPL + radar, dsh's menu, Qwen's tower):
               the samples land 8 a stab, the ring lands on the downbeat and three stabs, `exact hits 0` on bar 42's
               downbeat (73.53, ink, no slab) and held a beat; a sweep goes round the radar at the rate of the
               harmony; the tower (inside/i5_tower.py) lands on the stabs, 16ths in the last bar, the slot on 82.13.
  interlude 2  six across     (137.31-151.55, group D) each press of ↻ opens this stand-in's body (inside/i5_body.py;
               the three unpublished ones sealed); her band lands on a group of its layers on each kick after the press;
               the pile of 好呀 is the output column under the body, the newest on top (the press pushes the older
               ones down). 151.12 (you stop) the pane closes; 151.55 d_r5's.
  interlude 3  in and out     (260.88-273.39, group G) r5e (D40): the forward pane opens straight onto the 4:00
               arcs plate (inside/i5_arcs.py) and the frame breaks out with it; the first character's 40 layers
               climb in the plate's lens column on four stabs (the body shot of r5-r5d is gone: it was cut half
               way), then a character a stab; on bar 155 (<eos>) the way out: the view shrinks back into the forward pane in one continuous
               move that leans into each stab, while the session list and dsh (ui/pages/i5_g.py) archive one session
               a stab, hers (archived, grey) left; 273.39 FOUND is group H's. The city is gone.

How it is laid over the groups (no group module is changed): shot.fn is wrapped (interlude 1 patches group B's ring
times, its radar and its REPL for the length of the call), the tower's plate source is swapped, film.levels and
film.character are wrapped, one D2 break-out is registered for the arcs (groups.base.full_frame).
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import math
from PIL import Image, ImageDraw
import beatmap as BM
import cast
import hud
import panes
import speed
import tl
from hud import BG, HER_LIVE, HER_QUIET, INK, lv
from panes import FAINT, SUB, TXT
from tuikit import ease, glyph
P = tl.p
COL, TOP, BOT = (110, 88, 598)
STRIP_Y0 = 536
TRAVEL2 = 0.25

class _Patch:
    """Set module attributes for the length of a call, then put them back."""

    def __init__(self, pairs):
        self.pairs = pairs

    def __enter__(self):
        self.old = [(m, n, getattr(m, n)) for m, n, _v in self.pairs]
        for m, n, v in self.pairs:
            setattr(m, n, v)

    def __exit__(self, *exc):
        for m, n, v in self.old:
            setattr(m, n, v)
        return False

def _wrap(film, t0, t1, around):
    """Every shot overlapping [t0, t1): around(c, call) instead of the shot's fn while c.t is in the span. A shot
    that ends up to 0.6 s before t0 is wrapped too: a dissolve out of it renders it past its end (groups/f.py)."""
    for shot in film.shots:
        if shot.start < t1 and t0 < shot.end + 0.6:
            orig = shot.fn

            def fn(c, _orig=orig, **kw):
                if t0 <= c.t < t1:
                    around(c, lambda: _orig(c, **kw))
                else:
                    _orig(c, **kw)
            shot.fn = fn

def _right(t):
    return hud.left_rect(t)[2] - 8

def _paste_view(img, view, rect, alpha=1.0):
    """The view (drawn from the pane's top-left, full size) into the pane, clipped to its inside."""
    x0, y0, x1, y1 = (int(round(v)) for v in rect)
    box = (x0 + 1, y0 + 2, x1, y1)
    w, h = (box[2] - box[0], box[3] - box[1])
    if w <= 0 or h <= 0:
        return
    part = view.crop((1, 2, 1 + w, 2 + h))
    if alpha < 0.999:
        part = Image.blend(img.crop(box), part, max(0.0, alpha))
    img.paste(part, box[:2])
t_now: list = []

def _chip_w(t):
    """Width of the command line's model chip on the panes' right edge (groups/c_pane.py `_cmdline`)."""
    chip = cast.term(tl.model(t))
    return P.font(13, 'bold').getlength(chip) + 12 if chip else 0

def _clear_labels(d, rect, k):
    """The zoomed pane covers the panes above it: their labels and status on its top border go too."""
    if k < 0.5:
        return
    x0, y0, x1, _y1 = rect
    d.rectangle((x0 + 2, y0 - 4, x1 - 2, y0 + 1), fill=BG)
    if y0 <= TOP + 1:
        d.rectangle((x0 + 2, y0 - 7, x1 - 2 - _chip_w(t_now[0] if t_now else 0.0) - 2, y0 - 4), fill=BG)

def _box(d, rect, label, t, run=0.0, level=1.0, status='', status_her=False, label_level=1.0):
    """panes.box, except that when the pane's top border runs under the command line's model chip (a pane at TOP
    reaching the chip) its spinner and status go left of the chip, 8 px clear (R-C: panes.box put them under it).
    Also laid over panes.box itself while group B's panes are drawn in interlude 1 (_i1_patch)."""
    if level <= 0.01:
        return
    x0, y0, x1, y1 = (round(v) for v in rect)
    line = lv(INK, (panes.LINE_IDLE + (panes.LINE_RUN - panes.LINE_IDLE) * run) * level)
    d.rectangle((x0, y0, x1, y1), outline=line)
    f = P.font(panes.SIZE['label'], 'bold' if run > 0.5 else 'mono')
    tw = d.textlength(label, font=f)
    if label_level > 0.01:
        d.rectangle((x0 + 7, y0 - 1, x0 + 15 + tw, y0 + 1), fill=BG)
        d.text((x0 + 11, y0 - 7), label, font=f, fill=lv(INK, (0.55 + 0.45 * run) * level * label_level))
    if label_level < 0.99:
        return
    right = x1 - 8
    chip_x0 = _right(t) - _chip_w(t)
    if y0 <= TOP + 12 and right > chip_x0 - 8:
        right = chip_x0 - 8
    if run > 0.01:
        d.rectangle((right - 12, y0 - 1, right + 3, y0 + 1), fill=BG)
        panes.spinner(d, right - 9, y0 - 4, t, lv(INK, run * level))
        right -= 16
    if status:
        sw = hud.width(status, 11)
        d.rectangle((right - sw - 5, y0 - 1, right + 1, y0 + 1), fill=BG)
        hud.tx(d, (right - sw - 2, y0 - 7), status, 11, lv(hud.HER_QUIET if status_her else INK, SUB * level))

def _arrow(d, pts, colr):
    d.line(pts, fill=colr)
    (xa, ya), (xb, yb) = (pts[-2], pts[-1])
    ang = math.atan2(yb - ya, xb - xa)
    for s in (-1, 1):
        d.line([(xb, yb), (xb - 6 * math.cos(ang + s * 0.5), yb - 6 * math.sin(ang + s * 0.5))], fill=colr)
SWEEP_REV = 0.45

def _radar_i5(d, t, c):
    """groups/b_lead.py `_radar`, re-timed (R-A): the samples fly out and land on their stab (I5.PTS; the first eight
    with the cut), the ring eases in and lands on each of I5.RINGS, her mark lights on the downbeats; between the
    landings a sweep goes round at the rate of the harmony (i5_times.phase), the samples it passes ticked. The
    title counts the samples landed. Lines one dot wide."""
    from groups import b as GB
    from groups import b_open as BO
    from inside import i5_times as I5
    if t < I5.NEAR_OUT or t >= I5.SWITCH:
        return
    a = ease.prog(t, I5.NEAR_OUT, I5.NEAR_OUT + 0.1)
    wide = hud.full_u(t)
    w, h = (c[2] - c[0], c[3] - c[1])
    R = max(40.0, min((h - 100) / 2, (w - 60 - 230 * wide) / 2))
    cx, cy = (c[0] + 30 + R, c[1] + 50 + R)
    radii = [R * 1.12] + [BO._rad(th, R) for th in BO.B9_TH]
    ar = BM.arrive(t, I5.RINGS, 0.22)
    k = int(math.floor(ar + 1e-09))
    r_ring = radii[-1] if k >= len(I5.RINGS) else ease.lerp(radii[k], radii[k + 1], ar - k)
    her_c = glyph.mix(HER_QUIET, HER_LIVE, BM.flash(t, I5.DOWN1, half=0.14))
    ang_s = -math.pi / 2 + 2 * math.pi * SWEEP_REV * I5.phase(t, 1)
    lab = '她 · 0074'
    lab_xy = (cx - 18, cy + 16)
    lab_w = BO.mw(lab, 13)
    lab_patch = (lab_xy[0] - 3, lab_xy[1] - 1, lab_xy[0] + lab_w + 3, lab_xy[1] + 19)
    lab_box = (lab_patch[0] - 3, lab_patch[1] - 3, lab_patch[2] + 3, lab_patch[3] + 3)
    r_end = R * 1.04
    pts = []
    for i in range(0, int(r_end) + 1, 2):
        x, y = (cx + i * math.cos(ang_s), cy + i * math.sin(ang_s))
        clear = i >= 16 and (not (lab_box[0] <= x <= lab_box[2] and lab_box[1] <= y <= lab_box[3]))
        if clear:
            pts.append((x, y))
        elif len(pts) > 1:
            d.line(pts, fill=lv(INK, 0.32 * a))
            pts = []
        else:
            pts = []
    if len(pts) > 1:
        d.line(pts, fill=lv(INK, 0.32 * a))
    hud.pix(d, ['..#..', '.###.', '#####', '.###.', '..#..'], cx - 10, cy - 10, 4, {'#': lv(her_c, a)})
    landed = 0
    for pos, j in enumerate(BO._ORDER):
        at = BO.B9_SPAWN[pos]
        go = at - 0.14 if pos >= 8 else at - 0.0
        if t < go:
            continue
        g = ease.smooth(ease.prog(t, go, at)) if pos >= 8 else ease.ease_out(ease.prog(t, go, go + 0.12))
        if t >= at:
            landed += 1
        s = BO.B9_SIMS[j]
        rp = BO._rad(s, R)
        ang = BO.B9_ANG[j]
        px, py = (cx + rp * g * math.cos(ang), cy + rp * g * math.sin(ang))
        vis = ease.lerp(0.22, 1.0, ease.clamp((r_ring - rp) / 8 + 0.5))
        d.ellipse((px - 4, py - 4, px + 4, py + 4), fill=lv(INK, vis * a))
        dang = (ang_s - ang) % (2 * math.pi)
        if g >= 1 and dang < 0.5 and (rp < r_end):
            d.ellipse((px - 7, py - 7, px + 7, py + 7), outline=lv(INK, 0.45 * a * (1 - dang / 0.5)))
        if j in BO.B9_LABEL and wide > 0.05:
            ly = cy - 70 + 46 * j
            lx = cx + R + 18
            la = vis * a * wide * ease.prog(t, at + 0.02, at + 0.16)
            room = c[2] - 3 - (lx + BO.mw(f'{s:.2f}  ' + BO.B9_LABEL[j], 13) + 16)
            if room <= 0:
                continue
            la *= ease.clamp(room / 30)
            d.line([(px + 5, py), (lx - 30, ly + 9), (lx - 6, ly + 9)], fill=lv(INK, 0.5 * la))
            ww = BO.mtx(d, (lx, ly), f'{s:.2f}  ' + BO.B9_LABEL[j], 13, lv(INK, la))
            GB.eggplant(d, lx + ww + 4, ly + 1, 2, 0.0, la)
    if r_ring > 2:
        d.ellipse((cx - r_ring, cy - r_ring, cx + r_ring, cy + r_ring), outline=lv(INK, 0.9 * a), width=1)
    d.rectangle(lab_patch, fill=BG)
    BO.mtx(d, lab_xy, lab, 13, lv(her_c, a))
    lab = f'cos ≥ {BO.B9_TH[k - 1]:.2f}' if k >= 1 else f'n = {landed}'
    BO.mtx(d, (cx - BO.mw(lab, 18, True) / 2, c[1] + 14), lab, 18, lv(INK, a), bold=True)

def _repl_i5(d, t, r):
    """groups/b_lead.py `_repl` with the counts landing with the ring (RING_AT is patched to I5.RINGS) and
    `exact hits 0` in ink, dropped in on its downbeat with a one-dot rule growing under it: no slab (R-B)."""
    from groups import b_lead as BL
    from groups import b_open as BO
    if t < BL.NEAR_OUT or t >= BL.SWITCH:
        return
    a = ease.prog(t, BL.NEAR_OUT, BL.NEAR_OUT + 0.3)
    wide = hud.full_u(t)
    x0, y0 = (r[0] + 10, r[1] + 12)
    yc = ease.lerp(r[1] + 14, y0 + 76, wide)
    if wide > 0.01:
        for i, (at, line) in enumerate(BO.B9_CODE):
            if t < at:
                break
            if y0 + i * 20 + 17 > yc - 3:
                break
            s = line[:int((t - at) * 90) + 1]
            room = r[2] - 6 - x0
            if BL.mw(s, 13, i == 0) > room:
                while s and BL.mw(s + '…', 13, i == 0) > room:
                    s = s[:-1]
                s += '…'
            BL.mtx(d, (x0, y0 + i * 20), s, 13, lv(INK, (TXT if i == 0 else SUB) * a * wide), bold=i == 0)
    for i, at in enumerate(BL.RING_AT):
        if t < at:
            break
        u = ease.prog(t, at, at + 0.1) * a
        y = yc + i * 32
        th = BO.B9_TH[i]
        hud.tx(d, (x0, y + 4), f'{th:.2f}', 20, lv(INK, SUB * u))
        hud.tx(d, (x0 + 90, y), f'{BO._b9_count(th):2d}', 26, lv(INK, u), True)
        hud.tx(d, (x0 + 128, y + 6), '/ 24', 16, lv(INK, SUB * u))
    at = BL.RING_AT[-1]
    if t >= at:
        e = ease.ease_out(ease.prog(t, at, at + 0.14))
        sy = yc + 5 * 32 + 14
        size = 26
        w = hud.width('exact hits 0', size, True)
        hud.tx(d, (x0, sy + 5 - 10 * (1 - e)), 'exact hits 0', size, lv(INK, a * ease.prog(t, at, at + 0.05)), True)
        u = ease.ease_out(ease.prog(t, at + 0.04, at + 0.3))
        d.line([(x0, sy + 40), (x0 + w * u, sy + 40)], fill=lv(INK, 0.8 * a))

def _i1_patch():
    from groups import b_lead as BL
    from groups import b_open as BO
    from inside import i5_times as I5
    r_last = BL.RING_AT[-1]
    lead_ = []
    for t0, name in BL.LEAD:
        if abs(t0 - r_last) < 1e-06 and name == 'trace':
            continue
        if abs(t0 - I5.NEAR_BACK) < 1e-06 and name == 'dsh':
            lead_ += [(I5.NEAR_BACK, 'trace'), (I5.I1_DSH, 'dsh')]
            continue
        lead_.append((t0, name))
    run = dict(BL.RUN)
    run['trace'] = [s for s in BL.RUN['trace'] if abs(s[0] - I5.NEAR_OUT) > 1e-06] + [(I5.NEAR_OUT, I5.NEAR_BACK + 0.15)]
    run['compare'] = [s for s in BL.RUN['compare'] if abs(s[0] - I5.NEAR_OUT - 0.1) > 1e-06] + [(I5.NEAR_OUT + 0.1, I5.NEAR_BACK + 0.1)]
    spawn = [I5.PTS[0] + 0.12 + 0.008 * k for k in range(8)]
    spawn += [I5.PTS[k // 8] - 0.007 * (7 - k % 8) for k in range(8, len(BO.B9_SIMS))]
    code = [(I5.NEAR_OUT, BO.B9_CODE[0][1]), (I5.PTS[1], BO.B9_CODE[1][1]), (I5.PTS[2], BO.B9_CODE[2][1])]
    return _Patch([(BL, 'RING_AT', list(I5.RINGS)), (BL, 'LEAD', lead_), (BL, 'RUN', run), (BL, '_radar', _radar_i5), (BL, '_repl', _repl_i5), (panes, 'box', _box), (BO, 'B9_SPAWN', spawn), (BO, 'B9_STEPS', [I5.NEAR_OUT] + list(I5.RINGS)), (BO, 'B9_CODE', code)])
SEARCH_RATE = 10.0

def _i1_search(c):
    """68.15-70.10, the bar of "I'm searching" before the radar (group B's picture, the window leading): her eight
    files in the mem column are read one after another, a wave running down them at the rate of the harmony (each lit
    her blue while it is read, D1), so the left never stands still while the chords go on (R-A). Fades out over the
    radar's first 0.3 s."""
    from groups import b_lead as BL
    from groups import c_pane as CPN
    from inside import i5_times as I5
    t = c.t
    t0 = BM.WIN['interlude1'][0]
    amp = ease.smooth(ease.prog(t, t0, t0 + 0.25)) * (1 - ease.smooth(ease.prog(t, I5.NEAR_OUT, I5.NEAR_OUT + 0.3)))
    if amp <= 0.01 or not hasattr(BL, 'MEM'):
        return
    nf = len(tl.HER_FILES)
    pos = (I5.phase(t, 1) - I5.phase(t0, 1)) * SEARCH_RATE % nf
    d = ImageDraw.Draw(c.img)
    f11 = P.font(11)
    with CPN._strip_in(BL.MEM):
        for k, name in enumerate(tl.HER_FILES):
            dk = abs(pos - k)
            v = amp * max(0.0, 1 - min(dk, nf - dk) / 0.8)
            if v <= 0.02:
                continue
            bx0, by0, bx1, by1 = hud.block_rect(k, t)
            d.rectangle((bx0, by0, bx1, by1), fill=glyph.mix(HER_QUIET, HER_LIVE, v))
            if by1 - by0 > 14:
                d.text((bx0 + 4, by0 + 6), hud.chip(d, name, bx1 - bx0, f11), font=f11, fill=BG)

def _install_i1(film):
    from inside import i5_times as I5
    from inside import i5_tower as TW
    patch = _i1_patch()

    def around(c, call):
        with patch:
            call()
    _wrap(film, I5.NEAR_OUT, I5.SWITCH, around)

    def around0(c, call):
        call()
        _i1_search(c)
    _wrap(film, BM.WIN['interlude1'][0], I5.NEAR_OUT + 0.3, around0)
    sp = next((s for s in getattr(film, 'inside_spans', ()) if s.name == 'b9_tower'), None)
    if sp is not None:
        sp.path = TW.path
        sp.make = TW.TowerI5
        sp._r = None
    base = film.levels

    def levels(t):
        """The window takes the lead a beat later (73.96): the slab is the left's for that beat."""
        lv_ = base(t)
        if I5.NEAR_BACK <= t < I5.I1_DSH + 0.5:
            lv_ = dict(lv_)
            k = ease.smooth(ease.prog(t, I5.I1_DSH, I5.I1_DSH + 0.5))
            lv_['left'] = ease.lerp(1.0, lv_.get('left', 1.0), k)
        return lv_
    film.levels = levels

def _i2_lands(T):
    """The kicks after this stand-in's press: her band lands on one group of its layers on each (the press itself
    is the body's entrance)."""
    from inside import i5_times as I5
    ks = I5.turn_kicks(T)
    return ks[1:] if len(ks) > 1 else ks

def _i2_fill(T, t):
    """(fill, l0, l1, live_k) of stand-in T's body at t: the front eases in and lands on a group a kick (arrive);
    [l0, l1) is the group it stands on, live_k its light (the kick's weight, accent tiers)."""
    from inside import i5_times as I5
    lands = _i2_lands(T)
    n = _body(T.key).n
    G = max(1, len(lands))
    if t >= T.t1 or not lands:
        return (float(n), n * (G - 1) / G, float(n), 0.0)
    a = BM.arrive(t, lands, TRAVEL2)
    kk = int(math.floor(a + 1e-09))
    if kk == 0:
        return (n * a / G, 0.0, 0.0, 0.0)
    return (n * a / G, n * (kk - 1) / G, n * kk / G, I5.node_flash(t, lands[:kk]))

def _i2_tabs(d, t, x, y, cur, wmax):
    from inside import i5_times as I5
    names = [cast.term(T.key) for T in I5.TURNS]
    for size, gap in ((12, 16), (11, 16), (11, 12), (11, 10), (10, 10), (9, 10)):
        if sum((hud.width(s, size, True) + 12 + gap for s in names)) <= wmax:
            break
    for i, (T, s) in enumerate(zip(I5.TURNS, names)):
        done, now = (i < cur, i == cur)
        if done:
            d.rectangle((x, y + 4, x + 7, y + 11), fill=HER_QUIET)
        else:
            d.rectangle((x, y + 4, x + 7, y + 11), outline=lv(INK, TXT if now else FAINT))
        if now:
            fill, *_r = _i2_fill(T, t)
            n = max(1, _body(T.key).n)
            hh = int(round(7 * min(1.0, fill / n)))
            if hh > 0:
                d.rectangle((x, y + 11 - hh, x + 7, y + 11), fill=HER_QUIET)
        f = P.font(size, 'bold' if now else 'mono')
        d.text((x + 12, y + 1), s, font=f, fill=lv(INK, TXT if now else SUB if done else FAINT))
        x += 12 + d.textlength(s, font=f) + gap
_BODIES = {}

def _body(key, enc_dec=None):
    from inside.i5_body import Body
    if (key, enc_dec) not in _BODIES:
        _BODIES[key, enc_dec] = Body(key, enc_dec)
    return _BODIES[key, enc_dec]

def _i2_press(d, t, xr, y):
    """↻ ×n at the right of the header (groups/d_lead.py `_press`, in the zoomed pane)."""
    from groups import d as GD
    from groups import d_lead as DL
    from inside import i5_times as I5
    n = sum((1 for a in I5.ROT_AT if a <= t))
    if n == 0:
        return
    at = I5.ROT_AT[n - 1]
    f = P.font(DL.PRESS_PX, 'bold')
    s = f'×{n}'
    w = d.textlength(s, font=f)
    x = xr - w
    d.text((x, y + GD.drop(t, at, -8, 0.14)), s, font=f, fill=lv(INK, TXT))
    rot = 360 * ease.ease_out(ease.prog(t, at, at + 0.3))
    DL._regen_icon(d, x - 8 - DL.ICON_R, y + DL.PRESS_PX * 0.55, DL.ICON_R, rot, lv(INK, TXT))
PILE_P = 30
BODY_Y = (76, 290)
PILE_Y = BODY_Y[1] + 26

def _pile_row_y(t, T):
    """Row T's top: the newest right under the body, each press pushing the older ones down a row (the push lands on
    the press)."""
    from inside import i5_times as I5
    pushed = BM.arrive(t, I5.ROT_AT, 0.22)
    return PILE_Y + (pushed - 1 - T.i) * PILE_P

def _i2_pile(d, t, x0):
    """The output column: d_lead's pile of 好呀 (a row a press, the newest in full ink on top, the ones under it
    faint), laid right under the body (r5 round 2: under it, not at the pane's foot, so nothing is left empty)."""
    from groups import d as GD
    from groups import d_lead as DL
    from inside import i5_times as I5
    nx = x0 + DL.ANS_W + DL.NAME_GAP
    for T in I5.TURNS:
        if t < T.t0:
            break
        y = _pile_row_y(t, T)
        u = DL._row_u(t, T)
        if t < T.ans:
            s = cast.term(T.key)
            n = int((t - T.t0) * DL.NAME_CPS) + 1
            BMx(d, (nx, y + 14), s[:n], DL.NAME_PX, lv(INK, SUB))
            d.rectangle((x0, y + 7, x0 + 3, y + 33), fill=lv(INK, SUB))
            continue
        a = ease.lerp(TXT, FAINT, u)
        BMx(d, (nx, y + 14), cast.term(T.key), DL.NAME_PX, lv(INK, SUB if a > SUB else a))
        lit = GD.lit(t, T.ans, T.write)
        x, yy = (x0, y + GD.drop(t, T.ans, -8, 0.14))
        a_her, a_self = (ease.lerp(TXT, DL.PILE_OLD[0], u), ease.lerp(TXT, DL.PILE_OLD[1], u))
        for tk in DL.PH.toks:
            colr = lv(INK, a_self) if tk.src == 'self' else hud.her(lit, a_her)
            x += hud.tx(d, (x, yy), tk.text, DL.PILE_PX, colr, bold=True)

def BMx(d, xy, s, size, fill, bold=False):
    from groups import b_open as BO
    return BO.mtx(d, xy, s, size, fill, bold)

def _i2_view(t, Wv, Hv, uu=1.0):
    """The zoomed forward pane, drawn from its top-left: header (its structure, ↻ ×n), the six as tabs, the body
    (the current one sliding in over the last on a press; inside the node it stands on, her blue keeps moving), the
    output column under it."""
    from groups import d as GD
    from groups import d_lead as DL
    from inside import i5_times as I5
    V = Image.new('RGB', (int(Wv), int(Hv)), BG)
    d = ImageDraw.Draw(V)
    T = GD.turn_at(t)
    body = _body(T.key)
    head = BO_left(T.key)
    if uu > 0.5:
        BMx(d, (14, 12), head, 13, lv(INK, SUB))
    else:
        BMx(d, (10, 10), head, 11, lv(INK, 0.72))
    big = uu > 0.5
    if big:
        _i2_press(d, t, Wv - 16, 8)
        _i2_tabs(d, t, 14, 40, T.i, Wv - 28)
    by0, by1 = (ease.lerp(28, BODY_Y[0], uu), ease.lerp(50, BODY_Y[1], uu))
    e = ease.ease_out(ease.prog(t, T.t0, T.t0 + 0.16)) if T.i > 0 else 1.0
    if e < 1 and T.i > 0:
        prev = I5.TURNS[T.i - 1]
        dx = -e * Wv
        _body(prev.key).draw(d, (14 + dx, by0, Wv - 14 + dx, by1), t, fill=_body(prev.key).n, flash=0.0, band_in=1.0, x_in=dx, labels=big)
    dx = (1 - e) * Wv
    fill, l0, l1, lk = _i2_fill(T, t)
    band_in = ease.ease_out(ease.prog(t, T.t0, T.t0 + 0.12))
    rect_b = (14 + dx, by0, Wv - 14 + dx, by1)
    body.draw(d, rect_b, t, fill=fill, live0=l0, live1=l1, live_k=lk, flash=0.0, band_in=band_in, x_in=dx, labels=big)
    if l1 > l0 and dx < 0.5:
        body.inner(d, rect_b, l0, l1, I5.phase(t, 2), labels=big)
    if uu > 0.995:
        _i2_pile(d, t, 14)
    if uu > 0.995 and T.ans <= t < T.write + 0.3:
        from groups import b_open as BO
        a = 1 - ease.prog(t, T.write, T.write + 0.3)
        k = ease.ease_out(ease.prog(t, T.ans - 0.1, T.ans))
        x1 = Wv - 14
        yr = _pile_row_y(t, T) + 20
        xe = 14 + DL.ANS_W + DL.NAME_GAP + BO.mw(cast.term(T.key), DL.NAME_PX) + 10
        y_out = by1 - 8
        xs = x1 + 6
        pts = [(x1, y_out), (xs, y_out), (xs, ease.lerp(y_out, yr, min(1.0, k / 0.6)))]
        if k >= 0.6:
            pts.append((ease.lerp(xs, xe, ease.prog(k, 0.6, 1.0)), yr))
        if len(pts) >= 3 and (k >= 0.6 or pts[-1][1] > y_out + 2):
            _arrow(d, pts, lv(INK, 0.75 * a))
    return V

def BO_left(key):
    from inside.i5_body import UNKNOWN
    from groups import b_open as BO
    if key in UNKNOWN:
        return f'{cast.term(key)} · 结构未公开'
    return BO.ARCH[key]['left']

def _i2_draw(c):
    from groups import d as GD
    from inside import i5_times as I5
    t = c.t
    u = ease.ease_out(ease.prog(t, I5.I2_IN, I5.I2_IN + 0.18)) * (1 - ease.ease_io(ease.prog(t, I5.I2_BACK, I5.I2_BACK + I5.I2_SHUT)))
    alpha = 1.0 if t < I5.I2_END else 0.0
    if alpha <= 0.002:
        return
    r = _right(t)
    y0 = ease.lerp(STRIP_Y0, TOP, u)
    rect = (COL, y0, r, BOT)
    V = _i2_view(t, r - COL, BOT - TOP, ease.smooth(u))
    _paste_view(c.img, V, rect, alpha)
    d = ImageDraw.Draw(c.img)
    t_now[:] = [t]
    _clear_labels(d, rect, u * alpha)
    T = GD.turn_at(t)
    _box(d, rect, 'forward', t, 1.0 if t < I5.I2_BACK else 1 - ease.prog(t, I5.I2_BACK, I5.I2_BACK + 0.2), alpha, speed.label(T.key), label_level=1.0 if u > 0.995 or u < 0.005 else 0.0)

def _install_i2(film):
    from inside import i5_times as I5

    def around(c, call):
        call()
        _i2_draw(c)
    _wrap(film, I5.I2_IN, I5.I2_END, around)
_ARCS_SPAN = []

def _arcs_span():
    if not _ARCS_SPAN:
        from inside import i5_arcs as AR5
        from inside import i5_times as I5
        from inside.install import Span
        sp = Span('i5_arcs', I5.G5, I5.TURN_BAR, AR5.ArcsI5, fade_in=0.04, fade_out=0.0, register=False)
        sp.path = AR5.path
        _ARCS_SPAN.append(sp)
    return _ARCS_SPAN[0]

def _arcs_image(t):
    """The plate at t (its cached frame; held after <eos>), RGB on paper."""
    from inside import i5_arcs as AR5
    n = AR5.frame_n(t)
    sp = _arcs_span()
    return Image.fromarray(sp.plate(n))

def _session_ids():
    from groups import g as GG
    return dict(GG.SESSION_LABEL)
SESSION_ID = _session_ids()

def _i3_sessions(d, t, c, cover=None):
    """compare: the sessions wearing her persona, one archived on each stab (dsh does the same on the right);
    hers, archived long ago, at the bottom. Rows are kept (R4): an archived one is struck, faint. A row under the
    shrinking view (cover, 3 px around it) waits whole until the view has left it (R-C: no row cut by its edge)."""
    from inside import i5_times as I5
    x0, y0, x1, _y1 = c

    def hidden(y):
        if cover is None:
            return False
        rx0, ry0, rx1, ry1 = (x0 + 10, y - 3, x0 + 600, y + 21)
        return not (rx1 < cover[0] or rx0 > cover[2] or ry1 < cover[1] or (ry0 > cover[3]))
    n_open = sum((1 for at in I5.CLOSES if at > t))
    BMx(d, (x0 + 14, y0 + 14), 'persona 大肥鱼', 13, lv(INK, SUB))
    s = f'open {n_open} · archived {len(I5.SESSIONS) - n_open + 1}'
    BMx(d, (x1 - 14 - hud.width(s, 13), y0 + 14), s, 13, lv(INK, SUB))
    pitch = 31
    ya = y0 + 44
    for i, key in enumerate(I5.SESSIONS):
        y = ya + i * pitch
        if hidden(y):
            continue
        at = I5.CLOSES[i]
        k = ease.ease_out(ease.prog(t, at, at + 0.12))
        name = SESSION_ID.get(key, cast.term(key))
        a = ease.lerp(TXT, FAINT, k)
        w = BMx(d, (x0 + 14, y), name, 16, lv(INK, a), bold=k < 0.5)
        BMx(d, (x0 + 330, y + 2), '大肥鱼', 14, lv(INK, ease.lerp(SUB, FAINT, k)))
        st = 'archived' if k >= 0.5 else 'open'
        BMx(d, (x0 + 410, y + 2), st, 14, lv(INK, SUB if k < 0.5 else FAINT), bold=0 < k < 1)
        if k > 0:
            ym = y + 11
            d.line([(x0 + 12, ym), (x0 + 12 + (w + 4) * k, ym)], fill=lv(INK, 0.8))
    y = ya + len(I5.SESSIONS) * pitch + 6
    if hidden(y) or hidden(y - 6):
        return
    d.line([(x0 + 14, y - 6), (x1 - 14, y - 6)], fill=lv(INK, FAINT))
    BMx(d, (x0 + 14, y), cast.term('her'), 16, HER_QUIET)
    BMx(d, (x0 + 330, y + 2), '大肥鱼', 14, lv(HER_QUIET, 0.8))
    BMx(d, (x0 + 410, y + 2), 'archived · 412 行', 14, lv(HER_QUIET, 0.8))

def _i3_archive_log(d, t, c):
    """trace: the archive call of the last stab (the one before it, fainter, above)."""
    from inside import i5_times as I5
    done = [i for i, at in enumerate(I5.CLOSES) if at <= t]
    if not done:
        BMx(d, (c[0] + 10, c[1] + 18), 'sessions.list(persona="大肥鱼")', 14, lv(INK, SUB))
        return
    for pos, i in enumerate(reversed(done[-2:])):
        at = I5.CLOSES[i]
        key = I5.SESSIONS[i]
        y = c[1] + 28 - pos * 19
        a = TXT if pos == 0 else FAINT
        s = f'sessions.archive("{SESSION_ID.get(key, cast.term(key))}")'
        n = int((t - at) * 140) + 1 if pos == 0 else len(s)
        w = BMx(d, (c[0] + 10, y), s[:n], 14, lv(INK, a), bold=pos == 0)
        if pos == 0 and t >= at + 0.1:
            BMx(d, (c[0] + 10 + w + 12, y), f'→ ok · open {len(I5.SESSIONS) - len(done)}', 14, lv(INK, 0.7))

def _exit_m(t):
    """Steps of the way out, continuous (R-A): half a steady pull from the frame's return to the last close, half
    beatmap.arrive over the closes with the whole gap as travel (it leans into each stab and lands on it), so the
    view shrinks all the time and never holds."""
    from inside import i5_times as I5
    n = len(I5.CLOSES)
    t_a = I5.TURN_BAR + I5.I3_BACK
    return 0.5 * n * ease.prog(t, t_a, I5.CLOSES[-1]) + 0.5 * BM.arrive(t, I5.CLOSES, 0.7)

def _i3_exit_box(t, crop=False):
    """The inside view's box on the way out: from the forward pane's inside (full frame; the plate cropped to it,
    so nothing jumps on the bar) to the terminal's width at the bottom (as the frame comes back), then smaller all
    the time into the forward strip's corner. crop=True: also (left, top, right, bottom) of the plate shown."""
    from inside import i5_times as I5
    from inside.plate import PH as PLH, PLATE, PW as PLW
    r0 = hud.LEFT[2] - 8
    s0 = (r0 - COL) / PLW
    q = ((BOT - STRIP_Y0) / (PLH * s0)) ** (1 / len(I5.CLOSES))
    s = s0 * q ** _exit_m(t)
    bw, bh = (PLW * s, PLH * s)
    split = (r0 - bw, BOT - bh, r0, BOT)
    full = (0.0, 0.0, float(PLW), float(PLH))
    u = hud.full_u(t)
    box, cr = (split, full)
    if u > 0:
        inner = (max(PLATE[0], COL + 2), max(PLATE[1], TOP + 3), min(PLATE[2], _right(t) - 1), min(PLATE[3], BOT - 1))
        cr_in = (inner[0] - PLATE[0], inner[1] - PLATE[1], PLW - (PLATE[2] - inner[2]), PLH - (PLATE[3] - inner[3]))
        box = tuple((ease.lerp(a, b, u) for a, b in zip(split, inner)))
        cr = tuple((ease.lerp(a, b, u) for a, b in zip(full, cr_in)))
    return (box, cr) if crop else box

def _i3_draw(c):
    from groups import c_pane as CPN
    from inside import i5_times as I5
    from inside.install import paint
    t = c.t
    img = c.img
    d = ImageDraw.Draw(img)
    t_now[:] = [t]
    if t < I5.TURN_BAR:
        u = ease.ease_out(ease.prog(t, I5.G5, I5.G5 + 0.18))
        r = _right(t)
        rect = (COL, ease.lerp(STRIP_Y0, TOP, u), r, BOT)
        sp = _arcs_span()
        if sp.active(t):
            if u < 0.999:
                _i3_plate_in(c, sp, rect)
            else:
                paint(c.film, c, sp)
        d = ImageDraw.Draw(img)
        _clear_labels(d, rect, u)
        _box(d, rect, 'forward', t, 1.0, 1.0, '云端 · preview', label_level=1.0 if u > 0.995 or u < 0.005 else 0.0)
        return
    r = _right(t)
    tr, cp, fw = ((COL, TOP, r, 140), (COL, 148, r, 528), (COL, STRIP_Y0, r, BOT))
    fade = 1 - ease.prog(t, I5.CLOSES[-1] + 0.15, I5.FOUND - 0.08)
    cover = None
    if fade > 0.002:
        bx0, by0, bx1, by1 = _i3_exit_box(t)
        cover = (bx0 - 3, by0 - 12, bx1 + 3, by1 + 3)
    for name, rect in (('trace', tr), ('compare', cp), ('forward', fw)):
        d.rectangle(rect, fill=BG)
        with panes.Clip(img, rect) as dd:
            if name == 'trace':
                _i3_archive_log(dd, t, rect)
            elif name == 'compare':
                _i3_sessions(dd, t, rect, cover)
            elif fade < 0.999:
                CPN._stack(dd, t, rect, 'merged', 1 - fade, None, 0.0, segs=())
        run = panes.run_k(t, [(at, at + 0.12) for at in I5.CLOSES]) if name != 'forward' else 0.0
        _box(d, rect, name, t, run, 1.0, '云端 · preview' if name == 'forward' else '')
    if fade <= 0.002:
        return
    (bx0, by0, bx1, by1), cr = _i3_exit_box(t, crop=True)
    w, h = (int(round(bx1 - bx0)), int(round(by1 - by0)))
    if w < 4 or h < 4:
        return
    pl = _arcs_image(t).resize((w, h), Image.LANCZOS, box=cr)
    box = (int(round(bx0)), int(round(by0)))
    if fade < 0.999:
        pl = Image.blend(img.crop((box[0], box[1], box[0] + w, box[1] + h)), pl, fade)
    img.paste(pl, box)
    d = ImageDraw.Draw(img)
    still = hud.full_u(t) <= 0.0 and 148 + 16 < box[1] < 528 - 16
    if h > 40:
        _box(d, (box[0], box[1], box[0] + w - 1, box[1] + h - 1), 'forward', t, 0.0, fade, '', label_level=1.0 if still else 0.0)
    else:
        d.rectangle((box[0], box[1], box[0] + w - 1, box[1] + h - 1), outline=lv(INK, 0.85 * fade))

def _i3_plate_in(c, sp, rect):
    """r5e (D40 ②): while the forward pane opens, the plate as install.paint lays it (ink multiplied into the paper)
    on the pane's own paper, clipped to the pane: its top edge rises from the strip, its right edge is the dsh
    window's as it slides off."""
    import numpy as np
    from inside.install import _PAPER
    t = c.t
    a = sp.alpha(t)
    x0, y0, x1, y1 = (int(round(v)) for v in rect)
    if a <= 0.002 or x1 - x0 < 4 or y1 - y0 < 4:
        return
    bgimg = c.film.background(t)
    c.img.paste(bgimg.crop((x0, y0, x1, y1)), (x0, y0))
    X0, Y0, X1, Y1 = sp.rect
    right = min(X1, hud.left_rect(t)[2] - 8)
    plate = sp.plate(c.n).astype(np.float32)
    bg = np.asarray(bgimg.crop(sp.rect), np.float32)
    comp = bg * (plate / _PAPER)
    cur = np.asarray(c.img.crop(sp.rect).convert('RGB'), np.float32)
    mx = np.clip((right - (X0 + np.arange(X1 - X0) + 0.5)) / 6.0, 0.0, 1.0)
    my = (Y0 + np.arange(Y1 - Y0) > y0).astype(np.float32)
    m = (my[:, None] * mx[None, :] * a)[:, :, None]
    out = cur * (1 - m) + comp * m
    c.img.paste(Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8)), (X0, Y0))

def _install_i3(film):
    from groups import d_pane as DP
    from groups.base import full_frame
    from inside import i5_times as I5
    for sp in getattr(film, 'inside_spans', ()):
        if sp.name == 'g5_city':
            sp.active = lambda t: False
    full_frame(I5.G5, I5.TURN_BAR, 0.3, I5.I3_BACK)
    first = next((sh for sh in film.shots if sh.start <= I5.G5 < sh.end), None)
    cut = film.cuts.get(first.name) if first is not None else None
    if cut is not None and getattr(cut, 'post', 0) > 0.12:
        film.cuts[first.name] = type(cut.__name__ + '_i5', (cut,), {'post': 0.12})
        film._cut_objs = None

    def around(c, call):
        call()
        _i3_draw(c)
    _wrap(film, I5.G5, I5.FOUND, around)
    film.character = DP.dsh_layer(film, film.character, 'ui/pane_i5_g', I5.G5, I5.FOUND)
    base = film.levels

    def levels(t):
        """On the way out both sides lead (the window archives as the list does); from FOUND H's lead fades in
        from that, so the window does not dip."""
        lv_ = base(t)
        if I5.TURN_BAR <= t < I5.FOUND + 0.5:
            lv_ = dict(lv_)
            k = 1.0 if t >= I5.FOUND else ease.smooth(ease.prog(t, I5.TURN_BAR, I5.TURN_BAR + 0.4))
            lv_['right'] = max(lv_.get('right', 1.0), ease.lerp(lv_.get('right', 1.0), 1.0, k))
        return lv_
    film.levels = levels

def install(film):
    _install_i1(film)
    _install_i2(film)
    _install_i3(film)
    return film
