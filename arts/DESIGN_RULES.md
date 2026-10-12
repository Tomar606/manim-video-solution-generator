# Design rules from review

Rules for drawing what goes on screen in an arts reel. Each one came from a user
review of a delivered video and names what it replaced. Read this before you draw
a storyboard, a mock-up or a scene. A rule only leaves this page when the user
reverses it.

Linked from `PROCESS.md` and `PROCESS_ARTS.md`. The look of each video still
changes every time (`arts/LOOKS.md`); these rules apply whatever the look.

**The bar.** On 2026-10-08 the user called GEO-C2-LA-01 ("पृथ्वी, रात में") and
POL-C3-LA-02 ("दो स्याही") "absolutely perfect… in all departments": the theme,
the presenter's positions and movement, the elements, the sound effects and the
way information was shown. Then: "keep making similar things. Not same. We can
repeat too, but we need variations." Sections 8–14 write down what those two
videos did, so every new one starts from it. Section 15 says what must change
from video to video and what may repeat.

---

## 1. Every element is something to remember

**Rule.** Each scene puts one structure on screen that a student could redraw in
the exam: a skeleton, a mapping, a diagram, a map, tiles, a list of pointers.
Words stacked one under another are not a structure.

**Why.** "Don't just show random texts. Show texts in a way the student remembers
them." (POL-C3-LA-05, 2026-10-09.) GEO-C2-LA-01 and POL-C3-LA-02 were praised for
doing this.

**Patterns that worked:**
- **The answer skeleton:** a box for परिचय, numbered slots for the points, a box
  for निष्कर्ष. It appears when the answer's shape is first announced, comes back
  at the start of a later part with the finished slots filled, and closes the
  video ticked.
- **Abbreviations decoded:** letter boxes along the top (S·A·A·R·C). Each box
  lights when its row arrives, and the row pairs the Hindi word with the English
  word, initial in yellow (दक्षिण एशियाई ↔ **S**outh **A**sian). The full English
  name goes underneath. Use this for any abbreviation he says, even if he only
  says it in Hindi: the letters are where the name comes from.
- **A metaphor drawn literally:** "एक मंच … की नींव" became a platform resting on
  three blocks (सहयोग, शांति, सामूहिक विकास) with a brace marked नींव.
- **A cause shown as an obstacle:** a striped tax barrier between two countries
  that drops so the goods cross. The user called this perfect.
- **Pointers:** a list of causes or features as separate rows, each with a bullet
  and its own background. Never as touching highlight blocks.
- **A recap list** that builds one row per point, with each point's picture back
  behind it.

## 2. Spacing: every element gets room

**Rule.**
- One left margin (64 px) for the whole video.
- At least **40 px between separate elements**: a heading and what follows it, two
  blocks, a stamp and a tag.
- At least **20 px between rows inside one element** (list rows, acronym rows).
- **24 px or more of padding inside any box** that holds text.
- Content under the top eyebrow starts at **y ≥ 190**. Content with no eyebrow
  starts at **y ≥ 120**. The progress bar sits at y 38 and the eyebrow at y 92.
- Nothing rests on the presenter's head: in an explaining scene, everything ends
  by y 1170 when he is centred at the bottom.

**Why.** "We have space, yet the SAFTA words are touching the heading. Give each
element a breathing space." The end card (skeleton, stamp and Notes tag) had the
same fault.

**Check.** In the stills check, look at every place where two elements meet. If
they touch or nearly touch, move one; never shrink the gap to fit more in.

## 3. Maps of countries

**Rule.**
- Show clear country boundaries, and **light each country's border as he names
  it** (yellow fill and stroke with a short glow). It then stays lit, and all of
  them light together when he gives the total.
- India's border comes **only** from an India-viewpoint dataset: Natural Earth
  `ne_10m_admin_0_countries_ind`. Before using it, check that these all fall
  inside India: Gilgit, Muzaffarabad, Aksai Chin, Leh, Siachen, the Shaksgam
  valley, Tawang and Itanagar. Record the source in the video's `sources.json`
  (PROCESS_ARTS rule 5).
- Tiny countries (the Maldives) get a ring at their real position, so the
  highlight can be seen.

**Rejected.** A map broken into its countries that drift apart and fit back
together ("remove this animation"). For "separate, then together", use eight boxes
that open into a ring around one centre, joined to it by spokes.

## 4. The presenter

**Rule.** When he is explaining over text and drawings, stand him in the middle at
the bottom of the frame, with everything drawn above him. Large and centred when
he talks to the student; small and centred for the recap; hidden only when a map
or diagram needs the whole frame.

**Why.** "The avatar can be in the middle." Pushing him to one side cost the left
column and looked off-balance (POL-C3-LA-05).

**Not a ban on other places.** A corner window, a circle or a split-screen seam is
right when the picture beside him is the point (GEO's window over footage, its
circle on the seam of a split screen). Section 9 is the rule for that: every
place he can be means something, and the layout gives the side he is not on to
something that needs it. What failed in LA-05 was a side position with nothing
earning the space it left.

## 5. Backgrounds

**Rule.**
- Prefer real footage behind everything: the clip sharp when the sentence is about
  it, and blurred and darkened behind drawn moments.
- Darken by **scaling** the light (`colorchannelmixer`, as `tools/reel/edit_from_scenes.py`
  does). Never subtract brightness (`eq=brightness=-x`): a blurred clip turns into
  black blobs.
- No procedural textures pretending to be a material (the drawn walnut "table"
  read as ripples and was rejected).

**Why.** "The background looks bad" (the round-table cut of POL-C3-LA-05). The
full-bleed footage look replaced it.

## 6. When the user wants a different look

**Rule.** Do not rebuild straight away. Render 3–4 distinct directions as stills
of the same three moments, using the real clips, presenter and data. Put them on
one page beside the current cut, and wait for the user to pick. Then rebuild. The
mock-up's blur, dim and colours must match what the render will produce.

**Why.** "Show me options for designs and then only move ahead. I will pick one."

## 7. The words on screen

- Screen text follows the voice: nothing appears before he says it, and labels use
  his words. A caption on a picture that he never says ("काम की तलाश") was cut.
- Any English shown is either his own words or the expansion of an abbreviation he
  uses (rule 1).
- Body text at least 40 px, headings at least 60 px (PROCESS_ARTS rule 15).

## 8. One spine that is the answer's shape

**Rule.** Every video has one recurring visual that IS the structure of the answer,
and keeps coming back to it: it opens the video, fills as each point is finished,
carries over between parts, and becomes the recap.

**Patterns that were praised:**
- **GEO:** a night globe the video returns to (the proof: lights follow rivers and
  avoid deserts) and a four-part ring round the presenter that lights one arc per
  factor across all three parts, then opens into a full-screen answer wheel.
- **POL-02:** one line, "लोकतंत्र की राह", over the years: low and red under the
  king, up in 1990, on the floor in 2002, up again from 2006. A strip at the top of
  nearly every scene with the current point glowing; full page for the roadmap, the
  fall and the recap, where it redraws one stretch per point with six rows under it.

**How to pick one.** Ask what shape the answer has. Factors → a ring, wheel or
pillars. A sequence of years → a line, a road, a ladder, a timeline. Causes and
effects → a chain or a flow. Comparison → two columns or a balance. Parts of an
institution → a tree or a building. The spine is the answer's shape drawn once;
everything else hangs off it.

**Across parts.** Part N ends with the spine in a state that asks a question
(the line on the floor at 2002 with a dotted "?" ahead; three of four arcs lit),
and a pointer to the next part ("Part 3 → चौथा कारक + example"); part N+1 opens
by replaying where it stands, the finished items ticked ("✓ भौगोलिक · ✓ आर्थिक"). A student who watches only one
part still sees where it sits in the whole answer.

## 9. The presenter has states, and each state means something

**Rule.** Choose 3–4 states per video and give each a meaning the student can
learn without being told. Write the meaning on the storyboard.

- **Talking to you** (large, centred): the hook, a point's heading, an exam line,
  "ध्यान से सुनना", the ending. The change of size itself says *this one matters*.
- **Explaining** (smaller, with the picture or diagram given the rest of the
  frame): most of the video.
- **Hidden**: only when a map, a date or the spine needs the whole page (the
  roadmap, "28 मई 2008", the globe's three pinned places).
- **Small** for a recap that fills the page.
- GEO also used a **window** (head, chest, hands, bottom-left over footage) and a
  **circle** (on the seam of a split screen, at the hub of the answer wheel).
- **Frame him so his hands show** in any window or box: he teaches with them.
  "He can be smaller inside the window just a bit so his hands show, like 10%"
  (GEO review).
- **Don't hold one state for long.** "Don't keep him in the portrait window the
  whole time" (GEO review): a part that keeps him in one state for minutes has
  stopped choosing.

**Movement.**
- He changes state **only on a cut**, with a **0.5 s glide centred on the cut**
  (smoothstep), never mid-shot, never a jump.
- Each state has fixed, measured free zones (`look.json` `place.*._covers`);
  text never enters them. His face is never covered.
- Treat him as part of the look: a paper cut-out with a white edge and a shadow
  on a printed poster (POL-02); a circle or window with a HUD frame on a satellite
  look (GEO). Never just pasted on top.

## 10. How information is shown

These were praised and may be reused, in a new skin each time:

- **Point headings** with a number, the year and the point's name, landing on
  his words (`3 · अप्रैल 2006 · जन-आंदोलन`), plus pips that fill one per point.
- **Definitions as a separate, smaller element** ("यानी" slips pinned beside
  the term), never in the same line as the term.
- **The line to write** in its own card and its own type (a serif in POL-02, an
  "exam line" card in GEO), so the student learns that this style goes on paper.
- **A date or number students get wrong gets a full-screen moment** with the
  presenter hidden, held long enough to read twice (28 मई 2008: 5.7 s).
- **Contrasts as a split screen** (crowd / desert; then / now) with him on the seam.
- **Flows as moving dots** (people pulled in by jobs, driven out by unrest), on a
  schematic shape, never on a real place.
- **Stamps for verdicts** (संसद भंग, then struck out and restamped संसद बहाल).
- **Counts as slots that fill** (1 of 3, 2 of 3, 3 of 3), not a sentence.
- **Real people as type-only name plates**, never a picture.
- **Every recap rebuilds the spine**, one point at a time, with each point's own
  picture back beside it, and the finished answer then **holds on one screen,
  all of it lit and readable, for at least 3 s** so a student can pause and copy
  it. Move the next cut if needed. (GEO's wheel was first built to close 0.35 s
  after it was complete; held to 3.6 s it cost nothing.)
- **The big word** for a question or a turn ("क्यों?", "4 नंबर पक्के"): the largest
  type in the video, alone, with a beat of sound. Kept apart from labels and from
  the line to write, so the three never look alike.
- **"पहले | आज" era tags** over two shots when he contrasts then and now.
- **A meter** that rises and falls with "अधिक" and "कम" (GEO's population meter).
- **A chain of cause as arrows**, one link per word: "जल → खेती → पेट भरता था",
  "अशांति → पलायन → घनत्व कम". Opposite verbs get the same device run both ways
  (dots pulled in for jobs, driven out by unrest).
- **A cliffhanger at the end of a part** (rule 8).

## 11. Colour carries meaning

**Rule.** At most two meaning colours beside the neutrals, each tied to one side
or one idea for the whole video, and the page may change with them.

- POL-02: crimson = राजा / राजशाही, blue = जनता / लोकतंत्र. Headings, stamps, the
  line and even the printed pictures took the ink of whoever held power, and the
  page tinted pink or pale blue with them.
- GEO: amber for people and lights, cyan for the interface, one red-orange used
  ONLY for unrest.
- A colour used decoratively elsewhere breaks the code: check every red and blue.

## 12. Motion and rhythm

- Every on-screen change lands on a word he says (`clock.at('...')`), never on a
  round number of seconds.
- Something changes at least every 4 s; check long scenes from the rendered
  layers, not by eye.
- One entrance family per video (stamp-press for a poster, scan-in for a HUD).
- Continuous motion of large areas is avoided: it costs render and file size and
  pulls the eye from the words. Motion is in the elements that teach.

## 13. Sound

**Rule.** A quiet palette that belongs to the look, under an untouched voice.

- One bed on **one clock through all parts** (part 2 picks up the exact sample
  part 1 ended on), about **28 dB under the voice**. No melody, no rhythm.
- Effects come **from the drawing code's cues** (`--cues`): every stamp, slide,
  tick and pencil stroke on screen has its sound, and nothing sounds that is not
  seen.
- **Nothing may sit on a word:** each effect at least 6 dB under the voice in
  1–4 kHz where it lands, or slid a few hundredths later, then turned down.
  The voice's loudness is checked unchanged in every delivered file.
- The palette is the look's own material: a synth pad, pings and ticks for the
  satellite; paper slides, stamp thuds and pencil for the poster; tanpura and wood
  for Magadha. A new look gets a new palette.

## 14. Pictures

- Veo shows manner, never fact (PROCESS_ARTS rules 1–3), and every clip is shown
  through the look's own treatment so it belongs to the video: a night grade for
  GEO, printed in one ink inside a paper frame for POL-02.
- A clip is the sentence's claim (a hand signing, doors closing on an empty hall,
  a paper into a box), not its setting.
- The first clip of a batch runs alone and is looked at before the rest.
- **A negative is never pinned on a real place he did not name.** War, unrest,
  poverty or people leaving go on a schematic shape or on footage that names no
  place (GEO's "driven out" dots sit on a made-up region). Only a place he names
  gets a pin, label or highlight, and only for what he says about it. Places the
  data shows but he does not name are left as the data shows them, neither
  labelled nor hidden (East Asia on GEO's night map).

## 15. Variation: what changes every video, and what may repeat

**Must change from the previous arts video:**
- the look (palette, type, material, captions skin),
- the form of the spine (not a line twice running if the answer allows another
  shape),
- how the presenter is set into the page,
- the transition family and the sound palette.

**May repeat, in the new skin:** any device in section 10, the presenter's state
grammar, the answer skeleton, the recap pattern, the question card. A device that
teaches well should come back; a look should not.

**Check before the storyboard:** read `arts/LOOKS.md`, and write on the board, in
one line per axis, how this video differs from the last two. If two videos of the
same subject run back to back, vary harder: the user will see them together.

**Bring one new idea each time**: a device, a map style or a presenter move the
earlier videos did not have, chosen because THIS answer needs it. Say on the board
what is reused (and from which video) and what is new.

**Don't buy novelty with a heavy build.** A new look is a new kit
(`design/kit.mjs`), not a new engine. GEO's globe cost 80 min of rendering; POL's
SVG line cost seconds. Take the heavy option only when the answer is about the
thing it shows.

**Proven devices to draw from** (video in brackets): answer skeleton (POL-02,
POL-05) · four-arc ring filling across parts, opening into a recap wheel (GEO) ·
line or road of years whose dots get their number when he says the year (POL-02)
· split screen with him on the seam (GEO) · पहले | आज tags (GEO) · meter (GEO) ·
dots pulled in / driven out (GEO) · named pins on a map or globe (GEO) · regions
glowing as named, then a flat map strip to recall all three (GEO) · borders lighting
as named (POL-05) · acronym letter boxes (POL-05) · a metaphor drawn literally,
platform on a foundation (POL-05) · an obstacle that drops (POL-05) · stamps,
struck and restamped (POL-02) · fill-in tiles (POL-02) · forked road (POL-02) ·
full-page date (POL-02) · counted figures, 22 of 100 lit (POL-05) · words struck
out together (POL-05) · a picture cracking along named causes (POL-05) · the
"छोड़ना मत" card with ✓ / ✗ rows (GEO) · the exam-sheet question card (all).
