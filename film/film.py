"""《world.search(you);》full film (PLAN_FULL.md, STORYBOARD_v2.md): your terminal on the left, the dsh
window on the right (screenshots from ui/page_full.py), one timeline, frame = f(t).

Each group A-H is a module in groups/ with register(film): it adds the shots of its own span, its LEAD
changes and its notes for the character layer. Shared pieces:
  tl.py       the main line (model, files, sim, stage)      syl.py   sung syllables
  hud.py      the terminal skeleton (strip, layers, fine print)
  inspect_.py the decoding device of the approved sample     cast.py  who wears the persona

The style sample's own code (G2, D16) is kept in sample_p3d/src_v4/.

Character layer: the dsh pane from ui/pane_full/NNNNN.png in the right rect with a hatched shadow. A shot
can hide it (ctx.state["pane"] = False) or move it (ctx.state["pane_dx"]).
Finish: deep(t) maps the whole frame into film 1's deep-sea colours (F, H5; group modules register spans).
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import os
import numpy as np
from PIL import Image, ImageDraw, ImageOps
import hud
import subs
import tl
import groups
from tuikit import Film, ease, glyph
from tuikit.chrome import Chrome
from tuikit.glyph import GLITCH
from tuikit.post import make_post
from tuikit.uipane import PaneFrames
BG, INK, HER = (hud.BG, hud.INK, hud.HER)
TEMPO_TAG = 'tempo: Allegro'
TEMPO_FADE, TEMPO_OPEN = (0.35, 0.3)

def _kimi_span():
    at = tl.MODEL_AT
    for i, (t0, k) in enumerate(at):
        if k == 'kimi':
            return (t0, at[i + 1][0])
    return None
KIMI_SPAN = _kimi_span()

def tempo_u(t):
    """(alpha of the tag, 0..1 of the space opened for it); both 0 outside Kimi's span (tl.model(t) == "kimi")."""
    if KIMI_SPAN is None:
        return (0.0, 0.0)
    t0, t1 = KIMI_SPAN
    alpha = ease.smooth(ease.prog(t, t0, t0 + TEMPO_FADE)) * (1 - ease.smooth(ease.prog(t, t1 - TEMPO_FADE, t1)))
    space = ease.smooth(ease.prog(t, t0 - TEMPO_OPEN, t0)) * (1 - ease.smooth(ease.prog(t, t1, t1 + TEMPO_OPEN)))
    return (alpha, space)

class Band(Chrome):
    """Lyric band: words type in on their onsets; the sung word gets a her-blue underline that grows over its
    sung length (no jumping black box, D15); a second line gives the Chinese, still for the whole line (R6).
    D1: the underline is the one lit blue only while nothing of hers is landing on the page (hud.live_k);
    the header's blue (memory label, waveform, progress) is the quiet blue."""

    def header(self, img, t, ctx):
        real = self.p.colors.get('her')
        self.p.colors['her'] = hud.HER_QUIET
        alpha, space = tempo_u(t)
        status = self.status
        if space > 0:
            n = int(round((len(TEMPO_TAG) + 3) * space))
            self.status = lambda t_, ctx_: (lambda s: s[:-1] + [(s[-1][0] + ' ' * n, s[-1][1])])(status(t_, ctx_))
        try:
            super().header(img, t, ctx)
        finally:
            self.p.colors['her'] = real
            self.status = status
        if alpha > 0.003 and self.p.has_rect('header'):
            self._tempo_tag(img, t, ctx, alpha)

    def _tempo_tag(self, img, t, ctx, alpha):
        """N19: `tempo: Allegro` after `pid 1077`, placed with the same arithmetic as tuikit's header (title and
        status items one after another, three spaces between)."""
        x0, y0, x1, y1 = self.p.rect('header')
        d = ImageDraw.Draw(img)
        f = self.p.font(14, 'bold')
        x = x0 + 24 + d.textlength(self.title + '   ', font=f)
        items = self.status(t, ctx)
        for text, _c in items[:-1]:
            x += d.textlength(text + '   ', font=f)
        x += d.textlength(items[-1][0] + '   ', font=f)
        bg = self.p.color('bg')
        d.text((x, (y0 + y1) // 2 - 8), TEMPO_TAG, font=f, fill=glyph.level(self.p.color('dim'), alpha, bg))

    def band(self, img, t):
        if subs.ON:
            return subs.band(self, img, t)
        if not self.p.has_rect('lyric_band'):
            return
        x0, y0, x1, y1 = self.p.rect('lyric_band')
        d = ImageDraw.Draw(img)
        bg, ink, her = (self.p.color('bg'), self.p.color('ink'), self.p.color('her'))
        hud.frame(d, (x0, y0, x1, y1), self.band_title, 12)
        L = self.p.lyrics.line_at(t)
        if L is None or not L.words:
            return
        font = self.band_font()
        under = glyph.mix(hud.HER_LIVE, hud.HER_QUIET, hud.live_k(t))
        alpha = 1.0
        until = self.p.lyrics.until(L)
        if until < self.p.lyrics.next_start(L):
            alpha = 1.0 - ease.prog(t, until - 0.5, until)
        px, py = (x0 + 26, y0 + 14)
        d.text((px - 18, py), '>', font=font, fill=glyph.level(hud.HER_QUIET, alpha, bg))
        for wp, w in zip(self.plan(L, font), L.words):
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
            d.text((px + wp.x, py), ''.join(shown), font=font, fill=glyph.level(ink, alpha, bg))
            end = max(w.end, w.start + 0.12)
            if w.start <= t < end + 0.25:
                u = ease.prog(t, w.start, end)
                fade = 1 - ease.prog(t, end, end + 0.25)
                tw = d.textlength(wp.text, font=font)
                d.rectangle((px + wp.x, py + font.size + 5, px + wp.x + tw * u, py + font.size + 8), fill=glyph.level(under, alpha * fade, bg))
        if L.id in tl.ZH:
            a_ = alpha * ease.prog(t, L.start - 0.05, L.start + 0.25)
            d.text((px, y1 - 30), tl.ZH[L.id], font=self.p.font(15, 'cjk'), fill=glyph.level(ink, 0.78 * a_, bg))
DEEP_BG = np.array(tl.p.color('deep'), np.float32)
DEEP_INK = np.array((198, 212, 236), np.float32)
HER_A = np.array(HER, np.float32)

def deep(t: float) -> float:
    u = 0.0
    for t0, t1, fi, fo in hud.DEEP:
        if t0 - 1e-06 <= t < t1 + fo:
            u = max(u, ease.smooth(ease.prog(t, t0, t0 + fi)) * (1 - ease.smooth(ease.prog(t, t1, t1 + fo))))
    return u

def to_deep(img: Image.Image, u: float) -> Image.Image:
    """Paper -> deep sea: luminance inverts onto deep-blue ink; her blue stays blue."""
    a = np.asarray(img, np.float32)
    lum = (a @ np.array([0.299, 0.587, 0.114], np.float32))[..., None] / 255.0
    out = DEEP_BG + (1 - lum) * (DEEP_INK - DEEP_BG)
    sat = (a.max(axis=2) - a.min(axis=2))[..., None] / 255.0
    keep = np.clip((sat - 0.25) * 2.5, 0, 1)
    out = out * (1 - keep) + (a * 0.85 + HER_A * 0.15) * keep
    mixed = a * (1 - u) + out * u
    return Image.fromarray(np.clip(mixed, 0, 255).astype(np.uint8))

def build(p):
    film = Film(p)
    pane = PaneFrames(p.path('ui/pane_v2' if tl.V2 else 'ui/pane_full'), p.FPS, (p.W, p.H))
    R = p.rect('right')
    lv = hud.lv

    def character(t, n, ctx):
        if ctx is not None and ctx.state.get('pane') is False:
            return None
        layer = Image.new('RGBA', (p.W, p.H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        dx = hud.pane_dx(t)
        if ctx is not None and 'pane_dx' in ctx.state:
            dx = int(ctx.state['pane_dx'])
        if R[0] + dx >= p.W:
            return None
        x0, y0, x1, y1 = (R[0] + dx, R[1], R[2] + dx, R[3])
        for k in range(x0 + 7 - (y1 - y0), x1 + 7, 5):
            a_ = (max(k, x0 + 7), y0 + 7 + max(0, x0 + 7 - k))
            b_ = (min(k + (y1 - y0), x1 + 7), y0 + 7 + min(y1 - y0, x1 + 7 - k))
            if a_[0] <= b_[0]:
                d.line([a_, b_], fill=lv(INK, 0.55) + (255,))
        pr = p.rect('pane')
        im = pane.layer(t, (pr[0] + dx, pr[1], pr[2] + dx, pr[3]))
        if im is not None:
            layer.alpha_composite(im)
        else:
            d.rectangle((pr[0] + dx, pr[1], pr[2] + dx, pr[3]), fill=(250, 250, 250, 255))
            d.text((pr[0] + dx + 20, pr[1] + 20), 'dsh pane: frame missing', font=p.font(12), fill=INK + (255,))
        d = ImageDraw.Draw(layer)
        d.rectangle((x0, y0, x1, y1), outline=INK + (255,), width=2)
        f13 = p.font(13)
        tw = d.textlength('dsh · web', font=f13)
        d.rectangle((x0 + 12, y0 - 7, x0 + 22 + tw, y0 + 7), fill=BG + (255,))
        d.text((x0 + 17, y0 - 7), 'dsh · web', font=f13, fill=INK + (255,))
        return layer
    film.character = character
    film.chrome = Band(p, title='WORLD.SEARCH(YOU);  you@surface:~$', band_title='stdin · query', status=tl.status, chapter=tl.chapter)
    film.post = make_post(bloom=0.0, scan=0.97, every=3)
    regions = film.lead_regions
    s_lv = p.setting('support_level', 0.42)
    sink = p.setting('support_sink', 0.86)

    def dim_paper(img, levels):
        for region, level in levels.items():
            rect = regions.get(region)
            if rect is None or level >= 0.999:
                continue
            k = min(1.0, (1 - level) / (1 - s_lv))
            part = img.crop(rect)
            grey = ImageOps.grayscale(part).convert('RGB')
            part = Image.blend(part, grey, 0.55 * k)
            part = Image.blend(part, Image.new('RGB', part.size, BG), 0.12 * k)
            if region == 'right':
                part = Image.eval(part, lambda v, m=1 - (1 - sink) * k: int(v * m))
            img.paste(part, rect[:2])
        return img
    film._dim = dim_paper
    if os.environ.get('DSH_SHADE') == 'd11':
        import lead
        lead.install(film)
    base_levels = film.levels

    def levels(t):
        """D2: while the terminal fills the frame it is never the dimmed side."""
        lv_ = base_levels(t)
        u = hud.full_u(t, p.setting('lead_fade', 0.5))
        if u > 0:
            lv_ = dict(lv_)
            lv_['left'] = ease.lerp(lv_['left'], 1.0, u)
        return lv_
    film.levels = levels

    def finish_deep(img, t):
        u = deep(t)
        return to_deep(img, u) if u > 0.003 else None
    mods = list(groups.ALL)
    if os.environ.get('DSH_A') == 'open':
        from groups import a_open
        mods = [a_open if m is groups.a else m for m in mods]
    if os.environ.get('DSH_B') == 'open':
        from groups import b_open
        mods = [b_open if m is groups.b else m for m in mods]
    elif os.environ.get('DSH_B') == 'pane':
        from groups import b_pane
        mods = [b_pane if m is groups.b else m for m in mods]
    elif os.environ.get('DSH_B') == 'lead':
        from groups import b_lead
        mods = [b_lead if m is groups.b else m for m in mods]
    if os.environ.get('DSH_D') == 'pane':
        from groups import d_pane
        mods = [d_pane if m is groups.d else m for m in mods]
    elif os.environ.get('DSH_D') == 'lead':
        from groups import d_lead
        mods = [d_lead if m is groups.d else m for m in mods]
    elif os.environ.get('DSH_D') == 'r5':
        from groups import d_r5
        mods = [d_r5 if m is groups.d else m for m in mods]
    if os.environ.get('DSH_E') == 'pane':
        from groups import e_pane
        mods = [e_pane if m is groups.e else m for m in mods]
    elif os.environ.get('DSH_E') == 'r5':
        from groups import e_r5
        mods = [e_r5 if m is groups.e else m for m in mods]
    if os.environ.get('DSH_F') == 'pane':
        from groups import f_pane
        mods = [f_pane if m is groups.f else m for m in mods]
    elif os.environ.get('DSH_F') == 'r5':
        from groups import f_r5
        mods = [f_r5 if m is groups.f else m for m in mods]
    if os.environ.get('DSH_G') == 'pane':
        from groups import g_pane
        mods = [g_pane if m is groups.g else m for m in mods]
    elif os.environ.get('DSH_G') == 'mirror':
        from groups import g_mirror
        mods = [g_mirror if m is groups.g else m for m in mods]
    elif os.environ.get('DSH_G') == 'lead':
        from groups import g_lead
        mods = [g_lead if m is groups.g else m for m in mods]
    elif os.environ.get('DSH_G') == 'r5':
        from groups import g_r5
        mods = [g_r5 if m is groups.g else m for m in mods]
    if os.environ.get('DSH_H') == 'pane':
        from groups import h_pane
        mods = [h_pane if m is groups.h else m for m in mods]
    elif os.environ.get('DSH_H') == 'a':
        from groups import h_a
        mods = [h_a if m is groups.h else m for m in mods]
    elif os.environ.get('DSH_H') == 'r5':
        from groups import h_r5
        mods = [h_r5 if m is groups.h else m for m in mods]
    elif os.environ.get('DSH_H') == 'r6':
        from groups import h_r6
        mods = [h_r6 if m is groups.h else m for m in mods]
    elif os.environ.get('DSH_H') == 'r7':
        from groups import h_r7
        mods = [h_r7 if m is groups.h else m for m in mods]
    elif os.environ.get('DSH_H') == 'r8':
        from groups import h_r8
        mods = [h_r8 if m is groups.h else m for m in mods]
    elif os.environ.get('DSH_H') == 'r9':
        from groups import h_r9
        mods = [h_r9 if m is groups.h else m for m in mods]
    elif os.environ.get('DSH_H') == 'r10':
        from groups import h_r10
        mods = [h_r10 if m is groups.h else m for m in mods]
    if tl.V2:
        from groups import c_p4
        c_mod = c_p4
        drop = set()
        if os.environ.get('DSH_C') == 'open':
            from groups import c_open
            c_mod, drop = (c_open, {'c2_arcs', 'c6_board'})
        elif os.environ.get('DSH_C') == 'pane':
            from groups import c_pane
            c_mod, drop = (c_pane, {'c2_arcs', 'c6_board'})
        elif os.environ.get('DSH_C') == 'lead':
            from groups import c_lead
            c_mod, drop = (c_lead, {'c2_arcs', 'c6_board'})
        film.use(*[c_mod if m is groups.c else m for m in mods])
        import inside.install
        import inside.shots
        spans = [s for s in inside.shots.spans() if s.name not in drop]
        if os.environ.get('DSH_G') == 'mirror':
            from groups import g_mirror
            spans = g_mirror.spans(spans)
        elif os.environ.get('DSH_G') == 'lead':
            from groups import g_lead
            spans = g_lead.spans(spans)
        elif os.environ.get('DSH_G') == 'r5':
            from groups import g_r5
            spans = g_r5.spans(spans)
        inside.install.install(film, spans)
    else:
        film.use(*mods)
    if os.environ.get('DSH_I') == 'r5':
        import interludes
        interludes.install(film)
    if os.environ.get('DSH_WALL') == 'r6':
        import wall
        wall.install(film)
    if os.environ.get('DSH_VIZ') == 'b':
        import viz_b
        viz_b.install(film)
    elif os.environ.get('DSH_VIZ'):
        import viz7
        viz7.install(film, os.environ['DSH_VIZ'])
    if os.environ.get('DSH_REP') == 'g':
        import rep_g
        rep_g.install(film)
    elif os.environ.get('DSH_REP') == 'g2':
        import rep_g2
        rep_g2.install(film)
    elif os.environ.get('DSH_REP') == 'g3':
        import rep_g3
        rep_g3.install(film)
    elif os.environ.get('DSH_REP') == 'g4':
        import rep_g4
        rep_g4.install(film)
    elif os.environ.get('DSH_REP') == 'g5':
        import rep_g5
        rep_g5.install(film)
    elif os.environ.get('DSH_REP') == 'g6':
        import rep_g6
        rep_g6.install(film)
    elif os.environ.get('DSH_REP') == 'g7':
        import rep_g7
        rep_g7.install(film)
    elif os.environ.get('DSH_REP') == 'g8':
        import rep_g8
        rep_g8.install(film)
    if os.environ.get('DSH_I2'):
        import rep_i2
        rep_i2.install(film)
    film.finish.append(finish_deep)
    film.finalize(end=tl.END)
    return film
