// The landing hero is a generated film still. The group takes turns speaking,
// and each halo holds a practice-app mark. Reduced motion keeps one still frame
// with the marks in place. The 3D campus stays on /campus/.
(function () {
  const canvas = document.getElementById('film-stage');
  if (!canvas || !canvas.getContext) return;
  const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const fine = window.matchMedia && window.matchMedia('(pointer: fine)').matches;
  const narrow = () => window.matchMedia && window.matchMedia('(max-width: 760px)').matches;
  const ctx = canvas.getContext('2d', { alpha: false });

  // Ring centers are fractions of the still, measured on the halo itself.
  // s is the icon diameter as a fraction of the still width, sized to the
  // opening inside the ring so the colored halo stays the frame.
  const WIDE = [
    { x: 0.481, y: 0.284, s: 0.014, icon: '/assets/marks/poe-solana.jpg' },
    { x: 0.574, y: 0.278, s: 0.014, icon: '/assets/marks/orrery.jpg' },
    { x: 0.672, y: 0.286, s: 0.014, icon: '/assets/marks/trustlock.jpg' },
    { x: 0.797, y: 0.280, s: 0.014, icon: '/assets/marks/picassol-hackathon.jpg' },
    { x: 0.882, y: 0.300, s: 0.014, icon: '/assets/marks/hydra.jpg' },
  ];
  const TALL = [
    { x: 0.181, y: 0.252, s: 0.024, icon: '/assets/marks/poe-solana.jpg' },
    { x: 0.354, y: 0.262, s: 0.024, icon: '/assets/marks/orrery.jpg' },
    { x: 0.503, y: 0.261, s: 0.024, icon: '/assets/marks/trustlock.jpg' },
    { x: 0.656, y: 0.261, s: 0.024, icon: '/assets/marks/picassol-hackathon.jpg' },
    { x: 0.800, y: 0.257, s: 0.024, icon: '/assets/marks/hydra.jpg' },
  ];
  const BEATS = [
    { key: 'a', who: [0, 1] },
    { key: 'b', who: [2, 3] },
    { key: 'c', who: [4, 3] },
  ];
  // A beat rests, then the heads ease into the next turn. The old 0.38s
  // linear swap snapped. The fade stays shorter than the hold so two
  // poses only overlap while a head is actually turning.
  const HOLD = 7.2;
  const FADE = 1.35;

  const icons = {};
  function image(url) {
    const im = new Image();
    im.decoding = 'async';
    im.src = url;
    return im;
  }
  function iconFor(url) {
    if (!icons[url]) icons[url] = image(url);
    return icons[url];
  }
  WIDE.concat(TALL).forEach(function (p) { iconFor(p.icon); });

  let pack = null;
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

  function makePack(phone) {
    const tag = phone ? 'tall' : 'wide';
    return {
      tag: tag,
      cast: phone ? TALL : WIDE,
      base: image(phone ? '/assets/hero-tall.jpg' : '/assets/hero-wide.jpg'),
      a: image('/assets/hero-talk-' + tag + '-a.jpg'),
      b: image('/assets/hero-talk-' + tag + '-b.jpg'),
      c: image('/assets/hero-talk-' + tag + '-c.jpg'),
    };
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

  function place(now) {
    const img = pack.base;
    const phone = pack.tag === 'tall';
    const t = now / 1000;
    const live = reduce ? 0 : 1;
    // Fit the still inside the stage so the illustration stays fully visible.
    const iw = img.naturalWidth;
    const ih = img.naturalHeight;
    const scale = Math.min(W / iw, H / ih);
    const dw = iw * scale;
    const dh = ih * scale;
    const dx = (W - dw) / 2;
    const dy = (H - dh) / 2;
    return { dx: dx, dy: dy, dw: dw, dh: dh, t: t, live: live, phone: phone };
  }

  function ease(u) {
    u = Math.max(0, Math.min(1, u));
    return u * u * (3 - 2 * u);
  }

  function talkAlpha(local) {
    if (local < FADE) return ease(local / FADE);
    if (local > HOLD - FADE) return ease((HOLD - local) / FADE);
    return 1;
  }

  function drawIcon(box, p, emphasis) {
    const img = iconFor(p.icon);
    if (!img.complete || !img.naturalWidth) return;
    const s = box.dw * p.s * (1 + 0.04 * emphasis);
    const sx = box.dx + p.x * box.dw;
    const sy = box.dy + p.y * box.dh;
    ctx.save();
    ctx.beginPath();
    ctx.arc(sx, sy, s / 2, 0, Math.PI * 2);
    ctx.fillStyle = '#f4efe6';
    ctx.fill();
    ctx.save();
    ctx.clip();
    const side = s * 1.55;
    ctx.drawImage(img, sx - side / 2, sy - side / 2, side, side);
    ctx.restore();
    ctx.lineWidth = Math.max(1.5, s * 0.045);
    ctx.strokeStyle = emphasis > 0.4 ? 'rgba(255,255,255,0.95)' : 'rgba(255,255,255,0.72)';
    ctx.stroke();
    ctx.restore();
  }

  function draw(now) {
    if (!ready || !W || !H || !pack) return;
    const box = place(now);
    const cast = pack.cast;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.fillStyle = '#f6f1e8';
    ctx.fillRect(0, 0, W, H);
    ctx.drawImage(pack.base, box.dx, box.dy, box.dw, box.dh);

    const beat = box.live ? BEATS[Math.floor(box.t / HOLD) % BEATS.length] : null;
    const alpha = beat ? talkAlpha(box.t % HOLD) : 0;
    const talk = beat && pack[beat.key];
    if (talk && talk.complete && talk.naturalWidth && alpha > 0.02) {
      ctx.save();
      ctx.globalAlpha = alpha;
      ctx.drawImage(talk, box.dx, box.dy, box.dw, box.dh);
      ctx.restore();
    }

    for (let i = 0; i < cast.length; i++) {
      const speaking = beat && beat.who.indexOf(i) !== -1 ? alpha : 0;
      drawIcon(box, cast[i], speaking);
    }

    if (!box.live) return;
    ctx.save();
    ctx.globalCompositeOperation = 'screen';
    const shaft = ctx.createLinearGradient(W * 0.78, 0, W * 0.42, H);
    const glow = 0.16 + Math.sin(box.t * 0.35) * 0.05;
    shaft.addColorStop(0, 'rgba(255, 246, 214, ' + glow + ')');
    shaft.addColorStop(0.42, 'rgba(255, 236, 190, 0)');
    ctx.fillStyle = shaft;
    ctx.translate(Math.sin(box.t * 0.22) * 24, 0);
    ctx.fillRect(-40, 0, W + 80, H);
    const ring = ctx.createRadialGradient(W * 0.66, H * 0.72, 8, W * 0.66, H * 0.72, Math.max(W, H) * 0.42);
    const pulse = 0.1 + Math.sin(box.t * 0.85) * 0.035;
    ring.addColorStop(0, 'rgba(120, 255, 214, ' + pulse + ')');
    ring.addColorStop(0.45, 'rgba(170, 120, 255, ' + (pulse * 0.55) + ')');
    ring.addColorStop(1, 'rgba(0, 0, 0, 0)');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.fillStyle = ring;
    ctx.fillRect(0, 0, W, H);
    ctx.globalCompositeOperation = 'lighter';
    for (let i = 0; i < motes.length; i++) {
      const m = motes[i];
      const x = m.x * W + Math.sin(box.t * m.s + m.p) * 28;
      const y = ((m.y * H - ((box.t * m.s * 22) % H)) + H) % H;
      ctx.globalAlpha = m.a * (0.45 + 0.55 * Math.sin(box.t * 1.3 + m.p));
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
    const phone = narrow();
    const tag = phone ? 'tall' : 'wide';
    if (pack && pack.tag === tag && ready) {
      resize();
      draw(performance.now());
      return;
    }
    pack = makePack(phone);
    ready = false;
    pack.base.onload = function () {
      ready = true;
      start();
    };
    if (pack.base.complete && pack.base.naturalWidth) {
      ready = true;
      start();
    }
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
