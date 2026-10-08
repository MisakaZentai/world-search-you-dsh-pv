"""tuikit: a small, song-agnostic framework for TUI-style music videos.

It distils the architecture that shipped the world.execute(me) TUI PV:
frame = f(t), shots on one timeline, staged cuts with carriers, a
character layer, LEAD/SUPPORT dimming, chrome and lyric band drawn last,
post, and chunked parallel rendering with the song muxed in.

Typical project layout (see ../example):

    PROJECT.yaml      constants (song, size, palette, rects)
    timing/           beats.json, words.json
    film.py           def build(project) -> tuikit.Film
"""
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
from .project import Project, load
from .timing import Clock, Lyrics, lands
from .film import Film, Ctx, Shot, Cut, Frame
from . import ease, glyph, carriers, post, chrome, uipane, space
__all__ = ['Project', 'load', 'Clock', 'Lyrics', 'lands', 'Film', 'Ctx', 'Shot', 'Cut', 'Frame', 'ease', 'glyph', 'carriers', 'post', 'chrome', 'uipane', 'space']
