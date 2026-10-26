"""Claude access layer with two interchangeable backends.

Everything LLM-facing in the pipeline goes through here, so model choice,
effort, vision and multi-turn repair loops are configured in exactly one place.

Backends
--------
``cli``     — shells out to the Claude Code CLI (``claude -p``). Billed to the
              user's Claude subscription (Max), so no ANTHROPIC_API_KEY is
              needed. Multi-turn conversations use ``--resume <session_id>``,
              which keeps the server-side prompt cache warm across repair
              attempts.
``api``     — the Anthropic SDK. Pay-per-token, but fully unattended (no CLI
              login), which is what you want in CI or on a build server.
``openai``  — the OpenAI SDK, for the stages where the team prefers it.

Selection is ``LLM_BACKEND=auto|cli|api|openai`` (default ``auto``): prefer the
Claude CLI when it's installed and logged in, otherwise the Anthropic key,
otherwise OpenAI. Individual callers can override per call with
``provider=``, which is how script writing runs on OpenAI while Manim codegen
and QC stay on Claude.

All backends expose the same three entry points — :func:`complete`,
:func:`complete_json` and :func:`new_conversation` — so callers never branch on
which one is active.
"""
from __future__ import annotations

import base64
import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_env_loaded = False


def _ensure_env() -> None:
    """Load .env once, whatever imported us.

    This runs at import time, *before* the defaults below are read: they are
    module-level `os.getenv` calls, so a later load would be too late and
    OPENAI_MODEL from .env would be silently ignored.
    """
    global _env_loaded
    if _env_loaded:
        return
    _env_loaded = True
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ModuleNotFoundError:
        pass


_ensure_env()

# Claude Opus 5. Adaptive thinking is on by default on this model; depth is
# controlled with output_config.effort rather than a token budget.
DEFAULT_MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-5")
DEFAULT_EFFORT = os.getenv("CLAUDE_EFFORT", "high")

# OpenAI model IDs move faster than this file does, so the default is an env
# var rather than a constant baked into the code. Set OPENAI_MODEL in .env.
DEFAULT_OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1")

# Codegen at high effort can think for a while; give it room before we call it.
CLI_TIMEOUT = int(os.getenv("CLAUDE_CLI_TIMEOUT", "900"))

_IMAGE_MEDIA_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
}


class LLMError(RuntimeError):
    """Raised when a completion cannot be produced (auth, timeout, refusal)."""


# --------------------------------------------------------------------------- #
# Backend selection                                                            #
# --------------------------------------------------------------------------- #
def cli_available() -> bool:
    _ensure_env()
    return shutil.which("claude") is not None


def api_available() -> bool:
    _ensure_env()
    if not os.getenv("ANTHROPIC_API_KEY"):
        return False
    try:
        import anthropic  # noqa: F401
    except ModuleNotFoundError:
        return False
    return True


def openai_available() -> bool:
    _ensure_env()
    if not os.getenv("OPENAI_API_KEY"):
        return False
    try:
        import openai  # noqa: F401
    except ModuleNotFoundError:
        return False
    return True


def resolve_provider(provider: str | None) -> str:
    """Turn a caller's provider preference into a concrete backend.

    ``None``/``"auto"`` defers to LLM_BACKEND; anything else is honoured
    explicitly so one stage can run on OpenAI while the rest stay on Claude.
    """
    choice = (provider or "auto").strip().lower()
    if choice in ("", "auto"):
        return active_backend()
    if choice in ("openai", "gpt"):
        if not openai_available():
            raise LLMError(
                "OpenAI was requested but is not usable.\n"
                "  Set OPENAI_API_KEY in .env, and install the SDK: "
                "pip install openai"
            )
        return "openai"
    if choice in ("claude", "anthropic"):
        return active_backend()
    if choice in ("cli", "api"):
        return choice
    raise LLMError(f"Unknown provider {provider!r}.")


def active_backend() -> str:
    """Return the default backend, honouring LLM_BACKEND."""
    choice = (os.getenv("LLM_BACKEND") or "auto").strip().lower()
    if choice == "openai":
        if not openai_available():
            raise LLMError(
                "LLM_BACKEND=openai but OPENAI_API_KEY is unset or the "
                "`openai` package is not installed."
            )
        return "openai"
    if choice == "cli":
        if not cli_available():
            raise LLMError(
                "LLM_BACKEND=cli but the `claude` CLI is not on PATH.\n"
                "Install it (npm i -g @anthropic-ai/claude-code) and run "
                "`claude` once to log in."
            )
        return "cli"
    if choice == "api":
        if not api_available():
            raise LLMError(
                "LLM_BACKEND=api but ANTHROPIC_API_KEY is unset or the "
                "`anthropic` package is not installed."
            )
        return "api"
    if choice not in ("auto", ""):
        raise LLMError(
            f"Unknown LLM_BACKEND={choice!r}. Use auto, cli, api or openai."
        )

    if cli_available():
        return "cli"
    if api_available():
        return "api"
    if openai_available():
        return "openai"
    raise LLMError(
        "No model access configured.\n"
        "  Option A (Claude subscription): install the Claude Code CLI and run "
        "`claude` once to log in.\n"
        "  Option B (Anthropic key): set ANTHROPIC_API_KEY in .env.\n"
        "  Option C (OpenAI key): set OPENAI_API_KEY in .env."
    )


def describe_backend() -> str:
    """Human-readable backend summary for `doctor` and startup banners."""
    try:
        backend = active_backend()
    except LLMError as exc:
        return f"unavailable ({exc.args[0].splitlines()[0]})"
    if backend == "cli":
        return f"claude CLI (subscription) · model={DEFAULT_MODEL}"
    if backend == "openai":
        return f"OpenAI (OPENAI_API_KEY) · model={DEFAULT_OPENAI_MODEL}"
    return f"Anthropic API (ANTHROPIC_API_KEY) · model={DEFAULT_MODEL}"


# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #
def _media_type(path: str) -> str:
    ext = Path(path).suffix.lower()
    if ext not in _IMAGE_MEDIA_TYPES:
        raise LLMError(f"Unsupported image type for vision: {path}")
    return _IMAGE_MEDIA_TYPES[ext]


def strip_fences(text: str) -> str:
    """Remove a wrapping ``` fence if the model added one anyway."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z0-9_-]*\n", "", text)
        text = re.sub(r"\n```$", "", text)
    return text.strip()


def extract_json(text: str) -> Any:
    """Pull the first complete JSON value out of a model response.

    The API backend gets schema-validated JSON for free; the CLI backend
    returns prose-capable text, so we locate the JSON payload ourselves.
    """
    cleaned = strip_fences(text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    # Scan for the first balanced {...} or [...] block.
    for opener, closer in (("{", "}"), ("[", "]")):
        start = cleaned.find(opener)
        if start == -1:
            continue
        depth = 0
        in_str = False
        escape = False
        for i in range(start, len(cleaned)):
            ch = cleaned[i]
            if in_str:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_str = False
                continue
            if ch == '"':
                in_str = True
            elif ch == opener:
                depth += 1
            elif ch == closer:
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(cleaned[start:i + 1])
                    except json.JSONDecodeError:
                        break
    raise LLMError(f"Model response did not contain valid JSON:\n{cleaned[:600]}")


# --------------------------------------------------------------------------- #
# Conversation — one multi-turn exchange, backend-agnostic                     #
# --------------------------------------------------------------------------- #
@dataclass
class Conversation:
    """A running exchange with Claude.

    ``send`` returns the assistant's text and remembers the turn, so repair
    loops can simply call it again with the error output. The CLI backend
    resumes its session id; the API backend replays the message array.
    """

    system: str
    model: str = DEFAULT_MODEL
    effort: str = DEFAULT_EFFORT
    backend: str = field(default_factory=active_backend)

    _session_id: str | None = field(default=None, init=False, repr=False)
    _messages: list[dict[str, Any]] = field(default_factory=list, init=False, repr=False)

    def send(self, prompt: str, *, images: list[str] | None = None) -> str:
        if self.backend == "cli":
            return self._send_cli(prompt, images or [])
        if self.backend == "openai":
            return self._send_openai(prompt, images or [])
        return self._send_api(prompt, images or [])

    # -- OpenAI ------------------------------------------------------------- #
    def _send_openai(self, prompt: str, images: list[str]) -> str:
        import openai

        content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
        for path in images:
            data = base64.standard_b64encode(Path(path).read_bytes()).decode()
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:{_media_type(path)};base64,{data}"},
            })

        if not self._messages:
            self._messages.append({"role": "system", "content": self.system})
        # Plain text stays a string: some models reject a single-element content
        # array, and every model accepts the string form.
        self._messages.append({
            "role": "user",
            "content": prompt if not images else content,
        })

        from src import usage

        client = _openai_client()
        model = self.model if self.model.startswith("gpt") or "/" in self.model \
            else DEFAULT_OPENAI_MODEL

        # Checked before the call: a cap you notice afterwards isn't a cap.
        usage.check_budget()
        try:
            response = client.chat.completions.create(
                model=model,
                messages=self._messages,
            )
        except openai.APIStatusError as exc:
            raise LLMError(
                f"OpenAI API error ({exc.status_code}): {exc}"
            ) from exc
        except openai.APIConnectionError as exc:
            raise LLMError(f"Could not reach OpenAI: {exc}") from exc

        if getattr(response, "usage", None):
            usage.record_text(model, response.usage)

        choice = response.choices[0]
        text = (choice.message.content or "").strip()
        if not text:
            raise LLMError(
                f"OpenAI returned no text (finish_reason="
                f"{choice.finish_reason!r})."
            )
        self._messages.append({"role": "assistant", "content": text})
        return text

    # -- CLI ---------------------------------------------------------------- #
    def _send_cli(self, prompt: str, images: list[str]) -> str:
        cmd = [
            "claude", "-p",
            "--output-format", "json",
            "--model", self.model,
            "--effort", self.effort,
            "--strict-mcp-config",       # ignore the user's MCP servers
            "--disable-slash-commands",  # and their skills
        ]
        if self._session_id:
            cmd += ["--resume", self._session_id]
        else:
            # --system-prompt replaces Claude Code's default agent prompt, so
            # the model is a pure generator rather than a coding agent.
            cmd += ["--system-prompt", self.system]

        if images:
            # Vision via the CLI: the model reads the files itself.
            dirs = sorted({str(Path(p).resolve().parent) for p in images})
            cmd += ["--max-turns", "12", "--allowed-tools", "Read"]
            for d in dirs:
                cmd += ["--add-dir", d]
            listing = "\n".join(f"- {Path(p).resolve()}" for p in images)
            prompt = (
                f"{prompt}\n\nRead these image files before answering "
                f"(use the Read tool on each):\n{listing}"
            )
        else:
            # No tools at all: pure text generation. The turn budget is not 1,
            # though — the model sometimes still reaches for a tool, and with a
            # single turn that denial ends the run with `error_max_turns` and no
            # text at all. A few spare turns let it recover and answer.
            cmd += ["--max-turns", "6", "--allowed-tools", ""]

        try:
            proc = subprocess.run(
                cmd, input=prompt, capture_output=True, text=True,
                timeout=CLI_TIMEOUT,
            )
        except subprocess.TimeoutExpired as exc:
            raise LLMError(f"claude CLI timed out after {CLI_TIMEOUT}s") from exc
        except FileNotFoundError as exc:
            raise LLMError("`claude` CLI not found on PATH.") from exc

        if proc.returncode != 0:
            raise LLMError(
                f"claude CLI failed (exit {proc.returncode}):\n"
                f"{(proc.stderr or proc.stdout)[-2000:]}"
            )
        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:
            raise LLMError(
                f"claude CLI returned non-JSON output:\n{proc.stdout[:1000]}"
            ) from exc

        if payload.get("is_error"):
            raise LLMError(
                f"claude CLI reported an error: {payload.get('result') or payload}"
            )
        self._session_id = payload.get("session_id") or self._session_id
        text = (payload.get("result") or "").strip()
        if not text:
            raise LLMError("claude CLI returned an empty result.")
        return text

    # -- API ---------------------------------------------------------------- #
    def _send_api(self, prompt: str, images: list[str]) -> str:
        import anthropic

        content: list[dict[str, Any]] = []
        for path in images:
            data = base64.standard_b64encode(Path(path).read_bytes()).decode()
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": _media_type(path),
                    "data": data,
                },
            })
        content.append({"type": "text", "text": prompt})
        self._messages.append({"role": "user", "content": content})

        client = _api_client()
        try:
            # Streaming keeps long codegen responses under the HTTP timeout.
            with client.messages.stream(
                model=self.model,
                max_tokens=32000,
                system=self.system,
                messages=self._messages,
                output_config={"effort": self.effort},
                thinking={"type": "adaptive"},
            ) as stream:
                message = stream.get_final_message()
        except anthropic.APIStatusError as exc:
            raise LLMError(f"Anthropic API error ({exc.status_code}): {exc}") from exc
        except anthropic.APIConnectionError as exc:
            raise LLMError(f"Could not reach the Anthropic API: {exc}") from exc

        if message.stop_reason == "refusal":
            raise LLMError(
                "Claude declined this request "
                f"({getattr(message.stop_details, 'category', 'unspecified')})."
            )

        self._messages.append({"role": "assistant", "content": message.content})
        text = "".join(b.text for b in message.content if b.type == "text").strip()
        if not text:
            raise LLMError("Anthropic API returned an empty response.")
        return text


_client = None
_oai_client = None


def _api_client():
    global _client
    if _client is None:
        _ensure_env()
        import anthropic
        _client = anthropic.Anthropic()
    return _client


def _openai_client():
    global _oai_client
    if _oai_client is None:
        _ensure_env()
        import openai
        # Reads OPENAI_API_KEY (and OPENAI_BASE_URL, if you front it with a
        # gateway) from the environment.
        _oai_client = openai.OpenAI()
    return _oai_client


# --------------------------------------------------------------------------- #
# Convenience entry points                                                     #
# --------------------------------------------------------------------------- #
def new_conversation(system: str, *, effort: str = DEFAULT_EFFORT,
                     model: str | None = None,
                     provider: str | None = None) -> Conversation:
    backend = resolve_provider(provider)
    default_model = DEFAULT_OPENAI_MODEL if backend == "openai" else DEFAULT_MODEL
    return Conversation(system=system, model=model or default_model,
                        effort=effort, backend=backend)


def complete(system: str, prompt: str, *, effort: str = DEFAULT_EFFORT,
             images: list[str] | None = None, model: str | None = None,
             provider: str | None = None) -> str:
    """One-shot text completion."""
    return new_conversation(system, effort=effort, model=model,
                            provider=provider).send(prompt, images=images)


def complete_json(system: str, prompt: str, schema_model, *,
                  effort: str = DEFAULT_EFFORT, images: list[str] | None = None,
                  model: str | None = None, provider: str | None = None):
    """Structured output validated against a pydantic model.

    The API backend uses ``messages.parse`` (schema-enforced). The CLI backend
    asks for JSON in the system prompt and validates the response locally, so
    both paths return the same validated object.
    """
    backend = resolve_provider(provider)
    if backend == "api" and not images:
        import anthropic
        client = _api_client()
        try:
            resp = client.messages.parse(
                model=model or DEFAULT_MODEL,
                max_tokens=16000,
                system=system,
                messages=[{"role": "user", "content": prompt}],
                output_config={"effort": effort},
                output_format=schema_model,
            )
        except anthropic.APIStatusError as exc:
            raise LLMError(f"Anthropic API error ({exc.status_code}): {exc}") from exc
        return resp.parsed_output

    schema = json.dumps(schema_model.model_json_schema(), indent=2)
    json_system = (
        f"{system}\n\n"
        "Respond with a single JSON object and nothing else — no prose, no "
        "markdown fences. It must validate against this JSON Schema:\n"
        f"{schema}"
    )
    raw = complete(json_system, prompt, effort=effort, images=images, model=model)
    return schema_model.model_validate(extract_json(raw))
