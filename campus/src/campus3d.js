// Sol.College 3D campus: a "hacker house college". Three shared sector rooms (DeFi, DePIN, DeAI) styled as a
// library-meets-hacker-room: procedural bookshelf walls with glowing violet spines, honey wood floor, a long glowing
// table with laptops, a wall screen naming each room, velvet wingback chairs, indigo LED wash and Solana-gradient
// accents. One CTO avatar per real project, seated at its room's table. Everything is procedural (no image or font
// downloads) and bundled with three.js by esbuild at build time. No network calls; selecting an avatar never invokes
// an agent.
//
// Input: pointer (click / tap an avatar, drag to orbit, swipe to change room, pinch to zoom), the room chips, and the
// keyboard (focus the canvas: Left/Right moves between avatars, Up/Down between rooms, Enter or Space opens details).
// Quality: "high" adds bloom and more particles; "low" (phones, weak GPUs) keeps geometry and particle counts down.
// Frame time is measured continuously: resolution drops (and bloom switches off) if the device cannot keep up.
// Text: avatar names are crisp HTML overlays projected from 3D each frame (system UI font, solid pills, collision
// stacking, distance fade); wall screens and the sign are canvas textures drawn at a fixed high resolution, so text
// stays sharp even when the 3D resolution is lowered. Paused CTO agents are drawn dimmed and labelled 'Paused'.
import {
  Scene, PerspectiveCamera, WebGLRenderer, Color, FogExp2, HemisphereLight, AmbientLight, PointLight, Mesh, Group,
  MeshStandardMaterial, MeshBasicMaterial, BoxGeometry, PlaneGeometry, SphereGeometry, CapsuleGeometry, TorusGeometry,
  CylinderGeometry, InstancedMesh, Object3D, Raycaster, Vector2, Vector3, CanvasTexture, SpriteMaterial, Sprite,
  BufferGeometry, Float32BufferAttribute, Points, PointsMaterial, AdditiveBlending, RepeatWrapping, SRGBColorSpace,
  ACESFilmicToneMapping, MathUtils, DoubleSide,
} from 'three';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass.js';

const ROOM = { DeFi: 0x14f195, DePIN: 0x22c8ff, DeAI: 0xb06bff };
const ROOM_CSS = { DeFi: '#14f195', DePIN: '#22c8ff', DeAI: '#b06bff' };
const INK = 0x07051a, INDIGO = 0x4b3bff, VIOLET = 0x9945ff;
const ROOM_W = 12, ROOM_D = 9, WALL_H = 5.2, GAP = 0.4;

// ---------- procedural textures ----------
function rng(seed) { let s = seed >>> 0; return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296); }

function bookshelfTextures(low) {
  const W = low ? 512 : 1024, H = low ? 256 : 512, r = rng(7);
  const c = document.createElement('canvas'); c.width = W; c.height = H;
  const e = document.createElement('canvas'); e.width = W; e.height = H;
  const g = c.getContext('2d'), ge = e.getContext('2d');
  g.fillStyle = '#140b2e'; g.fillRect(0, 0, W, H); ge.fillStyle = '#000'; ge.fillRect(0, 0, W, H);
  const rows = 4, bay = W / 4, rowH = H / rows, frame = W / 128;
  const spine = ['#3a2a8c', '#4b31b0', '#5b3fd0', '#2e2370', '#6a4be0', '#3d2f9a', '#7d5cf0', '#26205e', '#8f78ff', '#c9b8ff'];
  for (let row = 0; row < rows; row++) {
    for (let b = 0; b < 4; b++) {
      let x = b * bay + frame * 1.5; const x1 = (b + 1) * bay - frame * 1.5, base = (row + 1) * rowH - frame * 1.6;
      while (x < x1 - 4) {
        const bw = Math.max(3, (0.012 + r() * 0.02) * W), bh = rowH * (0.52 + r() * 0.36);
        if (x + bw > x1) break;
        if (r() < 0.08) { x += bw * 1.5; continue; } // gaps
        const col = spine[Math.floor(r() * spine.length)];
        const lean = r() < 0.06;
        g.save(); if (lean) { g.translate(x, base); g.rotate(-0.18); g.translate(-x, -base); }
        g.fillStyle = col; g.fillRect(x, base - bh, bw - 1, bh);
        g.fillStyle = 'rgba(255,255,255,0.18)'; g.fillRect(x + bw * 0.15, base - bh * 0.82, bw * 0.6, Math.max(1, H / 300));
        g.fillRect(x + bw * 0.15, base - bh * 0.3, bw * 0.6, Math.max(1, H / 300));
        g.fillStyle = 'rgba(0,0,0,0.35)'; g.fillRect(x + bw - 2, base - bh, 1, bh);
        g.restore();
        if (r() < 0.16) { ge.fillStyle = r() < 0.5 ? '#6d4bff' : (r() < 0.6 ? '#b48cff' : '#2bd9a0'); ge.globalAlpha = 0.5 + r() * 0.5; ge.fillRect(x, base - bh, bw - 1, bh); ge.globalAlpha = 1; }
        x += bw;
      }
    }
    // shelf plank
    g.fillStyle = '#24164f'; g.fillRect(0, (row + 1) * rowH - frame * 1.6, W, frame * 1.6);
    g.fillStyle = 'rgba(160,130,255,0.35)'; g.fillRect(0, (row + 1) * rowH - frame * 1.6, W, Math.max(1, frame * 0.25));
  }
  for (let b = 0; b <= 4; b++) { g.fillStyle = '#1c1142'; g.fillRect(b * bay - frame * 1.5, 0, frame * 3, H); }
  const map = new CanvasTexture(c), emap = new CanvasTexture(e);
  for (const t of [map, emap]) { t.wrapS = RepeatWrapping; t.colorSpace = SRGBColorSpace; t.anisotropy = 4; }
  return { map, emap };
}

function woodTexture(low) {
  const W = low ? 256 : 512, H = low ? 256 : 512, r = rng(11);
  const c = document.createElement('canvas'); c.width = W; c.height = H;
  const g = c.getContext('2d');
  const planks = 8, ph = H / planks;
  for (let i = 0; i < planks; i++) {
    let x = -r() * W;
    while (x < W) {
      const len = W * (0.45 + r() * 0.6), base = 150 + r() * 40;
      const grad = g.createLinearGradient(0, i * ph, 0, (i + 1) * ph);
      grad.addColorStop(0, `rgb(${base + 55},${base + 5},${base - 55})`); grad.addColorStop(1, `rgb(${base + 35},${base - 15},${base - 70})`);
      g.fillStyle = grad; g.fillRect(x, i * ph, len, ph);
      g.strokeStyle = 'rgba(70,35,10,0.18)'; g.lineWidth = 1;
      for (let k = 0; k < 5; k++) { g.beginPath(); const yy = i * ph + r() * ph; g.moveTo(x, yy); g.bezierCurveTo(x + len * 0.3, yy + (r() - 0.5) * 6, x + len * 0.6, yy + (r() - 0.5) * 6, x + len, yy); g.stroke(); }
      g.fillStyle = 'rgba(40,18,4,0.55)'; g.fillRect(x, i * ph, 2, ph);
      x += len;
    }
    g.fillStyle = 'rgba(30,12,2,0.6)'; g.fillRect(0, i * ph, W, 2);
  }
  const t = new CanvasTexture(c); t.wrapS = t.wrapT = RepeatWrapping; t.colorSpace = SRGBColorSpace; t.anisotropy = 8;
  return t;
}

function screenTexture(title, sub, accent, maxAniso) {
  // drawn at 1536x864 regardless of the 3D resolution, with large type: readable from the overview camera
  const W = 1536, H = 864, c = document.createElement('canvas'); c.width = W; c.height = H; const g = c.getContext('2d');
  const bg = g.createLinearGradient(0, 0, 0, H); bg.addColorStop(0, '#13208f'); bg.addColorStop(1, '#0a1260');
  g.fillStyle = bg; g.fillRect(0, 0, W, H);
  g.fillStyle = 'rgba(255,255,255,0.05)';
  for (let y = 0; y < H; y += 36) for (let x = 0; x < W; x += 36) if (((x * 7 + y * 13) % 5) === 0) g.fillRect(x, y, 30, 30);
  g.fillStyle = '#ffffff';
  for (const [x, y, w, h] of [[60, 60, 96, 30], [60, 90, 30, 66], [W - 156, 60, 96, 30], [W - 90, 90, 30, 66], [60, H - 90, 96, 30], [60, H - 156, 30, 66], [W - 156, H - 90, 96, 30], [W - 90, H - 156, 30, 66]]) g.fillRect(x, y, w, h);
  g.textAlign = 'center'; g.textBaseline = 'middle';
  g.font = '900 250px system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'; g.fillText(title, W / 2, 330);
  g.fillStyle = accent; g.fillRect(W / 2 - 300, 520, 600, 16);
  g.fillStyle = '#ffffff'; g.font = '800 104px system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'; g.fillText(sub, W / 2, 660);
  const t = new CanvasTexture(c); t.colorSpace = SRGBColorSpace; t.anisotropy = maxAniso || 8; return t;
}

function signTexture(maxAniso) {
  const c = document.createElement('canvas'); c.width = 2048; c.height = 512; const g = c.getContext('2d');
  g.textAlign = 'center'; g.textBaseline = 'middle';
  g.shadowColor = 'rgba(153,69,255,0.9)'; g.shadowBlur = 28;
  g.fillStyle = '#ffffff'; g.font = '900 264px system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'; g.fillText('SOL.COLLEGE', 1024, 220);
  g.shadowBlur = 0; g.font = '800 76px system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'; g.fillStyle = '#ece6ff'; g.fillText('HACKER HOUSE CAMPUS  ·  DEVNET LABS', 1024, 420);
  const t = new CanvasTexture(c); t.colorSpace = SRGBColorSpace; t.anisotropy = maxAniso || 8; return t;
}

function gradientTexture() {
  const c = document.createElement('canvas'); c.width = 256; c.height = 4; const g = c.getContext('2d');
  const gr = g.createLinearGradient(0, 0, 256, 0); gr.addColorStop(0, '#9945FF'); gr.addColorStop(0.5, '#5a7bff'); gr.addColorStop(1, '#14F195');
  g.fillStyle = gr; g.fillRect(0, 0, 256, 4); const t = new CanvasTexture(c); t.colorSpace = SRGBColorSpace; return t;
}

function glowTexture() {
  const c = document.createElement('canvas'); c.width = c.height = 128; const g = c.getContext('2d');
  const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.25, 'rgba(255,255,255,0.55)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = gr; g.fillRect(0, 0, 128, 128); return new CanvasTexture(c);
}

function uplightTexture() {
  const c = document.createElement('canvas'); c.width = 64; c.height = 256; const g = c.getContext('2d');
  const gr = g.createRadialGradient(32, 256, 2, 32, 256, 250); gr.addColorStop(0, 'rgba(255,255,255,0.95)'); gr.addColorStop(0.35, 'rgba(255,255,255,0.35)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = gr; g.fillRect(0, 0, 64, 256); return new CanvasTexture(c);
}

// Short display name for a label: strip "(…)" suffixes; long names keep whole words up to ~18 characters.
// The full name is always available (title tooltip, aria-label, and the expanded label on hover/focus/selection).
function shortName(name) {
  const full = String(name).replace(/\s*\(.*\)$/, '').trim();
  if (full.length <= 18) return full;
  let out = '';
  for (const w of full.split(/\s+/)) { if ((out + ' ' + w).trim().length > 18) break; out = (out + ' ' + w).trim(); }
  return out || full.slice(0, 18);
}

// ---------- scene ----------
export function mountCampus(container, data, opts = {}) {
  const { reducedMotion = false, onSelect = () => {}, onFocusAvatar, quality: q } = opts;
  const quality = q || ((matchMedia('(pointer: coarse)').matches || (navigator.hardwareConcurrency || 8) <= 4) ? 'low' : 'high');
  const low = quality === 'low';
  const w0 = container.clientWidth || 800, h0 = container.clientHeight || 440;
  const renderer = new WebGLRenderer({ antialias: !low, powerPreference: 'high-performance', alpha: false });
  let dpr = Math.min(devicePixelRatio || 1, low ? 1.5 : 1.75);
  renderer.setPixelRatio(dpr); renderer.setSize(w0, h0);
  renderer.toneMapping = ACESFilmicToneMapping; renderer.toneMappingExposure = 1.35; renderer.outputColorSpace = SRGBColorSpace;
  container.style.position = container.style.position || 'relative';
  container.appendChild(renderer.domElement);
  const canvas = renderer.domElement;
  const maxAniso = renderer.capabilities.getMaxAnisotropy();
  canvas.style.touchAction = 'pan-y'; // vertical swipes still scroll the page on phones

  const scene = new Scene(); scene.background = new Color(INK); scene.fog = new FogExp2(INK, low ? 0.03 : 0.024);
  const camera = new PerspectiveCamera(48, w0 / h0, 0.1, 120);
  scene.add(new HemisphereLight(0x9d8bff, 0x8a5a2a, 1.1));
  scene.add(new AmbientLight(0x3a2d8a, 0.7));

  const sectors = data.sectors.map((s) => s.id);
  const nRooms = sectors.length || 3;
  const roomX = (i) => (i - (nRooms - 1) / 2) * (ROOM_W + GAP);
  const totalW = nRooms * (ROOM_W + GAP);

  // floor
  const wood = woodTexture(low); wood.repeat.set(totalW / 6, ROOM_D / 3);
  const FLOOR_FRONT = 3.6, floorDepth = ROOM_D / 2 + FLOOR_FRONT;
  const floor = new Mesh(new PlaneGeometry(totalW + 1, floorDepth), new MeshStandardMaterial({ map: wood, roughness: 0.42, metalness: 0.08, color: 0xf3d2a6 }));
  floor.rotation.x = -Math.PI / 2; floor.position.z = FLOOR_FRONT - floorDepth / 2; scene.add(floor);
  wood.repeat.set((totalW + 1) / 5, floorDepth / 5);

  // glowing front edge of the floor (Solana gradient), like a stage lip
  const lip = new Mesh(new BoxGeometry(totalW + 1, 0.06, 0.06), new MeshBasicMaterial({ map: gradientTexture(), toneMapped: false })); lip.position.set(0, 0.03, FLOOR_FRONT); scene.add(lip);

  // bookshelf back wall (one long wall) and side walls
  const shelves = bookshelfTextures(low);
  const shelfMat = new MeshStandardMaterial({ map: shelves.map, emissiveMap: shelves.emap, emissive: 0xffffff, emissiveIntensity: low ? 0.9 : 0.75, roughness: 0.9 });
  shelves.map.repeat.set(totalW / 7, 1); shelves.emap.repeat.set(totalW / 7, 1);
  const back = new Mesh(new PlaneGeometry(totalW + 0.4, WALL_H), shelfMat);
  back.position.set(0, WALL_H / 2, -ROOM_D / 2); scene.add(back);
  const sideMat = shelfMat.clone(); sideMat.map = shelves.map.clone(); sideMat.emissiveMap = shelves.emap.clone();
  sideMat.map.repeat.set(ROOM_D / 7, 1); sideMat.emissiveMap.repeat.set(ROOM_D / 7, 1); sideMat.map.needsUpdate = sideMat.emissiveMap.needsUpdate = true;
  for (const sgn of [-1, 1]) {
    const side = new Mesh(new PlaneGeometry(ROOM_D, WALL_H), sideMat);
    side.position.set(sgn * (totalW / 2), WALL_H / 2, 0); side.rotation.y = -sgn * Math.PI / 2; scene.add(side);
  }
  // room dividers: low glass partitions with a Solana-gradient top rail
  const grad = gradientTexture();
  const railMat = new MeshBasicMaterial({ map: grad, toneMapped: false });
  const glassMat = new MeshStandardMaterial({ color: 0x5a3cff, transparent: true, opacity: 0.08, roughness: 0.1, metalness: 0.2, side: DoubleSide, depthWrite: false });
  for (let i = 1; i < nRooms; i++) {
    const x = (roomX(i - 1) + roomX(i)) / 2;
    const glass = new Mesh(new PlaneGeometry(ROOM_D * 0.75, 2.2), glassMat); glass.rotation.y = Math.PI / 2; glass.position.set(x, 1.1, -ROOM_D * 0.125); scene.add(glass);
  }
  // LED strip along the bottom of the walls + uplight washes
  const strip = new Mesh(new BoxGeometry(totalW, 0.05, 0.05), new MeshBasicMaterial({ color: 0x6a4bff, toneMapped: false }));
  strip.position.set(0, 0.04, -ROOM_D / 2 + 0.05); scene.add(strip);
  const upTex = uplightTexture();
  const upMat = new MeshBasicMaterial({ map: upTex, color: 0x5a3cff, transparent: true, opacity: low ? 0.55 : 0.45, blending: AdditiveBlending, depthWrite: false, toneMapped: false });
  const ups = Math.round(totalW / 2.6);
  for (let i = 0; i < ups; i++) {
    const p = new Mesh(new PlaneGeometry(1.6, WALL_H * 0.9), upMat); p.position.set(-totalW / 2 + (i + 0.5) * (totalW / ups), WALL_H * 0.45, -ROOM_D / 2 + 0.03); scene.add(p);
  }
  // signage
  const sign = new Mesh(new PlaneGeometry(6.8, 1.7), new MeshBasicMaterial({ map: signTexture(maxAniso), transparent: true, depthWrite: false, toneMapped: false }));
  sign.position.set(0, WALL_H - 0.72, -ROOM_D / 2 + 0.06); scene.add(sign);

  // shared geometries
  const glowTex = glowTexture();
  const legGeo = new BoxGeometry(0.12, 0.72, 1.3);
  const tableMat = new MeshStandardMaterial({ color: 0x2a1810, roughness: 0.28, metalness: 0.25 });
  const velvet = new MeshStandardMaterial({ color: 0x5226b8, roughness: 0.85, metalness: 0, emissive: 0x1a0a52, emissiveIntensity: 0.55 });
  const screenBack = new MeshStandardMaterial({ color: 0x0a0a14, roughness: 0.5 });

  // chairs: instanced wingbacks (seat, back, two wings, cushion) — 6 per room
  // Seating grows with the room: every project gets a seat. Up to 4 on the far side (facing the camera); beyond
  // that both sides are used and the spacing tightens so the table still fits the room.
  // Seating: active CTO agents sit at the table on the far side facing the camera (prominent, full size; a fifth+
  // active agent uses a backless stool on the near side). Paused agents stand in a back row by the bookshelves,
  // smaller and dimmed, offset by half a seat so they never hide an active agent.
  const isPaused = (p) => (p.agent && p.agent.state) === 'paused';
  const roomProjects = sectors.map((sid) => {
    const ps = data.projects.filter((p) => p.sector === sid);
    const act = ps.filter((p) => !isPaused(p)), pau = ps.filter(isPaused);
    const far = act.slice(0, 4), near = act.slice(4);
    return { far, near, back: pau };
  });
  const roomCounts = roomProjects.map((rp) => rp.far.length + rp.near.length);
  const sidesFor = (r) => (roomProjects[r].near.length ? 2 : 1);
  const perSide = (r) => Math.max(3, roomProjects[r].far.length, roomProjects[r].near.length, roomProjects[r].back.length - 1);
  const spacing = (r) => Math.min(2.4, (ROOM_W - 1.4) / perSide(r));
  const tableLen = (r) => perSide(r) * spacing(r) + 0.4;
  const parts = [
    [new BoxGeometry(0.8, 0.42, 0.75), [0, 0.21, 0]],
    [new BoxGeometry(0.85, 1.25, 0.2), [0, 0.82, 0.32]],
    [new BoxGeometry(0.14, 0.9, 0.6), [-0.42, 0.7, 0.08]],
    [new BoxGeometry(0.14, 0.9, 0.6), [0.42, 0.7, 0.08]],
  ];
  const seatPos = []; // [roomIndex] => [{x, z, rot, near, p}]
  for (let r = 0; r < nRooms; r++) {
    seatPos[r] = [];
    const { far, near } = roomProjects[r];
    const nF = far.length >= 2 ? far.length : 3, nN = near.length; // 2+ active agents: centred, no empty chairs between them
    for (let k = 0; k < nF; k++) seatPos[r].push({ x: roomX(r) + (k - (nF - 1) / 2) * spacing(r), z: -1.45, rot: Math.PI, near: false, p: far[k - Math.floor((nF - far.length) / 2)] || null });
    const nOff = nN === nF ? 0.5 : 0; // interleave when both sides have the same count
    for (let k = 0; k < nN; k++) seatPos[r].push({ x: roomX(r) + (k - (nN - 1) / 2 + nOff) * spacing(r), z: 1.35, rot: Math.PI, near: true, p: near[k] });
    const back = roomProjects[r].back, nB = back.length, bs = Math.min(spacing(r) * 1.1, (ROOM_W - 1.6) / Math.max(1, nB));
    for (let k = 0; k < nB; k++) seatPos[r].push({ x: roomX(r) + (k - (nB - 1) / 2) * bs, z: -3.7, rot: Math.PI, near: false, back: true, p: back[k] });
  }
  const chairCount = seatPos.reduce((n, s) => n + s.length, 0) || 1;
  const chairMeshes = parts.map(([g]) => { const m = new InstancedMesh(g, velvet, chairCount); scene.add(m); return m; });
  const dummy = new Object3D(), part = new Object3D(); let ci = 0;
  for (let r = 0; r < nRooms; r++) for (const { x, z, rot, near, back } of seatPos[r]) {
    dummy.position.set(x, 0, z); dummy.rotation.set(0, rot, 0); dummy.updateMatrix();
    parts.forEach(([, off], pi) => {
      part.position.set(off[0], off[1], off[2]); part.scale.setScalar(back || (near && pi > 0) ? 0 : near ? 0.85 : 1); part.updateMatrix();
      part.matrix.premultiply(dummy.matrix);
      chairMeshes[pi].setMatrixAt(ci, part.matrix);
    });
    ci++;
  }
  chairMeshes.forEach((m) => (m.instanceMatrix.needsUpdate = true));

  // ---------- HTML labels (crisp text, projected from 3D every frame) ----------
  const labelLayer = document.createElement('div'); labelLayer.className = 'c3-labels'; labelLayer.setAttribute('aria-hidden', 'true');
  container.appendChild(labelLayer);
  function makeLabel(p, css, paused) {
    const full = String(p.displayName).replace(/\s*\(.*\)$/, '').trim(), short = shortName(p.displayName);
    const el = document.createElement('button'); el.type = 'button'; el.tabIndex = -1; el.className = 'c3-label' + (paused ? ' is-paused' : '');
    el.style.setProperty('--acc', css); const tag = (p.agent && p.agent.label) || 'Paused';
    el.title = full + (paused ? ` (CTO agent: ${tag})` : '');
    el.innerHTML = '<span class="c3-dot"></span><span class="c3-short"></span><span class="c3-full"></span>' + (paused ? '<span class="c3-state"></span>' : '');
    if (paused) el.querySelector('.c3-state').textContent = tag;
    el.querySelector('.c3-short').textContent = short; el.querySelector('.c3-full').textContent = full;
    if (short === full) el.classList.add('no-short');
    el.addEventListener('click', (e) => { e.stopPropagation(); const s = p.slug; focusIdx = avatars.findIndex((x) => x.slug === s); highlight(s); onSelect(s); });
    el.addEventListener('pointerenter', () => { hovered = p.slug; wake(); });
    el.addEventListener('pointerleave', () => { if (hovered === p.slug) { hovered = null; wake(); } });
    labelLayer.appendChild(el);
    return { el, w: 0, h: 0, x: -1e4, y: -1e4, o: -1, full: false };
  }
  const roomLights = [];
  const avatars = [];
  const hitTargets = [];
  sectors.forEach((sid, r) => {
    const cx = roomX(r), accent = ROOM[sid] ?? VIOLET, css = ROOM_CSS[sid] ?? '#9945ff';
    const room = new Group(); scene.add(room);
    // table
    const L = tableLen(r);
    const top = new Mesh(new BoxGeometry(L, 0.12, 1.7), tableMat); top.position.set(cx, 0.78, 0); room.add(top);
    const edgeGeo = new BoxGeometry(L, 0.035, 0.035);
    for (const sx of [-(L / 2 - 0.5), L / 2 - 0.5]) { const leg = new Mesh(legGeo, tableMat); leg.position.set(cx + sx, 0.36, 0); room.add(leg); }
    const edgeMat = new MeshBasicMaterial({ map: grad, toneMapped: false });
    for (const sz of [-0.85, 0.85]) { const e = new Mesh(edgeGeo, edgeMat); e.position.set(cx, 0.78, sz); room.add(e); }
    // under-table glow
    const pool = new Mesh(new PlaneGeometry(9, 3.4), new MeshBasicMaterial({ map: glowTex, color: accent, transparent: true, opacity: 0.22, blending: AdditiveBlending, depthWrite: false, toneMapped: false }));
    pool.rotation.x = -Math.PI / 2; pool.position.set(cx, 0.012, 0); room.add(pool);
    // wall screen
    const ps = data.projects.filter((p) => p.sector === sid);
    const nAct = ps.filter((p) => !isPaused(p)).length, nPau = ps.length - nAct;
    const sub = !ps.length ? 'no projects yet' : nPau ? `${nAct} active · ${nPau} paused` : `${nAct} active agent${nAct === 1 ? '' : 's'}`;
    const scr = new Mesh(new PlaneGeometry(3.4, 1.9), new MeshBasicMaterial({ map: screenTexture(sid, sub, css, maxAniso), toneMapped: false }));
    scr.position.set(cx, 2.55, -ROOM_D / 2 + 0.08); room.add(scr);
    const bezel = new Mesh(new BoxGeometry(3.55, 2.05, 0.06), screenBack); bezel.position.set(cx, 2.55, -ROOM_D / 2 + 0.04); room.add(bezel);
    // room light (indigo wash tinted by sector)
    const pl = new PointLight(new Color(INDIGO).lerp(new Color(accent), 0.25), low ? 10 : 14, 14, 1.6); pl.position.set(cx, 3.6, -2.2); room.add(pl); roomLights.push(pl);
    const warm = new PointLight(0xffb36b, low ? 7 : 9, 9, 1.4); warm.position.set(cx, 3.1, 0.6); room.add(warm);
    for (const lx of [-2.2, 0, 2.2]) {
      const cord = new Mesh(new CylinderGeometry(0.01, 0.01, 1.4, 4), screenBack); cord.position.set(cx + lx, WALL_H - 0.7, 0); room.add(cord);
      const shade = new Mesh(new CylinderGeometry(0.12, 0.34, 0.3, low ? 10 : 18, 1, true), new MeshStandardMaterial({ color: 0x1a1430, roughness: 0.4, metalness: 0.6, side: DoubleSide })); shade.position.set(cx + lx, WALL_H - 1.45, 0); room.add(shade);
      const bulb = new Mesh(new SphereGeometry(0.09, 10, 8), new MeshBasicMaterial({ color: 0xffd29a, toneMapped: false })); bulb.position.set(cx + lx, WALL_H - 1.56, 0); room.add(bulb);
      const halo = new Sprite(new SpriteMaterial({ map: glowTex, color: 0xffb36b, transparent: true, opacity: 0.55, blending: AdditiveBlending, depthWrite: false })); halo.scale.set(1.3, 1.3, 1); halo.position.copy(bulb.position); room.add(halo);
    }
    // avatars: seated at the table, far side first (facing the camera)
    const sc = Math.min(1.3, spacing(r) / 1.85);
    seatPos[r].filter((s) => s.p).forEach((seat, j) => {
      const p = seat.p, paused = isPaused(p), asc = paused ? sc * 0.8 : sc;
      const a = new Group(); a.position.set(seat.x, 0, seat.z * 0.82); a.rotation.y = seat.rot; a.userData.base = asc; a.scale.setScalar(asc); room.add(a);
      const bodyMat = paused
        ? new MeshStandardMaterial({ color: 0x6a6488, emissive: 0x241c4a, emissiveIntensity: 0.25, roughness: 0.6, metalness: 0.05, transparent: true, opacity: 0.78 })
        : new MeshStandardMaterial({ color: new Color(0xf4f0ff).lerp(new Color(accent), 0.18), emissive: accent, emissiveIntensity: low ? 0.5 : 0.32, roughness: 0.3, metalness: 0.15 });
      const dimAccent = paused ? 0x5b5380 : accent;
      const body = new Mesh(new CapsuleGeometry(0.32, 0.55, low ? 4 : 8, low ? 10 : 18), bodyMat); body.position.y = 0.95;
      const head = new Mesh(new SphereGeometry(0.3, low ? 14 : 24, low ? 10 : 18), bodyMat); head.position.y = 1.72;
      const visor = new Mesh(new BoxGeometry(0.42, 0.1, 0.05), new MeshBasicMaterial({ color: dimAccent, toneMapped: false })); visor.position.set(0, 1.74, -0.27);
      const halo = new Mesh(new TorusGeometry(0.42, 0.025, 8, low ? 24 : 48), new MeshBasicMaterial({ color: accent, transparent: true, opacity: paused ? 0 : 0.9, toneMapped: false })); halo.rotation.x = Math.PI / 2; halo.position.y = 2.15; halo.visible = !paused;
      const glow = new Sprite(new SpriteMaterial({ map: glowTex, color: dimAccent, transparent: true, opacity: paused ? 0.12 : 0.5, blending: AdditiveBlending, depthWrite: false })); glow.scale.set(2.2, 2.2, 1); glow.position.y = 1.3;
      // laptop on the table in front of the avatar
      const lap = new Group(); lap.position.set(0, 0.84, -0.62);
      const lbase = new Mesh(new BoxGeometry(0.62, 0.03, 0.42), screenBack); lap.add(lbase);
      const lid = new Group(); lid.position.set(0, 0.015, -0.2); lid.rotation.x = -0.28; lap.add(lid);
      const shell = new Mesh(new BoxGeometry(0.62, 0.4, 0.02), screenBack); shell.position.y = 0.2; lid.add(shell);
      const lscr = new Mesh(new PlaneGeometry(0.56, 0.35), new MeshBasicMaterial({ color: paused ? 0x1a1838 : 0x6070ff, toneMapped: false })); lscr.position.set(0, 0.2, 0.011); lid.add(lscr);
      const logo = new Mesh(new PlaneGeometry(0.16, 0.05), new MeshBasicMaterial({ map: grad, toneMapped: false })); logo.position.set(0, 0.22, -0.011); logo.rotation.y = Math.PI; lid.add(logo);
      const base = new Mesh(new TorusGeometry(0.55, 0.03, 6, low ? 24 : 40), new MeshBasicMaterial({ color: dimAccent, transparent: true, opacity: paused ? 0.35 : 0.8, toneMapped: false })); base.rotation.x = Math.PI / 2; base.position.y = 0.03;
      const scarf = new Mesh(new TorusGeometry(0.3, 0.06, 8, low ? 16 : 28), paused ? new MeshBasicMaterial({ color: 0x4a4468 }) : new MeshBasicMaterial({ map: grad, toneMapped: false })); scarf.rotation.x = Math.PI / 2; scarf.position.y = 1.42;
      const hit = new Mesh(new CylinderGeometry(0.75, 0.75, 2.6, 8), new MeshBasicMaterial({ visible: false })); hit.position.y = 1.2; // generous tap target
      body.userData.slug = head.userData.slug = hit.userData.slug = p.slug;
      a.add(body, head, visor, halo, glow, base, scarf, hit); if (!seat.near && !seat.back) a.add(lap);
      const label = makeLabel(p, css, paused);
      avatars.push({ slug: p.slug, group: a, bodyMat, halo, glow, label, paused, room: r, phase: j * 1.7, hover: 0, target: 0, base: paused ? 0.25 : (low ? 0.5 : 0.32) });
      hitTargets.push(hit, body, head);
    });
  });

  // floating glow orbs (echoing the purple orbs of the coffee-bar graphics)
  const orbs = [];
  const orbCols = [0x9945ff, 0x6b5bff, 0x14f195, 0xc46bff, 0x4b3bff, 0x9945ff, 0x22c8ff];
  for (let i = 0; i < (low ? 5 : 9); i++) {
    const r0 = 0.12 + (i % 3) * 0.07, col = orbCols[i % orbCols.length];
    const o = new Mesh(new SphereGeometry(r0, 16, 12), new MeshBasicMaterial({ color: col, transparent: true, opacity: 0.9, toneMapped: false }));
    const g = new Sprite(new SpriteMaterial({ map: glowTex, color: col, transparent: true, opacity: 0.6, blending: AdditiveBlending, depthWrite: false })); g.scale.set(r0 * 9, r0 * 9, 1); o.add(g);
    o.position.set(-totalW / 2 + (i + 0.5) * (totalW / (low ? 5 : 9)), 3.4 + (i % 2) * 0.6, -2.8 + (i % 3) * 1.2);
    o.userData.y0 = o.position.y; o.userData.ph = i * 1.3; scene.add(o); orbs.push(o);
  }

  // particles (floating dust in the LED light)
  const nP = reducedMotion ? 0 : low ? 260 : 900;
  let particles = null;
  if (nP) {
    const pos = new Float32Array(nP * 3), col = new Float32Array(nP * 3), rr = rng(3);
    const cA = new Color(VIOLET), cB = new Color(0x14f195), cC = new Color(0x8fa0ff);
    for (let i = 0; i < nP; i++) {
      pos[i * 3] = (rr() - 0.5) * totalW; pos[i * 3 + 1] = rr() * WALL_H; pos[i * 3 + 2] = (rr() - 0.5) * (ROOM_D + 2);
      const c = rr() < 0.12 ? cB : rr() < 0.5 ? cA : cC; col.set([c.r, c.g, c.b], i * 3);
    }
    const g = new BufferGeometry(); g.setAttribute('position', new Float32BufferAttribute(pos, 3)); g.setAttribute('color', new Float32BufferAttribute(col, 3));
    particles = new Points(g, new PointsMaterial({ size: low ? 0.07 : 0.055, map: glowTex, vertexColors: true, transparent: true, opacity: 0.85, blending: AdditiveBlending, depthWrite: false, toneMapped: false }));
    scene.add(particles);
  }

  // ---------- post-processing (desktop / capable GPUs only) ----------
  let composer = null, bloom = null;
  const useBloom = !low && !opts.noBloom;
  if (useBloom) {
    composer = new EffectComposer(renderer); composer.setPixelRatio(dpr); composer.setSize(w0, h0);
    composer.addPass(new RenderPass(scene, camera));
    bloom = new UnrealBloomPass(new Vector2(w0, h0), 0.55, 0.5, 0.78); composer.addPass(bloom);
    composer.addPass(new OutputPass());
  }

  // ---------- camera rig ----------
  const views = [{ name: 'Overview', x: 0 }, ...sectors.map((s, i) => ({ name: `${s}`, x: roomX(i), room: i }))];
  const aspect0 = w0 / h0;
  const fitV = (h) => (h / 2) / Math.tan(MathUtils.degToRad(camera.fov / 2));
  const fitDist = (span) => (span / 2) / Math.tan(MathUtils.degToRad(camera.fov / 2)) / Math.max(0.55, camera.aspect) * 1.02;
  const rig = { yaw: 0, pitch: 0.3, dist: 18, tx: 0, ty: 1.25, tz: 0 };
  const goal = { ...rig };
  let viewIdx = 0, ready = false;
  const firstRoomWithProjects = sectors.findIndex((s) => data.projects.some((p) => p.sector === s));
  const setView = (i, instant) => {
    viewIdx = (i + views.length) % views.length; const v = views[viewIdx];
    goal.tx = v.x; goal.tz = viewIdx === 0 ? 0 : 0.2;
    const portrait = camera.aspect < 1;
    const fov = portrait ? 60 : 48; if (camera.fov !== fov) { camera.fov = fov; camera.updateProjectionMatrix(); }
    // portrait: lens shift so the room sits lower in the frame (the space above the bookshelves is otherwise empty)
    const W = container.clientWidth || 1, H = container.clientHeight || 1;
    if (portrait && viewIdx > 0) camera.setViewOffset(W, H, 0, -H * 0.07, W, H); else camera.clearViewOffset();
    const crowded = viewIdx > 0 && sidesFor(v.room) === 2;
    goal.dist = viewIdx === 0 ? Math.max(10, fitDist(totalW * (portrait ? 0.62 : 0.78)))
      : Math.max(6.5, fitV(crowded ? 8.5 : 6.2), fitDist(portrait ? Math.max(6.2, tableLen(v.room) + 0.5) : ROOM_W * (crowded ? 1.05 : 0.9)));
    goal.pitch = viewIdx === 0 ? 0.3 : crowded ? (portrait ? 0.36 : 0.42) : (portrait ? 0.34 : 0.22);
    goal.ty = crowded ? (portrait ? 1.6 : 1.2) : portrait ? 1.45 : 1.4; goal.yaw = 0;
    if (instant) Object.assign(rig, goal);
    chips.forEach((c, k) => c.setAttribute('aria-pressed', String(k === viewIdx)));
    if (ready) wake();
  };

  // room chips (HTML overlay)
  const nav = document.createElement('div'); nav.className = 'c3-nav'; nav.setAttribute('role', 'group'); nav.setAttribute('aria-label', 'Camera: choose a room');
  const chips = views.map((v, i) => { const b = document.createElement('button'); b.type = 'button'; b.className = 'c3-chip'; b.textContent = v.name; b.addEventListener('click', () => { userActed(); setView(i); }); nav.appendChild(b); return b; });
  container.appendChild(nav);
  const hint = document.createElement('div'); hint.className = 'c3-hint'; hint.textContent = matchMedia('(pointer: coarse)').matches ? 'Tap an avatar · swipe to change room' : 'Click an avatar · drag to look around'; container.appendChild(hint);

  // narrow screens start in the first room that has projects; wide screens start on the overview
  setView(aspect0 < 1.2 && firstRoomWithProjects >= 0 ? firstRoomWithProjects + 1 : 0, true);

  // ---------- interaction ----------
  canvas.tabIndex = 0;
  canvas.setAttribute('role', 'application');
  canvas.setAttribute('aria-roledescription', '3D campus');
  canvas.setAttribute('aria-label', `3D campus with ${avatars.length} project avatar${avatars.length === 1 ? '' : 's'}. Left and right arrows move between avatars, up and down between rooms; Enter opens details.`);
  const ray = new Raycaster(), v2 = new Vector2();
  let hovered = null, selected = null, idleUntil = 0, focusIdx = -1, nextTour = performance.now() + 9000;
  // portrait screens tour only the rooms that have projects (the overview is too small to read there)
  const tour = [viewIdx, ...sectors.map((s, i) => i + 1).filter((v) => roomCounts[v - 1] > 0 && v !== viewIdx), ...(viewIdx !== 0 && aspect0 >= 1.2 ? [0] : [])];
  let tourPos = 0;
  const userActed = () => { idleUntil = performance.now() + 7000; };
  const pick = (cx, cy) => {
    const r = canvas.getBoundingClientRect();
    v2.set(((cx - r.left) / r.width) * 2 - 1, -((cy - r.top) / r.height) * 2 + 1);
    ray.setFromCamera(v2, camera);
    const hit = ray.intersectObjects(hitTargets, false)[0];
    return hit ? hit.object.userData.slug : null;
  };
  const highlight = (slug) => { selected = slug; avatars.forEach((a) => (a.target = a.slug === slug ? 1 : 0)); if (ready) wake(); };
  const pointers = new Map(); let drag = null, pinch0 = 0;
  canvas.addEventListener('pointerdown', (e) => {
    pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (pointers.size === 1) drag = { x: e.clientX, y: e.clientY, t: performance.now(), yaw: goal.yaw, pitch: goal.pitch, moved: 0, type: e.pointerType };
    if (pointers.size === 2) { const [a, b] = [...pointers.values()]; pinch0 = Math.hypot(a.x - b.x, a.y - b.y); drag = null; }
    userActed();
  });
  canvas.addEventListener('pointermove', (e) => {
    if (pointers.has(e.pointerId)) pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (pointers.size === 2 && pinch0) {
      const [a, b] = [...pointers.values()]; const d = Math.hypot(a.x - b.x, a.y - b.y);
      goal.dist = MathUtils.clamp(goal.dist * (pinch0 / d), 6, 30); pinch0 = d; wake(); return;
    }
    if (drag) {
      const dx = e.clientX - drag.x, dy = e.clientY - drag.y; drag.moved = Math.max(drag.moved, Math.hypot(dx, dy));
      goal.yaw = MathUtils.clamp(drag.yaw - dx * 0.004, -0.75, 0.75);
      if (drag.type === 'mouse') goal.pitch = MathUtils.clamp(drag.pitch + dy * 0.003, 0.12, 0.95);
      wake(); return;
    }
    if (e.pointerType === 'mouse') { const s = pick(e.clientX, e.clientY); if (s !== hovered) { hovered = s; canvas.style.cursor = s ? 'pointer' : 'grab'; wake(); } }
  });
  const end = (e) => {
    pointers.delete(e.pointerId); if (pointers.size < 2) pinch0 = 0;
    if (!drag) return;
    const dt = performance.now() - drag.t, dx = e.clientX - drag.x;
    if (drag.moved < 8) { const s = pick(e.clientX, e.clientY); if (s) { focusIdx = avatars.findIndex((a) => a.slug === s); highlight(s); onSelect(s); } }
    else if (drag.type !== 'mouse' && Math.abs(dx) > 50 && dt < 450) { setView(viewIdx + (dx < 0 ? 1 : -1)); }
    else if (drag.type !== 'mouse') { goal.yaw = 0; }
    drag = null;
  };
  canvas.addEventListener('pointerup', end); canvas.addEventListener('pointercancel', end);
  canvas.addEventListener('pointerleave', () => { if (hovered) { hovered = null; wake(); } });
  canvas.style.cursor = 'grab';
  canvas.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowUp' || e.key === 'ArrowDown') { e.preventDefault(); userActed(); setView(viewIdx + (e.key === 'ArrowDown' ? 1 : -1)); return; }
    if (!avatars.length) return;
    if (e.key === 'ArrowRight') focusIdx = (focusIdx + 1) % avatars.length;
    else if (e.key === 'ArrowLeft') focusIdx = (focusIdx - 1 + avatars.length) % avatars.length;
    else if ((e.key === 'Enter' || e.key === ' ') && focusIdx >= 0) { e.preventDefault(); onSelect(avatars[focusIdx].slug); return; }
    else return;
    e.preventDefault(); userActed();
    const a = avatars[focusIdx]; highlight(a.slug); setView(a.room + 1);
    if (onFocusAvatar) onFocusAvatar(a.slug);
  });

  // ---------- loop ----------
  let raf = 0, visible = true, last = performance.now(), t = 0, frames = 0, acc = 0, slowStreak = 0, still = 0;
  const camPos = new Vector3();
  const render = () => { if (composer) composer.render(); else renderer.render(scene, camera); placeLabels(); };
  // Project every label anchor, then place labels in priority order (selected/hovered, active, paused; nearer
  // first). A label that would overlap one already placed is nudged upwards (up to 3 steps), then sideways; if it
  // still collides, a paused label is hidden. Distant paused labels fade out; anything off-screen or behind is hidden.
  const anchor = new Vector3(), camDir = new Vector3(), toA = new Vector3();
  const placeLabels = () => {
    const W = container.clientWidth, H = container.clientHeight; if (!W || !H) return;
    camera.getWorldDirection(camDir);
    const items = [];
    for (const a of avatars) {
      const L = a.label;
      a.group.getWorldPosition(anchor); anchor.y += 2.45 * a.group.scale.y;
      toA.copy(anchor).sub(camera.position); const dist = toA.length(); const facing = toA.dot(camDir) / dist;
      anchor.project(camera);
      const sx = (anchor.x + 1) / 2 * W, sy = (1 - anchor.y) / 2 * H;
      const on = facing > 0.2 && anchor.z < 1 && sx > -40 && sx < W + 40 && sy > -10 && sy < H + 10;
      const pri = (a.slug === selected || a.slug === hovered ? 0 : a.paused ? 2 : 1);
      const fade = a.paused ? MathUtils.clamp((22 - dist) / 6, 0, 1) : MathUtils.clamp((40 - dist) / 8, 0, 1);
      items.push({ a, L, sx, sy, on: on && fade > 0.05, pri, dist, fade });
    }
    items.sort((p, q) => p.pri - q.pri || p.dist - q.dist);
    const placed = [];
    const hit = (r) => placed.some((q) => r.x < q.x + q.w + 4 && r.x + r.w + 4 > q.x && r.y < q.y + q.h + 3 && r.y + r.h + 3 > q.y);
    for (const it of items) {
      const { a, L } = it;
      const full = a.slug === selected || a.slug === hovered;
      if (L.full !== full) { L.full = full; L.el.classList.toggle('is-full', full); L.w = 0; }
      L.el.classList.toggle('is-sel', a.slug === selected);
      if (!it.on) { if (L.o !== 0) { L.el.style.opacity = '0'; L.el.style.visibility = 'hidden'; L.o = 0; } continue; }
      if (!L.w) { L.w = L.el.offsetWidth; L.h = L.el.offsetHeight; }
      let r = { x: Math.round(it.sx - L.w / 2), y: Math.round(it.sy - L.h), w: L.w, h: L.h };
      r.x = Math.max(4, Math.min(W - L.w - 4, r.x)); r.y = Math.max(4, Math.min(H - L.h - 4, r.y));
      let ok = !hit(r);
      for (let k = 1; !ok && k <= 3; k++) { const c = { ...r, y: r.y - k * (L.h + 3) }; if (c.y >= 2 && !hit(c)) { r = c; ok = true; } }
      for (const dx of [1, -1]) { if (ok) break; const c = { ...r, x: r.x + dx * (L.w / 2 + 6) }; if (c.x >= 2 && c.x + c.w <= W - 2 && !hit(c)) { r = c; ok = true; } }
      if (!ok && it.pri === 2) { if (L.o !== 0) { L.el.style.opacity = '0'; L.el.style.visibility = 'hidden'; L.o = 0; } continue; }
      placed.push(r);
      const o = Math.round(it.fade * 100) / 100;
      if (L.x !== r.x || L.y !== r.y) { L.el.style.transform = `translate3d(${r.x}px,${r.y}px,0)`; L.x = r.x; L.y = r.y; }
      if (L.o !== o) { L.el.style.opacity = String(o); L.el.style.visibility = 'visible'; L.o = o; }
      L.el.style.zIndex = String(10 - it.pri);
    }
  };
  const step = (dt) => {
    const now = performance.now();
    const auto = !reducedMotion && now > idleUntil;
    // gentle fly-through: overview and the rooms that have projects, one stop every ~9 s while nobody is interacting
    if (auto && tour.length > 1 && now > nextTour && !selected) { tourPos = (tourPos + 1) % tour.length; setView(tour[tourPos]); nextTour = now + 9000; }
    if (!auto) nextTour = Math.max(nextTour, idleUntil + 4000);
    const k = 1 - Math.pow(0.0025, dt); // smooth follow
    const yawAuto = auto ? Math.sin(t * 0.12) * 0.32 : 0;
    rig.yaw += (goal.yaw + yawAuto - rig.yaw) * k; rig.pitch += (goal.pitch - rig.pitch) * k; rig.dist += (goal.dist - rig.dist) * k;
    rig.tx += (goal.tx - rig.tx) * k; rig.tz += (goal.tz - rig.tz) * k; rig.ty += (goal.ty - rig.ty) * k;
    camPos.set(rig.tx + Math.sin(rig.yaw) * Math.cos(rig.pitch) * rig.dist, rig.ty + Math.sin(rig.pitch) * rig.dist, rig.tz + Math.cos(rig.yaw) * Math.cos(rig.pitch) * rig.dist);
    camera.position.copy(camPos); camera.lookAt(rig.tx, rig.ty, rig.tz - 0.6);
    for (const a of avatars) {
      const want = Math.max(a.target, hovered === a.slug ? 0.7 : 0);
      a.hover += (want - a.hover) * Math.min(1, dt * 10);
      const bob = reducedMotion ? 0 : Math.sin(t * 1.6 + a.phase) * 0.04;
      a.group.position.y = bob; a.group.scale.setScalar(a.group.userData.base * (1 + a.hover * 0.12));
      a.bodyMat.emissiveIntensity = a.base + a.hover * (a.paused ? 0.35 : 0.9);
      a.halo.rotation.z = t * 0.8 + a.phase; a.halo.material.opacity = 0.6 + a.hover * 0.4;
      a.glow.material.opacity = (a.paused ? 0.1 : 0.35) + a.hover * 0.5 + (reducedMotion || a.paused ? 0 : Math.sin(t * 2 + a.phase) * 0.06);
    }
    if (particles) {
      const p = particles.geometry.attributes.position, arr = p.array;
      for (let i = 0; i < arr.length; i += 3) { arr[i + 1] += dt * (0.06 + (i % 7) * 0.012); arr[i] += Math.sin(t * 0.3 + i) * dt * 0.02; if (arr[i + 1] > WALL_H) arr[i + 1] = 0; }
      p.needsUpdate = true;
    }
    if (!reducedMotion) for (const o of orbs) o.position.y = o.userData.y0 + Math.sin(t * 0.6 + o.userData.ph) * 0.25;
    for (let i = 0; i < roomLights.length; i++) roomLights[i].intensity = (low ? 10 : 14) * (reducedMotion ? 1 : 0.9 + Math.sin(t * 0.7 + i * 2) * 0.1);
    // converged and nothing animating: allow the loop to idle (reduced motion)
    const moving = Math.abs(goal.yaw - rig.yaw) + Math.abs(goal.dist - rig.dist) + Math.abs(goal.tx - rig.tx) + Math.abs(goal.pitch - rig.pitch) > 0.002 || avatars.some((a) => Math.abs(a.hover - Math.max(a.target, hovered === a.slug ? 0.7 : 0)) > 0.01);
    still = moving ? 0 : still + 1;
  };
  const tick = () => {
    const now = performance.now(), dt = Math.min(0.05, (now - last) / 1000); last = now; t += dt;
    step(dt); render();
    // adaptive quality: lower resolution / drop bloom when frames are slow
    frames++; acc += dt;
    if (acc >= 1) {
      const fps = frames / acc; canvas.dataset.fps = String(Math.round(fps)); frames = 0; acc = 0;
      if (fps < 45) slowStreak++; else slowStreak = 0;
      if (slowStreak >= 2) {
        slowStreak = 0;
        if (dpr > 0.8) { dpr = Math.max(0.75, dpr - 0.25); renderer.setPixelRatio(dpr); if (composer) composer.setPixelRatio(dpr); resize(); }
        else if (composer) { composer = null; canvas.dataset.bloom = 'off'; }
      }
    }
    raf = visible && !(reducedMotion && still > 30) ? requestAnimationFrame(tick) : 0;
  };
  const wake = () => { still = 0; if (!raf && visible) { last = performance.now(); raf = requestAnimationFrame(tick); } };
  canvas.dataset.quality = quality; canvas.dataset.bloom = composer ? 'on' : 'off';
  ready = true; step(0.016); render(); wake();
  const io = typeof IntersectionObserver === 'function' ? new IntersectionObserver(([en]) => { visible = !!en && en.isIntersecting; if (visible) wake(); }) : null;
  if (io) io.observe(container);
  const onVis = () => { visible = document.visibilityState === 'visible'; if (visible) wake(); };
  document.addEventListener('visibilitychange', onVis);
  function resize() {
    const W = container.clientWidth, H = container.clientHeight; if (!W || !H) return;
    renderer.setSize(W, H); if (composer) composer.setSize(W, H); if (bloom) bloom.setSize(W, H);
    camera.aspect = W / H; camera.updateProjectionMatrix(); setView(viewIdx); for (const a of avatars) a.label.w = 0; wake();
  }
  const ro = typeof ResizeObserver === 'function' ? new ResizeObserver(resize) : null;
  if (ro) ro.observe(container); else addEventListener('resize', resize);
  // Screen positions of the avatars (CSS pixels, relative to the canvas): used by tests and by assistive overlays.
  const avatarScreenPositions = () => { const r = canvas.getBoundingClientRect(), v = new Vector3(); return avatars.map((a) => { a.group.getWorldPosition(v); v.y += 1.2; v.project(camera); return { slug: a.slug, x: (v.x + 1) / 2 * r.width, y: (1 - v.y) / 2 * r.height }; }); };
  canvas.campus = { avatarScreenPositions, setView: (i) => setView(i), camera: () => ({ fov: camera.fov, aspect: camera.aspect, pos: camera.position.toArray().map((x) => +x.toFixed(2)), goal: { ...goal }, view: viewIdx }) };
  return {
    canvas,
    highlight,
    quality,
    avatarScreenPositions,
    dispose() {
      cancelAnimationFrame(raf); raf = 0; if (io) io.disconnect(); if (ro) ro.disconnect(); document.removeEventListener('visibilitychange', onVis);
      scene.traverse((o) => { if (o.geometry) o.geometry.dispose(); const m = o.material; if (m) (Array.isArray(m) ? m : [m]).forEach((x) => { if (x.map) x.map.dispose(); if (x.emissiveMap) x.emissiveMap.dispose(); x.dispose(); }); });
      if (composer) composer.dispose?.(); renderer.dispose(); canvas.remove(); nav.remove(); hint.remove(); labelLayer.remove();
    },
  };
}
