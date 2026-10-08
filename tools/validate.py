"""Fail early instead of silently drawing a frame with missing UI assets."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def pages(start,end):
    missing=[]
    for recipe in json.loads((ROOT/'data/page_recipes.json').read_text('utf8')):
        folder=ROOT/'film/ui'/recipe['out_dir']
        for n,t in recipe['frames']:
            if start<=t<end and not (folder/f'{n:05d}.png').is_file():
                missing.append(f"{recipe['out_dir']}/{n:05d}.png")
    if missing:
        raise SystemExit(f'{len(missing)} UI frames missing; run build.py pages first. First: {missing[0]}')
    if not (ROOT/'film/timing/words.json').is_file():
        raise SystemExit('Missing local lyric timing; run build.py lyrics first.')
