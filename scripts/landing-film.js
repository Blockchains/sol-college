// The landing hero is a generated film still, kept alive with a slow camera, window light, and dust.
// Reduced motion draws one still frame. The 3D campus stays on /campus/.
(function () {
  const canvas = document.getElementById('film-stage');
  if (!canvas || !canvas.getContext) return;
  const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const fine = window.matchMedia && window.matchMedia('(pointer: fine)').matches;
  const narrow = () => window.matchMedia && window.matchMedia('(max-width: 760px)').matches;
  const ctx = canvas.getContext('2d', { alpha: false });
  const img = new Image();
  let ready = false;
  let playing = false;
  let W = 0;
  let H = 0;
  let dpr = 1;
  let px = 0;
  let py = 0;
  const motes = [];
  for (let i = 0; i < 56; i++) {
    motes.push({
      x: Math.random(),
      y: Math.random(),
      r: 0.7 + Math.random() * 1.8,
      s: 0.12 + Math.random() * 0.4,
      p: Math.random() * Math.PI * 2,
      a: 0.18 + Math.random() * 0.5,
    });
  }

  function src() {
    return narrow() ? '/assets/hero-tall.jpg' : '/assets/hero-wide.jpg';
  }

  function resize() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = canvas.clientWidth;
    H = canvas.clientHeight;
    canvas.width = Math.max(1, Math.round(W * dpr));
    canvas.height = Math.max(1, Math.round(H * dpr));
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';
  }

  function draw(now) {
    if (!ready || !W || !H) return;
    const t = now / 1000;
    const live = reduce ? 0 : 1;
    const phone = narrow();
    const zoom = (phone ? 1.04 : 1.05) + Math.sin(t * 0.16) * 0.025 * live;
    const ox = (Math.sin(t * 0.11) * (phone ? 10 : 16) + px * 22) * live;
    const oy = (Math.cos(t * 0.09) * 10 + py * 12) * live;
    const iw = img.naturalWidth;
    const ih = img.naturalHeight;
    const scale = Math.max(W / iw, H / ih) * zoom;
    const dw = iw * scale;
    const dh = ih * scale;
    // Keep the group in frame. The wide still has open wall on the left, so the crop prefers that side.
    let dx = (W - dw) / 2 + ox;
    if (!phone) dx = Math.max(dx, W - dw + 6);
    const dy = (H - dh) / 2 + oy;
    ctx.fillStyle = '#f6f1e8';
    ctx.fillRect(0, 0, W, H);
    ctx.drawImage(img, dx, dy, dw, dh);
    if (!live) return;
    ctx.save();
    ctx.globalCompositeOperation = 'screen';
    const shaft = ctx.createLinearGradient(W * 0.78, 0, W * 0.42, H);
    const glow = 0.16 + Math.sin(t * 0.35) * 0.05;
    shaft.addColorStop(0, 'rgba(255, 246, 214, ' + glow + ')');
    shaft.addColorStop(0.42, 'rgba(255, 236, 190, 0)');
    ctx.fillStyle = shaft;
    ctx.translate(Math.sin(t * 0.22) * 24, 0);
    ctx.fillRect(-40, 0, W + 80, H);
    const ring = ctx.createRadialGradient(W * 0.66, H * 0.72, 8, W * 0.66, H * 0.72, Math.max(W, H) * 0.42);
    const pulse = 0.1 + Math.sin(t * 0.85) * 0.035;
    ring.addColorStop(0, 'rgba(120, 255, 214, ' + pulse + ')');
    ring.addColorStop(0.45, 'rgba(170, 120, 255, ' + (pulse * 0.55) + ')');
    ring.addColorStop(1, 'rgba(0, 0, 0, 0)');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.fillStyle = ring;
    ctx.fillRect(0, 0, W, H);
    ctx.globalCompositeOperation = 'lighter';
    for (let i = 0; i < motes.length; i++) {
      const m = motes[i];
      const x = m.x * W + Math.sin(t * m.s + m.p) * 28;
      const y = ((m.y * H - ((t * m.s * 22) % H)) + H) % H;
      ctx.globalAlpha = m.a * (0.45 + 0.55 * Math.sin(t * 1.3 + m.p));
      ctx.fillStyle = i % 5 === 0 ? '#d7c6ff' : '#fff6df';
      ctx.beginPath();
      ctx.arc(x, y, m.r, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();
  }

  function frame(now) {
    draw(now);
    if (!reduce) requestAnimationFrame(frame);
  }

  function start() {
    resize();
    if (reduce) { draw(performance.now()); return; }
    if (playing) return;
    playing = true;
    requestAnimationFrame(frame);
  }

  function load() {
    const next = src();
    if (img.getAttribute('data-src') === next && ready) {
      resize();
      draw(performance.now());
      return;
    }
    ready = false;
    img.onload = function () {
      ready = true;
      img.setAttribute('data-src', next);
      start();
    };
    img.src = next;
  }

  if (fine && !reduce) {
    window.addEventListener('pointermove', function (e) {
      px = e.clientX / window.innerWidth - 0.5;
      py = e.clientY / window.innerHeight - 0.5;
    }, { passive: true });
  }
  window.addEventListener('resize', load);
  if (window.ResizeObserver) new ResizeObserver(function () { resize(); }).observe(canvas);
  load();
})();
