// Optional 3D campus (three.js, bundled by esbuild at build time). Three shared sector rooms with one
// avatar per project CTO agent. Click/tap or keyboard (Tab to canvas wrapper is not needed: the list is
// the accessible view) selects an avatar and opens the same details overlay. No network calls; selecting
// or approaching an avatar never invokes an agent.
import { Scene, PerspectiveCamera, WebGLRenderer, Color, HemisphereLight, DirectionalLight, Mesh, MeshStandardMaterial,
  BoxGeometry, CylinderGeometry, SphereGeometry, Group, Raycaster, Vector2, CanvasTexture, SpriteMaterial, Sprite } from 'three';

const ROOM_COLORS = { DeFi: 0x14f195, DePIN: 0x00c2ff, DeAI: 0x9945ff };

function label(text, color = '#e9edf5') {
  const c = document.createElement('canvas'); c.width = 512; c.height = 128;
  const g = c.getContext('2d'); g.font = 'bold 54px system-ui, sans-serif'; g.fillStyle = color; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillText(text.length > 22 ? text.slice(0, 21) + '…' : text, 256, 64);
  const s = new Sprite(new SpriteMaterial({ map: new CanvasTexture(c), transparent: true, depthWrite: false }));
  s.scale.set(4, 1, 1); return s;
}

export function mountCampus(container, data, { reducedMotion, onSelect }) {
  const w = container.clientWidth || 800, h = container.clientHeight || 440;
  const renderer = new WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2)); renderer.setSize(w, h);
  container.appendChild(renderer.domElement);
  const scene = new Scene(); scene.background = new Color(0x06070a);
  const camera = new PerspectiveCamera(50, w / h, 0.1, 200); camera.position.set(0, 14, 20); camera.lookAt(0, 0, 0);
  scene.add(new HemisphereLight(0xffffff, 0x223344, 1.1));
  const sun = new DirectionalLight(0xffffff, 1.2); sun.position.set(5, 12, 8); scene.add(sun);
  const avatars = [];
  data.sectors.forEach((s, i) => {
    const room = new Group(); room.position.x = (i - 1) * 11;
    const floor = new Mesh(new BoxGeometry(10, 0.3, 10), new MeshStandardMaterial({ color: ROOM_COLORS[s.id], transparent: true, opacity: 0.25 }));
    room.add(floor);
    for (const [x, z, sx, sz] of [[0, -5, 10, 0.2], [-5, 0, 0.2, 10], [5, 0, 0.2, 10]]) {
      const wall = new Mesh(new BoxGeometry(sx, 1.6, sz), new MeshStandardMaterial({ color: ROOM_COLORS[s.id], transparent: true, opacity: 0.35 }));
      wall.position.set(x, 0.8, z); room.add(wall);
    }
    const t = label(`${s.name} room`); t.position.set(0, 3.2, -4.5); room.add(t);
    const ps = data.projects.filter((p) => p.sector === s.id);
    if (ps.length === 0) { const e = label('no projects yet', '#9aa4b5'); e.position.set(0, 1.2, 0); room.add(e); }
    ps.forEach((p, j) => {
      const a = new Group(); const cols = Math.ceil(Math.sqrt(ps.length));
      a.position.set(((j % cols) - (cols - 1) / 2) * 2.6, 0.15, (Math.floor(j / cols) - 0.5) * 2.6 + 1);
      const mat = new MeshStandardMaterial({ color: 0xe9edf5, emissive: ROOM_COLORS[s.id], emissiveIntensity: 0.25 });
      const body = new Mesh(new CylinderGeometry(0.45, 0.55, 1.4, 20), mat); body.position.y = 0.85;
      const head = new Mesh(new SphereGeometry(0.42, 20, 16), mat); head.position.y = 1.9;
      body.userData.slug = head.userData.slug = p.slug;
      a.add(body, head);
      const n = label(p.displayName.replace(/\s*\(.*\)$/, '')); n.position.set(0, 2.9, 0); n.scale.set(3.2, 0.8, 1); a.add(n);
      room.add(a); avatars.push({ group: a, meshes: [body, head], mat, slug: p.slug });
    });
    scene.add(room);
  });
  const ray = new Raycaster(); const v = new Vector2();
  renderer.domElement.addEventListener('pointerdown', (e) => {
    const r = renderer.domElement.getBoundingClientRect();
    v.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
    ray.setFromCamera(v, camera);
    const hit = ray.intersectObjects(avatars.flatMap((a) => a.meshes))[0];
    if (hit) { avatars.forEach((a) => (a.mat.emissiveIntensity = a.slug === hit.object.userData.slug ? 0.9 : 0.25)); onSelect(hit.object.userData.slug); render(); }
  });
  let angle = 0, raf = 0;
  const render = () => renderer.render(scene, camera);
  const tick = () => { angle += 0.0015; camera.position.x = Math.sin(angle) * 20; camera.position.z = Math.cos(angle) * 20; camera.lookAt(0, 0, 0); render(); raf = requestAnimationFrame(tick); };
  if (reducedMotion) render(); else tick();
  addEventListener('resize', () => { const W = container.clientWidth, H = container.clientHeight; renderer.setSize(W, H); camera.aspect = W / H; camera.updateProjectionMatrix(); render(); });
  return { dispose() { cancelAnimationFrame(raf); renderer.dispose(); } };
}
