# Automating the planning / storyboarding stage of educational explainer videos with LLMs (state as of October 2026)

Researcher note on method and confidence: ~30 tool calls. Numbers below were read from the primary paper/doc unless marked otherwise. Items marked **[fetch-summary]** were extracted by a small summarising model from the page and not re-read by me; items marked **[read directly]** I read from the PDF tables myself. Several named tools in the brief were NOT reached in the time budget; they are listed under Gaps rather than filled from memory.

---

## 1. What do the best academic / open-source text-to-explainer-video systems do, and what are their measured failure modes?

### Takeaway
Every system that works splits the job into planner -> coder -> critic with an explicit intermediate storyboard, and every one of them reports the same residual weakness: spatial layout, which is the lowest-scoring dimension and the one the LLM judge agrees with humans least on. The two measured levers that moved quality most were (a) the planner/storyboard itself and (b) replacing free coordinates with a small discrete grid of anchors; the one production-scale system (Baidu LASEV) goes further and compiles a structured script through fixed templates.

### Cited Findings

**TheoremExplainAgent (TIGER-Lab, ACL 2025)** [fetch-summary]
- Two agents: a planner producing scene-by-scene story plans + narration, and a coding agent writing Manim, with iterative error-fix retries. Benchmark TheoremExplainBench = 240 theorems, 5 automated metrics. — [arXiv 2502.19400](https://arxiv.org/abs/2502.19400)
- Success rate is extremely model-dependent: o3-mini 93.8%, GPT-4o 55.0%, Gemini 2.0 Flash 14.6%, Claude 3.5 Sonnet v1 2.1% (2025-era models). — [arXiv 2502.19400v2](https://arxiv.org/html/2502.19400v2)
- Retries are what make it work: with 0 fix attempts success is ~7% (easy) / 3% (hard); with 5 attempts 93% / 96%. — [arXiv 2502.19400v2](https://arxiv.org/html/2502.19400v2)
- Element Layout is the lowest dimension (0.57-0.65 on a 0-1 scale) vs Visual Consistency 0.87-0.92 and Logical Flow 0.80-0.89; human-made Manim videos score 0.73 on layout. Reported defects: "overlapping texts, inconsistent sizes, or suboptimal object positioning". — [arXiv 2502.19400v2](https://arxiv.org/html/2502.19400v2)
- RAG over Manim docs HURT: o3-mini success fell 93.8% -> 82.1% and cost rose $1.16 -> $1.72 per video, because retrieved references were "overly generic or lacked relevance". — [arXiv 2502.19400v2](https://arxiv.org/html/2502.19400v2)
- Cost/time per video (o3-mini): ~434k input + ~154k output tokens, $1.16, 1,680 s (~28 min). — [arXiv 2502.19400v2](https://arxiv.org/html/2502.19400v2)
- The automated judge only tracks humans on visual things: Spearman with human ratings 0.72 (Visual Relevance), 0.42 (Element Layout), 0.14 (Accuracy & Depth), 0.16 (Logical Flow), 0.17 (Visual Consistency); inter-rater Krippendorff alpha 0.31-0.56. — [arXiv 2502.19400v2](https://arxiv.org/html/2502.19400v2)
- Dominant code failures: hallucinated Manim functions/signatures, LaTeX errors, ordinary coding errors. — [arXiv 2502.19400v2](https://arxiv.org/html/2502.19400v2)

**Code2Video (Show Lab NUS; arXiv Oct 2025, listed as an ICML 2026 poster)** [fetch-summary]
- Planner (topic -> hierarchical outline -> storyboard of lecture lines paired with animations, plus an external database of reference images/assets), Coder (Manim generated in parallel per section, with "ScopeRefine" debugging), Critic (VLM with visual anchor prompts). — [arXiv 2510.01174](https://arxiv.org/html/2510.01174); [ICML 2026 poster page](https://icml.cc/virtual/2026/poster/65050)
- Visual anchor prompt = the canvas discretised into a **6x6 grid** with fixed coordinate mappings; elements are placed at a point anchor or a region spanning anchors; an occupancy table is maintained so the Critic can detect overlap/occlusion/imbalance. A finer 8x8 grid performed WORSE (clutter). — [arXiv 2510.01174](https://arxiv.org/html/2510.01174)
- ScopeRefine: repair at line+-1 scope first, then the lecture-line block, then regenerate the section. Removing parallelism + ScopeRefine raises time 15.4 -> 149.8 min (9.7x) and tokens 30.8k -> 52.6k; naive retry-only costs 42.9 min (2.8x). — [arXiv 2510.01174](https://arxiv.org/html/2510.01174)
- Ablations on TeachQuiz: removing the Planner costs ~41 points, the external asset database ~30, visual anchors 26.8, the Critic 21.3. So the plan matters about twice as much as the critic. — [arXiv 2510.01174](https://arxiv.org/html/2510.01174)
- Full system ~14-16 min/topic and 19-50k tokens; TeachQuiz 86.0 (Claude Opus 4.1) vs 97.1 human; aesthetics 87.9 vs 99.7 for 3Blue1Brown vs 9.0 for Veo 3 pixel generation. Headline: +40% over direct code generation. — [arXiv 2510.01174](https://arxiv.org/html/2510.01174)
- Limitations: humans still better at storytelling/depth; asset retrieval sometimes returns unusable assets (e.g. black image on dark background). — [arXiv 2510.01174](https://arxiv.org/html/2510.01174)

**LASEV — "Beyond End-to-End Video Models" (Baidu, arXiv Feb 2026)** [fetch-summary] — the closest published analogue to this team's problem (solving K-12 problems as ~2-minute videos with a digital human).
- Four agents: Orchestrating, Solution (step-by-step reasoning), Illustration (optional Python/Manim visual code), Narration. They do NOT emit a video; they emit an **Executable Video Script (EVS)** = pedagogical content P + narration N + alignment/orchestration rules A, which is "deterministically compile[d] via template-driven assembly". — [arXiv 2602.11790](https://arxiv.org/html/2602.11790v1)
- Three heterogeneous critics gate every intermediate artifact: semantic (rubric + few-shot LLM), tool-based (compile/execute), rule-based (structural checks, keyword/function constraints). Ablation: single-agent baseline 42.0% publishable; semantic critique +40 points, tool critique +22.2, rule critique +10.0; full system 92-96% publishable. — [arXiv 2602.11790](https://arxiv.org/html/2602.11790v1)
- Middle-school maths: 96% usable, 96% publishable, but only **58% "perfect"**; error distribution: 4.0% critical (2% solution errors, 2% misread problem), 38% minor presentation issues. — [arXiv 2602.11790](https://arxiv.org/html/2602.11790v1)
- Claimed cost <= $0.07 per 2-minute video (LLM $0.056 with DeepSeek-R1, digital human <= $0.014) and capacity ">1 million videos per day". — [arXiv 2602.11790](https://arxiv.org/html/2602.11790v1)

**ManimAgent (arXiv June 2026)** [fetch-summary]
- Six agents (Storyboarder, Coder, Reviewer for crashes, Visual Reviser, VLM Reviewer scoring keyframes, distillers) plus a dual-channel Episodic Memory Bank: positive channel = success rationales as soft "Reference Examples" (written when VLM score >= 85/100), negative channel = validated failure patterns as hard "Known Pitfalls" (written only on crash->success or a >= 5-point visual improvement). Retrieval top-2 positive + top-3 negative per scene via MiniLM + Faiss. — [arXiv 2606.30296](https://arxiv.org/html/2606.30296v1)
- On 33 held-out tasks with blind human scoring: Pass@1 62.0% (empty memory) -> 84.9% (200 entries); reflection rounds 12.2 -> 6.5; quality 3.26 -> 3.88/5. Static Manim-code RAG reached 83.3% pass but still needed 11.4 rounds. — [arXiv 2606.30296](https://arxiv.org/html/2606.30296v1)
- VLM score vs blind human score: Pearson r = -0.17, Cohen's kappa = -0.07; human inter-rater kappa ~ -0.01 across 54 raters. The authors say this "prevents using VLM scores as primary evidence". — [arXiv 2606.30296](https://arxiv.org/html/2606.30296v1)
- Cost: 36-38k LLM tokens + 20-23k VLM tokens, 19-31 min wall-clock per task. — [arXiv 2606.30296](https://arxiv.org/html/2606.30296v1)

**Paper2Video / PaperTalker (Show Lab, Oct 2025)**
- "Tree Search Visual Choice": because LLMs are insensitive to fine-grained numeric adjustments, on a layout error the system renders several layout variants and has a VLM PICK one rather than asking the LLM to emit a corrected number. — [arXiv 2510.05096](https://arxiv.org/html/2510.05096v2)
- Evaluation metrics: Meta Similarity, PresentArena, PresentQuiz, IP Memory; PPTAgent and PresentAgent are baselines. — [arXiv 2510.05096](https://arxiv.org/html/2510.05096v2)

**Fine-tuned small models for Manim (arXiv Apr 2026)**
- First unified study of 17 open-source sub-30B LLMs across nine training x inference strategies on ManimBench: SFT improves code quality, GRPO (RL) improves visual output and responsiveness to extrinsic feedback during self-correction. — [arXiv 2604.18364](https://arxiv.org/html/2604.18364)

### Inferences
- The field's architecture has converged; this team's "visual director -> beats file -> render" is already the same shape. What the papers add is evidence about WHERE the leverage is: plan (41 pts) > assets (30) > anchors (27) > critic (21) in Code2Video; semantic critic (+40) > compile critic (+22) > rule critic (+10) in LASEV.
- The 6x6 anchor result generalises to the team's existing "anchor table by name" for diagram labels: the planner should choose among named slots, never emit coordinates. Coarser is better than finer.
- Paper2Video's "render N variants, let the VLM choose" matches what a low-technical operator can do too: pick from 3 stills rather than describe a fix. That converts review from authoring to selection.
- LASEV's 58% perfect / 38% minor-presentation-issue split at 96% publishable is the realistic ceiling for a fully automatic pipeline. A team whose bar is "user catches card tilt by eye" should expect roughly 4 in 10 plans to still need a human touch, and should design the touch to be seconds long.
- TheoremExplainAgent's RAG regression vs ManimAgent's memory gain is consistent: generic documentation retrieval hurts, retrieval of the system's OWN approved outputs and validated pitfalls helps.
- All the academic systems take 14-31 minutes and are topic->video. None of them is conditioned on a pre-recorded narration with word timings, none handles Devanagari, and none traces a textbook figure. Those three are this team's actual constraints and are unaddressed in the literature surveyed.

### Gaps
- Not reached in this session, so no sourced claims: Generative Manim, manim-agent, Math-To-Manim, "3b1b-style" agents, ManimML, Manim MCP servers, PresentAgent and PPTAgent internals, and any "Explain"/"video-as-code" paper by that exact name. They should be treated as unreviewed, not as irrelevant.
- I did not re-read the Code2Video, TEA, LASEV or ManimAgent tables myself; numbers come from a summarising fetch and should be spot-checked before being quoted externally.
- LASEV's ">1 million videos/day" is a capacity claim by the vendor in a preprint; I found no independent confirmation.
- No system surveyed reports results on Hindi/Devanagari or Indian curricula.

---

## 2. Template / DSL versus free-form code generation

### Takeaway
There is no clean head-to-head benchmark of "schema-validated scene spec" vs "free-form Manim", but the indirect evidence all points one way: free-form generation needs ~5 repair rounds to reach >90% render success and still scores worst on layout, while the only system operating at production scale compiles a structured script through templates. HeyGen's HyperFrames and the Remotion ecosystem have made "HTML/props as the IR, deterministic renderer underneath" the mainstream agent pattern in 2026.

### Cited Findings
- Free-form Manim: 7% first-attempt success rising to 93% only after 5 repair attempts (TEA). — [arXiv 2502.19400v2](https://arxiv.org/html/2502.19400v2)
- Free-form Manim with self-evolving memory still averages 6.5 reflection rounds and 19-31 minutes per task (ManimAgent). — [arXiv 2606.30296](https://arxiv.org/html/2606.30296v1)
- LASEV compiles an Executable Video Script deterministically "via template-driven assembly"; Illustration (generated Manim) is an OPTIONAL component of the script rather than the whole video. — [arXiv 2602.11790](https://arxiv.org/html/2602.11790v1)
- HyperFrames (HeyGen, Apache-2.0): a video is an HTML file; elements carry `data-start`, `data-duration`, `data-track-index`; animations (GSAP, CSS, Lottie, WAAPI) must be seekable and exposed on `window.__timelines`; headless Chrome seeks frame-by-frame and FFmpeg encodes, giving "same input, same frames, same output". CLI has `preview` (live reload), `lint`/`check`, `snapshot` (frame inspection) and `render`; a catalog of reusable blocks installs with `npx hyperframes add`. Ships 21 agent skills. [fetch-summary; star count reported as 58.4k, not independently checked] — [github.com/heygen-com/hyperframes](https://github.com/heygen-com/hyperframes)
- Stated rationale for HTML over React: LLMs generate HTML better than framework-specific composition models such as Remotion's `useCurrentFrame`. This is the vendor's/commentators' claim, not a measured result. — [noqta.tn write-up](https://www.noqta.tn/en/blog/heygen-hyperframes-html-to-mp4-ai-agent-video-2026)
- Storyboard IR examples in papers: Code2Video's outline -> storyboard of (lecture line, animation) pairs with 6x6 anchors; LASEV's EVS (P, N, A); VLM-SlideEval's flat element schema (`texts[]`, `rects[]`, `lines[]`, `images[]`, `tables[]` with x,y,w,h in a fixed 960x540 frame). — [arXiv 2510.01174](https://arxiv.org/html/2510.01174); [arXiv 2602.11790](https://arxiv.org/html/2602.11790v1); [arXiv 2510.22045](https://arxiv.org/pdf/2510.22045)
- Verifiable layout metrics as a reward: AeSlides defines collision, whitespace, aspect-ratio and balance metrics computed from the DOM/rendered slide and uses them as RL rewards instead of VLM opinion. [fetch-summary; specific numbers not extracted] — [arXiv 2604.22840](https://arxiv.org/pdf/2604.22840)

### Inferences
- Recommended IR for this team (my synthesis, not a published schema): one `plan.json` per part with `strategy` (enum: diagram_led | derivation | progressive_list | comparison | quiet), and `beats[]`, each beat = `{cue: {caption_line, word_index}, template: enum, slot: enum (named anchor), props: {...}, presenter: enum(default|partial|hidden), motion: enum}` with `template: "none"` as a first-class value so "no graphic" is a choice the schema forces the model to make explicitly per window. Timing is NEVER in the plan; it is resolved from the alignment file by `(caption_line, word_index)`.
- Templates should be the closed set the team already renders (list-fill-in, numbered table, derivation step with symbol legend, traced figure with named-anchor labels, answer page, Veo panel). Because the existing renderer has both Manim and an HTML/Playwright path, the same plan can be compiled to an HTML proxy for preview and to the final renderer for delivery.
- Free-form codegen should survive only as an escape hatch for a beat tagged `custom`, mirroring LASEV's optional Illustration component; such beats get routed to a skilled person, so the operator's queue contains only template-only plans.
- The plan being a closed enum over templates also makes the rule-based critic nearly free: "question says सचित्र and no `traced_figure` beat exists" is a JSON query, not a vision call.

### Gaps
- No paper found that directly measures first-pass success or human review time for constrained scene-spec vs free-form generation on the same tasks. The claim is supported only by cross-paper comparison.
- Remotion props + Zod schemas, Remotion's own agent skills, Shotstack JSON and Motion Canvas were not fetched; no sourced claims about them here.
- HyperFrames' handling of Devanagari shaping, KaTeX/MathJax and word-timestamp-driven captions was not verified.

---

## 3. Structured outputs, decomposition, caching and cost for long plans

### Takeaway
Claude's structured outputs (constrained decoding) are GA across the current model line and guarantee schema-valid JSON, but the grammar has hard complexity limits that a naive "one giant plan schema" will hit; the practical pattern is small required-field schemas per part with enums for templates/slots, and semantic rules checked in code afterwards.

### Cited Findings (all from Anthropic's docs, [fetch-summary])
- Supported models include claude-opus-5-5, claude-sonnet-5-5, claude-haiku-5-5, and the 4.5-4.8 line; two mechanisms: JSON outputs via `output_config.format` and strict tool use via `strict: true`; they can be combined. — [Claude docs: structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
- Hard limits per request: 20 strict tools; **24 optional parameters total** across all strict schemas; **16 parameters with union types** (`anyOf` / `["string","null"]`). Exceeding internal grammar size gives "Schema is too complex for compilation"; compilation timeout 180 s. — [Claude docs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
- Unsupported: recursive schemas, `minimum`/`maximum`/`multipleOf`, `minLength`/`maxLength`, array constraints beyond `minItems` 0 or 1, `additionalProperties` other than false, external `$ref`, regex lookaheads/backreferences/`\b`. — [Claude docs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
- Compiled grammars are cached 24 h from last use; changing schema structure invalidates it, changing only `name`/`description` does not. Changing `output_config.format` invalidates the PROMPT cache for that thread. — [Claude docs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
- `max_tokens` truncation yields output that may not match the schema; refusals return 200 with `stop_reason: "refusal"` and non-conforming output. Enum/const capitalisation is NOT guaranteed (compare case-insensitively). — [Claude docs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
- Structured outputs are also exposed in the Agent SDK. — [Claude Agent SDK docs](https://platform.claude.com/docs/en/agent-sdk/structured-outputs)
- Reference costs from the literature for whole-video agent runs: $1.16 and 588k tokens (TEA, o3-mini); 19-50k tokens (Code2Video); ~57-61k tokens (ManimAgent); $0.056 LLM cost (LASEV, DeepSeek-R1). — [arXiv 2502.19400v2](https://arxiv.org/html/2502.19400v2); [arXiv 2510.01174](https://arxiv.org/html/2510.01174); [arXiv 2606.30296](https://arxiv.org/html/2606.30296v1); [arXiv 2602.11790](https://arxiv.org/html/2602.11790v1)

### Inferences
- Schema design rules that follow directly from the limits: make every field `required` (use an explicit `"none"` enum value instead of an optional field — which also happens to encode "no graphic is a valid answer"); avoid per-template `anyOf` unions with many branches (16-union cap) — prefer a flat beat with `template` enum + a small generic `props` object, then validate template-specific props in Pydantic/Zod after the call; no numeric ranges in the schema, so word indices and counts must be range-checked in code.
- One request per part (the team's videos have 1-3 parts) keeps output well under truncation risk and lets a failed part be re-planned alone. Keep the schema byte-stable across videos so the 24 h grammar cache and the prompt cache both hit; put house rules, template catalogue and few-shot approved plans in the cached prefix, and only the question + caption lines in the suffix.
- Since enum casing is not guaranteed, template and slot names should be lower_snake_case ASCII single tokens.
- Decomposition that mirrors the evidence in section 1: (1) strategy classifier on the question wording (deterministic keyword rules first, LLM only on ties); (2) per-part planner with structured output; (3) rule critic in code; (4) semantic critic LLM with a rubric (caption-repetition, quiet-ratio, label named-when-spoken); (5) only then stills. This is LASEV's three-critic gate applied before any render.
- A plan of this kind is a few thousand output tokens; by analogy to the 19-60k-token whole-pipeline figures above, planning cost per video should be cents, not dollars — but see Gaps, I did not compute it from current prices.

### Gaps
- Current per-token prices, batch-API discount, and prompt-cache read/write multipliers for the 5.5 model line were NOT fetched; no cost-per-plan figure is given for that reason. The docs page fetched lists no stated incompatibility between structured outputs and the Batch API or extended thinking, but absence in a summary is not confirmation.
- OpenAI and Gemini structured-output limits were not checked.
- No published benchmark found on structured-output reliability for long (100+ element) plans specifically.

---

## 4. Automatic critics: VLM review, layout solvers, rubric judges

### Takeaway
VLMs are good at reading what is on a frame and poor at pixel geometry, and VLM scores of "quality" do not track human judgement well; the consistent recommendation in 2025-2026 work is to compute collisions, clipping and blank frames deterministically from the renderer's own geometry and reserve the VLM for semantic questions (wrong label on the wrong part, figure doesn't match the sentence).

### Cited Findings
- VLM-SlideEval (Microsoft PowerPoint AI, NeurIPS 2025 workshop) [read directly]: on element extraction from slide images, best end-to-end matching F1 is 0.72 (o3), GPT-5 0.71-0.72, GPT-4.1 0.59, GPT-4o 0.44; text content F1 0.76-0.78 for the best models; geometry error (1-IoU, lower is better) is ~0.55-0.57 even for the best models; font-family accuracy 0.17-0.42. — [arXiv 2510.22045](https://arxiv.org/pdf/2510.22045)
- Same paper: schema-valid parse rate collapses with slide complexity for older models (GPT-4.1: ~93% for <= 8 elements, 72.1% for 8-16, 32.8% for 16-32, 18.2% for >= 32) while o3/GPT-5 stay at 99.5%+. — [arXiv 2510.22045](https://arxiv.org/pdf/2510.22045)
- Same paper: for judging geometry/style degradation, a coarse 5-point scale is MORE consistent than a 100-point scale with no fidelity loss (consistency 0.87-0.95 vs 0.62-0.73 for geometry); models disagree with each other most on text quality (best pair Spearman ~0.55); slide-order/narrative recovery is near chance (Kendall tau 0.04-0.12). Conclusion: use "verifiable and accurate signals to gate selection". — [arXiv 2510.22045](https://arxiv.org/pdf/2510.22045)
- TEA: LLM/VLM judge vs human Spearman 0.42 on Element Layout, 0.72 on Visual Relevance, <= 0.17 on accuracy/logic/consistency. — [arXiv 2502.19400v2](https://arxiv.org/html/2502.19400v2)
- ManimAgent: VLM keyframe score vs blind human score r = -0.17. — [arXiv 2606.30296](https://arxiv.org/html/2606.30296v1)
- Code2Video: the Critic is effective when it is given structure — the 6x6 anchor grid and an occupancy table — rather than asked to eyeball; anchors are worth 26.8 TeachQuiz points and the Critic 21.3. — [arXiv 2510.01174](https://arxiv.org/html/2510.01174)
- Paper2Video: selection among rendered variants works better than asking for numeric corrections. — [arXiv 2510.05096](https://arxiv.org/html/2510.05096v2)
- Deterministic alternatives in the slide literature: SlidesGen-Bench uses a layout-analysis detector to get bounding boxes and computes metrics from them, reporting only 1.2% of errors falsely penalised due to extraction failures on dense/overlapping layouts [search snippet, not read]; AeSlides computes collision/whitespace/aspect/balance from the DOM; PPTBench documents that LLMs "frequently overlook layout constraints and cause content overlaps". — [arXiv 2601.09487](https://arxiv.org/html/2601.09487v2); [arXiv 2604.22840](https://arxiv.org/pdf/2604.22840); [arXiv 2512.02624](https://arxiv.org/html/2512.02624v1)
- LASEV's rubric-based semantic critic with few-shot examples was the single largest contributor (+40 points publishable rate). — [arXiv 2602.11790](https://arxiv.org/html/2602.11790v1)
- OpenMontage's post-render self-review is deterministic: ffprobe validation, frame extraction at 4 positions, audio-level analysis, subtitle verification, plus a 6-dimension "slideshow risk" score before compose. [fetch-summary] — [github.com/rahulrao85/OpenMontage](https://github.com/rahulrao85/OpenMontage)

### Inferences
- I found NO published accuracy figure for a VLM detecting a specific layout defect (overlap / clipping / label on wrong part) as a binary classifier. The nearest proxies — geometry 1-IoU ~0.55 for the best models, 0.42 layout correlation with humans, negative correlation in ManimAgent — say a VLM should not be the gate for geometric defects.
- Both of the team's renderers already know every element's bounding box (Manim mobjects; DOM rects in the Playwright renderer). A geometry pass over the PLAN'S resolved boxes — pairwise intersection, frame bounds, presenter-zone floor per `presenter` mode, caption band, minimum glyph height — catches overlap/clipping/blank before any pixel is rendered and with 100% recall by construction. With named slots, most collisions cannot be expressed in the first place.
- Blank-screen and frozen-screen are timeline properties, also computable from the plan: longest window with no visible template, and longest window with a visible template but no state change.
- Use the VLM where geometry cannot answer: "does this label's leader end on the part it names", "does the traced figure match the question", "is this tilt/handwriting acceptable". Ask binary or 5-point questions (per VLM-SlideEval), one defect per question, on a contact sheet of stills, and prefer pick-one-of-N over score-this.
- A pedagogy judge should be calibrated against the team's own approved/rejected plans before it is trusted; the literature gives no reason to expect an uncalibrated judge to agree with a human reviewer.

### Gaps
- No benchmark found on VLM defect detection for Devanagari text (conjunct mis-shaping, matra ordering) — exactly the silent failure the team has hit.
- Gemini video-understanding (as opposed to still-frame) accuracy for temporal defects such as label-audio desync was not researched.
- Constraint-based auto-layout solvers (Cassowary/kiwi, yoga/flexbox as a solver, Manim `arrange`/`next_to` based layout) were not researched; the recommendation above rests on reasoning rather than a cited evaluation.
- AeSlides and SlidesGen-Bench numbers were not read from the PDFs.

---

## 5. Fast preview loops / "animatic first"

### Takeaway
The open-source agent video stacks of 2026 all gate rendering behind a human-approved storyboard contact sheet, and the HTML-based renderers give a live-reload preview and single-frame snapshot for free; nothing in the literature renders first and reviews after.

### Cited Findings
- OpenMontage pipeline: research -> proposal -> script -> scene_plan -> assets -> edit -> compose, with enforced human approval at proposal, script, scene plan, generated assets and pre-publish; asset generation pauses on a scene-by-scene contact sheet ("Backlot") showing each take, its prompt, per-asset cost and quality score; plans are JSON checkpoints; superseded checkpoints are archived. [fetch-summary; repo metrics unreliable in the fetch] — [github.com/rahulrao85/OpenMontage](https://github.com/rahulrao85/OpenMontage)
- HyperFrames: `preview` live-reload in browser, `snapshot` for frame inspection, `lint`/`check` for validation before `render`; the stated authoring loop is prompt -> preview in the browser studio -> render. — [github.com/heygen-com/hyperframes](https://github.com/heygen-com/hyperframes); [noqta.tn write-up](https://www.noqta.tn/en/blog/heygen-hyperframes-html-to-mp4-ai-agent-video-2026)
- Commercial practice (agency blog, low evidentiary weight): creative directors pick concept directions and clients approve style frames before generation. — [Lemonlight](https://www.lemonlight.com/blog/human-in-the-loop-ai-video-production/)
- An edtech trade article frames AI learning-video production as a sequence of reviewable quality gates each requiring a qualified person to inspect and approve. (Opinion piece, not data.) — [EdTechReview](https://www.edtechreview.in/elearning/6-human-quality-gates-for-ai-generated-learning-videos/)
- Academic systems have no preview step and take 14-31 min per video end to end. — [arXiv 2510.01174](https://arxiv.org/html/2510.01174); [arXiv 2606.30296](https://arxiv.org/html/2606.30296v1)

### Inferences
- The 30-minute re-render cost comes from the plan being code. If the plan is data and templates are deterministic, three preview tiers become available: (1) text scene script (already the team's rule), (2) a contact sheet with one still per beat at the END state of that beat, rendered through the HTML/Playwright path in seconds, (3) a scrubbable in-browser animatic with the real audio where each beat is the template's final state popped in at its aligned cue time. Tier 3 is what catches label-sync and frozen-screen problems, and needs no Manim.
- Because templates are parametrised, a visual change after approval is a prop edit; re-render only the affected beat segment and re-concat rather than the whole video (the pipeline already conforms per-segment to audio).
- The contact sheet doubles as the VLM critic's input and the operator's approval surface, so the model and the human look at the same artifact.

### Gaps
- No published description found of an edtech team's animatic tooling specifically; evidence here is from general-purpose agent video projects and agency blogs.
- Manim-specific fast-preview techniques (low-quality flag, last-frame-only render, section caching, OpenGL renderer) were not researched in this session.

---

## 6. Word-level forced alignment for Hindi narration

### Takeaway
Because the script is known, this is forced alignment, not ASR, and the peer-reviewed evidence is unambiguous for English that classic HMM aligners (MFA) beat ASR-derived timestamps by a wide margin, with WhisperX worst; for Hindi there is no published head-to-head, so the choice is between a CTC aligner with a Hindi-native acoustic model (MMS or IndicWav2Vec-Hindi) and ElevenLabs' hosted forced-alignment endpoint, and it has to be settled on the team's own audio.

### Cited Findings
- MFA 3.0 benchmark paper (McAuliffe et al., June 2026) [read directly, Table 4], word-boundary accuracy within 10/25/50/100 ms on TIMIT: MFA ARPA 3.0 44.99/66.50/91.61/98.38 (mean error 19.93 ms); MMS 13.05/26.52/63.73/95.91 (mean 43.06 ms); **WhisperX 1.95/4.21/15.55/53.98 (mean 110.04 ms)**; NeMo Forced Aligner 7.61/15.50/38.23/70.03 (mean 78.24 ms); MAPS (neural, alignment-specific) 54.77/75.60/91.97/97.61. Buckeye (spontaneous) shows the same ordering: MFA ARPA 3.0 91.35% within 50 ms, MMS 61.85%, WhisperX 13.48%, NeMo 35.81%. — [arXiv 2606.18466](https://arxiv.org/pdf/2606.18466)
- Same paper's explanation: neural ASR systems "are trained to produce correct output strings rather than precise frame-level alignments, and CTC-based systems in particular collapse across different alignments for the same string". — [arXiv 2606.18466](https://arxiv.org/pdf/2606.18466)
- Same paper: MFA 3.0's pretrained-model table lists ~20 languages (Bulgarian ... Vietnamese, English including an India dialect); **Hindi is not in that table**. Dictionary coverage is extended to 34 more languages via VoxCommunis, and adaptation/remapping from the Global English model works (Korean: 21.8 -> 15.9 ms mean error after adaptation). Aligners "assume the transcript and pronunciations are correct... even small deviations can sometimes lead to catastrophic misalignments". — [arXiv 2606.18466](https://arxiv.org/pdf/2606.18466)
- Conflicting WhisperX numbers: the Technion MWA paper (June 2026) [read directly, Table 3], quoting Rousso et al. Interspeech 2024, gives TIMIT word accuracy at 10/25/50/100 ms as MFA 41.6/72.8/89.4/97.4, MMS 18.6/43.5/75.7/94.7, **WhisperX 22.4/52.7/82.4/94.2**, NVIDIA Canary-1B 9.23/23.11/44.23/72.81, and their MWA 58.0/81.3/91.6/97.8. — [arXiv 2606.10675](https://arxiv.org/pdf/2606.10675); contradicted on WhisperX by [arXiv 2606.18466](https://arxiv.org/pdf/2606.18466), which attributes differences to evaluating BEGIN rather than END timestamps ("resulting in some differences in precise numbers").
- MWA (MMS + unsupervised phoneme-boundary features + learned DP) needs no G2P and was trained on English only; on unseen languages it is mixed: Hebrew 61.1% within 25 ms vs MMS 41.3% but worse than MMS at 100 ms (81.4 vs 94.7); German on par with MFA. No Hindi/Indic evaluation. Code "will be released upon acceptance". — [arXiv 2606.10675](https://arxiv.org/pdf/2606.10675)
- NVIDIA Canary-1B used as an aligner is poor: 44.23% within 50 ms on TIMIT. — [arXiv 2606.10675](https://arxiv.org/pdf/2606.10675)
- ElevenLabs Forced Alignment API: Hindi is in the supported list (29 languages); takes audio + plain-string transcript; max 3 GB / 10 hours; no diarization; priced "same rate as the Speech to Text API". No accuracy claim is published. Third-party resellers list about $0.22 per audio-hour [reseller figure from a search snippet, not ElevenLabs' own price]. — [ElevenLabs docs](https://elevenlabs.io/docs/overview/capabilities/forced-alignment); [fal.ai listing](https://fal.ai/models/fal-ai/elevenlabs/forced-alignment/llms.txt)
- Hindi-native CTC aligner, local: `parseh/aligner-hi` is `ai4bharat/indicwav2vec-hindi` converted to int8 ONNX (Apache-2.0), run with NumPy + ONNX Runtime and CTC Viterbi for word or character spans on 16 kHz mono. Its only published "accuracy" is a self-consistency check on espeak-generated audio, explicitly "not a real-speech accuracy claim". — [Hugging Face: parseh/aligner-hi](https://huggingface.co/parseh/aligner-hi)
- AI4Bharat IndicMFA: an MFA-based aligner for Indic languages that replaces G2P with grapheme-to-grapheme, "focusing on letter-wise alignment". [search snippet; repo not read] — [github.com/AI4Bharat/IndicMFA](https://github.com/AI4Bharat/IndicMFA)
- AI4Bharat IndicConformer covers all 22 official Indian languages for ASR; users have asked how to run NeMo Forced Aligner on it (open HF discussion, no confirmed recipe seen). — [github.com/AI4Bharat/IndicConformerASR](https://github.com/AI4Bharat/IndicConformerASR); [HF discussion](https://huggingface.co/ai4bharat/indic-seamless/discussions/5)

### Inferences
- What accuracy is needed: a label popping on the word that names it is perceptually fine within about +-80-100 ms (2-3 frames at 30 fps). On English read speech, MMS-style CTC alignment puts ~95% of word starts within 100 ms and MFA ~98%; WhisperX in its default configuration is the riskiest choice (54-94% depending on which paper and which boundary). HeyGen/TTS narration is clean read speech, the easy case.
- WhisperX's default Hindi alignment model is a community wav2vec2 checkpoint rather than a first-party one, so its Hindi quality is specifically uncertain (background knowledge, not verified this session); the team's own memory note that HeyGen's SRT is off by up to 2.2 s shows vendor timestamps cannot be assumed.
- Recommended order to trial, cheapest first: (1) local CTC forced alignment with a Hindi acoustic model — `ctc-forced-aligner`/torchaudio `forced_align` with MMS, or the IndicWav2Vec-Hindi ONNX aligner — which runs on CPU on an 8 GB Mac since it is a single wav2vec2 forward pass over 2 minutes of audio; (2) ElevenLabs forced alignment as a hosted cross-check (the team already uses ElevenLabs; if narration is ElevenLabs TTS, the TTS-with-timestamps response gives character timings at synthesis time and makes alignment unnecessary — background knowledge, verify in their docs); (3) IndicMFA / MFA with an adapted model if sub-50 ms is ever needed.
- Text normalisation is the real failure source, not the model: the aligner needs the transcript exactly as spoken. The team's rule that spoken lines contain no digits or symbols is exactly the precondition; the remaining hazards are English loanwords written in Latin inside a Devanagari line, the danda, and nukta/chandrabindu variants missing from a model's vocabulary. Normalise to the model's character set and keep a map back to display tokens.
- Use two aligners and flag any word where they disagree by more than ~150 ms; a cue word in a flagged region goes to the operator. Per-word CTC confidence gives the same signal from one model.
- Build a 10-minute gold set once (hand-mark ~300 cue words in a waveform editor on real HeyGen audio) and measure each candidate at 50/100 ms. This is an afternoon and replaces every assumption above.

### Gaps
- **No published Hindi word-boundary accuracy numbers were found for any aligner** (MFA, MMS, WhisperX, IndicWav2Vec, IndicConformer, ElevenLabs, or others). All quantitative figures above are English (TIMIT/Buckeye), with Japanese/Korean/Hebrew/Dutch/German side results.
- Not researched: faster-whisper large-v3/turbo word timestamps, ElevenLabs Scribe v2 accuracy, Deepgram, AssemblyAI, Sarvam Saaras, NVIDIA Parakeet multilingual, and CPU/Apple-Silicon speed figures for any of them. No speed benchmarks are cited because none were read.
- ElevenLabs' first-party price for forced alignment was not confirmed (docs only say it equals the Speech-to-Text rate).
- Whether MFA 3.0 has a usable Hindi acoustic model/dictionary (as opposed to IndicMFA) was not confirmed.
- A "Speech-to-Text Forced Alignment Benchmark" (ResearchGate, 2025) and BFA (arXiv 2509.23147) surfaced in search but were not read.

---

## 7. Automatic figure handling: extraction, vectorisation, label anchors

### Takeaway
Raster-figure-to-editable-SVG became a real capability in 2026 (VFig, with frontier VLMs scoring higher still on its benchmark), but the published evaluations are on clean digital scientific figures with Latin text; for scanned Hindi textbook line art, classical tracing still wins on pixel fidelity and the unsolved part — which label names which part, and where its leader line ends — has no off-the-shelf benchmarked solution that I found.

### Cited Findings
- VFig (RAIVN Lab, arXiv Mar 2026): fine-tunes 4-8B VLMs (Qwen3-VL, InternVL3.5) to convert complex figure rasters into SVG built from semantic primitives; RL rewards include connectivity ("whether arrows and lines connect the correct endpoints") and details (text accuracy, font/stroke/colour). Code at github.com/RAIVNLab/VFig; models/data promised. [fetch-summary] — [arXiv 2603.24575](https://arxiv.org/html/2603.24575v1)
- VFig-Bench (392 scientific figures): VLM-judge score / LPIPS — Gemini 3 Pro 0.932 / 0.303; GPT-5.2 0.858 / 0.364; VFig 0.829 / 0.212; StarVector-8B 0.548 / 0.380. **VTracer has the best pixel fidelity (LPIPS 0.092)** but outputs "many unconstrained Bezier paths instead of editable primitives". — [arXiv 2603.24575](https://arxiv.org/html/2603.24575v1)
- VFig's stated weak spots: natural images, heavy textures and complex maths "resist clean SVG representation"; equations were filtered out of training as better suited to LaTeX. Nothing on scans or non-Latin text. — [arXiv 2603.24575](https://arxiv.org/html/2603.24575v1)
- A "Multimodal OCR" model (arXiv Mar 2026) claims higher image-to-SVG reconstruction quality than Gemini 3 Pro across charts, UI, scientific figures and chemical structure diagrams. [search snippet only] — [arXiv 2603.13032](https://arxiv.org/html/2603.13032v1)
- Other benchmarks that exist: SVG-Bench/StarVector (image-to-SVG, diagrams), Plot2XML (247 scientific diagrams with verified structural annotations), VGBench. [search snippets] — [StarVector](https://starvector.github.io/starvector/); [Draw with Thought, arXiv 2504.09479](https://arxiv.org/pdf/2504.09479)
- Labelled-part detection is an old, specifically studied problem in patents: a competition on detecting figures and part labels in patent drawings (2014). — [arXiv 1410.6751](https://arxiv.org/pdf/1410.6751)
- Relevant negative evidence on VLM geometry: best VLMs reach only ~0.45 IoU on element boxes in slides. — [arXiv 2510.22045](https://arxiv.org/pdf/2510.22045)

### Inferences
- The team's rule "figures are traced from the textbook scan, not generated or redrawn" is supported by VFig-Bench: tracing (VTracer) is 2-3x closer in LPIPS than any generative model. The generative models' advantage — editable primitives — matters for only one thing here: separating labels and leader lines from the drawing.
- A hybrid pipeline is the natural design (my proposal, each step individually standard but not benchmarked end-to-end on this material): (1) OCR the scan with word boxes to find every text region; (2) mask text out and trace the remaining line art with potrace/vtracer — the drawing stays pixel-faithful; (3) detect leader lines as thin straight/near-straight strokes with one endpoint adjacent to a text box (Hough/LSD on the skeleton), and take the FAR endpoint as the anchor on the part; (4) store `anchor_table[label_name] = (x, y)` in figure-normalised coordinates, which is the structure the team already uses; (5) have a VLM verify each (label, anchor) pair on a crop — a yes/no question it is good at — and route only the failures to a human.
- Labels are then re-typeset in Devanagari at render time from the anchor table, so OCR errors in the label TEXT do not matter as long as the box is found; the canonical label strings come from the answer/script, matched to OCR output fuzzily.
- A one-time click-to-fix UI over the auto-detected anchors (drag a dot) is the right fallback; with a per-chapter figure library (section 8) each figure is fixed once and reused for every PYQ on that chapter.
- The audio-sync rule composes with this: each anchor's label name is matched against the aligned transcript to get its cue word; labels with no spoken match are surfaced as "unspoken — declare", which is the team's existing preflight rule.

### Gaps
- Not researched this session: Mathpix figure-crop quality, DocLayout-YOLO, SAM 2/3 on line art, Surya / PaddleOCR / Gemini accuracy on Hindi labels in diagrams. No sourced claims are made about them.
- No benchmark found for leader-line detection or label-to-part association on textbook biology/physics/chemistry diagrams, in any language.
- No evaluation of any figure-vectorisation model on scanned (noisy, skewed, halftoned) sources or Devanagari text.
- VFig weights' actual availability and licence for commercial use were not confirmed beyond "will publicly release".

---

## 8. Retrieval and reuse of approved plans and figures

### Takeaway
The one controlled study (ManimAgent) shows that retrieving the system's own past successes and validated failures roughly halves repair rounds and lifts human pass rate from 62% to 85% within 200 entries, while generic documentation RAG has been shown to hurt.

### Cited Findings
- ManimAgent: memory of the system's own outputs, split into soft positive examples and hard negative constraints, top-2 positive + top-3 negative per scene, MiniLM embeddings + Faiss; Pass@1 62.0 -> 84.9%, reflection rounds 12.2 -> 6.5, gains monotone across 0/50/100/200 entries. — [arXiv 2606.30296](https://arxiv.org/html/2606.30296v1)
- Write-gating matters: negatives are stored only when a causal improvement was observed (crash->success or >= 5-point gain); lessons are stored as distilled rationales, not literal diffs, to transfer across scenes. — [arXiv 2606.30296](https://arxiv.org/html/2606.30296v1)
- Known failure modes of the memory: "memory rot" when the judging model changes, near-duplicate accumulation, validated only at O(100) entries. — [arXiv 2606.30296](https://arxiv.org/html/2606.30296v1)
- Generic RAG over library docs reduced success 93.8 -> 82.1% (TEA). — [arXiv 2502.19400v2](https://arxiv.org/html/2502.19400v2)
- An external curated asset database was the second-largest contributor in Code2Video (-30 TeachQuiz points when removed), but uncurated retrieval sometimes returned unusable assets. — [arXiv 2510.01174](https://arxiv.org/html/2510.01174)

### Inferences
- The team already has the raw material ManimAgent had to synthesise: human-approved plans (positive channel) and a written ledger of caught defects (negative channel: bug-ledger, MEMORY.md entries, preflight rules). Human approval is a far better write-gate than a VLM score, given the VLM-human correlations in section 4.
- Because MP Board PYQs cluster heavily by chapter and by question verb, exact-key retrieval beats embeddings as the first stage: key = (subject, chapter, strategy, marks). Embedding search over beat text is the fallback for cross-chapter analogues ("progressive list of 4 factors").
- Three reusable libraries, in order of payoff: (a) figures with their anchor tables, keyed by textbook figure — a new question on the same chapter reuses the traced figure and only re-cues labels to the new audio; (b) approved plans as few-shot examples for the same strategy; (c) the pitfalls list as hard constraints in the cached system prompt and, wherever possible, promoted into code checks.
- Keep 2-3 retrieved examples, not more — both ManimAgent's top-2 and TEA's RAG regression argue against stuffing context.

### Gaps
- No published work found on plan/beat retrieval for curriculum-aligned question banks specifically, or on embedding models for Hindi pedagogical text in this role.
- ManimAgent's result is on 33 probe tasks with chance-level human inter-rater agreement; treat the magnitude as indicative.

---

## 9. Published throughput numbers and human-in-the-loop checkpoints

### Takeaway
Reliable, independently verified videos-per-person-per-day figures essentially do not exist; the only hard data is from Baidu's preprint (fully automatic, 96% publishable, 58% perfect) and everything else is vendor or agency marketing — but those marketing numbers do put 10 two-minute videos per operator per day inside the range others claim.

### Cited Findings
- Baidu LASEV: claimed capacity >1M videos/day at <= $0.07 per 2-minute video, no manual editing in production; quality measured by certified experts on a 0-3 rubric: 96% publishable (score >= 2), 58% perfect (score 3) on middle-school maths, 4% critical errors (wrong solution or misread problem). — [arXiv 2602.11790](https://arxiv.org/html/2602.11790v1)
- Vendor blog (Frameo, low reliability): avatar tools produce "15 to 30" short social clips in a focused workday; narrative shorts with consistent characters 2 to 5 per day; one cited case went from a couple of videos per week to 10-15 per day "using automated storyboarding". [search snippet] — [frameo.ai](https://frameo.ai/blog/ai-video-tool-content-production-capacity/)
- Vendor-reported case (via TechSmith/aggregated snippet): Asia Pacific University lecturers generate 3-5 minute educational videos in 15-30 minutes. [search snippet, vendor-sourced] — [TechSmith](https://www.techsmith.com/blog/create-training-videos-with-ai/)
- A freelancer case study headline claims an AI pipeline "cut content time by 97%" using Claude API scripts + Make.com + Veo 3.1 Fast / Grok Imagine. [headline only, unverified] — [michaelkristof.com](https://www.michaelkristof.com/project/ai-video-production-pipeline-case-study/)
- Checkpoint structure in an open-source agent studio: five enforced approval gates (proposal, script, scene plan, generated assets, pre-publish), per-action cost approval threshold ($0.50 default) and total budget cap ($10 default). — [github.com/rahulrao85/OpenMontage](https://github.com/rahulrao85/OpenMontage)
- Academic per-video wall-clock, fully automatic: 28 min (TEA), 14-16 min (Code2Video), 19-31 min (ManimAgent). — [arXiv 2502.19400v2](https://arxiv.org/html/2502.19400v2); [arXiv 2510.01174](https://arxiv.org/html/2510.01174); [arXiv 2606.30296](https://arxiv.org/html/2606.30296v1)

### Inferences
- Arithmetic for the target: 10 videos in a ~6-hour productive day is 36 minutes of operator attention per video. With a 30-minute render that only works if renders are unattended and never repeated — i.e. every decision must be made before the render starts. That is the whole case for sections 2 and 5.
- A checkpoint design consistent with the evidence, sized for a low-technical operator: Gate 0 (automatic) rule + geometry + semantic critics on plan.json; Gate 1 (human, ~3-5 min) contact sheet + scrubbable animatic with real audio, actions limited to accept / pick alternative / toggle a beat to "none" / drag a label anchor / escalate; Gate 2 (automatic) the existing `tools/gates.py` on the final file; Gate 3 (human, sampled) watch-through of a fraction of outputs, feeding rejects to the pitfalls list. Escalated or `custom` beats go to the skilled person, who becomes a template author rather than a per-video planner.
- LASEV's 58%-perfect figure implies that even with strong critics roughly 4 in 10 automatically produced plans will have something a careful reviewer would change; the system should be judged on median operator minutes per video and on escaped-defect rate, not on first-pass perfection.
- Correctness risk concentrates in the 4% class (wrong solution / misread question). In this pipeline the answer and script are already human-reviewed upstream, so the planner should be forbidden from introducing facts: every on-screen string must be derivable from the script, answer or figure label set, checked by a string-provenance rule in code.

### Gaps
- No trustworthy, independently audited videos-per-person-per-day figure was found for any edtech or AI-video company; Indian edtech engineering blogs on this topic were not found in the searches run.
- No data found on review-time-per-video as a function of pipeline design, or on escaped-defect rates in production.
- Vendor throughput numbers above come from search snippets of marketing pages and were not opened.
