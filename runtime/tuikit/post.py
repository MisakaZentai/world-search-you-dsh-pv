"""Post: bloom and scanlines (CPU, numpy). Applied after chrome, before LEAD dimming.

The shipped film ran the same maths on the GPU with torch (see ../../tui/ARCHITECTURE.md);
CPU is fast enough at 1280x720 when frames are rendered in parallel processes.
Trail (phosphor persistence) is left out on purpose: it makes a frame depend on the previous
one, which breaks 'frame = f(t)' at chunk boundaries unless every chunk pre-renders a seed frame.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import numpy as np
from PIL import Image, ImageFilter

def make_post(bloom: float=0.35, radius: float=4.0, scan: float=0.784, every: int=3):

    def post(img: Image.Image) -> Image.Image:
        W, H = img.size
        a = np.asarray(img, dtype=np.float32)
        if bloom > 0:
            small = img.resize((W // 2, H // 2), Image.BILINEAR).filter(ImageFilter.GaussianBlur(radius / 2))
            b = np.asarray(small.resize((W, H), Image.BILINEAR), dtype=np.float32)
            a = a + b * bloom
        if scan < 1.0 and every > 1:
            a[every - 1::every] *= scan
        return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return post
