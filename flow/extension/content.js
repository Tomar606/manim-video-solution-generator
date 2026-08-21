/* PYQ Flow Bridge — status panel.
 *
 * READ-ONLY ON PURPOSE. Every control the upstream extension put here (teach,
 * connect, start, grab) has moved into background.js, because anything driven
 * from this page only runs while the page is in front of you — the one thing
 * this integration exists to avoid. So the panel reports and never drives: if
 * you close this tab's panel, or never open it, the run is unaffected.
 *
 * It reads the bridge's own /status endpoint rather than listening to the
 * worker, so it also tells you the truth when the worker has been recycled.
 */
(() => {
  if (window.__pyqFlowPanel) return;
  window.__pyqFlowPanel = true;

  const BRIDGE = "http://127.0.0.1:8765";

  const host = document.createElement("div");
  host.style.cssText = "position:fixed;z-index:2147483647;top:80px;left:16px;";
  const root = host.attachShadow({ mode: "open" });
  document.documentElement.appendChild(host);
  root.innerHTML = `
    <style>
      .p{font:12px/1.45 system-ui,sans-serif;width:250px;background:#101014;color:#eaeaea;
         border:1px solid #2a2a33;border-radius:10px;padding:11px;box-shadow:0 8px 30px rgba(0,0,0,.5)}
      h1{font-size:12px;margin:0 0 8px;letter-spacing:.02em;cursor:move}
      .k{color:#9a9aa5}
      .ok{color:#6fd08c}.bad{color:#e08a8a}.warn{color:#e0c07a}
      .st{margin-top:7px;white-space:pre-wrap;max-height:190px;overflow:auto;color:#c9c9d2}
      .hint{margin-top:7px;color:#7a7a85;font-size:11px}
    </style>
    <div class="p">
      <h1>PYQ Flow Bridge <span id="dot" class="bad">●</span></h1>
      <div class="st" id="st">connecting…</div>
      <div class="hint">Status only. The run is driven from the terminal and
      keeps going with this tab in the background.</div>
    </div>`;

  // drag by the title bar
  (() => {
    const bar = root.querySelector("h1");
    let drag = false, ox = 0, oy = 0;
    bar.addEventListener("mousedown", (e) => {
      const r = host.getBoundingClientRect();
      drag = true; ox = e.clientX - r.left; oy = e.clientY - r.top;
      host.style.left = r.left + "px"; host.style.top = r.top + "px";
      e.preventDefault();
    });
    window.addEventListener("mousemove", (e) => {
      if (!drag) return;
      host.style.left = Math.max(0, e.clientX - ox) + "px";
      host.style.top = Math.max(0, e.clientY - oy) + "px";
    });
    window.addEventListener("mouseup", () => { drag = false; });
  })();

  const st = root.getElementById("st");
  const dot = root.getElementById("dot");

  async function tick() {
    try {
      const r = await fetch(BRIDGE + "/status", { cache: "no-store" });
      const s = await r.json();
      dot.className = s.worker_seen_ago != null && s.worker_seen_ago < 15 ? "ok" : "warn";
      const lines = [
        `run       ${s.run || "—"}`,
        `scene     ${s.scene || "—"}`,
        `stage     ${s.stage || "idle"}`,
        `worker    ${s.worker_seen_ago == null ? "never seen" : s.worker_seen_ago.toFixed(0) + "s ago"}`,
      ];
      if (s.detail) lines.push("", s.detail);
      st.textContent = lines.join("\n");
    } catch (e) {
      dot.className = "bad";
      st.textContent = "bridge not running.\n\nStart it with:\n  video flow --serve\n\n(or just run `video veo <project>`,\nwhich starts it for you)";
    }
  }
  tick();
  setInterval(tick, 2000);
})();
