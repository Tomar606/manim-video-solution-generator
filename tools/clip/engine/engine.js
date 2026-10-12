/* ============================================================
   Arivihan Truth Layer — engine
   ONE RULE: the frame is a pure function of t.
   No requestAnimationFrame, no CSS transitions, no randomness.
   Same t  ->  same pixels, forever. That is what makes this
   pipeline auditable in a way a generative model can never be.
   ============================================================ */

const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const lerp  = (a, b, p) => a + (b - a) * p;
const easeOut     = p => 1 - Math.pow(1 - p, 3);
const easeOutBack = p => { const c=1.70158, c3=c+1; return 1 + c3*Math.pow(p-1,3) + c*Math.pow(p-1,2); };

/* Rate functions, borrowed from Manim's vocabulary. Put "ease" on any
   timeline action to pick one; the default stays easeOut so every existing
   spec renders exactly as before.
     smooth         S-curve, slow in and out  -> natural, the safe default
     rush_into      slow then fast            -> something leaving/being pulled
     rush_from      fast then slow            -> something arriving with weight
     linear         constant                  -> mechanical, current/flow
     there_and_back 0 -> 1 -> 0               -> emphasis without a state change  */
const EASE = {
  ease_out:       easeOut,
  smooth:         p => p * p * p * (p * (p * 6 - 15) + 10),
  linear:         p => p,
  rush_into:      p => p * p,
  rush_from:      p => 1 - (1 - p) * (1 - p),
  there_and_back: p => Math.sin(clamp(p, 0, 1) * Math.PI),
};
const easeFn = name => EASE[name] || easeOut;

/* Walk a chronological action list up to time t and return the state.
   Actions before t are fully applied; the one straddling t is
   interpolated; later ones do not exist yet. */
function stateAt(actions, t, initial) {
  const s = Object.assign({ opacity: 0, scale: 1, dx: 0, dy: 0, draw: 1, pulse: 0 }, initial);
  const list = [...(actions || [])].sort((a, b) => a.t - b.t);
  for (const a of list) {
    if (t <= a.t) break;
    const dur = a.dur ?? 0.45;
    const p   = clamp((t - a.t) / dur, 0, 1);
    const e   = easeFn(a.ease)(p);
    switch (a.action) {
      case 'fade_in':  s.opacity = lerp(s.opacity, 1, e); break;
      case 'fade_out': s.opacity = lerp(s.opacity, 0, e); break;
      case 'pop_in':
        s.opacity = lerp(s.opacity, 1, clamp(p / 0.45, 0, 1));
        s.scale   = lerp(0.86, 1, easeOutBack(p));
        break;
      case 'pop_out':
        s.opacity = lerp(s.opacity, 0, e);
        s.scale   = lerp(s.scale, 0.94, e);
        break;
      case 'move':
        s.dx = lerp(s.dx, a.to[0], e);
        s.dy = lerp(s.dy, a.to[1], e);
        break;
      case 'draw':
        // draw implies visibility. Without this an element whose only action
        // is `draw` keeps opacity 0 and never appears at all.
        s.draw = lerp(0, 1, e);
        s.opacity = Math.max(s.opacity, lerp(0, 1, clamp(p * 3, 0, 1)));
        break;
      case 'pulse': s.pulse = Math.sin(clamp(p,0,1) * Math.PI); break;
    }
  }
  return s;
}


/* A torn paper edge. Fixed vertices, not random: the frame must be a pure
   function of t, and a re-render must produce the same pixels. */
function tearPath() {
  const pts = [0,38, 46,26, 96,40, 152,22, 210,36, 268,18, 322,34, 384,20,
               440,38, 498,24, 556,40, 612,22, 668,36, 726,20, 780,34, 838,18,
               892,36, 948,22, 1004,38, 1052,24, 1080,34];
  let d = `M0,74 L0,${pts[1]}`;
  for (let i = 2; i < pts.length; i += 2) d += ` L${pts[i]},${pts[i + 1]}`;
  return d + ' L1080,74 Z';
}

/* ---------------- build the DOM once per segment ---------------- */

const $ = id => document.getElementById(id);
const SVGNS = 'http://www.w3.org/2000/svg';
let SEG = null, NODES = null;

function goldenize(text, golden) {
  // Wraps EXACTLY ONE occurrence of the golden word. Case-sensitive,
  // whole word only. If it is not found we fail loudly rather than
  // silently shipping a plain phrase.
  if (!golden) return escapeHTML(text);
  // Word boundaries must be Unicode-aware. JS `\b` is defined against [A-Za-z0-9_],
  // so it never fires beside a Devanagari letter or a subscript digit: `\bक्षारीय\b`
  // and `\bKMnO\u2084\b` both fail to match text that plainly contains them, and
  // goldenize then threw on every Hindi phrase. Letters, marks and numbers are the
  // boundary here, which behaves identically for Latin and Devanagari.
  const B = '[\\p{L}\\p{M}\\p{N}]';
  const re = new RegExp(`(?<!${B})(${golden.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})(?!${B})`, 'u');
  if (!re.test(text)) throw new Error(`golden word "${golden}" not found in phrase "${text}"`);
  let done = false;
  return escapeHTML(text).replace(re, m => done ? m : (done = true, `<span class="g">${m}</span>`));
}
const escapeHTML = s => s.replace(/[&<>]/g, c => ({ '&':'&amp;','<':'&lt;','>':'&gt;' }[c]));

async function build(seg) {
  SEG = seg;
  // Where the caption sits is a property of the SEGMENT, not of the theme:
  // low while the stage is busy, high when it is empty. Set here so the
  // whole frame is still a pure function of (spec, t).
  $('frame').classList.toggle('captop', seg.caption_pos === 'top');
  const stage = $('stage'), cap = $('caption'), eqWrap = $('eqWrap');
  stage.innerHTML = ''; cap.innerHTML = ''; $('eq').innerHTML = '';
  // The fit below writes INLINE top/height on #stage, and innerHTML does not
  // clear those. Left standing, one tall block lifts the stage for every
  // segment after it — the same shape of bug as the torn divider that
  // outlived its own panel.
  stage.style.top = ''; stage.style.height = '';
  // The arcs hang off #eqWrap, not #eq, so clearing #eq does not touch them
  // and every segment stacked the previous one's arrowheads on top of its
  // own. Scoped to DIRECT children and to our own class on purpose: KaTeX
  // builds \longrightarrow out of its own <svg> inside #eq, and a bare
  // querySelectorAll('svg') here deletes the arrow out of the equation.
  eqWrap.querySelectorAll(':scope > svg.eqarcs, :scope > .eqarc')
    .forEach(e => e.remove());
  NODES = { phrases: [], labels: [], svgEls: [], eq: null, arcs: [], arcSvg: null,
           blocks: [], veo: null };

  /* --- diagram: inline the SVG so we can address elements by id --- */
  if (seg.diagram && seg.diagram.asset) {
    const svgText = await (await fetch('../' + seg.diagram.asset)).text();
    stage.insertAdjacentHTML('afterbegin', svgText);
    const svg = stage.querySelector('svg');
    const carry = new Set(seg.diagram.carry_over || []);
    const tl = seg.diagram.timeline || [];
    const ids = new Set([...carry, ...tl.map(a => a.id)]);
    for (const id of ids) {
      const el = svg.querySelector('#' + CSS.escape(id));
      if (!el) throw new Error(`diagram id "${id}" missing in ${seg.diagram.asset}`);
      // support draw-on: a <path> dashes itself, a <g> dashes its stroked children
      const dashable = el.getTotalLength ? [el]
        : [...el.querySelectorAll('path,line,polyline,circle,ellipse,rect')];
      for (const d of dashable) {
        try {
          const L = d.getTotalLength ? d.getTotalLength() : 0;
          if (L > 0 && d.getAttribute('stroke')) d.style.strokeDasharray = L;
        } catch (e) {}
      }
      if (dashable.length && dashable[0].style.strokeDasharray) {
        el.style.strokeDasharray = dashable[0].style.strokeDasharray;
      }
      NODES.svgEls.push({ id, el,
        actions: tl.filter(a => a.id === id),
        initial: { opacity: carry.has(id) ? 1 : 0 } });
    }
    // anything not referenced is decorative scaffolding -> hide it
    svg.querySelectorAll('[data-optional]').forEach(el => {
      if (!ids.has(el.id)) el.style.display = 'none';
    });
  }

  /* --- labels --- */
  for (const l of (seg.labels || [])) {
    const d = document.createElement('div');
    d.className = 'lbl' + (l.accent ? ' accent' : '') + (l.center ? ' mid' : '') + (l.small ? ' sm' : '');
    d.textContent = l.text;
    d.style.left = (l.x * 1080) + 'px';
    d.style.top  = (l.y * parseFloat(getComputedStyle(document.documentElement)
                    .getPropertyValue('--stage-h'))) + 'px';
    stage.appendChild(d);
    // A label CARRIED from the previous segment (the same figure continuing)
    // is simply there from frame 0. Popping it in again at the boundary reads
    // as the figure blinking, because the DOM is rebuilt under it.
    NODES.labels.push({ el: d, carry: !!l.carry,
      actions: l.carry ? [...(l.t_out != null ? [{ action: 'fade_out', t: l.t_out, dur: 0.3 }] : [])] : [{ action: 'pop_in', t: l.t_in, dur: 0.4 },
                ...(l.t_out != null ? [{ action: 'fade_out', t: l.t_out, dur: 0.3 }] : [])] });
  }

  /* --- equation (KaTeX, deterministic; highlight = second render, cross-fade) --- */
  if (seg.equation) {
    const box = $('eq');
    // Make the wrapper visible BEFORE anything is measured. It is switched on
    // at the end of build(), and a getBoundingClientRect() inside a
    // display:none subtree returns 0x0 - so the fit below silently computed a
    // scale of 1 and the equation went off the frame anyway.
    eqWrap.style.display = 'flex';
    const mk = latex => { const s = document.createElement('span');
      s.style.position = 'absolute'; s.style.left = '50%'; s.style.top = '50%';
      s.style.transform = 'translate(-50%,-50%)';
      katex.render(latex, s, { displayMode: true, throwOnError: true,
                             trust: true, strict: false }); return s; };
    box.style.position = 'relative'; box.style.width = '940px'; box.style.height = '260px';
    const base = mk(seg.equation.latex); box.appendChild(base);
    // `highlight` may be ONE step (an object) or a LIST of them. The list is
    // what a summary ladder needs: five rows that fill in as they are named,
    // each step a complete re-render in which the rows not yet reached are
    // \phantom - so the block's geometry never moves and the fit below is
    // measured once for all of them. One highlight per segment would have
    // meant one DOM rebuild per row, and the whole list popping five times.
    const hiSpecs = seg.equation.highlight
      ? (Array.isArray(seg.equation.highlight) ? seg.equation.highlight
                                               : [seg.equation.highlight])
      : [];
    const his = hiSpecs.map(h => { const e = mk(h.latex); box.appendChild(e); return e; });
    const hi = his[0] || null;
    // Fit the equation to the box. A physics one-liner fits at 80px; a balanced
    // chemical equation does not, and ran off BOTH edges of the frame with its
    // first and last terms cut off. The factor is measured once at build time
    // from the widest of the two renders (base and highlight must not resize
    // when they cross-fade), so the frame stays a pure function of t.
    // document.fonts.ready alone is not enough: a face that has not been
    // ASKED for yet is not pending, so it resolves immediately and the
    // measurement is taken against a fallback. Upright \\mathrm chemistry
    // measured 30% narrow that way and went straight back off the frame.
    await Promise.all(['800 36px Mukta', '800 36px Poppins']
      .map(f => document.fonts.load(f).catch(() => {})));
    await Promise.all(['KaTeX_Main', 'KaTeX_Math', 'KaTeX_Size1', 'KaTeX_Size2',
                       'KaTeX_Size3', 'KaTeX_Size4', 'KaTeX_AMS']
      .flatMap(f => ['normal', 'italic', 'bold'].map(st =>
        document.fonts.load(`${st} 80px ${f}`).catch(() => {}))));
    await document.fonts.ready;
    // EQ_H was 250 inside a 470px band, so a one-line formula was scaled to
    // 0.74 and rendered smaller than the caption above it - KaTeX's display
    // strut makes even a short equation measure the full box height. 360
    // still leaves 55px of air top and bottom inside the stage.
    // EQ_H was 360 inside a 470px band. Part 3's summary is a FIVE row ladder
    // and height, not width, is what it is fitted by: at 360 the rows came out
    // 38px tall in a 1080px-wide frame with two thirds of the stage unused. 420
    // still leaves 25px of air top and bottom, and the stage's own band ends at
    // y=850 - a long way above the avatar line at 960 - so nothing moves into
    // the presenter's half.
    const EQ_W = 900, EQ_H = 420;
    const boxes = [base, ...his].map(e => e.getBoundingClientRect());
    const wide = Math.max(...boxes.map(r => r.width));
    const tall = Math.max(...boxes.map(r => r.height));
    // A SHORT equation was capped at k=1 and rendered smaller than the caption
    // band above it - "(n-1)d10 ns2" is 380px inside a 900px box and read as a
    // caption someone had set in a serif. The cap is an upper bound on GROWTH,
    // not on shrinkage; the two ratios below still make overflow impossible.
    const MAX_K = 1.85;
    const k = Math.min(MAX_K, EQ_W / (wide || 1), EQ_H / (tall || 1));
    if (Math.abs(k - 1) > 1e-3) for (const el of [base, ...his])
      el.style.transform = `translate(-50%,-50%) scale(${k.toFixed(4)})`;
    NODES.eq = { base, hi, his,
      actions: [{ action: 'pop_in', t: seg.equation.t_in, dur: 0.5 },
                ...(seg.equation.t_out != null ? [{ action:'fade_out', t: seg.equation.t_out, dur:0.35 }] : [])],
      hiT: hiSpecs.map(h => h.t) };

    /* --- redox arcs: the annotation every board answer carries -------------
       A bracket from the species that changes to what it becomes, named at the
       apex. Oxidation gold, reduction cyan - the same code redox-arrows.svg
       already uses, so a colour means the same thing everywhere in the video.

       Each end is a \htmlId in the LaTeX and the geometry is MEASURED off those
       two elements after the fit scale is applied. Nothing here is a pixel
       guess: KaTeX decides where a term lands and the fitter decides k, so any
       hardcoded offset would be wrong the moment an equation changed length.
       Measuring at build time keeps the frame a pure function of t. */
    for (const a of (seg.equation.arcs || [])) {
      const from = base.querySelector('#' + CSS.escape(a.from));
      const to   = base.querySelector('#' + CSS.escape(a.to));
      if (!from || !to) throw new Error(
        `equation arc "${a.from}" -> "${a.to}": term not found in the LaTeX`);
      const W = eqWrap.getBoundingClientRect();
      const rf = from.getBoundingClientRect(), rt = to.getBoundingClientRect();
      const above = a.side !== 'below';
      const x1 = rf.left + rf.width / 2 - W.left;
      const x2 = rt.left + rt.width / 2 - W.left;
      const edge = above ? Math.min(rf.top, rt.top) - W.top
                         : Math.max(rf.bottom, rt.bottom) - W.top;
      const y0   = edge + (above ? -16 : 16);
      const ctrl = edge + (above ? -96 : 96);
      // a symmetric cubic sits at 1/4 y0 + 3/4 ctrl at its midpoint - that is
      // where the name goes, so it rides the curve instead of floating beside it
      const apex = 0.25 * y0 + 0.75 * ctrl;

      if (!NODES.arcSvg) {
        NODES.arcSvg = document.createElementNS(SVGNS, 'svg');
        NODES.arcSvg.setAttribute('class', 'eqarcs');
        NODES.arcSvg.style.cssText = 'position:absolute;left:0;top:0;width:1080px;'
          + 'height:100%;overflow:visible;pointer-events:none';
        eqWrap.appendChild(NODES.arcSvg);
      }
      const path = document.createElementNS(SVGNS, 'path');
      path.setAttribute('d', `M ${x1} ${y0} C ${x1} ${ctrl} ${x2} ${ctrl} ${x2} ${y0}`);
      path.setAttribute('fill', 'none');
      path.setAttribute('stroke', a.color);
      path.setAttribute('stroke-width', '7');
      path.setAttribute('stroke-linecap', 'round');
      NODES.arcSvg.appendChild(path);
      const L = path.getTotalLength();
      path.style.strokeDasharray = L;

      const head = document.createElementNS(SVGNS, 'polygon');
      const sgn = above ? 1 : -1;
      head.setAttribute('points',
        `${x2},${y0 + sgn * 5} ${x2 - 14},${y0 - sgn * 19} ${x2 + 14},${y0 - sgn * 19}`);
      head.setAttribute('fill', a.color);
      NODES.arcSvg.appendChild(head);

      // the name is HTML, not SVG <text>: Devanagari needs the real font stack,
      // and this way it goes through the same render audit as every other word
      const lab = document.createElement('div');
      lab.className = 'eqarc';
      lab.textContent = a.label;
      lab.style.left = ((x1 + x2) / 2) + 'px';
      lab.style.top = apex + 'px';
      lab.style.color = a.color;
      eqWrap.appendChild(lab);
      // A short arc - KI to KIO3 spans barely 90px - is narrower than the word
      // that names it, and the label's plate then hides the very curve it
      // belongs to. Measured, not assumed: if the name will not fit across the
      // span it moves just outside the apex instead of riding on it.
      const lb = lab.getBoundingClientRect();
      if (lb.width + 12 > Math.abs(x2 - x1)) {
        lab.style.top = (apex + (above ? -1 : 1) * (lb.height / 2 + 10)) + 'px';
      }

      const t0 = a.t, out = seg.equation.t_out;
      const bye = out != null ? [{ action: 'fade_out', t: out, dur: 0.35 }] : [];
      NODES.arcs.push({ path, head, lab, len: L,
        actions:     [{ action: 'fade_in', t: t0,        dur: 0.30 },
                      { action: 'draw',    t: t0,        dur: 0.90 }, ...bye],
        headActions: [{ action: 'fade_in', t: t0 + 0.80, dur: 0.25 }, ...bye],
        labActions:  [{ action: 'pop_in',  t: t0 + 0.45, dur: 0.40 }, ...bye] });
    }
  }

  /* --- blocks: heading, counted list, two-way contrast -----------------
     Screen text that ORGANISES what was said. Built into #stage so it shares
     the diagram's band and cannot reach the presenter. A counted list fills
     IN rather than landing whole: every item stays on screen once named, the
     one being spoken bright and the rest at 55%, so the student can see where
     in the list he is. */
  NODES.blocks = [];
  if (seg.block) {
    const b = seg.block;
    const wrap = document.createElement('div');
    wrap.className = 'blk';
    if (b.title) {
      const h = document.createElement('div');
      h.className = 'bt'; h.textContent = b.title; wrap.appendChild(h);
    }
    const items = [];
    if (b.kind === 'points') {
      const ul = document.createElement('ul'); ul.className = 'pts';
      (b.items || []).forEach((it, i) => {
        const li = document.createElement('li');
        li.innerHTML = `<span class="n">${i + 1}</span><span class="x"></span>`;
        li.querySelector('.x').textContent = it.text;
        ul.appendChild(li);
        items.push({ el: li, t: it.t });
      });
      wrap.appendChild(ul);
    } else if (b.kind === 'compare') {
      const row = document.createElement('div'); row.className = 'cmp';
      (b.cards || []).forEach(c => {
        const d = document.createElement('div');
        d.className = 'card';
        d.innerHTML = '<div class="ch"></div><div class="cr"></div><div class="cb"></div>';
        d.querySelector('.ch').textContent = c.head;
        d.querySelector('.cb').textContent = c.body;
        row.appendChild(d);
        items.push({ el: d, t: c.t, card: true });
      });
      wrap.appendChild(row);
    } else {
      for (const line of (b.lines || [])) {
        const d = document.createElement('div');
        d.className = 'bl';
        d.innerHTML = goldenize(line.text ?? line, (line.golden ?? null));
        wrap.appendChild(d);
        items.push({ el: d, t: line.t ?? b.t_in ?? 0 });
      }
    }
    $('stage').appendChild(wrap);
    NODES.blocks.push({ el: wrap, items,
      actions: [{ action: 'fade_in', t: b.t_in ?? 0, dur: 0.35 },
                ...(b.t_out != null ? [{ action: 'fade_out', t: b.t_out, dur: 0.28 }] : [])] });
  }

  /* --- a generated clip's placeholder, for reading the storyboard --------- */
  NODES.veo = null;
  // BOTH must go. The divider is a SIBLING of the panel, not a child, so
  // removing '#veo' alone left it on screen for every later segment: the
  // torn paper ran across the middle of the step-list block long after the
  // clip it belonged to had ended.
  document.querySelectorAll('#veo, #veotear').forEach(e => e.remove());
  if (seg.veo) {
    const v = document.createElement('div');
    v.id = 'veo';
    v.className = seg.veo.mode === 'keyed' ? 'keyed' : 'panel';
    const lines = (seg.veo.lines || []).map(escapeHTML).join('<br>');
    v.innerHTML = `<div class="vk"></div><div class="vl">${lines}</div>`
                + `<div class="vn"></div>`
                + `<svg class="tear" viewBox="0 0 1080 74" preserveAspectRatio="none">`
                + `<path fill="#F4F1EA" d="${tearPath()}"/></svg>`;
    v.querySelector('.vk').textContent = seg.veo.kicker || 'VEO CLIP · PLACEHOLDER';
    v.querySelector('.vn').textContent = seg.veo.note || '';
    $('frame').appendChild(v);
    if (seg.veo.mode !== 'keyed') {
      // the divider is a sibling, not a child: it is a full-frame image whose
      // paper already sits at the seam, and nesting it would inherit the
      // panel's own top-edge fade mask and dissolve the rip as well
      const t = document.createElement('div');
      t.id = 'veotear';
      $('frame').appendChild(t);
    }
    NODES.veo = { el: v,
      actions: [{ action: 'fade_in', t: seg.veo.t_in ?? 0, dur: 0.3 },
                ...(seg.veo.t_out != null ? [{ action: 'fade_out', t: seg.veo.t_out, dur: 0.3 }] : [])] };
  }

  /* --- caption phrases --- */
  for (const ph of (seg.phrases || [])) {
    const d = document.createElement('div');
    const n = ph.text.length;
    d.className = 'phrase ' + (n <= 24 ? 'xl' : n <= 40 ? 'lg' : n <= 58 ? 'md' : 'sm');
    // U+2011 non-breaking hyphen: keeps "d-block" / "d-orbital" on one line
    // `\w` is ASCII-only, so a Devanagari compound was never protected and
    // "\u0926\u0930-\u0938\u094d\u0925\u093f\u0930\u093e\u0902\u0915" broke as "\u0926\u0930-" / "\u0938\u094d\u0925\u093f\u0930\u093e\u0902\u0915" across the two caption lines
    // (CHE-C3-SA-05). Mukta has no U+2011 glyph, so there the hyphen stays and
    // a WORD JOINER (U+2060, invisible) after it forbids the break instead.
    d.innerHTML = goldenize(ph.text, ph.golden).replace(/(\w)-(\w)/g, '$1\u2011$2')
      .replace(/([\p{L}\p{M}])-(?=[\p{L}\p{M}])/gu, '$1-\u2060');
    cap.appendChild(d);
    NODES.phrases.push({ el: d,
      actions: [{ action: 'pop_in',  t: ph.t_in,  dur: 0.38 },
                { action: 'pop_out', t: ph.t_out, dur: 0.16 }] });
    // pop_out fires AT t_out, not 0.22s before it: t_out means "the line is
    // finished". build_spec.py already subtracts the 0.16s hand-off from the
    // next caption's start, so the band clears exactly as the next one lands
    // and never a frame earlier. (bug ledger 29)
  }

  eqWrap.style.display = seg.equation ? 'flex' : 'none';
  $('stage').style.display =
    (seg.diagram || seg.block || (seg.labels || []).length) ? 'flex' : 'none';

  /* --- A BLOCK IS AS TALL AS ITS CONTENT; THE STAGE IS A FIXED 470px. -----
     Nothing clips, so a block that outgrows the stage simply keeps going
     down the plate and into the caption band. Part 2's recap did: six steps
     at the list's own type size measure 660px, so step six landed at
     1015-1050 and the caption sat on top of it.

     Lift the stage rather than shrink the type — in a block segment the
     plate ABOVE the stage is empty, so the room is already there and the
     words stay the size they were designed at. Only if lifting to MIN_TOP
     still is not enough does the block scale down to fit.

     Measured here, not predicted from the item count: what overflows is the
     rendered height, which depends on how many of the lines wrap. */
  if (seg.block && !seg.diagram && seg.caption_pos !== 'top') {
    const cssPx = n => parseFloat(getComputedStyle(document.documentElement)
                                    .getPropertyValue(n)) || 0;
    const MIN_TOP = 150, CLEAR = 72;   // one caption line of air, not a hairline
    const stageTop = cssPx('--stage-top');
    const limit = cssPx('--cap-top') - CLEAR;
    const h = $('stage').firstElementChild
      ? $('stage').firstElementChild.getBoundingClientRect().height : 0;
    const over = (stageTop + h) - limit;
    if (over > 0) {
      const top = Math.max(MIN_TOP, stageTop - over);
      $('stage').style.top = top + 'px';
      $('stage').style.height = Math.max(cssPx('--stage-h'), h) + 'px';
      const still = (top + h) - limit;
      if (still > 0) {                     // lifting alone could not do it
        const k = (limit - top) / h;
        $('stage').firstElementChild.style.transform = `scale(${k})`;
        $('stage').firstElementChild.style.transformOrigin = '0 0';
      }
    }
  }
}

/* ---------------- the one function that matters ---------------- */

function setTime(t) {
  for (const p of NODES.phrases) {
    const s = stateAt(p.actions, t, { opacity: 0 });
    p.el.style.opacity = s.opacity.toFixed(4);
    p.el.style.transform = `scale(${s.scale.toFixed(4)})`;
  }
  for (const l of NODES.labels) {
    const s = stateAt(l.actions, t, { opacity: l.carry ? 1 : 0 });
    l.el.style.opacity = s.opacity.toFixed(4);
    l.el.style.transform = `translate(-50%,-50%) scale(${s.scale.toFixed(4)})`;
  }
  for (const o of NODES.svgEls) {
    const s = stateAt(o.actions, t, o.initial);
    o.el.style.opacity = s.opacity.toFixed(4);
    o.el.style.transformBox = 'fill-box';
    o.el.style.transformOrigin = '50% 50%';
    o.el.style.transform = `translate(${s.dx}px,${s.dy}px) scale(${(s.scale*(1+0.05*s.pulse)).toFixed(4)})`;
    if (o.el.style.strokeDasharray) {
      const targets = o.el.getTotalLength ? [o.el]
        : [...o.el.querySelectorAll('path,line,polyline,circle,ellipse,rect')];
      for (const d of targets) {
        if (!d.style.strokeDasharray) continue;
        const L = parseFloat(d.style.strokeDasharray);
        d.style.strokeDashoffset = (L * (1 - s.draw)).toFixed(2);
      }
    }
  }
  for (const a of NODES.arcs) {
    const sp = stateAt(a.actions,     t, { opacity: 0 });
    const sh = stateAt(a.headActions, t, { opacity: 0 });
    const sl = stateAt(a.labActions,  t, { opacity: 0 });
    a.path.style.opacity = sp.opacity.toFixed(4);
    a.path.style.strokeDashoffset = (a.len * (1 - sp.draw)).toFixed(2);
    a.head.style.opacity = sh.opacity.toFixed(4);
    a.lab.style.opacity = sl.opacity.toFixed(4);
    a.lab.style.transform = `translate(-50%,-50%) scale(${sl.scale.toFixed(4)})`;
  }
  for (const b of NODES.blocks) {
    const s = stateAt(b.actions, t, { opacity: 0 });
    b.el.style.opacity = s.opacity.toFixed(4);
    // Which item is being spoken right now: the last one whose time has come.
    let k = -1;
    for (let i = 0; i < b.items.length; i++) if (t >= b.items[i].t) k = i;
    b.items.forEach((it, i) => {
      let o = 0;
      if (i <= k) {
        const app = clamp((t - it.t) / 0.35, 0, 1);
        if (i === k) o = app;
        else {
          const dim = clamp((t - b.items[i + 1].t) / 0.30, 0, 1);
          o = 1 - 0.45 * dim;
        }
      }
      it.el.style.opacity = o.toFixed(4);
      if (it.card) it.el.classList.toggle('on', i === k);
    });
  }
  if (NODES.veo) {
    const s = stateAt(NODES.veo.actions, t, { opacity: 0 });
    NODES.veo.el.style.opacity = s.opacity.toFixed(4);
  }
  if (NODES.eq) {
    const s = stateAt(NODES.eq.actions, t, { opacity: 0 });
    const box = $('eq');
    box.style.opacity = s.opacity.toFixed(4);
    box.style.transform = `scale(${s.scale.toFixed(4)})`;
    if (NODES.eq.his && NODES.eq.his.length) {
      // The layers are [base, step0, step1, ...] stacked on top of each other.
      // Exactly two are ever partly visible: the step whose time has arrived,
      // fading in, and the one before it, fading out. Everything else is 0, so
      // a step that has been superseded cannot bleed through the next.
      const { base, his, hiT } = NODES.eq;
      let k = -1;
      for (let i = 0; i < hiT.length; i++) if (t >= hiT[i]) k = i;
      const p = k < 0 ? 0 : clamp((t - hiT[k]) / 0.3, 0, 1);
      const layers = [base, ...his];
      for (const el of layers) el.style.opacity = '0';
      if (k < 0) layers[0].style.opacity = '1';
      else { layers[k + 1].style.opacity = p.toFixed(4);
             layers[k].style.opacity = (1 - p).toFixed(4); }
    }
  }
  document.body.dataset.t = t.toFixed(3);
}

/* exposed to Playwright */
window.RENDER = { build, setTime, get seg() { return SEG; } };
