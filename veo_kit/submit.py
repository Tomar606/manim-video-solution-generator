"""Queue character scenes in Google Flow with the three-image reference set attached.

    python veo_kit/submit.py PROMPT.txt [PROMPT.txt ...] --aspect landscape
    python veo_kit/submit.py projects/<slug>/veo/prompts/landscape/s0{1,4}.txt \\
        --character veo_kit/characters/ritesh.json --aspect vertical
    python veo_kit/submit.py ... --check        # every step except pressing submit

Each prompt costs credits. Queue two test scenes first, fetch them, and run the
QC (SETUP.md, step 8) before queueing the rest.

WHAT EACH SUBMISSION PROVES BEFORE PRESSING THE BUTTON
------------------------------------------------------
1. The tab is on the project GRID, not a clip editor. A prompt typed into a clip
   editor's box edits that clip; it is not a new generation.
2. The prompt bar has no stale chips. Attaching is additive, and a leftover
   reference is blended into the new clip silently.
3. Exactly the character's three references are attached, in order: face,
   turned head, build. The model weights earlier references more.
4. The prompt text actually landed. Flow's submit button reports itself enabled
   over an empty box.
5. Flow's aspect setting matches --aspect, when it can be read. The bridge cannot
   change it: it is a setting in Flow's own panel, and a clip in the wrong shape
   is a wasted generation.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import flowkit as fk  # noqa: E402

DEFAULT_CHARACTER = HERE / "characters" / "ritesh.json"

# Flow's settings control renders the output shape as a Material ligature
# (crop_16_9 / crop_9_16). Read, never set. Only the ligature and the bare ratio
# count: "portrait" and "landscape" turn up in prompts shown on the page.
ASPECT_JS = r"""
var t = (document.body.innerText || '');
var v = /crop_9_16|\b9:16\b/.test(t), l = /crop_16_9|\b16:9\b/.test(t);
return v && !l ? 'vertical' : (l && !v ? 'landscape' : null);
"""


def flat(s: str) -> str:
    return " ".join(s.split())


def submit_one(b, sel: dict, project: str, refs: list[Path], text: str,
               *, check: bool) -> str:
    fk.back_to_grid(b, project)
    if "/edit/" in (fk.tab_state(b).get("url") or ""):
        raise fk.KitError("still on a clip editor after going back to the grid")
    # Flow takes two generations at a time and hides the submit arrow while both
    # slots are full. Wait for one HERE, before the chips and the prompt go in,
    # so nothing sits typed in a bar Flow may re-render while we wait.
    if not fk.wait_for_submit(b, sel):
        raise fk.KitError("Flow has been at capacity for fifteen minutes")

    b.call("attach", timeout=60)
    left = fk.clear_chips(b, sel)
    if left:
        raise fk.KitError(f"{left} old reference chip(s) would not clear — remove "
                          f"them from the prompt bar by hand, then run again")

    for ref in refs:
        if fk.already_uploaded(b, sel, ref.name):
            print(f"    {ref.name}: already in Flow's Uploads")
        else:
            print(f"    {ref.name}: uploading")
            fk.upload(b, sel, ref)
    time.sleep(2.0)
    chips = 0
    for ref in refs:
        chips = fk.attach_by_name(b, sel, ref.name)
        time.sleep(1.5)
    print(f"    {chips} reference chip(s) on the prompt bar")
    if chips != len(refs):
        raise fk.KitError(f"expected {len(refs)} chips, found {chips} — look at the "
                          f"prompt bar before anything is generated")

    n = fk.set_prompt(b, sel, text)
    want = len(flat(text))
    print(f"    typed {n} of {want} characters")
    if n < 0.9 * want:
        raise fk.KitError("the prompt did not land in the box")
    if check:
        return "checked — NOT submitted (--check)"
    return fk.start_generation(b, sel)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("prompts", nargs="+", help="prompt .txt files, one per clip")
    ap.add_argument("--character", default=str(DEFAULT_CHARACTER))
    ap.add_argument("--aspect", choices=("landscape", "vertical"), required=True)
    ap.add_argument("--no-refs", action="store_true",
                    help="b-roll with no presenter: attach nothing, and prove the bar is empty")
    # A BACKGROUND IS UPLOADED, NOT DESCRIBED (CLAUDE.md) — and for this kit
    # that is not only about matching a plate. Asking Veo for a "chroma green
    # wall" gets a PALE, unevenly lit green: measured at RGB 125,192,138, which
    # in chroma space sits nearer his skin and black polo than it does to a
    # real key colour. Neither chromakey nor colorkey can separate him from it
    # — every setting either leaves the wall or eats his face and hands. So a
    # scene that needs a particular background is GENERATED on it.
    ap.add_argument("--plate", default="",
                    help="an image to attach as the scene's background, after the refs")
    ap.add_argument("--check", action="store_true",
                    help="do everything except press submit (costs nothing)")
    ap.add_argument("--gap", type=float, default=8.0,
                    help="seconds between submissions")
    a = ap.parse_args()

    ch = json.loads(Path(a.character).read_text(encoding="utf-8"))
    refs = [] if a.no_refs else [fk.ROOT / p for p in ch["refs"][a.aspect]]
    if a.plate:
        # LAST, on purpose: Flow weights earlier ingredients more, and what must
        # survive is his face. The plate only has to set the room.
        refs = refs + [Path(a.plate).resolve()]
    missing = [str(p) for p in refs if not p.is_file()]
    if missing:
        print("  missing reference images (SETUP.md step 3):")
        for m in missing:
            print(f"    {m}")
        return 1
    texts = []
    for p in a.prompts:
        t = Path(p).read_text(encoding="utf-8").strip()
        if not t:
            print(f"  {p} is empty"); return 1
        texts.append((Path(p), t))

    sel = fk.selectors()
    b, project = fk.connect()
    print(f"flow project: {project.rstrip('/').rsplit('/', 1)[-1]}", flush=True)   # tools/kit_veo.py records it
    try:
        fk.back_to_grid(b, project)
        seen = fk.ev(b, ASPECT_JS)
        if seen and seen != a.aspect:
            print(f"  Flow is set to {seen.upper()} output and you asked for "
                  f"{a.aspect}. Change it in Flow's settings panel (the tune "
                  f"control on the prompt bar), then run again.")
            return 1
        if not seen:
            print(f"  (could not read Flow's aspect setting — make sure it is "
                  f"{a.aspect} before this spends credits)")
        bad = 0
        for i, (p, text) in enumerate(texts):
            print(f"[{i + 1}/{len(texts)}] {p.name}  ({len(text.split())} words)")
            try:
                print(f"    {submit_one(b, sel, project, refs, text, check=a.check)}")
            except fk.UserBusy as exc:
                print(f"    stopped: {exc}"); return 2
            except fk.KitError as exc:
                print(f"    FAILED: {exc}"); bad += 1
                if "refused" in str(exc):
                    return 1
            if i + 1 < len(texts):
                time.sleep(a.gap)
        return 1 if bad else 0
    finally:
        b.stop()


if __name__ == "__main__":
    raise SystemExit(main())
