"""What the API keys are costing us.

Every paid call appends one line to a local ledger before the pipeline moves on,
so spend is answerable at any moment without opening a billing dashboard —
per video, per stage, per model.

Two things are deliberate:

**Token and image counts are exact; money is an estimate.** The counts come
straight off the API response. The prices come from :data:`PRICES`, which is a
table in this file that goes stale the moment OpenAI changes it — so it's
overridable from ``pricing.json`` and every report says plainly that the dollar
figure is derived, not billed. Never quote these numbers as an invoice.

**The budget is checked before the call, not after.** ``OPENAI_BUDGET_USD``
stops work when the estimated spend crosses it, because a limit you discover
afterwards isn't a limit.
"""
from __future__ import annotations

import json
import os
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LEDGER = Path(os.getenv("USAGE_LEDGER", REPO_ROOT / ".usage" / "spend.jsonl"))
PRICING_OVERRIDE = REPO_ROOT / "pricing.json"

_lock = threading.Lock()

# USD per 1M tokens (input, output). CHECK THESE against openai.com/pricing —
# they are a starting point, not a source of truth, and they will drift.
# Override without touching code by creating pricing.json:
#     {"gpt-5": {"input": 1.25, "output": 10.0}}
PRICES: dict[str, dict[str, float]] = {
    "gpt-5":          {"input": 1.25, "output": 10.00},
    "gpt-5-mini":     {"input": 0.25, "output": 2.00},
    "gpt-5-nano":     {"input": 0.05, "output": 0.40},
    "gpt-4.1":        {"input": 2.00, "output": 8.00},
    "gpt-4.1-mini":   {"input": 0.40, "output": 1.60},
    "gpt-4.1-nano":   {"input": 0.10, "output": 0.40},
    "gpt-4o":         {"input": 2.50, "output": 10.00},
    "gpt-4o-mini":    {"input": 0.15, "output": 0.60},
}

# USD per generated image, by model and quality. Same caveat as above.
IMAGE_PRICES: dict[str, dict[str, float]] = {
    "gpt-image-2":     {"low": 0.02, "medium": 0.04, "high": 0.08},
    "gpt-image-1.5":   {"low": 0.02, "medium": 0.04, "high": 0.08},
    "gpt-image-1":     {"low": 0.011, "medium": 0.042, "high": 0.167},
    "gpt-image-1-mini": {"low": 0.005, "medium": 0.011, "high": 0.036},
}

DEFAULT_IMAGE_PRICE = 0.04


def _load_overrides() -> None:
    """Let the team correct prices without a code change."""
    if not PRICING_OVERRIDE.is_file():
        return
    try:
        data = json.loads(PRICING_OVERRIDE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return
    for model, prices in (data.get("text") or data).items():
        if isinstance(prices, dict) and "input" in prices:
            PRICES[model] = {"input": float(prices["input"]),
                             "output": float(prices["output"])}
    for model, prices in (data.get("image") or {}).items():
        if isinstance(prices, dict):
            IMAGE_PRICES[model] = {k: float(v) for k, v in prices.items()}


_load_overrides()


def _price_for(model: str) -> dict[str, float] | None:
    if model in PRICES:
        return PRICES[model]
    # Dated snapshots like gpt-5-2025-08-07 price as their base model.
    for known in sorted(PRICES, key=len, reverse=True):
        if model.startswith(known):
            return PRICES[known]
    return None


def text_cost(model: str, input_tokens: int, output_tokens: int) -> float | None:
    price = _price_for(model)
    if price is None:
        return None
    return (input_tokens * price["input"] + output_tokens * price["output"]) / 1e6


def image_cost(model: str, count: int, quality: str = "medium") -> float:
    table = IMAGE_PRICES.get(model)
    if table is None:
        for known in sorted(IMAGE_PRICES, key=len, reverse=True):
            if model.startswith(known):
                table = IMAGE_PRICES[known]
                break
    if table is None:
        return count * DEFAULT_IMAGE_PRICE
    return count * table.get(quality, DEFAULT_IMAGE_PRICE)


@dataclass
class Entry:
    kind: str                # text | image
    provider: str
    model: str
    stage: str = ""
    project: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    images: int = 0
    cost_usd: float | None = None
    note: str = ""

    def to_dict(self) -> dict:
        return {
            "ts": datetime.now().isoformat(timespec="seconds"),
            "kind": self.kind, "provider": self.provider, "model": self.model,
            "stage": self.stage, "project": self.project,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "images": self.images,
            "cost_usd": round(self.cost_usd, 6) if self.cost_usd is not None else None,
            "note": self.note,
        }


# Set by the CLI so every call records which video and stage it belongs to.
_context = {"stage": "", "project": ""}


def set_context(stage: str = "", project: str = "") -> None:
    _context["stage"] = stage or _context["stage"]
    _context["project"] = project or _context["project"]


def record(entry: Entry) -> None:
    """Append one call to the ledger. Never raises — accounting must not be able
    to fail a render."""
    try:
        entry.stage = entry.stage or _context["stage"]
        entry.project = entry.project or _context["project"]
        LEDGER.parent.mkdir(parents=True, exist_ok=True)
        with _lock, open(LEDGER, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")
    except OSError:
        pass


def record_text(model: str, usage, *, provider: str = "openai",
                stage: str = "", project: str = "", note: str = "") -> None:
    """Record a chat completion from an SDK usage object."""
    inp = int(getattr(usage, "prompt_tokens", 0) or
              getattr(usage, "input_tokens", 0) or 0)
    out = int(getattr(usage, "completion_tokens", 0) or
              getattr(usage, "output_tokens", 0) or 0)
    record(Entry(kind="text", provider=provider, model=model, stage=stage,
                 project=project, input_tokens=inp, output_tokens=out,
                 cost_usd=text_cost(model, inp, out), note=note))


def record_image(model: str, count: int, *, quality: str = "medium",
                 stage: str = "", project: str = "", note: str = "") -> None:
    record(Entry(kind="image", provider="openai", model=model, stage=stage,
                 project=project, images=count,
                 cost_usd=image_cost(model, count, quality), note=note))


# --------------------------------------------------------------------------- #
# Reading it back                                                              #
# --------------------------------------------------------------------------- #
def entries(since_days: int | None = None, project: str = "") -> list[dict]:
    if not LEDGER.is_file():
        return []
    cutoff = (datetime.now() - timedelta(days=since_days)) if since_days else None
    out = []
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if project and row.get("project") != project:
            continue
        if cutoff:
            try:
                if datetime.fromisoformat(row["ts"]) < cutoff:
                    continue
            except (KeyError, ValueError):
                pass
        out.append(row)
    return out


def total(since_days: int | None = None, project: str = "") -> float:
    return sum(r.get("cost_usd") or 0.0
               for r in entries(since_days=since_days, project=project))


def summary(since_days: int | None = None, project: str = "") -> dict:
    rows = entries(since_days=since_days, project=project)
    by_model: dict[str, dict] = {}
    by_stage: dict[str, float] = {}
    by_project: dict[str, float] = {}
    unpriced = 0

    for row in rows:
        cost = row.get("cost_usd")
        if cost is None:
            unpriced += 1
            cost = 0.0
        m = by_model.setdefault(row.get("model", "?"),
                                {"calls": 0, "in": 0, "out": 0,
                                 "images": 0, "cost": 0.0})
        m["calls"] += 1
        m["in"] += row.get("input_tokens", 0)
        m["out"] += row.get("output_tokens", 0)
        m["images"] += row.get("images", 0)
        m["cost"] += cost
        by_stage[row.get("stage") or "—"] = \
            by_stage.get(row.get("stage") or "—", 0.0) + cost
        by_project[row.get("project") or "—"] = \
            by_project.get(row.get("project") or "—", 0.0) + cost

    return {
        "calls": len(rows),
        "total_usd": round(sum(r.get("cost_usd") or 0.0 for r in rows), 4),
        "unpriced_calls": unpriced,
        "by_model": by_model,
        "by_stage": by_stage,
        "by_project": by_project,
        "ledger": str(LEDGER),
    }


# --------------------------------------------------------------------------- #
# The cap                                                                      #
# --------------------------------------------------------------------------- #
class BudgetExceeded(RuntimeError):
    pass


def budget_usd() -> float | None:
    raw = os.getenv("OPENAI_BUDGET_USD", "").strip()
    try:
        return float(raw) if raw else None
    except ValueError:
        return None


def check_budget(about_to_spend: float = 0.0) -> None:
    """Raise before a paid call if it would cross the configured cap."""
    cap = budget_usd()
    if cap is None:
        return
    spent = total()
    if spent + about_to_spend > cap:
        raise BudgetExceeded(
            f"OpenAI spend cap reached: ${spent:.2f} already recorded against a "
            f"${cap:.2f} limit (OPENAI_BUDGET_USD).\n"
            f"Raise the cap, or clear the ledger at {LEDGER}."
        )


def format_summary(data: dict) -> str:
    lines = [
        f"OpenAI spend — {data['calls']} call(s), "
        f"estimated ${data['total_usd']:.4f}",
        "",
    ]
    if data["by_model"]:
        lines.append("  by model")
        for model, m in sorted(data["by_model"].items(),
                               key=lambda kv: -kv[1]["cost"]):
            detail = (f"{m['in']:,} in / {m['out']:,} out tokens"
                      if m["in"] or m["out"] else f"{m['images']} image(s)")
            lines.append(f"    {model:<22} {m['calls']:>3} calls  "
                         f"${m['cost']:.4f}   {detail}")
    if data["by_stage"]:
        lines.append("")
        lines.append("  by stage")
        for stage, cost in sorted(data["by_stage"].items(), key=lambda kv: -kv[1]):
            lines.append(f"    {stage:<22} ${cost:.4f}")
    if data["by_project"] and len(data["by_project"]) > 1:
        lines.append("")
        lines.append("  by video")
        for name, cost in sorted(data["by_project"].items(), key=lambda kv: -kv[1]):
            lines.append(f"    {name:<22} ${cost:.4f}")
    if data["unpriced_calls"]:
        lines.append("")
        lines.append(f"  ⚠️  {data['unpriced_calls']} call(s) had no price entry — "
                     f"cost understated. Add the model to pricing.json.")
    cap = budget_usd()
    if cap:
        lines.append("")
        lines.append(f"  cap ${cap:.2f} (OPENAI_BUDGET_USD) — "
                     f"${max(cap - data['total_usd'], 0):.2f} left")
    lines.append("")
    lines.append("  Token and image counts are exact; dollar figures are")
    lines.append("  estimates from the local price table, not billed amounts.")
    return "\n".join(lines)
