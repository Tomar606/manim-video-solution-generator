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

/* ---------------- build the DOM once per segment ---------------- */

const $ = id => document.getElementById(id);
let SEG = null, NODES = null;

function goldenize(text, golden) {
  // Wraps EXACTLY ONE occurrence of the golden word. Case-sensitive,
  // whole word only. If it is not found we fail loudly rather than
  // silently shipping a plain phrase.
  if (!golden) return escapeHTML(text);
  // \b is ASCII-only in JavaScript, so it matches neither side of a
  // Devanagari word — every Hindi golden word threw "not found" and the
  // page never signalled READY. Use explicit separators instead.
  const esc = golden.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const SEP = '(?:^|$|[\\s\u0964\u0965.,;:!?()\\[\\]"\'\u2014-])';
  const re = new RegExp('(?<=' + SEP + ')(' + esc + ')(?=' + SEP + ')', 'u');
  if (!re.test(text)) throw new Error(`golden word "${golden}" not found in phrase "${text}"`);
  let done = false;
  return escapeHTML(text).replace(re, m => done ? m : (done = true, `<span class="g">${m}</span>`));
}
const escapeHTML = s => s.replace(/[&<>]/g, c => ({ '&':'&amp;','<':'&lt;','>':'&gt;' }[c]));

window.__FITV = 4;
async function build(seg) {
  SEG = seg;
  const stage = $('stage'), cap = $('caption'), eqWrap = $('eqWrap');
  stage.innerHTML = ''; cap.innerHTML = ''; $('eq').innerHTML = '';
  NODES = { phrases: [], labels: [], svgEls: [], eq: null };

  /* --- stage geometry, per segment ---
     Most segments use the band from style.css: content above the halfway line
     so the presenter never covers it. A segment that hides the presenter
     outright (`presenter: "hidden"` in the beat plan) can have the taller band
     instead, and says so here rather than in the stylesheet -- editing the
     stylesheet between renders means the height depends on which run you are
     in, and a forgotten restore silently reformats every later video. */
  const root = document.documentElement;
  if (seg.stage) {
    root.style.setProperty('--stage-top', seg.stage.top + 'px');
    root.style.setProperty('--stage-h', seg.stage.h + 'px');
  } else {
    root.style.removeProperty('--stage-top');
    root.style.removeProperty('--stage-h');
  }

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
    d.className = 'lbl' + (l.accent ? ' accent' : '');
    d.textContent = l.text;
    d.style.left = (l.x * 1080) + 'px';
    d.style.top  = (l.y * parseFloat(getComputedStyle(document.documentElement)
                    .getPropertyValue('--stage-h'))) + 'px';
    stage.appendChild(d);
    NODES.labels.push({ el: d,
      actions: [{ action: 'pop_in', t: l.t_in, dur: 0.4 },
                ...(l.t_out != null ? [{ action: 'fade_out', t: l.t_out, dur: 0.3 }] : [])] });
  }

  /* --- equation (KaTeX, deterministic; highlight = second render, cross-fade) --- */
  if (seg.equation) {
    // WAIT FOR THE FONTS FIRST. build() runs while the KaTeX webfonts are still
    // loading, so anything measured before this point is measured in the
    // fallback face -- the maths then reflows wider once the real fonts arrive
    // and the fit below is left describing type that no longer exists. Three
    // different ways of measuring all returned the same wrong width because of
    // this, not because of the measurement.
    await document.fonts.ready;
    const box = $('eq');
    // The wrapper is hidden between equation segments and a hidden element
    // measures as zero, so fit() would decide everything already fits. Show it
    // before anything is typeset; the line at the end of build() is then a
    // no-op for this branch.
    eqWrap.style.display = 'flex';
    // FIT THE EQUATION TO THE BOX. At the house size a reaction with six
    // species is far wider than the 940px frame allows, and KaTeX does not
    // wrap -- it simply runs off both edges, which is what shipped. Measure
    // what was actually typeset and step the size down until it fits, rather
    // than picking a smaller constant that would shrink the short ones too.
    const BOX_W = 1000, BOX_H = 420;
    // MEASURE THE TYPESET MATH, NOT THE SPAN AROUND IT. The span is absolutely
    // positioned, so it is laid out shrink-to-fit against half the box and its
    // rect answers neither question -- fitting against it left every reaction
    // about 100px wider than the frame while reporting that it fits. `.katex`
    // is the box KaTeX actually drew, and display mode's 1em margins are
    // dropped because the surrounding band is the spacing.
    const fit = el => {
      // display mode's 1em margins are dead space here -- the band around the
      // equation is the spacing -- and they were being counted as height.
      const inner = el.querySelector('.katex-display');
      if (inner) { inner.style.margin = '0'; inner.style.width = 'max-content'; }
      // MEASURE THE MATHS, NOT THE BOX AROUND IT. Both the span (absolutely
      // positioned, so laid out shrink-to-fit against half the frame) and
      // `.katex` (a BLOCK in display mode) report the width of their container,
      // not of the type: every reaction measured 1015px whatever the font size,
      // so the fit loop stopped one step in and left the maths running to both
      // frame edges. `width: max-content` makes the span report the type.
      el.style.width = 'max-content';
      let size = 80;
      for (let i = 0; i < 24; i++) {
        el.style.fontSize = size + 'px';
        const r = el.getBoundingClientRect();
        if (!r.width || (r.width <= BOX_W && r.height <= BOX_H)) break;
        const next = size * Math.min(BOX_W / r.width, BOX_H / r.height) * 0.98;
        if (next >= size) break;
        size = Math.max(28, next);
      }
      el.style.fontSize = size + 'px';
    };
    const mk = latex => { const s = document.createElement('span');
      s.style.position = 'absolute'; s.style.left = '50%'; s.style.top = '50%';
      s.style.transform = 'translate(-50%,-50%)';
      katex.render(latex, s, { displayMode: true, throwOnError: true });
      box.appendChild(s); return s; };
    // 400px, not 260: the stage band runs 380 -> 850 and nothing else is in
    // it, so a reaction broken over two or three lines can still be typeset
    // large. At 260 the fit above had to drop a six-species reaction to
    // about 40% of house size to make it fit vertically.
    box.style.position = 'relative'; box.style.width = '1040px'; box.style.height = '440px';
    const base = mk(seg.equation.latex);
    let hi = null;
    if (seg.equation.highlight) { hi = mk(seg.equation.highlight.latex); }
    // FIT ONLY AFTER THE MATHS HAS ITS REAL FONTS. `document.fonts.ready`
    // before rendering resolves instantly -- nothing is pending until KaTeX
    // asks for a face -- so the fit ran against the fallback and every
    // reaction reflowed about 100px wider once KaTeX_Main arrived. Render,
    // let a frame pass so the loads are registered, wait, then measure.
    await document.fonts.ready;
    await new Promise(r => requestAnimationFrame(r));
    await document.fonts.ready;
    fit(base); if (hi) fit(hi);
    NODES.eq = { base, hi,
      actions: [{ action: 'pop_in', t: seg.equation.t_in, dur: 0.5 },
                ...(seg.equation.t_out != null ? [{ action:'fade_out', t: seg.equation.t_out, dur:0.35 }] : [])],
      hiT: seg.equation.highlight ? seg.equation.highlight.t : null };
  }

  /* --- caption phrases --- */
  for (const ph of (seg.phrases || [])) {
    const d = document.createElement('div');
    const n = ph.text.length;
    d.className = 'phrase ' + (n <= 24 ? 'xl' : n <= 40 ? 'lg' : n <= 58 ? 'md' : 'sm');
    // U+2011 non-breaking hyphen: keeps "d-block" / "d-orbital" on one line
    d.innerHTML = goldenize(ph.text, ph.golden).replace(/(\w)-(\w)/g, '$1\u2011$2');
    cap.appendChild(d);
    NODES.phrases.push({ el: d,
      actions: [{ action: 'pop_in',  t: ph.t_in,  dur: 0.38 },
                { action: 'pop_out', t: ph.t_out - 0.22, dur: 0.22 }] });
  }

  eqWrap.style.display = seg.equation ? 'flex' : 'none';
  $('stage').style.display = (seg.diagram || (seg.labels || []).length) ? 'flex' : 'none';
}

/* ---------------- the one function that matters ---------------- */

function setTime(t) {
  for (const p of NODES.phrases) {
    const s = stateAt(p.actions, t, { opacity: 0 });
    p.el.style.opacity = s.opacity.toFixed(4);
    p.el.style.transform = `scale(${s.scale.toFixed(4)})`;
  }
  for (const l of NODES.labels) {
    const s = stateAt(l.actions, t, { opacity: 0 });
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
  if (NODES.eq) {
    const s = stateAt(NODES.eq.actions, t, { opacity: 0 });
    const box = $('eq');
    box.style.opacity = s.opacity.toFixed(4);
    box.style.transform = `scale(${s.scale.toFixed(4)})`;
    if (NODES.eq.hi) {
      const on = NODES.eq.hiT != null && t >= NODES.eq.hiT;
      const p = on ? clamp((t - NODES.eq.hiT) / 0.3, 0, 1) : 0;
      NODES.eq.hi.style.opacity   = p.toFixed(4);
      NODES.eq.base.style.opacity = (1 - p).toFixed(4);
    }
  }
  document.body.dataset.t = t.toFixed(3);
}

/* exposed to Playwright */
window.RENDER = { build, setTime, get seg() { return SEG; } };
