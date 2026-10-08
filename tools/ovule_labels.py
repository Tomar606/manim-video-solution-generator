"""Build the ovule chip spec from the figure's anchor table.

    python tools/ovule_labels.py

The anchors come out of `ovule_plate_svg.py`, measured on the masks and checked
to land on the part they name. This turns them into the chip spec the band
renderer takes, which needs two more things the anchor table cannot know:

    WHERE THE WORD GOES, as opposed to where it points. The figure is letterboxed
    into a 1080-wide band, so the margins either side are the only free space,
    and a label is centred on its coordinate — so its y has to be pushed off its
    anchor's y whenever two labels on the same side would sit on top of each
    other. Done by hand once, this is the thing that rots: the labels were
    right, the figure was re-rendered a little taller, and two of them landed on
    the same line.

    WHICH LABELS ARE UP YET. The video names the parts one at a time and every label
    STAYS once shown, so each slug carries every label named so far.

The label text is the video's own wording, and the same strings are spoken and
captioned; do not respell them here.
"""
from __future__ import annotations

import json
from pathlib import Path

ASSET = Path("tools/edu/renderer/assets/ovule-plate.svg")
SPEC = Path("tools/edu/renderer/spec/chips/ovule.json")
BAND_W, BAND_H = 1080, 700   # must match the chip spec's h below

# Which margin each label's word sits in. The plate puts almost everything on
# the right; the three parts of the stalk read better on the left, beside it.
SIDE = {"निभाग": "R", "अध्यावरण": "R", "भ्रूणकोष": "R", "बीजाण्डद्वार": "R",
        "बीजाण्डकाय": "L", "हाइलम": "L", "बीजाण्डवृन्त": "L"}
COL = {"L": 0.15, "R": 0.85}
# The chip sits ABOVE the usual stage band. Captions on these four videos
# end at row 243 and the band starts at 380, so 137px of the frame was
# empty; the figure needs it, because the alternative is a diagram short
# enough to clear the presenter and too small to read.
CHIP_TOP = 300
GAP = 0.085          # centre-to-centre, as a fraction of the band's height

# The order the video names them in, and it is the EXISTING one, unchanged.
# Each slug shows these labels and every one before them. Splitting a step is
# not a free edit: the narration is already cut to this progression, and moving
# हाइलम into a step of its own put it on screen a beat after it is spoken.
STEPS = [("p1a-plain", []), ("p1b-funicle", ["बीजाण्डवृन्त", "हाइलम"]),
         ("p1c-integ", ["अध्यावरण"]), ("p1d-micro", ["बीजाण्डद्वार"]),
         ("p2a-nucellus", ["बीजाण्डकाय"]), ("p2b-chalaza", ["निभाग"]),
         ("p2c-sac", ["भ्रूणकोष"])]


def to_band(fx: float, fy: float, fw: int, fh: int) -> tuple[float, float]:
    """Figure fraction -> band fraction, through the letterbox.

    The band renderer drops the SVG into a 1080 x h box at its own aspect, so
    the figure does not fill the band and an anchor written as a band fraction
    is wrong the moment the band height changes. This is that mapping, done once.
    """
    k = min(BAND_W / fw, BAND_H / fh)
    rw, rh = fw * k, fh * k
    return (((BAND_W - rw) / 2 + fx * rw) / BAND_W,
            ((BAND_H - rh) / 2 + fy * rh) / BAND_H)


def place(names: list[str], anch: dict) -> list[list]:
    """Lay the words out in the margins, pushed apart to stay legible."""
    out = {}
    for side in ("L", "R"):
        rows = sorted([n for n in names if SIDE[n] == side], key=lambda n: anch[n][1])
        ys = [anch[n][1] for n in rows]
        for i in range(1, len(ys)):            # push down
            ys[i] = max(ys[i], ys[i - 1] + GAP)
        for i in range(len(ys) - 2, -1, -1):   # then back up, if it ran off
            ys[i] = min(ys[i], ys[i + 1] - GAP)
        for n, y in zip(rows, ys):
            out[n] = [COL[side], round(min(max(y, 0.06), 0.94), 4)]
    return [[n, *out[n], *[round(v, 4) for v in anch[n]]] for n in names]


def main() -> None:
    a = json.loads(ASSET.with_suffix(".anchors.json").read_text(encoding="utf-8"))
    fw, fh = a["figure"]
    anch = {k: to_band(*v, fw, fh) for k, v in a["anchors"].items()}
    missing = [n for n in SIDE if n not in anch]
    if missing:
        raise SystemExit(f"no anchor for: {', '.join(missing)}")

    chips, shown = [], []
    for slug, names in STEPS:
        shown = shown + names
        chips.append({"slug": slug, "mode": "svg", "svg": f"assets/{ASSET.name}",
                      "h": BAND_H, "labels": json.dumps(place(shown, anch),
                                                        ensure_ascii=False)})

    # The embryo-sac close-up is a different figure and keeps its own chips.
    # Filtering on the OLD asset name alone is not enough — this tool is run
    # repeatedly, and after the first run its own chips no longer name it, so
    # they were kept as well and the spec grew a duplicate set every time.
    # Slug is the identity that matters.
    mine = {slug for slug, _ in STEPS}
    old = json.loads(SPEC.read_text(encoding="utf-8"))
    keep = [c for c in old
            if c["slug"] not in mine and "ovule-v2" not in c.get("svg", "")]
    SPEC.write_text(json.dumps(chips + keep, ensure_ascii=False, indent=1),
                    encoding="utf-8")
    print(f"  {SPEC}: {len(chips)} ovule chips rebuilt, {len(keep)} kept")

    # The height and the top belong together and live in two different files:
    # `h` is the chip spec's, because it sizes the PNG, and `top` is the plan's,
    # because burn_chips reads placement from there. Setting one without the
    # other is how the figure ends up in the wrong place, so both are written
    # here. Only OUR slugs are touched — the embryo-sac chips share these plans
    # and sit in the ordinary band.
    for plan in sorted(Path("projects/bio-c1-la-01").glob("plan_part*.json")):
        rows = json.loads(plan.read_text(encoding="utf-8"))
        hit = 0
        for r in rows:
            if Path(r["png"]).stem in mine:
                r["top"], hit = CHIP_TOP, hit + 1
        if hit:
            plan.write_text(json.dumps(rows, ensure_ascii=False, indent=1),
                            encoding="utf-8")
            print(f"  {plan.name}: {hit} chip(s) placed at top={CHIP_TOP}")
    for n, (x, y) in anch.items():
        if n in SIDE:
            print(f"    {n:22s} word x={COL[SIDE[n]]:.2f}  points to ({x:.3f}, {y:.3f})")


if __name__ == "__main__":
    main()
