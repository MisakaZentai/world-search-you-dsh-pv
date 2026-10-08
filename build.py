"""CPU build entry point for the r21 release. Run --help for individual steps."""
from __future__ import annotations
import argparse, hashlib, json, os, shutil, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def configure():
    data=json.loads((ROOT/'data/r21.json').read_text('utf8'))
    for key in list(os.environ):
        if key.startswith('DSH_'):os.environ.pop(key)
    os.environ.update(data['env'])
    os.environ['PYTHONUTF8']='1'
    os.environ['PYTHONDONTWRITEBYTECODE']='1'
    paths=[ROOT,ROOT/'runtime',ROOT/'film',ROOT/'film/ui']
    sys.path[:0]=[str(p) for p in paths]
    os.environ['PYTHONPATH']=os.pathsep.join(map(str,paths))
    os.environ['TUIKIT_ROOT']=str(ROOT/'runtime')
    sys.dont_write_bytecode=True
    return data

def check(require_song=True):
    from PIL import ImageFont
    import numpy, yaml
    missing=[name for name in ['node','ffmpeg','ffprobe'] if not shutil.which(name)]
    fonts=['consola.ttf','consolab.ttf','msyh.ttc','msyhbd.ttc','seguisb.ttf']
    for name in fonts:
        try:ImageFont.truetype('C:/Windows/Fonts/'+name,12)
        except OSError:missing.append('font '+name)
    if require_song:
        song=ROOT/'input/song.wav'
        meta=json.loads((ROOT/'data/input_fingerprint.json').read_text('utf8'))
        if not song.exists():missing.append('input/song.wav')
        elif hashlib.sha256(song.read_bytes()).hexdigest()!=meta['song_wav_sha256']:
            raise SystemExit('Song fingerprint mismatch. See input/README.md; do not silently use another master.')
    if missing:raise SystemExit('Missing: '+', '.join(missing))
    print('check: Python libraries, tools, fonts'+(' and song fingerprint' if require_song else '')+' OK')

def interval(args,data):
    start=args.start;end=data['end'] if args.end is None else args.end
    if not 0<=start<end<=data['end']:raise SystemExit('Invalid render interval')
    tag='film' if start==0 and end==data['end'] else f'sample_{start:g}_{end:g}'
    return start,end,tag

def render(args,data):
    from tools.validate import pages
    from tuikit.render import render as render_master
    out=ROOT/'out';out.mkdir(exist_ok=True)
    start,end,tag=interval(args,data)
    pages(start,end)
    master=out/f'{tag}_master.mp4'
    if master.exists():raise SystemExit(f'Refusing existing master: {master}')
    render_master(ROOT/'film',start,end,str(master),workers=args.workers,master=True,audio=False)
    encode(args,data)

def encode(args,data):
    check()
    start,end,tag=interval(args,data)
    master=ROOT/'out'/f'{tag}_master.mp4'
    if not master.is_file():raise SystemExit(f'Missing master: {master}')
    out=args.output_dir or ROOT/'out';out.mkdir(parents=True,exist_ok=True)
    duration=(round(end*24)-round(start*24))/24
    delay=data['chime_ms']-round(round(start*24)/24*1000)
    cmd=['ffmpeg','-n','-v','error','-i',str(master),'-ss',str(round(start*24)/24),'-i',str(ROOT/'input/song.wav')]
    mix=f'[1:a]aresample=44100,apad=whole_dur={duration},atrim=0:{duration},asetpts=PTS-STARTPTS[music]'
    if 0<=delay<duration*1000:
        cmd+=['-i',str(ROOT/'film/assets/audio/chime_g.wav')]
        mix+=f';[2:a]aresample=44100,adelay={delay}|{delay}[chime];[music][chime]amix=inputs=2:duration=first:normalize=0[a]'
    else:mix+=';[music]anull[a]'
    base=cmd+['-filter_complex',mix,'-map','0:v','-map','[a]','-t',str(duration),'-c:a','aac','-ar','44100','-b:a','320k',
       '-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-movflags','+faststart']
    color='out_color_matrix=bt709:out_range=tv,format=yuv420p,setparams=range=tv:colorspace=bt709:color_primaries=bt709:color_trc=bt709'
    subprocess.run(base+['-vf','scale=iw:ih:'+color,'-c:v','libx264','-crf','16',str(out/f'{tag}.mp4')],check=True)
    if args.four_k:
        subprocess.run(base+['-vf','scale=iw*3:ih*3:flags=neighbor:'+color,'-c:v','libx265','-preset','medium','-crf','16','-tag:v','hvc1',str(out/f'{tag}_4k.mp4')],check=True)
    print(f'encode: {tag}, {round(duration*24)} frames')

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('step',choices=['check','lyrics','pages','render','encode','all'])
    ap.add_argument('--fetch',action='store_true',help='Download missing LRC from LRCLIB')
    ap.add_argument('--workers',type=int,default=4)
    ap.add_argument('--page-workers',type=int,default=2)
    ap.add_argument('--4k',dest='four_k',action='store_true')
    ap.add_argument('--start',type=float,default=0)
    ap.add_argument('--end',type=float)
    ap.add_argument('--output-dir',type=Path,help='Encoded media destination; masters remain in out/')
    ap.add_argument('--samples',action='store_true',help='pages only: three screenshots per recipe')
    ap.add_argument('--from-source',action='store_true',help='Rebuild HTML from editable page code instead of the r21 snapshots')
    a=ap.parse_args()
    if min(a.workers,a.page_workers)<1:ap.error('worker counts must be positive')
    if a.samples and a.step!='pages':ap.error('--samples is only valid with pages')
    data=configure()
    if a.step in ['check','all']:check()
    if a.step in ['lyrics','all']:
        from tools.lyrics import build
        build(fetch=a.fetch)
    if a.step in ['pages','all']:
        from tools.pages import build
        build(workers=a.page_workers,samples=a.samples,from_source=a.from_source,start=a.start,end=a.end)
    if a.step in ['render','all']:render(a,data)
    if a.step=='encode':encode(a,data)

if __name__=='__main__':main()
