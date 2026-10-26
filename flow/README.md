# Flow bridge: the Chrome extension that drives Google Flow (Veo)

`flow/extension` ("PYQ Flow Bridge") lets the pipeline type prompts into Google Flow and download the
clips from a background tab. `src/flow_bridge.py` is its Python half, on port 8765.

1. In Chrome, open `chrome://extensions`, turn on Developer mode, choose **Load unpacked**, and pick
   `flow/extension`.
2. Turn off any other bridge extension. Another project (flow-animator) ships one on the same port, and
   the two race for jobs.
3. Sign in at flow.google.com and open a project. The tab can stay in the background.
4. Check it: `tools/doctor.py --flow`.

Everything else goes through `tools/kit_veo.py` (setup, submit, fetch, clean); see the `reel` skill. After a
Flow redesign, the selectors live in `flow/selectors.json`.
