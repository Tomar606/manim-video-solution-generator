"""Generate exactly one real clip, end to end. SPENDS ONE CREDIT.

    .venv-tools/bin/python tools/flow_smoke.py

`flow_probe.py` stops where the money starts: it proves the page can be read and
typed into, and nothing beyond that. This closes the remaining link — submit,
wait, work out which of Flow's media is the clip, pull it through the browser
session, and confirm the bytes decode as video.

It is deliberately not `video veo`. That needs a project with beats, a written
prompt and a review pass, and when something breaks in there it is hard to say
which stage did it. This is the same journey with everything else removed, so a
failure names its own cause.

WHAT IT IS REALLY TESTING
-------------------------
The upload/clip collision, above all. Flow gives an uploaded image a media URL
shaped exactly like a finished clip's, so "a key that was not there a moment ago"
is not sufficient to identify a generation. The plate is attached here precisely
because that is the case that broke: snapshot the media set BEFORE the upload and
the first poll hands back the plate, which then downloads as a PNG named .mp4 and
fails a visual review that was never the problem.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.flow_bridge import FlowBridge, FlowError, inbox_dir, inbox_rel, settled  # noqa: E402

try:
    sys.stdout.reconfigure(line_buffering=True)
except AttributeError:
    pass

SELECTORS = ROOT / "flow" / "selectors.json"
PLATE = ROOT / "assets" / "backgrounds" / "chemistry.png"
TIMEOUT = 900          # Flow takes minutes; a stuck queue takes forever
POLL = 10

# Written to the house contract on purpose, so this also exercises `audit()`'s
# rules rather than proving that some unrelated prompt can be submitted:
# the background is referred to and never described, the clip is declared silent,
# the change resolves inside the clip, and both forbidden families are named only
# in the NEGATIVE list.
PROMPT = """The supplied background image is unchanged for the whole clip. Sitting on
it, in the upper half of the frame, a clean iron nail rests in a shallow glass dish
holding a thin layer of water. A film of orange-brown rust creeps outward from the
waterline across the bright metal, spreading steadily over the exposed surface and
deepening in colour until the whole nail is evenly dulled and the change has
finished. The camera is locked and static. Lighting is soft, even and neutral.
Clean instructional illustration, photoreal materials, accurate rather than
decorative, one idea in the frame. The clip is silent, with no voiceover and no
narration."""

NEGATIVE = ("text, letters, words in any script, numerals, captions, subtitles, "
            "labels, equations, typography; border, frame, vignette, title card, "
            "end card, sparkle, glint, lens flare, floating particles, glow, "
            "overlay panel, interface elements; camera pan, zoom, push-in, "
            "handheld drift; speech, voiceover, music")


def main() -> int:
    sel = json.loads(SELECTORS.read_text(encoding="utf-8"))
    b = FlowBridge().start()
    t0 = time.time()
    try:
        info = b.wait_for_worker(timeout=60)
        print(f"tab: {info.get('tab')}")
        b.call("attach", timeout=120)

        print(f"\nattaching the plate ({PLATE.name})")
        got = b.call("set_image", paths=[str(PLATE.resolve())],
                     selector=sel["plate_input"], timeout=180)
        print(f"  used {got.get('used')} of {got.get('files')}  multiple={got.get('multiple')}")

        # AFTER the upload. This ordering IS the test.
        time.sleep(4)
        media = b.call("list_media", timeout=60).get("media", [])
        before = {m["key"] for m in media}
        tagged = sum(1 for m in media if "video" in m)
        print(f"  media before submitting: {len(before)}"
              + (f" ({tagged} carry a video/image tag)" if tagged else
                 "  [extension not reloaded — no tags; the ordering fix still holds]"))

        print("\ntyping the prompt")
        r = b.call("set_prompt", text=f"{PROMPT}\n\nNEGATIVE: {NEGATIVE}",
                   selector=sel["prompt"], timeout=180)
        print(f"  {r.get('chars')} chars into {r.get('editor')}")

        print("\nsubmitting — this is the credit")
        if sel.get("generate_selector"):
            b.call("click", selector=sel["generate_selector"], timeout=60)
        else:
            b.call("click", text=sel["generate_text"], timeout=60)

        time.sleep(5)
        deadline = time.time() + TIMEOUT
        key = None
        seen_still = False
        while time.time() < deadline:
            now = b.call("list_media", timeout=60).get("media", [])
            new = [m for m in now if m["key"] not in before]
            vids = [m for m in new if m.get("video")]
            stills = [m for m in new if not m.get("video")]
            if stills and not seen_still:
                # Measured at 23s on the first real run, against a clip that took
                # minutes. Flow mints a key the moment the generation is QUEUED
                # and renders it as an <img> preview — a different key from the
                # finished clip's. Downloading it yields a JPEG, which Chrome
                # then saves under a .jpeg name of its own choosing, so the run
                # reports "the download never landed" and points nowhere useful.
                seen_still = True
                print(f"\n  placeholder after {int(time.time() - t0)}s "
                      f"({stills[0]['key'][:20]}…) — not the clip, still waiting")
            if vids:
                key, url = vids[0]["key"], vids[0]["url"]
                print(f"\n  VIDEO after {int(time.time() - t0)}s: {key[:28]}")
                break
            left = int(deadline - time.time())
            print(f"  waiting… {left // 60}m{left % 60:02d}s left", end="\r")
            time.sleep(POLL)
        else:
            print("\n❌ Flow produced nothing. Check the tab: a generation that "
                  "fails its own safety or quota check shows an error in the UI "
                  "and never emits a media URL.")
            return 1

        name = "flow_smoke.mp4"
        print("\ndownloading through the browser session")
        b.call("download", url=url, filename=inbox_rel(name), timeout=600)
        dest = inbox_dir() / name
        for _ in range(60):
            if dest.is_file() and settled(dest):
                break
            time.sleep(1)
        else:
            print(f"❌ the download never landed at {dest}")
            return 1

        size = dest.stat().st_size
        print(f"  {dest}  ({size / 1_000_000:.2f} MB)")

        # The point of the whole exercise: is it actually a video? An uploaded
        # PNG saved under an .mp4 name passes every check up to here.
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
             "stream=codec_name,width,height,duration,nb_frames",
             "-of", "json", str(dest)],
            capture_output=True, text=True)
        try:
            st = json.loads(probe.stdout)["streams"][0]
        except (ValueError, KeyError, IndexError):
            print(f"❌ NOT A VIDEO — ffprobe found no video stream.\n"
                  f"   {probe.stderr.strip()[:200]}\n"
                  f"   This is the upload/clip collision: an attached image was "
                  f"taken for the generated clip.")
            return 1
        print(f"\n✅ {st.get('codec_name')} {st.get('width')}x{st.get('height')} "
              f"{float(st.get('duration', 0)):.2f}s  {st.get('nb_frames')} frames")
        print(f"   total elapsed {int(time.time() - t0)}s")
        return 0
    except FlowError as exc:
        print(f"\n❌ {exc}")
        return 1
    finally:
        try:
            b.call("set_prompt", text="", selector=sel["prompt"], timeout=20)
            b.call("detach", timeout=20)
        except FlowError:
            pass
        b.stop()


if __name__ == "__main__":
    sys.exit(main())
