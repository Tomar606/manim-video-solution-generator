# veo_kit: the Flow submission and download pieces

What the kit uses from here:

| File | Used for |
|---|---|
| `submit.py` | types each prompt into Flow and presses generate (`--no-refs` for b-roll; `--check` costs nothing) |
| `grab_tiles.py` | downloads the newest N clips from the project grid (newest first) |
| `flowkit.py` | the shared pieces: connect, read the tab, the prompt bar |
| `face_gate.py` | the gate that checks the presenter in a finished video is the real man |
| `characters/` | the presenter's reference set, read by `submit.py` and `face_gate.py` |

Don't call these by hand: `tools/kit_veo.py setup | submit | fetch | clean <slug>` wraps them, records what
was queued, files each clip under its id and removes Flow's sparkle. The prompt rules are in
`lab/kit_test/STANDARD.md`.
