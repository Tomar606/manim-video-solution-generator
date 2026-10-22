# Programmatic video rendering frameworks (state as of 8 October 2026)

Method note: repo statistics (stars, last push, latest release, licence) were read from the GitHub REST API on 2026-10-08 and are cited to the repo URL. Everything else is cited to the page it was read from. Where a page was read through a summarising fetch and a number could not be cross-checked, it is flagged. Nothing here was benchmarked by me; no framework was installed or run.

## 1. What each framework is, and how alive it is (landscape and maturity)

### Takeaway
Two browser-based frameworks are far ahead of everything else in activity: Remotion (62k stars, release on 7 Oct 2026) and HeyGen's HyperFrames (58k stars seven months after creation, release on 7 Oct 2026, still 0.x). Motion Canvas and Revideo have slowed to maintenance pace (no tagged Motion Canvas release since Dec 2024; Revideo's founder now runs a different one-person product), and Manim Community shipped v0.21.0 in August 2026 with Typst support and a roughly 2x faster Cairo renderer.

### Cited Findings

**HyperFrames (HeyGen)**
- 58,410 stars, Apache-2.0, repo created 2026-03-10, last push 2026-10-07, latest release v0.8.140 published 2026-10-07 (GitHub API). — [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes)
- Described as an open-source framework to "create, preview, and render HTML-based video compositions" with first-class agent support; requires Node.js 22+ and FFmpeg; seven packages (CLI, core, engine, producer, studio, player, shader-transitions) plus an optional AWS Lambda module. — [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes)
- Timeline model: clips, timing and tracks are HTML elements with `data-*` attributes; animation comes through seekable adapters — "GSAP, CSS, Lottie, Three.js, Anime.js, WAAPI, or your own frame adapter". — [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes)
- Render architecture: the runtime exposes `window.__hf.seek(timeSeconds)`; "the renderer never calls play(). It calls seek(0), screenshots, seek(1/30), screenshots…". Uses `chrome-headless-shell` with `--deterministic-mode --enable-begin-frame-control --run-all-compositor-stages-before-draw` and the `HeadlessExperimental.beginFrame` CDP call for an atomic layout-paint-composite-screenshot cycle. Parallel rendering splits across multiple Chrome processes and FFmpeg concatenates chunks. — [HeyGen research: HTML to video, 22 June 2026](https://www.heygen.com/research/html-to-video)
- Determinism measures: Google Fonts imports are rewritten to base64-embedded local copies; `Date.now()`, unseeded `Math.random()` and network fetches are disallowed at render; time is quantised to the frame grid. — [HeyGen research: HTML to video](https://www.heygen.com/research/html-to-video)
- **Platform limitation that matters for a Mac shop:** fully deterministic BeginFrame capture works only on Linux; macOS and Windows fall back to `Page.captureScreenshot` with heuristic timing. — [HeyGen research: HTML to video](https://www.heygen.com/research/html-to-video)
- **Embedded video limitation:** headless Chrome video decoding is unreliable, so HyperFrames pre-extracts each `<video>` to JPEG frames with FFmpeg and swaps in an `<img>` per frame; "video-heavy compositions require single-worker fallback"; blob URLs, streaming sources and dynamically set `src` are harder to handle. — [HeyGen research: HTML to video](https://www.heygen.com/research/html-to-video)
- Output formats: MP4, WebM (with transparency), MOV ProRes 4444 (with alpha), GIF, PNG sequence, HLS. Render modes: local, Docker, AWS Lambda, Google Cloud Run. — [HyperFrames rendering guide](https://hyperframes.heygen.com/guides/rendering)
- Agent authoring: a Claude Code marketplace plugin, 21 published skills installable via a registry, and a `/hyperframes` router skill; also a hosted MCP connector ("create and render without installing the local CLI") and WebMCP tools exposed by Studio so an agent can drive the editor. — [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes); [HyperFrames docs index](https://hyperframes.heygen.com/llms.txt)
- Studio has a GUI timeline ("Move, trim, split, align, and inspect clips"), a canvas editor, keyframe editing and a captions editor. — [HyperFrames docs index](https://hyperframes.heygen.com/llms.txt)
- Audio: a dedicated audio skill with voiceover ducking ("dip a music bed only in the bands the voice occupies") and an effects chain (EQ, compressor, limiter, etc.). — [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes)
- Over 50 prebuilt components/blocks (social overlays, shader transitions, data visualisations) are reported by a secondary write-up. — [silenceper.com, 2 May 2026](https://silenceper.com/en/article/2026-05-02-hyperframes-html-video-rendering/)

**Remotion**
- 62,337 stars, last push 2026-10-07, latest release v4.0.534 published 2026-10-07; licence is a custom one (GitHub reports NOASSERTION). — [remotion-dev/remotion](https://github.com/remotion-dev/remotion)
- Authoring model contrast, from HeyGen's own comparison: Remotion is "React and TypeScript" where "your code reads the frame number and returns the values"; HyperFrames is plain HTML/CSS/JS that "the renderer pauses … and seeks". — [HyperFrames vs Remotion guide](https://hyperframes.heygen.com/guides/hyperframes-vs-remotion)
- Official Agent Skills are installed with `npx remotion skills add`; they cover best practices, compositions, layout/animation/typography, media, audio, fonts, Studio, rendering, captions and maps. The Remotion MCP was deprecated in favour of the skills, with the hosted MCP to shut down no earlier than 31 Aug 2026. — [Remotion AI skills docs](https://www.remotion.dev/docs/ai/skills); [tella.com walkthrough](https://www.tella.com/blog/how-to-use-remotion-agent-skills-with-claude-code)
- Current recommended video tag is `<Video>` from `@remotion/media`; the older `<Html5Video>` and `<OffthreadVideo>` "are not optimized". — [Remotion performance docs](https://www.remotion.dev/docs/performance)

**Motion Canvas and Revideo**
- Motion Canvas: 19,249 stars, MIT, last push 2026-07-02, but latest tagged release is v3.17.2 from 2024-12-14 (older than the 2025-2026 window — flagged). — [motion-canvas/motion-canvas](https://github.com/motion-canvas/motion-canvas)
- Revideo: the repo `redotvideo/revideo` now redirects to `midrender/revideo`; 4,088 stars, MIT, last push 2026-07-15, no GitHub releases listed. — [midrender/revideo](https://github.com/midrender/revideo)
- Revideo's README still advertises parallel rendering across workers, `<Audio/>` with frame-accurate sync, a React `<Player/>` for in-browser preview and deployment on Cloud Run. — [midrender/revideo](https://github.com/midrender/revideo)
- Revideo's founder (Konstantin Hohr) now lists Midrender, "a visual editor for creating motion graphics powered by AI", as the company product; team size 1. The YC page makes no statement about Revideo's maintenance. — [YC: Midrender](https://www.ycombinator.com/companies/midrender)

**Manim family**
- Manim Community: 41,331 stars, MIT, last push 2026-10-06, latest release v0.21.0 published 2026-08-10. — [ManimCommunity/manim](https://github.com/ManimCommunity/manim)
- v0.21.0 highlights: first-class Typst support (new `Typst` and `MathTypst` mobjects that render to SVG with no TeX install), Cairo renderer about 2x faster on animation-heavy scenes (release page text says 2.2x via vectorised path operations), concurrent partial-movie encoding via `max_inflight_encoders`, and cache hashing 94-98% cheaper. — [Manim releases](https://github.com/ManimCommunity/manim/releases)
- ManimGL (3b1b): 94,718 stars, last push 2026-09-09, latest tagged release v1.7.2 from 2024-12-13 (flagged as old). — [3b1b/manim](https://github.com/3b1b/manim)
- manim-slides: 955 stars, MIT, v5.7.0 published 2026-09-14. It is a presentation tool, not a renderer. — [jeertmans/manim-slides](https://github.com/jeertmans/manim-slides)
- manim-web (maloyan): a TypeScript port running client-side with Canvas/WebGL and MathJax/KaTeX for LaTeX; last update reported as 1 May 2026. — [gittrend: maloyan/manim-web](https://gittrend.io/repo/maloyan/manim-web); [Show HN thread](https://hn.svelte.dev/item/47155375)
- Academa Studio (public launch 29 July 2026): a Manim-API-compatible engine written in Rust on wgpu, compiled to WebAssembly and driven from Pyodide in the browser; the author says the engine was built independently and given Manim API compatibility afterwards. — [Show HN thread](https://hn.svelte.dev/item/49091703)

**Smaller / older libraries (GitHub API, 2026-10-08)**
- editly: 5,518 stars, MIT, last push 2025-05-12, latest release a release candidate from Jan 2025. — [mifi/editly](https://github.com/mifi/editly)
- Twick: 537 stars, custom licence, last push 2026-06-04, v0.15.31 (March 2026). — [ncounterspecialist/twick](https://github.com/ncounterspecialist/twick)
- Diffusion Studio core: 1,247 stars, MPL-2.0, last push 2025-11-18, latest release v1.1.1 from Oct 2024. — [diffusionstudio/core](https://github.com/diffusionstudio/core)
- Etro: 1,150 stars, **GPL-3.0**, last push 2026-10-05, v0.14.1 (Aug 2026). — [etro-js/etro](https://github.com/etro-js/etro)
- MoviePy: 14,959 stars, MIT, last push 2026-08-26, latest release v2.2.1 from 2025-05-21. — [Zulko/moviepy](https://github.com/Zulko/moviepy)
- FFCreator: 3,163 stars, MIT, last push 2024-12-19, latest release v6.8.1 from Feb 2023 — effectively dormant. — [tnfe/FFCreator](https://github.com/tnfe/FFCreator)
- Theatre.js: 12,733 stars, Apache-2.0, last push 2024-08-14 — effectively dormant. — [theatre-js/theatre](https://github.com/theatre-js/theatre)

**Template-API SaaS (secondary source only — a vendor comparison blog, treat prices as indicative)**
- Shotstack about $49 for 200 minutes of 720p (roughly $0.25 per video minute); Creatomate Essential $54/month for 2,000 credits, effective $0.10-$0.84 per minute depending on resolution and frame rate; JSON2Video about $49/month for roughly 200 minutes of Full HD; Plainly from $69/month (After Effects based). — [motionbox.io comparison, Aug 2026](https://motionbox.io/blog/best-json2video-alternatives-in-2026)

### Inferences
- HyperFrames is at v0.8.x with a release nearly every day (v0.7.38 to v0.8.140 within months). That is high velocity and also high churn: pin an exact version, and expect breaking changes. Its headline star count (58k in seven months) reflects hype as much as production maturity.
- The summarised fetch of the Manim releases page returned release dates that were plainly wrong (it dated v0.21.0 to 2024); the GitHub API date of 2026-08-10 is the reliable one. Only v0.21.0's date is asserted here.
- Revideo looks like a maintenance risk: no releases on GitHub, founder attention on another product, last push three months ago. Motion Canvas is alive in commits but has not tagged a release in 22 months.
- Theatre.js, FFCreator, editly and Diffusion Studio core can be dropped from consideration on activity alone. Etro's GPL-3.0 licence is a problem for a closed commercial pipeline.
- None of the SaaS template APIs is likely to fit: the workload needs KaTeX, traced SVG diagrams with audio-synced labels and a custom keyed presenter, which are code-level features, and SaaS per-minute pricing is 5-40x the cloud-function cost of self-rendering (see section 4).

### Gaps
- Not researched in this pass for lack of tool budget, so no claims are made: Mosaico, Rendley, Rive/Lottie render pipelines, After Effects + nexrender, Blender headless. (The nexrender repo was not found at `inlet/nexrender`; its current location was not confirmed.)
- Remotion Studio and Remotion Player feature detail (in-browser preview/editing, visual props editing) was not fetched from primary docs in this pass; the existence of both is well known but specifics are unverified here.
- Remotion's Rust compositor / headless-shell internals were not confirmed from a 2026 primary source.
- HyperFrames open-issue count: the repo page shows 56 open issues while the API's `open_issues_count` (which includes pull requests) is 188.

## 2. Devanagari shaping and LaTeX-quality maths in the same text run

### Takeaway
Any Chromium-based renderer (HyperFrames, Remotion, Revideo/Motion Canvas's HTML layer, the team's existing Playwright renderer) solves the "Hindi and maths cannot mix" problem by construction, because HarfBuzz shapes the Devanagari and KaTeX/MathJax lays out the maths in the same DOM line. The documented caveat is inside KaTeX itself: Brahmic glyphs placed *inside* a formula's `\text{}` use system fonts and approximate metrics, so Hindi should sit in ordinary HTML around the formula rather than inside it.

### Cited Findings
- KaTeX: "Armenian, Brahmic, Georgian, Chinese, Japanese, and Korean glyphs are always accepted in text mode. However, these glyphs will be rendered from system fonts (not KaTeX-supplied fonts) so their typography may clash." — [KaTeX supported functions](https://katex.org/docs/supported.html)
- KaTeX: such glyphs "may cause small vertical alignment issues … other accepted glyphs are treated as if they are each as tall as the letter M in the current KaTeX font." — [KaTeX supported functions](https://katex.org/docs/supported.html)
- KaTeX exposes a `.brahmic_fallback` CSS class (alongside `.cjk_fallback` etc.) so a specific font can be supplied for these glyphs. — [KaTeX supported functions](https://katex.org/docs/supported.html)
- HyperFrames embeds fonts as base64 local copies at render time so output does not depend on network font loading. — [HeyGen research: HTML to video](https://www.heygen.com/research/html-to-video)
- Manim v0.21.0 adds `Typst` and `MathTypst` mobjects rendering markup and maths straight to SVG without TeX. — [Manim releases](https://github.com/ManimCommunity/manim/releases)
- Motion Canvas has a `Latex` component for formulas. — [Motion Canvas LaTeX docs](https://motioncanvas.io/docs/latex)

### Inferences
- The clean pattern in HTML is `<span lang="hi">विभव</span> <span class="katex">…</span>` on one line: Devanagari never enters KaTeX, so the system-font and M-height caveats never trigger. Where a Hindi subscript is unavoidable (the `E°सेल` case), set `.brahmic_fallback { font-family: <the house Devanagari face> }` and verify the baseline by frame review.
- Manim's new Typst path may also remove the split inside Manim, since Typst shapes text with a HarfBuzz-compatible shaper and sets maths in one document. This is unverified for Devanagari and should be tested before relying on it.
- Motion Canvas/Revideo draw to a 2D canvas rather than the DOM; canvas `fillText` in Chromium does shape Devanagari, but mixing shaped Hindi and LaTeX on one line there is manual layout, not free as it is in the DOM.

### Gaps
- No source was found reporting a concrete Devanagari rendering bug in HyperFrames, Remotion or headless Chromium in 2025-2026. Absence of reports is not proof of absence; the known risk class is a headless Linux container without the Devanagari font installed, giving tofu or a fallback face.
- MathJax's handling of Devanagari inside `\text{}` was not checked.
- Typst's Devanagari-plus-maths quality inside Manim v0.21.0 is untested and unsourced.

## 3. Step-by-step equation animation (the TransformMatchingTex equivalent)

### Takeaway
The only web framework with a documented, built-in equivalent of Manim's matching-parts equation morph is Motion Canvas's `Latex` component (inherited by Revideo); in HyperFrames or Remotion it has to be built from KaTeX/MathJax output plus a FLIP-style tween, and no maintained off-the-shelf library for that was found.

### Cited Findings
- Motion Canvas: "You can animate LaTeX by tweening the tex property"; formulas are split into parts either as an array (`tex={['a^2', '+', 'b^2', '=', 'c^2']}`) or with `{{ }}` syntax. — [Motion Canvas LaTeX docs](https://motioncanvas.io/docs/latex)
- Motion Canvas matching rule: a part only in the source is faded out, a part only in the target is faded in, and parts present in both are tweened. — [Motion Canvas LaTeX docs](https://motioncanvas.io/docs/latex)
- The `{{ }}` splitting/tweening arrived in Motion Canvas 3.17.0. — [Motion Canvas 3.17.0 blog](https://motioncanvas.io/blog/version-3.17.0)
- HyperFrames accepts any seekable animation runtime through a three-method `FrameAdapter` (`init`, `getDurationFrames`, `seekFrame`), with GSAP as the default. — [HeyGen research: HTML to video](https://www.heygen.com/research/html-to-video)
- Manim v0.20-0.21 rewrote `MathTex` and added `MathTypst`, so Manim remains the reference implementation for this effect. — [Manim releases](https://github.com/ManimCommunity/manim/releases)

### Inferences
- Practical HTML recipe (my design, not a sourced product): render each derivation step with KaTeX, tag matching terms with `\htmlId`/`\htmlClass` (requires KaTeX `trust`), measure bounding boxes of both steps, and drive a GSAP timeline that translates/scales shared terms and cross-fades the rest. GSAP's Flip plugin does exactly this bookkeeping, and because GSAP timelines are seekable they are deterministic under both HyperFrames and Remotion (driven by frame number). This gives position-morphing, not true glyph-outline morphing.
- True outline morphing (a `2` turning into a `4`) needs SVG paths: MathJax SVG output plus a path-morph tween. That is rarely pedagogically necessary for board-exam derivations, where "this term moves across the equals sign" is the teaching content.
- A hybrid is defensible: keep Manim only for the derivation beats that genuinely need matched morphing, render them as alpha clips, and place them inside the HTML composition as video.

### Gaps
- No 2025-2026 library was found that packages "KaTeX + FLIP equation morph" for Remotion or HyperFrames; whether HyperFrames' component catalogue includes an equation block was not checked.
- Quality comparison between Motion Canvas `Latex` tweening and Manim `TransformMatchingTex` on long multi-line derivations: no source found.

## 4. Measured render throughput, parallel/distributed rendering, and cost per video-minute

### Takeaway
No trustworthy published benchmark for 1080x1920@30 on Apple Silicon was found for any framework; the available numbers are a HyperFrames issue on a Linux RTX 3090 box (trivial content, 1.5-6x faster than realtime) and one third-party Remotion measurement on an unspecified cloud VM (0.43x realtime for a 60s portrait captioned video). Distributed rendering on AWS Lambda is mature for Remotion and available for HyperFrames, at roughly $0.02 per video-minute of compute.

### Cited Findings
- HyperFrames, Linux, RTX 3090, chrome-headless-shell 152, v0.8.79, 1920x1080@30, 10-second composition with one GSAP tween and no media: 5.4-6.5s wall time with 1-5 workers (BeginFrame capture); 9.6-11.0s with 6-8 workers because every worker's BeginFrame probe times out and falls back to screenshot capture. — [hyperframes issue #4584, opened 27 Sep 2026, open](https://github.com/heygen-com/hyperframes/issues/4584)
- Same issue, 60-second clip: 10.3s at 5 workers with BeginFrame versus 22.2s at 6 workers in screenshot fallback; `--workers auto` picks 6 on that machine, so the default takes the slow path. — [hyperframes issue #4584](https://github.com/heygen-com/hyperframes/issues/4584)
- HyperFrames shader transitions defeat worker parallelism: a timeline with 14 shader transitions of 0.3s rendered in 2m15.0s versus 13.9s with hard cuts (about 9.7x slower). — [hyperframes issue #677](https://github.com/heygen-com/hyperframes/issues/677)
- HyperFrames docs example: one CSS declaration changed a 300-frame 1920x1080 render from 9.8s to 25.0s (median of three); expensive items named are large blurs, `backdrop-filter`, many shadowed layers, oversized source images, and VP9 ("transparent WebM is CPU-heavy"). — [HyperFrames performance guide](https://hyperframes.heygen.com/guides/performance)
- HyperFrames on macOS with hardware GPU: "drawElement fast capture is now on by default — roughly 2x faster capture" (from a release note surfaced in search; not opened directly). — [newreleases.io: hyperframes v0.7.38](https://newreleases.io/project/github/heygen-com/hyperframes/release/v0.7.38)
- Remotion 4.0.532, 60-second 1080x1920@30 React composition "with captions and effects", unspecified cloud VM: median of three runs 139.6s (2.327s per output second); 212.3s inside Docker. The same PR measured FFmpeg-only approaches at 8.9-10.8s. The author marks the result provisional and the machine as not a reference system. — [Your_Editor PR #12, Oct 2026](https://github.com/mahmoudemad68/Your_Editor/pull/12)
- Remotion on Modal: about 60 seconds to render a 20-second 1080p video on a single 4-core container (search-snippet figure, not opened). — [creativeghq/remotion-modal issue #1](https://github.com/creativeghq/remotion-modal/issues/1)
- Remotion Lambda official cost examples (2048 MB, us-east-1, v4.0.381): 1-minute video, warm, 18.91s, $0.017; cold 15.52s, $0.021; 10-minute HD video with a remote video, warm, 56.09s, $0.103; 10-second 4K, warm, 45.28s, $0.013. S3, bandwidth, CloudWatch and the Remotion licence are extra. — [Remotion Lambda cost examples](https://www.remotion.dev/docs/lambda/cost-example)
- Remotion Lambda marketing figures: an 80-second video in 15 seconds; a 2-hour video in 12 minutes; about $0.01 per minute estimated. — [Remotion Lambda](https://www.remotion.dev/lambda)
- Remotion tuning: `--concurrency` helps or hurts depending on machine, measured with `npx remotion benchmark`; PNG frames are slower than JPEG but required for transparency; VP8/VP9 encode is "very slow"; GPU-accelerated CSS (shadows, blur, gradients) and WebGL can bottleneck on GPU-less cloud instances. — [Remotion performance docs](https://www.remotion.dev/docs/performance)
- HyperFrames on AWS: Step Functions "Plan → Map(N) RenderChunk → Assemble" over a single Lambda with bundled Chromium and ffmpeg; default concurrency 8; one sample render cost "$0.0214 (Lambda $0.0210 + SFN $0.0004)" excluding S3 transfer; SDR only, no completion webhook, each region an independent stack. — [HyperFrames AWS Lambda docs](https://hyperframes.heygen.com/deploy/aws-lambda.md)
- Manim v0.21.0: Cairo about 2x faster on animation-heavy scenes; partial movie files can be encoded concurrently. — [Manim releases](https://github.com/ManimCommunity/manim/releases)

### Inferences
- Converting the cited numbers: HyperFrames' trivial 60s/1080p30 clip at 10.3s is about 175 fps (5.8x realtime) on a desktop GPU; the Remotion portrait captioned 60s at 139.6s is about 12.9 fps (0.43x realtime) on an unknown VM. These are **not comparable** (different content, hardware and worker counts) and neither includes an embedded presenter video. They bracket expectations rather than rank the tools.
- For this workload the presenter video is in every frame, which is the worst case for HyperFrames' parallelism (documented single-worker fallback for video-heavy compositions) and is CPU-bound frame extraction in both tools. On the 8GB M2, also note HyperFrames loses BeginFrame determinism on macOS. A realistic expectation for a 2-minute portrait video on that Mac is a few minutes, not seconds — still an order of magnitude below the current 26-47 minutes per 90s part, but this must be measured, not assumed.
- Cloud cost is negligible at the target volume: 10 two-minute videos/day at about $0.02-$0.04 per video is well under $1 per operator per day in Lambda compute, on either framework. Wall-clock is 20-60s per video on Lambda, which removes the 8GB Mac from the critical path entirely.
- An in-between option is one Linux box (the BeginFrame-supported platform) as a render server; the issue above suggests capping HyperFrames workers at 5 per GPU until #4584 is fixed.

### Gaps
- No measured Apple Silicon numbers (M1/M2/M3) for Remotion or HyperFrames at 1080x1920@30 were found. This is the single most important missing figure and needs a local spike on the actual M2.
- No throughput numbers at all for Motion Canvas/Revideo, Manim OpenGL renderer, or ManimGL on comparable content.
- HyperFrames' Lambda sample cost is not tied to a stated duration/resolution in the docs excerpt, so a per-minute figure cannot be derived from it.
- RAM use per Chrome worker (critical on 8GB) is not documented by either project in the pages read.
- Google Cloud Run pricing/timing for either framework was not found.

## 5. Chroma key and alpha compositing of the presenter inside the framework

### Takeaway
Remotion now ships a first-party WebGL2 chroma-key effect (`colorKey()` in `@remotion/effects`, v4.0.472+) that applies directly to `<Video>`, and natively plays alpha WebM, so the presenter key can live inside the composition. HyperFrames documents alpha in and out (transparent WebM / ProRes 4444) and an ML background-removal command, but no green-screen chroma key was found in its docs, and its embedded-video path (pre-extracted JPEG frames) is its weakest area.

### Cited Findings
- Remotion `colorKey()`: "a classic color key (chroma key) effect that turns pixels close to a chosen color transparent"; introduced in v4.0.472 in `@remotion/effects`; works on canvas-based components `<Video>`, `<HtmlInCanvas>` and `<Solid>`; parameters `keyColor` (default `#00ff00`), `similarity` (0.18), `smoothness` (0.08), `spillSuppression` (0.25); requires a WebGL2 backend at render (the `--gl` flag). — [Remotion colorKey docs](https://www.remotion.dev/docs/effects/color-key)
- Remotion also documents a manual route: draw video frames to a `<canvas>` with `drawImage()` and manipulate pixels. — [Remotion video manipulation](https://www.remotion.dev/docs/video-manipulation); [Remotion greenscreen](https://www.remotion.dev/docs/greenscreen)
- Remotion: "Transparent videos with an alpha channel are natively supported by `<Video>` from `@remotion/media`" (WebM); `<OffthreadVideo>` needs the `transparent` prop. — [Remotion transparency docs](https://www.remotion.dev/docs/videos/transparency)
- Remotion transparent *output* requires PNG frames, which are slower than JPEG. — [Remotion performance docs](https://www.remotion.dev/docs/performance)
- HyperFrames output: WebM and MOV (ProRes 4444) preserve alpha; "Leave the composition background unpainted wherever the output must remain transparent." — [HyperFrames rendering guide](https://hyperframes.heygen.com/guides/rendering)
- HyperFrames `npx hyperframes remove-background subject.mp4 -o subject.webm` uses a local human-segmentation (matting) model, **not** chroma key; outputs transparent WebM / ProRes 4444 / PNG; it "underperforms on fine hair over busy backgrounds" and where "VFX-grade frame-to-frame edge stability" is needed. — [HyperFrames remove-background guide](https://hyperframes.heygen.com/guides/remove-background.md)
- HyperFrames has an "HTML in Canvas" guide ("Use live DOM content as a texture for WebGL and canvas effects") and a "Captions and talking-head footage" guide. — [HyperFrames docs index](https://hyperframes.heygen.com/llms.txt)
- HyperFrames replaces each `<video>` with per-frame JPEG `<img>` elements at render time. — [HeyGen research: HTML to video](https://www.heygen.com/research/html-to-video)

### Inferences
- Remotion is the only framework here with a documented, parameterised, in-composition green-screen key including spill suppression. That directly targets the 800-line ffmpeg compositor.
- In HyperFrames the cheapest correct route is to key once outside the composition (a single ffmpeg pass per presenter clip to alpha WebM, or HeyGen's own transparent-background export if the plan offers it), then layer the alpha WebM. Because HyperFrames turns videos into JPEG frames, and JPEG has no alpha, whether alpha survives that extraction path for an input WebM needs to be tested — the remove-background guide implies it does, but the engine article describes JPEG extraction.
- A real green-screen plate keys better with a chroma keyer than with a matting model (hair edges, temporal stability), so `remove-background` is not a substitute for the current key.
- Either way the expensive part of today's compositor — per-frame full-resolution ffmpeg filter graphs across a whole part — collapses into one keyed presenter asset that is cached and reused; that pre-key step is seconds-to-a-minute of ffmpeg, independent of framework.

### Gaps
- No HyperFrames doc page for green-screen chroma key was found; whether its shader/HTML-in-canvas layer can key a `<video>` deterministically at render was not verified.
- Quality of Remotion's `colorKey()` against a tuned ffmpeg chromakey + despill on HeyGen footage is untested; no third-party comparison found.
- Whether HeyGen's avatar export offers a transparent WebM for this team's plan was not checked.
- Motion Canvas/Revideo and Manim chroma-key capabilities were not researched.

## 6. Suitability for LLM agents, live preview, and a non-technical operator adjusting timing in a GUI

### Takeaway
Both leaders have official agent skill packs and a live preview; HyperFrames is the more agent- and operator-oriented of the two (plain HTML an LLM writes fluently, a Studio with drag/trim timeline and caption editor, MCP and WebMCP control), while Remotion's strength is typed, schema-validated templates where the agent or operator only supplies JSON props. For "deterministic, top-notch, low-technical operators", fixed templates plus data beat free-form generated scenes in either framework.

### Cited Findings
- HyperFrames positions agents as first-class: Claude Code plugin, 21 skills, a router skill that "confirms every creation brief up front". — [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes)
- HyperFrames Studio: canvas editing, timeline ("Move, trim, split, align, and inspect clips"), animation/keyframe editing, captions editor; a hosted MCP connector; Studio "exposes its editing capabilities as WebMCP tools" so an agent can drive it. — [HyperFrames docs index](https://hyperframes.heygen.com/llms.txt)
- HyperFrames supports templated renders with variables on Lambda ("Render compositions with different variable values"), with a 256 KiB Step Functions input cap. — [HyperFrames docs index](https://hyperframes.heygen.com/llms.txt); [HyperFrames AWS Lambda docs](https://hyperframes.heygen.com/deploy/aws-lambda.md)
- HyperFrames claims preview/render parity is "enforced" via SHA256 verification of the runtime bundle. — [HeyGen research: HTML to video](https://www.heygen.com/research/html-to-video)
- Remotion Agent Skills are installed per project (`npx remotion skills add`), load relevant rule files on demand, and include a captions/subtitles skill; the MCP server is deprecated in their favour. — [Remotion AI skills docs](https://www.remotion.dev/docs/ai/skills); [tella.com walkthrough](https://www.tella.com/blog/how-to-use-remotion-agent-skills-with-claude-code)
- HeyGen's own guidance on choosing: Remotion "when video belongs inside a React system with typed components, application data, and established rendering infrastructure"; HyperFrames "when the source is ordinary HTML, CSS, GSAP, Lottie". — [moda.app: HyperFrames vs Remotion](https://moda.app/blog/hyperframes-vs-remotion) (third-party blog summarising the comparison)
- Revideo offers a React `<Player/>` that "accepts dynamic inputs, so the same project drives both preview and final render". — [midrender/revideo](https://github.com/midrender/revideo)
- A dissenting practitioner view exists: a Chinese-language product-manager post titled (translated) "after using Remotion for vibe-motion effects I never want to touch HyperFrames again". Not read in full. — [woshipm.com](https://www.woshipm.com/?p=6408883)

### Inferences
- The existing home-grown Playwright renderer already produces HTML frames with d3 and KaTeX. Those pages port to HyperFrames with far less rewriting than to Remotion (which needs them recast as React components driven by `useCurrentFrame()`), consistent with HeyGen's "drops in close to as-is" claim — a vendor claim, but structurally plausible.
- The requirement that timing comes from the presenter's audio (word-timed captions, label cues) means timing should be *data* (a JSON of cue times) consumed by fixed templates. A GUI timeline that lets an operator drag clips is then a correction tool, not the authoring path — and note the project's own rule that narration sets the clock, so free dragging can desync by design.
- The "hand-written per-video build script" pain is not solved by any framework by itself. It is solved by defining a small set of beat templates (question card, counted list, table, labelled figure, derivation, Veo panel, answer page) with a props schema, and having the agent emit only props. Remotion makes this pattern idiomatic (typed props, schema validation); HyperFrames supports it through variables/templates but its culture and skills lean toward free-form agent-written HTML, which is the opposite of deterministic.

### Gaps
- Remotion Studio's visual props editor and Remotion Player (embedding a preview in the team's own dashboard) were not verified from primary docs in this pass.
- No independent review was found of how well HyperFrames Studio's timeline works for non-technical operators in production.
- Whether HyperFrames Studio edits round-trip losslessly into template source (rather than a one-off composition) is unknown.
- Remotion `@remotion/captions` package specifics (word-level timing format, Devanagari handling) were not fetched.

## 7. Licensing and cost for a commercial team of 5-20

### Takeaway
HyperFrames is Apache-2.0 with no seat or render fees; Remotion is free only up to 3 people, so this team needs a Company licence — $25/seat/month for people who build videos, or $0.01 per render with a $100/month minimum for automated pipelines. At 10 videos per operator per day either Remotion plan is small money next to operator salaries, but it is a real recurring obligation and a licence review HyperFrames does not need.

### Cited Findings
- Remotion free licence: "For individuals and companies of up to 3 people". — [remotion.pro licence page](https://www.remotion.pro/license)
- Remotion Company licence, Creators: $25 per seat per month, one seat per user. — [remotion.pro licence page](https://www.remotion.pro/license)
- Remotion Company licence, Automators: $0.01 per render with a $100/month minimum spend; "Developers working on automation projects do not require a Seat." — [remotion.pro licence page](https://www.remotion.pro/license)
- Remotion Enterprise: "Starting at $500 per month". — [remotion.pro licence page](https://www.remotion.pro/license)
- HyperFrames: Apache 2.0, described by HeyGen as "no seat count and no license review". — [HyperFrames vs Remotion guide](https://hyperframes.heygen.com/guides/hyperframes-vs-remotion)
- Motion Canvas, Revideo, Manim Community, ManimGL, MoviePy, editly: MIT. Etro: GPL-3.0. Diffusion Studio core: MPL-2.0. — [motion-canvas](https://github.com/motion-canvas/motion-canvas); [midrender/revideo](https://github.com/midrender/revideo); [ManimCommunity/manim](https://github.com/ManimCommunity/manim); [etro-js/etro](https://github.com/etro-js/etro); [diffusionstudio/core](https://github.com/diffusionstudio/core)
- GSAP, HyperFrames' default animation runtime, is a separate library with its own licence — see gap below. — [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes)

### Inferences
- Remotion cost model for this team (arithmetic on the cited prices): 5 operators x 10 videos x about 25 working days = 1,250 renders/month = $12.50 at $0.01, so the $100 minimum applies: about $100/month, about $1,200/year on Automators. On Creators it would be $25 x seats: $125/month for 5, $500/month for 20. Re-renders and previews may count as renders; which plan applies to an internal content pipeline (rather than a customer-facing app) should be confirmed with Remotion.
- Self-rendered cloud compute for either framework is on the order of $0.02 per video-minute (section 4), versus about $0.10-$0.84 per minute for template SaaS — and SaaS cannot do the maths/diagram work anyway.

### Gaps
- Remotion's full licence text was not readable through the fetch (the docs page returned only navigation); the figures above come from remotion.pro. Edge cases — whether contractors count toward headcount, whether failed or preview renders are billed — are unverified.
- GSAP's current licence terms (it was made free including for commercial use after the Webflow acquisition, per my recollection) were not re-verified in this pass.
- Twick's custom licence terms were not read.

## 8. Migration from Manim: what stays, what moves, and which framework fits

### Takeaway
Most of what is on screen in these videos — captions, question card, counted lists, tables, labelled SVG figures, KaTeX lines, the Veo panel, the answer page and the keyed presenter — is HTML/CSS/SVG layout that a Chromium renderer does better and in one text path; Manim should shrink to a specialist that renders occasional alpha clips (3D, true matched-term derivation morphs). Between the two serious candidates, the evidence favours Remotion for a deterministic template factory with in-framework keying, and HyperFrames for lowest-friction reuse of the existing HTML renderer and for licence simplicity; the deciding measurement (render time on the actual M2 and on Lambda with the presenter video embedded) does not exist in public sources and needs a one-day spike.

### Cited Findings
- HyperFrames' own description of what drops in: "HTML, CSS, and a GSAP or Lottie animation usually drop in close to as-is", whereas for Remotion they are "rewritten as React components". — [HyperFrames vs Remotion guide](https://hyperframes.heygen.com/guides/hyperframes-vs-remotion)
- HyperFrames can import Three.js, Lottie and custom frame adapters, but "libraries requiring autonomous clock control require wrapping or offline frame rendering". — [HeyGen research: HTML to video](https://www.heygen.com/research/html-to-video)
- HyperFrames deterministic capture is Linux-only; macOS falls back to screenshot capture. — [HeyGen research: HTML to video](https://www.heygen.com/research/html-to-video)
- HyperFrames video-heavy compositions fall back to a single worker. — [HeyGen research: HTML to video](https://www.heygen.com/research/html-to-video)
- Remotion provides in-composition chroma key with spill suppression and native alpha video. — [Remotion colorKey docs](https://www.remotion.dev/docs/effects/color-key); [Remotion transparency docs](https://www.remotion.dev/docs/videos/transparency)
- Remotion Lambda renders a 1-minute video in about 19s for about $0.017. — [Remotion Lambda cost examples](https://www.remotion.dev/docs/lambda/cost-example)
- Both HyperFrames and Remotion can output or ingest alpha video (ProRes 4444 / WebM), which is the interchange format for a Manim-rendered insert. — [HyperFrames rendering guide](https://hyperframes.heygen.com/guides/rendering); [Remotion transparency docs](https://www.remotion.dev/docs/videos/transparency)
- Motion Canvas has the built-in equation part-tweening but its last tagged release is Dec 2024, and Revideo's steward has moved on. — [Motion Canvas LaTeX docs](https://motioncanvas.io/docs/latex); [motion-canvas/motion-canvas](https://github.com/motion-canvas/motion-canvas); [YC: Midrender](https://www.ycombinator.com/companies/midrender)
- Manim v0.21.0 is materially faster (Cairo about 2x) and adds Typst, so keeping it as a specialist is not a dead end. — [Manim releases](https://github.com/ManimCommunity/manim/releases)

### Inferences
- **Better as HTML templates (move):** word-timed captions, question card, numbered lists that fill in, tables, pill labels, textbook-traced SVG diagrams with labels attached by anchor name (SVG ids/CSS make this natural), KaTeX equations with a symbol legend, simple "term moves / line rewrites" derivations via GSAP Flip, the Veo clip panel, the answer page, transitions, and the presenter layer. All of these are layout and typography, where Chromium's text stack (one path for Hindi and maths) removes the Pango-versus-LaTeX split entirely.
- **Stays in Manim (or is pre-rendered once):** true 3D (the helix), and derivations that need genuine matched-glyph morphing. Render these as transparent clips and drop them in as assets; do not keep Manim on the per-video critical path.
- **Why the 26-47 minute composite should disappear in either framework:** the browser composites captions, graphics and presenter in one pass per frame, and frame capture parallelises across workers or Lambda chunks; today's cost is a serial ffmpeg filter graph plus a separate screenshot renderer.
- **Fit ranking for this workload (judgement, not measurement):**
  1. *Remotion* — strongest on determinism of templates (typed props), first-party chroma key, mature Lambda with published costs, six years of releases. Costs: licence (about $100+/month), and rewriting the existing HTML/d3/KaTeX pages as React components.
  2. *HyperFrames* — strongest on reuse (the team already writes HTML frames; the presenter vendor is the framework vendor), agent ergonomics, operator-facing Studio timeline, and zero licence cost. Costs: 0.x churn with near-daily releases, macOS is the non-deterministic capture path, embedded video forces single-worker, no documented green-screen key, and an open bug where default worker count halves speed on a GPU.
  3. *Motion Canvas / Revideo* — only choice with built-in equation tweening, but canvas-based text layout and weak maintenance make it a poor base for a production factory.
- A reasonable de-risked path: build two or three beat templates (captions + counted list + labelled figure + presenter) in both Remotion and HyperFrames, render the same 90-second part on the M2 and on Lambda, and compare wall time, RAM, and frame-level determinism across two runs. The public evidence cannot settle this.

### Gaps
- No published case study was found of an edtech or Indic-language team migrating from Manim to Remotion or HyperFrames.
- No measured comparison of the two frameworks on a presenter-video-in-every-frame portrait composition exists in the sources found; all throughput conclusions above are inferences.
- Engineering effort for the migration (person-weeks) cannot be sourced and was not estimated.
- Whether Remotion's licence terms treat this internal pipeline as "Creators" or "Automators" is unconfirmed.
- Frameworks named in the brief but not researched in this pass: Mosaico, Rendley, Rive/Lottie pipelines, After Effects + nexrender/Plainly workflow detail, Blender headless.
