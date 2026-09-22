# Veo character kit

Talking-presenter clips from Google Flow (Veo) that look like the real presenter
and say the scripted Hindi line, in landscape or vertical, downloaded and checked
automatically.

**Start with [SETUP.md](SETUP.md).** It is written so that a Claude Code
instance on a fresh machine can set everything up and run it: prerequisites,
the Chrome extension, the reference images, prompt rules,
generating, downloading, QC and troubleshooting.

The short version, once set up:

```bash
PY=.venv-tools/bin/python
$PY veo_kit/syllables.py --file projects/<slug>/veo/lines.json            # 33-42 syllables each
$PY veo_kit/build_prompts.py projects/<slug>/veo --aspect landscape        # or vertical
$PY veo_kit/submit.py projects/<slug>/veo/prompts/landscape/s0{1,4}.txt --aspect landscape
$PY veo_kit/fetch.py --prompts projects/<slug>/veo/prompts/landscape \
    --out projects/<slug>/veo/clips --aspect landscape --expect 2
$PY veo_kit/face_gate.py projects/<slug>/veo/clips/s01.mp4 --at 1 2.5 4 5.5 7 8.5 9.5
$PY veo_kit/speech_qc.py projects/<slug>/veo/clips/s01.mp4 --line-file projects/<slug>/veo/lines.json --n 1
```
