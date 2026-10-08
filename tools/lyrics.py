"""Rebuild word timing from a local LRC or LRCLIB; validate every line and word before writing."""
from __future__ import annotations
import hashlib, json, re, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def digest(text): return hashlib.sha256(text.encode('utf8')).hexdigest()
def norm(text): return ' '.join(text.replace('’', "'").split())

def build(fetch=False):
    src = ROOT / 'input/lyrics.lrc'
    if not src.exists():
        if not fetch:
            raise SystemExit('Missing input/lyrics.lrc. Supply an LRC, or run build.py lyrics --fetch.')
        meta=json.loads((ROOT/'data/input_fingerprint.json').read_text('utf8'))
        request=urllib.request.Request(f"https://lrclib.net/api/get/{meta['lrclib_id']}",headers={'User-Agent':'PV02-r21-lyric-builder/1.0'})
        with urllib.request.urlopen(request,timeout=30) as response:
            data=json.load(response)
        text=data.get('syncedLyrics')
        if not text:raise SystemExit('LRCLIB returned no synced lyrics; supply a local LRC.')
        src.parent.mkdir(exist_ok=True)
        src.write_text(text,encoding='utf8')
    candidates={}
    for raw in src.read_text('utf-8-sig').splitlines():
        line=norm(re.sub(r'^(?:\[[^\]]*\])+','',raw))
        if line:candidates[digest(line)]=line
    times=json.loads((ROOT/'data/word_times.json').read_text('utf8'))
    lines=[]; errors=[]
    for spec in times['lines']:
        line=candidates.get(spec['sha256'])
        if line is None:
            errors.append(f"line {spec['id']}: text fingerprint mismatch")
            continue
        tokens=line.split()
        if [digest(w) for w in tokens] != spec['word_hashes']:
            errors.append(f"line {spec['id']}: word fingerprint mismatch")
            continue
        item={k:spec[k] for k in ['id','start','end','display_end'] if k in spec}
        item['text']=line
        item['words']=[dict(w,text=t) for w,t in zip(spec['words'],tokens)]
        lines.append(item)
    if errors:raise SystemExit('\n'.join(errors)+'\nNo timing file was written.')
    result={'schema_version':2,'status':'aligned','time_unit':'seconds','duration':times['duration'],
            'lines':lines,'words':[w for line in lines for w in line['words']]}
    dst=ROOT/'film/timing/words.json'
    dst.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    ids=ROOT/'input/subtitle_ids.json'
    if ids.exists():
        value=json.loads(ids.read_text('utf8'))
        if not isinstance(value.get('en'),dict) or not isinstance(value.get('zh'),dict):raise ValueError('Invalid subtitle IDs')
        (ROOT/'film/subs_ids.json').write_text(json.dumps(value,ensure_ascii=False),encoding='utf8')
    print(f"lyrics: {len(lines)} lines, {len(result['words'])} words verified")
