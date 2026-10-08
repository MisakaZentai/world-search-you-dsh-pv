"""inside_lab common: a synthetic 64-layer decoder + a small dot renderer.

Nothing here imports the project's modules; nothing here writes outside inside_lab/.

The "model" is synthetic but every visible quantity is shaped like a real one:
  * columns  = token positions in the context (persona, memory file names, an old turn, the question)
  * rows     = the residual stream after each of 64 blocks (Qwen3-32B-class depth)
  * dots     = a handful of residual dimensions of that (layer, position) vector
  * bottom   = token embedding (per-token random: looks like noise)
  * higher   = accumulated residual: segment-level and feature-level structure, norm grows
  * column 0 = attention sink with one "massive activation" dim (Sun et al. 2024)
  * attention= per (step, layer) weights over earlier positions: sink, previous-token heads in
               early layers, a few content heads that read specific tokens (EVENTS below)
  * lens     = logit-lens readout at layers 12/24/36/48/64 (LENS below), confidence rising with depth
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import hashlib
import math
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
W, H, FPS = (1280, 720, 24)
FONT_PATHS = {'cjk': 'C:/Windows/Fonts/msyh.ttc', 'cjkb': 'C:/Windows/Fonts/msyhbd.ttc', 'mono': 'C:/Windows/Fonts/consola.ttf', 'monob': 'C:/Windows/Fonts/consolab.ttf'}
_FONTS: dict = {}

def font(size: int, kind: str='cjk'):
    key = (size, kind)
    if key not in _FONTS:
        _FONTS[key] = ImageFont.truetype(FONT_PATHS[kind], size)
    return _FONTS[key]

def is_cjk(s: str) -> bool:
    return all((ord(c) > 11904 for c in s))
SEGMENTS = [('sys', ['<|im_start|>', 'system']), ('persona', ['你', '是', '大', '肥', '鱼', '，', '一只', '住在', '终端', '里', '的', '猫', '，', '说话', '结尾', '带', '喵', '。']), ('memory', ['memory', '/you/', 'first', '_hello', '.md', 'your', '_cat', '.md', 'rainy', '_day', '.md', 'fish', '_soup', '.md', 'good', 'night', '.md', 'typo', '_you', '.md']), ('history', ['<|im_start|>', 'user', '你', '还在', '吗', '？', '<|im_start|>', 'assistant', '在', '的', '喵', '。']), ('user', ['<|im_start|>', 'user', '今晚', '想', '吃', '什么', '？']), ('asst', ['<|im_start|>', 'assistant'])]
ANSWER = ['吃', '鱼', '喵']
QUESTION = '今晚想吃什么？'
TOKENS: list[str] = []
SEG_OF: list[str] = []
for _name, _toks in SEGMENTS:
    for _t in _toks:
        TOKENS.append(_t)
        SEG_OF.append(_name)
N_CTX = len(TOKENS)
TOKENS_ALL = TOKENS + ANSWER
SEG_ALL = SEG_OF + ['gen'] * len(ANSWER)
NCOL = len(TOKENS_ALL)
L = 64
LENS_LAYERS = [12, 24, 36, 48, 64]
LENS = [['我', '作', '想', '吃', '吃'], ['的', '饭', '肉', '鱼', '鱼'], ['。', '！', '吧', '喵', '喵']]
LENS_CONF = [0.1, 0.2, 0.38, 0.68, 0.93]
CUR_COL = [N_CTX - 1, N_CTX, N_CTX + 1]

def pos(seg: str, tok: str, nth: int=0) -> int:
    hits = [i for i, (s, t) in enumerate(zip(SEG_OF, TOKENS)) if s == seg and t == tok]
    return hits[nth]
EVENTS = [[(17, [(pos('user', '吃'), 0.95), (pos('user', '什么'), 0.5)]), (31, [(pos('memory', 'fish'), 0.7), (pos('memory', '_soup'), 0.45)]), (46, [(pos('persona', '猫'), 0.6)])], [(21, [(pos('persona', '鱼'), 0.95), (pos('persona', '肥'), 0.4)]), (37, [(pos('memory', 'fish'), 0.7)])], [(19, [(pos('persona', '喵'), 0.95), (pos('persona', '带'), 0.4)]), (42, [(pos('history', '喵'), 0.6), (pos('memory', '_cat'), 0.5)])]]
FEATURES = {'cat': ([3], +1, {'猫', '喵', 'your', '_cat', '大', '肥', '鱼'}, 38, 14), 'food': ([1], +1, {'吃', '鱼', 'fish', '_soup', '今晚', '什么'}, 30, 12), 'you': ([4], -1, {'你', '_you', 'your', 'typo'}, 26, 10), 'md': ([2, 5], +1, {'.md'}, 14, 8)}

def _tok_seed(s: str) -> int:
    return int(hashlib.md5(s.encode('utf-8')).hexdigest()[:8], 16)

def build_residual(D: int=6, seed: int=11):
    """Return I[l-1, p, d] in [0,1]: display intensity of residual dims; also R raw."""
    rng = np.random.default_rng(seed)
    E = np.stack([np.random.default_rng(_tok_seed(t)).standard_normal(D) for t in TOKENS_ALL])
    walk = np.cumsum(rng.standard_normal((L, NCOL, D)) * 0.2, axis=0)
    segs = sorted(set(SEG_ALL))
    S = {}
    for sname in segs:
        w = np.cumsum(rng.standard_normal((L + 8, D)) * 0.45, axis=0)
        k = np.ones(7) / 7
        w = np.stack([np.convolve(w[:, d], k, mode='same') for d in range(D)], axis=1)[4:L + 4]
        S[sname] = w
    seg_arr = np.stack([S[s] for s in SEG_ALL], axis=1)
    lv = np.arange(1, L + 1) / L
    a = 1.15 - 0.85 * lv
    c = 1.9 * lv ** 1.4
    R = a[:, None, None] * E[None] + walk + c[:, None, None] * seg_arr
    Rs = R.copy()
    for p in range(1, NCOL - 1):
        same_l = SEG_ALL[p - 1] == SEG_ALL[p]
        same_r = SEG_ALL[p + 1] == SEG_ALL[p]
        acc = R[:, p].copy()
        n = 1.0
        if same_l:
            acc += R[:, p - 1]
            n += 1
        if same_r:
            acc += R[:, p + 1]
            n += 1
        Rs[:, p] = acc / n
    mix = (lv ** 1.2)[:, None, None]
    R = (1 - mix) * R + mix * Rs
    for _name, (dims, sign, members, lc, lw) in FEATURES.items():
        prof = np.exp(-((np.arange(1, L + 1) - lc) / lw) ** 2) * 3.2
        for p, t in enumerate(TOKENS_ALL):
            if t in members:
                for d in dims:
                    R[:, p, d] += sign * prof
    R[2:, 0, 0] += 9.0
    R[2:, 0, 3] -= 3.0
    rms = np.sqrt((R[:, 1:, :] ** 2).mean(axis=(1, 2)))[:, None, None]
    v = np.abs(R) / rms
    I = np.clip((v - 0.35) / 1.9, 0, 1) ** 1.15
    return (I.astype(np.float32), R)

def build_activity(D: int=6, seed: int=5):
    """Return I[l-1, p, d] in [0,1]: what each block writes at (layer, position), a few dims.

    Low blocks write high-entropy, token-local updates (looks like static).  Higher blocks write
    updates that are shared inside a segment and vary smoothly (contextual mixing), plus sparse
    semantic features that fire on related tokens across segments, plus the sink's massive dim.
    """
    rng = np.random.default_rng(seed)
    lv = (np.arange(1, L + 1) / L)[:, None, None]
    noise = np.abs(rng.standard_normal((L, NCOL, D)))
    E = np.stack([np.abs(np.random.default_rng(_tok_seed(t)).standard_normal(D)) for t in TOKENS_ALL])
    low = 0.55 * noise + 0.45 * E[None]
    segs = sorted(set(SEG_ALL))
    struct = np.zeros((L, NCOL, D))
    for sname in segs:
        cols = [i for i, s in enumerate(SEG_ALL) if s == sname]
        P = np.abs(rng.standard_normal(D)) * 0.9 + 0.25
        P[rng.integers(0, D)] *= 0.15
        k = np.ones(9) / 9
        mod_l = np.convolve(rng.standard_normal(L + 16), k, mode='same')[8:L + 8]
        mod_l = 0.65 + 0.45 * np.tanh(2.2 * mod_l)
        n = len(cols)
        mod_p = np.convolve(rng.standard_normal(n + 6), np.ones(5) / 5, mode='same')[3:n + 3]
        mod_p = 1 + 0.55 * np.tanh(2.0 * mod_p)
        P2 = np.abs(rng.standard_normal(D)) * 0.9 + 0.2
        blend = np.clip((np.arange(1, L + 1) - 40) / 14, 0, 1)[:, None]
        pat = (1 - blend) * P[None] + blend * P2[None]
        for j, c in enumerate(cols):
            struct[:, c, :] = pat * mod_l[:, None] * mod_p[j]
    struct *= 1 + 0.12 * rng.standard_normal((L, NCOL, D))
    for _name, (dims, sign, members, lc, lw) in FEATURES.items():
        prof = np.exp(-((np.arange(1, L + 1) - lc) / lw) ** 4) * 2.1
        for p, t in enumerate(TOKENS_ALL):
            if t in members:
                for d in dims:
                    struct[:, p, d] += prof
    struct[3:, 0, 0] += 3.2
    struct[3:, 0, 3] += 1.4
    wn = (1 - lv) ** 1.6
    ws = np.clip(lv * 1.25, 0, 1) ** 1.1
    A = wn * low * 1.1 + ws * struct * 0.85
    I = np.clip((A - 0.22) / 1.25, 0, 1)
    return I.astype(np.float32)

def attn_weights(step: int, layer: int) -> np.ndarray:
    """Weights over columns 0..c-1 for the query at column c, at a given layer (1-based)."""
    c = CUR_COL[step]
    w = np.zeros(NCOL, np.float32)
    if layer >= 2:
        w[0] += 0.28
    if layer <= 9:
        w[c - 1] += 0.55
        w[c - 2] += 0.12
    idx = np.arange(c)
    w[:c] += 0.05 * np.exp(-(c - 1 - idx) / 4.0)
    for lay, targets in EVENTS[step]:
        b = math.exp(-((layer - lay) / 1.6) ** 2)
        for p, wt in targets:
            w[p] += wt * b
    w[c:] = 0
    return w

def attn_table() -> np.ndarray:
    """A[step, l-1, p]"""
    return np.stack([np.stack([attn_weights(s, l) for l in range(1, L + 1)]) for s in range(len(ANSWER))])

def smooth(u):
    u = np.clip(u, 0.0, 1.0)
    return u * u * (3 - 2 * u)

def front_progress(u):
    """0..1 -> 0..1, mostly linear (a sweep), eased only at the ends."""
    u = np.clip(u, 0.0, 1.0)
    return 0.72 * u + 0.28 * smooth(u)

def pass_times(t0: float, dur: float, nrows: int=L) -> np.ndarray:
    """Time at which the front (rising 0..nrows over dur) crosses row centre l-0.5, l=1..nrows."""
    uu = np.linspace(0, 1, 4001)
    hh = front_progress(uu) * nrows
    return t0 + dur * np.interp(np.arange(1, nrows + 1) - 0.5, hh, uu)

def env_decay(dt, tau, attack=0.012):
    """0 before dt=0, quick attack, exponential decay."""
    dt = np.asarray(dt, np.float32)
    a = np.clip(dt / attack, 0, 1)
    return np.where(dt < 0, 0.0, a * np.exp(-np.maximum(dt, 0) / tau)).astype(np.float32)
DOT_K = np.array([[0.18, 0.5, 0.18], [0.5, 1.0, 0.5], [0.18, 0.5, 0.18]], np.float32)

def dotify(buf: np.ndarray, k: np.ndarray=DOT_K) -> np.ndarray:
    out = np.zeros_like(buf)
    r = k.shape[0] // 2
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            wgt = k[dy + r, dx + r]
            if wgt == 0:
                continue
            ys = slice(max(0, dy), buf.shape[0] + min(0, dy))
            yd = slice(max(0, -dy), buf.shape[0] + min(0, -dy))
            xs = slice(max(0, dx), buf.shape[1] + min(0, dx))
            xd = slice(max(0, -dx), buf.shape[1] + min(0, -dx))
            out[ys, xs] += wgt * buf[yd, xd]
    return out

def splat(buf: np.ndarray, xs, ys, vals):
    """Bilinear point splat (adds)."""
    xs = np.asarray(xs, np.float32)
    ys = np.asarray(ys, np.float32)
    vals = np.asarray(vals, np.float32)
    ok = (xs >= 0) & (ys >= 0) & (xs < buf.shape[1] - 1) & (ys < buf.shape[0] - 1) & (vals > 0.0001)
    xs, ys, vals = (xs[ok], ys[ok], vals[ok])
    x0 = np.floor(xs).astype(np.int32)
    y0 = np.floor(ys).astype(np.int32)
    fx = xs - x0
    fy = ys - y0
    np.add.at(buf, (y0, x0), vals * (1 - fx) * (1 - fy))
    np.add.at(buf, (y0, x0 + 1), vals * fx * (1 - fy))
    np.add.at(buf, (y0 + 1, x0), vals * (1 - fx) * fy)
    np.add.at(buf, (y0 + 1, x0 + 1), vals * fx * fy)

def _box(a: np.ndarray, r: int, axis: int) -> np.ndarray:
    c = np.cumsum(np.pad(a, [(r + 1, r) if i == axis else (0, 0) for i in range(a.ndim)], mode='edge'), axis=axis)
    n = a.shape[axis]
    hi = np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis)
    lo = np.take(c, np.arange(0, n), axis=axis)
    return (hi - lo) / (2 * r + 1)

def glow(buf: np.ndarray, factor: int=4, r: int=3, passes: int=2) -> np.ndarray:
    h, w = buf.shape
    small = buf[:h - h % factor, :w - w % factor].reshape(h // factor, factor, w // factor, factor).mean(axis=(1, 3))
    for _ in range(passes):
        small = _box(_box(small, r, 0), r, 1)
    im = Image.fromarray(small.astype(np.float32), mode='F').resize((w, h), Image.BILINEAR)
    return np.asarray(im, np.float32)

def text_mask(s: str, size: int, kind: str='cjk') -> np.ndarray:
    f = font(size, kind)
    pad = 4
    bb = f.getbbox(s)
    w = bb[2] - bb[0] + pad * 2
    h = bb[3] - bb[1] + pad * 2
    im = Image.new('L', (max(1, w), max(1, h)), 0)
    ImageDraw.Draw(im).text((pad - bb[0], pad - bb[1]), s, font=f, fill=255)
    a = np.asarray(im, np.float32) / 255.0
    ys, xs = np.nonzero(a > 0.02)
    if len(ys) == 0:
        return np.zeros((1, 1), np.float32)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]

def label_mask(tok: str, size: int=10) -> np.ndarray:
    """Token label for a narrow column: CJK stacked upright, latin rotated (reads bottom-up)."""
    disp = {'<|im_start|>': '<s>', 'system': 'sys', 'assistant': 'asst'}.get(tok, tok)
    if is_cjk(disp):
        parts = [text_mask(ch, size + 1, 'cjk') for ch in disp]
        wmax = max((p.shape[1] for p in parts))
        gap = 2
        hh = sum((p.shape[0] for p in parts)) + gap * (len(parts) - 1)
        out = np.zeros((hh, wmax), np.float32)
        y = 0
        for p in parts:
            x = (wmax - p.shape[1]) // 2
            out[y:y + p.shape[0], x:x + p.shape[1]] = p
            y += p.shape[0] + gap
        return out
    m = text_mask(disp, size, 'mono')
    return np.rot90(m, 1).copy()

def blit(buf: np.ndarray, m: np.ndarray, x: int, y: int, val: float=1.0):
    h, w = m.shape
    x0, y0 = (max(0, x), max(0, y))
    x1, y1 = (min(buf.shape[1], x + w), min(buf.shape[0], y + h))
    if x1 <= x0 or y1 <= y0:
        return
    buf[y0:y1, x0:x1] += val * m[y0 - y:y1 - y, x0 - x:x1 - x]

def glyph_dots(ch: str, n: int=14, thr: float=0.34, kind: str='cjkb'):
    """Rasterise a character onto an n x n dot grid. Returns (ii, jj, cov) of lit dots."""
    S = n * 8
    im = Image.new('L', (S, S), 0)
    f = font(int(S * 0.92), kind)
    bb = f.getbbox(ch)
    gw, gh = (bb[2] - bb[0], bb[3] - bb[1])
    ImageDraw.Draw(im).text(((S - gw) / 2 - bb[0], (S - gh) / 2 - bb[1]), ch, font=f, fill=255)
    a = np.asarray(im, np.float32).reshape(n, 8, n, 8).mean(axis=(1, 3)) / 255.0
    ii, jj = np.nonzero(a > thr)
    return (ii, jj, a[ii, jj])

class Writer:

    def __init__(self, path: str, w: int=W, h: int=H, fps: int=FPS, crf: int=14):
        self.p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{w}x{h}', '-r', str(fps), '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', str(crf), '-pix_fmt', 'yuv420p', '-movflags', '+faststart', path], stdin=subprocess.PIPE)

    def write(self, rgb: np.ndarray):
        self.p.stdin.write(np.ascontiguousarray(rgb, dtype=np.uint8).tobytes())

    def close(self):
        self.p.stdin.close()
        self.p.wait()

def hex2rgb(h: str) -> np.ndarray:
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255.0
