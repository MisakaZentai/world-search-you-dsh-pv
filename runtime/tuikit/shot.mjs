// Deterministic, local-only page screenshots. No server or model service is used.
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL, fileURLToPath} from 'node:url';

const root=process.env.PLAYWRIGHT_ROOT || path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const require=createRequire(path.join(root,'package.json'));
const {chromium}=require('playwright');
const file=path.resolve(process.argv[2]);
const base=path.dirname(file);
const spec=JSON.parse(fs.readFileSync(file,'utf8'));
const only=new Set(process.argv.slice(3).map(Number));
const outDir=path.resolve(base,spec.out_dir || 'pane_frames');
fs.mkdirSync(outDir,{recursive:true});
const browser=await chromium.launch({args:['--disable-gpu']});
let count=0;
try {
  const page=await browser.newPage({viewport:spec.viewport,deviceScaleFactor:spec.scale || 1});
  await page.route(/^https?:\/\//,route=>route.abort());
  const errors=[];
  page.on('requestfailed',request=>errors.push(request.url()));
  page.on('pageerror',error=>errors.push(error.message));
  await page.goto(pathToFileURL(path.resolve(base,spec.page)).href);
  await page.evaluate(()=>document.fonts.ready);
  let first=true;
  for (const f of spec.frames) {
    if (only.size && !only.has(f.n)) continue;
    await page.evaluate(({body,sheets,all,t})=>{
      if(sheets) for(const id of all) {const el=document.getElementById(id);if(el)el.disabled=!sheets.includes(id);}
      const app=document.getElementById('app');
      if(app.dataset.body!==body){app.innerHTML=body;app.dataset.body=body;}
      for(const a of document.getAnimations()){
        const timing=a.effect.getComputedTiming();
        const dur=typeof timing.duration==='number' && timing.duration>0 ? timing.duration : 1000;
        a.pause();a.currentTime=timing.iterations===Infinity ? (t*1000)%dur : dur;
      }
    },{body:f.body,sheets:f.sheets || null,all:spec.all_sheets || [],t:f.t});
    if(first){await page.waitForTimeout(150);first=false;}
    await page.evaluate(()=>Promise.all([...document.images].map(i=>i.decode())));
    if(errors.length)throw new Error(`Page resource failure: ${errors.join(', ')}`);
    await page.screenshot({path:path.join(outDir,String(f.n).padStart(5,'0')+'.png'),omitBackground:!!spec.transparent});
    count++;
  }
} finally {await browser.close();}
console.log(`${count} frames -> ${outDir}`);
