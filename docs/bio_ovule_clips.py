"""The ten ovule clips, each anchored to one line of narration.

EVERY CLIP IS ANCHORED TO THE SAME MASTER IMAGE, not to the clip before it.
These all show one diagram at different stages, so a chain would compound error —
clip 4 drifts and 5 through 10 inherit it. A shared master keeps a failure
isolated: clip 7 can be regenerated alone and still match the rest.

The master is attached as a reference to every generation, so the wording below
does NOT re-describe the ovule. It says what CHANGES. Re-describing a thing the
model can already see is how two descriptions of one object become two objects.

No labels anywhere. Every name in this script — बीजाण्डवृन्त, अध्यावरण,
बीजाण्डद्वार — is Devanagari, typeset by src/veo_labels.py and composited over
the clip. Counts are labels too: the 7-cells-8-nuclei arithmetic is never drawn.
"""

# Shared, verbatim in every clip. CONSISTENCY.md rule 1: models drift on
# paraphrase, so the words that must not change are written once.
ANATROPOUS = (
    "The ovule is inverted on its stalk: the stalk runs up alongside the body, and the small "
    "opening in the coats lies at the SAME end as the stalk, close beside the join. The end "
    "furthest from the stalk is closed."
)

ANCHOR = (
    "The supplied picture shows the diagram as it already is. Keep it exactly as it is — "
    "same shapes, same colours, same positions, same size — and add only what is described "
    "below. Nothing already present moves, changes colour, resizes or is redrawn."
)

GREEN = (
    "The background stays one flat, even, saturated chroma green, edge to edge, the same "
    "green in every frame, with nothing else in it: no floor, no wall, no surface, no "
    "horizon, no shadow cast onto it, and no gradient or texture in the green."
)

STYLE = (
    "Clean educational textbook illustration: bold dark outlines, flat saturated colours, "
    "smooth cel shading. A drawing from a school biology book — not a photograph, not a "
    "microscope image, not a realistic 3D render."
)

TAIL = (
    "The whole drawing stays complete with green all around it and clear of every edge in "
    "every frame. The camera is locked and static. Nothing in the drawing is green and no "
    "part of it is transparent. The clip is silent, with no voiceover and no narration."
)

NEG = (
    "text, letters, words in any script, Devanagari, numerals, digits, captions, subtitles, "
    "labels, callouts, leader lines, typography; border, frame, vignette, title card, "
    "sparkle, glint, lens flare, floating particles, glow, interface elements; a floor, a "
    "wall, a table, a horizon, a room, scenery, a shadow cast onto the background, a "
    "gradient or vignette in the green; photorealistic rendering, a microscope photograph, "
    "a realistic 3D render; a seed, a fruit, a flower, a petal, a leaf, a root; the existing "
    "diagram being redrawn, recoloured, resized, moved or restyled; a second ovule; "
    "the drawing growing past any edge or being cut off by any edge; "
    "camera pan, zoom, push-in, rotation; voiceover, narration, speech, music"
)

# n -> (narration anchor for the record, what CHANGES, extra bans, checks)
CLIPS = {
    1: (
        "अण्डाशय में एक या अधिक बीजाण्ड … बीजाण्डासन से जुड़े होते हैं",
        "This one clip does NOT use the master. Draw, on empty green, an ovary in section: "
        "a rounded chamber with a thickened ridge along its inner wall, and three small oval "
        "ovules attached to that ridge, each by its own short stalk. The ovules appear one "
        "after another along the ridge and stay",
        "a fruit, a seed, a whole flower, more than four ovules, ovules floating free of "
        "the ridge",
        ["three ovules, each joined to the ridge by its own stalk",
         "no ovule floats free of the wall",
         "the chamber is closed, not cut open at the side"],
    ),
    2: (
        "बीजाण्ड एक छोटे डंठल जैसी संरचना द्वारा … बीजाण्डवृन्त",
        "the short curved stalk draws itself in from the lower left and meets the body of the "
        "ovule at a single point, and a small thickening settles at exactly that meeting point",
        "the stalk fusing along the side of the body, more than one stalk, the stalk "
        "entering the body",
        ["the stalk meets the body at ONE point, not along a length",
         "the thickening is at the meeting point and nowhere else"],
    ),
    3: (
        "प्रत्येक बीजाण्ड एक अथवा दो, प्रायः दो, सुरक्षात्मक आवरणों से घिरा",
        "two protective coats wrap around the body of the ovule in turn — first an outer coat, "
        "then a second one inside it — drawn as two distinct concentric layers in different "
        "colours. Both stop short close beside where the stalk meets the body, leaving a narrow gap "
        "there — the body is inverted, so the gap and the stalk are at the SAME end",
        "one coat only, three or more coats, the coats meeting and sealing the gap, "
        "the gap being at the far end away from the stalk, the body standing straight up "
        "instead of inverted alongside its stalk",
        ["exactly TWO coats, one inside the other",
         "both coats stop short BESIDE the stalk, at the same end, leaving a gap",
         "the gap is NOT at the far end away from the stalk"],
    ),
    4: (
        "अध्यावरण से ढका नहीं होता … छोटे छिद्र … पराग नलिका … प्रवेश करती है",
        "a slender tube grows in from outside the diagram, reaches the narrow gap at the end "
        "beside the stalk, and passes through that gap into the body. It enters only "
        "through the gap",
        "the tube entering through the coats, the tube entering at the far closed end, the tube "
        "branching, more than one tube",
        ["the tube passes through the GAP and not through a coat",
         "the gap is beside the stalk, not opposite it",
         "exactly one tube"],
    ),
    5: (
        "बीजाण्ड के अंदर मृदूतकी कोशिकाओं से बना मुख्य भाग … बीजाण्डकाय",
        "the space inside the coats fills with a soft, evenly textured tissue, spreading until "
        "it occupies the whole interior. The two opposite ends of that tissue become "
        "distinct — the end at the gap, and the end furthest from it",
        "the tissue spilling outside the coats, the tissue replacing the coats, cells drawn "
        "inside the tissue",
        ["the tissue stays inside the coats",
         "the two distinguished ends are at OPPOSITE poles of the body"],
    ),
    6: (
        "बीजाण्डकाय के अंदर, लगभग बीच में लेकिन थोड़ा-सा बीजाण्डद्वार की ओर … भ्रूण कोष",
        "one large smooth oval sac fades up inside that tissue, placed centrally but clearly "
        "offset toward the end with the gap. The sac is empty inside and large enough that "
        "its interior is plainly visible",
        "the sac being centred, the sac at the far end, more than one sac, anything drawn "
        "inside the sac, a small or cramped sac",
        ["exactly one sac",
         "the sac is offset toward the gap end, not centred and not at the far end",
         "the sac is EMPTY — nothing inside it yet",
         "the sac is large enough to hold three separate groups later"],
    ),
    7: (
        "बीजाण्डद्वार के सिरे की ओर अण्ड उपकरण … एक अण्ड कोशिका और दो सहाय कोशिकाओं से",
        "inside the sac, at the end nearest the gap, three cells appear together as one group: "
        "one clearly larger cell with two smaller cells beside it. They fill only that end of "
        "the sac and the rest of it stays empty",
        "more or fewer than three cells, three equal cells, the group at the far end, "
        "the group filling the whole sac",
        ["exactly three cells in the group",
         "one is clearly larger than the other two",
         "the group is at the end of the sac nearest the gap"],
    ),
    8: (
        "इसके बिल्कुल विपरीत … तीन प्रतिव्यासांत कोशिकाएँ",
        "inside the sac, at the end furthest from the gap, three more cells appear together as "
        "a group. They are similar to each other in size and sit opposite the first group, "
        "with the middle of the sac still empty between them",
        "more or fewer than three cells, the group at the same end as the first group, "
        "the two groups touching",
        ["exactly three cells in this group",
         "they are at the OPPOSITE end from the first group",
         "the middle of the sac is still empty"],
    ),
    9: (
        "भ्रूणकोष के बीच में एक बड़ी केन्द्रीय कोशिका … जिसमें दो ध्रुवीय केन्द्रक",
        "one large cell fills the middle of the sac between the two groups, and two small "
        "round nuclei appear inside that single cell, apart from each other",
        "more than one central cell, one nucleus, three or more nuclei, the nuclei outside "
        "the central cell, the central cell swallowing the end groups",
        ["exactly one large central cell",
         "exactly two nuclei, both inside that one cell",
         "the two end groups are still present and unchanged"],
    ),
    10: (
        "दो ध्रुवीय केन्द्रक आपस में मिलकर द्वितीयक केन्द्रक … नर युग्मक … PEN",
        "the two nuclei inside the central cell drift toward each other and merge into a single "
        "larger nucleus. Then one small round body travels in through the gap end and merges "
        "with that single nucleus, leaving one nucleus in the central cell at the end",
        "the nuclei staying separate, three nuclei at the end, two nuclei at the end, "
        "the male body merging before the two nuclei have joined",
        ["the two nuclei become ONE before the male body arrives",
         "exactly one nucleus remains in the central cell at the end",
         "the arriving body enters from the gap end"],
    ),
}


def prompt_for(n: int) -> tuple[str, str]:
    anchor, change, bans, _ = CLIPS[n]
    head = "" if n == 1 else ANCHOR + "\n\n"
    return (f"{head}{ANATROPOUS}\n\n{GREEN}\n\n{STYLE}\n\nOver the clip, {change}. The movement is steady "
            f"and finishes within the clip.\n\n{TAIL}",
            f"{NEG}, {bans}")


def checks_for(n: int) -> list[str]:
    return CLIPS[n][3]
