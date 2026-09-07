"""The local half of the Flow bridge: Python drives, the extension obeys.

WHY PYTHON IS THE DRIVER
-----------------------
The upstream flow-bridge put the run loop in the browser and had Python serve it
a list of prompts. That inverts badly here: our loop is not "fill N boxes", it is
"submit, wait, download, look at the frames, decide whether the animation is
actually right, rewrite the prompt, go again". None of that belongs in a service
worker, and none of it can be tested without a browser if it lives there.

So this module owns the loop and the extension is reduced to a remote with seven
verbs (`ping`, `attach`, `eval`, `set_prompt`, `set_image`, `click`,
`list_media`, `download`). Each is small enough to be obviously correct, which
matters because the browser half is the part we cannot unit-test.

HOW A COMMAND TRAVELS
---------------------
    call()  ->  _pending queue  ->  GET /job (worker long-polls)
                                        |
                                    worker runs it
                                        v
    call() returns  <-  _results  <-  POST /event

`GET /job` blocks for up to LONGPOLL seconds and then answers 204, so an idle
worker costs one request every 25 seconds and a queued command starts within
milliseconds.

WHAT THIS DELIBERATELY DOES NOT DO
----------------------------------
No websockets, so no dependency. No CORS wildcard on anything that mutates: the
only endpoint a web page may read is `/status`, and it is read-only. `/job` and
`/event` are for the extension, which is exempt from CORS through its own
host_permissions.
"""
from __future__ import annotations

import json
import os
import queue
import threading
import time
import uuid
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PORT = int(os.environ.get("FLOW_BRIDGE_PORT", "8765"))
EXPECTED_BUILD = 8       # must match BRIDGE_BUILD in flow/extension/background.js
LONGPOLL = 25.0          # seconds a /job request parks before answering 204
DOWNLOAD_DIR = Path(os.environ.get(
    "FLOW_DOWNLOAD_DIR", str(Path.home() / "Downloads"))).expanduser()
INBOX_NAME = "pyq_flow_inbox"       # a subfolder of DOWNLOAD_DIR, per Chrome's rules


class FlowError(RuntimeError):
    """The extension reported a failure, or never answered."""


class StaleExtension(FlowError):
    """The extension answered, but it is not the build this code was written
    against. Deliberately a distinct type: `wait_for_worker` retries FlowError,
    and retrying this one only delays the report."""


@dataclass
class _Cmd:
    id: str
    body: dict
    done: threading.Event = field(default_factory=threading.Event)
    result: dict | None = None
    error: str | None = None


class FlowBridge:
    """Serves commands to the extension and collects their results."""

    def __init__(self, port: int = PORT):
        self.port = port
        self._pending: queue.Queue[_Cmd] = queue.Queue()
        self._inflight: dict[str, _Cmd] = {}
        self._lock = threading.Lock()
        self._httpd: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None
        self.worker_seen: float | None = None
        self.status: dict = {"run": None, "scene": None, "stage": "idle", "detail": ""}

    # ------------------------------------------------------------ lifecycle --
    def start(self) -> "FlowBridge":
        bridge = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, *a):          # quiet; the pipeline prints its own
                pass

            def _send(self, code: int, payload=None, *, cors=False):
                body = b"" if payload is None else json.dumps(payload).encode()
                self.send_response(code)
                if payload is not None:
                    self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                if cors:
                    # Only /status is readable from a page, and only for the
                    # on-page panel. Chrome's private-network check needs the
                    # third header or the fetch is blocked before it is sent.
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.send_header("Access-Control-Allow-Methods", "GET,OPTIONS")
                    self.send_header("Access-Control-Allow-Private-Network", "true")
                self.end_headers()
                if body:
                    self.wfile.write(body)

            def do_OPTIONS(self):
                self._send(204, cors=True)

            def do_GET(self):
                if self.path.startswith("/job"):
                    bridge.worker_seen = time.time()
                    try:
                        cmd = bridge._pending.get(timeout=LONGPOLL)
                    except queue.Empty:
                        self._send(204)
                        return
                    self._send(200, dict(cmd.body, id=cmd.id))
                elif self.path.startswith("/status"):
                    ago = (None if bridge.worker_seen is None
                           else time.time() - bridge.worker_seen)
                    self._send(200, dict(bridge.status, worker_seen_ago=ago), cors=True)
                else:
                    self._send(200, {"ok": True, "service": "pyq-flow-bridge"})

            def do_POST(self):
                n = int(self.headers.get("Content-Length", 0) or 0)
                raw = self.rfile.read(n) if n else b"{}"
                if self.path.startswith("/event"):
                    bridge.worker_seen = time.time()
                    try:
                        msg = json.loads(raw)
                    except ValueError:
                        self._send(400, {"ok": False})
                        return
                    with bridge._lock:
                        cmd = bridge._inflight.pop(msg.get("id"), None)
                    if cmd is not None:
                        if msg.get("ok"):
                            cmd.result = msg.get("data") or {}
                        else:
                            cmd.error = msg.get("error") or "unknown extension error"
                        cmd.done.set()
                self._send(200, {"ok": True})

        class QuietServer(ThreadingHTTPServer):
            """Same server, without the traceback for a dropped long poll.

            The extension parks a GET /job for 25 seconds at a time, so its
            connection is routinely still open when the service worker is
            recycled or the tab is reloaded — and every one of those prints a
            full ConnectionResetError traceback to stderr. Nothing is wrong and
            nothing is lost: the worker reconnects on its next poll. But the
            tracebacks land in the middle of a run's progress output and read
            exactly like a crash, which is worse than useless during a stage
            that legitimately takes twenty minutes.
            """

            def handle_error(self, request, client_address):
                import sys as _sys
                exc = _sys.exc_info()[1]
                if isinstance(exc, (ConnectionResetError, BrokenPipeError,
                                    ConnectionAbortedError)):
                    return
                super().handle_error(request, client_address)

        self._httpd = QuietServer(("127.0.0.1", self.port), Handler)
        self._httpd.daemon_threads = True
        self._thread = threading.Thread(target=self._httpd.serve_forever,
                                        name="flow-bridge", daemon=True)
        self._thread.start()
        return self

    def stop(self) -> None:
        if self._httpd is not None:
            self._httpd.shutdown()
            self._httpd.server_close()
            self._httpd = None

    def __enter__(self):
        return self.start()

    def __exit__(self, *exc):
        self.stop()

    # -------------------------------------------------------------- driving --
    def call(self, cmd: str, *, timeout: float = 180.0, **kw) -> dict:
        """Queue one command and block until the extension answers."""
        c = _Cmd(id=uuid.uuid4().hex[:12], body=dict(kw, cmd=cmd))
        with self._lock:
            self._inflight[c.id] = c
        self._pending.put(c)
        if not c.done.wait(timeout):
            with self._lock:
                self._inflight.pop(c.id, None)
            raise FlowError(
                f"'{cmd}' timed out after {timeout:.0f}s with no answer from the "
                f"extension. Is Chrome running with the PYQ Flow Bridge loaded, "
                f"and is a Google Flow tab open?")
        if c.error:
            raise FlowError(f"{cmd}: {c.error}")
        return c.result or {}

    def wait_for_worker(self, timeout: float = 60.0) -> dict:
        """Block until the extension answers a ping, then report the Flow tab.

        Also checks the build. An unpacked extension has no hot reload, and a
        stale one does not announce itself — it fails later, somewhere else,
        looking exactly like Flow having changed its UI. Saying so here costs
        one comparison and has already saved two wrong investigations.
        """
        deadline = time.time() + timeout
        last: Exception | None = None
        while time.time() < deadline:
            try:
                info = self.call("ping", timeout=min(20.0, deadline - time.time()))
            except FlowError as e:
                last = e
                continue
            # OUTSIDE the retry. A build mismatch is not a transient failure and
            # retrying it just burns the timeout before reporting the one thing
            # that was actually wrong.
            got = info.get("build")
            if got != EXPECTED_BUILD:
                raise StaleExtension(
                    f"the loaded extension is build {got!r} but this code expects "
                    f"{EXPECTED_BUILD}. Reload it — chrome://extensions (or "
                    f"brave://extensions) -> reload on the Flow bridge -> then "
                    f"hard-reload the Flow tab. There is no hot reload, and a "
                    f"stale build fails like a Flow redesign rather than like "
                    f"stale code, so nothing below here is worth debugging until "
                    f"the builds match.")
            return info
        raise FlowError(
            "the PYQ Flow Bridge extension never answered.\n"
            "  1. chrome://extensions -> Developer mode -> Load unpacked -> flow/extension\n"
            "  2. open your Google Flow project in a tab (it may stay in the background)\n"
            f"  last error: {last}")

    def set_prompt(self, text: str, *, selector: str = ".ProseMirror",
                   timeout: float = 60.0) -> int:
        """Put `text` in Flow's prompt box and prove it landed. Returns its length.

        The extension's own set_prompt types into a Slate editor. Flow has since
        migrated the prompt box to ProseMirror, and typing no longer lands: the
        readback returns the PLACEHOLDER ("What do you want to create?", 27
        chars) and the run aborts claiming the prompt did not land — which was
        true, but for a reason the message did not name.

        A paste event is the one insertion path both editors honour, so this
        goes through `eval` and dispatches one. It also selects the existing
        contents first, so a leftover prompt is REPLACED rather than appended;
        appending silently generates from two prompts at once.
        """
        js_sel, js_txt = json.dumps(selector), json.dumps(text)
        set_js = (
            f"const el=document.querySelector({js_sel});"
            "if(!el) return 'NO_EDITOR';"
            "el.focus();"
            "const s=window.getSelection(), r=document.createRange();"
            "r.selectNodeContents(el); s.removeAllRanges(); s.addRange(r);"
            "const dt=new DataTransfer(); dt.setData('text/plain', " + js_txt + ");"
            "el.dispatchEvent(new ClipboardEvent('paste',"
            "  {clipboardData:dt, bubbles:true, cancelable:true}));"
            "return 'ok';"
        )
        if self.call("eval", expr=set_js, timeout=timeout)["value"] == "NO_EDITOR":
            raise FlowError(f"set_prompt: no prompt box matched {selector!r} — "
                            "Flow has moved it again; fix flow/selectors.json")
        time.sleep(1.0)
        read = f"const el=document.querySelector({js_sel}); return el?String(el.innerText.length):'0';"
        got = int(self.call("eval", expr=read, timeout=timeout)["value"])
        # Compare on a floor, not equality: the editor normalises whitespace and
        # trailing newlines, so an exact match never holds.
        if got < len(text) * 0.9:
            raise FlowError(f"set_prompt: only {got} of {len(text)} chars landed")
        return got

    def set_status(self, **kw) -> None:
        self.status.update(kw)


# --------------------------------------------------------------------------- #
# Where downloads land.
#
# chrome.downloads.download only accepts a path RELATIVE to the browser's
# download directory and rejects `..` and absolute paths, so clips arrive in
# ~/Downloads/pyq_flow_inbox and are moved into the project afterwards. Do not
# try to make Chrome write straight into projects/ — it will refuse, and the
# error surfaces as a bare "download refused".
# --------------------------------------------------------------------------- #
def inbox_dir() -> Path:
    d = DOWNLOAD_DIR / INBOX_NAME
    d.mkdir(parents=True, exist_ok=True)
    return d


def inbox_rel(name: str) -> str:
    return f"{INBOX_NAME}/{name}"


def settled(path: Path, *, min_bytes: int = 20_000, wait: float = 1.0) -> bool:
    """True once a file has stopped growing — i.e. the download finished."""
    try:
        a = path.stat().st_size
        time.sleep(wait)
        return a >= min_bytes and path.stat().st_size == a
    except OSError:
        return False


def serve_forever(port: int = PORT) -> int:
    """`video flow --serve`: run the bridge on its own so the extension can
    connect and stay connected between pipeline runs."""
    b = FlowBridge(port).start()
    print(f"flow bridge on http://127.0.0.1:{port}")
    print(f"inbox: {inbox_dir()}")
    try:
        info = b.wait_for_worker(timeout=30)
        print(f"extension connected — flow tab: {info.get('tab') or 'none open yet'}")
    except FlowError as e:
        print(f"waiting for the extension…\n{e}")
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        b.stop()
    return 0
