// Jet A-1 fuel farm (JIG 2 airport depot): deterministic 3D explainer.
// window.renderAt(t) draws the frame for time t (seconds) and returns a JPEG data URL.
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const W = 1920, H = 1080;
const TL = await (await fetch('../build/timeline.json')).json();
const S = Object.fromEntries(TL.scenes.map(s => [s.key, s.start]));
const SEN = Object.fromEntries(TL.scenes.map(s => [s.key, s.sentences.map(x => x.t0)]));
const END = TL.end;
await document.fonts.load('700 40px Inter'); await document.fonts.load('500 40px Inter'); await document.fonts.load('800 40px Inter');

// ------------------------------------------------------------------ helpers
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const ss = (t, a, b) => { const u = clamp((t - a) / (b - a)); return u * u * (3 - 2 * u); };
const win = (t, a, b, f = .5) => ss(t, a, a + f) * (1 - ss(t, b - f, b));
const V = (x, y, z) => new THREE.Vector3(x, y, z);
const rand = (() => { let s = 7; return () => (s = (s * 16807) % 2147483647) / 2147483647; })();

const C = {
  bg: 0x161a1e, ground: 0x2b3035, bund: 0x7d8286, concrete: 0x9a9fa3, apron: 0x6b7075,
  shell: 0xe6e9eb, steel: 0x5a6168, dark: 0x30353a, amber: 0xe3a83a, teal: 0x3aaea9,
  coral: 0xe4705a, cream: 0xf3e8cf, glass: 0x26343c, white: 0xf2f3f4,
};

// ------------------------------------------------------------------ renderer
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setSize(W, H, false);
renderer.setPixelRatio(1);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.92;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.localClippingEnabled = true;
const glCanvas = renderer.domElement; glCanvas.id = 'gl';

const scene = new THREE.Scene();
scene.background = new THREE.Color(C.bg);
scene.fog = new THREE.Fog(C.bg, 170, 360);
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
scene.environmentIntensity = 0.38;

const camera = new THREE.PerspectiveCamera(34, W / H, 0.1, 900);
const hemi = new THREE.HemisphereLight(0xdfe6ec, 0x2a2d30, 0.55); scene.add(hemi);
const sun = new THREE.DirectionalLight(0xfff3e2, 2.1);
sun.castShadow = true; sun.shadow.mapSize.set(4096, 4096); sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.04;
scene.add(sun); scene.add(sun.target);
const SUN_DIR = V(-0.45, 0.8, 0.38).normalize();

// ------------------------------------------------------------------ materials
const std = (color, o = {}) => new THREE.MeshStandardMaterial({ color, roughness: .6, metalness: .1, ...o });
const M = {
  shell: std(C.shell, { roughness: .42, metalness: .28 }),
  steel: std(C.steel, { roughness: .4, metalness: .65 }),
  dark: std(C.dark, { roughness: .55, metalness: .4 }),
  concrete: std(C.concrete, { roughness: .95, metalness: 0 }),
  bund: std(C.bund, { roughness: .95, metalness: 0 }),
  rail: std(C.amber, { roughness: .5, metalness: .2 }),
  coral: std(C.coral, { roughness: .5 }),
  rubber: std(0x1b1d1f, { roughness: .8 }),
  glass: std(C.glass, { roughness: .15, metalness: .5 }),
  white: std(C.white, { roughness: .45, metalness: .15 }),
  belly: std(0xb9bec3, { roughness: .5, metalness: .2 }),
  tail: std(C.teal, { roughness: .45, metalness: .15 }),
};

function canvasTex(w, h, draw) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t;
}

// ground with a faint survey grid
const gridTex = canvasTex(512, 512, (g, w, h) => {
  g.fillStyle = '#2b3035'; g.fillRect(0, 0, w, h);
  for (let i = 0; i < 4000; i++) { g.fillStyle = `rgba(255,255,255,${rand() * .025})`; g.fillRect(rand() * w, rand() * h, 2, 2); }
  g.strokeStyle = 'rgba(255,255,255,0.06)'; g.lineWidth = 2; g.strokeRect(0, 0, w, h);
});
gridTex.wrapS = gridTex.wrapT = THREE.RepeatWrapping; gridTex.repeat.set(80, 80);
const groundMat = new THREE.MeshStandardMaterial({ map: gridTex, roughness: .97, metalness: 0, transparent: true, opacity: 1 });
const ground = new THREE.Mesh(new THREE.PlaneGeometry(800, 800), groundMat);
ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true; scene.add(ground);

function add(geo, mat, x = 0, y = 0, z = 0, parent = scene, cast = true) {
  const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z);
  m.castShadow = cast; m.receiveShadow = true; parent.add(m); return m;
}
function box(w, h, d, mat, x, y, z, parent) { return add(new THREE.BoxGeometry(w, h, d), mat, x, y, z, parent); }
function cylBetween(a, b, r, mat, parent = scene, seg = 24) {
  const d = b.clone().sub(a); const L = d.length();
  const m = add(new THREE.CylinderGeometry(r, r, L, seg), mat, 0, 0, 0, parent);
  m.position.copy(a).addScaledVector(d, .5);
  m.quaternion.setFromUnitVectors(V(0, 1, 0), d.normalize());
  return m;
}

// ------------------------------------------------------------------ pipes + flow
class Polyline extends THREE.Curve {
  constructor(pts) { super(); this.p = pts; this.L = [0];
    for (let i = 1; i < pts.length; i++) this.L.push(this.L[i - 1] + pts[i].distanceTo(pts[i - 1])); }
  get length() { return this.L[this.L.length - 1]; }
  getPoint(u, target = new THREE.Vector3()) {
    const s = clamp(u) * this.length; let i = 1;
    while (i < this.L.length - 1 && this.L[i] < s) i++;
    const f = (s - this.L[i - 1]) / Math.max(1e-6, this.L[i] - this.L[i - 1]);
    return target.copy(this.p[i - 1]).lerp(this.p[i], f);
  }
}
const chevron = (col) => canvasTex(256, 64, (g, w, h) => {
  g.clearRect(0, 0, w, h);
  g.strokeStyle = col; g.lineWidth = 7; g.lineJoin = 'miter';
  for (const x0 of [60, 188]) { g.beginPath(); g.moveTo(x0, 6); g.lineTo(x0 + 22, h / 2); g.lineTo(x0, h - 6); g.stroke(); }
});
const flows = [];
function pipe(pts, r = .2, mat = M.steel, opts = {}) {
  pts = pts.map(p => Array.isArray(p) ? V(...p) : p);
  for (let i = 1; i < pts.length; i++) cylBetween(pts[i - 1], pts[i], r, mat, opts.parent);
  for (let i = 1; i < pts.length - 1; i++) add(new THREE.SphereGeometry(r * 1.02, 20, 12), mat, pts[i].x, pts[i].y, pts[i].z, opts.parent);
  if (opts.supports) for (let i = 1; i < pts.length; i++) {
    const a = pts[i - 1], b = pts[i]; if (Math.abs(a.y - b.y) > .01 || a.y < .5) continue;
    const n = Math.floor(a.distanceTo(b) / 7);
    for (let k = 1; k <= n; k++) { const p = a.clone().lerp(b, k / (n + 1)); box(.35, p.y - r, .9, M.concrete, p.x, (p.y - r) / 2, p.z); }
  }
  return pts;
}
// animated chevrons riding on top of a pipe run
function flow(pts, r, color, key) {
  pts = pts.map(p => Array.isArray(p) ? V(...p) : p);
  const curve = new Polyline(pts);
  const tex = chevron(color === C.teal ? '#7fe3dc' : '#ffd27a');
  tex.wrapS = THREE.RepeatWrapping; tex.repeat.set(curve.length / 1.6, 1);
  const mat = new THREE.MeshBasicMaterial({ map: tex, color: 0xffffff, transparent: true, opacity: 0, depthWrite: false, toneMapped: false });
  const sleeve = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0, depthWrite: false, toneMapped: false });
  const segs = Math.max(8, Math.round(curve.length * 3));
  const m1 = new THREE.Mesh(new THREE.TubeGeometry(curve, segs, r * 1.18, 16, false), sleeve);
  const m2 = new THREE.Mesh(new THREE.TubeGeometry(curve, segs, r * 1.25, 16, false), mat);
  m1.renderOrder = 5; m2.renderOrder = 6; scene.add(m1); scene.add(m2);
  const f = { key, tex, mat, sleeve, len: curve.length, curve, mesh: [m1, m2] };
  flows.push(f); return f;
}
function setFlow(f, a, t, speed = 3.0, fill = 1) {
  f.mat.opacity = a * .8; f.sleeve.opacity = a * .24;
  f.tex.offset.x = -(t * speed) / 1.6;
  f.mesh.forEach(m => { m.visible = a > .003; m.geometry.setDrawRange(0, Math.ceil(m.geometry.index.count * clamp(fill) / 6) * 6); });
}

function valve(x, y, z, axis = 'x', scale = 1, parent = scene) {
  const g = new THREE.Group(); g.position.set(x, y, z); parent.add(g);
  box(.55 * scale, .55 * scale, .55 * scale, M.dark, 0, 0, 0, g);
  const st = add(new THREE.CylinderGeometry(.05 * scale, .05 * scale, .6 * scale, 8), M.steel, 0, .5 * scale, 0, g);
  const hw = add(new THREE.TorusGeometry(.28 * scale, .045 * scale, 8, 24), M.coral, 0, .8 * scale, 0, g);
  hw.rotation.x = Math.PI / 2;
  if (axis === 'z') g.rotation.y = Math.PI / 2;
  return g;
}

// ------------------------------------------------------------------ RECEIPT (x -140 .. -45)
const PIPE_Y = 1.6;
const R1 = pipe([[-170, PIPE_Y, 6], [-56.15, PIPE_Y, 6]], .3, M.steel, { supports: true });
valve(-62, PIPE_Y, 6, 'x', 1.4);
for (const x of [-120, -95]) { // pipeline marker posts
  add(new THREE.CylinderGeometry(.08, .08, 1.4, 10), M.rail, x, .7, 8.5);
  box(.5, .35, .06, M.rail, x, 1.45, 8.5);
}
// receipt filter: vertical vessel on legs
const RF = V(-55, 0, 6);
{
  const g = new THREE.Group(); g.position.copy(RF); scene.add(g);
  add(new THREE.CylinderGeometry(1.15, 1.15, 2.6, 48), M.shell, 0, 2.2, 0, g);
  const top = add(new THREE.SphereGeometry(1.15, 48, 16, 0, Math.PI * 2, 0, Math.PI / 2), M.shell, 0, 3.5, 0, g); top.scale.y = .5;
  const bot = add(new THREE.SphereGeometry(1.15, 48, 16, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2), M.shell, 0, .9, 0, g); bot.scale.y = .5;
  for (const [lx, lz] of [[.8, .8], [-.8, .8], [.8, -.8], [-.8, -.8]]) add(new THREE.CylinderGeometry(.07, .07, .9, 8), M.steel, lx, .45, lz, g);
  add(new THREE.CylinderGeometry(.12, .12, .7, 12), M.steel, 0, 4.1, 0, g); // vent
  add(new THREE.CylinderGeometry(.18, .18, .1, 16), M.coral, 0, 4.5, 0, g);
  add(new THREE.CylinderGeometry(.1, .1, .5, 10), M.steel, 0, .2, 0, g); // drain
  valve(.0, .1, .7, 'z', .5, g);
}
const R2 = pipe([[-53.85, PIPE_Y, 6], [-44, PIPE_Y, 6], [-44, PIPE_Y, -11.5], [-8, PIPE_Y, -11.5]], .25, M.steel, { supports: true });
pipe([[-26, PIPE_Y, -11.5], [-26, PIPE_Y, -6.95]], .22); pipe([[-8, PIPE_Y, -11.5], [-8, PIPE_Y, -6.95]], .22);
valve(-26, PIPE_Y, -9.5, 'z', 1); valve(-8, PIPE_Y, -9.5, 'z', 1);
// sample point cabinet + sample jar
const SP = V(-50.5, 0, 8.8);
box(.9, 1.1, .6, M.white, SP.x, .55, SP.z);
pipe([[-50.5, PIPE_Y, 6], [-50.5, PIPE_Y, 8.6], [-50.5, 1.15, 8.6]], .06);
const jarMat = new THREE.MeshPhysicalMaterial({ color: 0xffe2a0, transmission: 0, transparent: true, opacity: .75, roughness: .1, emissive: 0x6b4300, emissiveIntensity: .35 });
add(new THREE.CylinderGeometry(.13, .13, .32, 20), jarMat, SP.x + .2, 1.27, SP.z + .1);

// ------------------------------------------------------------------ BUND + TANKS
function wall(x0, z0, x1, z1) {
  const L = Math.hypot(x1 - x0, z1 - z0);
  const m = box(x1 !== x0 ? L : .4, 1.25, z1 !== z0 ? L : .4, M.bund, (x0 + x1) / 2, .625, (z0 + z1) / 2);
  return m;
}
wall(-39, -16, 3, -16); wall(-39, 15, 3, 15); wall(-39, -16, -39, 15); wall(3, -16, 3, 15);
{ const f = add(new THREE.PlaneGeometry(42, 31), std(0x5d6267, { roughness: .95 }), -18, .02, -.5); f.rotation.x = -Math.PI / 2; f.castShadow = false; }

const TR = 7, TH = 12, TB = .6;   // tank radius, shell height, base (rim) height
const FILL = 9.6, FLOOR_DROP = .6;
const clipT1 = new THREE.Plane(V(0, 0, -1), 50);   // keeps z <= constant
const clipF1 = new THREE.Plane(V(0, 0, -1), 50);

const gradeTex = canvasTex(1024, 160, (g, w, h) => {
  g.fillStyle = '#121314'; g.fillRect(0, 0, w, h);
  g.fillStyle = '#ffffff'; g.font = '800 104px Inter'; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillText('JET A-1', w / 2, h / 2 + 4);
});
const numTex = (s) => canvasTex(512, 128, (g, w, h) => {
  g.fillStyle = 'rgba(0,0,0,0)'; g.clearRect(0, 0, w, h);
  g.fillStyle = '#2a2e32'; g.font = '700 92px Inter'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(s, w / 2, h / 2);
});

function tank(cx, cz, name, clip) {
  const g = new THREE.Group(); g.position.set(cx, 0, cz); scene.add(g);
  const cp = clip ? [clip] : null;
  const shellMat = M.shell.clone(); shellMat.side = THREE.DoubleSide; if (cp) shellMat.clippingPlanes = cp;
  const concMat = M.concrete.clone(); if (cp) concMat.clippingPlanes = cp;
  const steelMat = M.steel.clone(); if (cp) steelMat.clippingPlanes = cp;
  const railMat = M.rail.clone(); if (cp) railMat.clippingPlanes = cp;
  add(new THREE.CylinderGeometry(TR + .5, TR + .65, .6, 96), concMat, 0, .3, 0, g);
  add(new THREE.CylinderGeometry(TR, TR, TH, 128, 1, true), shellMat, 0, TB + TH / 2, 0, g);
  const roof = add(new THREE.ConeGeometry(TR + .15, 1.5, 128, 1, true), shellMat, 0, TB + TH + .75, 0, g);
  for (const y of [TB + .1, TB + TH - .9]) { const r = add(new THREE.TorusGeometry(TR + .04, .07, 8, 128), steelMat, 0, y, 0, g); r.rotation.x = Math.PI / 2; }
  // roof handrail
  const hr = add(new THREE.TorusGeometry(TR - .3, .035, 6, 128), railMat, 0, TB + TH + 1.2, 0, g); hr.rotation.x = Math.PI / 2;
  for (let i = 0; i < 28; i++) { const a = i / 28 * Math.PI * 2; add(new THREE.CylinderGeometry(.03, .03, 1.1, 6), railMat, Math.sin(a) * (TR - .3), TB + TH + .65, Math.cos(a) * (TR - .3), g); }
  // vents / hatch on roof
  add(new THREE.CylinderGeometry(.35, .35, .9, 20), steelMat, 0, TB + TH + 1.9, 0, g);
  add(new THREE.CylinderGeometry(.6, .6, .15, 20), steelMat, 0, TB + TH + 2.4, 0, g);
  add(new THREE.CylinderGeometry(.3, .3, .4, 16), steelMat, 3, TB + TH + .5, 1.5, g);
  // spiral stair (stringer + treads) on the back-left
  for (let i = 0; i < 46; i++) {
    const a = -2.2 - i * 0.055, y = TB + .3 + i * (TH / 46);
    const tr = add(new THREE.BoxGeometry(1.1, .06, .35), steelMat, Math.sin(a) * (TR + .6), y, Math.cos(a) * (TR + .6), g); tr.rotation.y = a;
    if (i % 3 === 0) add(new THREE.CylinderGeometry(.025, .025, 1.0, 6), railMat, Math.sin(a) * (TR + 1.15), y + .5, Math.cos(a) * (TR + 1.15), g);
  }
  // grade identification band (EI 1542: black, white lettering) + tank number
  const band = add(new THREE.CylinderGeometry(TR + .03, TR + .03, 1.25, 64, 1, true, -.55, 1.1), new THREE.MeshStandardMaterial({ map: gradeTex, roughness: .6, clippingPlanes: cp }), 0, 9.2, 0, g); band.castShadow = false;
  const nb = add(new THREE.CylinderGeometry(TR + .03, TR + .03, 1.0, 64, 1, true, -.4, .8), new THREE.MeshStandardMaterial({ map: numTex(name), transparent: true, roughness: .6, clippingPlanes: cp }), 0, 3.4, 0, g); nb.castShadow = false;
  if (clip) { band.rotation.y = -1.1; nb.rotation.y = -1.25; } else { band.rotation.y = -.35; nb.rotation.y = -.35; }
  return g;
}
const T1 = V(-26, 0, 0), T2 = V(-8, 0, 0);
const tank1 = tank(T1.x, T1.z, 'T-101', clipT1);
const tank2 = tank(T2.x, T2.z, 'T-102', null);

// ---- T1 internals (cutaway)
const cut = (m) => { m.clippingPlanes = [clipT1]; return m; };
const fuelMat = cut(new THREE.MeshStandardMaterial({ color: C.amber, transparent: true, opacity: .3, roughness: .25, metalness: 0, emissive: 0x5a3500, emissiveIntensity: .35, depthWrite: false, side: THREE.DoubleSide }));
const fuelCapMat = new THREE.MeshStandardMaterial({ color: 0xd99a2b, transparent: true, opacity: .0, roughness: .35, emissive: 0x6a3f00, emissiveIntensity: .45, side: THREE.DoubleSide, depthWrite: false });
const waterMat = cut(new THREE.MeshStandardMaterial({ color: C.teal, roughness: .2, emissive: 0x0b4f4c, emissiveIntensity: .5, side: THREE.DoubleSide }));
const waterCapMat = new THREE.MeshStandardMaterial({ color: C.teal, roughness: .3, emissive: 0x0b4f4c, emissiveIntensity: .6, side: THREE.DoubleSide, transparent: true, opacity: 0 });
const floorMat = cut(std(0xc9cdd0, { roughness: .6, metalness: .2, side: THREE.DoubleSide }));
const inT1 = new THREE.Group(); inT1.position.copy(T1); scene.add(inT1);
{
  const fl = add(new THREE.ConeGeometry(TR - .02, FLOOR_DROP, 96, 1, true), floorMat, 0, FLOOR_DROP / 2 + .0, 0, inT1, false); fl.rotation.x = Math.PI;
}
const fuelBody = add(new THREE.CylinderGeometry(TR - .06, TR - .06, FILL - TB, 96, 1, false), fuelMat, 0, TB + (FILL - TB) / 2, 0, inT1, false);
const fuelCone = add(new THREE.ConeGeometry(TR - .06, FLOOR_DROP, 96, 1, false), fuelMat, 0, FLOOR_DROP / 2, 0, inT1, false); fuelCone.rotation.x = Math.PI;
fuelBody.renderOrder = 2; fuelCone.renderOrder = 2;
// section faces of the liquid on the cut plane
const fuelCap = add(new THREE.PlaneGeometry(1, 1), fuelCapMat, 0, 0, 0, inT1, false); fuelCap.renderOrder = 3;
const fuelCapTri = add(new THREE.BufferGeometry().setFromPoints([V(-1, 0, 0), V(1, 0, 0), V(0, -1, 0)]), fuelCapMat, 0, 0, 0, inT1, false); fuelCapTri.renderOrder = 3;
// water: inverted cone at the low point + sump pot
const water = add(new THREE.ConeGeometry(1, 1, 64, 1, false), waterMat, 0, 0, 0, inT1, false); water.rotation.x = Math.PI;
const waterCap = add(new THREE.BufferGeometry().setFromPoints([V(-1, 0, 0), V(1, 0, 0), V(0, -1, 0)]), waterCapMat, 0, 0, 0, inT1, false);
add(new THREE.CylinderGeometry(.55, .55, .55, 32, 1, true), floorMat, 0, -.27, 0, inT1, false);
const sumpWater = add(new THREE.CylinderGeometry(.5, .5, .5, 32), waterMat, 0, -.27, 0, inT1, false);
// water drain-off line from the sump to a drain valve in front of the tank
const DRAIN = pipe([[T1.x, -.45, 0], [T1.x, -.45, 10.5], [T1.x, .5, 10.5]], .12, M.dark);
const drainValve = valve(T1.x, .55, 10.5, 'z', .7);
// droplets
const DROP_N = 90;
const dropGeo = new THREE.SphereGeometry(.13, 12, 8);
const dropMat = cut(new THREE.MeshStandardMaterial({ color: 0x55d0c8, emissive: 0x1a7d77, emissiveIntensity: .8, roughness: .2 }));
const drops = new THREE.InstancedMesh(dropGeo, dropMat, DROP_N); drops.frustumCulled = false; inT1.add(drops);
const DROPS = [];
for (let i = 0; i < DROP_N; i++) {
  const a = rand() * Math.PI * 2, r = Math.sqrt(rand()) * (TR - .6);
  let x = Math.cos(a) * r, z = -Math.abs(Math.sin(a) * r) - .25;
  DROPS.push({ x, z, y: TB + .6 + rand() * (FILL - TB - 1.3), t0: rand(), v: .9 + rand() * .9, late: i % 7 === 0 });
}
// floating suction: pivot near the outlet, arm up to a pontoon float
const PIV = V(TR - .7, PIPE_Y, -1.6);
const ARM_L = 9.3;
const armMat = cut(M.dark.clone());
const floatMat = cut(M.coral.clone());
const arm = add(new THREE.CylinderGeometry(.2, .2, ARM_L, 20), armMat, 0, 0, 0, inT1);
const flt = add(new THREE.CylinderGeometry(.42, .42, 2.6, 24), floatMat, 0, 0, 0, inT1); flt.rotation.x = Math.PI / 2;
add(new THREE.SphereGeometry(.32, 16, 12), armMat, PIV.x, PIV.y, PIV.z, inT1);
function floatPos() {
  const fy = FILL - .18, dy = fy - PIV.y, dx = Math.sqrt(ARM_L * ARM_L - dy * dy);
  return V(PIV.x - dx, fy, PIV.z);
}
{
  const fp = floatPos(); const d = fp.clone().sub(PIV);
  arm.position.copy(PIV).addScaledVector(d, .5); arm.quaternion.setFromUnitVectors(V(0, 1, 0), d.clone().normalize());
  flt.position.copy(fp);
}
// issue line from T1 through the pump to the filter water separators
const R3 = pipe([[T1.x + TR - .05, PIPE_Y, -1.6], [-17, PIPE_Y, -1.6], [-17, PIPE_Y, 10], [12.4, PIPE_Y, 10]], .25, M.steel, { supports: true });
valve(-17, PIPE_Y, 4, 'z', 1);

// ------------------------------------------------------------------ QC LAB
const LAB = V(-20, 0, 24);
{
  const g = new THREE.Group(); g.position.copy(LAB); scene.add(g);
  box(10, 3.6, 6, M.white, 0, 1.8, 0, g);
  box(10.4, .25, 6.4, M.dark, 0, 3.72, 0, g);
  for (let i = 0; i < 3; i++) box(1.8, 1.1, .05, M.glass, -3 + i * 2.6, 2.1, 3.02, g);
  box(1.1, 2.2, .05, M.dark, 3.6, 1.1, 3.02, g);
  const sign = add(new THREE.PlaneGeometry(4.2, .6), new THREE.MeshStandardMaterial({ map: canvasTex(840, 120, (c, w, h) => {
    c.fillStyle = '#2a2f34'; c.fillRect(0, 0, w, h); c.fillStyle = '#f3e8cf'; c.font = '700 64px Inter'; c.textAlign = 'center'; c.textBaseline = 'middle';
    c.fillText('QC LABORATORY', w / 2, h / 2 + 3);
  }), roughness: .6 }), -1, 3.2, 3.03, g);
  sign.castShadow = false;
  box(1.6, .6, 1.2, M.steel, -3, 4.1, -1, g); // HVAC
}

// ------------------------------------------------------------------ PUMPS + FILTER WATER SEPARATORS
{ const p = add(new THREE.BoxGeometry(22, .25, 17), M.concrete, 21, .12, 3.5); p.castShadow = false; }
function pump(x, z) {
  const g = new THREE.Group(); g.position.set(x, 0, z); scene.add(g);
  box(3.2, .3, 1.2, M.dark, .4, .4, 0, g);
  const cs = add(new THREE.CylinderGeometry(.62, .62, .55, 32), std(0x3c6f8a, { roughness: .45, metalness: .4 }), -.7, 1.25, 0, g); cs.rotation.x = Math.PI / 2;
  const mo = add(new THREE.CylinderGeometry(.5, .5, 1.7, 32), std(0x3c6f8a, { roughness: .45, metalness: .4 }), 1.0, 1.05, 0, g); mo.rotation.z = Math.PI / 2;
  for (let i = 0; i < 8; i++) { const fn = add(new THREE.BoxGeometry(1.5, .04, .04), M.dark, 1.0, 1.05 + Math.sin(i / 8 * 6.28) * .52, Math.cos(i / 8 * 6.28) * .52, g); }
  return g;
}
pump(13.6, 10); pump(13.6, 6.6);
pipe([[12.4, PIPE_Y, 6.6], [12.0, PIPE_Y, 6.6]], .2);
const R4 = pipe([[12.9, PIPE_Y, 10], [16.5, PIPE_Y, 10], [18.5, PIPE_Y, 10], [18.5, PIPE_Y, 4], [21.2, PIPE_Y, 4]], .22, M.steel, { supports: false });
valve(16.5, PIPE_Y, 10, 'x', .9);

const FWS = V(24, 2.0, 4);
const FL = 5.2, FRAD = .95;
function fws(c, clip) {
  const cp = clip ? [clip] : null;
  const g = new THREE.Group(); g.position.copy(c); scene.add(g);
  const sm = M.shell.clone(); sm.side = THREE.DoubleSide; if (cp) sm.clippingPlanes = cp;
  const st = M.steel.clone(); if (cp) st.clippingPlanes = cp;
  const body = add(new THREE.CylinderGeometry(FRAD, FRAD, FL, 64, 1, true), sm, 0, 0, 0, g); body.rotation.z = Math.PI / 2;
  for (const s of [-1, 1]) { const h = add(new THREE.SphereGeometry(FRAD, 48, 24, 0, Math.PI * 2, 0, Math.PI / 2), sm, s * FL / 2, 0, 0, g); h.rotation.z = -s * Math.PI / 2; h.scale.y = .45; }
  for (const x of [-1.6, 1.6]) box(.35, 1.0, 1.4, M.dark, x, -1.2, 0, g);
  // sump boot + drain
  add(new THREE.CylinderGeometry(.28, .28, .9, 24, 1, true), sm, 1.3, -1.25, 0, g);
  add(new THREE.CylinderGeometry(.28, .28, .04, 24), st, 1.3, -1.7, 0, g);
  pipe([V(1.3, -1.7, 0), V(1.3, -1.95, 0), V(1.3, -1.95, .9)], .05, M.dark, { parent: g });
  // differential pressure gauge on a stand
  pipe([V(-.6, FRAD, 0), V(-.6, FRAD + .7, 0)], .04, M.steel, { parent: g });
  pipe([V(.8, FRAD, 0), V(.8, FRAD + .7, 0), V(-.2, FRAD + .7, 0)], .04, M.steel, { parent: g });
  return g;
}
const fws1 = fws(FWS, clipF1);
const fws2 = fws(V(24, 2.0, -.5), null);
pipe([[18.5, PIPE_Y, 4], [18.5, PIPE_Y, -.5], [21.2, PIPE_Y, -.5]], .2);
// dP gauge dial (on FWS-1, front)
const dialTex = canvasTex(256, 256, (g, w, h) => {
  g.fillStyle = '#f4f4f2'; g.beginPath(); g.arc(128, 128, 124, 0, 7); g.fill();
  g.strokeStyle = '#222'; g.lineWidth = 8; g.stroke();
  for (let i = 0; i <= 10; i++) { const a = Math.PI * (.75 + 1.5 * i / 10); g.lineWidth = i % 5 ? 3 : 6;
    g.beginPath(); g.moveTo(128 + Math.cos(a) * 92, 128 + Math.sin(a) * 92); g.lineTo(128 + Math.cos(a) * 112, 128 + Math.sin(a) * 112); g.stroke(); }
  g.strokeStyle = '#3aaea9'; g.lineWidth = 14; g.beginPath(); g.arc(128, 128, 102, Math.PI * .75, Math.PI * 1.65); g.stroke();
  g.strokeStyle = '#e4705a'; g.beginPath(); g.arc(128, 128, 102, Math.PI * 2.0, Math.PI * 2.25); g.stroke();
  g.fillStyle = '#222'; g.font = '700 30px Inter'; g.textAlign = 'center'; g.fillText('ΔP', 128, 190);
});
const dial = new THREE.Group(); dial.position.set(FWS.x + .3, FWS.y + FRAD + .9, FWS.z + .02); scene.add(dial);
{ const d = add(new THREE.CylinderGeometry(.32, .32, .12, 32), M.dark, 0, 0, 0, dial); d.rotation.x = Math.PI / 2;
  const f = add(new THREE.CircleGeometry(.29, 32), new THREE.MeshBasicMaterial({ map: dialTex }), 0, 0, .065, dial, false); }
const needle = add(new THREE.BoxGeometry(.03, .22, .01), new THREE.MeshBasicMaterial({ color: 0x111111 }), 0, 0, .075, dial, false);
needle.geometry.translate(0, .1, 0);
// FWS-1 internals
const inF = new THREE.Group(); inF.position.copy(FWS); scene.add(inF);
const fCut = (m) => { m.clippingPlanes = [clipF1]; return m; };
const fFuel = add(new THREE.CylinderGeometry(FRAD - .04, FRAD - .04, FL - .1, 48), fCut(new THREE.MeshStandardMaterial({ color: C.amber, transparent: true, opacity: .25, emissive: 0x5a3500, emissiveIntensity: .3, depthWrite: false, side: THREE.DoubleSide })), 0, 0, 0, inF, false);
fFuel.rotation.z = Math.PI / 2; fFuel.renderOrder = 2;
add(new THREE.CylinderGeometry(FRAD - .03, FRAD - .03, .06, 48), fCut(M.steel.clone()), -1.75, 0, 0, inF).rotation.z = Math.PI / 2;
add(new THREE.CylinderGeometry(FRAD - .03, FRAD - .03, .06, 48), fCut(M.steel.clone()), .45, 0, 0, inF).rotation.z = Math.PI / 2;
const coalMat = fCut(std(0xf0ece2, { roughness: .9 }));
const sepMat = fCut(std(C.teal, { roughness: .55, metalness: .2 }));
const COAL = [], SEPS = [];
for (let i = 0; i < 6; i++) { const a = i / 6 * Math.PI * 2 + .3; const y = Math.cos(a) * .48, z = Math.sin(a) * .48;
  const e = add(new THREE.CylinderGeometry(.15, .15, 2.0, 20), coalMat, -.72, y, z, inF); e.rotation.z = Math.PI / 2; COAL.push(V(.3, y, z)); }
for (let i = 0; i < 3; i++) { const a = i / 3 * Math.PI * 2 + .9; const y = Math.cos(a) * .4 + .15, z = Math.sin(a) * .4;
  const e = add(new THREE.CylinderGeometry(.2, .2, 1.4, 20), sepMat, 1.25, y, z, inF); e.rotation.z = Math.PI / 2; SEPS.push(V(1.25, y, z)); }
const fwsWater = add(new THREE.CylinderGeometry(.25, .25, 1, 24), fCut(waterMat.clone()), 1.3, -1.6, 0, inF, false);
const FD_N = 24;
const fDrops = new THREE.InstancedMesh(new THREE.SphereGeometry(.06, 10, 8), fCut(dropMat.clone()), FD_N); fDrops.frustumCulled = false; inF.add(fDrops);
const FDROPS = Array.from({ length: FD_N }, (_, i) => ({ ph: i / FD_N, c: COAL[i % COAL.length], z: -.1 - rand() * .6 }));

// ------------------------------------------------------------------ HYDRANT + APRON + AIRCRAFT
const R5 = pipe([[FWS.x + FL / 2 + .4, PIPE_Y, 4], [31, PIPE_Y, 4], [31, -1.6, 4], [82, -1.6, 4], [82, -1.6, 10.5], [82, -.25, 10.5]], .3, M.steel);
valve(29.5, PIPE_Y, 4, 'x', .9);
const apronMat = std(C.apron, { roughness: .92, transparent: true });
{ const a = add(new THREE.PlaneGeometry(90, 70), apronMat, 100, .03, 0); a.rotation.x = -Math.PI / 2; a.castShadow = false; }
for (let x = 38; x < 80; x += 9) { add(new THREE.CylinderGeometry(.09, .09, .9, 8), M.rail, x, .45, 5.5); box(.4, .25, .05, M.rail, x, .95, 5.5); }
const lineMat = new THREE.MeshBasicMaterial({ color: 0xc9a23f });
{ const l = add(new THREE.PlaneGeometry(70, .3), lineMat, 100, .05, 0, scene, false); l.rotation.x = -Math.PI / 2; }
const PIT = V(82, 0, 10.5);
box(1.0, .06, 1.0, M.dark, PIT.x, .06, PIT.z);
add(new THREE.CylinderGeometry(.2, .2, .3, 16), M.coral, PIT.x, .2, PIT.z);
// hydrant dispenser vehicle
const DISP = V(84.6, 0, 13.4);
{
  const g = new THREE.Group(); g.position.copy(DISP); scene.add(g);
  const body = std(0xe8e9ea, { roughness: .5, metalness: .2 });
  box(6.4, .5, 2.3, M.dark, 0, .75, 0, g);
  box(1.9, 1.7, 2.2, body, -2.3, 1.85, 0, g);
  box(.9, .6, 2.05, M.glass, -3.12, 2.2, 0, g);
  box(4.2, .7, 2.2, body, 1.05, 1.35, 0, g);
  for (const [wx, wz] of [[-2.2, 1.1], [-2.2, -1.1], [2.0, 1.1], [2.0, -1.1]]) { const w = add(new THREE.CylinderGeometry(.48, .48, .35, 24), M.rubber, wx, .48, wz, g); w.rotation.x = Math.PI / 2; }
  add(new THREE.CylinderGeometry(.45, .45, 1.5, 32), M.white, .2, 2.45, -.3, g); // filter vessel
  add(new THREE.CylinderGeometry(.47, .47, .12, 32), M.dark, .2, 3.25, -.3, g);
  box(1.5, .1, 1.6, M.steel, 2.4, 2.75, .1, g); // elevating platform
  for (const [px, pz] of [[1.7, .9], [3.1, .9], [1.7, -.7], [3.1, -.7]]) add(new THREE.CylinderGeometry(.03, .03, 1.0, 6), M.rail, px, 3.25, pz, g);
  const r1 = add(new THREE.TorusGeometry(.7, .03, 6, 4, Math.PI * 2), M.rail, 2.4, 3.75, .1, g); r1.rotation.set(Math.PI / 2, 0, Math.PI / 4); r1.scale.set(1, 1.15, 1);
  box(.3, .25, .3, M.coral, -1.4, 1.95, 1.12, g); // deadman / control box
}
const DFILT = V(DISP.x + .2, 3.3, DISP.z - .3);
function hose(pts, r = .09) {
  const cv = new THREE.CatmullRomCurve3(pts.map(p => V(...p)));
  add(new THREE.TubeGeometry(cv, 60, r, 12), M.rubber); return cv;
}
const H1 = hose([[PIT.x, .3, PIT.z], [PIT.x + .6, .25, PIT.z + 1.0], [DISP.x - 1.6, .3, DISP.z - 1.25], [DISP.x - 1.2, .9, DISP.z - 1.15]]);
// aircraft (nose toward -x, left wing toward +z / camera)
const AC = V(84, 0, 0);
const COUP = V(AC.x + 4.2, 2.62, 9.6);
{
  const g = new THREE.Group(); g.position.copy(AC); scene.add(g);
  const fus = add(new THREE.CylinderGeometry(2.35, 2.35, 34, 64), M.white, 1, 3.7, 0, g); fus.rotation.z = Math.PI / 2;
  const belly = add(new THREE.CylinderGeometry(2.37, 2.37, 33.6, 64, 1, true, Math.PI * .65, Math.PI * .7), M.belly, 1, 3.7, 0, g); belly.rotation.z = Math.PI / 2;
  const nose = add(new THREE.SphereGeometry(2.35, 48, 24, 0, Math.PI * 2, 0, Math.PI / 2), M.white, -16, 3.7, 0, g); nose.rotation.z = Math.PI / 2; nose.scale.y = 1.35;
  box(.05, .55, 2.6, M.glass, -19.0, 4.55, 0, g).rotation.z = -.5;
  const tc = add(new THREE.ConeGeometry(2.35, 8, 48), M.white, 22, 4.2, 0, g); tc.rotation.z = -Math.PI / 2; tc.scale.set(1, 1, .9);
  for (let i = 0; i < 26; i++) box(.06, .32, .25, M.glass, -12 + i * 1.1, 4.35, 2.3, g);
  for (let i = 0; i < 26; i++) box(.06, .32, .25, M.glass, -12 + i * 1.1, 4.35, -2.3, g);
  // wings (swept), extruded planform
  const wingShape = (s) => { const sh = new THREE.Shape(); sh.moveTo(-3.5, 1.8 * s); sh.lineTo(5.5, 1.8 * s); sh.lineTo(10.2, 18.5 * s); sh.lineTo(8.0, 18.5 * s); sh.closePath(); return sh; };
  for (const s of [1, -1]) {
    const geo = new THREE.ExtrudeGeometry(wingShape(s), { depth: .42, bevelEnabled: true, bevelThickness: .08, bevelSize: .08, bevelSegments: 2 });
    const wm = add(geo, M.white, 0, 0, 0, g); wm.rotation.x = Math.PI / 2; wm.position.y = 3.05;
    // engine + pylon
    const en = add(new THREE.CylinderGeometry(1.05, .95, 4.2, 40), std(0xd9dcdf, { roughness: .4, metalness: .35 }), -1.6, 1.85, 6.3 * s, g); en.rotation.z = Math.PI / 2;
    const inl = add(new THREE.TorusGeometry(1.0, .09, 10, 40), M.steel, -3.7, 1.85, 6.3 * s, g); inl.rotation.y = Math.PI / 2;
    const ic = add(new THREE.CircleGeometry(.95, 32), M.dark, -3.68, 1.85, 6.3 * s, g, false); ic.rotation.y = -Math.PI / 2;
    box(2.4, .9, .3, M.white, -.4, 2.6, 6.3 * s, g);
    // main gear
    add(new THREE.CylinderGeometry(.12, .12, 1.4, 10), M.steel, 4.6, 1.5, 3.3 * s, g);
    for (const dx of [-.5, .5]) { const w = add(new THREE.CylinderGeometry(.55, .55, .4, 24), M.rubber, 4.6 + dx, .55, 3.3 * s, g); w.rotation.x = Math.PI / 2; }
    // horizontal stabiliser
    const hs = new THREE.Shape(); hs.moveTo(18, 1.0 * s); hs.lineTo(22, 1.0 * s); hs.lineTo(24.4, 7.2 * s); hs.lineTo(23.0, 7.2 * s); hs.closePath();
    const hm = add(new THREE.ExtrudeGeometry(hs, { depth: .25, bevelEnabled: false }), M.white, 0, 0, 0, g); hm.rotation.x = Math.PI / 2; hm.position.y = 4.9;
  }
  const fin = new THREE.Shape(); fin.moveTo(15.5, 5.6); fin.lineTo(22.5, 5.6); fin.lineTo(25.2, 13.2); fin.lineTo(22.6, 13.2); fin.closePath();
  const fm = add(new THREE.ExtrudeGeometry(fin, { depth: .35, bevelEnabled: false }), M.tail, 0, 0, -.17, g);
  add(new THREE.CylinderGeometry(.1, .1, 1.6, 10), M.steel, -13.5, 1.3, 0, g);
  const nw = add(new THREE.CylinderGeometry(.42, .42, .3, 20), M.rubber, -13.5, .45, 0, g); nw.rotation.x = Math.PI / 2;
  // refuel coupling adaptor under left wing
  add(new THREE.CylinderGeometry(.16, .16, .35, 16), M.coral, COUP.x - AC.x, COUP.y + .1, COUP.z, g);
}
const H2 = hose([[DISP.x + 2.2, 2.9, DISP.z - .5], [DISP.x + 2.6, 3.6, DISP.z - 1.6], [COUP.x + .2, 3.1, COUP.z + 1.4], [COUP.x, 2.45, COUP.z]], .1);

// ------------------------------------------------------------------ flow overlays
const F = {
  r1: flow(R1, .3, C.amber), r2: flow(R2, .25, C.amber),
  r2a: flow([[-26, PIPE_Y, -11.5], [-26, PIPE_Y, -7]], .22, C.amber), r2b: flow([[-8, PIPE_Y, -11.5], [-8, PIPE_Y, -7]], .22, C.amber),
  arm: flow([floatPos().add(T1), PIV.clone().add(T1), V(T1.x + TR, PIPE_Y, -1.6)], .2, C.amber),
  r3: flow(R3, .25, C.amber), r4: flow(R4, .22, C.amber),
  fws: flow([[FWS.x - FL / 2 - .2, FWS.y, FWS.z], [FWS.x + FL / 2 + .2, FWS.y, FWS.z]], .14, C.amber),
  r5: flow(R5, .3, C.amber),
  h1: flow(H1.getPoints(40), .09, C.amber), h2: flow(H2.getPoints(40), .1, C.amber),
  drain: flow(DRAIN, .12, C.teal),
};

// ------------------------------------------------------------------ camera path (non-uniform Catmull-Rom)
const K = [
  [0.0, [-110, 70, 130], [-8, 0, 0]],
  [S.receipt - 1.8, [-55, 52, 100], [0, 0, 2]],
  [S.receipt + 1.6, [-86, 10, 32], [-66, 2, 6]],
  [SEN.receipt[2], [-63, 7.5, 24], [-55, 2.6, 6]],
  [S.storage - .6, [-49, 8.5, 25], [-52.5, 2.4, 6.5]],
  [S.storage + 2.2, [-26, 11.5, 42], [-26, 6, 0]],
  [SEN.storage[2] + .4, [-25, 8, 34], [-26, 4, 0]],
  [S.release - .3, [-24.5, 4.8, 24], [-26, 1.4, 0]],
  [S.release + 2.6, [-4, 17, 50], [-18, 4, 10]],
  [S.filtration - .2, [-8, 15, 46], [-19.5, 4, 10]],
  [SEN.filtration[1] + .8, [-19, 10, 30], [-24, 6.5, -1.2]],
  [SEN.filtration[2] + .2, [2, 9, 28], [12, 2, 8]],
  [SEN.filtration[2] + 2.0, [20.6, 5.0, 14.6], [24, 1.8, 3.4]],
  [S.delivery - .2, [19.4, 4.4, 12.6], [24.2, 1.9, 3.4]],
  [SEN.delivery[1] + .8, [42, 13, 28], [55, -1.2, 5]],
  [SEN.delivery[1] + 4.2, [66, 9.5, 33], [82, 2, 10]],
  [S.control - .4, [74.5, 6.2, 27.5], [85.5, 2.4, 10.5]],
  [SEN.control[1] - .6, [26, 82, 138], [24, 0, 3]],
  [END, [24, 96, 150], [24, 0, 3]],
].map(([t, p, q]) => ({ t, p: V(...p), q: V(...q) }));
function hermite(key, t) {
  let i = 0; while (i < K.length - 2 && t > K[i + 1].t) i++;
  const a = K[i], b = K[i + 1], pa = K[Math.max(0, i - 1)], pb = K[Math.min(K.length - 1, i + 2)];
  const dt = b.t - a.t, u = clamp((t - a.t) / dt);
  const ma = a === pa ? V(0, 0, 0) : b[key].clone().sub(pa[key]).multiplyScalar(dt / (b.t - pa.t));
  const mb = b === pb ? V(0, 0, 0) : pb[key].clone().sub(a[key]).multiplyScalar(dt / (pb.t - a.t));
  const u2 = u * u, u3 = u2 * u;
  return a[key].clone().multiplyScalar(2 * u3 - 3 * u2 + 1).add(ma.multiplyScalar(u3 - 2 * u2 + u))
    .add(b[key].clone().multiplyScalar(-2 * u3 + 3 * u2)).add(mb.multiplyScalar(u3 - u2));
}

// ------------------------------------------------------------------ per-frame state
function waterLevel(t) {
  // grows as droplets arrive, shrinks when drained
  return .14 + .36 * ss(t, SEN.storage[2] + .2, SEN.storage[2] + 3.6) - .38 * ss(t, SEN.storage[2] + 3.9, S.release + .2);
}
function updateScene(t) {
  // camera
  const p = hermite('p', t), q = hermite('q', t);
  camera.position.copy(p); camera.lookAt(q); camera.updateMatrixWorld();
  // shadow frustum follows the subject
  const span = clamp(p.distanceTo(q) * .55, 22, 110);
  sun.position.copy(q).addScaledVector(SUN_DIR, 120); sun.target.position.copy(q);
  Object.assign(sun.shadow.camera, { left: -span, right: span, top: span, bottom: -span, near: 1, far: 300 });
  sun.shadow.camera.updateProjectionMatrix();

  // ---- T1 cutaway (open at storage, stays open through filtration, closes for delivery)
  const cutK = ss(t, S.storage + .6, S.storage + 2.4) * (1 - ss(t, S.delivery + 1.5, S.delivery + 3.5));
  const c = (1 - cutK) * (TR + .8);
  clipT1.constant = T1.z + c;
  const capA = ss(cutK, .92, 1);
  const chord = c < TR ? 2 * Math.sqrt(TR * TR - c * c) - .12 : 0;
  fuelCap.position.set(0, TB + (FILL - TB) / 2, c - .01); fuelCap.scale.set(chord, FILL - TB, 1);
  fuelCapTri.position.set(0, TB, c - .01); fuelCapTri.scale.set(chord / 2, FLOOR_DROP, 1);
  fuelCapMat.opacity = .26 * capA;
  const hw = waterLevel(t), rw = hw / FLOOR_DROP * TR;
  water.scale.set(rw, hw, rw); water.position.set(0, hw / 2, 0);
  waterCap.position.set(0, hw, c - .015); waterCap.scale.set(rw, hw, 1); waterCapMat.opacity = capA;
  sumpWater.scale.y = clamp(hw / .2, .15, 1);
  [inT1].forEach(g => g.visible = cutK > .01);
  // droplets: appear (water coming out of solution), sink, slide to the sump
  const tAppear = S.storage + 1.2, tSink = SEN.storage[2] + .1;
  const dm = new THREE.Matrix4();
  for (let i = 0; i < DROP_N; i++) {
    const d = DROPS[i]; let x = d.x, z = d.z, y = d.y, s = ss(t, tAppear + d.t0 * 1.5, tAppear + d.t0 * 1.5 + .4);
    const t0 = tSink + d.t0 * .8 + (d.late ? 2.2 : 0);
    if (t > t0) {
      const r0 = Math.hypot(x, z), floorY = FLOOR_DROP * r0 / TR + .1;
      const fall = (y - floorY) / (5.0 * d.v);
      const u = (t - t0);
      if (u < fall) y = y - (y - floorY) * (u / fall) ** 1.6;
      else { const k = clamp((u - fall) / .9); x *= 1 - k; z *= 1 - k; y = FLOOR_DROP * Math.hypot(x, z) / TR + .1; s *= 1 - ss(k, .7, 1); }
    }
    dm.compose(V(x, y, z), new THREE.Quaternion(), V(s, s * 1.15, s).multiplyScalar(s > .001 ? 1 : 0));
    drops.setMatrixAt(i, dm);
  }
  drops.instanceMatrix.needsUpdate = true;
  drops.visible = t > tAppear && t < S.release + 1;

  // ---- FWS-1 cutaway
  const fK = ss(t, SEN.filtration[2] + 1.0, SEN.filtration[2] + 2.4) * (1 - ss(t, S.control - 1, S.control + 1));
  clipF1.constant = FWS.z + (1 - fK) * (FRAD + .6);
  inF.visible = fK > .01;
  for (let i = 0; i < FD_N; i++) {
    const d = FDROPS[i]; const ph = ((t * .45) + d.ph) % 1;
    let pos, s;
    if (ph < .45) { const u = ph / .45; pos = V(.3 + .2 * u, d.c.y * (1 - u * .2), Math.min(d.c.z, -.05) - .05); s = .6 + 1.4 * u; }
    else { const u = (ph - .45) / .55; pos = V(.5 + .8 * u, d.c.y * .8 * (1 - u) + (-1.1) * u * u, -.15); s = 2.0; }
    dm.compose(pos, new THREE.Quaternion(), V(s, s, s).multiplyScalar(fK));
    fDrops.setMatrixAt(i, dm);
  }
  fDrops.instanceMatrix.needsUpdate = true;
  fwsWater.scale.y = .25 + .2 * ss(t, SEN.filtration[2], S.delivery); fwsWater.position.y = -1.7 + fwsWater.scale.y / 2;
  needle.rotation.z = -(Math.PI * (-.25 + .38 * ss(t, SEN.filtration[2] + 3.0, SEN.filtration[2] + 4.5)) - Math.PI / 2) + Math.PI;

  // ---- ground goes translucent to show the buried hydrant main
  const xr = ss(t, S.delivery + .4, SEN.delivery[1] + .6) * (1 - ss(t, S.control + 1, S.control + 3)) + .55 * ss(t, SEN.control[1] - 1, SEN.control[1] + 1);
  groundMat.opacity = 1 - .6 * xr; groundMat.depthWrite = xr < .05; apronMat.opacity = 1 - .5 * xr; apronMat.depthWrite = xr < .05;

  // ---- flows
  const allOn = ss(t, SEN.control[1] - .6, SEN.control[1] + 1.4);
  const on = (a, b) => Math.max(allOn, win(t, a, b, .5));
  setFlow(F.r1, on(SEN.receipt[1] - .2, S.storage + 1.0), t);
  setFlow(F.r2, on(SEN.receipt[2], S.storage + 1.6), t, 3, ss(t, SEN.receipt[2], SEN.receipt[2] + 2.5) + allOn);
  setFlow(F.r2a, on(SEN.receipt[2] + 1.5, S.storage + 1.6), t); setFlow(F.r2b, Math.max(allOn * 0, win(t, SEN.receipt[2] + 1.5, S.storage + 1.6, .5)), t);
  setFlow(F.arm, Math.max(allOn * cutK, win(t, SEN.filtration[1] + .3, SEN.filtration[2] + 2.5, .6)), t, 2);
  setFlow(F.r3, on(SEN.filtration[1] + 1.4, SEN.filtration[2] + 3.0), t, 3, ss(t, SEN.filtration[1] + 1.4, SEN.filtration[2] + 1.6) + allOn);
  setFlow(F.r4, on(SEN.filtration[2] - .2, S.delivery + 1), t);
  setFlow(F.fws, on(SEN.filtration[2] + 1.2, S.delivery + 1.2), t, 1.6);
  setFlow(F.r5, on(S.delivery + .2, S.control + .6), t, 3.5, ss(t, S.delivery + .2, SEN.delivery[1] + 3) + allOn);
  setFlow(F.h1, on(SEN.delivery[1] + 2.4, S.control + .6), t, 2);
  setFlow(F.h2, on(SEN.delivery[1] + 3.6, S.control + .6), t, 2);
  setFlow(F.drain, win(t, SEN.storage[2] + 3.6, S.release + 1.0, .4), t, 2);
  drainValve.children[2].rotation.z = ss(t, SEN.storage[2] + 3.3, SEN.storage[2] + 3.8) * Math.PI / 2;

  // float pulses when narrated
  floatMat.emissive = new THREE.Color(C.coral); floatMat.emissiveIntensity = .5 * win(t, SEN.filtration[1], SEN.filtration[2], .4);
}

// ------------------------------------------------------------------ 2D overlay
const out = document.getElementById('out');
const g2 = out.getContext('2d');
const FONT = 'Inter';
const COL = { cream: '#f3e8cf', amber: '#e3a83a', teal: '#5cc9c3', coral: '#e4705a', dim: 'rgba(243,232,207,0.62)', panel: 'rgba(17,20,23,0.84)', line: 'rgba(243,232,207,0.85)' };
function proj(v) { const p = v.clone().project(camera); return { x: (p.x + 1) / 2 * W, y: (1 - p.y) / 2 * H, ok: p.z < 1 }; }
function rr(x, y, w, h, r) { g2.beginPath(); g2.roundRect(x, y, w, h, r); }
function text(s, x, y, size, weight = 500, color = COL.cream, align = 'left', alpha = 1, track = 0) {
  g2.globalAlpha = alpha; g2.fillStyle = color; g2.font = `${weight} ${size}px ${FONT}`; g2.textAlign = align; g2.textBaseline = 'alphabetic';
  if (track) g2.letterSpacing = `${track}px`; else g2.letterSpacing = '0px';
  g2.fillText(s, x, y); g2.globalAlpha = 1; g2.letterSpacing = '0px';
}
function tw(s, size, weight = 500, track = 0) { g2.font = `${weight} ${size}px ${FONT}`; g2.letterSpacing = `${track}px`; const w = g2.measureText(s).width; g2.letterSpacing = '0px'; return w; }

// leader-line callout anchored to a 3D point
function callout(t, t0, t1, anchor, dx, dy, title, sub, color = COL.cream) {
  const a = win(t, t0, t1, .45); if (a <= 0) return;
  const p = proj(anchor); if (!p.ok) return;
  const wlab = Math.max(tw(title, 27, 650), sub ? tw(sub, 21, 450) : 0) + 30;
  if (dx >= 0 && p.x + dx + wlab > 1860) dx = -Math.abs(dx);
  else if (dx < 0 && p.x + dx - wlab < 60) dx = Math.abs(dx);
  if (p.y + dy < 270) dy = 270 - p.y;
  if (p.y + dy > 880) dy = 880 - p.y;
  const k = ss(t, t0, t0 + .55), kt = ss(t, t0 + .35, t0 + .8) * (1 - ss(t, t1 - .45, t1));
  const ex = p.x + dx, ey = p.y + dy, mx = p.x + dx * .35;
  g2.globalAlpha = a; g2.strokeStyle = COL.line; g2.lineWidth = 2;
  g2.beginPath(); g2.arc(p.x, p.y, 6, 0, 7); g2.fillStyle = color; g2.fill();
  g2.beginPath(); g2.arc(p.x, p.y, 11, 0, 7); g2.globalAlpha = a * .5; g2.stroke(); g2.globalAlpha = a;
  // path: anchor -> elbow -> end, drawn progressively
  const L1 = Math.hypot(mx - p.x, ey - p.y), L2 = Math.abs(ex - mx), tot = L1 + L2, d = tot * k;
  g2.beginPath(); g2.moveTo(p.x, p.y);
  if (d <= L1) g2.lineTo(p.x + (mx - p.x) * d / L1, p.y + (ey - p.y) * d / L1);
  else { g2.lineTo(mx, ey); g2.lineTo(mx + Math.sign(dx) * (d - L1), ey); }
  g2.stroke();
  const al = dx >= 0 ? 'left' : 'right', tx = ex + (dx >= 0 ? 14 : -14);
  const bw = Math.max(tw(title, 27, 650), sub ? tw(sub, 21, 450) : 0) + 24, bh = sub ? 78 : 46;
  g2.globalAlpha = kt * .78; g2.fillStyle = 'rgba(17,20,23,0.8)';
  rr(dx >= 0 ? tx - 10 : tx - bw + 10, ey - 25, bw, bh, 6); g2.fill(); g2.globalAlpha = 1;
  text(title, tx, ey + 9, 27, 650, COL.cream, al, kt);
  if (sub) text(sub, tx, ey + 42, 21, 450, COL.dim, al, kt);
  g2.globalAlpha = 1;
}
function panel(x, y, w, h, a) { g2.globalAlpha = a; g2.fillStyle = COL.panel; rr(x, y, w, h, 10); g2.fill(); g2.strokeStyle = 'rgba(243,232,207,0.18)'; g2.lineWidth = 1.5; g2.stroke(); g2.globalAlpha = 1; }
function tick(x, y, s, prog, color = COL.teal, a = 1) {
  if (prog <= 0) return; g2.globalAlpha = a; g2.strokeStyle = color; g2.lineWidth = 4; g2.lineCap = 'round'; g2.lineJoin = 'round';
  const P = [[x - .5 * s, y], [x - .12 * s, y + .38 * s], [x + .55 * s, y - .45 * s]];
  const L = [Math.hypot(P[1][0] - P[0][0], P[1][1] - P[0][1]), Math.hypot(P[2][0] - P[1][0], P[2][1] - P[1][1])];
  let d = (L[0] + L[1]) * prog; g2.beginPath(); g2.moveTo(...P[0]);
  if (d <= L[0]) g2.lineTo(P[0][0] + (P[1][0] - P[0][0]) * d / L[0], P[0][1] + (P[1][1] - P[0][1]) * d / L[0]);
  else { g2.lineTo(...P[1]); d -= L[0]; g2.lineTo(P[1][0] + (P[2][0] - P[1][0]) * d / L[1], P[1][1] + (P[2][1] - P[1][1]) * d / L[1]); }
  g2.stroke(); g2.globalAlpha = 1; g2.lineCap = 'butt';
}

const STEPS = [['receipt', 'RECEIPT'], ['storage', 'STORAGE & SETTLING'], ['release', 'RELEASE'], ['filtration', 'FILTRATION'], ['delivery', 'DELIVERY']];
function chrome(t) {
  // title block (overview)
  const ta = win(t, .4, S.receipt - .3, .8);
  if (ta > 0) {
    text('JIG 2 · AIRPORT DEPOT OPERATIONS', 120, 150, 22, 600, COL.amber, 'left', ta, 3);
    text('Jet A-1 Fuel Farm', 120, 222, 66, 700, COL.cream, 'left', ta);
    text('From pipeline to wing: five controlled steps', 120, 268, 28, 400, COL.dim, 'left', ta);
    g2.globalAlpha = ta; g2.fillStyle = COL.amber; g2.fillRect(120, 290, 120 * ss(t, .6, 1.8), 4); g2.globalAlpha = 1;
  }
  // step chip + tracker
  let cur = -1; STEPS.forEach(([k], i) => { if (t >= S[k] - .2) cur = i; });
  const ca = ss(t, S.receipt - .2, S.receipt + .4) * (1 - ss(t, S.control - .3, S.control + .5));
  if (cur >= 0 && ca > 0) {
    const [k, name] = STEPS[cur];
    const sa = ca * ss(t, S[k] - .2, S[k] + .35);
    text(`STEP 0${cur + 1}`, 120, 140, 22, 700, COL.amber, 'left', sa, 4);
    text(name, 120, 192, 46, 700, COL.cream, 'left', sa, 1);
    g2.globalAlpha = sa; g2.fillStyle = COL.amber; g2.fillRect(120, 212, 72, 4); g2.globalAlpha = 1;
    // tracker (top right)
    const x0 = 1800 - 5 * 172;
    panel(x0 - 22, 96, 5 * 172 + 30, 76, ca * .75);
    for (let i = 0; i < 5; i++) {
      const x = x0 + i * 172; const done = i < cur, act = i === cur;
      g2.globalAlpha = ca; g2.fillStyle = act ? COL.amber : done ? 'rgba(243,232,207,0.75)' : 'rgba(243,232,207,0.22)';
      g2.fillRect(x, 118, 160, 4);
      text(`0${i + 1}`, x, 150, 20, 700, act ? COL.amber : done ? COL.cream : 'rgba(243,232,207,0.4)', 'left', ca, 2);
      text(STEPS[i][1].split(' ')[0], x + 36, 150, 18, 500, act ? COL.cream : 'rgba(243,232,207,0.45)', 'left', ca, 1);
    }
  }
}

function captions(t) {
  const c = TL.captions.find(c => t >= c.t0 - .1 && t <= c.t1 + .3);
  if (!c) return;
  const a = ss(t, c.t0 - .1, c.t0 + .05) * (1 - ss(t, c.t1 + .15, c.t1 + .3));
  const size = 36, maxW = 1400;
  // wrap to <= 2 lines
  const words = c.text.split(' '); let lines = [c.text];
  if (tw(c.text, size, 500) > maxW) {
    let best = null;
    for (let i = 1; i < words.length; i++) { const l = words.slice(0, i).join(' '), r = words.slice(i).join(' ');
      const m = Math.max(tw(l, size, 500), tw(r, size, 500)); if (!best || m < best[0]) best = [m, [l, r]]; }
    lines = best[1];
  }
  const w = Math.max(...lines.map(l => tw(l, size, 500))) + 56, h = lines.length * 48 + 30;
  const y = 1012 - h;
  panel(960 - w / 2, y, w, h, a * .92);
  lines.forEach((l, i) => text(l, 960, y + 52 + i * 48, size, 500, COL.cream, 'center', a));
}

function overlays(t) {
  const P = (x, y, z) => V(x, y, z);
  // overview: station markers
  STEPS.forEach(([k, name], i) => {
    const pts = [P(-55, 5.2, 6), P(-26, 16.5, 0), P(-20, 5.0, 24), P(24, 4.2, 4), P(84.6, 4.5, 13.4)];
    const a = win(t, 3.0 + i * .45, S.receipt - .6, .4); if (a <= 0) return;
    const p = proj(pts[i]);
    g2.globalAlpha = a; g2.strokeStyle = COL.amber; g2.lineWidth = 2; g2.beginPath(); g2.moveTo(p.x, p.y); g2.lineTo(p.x, p.y - 46); g2.stroke();
    g2.fillStyle = COL.amber; g2.beginPath(); g2.arc(p.x, p.y, 5, 0, 7); g2.fill();
    const lab = `0${i + 1}  ${name.split(' ')[0]}`; const w = tw(lab, 20, 650, 1) + 26;
    g2.fillStyle = COL.panel; rr(p.x - w / 2, p.y - 86, w, 38, 6); g2.fill();
    text(lab, p.x, p.y - 60, 20, 650, COL.cream, 'center', a, 1); g2.globalAlpha = 1;
  });

  // ---- RECEIPT
  const r = SEN.receipt;
  callout(t, r[1] + .2, S.storage + .2, P(-78, PIPE_Y + .3, 6), -40, -150, 'Cross-country pipeline', 'Jet A-1 batch from refinery');
  {
    const a = win(t, r[1] + .8, S.storage - .2, .5);
    if (a > 0) {
      const x = 1290, y = 300, w = 510, h = 300; panel(x, y, w, h, a);
      text('CERTIFICATE OF QUALITY', x + 30, y + 48, 20, 700, COL.amber, 'left', a, 3);
      text('Jet A-1 · DEF STAN 91-091 / AFQRJOS', x + 30, y + 86, 23, 600, COL.cream, 'left', a);
      const rows = [['Batch', '0427'], ['Density @ 15 °C', '801.4 kg/m³'], ['Freezing point', '−51 °C'], ['Flash point', '42 °C']];
      rows.forEach(([k, v], i) => { const yy = y + 134 + i * 38; const ra = a * ss(t, r[1] + 1.0 + i * .2, r[1] + 1.4 + i * .2);
        text(k, x + 30, yy, 22, 450, COL.dim, 'left', ra); text(v, x + w - 30, yy, 22, 600, COL.cream, 'right', ra); });
      g2.globalAlpha = a; g2.fillStyle = 'rgba(243,232,207,0.15)'; g2.fillRect(x + 30, y + 104, w - 60, 1); g2.globalAlpha = 1;
    }
  }
  callout(t, r[2] + .1, S.storage + .2, P(-55, 3.6, 6), -60, -160, 'Receipt filtration', 'Removes water and particulates on intake');
  callout(t, r[2] + 1.5, S.storage + .2, P(SP.x + .2, 1.4, SP.z + .1), 110, 120, 'Sample point', 'Density vs certificate · Δ ≤ 3.0 kg/m³', COL.amber);

  // ---- STORAGE
  const s = SEN.storage, T = (x, y, z) => P(T1.x + x, y, T1.z + z);
  callout(t, s[1] + .1, S.release + .6, T(-5.6, .48, -.4), -120, 90, 'Cone-down floor', 'Low point at the tank centre');
  callout(t, s[1] + 1.0, S.release + .6, T(-4.2, 11.0, -3.5), -170, -70, 'Epoxy-lined shell', 'Fixed roof · free-vent');
  callout(t, s[2] + .1, S.release + .6, T(4, 6, -1), 200, -60, 'Jet A-1', 'ρ 775–840 kg/m³', COL.amber);
  callout(t, s[2] + .8, S.release + .6, T(.9, .14, -.3), 230, 70, 'Free water', 'ρ ≈ 1000 kg/m³', COL.teal);
  callout(t, s[2] + 3.6, S.release + .6, P(T1.x, .7, 10.5), 150, 70, 'Water drain-off', 'Sump drained to slops', COL.teal);

  // ---- RELEASE
  const rl = SEN.release;
  callout(t, S.release + .5, S.filtration - .2, P(LAB.x - 1, 3.9, LAB.z), -80, -150, 'Quality control laboratory', null);
  {
    const a = win(t, rl[1] - .2, S.filtration - .1, .5);
    if (a > 0) {
      const x = 1250, y = 250, w = 560, h = 420; panel(x, y, w, h, a);
      text('RECERTIFICATION TEST · T-101', x + 30, y + 48, 20, 700, COL.amber, 'left', a, 3);
      const rows = [['Settling period', 'Complete'], ['Appearance', 'Clear & bright'], ['Free water (detector)', 'Pass'], ['Density @ 15 °C', '801.2 kg/m³ (Δ 0.2)']];
      rows.forEach(([k, v], i) => { const yy = y + 104 + i * 54; const t0 = rl[1] + .4 + i * .55; const ra = a * ss(t, t0, t0 + .3);
        text(k, x + 30, yy, 23, 450, COL.dim, 'left', ra); text(v, x + w - 74, yy, 23, 600, COL.cream, 'right', ra);
        tick(x + w - 42, yy - 8, 22, ss(t, t0 + .2, t0 + .5), COL.teal, a); });
      g2.globalAlpha = a; g2.fillStyle = 'rgba(243,232,207,0.15)'; g2.fillRect(x + 30, y + 318, w - 60, 1); g2.globalAlpha = 1;
      const st = ss(t, rl[1] + 3.0, rl[1] + 3.35);
      text('Authorised signatory', x + 30, y + 360, 20, 450, COL.dim, 'left', a);
      if (st > 0) {
        const sc = 1 + .35 * (1 - st);
        g2.save(); g2.translate(x + w - 135, y + 372); g2.rotate(-.06); g2.scale(sc, sc);
        g2.globalAlpha = a * st; g2.strokeStyle = COL.teal; g2.lineWidth = 3; rr(-118, -30, 236, 54, 6); g2.stroke();
        text('RELEASED FOR ISSUE', 0, 5, 21, 800, COL.teal, 'center', a * st, 2); g2.restore();
      }
      // signature scribble
      const sp = ss(t, rl[1] + 2.2, rl[1] + 3.0);
      if (sp > 0) { g2.globalAlpha = a; g2.strokeStyle = COL.cream; g2.lineWidth = 2.5; g2.beginPath();
        for (let i = 0; i <= 80 * sp; i++) { const u = i / 80; const xx = x + 238 + u * 80, yy = y + 360 - 10 * Math.sin(u * 19) * (u < .7 ? 1 : .4) - 6 * Math.sin(u * 5);
          i ? g2.lineTo(xx, yy) : g2.moveTo(xx, yy); } g2.stroke(); g2.globalAlpha = 1; }
    }
    // tank status tag
    const sa = win(t, S.release + .3, S.filtration + .8, .4);
    if (sa > 0) {
      const p = proj(P(T1.x, TB + TH + 3.2, T1.z)); p.y = Math.max(p.y, 280); const rel = ss(t, rl[1] + 3.0, rl[1] + 3.3);
      const lab = rel > .5 ? 'T-101 · RELEASED' : 'T-101 · QUARANTINE'; const col = rel > .5 ? COL.teal : COL.coral;
      const w = tw(lab, 21, 700, 2) + 34;
      g2.globalAlpha = sa; g2.fillStyle = COL.panel; rr(p.x - w / 2, p.y - 22, w, 44, 22); g2.fill();
      g2.strokeStyle = col; g2.lineWidth = 2; g2.stroke(); text(lab, p.x, p.y + 8, 21, 700, col, 'center', sa, 2); g2.globalAlpha = 1;
    }
  }

  // ---- FILTRATION
  const f = SEN.filtration;
  const fp = floatPos().add(T1);
  callout(t, f[1] + .1, f[2] + 1.6, fp.clone().add(V(-.6, .3, -1.0)), -150, -110, 'Pontoon float', 'Rides the fuel surface', COL.coral);
  callout(t, f[1] + .8, f[2] + 1.6, PIV.clone().add(T1).add(V(-2.2, 2.2, 0)), 170, 90, 'Pivoting draw-off arm', 'Outlet clear of bottom water');
  callout(t, f[2] + 1.6, S.delivery + .4, P(FWS.x - 1.2, FWS.y + .7, FWS.z - .4), -230, 190, 'Stage 1 · Coalescer elements', 'Merge fine droplets into drops');
  callout(t, f[2] + 2.4, S.delivery + .4, P(FWS.x + 1.25, FWS.y + .35, FWS.z - .2), 190, -40, 'Stage 2 · Separator elements', 'Hydrophobic screens repel water', COL.teal);
  callout(t, f[2] + 3.2, S.delivery + .4, P(FWS.x + 1.3, FWS.y - 1.55, FWS.z), 190, 70, 'Water sump', 'Drained and checked daily', COL.teal);
  callout(t, f[2] + 3.9, S.delivery + .4, P(FWS.x + .3, FWS.y + FRAD + .9, FWS.z + .1), -330, 40, 'Differential pressure gauge', 'EI 1581 vessel · ΔP logged', COL.amber);

  // ---- DELIVERY
  const d = SEN.delivery;
  callout(t, d[1] + .3, d[1] + 4.0, P(58, -1.6, 4), 60, -190, 'Hydrant main', 'Buried · cathodically protected');
  callout(t, d[1] + 2.4, S.control + .2, P(PIT.x, .4, PIT.z), -170, 60, 'Hydrant pit valve', null);
  callout(t, d[1] + 3.0, S.control + .2, DFILT, -40, -170, 'Hydrant dispenser', 'Filter · meter · deadman control', COL.amber);
  callout(t, d[1] + 4.0, S.control + .2, COUP, 150, -120, 'Wing refuelling coupling', 'Pressure refuel, underwing');

  // ---- CONTROL
  const cc = SEN.control;
  {
    const a = win(t, S.control + .3, cc[1] + .2, .5);
    if (a > 0) {
      const x = 110, y = 250, w = 560, h = 360; panel(x, y, w, h, a);
      text('DAILY QUALITY CONTROL', x + 30, y + 48, 20, 700, COL.amber, 'left', a, 3);
      const rows = ['Tank & vessel low-point samples', 'Chemical water detector', 'Filter ΔP readings trended', 'Hydrant low-point drains', 'Records signed & retained'];
      rows.forEach((k, i) => { const yy = y + 104 + i * 52; const t0 = S.control + .7 + i * .7;
        text(k, x + 30, yy, 23, 500, COL.cream, 'left', a * ss(t, t0, t0 + .3)); tick(x + w - 44, yy - 8, 22, ss(t, t0 + .2, t0 + .5), COL.teal, a); });
    }
    // barriers: numbered pins at each control point
    const pins = [[P(-55, 4.6, 6), 'Receipt filter'], [P(T1.x, TB + TH + 2.5, T1.z), 'Settling & sump'], [P(LAB.x, 4.3, LAB.z), 'Release test'],
                  [P(FWS.x, FWS.y + 2.2, FWS.z), 'Filter water separator'], [P(DISP.x, 4.2, DISP.z), 'Dispenser filter']];
    pins.forEach(([pt, lab], i) => {
      const t0 = cc[1] + .3 + i * .55, a2 = ss(t, t0, t0 + .35) * (1 - ss(t, END - .6, END)); if (a2 <= 0) return;
      const p = proj(pt), up = 70 + (i % 2) * 40;
      g2.globalAlpha = a2; g2.strokeStyle = COL.teal; g2.lineWidth = 2; g2.beginPath(); g2.moveTo(p.x, p.y); g2.lineTo(p.x, p.y - up); g2.stroke();
      g2.fillStyle = COL.teal; g2.beginPath(); g2.arc(p.x, p.y, 5, 0, 7); g2.fill();
      g2.beginPath(); g2.arc(p.x, p.y - up - 20, 20, 0, 7); g2.fill();
      text(String(i + 1), p.x, p.y - up - 12, 22, 800, '#10201f', 'center', a2);
      text(lab, p.x, p.y - up - 52, 20, 600, COL.cream, 'center', a2);
      g2.globalAlpha = 1;
    });
    const ea = ss(t, cc[1] + 3.6, cc[1] + 4.4) * (1 - ss(t, END - .6, END));
    if (ea > 0) {
      text('CLEAN · DRY · ON-SPECIFICATION · PROVEN', 960, 175, 24, 700, COL.amber, 'center', ea, 5);
    }
  }
}

// ------------------------------------------------------------------ frame
window.renderAt = (t) => {
  updateScene(t);
  renderer.render(scene, camera);
  g2.globalAlpha = 1; g2.drawImage(glCanvas, 0, 0, W, H);
  overlays(t); chrome(t); captions(t);
  const fade = Math.max(1 - ss(t, 0, .8), ss(t, END - .5, END));
  if (fade > 0) { g2.globalAlpha = fade; g2.fillStyle = '#0d1012'; g2.fillRect(0, 0, W, H); g2.globalAlpha = 1; }
  return out.toDataURL('image/jpeg', 0.94);
};
window.TL = TL;
window.ready = true;
