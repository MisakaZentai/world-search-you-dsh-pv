"""Render CLI. The project directory holds PROJECT.yaml and film.py (def build(project) -> Film).

  python -m tuikit.render <project> stills <t> [<t> ...] [--out stills] [--samples N|auto]
  python -m tuikit.render <project> render <t0> <t1> <out.mp4> [--workers 8] [--master] [--no-audio]
                                          [--samples N|auto] [--shutter 0.2] [--tol 3]
  python -m tuikit.render <project> strips <t0> <t1> [--out strips]
  python -m tuikit.render <project> perf <t0> <t1> [--samples N|auto]
  python -m tuikit.render <project> upscale <in.mp4> <out.mp4> [--scale 3] [--mix wav@t ...] [--codec hevc_nvenc | --cpu]
  python -m tuikit.render <project> small <in.mp4> <out.mp4> [--width 960]

t0 / t1 are song seconds or shot names (t0 = the shot's start, t1 = its end), e.g. "render boot fall".

render: frames are split into contiguous chunks and rendered by worker processes, each piping raw
RGB into its own ffmpeg; chunks are concatenated and the song is muxed from the original audio at
the same offset. --master writes lossless libx264rgb (qp 0) for the delivery chain.
strips: for every cut in range, 15 frames at 12 fps from T-0.6 s (frame 8 is the cut), tiled 5x3.
upscale: integer nearest-neighbour upscale (glyph pixels stay crisp) + audio from the original
file, optionally mixed with extra sounds at given song times. hevc_nvenc encodes on the GPU (ask the
owner first, <local-production-path> --cpu is libx265 (preset medium, CRF 16, hvc1).
Audio is cut to the video's length and, where the film runs past the song (an ending in silence),
padded with silence: render and upscale never cut the film to the song (before 2026-10-06 upscale did).
perf: ms per frame (avg / p50 / p95 / max) per shot, and the sub-frame histogram with --samples.

Colour: every YUV output converts RGB with the BT.709 matrix and tags primaries, transfer and matrix
as BT.709. Untagged HD is decoded as BT.709 by browsers and phones; converting with ffmpeg's default
BT.601 matrix shifted #ff3b30 by 17 levels (measured 2026-09-28). Same fix as pdoom-video's render.ts.
"""
from __future__ import annotations
from pv_paths import ROOT as PV_ROOT
from pv_text import load_chinese, lyric_fragment
import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from PIL import Image, ImageDraw
from .project import load
_FILM = None

def load_film(project_dir):
    p = load(project_dir)
    spec = importlib.util.spec_from_file_location(f'film_{p.cfg['project']['id']}', p.root / 'film.py')
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(p.root))
    spec.loader.exec_module(mod)
    film = mod.build(p)
    film.finalize()
    return film

def _init(project_dir):
    global _FILM
    _FILM = load_film(project_dir)
BT709 = 'out_color_matrix=bt709:out_range=tv'
TAGS = 'setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709'
TAG_FLAGS = ['-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709']

def yuv709(pre: str='') -> str:
    """-vf chain: optional scaling, RGB -> YUV 4:2:0 with the BT.709 matrix, BT.709 tags."""
    scale = f'scale={pre}:{BT709}' if pre else f'scale={BT709}'
    return f'{scale},format=yuv420p,{TAGS}'

def _encoder_args(master: bool):
    if master:
        return ['-c:v', 'libx264rgb', '-qp', '0', '-preset', 'veryfast', '-pix_fmt', 'rgb24']
    return ['-vf', yuv709(), '-c:v', 'libx264', '-preset', 'fast', '-crf', '17', *TAG_FLAGS]

def _samples(v):
    return v if v in (None, 'auto') else int(v)

def _chunk(a: int, b: int, out: str, master: bool, ffmpeg: str, samples=1, shutter=0.2, tol=3.0):
    film = _FILM
    W, H, fps = (film.p.W, film.p.H, film.p.FPS)
    cmd = [ffmpeg, '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-', '-an', *_encoder_args(master), '-threads', '2', out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    hist: dict[int, int] = {}
    for n in range(a, b):
        proc.stdin.write(film.frame(n, samples, shutter, tol).tobytes())
        hist[film.last_samples] = hist.get(film.last_samples, 0) + 1
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError(f'ffmpeg failed on chunk {a}-{b}')
    return (out, hist)

def resolve(project_dir, a, b):
    """(t0, t1) from seconds or shot names."""

    def num(x):
        try:
            return float(x)
        except (TypeError, ValueError):
            return None
    t0, t1 = (num(a), num(b))
    if t0 is not None and t1 is not None:
        return (t0, t1)
    shots = {s.name: s for s in load_film(project_dir).shots}
    try:
        return (t0 if t0 is not None else shots[a].start, t1 if t1 is not None else shots[b].end)
    except KeyError as e:
        raise SystemExit(f'unknown shot {e}; shots: {', '.join(shots)}')

def render(project_dir, t0, t1, out: str, workers: int=8, master: bool=False, audio: bool=True, samples=1, shutter: float=0.2, tol: float=3.0):
    p = load(project_dir)
    t0, t1 = resolve(project_dir, t0, t1)
    ffmpeg = p.tool('ffmpeg', 'ffmpeg')
    n0, n1 = (int(round(t0 * p.FPS)), int(round(t1 * p.FPS)))
    if n1 <= n0:
        raise SystemExit(f'render: empty range {t0}-{t1} s (t1 must be later than t0)')
    out = Path(out).resolve()
    seg = out.parent / f'_segments_{out.stem}'
    # Render segments are retained; no automatic deletion.
    seg.mkdir(parents=True, exist_ok=False)
    k = max(1, min(workers * 2, n1 - n0))
    bounds = [n0 + (n1 - n0) * i // k for i in range(k + 1)]
    jobs = [(bounds[i], bounds[i + 1], str(seg / f'seg_{i:03d}.mp4'), master, ffmpeg, samples, shutter, tol) for i in range(k) if bounds[i + 1] > bounds[i]]
    started = time.time()
    with ProcessPoolExecutor(max_workers=workers, initializer=_init, initargs=(str(p.root),)) as ex:
        done = list(ex.map(_chunk, *zip(*jobs)))
    parts = [x for x, _ in done]
    hist: dict[int, int] = {}
    for _, h in done:
        for c, v in h.items():
            hist[c] = hist.get(c, 0) + v
    lst = seg / 'list.txt'
    lst.write_text(''.join((f"file '{Path(x).as_posix()}'\n" for x in parts)), encoding='utf-8')
    cmd = [ffmpeg, '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', str(lst)]
    if audio and p.audio.exists():
        dur = f'{(n1 - n0) / p.FPS:.4f}'
        cmd += ['-ss', f'{n0 / p.FPS:.4f}', '-t', dur, '-i', str(p.audio), '-map', '0:v', '-map', '1:a', '-af', f'apad=whole_dur={dur}', '-c:a', 'aac', '-b:a', '320k' if master else '192k']
    cmd += ['-c:v', 'copy', '-movflags', '+faststart', str(out)]
    subprocess.run(cmd, check=True)
    # Render segments are retained; no automatic deletion.
    print(f'{out.name}: {n1 - n0} frames in {time.time() - started:.1f} s ({workers} workers)')
    if samples not in (1, None):
        print('sub-frames per frame (count:frames):', ' '.join((f'{c}:{v}' for c, v in sorted(hist.items()))))

def stills(project_dir, times, out_dir='stills', samples=1, shutter=0.2, tol=3.0):
    film = load_film(project_dir)
    out = film.p.path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for t in times:
        n = int(round(t * film.p.FPS))
        film.frame(n, samples, shutter, tol).save(out / f'{t:07.3f}.png')
        if samples not in (1, None):
            print(f't={t}: {film.last_samples} sub-frames')
    print(f'{len(times)} stills -> {out}')

def perf(project_dir, t0, t1, samples=1, shutter=0.2, tol=3.0):
    """ms per frame by shot (single process: multiply throughput by the worker count)."""
    t0, t1 = resolve(project_dir, t0, t1)
    film = load_film(project_dir)
    fps = film.p.FPS
    by_shot: dict[str, list] = {}
    hist: dict[int, int] = {}
    for n in range(int(round(t0 * fps)), int(round(t1 * fps))):
        a = time.perf_counter()
        film.frame(n, samples, shutter, tol)
        ms = (time.perf_counter() - a) * 1000
        by_shot.setdefault(film.shot_at(n / fps).name, []).append(ms)
        hist[film.last_samples] = hist.get(film.last_samples, 0) + 1
    for name, v in by_shot.items():
        v.sort()
        print(f'{name:>16}: {len(v):4d} frames  avg {sum(v) / len(v):7.1f} ms  p50 {v[len(v) // 2]:7.1f}  p95 {v[int(len(v) * 0.95)]:7.1f}  max {v[-1]:7.1f}')
    print('sub-frames (count:frames):', ' '.join((f'{c}:{v}' for c, v in sorted(hist.items()))))

def strips(project_dir, t0, t1, out_dir='strips'):
    t0, t1 = resolve(project_dir, t0, t1)
    film = load_film(project_dir)
    out = film.p.path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    font = film.p.font(14, 'bold')
    report = []
    for i, s in enumerate(film.shots[1:], 1):
        if not t0 <= s.start < t1:
            continue
        cut = film.cuts.get(s.name)
        tiles = []
        cut_n = int(round(s.start * film.p.FPS))
        for k in range(15):
            fn = int(round((s.start - 0.6 + k / 12) * film.p.FPS))
            if k == 7:
                fn = cut_n
            im = film.frame(fn).resize((384, 216), Image.BILINEAR)
            d = ImageDraw.Draw(im)
            d.text((6, 4), f'{fn / film.p.FPS:7.3f}{('  CUT' if k == 7 else '')}', font=font, fill=(255, 220, 90) if k == 7 else (230, 230, 230))
            tiles.append(im)
        sheet = Image.new('RGB', (384 * 5, 216 * 3))
        for k, im in enumerate(tiles):
            sheet.paste(im, (k % 5 * 384, k // 5 * 216))
        name = f'cut_{i:02d}_{s.start:07.3f}_{film.shots[i - 1].name}__{s.name}.png'
        sheet.save(out / name)
        report.append({'cut': i, 't': s.start, 'out': film.shots[i - 1].name, 'in': s.name, 'verb': getattr(cut, 'verb', 'HARD'), 'why': getattr(cut, 'why', ''), 'strip': name})
    (out / 'cuts.json').write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'{len(report)} strips -> {out}')

def video_seconds(p, src: str) -> float:
    """Length of the first video stream (ffprobe; the container's length if the stream has none)."""
    out = subprocess.run([p.tool('ffprobe', 'ffprobe'), '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=duration:format=duration', '-of', 'json', src], check=True, capture_output=True, text=True).stdout
    info = json.loads(out)
    for d in [s.get('duration') for s in info.get('streams', [])] + [info.get('format', {}).get('duration')]:
        try:
            return float(d)
        except (TypeError, ValueError):
            pass
    raise SystemExit(f'upscale: no duration in {src}')

def upscale(project_dir, src: str, dst: str, scale: int=3, mixes=(), codec: str | None=None, bitrate: str | None=None):
    p = load(project_dir)
    up = p.cfg['video'].get('upload', {})
    scale = scale or up.get('scale', 3)
    codec = codec or up.get('codec', 'hevc_nvenc')
    bitrate = bitrate or up.get('bitrate', '23M')
    ffmpeg = p.tool('ffmpeg_nvenc', p.tool('ffmpeg', 'ffmpeg')) if 'nvenc' in codec else p.tool('ffmpeg', 'ffmpeg')
    end = f'{video_seconds(p, src):.6f}'
    cmd = [ffmpeg, '-y', '-v', 'error', '-i', src, '-i', str(p.audio)]
    filt = ['[0:v]' + yuv709(f'iw*{scale}:ih*{scale}:flags=neighbor') + '[v]', f'[1:a]apad=whole_dur={end}[s]']
    labels = []
    for j, m in enumerate(mixes):
        path, at = m.rsplit('@', 1)
        cmd += ['-i', path]
        ms = int(float(at) * 1000)
        filt.append(f'[{j + 2}:a]aresample=44100,adelay={ms}|{ms}[m{j}]')
        labels.append(f'[m{j}]')
    if labels:
        filt.append(f'[s]{''.join(labels)}amix=inputs={len(labels) + 1}:duration=first:normalize=0,atrim=end={end}[a]')
    else:
        filt.append(f'[s]atrim=end={end}[a]')
    cmd += ['-filter_complex', ';'.join(filt), '-map', '[v]', '-map', '[a]']
    if 'nvenc' in codec:
        cmd += ['-c:v', codec, '-rc', 'vbr', '-b:v', bitrate, '-maxrate', '30M', '-bufsize', '46M', '-preset', 'p7']
    elif codec == 'libx265':
        cmd += ['-c:v', codec, '-preset', 'medium', '-crf', '16', '-tag:v', 'hvc1', '-color_range', 'tv']
    else:
        cmd += ['-c:v', codec, '-crf', '16', '-preset', 'slow']
    cmd += [*TAG_FLAGS, '-c:a', 'aac', '-b:a', up.get('audio_bitrate', '320k'), '-movflags', '+faststart', dst]
    subprocess.run(cmd, check=True)
    print(f'{dst}: x{scale} {codec}, {float(end):.3f} s')

def small(project_dir, src: str, dst: str, width: int=960):
    p = load(project_dir)
    subprocess.run([p.tool('ffmpeg', 'ffmpeg'), '-y', '-v', 'error', '-i', src, '-vf', yuv709(f'{width}:-2'), '-c:v', 'libx264', '-crf', '26', '-preset', 'fast', *TAG_FLAGS, '-c:a', 'aac', '-b:a', '128k', dst], check=True)
    print(f'{dst}: {width} wide')

def main(argv=None):
    ap = argparse.ArgumentParser(prog='tuikit.render')
    ap.add_argument('project')
    sub = ap.add_subparsers(dest='cmd', required=True)

    def sampling(x):
        x.add_argument('--samples', default='1', help='sub-frames per frame: N or auto (motion blur)')
        x.add_argument('--shutter', type=float, default=0.2, help='fraction of the frame time')
        x.add_argument('--tol', type=float, default=3.0, help='auto: stop below this many 8-bit levels')
    s = sub.add_parser('stills')
    s.add_argument('times', nargs='+', type=float)
    s.add_argument('--out', default='stills')
    sampling(s)
    r = sub.add_parser('render')
    r.add_argument('t0')
    r.add_argument('t1')
    r.add_argument('out')
    r.add_argument('--workers', type=int, default=max(1, (os.cpu_count() or 2) // 2))
    r.add_argument('--master', action='store_true')
    r.add_argument('--no-audio', action='store_true')
    sampling(r)
    st = sub.add_parser('strips')
    st.add_argument('t0')
    st.add_argument('t1')
    st.add_argument('--out', default='strips')
    pf = sub.add_parser('perf')
    pf.add_argument('t0')
    pf.add_argument('t1')
    sampling(pf)
    u = sub.add_parser('upscale')
    u.add_argument('src')
    u.add_argument('dst')
    u.add_argument('--scale', type=int, default=0)
    u.add_argument('--mix', action='append', default=[])
    u.add_argument('--codec')
    u.add_argument('--bitrate')
    u.add_argument('--cpu', dest='codec', action='store_const', const='libx265', help='libx265 on the CPU, no GPU')
    sm = sub.add_parser('small')
    sm.add_argument('src')
    sm.add_argument('dst')
    sm.add_argument('--width', type=int, default=960)
    a = ap.parse_args(argv)
    if a.cmd == 'stills':
        stills(a.project, a.times, a.out, _samples(a.samples), a.shutter, a.tol)
    elif a.cmd == 'render':
        render(a.project, a.t0, a.t1, a.out, a.workers, a.master, not a.no_audio, _samples(a.samples), a.shutter, a.tol)
    elif a.cmd == 'strips':
        strips(a.project, a.t0, a.t1, a.out)
    elif a.cmd == 'perf':
        perf(a.project, a.t0, a.t1, _samples(a.samples), a.shutter, a.tol)
    elif a.cmd == 'upscale':
        upscale(a.project, a.src, a.dst, a.scale, a.mix, a.codec, a.bitrate)
    elif a.cmd == 'small':
        small(a.project, a.src, a.dst, a.width)
if __name__ == '__main__':
    main()
