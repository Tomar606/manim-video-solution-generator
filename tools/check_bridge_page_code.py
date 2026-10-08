"""Syntax-check the JavaScript the bridge sends INTO the page.

    python tools/check_bridge_page_code.py [flow/extension/background.js]

`node --check background.js` proves the EXTENSION parses. It says nothing about
the code inside the template literals that `evaluate()` ships to the page --
that is a string as far as the extension is concerned, and a broken one loads
and runs perfectly until the moment it is used.

THE BUG THIS EXISTS FOR
-----------------------
A template literal resolves its own escapes before anyone else sees them. So

    v.match(/\\/asb\\/([A-Za-z0-9_-]{12,})/)      written with ONE backslash

arrives at the page as

    v.match(//asb/([A-Za-z0-9_-]{12,})/)

where `//` opens a line comment that swallows the rest of the statement. The
page answers `SyntaxError: Unexpected token 'var'`, which reads like a Flow
redesign rather than like an escaping slip, and the fix shipped in build 9 and
was never once executed. A stray backtick inside a comment does the same thing
more bluntly: it ends the literal outright.

HOW IT CHECKS
-------------
Each `evaluate(` template is extracted, its escapes resolved exactly as JS
would, and the result is handed to `node --check` wrapped the way `evaluate()`
wraps it -- inside `(function(){ ... })()`. That is the same text the page gets.

A template carrying `${...}` is checked with each interpolation replaced by a
string literal: the point is the surrounding code, and the interpolated values
are already JSON.stringify'd at the call sites.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "flow/extension/background.js"


# Where page code is written. `evaluate(`...`)` is the common case; a helper
# that BUILDS an expression and hands it to evaluate() as a variable is the
# other, and it is invisible to a search for the call site — so any `return `
# template that touches the document is checked too.


def templates(src: str) -> list[tuple[int, str]]:
    """Every template literal holding page code, as (line number, raw contents).

    Scanned by hand rather than by regex: the contents contain backslashes,
    braces and quotes, and a regex that copes with those is harder to trust
    than a cursor.
    """
    out = []
    for opener in ("evaluate(`", "return `"):
        out += _scan(src, opener)
    return sorted(out)


def _scan(src: str, opener: str) -> list[tuple[int, str]]:
    out, i = [], 0
    while True:
        i = src.find(opener, i)
        if i < 0:
            return out
        start = i + len(opener)
        j, depth = start, 0
        while j < len(src):
            c = src[j]
            if c == "\\":
                j += 2
                continue
            if c == "$" and src[j + 1:j + 2] == "{":
                depth += 1
                j += 2
                continue
            if c == "}" and depth:
                depth -= 1
            elif c == "`" and not depth:
                break
            j += 1
        body = src[start:j]
        # A `return `...`` that is not page code — a message, a path — has no
        # business being syntax-checked as JavaScript. Page code always touches
        # the document or returns a value.
        if opener != "evaluate(`" and "document." not in body and "return " not in body:
            i = j + 1
            continue
        out.append((src.count("\n", 0, start) + 1, body))
        i = j + 1


ESCAPES = {"n": "\n", "t": "\t", "r": "\r", "`": "`", "\\": "\\", "$": "$"}


def resolve(raw: str) -> str:
    """What the page receives: template escapes applied, `${...}` stubbed.

    An unrecognised escape resolves to the character itself, which is the whole
    trap -- backslash-slash becomes slash.
    """
    out, i = [], 0
    while i < len(raw):
        c = raw[i]
        if c == "\\" and i + 1 < len(raw):
            nxt = raw[i + 1]
            out.append(ESCAPES.get(nxt, nxt))
            i += 2
            continue
        if c == "$" and raw[i + 1:i + 2] == "{":
            depth, j = 1, i + 2
            while j < len(raw) and depth:
                depth += (raw[j] == "{") - (raw[j] == "}")
                j += 1
            out.append('"__interpolated__"')
            i = j
            continue
        out.append(c)
        i += 1
    return "".join(out)


PY_SENDERS = (ROOT / "src/veo.py",)      # Python that ships JS via expr="..."


def python_page_code(path: Path) -> list[tuple[int, str]]:
    """JS passed from Python as `expr=` — the other half of the same hazard.

    A page-code string written in Python goes through a Python quote AND a JS
    parser before the page sees it, so it has one more chance to be mangled than
    the extension's own templates do. It has been mangled: a `.replace(/\n/g,' ')`
    written in a non-raw heredoc reached the page as a literal newline INSIDE a
    regex literal, and Flow answered "Invalid regular expression: missing /".
    Python has already applied its escapes by the time we read the file, so what
    is in the AST node is exactly what the page gets — no resolve() step needed.
    """
    import ast
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.keyword) or node.arg != "expr":
            continue
        v = node.value
        if isinstance(v, ast.Constant) and isinstance(v.value, str):
            if "document." in v.value or "return " in v.value:
                out.append((v.lineno, v.value))
    return out


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    src = path.read_text(encoding="utf-8")
    found = templates(src)
    if not found:
        print(f"  no evaluate() templates in {path} — has the helper been renamed?")
        return 1

    # Python page code is checked verbatim; the extension's is checked after the
    # template escapes are resolved. Flagged so the two cannot be confused.
    jobs = [(path.name, line, resolve(raw)) for line, raw in found]
    if len(sys.argv) <= 1:
        for f in PY_SENDERS:
            jobs += [(f.name, line, code) for line, code in python_page_code(f)]

    bad = []
    with tempfile.TemporaryDirectory() as td:
        for who, line, page in jobs:
            f = Path(td) / f"page_{who}_{line}.js"
            # Wrapped exactly as evaluate() wraps it, or a bare `return` at the
            # top level is a syntax error here and legal there.
            f.write_text("(function(){" + page + "})()", encoding="utf-8")
            r = subprocess.run(["node", "--check", str(f)],
                               capture_output=True, text=True)
            if r.returncode:
                why = (r.stderr.strip().splitlines() or ["?"])
                why = next((l for l in why if "Error" in l), why[0])
                bad.append((f"{who}:{line}", why.strip()))
            else:
                print(f"  {who}:{line}  page code ok ({len(page)} chars)")

    if bad:
        print("BRIDGE PAGE CODE FAILED:")
        for where, why in bad:
            print(f"  {where} — {why}")
            print("     the extension parses; the code it SENDS does not. Check "
                  "for a single backslash or a backtick inside the template.")
        return 1
    print(f"  bridge page code ok — {len(jobs)} block(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
