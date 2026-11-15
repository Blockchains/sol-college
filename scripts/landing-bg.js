// Sol.College landing: faint drifting particles over the CSS aurora. Cheap by design: a few dozen dots, capped at
// ~30 fps, paused when the tab is hidden, and not started at all with reduced motion or Save-Data.
(function () {
  var c = document.getElementById('bg-particles');
  if (!c || !c.getContext) return;
  var mq = function (q) { return window.matchMedia && window.matchMedia(q).matches; };
  if (mq('(prefers-reduced-motion: reduce)') || (navigator.connection && navigator.connection.saveData)) { c.remove(); return; }
  var g = c.getContext('2d'), dpr = Math.min(window.devicePixelRatio || 1, 1.5), W = 0, H = 0, dots = [], last = 0, raf = 0;
  var N = mq('(max-width: 760px)') ? 22 : 48;
  var cols = ['153,69,255', '120,110,255', '20,241,149', '255,184,107'];
  function size() { W = innerWidth; H = innerHeight; c.width = W * dpr; c.height = H * dpr; g.setTransform(dpr, 0, 0, dpr, 0, 0); }
  function seed() {
    dots = [];
    for (var i = 0; i < N; i++) dots.push({ x: Math.random() * W, y: Math.random() * H, r: 0.6 + Math.random() * 1.6, vx: (Math.random() - 0.5) * 0.08, vy: -0.05 - Math.random() * 0.12, a: 0.15 + Math.random() * 0.45, c: cols[i % 7 === 0 ? 2 : i % 11 === 0 ? 3 : i % 2] });
  }
  function frame(t) {
    raf = requestAnimationFrame(frame);
    if (t - last < 33) return; var dt = Math.min(3, (t - last) / 16.7); last = t;
    g.clearRect(0, 0, W, H);
    for (var i = 0; i < dots.length; i++) {
      var d = dots[i]; d.x += d.vx * dt; d.y += d.vy * dt;
      if (d.y < -10) { d.y = H + 10; d.x = Math.random() * W; } if (d.x < -10) d.x = W + 10; if (d.x > W + 10) d.x = -10;
      g.beginPath(); g.fillStyle = 'rgba(' + d.c + ',' + d.a + ')'; g.shadowColor = 'rgba(' + d.c + ',0.9)'; g.shadowBlur = 8; g.arc(d.x, d.y, d.r, 0, 6.283); g.fill();
    }
  }
  size(); seed();
  addEventListener('resize', function () { size(); });
  document.addEventListener('visibilitychange', function () { if (document.hidden) { cancelAnimationFrame(raf); raf = 0; } else if (!raf) raf = requestAnimationFrame(frame); });
  raf = requestAnimationFrame(frame);
})();
