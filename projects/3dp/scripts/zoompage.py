"""zoompage: a private Artifact page for a message's pictures (build-3dp, Pictures: zoom pages; user 2026-10-11).

Each picture shows full width and opens full screen to zoom and pan (wheel or pinch, drag, double-click or double-tap,
+ / - / Fit buttons). Each model shows in one 3D viewer to turn, zoom and pan (OrbitControls), switched by chips that
keep the view, with optional per-face colors (a 3D check's stress), a loaded shape (displacement times a scale), labels
at points, and context meshes (rod, wires, clip) toggled together. Writes the page and its files into out_dir and returns
the Artifact tool's files map; publish with Artifact(file_path=html, files=files_map), one page per message.

  import sys; sys.path.insert(0, "[repo]/projects/3dp/scripts"); import zoompage as Z
  m = Z.Model("A  As drawn", tris, rgb=face_rgb, disp=vertex_disp, labels=[((x, y, z), "98 MPa")])
  html, files = Z.page(out_dir, "Raised Hook Check", "One line on what the page shows.", eyebrow="shelf, twist-lock front piece",
                       pictures=[(png, "caption")], models=[m], context=[(rod_tris, (0.3, 0.3, 0.33), "rod and wires")],
                       legend=Z.stress_legend(75, "largest tension, MPa"), source="made by ...")
  Z.tris(trimesh_or_manifold_mesh) -> (n, 3, 3) triangles; Z.reds(values, limit) -> face colors as the stress pictures.

tris are (n, 3, 3) float in mm, z up; rgb (n, 3) per face in 0..1 (or one color); disp (n, 3, 3) per corner, mm.
Model files are base64 text (m0.txt ...), because the Artifact tool serves no raw binary type; the page decodes them.
Needs numpy (and matplotlib for reds). The page loads three.js 0.147.0 from jsDelivr. Written 2026-10-11 (shelf thread)."""
import base64
import html as H
import json
import os
import shutil
import numpy as np

THREE = "https://cdn.jsdelivr.net/npm/three@0.147.0/build/three.min.js"
ORBIT = "https://cdn.jsdelivr.net/npm/three@0.147.0/examples/js/controls/OrbitControls.js"


class Model:
    def __init__(self, name, tris, rgb=(0.86, 0.84, 0.78), disp=None, labels=(), note=""):
        self.name, self.tris, self.rgb, self.disp, self.labels, self.note = name, np.asarray(tris, np.float32), rgb, disp, list(labels), note


def tris(mesh):
    """(n, 3, 3) triangles from a trimesh.Trimesh, a manifold3d Manifold (via its mesh) or a (V, F) pair."""
    if hasattr(mesh, "to_mesh"):
        mm = mesh.to_mesh(); V, F = np.asarray(mm.vert_properties)[:, :3], np.asarray(mm.tri_verts)
    elif hasattr(mesh, "vertices"):
        V, F = np.asarray(mesh.vertices), np.asarray(mesh.faces)
    else:
        V, F = mesh
    return np.asarray(V, np.float32)[np.asarray(F)]


def reds(values, limit, over=(0.35, 0.1, 0.45)):
    """Face colors as front-twist_stress.py: matplotlib Reds from 0 to limit, purple over it."""
    import matplotlib
    cm = matplotlib.colormaps["Reds"]; v = np.clip(np.asarray(values, float), 0, None)
    col = cm(0.08 + 0.85 * np.minimum(v / limit, 1))[:, :3]; col[v > limit] = over
    return col


def stress_legend(limit, label, over_text="purple: over the limit"):
    """A legend dict for page(): a Reds bar from 0 to limit."""
    import matplotlib
    cm = matplotlib.colormaps["Reds"]; stops = [cm(0.08 + 0.85 * t)[:3] for t in np.linspace(0, 1, 6)]
    return dict(stops=["#%02x%02x%02x" % tuple(int(255 * c) for c in s) for s in stops], lo="0", hi=f"{limit:g}", label=label, over=over_text)


def _pack(t, rgb, disp):
    n = len(t); col = np.broadcast_to(np.asarray(rgb, float).reshape(-1, 3), (n, 3)) if np.ndim(rgb) == 2 else np.tile(np.asarray(rgb, float), (n, 1))
    c8 = np.repeat(np.clip(np.round(col * 255), 0, 255).astype(np.uint8), 3, axis=0).ravel()        # per corner
    pad = (-len(c8)) % 4
    parts = [t.astype(np.float32).ravel().tobytes(), c8.tobytes() + b"\0" * pad]
    if disp is not None: parts.append(np.asarray(disp, np.float32).reshape(n * 9).tobytes())
    return b"".join(parts)


def page(out_dir, title, intro, pictures=(), models=(), context=(), legend=None, eyebrow="", source="", disp_scale=5.0, name="index.html",
         view=(0.75, -0.8, 0.85)):
    """Write name and its files into out_dir; return (html path, files map for the Artifact tool).
    view: the direction the 3D viewer starts looking from (toward the eye, z up), e.g. (0.45, 1.0, 0.55) to face a cut on the +y side."""
    os.makedirs(out_dir, exist_ok=True); files = {}; pics = []; mods = []; ctx = []
    for i, (p, cap) in enumerate(pictures):
        fn = f"p{i}{os.path.splitext(p)[1]}"; shutil.copyfile(p, os.path.join(out_dir, fn)); files[fn] = os.path.join(out_dir, fn)
        try:
            from PIL import Image
            w, h = Image.open(p).size
        except Exception:
            w, h = 0, 0
        pics.append(dict(src=fn, cap=cap, w=w, h=h))
    for i, m in enumerate(models):
        fn = f"m{i}.txt"; open(os.path.join(out_dir, fn), "wb").write(base64.b64encode(_pack(m.tris, m.rgb, m.disp))); files[fn] = os.path.join(out_dir, fn)
        mods.append(dict(name=m.name, file=fn, n=len(m.tris), disp=m.disp is not None, note=m.note,
                         labels=[dict(p=[float(c) for c in q], t=t) for q, t in m.labels]))
    if context:
        blob = b""
        for t, rgb, lab in context:
            t = np.asarray(t, np.float32); ctx.append(dict(off=len(blob), n=len(t), rgb=[float(c) for c in rgb], label=lab)); blob += t.ravel().tobytes()
        open(os.path.join(out_dir, "ctx.txt"), "wb").write(base64.b64encode(blob)); files["ctx.txt"] = os.path.join(out_dir, "ctx.txt")
    data = dict(pictures=pics, models=mods, context=ctx, legend=legend, scale=disp_scale, view=[float(v) for v in view])
    ctx_label = " and ".join(dict.fromkeys(c["label"] for c in ctx)) if ctx else ""
    out = os.path.join(out_dir, name)
    open(out, "w", encoding="ascii").write(TEMPLATE.replace("%%TITLE%%", H.escape(title)).replace("%%INTRO%%", H.escape(intro))
                         .replace("%%EYEBROW%%", H.escape(eyebrow)).replace("%%SOURCE%%", H.escape(source))
                         .replace("%%CTX%%", H.escape(ctx_label.capitalize() or "Context")).replace("%%THREE%%", THREE).replace("%%ORBIT%%", ORBIT)
                         .replace("%%DATA%%", json.dumps(data).replace("</", "<\\/")).replace("%%SCALE%%", f"{disp_scale:g}")
                         .encode("ascii", "xmlcharrefreplace").decode())          # character references: no charset needed
    return out, files


TEMPLATE = r"""<title>%%TITLE%%</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans+Condensed:wght@500;600&family=IBM+Plex+Sans:wght@400;500&display=swap">
<style>
/* Layout: one reading column; a 3D stage on top, then full-width pictures that open into a full-screen zoom viewer. */
:root {
  --bg: #f4f6f8; --panel: #ffffff; --stage: #e6eaef; --fg: #1b222b; --muted: #5a6573; --line: #d3d9e0; --accent: #2a5d99; --chip: #eef2f6;
  --f-head: "IBM Plex Sans Condensed", "Arial Narrow", system-ui, sans-serif; --f-body: "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  --f-data: "IBM Plex Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #11151a; --panel: #181e25; --stage: #0c1014; --fg: #e3e8ee; --muted: #98a4b2; --line: #2a333d; --accent: #82b2ea; --chip: #1f2730; color-scheme: dark } }
:root[data-theme="dark"] { --bg: #11151a; --panel: #181e25; --stage: #0c1014; --fg: #e3e8ee; --muted: #98a4b2; --line: #2a333d; --accent: #82b2ea; --chip: #1f2730; color-scheme: dark }
body { background: var(--bg); color: var(--fg); font-family: var(--f-body); font-size: 15px; line-height: 1.5; }
.wrap { max-width: 1100px; margin: 0 auto; padding-inline: 16px; padding-block: 20px 48px; display: grid; gap: 28px; }
header { display: grid; gap: 6px; }
.eyebrow { font-family: var(--f-data); font-size: 12px; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); }
h1 { font-family: var(--f-head); font-weight: 600; font-size: clamp(24px, 4vw, 34px); line-height: 1.15; margin: 0; text-wrap: balance; }
h2 { font-family: var(--f-head); font-weight: 600; font-size: 20px; margin: 0; }
.intro { margin: 0; max-width: 68ch; color: var(--fg); }
section { display: grid; gap: 12px; min-width: 0; }
.hint { font-size: 13px; color: var(--muted); margin: 0; }
.stage { position: relative; background: var(--stage); border: 1px solid var(--line); border-radius: 6px; overflow: hidden; height: min(62vh, 560px); touch-action: none; }
.stage.full { position: fixed; inset: 0; height: auto; z-index: 20; border-radius: 0; border: 0; padding-top: env(safe-area-inset-top, 0px); }
.stage canvas { display: block; width: 100%; height: 100%; }
.tags { position: absolute; inset: 0; pointer-events: none; }
.tag { position: absolute; transform: translate(-50%, -100%); font-family: var(--f-data); font-size: 12px; white-space: nowrap; background: var(--panel); color: var(--fg); border: 1px solid var(--line); border-radius: 3px; padding: 1px 5px; }
.tag::after { content: ""; position: absolute; left: 50%; bottom: -5px; width: 1px; height: 5px; background: var(--fg); }
.stage .corner { position: absolute; top: calc(8px + env(safe-area-inset-top, 0px)); right: 8px; display: flex; gap: 6px; }
.bar { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.chip, .btn { font: 500 13px var(--f-body); color: var(--fg); background: var(--chip); border: 1px solid var(--line); border-radius: 999px; padding: 5px 12px; cursor: pointer; }
.btn { border-radius: 5px; background: var(--panel); }
.chip[aria-pressed="true"] { background: var(--accent); border-color: var(--accent); color: var(--panel); }
.chip:focus-visible, .btn:focus-visible, .fig button:focus-visible, label:focus-within { outline: 2px solid var(--accent); outline-offset: 2px; }
label.tog { display: inline-flex; gap: 6px; align-items: center; font-size: 13px; color: var(--fg); cursor: pointer; }
.note { font-size: 13px; color: var(--muted); margin: 0; }
.legend { display: grid; grid-template-columns: auto minmax(120px, 280px) auto; gap: 8px; align-items: center; font-family: var(--f-data); font-size: 12px; color: var(--muted); }
.legend .ramp { height: 10px; border-radius: 2px; border: 1px solid var(--line); }
.legend .lab { grid-column: 1 / -1; font-family: var(--f-body); }
.figs { display: grid; gap: 22px; }
.fig { margin: 0; display: grid; gap: 6px; min-width: 0; }
.fig button { padding: 0; border: 1px solid var(--line); border-radius: 6px; background: #fff; cursor: zoom-in; overflow: hidden; }
.fig img { display: block; width: 100%; height: auto; }
.fig figcaption { font-size: 13px; color: var(--muted); }
.zoom { position: fixed; inset: 0; z-index: 30; background: rgba(10, 12, 15, .94); touch-action: none; overflow: hidden; }
.zoom img { position: absolute; left: 0; top: 0; transform-origin: 0 0; max-width: none; user-select: none; -webkit-user-drag: none; background: #fff; }
.zoom .corner { position: absolute; top: calc(10px + env(safe-area-inset-top, 0px)); right: 10px; display: flex; gap: 6px; }
.zoom .cap { position: absolute; left: 12px; right: 12px; bottom: calc(10px + env(safe-area-inset-bottom, 0px)); color: #e8ecf0; font-size: 13px; text-shadow: 0 1px 2px #000; pointer-events: none; }
footer { font-family: var(--f-data); font-size: 12px; color: var(--muted); border-top: 1px solid var(--line); padding-top: 10px; overflow-wrap: anywhere; }
@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
</style>
<div class="wrap">
  <header><div class="eyebrow">%%EYEBROW%%</div><h1>%%TITLE%%</h1><p class="intro">%%INTRO%%</p></header>
  <section id="models3d" hidden>
    <h2>3D models</h2>
    <div class="bar" id="chips" role="group" aria-label="Model"></div>
    <div class="stage" id="stage"><canvas id="cv"></canvas><div class="tags" id="tags"></div>
      <div class="corner"><button class="btn" id="reset" type="button">Reset view</button><button class="btn" id="full" type="button">Full screen</button></div></div>
    <div class="bar">
      <label class="tog" id="dispwrap"><input type="checkbox" id="disp"> Loaded shape, movement &times;%%SCALE%%</label>
      <label class="tog" id="ctxwrap"><input type="checkbox" id="ctx" checked> %%CTX%%</label>
      <label class="tog"><input type="checkbox" id="labs" checked> Labels</label>
    </div>
    <p class="note" id="mnote"></p>
    <div class="legend" id="legend" hidden></div>
    <p class="hint">Drag to turn, scroll or pinch to zoom, right-drag or two-finger drag to pan.</p>
  </section>
  <section id="picsec" hidden><h2>Pictures</h2><p class="hint">Tap a picture to open it full screen, then pinch, scroll or double-tap to zoom.</p><div class="figs" id="figs"></div></section>
  <footer>%%SOURCE%%</footer>
</div>
<div class="zoom" id="zoom" hidden><img id="zimg" alt=""><div class="corner"><button class="btn" id="zin" type="button">+</button><button class="btn" id="zout" type="button">&minus;</button><button class="btn" id="zfit" type="button">Fit</button><button class="btn" id="zclose" type="button">Close</button></div><div class="cap" id="zcap"></div></div>
<script id="data" type="application/json">%%DATA%%</script>
<script src="%%THREE%%"></script>
<script src="%%ORBIT%%"></script>
<script>
const D = JSON.parse(document.getElementById("data").textContent);
const $ = id => document.getElementById(id);
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();

/* pictures and the full-screen zoom viewer */
if (D.pictures.length) {
  $("picsec").hidden = false;
  D.pictures.forEach((p, i) => {
    const f = document.createElement("figure"); f.className = "fig";
    const b = document.createElement("button"); b.type = "button"; b.setAttribute("aria-label", "Open picture " + (i + 1) + " full screen");
    const im = document.createElement("img"); im.src = p.src; im.alt = p.cap; im.loading = i ? "lazy" : "eager"; if (p.w) { im.width = p.w; im.height = p.h; }
    b.appendChild(im); b.onclick = () => openZoom(p); f.appendChild(b);
    const c = document.createElement("figcaption"); c.textContent = p.cap; f.appendChild(c); $("figs").appendChild(f);
  });
}
const Z = { s: 1, x: 0, y: 0, pts: new Map(), last: null, tap: 0 };
function apply() { $("zimg").style.transform = `translate(${Z.x}px,${Z.y}px) scale(${Z.s})`; }
function fit() { const im = $("zimg"), W = innerWidth, Hh = innerHeight; const w = im.naturalWidth || 1, h = im.naturalHeight || 1;
  Z.s = Math.min(W / w, Hh / h); Z.min = Z.s * 0.8; Z.x = (W - w * Z.s) / 2; Z.y = (Hh - h * Z.s) / 2; apply(); }
function zoomAt(f, cx, cy) { const s = Math.min(Math.max(Z.s * f, Z.min || 0.05), 8); Z.x = cx - (cx - Z.x) * s / Z.s; Z.y = cy - (cy - Z.y) * s / Z.s; Z.s = s; apply(); }
function openZoom(p) { const im = $("zimg"); $("zcap").textContent = p.cap; $("zoom").hidden = false; im.onload = fit; im.src = p.src; if (im.complete) fit(); $("zclose").focus(); }
function closeZoom() { $("zoom").hidden = true; Z.pts.clear(); }
$("zclose").onclick = closeZoom; $("zfit").onclick = fit;
$("zin").onclick = () => zoomAt(1.6, innerWidth / 2, innerHeight / 2); $("zout").onclick = () => zoomAt(1 / 1.6, innerWidth / 2, innerHeight / 2);
addEventListener("keydown", e => { if (!$("zoom").hidden && e.key === "Escape") closeZoom(); });
const zr = $("zoom");
zr.addEventListener("wheel", e => { e.preventDefault(); zoomAt(Math.exp(-e.deltaY * 0.0015), e.clientX, e.clientY); }, { passive: false });
zr.addEventListener("pointerdown", e => { if (e.target.closest("button")) return; zr.setPointerCapture(e.pointerId); Z.pts.set(e.pointerId, [e.clientX, e.clientY]);
  const now = Date.now(); if (Z.pts.size === 1 && now - Z.tap < 300) { zoomAt(Z.s < (Z.min / 0.8) * 1.5 ? 3 : (Z.min / 0.8) / Z.s, e.clientX, e.clientY); } Z.tap = now; Z.last = null; });
zr.addEventListener("pointermove", e => { if (!Z.pts.has(e.pointerId)) return; const prev = Z.pts.get(e.pointerId); Z.pts.set(e.pointerId, [e.clientX, e.clientY]);
  if (Z.pts.size === 1) { Z.x += e.clientX - prev[0]; Z.y += e.clientY - prev[1]; apply(); }
  else if (Z.pts.size === 2) { const [a, b] = [...Z.pts.values()]; const d = Math.hypot(a[0] - b[0], a[1] - b[1]), m = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
    if (Z.last) { Z.x += m[0] - Z.last.m[0]; Z.y += m[1] - Z.last.m[1]; zoomAt(d / Z.last.d, m[0], m[1]); } Z.last = { d, m }; } });
const up = e => { Z.pts.delete(e.pointerId); Z.last = null; };
zr.addEventListener("pointerup", up); zr.addEventListener("pointercancel", up);
addEventListener("resize", () => { if (!$("zoom").hidden) fit(); });

/* 3D viewer */
if (D.models.length && window.THREE) {
  $("models3d").hidden = false;
  const cv = $("cv"), stage = $("stage");
  const R = new THREE.WebGLRenderer({ canvas: cv, antialias: true, preserveDrawingBuffer: true }); R.setPixelRatio(Math.min(devicePixelRatio, 2));
  const scene = new THREE.Scene(), cam = new THREE.PerspectiveCamera(30, 1, 0.1, 5000); cam.up.set(0, 0, 1);
  scene.add(new THREE.HemisphereLight(0xffffff, 0x8890a0, 0.75)); const sun = new THREE.DirectionalLight(0xffffff, 0.6); cam.add(sun); sun.position.set(0.4, 0.7, 1); scene.add(cam);
  const ctl = new THREE.OrbitControls(cam, cv); ctl.enableDamping = true; ctl.dampingFactor = 0.12; ctl.screenSpacePanning = true;
  const groups = [], ctxGroup = new THREE.Group(); scene.add(ctxGroup);
  let cur = 0, home = null;
  function bg() { scene.background = new THREE.Color(css("--stage") || "#e6eaef"); }
  bg(); matchMedia("(prefers-color-scheme: dark)").addEventListener("change", bg); new MutationObserver(bg).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
  function edgesOf(geo) { const e = new THREE.LineSegments(new THREE.EdgesGeometry(geo, 28), new THREE.LineBasicMaterial({ color: 0x20262e, transparent: true, opacity: 0.55 })); return e; }
  function size() { const w = stage.clientWidth, h = stage.clientHeight; R.setSize(w, h, false); cam.aspect = w / Math.max(h, 1); cam.updateProjectionMatrix(); }
  new ResizeObserver(size).observe(stage);
  async function bin(f) { const s = atob((await (await fetch(f)).text()).trim()); const u = new Uint8Array(s.length);   // model files are base64 text (artifacts serve no raw binary)
    for (let k = 0; k < s.length; k++) u[k] = s.charCodeAt(k); return u.buffer; }
  async function load(m, i) {
    const buf = await bin(m.file); const n9 = m.n * 9;
    const pos = new Float32Array(buf, 0, n9), col8 = new Uint8Array(buf, n9 * 4, n9), off = n9 * 4 + n9 + ((4 - n9 % 4) % 4);
    const disp = m.disp ? new Float32Array(buf, off, n9) : null;
    const geo = new THREE.BufferGeometry(); const p = new Float32Array(pos); geo.setAttribute("position", new THREE.BufferAttribute(p, 3));
    geo.setAttribute("color", new THREE.BufferAttribute(new Float32Array(col8).map(v => v / 255), 3)); geo.computeVertexNormals();
    const mesh = new THREE.Mesh(geo, new THREE.MeshLambertMaterial({ vertexColors: true, side: THREE.DoubleSide }));
    const g = new THREE.Group(); g.add(mesh); const ed = edgesOf(geo); g.add(ed); g.visible = i === cur;
    g.userData = { geo, base: new Float32Array(pos), disp, ed, m }; scene.add(g); groups[i] = g; return g;
  }
  function setDisp() {
    groups.forEach(g => { if (!g) return; const u = g.userData, on = $("disp").checked && u.disp, a = g.userData.geo.attributes.position.array;
      for (let k = 0; k < a.length; k++) a[k] = u.base[k] + (on ? D.scale * u.disp[k] : 0);
      u.geo.attributes.position.needsUpdate = true; u.geo.computeVertexNormals(); g.remove(u.ed); u.ed = edgesOf(u.geo); g.add(u.ed); });
  }
  function show(i) { cur = i; groups.forEach((g, k) => g && (g.visible = k === i)); [...$("chips").children].forEach((c, k) => c.setAttribute("aria-pressed", k === i));
    const m = D.models[i]; $("mnote").textContent = m.note || ""; $("dispwrap").hidden = !D.models.some(q => q.disp); drawTags(); }
  D.models.forEach((m, i) => { const c = document.createElement("button"); c.type = "button"; c.className = "chip"; c.textContent = m.name; c.onclick = () => show(i); $("chips").appendChild(c); });
  const tags = $("tags");
  function drawTags() { tags.innerHTML = ""; if (!$("labs").checked) return; const m = D.models[cur]; const w = stage.clientWidth, h = stage.clientHeight;
    (m.labels || []).forEach(L => { const v = new THREE.Vector3(...L.p); v.project(cam); if (v.z > 1) return;
      const d = document.createElement("div"); d.className = "tag"; d.textContent = L.t; let x = (v.x + 1) / 2 * w, y = (1 - v.y) / 2 * h - 6;
      d.style.left = x + "px"; d.style.top = y + "px"; tags.appendChild(d);
      for (let k = 0; k < 6; k++) { const r = d.getBoundingClientRect(); const hit = [...tags.children].some(o => o !== d && (q => !(q.right < r.left || q.left > r.right || q.bottom < r.top || q.top > r.bottom))(o.getBoundingClientRect()));
        if (!hit) break; y -= r.height + 2; d.style.top = y + "px"; } }); }
  function frame() { const box = new THREE.Box3(); groups.forEach(g => g && box.expandByObject(g)); const s = box.getBoundingSphere(new THREE.Sphere());
    const vf = THREE.MathUtils.degToRad(cam.fov), hf = 2 * Math.atan(Math.tan(vf / 2) * cam.aspect), half = Math.min(vf, hf) / 2;
    const dir = new THREE.Vector3(...(D.view || [0.75, -0.8, 0.85])).normalize(); cam.position.copy(s.center).addScaledVector(dir, s.radius / Math.sin(half) * 0.95);
    ctl.target.copy(s.center); cam.near = s.radius / 50; cam.far = s.radius * 50; cam.updateProjectionMatrix(); ctl.update(); home = { p: cam.position.clone(), t: s.center.clone() }; }
  $("reset").onclick = () => { if (home) { cam.position.copy(home.p); ctl.target.copy(home.t); ctl.update(); } };
  $("full").onclick = () => { const f = stage.classList.toggle("full"); $("full").textContent = f ? "Exit full screen" : "Full screen"; size(); };
  $("disp").onchange = setDisp; $("ctx").onchange = () => { ctxGroup.visible = $("ctx").checked; }; $("labs").onchange = drawTags;
  (async () => {
    if (D.context.length) { const buf = await bin("ctx.txt");
      D.context.forEach(c => { const geo = new THREE.BufferGeometry(); geo.setAttribute("position", new THREE.BufferAttribute(new Float32Array(buf, c.off, c.n * 9).slice(), 3)); geo.computeVertexNormals();
        ctxGroup.add(new THREE.Mesh(geo, new THREE.MeshLambertMaterial({ color: new THREE.Color(...c.rgb), side: THREE.DoubleSide }))); ctxGroup.add(edgesOf(geo)); }); }
    else { $("ctxwrap").hidden = true; }
    await Promise.all(D.models.map(load)); show(0); size(); frame();
    if (D.legend) { const L = D.legend, el = $("legend"); el.hidden = false;
      el.innerHTML = `<span>${L.lo}</span><div class="ramp" style="background:linear-gradient(90deg,${L.stops.join(",")})"></div><span>${L.hi}</span><span class="lab"></span>`;
      el.querySelector(".lab").textContent = L.label + (L.over ? "; " + L.over : ""); }
    ctl.addEventListener("change", drawTags); addEventListener("resize", drawTags); drawTags();
    (function loop() { ctl.update(); R.render(scene, cam); requestAnimationFrame(loop); })();
  })();
} else if (D.models.length) { $("models3d").hidden = false; $("mnote").textContent = "The 3D viewer couldn't load three.js; the pictures below still work."; }
</script>
"""
