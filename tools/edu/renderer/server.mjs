import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const TYPES = { '.html':'text/html', '.js':'text/javascript', '.mjs':'text/javascript',
  '.css':'text/css', '.json':'application/json', '.svg':'image/svg+xml',
  '.woff2':'font/woff2', '.woff':'font/woff', '.ttf':'font/ttf', '.png':'image/png' };

export function serve(root, port = 0) {
  const s = http.createServer((req, res) => {
    const rel = decodeURIComponent(req.url.split('?')[0]).replace(/^\/+/, '');
    const file = path.join(root, rel || 'renderer/index.html');
    if (!file.startsWith(root)) { res.writeHead(403).end(); return; }
    fs.readFile(file, (err, buf) => {
      if (err) { res.writeHead(404).end('not found: ' + rel); return; }
      res.writeHead(200, { 'content-type': TYPES[path.extname(file)] || 'application/octet-stream',
                           'cache-control': 'no-store' });
      res.end(buf);
    });
  });
  return new Promise(r => s.listen(port, '127.0.0.1', () => r({ server: s, port: s.address().port })));
}

/* run directly:  node server.mjs   -> preview at http://localhost:5178/renderer/ */
const thisFile = fileURLToPath(import.meta.url);
if (process.argv[1] && path.resolve(process.argv[1]) === thisFile) {
  const root = path.dirname(thisFile);
  const { port } = await serve(root, 5178);
  console.log(`preview:  http://localhost:${port}/renderer/index.html`);
  console.log('scrub through each segment here BEFORE you render. This is the QC gate.');
}
