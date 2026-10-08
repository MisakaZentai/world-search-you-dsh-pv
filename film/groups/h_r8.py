"""Group H r8 (r19 sample; sample_r19/README.md): r7 (groups/h_r7.py, kept unchanged) without the cut back to now;
film 1's last frame holds to the end and a small egg is born in its black.

  主人 on r18: the cut from film 1's black to the paper "now" (297.5) read as a flash; "感觉可以直接删掉，然后黑色部分留个
  彩蛋就好，和上一作呼应", the egg: "走之前 ds-v5-preview 逐渐出现的小彩蛋".

  297.5-301.5  film 1's last frame as before (her caret blinking in her card, her label DeepSeek-V4.1-Flash Max).
               Far right in the black, on her label's line, a new model is born the way she was in film 1's opening
               (pv_dsh_frontend_20260927/batch_a1.model_name, the composer's model label): a seed cell lights (film 1's
               light cell, in the merged one's not-quite-blue), then beside it, in film 1's label face and ink, the
               label types itself and grows: æ¨¡åž‹ (film 1's garbled 模型) -> ckpt-000000 .. ckpt-213000 ->
               sft-step-0000 .. 1200 -> rl-step-0000 .. 0640 -> deepseek-v5-flash-preview, which it keeps. No card,
               no conversation; it never reaches her. Steps on the beat grid run on past the music (silence).

Switches: DSH_H=r8 (film.py); DSH_END=story for the names (cast.py) as before, but r8 adds no now shot.
The dsh pane frames are r7's (ui/pane_h_r7, FOUND .. LAND); its now frames are not used.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import tl
from groups import d_pane as DP
from groups import g as GG
from groups import h as GH
from groups import h_r5 as H5
from groups import h_r6 as H6
from groups import h_r7 as H7
from groups.base import add, full_frame
import hud
from hud import INK, lv
from tuikit import ease
from tuikit.uipane import PaneFrames
P = tl.p
FPS = P.FPS
T0, H1_BACK, TOMATO_T, PIN_T = (H7.T0, H7.H1_BACK, H7.TOMATO_T, H7.PIN_T)
PROG_T, RUFF, JUICE, JUICE_END = (H7.PROG_T, H7.RUFF, H7.JUICE, H7.JUICE_END)
QUIET, PRESS, LAND, MOVE, REVEAL, RIGHT_BACK = (H7.QUIET, H7.PRESS, H7.LAND, H7.MOVE, H7.REVEAL, H7.RIGHT_BACK)
SUPPORT, TITLE, CMD, STAGE = (H7.SUPPORT, H7.TITLE, H7.CMD, H7.STAGE)
B0 = tl.next_beat(tl.END - 0.05)
BEAT = tl.next_beat(B0 + 0.001) - B0

def _b(k: float) -> float:
    return B0 + k * BEAT
SEED_AT = _b(0)
TYPE_AT = _b(0.5)
CKPT = (_b(2), _b(4))
SFT = (_b(4), _b(5))
RL = (_b(5), _b(5.5))
NAME_AT = _b(5.5)
END = tl.END + 4.0
assert NAME_AT + 0.45 + 1.0 <= END
GARBLED = '模型'.encode('utf8').decode('cp1252')
NAME = 'deepseek-v5-flash-preview'
CPS = 12
LABEL_COL = H5.LABEL_COL
SEED_COL = P.color('merged')
SEED_XY = (962, GH.LABEL_TOP + 5)
TEXT_X = SEED_XY[0] + 14

def label(t: float) -> str:
    """The new label at t, film 1's model_name sequence compressed onto the beat grid."""
    if t < TYPE_AT:
        return ''
    if t < CKPT[0]:
        return GARBLED[:int((t - TYPE_AT) * CPS) + 1]
    if t < SFT[0]:
        x = ease.prog(t, *CKPT)
        return f'ckpt-{round(213000 * x ** 1.3):06d}'
    if t < RL[0]:
        return f'sft-step-{round(1200 * ease.prog(t, *SFT)):04d}'
    if t < NAME_AT:
        return f'rl-step-{round(640 * ease.prog(t, *RL)):04d}'
    if t < NAME_AT + 0.15:
        old = 'rl-step-0640'
        return old[:round(len(old) * (1 - (t - NAME_AT) / 0.15))]
    return NAME[:round(len(NAME) * ease.clamp((t - NAME_AT - 0.15) / 0.3))]

def _stage_flash(t: float) -> float:
    """1 on each change of stage (the seed brightens), decaying in 0.25 s."""
    k = 0.0
    for a in (SEED_AT, TYPE_AT, CKPT[0], SFT[0], RL[0], NAME_AT + 0.45):
        if a <= t:
            k = max(k, 1 - ease.prog(t, a, a + 0.25))
    return k

@lru_cache(maxsize=16)
def _cell(glow_q: int) -> Image.Image:
    """Film 1's light cell (a square with a soft halo), 6 px, in SEED_COL; glow_q/10 is the halo strength."""
    s, pad = (6, 10)
    a = Image.new('L', (s + 2 * pad, s + 2 * pad), 0)
    ImageDraw.Draw(a).rectangle([pad, pad, pad + s - 1, pad + s - 1], fill=255)
    halo = a.filter(ImageFilter.GaussianBlur(3)).point(lambda v: min(255, int(v * glow_q / 10 * 2.4)))
    im = Image.new('RGBA', a.size, SEED_COL + (0,))
    im.putalpha(halo)
    body = Image.new('RGBA', a.size, SEED_COL + (0,))
    body.putalpha(a)
    im.alpha_composite(body)
    return im

def draw_egg(img: Image.Image, t: float):
    if t < SEED_AT:
        return
    a = ease.ease_out(ease.prog(t, SEED_AT, SEED_AT + 0.25))
    sp = _cell(int(round(10 * (0.5 + 0.5 * _stage_flash(t)))))
    if a < 0.999:
        al = sp.getchannel('A').point(lambda v: int(v * a))
        sp = sp.copy()
        sp.putalpha(al)
    x, y = SEED_XY
    base = img.convert('RGBA')
    base.alpha_composite(sp, (x - sp.width // 2, y - sp.height // 2))
    s = label(t)
    if s:
        f = GH._label_font()
        top = GH.LABEL_TOP - f.getbbox('D')[1]
        ImageDraw.Draw(base).text((TEXT_X, top), s, font=f, fill=LABEL_COL + (255,))
    img.paste(base.convert('RGB'))

def register(film, end=None, egg=None):
    """end / egg: the last shot's end and its egg drawer (img, t); r19's by default (groups/h_r9.py passes its own)."""
    end = END if end is None else end
    egg = draw_egg if egg is None else egg
    full_frame(T0, H1_BACK, 0.3, 0.4)
    for i in range(7):
        hud.LIVE.append((PROG_T[i], PROG_T[i + 1] if i < 6 else RUFF[0]))
    for (a, _s), nx in zip(H5.TOM_SEG, [x[0] for x in H5.TOM_SEG[1:]] + [PIN_T[0]]):
        hud.LIVE.append((a, nx))
    hud.LIVE.append((JUICE, JUICE_END))
    add(film, 'h1_check', T0, H1_BACK, H7._body, TITLE)
    add(film, 'h2_model', H1_BACK, TOMATO_T[0] - 0.3, H7._body, TITLE)
    add(film, 'h3_tomato', TOMATO_T[0] - 0.3, QUIET, H7._body, TITLE)
    add(film, 'h4_quiet', QUIET, PRESS, H7._body, TITLE)
    film.character = DP.dsh_layer(film, film.character, 'ui/pane_h_r7', GG.FOUND, LAND)
    pane = PaneFrames(tl.HERE / 'ui/pane_h_r7', FPS, (P.W, P.H))

    def slide_fn(c):
        t = c.t
        img = film.background(t)
        d = ImageDraw.Draw(img)
        fade = SUPPORT * (1 - ease.smooth(ease.prog(t, PRESS, MOVE[0] + 0.3)))
        if fade > 0.01:
            hud.frame(d, hud.left_rect(t), TITLE, level=fade)
            hud.tx(d, (36, hud.Y_CMD), CMD, 13, lv(INK, 0.86 * fade))
            H7.draw_left(img, d, t, fade)
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
        if PRESS <= t < LAND:
            return {k: 1.0 for k in lv_}
        if RIGHT_BACK[0] <= t < PRESS and 'right' in lv_:
            up = s_lv + (1 - s_lv) * ease.smooth(ease.prog(t, *RIGHT_BACK))
            lv_ = dict(lv_)
            lv_['right'] = max(lv_['right'], up)
        return lv_
    film.levels = levels

    def last_fn(c):
        img = H6.last_frame(c.t)
        egg(img, c.t)
        c.img.paste(H5.zoomed(img, c.t))
        c.black = True
    film.add('h5_last', LAND, end, last_fn, chapter=chap)
    for t0, side in [(T0, 'both'), (REVEAL, 'left'), (QUIET, 'right')]:
        film.set_lead(t0, side)
    from groups.f import dissolve
    dissolve(film, 'h1_check', 0.4)
    film.finish.append(H6._finish)
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
