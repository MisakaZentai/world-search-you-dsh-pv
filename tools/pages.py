"""Regenerate the r21 UI panes, using the recorded frame ranges and original page functions."""
from __future__ import annotations
import concurrent.futures, lzma, importlib, json, os, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def build(workers=2, samples=False, from_source=False, start=0, end=None):
    recipes=json.loads((ROOT/'data/page_recipes.json').read_text('utf8'))
    ui=ROOT/'film/ui'
    jobs=[]
    for recipe in recipes:
        indices=recipe['frames']
        indices=[(n,t) for n,t in indices if start<=t and (end is None or t<end)]
        if not indices:continue
        if samples:
            indices=[indices[i] for i in sorted({0,len(indices)//2,len(indices)-1})]
        if from_source:
            fn=importlib.import_module(recipe['module']).body
            spec={k:v for k,v in recipe.items() if k not in ['name','module','frames']}
            spec['frames']=[{'n':n,'t':t,'body':fn(t)} for n,t in indices]
        else:
            spec=json.loads(lzma.decompress((ROOT/f"data/pages/{recipe['name']}.json.xz").read_bytes()))
            selected={n for n,t in indices}
            spec['frames']=[f for f in spec['frames'] if f['n'] in selected]
        path=ui/f"frames_release_{recipe['name']}.json"
        path.write_text(json.dumps(spec,ensure_ascii=False),encoding='utf8')
        jobs.append(path)
    def shot(path):
        subprocess.run(['node',str(ROOT/'runtime/tuikit/shot.mjs'),str(path)],check=True,cwd=ROOT)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(shot,jobs))
