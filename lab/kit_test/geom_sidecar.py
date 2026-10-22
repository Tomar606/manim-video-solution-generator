"""Write the .geom.json that tools/gates.py needs beside a kit-pipeline video.

    python lab/kit_test/geom_sidecar.py <plan.json> <final.mp4>

The output gate checks the presenter against the geometry the video was BUILT with,
read from a sidecar next to the file; a video without one fails ("no geometry
sidecar").  Until 22 Oct 2026 this was written by hand, by copying the sidecar of an
earlier video out of a projects/*/final folder.  That folder is never committed, so
on any other machine the gates could not run at all.  The geometry is all in the
compiled timeline, so this derives it from there.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sidecar(plan_p: Path, video: Path) -> Path:
    tl_js = HERE / "out" / plan_p.stem / "timeline.js"
    t = tl_js.read_text()
    tl = json.loads(t[t.index("=") + 1:].strip().rstrip(";"))
    card = next((b["pbox"] for b in tl["beats"] if b["pbox"].get("card")), None)
    g = {"_note": "kit pipeline: presenter in a rounded card at the bottom right (not bottom-anchored, "
                  "so the anchoring check does not apply), free-standing on 'full' beats, and in circle hubs; "
                  "one uniform scale throughout",
         "dx_out": 0}
    if card:
        x, y, w, h = card["box"]
        g["presenter_card"] = {"box": [x, y, w, h], "radius": card["radius"], "scale": card["scale"],
                               "top_frac": round(y / 1920, 4)}
    g["hub"] = [{"beat": b["id"], "cx": b["pbox"]["cx"], "cy": b["pbox"]["cy"], "r": b["pbox"]["r"],
                 "scale": b["pbox"]["scale"]} for b in tl["beats"] if b["presenter"] == "hub"]
    out = video.with_name(video.name + ".geom.json")
    out.write_text(json.dumps(g, indent=1))
    return out


if __name__ == "__main__":
    print(sidecar(Path(sys.argv[1]), Path(sys.argv[2])))
