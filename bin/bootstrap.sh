#!/usr/bin/env bash
# Set this machine up to run the pipeline natively (macOS / Linux).
#
# Docker is the other option and needs none of this — see README. Use this when
# you want faster renders, or you can't run Docker Desktop.
#
#   ./bin/bootstrap.sh          set up
#   ./bin/bootstrap.sh --check  just report what's missing
set -euo pipefail

cd "$(dirname "$0")/.."
CHECK_ONLY=false
[[ "${1:-}" == "--check" ]] && CHECK_ONLY=true

ok()   { printf '  \033[32m✓\033[0m %s\n' "$1"; }
warn() { printf '  \033[33m!\033[0m %s\n' "$1"; }
bad()  { printf '  \033[31m✗\033[0m %s\n' "$1"; }
have() { command -v "$1" >/dev/null 2>&1; }

echo "Video pipeline — native setup"
echo "=============================="

# --- Python ---------------------------------------------------------------
# Manim 0.18 does not build on 3.13+, so pick the newest supported interpreter.
PY=""
for candidate in python3.12 python3.11 python3.10 python3; do
  if have "$candidate"; then
    ver=$("$candidate" -c 'import sys;print("%d.%d"%sys.version_info[:2])')
    case "$ver" in
      3.10|3.11|3.12) PY="$candidate"; break ;;
    esac
  fi
done
if [[ -z "$PY" ]]; then
  bad "No Python 3.10-3.12 found (Manim 0.18 does not support 3.13+)."
  echo "     macOS:  brew install python@3.12"
  echo "     Ubuntu: sudo apt install python3.12 python3.12-venv"
  exit 1
fi
ok "python: $PY ($($PY -V 2>&1 | cut -d' ' -f2))"

# --- system tools ---------------------------------------------------------
MISSING=()
have ffmpeg  && ok "ffmpeg"  || { bad "ffmpeg missing";  MISSING+=(ffmpeg); }
have latex   && ok "latex"   || { bad "LaTeX missing (equations won't render)"; MISSING+=(latex); }
# pycairo builds from source and locates cairo through pkg-config. Without it
# `pip install manim` dies with "Dependency lookup for cairo ... failed", even
# when cairo itself is installed — so this is a hard requirement, not a nicety.
have pkg-config && ok "pkg-config" || { bad "pkg-config missing (pycairo won't build)"; MISSING+=(pkg-config); }
have node    && ok "node"    || warn "node missing (needed for the Claude CLI)"
have claude  && ok "claude CLI" || warn "claude CLI missing"

if (( ${#MISSING[@]} )); then
  echo
  echo "Install the missing pieces:"
  if [[ "$(uname)" == "Darwin" ]]; then
    echo "  brew install ffmpeg pkg-config cairo pango"
    echo "  brew install --cask mactex-no-gui     # ~5GB, has every package manim needs"
    echo "     (basictex is ~500MB but then needs: sudo tlmgr install standalone"
    echo "      preview doublestroke relsize ragged2e fundus-calligra physics)"
  else
    echo "  sudo apt update"
    echo "  sudo apt install -y ffmpeg build-essential pkg-config libcairo2-dev libpango1.0-dev"
    echo "  sudo apt install -y texlive texlive-latex-extra texlive-fonts-extra texlive-science dvisvgm"
  fi
fi

if ! have claude; then
  echo
  echo "For Claude access on your subscription (no API key needed):"
  echo "  npm install -g @anthropic-ai/claude-code && claude   # log in once"
fi

$CHECK_ONLY && { echo; echo "Check complete."; exit 0; }

# --- venv -----------------------------------------------------------------
echo
if [[ ! -d .venv ]]; then
  echo "Creating .venv ..."
  "$PY" -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --quiet --upgrade pip
echo "Installing Python dependencies (this takes a few minutes the first time)..."
python -m pip install --quiet -r requirements.txt
ok "dependencies installed"

# --- env ------------------------------------------------------------------
if [[ ! -f .env && -f .env.example ]]; then
  cp .env.example .env
  ok ".env created from .env.example — add your ELEVENLABS_API_KEY"
fi

# --- sound effects --------------------------------------------------------
python video.py sfx >/dev/null 2>&1 && ok "sound effect library built" || \
  warn "could not build the sound effects (ffmpeg?)"

echo
echo "=============================="
python video.py doctor || true
echo
echo "Ready. Try:"
echo "  ./bin/video dashboard                    # browser UI"
echo '  ./bin/video new "Deriving the quadratic formula"'
