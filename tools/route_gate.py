"""Decide — and then enforce — what a beat is drawn with.

    python tools/route_gate.py projects/<slug>/route_part<N>.json [--explain]

Three jobs, in one pass, all of them blocking:

  1. ROUTE.  Veo, or Manim/SVG. The decision is made from what the beat has to
     get RIGHT, not from what it looks like.
  2. MINIMUM. Every video carries at least one generated clip, and should carry
     two. Veo is what makes these look like something a student wants to watch;
     a video with none has quietly become a slideshow.
  3. PROOF.  A beat routed to Veo may not reach the build with an ungraded or
     failing clip. src/veo_qc.py writes the verdict; this refuses to proceed
     without it.

WHY THE ROUTE IS DECIDED THIS WAY
---------------------------------
docs/bio-veo-vs-manim-routing.md is a post-mortem on fourteen generated clips,
graded against their own checks. The failures were not spread evenly. Every one
of them failed on the same thing:

    a discrete quantity that IS the answer.

9:3:3:1 came out 9:4:4:4. Three antipodals came out two. An anatropous ovule
came out orthotropous. Arrows pointed the wrong way. A-T and G-C paired with
whatever was nearest.

Three of those were then re-briefed precisely — the exact number named, every
alternative banned, the constraint stated three ways — and they failed again.
That settles it as a capability boundary rather than a wording problem, which is
why the checks below are HARD and not advisory. No amount of prompt iteration
buys a beat past them, and pretending otherwise costs a generation cycle each
time.

Veo renders MANNER reliably. It knows what unzipping looks like, what a phage
does, what a pond contains. Ask it for the verb; ask Manim for the number.

WHY THE DEFAULT IS VEO
----------------------
Where a beat could go either way, it goes to Veo. Not because the drawing is
worse but because the generated clip is what makes the video feel made rather
than assembled, and engagement is a real requirement rather than a decoration.
The router therefore WARNS on a beat that declares no marked fact and is drawn
anyway — that is a choice someone should have to justify.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# A beat that must get any of these right cannot be generated. The names are the
# categories the post-mortem's failures actually fell into, kept separate so the
# refusal message can say which one applies.
MARKS = {
    "quantity":  "an exact count is the marked fact (three cells, two bonds)",
    "order":     "a sequence or ranking is the marked fact (trophic tiers)",
    "direction": "a direction is the marked fact (5'->3', eaten -> eater)",
    "pairing":   "which thing goes with which is the marked fact (A-T, G-C)",
    "reproduce": "the student must copy this exact figure into the answer book",
}

MIN_VEO = 1          # a video with none has stopped being a video
WANT_VEO = 2         # below this is a warning, not a refusal

VEO_ROUTES = {"veo"}
DRAWN_ROUTES = {"manim", "svg", "chip"}


def check(beats: list[dict], *, explain: bool = False) -> list[str]:
    fails: list[str] = []
    warns: list[str] = []
    veo = [b for b in beats if b.get("route") in VEO_ROUTES]

    for b in beats:
        slug = b.get("slug", "?")
        route = b.get("route")
        marked = {k for k, v in (b.get("marked") or {}).items() if v}

        if route not in VEO_ROUTES | DRAWN_ROUTES:
            fails.append(f"{slug}: route {route!r} is not one of "
                         f"{sorted(VEO_ROUTES | DRAWN_ROUTES)}")
            continue

        unknown = marked - set(MARKS)
        if unknown:
            fails.append(f"{slug}: unknown marked fact(s) {sorted(unknown)}")

        if route in VEO_ROUTES and marked:
            why = "; ".join(MARKS[m] for m in sorted(marked & set(MARKS)))
            fails.append(f"{slug}: routed to Veo but {why}. Generation does not "
                         f"reliably produce this, and re-briefing has been tried "
                         f"and failed — draw it instead")

        # The tie-break the house wants: if nothing has to be exact, generate it.
        if route in DRAWN_ROUTES and not marked:
            warns.append(f"{slug}: nothing is declared as a marked fact, so this "
                         f"could be generated — drawn beats should say why")

        # Veo cannot set Devanagari, so any label on a generated clip is an
        # overlay. A beat that has labels and does not say so is a clip that
        # will come back with invented lettering on it.
        if route in VEO_ROUTES and b.get("labels") and b.get("overlay") != "manim":
            fails.append(f"{slug}: has labels {b['labels']} but no "
                         f'"overlay": "manim" — no video model sets Devanagari, '
                         f"so labels are composited, never generated")

        # Proof, for anything already generated.
        if route in VEO_ROUTES and b.get("clip"):
            qcf = b.get("qc")
            if not qcf:
                fails.append(f"{slug}: has a clip but no qc verdict recorded")
            else:
                p = Path(qcf) if Path(qcf).is_absolute() else ROOT / qcf
                if not p.is_file():
                    fails.append(f"{slug}: qc verdict {qcf} is missing")
                else:
                    v = json.loads(p.read_text()).get("verdict")
                    if v != "pass":
                        fails.append(f"{slug}: qc verdict is {v!r}, not 'pass'")

        # Prompt hygiene, reusing the audit that already exists rather than a
        # second opinion about the same prompt.
        if route in VEO_ROUTES and b.get("prompt"):
            try:
                from src.veo_prompts import audit
                for line in audit({"prompt": b["prompt"],
                                   "negative": b.get("negative", "")}):
                    fails.append(f"{slug}: {line}")
            except Exception as exc:                      # noqa: BLE001
                warns.append(f"{slug}: prompt audit unavailable ({exc})")

        if explain:
            tag = "VEO " if route in VEO_ROUTES else route.upper().ljust(4)
            why = ", ".join(sorted(marked)) or "no marked fact"
            print(f"  {tag} {slug:22s} {why}")

    if len(veo) < MIN_VEO:
        fails.append(f"only {len(veo)} beat(s) routed to Veo; every video carries "
                     f"at least {MIN_VEO}. If nothing here can be generated, say "
                     f"so explicitly rather than letting it default to none")
    elif len(veo) < WANT_VEO:
        warns.append(f"only {len(veo)} Veo beat; {WANT_VEO} is the house target")

    for w in warns:
        print(f"  warn: {w}")
    return fails


def main() -> int:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    path = Path(sys.argv[1])
    beats = json.loads(path.read_text())
    fails = check(beats, explain="--explain" in sys.argv)
    if fails:
        print("ROUTE GATE FAILED:")
        for f in fails:
            print(f"  {f}")
        return 1
    veo = sum(1 for b in beats if b.get("route") in VEO_ROUTES)
    print(f"  route gate ok — {len(beats)} beats, {veo} generated, "
          f"{len(beats) - veo} drawn")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
