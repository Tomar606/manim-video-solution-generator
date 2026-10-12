// POL-C3-LA-02: the one map plate. Central Himalaya and the Ganga plain, in two inks.
//
//   node work/pol-c3-la-02/design/map.mjs      -> assets/map.png (960x720) + assets/map.json
//
// What is on it, and what is deliberately not:
//   * RELIEF is Natural Earth's 10m shaded relief (grayscale hillshade), resampled
//     pixel by pixel through the same d3-geo projection the rivers are drawn with,
//     so tone and line cannot drift apart. It is printed as ONE blue ink: shadowed
//     slopes carry ink, lit slopes are left as paper, and a tone of local
//     ruggedness sits under both, so the darker the plate the steeper the ground.
//     The tone is then laid in a few flat tints, the way a screen print is.
//     The plain has no relief and is therefore bare paper.
//   * RIVERS are Natural Earth's 10m centrelines. Fine blue lines, cased in paper
//     so they still read where they cross the mountain tone.
//   * NO BORDERS OF ANY KIND. No country, admin or boundary layer is loaded, and
//     no coastline is stroked. NO TEXT either: नेपाल and भारत are typeset later,
//     at the anchors this file writes to map.json.
//
// Drawing only. The two data files it reads were cut by map_prep.py (a one-off).
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';
import { renderStills } from '../../../tools/reel/layers.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '../../..');
const ASSETS = path.join(HERE, '../assets');
const DATA = path.join(ASSETS, 'data');
const VENDOR = path.join(ROOT, 'tools/reel/vendor');
const look = JSON.parse(fs.readFileSync(path.join(HERE, '../look.json'), 'utf8'));

const SIZE = [960, 720];
const RELIEF = { file: 'relief_sr_72-95E_19-36N.png', lon0: 72, lat1: 36, ppd: 45 };
const RIVERS = 'rivers_72-95E_19-36N.geojson';
// Mercator, 64 px per degree of longitude: 15 degrees across the 960.
const PROJ = { name: 'geoMercator', scale: 64 * 180 / Math.PI, center: [83.25, 27.6], translate: [SIZE[0] / 2, SIZE[1] / 2] };
// india: the brief's 81E 25.5N lands on the Yamuna a few km above the Sangam, with the Ganga
// through the same word. One degree south-west is the nearest open paper (measured on the plate).
const PLACES = { nepal: [84.0, 28.3], india: [80.1, 24.6], kathmandu: [85.32, 27.71], delhi: [77.21, 28.61] };
const ASKED = { india: [81.0, 25.5] };
// Stroke width by river. Names are Natural Earth's; "Sapt" is the Sapt Kosi, and
// Maquan + Yarlung are the Tsangpo, i.e. the Brahmaputra above the gorge.
const WIDTH = { Ganges: 3.0, Brahmaputra: 2.8, Yarlung: 2.0, Maquan: 1.6, Yamuna: 2.2, 'Ghäghara': 2.2, Gandak: 2.2, Sapt: 2.2 };
const OTHER = 1.15;
// Below this latitude the Ganges feature is its delta: a fan of distributaries, drawn fine.
const DELTA = { name: 'Ganges', south_of: 23.8, width: 1.3 };
// Ink: 0 = continuous tone, N = N flat tints with a soft edge between them.
const TONES = Number(process.env.MAP_TONES ?? 5), EDGE = 0.16, INKMAX = 0.9;

const d3src = ['d3-array.min.js', 'd3-geo.min.js'].map(f => fs.readFileSync(path.join(VENDOR, f), 'utf8'));
const rivers = fs.readFileSync(path.join(DATA, RIVERS), 'utf8');
const relief = fs.readFileSync(path.join(DATA, RELIEF.file)).toString('base64');

const html = `<!doctype html><html><head><meta charset="utf-8">
<script>${d3src[0]}</script><script>${d3src[1]}</script>
<style>
html,body{margin:0;background:${look.paper}}
#st{position:relative;width:${SIZE[0]}px;height:${SIZE[1]}px;overflow:hidden;background:${look.paper}}
#st canvas,#st svg{position:absolute;left:0;top:0}
</style></head><body>
<div id="st"><canvas id="c" width="${SIZE[0]}" height="${SIZE[1]}"></canvas><svg id="s" width="${SIZE[0]}" height="${SIZE[1]}"></svg></div>
<script>
const W=${SIZE[0]}, H=${SIZE[1]}, P=${JSON.stringify(PROJ)}, R=${JSON.stringify(RELIEF)};
const PAPER=${JSON.stringify(look.paper)}, BLUE=${JSON.stringify(look.blue)};
const RIVERS=${rivers}, WIDTH=${JSON.stringify(WIDTH)}, OTHER=${OTHER}, DELTA=${JSON.stringify(DELTA)};
const TONES=${TONES}, EDGE=${EDGE}, INKMAX=${INKMAX};
const proj=d3.geoMercator().scale(P.scale).center(P.center).translate(P.translate);
const rgb=h=>[1,3,5].map(i=>parseInt(h.slice(i,i+2),16));

// three box passes: near enough a gaussian of that radius
function blur(a,r){
  let src=Float32Array.from(a), dst=new Float32Array(a.length);
  for(let pass=0;pass<3;pass++){
    for(let y=0;y<H;y++){let s=0; const o=y*W;
      for(let x=-r;x<=r;x++) s+=src[o+Math.min(W-1,Math.max(0,x))];
      for(let x=0;x<W;x++){dst[o+x]=s/(2*r+1); s+=src[o+Math.min(W-1,x+r+1)]-src[o+Math.max(0,x-r)];}}
    [src,dst]=[dst,src];
    for(let x=0;x<W;x++){let s=0;
      for(let y=-r;y<=r;y++) s+=src[Math.min(H-1,Math.max(0,y))*W+x];
      for(let y=0;y<H;y++){dst[y*W+x]=s/(2*r+1); s+=src[Math.min(H-1,y+r+1)*W+x]-src[Math.max(0,y-r)*W+x];}}
    [src,dst]=[dst,src];
  }
  return src;
}
const step=(a,b,v)=>{const t=Math.min(1,Math.max(0,(v-a)/(b-a))); return t*t*(3-2*t);};
const pct=(a,q)=>{const s=Float32Array.from(a).sort(); return s[Math.floor(q*(s.length-1))];};
// a fixed grain, so the plate is the same picture on every run
const grain=(x,y)=>{let h=Math.imul(x,374761393)^Math.imul(y,668265263); h=Math.imul(h^(h>>>13),1274126177); return ((h^(h>>>16))>>>0)/4294967295-.5;};

window.frameKey=()=>'map';
window.render=()=>{};
window.READY=new Promise((done,fail)=>{const img=new Image(); img.onerror=fail; img.onload=()=>{
  // ---- the hillshade, resampled through the projection (bilinear)
  const sc=document.createElement('canvas'); sc.width=img.width; sc.height=img.height;
  const sx=sc.getContext('2d',{willReadFrequently:true}); sx.drawImage(img,0,0);
  const S=sx.getImageData(0,0,img.width,img.height).data, IW=img.width, IH=img.height;
  const hist=new Uint32Array(256); for(let i=0;i<S.length;i+=4) hist[S[i]]++;
  let flat=0; for(let v=1;v<256;v++) if(hist[v]>hist[flat]) flat=v;      // level ground = the commonest gray
  flat/=255;
  const sh=new Float32Array(W*H);
  for(let y=0;y<H;y++) for(let x=0;x<W;x++){
    const ll=proj.invert([x+.5,y+.5]);
    let fx=(ll[0]-R.lon0)*R.ppd-.5, fy=(R.lat1-ll[1])*R.ppd-.5;
    fx=Math.max(0,Math.min(IW-1.001,fx)); fy=Math.max(0,Math.min(IH-1.001,fy));
    const x0=fx|0,y0=fy|0,ax=fx-x0,ay=fy-y0,i=(y0*IW+x0)*4,w=IW*4;
    sh[y*W+x]=((S[i]*(1-ax)+S[i+4]*ax)*(1-ay)+(S[i+w]*(1-ax)+S[i+w+4]*ax)*ay)/255;
  }
  // ---- one ink: shadow + ruggedness, lit slopes knocked out to paper
  const dev=sh.map(v=>Math.abs(v-flat));
  const rug=blur(dev,4), land=blur(rug,14);
  const nS=pct(sh.map(v=>Math.max(0,flat-v)),.995)||1, nR=pct(rug,.99)||1, nL=pct(land,.99)||1;
  const ctx=document.getElementById('c').getContext('2d'), out=ctx.createImageData(W,H), O=out.data;
  const pa=rgb(PAPER), bl=rgb(BLUE);
  for(let y=0;y<H;y++) for(let x=0;x<W;x++){
    const j=y*W+x, d=sh[j]-flat;
    const shadow=Math.min(1,Math.max(0,-d)/nS), lit=Math.min(1,Math.max(0,d)/(1-flat));
    const r=Math.min(1,rug[j]/nR);
    const l=Math.min(1,land[j]/nL)*step(.05,.25,r);  // gated, or the range wears a halo out over the plain
    let k=.78*Math.pow(shadow,.8)+.34*r+.20*l-.55*lit*r;
    k=Math.max(0,k-.035)/(1-.035);                 // the plain stays bare paper
    if(TONES){const q=k*TONES, f=Math.floor(q); k=(f+step(.5-EDGE,.5+EDGE,q-f))/TONES;}   // flat tints, as a screen print lays them
    k=Math.min(INKMAX,k)*(1+.10*grain(x,y));
    k=Math.max(0,Math.min(1,k));
    const g=2.2*grain(x+7919,y+104729);            // paper tooth
    for(let c=0;c<3;c++) O[j*4+c]=pa[c]+(bl[c]-pa[c])*k+g;
    O[j*4+3]=255;
  }
  ctx.putImageData(out,0,0);

  // ---- rivers
  const path=d3.geoPath(proj);
  const fs=RIVERS.features.flatMap(f=>f.geometry.coordinates.map(ln=>{
    const n=f.properties.name, delta=n===DELTA.name&&Math.min(...ln.map(p=>p[1]))<DELTA.south_of;
    return {d:path({type:'LineString',coordinates:ln}), w:delta?DELTA.width:(WIDTH[n]||OTHER)};
  })).filter(f=>f.d).sort((a,b)=>a.w-b.w);
  const line=(f,stroke,w,o)=>'<path d="'+f.d+'" fill="none" stroke="'+stroke+'" stroke-width="'+w+'" stroke-opacity="'+o+'" stroke-linecap="round" stroke-linejoin="round"/>';
  document.getElementById('s').innerHTML=
    fs.map(f=>line(f,PAPER,f.w+2.8,.85)).join('')+fs.map(f=>line(f,BLUE,f.w,f.w>OTHER?1:.85)).join('');
  done();
}; img.src='data:image/png;base64,${relief}';});
</script></body></html>`;

const [file] = await renderStills({ html, outDir: ASSETS, times: [0], layers: ['map'], size: SIZE });
fs.renameSync(file, path.join(ASSETS, 'map.png'));

// ---- the same d3-geo, in Node, for the numbers other code needs
const ctx = vm.createContext({});
for (const s of d3src) vm.runInContext(s, ctx);
const proj = ctx.d3.geoMercator().scale(PROJ.scale).center(PROJ.center).translate(PROJ.translate);
const px = ll => proj(ll).map(v => Math.round(v));
const deg = xy => proj.invert(xy).map(v => +v.toFixed(3));
const NE = 'public domain (Natural Earth)';
fs.writeFileSync(path.join(ASSETS, 'map.json'), JSON.stringify({
  size: SIZE,
  projection: `Mercator (d3.geoMercator, spherical), north up; scale ${PROJ.scale.toFixed(3)} = 64 px per degree of longitude, `
    + `center [${PROJ.center}] at pixel [${PROJ.translate}]`,
  projection_d3: PROJ,
  bounds: [deg([0, SIZE[1]]), deg([SIZE[0], 0])],
  sources: [
    { file: `work/pol-c3-la-02/assets/data/${RELIEF.file}`, licence: NE,
      what: 'Natural Earth 10m Shaded Relief, low-res edition (SR_LR.tif, v2.0.0, 16200x8100, 45 px/degree), grayscale hillshade cropped to 72-95E 19-36N' },
    { file: `work/pol-c3-la-02/assets/data/${RIVERS}`, licence: NE,
      what: 'Natural Earth 10m rivers + lake centerlines (ne_10m_rivers_lake_centerlines), cut to the same box' },
  ],
  anchors: Object.fromEntries(Object.entries(PLACES).map(([k, ll]) => [k, px(ll)])),
  anchors_lonlat: PLACES,
  anchors_as_asked: Object.fromEntries(Object.entries(ASKED).map(([k, ll]) => [k, px(ll)])),
  note: 'Relief is real data, not drawn: the blue tone is the Natural Earth hillshade (shadowed slopes inked, lit slopes left as paper) '
    + 'plus a tone of local ruggedness measured from the same hillshade, so darker means steeper. No elevation model was used, so tone is '
    + 'not height: the high Himalaya is darkest because it is the most rugged ground, and flat ground (the plain, and any sea) is bare paper. '
    + 'Rivers and relief only: no country, admin or boundary layer was loaded, no coastline is stroked, and there is no text. '
    + (TONES ? `The tone is laid in ${TONES} flat tints, as a screen print would be. ` : '')
    + 'anchors.india is at 80.1E 24.6N, not the 81E 25.5N first asked for: that point (anchors_as_asked.india) sits on the Yamuna just above '
    + 'its confluence with the Ganga, so both rivers would run through the word; the anchor given is the nearest open paper, just south of the Yamuna. '
    + 'anchors.nepal is on the darkest part of the plate, so a label there needs a paper-coloured face or a paper casing. '
    + 'kathmandu and delhi are end points for arrows and are not marked on the plate. Drawn by design/map.mjs; data cut once by design/map_prep.py.',
}, null, 1) + '\n');
console.log('wrote', path.join(ASSETS, 'map.png'), 'and map.json');
