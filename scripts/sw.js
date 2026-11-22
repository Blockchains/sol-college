/* Sol.College service worker: silent updates, network-first HTML and landing assets.
   __SC_RELEASE__ is replaced at build time so each deploy registers as a new worker. */
var RELEASE = '__SC_RELEASE__';

self.addEventListener('install', function () {
  self.skipWaiting();
});

self.addEventListener('activate', function (event) {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('message', function (event) {
  if (event.data && event.data.type === 'SKIP_WAITING') self.skipWaiting();
});

self.addEventListener('fetch', function (event) {
  var req = event.request;
  if (req.method !== 'GET') return;
  var url;
  try { url = new URL(req.url); } catch (e) { return; }
  if (url.origin !== self.location.origin) return;
  var path = url.pathname;
  var dest = req.destination;
  var isDoc = dest === 'document' || path === '/' || /\/$/.test(path) || /\.html$/.test(path);
  var isShell = dest === 'style' || dest === 'script' ||
    path === '/release.json' || path === '/sw.js' ||
    path.indexOf('/assets/landing') === 0;
  if (!isDoc && !isShell) return;
  event.respondWith(
    fetch(req, { cache: 'no-store' }).catch(function () { return fetch(req); })
  );
});
