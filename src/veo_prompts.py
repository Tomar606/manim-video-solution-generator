"""Write the Flow/Veo prompt for one PYQ beat, and rewrite it when it comes back wrong.

WHEN A BEAT GOES TO VEO AT ALL
------------------------------
Rarely, and never by default. PIPELINE.md's routing table stands: equation
chains, graphs, geometric construction and schematic apparatus all render
correctly in Manim by construction, and roughly half of every Veo NEGATIVE list
we have ever written exists only to suppress Veo's text failures. A beat earns a
Veo clip when the thing that has to move is *photoreal or organic* — rust
creeping across iron, a flame's colour changing, gas bubbling off an electrode,
tissue swelling under osmosis — and neither Manim nor a still image can show it
moving. Everything else stays where it is.

THE CONTRACT EVERY PROMPT HERE MUST HONOUR
------------------------------------------
Three of these come from the house skill, which already learned them the
expensive way (`.claude/skills/video-prompt/references/bug-ledger.md`); the
fourth is ours and is the strictest.

  §15 UPLOADED BACKGROUND. The subject plate from `assets/backgrounds/` is
       attached to the generation, so the prompt must never *describe* a
       background — describing one makes Veo build its own and discard ours, or
       blend the two and leave a seam. The animation sits ON the plate, and the
       plate is the same plate Manim renders, which is what lets a clip be
       dropped into the middle of a rendered part without a visible cut.

  §17 SILENT. The audio is the HeyGen presenter's. A clip that generates its own
       voiceover gives us two voices over each other AND makes Veo burn in its
       own captions.

  §18 BAND. Adapted: the reels track reserves the bottom half, this track
       reserves BOTH ends — the caption strip at the top and the presenter at
       the bottom. See LAYOUT.

  NOTHING BUT THE ANIMATION. Ours, and absolute. The clip contains the thing
       being demonstrated and nothing else — no text of any kind, and no
       decoration either: no border, no frame, no vignette, no panel, no title
       card, no end card, no sparkle, no lens flare, no floating particle, no
       progress bar, no interface furniture.

       The text half is forced on us: every word on screen in this track is
       Devanagari, Veo cannot set Devanagari, and a clip with mangled Hindi in
       it is unusable however good the animation is. Labels are not lost — they
       are rendered by us, in the right font, over the top of this clip
       (`labels` on a video beat; see src/veo.py and tools/composite.py), and
       they land on the caption that names the part, which a generated label
       could never do.

       The decoration half is a quality rule. Everything that reaches the
       screen has to be there because the student needs it; a lens flare over a
       corrosion demonstration is not a better video, it is a distraction with
       production value. One idea in the frame, cleanly shown.

       Both halves are stated POSITIVELY in the prompt and enumerated in the
       NEGATIVE list, never the other way round. Naming a thing in the positive
       section is a signal to draw it — that is the ledger's most expensive
       entry, and the reason `audit()` refuses a prompt containing certain words
       at all.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from src.llm import complete, strip_fences

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / ".claude" / "skills" / "video-prompt"
PLATES = ROOT / "assets" / "backgrounds"

# --------------------------------------------------------------------------- #
# The frame. These numbers are not style — they are measured off the two things
# that share the frame with the clip, and if either moves, these move with it.
#
#   CAPTION_BAND  tools/composite.py composites nothing here, but Manim writes
#                 the caption at 0.090 and it can run to two lines. 0.26 is the
#                 cut line the compositor uses, chosen to clear two lines and
#                 still sit above STAGE_TOP (0.290) in the scene template.
#   PRESENTER_TOP composite.py puts the presenter's head at FULL_Y=966 of 1920.
#                 A clip that draws below 0.503 draws behind him.
# --------------------------------------------------------------------------- #
LAYOUT = {
    "size": "1080x1920 vertical 9:16",
    "caption_cut": 0.26,       # everything above this is the caption strip
    "presenter_top": 0.50,     # everything below this is the presenter
    "partial_bottom": 0.70,    # see FRAMES: the presenter is covered to the chest
    "full_bottom": 0.92,       # when the presenter steps aside, the usable floor
}

# How much of the frame a beat is allowed to use, and what it costs.
#
# The narrow default exists because the presenter is the clock and he is on
# screen; it is not a stylistic preference. But some ideas genuinely do not fit
# above the middle line — a tall apparatus, two vessels side by side, anything
# with a vertical process in it — and squeezing them into the band makes them
# too small to read, which fails the student in a quieter way than a layout
# error does.
#
# So there is a middle setting. `partial` lets the animation come down over the
# presenter's upper body while keeping the bottom of the frame clear, so he is
# still visibly present and the diagram is still legible. It is a real
# trade-off, chosen per beat and never the default:
#
#   presenter   content above the middle. He is fully visible. Use it whenever
#               the subject fits, which is most of the time.
#   partial     content may reach down over his chest; the bottom stays empty.
#               For a subject that is unreadable at band size.
#   full        he fades out for this beat and the frame is yours to the bottom
#               margin. The most room, and the most disruptive.
FRAMES = {
    "presenter": "presenter_top",
    "partial": "partial_bottom",
    "full": "full_bottom",
}


def frame_of(beat: dict) -> str:
    """Which of FRAMES a beat asks for, from its `presenter` key.

    `presenter: hidden` predates the middle setting and still means the whole
    frame, so old beats keep behaving exactly as they did.
    """
    want = (beat.get("presenter") or "").strip().lower()
    if want == "hidden":
        return "full"
    if want in ("partial", "low", "wide"):
        return "partial"
    return "presenter"


def layout_of(beat: dict) -> str:
    """How the finished clip is laid into the frame: `panel` or `full`.

    This changes what the PROMPT has to ask for, which is easy to miss because
    it is decided by the compositor. Under `full` the generated frame becomes
    the video frame, so the subject has to keep out of the caption strip at the
    top and out of the presenter's half at the bottom — that is what the guide
    line wording is for. Under `panel` the clip is laid in WHOLE inside a band
    of its own, above a torn-paper divider, with the caption and the presenter
    outside it. Asking for the guide lines there wastes three quarters of the
    picture and pushes the subject up into the band's own dissolve.

    The default matches tools/composite.py's DEFAULT_VEO_LAYOUT, so the prompt
    and the composite cannot disagree about which of the two is happening.
    """
    want = (beat.get("layout") or "panel").strip().lower()
    if want not in ("panel", "full"):
        raise ValueError(f"unknown layout {want!r}; expected 'panel' or 'full'")
    return want


BACKDROPS = ("plate", "green", "own")


def backdrop_of(beat: dict) -> str:
    """What this clip is generated ON, which decides how much work the run does.

    plate  the house background is UPLOADED into Flow and the clip is generated
           on it, so the clip can be cut into the middle of a Manim render of
           the same picture with no visible join. Necessary for the full-bleed
           layout, where the generated frame IS the video frame.
    green  a flat chroma field, keyed at composite time. No upload; the
           background behind the animation is this render's own plate, which is
           an exact match rather than Veo's approximation of one.
    own    Veo's own plain backdrop, laid into the panel whole and not keyed.
           The panel is a DESIGNATED AREA with a torn-paper edge, so nothing
           has to match anything: the clip's background simply is the panel.

    `own` is the cheapest by a long way. It removes the upload-and-attach path
    entirely — no reference images, no asset picker, no chips to verify — which
    is the most fragile part of the Flow route and the source of most of its
    failures. It only works under `panel`; full-bleed still needs the plate.
    """
    want = (beat.get("background") or "").strip().lower()
    if want in ("green", "chroma"):
        return "green"
    if want in ("own", "none", "self"):
        return "own"
    if want in ("", "plate"):
        return "plate"
    raise ValueError(f"unknown background {want!r}; expected one of {BACKDROPS}")


def is_green(beat: dict) -> bool:
    """Whether this beat is generated on a chroma field and keyed afterwards."""
    return backdrop_of(beat) == "green"


def floor_for(frame: str) -> float:
    """The lowest fraction of the frame height this mode may draw down to."""
    try:
        return LAYOUT[FRAMES[frame]]
    except KeyError:
        raise ValueError(
            f"unknown frame mode {frame!r}; expected one of {sorted(FRAMES)}")

SUBJECTS = {"physics", "chemistry", "biology", "maths"}


def plate_for(subject: str) -> Path:
    """The background image this clip must be generated on top of."""
    s = (subject or "").strip().lower()
    if s not in SUBJECTS:
        raise ValueError(
            f"meta.json says subject={subject!r}; expected one of {sorted(SUBJECTS)} "
            f"so a background plate can be attached to the generation")
    p = PLATES / f"{s}.png"
    if not p.is_file():
        raise FileNotFoundError(f"no background plate at {p}")
    return p


def reference_for(root: Path, name: str) -> Path:
    """The textbook's own picture of a figure, to attach alongside the plate.

    A generated apparatus is a plausible apparatus, and plausible is not what
    this track needs. `tools/figure_from_scan.py` already argues this at length
    for the Manim path: three attempts at the Berkeley-Hartley apparatus each
    produced a different machine, none of them the one in the book, and a
    student comparing the video against the page they revise from sees two
    different machines. Veo invents in exactly the same way, so it gets the same
    answer — the book's own picture goes in with the prompt.

    Two files can serve, and the raw crop is preferred:

      <name>_scan.png     the untouched crop of the book page: the printed
                          drawing with its own line weight and paper tone, which
                          is what "familiar to the student" actually means.
      <name>_preview.png  the traced version. Cleaner, and still the book's own
                          ink, so this is a real fallback rather than a
                          consolation — but tracing has already thrown the
                          shading away, and shading is much of what makes a
                          generated apparatus resemble the printed one.
    """
    # assets/references/ holds a still made FOR this beat — the look and the
    # starting arrangement in one picture. It wins over a book scan when both
    # exist: the scan says what the thing is, the reference says what this clip
    # must be made of.
    ref = Path(root) / "assets" / "references" / f"{name}.png"
    if ref.is_file():
        return ref
    figs = Path(root) / "assets" / "figures"
    for suffix in ("_scan.png", "_preview.png"):
        p = figs / f"{name}{suffix}"
        if p.is_file():
            return p
    raise FileNotFoundError(
        f"the beat asks for reference figure {name!r} but neither "
        f"{figs / (name + '_scan.png')} nor {figs / (name + '_preview.png')} "
        f"exists. Crop it out of the book scan first:\n"
        f"    python tools/figure_from_scan.py inbox/scans/<slug>.png \\\n"
        f"        --crop L,T,R,B --out {figs / name}")


def load_skill() -> str:
    """SKILL.md and its reference blocks, as one system prompt.

    Same three files `src/frames.py` loads. Kept as its own function rather than
    imported from there because importing frames drags in the image-generation
    stack and its OpenAI client, which this module never needs.
    """
    parts = []
    for name in ("SKILL.md", "references/blocks.md", "references/bug-ledger.md"):
        path = SKILL_DIR / name
        if path.is_file():
            parts.append(f"===== {name} =====\n{path.read_text(encoding='utf-8')}")
    if not parts:
        raise FileNotFoundError(
            f"The video-prompt skill isn't in {SKILL_DIR}. Unpack video-prompt.skill.")
    return "\n\n".join(parts)


# The part of the contract that is ours rather than the skill's, spelled out for
# the writer. Kept as prose because that is what the model reads best, and kept
# here rather than in the task string so a change is reviewable in one place.
# The BACKGROUND paragraph of the contract, which is different depending on what
# was actually uploaded — and getting it wrong is not cosmetic. §15's whole
# mechanism is that the prompt REFERS to the supplied image instead of describing
# a background; a prompt that talks about "the supplied background plate" when
# what was supplied is the previous clip's final frame is describing a picture
# the tool cannot see, which is the failure §15 exists to prevent.
# The chroma field. GREEN is the default, but it is the WRONG choice for botany
# and that is not a preference — it is measured. A plant diagram is green by
# nature (stalks, tissue, leaves), so on a green field the subject and the
# background collide: an ovule came back with its embryo sac at rgb(35,189,37)
# against a background of rgb(33,190,37), and the key punched a hole exactly
# where the most important part of the diagram was. Banning green in the subject
# fights the subject matter on every clip, and one slip is invisible until after
# the key.
#
# So pick a field the subject cannot contain. Blue for plants; green stays right
# for most animal and molecular work.
CHROMA = {
    "green": ("#00B140", "chroma green"),
    "blue":  ("#0047BB", "chroma blue"),
}
GREEN = CHROMA["green"][0]      # kept for callers that predate the choice


# The look every clip in a subject shares, stated in the SAME WORDS every time.
# CONSISTENCY.md's first rule: models drift on paraphrase, so a house style is
# worth nothing unless it is repeated verbatim. Add a subject here rather than
# describing the style inline in a brief.
STYLES = {
    "textbook": (
        "Drawn as a clean educational textbook illustration: bold dark outlines, "
        "flat saturated colours, smooth cel shading, simple clear shapes. It is a "
        "drawing from a school biology book — not a photograph, not a microscope "
        "image, and not a realistic three-dimensional render."),
    "photoreal": (
        "Photoreal materials under soft, even, neutral lighting. Clean "
        "instructional photography: accurate before it is pretty, one idea in "
        "the frame, nothing a student could mistake for part of the apparatus."),
    "realistic": (
        "Photoreal three-dimensional scientific visualisation, the kind a "
        "natural-history documentary uses: every object is a physical thing "
        "with volume, weight and real surface material, lit by one soft "
        "directional key with gentle fill, with soft contact shading where "
        "forms meet and a shallow, unshowy depth of field. Rendered, not drawn "
        "— no flat fills, no outlines, no cel shading, no cartoon proportions "
        "and no diagram styling. The realism is in the materials, the lighting "
        "and the way things move: shapes, counts and directions stay exactly as "
        "described above, because a beautiful render of the wrong structure is "
        "worth less than a plain drawing of the right one. Movement is smooth, "
        "unhurried and physically plausible, with weight behind it — nothing "
        "snaps, pops or slides."),
}


DEFAULT_STYLE = (
    "clean instructional illustration for a Class 12 exam answer — accurate "
    "before it is pretty, and finished-looking rather than busy. One idea in "
    "the frame, well lit, well composed, nothing a student could mistake for "
    "part of the apparatus.")


def style_of(beat: dict) -> str | None:
    """The look this beat is generated in, by name. None keeps the house default."""
    want = (beat.get("style") or "").strip().lower() or None
    if want and want not in STYLES:
        raise ValueError(f"unknown style {want!r}; expected one of {sorted(STYLES)}")
    return want


def style_clause(style: str | None) -> str:
    if not style:
        return ""
    try:
        return "\n\nSTYLE: " + STYLES[style]
    except KeyError:
        raise ValueError(f"unknown style {style!r}; expected one of {sorted(STYLES)}")


def _green_clause(style: str | None = None, chroma: str = "green") -> str:
    """The background clause for a clip that will be keyed rather than plated.

    SHORTER ON PURPOSE. The plate version has to argue at length because it is
    asking Veo not to touch something it very much wants to touch, and the bug
    ledger's §16 rule says that arguing about a thing is itself a signal to draw
    it — the LOGO SAFE AREA block produced logos in both corners. Asking for a
    flat green field is a thing Veo is happy to do, so it takes three sentences
    instead of three paragraphs, and there is nothing to protect.

    Note what is NOT here: any band, any guide line, any size check. Placement
    stops being something we ask for and becomes something we do — the keyed clip
    is scaled and positioned by the compositor, which cannot be argued with.
    """
    hexv, name = CHROMA[chroma]
    return f"""BACKGROUND: the entire background is one flat, even, saturated {name}
({hexv}), edge to edge, with nothing else in it at all. It is the same green in
every frame and in every part of the frame. The subject floats on that green.

There is no floor, no wall, no table, no surface, no horizon, no room, no
shadow cast onto anything, and no gradient, texture, vignette or lighting
falloff in the green. The subject casts no shadow onto the background.

NOTHING IN THE SUBJECT IS THAT COLOUR, and nothing in it is transparent enough to
show the background through it — the background is removed afterwards, and anything green
or see-through disappears with it. Every other colour is available and should be
used freely — the field colour is chosen so the subject never needs it.{style_clause(style)}

FILL THE FRAME WITH THE SUBJECT. It is scaled down and positioned afterwards, so
every pixel it does not occupy is resolution thrown away: make it as large as it
can be while still complete, with only a modest margin of green around it.
Measured on the first keyed clip — a subject occupying 4% of the frame had to be
enlarged 1.4x to fill its slot, and softened. This is the exact OPPOSITE of the
rule for a clip generated on the plate, where the subject must be small and sit
inside a band; here the band is applied by the compositor and the only thing
size costs is sharpness.

BUT STILL COMPLETE, and clear of every edge — IN EVERY FRAME, not merely the
first. A subject that starts complete and grows past the edge is the failure that
actually happens: measured on a DNA replication clip, one helix became two, the
drawing needed more width, and the model took it from the margin until both
helices ran off the top and bottom. Whatever the subject BECOMES by the end must
also fit, so size it for its largest moment and let the opening frame look
emptier than feels natural. A subject touching an edge cannot be repositioned,
and one cropped by an edge cannot be used at all."""


def _background_clause(*, carried: bool, referenced: bool) -> str:
    if carried:
        first = """FIRST FRAME: the image attached to this generation is the exact frame the
PREVIOUS clip in this sequence ended on. It is not a mood reference and not a
style hint — it is the picture the student is looking at at the instant this
clip begins, and this clip has to CONTINUE it.

Everything visible in it is already decided and is not yours to redesign: the
background, the apparatus and where each part of it sits, its colours and
proportions, the direction and warmth of the light, the camera's distance and
angle. Begin on that arrangement, unchanged, and animate the change described
below from there. Do not restate the scene, do not re-stage it "better", do not
move the camera to a nicer angle, do not adjust the lighting.

Skill §15 applies in full to this frame the way it normally applies to a plate:
do not recolour, blur, extend, crop, scale or animate the supplied image. The
two clips are cut together with no transition, so anything that shifts between
its last frame and your first is a visible jump in the finished video."""
    else:
        first = """BACKGROUND: a background image IS attached to this generation. Skill §15 applies
in full: do not describe a background, do not invent one, do not recolour,
blur, extend, crop, scale or animate the one supplied. It must look identical in
the first frame and the last, and identical to the same plate rendered elsewhere
in the video — this clip is spliced into the middle of a longer render and any
drift in the plate reads as a jump cut.

NOTHING IS ADDED TO IT EITHER, and this is the failure that actually happens.
The supplied picture already carries whatever marks it carries; it gets no
others. Do not add artwork to it, do not add objects, symbols, diagrams,
molecules, formulae, letters or numbers to it, do not fill its empty areas, and
do not "complete" or enrich its design. Measured on a real generation: a plate
carrying one flask and one molecule came back carrying a flask, four molecules,
a benzene ring, a DNA helix and two chemical formulae written in text. Every one
of those was invented, and every one of them makes the splice visible.

Treat the supplied picture as UNTOUCHABLE — not as a style to imitate and not as
a starting point to build on. It is a photograph of the wall this animation is
happening in front of. Reproduce it exactly, and put the subject in front of it.

THE SUPPLIED PICTURE IS NOT A STAGE TO BE COVERED. It stays VISIBLE around
whatever is drawn — above it, below it, and on both sides of it. What this clip
shows is a compact object sitting ON that picture, not a scene of its own that
fills the frame. Nothing is drawn edge to edge, and nothing brings its own
environment with it: no floor, no wall, no tabletop, no horizon, no expanse of
liquid, no room. Those all replace the supplied picture, and a clip whose
background is not the supplied picture cannot be used at all — however good the
animation on it is — because it is cut into a render of that exact picture and
the join would be a hard cut.

Describing any surface, surround or setting is therefore the single most
dangerous thing you can do in this prompt. Describe the OBJECT and what changes
about it, and nothing else."""

    if not referenced:
        return first

    return first + """

REFERENCE FIGURE: a SECOND image is attached — the figure as it is printed in
the student's own textbook. It is there to be matched, not copied: build the
apparatus this clip shows to that arrangement, that shape, those proportions and
those relative positions, so that a student who has revised from the book
recognises what they are looking at without having to work it out.

Match the arrangement and ignore the medium. It is a page scan, so it is flat
line art on paper, and this clip is not: keep your own lighting, depth and
materials. Reproduce its LAYOUT, not its paper, its line weight, its greyness or
its printing. And note that any lettering visible on the scan is part of the
book, not part of the brief — those labels are typeset separately and laid over
this clip afterwards, so nothing written on the scan may appear in the frame.

Where the scan and the description below disagree, the description wins: the
book's own figure has been checked against the verified answer, and where it was
found wanting that is exactly what the brief is correcting."""


# A keyed panel clip: no background language at all (the green clause covers
# it), and no guide lines (the compositor places it) — but the subject still has
# to be centred and whole, because the panel takes the whole picture.
GREEN_PANEL_PLACEMENT = """WHERE THE ANIMATION SITS. The subject is CENTRED in the picture, both across it
and down it, and large enough to read comfortably while an even margin of plain
background remains on all four sides.

THE WHOLE SUBJECT IS INSIDE THE PICTURE. Every object is shown COMPLETE, both
ends visible, nothing running off any edge and nothing cut through by the side
of the picture. A subject that is naturally long is laid ACROSS the picture and
made short enough that both ends sit inside it.

It never grows, expands, drifts or scales up during the clip: it is exactly the
same size in the last frame as in the first.

"""


# SEEN THREE TIMES, SO IT IS WRITTEN DOWN. When one object separates into two,
# Veo lets their colours converge: the grey backbone drifted to tan partway
# through and both freed strands ended the same colour, on three generations in
# a row, with the reference image getting the START exactly right every time. A
# reference fixes what a thing is MADE OF; it does not survive a change of
# topology, and separating is the moment identity is lost.
# A FINISHED CHANGE THAT HOLDS IS CORRECT, and saying so stops the repair loop
# inventing the opposite. A review read a deliberate hold as "the fork stalls
# instead of continuing", the revision turned that into a standing check —
# "keeps moving rightward every second and never freezes" — and the next clip
# was failed for doing exactly what the brief asked. src/veo_conform.py holds
# the end state to fill the window anyway, so a clip that arrives already
# holding is the easy case, not a defect.
SETTLES_AND_HOLDS = """THE CHANGE FINISHES INSIDE THE CLIP AND THEN STAYS PUT. It runs once, comes to
rest where the description says, and holds that finished state, motionless and
complete, to the last frame. Reaching the end early is correct; the held state
is the answer the student is looking at. What is wrong is the opposite: a change
still in progress when the clip ends, or one that starts over, reverses, or
carries on past where it was told to stop.

"""

IDENTITY_HOLDS = """IDENTITY SURVIVES THE CHANGE. Every part keeps the colour and the material it
has in the first frame, for the whole clip, and most of all while it is moving
or coming apart. When one thing separates into two, the two do NOT drift towards
each other's colour and do not both end up the colour of whichever was brighter:
each keeps its own, and the two stay plainly different at every moment,
including the very last frame. Nothing recolours, fades, dulls or takes on a
neighbour's material at any point.

"""

REFERENCED_START = """THE SUPPLIED PICTURE IS THIS CLIP'S FIRST FRAME. It shows the subject exactly
as it must be built and the background exactly as it must look: the same parts,
the same number of them, the same colours, the same materials, the same
lighting, the same background.

Begin on that picture, unchanged, and animate only the change described below.
Nothing in it is a suggestion to be reinterpreted: do not restyle it, do not
rebuild the subject a different way, do not add a part it does not have, do not
change how many of anything there are, and do not bring the background into
focus. Everything not named as changing stays exactly as the picture has it,
from the first frame to the last.

"""

OWN_BACKDROP = """BACKGROUND: a plain, even, unlit dark backdrop behind the subject — one deep,
desaturated colour, the same in every frame and in every part of the frame, with
nothing else in it at all.

There is no floor, no wall, no table, no surface, no horizon, no room, no
laboratory, no window and no scenery of any kind. No gradient, no texture, no
vignette, no lighting falloff, no pattern, no artwork and no second colour. The
subject does not cast a shadow onto it. Nothing in the picture suggests a place;
the subject is simply on a dark ground.

"""


# The backdrop for a REALISTIC clip, which is not the flat card the other modes
# want. The house reference is a macro shot of dodder on a host stem: the
# subject sharp and close, the background a soft wash of out-of-focus green.
# That defocus is most of why it reads as real rather than as a render — a
# photoreal subject pasted on a flat field looks like a cut-out. But it must
# stay UNREADABLE: the moment a leaf or a bench edge can be identified, the clip
# has an invented setting in it and stops matching the rest of the video.
REALISTIC_BACKDROP = """BACKGROUND: the subject is the only thing in focus. Behind it lies a soft,
heavily out-of-focus wash of DEEP, DARK, DESATURATED colour — depth, not
scenery. It is dark enough that the lit subject is clearly the brightest thing
in the picture: a low-key background, never pale, never cream, never white,
never brighter than the subject. Nothing in it is sharp and nothing in it is
identifiable: no leaf, branch, wall, floor, table, horizon, room, window,
instrument, cell, molecule or man-made edge can be made out anywhere, and in
particular no blurred copy of the subject itself — only smooth dark tone. It is
the same wash from the first frame to the last, it never comes into focus, and
nothing in it moves independently of the subject.

The subject is lit as a real object: one soft directional key with gentle fill,
the falloff and the soft contact shading a real light would give it.

"""


def house_contract(*, frame: str = "presenter", carried: bool = False,
                   referenced: bool = False, green: bool = False,
                   style: str | None = None, chroma: str = "green",
                   layout: str = "full", backdrop: str = "plate") -> str:
    """The contract for one clip.

    `frame` and `green` are ORTHOGONAL and it took a wrong turn to see it.
    `frame` says which band of the finished video this clip occupies — the
    compositor needs that whether or not the clip is keyed. `green` says how the
    clip is GENERATED: on the plate, or on a chroma field to be keyed out later.

    They interact in one place. On a keyed clip the band is achieved by scaling
    and positioning at composite time, so asking Veo for it as well is not
    belt-and-braces — it is one more chance to draw a line or a measurement into
    a frame that must carry no marks at all.
    """
    top = LAYOUT["caption_cut"]
    bot = floor_for(frame)
    full_frame = frame == "full"
    # DELIBERATELY NO NUMBERS. The first entry in the bug ledger is a clip that
    # rendered "12-30%" and "Band D" as visible text, because the layout
    # instructions contained percentages and a zone name — and the model treated
    # them as things to draw. This track cannot absorb that at all: its whole
    # contract is that the frame carries the animation and NOT ONE character.
    # `top` and `bot` still drive the wording; they just never reach the prompt.
    lower_line = {
        "full": "close to the bottom edge of the frame",
        "partial": "across the frame well below the middle, leaving roughly the "
                   "bottom third clear",
        "presenter": "straight across the exact middle of the frame",
    }[frame]
    reserved_bottom = {
        "full": "Below the lower guide line there is nothing but background — a "
                "narrow margin along the bottom edge, kept clear.",
        "partial": "Below the lower guide line there is nothing but background. "
                   "The bottom of the frame stays completely empty, because a "
                   "presenter is composited there afterwards and has to remain "
                   "visible; anything drawn down there would cover him.",
        "presenter": "Below the lower guide line there is nothing but background. "
                     "The entire lower half of the frame stays empty, because a "
                     "presenter is composited into it afterwards; anything drawn "
                     "there ends up hidden behind him.",
    }[frame]
    background = (_green_clause(style, chroma) if green
                  else REFERENCED_START if backdrop == "own" and referenced
                  else (REALISTIC_BACKDROP if style == "realistic" else OWN_BACKDROP)
                  if backdrop == "own"
                  else _background_clause(carried=carried, referenced=referenced))
    # A keyed clip is PLACED by the compositor, so none of the band language
    # applies to it — and leaving it in would be worse than useless. It would be
    # asking Veo to solve a problem we have already taken away from it, and every
    # extra clause about where things sit is another chance to draw a line, a
    # band or a measurement into a frame that must carry no marks at all.
    # THE PANEL LAYOUT USES THE WHOLE PICTURE, so none of the guide-line wording
    # applies to it. The clip is laid into a band of its own with the caption
    # above it and the presenter below it, and nothing is cropped away — so the
    # subject is centred and comfortably large, exactly the composition the
    # guide lines exist to prevent under `full`. Getting this wrong is not
    # cosmetic: it puts the subject in the top quarter of the picture, which is
    # the quarter the band dissolves into the plate.
    panel_placement = """WHERE THE ANIMATION SITS. The whole picture is used, edge to edge, and nothing
in it is cropped away afterwards.

The subject is CENTRED in the picture, both across it and down it, and is large
enough to read comfortably while a clear, even margin of plain background
remains on all four sides. It is not pushed to the top, not pushed to one side,
and not scaled up until it touches an edge.

THE WHOLE SUBJECT IS INSIDE THE PICTURE, and this matters most for anything with
a long axis. Every object is shown COMPLETE: both of its ends are visible, with
clear background beyond each end. Nothing runs off any edge and nothing is cut
through by the side of the picture.

A subject that is naturally long — a rod, a strip, a tube, a column, a stem, a
long molecule — is laid ACROSS the picture and made short enough that both ends
sit inside it, rather than allowed to continue past the edge. A small complete
object is correct; a large one running out of frame is not, however good it
looks on its own.

SIZE CHECK, BEFORE ANYTHING IS DRAWN: the subject — including every arrow, glow,
shadow, ripple, reflection and inset belonging to it — is scaled so that its
whole height and its whole width fit inside the picture with that margin still
left. It never grows, expands, drifts or scales up at any moment during the
clip. It is exactly the same size in the last frame as in the first.

No line, no band, no edge, no seam, no border, no frame and no change of tone or
brightness appears anywhere in the picture at any moment.

"""
    placement = "" if green else f"""WHERE THE ANIMATION SITS. Picture two invisible horizontal guide lines: an upper
one a short way down from the top edge, and a lower one running {lower_line}.
Everything that is drawn lives in the space BETWEEN those two lines.

Above the upper guide line there is nothing but background. That strip is covered
by other material later, so anything drawn up there is discarded and wasted.
{reserved_bottom}

The subject therefore sits HIGH in the frame, in the upper middle. It is not
centred in the frame and it does not fill the frame.

The guide lines are a composition aid for you only. They are NEVER drawn. No
line, no band, no edge, no panel, no seam, no border, no frame and no change of
tone or brightness appears anywhere in the picture at any moment.

SIZE CHECK, BEFORE ANYTHING IS DRAWN: the subject — including every arrow, glow,
shadow, ripple, reflection and inset belonging to it — is scaled so that its
whole height fits in that space with a clear visible margin still left below it.
If any part of it would reach the lower guide line, the whole thing is made
smaller until it does not. It never grows, expands, drifts downward or scales up
at any moment during the clip. It is exactly the same size in the last frame as
in the first.

THE WHOLE SUBJECT IS INSIDE THE PICTURE, and this matters most for anything with
a long axis. Every object is shown COMPLETE: both of its ends are visible, with
clear background above the top end and below the bottom end. Nothing runs off the
top edge, nothing runs off the bottom edge, nothing is cut through by the side of
the picture, and nothing spans the full height of the frame.

A subject that is naturally long — a rod, a strip, a tube, a column, a stem — is
made SHORT ENOUGH TO FIT rather than allowed to continue past the edge. Scale it
down until its entire length, both ends included, sits inside the space between
the guide lines. A small complete object is correct; a large one running out of
frame is not, however good it looks on its own.

"""
    # Under `panel` the subject is MEANT to sit in the middle and fill most of
    # the picture, so the clauses that forbid exactly that have to come out of
    # the negative list as well. Leaving them in is the same mistake as the
    # guide-line wording, one step further along where it is harder to see.
    # HALF THE NEGATIVE LIST EXISTS TO PROTECT A PICTURE WE UPLOADED. With no
    # upload there is no such picture, and naming one anyway is an instruction
    # to invent it — the same mistake as writing "logo" into a prompt that wants
    # no logo. Those clauses come out for `green` and `own`.
    protect = ("the supplied background being covered or replaced, the "
               "background being redrawn in a similar style, a plausible "
               "imitation of the supplied background instead of the supplied "
               "background itself, " if backdrop == "plate" else
               "anything in the background coming into focus or becoming "
               "recognisable, a sharp edge anywhere behind the subject, "
               if style == "realistic" else
               "the background gaining any detail, texture, pattern, scenery or "
               "second colour, ")
    # THE SHAPE OF THE GENERATION FOLLOWS THE LAYOUT.
    # Under `full` the generated frame IS the video frame, so it is the portrait
    # frame. Under `panel` it is a landscape band, and asking for a portrait
    # clip there means the compositor crops a centre strip out of it and throws
    # two thirds of the generation away.
    shape = ("1920x1080 horizontal 16:9" if layout == "panel"
             else LAYOUT["size"])
    # THE STYLE LINE IS THE WHOLE LOOK, so it is one string chosen by name
    # rather than prose written per beat. CONSISTENCY.md's first rule: models
    # drift on paraphrase, so a house style is worth nothing unless it is
    # repeated verbatim. It used to reach only the chroma branch, which meant
    # every plate and panel clip silently got the illustration look no matter
    # what the beat asked for.
    style_text = STYLES.get(style or "", DEFAULT_STYLE)
    if style and style not in STYLES:
        raise ValueError(f"unknown style {style!r}; expected one of {sorted(STYLES)}")
    ground = {"plate": "the supplied background",
              "green": "that green",
              "own": "that dark ground"}[backdrop]
    camera_why = ("The plate must not move, and a moving camera moves it."
                  if backdrop == "plate" else
                  "The background must not move, and a moving camera moves it.")
    identity = IDENTITY_HOLDS if not green else ""
    settles = SETTLES_AND_HOLDS
    keep_colour = ("a part changing colour during the clip, two things that "
                   "separate ending up the same colour as each other, a strand "
                   "or ribbon losing its own colour, ")
    keep_out = ("the subject growing, expanding or drifting during the clip, "
                "the subject touching any edge of the picture; "
                if layout == "panel" else
                "the subject reaching or crossing the middle of the frame, "
                "growing, expanding or drifting downward, the illustration "
                "filling the whole frame, a full-frame poster layout; ")
    if layout == "panel":
        # The panel scales the WHOLE generated frame into its band, so a subject
        # sitting in a corner lands in that corner. What drops out for a keyed
        # or self-backed clip is the background ARGUMENT, not the composition:
        # there is no plate to protect, so the long clause about not touching it
        # goes and the short one about where the subject sits stays.
        placement = (panel_placement if backdrop == "plate"
                     else GREEN_PANEL_PLACEMENT)
    return f"""THIS TRACK'S CONTRACT — these override anything in the skill they disagree with.

FORMAT: {shape}, and the clip is SILENT (skill §17 applies in full).

{background}

{placement}{identity}{settles}THE FRAME CONTAINS THE ANIMATION AND NOTHING ELSE. This is the strictest rule
in the pack and it has no exceptions. What is drawn is the thing being
demonstrated, on {ground}, and that is the complete list of what
appears. Everything a viewer sees must be part of the demonstration itself.

Two consequences, and both are absolute:

  1. Nothing written. No words, no letters in any script, no numerals, no
     equations, no chemical formulae, no units, no axis numbers, no legend, no
     caption, no subtitle, no label of any kind. Everything written in this
     video is Devanagari and is typeset separately in the correct font and laid
     over this clip afterwards — so a generated letterform is a defect even when
     it is beautiful. Describe what is SHOWN, never what is named.

  2. Nothing decorative. No border, no frame, no vignette, no split panel, no
     title card, no end card, no sparkle, no glint, no lens flare, no floating
     particle, no dust mote, no light ray, no interface element, no arrow that
     is not itself part of the mechanism being taught. If a student could not
     say what an element is teaching them, it does not belong in the frame.

State both of these positively — say what IS in the frame. Put the forbidden
things ONLY in the NEGATIVE list, in the tool's own vocabulary, and never in the
body of the prompt: naming a thing where the tool is being told what to draw is
how it ends up drawn.

CAMERA: locked and static. No push-in, no pull-back, no pan, no handheld drift,
no rack focus. {camera_why}

STYLE: {style_text}

THE NEGATIVE LIST must include, at minimum, every category above: on-screen
text, letters, numerals, subtitles, captions, labels, equations; borders, frames,
vignettes, title cards, sparkles, lens flares, floating particles and interface
elements; a floor, a wall, a tabletop, a horizon, a room, an expanse of liquid or
any other invented surrounding, the subject bringing its own environment, {protect}extra artwork added to the
background, additional molecules, additional symbols, additional diagrams,
additional formulae or lettering on the background; {keep_colour}{keep_out}a visible line, band or seam across the frame; and the
subject running off the top edge, running off the bottom edge, being cut off by
any edge of the picture, or spanning the full height of the frame."""


def _captions_around(lines: list[dict], at: int, span: int = 3) -> str:
    lo, hi = max(0, at - 1), min(len(lines), at + span)
    return "\n".join(f"[{i}] {lines[i]['text']}" for i in range(lo, hi))


# What the writer is told about the clips on either side of this one. Empty for a
# standalone beat, which is what keeps the old prompts byte-identical.
def _chain_context(*, previous: dict | None, position: str, carried: bool) -> str:
    if not (previous or position or carried):
        return ""
    out = ["\nTHIS CLIP IS PART OF A SEQUENCE."]
    if position:
        out.append(f"Its place in that sequence: {position}.")
    out.append(
        "The clips play back to back with no transition between them, so they "
        "have to read as ONE continuous demonstration filmed in one take — not "
        "as several takes of the same subject. The student's eye is on the same "
        "apparatus across the cut and will catch anything that jumps.")
    if previous:
        out.append(
            "\nTHE PROMPT THAT PRODUCED THE CLIP IMMEDIATELY BEFORE THIS ONE. "
            "Reuse its wording for everything the two clips share — the "
            "apparatus, the materials, the palette, the lighting, the camera. "
            "Do not paraphrase those clauses and do not improve them: two "
            "descriptions of the same object produce two objects, and this is "
            "the single most common way a sequence falls apart.\n"
            f"{previous['prompt']}")
        if previous.get("negative"):
            out.append(f"\nAnd its NEGATIVE list, which yours should keep:\n"
                       f"{previous['negative']}")
    out.append(
        "\nWhat you write must move the demonstration FORWARD from there. This "
        "clip is not a variation on the last one and not a second angle on it — "
        "it is the next thing that happens. Say what CHANGES; leave everything "
        "else exactly as it already is.")
    return "\n".join(out)


def _look_clause(look: str, referenced: bool) -> str:
    """How the subject ALREADY looks, in the author's own words.

    Without this the writer picks a palette and materials for itself, and on a
    referenced beat that is actively harmful: the reference image is attached in
    Flow as the first frame, so a prompt describing deep teal backbones against
    an image showing amber and slate blue hands the model two brutally different
    briefs and it splits the difference. That is what happened here — the beat
    file carried an exact `look`, nothing read it, and the stored prompt for the
    primer beat described a subject that matches neither the reference nor the
    clip already accepted for the beat before it.
    """
    if not look:
        return ""
    tail = ("It is ALSO the image attached in Flow, which is this clip's first "
            "frame, so the words and the picture have to agree exactly."
            if referenced else
            "It is the first frame; the clip starts from here.")
    return f"""
THE SUBJECT AS IT ALREADY LOOKS — same parts, same number of them, same
colours, same materials. Describe it in THESE terms and invent nothing new
about its appearance; spend your words on what MOVES instead. {tail}
{look}
"""


def write_prompt(*, brief: str, lines: list[dict], at: int, subject: str,
                 question: str, accuracy: str = "", script: str = "",
                 look: str = "",
                 frame: str = "presenter", green: bool = False,
                 style: str | None = None, duration: int = 8,
                 carried: bool = False, referenced: bool = False,
                 previous: dict | None = None, position: str = "",
                 layout: str = "full", backdrop: str = "plate",
                 provider: str | None = None) -> dict:
    """Turn one beat's brief into a generation-ready Flow prompt.

    Returns ``{"prompt": ..., "negative": ..., "checks": [...]}``; `checks` is
    the list the visual review is graded against, written by the same pass that
    wrote the prompt so the two cannot drift apart.

    `carried`, `referenced`, `previous` and `position` are the chain arguments
    and all four default off, so a standalone beat is written exactly as before.
    `previous` is the SPEC of the clip immediately before this one in the chain,
    not merely its brief: the writer needs to see the clauses that produced the
    picture it is being asked to continue, because the fastest way to break a
    chain is to describe the same apparatus in different words.
    """
    skill = load_skill()
    task = f"""Write ONE Flow/Veo prompt for a single beat of a Hindi PYQ answer video.

{house_contract(frame=frame, carried=carried, referenced=referenced, green=green, style=style, layout=layout, backdrop=backdrop)}
{_chain_context(previous=previous, position=position, carried=carried)}

THE QUESTION THIS VIDEO ANSWERS:
{question}

WHAT THIS BEAT MUST SHOW (the author's brief — this is the whole job):
{brief}
{_look_clause(look, referenced)}
WHAT THE PRESENTER IS SAYING WHILE IT PLAYS (for timing and emphasis only; do
NOT put any of these words on screen):
{_captions_around(lines, at)}

THE VERIFIED ANSWER — this is the corrected version, not the question paper's.
Every fact the animation shows must agree with it, and each error named here
must be impossible to read into the clip:
{accuracy or '(none supplied — still refuse to draw anything you are unsure of)'}

THE SCRIPT THIS VIDEO IS BUILT FROM, for context on how the topic is being
taught and which parts the teacher leans on. Illustrate the explanation actually
being given, not the topic in general:
{script[:4000] or '(not supplied)'}

LENGTH: the clip is {duration} seconds and the WHOLE animation has to happen
inside it. Give the prompt an explicit time budget, in seconds, written into the
prompt itself — for example "for the first second nothing moves", "over the next
four seconds X travels from A to B", "by the sixth second it is complete", "it
then holds unchanged to the last frame". Make the budget add up to less than
{duration} so there is time left to hold the finished state.

This is the failure this beat set keeps hitting: without a stated budget the
model paces the action across the whole clip and it is still moving when the
video cuts, or it dawdles and the change never legibly happens at all. Three
generations of the supercoiling beat came back as a helix that barely moved.

A change that RESOLVES and then HOLDS is what is wanted — the finished state can
be held on screen to fill a longer window, and a half-finished one cannot. Do
NOT try to fill a longer window with movement; the clip is fitted to the
narration afterwards.

Return JSON and nothing else:
{{"prompt": "the full prompt, 140-260 words, in the house block style. It MUST
             contain the word `silent` — the clip carries no audio and saying
             so is the only thing that stops the tool inventing a voice-over
             and burning its own captions into the picture. SPEND
             THE LENGTH ON THE MECHANISM: what each part is, how many there
             are, which way each one moves, what touches what, and what the
             last frame looks like. Every detail you leave out is one the
             model chooses for itself, and it chooses wrong on exactly the
             things a Class 12 examiner marks. Do not spend it on light,
             mood, lens or style",
  "negative": "the NEGATIVE list, comma separated",
  "checks": ["a short factual statement a reviewer can confirm or deny by
              looking at a frame", "..."]}}

`checks` is what a vision model will grade the finished clip against, so make
each one observable in a still frame and specific enough to fail: not "the
diagram is correct" but "the copper strip is in the blue solution and the zinc
strip is in the colourless one"."""

    raw = strip_fences(complete(skill, task, effort="high", provider=provider))
    return _parse(raw)


def revise_prompt(previous: dict, defects: list[str], *,
                  provider: str | None = None) -> dict:
    """Rewrite a prompt to kill the specific defects the review found.

    Deliberately narrow. A rewrite that reconsiders the whole shot usually
    trades the defect for a new one; the ledger's entries are almost all of the
    form "one clause was missing", so the instruction is to add or tighten
    clauses and change nothing else.
    """
    skill = load_skill()
    task = f"""This prompt was generated and the clip came back wrong.

THE PROMPT THAT WAS USED:
{previous['prompt']}

ITS NEGATIVE LIST:
{previous.get('negative', '')}

WHAT THE REVIEW SAW WRONG:
{chr(10).join('- ' + d for d in defects)}

Fix exactly these defects and change nothing else. Keep the shot, the subject,
the framing and the band. Prefer adding an explicit clause that forbids the
defect and an explicit clause that states the correct alternative, over
rewriting a sentence that was already working — a full rewrite usually swaps one
defect for another. Add each defect to the NEGATIVE list in the tool's own
vocabulary.

DO NOT WRITE A CHECK THE BRIEF DOES NOT ASK FOR. A review once read a
deliberate hold — the change finishing early and staying put, which is what this
track wants — as a stall, and the revision turned that reading into a permanent
check demanding continuous motion. Every later clip was then failed for obeying
the brief. If a reported defect contradicts the brief, the report is wrong: leave
that clause alone and fix the others.

STAY UNDER 300 WORDS. A revision adds clauses and removes none, so prompts grow
every round — one came back at 611 words, nearly twice the ceiling, and was sent
straight back. If fixing these defects needs more words than you have, take them
from the description of light, mood, materials and style, which the tool renders
well without being told. Never take them from the mechanism: what each part is,
how many there are, which way each moves, what touches what, and what the last
frame looks like.

Return the same JSON shape: {{"prompt": ..., "negative": ..., "checks": [...]}}
Keep every check from before and add one per defect."""

    raw = strip_fences(complete(skill, task, effort="high", provider=provider))
    out = _parse(raw)

    # A REVISION MUST BE THE WHOLE PROMPT, NOT A REFERENCE TO IT.
    #
    # Asked to change one clause, the writer sometimes answers with a note
    # meaning "this part is unchanged" — literally "<unchanged — resubmit
    # verbatim>". _parse accepts it, because it is a non-empty string, and it
    # becomes the prompt. The next revision is then handed a nine-word stub and
    # refuses outright: "the two blocks I'm supposed to revise came through as
    # the literal placeholder text". The run dies two steps from the cause.
    if _is_placeholder(out["prompt"], previous["prompt"]):
        out = _parse(strip_fences(complete(skill, task + """

YOUR LAST ANSWER WAS A PLACEHOLDER, not a prompt. Return the COMPLETE prompt
text, every sentence of it, written out in full — including every sentence you
are leaving unchanged. There is nothing on the other end to paste it into: what
you return is what gets sent to the tool verbatim.""",
                                          effort="high", provider=provider)))
        if _is_placeholder(out["prompt"], previous["prompt"]):
            raise ValueError(
                "the prompt writer answered two revisions with a placeholder "
                f"instead of the prompt ({out['prompt'][:80]!r})")
    return out


def _is_placeholder(text: str, previous: str) -> bool:
    """Whether a 'revision' is a note about the prompt rather than the prompt."""
    t = text.strip()
    if t.startswith("<") and t.endswith(">"):
        return True
    if re.search(r"^\s*\[?\s*(unchanged|same as|as above|see above)\b", t, re.I):
        return True
    # A real revision adds a clause or two. Losing two thirds of the prompt is
    # not a revision, whatever it says.
    return len(t.split()) < max(60, len(previous.split()) // 3)


def _parse(raw: str) -> dict:
    try:
        data = json.loads(raw)
    except ValueError:
        m = re.search(r"\{.*\}", raw, re.S)
        if not m:
            raise ValueError(f"the prompt writer did not return JSON:\n{raw[:400]}")
        data = json.loads(m.group(0))
    if not data.get("prompt"):
        raise ValueError(f"the prompt writer returned no prompt:\n{raw[:400]}")
    data.setdefault("negative", "")
    data.setdefault("checks", [])
    return data


BANNED = ("logo", "watermark", "badge", "wordmark")

# The two families the NEGATIVE list must cover, because the prompt body is not
# allowed to name them. One term from each pair is enough — the point is that
# the category was thought about, not that a particular synonym was used.
REQUIRED_NEGATIVES = {
    "on-screen text": ("text", "letter", "word", "caption", "subtitle",
                       "numeral", "number", "label", "typography", "writing"),
    "decoration": ("border", "frame", "vignette", "sparkle", "flare",
                   "particle", "title card", "glow", "overlay", "panel"),
}


def audit(spec: dict, *, carried: bool = False, green: bool = False,
          backdrop: str | None = None, style: str | None = None,
          referenced: bool = False) -> list[str]:
    """Mechanical checks on a written prompt. No model — these are the mistakes
    that are cheap to detect and expensive to discover in a rendered clip."""
    bad = []
    text = spec["prompt"]
    low = text.lower()
    neg = (spec.get("negative") or "").lower()

    # The hard rule: the frame carries the animation and nothing else. The
    # prompt body may not name the forbidden things (naming is drawing), so the
    # only place the rule can be checked mechanically is the negative list —
    # which makes an incomplete negative list a real failure, not a nit.
    for family, terms in REQUIRED_NEGATIVES.items():
        if not any(t in neg for t in terms):
            bad.append(f"the NEGATIVE list says nothing about {family}; the clip "
                       f"must carry the animation and nothing else, and the "
                       f"prompt body is not allowed to say so")

    # The ledger's most expensive entry: naming a thing is a signal to draw it.
    # A prompt that says "no logo" produced a logo in both top corners.
    for w in BANNED:
        if w in low:
            bad.append(f"the prompt contains the word {w!r} — naming it makes Veo "
                       f"draw it, even in a negative (bug-ledger)")

    # Resolve the mode BEFORE the silence rule, because one mode inverts it.
    if backdrop is None:
        backdrop = "green" if green else "plate"
    # SILENCE, except for a presenter clip — whose entire job is that he talks.
    # Asking a speaking clip to be silent is not a safety net, it is a gate that
    # can never pass, and a gate that can never pass gets switched off wholesale.
    if backdrop != "presenter" and not re.search(
            r"silent|no voiceover|no narration", low):
        bad.append("the prompt does not declare the clip silent (§17), so Veo "
                   "will generate a voice and burn in its own captions")
    # `green` is kept as an argument for callers that predate `backdrop`.
    green = backdrop == "green"

    if backdrop == "own" and referenced:
        # The background arrived as a picture, so describing it in words is not
        # merely redundant — it invites the tool to build a second one and
        # choose between them. What the prompt owes here is the CHANGE, and a
        # statement that the supplied frame is where the clip starts.
        if not re.search(r"supplied|attached|reference|first frame|begins? on", low):
            bad.append("a reference picture is attached but the prompt never "
                       "says the clip starts from it, so it reads as a fresh "
                       "shot and the picture is treated as a loose style hint")
    elif backdrop == "own":
        # Nothing was uploaded, so §15 has nothing to check — and applying it
        # would push the prompt to describe a background that does not exist,
        # which is the same mistake as naming a logo. What matters instead is
        # that the ground it DOES describe is plain, because the clip is laid
        # into a designated panel and any scenery in it becomes scenery in the
        # video.
        if not re.search(r"plain|flat|even|unlit|featureless", low):
            bad.append("this clip supplies its own background, but the prompt "
                       "never asks for a plain one — an invented room or bench "
                       "ends up inside the panel and reads as a different video")
        # "the floor of the trough" is the inside of the glassware, not a room.
        # The bare word-list flagged it and three revisions could not clear it,
        # because the prompt was correct: a vessel HAS a floor. Only that exact
        # construction is exempt — "on the floor" still fails, as it should.
        placed = re.sub(
            r"\b(?:floor|base|bottom)\s+of\s+the\s+"
            r"(?:trough|beaker|tumbler|glass|tube|cell|vessel|jar|tank|flask|dish)\b",
            " ", low)
        if re.search(r"\b(floor|tabletop|bench|laboratory|room|horizon)\b", placed):
            bad.append("the prompt puts the subject in a place; the panel wants "
                       "a background with nothing identifiable in it")
        if style == "realistic" and not re.search(r"dark|deep|low.key|dim", low):
            bad.append("this clip is laid into a panel on a dark plate, but the "
                       "prompt never says the background is dark — a pale one "
                       "reads as a lightbox cut into the video")
        if style == "realistic" and not re.search(
                r"out.of.focus|defocus|blurred|shallow depth", low):
            bad.append("this is a realistic clip, but the prompt never asks for "
                       "an out-of-focus background — a photoreal subject on a "
                       "flat field reads as a cut-out, and the defocus is most "
                       "of what makes it look real")
    elif backdrop == "presenter":
        # A GENERATED PRESENTER SPEAKING ON LOCATION. Not b-roll: the whole point
        # is that he talks, so the silence rule is inverted here, and a presenter
        # in frame is required rather than banned. What goes wrong instead:
        #
        # PACE. Every one of the 23 presenter prompts in POL-C2-LA-01 said "in a
        # warm, clear, UNHURRIED teacher's voice", three added "slowly", and the
        # build came back at 31 pauses a minute against the house 23.6, with 30%
        # dead air against 16%. Veo did as it was told. On a route where the voice
        # is replaced afterwards this is not a style note — a slow take leaves the
        # mouth open longer than the dub needs and the lip sync drifts.
        # SCOPED TO THE DELIVERY. "the camera slowly pushing in" is about the
        # lens, not his voice, and flagging it made the gate fire on every clip
        # that had the camera movement the batch needs.
        voice_bits = " ".join(
            s for s in re.split(r"(?<=[.!?]) ", low)
            if re.search(r"voice|says|speaking|speaks|delivery|teacher's", s))
        for w in ("unhurried", "slowly", "measured pace", "deliberate pace",
                  "calm voice", "gentle voice", "takes his time", "pauses between"):
            if w in voice_bits:
                bad.append(f"the delivery is described as {w!r}; that is how the "
                           f"last build got 30% dead air. State the pace "
                           f"positively instead — brisk, running one sentence "
                           f"into the next, no long pauses")
        if not re.search(r"brisk|keeps? going|straight into the next|without pausing|"
                         r"does not pause", low):
            bad.append("the prompt never asks for a brisk delivery, so Veo will "
                       "default to the slow reading that produced 30% dead air")
        if not re.search(r"he says|says in hindi|speaking in hindi|says:", low):
            bad.append("this is a presenter clip but the prompt never gives him a "
                       "line to say")
        if not re.search(r"reference image|the man from the reference", low):
            bad.append("the prompt does not tie him to the character reference, so "
                       "across a batch he will drift into a different man")
        if not re.search(r"india|indian|field|village", low):
            bad.append("the prompt never names India or an Indian setting")
        # NO CAMERA BAN HERE. That rule belongs to b-roll, where a moving
        # camera moves a background that has to composite under a keyed
        # presenter. A presenter clip IS the whole frame, so nothing composites
        # and the ban only produced twelve identical locked-off shots in a row.
        # Movement is wanted; sameness is the defect.
        # SCOPED TO THE CAMERA. Looking for movement words anywhere in the prompt
        # matched "he turns into the arc", so a locked-off shot passed on the
        # strength of its ACTION. Only sentences that mention the camera count.
        cam_bits = " ".join(s for s in re.split(r"(?<=[.!?]) ", low)
                            if "camera" in s or "handheld" in s)
        moves = re.search(r"\b(push|pull|track|arc|crane|drift|dolly|tilt)"
                          r"(es|s|ing)?\b|handheld|camera moves|"
                          r"walks toward the camera", cam_bits)
        # A straight front-facing locked-off shot is a legitimate choice and a
        # useful change of rhythm — it is only a defect when it is EVERY clip.
        # So it passes here if it says so plainly, and batch_variety() below is
        # what refuses a batch that is all of them.
        deliberate = re.search(r"locked off|holding still|static shot|"
                               r"straight to camera|front.facing", cam_bits)
        if not moves and not deliberate:
            bad.append("the shot neither moves nor states that it is deliberately "
                       "locked off; say which, so the batch does not drift into "
                       "twelve identical medium shots by default")
        if not re.search(r"wide shot|close shot|over.the.shoulder|low angle|"
                         r"high angle|medium shot|three.quarter", low):
            bad.append("the prompt states no shot size, so the batch defaults "
                       "to the same medium shot every time")

    elif backdrop == "location":
        # FULL-FRAME LOCATION B-ROLL. Nothing is uploaded and there is no panel:
        # the clip REPLACES the picture for a few seconds while the presenter's
        # audio keeps running. So §15 has nothing to check, and the `own` checks
        # are actively wrong here — that mode forbids naming a place, and naming
        # the place is the entire job of a b-roll shot.
        #
        # What goes wrong instead, every time, is one of four things, and all
        # four have shipped:
        if not re.search(r"live.action|video footage|filmed with a real camera", low):
            bad.append("the prompt never says this is live-action video, so Flow "
                       "reads it as describing a photograph and returns a still — "
                       "this happened twice before the opener was made mandatory")
        if not re.search(r"india|indian|kashmir|hyderabad|punjab|delhi|bengal", low):
            bad.append("the prompt never names India or an Indian place; a batch "
                       "that said 'ordinary townspeople' with no country came back "
                       "EUROPEAN — flat caps, cobbled streets — in a video about "
                       "जूनागढ़ का जनमत-संग्रह")
        if not re.search(r"\b(people|crowd|men|women|famil(?:y|ies)|villagers|father|mother|"
                         r"child|children|neighbours|passengers|"
                         r"soldiers|clerks|delegates|voters|shopkeepers|queue)\b", low):
            bad.append("the prompt names no people; an empty lane was once asked "
                       "to carry रजाकारों की हिंसा and an empty chamber to carry "
                       "Pakistan arguing at the UN, and an empty room teaches "
                       "nothing — b-roll must show someone doing the thing")
        if not re.search(r"continuous motion|keeps? moving|throughout|"
                         r"moves?|walk|march|hurry|shuffle|drift|turning", low):
            bad.append("the prompt never states what MOVES; 'wide static shot' "
                       "reads as a photograph and comes back as a still")
        if re.search(r"\b(presenter|teacher|narrator|host|addressing the camera|"
                     r"pieces? to camera)\b", low):
            bad.append("the prompt puts a presenter in the shot; on a build with "
                       "HeyGen plates the presenter exists only there, and a "
                       "second one in the b-roll reads as a different person")

    elif green:
        # There is no supplied image to refer to, and the whole point is a field
        # that gets removed — so §15's check is not merely irrelevant here, it
        # would push the prompt to describe a background we are about to delete.
        if not re.search(r"chroma green|green screen|flat green", low):
            bad.append("this clip is keyed, but the prompt never asks for a flat "
                       "chroma green background — without it there is nothing to "
                       "key and the clip cannot be composited")
        if re.search(r"\bshadow (on|onto|across) the (floor|ground|surface|background)", low):
            bad.append("the prompt asks for a shadow cast onto the background, "
                       "which keys out with the background and leaves a hole")
    elif not re.search(r"supplied|attached|uploaded", low):
        bad.append("the prompt does not refer to the supplied background image "
                   "(§15), so Veo will generate its own and discard the plate")
    if carried and not re.search(
            r"continu|carries on|carry on|resumes|picks up|"
            r"(first|opening|supplied|attached|previous) frame", low):
        # A chained prompt that reads as a fresh shot description gets a fresh
        # shot. The supplied frame is not a style reference — the prompt has to
        # say that the picture is already on screen and this clip continues it,
        # or Veo re-stages the whole thing and the cut jumps.
        bad.append("this clip continues the previous one and is generated from "
                   "its final frame, but the prompt never says so — it reads as "
                   "a fresh shot, and Veo will re-stage the scene rather than "
                   "carry it on")
    if backdrop != "presenter" \
            and re.search(r"\bcamera\b.*\b(pan|push|pull|zoom|dolly|track|crane|"
                          r"handheld)(s|es|ing|ning|ling|lying)?\b", low) \
            and not re.search(r"no (pan|push|pull|zoom|dolly|camera move)", low):
        bad.append("the prompt moves the camera, which moves the background")

    # Ledger entry #1, enforced rather than merely avoided. The contract no
    # longer contains percentages, but the prompt is written by a model that has
    # read a lot of layout instructions, and it reintroduces them unprompted. A
    # measurement in the body is a measurement that can be drawn, and one drawn
    # character fails the whole clip in this track.
    for token in re.findall(r"\d+\s?%|\b\d+\s?(?:px|pixels?)\b|\bzone [A-Z]\b|"
                            r"\bband [A-D]\b", low):
        bad.append(f"the prompt contains the measurement {token.strip()!r}; "
                   f"numbers and zone names in layout instructions get RENDERED "
                   f"as visible text (bug-ledger #1), and this clip may carry no "
                   f"text at all. Say where the subject sits in words instead")
    # The guide lines are a composition aid. Naming them as things — rather than
    # as a way of describing where the subject goes — is the same failure mode as
    # §16's logo: the model draws what the prompt names.
    if re.search(r"draw(s|n|ing)? (a|the) (invisible )?(guide ?)?line", low):
        bad.append("the prompt talks about drawing a guide line; it is a "
                   "composition aid and must never be described as drawn")

    # THE BUDGET WAS RAISED DELIBERATELY, from 90-160 with a cap at 220.
    #
    # The old ceiling came from watching Veo drop clauses out of long prompts,
    # and that observation stands — but the clauses it drops are the ones nobody
    # spelled out, and this track's failures are failures of ACCURACY: a rung
    # bridging a gap it should not, a fork opening the wrong way. Those are
    # fixed by saying more, not less. So the target moves up and the ceiling
    # stays, because a ceiling is what keeps the detail on the mechanism rather
    # than on the lighting.
    words = len(text.split())
    if words < 90:
        bad.append(f"the prompt is {words} words; under-specified prompts drift, "
                   f"and every unstated detail is one Veo chooses for itself "
                   f"(the house target is 140-260)")
    if words > 320:
        bad.append(f"the prompt is {words} words; past this Veo starts dropping "
                   f"clauses, and the dropped one is never the one you would "
                   f"pick. Cut description of light, mood and style before you "
                   f"cut a word about the mechanism")
    if not spec.get("checks"):
        bad.append("no checks were written, so the visual review has nothing to "
                   "grade the clip against")
    return bad


def batch_variety(shots: dict, *, max_static: float = 0.4) -> list[str]:
    """Refuse a BATCH that is all the same shot.

    Variety is a property of the set, not of any one clip, so no per-clip gate
    can see it. The first GEO batch passed every individual check and still came
    back as twelve identical locked-off medium shots, because each prompt was
    separately fine and collectively identical.
    """
    bad = []
    if not shots:
        return bad
    sizes, static = [], 0
    for k, s in shots.items():
        low = (s.get("shot") or s.get("prompt", "")).lower()
        m = re.search(r"wide shot|close shot|medium wide|medium shot|"
                      r"over.the.shoulder|low angle|high angle", low)
        sizes.append(m.group(0) if m else "unstated")
        if not re.search(r"\b(push|pull|track|arc|crane|drift|dolly|tilt)"
                         r"(es|s|ing)?\b|handheld|camera moves|"
                         r"walks toward the camera", low):
            static += 1
    frac = static / len(shots)
    if frac > max_static:
        bad.append(f"{static} of {len(shots)} clips are locked off "
                   f"({frac*100:.0f}%); over {max_static*100:.0f}% and the batch "
                   f"reads as one unchanging shot")
    if len(set(sizes)) < 3:
        bad.append(f"the batch uses only {len(set(sizes))} shot size(s) "
                   f"({', '.join(sorted(set(sizes)))}); vary them")
    return bad
