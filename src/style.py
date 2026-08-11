"""The house voice, learned from scripts you've already approved.

A model asked to "write like a teacher" invents its own teacher. The only
reliable way to get *your* presenter's voice is to show it real scripts your
team has shipped and the exact phrasings you want reused — so this module loads
both from ``style/`` and turns them into prompt material.

    style/
      samples/            approved scripts, verbatim (.md or .txt)
      variations.yaml     the recurring lines, with approved alternatives

``variations.yaml`` is the part worth explaining. Recurring moments — opening a
video, moving to the next step, revealing an answer, signing off — are where
generated scripts sound most obviously synthetic, because the model reaches for
the same construction every time. Giving it a bank of approved alternatives, and
telling it which have been used recently, fixes that at the source rather than
catching it in review.

Nothing here is required: with an empty ``style/`` the generator falls back to
its built-in instructions, and everything still runs.
"""
from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
STYLE_DIR = REPO_ROOT / "style"
SAMPLES_DIR = STYLE_DIR / "samples"
VARIATIONS_FILE = STYLE_DIR / "variations.yaml"

SAMPLE_SUFFIXES = (".md", ".txt")

# Enough sample text to establish a voice without crowding out the actual task.
MAX_SAMPLE_CHARS = 14000

# The moments a script keeps having to get through. Names are conventions, not
# a fixed set — any key in variations.yaml is offered to the writer.
KNOWN_SLOTS = ("opener", "hook", "transition", "step", "emphasis",
               "question", "answer", "recap", "closing")


@dataclass
class StyleGuide:
    samples: list[tuple[str, str]] = field(default_factory=list)  # (name, text)
    variations: dict[str, list[str]] = field(default_factory=dict)
    notes: str = ""
    mode: str = "inspiration"        # inspiration | verbatim

    @property
    def has_samples(self) -> bool:
        return bool(self.samples)

    @property
    def has_variations(self) -> bool:
        return any(self.variations.values())

    @property
    def is_empty(self) -> bool:
        return not (self.has_samples or self.has_variations or self.notes)

    def sample_text(self, limit: int = MAX_SAMPLE_CHARS) -> str:
        """Approved scripts, concatenated and trimmed to a prompt-sized budget."""
        out, used = [], 0
        for name, text in self.samples:
            block = f"--- {name} ---\n{text.strip()}\n"
            if used + len(block) > limit:
                break
            out.append(block)
            used += len(block)
        return "\n".join(out)

    def describe(self) -> str:
        parts = []
        if self.samples:
            parts.append(f"{len(self.samples)} sample script(s)")
        if self.has_variations:
            total = sum(len(v) for v in self.variations.values())
            parts.append(f"{total} approved line(s) across "
                         f"{len(self.variations)} slot(s)")
        if self.notes:
            parts.append("style notes")
        return ", ".join(parts) if parts else "empty (using built-in defaults)"

    # ------------------------------------------------------------------ #
    def prompt_section(self, *, seed: int | None = None) -> str:
        """The style half of the drafting prompt."""
        if self.is_empty:
            return ""
        blocks: list[str] = []

        if self.notes:
            blocks.append(f"HOUSE STYLE NOTES:\n{self.notes.strip()}")

        if self.has_samples:
            blocks.append(
                "APPROVED SCRIPTS — this is the voice to match. Study the "
                "rhythm, sentence length, how much Hindi versus English, and "
                "how each beat opens. Do not copy their content:\n\n"
                + self.sample_text()
            )

        if self.has_variations:
            rng = random.Random(seed)
            lines = []
            for slot, options in self.variations.items():
                if not options:
                    continue
                # Shuffle so the model doesn't anchor on whichever we list first
                # — the first option would otherwise win every single video.
                shuffled = options[:]
                rng.shuffle(shuffled)
                shown = shuffled[:8]
                lines.append(f"  {slot}:")
                lines += [f"    - {o}" for o in shown]
            verb = ("Use these lines VERBATIM at the matching moments."
                    if self.mode == "verbatim" else
                    "Use these as the tone to match; reuse them directly when "
                    "they fit naturally.")
            blocks.append(
                f"APPROVED PHRASINGS — {verb} Pick a DIFFERENT one each time a "
                f"slot recurs; never open two beats the same way:\n"
                + "\n".join(lines)
            )

        return "\n\n".join(blocks)


def _read_notes() -> str:
    for name in ("NOTES.md", "notes.md", "STYLE.md"):
        path = STYLE_DIR / name
        if path.is_file():
            return path.read_text(encoding="utf-8")
    return ""


def _strip_frontmatter(text: str) -> str:
    """Samples may be full scripts; the voice lives in the body."""
    stripped = text.lstrip("﻿")
    if stripped.lstrip().startswith("---"):
        match = re.search(r"\n---[ \t]*\n", stripped)
        if match:
            return stripped[match.end():]
    return stripped


def load(style_dir: Path | str = STYLE_DIR) -> StyleGuide:
    """Load whatever the team has put in ``style/``. Missing pieces are fine."""
    base = Path(style_dir)
    guide = StyleGuide(notes=_read_notes() if base == STYLE_DIR else "")

    samples_dir = base / "samples"
    if samples_dir.is_dir():
        for path in sorted(samples_dir.iterdir()):
            if path.suffix.lower() in SAMPLE_SUFFIXES and path.is_file():
                try:
                    guide.samples.append(
                        (path.name, _strip_frontmatter(
                            path.read_text(encoding="utf-8")))
                    )
                except OSError:
                    continue

    variations_file = base / "variations.yaml"
    if variations_file.is_file():
        try:
            import yaml
            raw = yaml.safe_load(variations_file.read_text(encoding="utf-8")) or {}
        except Exception as exc:                      # noqa: BLE001
            print(f"   ⚠️  could not read {variations_file}: {exc}")
            raw = {}
        if isinstance(raw, dict):
            mode = str(raw.pop("mode", "inspiration")).strip().lower()
            guide.mode = mode if mode in ("inspiration", "verbatim") else "inspiration"
            extra_notes = raw.pop("notes", "")
            if extra_notes:
                guide.notes = f"{guide.notes}\n{extra_notes}".strip()
            for slot, options in raw.items():
                if isinstance(options, str):
                    options = [options]
                if isinstance(options, list):
                    cleaned = [str(o).strip() for o in options if str(o).strip()]
                    if cleaned:
                        guide.variations[str(slot)] = cleaned
    return guide


def scaffold(style_dir: Path | str = STYLE_DIR) -> Path:
    """Create ``style/`` with a commented template. Never overwrites."""
    base = Path(style_dir)
    (base / "samples").mkdir(parents=True, exist_ok=True)
    target = base / "variations.yaml"
    if not target.exists():
        target.write_text(TEMPLATE, encoding="utf-8")
    readme = base / "README.md"
    if not readme.exists():
        readme.write_text(README, encoding="utf-8")
    return base


TEMPLATE = """\
# Approved phrasings for the presenter.
#
# Each key is a moment that recurs in every video; each list is the alternatives
# the team has approved for it. The writer picks a different one each time a slot
# comes round, so ten videos don't all open the same way.
#
# mode: inspiration  -> match the tone, reuse when it fits (default)
# mode: verbatim     -> use these exact lines at the matching moments
mode: inspiration

# Optional free-text guidance appended to the house style notes.
notes: |
  Speak to a student who is trying, not to a class. Technical terms stay in
  English; everything joining them is Hindi.

opener:
  - Chalo, aaj ek interesting sawaal se shuru karte hain.
  - Aaj hum ek aisa concept dekhenge jo exam mein bar bar aata hai.

hook:
  - Yeh sawaal dekhne mein simple lagta hai, par ismein ek twist hai.

transition:
  - Theek hai, ab aage badhte hain.
  - Ab isko thoda aur simplify karte hain.

emphasis:
  - Yeh wala step sabse important hai, dhyaan se dekhna.

question:
  - Ab socho, agar yeh value badal jaaye toh kya hoga?

answer:
  - Toh hamara final answer yeh raha.

closing:
  - Bas itna hi. Agli video mein milte hain.
"""

README = """\
# Style corpus

What the presenter sounds like. Two inputs, both optional:

## `samples/`

Drop **real scripts you have already shipped and approved** here, as `.md` or
`.txt`. They can be full pipeline scripts (frontmatter is stripped automatically)
or just the spoken lines. These carry more weight than any written instruction —
the writer matches their rhythm, sentence length and Hindi/English balance.

Three to six varied samples work better than twenty similar ones. Include a short
video and a long one, an easy topic and a hard one.

## `variations.yaml`

The recurring lines — how a video opens, how it moves between steps, how the
answer lands, how it signs off — with every approved alternative. The writer
picks a different one each time, which is what stops a run of videos sounding
identical.

Add as many slots as you like; the names are just conventions.

## Checking it works

```bash
video style                 # what's loaded
video eval <project>        # score an existing script against it
```
"""
