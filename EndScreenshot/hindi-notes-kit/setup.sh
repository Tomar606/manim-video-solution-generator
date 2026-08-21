#!/usr/bin/env bash
# One-time setup for the Hindi handwritten-notes kit. Run from the kit root:
#     bash setup.sh
set -euo pipefail
KIT="$(cd "$(dirname "$0")" && pwd)"
cd "$KIT"

echo "==> python venv"
python3 -m venv .venv
./.venv/bin/pip install --upgrade pip >/dev/null
./.venv/bin/pip install -r requirements.txt

echo "==> chromium for playwright (Devanagari text shaping — Pillow cannot do it)"
./.venv/bin/playwright install chromium

echo "==> cost guard auto-load"
# cost_guard.py monkeypatches every openai images.edit call to clamp quality, cap the
# number of input images and downscale them. It must load in EVERY interpreter, so it
# goes in as a .pth (sitecustomize.py does not work — Homebrew python shadows it).
SP="$(./.venv/bin/python -c 'import site;print(site.getsitepackages()[0])')"
printf "import sys; sys.path.insert(0, %r); import cost_guard\n" "$KIT/GPT-Notes" \
  > "$SP/zz_cost_guard.pth"
./.venv/bin/python -c "import cost_guard; print('   cost_guard loaded OK')"

echo "==> .env"
if [ ! -f GPT-Notes/.env ]; then
  cp GPT-Notes/.env.example GPT-Notes/.env
  echo "   created GPT-Notes/.env — PUT YOUR OPENAI_API_KEY IN IT"
else
  echo "   GPT-Notes/.env already exists, left alone"
fi

echo
echo "Setup done. Verify with a zero-cost dry run:"
echo "  cd \"$KIT/GPT-Notes/Hindi Hand\""
echo "  ../../.venv/bin/python mockup/import_notes.py Hindi/Ch1"
echo "  ../../.venv/bin/python mockup/typeset_mockup.py Hindi-Ch1"
echo "  ../../.venv/bin/python mockup/preflight.py Hindi-Ch1"
echo "  DRY_RUN=1 ../../.venv/bin/python mockup/gen_from_mockup.py Hindi-Ch1"
