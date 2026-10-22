# Avatar presenter, TTS, generative video and matting tools (state as of 8 Oct 2026)

Reading notes for the report writer:
- About 40 search/fetch calls were made. The scope (six questions, ~70 named products) is far larger than that budget, so coverage is uneven: HeyGen, Veo/Gemini API, ElevenLabs and Sarvam were read from primary docs; most other vendors rest on one secondary source or were not reached at all. Every "Gaps" section lists what was NOT checked. Do not read silence as "not available".
- Pages were read through a summarising fetch tool, so quoted strings are that tool's extraction of the page, not my own reading of raw HTML. Where an extraction looked wrong I say so.
- Several product names below (ElevenLabs v4, Gemini Omni, Nano Banana 2.1, Gemini 3.8 Flash TTS, HeyGen Avatar V, Seedance 2.5) come from the fetched pages and are newer than anything I could cross-check independently.
- USD-per-video arithmetic in "Inferences" is mine, from the cited unit prices.

## 1. HeyGen API in 2026 — does it remove the manual download and the green screen?

### Takeaway
Yes on both counts, on paper: the v3 API (`POST /v3/videos`) renders a digital-twin avatar in 9:16 at 1080p with `output_format: "webm"`, which per the docs "automatically removes the background and adds an alpha channel", accepts an externally produced audio file, and notifies by webhook. It does not return word-level timestamps (SRT sidecar only), and the v1/v2 endpoints are retired on 1 Nov 2026, so anything built now should target v3.

### Cited Findings

API shape and migration
- v2 `POST /v2/video/generate` becomes `POST /v3/videos` with a `type` of `avatar`, `image`, `cinematic_avatar` or `studio`; Video Agent moves to `POST /v3/video-agents`; TTS to `POST /v3/voices/speech`; new v3-only `POST /v3/lipsyncs` (speed/precision modes) and voice design — [HeyGen endpoint version comparison](https://developers.heygen.com/endpoint-version-comparison.md)
- "v1/v2 endpoints remain fully operational through October 31, 2026"; retired from 1 Nov 2026; v3 is recommended for all new development — [HeyGen endpoint version comparison](https://developers.heygen.com/endpoint-version-comparison.md)
- The multi-scene Studio API is still v2-only per the search summary of the same doc set, "maintenance continuing until v3 equivalents are available" (the create-video schema nevertheless lists a `studio` type in v3 — the two statements were not reconciled) — [HeyGen endpoint version comparison](https://developers.heygen.com/endpoint-version-comparison.md); [Create Video reference](https://developers.heygen.com/reference/create-video.md)
- Rendering engine is chosen per request via `engine`: `avatar_iii`, `avatar_iv` (default), `avatar_v` — [Create Video reference](https://developers.heygen.com/reference/create-video.md)
- Avatar V is described as "HeyGen's highest-fidelity v3 rendering engine, using cross-reference-driven animation"; supports body motion and hand gestures through a natural-language `motion_prompt`; `digital_twin` avatars only; opt-in per look (check `supported_api_engines`) — [Avatar V doc](https://developers.heygen.com/avatar-v.md)
- Docs exist for creating avatars via API: Digital Twin (avatar from video) and Photo Avatar — [HeyGen docs index (llms.txt)](https://developers.heygen.com/llms.txt)

Transparent output (the green-screen question)
- `output_format: "webm"` on `POST /v3/videos` is "the single required parameter" for a transparent background with alpha channel; MP4 cannot carry alpha — [Transparent Background Videos](https://developers.heygen.com/transparent-background-videos.md)
- Supported with Avatar IV (default), Avatar V and Avatar III, across digital twin, studio avatar and photo avatar looks; NOT supported for cinematic avatars — [Transparent Background Videos](https://developers.heygen.com/transparent-background-videos.md)
- The avatar must have been "trained with matting (background separation)" — standard for recent avatars; older ones are rejected with "This video avatar does not support webm output." — [Transparent Background Videos](https://developers.heygen.com/transparent-background-videos.md)
- `output_format: "webm"` cannot be combined with a `background` object; there is also a boolean `remove_background` ("Video avatars must be trained with matting enabled") — [Transparent Background Videos](https://developers.heygen.com/transparent-background-videos.md); [Create Video reference](https://developers.heygen.com/reference/create-video.md)
- Conflict: the legacy v2 WebM page says the WebM endpoint "does not support custom avatars — it only supports HeyGen's studio avatars". The v3 page says digital twins qualify. The legacy page is the older one — [legacy WebM doc (search result)](https://docs.heygen.com/docs/create-webm-avatar-videos); [v3 Transparent Background Videos](https://developers.heygen.com/transparent-background-videos.md)

Output, audio, captions, webhooks
- Aspect ratios `16:9`, `9:16`, `4:5`, `5:4`, `1:1`, `auto`; resolutions `720p`, `1080p`, `4k`; "Avatar IV and Avatar V render the avatar at up to 1080p: with 4k, the avatar is composited onto a 4K canvas" — [Create Video reference](https://developers.heygen.com/reference/create-video.md)
- Usage-limits page says supported aspect ratios are "16:9 or 9:16", width/height 128–4,096 px, avatar video at 25 fps, default 1080p (narrower than the schema's list — treat 16:9 and 9:16 as the safe set) — [Usage Limits](https://developers.heygen.com/docs/usage-limits.md)
- Voice input can be `script` + `voice_id`, or external audio via `audio_url` (public HTTPS) or `audio_asset_id` — [Create Video reference](https://developers.heygen.com/reference/create-video.md)
- Built-in TTS engines: ElevenLabs, Fish Audio, Starfish; ElevenLabs models selectable: `eleven_multilingual_v2`, `eleven_turbo_v2_5`, `eleven_flash_v2_5`, `eleven_v3`, `eleven_v4`, with `stability`, `similarity_boost`, `style`, `use_speaker_boost` — [Create Video reference](https://developers.heygen.com/reference/create-video.md)
- Captions: `output_settings.captions` with `file_format: srt`; "A sidecar subtitle file is always generated and returned via subtitle_url" — [Create Video reference](https://developers.heygen.com/reference/create-video.md)
- `GET /v3/videos/{video_id}` returns `video_url`, `subtitle_url` (SRT), `captioned_video_url`, `thumbnail_url`, `gif_url`, `duration`, `status`, `failure_code`, `failure_message`. No word-level timestamp field is documented — [Get Video reference](https://developers.heygen.com/reference/get-video.md)
- Webhooks: per-request `callback_url` + `callback_id`, and managed webhook endpoints with signed payloads and secret rotation — [Create Video reference](https://developers.heygen.com/reference/create-video.md); [HeyGen endpoint version comparison](https://developers.heygen.com/endpoint-version-comparison.md)

Limits
- Pay-As-You-Go: 10 concurrent workflows, no burst. Enterprise: 20 included, burst "up to +50 per workflow type at 1.5×" the contract rate — [Usage Limits](https://developers.heygen.com/docs/usage-limits.md)
- Script max 5,000 characters; 30 minutes per scene; write operations 10/s, heavy operations 30/min, batch creation endpoints 30/min on all tiers — [Usage Limits](https://developers.heygen.com/docs/usage-limits.md)
- Batch endpoints exist (`Batch Videos`, `Create Video Batch`) — [HeyGen docs index (llms.txt)](https://developers.heygen.com/llms.txt)

Pricing (secondary sources only — the primary table could not be read)
- API usage is billed from a prepaid USD wallet, minimum $5, per second of output; no monthly fee; "An API Key bills HeyGen's prepaid wallet, while OAuth bills your web-plan credits" — search summary of [HeyGen help: API pricing explained](https://help.heygen.com/en/articles/10060327-heygen-api-pricing-explained) and [G2: HeyGen API pricing](https://www.g2.com/articles/heygen-api-pricing)
- Per-second rates as reported: Avatar III Digital Twin $0.0167/s; Avatar III Photo Avatar $0.0433/s; Avatar IV Photo Avatar $0.05/s; Avatar V, Avatar IV Digital Twin and Studio Avatar $0.0667/s — [G2: HeyGen API pricing](https://www.g2.com/articles/heygen-api-pricing) (page returned 403 on direct fetch; figures are from the search snippet)
- Consistent second source: "$4 per 1080p minute for a Digital Twin on Avatar IV according to published API rates from July 2026"; Avatar IV variants $0.05–$0.10/s; no free API credits since Feb 2026 — [Creatify blog on HeyGen pricing](https://creatify.ai/blog/heygen-pricing-(2026)-plans-and-what-you-ll-actually-pay) (a competitor's blog)
- In the web app, a one-minute Avatar IV video uses 20 credits — [Creatify blog on HeyGen pricing](https://creatify.ai/blog/heygen-pricing-(2026)-plans-and-what-you-ll-actually-pay)

Agent surfaces
- Remote MCP server at `https://mcp.heygen.com/mcp/v1/`, OAuth, "no API key required"; tools cover Video Agent, video creation, templates, voices (catalog, cloning, synthesis), translation, avatar management, asset upload; "Usage draws on your existing HeyGen plan's credits" rather than the API wallet — [HeyGen MCP overview](https://developers.heygen.com/mcp/overview.md)
- Docs list setup pages for Claude Code, Claude Web, Cursor and Gemini CLI, a CLI, and two skills (`heygen-video`, `heygen-avatar`) — [HeyGen docs index (llms.txt)](https://developers.heygen.com/llms.txt)
- Video Agent has an API (`POST /v3/video-agents`), a prompting guide and interactive sessions; styles, references and interactive chat are v3-only — [HeyGen docs index (llms.txt)](https://developers.heygen.com/llms.txt); [HeyGen endpoint version comparison](https://developers.heygen.com/endpoint-version-comparison.md)

### Inferences
- Presenter cost for one 120-second video at the reported rates: Avatar IV or V digital twin 120 × $0.0667 = about $8.00; Avatar III digital twin 120 × $0.0167 = about $2.00. At 10 videos/day that is roughly $80/day (IV/V) or $20/day (III) per operator. Whether WebM output carries a surcharge is not documented.
- The API path removes three current manual steps at once: the hand download (webhook + `video_url`), the hsvkey calibration (alpha WebM), and the landscape-to-portrait reframing (native `9:16`). The condition is that the team's digital twin was trained with matting; an older twin would need re-creating.
- The SRT problem is not solved by HeyGen itself: the API still only hands back an SRT sidecar. The clean fix is to synthesise narration outside HeyGen with a TTS that returns alignment (see Q3), pass it in as `audio_url`, and build captions from the TTS alignment. That also keeps the repo's "narration sets the clock" rule intact.
- Two billing routes exist and they are different money: API key = prepaid wallet per second; MCP/OAuth = web-plan credits. For 20 minutes of avatar per operator per day, which is cheaper depends on the plan's credit allowance, which was not checked.
- Avatar V's `motion_prompt` is the only documented route to directed hand gestures; it is digital-twin-only and opt-in per look.

### Gaps
- HeyGen's own price table was not read: `developers.heygen.com/docs/pricing` returned 404, the help-centre article rendered without its table, G2 returned 403. The per-second rates above are secondary and should be confirmed in the dashboard before budgeting.
- Not verified: whether WebM is VP8 or VP9, its bitrate/edge quality on hair, and whether alpha quality matches a good key. Needs a one-clip test.
- Not verified: Hindi voice quality inside HeyGen, and whether a cloned ElevenLabs voice in the team's own ElevenLabs account can be referenced directly (the schema only shows ElevenLabs as a selectable engine).
- Not verified: accuracy of the API's `subtitle_url` SRT timings (the team's 2-second error was observed on manual exports).
- Enterprise pricing, web-plan tiers and credit allowances, and Video Agent pricing were not retrieved.
- Availability/billing from India was not checked.

## 2. Alternatives for a consistent talking presenter (SaaS and open source)

### Takeaway
I found very little solid, primary-sourced material here; the only firm facts are a handful of prices and the InfiniteTalk repo details. Nothing found suggests an alternative that beats HeyGen's documented combination of digital twin + alpha WebM + 9:16 + external audio, but that is absence of evidence from a thin search, not a comparison.

### Cited Findings
- Tavus: "$1 per generated minute and $0.37 per real-time conversation minute" — [techsy.io avatar generator roundup](https://techsy.io/en/blog/best-ai-avatar-generators-2026) (secondary)
- Synthesia: free tier 10 min/month, Starter about $29/month; D-ID Lite about $5.99/month; Hedra Basic about $15/month; D-ID's API is billed per minute separately from Studio (rate not given) — [techsy.io avatar generator roundup](https://techsy.io/en/blog/best-ai-avatar-generators-2026); [Argil blog on D-ID pricing](https://argil.ai/blog/d-id-pricing) (a competitor's blog)
- Argil: Classic $39/month, Pro $149/month — [Argil blog on D-ID pricing](https://argil.ai/blog/d-id-pricing)
- Hedra Character-3 from a still photo gives "casual, slightly imperfect motion that actually reads as human for social clips" (reviewer opinion) — [techsy.io avatar generator roundup](https://techsy.io/en/blog/best-ai-avatar-generators-2026)
- InfiniteTalk (MeiGen-AI): Apache 2.0; built on Wan2.1-I2V-14B-480P; 480p and 720p; image-to-video and video-to-video dubbing; 40 sampling steps by default, 4–8 with FusioniX/Lightx2v LoRA; low-VRAM flag and FP8 quantised weights; "unlimited" length claimed with a default 1,000-frame cap (~40 s) — [InfiniteTalk GitHub](https://github.com/MeiGen-AI/InfiniteTalk)
- InfiniteTalk limitations stated in the repo: colour shifts beyond about 1 minute of I2V; the acceleration LoRA reduces identity preservation in longer videos; audio encoder is `chinese-wav2vec2-base`, multilingual ability not documented — [InfiniteTalk GitHub](https://github.com/MeiGen-AI/InfiniteTalk)
- Hosted InfiniteTalk at $0.03 per second, "up to 10 minutes, in any language" (vendor claim) — [Atlas Cloud InfiniteTalk page](https://www.atlascloud.ai/infinitetalk)
- OmniAvatar 14B: VRAM from 8 GB to 36 GB depending on configuration, 4.8 s/it to 22.1 s/it; released June 2025 — [OmniAvatar-14B model card mirror](https://huggingface.co/Weyther/OmniAvatar-14B)
- Other open models surfaced by search but not examined: SoulX-FlashHead ("96 FPS, or 3-concurrent real-time (25+ FPS) streaming on single RTX4090") and daVinci-MagiHuman ("15B open-source model ... Apache 2.0 licensed, multilingual") — [WaveSpeed talking-head tag page](https://wavespeed.ai/blog/tags/talking-head/); [SoulX-FlashHead mirror](https://cnb.cool/cdshiftingstars/SoulX-FlashHead)

### Inferences
- Hosted InfiniteTalk at $0.03/s is 120 × 0.03 = $3.60 per 2-minute presenter — between HeyGen Avatar III ($2.00) and Avatar IV/V ($8.00) at the reported rates — but it delivers an opaque 480p/720p clip, so it reintroduces a matting step and an upscale, and the repo itself warns of colour drift past a minute. On the facts found it does not reduce manual work versus HeyGen v3.
- Tavus at $1/min ($2.00 per video) is price-competitive with HeyGen Avatar III; whether it offers alpha output, 9:16 and good Hindi was not checked.
- For this team (low-technical operators, top quality, an existing HeyGen twin), self-hosting an open talking-head model adds GPU operations and a quality-control burden for a saving of at most a few dollars per video. That is a judgement, not a measured result.

### Gaps
- Not researched at all (no call made): Captions/Mirage, Colossyan, Akool, Creatify, OmniHuman (hosted), EchoMimic v3, Hallo3, LatentSync, MuseTalk, Sonic, FantasyTalking, HunyuanVideo-Avatar, Wan S2V. No licence, VRAM, speed or quality facts were gathered for these.
- No source found on Hindi lip-sync quality for any SaaS or open model; no head-to-head benchmark located.
- Transparent-background/alpha output and portrait support were not confirmed for Synthesia, D-ID, Tavus, Argil or Hedra.
- API (as opposed to subscription) pricing was not found for Synthesia, D-ID, Hedra or Argil.
- GPU rental cost per finished minute for the open models was not computed; no speed figures were obtained that would allow it.

## 3. Hindi TTS

### Takeaway
Sarvam Bulbul v3 is the cheapest by roughly an order of magnitude and wins the two Hindi comparisons I found (one vendor-commissioned, one small in-house benchmark), with a pronunciation dictionary and voice cloning; but I found no evidence it returns timestamps. ElevenLabs returns character-level alignment, which is the thing that would fix the caption-timing problem, at about 4–7x the price.

### Cited Findings

Sarvam Bulbul
- Bulbul v3: "Rs. 30 per 10,000 characters"; 35+ voices; 11 Indian languages including Hindi; code-switching "at the model level" for Hinglish; sample rates 8/16/22.05/24/48 kHz; REST handles up to 2,500 characters per request; consent-based voice cloning from 30–60 s samples — [Sarvam text-to-speech page](https://www.sarvam.ai/text-to-speech)
- A second listing describes the same ₹30/10k rate as a beta price — [callmissed Bulbul v3 listing](https://www.callmissed.com/models/bulbul-v3) (secondary; whether the price is still "beta" is unclear)
- ₹100 free credits on signup that "never expire"; tiers Starter (pay-as-you-go), Pro ₹10,000, Business ₹50,000, Enterprise; TTS REST limits 60/200/1,000 req/min, with Bulbul v3 Starter reduced to 30 req/min — [Sarvam pricing and rate limits docs](https://docs.sarvam.ai/api-reference-docs/getting-started/pricing)
- Pronunciation dictionary for Bulbul v3: upload JSON of word → spoken form, receive a `dictionary_id`, pass as `dict_id` on REST, HTTP stream or WebSocket; limits 10 dictionaries per user, 100 words per dictionary, 1 MB — [Sarvam pronunciation dictionary docs](https://docs.sarvam.ai/api/api-guides-tutorials/text-to-speech/pronunciation-dictionary)
- Blind A/B listening study by Josh Talks, 500+ annotators, 20,000+ votes, 11 languages: Bulbul v3 most preferred overall; at 8 kHz it beat ElevenLabs Flash v2.5 (77.95% vs 10.37%), ElevenLabs v3 alpha (43.64% vs 28.14%) and Cartesia Sonic-3 (40.08% vs 29.43%); at full band "ElevenLabs v3 alpha leads on audio quality; Bulbul V3 outperforms Cartesia Sonic-3" — [Sarvam Bulbul v3 blog](https://sarvam.ai/blogs/bulbul-v3) (published by the vendor; results are across 11 languages, not Hindi alone)

Independent-ish Hindi benchmark
- Caller Digital internal benchmark, 10 July 2026, Hindi: Bulbul MOS 4.5, code-switching 4.4, Indian-name accuracy 92%, about ₹1.50–2.00/min; ElevenLabs MOS 4.2, code-switching 3.8, names 78%, about ₹2.50–3.50/min; Google Cloud MOS 3.9, 3.4, 65%, about ₹1.20/min; AI4Bharat MOS 3.7, 3.3, 70%, about ₹0.10–0.30/min — [Caller Digital Indic TTS benchmark](https://caller.digital/blog/indic-tts-benchmark-bulbul-elevenlabs-sarvam-google-ai4bharat-2026) (a voice-agent company's own test on call-centre prompts; method and sample size not stated; model versions not stated)
- Same source, qualitative: ElevenLabs has slightly "American-English-influenced prosody on Hindi sentences" with noticeable code-switch boundaries; Google Neural2 is "functional and clean but flat" — [Caller Digital Indic TTS benchmark](https://caller.digital/blog/indic-tts-benchmark-bulbul-elevenlabs-sarvam-google-ai4bharat-2026)

ElevenLabs
- API price per 1,000 characters: v4 $0.022 (72% promotional discount until 12 Oct 2026, regular $0.08); v4 Turbo $0.011 (regular $0.04); v3 $0.08; v3 Conversational $0.04; Multilingual v2 $0.08; Flash/Turbo $0.04 — [ElevenLabs API pricing](https://elevenlabs.io/pricing/api)
- Plans: Starter $6, Creator $22, Pro $99, Scale $299, Business $990 per month; 90+ languages; audio tags on v4 — [ElevenLabs API pricing](https://elevenlabs.io/pricing/api)
- `/v1/text-to-speech/{voice_id}/with-timestamps` (and a streaming variant) returns audio plus an `alignment` object with per-character start/end times — [ElevenLabs SDK docs mirror (tessl)](https://tessl.io/registry/tessl/npm-elevenlabs/1.59.0/files/docs/text-to-speech.md); [Bifrost ElevenLabs provider docs](https://docs.getbifrost.ai/providers/supported-providers/elevenlabs.md)
- Pronunciation dictionaries: alias rules (text substitution) or phoneme rules; "Eleven v4 supports phoneme rules and inline IPA"; up to three dictionaries per request; v4 is claimed to handle "abbreviations, technical terms, names, and mixed-language text more accurately than any model before it" (vendor claim) — [ElevenLabs pronunciation dictionary guide](https://elevenlabs.io/blog/pronunciation-dictionary-guide)
- `apply_language_text_normalization` "is currently only supported for Japanese" — [Bifrost ElevenLabs provider docs](https://docs.getbifrost.ai/providers/supported-providers/elevenlabs.md) (third-party doc; may be stale)

Google
- Gemini 3.8 Flash TTS: $9 per 1M audio tokens through 31 Dec 2026, $18 from 1 Jan 2027; Flash-Lite TTS $6, then $12 — [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing)

### Inferences
- Rough cost of narration for one 2-minute video, assuming about 2,000 characters of Devanagari (my assumption, not measured): Sarvam ₹6; ElevenLabs v3 or v4 at list $0.16; v4 on the promotion $0.044. TTS is therefore a rounding error next to the avatar ($2–8) and generated clips ($1–10); choose on quality and timestamps, not price.
- The pipeline's existing rule that spoken lines contain no digits or symbols already sidesteps most number/formula-token normalisation risk, which matters because ElevenLabs' language-specific normalisation reportedly does not cover Hindi.
- If Sarvam has no timestamp output, using it means adding a forced-alignment step to get caption timings; ElevenLabs gives alignment for free. Either way captions should be built from the narration audio's alignment and not from HeyGen's SRT.
- Both benchmarks favour Bulbul on telephony/call-centre material. Neither tests two-minute expository teaching narration at studio quality, where the Josh Talks study itself says ElevenLabs v3 leads on audio quality. A side-by-side on three real scripts is the only way to settle it for this use.
- Sarvam's dictionary cap (100 words × 10 dictionaries) is small for a Class 12 science vocabulary; per-subject dictionaries would be needed.

### Gaps
- No documentation found either way on Sarvam timestamps/word alignment — two Sarvam pages were read and neither mentions it. Treat as "not offered" until checked against the API reference.
- Not confirmed that ElevenLabs `with-timestamps` works with v3 and v4 specifically, nor how alignment behaves on Devanagari conjuncts.
- Not researched (no call made): Cartesia Sonic pricing/features, OpenAI TTS, Azure, Chirp 3 HD, AI4Bharat Indic Parler-TTS / IndicF5 licences and quality, Smallest.ai, Hume. Bulbul v2 pricing was not retrieved.
- Gemini TTS: no Hindi quality evidence, no dollars-per-minute conversion (tokens per second of audio not retrieved), no timestamp information.
- No source found on any model's handling of spelled-out chemical formulae or Latin letters inside Hindi sentences.
- Voice-cloning terms and pricing for ElevenLabs were not retrieved.

## 4. Generative video through real APIs instead of Flow automation

### Takeaway
Veo 3.1 is available on the paid Gemini API at $0.05–$0.60 per second with image-to-video, first+last frame, up to three reference images and video extension — everything the Flow extension is being used to reach. The marker the team sees in Flow is very likely a visible watermark that Flow applies mandatorily in India; whether Gemini API / Vertex output carries any visible mark was not confirmed and is the single most important thing to test.

### Cited Findings

Veo on the Gemini API
- Model IDs `veo-3.1-generate-preview`, `veo-3.1-fast-generate-preview`, `veo-3.1-lite-generate-preview` — [Gemini API Veo docs](https://ai.google.dev/gemini-api/docs/veo)
- Price per second of output: Standard $0.40 (720p/1080p), $0.60 (4K); Fast $0.10 (720p), $0.12 (1080p), $0.30 (4K); Lite $0.05 (720p), $0.08 (1080p) — [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing); same figures dated 11 Sep 2026 at [benchlm.ai Veo pricing](https://benchlm.ai/media-pricing/veo)
- Durations 4, 6 or 8 s; 8 s is required at 1080p/4K or when using reference images; 24 fps; aspect ratios 16:9 and 9:16 only — [Gemini API Veo docs](https://ai.google.dev/gemini-api/docs/veo)
- Image-to-video on all three variants; first/last-frame interpolation on Veo 3.1 and Fast; up to 3 reference images on Veo 3.1 and Fast (not Lite) — [Gemini API Veo docs](https://ai.google.dev/gemini-api/docs/veo)
- Extension: Veo 3.1 and Fast only; extends a previous generation by 7 s, repeatable up to 20 times, 720p only — [Gemini API Veo docs](https://ai.google.dev/gemini-api/docs/veo)
- Latency minimum 11 s, up to 6 minutes at peak; generated videos kept on the server for 2 days; audio generated natively — [Gemini API Veo docs](https://ai.google.dev/gemini-api/docs/veo)
- Regional `personGeneration` restrictions are listed for EU, UK, CH and MENA; India is not mentioned — [Gemini API Veo docs](https://ai.google.dev/gemini-api/docs/veo)
- A newer Google video model exists: `gemini-omni-1.1-flash`, about $0.10 per second of 720p video (5,792 tokens/s at $17.50 per 1M) — [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing)

Watermarks
- "Google Flow stamps a small 'veo' wordmark in the corner of videos from most accounts"; there is a "Visible watermarking" toggle under the profile picture in Flow; India, South Korea and Vietnam are places "where the badge applies automatically regardless of the setting" — [Atlas Cloud article on the Veo watermark](https://www.atlascloud.ai/blog/tips/veo-watermark-remover) (a reseller's blog quoting Flow's help text; not Google's own page)
- "All outputs generated in Google Flow using Veo, Omni, or Nano Banana include invisible SynthID watermarks" — no tier exemption — [Atlas Cloud article on the Veo watermark](https://www.atlascloud.ai/blog/tips/veo-watermark-remover)
- Google's India launch post says videos carry "a visible watermark and ... an invisible digital SynthID watermark" (consumer Gemini app) — [Google India blog: Veo 3 launches in India](https://blog.google/intl/en-in/company-news/technology/veo-3-launches-in-india/)
- The Gemini API Veo page says videos receive SynthID watermarking. The fetch tool summarised this as a "visible identification method"; SynthID is described everywhere else as imperceptible, so I treat that summary as a misreading, not as evidence of a visible mark — [Gemini API Veo docs](https://ai.google.dev/gemini-api/docs/veo); [YourStory on Veo 3.1](https://yourstory.com/ai-story/google-veo-3-1-ingredients-to-video-update)
- One search summary claimed Vertex AI users "can choose whether to embed SynthID tags or visible overlays"; I could not trace that to a Google page — unverified — [Google developer forum thread: Veo 3 – Vertex AI and other APIs](https://discuss.google.dev/t/veo-3-vertex-ai-and-other-apis/257446)

Competitors and aggregators
- fal.ai image-to-video prices: Seedance 2.0 $0.3024–0.3034/s Standard, $0.2419/s Fast (720p, audio included); Kling 3.0 Pro $0.112/s audio off, $0.168/s with audio, $0.196/s with voice control; Veo 3.1 $0.20/s without audio, $0.40/s with audio — [fal.ai image-to-video API listing](https://fal.ai/explore/image-to-video-apis); [fal.ai Seedance 2.0 vs Kling 3.0](https://fal.ai/learn/tools/seedance-2-0-vs-kling-3-0)
- Conflict: a roundup lists Seedance 2.0 Fast at "~$0.09/second" and Kling 3.0 at "roughly $0.10/sec" — much lower than fal's Seedance price; resolution/provider basis not stated — [techsy.io best AI video models](https://techsy.io/en/blog/best-ai-video-models)
- Seedance 2.0 accepts up to 9 reference images, 3 reference videos and 3 audio clips in one call, addressable by name in the prompt — [fal.ai Seedance 2.0 vs Kling 3.0](https://fal.ai/learn/tools/seedance-2-0-vs-kling-3-0)
- Kling 3.0 adds multi-shot storyboarding, element referencing and 15-second output; "Elements 3.0 caps at four reference images plus a video lock" — [fal.ai Seedance 2.0 vs Kling 3.0](https://fal.ai/learn/tools/seedance-2-0-vs-kling-3-0)
- Seedance 2.0 led the Artificial Analysis image-to-video arena at about 1,344–1,351 Elo as of June 2026; Kling 3.0 topped a different arena (llm-stats) — [techsy.io best AI video models](https://techsy.io/en/blog/best-ai-video-models) (secondary report of the leaderboards; the leaderboard itself was not opened)
- "OpenAI is switching Sora 2 off, with the API ending on September 24, 2026" — [techsy.io best AI video models](https://techsy.io/en/blog/best-ai-video-models) (single secondary source; not confirmed with OpenAI)
- A "Seedance 2.5" is advertised as live on Atlas Cloud (banner text only; no details gathered) — [Atlas Cloud Kling consistency guide](https://www.atlascloud.ai/blog/tips/how-to-use-kling-3.0-for-character-consistency)
- HeyGen's own `cinematic_avatar` video type is described as a "Seedance pipeline" — [HeyGen Create Video reference](https://developers.heygen.com/reference/create-video.md)

Image models
- Gemini API image prices: Nano Banana 2.1 (`gemini-nano-banana-2.1`) about $0.034 per 1K image, $0.050 per 2K, $0.113 per 4K (half price in batch); Gemini 3.1 Flash Image about $0.067 per 1K image; Flash Lite Image about $0.034 — [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing)
- Nano Banana 2 is claimed to render accurate text in "Japanese, Chinese, Korean, Arabic, and dozens of other languages" — [Framia blog on Nano Banana 2 multilingual text](https://framia.converge.ai/page/en-US/blog/nano-banana-2-multilingual-text) (marketing blog; Hindi/Devanagari not named)

### Inferences
- Cost of generated footage per video, assuming three 8-second clips = 24 s (my assumption): Veo 3.1 Lite 720p $1.20; Veo 3.1 Fast 1080p $2.88; Kling 3.0 Pro on fal, no audio, $2.69; Seedance 2.0 Fast on fal $5.81; Veo 3.1 Standard $9.60. Rejected takes multiply these; the repo's review loop means the real figure is some multiple of the list price.
- The API directly addresses the three Flow pain points in the brief: (a) no browser automation — a plain REST call with an operation to poll; (b) the subject plate can be sent as the image-to-video input, matching the repo's "background is uploaded, not described" rule; (c) clip-to-clip mismatch has three documented tools — the previous clip's last frame as first frame, first+last-frame interpolation, and the 7-second extension chain. Extension is 720p-only, so a chained sequence would be 720p throughout.
- The "sparkle" the team delogos is plausibly Flow's mandatory-in-India visible watermark. That rule is described for Flow (and the consumer app), not for the developer API. It is likely, but not confirmed, that Gemini API output carries only the invisible SynthID. Budget a ten-minute test with one paid API call from an Indian billing account before designing around it.
- 16:9/9:16 only and an 8-second ceiling per generation are properties of Veo itself, not of Flow, so moving to the API does not change them. Kling 3.0's 15-second output would cover a typical beat in one generation where Veo needs a slow/loop/hold.
- For apparatus consistency across consecutive beats, Seedance 2.0's nine named reference images and Kling's Elements are purpose-built for it and Veo's limit is three reference images. No source I found tests any of them on text-free scientific process shots, so "which is most accurate" is open.
- Going through fal.ai for Veo is not cheaper than Google direct for the tiers found ($0.20–0.40/s on fal vs $0.10–0.12/s for Veo 3.1 Fast direct); an aggregator's value would be a single integration across Kling/Seedance/Veo, not price.

### Gaps
- Visible-watermark behaviour of Gemini API and Vertex AI output, specifically for Indian accounts, is unconfirmed. No Google page was found that states it either way.
- Vertex AI pricing, rate limits/quotas for Veo on either surface, and whether the paid Gemini API is purchasable from India were not retrieved.
- Whether a Veo newer than 3.1 exists was not established; the Gemini API docs list only 3.1 variants plus Gemini Omni 1.1 Flash. Omni's durations, aspect ratios and conditioning features were not retrieved.
- Not researched (no call made): Runway Gen-4/4.5 and Aleph, Luma Ray 3, Hailuo/MiniMax, Pika, Wan 2.2/2.5/2.6 open weights, LTX-2, HunyuanVideo, Replicate and Higgsfield pricing, Kling's and ByteDance's own first-party API prices.
- The Artificial Analysis leaderboard was not opened directly; current rankings are second-hand and dated June 2026.
- Sora 2 API shutdown rests on one secondary source.
- Devanagari text accuracy and transparent-background output were not verified for any image model (Nano Banana, GPT-image, Seedream, Ideogram, FLUX.2). GPT-image, Seedream, Ideogram and FLUX.2 pricing was not retrieved.

## 5. Matting without a green screen, and better keying if green stays

### Takeaway
MatAnyone 2 (CVPR 2026) is the current open state of the art for human video matting, but it ships under the NTU S-Lab License 1.0 — which needs a licence read before commercial use — and needs a first-frame mask. I gathered almost nothing on speed, Apple Silicon performance or the other tools, and if HeyGen's alpha WebM works for the team's twin this whole stage disappears.

### Cited Findings
- MatAnyone 2: CVPR 2026 paper from NTU S-Lab and SenseTime; introduces a learned Matting Quality Evaluator and the VMReal dataset (28,000 clips, 2.4M frames); on the CRGNN real-world benchmark it cuts MAD by 26% and gradient error by 24.5% versus MatAnyone 1 — [MatAnyone 2 paper (CVPR 2026 open access)](https://openaccess.thecvf.com/content/CVPR2026/html/Yang_MatAnyone_2_Scaling_Video_Matting_via_a_Learned_Quality_Evaluator_CVPR_2026_paper.html); [arXiv 2512.11782](https://arxiv.org/abs/2512.11782v1); summary figures via [gaga.art write-up](https://gaga.art/blog/matanyone-2/)
- Licence: "NTU S-Lab License 1.0"; the repo says "Redistribution and use should follow this license" — [MatAnyone2 GitHub](https://github.com/pq-yang/MatAnyone2)
- Input is "a video and its first-frame segmentation mask" (obtainable from SAM2); outputs a foreground video and an alpha video; no default resolution limit; examples use `cuda:0`; no MPS/Apple Silicon support mentioned in the repo — [MatAnyone2 GitHub](https://github.com/pq-yang/MatAnyone2)
- A third-party comparison table rates MatAnyone 2 as hair-level precision with 8 GB+ VRAM, and RobustVideoMatting as medium edge accuracy with flicker and lower VRAM — [aifilms.ai MatAnyone 2 write-up](https://studio.aifilms.ai/blog/matanyone-2-video-matting) (secondary, no method given)
- Search surfaced claims of "production mattes at up to 2K and 60fps" with guided-filter edge refinement, a ComfyUI pipeline that uses BiRefNet to auto-generate the person mask, and "MatAnyone2Kit", a third-party Core ML / Swift port for Apple platforms — [Hugging Face mirror kamaz01/MatAnyone2](https://huggingface.co/kamaz01/MatAnyone2); [RunComfy TrentNodes MatAnyone node](https://www.runcomfy.com/comfyui-nodes/TrentNodes/mat-anyone-matte) (none of these opened or tested)
- MatAnyone is offered as a hosted model by Beeble — [Beeble MatAnyone page](https://beeble.ai/models/matanyone)
- Upstream alternative that avoids matting altogether: HeyGen `output_format: "webm"` delivers alpha directly for matting-trained avatars — [HeyGen Transparent Background Videos](https://developers.heygen.com/transparent-background-videos.md)

### Inferences
- Order of preference on the evidence found: (1) alpha WebM straight from HeyGen — no keying, no calibration, nothing for an operator to do; (2) if that fails a quality test, keep the green-screen MP4 and automate the key; (3) only then a learned matte. A green plate is an easier problem than arbitrary-background matting, so option 3 is mostly relevant if the presenter source ever stops being HeyGen.
- The team's machine is an 8 GB Apple Silicon box that already swaps (per project notes). MatAnyone 2 with a quoted 8 GB+ VRAM requirement and CUDA-only examples is not a comfortable fit locally; it would mean a rented GPU or a hosted endpoint.
- The NTU S-Lab licence family has historically been non-commercial; I did not read this repo's licence file, so that is a flag to check and not a finding.

### Gaps
- Not researched (no call made): RobustVideoMatting, BiRefNet video use, BackgroundMattingV2, MODNet, SAM 2 / SAM 3 + matting pipelines, Apple Vision person segmentation, DaVinci Resolve Magic Mask, Runway/Unscreen/Kling background-removal APIs — no licences, speeds or quality facts gathered.
- No fps figures found for any matting model on Apple Silicon or on a specific NVIDIA card.
- The commercial-use terms of NTU S-Lab License 1.0 for MatAnyone 2 were not read.
- Nothing was researched on improved chroma keying: GPU keyers, ffmpeg hardware-accelerated filters, or automatic key calibration (for example sampling the plate colour per clip). This part of the question is unanswered.
- Edge quality of HeyGen's alpha WebM on hair is untested.

## 6. Scientific-animation alternatives to generative video

### Takeaway
Barely researched: one search, which returned only BioRender subscription pricing and licensing terms. No evidence was gathered on stock science-animation libraries, molecular Blender tools, or Rive/Lottie.

### Cited Findings
- BioRender: Academic Individual $35/month billed annually or $39 month-to-month; Industry Individual $95/month billed annually or $115 month-to-month; library of 50,000+ life-science icons and templates — [ConceptViz: BioRender pricing 2026](https://conceptviz.app/blog/biorender-pricing-2026) (a competitor's blog)
- BioRender licensing as reported: free-plan figures cannot be used in publications or commercial work; finished graphics must carry "Created with BioRender.com" or the figure URL; publication licence generated on export from a paid plan — [ConceptViz: BioRender pricing 2026](https://conceptviz.app/blog/biorender-pricing-2026)

### Inferences
- A commercial edtech company would fall under BioRender's Industry tier, and the attribution requirement conflicts with this project's rule that the screen carries nothing but what teaches. That makes BioRender a poor fit for on-screen video assets on the terms reported, though the terms should be read at source.
- The reuse argument is structural and independent of any vendor: a Class 12 syllabus has a bounded set of processes (rusting, electrolysis, a galvanic cell, and so on). A process shot that is generated once, reviewed once and stored keyed by concept costs nothing and carries no review risk on its second use, whereas each fresh generation costs $1–10 and a review pass. This is my reasoning, not a sourced finding.

### Gaps
- Not researched: stock/licensed science animation libraries (Science Photo Library, Shutterstock/Pond5/Storyblocks science collections, and any with an API), their licence terms for commercial educational video, and prices.
- Not researched: Blender molecular tooling (for example Molecular Nodes), Rive and Lottie libraries, or any Indian-curriculum-specific animation library.
- BioRender's own pricing/licence pages were not opened; animation/export capabilities were not checked.

## Closing synthesis: what removes the manual steps at the lowest cost per finished 2-minute video

### Takeaway
On the evidence gathered, the lowest-effort route is: narration from a TTS API, passed as audio to HeyGen v3 for a 9:16 alpha-WebM digital twin delivered by webhook, plus Veo 3.1 Fast or Lite on the paid Gemini API for process shots. That removes the manual download, the keying and the Flow extension for roughly $3–11 per video in vendor charges, dominated by the avatar engine choice. Two facts in that chain are unverified and should be tested before committing: HeyGen's list prices and alpha quality, and whether Gemini API output is free of a visible mark in India.

### Cited Findings
- HeyGen: alpha WebM, 9:16, external `audio_url`, webhooks, 10 concurrent jobs on pay-as-you-go — [Transparent Background Videos](https://developers.heygen.com/transparent-background-videos.md); [Create Video reference](https://developers.heygen.com/reference/create-video.md); [Usage Limits](https://developers.heygen.com/docs/usage-limits.md)
- HeyGen reported rates: $0.0167/s (Avatar III digital twin) to $0.0667/s (Avatar IV/V digital twin) — [G2: HeyGen API pricing](https://www.g2.com/articles/heygen-api-pricing)
- Veo 3.1 Lite $0.05/s (720p), Fast $0.12/s (1080p), Standard $0.40/s — [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing)
- Sarvam Bulbul v3 ₹30 per 10,000 characters; ElevenLabs v3/v4 $0.08 per 1,000 characters at list — [Sarvam text-to-speech page](https://www.sarvam.ai/text-to-speech); [ElevenLabs API pricing](https://elevenlabs.io/pricing/api)
- ElevenLabs returns per-character alignment; HeyGen returns only an SRT — [ElevenLabs SDK docs mirror (tessl)](https://tessl.io/registry/tessl/npm-elevenlabs/1.59.0/files/docs/text-to-speech.md); [HeyGen Get Video reference](https://developers.heygen.com/reference/get-video.md)

### Inferences
Per-video vendor cost, 120 s of presenter + 24 s of generated footage + about 2,000 characters of narration (assumptions mine; excludes rejected takes, LLM calls and compute):

| Component | Cheapest documented option | Higher-quality option |
|---|---|---|
| Narration | Sarvam Bulbul v3, about ₹6 | ElevenLabs v3/v4, about $0.16 list |
| Presenter | HeyGen Avatar III digital twin, about $2.00 | HeyGen Avatar IV or V digital twin, about $8.00 |
| Process shots | Veo 3.1 Lite 720p, about $1.20 | Veo 3.1 Fast 1080p, about $2.88 (Standard: $9.60) |
| Keying | none (alpha WebM) | none (alpha WebM) |
| Total | about $3.30 | about $11.00 (about $17.80 with Veo Standard) |

- At 10 videos per operator per day that is about $33–110 per operator per day before retries. The avatar engine is the dominant line and the main cost lever; a blind comparison of Avatar III vs IV vs V on the team's own twin decides most of the budget.
- Suggested test order, cheapest first: (1) one `POST /v3/videos` with the existing twin, `aspect_ratio: "9:16"`, `output_format: "webm"`, `audio_url` — checks matting eligibility, alpha edge quality and real price in one call; (2) one paid Gemini API Veo 3.1 Fast image-to-video call from the team's own billing account — checks the visible mark and India availability; (3) the same three Hindi scripts through Bulbul v3 and ElevenLabs v3/v4 for a listening test, and a check of whether Sarvam returns alignment.
- Concurrency is not the constraint: 10 concurrent HeyGen jobs on pay-as-you-go against a target of 10 videos per operator per day.

### Gaps
- Total cost excludes failure rates. No source gives rejection rates for generated science clips; the project's own review logs are the right source.
- Everything in Q2, Q5 and Q6 marked "not researched" could change this recommendation in principle — in particular a cheaper SaaS avatar with alpha output, or a first-party Kling/Seedance price well below fal's.
- HeyGen web-plan credit economics (the MCP/OAuth billing route) were not compared with the API wallet.
