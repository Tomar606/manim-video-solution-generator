import { chromium } from 'playwright';
import { createServer } from 'http';
import { readFile } from 'fs/promises';
import { extname, join } from 'path';
const ROOT = process.cwd();
const TYPES = {'.html':'text/html','.js':'text/javascript','.css':'text/css',
  '.json':'application/json','.svg':'image/svg+xml','.png':'image/png','.woff2':'font/woff2'};
const server = createServer(async (req,res)=>{
  try{ const p = join(ROOT, decodeURIComponent(req.url.split('?')[0]));
    const b = await readFile(p);
    res.writeHead(200,{'Content-Type':TYPES[extname(p)]||'application/octet-stream'}); res.end(b);
  }catch(e){ res.writeHead(404); res.end('nf'); }
});
await new Promise(r=>server.listen(0,r));
const port = server.address().port;
const browser = await chromium.launch();
const page = await browser.newPage({viewport:{width:1080,height:1920}});
page.on('console', m => console.log('CONSOLE:', m.type(), m.text().slice(0,300)));
page.on('pageerror', e => console.log('PAGEERROR:', String(e).slice(0,400)));
await page.goto(`http://localhost:${port}/renderer/index.html?headless=1`, {waitUntil:'networkidle'});
await page.waitForTimeout(4000);
console.log('READY =', await page.evaluate(()=>window.READY));
await browser.close(); server.close(); process.exit(0);
