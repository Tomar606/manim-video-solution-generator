# BIO-C1-LA-01 — प्रारूपिक आवृतबीजी बीजाण्ड

Script: `inbox/bio_scripts/Prarupik_Avrutbij_Bijand_Revised_Biology_Reel_Script__1_.txt`
Question (2024, 6 marks): *एक प्रारूपी आवृतबीजी बीजाण्ड के भागों का विवरण देते हुए
स्पष्ट एवं साफ-सुथरा नामांकित चित्र बनाइए।*

The question asks for a **labelled diagram**, so here the picture is not
decoration — it is the answer. That makes this the densest script in the set for
animation, and the right one to build the template from.

## The through-line, and why it dictates the approach

This script builds ONE diagram progressively. Part 1 adds the outer parts one at
a time; Part 2 populates the embryo sac inside it. Every clip therefore shows
**the same ovule** at a later stage of construction.

That makes consistency the whole problem. Ten independently generated ovules will
be ten different ovules, and a student watching them in sequence sees the diagram
change shape under them — which is worse than no animation. So each clip after
the first is conditioned on the previous one's final frame, and the run stops
rather than continuing from a clip that failed review (`src/veo_sequence.py`).

## The animations

Numbers are the order they appear. "Anchor" is the narration line the clip must
illustrate — the clip is cut to that line, not to the part.

### PART 1 — the parts of the ovule

| # | anchor (narration) | what the clip shows |
|---|---|---|
| 1 | *अण्डाशय में एक या अधिक बीजाण्ड … बीजाण्डासन से जुड़े होते हैं* | an ovary in section, with two or three ovules attached along the placenta inside it — the establishing shot, before we go in on one |
| 2 | *बीजाण्ड एक छोटे डंठल जैसी संरचना द्वारा … बीजाण्डवृन्त* | one ovule alone; the stalk (funicle) draws itself from the placenta to the ovule body, and the join point (hilum) settles |
| 3 | *प्रत्येक बीजाण्ड एक अथवा दो, प्रायः दो, सुरक्षात्मक आवरणों से घिरा* | two coats wrap around the ovule body in turn, outer then inner, leaving the body visible beneath |
| 4 | *यह … अध्यावरण से ढका नहीं होता … छोटे से छिद्र … पराग नलिका … प्रवेश करती है* | at the end away from the stalk the two coats stop short, leaving a small gap; a pollen tube then grows in through that gap |
| 5 | *बीजाण्ड के अंदर मृदूतकी कोशिकाओं से बना मुख्य भाग … बीजाण्डकाय* | the body inside the coats fills with soft tissue, and the two opposite ends become distinct — the pore end and the far end |
| 6 | *बीजाण्डकाय के अंदर, लगभग बीच में लेकिन थोड़ा-सा बीजाण्डद्वार की ओर … भ्रूण कोष* | a large oval sac fades up inside the tissue, sitting centrally but offset toward the pore end |

### PART 2 — inside the embryo sac

| # | anchor (narration) | what the clip shows |
|---|---|---|
| 7 | *बीजाण्डद्वार के सिरे की ओर अण्ड उपकरण … एक अण्ड कोशिका और दो सहाय कोशिकाओं से* | at the pore end of the sac, one larger cell and two smaller ones appear together as a group of three |
| 8 | *इसके बिल्कुल विपरीत … तीन प्रतिव्यासांत कोशिकाएँ* | at the opposite end, three cells appear together |
| 9 | *भ्रूणकोष के बीच में एक बड़ी केन्द्रीय कोशिका … जिसमें दो ध्रुवीय केन्द्रक* | one large cell fills the middle of the sac and two nuclei appear inside it |
| 10 | *दो ध्रुवीय केन्द्रक आपस में मिलकर द्वितीयक केन्द्रक बनाते हैं … नर युग्मक के साथ … PEN* | the two nuclei drift together and merge into one; a male gamete then arrives and merges with it |

## What is NOT animated

- The opening ("2024 में पूछा गया था"), the exam advice, the Notes-button close.
- Every `ON SCREEN:` block. Those are Devanagari text — part names, the 7/8 count,
  the recap order — typeset by `src/veo_labels.py` and composited over the clip.
  **Veo draws none of them.** A generated Devanagari letterform is a defect
  however neat, because no video model sets the script correctly.
- The 7-cells-8-nuclei arithmetic. It is a count, and counts are carried by
  labels, not by asking a generator to render digits.

## CORRECTION — anatropous orientation

The first draft of these checks said the micropyle sits at the end OPPOSITE the
stalk. That is wrong for this question, and it is the error the whole diagram
exists to avoid.

The script specifies an **anatropous** ovule (*आवृतबीजियों में एनाट्रॉपस बीजाण्ड
सबसे सामान्य प्रकार का बीजाण्ड होता है*), and anatropous means the body is
INVERTED through 180° on its stalk. That inversion carries the micropylar end
back down alongside the funicle, so:

- the **micropyle lies close to the hilum**, next to the funicle — not opposite it
- the **chalaza** is at the far end, away from the stalk
- the funicle runs alongside the inverted body, often fused to it as a ridge (the raphe)

An ovule with the micropyle at the far end from the stalk is ORTHOTROPOUS — a
different type, and not what the question asks for.

This is the bug ledger's GAG/GTG lesson repeating: a brief that gives authority to
a wrong assumption produces a clip that is confidently wrong, and the frame review
cannot catch it because the review is graded against the brief.

## Biology checks

Graded per clip; a failure names the fact that is wrong.

1. two or three ovules, each attached to the placenta by its own stalk
2. the stalk meets the ovule body at one point; the ovule is not free-floating
3. **two** coats, not one; they wrap the body and do not seal it completely
4. the micropyle lies NEAR the funicle and hilum (anatropous inversion), not at
   the far end; the pollen tube enters through it and not through the coats
5. the chalaza is at the end AWAY from the stalk, opposite the micropyle
6. the embryo sac is a DISTINCT body inside the nucellus — the nucellus is not
   merely one solid mass — and it is offset toward the micropylar end
7. exactly three cells at the pore end, one clearly larger than the other two
8. exactly three cells at the far end
9. exactly one large central cell, containing exactly two nuclei
10. the two nuclei become ONE before the male gamete arrives; the result is a
    single nucleus, not three

## Open question

Clips 1–6 build outward and 7–10 build inward, so the sac has to be drawn at a
size in clip 6 that still has room for three groups of cells in clips 7–9. If the
chain drifts, the fix is to generate clip 6 with the interior already sketched
faintly, so later clips have somewhere to put things.
