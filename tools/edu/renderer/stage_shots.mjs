// Render one still per animation STAGE, so the sequence can be judged before
// committing to a render.
import { chromium } from 'playwright';
import { createServer } from 'http';
import { readFile } from 'fs/promises';
import { extname, join } from 'path';
const ROOT = process.cwd();
const T = {'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json',
  '.svg':'image/svg+xml','.png':'image/png','.woff2':'font/woff2','.woff':'font/woff','.ttf':'font/ttf'};
const server = createServer(async (rq,rs)=>{ try{
  const p = join(ROOT, decodeURIComponent(rq.url.split('?')[0]));
  const b = await readFile(p);
  rs.writeHead(200,{'Content-Type':T[extname(p)]||'application/octet-stream'}); rs.end(b);
}catch{ rs.writeHead(404); rs.end('nf'); }});
await new Promise(r=>server.listen(0,r));
const port = server.address().port;
const browser = await chromium.launch();
const specs = JSON.parse(await readFile('spec/segments.json','utf8'));
for (let i=0;i<specs.length;i++){
  const page = await browser.newPage({viewport:{width:1080,height:1920}});
  await page.goto(`http://localhost:${port}/renderer/index.html?headless=1&seg=${i}`,{waitUntil:'networkidle'});
  await page.waitForFunction(()=>window.READY===true);
  await page.evaluate(bg=>{ const f=document.getElementById('frame');
    f.style.background=`#000 url('../${bg}') center/cover no-repeat`;
    document.body.style.background='#000'; }, 'assets/chalk-background.png');
  await page.evaluate(t=>window.RENDER.setTime(t), specs[i].duration - 0.3);
  await page.waitForTimeout(400);
  await page.screenshot({path:`out/stage-${i+1}.png`});
  await page.close();
}
await browser.close(); server.close(); process.exit(0);
