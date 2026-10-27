# The reel standard

What a finished PYQ reel looks like and how it is delivered. It is taken from the four latest
videos, which are the reference. Match them; when this page and a reference video disagree,
the video wins and this page is wrong.

Each rule says how it is held: **gate** (a check refuses the video), **default** (the code does it
unless told otherwise), or **review** (a person checks it on the frames sheet or the final watch).

## The reference videos

| Video | Subject | Length | Look | What it is the reference for |
|---|---|---|---|---|
| PHY — व्हीटस्टोन सेतु व मीटर सेतु | Physics | 2:54 | `labbook`, blurred lab plate | Realistic apparatus: the bridge drawn as a real lab object on a wood board, not a schematic |
| CHE — मोलरता | Chemistry | 2:02 | `chemlab`, lab wall with glass cylinders | The presenter grade (true to source, softened); realistic glassware; the answer page at the "screenshot" cue |
| HIS-C11-SA-01 — जननेता गाँधी | History | 2:15 | `khadi`, 1930 photographs in sepia | Veo coverage (31 of 33 beats on generated footage); pacing (hook and question at 1.2×, the rest at 1.1×) |
| HIS-C6-SA-04 — भक्ति संतों के उपदेश | History | in progress | `pothi`, Varanasi at sunrise | Real period paintings as portraits; a gallery that returns at the recap |

Their plans are `plan_phy_wheatstone_p1.json`, `plan_che_molarity_p1.json`,
`plan_his_c11_sa_01_p1.json` and `plan_his_c6_sa_04_p1.json` in this folder, built by the
matching `make_*_plans.py`. A new video starts from the closest one.

## The file

| | Standard | Held by |
|---|---|---|
| Frame | 1080 × 1920, 30 fps, H.264, about 6–8 Mbit/s | default |
| Audio | AAC, 48 kHz stereo, 192 kbit/s | default |
| Loudness | −16 LUFS integrated, peaks at or below −1 dBFS | gate: `loudness_gate` (Wheatstone, delivered before it, peaks at +0.2 dBFS) |
| Sound | the voice and sound effects only, **no background music** | default |
| Length | set by the narration; the latest run 2:00–2:55 plus the answer page | — |

## The video, in order

1. **Hook on moving footage.** The first frame is a Veo clip, never a title over a talking head,
   with the board's seal over it: the MPBSE seal large, and a seal-blue pill under it reading
   "MP Board | कक्षा 12" (`{"type": "boardtag", "slot": "upper", "at": [0, 0.05]}`; the team's chosen opener,
   27 Oct 2026, replacing the state outline). *gate: `hook_visual`. A plan may set `"hook": "exempt"`
   only while its Veo clips are still being generated; it must be off for the render.*
2. **The years on real exam sheets**, one sheet per year, each year landing as it is spoken.
3. **The question on the torn exam sheet**, each printed line highlighting as he reads it, with
   the marks sticker. *gate: preflight fails a card without `marks`*
4. **The teaching**, one point at a time:
   - a numbered headline for each point, and the spine counter at the top filling as points finish;
   - each point says *who/what* first, then the one thing to remember, set large;
   - screen text **organises** what is said (a heading, a list, a comparison); it does not repeat
     the caption. *review*
   - counted lists show digits (1, 2, 3) and fill in one by one; every item stays on screen. *review*
5. **Recap** that lights each point as he names it.
6. **"पूरे 3 नंबर पक्के"** (or the question's marks) as the one large line.
7. **The answer page at the narrator's cue** ("screenshot लो", "notes button में मिल जाएगा"), staying to
   the end. *review*
8. **The answer page appended** after the narration, held 7 seconds (`answer_outro.py --hold 7`). Every
   video ends on it, whatever the narration says. *default in the render script*

## The presenter

- Card style: a 452 × 560 card at the bottom centre (x 314, y 1130); some beats show him full-frame.
  He is **always centred horizontally** and **never stretched**: he is scaled from a height only.
  *gates: `avatar_shape_gate`, `face_gate`, `output_gate`*
- Framing: `{"crop": [600, 150, 1340, 1000], "full_w": 735}`, the size used in the Hindi reference reel.
- Full-frame, he runs solid to the bottom edge of the frame: **no fade at the bottom** (user, 26 Oct 2026).
  `scene_match` is `{"tint": 0.05, "wrap": 0.12, "wrap_px": 6}` with no `bottom_fade`.
- Grade: the Molarity grade (true to source, contrast eased, softened):
  `{"exposure": 1.0, "contrast": 0.94, "warm": 0.99, "saturation": 0.96, "shadow_lift": 0.4,
  "lift_radius": 14, "define": 0.04, "matte_soft": 1.0, "matte_choke": 0.05, "soften": {"amount": 0.55, "radius": 1.8}}`
- Nothing that teaches sits under him. *gate: stills layout check ("reaches the presenter")*

## Captions

- At the bottom, keyword highlighted.
- **None under the question card**: they start once the card has gone. *gate: `caption_after_question`*
- Synced to the words actually spoken, never to the HeyGen SRT times (those are out by up to 2.2 s).
  Use the Whisper word clock, or `tools/pause_align.py` when Whisper is unavailable. *review*
- No em-dashes on screen. *gate: `no_em_dash`*

## The look

- **One theme pack per video**: plate, fonts, card style, card backdrop and photo treatment all
  from one world that matches the topic (Gandhi: khadi and 1930 sepia; Bhakti: manuscript pages
  and Varanasi). **No two videos share a skin.** *review*
- **Veo behind nearly every beat**, dimmed behind cards and slow. The plate shows only where no clip
  fits. *review*
- The plate is a real photograph of the topic's world, **lightly** blurred (about 6 px) and darkened
  so white cards read. *review*
- Real photographs and period paintings where they teach, from Wikimedia Commons with a
  commercial-use licence, each recorded in the folder's `credits.json`. Never a picture lifted
  off a search page. *review*
- Science: apparatus drawn as **real lab objects**, never flat schematics; mechanisms animated in
  the right direction; every formula symbol named under it. *review*
- Labels stay once shown. *review*
- Transitions follow what the cut means. No dissolve across the presenter, since it ghosts him; no zoom-in
  transition. *review*
- Sound effects come from beats (an element landing, a stamp, a page), never from captions, and peak on the
  visual they mark. *default in compose*
- Ion charges and formulae are typeset (KaTeX), so a sign sits level with its digit. Political science
  always carries Indian iconography, whatever country the question is about. *review*

## Correctness first: exact diagrams, not generated ones

Anything a student must reproduce in the exam is drawn **exactly**, never generated:
- circuits, apparatus, reaction setups, mechanisms and cycles, labelled biological structures, graphs, maps;
- as SVG/HTML elements in `stage.html`, or as a Manim render in `projects/<slug>/diagrams/<id>.mp4`;
- the mechanism's direction and order right, every label named as it is spoken, textbook colour conventions.

Veo is for atmosphere only. A generated clip that shows what the answer says is wrong is worse than no
clip. *review*

## Veo clips

- Vertical 9:16, 8-second clips, one per beat that needs one. Prompts are written by the pipeline,
  never by hand: live-action, the subject in the upper half, and the full NEGATIVE list.
- A prompt never contains digits, percentages, or the words logo, watermark, badge or wordmark:
  whatever a prompt names gets drawn.
- Flow burns a small sparkle into every clip; it is removed (`delogo`) before the clip is used.
  *gate: `veo_logo_gate` (does not see kit clips yet, so this is review for now)*
- A clip is never reversed to fill time; it is slowed, looped or held.
- Generated footage never depicts revered figures who must not be portrayed (the Sikh Gurus);
  show objects and places instead and keep their faces to period paintings.

## The answer page

- The **in-house sheet**: ruled paper, handwriting, the Arivihan watermark. *gate: `answer_page_gate`*
- Usually in column AK ("Final Answer Photo Link"), but not always. `tools/sheet_fetch.py` searches the whole
  row of the question's sheet and checks each candidate with the gate's own tests. Column L ("Question
  Answer Image Link") is normally the textbook scan; it is tried last and rejected unless it really is the
  house page.
- **A missing page never holds up a reel.** It is rendered and delivered without the page, recorded as
  pending, and `tools/deliver.py --pending` appends it once it is in the sheet (any column) or someone
  sends it (`tools/sheet_fetch.py <ID> --page <file or link>`). The page goes on the end; showing it at the
  narrator's cue as well needs a re-render.

## Delivery

| | Standard |
|---|---|
| Gates | `tools/gates.py <slug> <video>` exits 0: no failures; every skip prints its reason |
| Reviews | the frames sheet approved before the render; the final watched once against the defect checklist |
| Science | `~/Desktop/Final <Subject>/<ID — हिंदी शीर्षक>/1.mp4` |
| Arts | `~/Desktop/Final Arts/Final <Subject>/<ID — हिंदी शीर्षक>/1.mp4` |
| Parts | `1.mp4`, `2.mp4` … in the same folder; nothing else in the folder |
| ID | the sheet's question ID; "(ID pending)" only when the question is not in the sheet yet |
| Kept | `projects/<slug>/final/<slug>_part<N>.mp4` and its `.geom.json` sidecar |
| Re-delivery | overwrite `1.mp4` in place; keep the previous file in `projects/<slug>/final/` until the new one is confirmed |
