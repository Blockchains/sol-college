// Sol.College campus: accessible 2D list first; optional 3D view loaded on demand.
// Reads only /campus/data.json (allowlisted public projection). Makes no API calls, invokes no agents.
const $ = (s, el = document) => el.querySelector(s);
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const fmtDate = (iso) => { const d = new Date(iso); return isNaN(d) ? esc(iso) : d.toISOString().slice(0, 10); };
let DATA = null;
let selected = null;

function projectCard(p, headingLevel = 3) {
  const h = `h${headingLevel}`;
  const assignments = p.assignments.length
    ? `<ul>${p.assignments.map((a) => `<li>${a.issueUrl ? `<a href="${esc(a.issueUrl)}">${esc(a.title)}</a>` : esc(a.title)} <span class="small">(${esc(a.status)}; ${a.skills.map(esc).join(', ')})</span></li>`).join('')}</ul>`
    : '<p class="empty">No public assignments yet.</p>';
  const records = p.records.length
    ? `<details><summary>Engineering record (${p.records.length})</summary><ul>${p.records.map((r) => `<li><a href="${esc(r.url)}">${esc(r.title)}</a> <span class="small">${esc(r.type)}, ${fmtDate(r.at)}</span></li>`).join('')}</ul></details>`
    : '<p class="empty">No public records yet.</p>';
  const g = p.progression;
  const paused = p.agent && p.agent.state === 'paused';
  const agentLine = p.agent && p.agent.state !== 'none' ? `<p class="agent-state${paused ? ' is-paused' : ''}"><b>${paused ? 'CTO agent paused' : 'CTO agent active'}.</b> ${esc(p.agent.note)}</p>` : '';
  return `<article class="card${paused ? ' is-paused' : ''}" id="p-${esc(p.slug)}" data-slug="${esc(p.slug)}" tabindex="-1">
    <div class="cto"><span class="avatar" aria-hidden="true"></span><span>${esc(p.cto.label)}</span></div>
    ${agentLine}
    <${h}>${esc(p.displayName)}</${h}>
    <p>${esc(p.description)}</p>
    ${p.demonstrationNotice ? `<p class="demo"><b>Demonstration.</b> ${esc(p.demonstrationNotice)}</p>` : ''}
    <ul class="tags" aria-label="Sector and skills"><li>${esc(p.sector)}</li>${p.requiredSkills.map((s) => `<li>${esc(s)}</li>`).join('')}</ul>
    <p class="small">Status: ${esc(p.status)}. Last updated ${fmtDate(p.lastUpdated)}.</p>
    <div class="prog" aria-label="Contribution progression">
      <div><b>${g.approvedExperiments}</b>experiments</div><div><b>${g.testedCandidates}</b>tested candidates</div><div><b>${g.adoptionPackages}</b>adoption packages</div>
      <div><b>${g.projectAccepted}</b>project-accepted</div><div><b>${g.activeCredentials}</b>active credentials</div><div><b>${g.ideas}</b>ideas</div>
    </div>
    ${liveStatusHtml(p)}
    <h4>Open assignments</h4>${assignments}
    ${records}
    <p class="small">${esc(p.coordination)} <a href="${esc(p.contactRoute)}">Open a coordination request</a>. Repos: <a href="https://github.com/${esc(p.repos.lab)}">lab fork</a>, <a href="https://github.com/${esc(p.repos.upstream)}">upstream</a>.</p>
  </article>`;
}

function liveStatusHtml(p) {
  const s = p.liveStatus;
  if (!s) return '<p class="small">CTO agent status: no autonomous run recorded yet.</p>';
  const act = s.activity.slice(0, 4).map((a) => `<li>${a.url ? `<a href="${esc(a.url)}">${esc(a.text)}</a>` : esc(a.text)} <span class="small">${fmtDate(a.at)}</span></li>`).join('');
  return `<div class="live"><h4>CTO agent status <span class="small">(updated ${fmtDate(s.updatedAt)}${s.runUrl ? `, <a href="${esc(s.runUrl)}">run</a>` : ''})</span></h4>
    ${s.report ? `<p>${esc(s.report.summary)}</p>` : '<p class="small">Lab Reporter status pending.</p>'}
    <p class="small">${s.pendingTasks} task(s) in progress with the CTO agent; ${s.openLabPullRequests} open lab pull request(s).</p>
    ${act ? `<ul class="small">${act}</ul>` : ''}</div>`;
}

function filtered() {
  const q = $('#q').value.trim().toLowerCase();
  const sector = (document.querySelector('input[name=sector]:checked') || {}).value || '';
  const openOnly = $('#openOnly').checked;
  return DATA.projects.filter((p) => {
    if (sector && p.sector !== sector) return false;
    if (openOnly && !p.assignments.some((a) => a.status === 'open')) return false;
    if (!q) return true;
    const hay = [p.displayName, p.description, p.sector, ...p.requiredSkills, ...p.assignments.map((a) => a.title)].join(' ').toLowerCase();
    return hay.includes(q);
  });
}

function renderRooms() {
  const list = filtered();
  const sector = (document.querySelector('input[name=sector]:checked') || {}).value || '';
  $('#count').textContent = `${list.length} of ${DATA.projects.length} project${DATA.projects.length === 1 ? '' : 's'} shown`;
  $('#rooms').innerHTML = DATA.sectors.filter((s) => !sector || s.id === sector).map((s) => {
    // active CTO agents first, paused ones after (stable order otherwise)
    const ps = list.filter((p) => p.sector === s.id).sort((x, y) => ((x.agent && x.agent.state === 'paused') ? 1 : 0) - ((y.agent && y.agent.state === 'paused') ? 1 : 0));
    return `<section class="room" aria-labelledby="room-${s.id}"><h2 id="room-${s.id}">${esc(s.name)} room <small>${esc(s.blurb)}</small></h2>
      ${ps.length ? `<div class="cards">${ps.map((p) => projectCard(p)).join('')}</div>` : `<p class="empty">No ${s.id === 'DeFi' ? 'matching ' : ''}projects in this room yet.</p>`}</section>`;
  }).join('');
  if (selected) { const el = document.getElementById(`p-${selected}`); if (el) el.classList.add('selected'); }
}

export function selectProject(slug, { focusList = false } = {}) {
  selected = slug;
  document.querySelectorAll('.card.selected').forEach((c) => c.classList.remove('selected'));
  const el = document.getElementById(`p-${slug}`);
  if (el) { el.classList.add('selected'); if (focusList) { el.scrollIntoView({ block: 'center' }); el.focus(); } }
  const p = DATA.projects.find((x) => x.slug === slug);
  const ov = $('#overlay');
  if (p && !$('#stage').hidden) {
    ov.innerHTML = `<button type="button" id="closeOv" aria-label="Close details" style="float:right">×</button><div id="overlayTitle"></div>${projectCard(p, 3).replace('tabindex="-1"', '')}`;
    ov.hidden = false;
    $('#closeOv').onclick = () => { ov.hidden = true; };
  }
}

function renderCredentials() {
  const cs = DATA.credentials;
  $('#credList').innerHTML = cs.length
    ? `<h3>Published credentials</h3><ul>${cs.map((c) => `<li><code>${esc(c.credentialId)}</code>: ${esc(c.subject)}, ${esc(c.acceptedWork)} (${esc(c.project)}) <b class="${c.status === 'active' ? 'ok' : 'bad'}">${esc(c.status)}</b></li>`).join('')}</ul>`
    : '<p class="empty">No credentials have been issued yet. A credential appears only after an authorised project reviewer accepts an exact adoption package.</p>';
}

function verify(id) {
  const out = $('#verifyOut');
  const c = DATA.credentials.find((x) => x.credentialId === id.trim());
  if (!id.trim()) { out.innerHTML = ''; return; }
  if (!c) { out.innerHTML = `<p class="bad">No credential with ID <code>${esc(id)}</code> is published by Sol.College.</p>`; return; }
  const hist = c.statusHistory.map((h) => `<li>${esc(h.status)} on ${fmtDate(h.changedAt)}${h.reason ? `: ${esc(h.reason)}` : ''}</li>`).join('');
  out.innerHTML = `<div class="card"><p><b class="${c.status === 'active' ? 'ok' : 'bad'}">${c.status === 'active' ? 'Active' : c.status === 'revoked' ? 'Revoked' : 'Superseded'}</b> credential <code>${esc(c.credentialId)}</code></p>
    <p>${esc(c.subject)}: <b>${esc(c.acceptedWork)}</b> in ${esc(c.project)}. Accepted commit <code>${esc(c.acceptedCommit.slice(0, 12))}</code>, package ${esc(c.packageId)}, accepted by ${esc(c.reviewer)}, issued ${fmtDate(c.issuedAt)}.</p>
    <ul>${hist}</ul><p><a href="${esc(c.recordUrl)}">Published record</a></p></div>`;
}

async function main() {
  const r = await fetch('/campus/data.json', { cache: 'no-cache' });
  DATA = await r.json();
  $('#notices').innerHTML = DATA.notices.map((n) => `<li>${esc(n)}</li>`).join('');
  renderRooms();
  renderCredentials();
  // Deep link from the landing page: /campus/#p-<slug> selects and focuses that project card.
  const hp = decodeURIComponent(location.hash.replace(/^#p-/, ''));
  if (location.hash.startsWith('#p-') && DATA.projects.some((p) => p.slug === hp)) selectProject(hp, { focusList: true });
  $('#filters').addEventListener('input', renderRooms);
  $('#verifyForm').addEventListener('submit', (e) => { e.preventDefault(); verify($('#credId').value); history.replaceState(null, '', `?id=${encodeURIComponent($('#credId').value.trim())}#verify`); });
  const qid = new URLSearchParams(location.search).get('id');
  if (qid) { $('#credId').value = qid; verify(qid); }
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const coarse = matchMedia('(pointer: coarse)').matches || matchMedia('(max-width: 760px)').matches;
  const quality = coarse || (navigator.hardwareConcurrency || 8) <= 4 || (navigator.deviceMemory || 8) <= 4 ? 'low' : 'high';
  const saver = (navigator.connection || {}).saveData === true;
  $('#motionNote').textContent = reduce ? 'Reduced motion is on: the 3D view is not shown automatically and does not animate.' : '';
  let scene = null;
  const toggle = async (show) => {
    const stage = $('#stage');
    stage.hidden = !show;
    $('#toggle3d').setAttribute('aria-pressed', String(show));
    $('#toggle3d').textContent = show ? 'Hide 3D campus' : 'Show 3D campus';
    if (show && !scene) {
      try {
        const mod = await import('/campus/campus3d.js');
        scene = mod.mountCampus($('#canvasWrap'), DATA, { reducedMotion: reduce, quality, onSelect: (slug) => selectProject(slug, { focusList: false }) });
      } catch (e) {
        $('#canvasWrap').innerHTML = `<p class="small" style="padding:12px">3D view unavailable on this device (${esc(e.message)}). The list is the full campus.</p>`;
      }
    }
    if (!show) $('#overlay').hidden = true;
  };
  $('#toggle3d').addEventListener('click', () => toggle($('#stage').hidden));
  // Show the 3D campus automatically (phones included) unless reduced motion or data saver is on; the list stays the full view.
  const webgl = (() => { try { const c = document.createElement('canvas'); return !!(c.getContext('webgl2') || c.getContext('webgl')); } catch { return false; } })();
  if (!reduce && !saver && webgl && !location.hash.startsWith('#p-')) (window.requestIdleCallback || ((f) => setTimeout(f, 200)))(() => toggle(true));
}
main().catch((e) => { $('#rooms').innerHTML = `<p class="bad">Could not load campus data: ${esc(e.message)}</p>`; });
