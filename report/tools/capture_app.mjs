/**
 * capture_app.mjs -- full-page, 2x screenshots of the running web app for the report.
 *
 *   streamlit run app/streamlit_app.py            (in another terminal)
 *   node report/tools/capture_app.mjs
 *
 * Drives headless Chrome through the DevTools protocol (Node's built-in fetch and
 * WebSocket -- nothing to install). A plain `chrome --screenshot` fires before
 * Streamlit has rendered, so this waits for the page content, then grows the
 * window to the content's full height before capturing.
 */
import { spawn } from "node:child_process";
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const BASE = process.env.APP_URL || "http://localhost:8501";
const OUT = join(dirname(fileURLToPath(import.meta.url)), "..", "figures", "app");
const PORT = 9333;
const WIDTH = 1440;
const PAGES = [
  ["overview", "/", "Wine Quality Prediction Using"],
  ["dataset", "/dataset", "Summary statistics"],
  ["reproduction", "/reproduction", "Why 89.73"],
  ["class_balancing", "/class-balancing", "Accuracy, macro-F1 and per-class recall"],
  ["improvement", "/improvement", "Every candidate"],
  ["feature_importance", "/feature-importance", "How many lab tests"],
  ["predict", "/predict", "Batch prediction"],
];

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
mkdirSync(OUT, { recursive: true });

const chrome = spawn(CHROME, [
  "--headless=new", `--remote-debugging-port=${PORT}`, "--hide-scrollbars", "--no-first-run",
  `--user-data-dir=${join(process.env.TMPDIR || "/tmp", "capture-app-chrome")}`, "about:blank",
], { stdio: "ignore" });

let ws, nextId = 0;
const pending = new Map();
function send(method, params = {}) {
  const id = ++nextId;
  ws.send(JSON.stringify({ id, method, params }));
  return new Promise((resolve, reject) => pending.set(id, { resolve, reject }));
}
async function evaluate(expr) {
  const r = await send("Runtime.evaluate", { expression: expr, returnByValue: true });
  return r.result.value;
}

try {
  let target;
  for (let i = 0; i < 50 && !target; i++) {
    try {
      const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
      target = list.find((t) => t.type === "page");
    } catch { await sleep(200); }
  }
  ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((r) => ws.addEventListener("open", r));
  ws.addEventListener("message", (e) => {
    const m = JSON.parse(e.data);
    if (m.id && pending.has(m.id)) {
      const p = pending.get(m.id); pending.delete(m.id);
      m.error ? p.reject(new Error(m.error.message)) : p.resolve(m.result);
    }
  });
  await send("Page.enable");
  await send("Emulation.setDeviceMetricsOverride", { width: WIDTH, height: 900, deviceScaleFactor: 2, mobile: false });

  for (const [name, path, marker] of PAGES) {
    await send("Emulation.setDeviceMetricsOverride", { width: WIDTH, height: 900, deviceScaleFactor: 2, mobile: false });
    await send("Page.navigate", { url: BASE + path });
    // Wait until the page's own content is on screen and the app has stopped running.
    let ready = false;
    for (let i = 0; i < 120 && !ready; i++) {
      await sleep(500);
      ready = await evaluate(`document.body.innerText.includes(${JSON.stringify(marker)}) &&
        !document.querySelector('[data-testid="stStatusWidget"]')`);
    }
    if (!ready) throw new Error(`page did not finish rendering: ${name}`);
    await sleep(2500); // let charts and images finish drawing
    const height = await evaluate(`Math.ceil(Math.max(
      ...[...document.querySelectorAll('[data-testid="stMain"], [data-testid="stMainBlockContainer"], section.main')]
        .map(e => e.scrollHeight), 900))`);
    await send("Emulation.setDeviceMetricsOverride", { width: WIDTH, height: Math.min(height + 40, 6000), deviceScaleFactor: 2, mobile: false });
    await sleep(2500);
    const shot = await send("Page.captureScreenshot", { format: "png" });
    writeFileSync(join(OUT, `app_${name}.png`), Buffer.from(shot.data, "base64"));
    console.log(`captured app_${name}.png  (${WIDTH} x ${Math.min(height + 40, 6000)} css px)`);
  }
} finally {
  ws?.close();
  chrome.kill();
}
