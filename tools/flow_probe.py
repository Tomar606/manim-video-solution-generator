"""Exercise the browser bridge one verb at a time, without spending credits.

    .venv-tools/bin/python tools/flow_probe.py              # the whole free ladder
    .venv-tools/bin/python tools/flow_probe.py --step image # just one rung
    .venv-tools/bin/python tools/flow_probe.py --find-clear # hunt the ✕ selector
    .venv-tools/bin/python tools/flow_probe.py --generate   # SPENDS A CREDIT

WHY A SEPARATE TOOL AND NOT A TEST
----------------------------------
`test_veo_flow.py` covers everything that can be checked without Chrome, which
is most of the logic and none of the risk. What it cannot cover is the half that
only exists in a live Flow tab: whether the prompt box is still a Slate editor,
whether the reference control accepts more than one file, what the remove button
on a reference chip is called this week. Those are questions about somebody
else's SPA, they change without notice, and the only way to answer them is to
ask the page.

So this is a ladder rather than a test suite. Each rung is cheaper to fail than
the one above it, and every rung below `--generate` is free — no generation is
submitted, no credit is spent, and nothing is left behind in your project. Run
it top to bottom after Flow ships a redesign and the failing rung tells you
which line of `flow/selectors.json` to edit.

WHAT IT PUTS BACK
-----------------
The prompt box is emptied and attached images are cleared on the way out, even
when a rung fails. A probe that leaves a marker string in the editor is a probe
that gets submitted by accident with the next click.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.flow_bridge import FlowBridge, FlowError  # noqa: E402

# Watched while it runs, and half the value is seeing which rung hangs — but
# Python only line-buffers to a tty, so piping this anywhere would hide every
# line until it exited.
try:
    sys.stdout.reconfigure(line_buffering=True)
except AttributeError:
    pass

SELECTORS = ROOT / "flow" / "selectors.json"
MARKER = "flow-probe check — this text is not a prompt and was not submitted"

OK, BAD, WARN = "  ✅", "  ❌", "  ⚠ "
findings: list[str] = []


def note(kind: str, msg: str) -> None:
    print(f"{kind} {msg}")
    if kind is BAD:
        findings.append(msg)


def selectors() -> dict:
    return json.loads(SELECTORS.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- #
# The rungs. Each takes (bridge, selectors) and returns True when it is safe to
# keep climbing — a rung that fails usually makes every rung above it meaningless
# (there is no point testing the prompt box if no tab was found).
# --------------------------------------------------------------------------- #
def rung_connect(b: FlowBridge, sel: dict) -> bool:
    print("\n1. the extension and the tab")
    try:
        info = b.wait_for_worker(timeout=30)
    except FlowError as exc:
        note(BAD, str(exc))
        return False
    note(OK, "the extension answered")
    tab = info.get("tab")
    if not tab:
        note(BAD, "no Google Flow tab is open. Open your project in any tab — "
                  "it may stay in the background.")
        return False
    note(OK, f"flow tab: {tab}")
    if "/project/" not in tab:
        note(WARN, "that tab is not inside a project, so it has no prompt box. "
                   "Open the project itself.")
        return False
    b.call("attach", timeout=60)
    note(OK, "debugger attached (Chrome will show a banner on that tab)")
    return True


def rung_page(b: FlowBridge, sel: dict) -> bool:
    print("\n2. what the page looks like from in there")
    got = b.call("eval", expr="""
        return {
          title: document.title,
          focused: document.hasFocus(),
          slate: document.querySelectorAll('[data-slate-editor="true"]').length,
          editable: document.querySelectorAll('[contenteditable="true"]').length,
          textareas: document.querySelectorAll('textarea').length,
          fileInputs: document.querySelectorAll('input[type="file"]').length,
          buttons: document.querySelectorAll('button,[role="button"]').length,
        };
    """, timeout=60)["value"]
    for k, v in got.items():
        print(f"     {k}: {v}")
    # This is THE thing that makes a background tab work. If it reads false the
    # renderer never got focus emulation and Slate will silently drop input.
    if got.get("focused"):
        note(OK, "the renderer believes it has focus (Emulation.setFocusEmulationEnabled)")
    else:
        note(BAD, "document.hasFocus() is false — focus emulation did not take, "
                  "and Slate will drop the prompt without erroring. Check "
                  "`Emulation.setFocusEmulationEnabled` in background.js.")
    return True


def rung_prompt(b: FlowBridge, sel: dict) -> bool:
    print("\n3. the prompt box (types a marker, reads it back, empties it)")
    try:
        got = b.call("set_prompt", text=MARKER, selector=sel["prompt"], timeout=120)
    except FlowError as exc:
        note(BAD, f"{exc}\n     -> `prompt` in flow/selectors.json no longer "
                  f"matches. Inspect the box and prefer a data- attribute.")
        return False
    note(OK, f"text landed: {got.get('chars')} chars into {got.get('editor')}")

    back = b.call("eval", expr=f"""
        var el = document.querySelector({json.dumps(sel['prompt'])});
        return el ? (el.innerText || el.value || "") : null;
    """, timeout=60)["value"]
    if back and MARKER.split("—")[0].strip() in back:
        note(OK, "and reads back from the page as the same text")
    else:
        note(BAD, f"the editor holds something else: {str(back)[:80]!r}")
    return True


def rung_generate(b: FlowBridge, sel: dict) -> bool:
    """Find the Generate button. Deliberately does NOT click it."""
    print("\n4. the Generate button (found, not clicked)")
    if sel.get("generate_selector"):
        expr = f"var el = document.querySelector({json.dumps(sel['generate_selector'])});"
        what = sel["generate_selector"]
    else:
        want = json.dumps(str(sel["generate_text"]).lower())
        what = f"text={sel['generate_text']}"
        expr = f"""
          var want = {want}, best = null, bestLen = 1e9;
          for (const n of document.querySelectorAll('button,[role="button"],a')) {{
            if (n.offsetParent === null) continue;
            var t = ((n.innerText||"") + " " + (n.getAttribute('aria-label')||"")).trim().toLowerCase();
            if (t && t.indexOf(want) >= 0 && t.length < bestLen) {{ best = n; bestLen = t.length; }}
          }}
          var el = best;"""
    got = b.call("eval", expr=expr + """
        if (!el) return null;
        return {label: (el.innerText || el.getAttribute('aria-label') || "").trim().slice(0, 40),
                disabled: !!(el.disabled || el.getAttribute('aria-disabled') === 'true')};
    """, timeout=60)["value"]
    if not got:
        note(BAD, f"no Generate button matched {what} — fix `generate_text` or "
                  f"`generate_selector` in flow/selectors.json")
        return False
    note(OK, f"found: {got['label']!r}")
    if got["disabled"]:
        # Not a failure by itself: Flow disables Send until the box has text, and
        # rung 3 has just emptied it in some layouts. Worth saying, because a
        # disabled button at RUN time means the prompt did not land.
        note(WARN, "it is currently disabled — expected if the prompt box is "
                   "empty, a real problem if it stays disabled after a prompt "
                   "has landed")
    else:
        note(OK, "and it is enabled")
    return True


def rung_media(b: FlowBridge, sel: dict) -> bool:
    print("\n5. reading the clips already on the page")
    media = b.call("list_media", timeout=60).get("media", [])
    note(OK, f"{len(media)} clip media URL(s) visible")
    for m in media[:3]:
        print(f"     {m['key']}")
    if not media:
        note(WARN, "none found. Fine on an empty project; if this project HAS "
                   "clips, Flow has changed how it embeds media URLs and "
                   "`listMedia` in background.js needs looking at.")
    return True


def rung_image(b: FlowBridge, sel: dict, probe_png: Path) -> bool:
    """The rung that matters most, because it is the one nobody can predict."""
    print("\n6. the reference-image control")
    info = b.call("eval", expr=f"""
        var out = [];
        for (const el of document.querySelectorAll({json.dumps(sel['plate_input'])})) {{
          out.push({{accept: el.getAttribute('accept') || "",
                     multiple: el.multiple,
                     hidden: el.offsetParent === null}});
        }}
        return out;
    """, timeout=60)["value"]
    if not info:
        note(BAD, f"no file input matched {sel['plate_input']!r}. Flow often "
                  f"only mounts it once the reference panel has been opened — "
                  f"open that panel by hand in the tab and run this again.")
        return False
    for i, el in enumerate(info):
        print(f"     input {i}: accept={el['accept']!r} multiple={el['multiple']} "
              f"hidden={el['hidden']}")

    got = b.call("set_image", paths=[str(probe_png)],
                 selector=sel["plate_input"], timeout=120)
    note(OK, f"attached {probe_png.name}")

    # THE open question. Everything about how a sequence uploads its carry frame
    # and its textbook figure together depends on the answer.
    if got.get("multiple"):
        note(OK, "the control accepts MULTIPLE files — a sequenced clip can "
                 "carry its previous frame and the textbook figure together")
    else:
        note(WARN, "the control takes ONE file. src/veo_sequence.uploads() is "
                   "ordered for exactly this: the carry frame goes up and the "
                   "textbook figure is dropped, and the run says so per clip. "
                   "Worth knowing before you read a sequence's output.")
    print("     -> look at the tab now: did a reference image appear in the UI?")
    return True


def rung_clear(b: FlowBridge, sel: dict) -> bool:
    print("\n7. clearing an attached reference")
    got = b.call("clear_images", selector=sel["plate_input"],
                 clear_selector=sel.get("reference_clear"), timeout=120)
    if not got.get("knows_clear_button"):
        note(WARN, "`reference_clear` is null in flow/selectors.json, so only "
                   "the file input was emptied. Flow keeps its own state for "
                   "the chips it has drawn — run --find-clear to identify the "
                   "remove button, or a carry frame will ride along into the "
                   "clip after next.")
    else:
        note(OK, f"clicked {got.get('removed')} remove button(s)")
    print("     -> look at the tab: is the reference image GONE from the UI?")
    print("        if it is still there, the selector is wrong however this reads.")
    return True


# --------------------------------------------------------------------------- #
def find_clear(b: FlowBridge, sel: dict, probe_png: Path) -> None:
    """Identify the control that removes an attached reference image.

    Works by difference rather than by guessing: snapshot every visible control,
    attach an image, snapshot again. Whatever appeared is a candidate, and the
    remove button is essentially always among them because it cannot exist
    before there is something to remove.
    """
    snap = """
        var out = [];
        for (const el of document.querySelectorAll('button,[role="button"],[aria-label]')) {
          if (el.offsetParent === null) continue;
          out.push(JSON.stringify({
            tag: el.tagName.toLowerCase(),
            label: (el.getAttribute('aria-label') || "").slice(0, 60),
            text: (el.innerText || "").trim().slice(0, 30),
            title: (el.getAttribute('title') || "").slice(0, 40),
            testid: el.getAttribute('data-testid') || ""
          }));
        }
        return out;
    """
    print("\nfinding the remove button")
    print("  clearing anything already attached…")
    b.call("clear_images", selector=sel["plate_input"],
           clear_selector=sel.get("reference_clear"), timeout=120)
    time.sleep(1.0)

    before = set(b.call("eval", expr=snap, timeout=60)["value"])
    print(f"  {len(before)} controls visible before")

    b.call("set_image", paths=[str(probe_png)], selector=sel["plate_input"],
           timeout=120)
    print("  attached the probe image; waiting for Flow to render the chip…")
    time.sleep(2.5)

    after = b.call("eval", expr=snap, timeout=60)["value"]
    fresh = [json.loads(x) for x in after if x not in before]
    if not fresh:
        print("\n  Nothing new appeared. Either the image did not attach (check "
              "the tab), or Flow renders the remove control only on hover — in "
              "which case hover the chip yourself and read the ✕ off DevTools.")
        return

    print(f"\n  {len(fresh)} control(s) appeared. The remove button is almost "
          f"certainly one of these:\n")
    for c in fresh:
        bits = [f"<{c['tag']}>"]
        if c["label"]:
            bits.append(f"aria-label={c['label']!r}")
        if c["text"]:
            bits.append(f"text={c['text']!r}")
        if c["title"]:
            bits.append(f"title={c['title']!r}")
        if c["testid"]:
            bits.append(f"data-testid={c['testid']!r}")
        print("    " + "  ".join(bits))
        # Suggested in the order flow/selectors.json asks for: a data- attribute,
        # then an aria-label, and never a hashed class.
        if c["testid"]:
            print(f'      -> "reference_clear": "[data-testid=\\"{c["testid"]}\\"]"')
        elif c["label"]:
            print(f'      -> "reference_clear": "[aria-label=\\"{c["label"]}\\"]"')
    print("\n  Put the right one in flow/selectors.json, then re-run "
          "`--step clear` and WATCH THE TAB: the only proof that works is the "
          "reference image disappearing from the UI.")


# --------------------------------------------------------------------------- #
def make_probe_png(dest: Path) -> Path:
    """A small, obviously-artificial image, so it is unmistakable in the UI."""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        # Any real file will do for testing the plumbing; a plate is guaranteed
        # to be here and is a valid PNG.
        return ROOT / "assets" / "backgrounds" / "chemistry.png"
    im = Image.new("RGB", (480, 480), "#ff00ff")
    d = ImageDraw.Draw(im)
    d.rectangle([40, 40, 440, 440], outline="black", width=12)
    d.line([40, 40, 440, 440], fill="black", width=12)
    d.line([440, 40, 40, 440], fill="black", width=12)
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest)
    return dest


STEPS = ("connect", "page", "prompt", "generate", "media", "image", "clear")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--step", choices=STEPS,
                    help="run one rung instead of the ladder (connect always runs)")
    ap.add_argument("--find-clear", action="store_true",
                    help="identify the button that removes an attached reference")
    ap.add_argument("--generate", action="store_true",
                    help="SPENDS A CREDIT: submit the prompt currently in the box")
    ap.add_argument("--port", type=int, default=8765)
    args = ap.parse_args()

    sel = selectors()
    probe_png = make_probe_png(ROOT / "out" / "flow_probe.png")
    b = FlowBridge(args.port).start()
    connected = False
    try:
        if not rung_connect(b, sel):
            return 1
        connected = True

        if args.find_clear:
            find_clear(b, sel, probe_png)
            return 0

        wanted = [args.step] if args.step else list(STEPS)
        for name in wanted:
            if name == "connect":
                continue
            fn = {"page": rung_page, "prompt": rung_prompt,
                  "generate": rung_generate, "media": rung_media,
                  "clear": rung_clear}.get(name)
            try:
                if name == "image":
                    rung_image(b, sel, probe_png)
                elif fn and not fn(b, sel):
                    break
            except FlowError as exc:
                note(BAD, f"{name}: {exc}")
                break

        if args.generate:
            print("\n8. submitting — THIS SPENDS A CREDIT")
            b.call("set_prompt", text=MARKER, selector=sel["prompt"], timeout=120)
            before = {m["key"] for m in b.call("list_media", timeout=60)["media"]}
            if sel.get("generate_selector"):
                b.call("click", selector=sel["generate_selector"], timeout=60)
            else:
                b.call("click", text=sel["generate_text"], timeout=60)
            note(OK, "submitted; waiting up to 5 minutes for a new media key")
            deadline = time.time() + 300
            while time.time() < deadline:
                new = {m["key"] for m in b.call("list_media", timeout=60)["media"]} - before
                if new:
                    note(OK, f"Flow produced {sorted(new)[0]}")
                    break
                time.sleep(10)
            else:
                note(BAD, "nothing appeared in 5 minutes — check the tab for a "
                          "quota or safety error, which never emits a media URL")
    finally:
        # Tidy up after any rung that ran, because a marker string left in the
        # editor is a marker string that gets submitted with somebody's next
        # click. But only if we ever reached the page: with no worker answering,
        # each of these blocks for its full timeout, and the connect failure —
        # the likeliest one, and the one you want answered fastest — would take
        # minutes to report.
        if connected:
            print("\nputting the page back")
            for cmd, kw in (("set_prompt", {"text": "", "selector": sel["prompt"]}),
                            ("clear_images", {"selector": sel["plate_input"],
                                              "clear_selector": sel.get("reference_clear")}),
                            ("detach", {})):
                try:
                    b.call(cmd, timeout=20, **kw)
                except FlowError as exc:
                    print(f"{WARN} could not {cmd}: {str(exc)[:90]}")
        b.stop()

    print()
    if findings:
        print(f"{len(findings)} problem(s):")
        for f in findings:
            print(f"  - {f}")
        return 1
    print("every rung passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
