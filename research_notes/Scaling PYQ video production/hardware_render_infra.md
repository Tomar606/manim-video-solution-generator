# Hardware and render infrastructure for scaling the PYQ video pipeline (state as of 8 Oct 2026)

Reading conventions used throughout:
- **[fetched]** = I opened the page and read the figure. **[snippet]** = the figure came from a search-result summary only; the page itself was not opened (or returned 403), so treat as lower confidence.
- **[local]** = measured on the team's current machine in this session.
- INR/USD conversions are mine and use a round **Rs 90 = USD 1 (assumption, not sourced)**; they are for order-of-magnitude only.
- Two market facts dominate every buying decision in late 2026 and were not true a year earlier: (1) a DRAM/NAND shortage has roughly tripled PC memory prices in India and pushed Hetzner's prices up sharply; (2) Apple refreshed the Mac mini and Mac Studio on 22 Sept 2026 at visibly higher India prices.

---

## 1. Apple Silicon options in late 2026 (lineup, India prices, measured performance, RAM, storage)

### Takeaway
The desktop Mac lineup was refreshed on 22 Sept 2026: Mac mini is now M6 (from Rs 99,900, 16 GB) or M5 Pro (from Rs 2,09,900, 24 GB/512 GB), Mac Studio is M5 Max (from Rs 2,79,900) or M5 Ultra (from Rs 6,29,900). The entry price of a usable Mac render node has risen a lot versus the M4 mini (Rs 59,900 at launch in 2024), and independent media-pipeline benchmarks for the new chips are still thin.

### Cited Findings

**Lineup and India prices**
- New Mac mini (M6, M5 Pro) and Mac Studio (M5 Max, M5 Ultra) were announced 26 Aug 2026, pre-order open, shipping from 22 Sept 2026. India start prices: Mac mini M6 Rs 99,900 "for the 16GB RAM and 256GB storage model"; Mac mini M5 Pro Rs 2,09,900; Mac Studio M5 Max Rs 2,79,900; Mac Studio M5 Ultra Rs 6,29,900. [fetched] — [ETV Bharat, 26 Aug 2026](https://www.etvbharat.com/amp/en/technology/2026-apple-mac-studio-2026-mac-mini-m6-chip-m5-ultra-chip-enn26082601315)
- Same prices plus education prices: mini M6 Rs 88,900, mini M5 Pro Rs 1,97,900, Studio M5 Max Rs 2,56,900, Studio M5 Ultra Rs 5,84,900. Specs: M6 = 12-core CPU / 12-core GPU, 16 GB up to 32 GB, 170 GB/s memory bandwidth; M5 Pro = up to 18-core CPU / 20-core GPU, up to 64 GB, 307 GB/s; M5 Max = 18-core CPU, up to 40-core GPU, up to 128 GB; M5 Ultra = up to 36-core CPU, 80-core GPU, up to 512 GB (512 GB config ships late October). Mac mini has 2.5 Gb Ethernet standard with a 10 Gb option; Mac Studio has Thunderbolt 5. [fetched] — [Gizbot](https://www.gizbot.com/laptop/news/apple-mac-mini-m6-mac-studio-m5-ultra-india-price-specs-availability-128701.html)
- Mac mini M6 with 24 GB / 512 GB is Rs 1,47,900; the M5 Pro mini's Rs 2,09,900 base is 24 GB / 512 GB; M5 Pro memory 24-64 GB, storage 512 GB-8 TB. [snippet] — [Technosports](https://technosports.co.in/mac-mini-m6-india-price-all-variants/), [Business Standard](https://www.business-standard.com/technology/gadgets/apple-refreshes-mac-mini-with-new-m6-chip-check-india-price-offers-126082600328_1.html) (the Business Standard page returned 403 on fetch)
- CONFLICT / unverified: a search summary gave "Mac mini with M6 starts at $1,249 ... M5 Pro $2,399 ... Mac Studio M5 Max $3,499 ... M5 Ultra $7,799". Rs 99,900 against $1,249 implies Rs 80/USD, which is cheaper than Apple India normally is, and one of the pages returned is a Canadian outlet, so these may be CAD not USD. US list prices are NOT confirmed. [snippet] — [WiFi HiFi](https://wifihifi.com/?p=36552), [Deccan Herald (403 on fetch)](https://www.deccanherald.com/technology/apple-unveils-all-new-mac-mini-mac-studio-with-next-gen-m6-m5-silicons-4123800)
- Reviewers flag the value regression: Tom's Hardware titles its review "Strong performance, but losing its grip on value"; Macworld titles the M5 Pro mini review "Killer performance at a lethal price". [snippet, titles only] — [Tom's Hardware](https://www.tomshardware.com/desktops/mini-pcs/apple-mac-mini-late-2026-review), [Macworld](https://www.macworld.com/article/3239233/mac-mini-m5-pro-review-killer-performance-at-a-lethal-price.html)
- Previous generation for reference: M4 Mac mini launched in India at Rs 59,900 (Oct 2024); M4 Pro mini Rs 1,49,900. [snippet] — [Business Today](https://www.businesstoday.in/amp/technology/news/story/apple-launches-new-mac-mini-in-india-at-rs-59990-with-almost-double-performance-better-connectivity-452017-2024-10-30), [The Tech Outlook](https://www.thetechoutlook.com/new-release/gadgets-release/new-apple-mac-mini-m4-and-m4-pro-models-launched-with-a-smaller-design-better-performance-and-with-apple-intelligence/)
- M4 Mac mini 16 GB / 512 GB is listed at Rs 79,900 on an Indian price tracker but shown OUT OF STOCK; price last changed 16 Jun 2026. [snippet] — [Smartprix](https://www.smartprix.com/computers/apple-m4-mac-mini-mu9e3hn-a-apple-m4-16-gb-ppd1uqjlpa3l)
- Previous-generation Mac Studio (Mar 2025): M4 Max 36 GB / 512 GB from Rs 2,14,900; M3 Ultra 96 GB / 1 TB from Rs 4,29,900. [snippet] — [Business Today](https://www.businesstoday.in/amp/technology/news/story/apple-unveils-new-mac-studio-with-m4-max-and-m3-ultra-466869-2025-03-05)
- Laptops (M5, launched March 2026): MacBook Air 13" 16 GB / 512 GB Rs 1,19,900; Air 15" Rs 1,44,900; MacBook Pro 14" M5 16 GB / 512 GB Rs 1,69,900, 16 GB / 1 TB Rs 1,89,900, 24 GB / 1 TB Rs 2,09,900. Base Air is now 16 GB / 512 GB. [snippet] — [ETV Bharat](https://www.etvbharat.com/amp/en/technology/apple-macbook-air-2026-launched-in-india-price-specifications-enn26030401257); a later report says the Air M5 street price fell "close to Rs 1 lakh" — [TelecomTalk](https://telecomtalk.info/macbook-air-m5-price-falls-close-to-rs-1-lakh-in-india/1008740/)

**CPU performance**
- Geekbench 7: M6 4,055 single-core / 22,695 multi-core; M5 Pro 34,281 multi-core. M6 is ~21% faster single-core than the M4 Pro mini. Apple's claims for M6 vs M4: up to 40% faster CPU, 2x graphics, up to 4x AI. [snippet] — [Tom's Hardware](https://www.tomshardware.com/desktops/mini-pcs/apple-mac-mini-late-2026-review), [Macworld](https://www.macworld.com/article/2964754/2026-mac-mini-m5-pro-design-specs-release-date.html)

**Whisper on Apple Silicon**
- whisper.cpp with Metal, large-v3: M1 2-3x realtime, M5 Pro 10-12x, M5 Max 12-14x; large-v3-turbo 14-18x realtime on base M5. Page dated 26 Aug 2026 and states M6 / M5 Ultra "have no independent Whisper/Metal benchmarks yet". Aggregator site, methodology not shown — treat as indicative. [fetched] — [PromptQuorum](https://www.promptquorum.com/local-llms/apple-silicon-whisper-metal-benchmark)
- A community speed test repo reports on M4: mlx-whisper large-v3-turbo and whisper.cpp large-v3-turbo-q5_0 (CoreML, 4 threads) at roughly 1.0-1.2 (units ambiguous in the summary — almost certainly seconds for a short clip, not a realtime factor). [snippet, ambiguous] — [mac-whisper-speedtest](https://github.com/anvanvan/mac-whisper-speedtest)
- large-v3-turbo cuts the decoder from 32 layers to 4 (1.55B -> 809M params), 2-5x faster with near-identical accuracy. [snippet] — [Whisper Notes](https://whispernotes.app/es/blog/introducing-whisper-large-v3-turbo)

**VideoToolbox encode**
- h264_videotoolbox: ~10-20% larger files than libx264 at ~5-10x the speed (one guide: ~1.15x size at ~8x speed). [snippet] — [Frame docs](https://www.mintlify.com/66HEX/frame/guides/hardware-acceleration)
- Reported VideoToolbox H.264 weaknesses: visible artefacts on animated slideshows/blur at 1080p60 where NVENC and libx264 look better at equal size; defaults give soft detail. On M1 hardware HEVC encode is ~15x faster than libx265 and handles 4K in realtime. (Old M1-era sources.) [snippet] — [Apple Developer Forums](https://developer.apple.com/forums/thread/678210), [yre.jp](https://yre.jp/en/post/m1mac_h265/)

**Storage and current machine**
- 2 TB NVMe prices in India (2026): Kingston KC3000 Rs 9,990 (listed), Adata XPG S60 Rs 15,990, Crucial P3 Plus Rs 27,500 — wide spread, check the day's price. [snippet] — [ModX Computers](https://modxcomputers.com/product/adata-xpg-gammix-s60-2tb-nvme-gen4/), [Micro Center India](https://microcenterindia.com/collections/nvme-ssd)
- [local] The current machine reports 8 logical CPUs and 8,589,934,592 bytes (8 GB) RAM; ffmpeg is Homebrew 8.1 with only `videotoolbox` as a hwaccel. — reference: [ffmpeg hwaccel docs](https://trac.ffmpeg.org/wiki/HWAccelIntro)

### Inferences
- **8 GB is the root cause of most of the observed pain, not CPU speed.** Chromium + a 1080x1920 RGBA filter graph + x264 lookahead + Whisper large cannot coexist in 8 GB; the 13 GB swap and crashes are the symptom. Minimum sensible operator machine is 24 GB; 16 GB works only if exactly one heavy job runs at a time.
- Cheapest new Apple machine that is not memory-starved is the **Mac mini M6 24 GB / 512 GB at Rs 1,47,900 (~USD 1,640)**. The M5 Pro mini (Rs 2,09,900, ~USD 2,330) buys ~50% more multicore (34,281 vs 22,695) for 42% more money — reasonable for a shared render node, poor value per operator seat.
- Do not buy internal Apple SSD upgrades: a 2 TB external NVMe plus a Thunderbolt/USB4 enclosure is roughly Rs 13,000-30,000 (drive price above plus an enclosure — enclosure price NOT sourced), far below Apple's upgrade steps. 256 GB internal is too small for this workload even with external scratch; take 512 GB.
- Remaining M4 mini stock (Rs 79,900 for 16/512 where found) is the bargain if any can still be bought, but stock appears to be drying up.
- For transcription the Whisper stage is negligible on any current Mac: at 10x+ realtime a 90 s part transcribes in under 10 s. It only hurts today because the model's memory competes with everything else in 8 GB.

### Gaps
- Confirmed US list prices for the Sept 2026 Mac mini / Mac Studio (the figures found are probably CAD). Apple India's own store page was not fetched; all India prices come from Indian news outlets quoting Apple.
- Full India price ladder (M6 32 GB, M5 Pro 48/64 GB, Studio RAM steps, 10 GbE option price).
- No measured ffmpeg/VideoToolbox fps, ProRes encode fps, or headless-Chromium frames/s numbers for M4, M5 or M6 were found. No WhisperKit numbers found. No MLX-Whisper realtime factors on M5/M6 found.
- Whether Apple still sells M4 minis officially (refurb or otherwise) in India was not established.
- Peak RAM per stage for this specific pipeline is not measured; the 24 GB recommendation is a judgement.

---

## 2. PC/Linux alternative (Ryzen/Threadripper/Core Ultra + RTX 50-series, India prices, NVENC/CUDA filters, shared render server)

### Takeaway
A Linux box with a 16-core Ryzen and an RTX 5070 Ti-class card is the only option where the whole composite (decode -> key -> overlay -> encode) can stay on the GPU with stock ffmpeg filters, but the 2026 memory shortage has pushed a 64 GB DDR5 kit alone to Rs 83,000+, erasing most of the traditional PC price advantage over a Mac mini.

### Cited Findings
- RTX 5070 Ti 16 GB: listed at Rs 80,000 on one aggregator, but current street price is quoted at ~Rs 1,00,800-1,11,300; RTX 5080 16 GB listed at Rs 1,07,000 (aggregator list price, likely stale/low). [snippet; sources disagree with each other] — [Smartprix](https://www.smartprix.com/computer_graphic_cards/nvidia-brand), [GetPC](https://getpc.co.in/parts/nvidia-rtx-5070-ti)
- Ryzen 9 9950X (16C/32T): all-time low Rs 54,829, average Rs 65,444, Amazon India listing Rs 78,999; forum reports ~Rs 61,000 locally. [snippet] — [pricehistory.app](https://pricehistory.app/p/amd-ryz-n-9-9950x-desktop-processor-zAqGBxmb), [TechEnclave](https://techenclave.com/threads/ryzen-9-9950x3d-reviewed-spoiler-its-great.226002/post-2593991)
- Memory shortage: a 32 GB DDR5 kit that cost ~Rs 8,000 a year ago is Rs 25,000-30,000 (other source: Rs 40,000-42,000); Crucial Pro 64 GB kit Rs 83,289; Corsair Dominator 64 GB Rs 1,23,999. Cause: AI data-centre demand diverting DRAM. [snippet] — [CloudPe](https://www.cloudpe.com/blog/why-is-ram-pricing-increasing-in-india-heres-what-businesses-need-to-know-in-2026/), [MagicDrop](https://magicdrop.in/drops/64gb-ram)
- An Indian system builder's site banner: "PC prices will rise in JULY 2026 due to AI component scarcity". [snippet] — [ModX Computers](https://modxcomputers.com/product/adata-xpg-gammix-s60-2tb-nvme-gen4/)
- `chromakey_cuda` (merged July 2022) is a CUDA YUV chroma-key that operates on CUDA frames; `overlay_cuda` accepts only CUDA frames; documented usage keys one input and overlays it on a `scale_cuda` base, encoding with `h264_nvenc`, entirely on the GPU. [snippet] — [ffmpeg-cvslog: add chromakey_cuda](https://ffmpeg.org/pipermail/ffmpeg-cvslog/2022-July/132988.html), [ffmpeg-devel March 2025 thread](https://ffmpeg.org/pipermail/ffmpeg-devel/2025-March/341251.html)
- faster-whisper on RTX 4090: large-v3-turbo ~80x realtime single stream, ~175x batched at 16. Turbo needs ~1.6 GB VRAM at INT8. On an RTX 3060 laptop, batched (10) turbo took 18.7 s vs 43.0 s for large-v3 on the same test. Vendor/aggregator blogs, not a controlled benchmark. [snippet] — [GigaGPU](https://gigagpu.com/rtx-4090-24gb-whisper-benchmark/), [Vexascribe](https://vexascribe.com/whisper-large-v3-vs-turbo)
- Modern NVENC (Turing and newer) matched or beat x264 medium in 8 of 11 test sequences in one VMAF comparison. [snippet] — [FaceOfIT](https://www.faceofit.com/nvenc-vs-x264/), [Igor's Lab VMAF analysis](https://www.igorslab.de/en/nvidias-nvenc-vs-cpu-encoding-the-turing-video-encoder-for-twitch-streaming-co-comparison-analysis-with-netflix-vmaf/3/)

### Inferences
- Rough build for one shared render box (ESTIMATE, parts summed from the figures above; motherboard/PSU/case/cooler figure is my guess, not sourced): 9950X ~Rs 65,000 + RTX 5070 Ti ~Rs 1,05,000 + 64 GB DDR5 ~Rs 85,000 + 2 TB NVMe ~Rs 16,000 + board/PSU/case/cooler ~Rs 55,000 = **~Rs 3.2-3.5 lakh (~USD 3,600-3,900)**. A year ago the RAM line would have been ~Rs 16,000.
- One such box can plausibly serve 5-10 operators **as a queue worker**, because the binding constraint is throughput per day (see section 8), not interactivity. It cannot serve them as a shared interactive desktop.
- `chromakey_cuda` is a single YUV-distance key. The current recipe (hsvkey twice + blend + erosion + despill) has no CUDA equivalent, so moving to the GPU path means re-tuning the key and re-approving the look, not just swapping filter names. The spill/edge quality on a real HeyGen plate is untested.
- The GPU is only worth buying if the composite stage is actually moved onto it. Manim (Cairo) and Chromium screenshotting are CPU-bound and get nothing from an RTX card. If the composite is fixed in software (section 3), the GPU line item can be dropped and a 9950X-only box at ~Rs 2.2-2.4 lakh (estimate) or a Mac mini M5 Pro does the job.
- Operational cost for a low-technical team: a Linux/NVIDIA box needs driver + ffmpeg-with-nvidia build maintenance that a Mac does not. Someone technical must own it.

### Gaps
- No measured fps for `chromakey_cuda` + `overlay_cuda` at 1080x1920 was found anywhere; the ffmpeg docs and list posts give usage only.
- Threadripper and Core Ultra India prices were not researched; complete-workstation (prebuilt) India prices were not found.
- No source establishes how many concurrent NVENC/CUDA sessions a 5070 Ti handles for this graph.
- GPU prices in India are inconsistent across trackers (Rs 80,000 vs Rs 1,00,000+ for the same card); get a live quote.

---

## 3. ffmpeg-level speedups for chroma-key compositing, and alternatives to ffmpeg

### Takeaway
The filters in the current recipe are all slice-threaded in ffmpeg 8.1, so a "single-threaded, CPU mostly idle" composite points at pixel-format conversions, an un-threaded stage, memory pressure/swap, or the 3-thread cap rather than at the keying maths — which means the cheapest win is restructuring the graph and pre-keying the presenter once, before any hardware purchase. I found no published benchmark for any tool showing keyed 1080x1920 compositing fps, so "faster than realtime" claims below are engineering judgement, not measurements.

### Cited Findings
- [local] `ffmpeg -filters` on the team's ffmpeg 8.1 marks **hsvkey, chromakey, colorkey, despill, erosion, blend, overlay, maskedmerge, premultiply, geq, lut3d as `TS`** (timeline + slice threading). **`format`, `scale`, `crop` are `..`** (no slice threading); `alphamerge` is `T.`. — reference: [ffmpeg filters documentation](https://ffmpeg.org/ffmpeg-filters.html)
- [local] The same build has **no libplacebo, no Vulkan filters, no OpenCL filters, no `overlay_videotoolbox`, no CUDA**; the only GPU filters present are `scale_vt` and `transpose_vt`. Encoders present: libx264, h264_videotoolbox, hevc_videotoolbox, prores_videotoolbox, prores_ks, ffv1, qoi, libvpx-vp9, libsvtav1. — reference: [Homebrew ffmpeg configuration shown by `ffmpeg -version`](https://formulae.brew.sh/formula/ffmpeg)
- `-filter_threads` sets threads per simple filter pipeline and `-filter_complex_threads` sets them for `-filter_complex` graphs; default is the number of CPUs. Only filters flagged `AVFILTER_FLAG_SLICE_THREADS` use them. [snippet] — [ffmpeg-devel patch: parameters for filter thread counts](https://lists.ffmpeg.org/pipermail/ffmpeg-devel/2016-October/201974.html)
- An `overlay_videotoolbox` filter (Metal/CoreImage/VideoToolbox, auto hardware format conversion between differing inputs) was submitted to ffmpeg-devel in Feb-Mar 2024. [snippet] — [ffmpeg-devel PATCH v4](https://ffmpeg.org/pipermail/ffmpeg-devel/2024-March/322822.html). It is absent from the local 8.1 Homebrew build [local].
- libplacebo filter: GPU processing via Vulkan (including MoltenVK on macOS), OpenGL or D3D11; in ffmpeg it "currently only accepts Vulkan input frames"; supports multiple inputs and custom shaders; always works internally in 4:4:4. Documented for scaling, colour, tone-mapping, debanding — not keying. [snippet] — [ffmpeg 8.0 libplacebo filter docs](https://ayosec.github.io/ffmpeg-filters-docs/8.0/Filters/Video/libplacebo.html), [libplacebo](https://github.com/haasn/libplacebo)
- Jellyfin's macOS notes: hardware-accelerated complex filter chains on macOS are limited to OpenCL- and Vulkan-based filters. [snippet] — [Jellyfin Apple HWA docs](https://jellyfin.org/docs/general/post-install/transcoding/hardware-acceleration/apple)
- x264 presets: from medium, slow costs +40% time, slower +100%, veryslow +280%; medium and veryslow both reach VMAF 95, veryslow at a lower bitrate; veryfast is measurably worse than medium/fast. [snippet] — [Streaming Learning Center](https://streaminglearningcenter.com/?p=21298)
- Remotion render guidance (applies equally to any Chromium-screenshot renderer): JPEG frames encode faster than PNG, PNG only needed for transparency; the GPU is disabled by default in headless mode, which significantly slows WebGL / canvas / `box-shadow` / `text-shadow` / gradient / filter effects; VP8/VP9 encode is "very slow"; default concurrency is half the threads and should be tuned with `npx remotion benchmark`. [fetched] — [Remotion performance docs](https://www.remotion.dev/docs/performance), [Remotion GPU docs](https://www.remotion.dev/docs/gpu)
- Smelter (Software Mansion, formerly LiveCompositor) is a real-time compositor aimed at live mixing; where Daily VCS and LiveKit Egress run React in headless Chromium, Smelter compiles React to a native scene graph rendered on the GPU. [snippet] — [Software Mansion blog](https://hackathon.swmansion.com/blog/the-missing-layer-in-live-video-streaming-ap-is-programmable-video-composition/)

### Inferences
(Items marked BK are from my background knowledge of ffmpeg and were not re-verified against a source in this session.)

Ranked by expected payoff per unit of effort:
1. **Find the real bottleneck first.** Because every keying filter is slice-threaded, an idle CPU means the graph is waiting on something serial. Prime suspects: implicit `format=rgba`/`gbrap` conversions inserted between YUV-native filters (hsvkey works on YUV; `blend` and `overlay` each have format preferences) — swscale conversions are not slice-threaded in this build; the `-threads 3` cap also limiting filter threads; and swap. Run the graph with `-loglevel verbose` to see auto-inserted `scale` filters, and with `-benchmark -f null -` to separate filter cost from x264 cost.
2. **Pre-key the presenter once per take** into an alpha intermediate and reuse it for every re-render. The presenter clip changes far less often than overlays do, so today's pipeline re-pays the key (the expensive part) on every re-render. Candidate intermediates (BK): ProRes 4444 via `prores_ks` or `prores_videotoolbox` (fast decode, large files, ~1+ GB/min at this size — estimate); HEVC-with-alpha via `hevc_videotoolbox -alpha_quality` (small, hardware decode, Apple-only); FFV1/QOI (lossless, CPU-heavy, huge); VP9 alpha (slow to encode — consistent with Remotion's VP8/VP9 warning above). ProRes 4444 is the safe default; on a 256 GB disk it needs external scratch.
3. **Keep the graph in one pixel-format family end to end** (yuva420p/yuva444p throughout, single explicit conversion at the encoder) to avoid RGBA round trips.
4. **Segment-parallel encode + concat**: split each part into N time slices, run N ffmpeg processes, concat with stream copy. Turns a serial graph into N-way parallel regardless of filter threading. Costs N x memory, so it only works after the RAM upgrade.
5. **Encoder choice matters least.** The filter graph, not x264, is the bottleneck. With the graph fixed, x264 `medium`/`fast` at 1080x1920p30 is comfortably faster than realtime on any current 10+ core chip (judgement, not measured). VideoToolbox is ~5-10x faster still but ~10-20% larger at equal quality and reported weaker on flat animated graphics, which is exactly this content; platforms re-encode uploads anyway, so use it for previews and keep x264 for finals.
6. **GPU filter path** only on Linux/NVIDIA (section 2). On macOS there is no stock GPU keyer in ffmpeg: `overlay_videotoolbox` is not in the shipping Homebrew build, OpenCL and libplacebo are not compiled in, and libplacebo has no keying filter without a custom shader.

Alternatives to ffmpeg — realism for a keyed 1080x1920 30 fps composite (all judgement, none benchmarked here):
- **Likely faster than realtime, moderate effort:** a small custom compositor — PyAV (hardware decode) -> GPU tensor (MLX/Metal on Mac, CuPy/torch on NVIDIA) for key + despill + over -> pipe NV12 to VideoToolbox/NVENC. A 2-megapixel key is trivial GPU work; decode/encode become the limit. Cost: owning custom code.
- **Likely faster than realtime, GPU-native:** Smelter/wgpu-based compositors and WebGL/WebGPU + WebCodecs in headless Chrome (the key becomes a fragment shader). Smelter is live-oriented; offline deterministic rendering and custom key shaders need verification. Headless Chrome needs the GPU explicitly enabled (see Remotion finding).
- **Capable but heavy / wrong shape:** DaVinci Resolve scripting / Fusion headless (excellent keyer, GPU, but headless automation requires Studio licences and is fragile for low-technical operators); Blender VSE/compositor headless (works, slow start-up, keying node graph must be authored); Nuke (cost prohibitive); Natron (largely unmaintained, CPU).
- **Unlikely to beat a fixed ffmpeg graph:** MLT/melt and GStreamer (CPU keyers by default; GStreamer GL elements can be fast but pipelines are hard to author); VapourSynth (great threading, but frame-server plumbing for alpha overlay is awkward); Remotion/HyperFrames (they render the HTML layer; the keyed video overlay still goes through Chromium video decode, which Remotion's own docs call a bottleneck).

### Gaps
- No published fps benchmark was found for hsvkey/chromakey/overlay on Apple Silicon, for `chromakey_cuda`, or for any of the alternative compositors at this resolution. Every speed claim in Inferences needs a 10-minute local benchmark before money is spent on the basis of it.
- Whether `overlay_videotoolbox` was ever merged upstream (and into which release) was not confirmed; it is only confirmed absent locally.
- HEVC-with-alpha and `prores_videotoolbox` 4444 behaviour through ffmpeg 8.1 (decode of alpha via VideoToolbox, premultiplication handling) was not verified against documentation in this session.
- Smelter's offline (non-realtime) render mode, shader-based keying support and licence terms were not checked.
- x264-vs-VideoToolbox-vs-NVENC quality specifically at social-media bitrates for flat-colour educational graphics: no source found.

---

## 4. Manim performance (renderer status, caching, parallelism, GPU)

### Takeaway
Manim Community is at v0.21.0 with Cairo still the default production renderer; the OpenGL renderer is still not the supported path and a WebGPU renderer PR was closed unmerged in Sept 2026, so there is no GPU shortcut — Manim throughput comes from caching, one-process-per-scene parallelism and more cores/RAM.

### Cited Findings
- v0.20.0 was released 20 Feb 2026; the stable docs now show v0.21.0 as current. v0.20.0 highlights: MathTex rewrite, `Mobject.always` updater builder, `--seed` option; breaking changes to ImageMobject resampling and some colours. No Cairo/OpenGL performance, caching or encoding changes listed. [fetched] — [Manim v0.20.0 changelog](https://docs.manim.community/en/stable/changelog/0.20.0-changelog.html)
- A WebGPU renderer PR (`--renderer webgpu`, built on wgpu-py, 35 commits, Slug/SDF-based stroke and fill) was **closed as stale on 12 Sept 2026**; maintainers said the render flow needs a unified `RendererProtocol` refactor first (parallel PRs #4916, #4966, #5008) and a third renderer would complicate that. [fetched] — [ManimCommunity/manim PR #4968](https://github.com/ManimCommunity/manim/pull/4968)
- A long-running "rewrite the rendering system" effort exists as PR #3112. [snippet] — [ManimCommunity/manim PR #3112](https://github.com/ManimCommunity/manim/pull/3112)
- OpenGL renderer gained caching/skipping support back in v0.5.0 and is still described in docs as under development. [snippet] — [Manim v0.5.0 changelog](https://docs.manim.community/en/stable/changelog/0.5.0-changelog.html)

### Inferences
(BK = background knowledge, not re-verified this session.)
- BK: Cairo rendering is single-threaded per scene and CPU-bound; each `self.play()` is hashed and written as a partial movie file, so an unchanged animation is skipped on re-render unless `--disable_caching` is set or the hash is invalidated (anything non-deterministic in the scene, e.g. unseeded randomness — the new `--seed` option helps). Compiled LaTeX is cached as SVG in `media/Tex`, so TeX cost is paid once per distinct string as long as the media directory persists.
- Therefore: **persist `media/` between runs** (do not wipe it in build scripts or throw it away with ephemeral containers), render **each part as its own process** and run as many processes as there are performance cores and RAM allows. With 1-4 parts per video this gives near-linear speedup on a 12-18 core machine.
- Docker on Linux is the natural home for Manim on a shared render box (reproducible TinyTeX + fonts). On Apple Silicon, Docker runs in a Linux VM with its own memory reservation — a poor idea on 8-16 GB machines and one reason to run Manim natively on Macs or move it to the Linux box.
- `--transparent` forces an alpha-capable output (BK: ProRes 4444 .mov or WebM), which is slower to write and much larger; given the PYQ track's rule that Manim carries the full background, there is no reason to pay for it.
- Do not plan around the OpenGL renderer: output differs from Cairo for some mobjects and it needs a GL context on headless servers.

### Gaps
- No measured "typical realtime factor" for Manim CE Cairo at 1080x1920p30 was found; it varies enormously with scene complexity. Needs a local timing over a sample of real scenes.
- v0.21.0 changelog contents and supported Python versions were not fetched.
- The search for Manim-specific caching/parallelism documentation returned nothing relevant; the caching statements above are from background knowledge.

---

## 5. Cloud / serverless render options and cost per rendered video-minute

### Takeaway
Raw compute for this workload is cheap everywhere (a few US cents per finished video-minute once the composite is fixed); the real costs are engineering time and data movement, and two traditional bargains have weakened in 2026 — Hetzner raised prices sharply and Cloud Run GPUs in Mumbai are invitation-only.

### Cited Findings
- **Remotion Lambda** (2048 MB, us-east-1, v4.0.381): 1-minute video $0.017 warm / $0.021 cold in ~16-19 s wall time; 10-minute HD video $0.103 warm / $0.108 cold in ~56-61 s; 10 s 4K $0.013. Rule of thumb ~$0.01 per video-minute. Excludes S3, bandwidth, CloudWatch and the Remotion company licence for teams above three people. [fetched] — [Remotion Lambda cost examples](https://remotion.dev/docs/lambda/cost-example), [Remotion Lambda docs](https://remotion.dev/docs/lambda)
- **AWS EC2 Mumbai (ap-south-1)**: c7i.xlarge $0.1785/h on-demand; c8g.xlarge (Graviton4, 4 vCPU) $0.1080/h on-demand, ~$0.054/h spot. [snippet] — [DoiT c7i.xlarge ap-south-1](https://www.doit.com/compute/spot/ap-south-1/c7i.xlarge), [DevZero c8g.xlarge](https://www.devzero.io/instances/aws/c8g.xlarge)
- **GCP Cloud Run GPU**: L4 supported; minimum 4 CPU / 16 GiB with a GPU; **asia-south1 (Mumbai) is available by invitation only** — contact the Google account team. [snippet] — [Cloud Run GPU docs](https://docs.cloud.google.com/run/docs/configuring/services/gpu)
- **Modal**: CPU $0.0000131 per physical core-second (1 core = 2 vCPU), memory $0.00000222 per GiB-second, per-second billing; pinning a region costs 1.5-1.75x; non-preemptible 3x; L4 from $0.799/GPU-hour. [snippet, third-party pricing trackers] — [Beam: Modal pricing explained](https://www.beam.cloud/blog/modal-pricing-explained), [computeprices.com Modal L4](https://computeprices.com/providers/modal/gpus/l4)
- **RunPod**: L4 from $0.39/GPU-hour; RTX 3090 spot from $0.22/h; per-second billing. [snippet] — [computeprices.com RunPod L4](https://computeprices.com/providers/runpod/gpus/l4), [Deploybase](https://deploybase.ai/articles/runpod-gpu-pricing)
- **Hetzner**: price rises on 1 Apr 2026 (auction servers ~+3%, cloud +30-43%) and again for new orders from 15 Jun 2026; reporting of US virtual servers up 107-204% and some dedicated/cloud plans "nearly tripled"; AX102 quoted at EUR 452.30/month after June. Cause: hardware procurement costs (DRAM +171% YoY per one tracker). [fetched for The Stack; others snippet] — [The Stack](https://www.thestack.technology/hosting-firm-hetzner-hikes-prices-sharply-amid-supply-chain-pain/), [Data Center Dynamics](https://www.datacenterdynamics.com/en/news/german-cloud-firm-hetzner-hikes-prices-by-up-to-50-percent-due-to-drastic-component-price-increases), [agentdeals.dev summary](https://agentdeals.dev/hetzner-pricing-2026)
- **Hosted Macs**: AWS mac2-m2pro.metal $1.56/h with a 24-hour minimum dedicated-host charge (~$37.44 minimum); MacStadium M4 mini from $149/month, M4 Pro 48 GB/1 TB $349/month; Scaleway Mac mini M4 EUR 0.22/h, M4 Pro EUR 0.49/h (EUR 335/month), M2 EUR 0.17/h, 24-hour minimum. [snippet] — [Vantage mac2-m2pro.metal](https://instances.vantage.sh/aws/ec2/mac2-m2pro.metal), [MacStadium pricing](https://macstadium.com/pricing?p=mini2018), [Scaleway Apple silicon pricing](https://scaleway.com/en/pricing/apple-silicon)
- **Object storage**: Cloudflare R2 $0.015/GB-month, zero egress; AWS S3 Standard $0.023/GB-month with $0.09/GB egress for the first 10 TB (US-region figure; ap-south-1 differs); Backblaze B2 $6.95/TB-month with free egress up to 3x stored volume then $0.01/GB. [snippet] — [mecanik.dev R2 pricing explained](https://mecanik.dev/en/posts/cloudflare-r2-pricing-explained-real-costs-vs-s3-and-backblaze/), [infratally comparison](https://infratally.com/articles/cloudflare-r2-vs-aws-s3-vs-backblaze-b2-2026/)

### Inferences
- Cost per finished video-minute, CPU cloud (ESTIMATE): if the fixed pipeline runs at ~3x realtime on an 8-vCPU Graviton instance (c8g.2xlarge, assumed 2x the xlarge price = ~$0.216/h on-demand), one video-minute costs ~3 min x $0.216/60 = **~$0.011 (~Rs 1) on-demand, about half that on spot**. At today's 17-31x realtime the same minute would cost $0.06-0.11 — still cheap in money, hopeless in wall-clock unless fanned out.
- Remotion Lambda's ~$0.01/min is the right order of magnitude for the HTML-frame stage only; it does not run Manim, Whisper or the presenter key, and a 5+ person team needs the paid company licence.
- A 24-hour minimum makes AWS Mac hosts pointless for bursty rendering; MacStadium/Scaleway monthly Macs ($149-349) cost in 6-12 months what buying a Mac mini outright does. Hosted Macs only make sense to avoid capex or customs, not to save money.
- Hetzner is in Europe (roughly 120-180 ms from India — not sourced) and no longer the obvious cheap default; for an upload-heavy workflow Mumbai-region compute or a local box is better. Uploading a 1920x1080 presenter clip from an Indian office connection will usually dominate cloud turnaround more than render time.
- Storage volume (ESTIMATE, assumptions mine): 150-300 finished videos/day at ~60 MB each plus ~200 MB of presenter source per video is ~40-80 GB/day, ~1-2.5 TB/month. On R2 that is ~$15-37/month for the first month's data, growing linearly unless sources are expired; S3 egress at $0.09/GB would add ~$90-225/month if everything is pulled back once. Prefer R2 or B2, and set a lifecycle rule on intermediates.
- Serverless (Modal, Cloud Run jobs, Fly Machines) fits the bursty per-part job shape well but needs a container with Manim + TinyTeX + Chromium + ffmpeg + fonts (several GB; cold starts matter) and someone to own it.

### Gaps
- Not researched or no data found: AWS Batch/Fargate rates, g6 pricing in Mumbai, Cloud Run CPU/GPU per-second rates, Fly Machines, Cloudflare Containers, GitHub Actions larger-runner pricing, Remotion Cloud Run cost examples, current Hetzner auction-server monthly prices.
- Modal/RunPod figures are from third-party trackers, not the vendors' own pricing pages.
- Latency/throughput from Indian ISPs to Hetzner or to ap-south-1 was not measured or sourced.
- S3 pricing specific to ap-south-1 (storage and egress) was not confirmed.

---

## 6. Shared storage and asset management for a small team

### Takeaway
I found a current India price for a small Synology NAS but no sourced comparative evidence on NAS vs bucket, Git LFS/DVC/lakeFS or content-addressed render caches; the recommendations here are engineering judgement and should be labelled as such in the report.

### Cited Findings
- Synology DS925+ (4-bay, AMD Ryzen V1500B, 4 GB ECC expandable to 32 GB, **2x 2.5 GbE — not 10 GbE**): diskless Rs 73,500-74,999 in India; 16 TB bundle (4x 4 TB WD Red Plus) Rs 1,83,711. [snippet] — [pricehistory.app DS925+](https://pricehistory.app/p/synology-ds925-2x-2-5gbe-ports-ryzen-yRflCLIm), [Vishal Peripherals](https://vishalperipherals.com/collections/synology), [NAS Compares](https://nascompares.com/?p=79824)
- New Mac minis ship with 2.5 Gb Ethernet as standard (10 Gb optional), matching the DS925+ ports without an upgrade. [fetched] — [Gizbot](https://www.gizbot.com/laptop/news/apple-mac-mini-m6-mac-studio-m5-ultra-india-price-specs-availability-128701.html)
- Object-storage prices as in section 5 (R2 $0.015/GB-month zero egress; B2 $6.95/TB-month). [snippet] — [infratally comparison](https://infratally.com/articles/cloudflare-r2-vs-aws-s3-vs-backblaze-b2-2026/)

### Inferences
- Simplest robust shape for 3-10 low-technical operators in one office: **render locally on fast NVMe scratch, publish finished outputs and source takes to one shared place**. Never render directly onto a network share (many small partial-movie files, latency, and file-locking problems).
- NAS (Rs ~1.8 lakh with disks) suits a single office with slow uplink: LAN-speed transfer of presenter clips, no monthly fee, but it needs backup and a 2.5 GbE switch. A bucket (R2/B2) suits a distributed team or cloud rendering and costs ~Rs 1,500-3,500/month at the volumes estimated above. A hybrid — NAS as working store, nightly sync of finals to a bucket — covers both and gives off-site backup.
- Git LFS is a poor fit for multi-GB presenter takes (bandwidth quotas, slow clones); DVC or plain content-hashed bucket paths are closer to the need; lakeFS is overkill at this scale. (Judgement, not sourced.)
- **Content-addressed render cache** is the highest-leverage storage idea: key each stage's output on a hash of (stage code version + inputs + parameters) — e.g. keyed-presenter intermediate keyed on (source clip hash + key parameters); Manim part on (scene source + beats file + fonts + Manim version). Unchanged parts then never re-render on any machine, which directly attacks the "plus re-renders" multiplier in the capacity estimate. The repo's own note that model-written prompts break caches is the same failure mode to watch for: anything non-deterministic in a key defeats it.

### Gaps
- No sources gathered on Git LFS vs DVC vs lakeFS for media, on NAS-vs-cloud total cost for small video teams, or on shared-cache designs; no 10 GbE NAS price for India.
- Hard-drive availability in India in late 2026 is uncertain — one tracker says hard drives are "sold out for the year" at hyperscaler level ([agentdeals.dev](https://agentdeals.dev/hetzner-pricing-2026)); bundle prices above may not be obtainable.

---

## 7. Reliability practices

### Takeaway
No external sources were gathered for this question within the tool budget; what follows is judgement grounded in the failures described in the brief (swap crash at two heavy jobs, silent failure on a full disk) and should be presented as recommendation, not finding.

### Cited Findings
- The failure modes to design against are documented in the workload brief and are consistent with the local machine: 8 GB RAM, 8 CPUs [local], ffmpeg 8.1. — reference: [ffmpeg documentation](https://ffmpeg.org/ffmpeg.html)
- Remotion's guidance that concurrency that is too high is counterproductive, and that it should be found by benchmark rather than assumed, is the one sourced datum on concurrency tuning. [fetched] — [Remotion performance docs](https://www.remotion.dev/docs/performance)

### Inferences
- One queue per machine with **weighted slots** rather than a job count: declare each stage's peak RAM (measure it once with `/usr/bin/time -l` on macOS or cgroup `memory.peak` on Linux) and admit jobs only while the sum fits in ~75% of RAM. On 8 GB that degenerates to "one heavy job"; on 24-64 GB it safely admits several.
- On a Linux render box, enforce the limit rather than trusting it: run each job in a container or systemd scope with a hard memory limit so a runaway job is killed instead of swapping the host. macOS has no equivalent hard per-process cap, another argument for putting the shared worker on Linux or simply over-provisioning RAM on Macs.
- **Disk guard as a pre-flight gate that fails loudly**: refuse to start a job when free space is below (estimated output + intermediates) x 2, and treat any ffmpeg non-zero exit or an output shorter than expected (ffprobe duration check) as failure. Add automatic cleanup of intermediates older than N days. ProRes 4444 intermediates make this mandatory.
- A lightweight local queue (SQLite-backed or a simple Redis queue) is enough for one box; for several workers a pull model — workers claim jobs from a shared table/bucket — tolerates machines going offline.
- Observability for low-technical operators means one status page: queue depth, per-job stage and elapsed time, last error in plain language, free disk and free RAM per machine. Record per-stage wall time and peak RAM for every job; that dataset is what turns the capacity estimate below from a guess into a measurement.

### Gaps
- No practitioner sources (HN/Reddit/post-mortems) or tool comparisons (Celery/RQ/Temporal/Nomad/Slurm, etc.) were collected. This whole section is unsourced judgement.

---

## 8. Worked capacity estimate (5 operators x 10 videos/day)

### Takeaway
At today's measured 17-31x realtime for compositing, 5 operators need on the order of 100+ machine-hours of compositing per day, which no hardware purchase alone fixes; if the composite is brought to roughly realtime and the whole pipeline to about 3x realtime, the same demand is ~15-20 machine-hours per day, which two or three 24 GB Mac minis, or one shared render box running long hours, can deliver. Every number in this section is an estimate derived from the brief's figures and the prices above.

### Cited Findings
- Inputs from prices above: Mac mini M6 24 GB/512 GB Rs 1,47,900 [snippet] — [Technosports](https://technosports.co.in/mac-mini-m6-india-price-all-variants/); Mac mini M5 Pro 24 GB/512 GB Rs 2,09,900 [fetched] — [ETV Bharat](https://www.etvbharat.com/amp/en/technology/2026-apple-mac-studio-2026-mac-mini-m6-chip-m5-ultra-chip-enn26082601315); c8g.xlarge Mumbai $0.108/h on-demand, ~$0.054/h spot [snippet] — [DevZero](https://www.devzero.io/instances/aws/c8g.xlarge); R2 $0.015/GB-month [snippet] — [infratally](https://infratally.com/articles/cloudflare-r2-vs-aws-s3-vs-backblaze-b2-2026/); Remotion Lambda ~$0.01-0.02 per video-minute [fetched] — [Remotion cost examples](https://remotion.dev/docs/lambda/cost-example)

### Inferences

**Demand (derived from the brief)**
- Finished output: 5 operators x 10 videos x 2 min = **100 finished video-minutes/day**.
- Part renders: 20-40 parts per operator per day -> 100-200 part renders/day; at 60-120 s each, call it ~90 s average -> **150-300 part-minutes/day**. With a re-render factor of 1.5x (assumption): **~225-450 rendered minutes/day**; planning figure **~340**.
- For 10 operators double everything; for 3 operators multiply by 0.6.

**Supply at different speeds (planning figure 340 rendered minutes/day)**
| Pipeline speed (wall-clock per output minute, all stages) | Machine-hours/day needed | What it means |
|---|---|---|
| ~25x (today's composite alone: 26-47 min per 90 s = 17-31x) | ~140 h | impossible locally; ~18 machines for an 8 h day |
| 6x | ~34 h | 4-5 machines over 8 h, or 2 running ~17 h |
| 3x (target after software fixes) | ~17 h | 2-3 machines over 8 h, or 1 box running 17 h |
| 1.5x (pre-keyed presenter + cache hits + parallel parts) | ~8.5 h | 1 dedicated box in a working day |

The software fix is worth a factor of ~8; no hardware option on the list is.

**Configurations (capex in INR; USD at the assumed Rs 90)**
- **A. Local-only, every operator self-sufficient.** 5x Mac mini M6 24 GB/512 GB = Rs 7.4 lakh (~USD 8,200) + 5x 2 TB external NVMe with enclosure ~Rs 1.0 lakh (estimate) + monitors/peripherals not counted. Each machine needs ~3.4 h/day of rendering at 3x — fits easily and renders in the background while the operator works. Opex ~nil. Simplest for low-technical operators; no shared infrastructure to break. At 10 operators: ~Rs 17 lakh.
- **B. Hybrid: light seats + one shared render node (cheapest that meets the target).** Operators author on modest machines (existing M2 8 GB machines can author and preview but should not render; new seats could be MacBook Air M5 16 GB at ~Rs 1.0-1.2 lakh); one render node — Mac mini M5 Pro 24-48 GB (Rs 2.1 lakh+) or a 9950X Linux box (~Rs 2.2-3.5 lakh depending on GPU, estimate) — runs the queue. At 3x it needs ~17 h/day for 5 operators: workable overnight but with queueing delay during the day, so **two nodes (~Rs 4.2 lakh, ~USD 4,700)** is the comfortable configuration, plus a DS925+ NAS (~Rs 1.8 lakh with disks) if a shared store is wanted. Total ~Rs 4-6 lakh if existing laptops are kept. Requires a queue, a status page and someone technical to own them.
- **C. Cloud-only compute.** At 3x on 8-vCPU Graviton (~$0.216/h on-demand, assumed 2x the xlarge rate): 17 h/day x $0.216 = ~$3.7/day = **~$80-110/month (~Rs 7,000-10,000)** on-demand, roughly half on spot; plus storage ~$15-40/month on R2. Compute is trivially cheap. The costs are elsewhere: uploading every 1080p presenter take over an office uplink, container engineering for Manim + TinyTeX + Chromium + fonts, and operators still need capable seats (the 8 GB Macs remain a problem for authoring and preview). Zero capex, highest engineering dependence.

**Reading across the three:** compute is cheap in all of them; the scarce resources are RAM per seat, engineering attention and upload bandwidth. For a low-technical team, A is the lowest-risk, B the lowest-cost if existing machines stay, C the most elastic. A staged path — fix the composite in software first, measure the real per-stage realtime factors on one new 24 GB machine, then choose A or B — avoids buying hardware to compensate for a graph problem.

### Gaps
- The 3x and 1.5x pipeline speeds are targets, not measurements. Per-stage timings (Manim, HTML frames, Whisper, composite, encode, QC upload) on a 24 GB+ machine do not exist yet; the capacity table should be re-run once they do.
- The re-render multiplier (1.5x) and the 90 s average part length are assumptions.
- Claude-vision QC time and API cost per video are outside this note's scope and not included in opex.
- Electricity, UPS, office uplink speed, customs/GST specifics and warranty/AppleCare costs in India were not researched.
- Exchange rate is an assumed Rs 90/USD; no sourced rate for October 2026.
