# Workflow orchestration, operator tooling, review/QC and production-process design for an AI-assisted video factory (state as of Oct 2026)

Researcher's note on coverage: I made about 25 search/fetch calls. Questions 1, 3, 5 and parts of 4, 6, 7 have primary-source findings. Questions 2, 8, 9 and large parts of 4 and 6 were NOT researched against live sources in this pass; for those, the "Gaps" sections list candidates from my background knowledge, explicitly marked unverified. Nothing in "Cited Findings" comes from memory. Where a finding comes only from a search-result snippet (page not opened), it is tagged "(snippet only)".

## 1. Durable workflow / job orchestration for long-running, retryable, human-in-the-loop media jobs

### Takeaway
For one box, a 3-10 person team and no platform engineer, the verified short list is DBOS (a Postgres-backed library, no server), Dagster OSS (asset model plus a `pool` limit of 1 for the heavy render), Prefect 3 (built-in pause-for-input form in its UI) and Hatchet Lite (single Docker image); Temporal is described by a competitor's docs as a "heavyweight orchestration service" and I found no evidence it is the right size for this team. I found no reliable source on what AI video companies actually run.

### Cited Findings

DBOS
- DBOS needs only "a Postgres database" and an open-source library; "no additional infrastructure for you to configure or manage" (no orchestration server). It persists workflow state to Postgres and on failure "uses this saved state to recover it from the last completed step." — [DBOS docs, Why DBOS](https://docs.dbos.dev/why-dbos)
- DBOS's own comparison: "Temporal implements durable workflows in a heavyweight orchestration service, whereas DBOS implements them in a Postgres-backed library." (vendor claim about a competitor) — [DBOS docs, Why DBOS](https://docs.dbos.dev/why-dbos)
- DBOS docs say it natively integrates human-in-the-loop for agents. — [DBOS docs, Why DBOS](https://docs.dbos.dev/why-dbos)
- DBOS queues have two concurrency controls: worker concurrency ("maximum number of workflows from a queue that can run concurrently on a single DBOS process") and global concurrency (across all processes), plus rate limits on how many functions may start per period, positioned for rate-limited LLM APIs. — [DBOS Python queue tutorial](https://docs.dbos.dev/python/tutorials/queue-tutorial)

Dagster
- An asset or op is assigned to a pool with `@dg.asset(pool="database")`; the limit is set in `dagster.yaml` (`concurrency: pools: default_limit: 1`) or with `dagster instance concurrency set database 1`. Pools are available in open-source Dagster. — [Dagster docs, Concurrency pools](https://dagster.io/docs/guides/operate/managing-concurrency/concurrency-pools)
- Default pool granularity is `op` ("only one op executes at a time across all runs"); it can be changed to `run`. — [Dagster docs, Concurrency pools](https://dagster.io/docs/guides/operate/managing-concurrency/concurrency-pools)
- Caveat: "By default, Dagster does not automatically free concurrency pool slots when a run is cancelled or fails", which can deadlock the pool; the fix is `run_monitoring: enabled: true` with `free_slots_after_run_end_seconds`. — [Dagster docs, Concurrency pools](https://dagster.io/docs/guides/operate/managing-concurrency/concurrency-pools)

Prefect 3
- `pause_flow_run()` and `suspend_flow_run()` take a `wait_for_input` parameter (a built-in type, a pydantic `BaseModel`, or a `RunInput` subclass). When the flow pauses, Prefect renders a form in its UI; `.with_initial_data()` sets default values and a Markdown description for the reviewer; a timeout can be given. Custom validation runs after resume, so it needs explicit error handling. — [Prefect 3 docs, Interactive workflows](https://docs.prefect.io/v3/advanced/interactive)

Hatchet
- Three self-hosting modes: Hatchet Lite ("Single docker image with bundled engine and API", for "development, testing, or low-throughput production"), Docker Compose (PostgreSQL required, RabbitMQ optional but recommended), and Kubernetes Helm charts. — [Hatchet docs, Self-hosting](https://docs.hatchet.run/self-hosting)
- Concurrency strategies: Group Round Robin (queue and dispatch when a slot opens), Cancel In Progress, Cancel Newest, Cancel Queued Except Newest, Cancel Queued Except Oldest. Keys are CEL expressions over workflow input and metadata; limits can be shared across workflows by name; `max_runs` takes an int or a CEL expression. — [Hatchet docs, Concurrency](https://docs.hatchet.run/home/concurrency)

Inngest (snippet only)
- A ranking site says Inngest reported over 7,000 organisations by early 2026, with a $99/month Pro plan and self-host options at enterprise tiers. Not opened; aggregator, treat as unverified. — [Automation Atlas ranking](https://automationatlas.io/rankings/best-durable-workflow-engines-2026/)

### Inferences
- The "one heavy job at a time on an 8GB machine" rule maps directly onto a named limit of 1: a Dagster pool `render` with limit 1, a DBOS queue with global concurrency 1, or a Hatchet Group Round Robin key with `max_runs` 1. Light stages (LLM calls, sheet reads, gates) can sit outside that limit and run concurrently.
- The existing design (per-project JSON state, "narration sets the clock", stages that must run in order) is already a DAG with a resource lock; the smallest change is DBOS, because it is a library added to the existing Python CLI and needs only Postgres, where every other verified option adds at least one always-on service.
- Prefect's pause form is the only verified ready-made "approve / edit a value / resume" UI in this set, which matters if the team does not want to build the approval screen itself. With DBOS or Hatchet the approval screen has to be built (the existing FastAPI dashboard is the obvious place).
- Dagster's failure-does-not-release-the-slot default is exactly the kind of silent hang a non-engineer operator cannot diagnose; if Dagster is chosen, run monitoring must be on from day one.

### Gaps
- No reliable source found on what AI video companies (Synthesia, HeyGen, Descript, Captions) use for orchestration. Not answered.
- Not researched live, so unverified: Temporal self-host footprint and Cloud pricing; Restate; Windmill; Kestra; n8n; Airflow; Celery/RQ/Dramatiq/Huey; Trigger.dev v4; Vercel Workflow. A May 2026 comparison series on youngju.dev covering most of these appeared in search but the site failed DNS resolution.
- Not verified: licences of DBOS and Hatchet (background knowledge says MIT for both); Hatchet's human-in-the-loop primitive; DBOS Conductor pricing; Prefect 3 and DBOS step-level caching semantics (background knowledge: Prefect has task cache policies keyed on inputs; DBOS memoises completed steps for recovery, not across separate runs).
- Whether any of these run acceptably on an 8GB macOS box alongside a render was not tested or sourced.

## 2. Content-addressed build systems so only changed parts re-render

### Takeaway
Not researched against live sources in this pass; no cited findings. The one verified adjacent fact is that Dagster OSS models work as assets with per-asset concurrency pools, which makes it a candidate for both the orchestration and the incremental-build role.

### Cited Findings
- Dagster assets can be individually decorated and assigned to concurrency pools, so a per-beat or per-stage asset graph with a render lock is expressible in open-source Dagster. — [Dagster docs, Concurrency pools](https://dagster.io/docs/guides/operate/managing-concurrency/concurrency-pools)

### Inferences
- The stated pain ("each fix costs a 30+ minute re-render") is a cache-granularity problem before it is an orchestration problem: if the unit of render is the beat (the repo's own "a beat is a clip" idea) and each beat's output is keyed on a hash of its inputs (beat JSON, timing, template version, fonts, assets), a one-beat fix re-renders one beat plus the final concat/composite. Any of the tools named in the brief can do this; the design decision is the cache key, not the tool.
- The repo already hit this class of bug: the frames cache is keyed on a model-written prompt that changes every run. A content-addressed build only works if every input is deterministic or pinned, so LLM outputs must be stored as files and treated as sources, not regenerated.

### Gaps
- Unverified background knowledge, offered as leads only: DVC pipelines (`dvc.yaml` stages with deps/outs hashed, `dvc repro` skips unchanged stages, handles large binary outputs); Snakemake and doit (Python-native, file/hash based, single-machine friendly); Bazel/Pants (strong hermetic caching, high setup cost, probably too heavy for this team); Make/Just/Task (timestamp-based or no caching, weak for this); Manim's own per-animation partial-movie cache.
- No published examples of incremental rendering in video pipelines were found or searched for.

## 3. Agent harnesses for non-technical operators

### Takeaway
Claude Code's headless mode (`claude -p`) and the Agent SDK are documented, scriptable and give machine-readable cost per run, which is enough to wrap the pipeline as a fixed set of allowed tools with an operator never seeing a terminal. Since 15 June 2026, headless and SDK use on subscription plans reportedly draws on a separate dollar-denominated monthly credit (secondary source), so per-video agent cost is now a real budget line rather than "free on the subscription".

### Cited Findings

Headless mode and guardrails
- `claude -p` runs the same agent loop non-interactively; it exits 0 on success and non-zero on failure, so scripts can branch on it. — [Claude Code docs, Run Claude Code programmatically](https://code.claude.com/docs/en/headless)
- `--allowedTools` uses permission-rule syntax with prefix matching, e.g. `Bash(git diff *)`, so the agent can be restricted to a named set of commands. — [Claude Code docs, headless](https://code.claude.com/docs/en/headless)
- Permission modes for unattended runs: `dontAsk` denies every call that would otherwise prompt (for locked-down runs); `acceptEdits` auto-approves file writes and common filesystem commands; `auto` has a classifier review actions. `--permission-prompts none` (v2.1.259+) denies anything unresolved and tells Claude not to retry; denials are listed in `permission_denials` in the result. — [Claude Code docs, headless](https://code.claude.com/docs/en/headless)
- `--output-format json` with `--json-schema` returns schema-conforming output in a `structured_output` field; an invalid schema is an error rather than silently ignored (since v2.1.205). — [Claude Code docs, headless](https://code.claude.com/docs/en/headless)
- With `--output-format json` the payload includes `total_cost_usd` and a per-model breakdown (client-side estimates), cumulative across `--continue`/`--resume`. — [Claude Code docs, headless](https://code.claude.com/docs/en/headless)
- `--bare` skips auto-discovery of hooks, skills, commands, subagents, plugins, MCP servers, auto memory and CLAUDE.md, for "the same result on every machine"; it requires `ANTHROPIC_API_KEY` (does not use the subscription login) and is "the recommended mode for scripted and SDK calls, and will become the default for `-p` in a future release." — [Claude Code docs, headless](https://code.claude.com/docs/en/headless)
- Without `--bare`, a `-p` session runs the project's hooks and connects its `.mcp.json` servers with no trust dialog, even in a folder never trusted. — [Claude Code docs, headless](https://code.claude.com/docs/en/headless)
- User-invoked skills work in `-p` mode by including `/skill-name` in the prompt. — [Claude Code docs, headless](https://code.claude.com/docs/en/headless)
- `--resume <session_id>` continues a specific session, from any directory on the machine (v2.1.223+). — [Claude Code docs, headless](https://code.claude.com/docs/en/headless)
- The Agent SDK exposes custom tools via the `@tool` decorator and `createSdkMcpServer`, plus hooks and external MCP servers (search-result summary of the official custom-tools page; page not opened). — [Claude Agent SDK docs, Custom tools](https://platform.claude.com/docs/en/agent-sdk/custom-tools)

Billing of headless use on subscriptions (secondary source; the cited Anthropic help-centre article was not opened)
- From 15 June 2026, programmatic use (Agent SDK in your own projects, `claude -p`, Claude Code GitHub Actions, third-party apps on the SDK) consumes a monthly Agent SDK credit: Pro $20, Max 5x $100, Max 20x $200, Team Standard $20/seat, Team Premium $100/seat. Interactive Claude Code is unaffected. The credit "is consumed at the same per-model rates Anthropic publishes for the API." — [Totalum blog](https://www.totalum.app/blog/claude-agent-sdk-credits-2026)

API prices (official)
- Per million tokens, input/output: Opus 5.5 $4/$20; Sonnet 5.5 $2/$10; Sonnet 5 $2/$10; Haiku 5.5 $0.10/$0.50 for prompts up to 100k tokens ($0.50/$2.50 above); Haiku 4.5 $1/$5. — [Claude pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- Batch API: 50% off input and output (e.g. Sonnet 5.5 $1/$5, Opus 5.5 $2/$10). Batch and caching discounts stack. — [Claude pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- Prompt caching: 5-minute write 1.25x, 1-hour write 2x, read 0.1x base input (0.05x on Opus 5.5 and Sonnet 5.5). The page is internally inconsistent for Sonnet 5.5: the table lists cache hits at $0.20/MTok while the text says $0.10. — [Claude pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- Claude 4.7+ models use a tokenizer producing roughly 30% more tokens for the same text; 1M context is at standard pricing on 4.6+ models except Haiku 5.5. — [Claude pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- Claude Managed Agents: standard token rates plus $0.08 per session-hour of `running` time; no batch discount. — [Claude pricing](https://platform.claude.com/docs/en/about-claude/pricing)

### Inferences
- The "bespoke build script per video" problem is addressable with the documented controls: give the agent an allow-list of pipeline commands only (for example `Bash(python video.py *)` and `Bash(python tools/gates.py *)`), no general Bash and no Write outside the project's beats/script files, and it physically cannot produce a one-off script. This is a configuration change, not a new framework.
- `--json-schema` suits the planning stage: the visual plan (beats JSON) can be demanded as schema-valid structured output, turning "the plan parses" into a hard gate.
- Illustrative cost arithmetic (my assumptions, not measured): a planning run with 200k cached-read input tokens, 50k fresh input and 30k output on Sonnet 5.5 is about 200k x $0.10-0.20/M + 50k x $2/M + 30k x $10/M = roughly $0.42-0.44 per video; on Opus 5.5 roughly $0.84. At 10 videos/day per operator that is about $4-9/day, so a $20 Pro credit would last 2-5 working days and API-key billing (or Team Premium/Max seats) is the realistic footing. The real figure should be read from `total_cost_usd` on actual runs.
- Non-interactive stages that can wait (answer verification, script drafting for tomorrow's batch, QC frame review) are candidates for the Batch API at half price; interactive planning is not.
- `--bare` plus an explicit `--mcp-config`/`--settings` gives reproducibility across operator machines but drops CLAUDE.md and memory, where this project's rules currently live. That is a forcing function to move rules into tools, schemas and gates (see question 8).

### Gaps
- Not researched: Claude Cowork/desktop app suitability for operators, scheduled cloud agents, specific MCP servers (Google Drive/Sheets, HeyGen, ffmpeg, Remotion, HyperFrames), OpenAI Agents SDK/Codex, Google ADK, LangGraph.
- The June 2026 credit change is from one third-party blog; the Anthropic help article it cites ("Use the Claude Agent SDK with your Claude plan") was not opened. Verify before budgeting.
- No published per-video token-cost figures from comparable pipelines were found.

## 4. Operator UI options

### Takeaway
Only two items were verified: Remotion's Editor Starter is a $600 paid template for a browser timeline editor, and Prefect's UI can render an approval/input form with no front-end work. The broader builder and embeddable-editor comparison was not researched.

### Cited Findings
- Remotion Editor Starter costs $600 (bought at remotion.pro); buyers of the separate Timeline component get a full refund of it on upgrading; it is bundled with the Remotion Enterprise License. — [Remotion docs, Editor Starter: Buy](https://www.remotion.dev/docs/editor-starter/buy)
- Remotion company licences start around $25/seat/month or $0.01/render with a $100/month minimum (snippet only; the official licence page did not return the figures when fetched). — [Remotion pricing docs](https://www.remotion.dev/docs/pricing)
- Prefect 3 shows a typed form in its UI when a flow pauses, with default values and a Markdown description for the person approving. — [Prefect 3 docs, Interactive workflows](https://docs.prefect.io/v3/advanced/interactive)

### Inferences
- Because narration sets the clock and clips cannot be dragged to retime, a full NLE-style timeline editor is the wrong shape for this pipeline. What the operator needs is a storyboard review: one row per beat with its still, caption text, the gate results, and three actions (approve, edit a bounded field, reject with a reason code). That can be built on the existing FastAPI dashboard, or as a Prefect pause form in the short term.
- The Remotion editor options only pay off if rendering moves to Remotion/HTML; with Manim as the renderer they add a licence and a second stack without removing the re-render cost.
- A spreadsheet-like queue (the Google Sheet the team already uses, or a self-hosted equivalent) as the status board keeps operators in a tool they know; the orchestrator should write status back to it rather than making operators learn a workflow UI.

### Gaps
- Not researched: Retool, Appsmith, Budibase, Streamlit, Gradio, NiceGUI, Reflex, Next.js + shadcn; Airtable/NocoDB/Baserow as queue; Twick, Diffusion Studio, DesignCombo/react-video-editor, OpenCut, Motionity, IMG.LY CE.SDK, Etro. No pricing, licence or activity data collected for any of them.
- Remotion licence thresholds (team size at which a company licence is required) not confirmed from the primary page.

## 5. Review and approval tooling

### Takeaway
Kitsu is the one verified open-source, self-hostable option that combines task status ("Waiting for Approval" then "Retake"/"Done") with frame-accurate annotated review and an API, which matches a "review, comment at a timestamp, send back as a structured fix" loop. Frame.io is cheap for small teams but is a review tool only.

### Cited Findings
- Kitsu is open source and free to self-host. Hosted plans, per user per month billed annually: Agency EUR 20 (1-20 users, 100GB), Production EUR 30 (1-100 users, 3TB), Studio EUR 35 (1-300 users, 10TB); Enterprise is custom with on-premise install. REST routes and an event stream are available on all subscriptions; two-week trial. — [CGWire pricing](https://www.cg-wire.com/pricing)
- The same page says review capabilities and the playlist builder are in the Production and Studio tiers (implying not in Agency). — [CGWire pricing](https://www.cg-wire.com/pricing)
- Kitsu is AGPL; statuses drive review (artists set Waiting for Approval, supervisors answer Retake or Done); review includes drawing on frames, frame tags that work as timestamps, playlists for dailies, a synced review room, and guest access by public link (snippet only, third-party comparison page). — [Morphic, ShotGrid alternatives](https://morphic.com/resources/alternatives/shotgrid-alternatives)
- Frame.io: free plan covers 2 members and 2GB; Pro is $13 per member per month on annual billing for up to 5 members (snippet only, third-party). — [Morphic, Krock.io alternatives](https://morphic.com/de/resources/alternatives/krock-io-alternatives)

### Inferences
- Kitsu's event stream plus REST API is the hook for "timestamped comment becomes a structured fix": a Retake event with a frame tag can be mapped to the beat whose time window contains that frame and opened as a fix task against that beat's JSON. This mapping is my design suggestion; I found no source describing someone doing it.
- For a team already living in the pipeline's own dashboard, a minimal in-house review page (video player, click to stamp the time, pick a defect category from the gate list, free-text note) may be cheaper than adopting a tracker, and defect categories that recur become new gates.
- Self-hosting Kitsu adds a Postgres-backed web service to maintain on a machine with no platform engineer; the EUR 20-30/user hosted tier for 3-10 people is EUR 60-300/month.

### Gaps
- Not researched: Wipster, Filestage, ReviewStudio, Krock, ftrack, ShotGrid/Flow Production Tracking, SyncSketch.
- Kitsu's resource footprint, and whether it handles portrait video review well, not verified.
- No source found for an existing integration that turns review comments into machine-actionable fixes.

## 6. Automated QC

### Takeaway
Whole-video VLM review is now cheap enough to run on every build: Gemini documents roughly 100 tokens per second of video at low resolution and 300 at default, so a two-minute video is about 12k-36k input tokens. Classical checks, OCR, visual regression and LLM-eval tooling were not researched in this pass.

### Cited Findings
- Gemini video input costs approximately 100 tokens/second at low media resolution and approximately 300 tokens/second at default; default sampling is 1 FPS (66 or 258 tokens per frame) and is adjustable with an `fps` parameter. — [Gemini API docs, Video understanding](https://ai.google.dev/gemini-api/docs/video-understanding)
- 1M-context models accept up to 1 hour of video at default resolution or 3 hours at low; prompts reference moments in `MM:SS`; File API upload limit is 20GB paid / 2GB free, inline under 100MB. — [Gemini API docs, Video understanding](https://ai.google.dev/gemini-api/docs/video-understanding)
- An "agentic" video mode (model chooses which parts and frame rate to load) is supported on Gemini 3.8 Flash, 3.7 Flash, 3.6 Flash and 3.5 Flash Lite. — [Gemini API docs, Video understanding](https://ai.google.dev/gemini-api/docs/video-understanding)
- Google reports up to 88% fewer tokens, up to 66% lower cost and up to 7% higher accuracy for the agentic mode (snippet only, third-party write-up of a vendor claim). — [How AI Works](https://howaiworks.ai/blog/google-gemini-agentic-video-2026)
- Gemini 3.7/3.8 Flash input priced at an introductory $0.75/MTok, doubling to $1.50 on 1 January 2027 (snippet only, low-quality aggregator; unverified). — [techsy.io](https://techsy.io/en/blog/gemini-omni-api-pricing)

### Inferences
- At 1 FPS default sampling, a 120-second video is about 36k input tokens (12k at low resolution). Even at the unverified $0.75-1.50/MTok this is roughly $0.01-0.05 per full-video review, negligible against a 30-minute re-render. Cost is not the constraint; reliability of the verdict is.
- 1 FPS sampling will miss sub-second defects (a one-frame flash, a caption that is late by 300ms), so VLM review complements the mechanical gates and does not replace them. Raising `fps` for short windows around beat boundaries is the documented lever.
- The highest-value change to the "defects are caught by a human watching the final video" problem is to run QC on cheap pre-render artefacts (per-beat stills, a low-resolution draft render) before the expensive render, which the project's own "frames before rendering" rule already points to; the gates then run on the final file as confirmation, not discovery.
- Every defect a human catches in the final video should be logged with a category; categories that recur are the backlog for new gates. This is how the existing ~15 gates came about and it should be made an explicit step.

### Gaps
- Not researched, and listed from unverified background knowledge as leads: ffmpeg `blackdetect`, `freezedetect`, `silencedetect` and `ebur128`/`loudnorm` filters for blank/frozen/silent/loudness checks; VMAF and SSIM for comparing a render to a reference; MediaPipe face detection for presenter occlusion; Surya, PaddleOCR and Tesseract for Devanagari OCR (relative accuracy on Devanagari conjuncts not known to me with a source); pixelmatch, reg-suit, Playwright snapshots, Percy/Chromatic for golden-frame regression of templates; promptfoo, Braintrust, Langfuse, Inspect for LLM-stage evals.
- No benchmark found for VLM accuracy on Hindi on-screen text errors, which is the specific failure this team cares about. This should be measured in-house on a set of known-bad videos before relying on it.
- Claude vision per-image token cost and open-model (Qwen-VL) options not checked.
- Gemini pricing not confirmed from Google's pricing page.

## 7. Process design and published throughput numbers

### Takeaway
Published numbers are vendor case studies for avatar-only videos and are far below or not comparable with the target: the best-documented one is a single instructional designer producing 200+ micro-videos in about six months with each taking under an hour. I found no published per-operator throughput for a composited, animated, QC-gated video like this team's, so 10 per operator per day should be treated as an unbenchmarked target.

### Cited Findings
- Zoom (Synthesia case study): one instructional designer made 200+ micro-videos in about 6 months; a video is generated in under an hour versus a full day of recording for about 15 minutes of usable video; claimed 90% faster; 15-20 hours/month freed per subject-matter expert. Vendor-published. — [Synthesia case study: Zoom](https://www.synthesia.io/case-studies/zoom)
- Vision Creative Labs went from 1-2 videos annually to 50-60 per day using HeyGen (snippet only; organisational output, team size not stated; vendor-published). — [HeyGen blog](https://www.heygen.com/blog/best-ai-video-generators-tested-and-reviewed)
- DuPont (Synthesia): about $10,000 lower outsourcing cost per video and 80% faster production (snippet only, via a third-party summary). — [note.com summary](https://note.com/ai_video_creator/n/n49181b02776a?hl=en)

### Inferences
- Arithmetic on the target: 10 videos in an 8-hour day is a takt time of 48 minutes per video, and that is an upper bound on human attention per video with zero slack. A realistic budget leaving time for breaks, rework and queue management is 25-35 minutes of attention per video. Today planning alone takes "hours", so planning must fall by roughly an order of magnitude; that is the binding constraint, not rendering.
- Machine arithmetic: if a render is 30+ minutes and the box runs one heavy job at a time, 10 videos is 5+ hours of serial render per operator per day with no re-renders. One re-render per video doubles it past a working day. So 10/day per operator on one 8GB machine is infeasible unless (a) renders run overnight or on other hardware, (b) the first-pass yield is near 100%, or (c) re-renders are incremental (question 2). With 3-10 operators sharing one box it is impossible; rendering has to move to a queue with more than one worker.
- Zoom's figure is about 200 videos over roughly 125 working days, under 2 per day for one person on a far simpler product. The target is about 5x that on a harder product, which says the gain has to come from removing human decisions (templates, batching), not from operators working faster.
- Process levers consistent with the above: batch by chapter and template so one planning decision covers many videos (the director's `question_strategy()` already classifies by question wording, which is a natural template key); separate attended stages (script approval, storyboard approval, final watch) from unattended ones and batch the attended ones into fixed review sessions; put a WIP limit on videos awaiting render equal to what the machine can finish overnight; measure first-pass yield (share of videos that pass gates and human watch with no re-render) as the primary metric.

### Gaps
- No numbers found for Physics Wallah, Khan Academy/Khanmigo, Unacademy, Duolingo, Wibbitz, faceless-channel operations, Spotify Wrapped or GitHub Unwrapped. The Remotion success-stories archive lists titles only (e.g. "Making a million dollars with Remotion", Typeframes, Yarx marathon videos) and the individual pages were not opened.
- No sourced benchmark for minutes of human attention per video in comparable pipelines, nor for animation-studio practices (definition-of-done checklists, dailies cadence) beyond what Kitsu's status model implies.
- All throughput figures above are vendor marketing; none is independently verified.

## 8. Knowledge management: prose into enforced rules

### Takeaway
Not researched against external sources. The only cited mechanisms are Claude Code's own: schema-validated output and permission allow-lists make rules enforceable rather than advisory, and the recommended `--bare` mode does not load CLAUDE.md or memory at all, so rules that live only in prose will not reach scripted runs.

### Cited Findings
- `--bare` skips CLAUDE.md, auto memory, skills, hooks and MCP auto-discovery and is slated to become the default for `-p`; context must then be passed explicitly (`--append-system-prompt-file`, `--settings`, `--mcp-config`, `--agents`). — [Claude Code docs, headless](https://code.claude.com/docs/en/headless)
- `--json-schema` enforces a JSON Schema on output and fails loudly on an invalid schema. — [Claude Code docs, headless](https://code.claude.com/docs/en/headless)
- Permission rules can restrict the agent to named command prefixes, and unresolved requests are denied and reported in `permission_denials`. — [Claude Code docs, headless](https://code.claude.com/docs/en/headless)

### Inferences
- A practical triage for each gotcha in the bug ledger and memory notes: (1) can a schema reject it (a JSON Schema on beats/meta, e.g. `marks` required, no percentage strings in a prompt field); (2) can a linter or gate reject it (the existing gates, a banned-word check on generation prompts); (3) can a hook block it (a pre-tool hook refusing edits to generated directories); (4) only if none apply does it stay as prose. The project already does this in places (preflight fails without `marks`; `audit()` refuses a prompt containing a percentage), so this is extending an existing habit, not a new practice.
- Each rule converted this way should carry a test fixture of the original failure, so the rule cannot be silently weakened.
- Design tokens (font, sizes, safe-area floors, colours) belong in one machine-readable file read by the renderer, the label placer and the frame review, since the project notes the floor is currently checked in three places.

### Gaps
- No external sources gathered on video design-system tokens, template libraries, or published practice for converting runbooks into lint rules.

## 9. Team practices for non-engineers: packaging, setup, secrets

### Takeaway
Not researched against external sources in this pass; no tool comparison is offered. The one verified, relevant fact is a security caveat about running Claude Code headless in untrusted folders.

### Cited Findings
- Without `--bare`, a `claude -p` session runs the hooks in a project's `.claude/settings.json` and connects its `.mcp.json` servers with no workspace trust dialog and no per-server approval, even in a folder never trusted. — [Claude Code docs, headless](https://code.claude.com/docs/en/headless)
- In bare mode Claude Code never reads OAuth credentials or the system keychain; it needs `ANTHROPIC_API_KEY` in the environment or an `apiKeyHelper` in `--settings`. — [Claude Code docs, headless](https://code.claude.com/docs/en/headless)

### Inferences
- The fragile parts of this environment are system-level, not Python-level (LaTeX, Pango fonts, libraqm for Pillow, ffmpeg build flags). That argues for operators not having a local environment at all: a shared render host or container behind the dashboard, with operators using only a browser. Per-operator installs multiply exactly the class of silent failure the notes describe (wrong font substituted, Devanagari mis-shaped).
- An `apiKeyHelper` or server-side key keeps API keys off operator machines; operators authenticate to the dashboard, not to providers.
- Error messages should be written at the gate layer, where the pipeline knows what the operator can do next (re-approve, re-record, escalate), since a Manim traceback is not actionable for a non-engineer.

### Gaps
- Not researched: Docker/devcontainers, Nix, uv, pixi, single installers, cloud dev environments (Codespaces and similar), and their cost and usability from India. Background knowledge only, unverified: uv gives fast reproducible Python environments with a lockfile; pixi additionally pins conda-forge system libraries such as ffmpeg, cairo and pango, which is the gap uv leaves for this stack.
- No sources gathered on secrets managers or permission models suited to a 3-10 person team.
