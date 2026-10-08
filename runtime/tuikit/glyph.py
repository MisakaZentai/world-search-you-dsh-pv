"""Glyph drawing: decode-typing, token chips, TUI boxes, background field, text sprites."""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import random
import zlib
from PIL import Image, ImageDraw, ImageFilter
from . import ease
GLITCH = '#$%&*+=?@<>/\\|~^_-:;01░▒▓█'

def mix(c1, c2, u: float) -> tuple:
    return tuple((int(a + (b - a) * u) for a, b in zip(c1, c2)))

def level(color, lv: float, bg=(0, 0, 0)) -> tuple:
    """Colour at brightness lv (0..1) over bg."""
    return mix(bg, color, max(0.0, min(1.0, lv)))

def decode(text: str, t: float, t0: float, cps: float=40.0, settle: float=0.08, seed: int=0, charset: str=GLITCH) -> str:
    """Typing with a short scramble per character: char i appears at t0 + i/cps as a random glyph,
    and holds its real value after `settle` seconds. Spaces are never scrambled."""
    out = []
    for i, ch in enumerate(text):
        ti = t0 + i / cps
        if t < ti:
            break
        if ch == ' ' or t >= ti + settle:
            out.append(ch)
        else:
            r = random.Random(seed * 7919 + i * 131 + ease.tick(t, 60))
            out.append(r.choice(charset))
    return ''.join(out)

def typed(text: str, t: float, t0: float, cps: float) -> str:
    """Plain typing without scramble."""
    if t < t0:
        return ''
    return text[:int((t - t0) * cps)] if cps > 0 else text

def token_id(tok: str) -> int:
    return zlib.crc32(tok.encode('utf-8')) % 100000

def box(d: ImageDraw.ImageDraw, rect, color, title: str | None=None, font=None, level_: float=1.0, bg=(0, 0, 0), bracket: int=7, title_color=None):
    """TUI pane: thin outline, brighter corner brackets, optional title chip on the top edge."""
    x0, y0, x1, y1 = rect
    line = level(color, 0.35 * level_, bg)
    corner = level(color, level_, bg)
    d.rectangle(rect, outline=line)
    for cx, cy, sx, sy in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        d.line([(cx, cy), (cx + sx * bracket, cy)], fill=corner)
        d.line([(cx, cy), (cx, cy + sy * bracket)], fill=corner)
    if title and font:
        tw = d.textlength(title, font=font)
        d.rectangle((x0 + 10, y0 - 7, x0 + 18 + tw, y0 + 7), fill=bg)
        d.text((x0 + 14, y0 - 8), title, font=font, fill=level(title_color or color, level_, bg))

def dot_field(img: Image.Image, t: float, color, step: int=16, speed: float=12.0, lv: float=0.18, bg=(0, 0, 0)):
    """Slowly drifting dot grid: ambient motion that fills empty space without shouting."""
    d = ImageDraw.Draw(img)
    off = int(t * speed) % step
    c = level(color, lv, bg)
    for y in range(off % step, img.height, step):
        for x in range(0, img.width, step):
            d.point((x, y), fill=c)

def text_sprite(text: str, font, fill, pad: int=2) -> Image.Image:
    """Clean RGBA sprite of a string: the preferred carrier (redrawn ink, not a screenshot)."""
    tmp = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
    x0, y0, x1, y1 = tmp.textbbox((0, 0), text, font=font)
    im = Image.new('RGBA', (x1 - x0 + 2 * pad, y1 - y0 + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((pad - x0, pad - y0), text, font=font, fill=tuple(fill) + (255,))
    return im

def halo(sprite: Image.Image, color, radius: int=3, strength: float=0.8) -> Image.Image:
    """Add a soft glow around a sprite (the 'lift' of a carrier)."""
    a = sprite.getchannel('A')
    pad = radius * 3
    big = Image.new('L', (sprite.width + 2 * pad, sprite.height + 2 * pad), 0)
    big.paste(a, (pad, pad))
    glow = big.filter(ImageFilter.GaussianBlur(radius)).point(lambda v: int(v * strength))
    out = Image.new('RGBA', big.size, tuple(color) + (0,))
    out.putalpha(glow)
    out.alpha_composite(sprite, (pad, pad))
    return out

def chips(d: ImageDraw.ImageDraw, xy, tokens: list[str], font, colors, small_font=None, gap: int=6, inverted: set | None=None, bg=(0, 0, 0)):
    """Token chips with CRC ids underneath; `inverted` tokens get a filled chip (keywords)."""
    x, y = xy
    inverted = inverted or set()
    for i, tok in enumerate(tokens):
        col = colors[i] if isinstance(colors, list) else colors
        tw = d.textlength(tok, font=font)
        if tok in inverted:
            d.rectangle((x - 3, y - 2, x + tw + 3, y + font.size + 4), fill=col)
            d.text((x, y), tok, font=font, fill=bg)
        else:
            d.text((x, y), tok, font=font, fill=col)
        if small_font:
            d.text((x, y + font.size + 6), str(token_id(tok)), font=small_font, fill=level(col, 0.45, bg))
        x += tw + gap
    return x
