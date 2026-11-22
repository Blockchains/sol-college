/* Silent site updates. Compares /release.json to a local snapshot and reloads
   once when the app or curriculum changes. Registers a network-first service
   worker (skipWaiting + clients.claim) so returning visitors get the new
   HTML without an update banner. */
(function () {
  var KEY = 'sc-release-seen';
  var RELOAD_LOCK = 'sc-release-reloading';

  function load() {
    try { return JSON.parse(localStorage.getItem(KEY) || 'null'); }
    catch (e) { return null; }
  }
  function save(v) {
    try { localStorage.setItem(KEY, JSON.stringify(v)); }
    catch (e) {}
  }
  function snapshot(rel) {
    return {
      app_release: rel.app_release,
      curriculum_version: rel.curriculum_version,
      built_at: rel.built_at,
      at: Date.now()
    };
  }

  function registerWorker() {
    if (!('serviceWorker' in navigator)) return;
    var alreadyControlled = !!navigator.serviceWorker.controller;
    navigator.serviceWorker.register('/sw.js').catch(function () { /* optional */ });
    if (alreadyControlled) {
      var refreshing = false;
      navigator.serviceWorker.addEventListener('controllerchange', function () {
        if (refreshing) return;
        refreshing = true;
        location.reload();
      });
    }
    if (navigator.serviceWorker.getRegistration) {
      navigator.serviceWorker.getRegistration().then(function (reg) {
        if (!reg) return;
        if (reg.waiting) {
          try { reg.waiting.postMessage({ type: 'SKIP_WAITING' }); } catch (e) {}
        }
        if (reg.update) reg.update();
      });
    }
  }

  function check() {
    if (typeof fetch !== 'function') return;
    fetch('/release.json', { cache: 'no-store' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (rel) {
        if (!rel || !rel.app_release) return;
        var seen = load();
        if (!seen) {
          save(snapshot(rel));
          return;
        }
        var changed =
          seen.app_release !== rel.app_release ||
          seen.curriculum_version !== rel.curriculum_version;
        if (!changed) {
          save(snapshot(rel));
          return;
        }
        var lock = String(rel.app_release) + ':' + String(rel.curriculum_version || '');
        try {
          if (sessionStorage.getItem(RELOAD_LOCK) === lock) {
            save(snapshot(rel));
            return;
          }
          sessionStorage.setItem(RELOAD_LOCK, lock);
        } catch (e) {}
        save(snapshot(rel));
        location.reload();
      })
      .catch(function () { /* offline / blocked: do not interrupt learning */ });
  }

  registerWorker();
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', check);
  } else {
    check();
  }
})();
