/* Stale-tab / cache update notice. Compares /release.json to a local snapshot. */
(function () {
  var KEY = 'sc-release-seen';
  var BANNER_ID = 'sc-release-banner';

  function load() {
    try { return JSON.parse(localStorage.getItem(KEY) || 'null'); }
    catch (e) { return null; }
  }
  function save(v) {
    try { localStorage.setItem(KEY, JSON.stringify(v)); }
    catch (e) {}
  }
  function esc(s) {
    return String(s || '').replace(/[&<>"']/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c];
    });
  }

  function showBanner(rel) {
    if (document.getElementById(BANNER_ID)) return;
    var el = document.createElement('div');
    el.id = BANNER_ID;
    el.setAttribute('role', 'status');
    el.style.cssText = [
      'position:sticky', 'top:0', 'z-index:100', 'padding:10px 14px',
      'background:#14122a', 'color:#eee', 'border-bottom:1px solid #3a3658',
      'font:14px/1.4 ui-sans-serif,system-ui,sans-serif', 'display:flex',
      'gap:12px', 'align-items:center', 'justify-content:space-between', 'flex-wrap:wrap'
    ].join(';');
    el.innerHTML =
      '<p style="margin:0;max-width:46rem">A newer Sol.College build is available' +
      (rel && rel.app_release ? ' (<code>' + esc(rel.app_release) + '</code>)' : '') +
      '. Reload to pick up lesson and curriculum updates. Your local progress stays in this browser.</p>' +
      '<span style="display:flex;gap:8px;flex-wrap:wrap">' +
      '<button type="button" data-reload style="min-height:40px;padding:8px 12px;border-radius:8px;border:0;background:#14f195;color:#0b0a14;font-weight:700;cursor:pointer">Reload</button>' +
      '<button type="button" data-dismiss style="min-height:40px;padding:8px 12px;border-radius:8px;border:1px solid #5a5678;background:transparent;color:#eee;cursor:pointer">Dismiss</button>' +
      '</span>';
    el.querySelector('[data-reload]').addEventListener('click', function () {
      location.reload();
    });
    el.querySelector('[data-dismiss]').addEventListener('click', function () {
      save({
        app_release: rel.app_release,
        curriculum_version: rel.curriculum_version,
        built_at: rel.built_at,
        dismissed: true,
        at: Date.now()
      });
      el.remove();
    });
    document.body.insertBefore(el, document.body.firstChild);
  }

  function check() {
    if (typeof fetch !== 'function') return;
    fetch('/release.json', { cache: 'no-store' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (rel) {
        if (!rel || !rel.app_release) return;
        var seen = load();
        if (!seen) {
          save({
            app_release: rel.app_release,
            curriculum_version: rel.curriculum_version,
            built_at: rel.built_at,
            at: Date.now()
          });
          return;
        }
        var changed =
          seen.app_release !== rel.app_release ||
          seen.curriculum_version !== rel.curriculum_version;
        if (changed) showBanner(rel);
        else {
          save({
            app_release: rel.app_release,
            curriculum_version: rel.curriculum_version,
            built_at: rel.built_at,
            at: Date.now()
          });
        }
      })
      .catch(function () { /* offline / blocked: do not interrupt learning */ });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', check);
  } else {
    check();
  }
})();
