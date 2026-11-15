// Sol.College landing: live campus hero.
// First paint = server-rendered 2D rooms (no JS needed). After load (when the browser is idle), three.js is
// lazy-loaded from /campus/campus3d.js and the 2D rooms become a compact list under the 3D scene. Phones get the
// 3D scene too, in a lighter "low" quality (no bloom, fewer particles, capped resolution, adaptive DPR).
// Reduced motion, no WebGL, Save-Data / 2g and very low-memory devices keep the accessible 2D rooms.
// Data: embedded allowlisted list (#ch-data) and, when available, the public projection /campus/data.json.
// No agent is called and no conversation is started from this page.
const $ = (s, el = document) => el.querySelector(s);
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const hero = $('#campus-hero');
if (hero) init();

function init() {
  const stage = $('#ch-stage');
  const dialog = $('#ch-dialog');
  const embedded = JSON.parse(($('#ch-data') || {}).textContent || '[]');
  let full = null;          // /campus/data.json, fetched lazily
  let scene = null;         // 3D handle
  let lastTrigger = null;

  const loadFull = () => full ? Promise.resolve(full) : fetch('/campus/data.json', { cache: 'no-cache' })
    .then((r) => (r.ok ? r.json() : Promise.reject(new Error(String(r.status)))))
    .then((d) => (d && Array.isArray(d.projects) && Array.isArray(d.sectors) ? (full = d) : Promise.reject(new Error('bad data'))));

  const detailHtml = (slug) => {
    const fp = full && full.projects.find((p) => p.slug === slug);
    const ep = embedded.find((p) => p.slug === slug);
    const p = fp || ep;
    if (!p) return '<p>Project not found.</p>';
    const ag = (fp && fp.agent) || ep && ep.agent;
    const state = ag ? (ag.state === 'paused' ? `<p class="ch-agent is-paused"><b>CTO agent paused.</b> ${esc(ag.note)}</p>` : ag.state === 'active' ? `<p class="ch-agent"><span class="live-dot" aria-hidden="true"></span><b>CTO agent active.</b> ${esc(ag.note)}</p>` : '') : '';
    const demo = p.demonstrationNotice ? `<p class="ch-demo-note"><b>Demonstration project.</b> ${esc(p.demonstrationNotice)}</p>` : '';
    let more = '';
    if (fp) {
      const g = fp.progression || {};
      const open = (fp.assignments || []).filter((a) => a.status === 'open');
      more = `<p class="ch-meta">${esc(fp.sector)} room · ${esc(fp.status)} · ${esc(fp.cto && fp.cto.label)}</p>
        <ul class="ch-prog" aria-label="Contribution progression">
          <li><b>${g.approvedExperiments ?? 0}</b> experiments</li><li><b>${g.testedCandidates ?? 0}</b> tested candidates</li>
          <li><b>${g.adoptionPackages ?? 0}</b> adoption packages</li><li><b>${g.projectAccepted ?? 0}</b> project-accepted</li>
          <li><b>${g.activeCredentials ?? 0}</b> active credentials</li></ul>
        ${open.length ? `<h4>Open assignments</h4><ul>${open.map((a) => `<li>${a.issueUrl ? `<a href="${esc(a.issueUrl)}">${esc(a.title)}</a>` : esc(a.title)}</li>`).join('')}</ul>` : ''}
        ${fp.liveStatus ? `<h4>CTO agent status</h4>${fp.liveStatus.report ? `<p>${esc(fp.liveStatus.report.summary)}</p>` : ''}<p class="ch-meta">${fp.liveStatus.pendingTasks} task(s) in progress · ${fp.liveStatus.openLabPullRequests} open lab PR(s) · updated ${esc(String(fp.liveStatus.updatedAt).slice(0, 16).replace('T', ' '))} UTC${fp.liveStatus.runUrl ? ` · <a href="${esc(fp.liveStatus.runUrl)}">latest run</a>` : ''}</p>${fp.liveStatus.activity.length ? `<ul class="ch-meta">${fp.liveStatus.activity.slice(0, 3).map((a) => `<li>${a.url ? `<a href="${esc(a.url)}">${esc(a.text)}</a>` : esc(a.text)}</li>`).join('')}</ul>` : ''}` : ''}
        <p class="ch-meta">Repos: <a href="https://github.com/${esc(fp.repos.lab)}">lab fork</a> · <a href="https://github.com/${esc(fp.repos.upstream)}">upstream</a> · <a href="${esc(fp.contactRoute)}">coordination request</a></p>`;
    } else {
      more = `<p class="ch-meta">${esc(p.sector)} room</p>`;
    }
    return `<h3 id="ch-dialog-title">${esc(p.displayName)}</h3>${state}<p>${esc(p.description)}</p>${demo}${more}
      <p><a href="/campus/#p-${encodeURIComponent(p.slug)}">Open in the campus</a></p>`;
  };

  const open = (slug, trigger) => {
    lastTrigger = trigger || document.activeElement;
    if (scene) scene.highlight(slug);
    const show = () => {
      $('#ch-dialog-body').innerHTML = detailHtml(slug);
      if (typeof dialog.showModal === 'function') {
        if (!dialog.open) dialog.showModal();
        // start at the top (the Close button would otherwise take focus and scroll the dialog to the bottom)
        const h = $('#ch-dialog-title'); if (h) { h.tabIndex = -1; h.focus(); } dialog.scrollTop = 0;
      }
      else { location.href = `/campus/#p-${encodeURIComponent(slug)}`; }
    };
    loadFull().then(show, show);
  };
  dialog.addEventListener('close', () => { if (lastTrigger && document.contains(lastTrigger)) lastTrigger.focus(); });
  dialog.addEventListener('click', (e) => { if (e.target === dialog) dialog.close(); }); // backdrop click

  hero.addEventListener('click', (e) => {
    const b = e.target.closest('.ch-avatar');
    if (b) open(b.dataset.slug, b);
  });

  // ---- decide whether to upgrade to 3D ----
  const mq = (q) => window.matchMedia && window.matchMedia(q).matches;
  const reduced = () => mq('(prefers-reduced-motion: reduce)');
  const lowPower = () => {
    const c = navigator.connection || {};
    return c.saveData === true || /(^|-)2g$/.test(c.effectiveType || '') || (navigator.deviceMemory || 8) < 1 || (navigator.hardwareConcurrency || 8) < 2;
  };
  const quality = () => (mq('(pointer: coarse)') || mq('(max-width: 760px)') || (navigator.hardwareConcurrency || 8) <= 4 || (navigator.deviceMemory || 8) <= 4 ? 'low' : 'high');
  const webgl = () => { try { const c = document.createElement('canvas'); return !!(window.WebGLRenderingContext && (c.getContext('webgl2') || c.getContext('webgl'))); } catch { return false; } };
  const why = () => (reduced() ? 'reduced motion is on' : lowPower() ? 'data saver or a low-power device' : !webgl() ? 'WebGL is not available' : '');

  const setMode = (m, note) => {
    stage.dataset.mode = m;
    const n = $('#ch-note');
    if (n && note) n.textContent = note;
  };

  async function upgrade() {
    if (scene || why()) { if (why()) setMode('2d', `Showing the 2D rooms (${why()}). Select a project to see its details.`); return; }
    try {
      const [mod, data] = await Promise.all([import('/campus/campus3d.js'), loadFull()]);
      if (why()) return;
      const holder = document.createElement('div');
      holder.className = 'ch-canvas';
      stage.prepend(holder);
      const slugs = new Set(embedded.map((p) => p.slug));
      // Only projects that are both in the build-time list and the public projection are shown.
      const shown = { sectors: data.sectors, projects: data.projects.filter((p) => slugs.has(p.slug)) };
      scene = mod.mountCampus(holder, shown, {
        reducedMotion: false,
        quality: quality(),
        onSelect: (slug) => open(slug, scene && scene.canvas),
        onFocusAvatar: (slug) => { const n = $('#ch-note'); const p = shown.projects.find((x) => x.slug === slug); if (n && p) n.textContent = `${p.displayName}: press Enter for details.`; },
      });
      setMode('3d', mq('(pointer: coarse)')
        ? 'Tap an avatar to see project details. Swipe sideways or use the room buttons to move between rooms. The same projects are listed below.'
        : 'Click an avatar (or focus the scene: arrow keys move between avatars and rooms, Enter opens details). Drag to look around. The same projects are listed below.');
    } catch (err) {
      if (window.console) console.warn('campus 3D unavailable:', err && err.message);
      setMode('2d', 'Showing the 2D rooms (the 3D view could not load). Select a project to see its details.');
    }
  }
  // Capable devices show a CSS preview of the room right away (data-mode="loading") and start loading the 3D
  // bundle as soon as the main thread is idle (no waiting for every image on the page).
  if (!why()) setMode('loading');
  const later = window.requestIdleCallback ? (f) => window.requestIdleCallback(f, { timeout: 1200 }) : (f) => setTimeout(f, 200);
  later(upgrade);

  // Turning reduced motion on (or rotating to a small screen) drops back to 2D.
  const downgrade = () => { if (scene && why()) { scene.dispose(); scene = null; $('.ch-canvas', stage)?.remove(); setMode('2d', `Showing the 2D rooms (${why()}). Select a project to see its details.`); } };
  window.matchMedia?.('(prefers-reduced-motion: reduce)').addEventListener?.('change', downgrade);
}
