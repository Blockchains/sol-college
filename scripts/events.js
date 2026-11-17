(function () {
  var ZONE_KEY = 'sol-college-tz';
  var SAVE_KEY = 'sol-college-saved-events';

  function zone() {
    var saved = '';
    try { saved = localStorage.getItem(ZONE_KEY) || ''; } catch (e) { saved = ''; }
    if (saved) return saved;
    try { return Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC'; }
    catch (e) { return 'UTC'; }
  }

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c];
    });
  }

  function savedIds() {
    try { return JSON.parse(localStorage.getItem(SAVE_KEY) || '[]'); }
    catch (e) { return []; }
  }

  function setSaved(ids) {
    try { localStorage.setItem(SAVE_KEY, JSON.stringify(ids)); } catch (e) {}
  }

  function fmt(date, tz) {
    return new Intl.DateTimeFormat('en-GB', {
      timeZone: tz, weekday: 'short', day: 'numeric', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit', hourCycle: 'h23'
    }).format(date);
  }

  function clock(date, tz) {
    return new Intl.DateTimeFormat('en-GB', {
      timeZone: tz, hour: '2-digit', minute: '2-digit', hourCycle: 'h23'
    }).format(date);
  }

  function dayKey(date, tz) {
    return new Intl.DateTimeFormat('en-CA', {
      timeZone: tz, year: 'numeric', month: '2-digit', day: '2-digit'
    }).format(date);
  }

  function yourTime(start, end, eventTz, viewer) {
    if (!start) return '';
    var s = new Date(start);
    var e = end ? new Date(end) : null;
    if (viewer === eventTz) return 'Your time matches the event time.';
    var text = fmt(s, viewer);
    if (e) text += dayKey(s, viewer) === dayKey(e, viewer) ? '–' + clock(e, viewer) : ' – ' + fmt(e, viewer);
    return text + ' (' + viewer + ')';
  }

  function applyTimes() {
    var viewer = zone();
    var label = document.getElementById('ev-zone-now');
    if (label) label.textContent = viewer;
    document.querySelectorAll('.ev-your').forEach(function (node) {
      var wrap = node.closest('.ev-when');
      if (!wrap) return;
      node.textContent = yourTime(wrap.getAttribute('data-start'), wrap.getAttribute('data-end'), wrap.getAttribute('data-tz') || '', viewer);
    });
  }

  function applySaved() {
    var ids = savedIds();
    document.querySelectorAll('[data-save]').forEach(function (btn) {
      var on = ids.indexOf(btn.getAttribute('data-save')) !== -1;
      btn.setAttribute('aria-pressed', on ? 'true' : 'false');
      btn.textContent = on ? 'Saved on this browser' : 'Save';
    });
  }

  document.querySelectorAll('[data-save]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var id = btn.getAttribute('data-save');
      var ids = savedIds().filter(function (x) { return x !== id; });
      if (btn.getAttribute('aria-pressed') !== 'true') ids.push(id);
      setSaved(ids);
      applySaved();
      render();
    });
  });

  var zoneSelect = document.getElementById('ev-zone');
  if (zoneSelect) {
    var current = zone();
    if (![].some.call(zoneSelect.options, function (o) { return o.value === current; })) {
      var opt = document.createElement('option');
      opt.value = current;
      opt.textContent = current;
      zoneSelect.prepend(opt);
    }
    zoneSelect.value = current;
    zoneSelect.addEventListener('change', function () {
      try { localStorage.setItem(ZONE_KEY, zoneSelect.value); } catch (e) {}
      applyTimes();
    });
  }

  var app = document.getElementById('ev-app');
  if (!app) {
    applyTimes();
    applySaved();
    return;
  }

  var list = document.getElementById('ev-list');
  var soon = document.getElementById('ev-soon');
  var soonH = document.getElementById('ev-soon-h');
  var laterH = document.getElementById('ev-later-h');
  var empty = document.getElementById('ev-empty');
  var count = document.getElementById('ev-count');
  var cards = [].slice.call(list.querySelectorAll('.ev-card'));
  var q = document.getElementById('ev-q');
  var filters = {
    format: document.getElementById('f-format'),
    intent: document.getElementById('f-intent'),
    country: document.getElementById('f-country'),
    price: document.getElementById('f-price'),
    level: document.getElementById('f-level'),
    lang: document.getElementById('f-lang'),
    when: document.getElementById('f-when')
  };

  function weekEnd() {
    return Date.now() + 7 * 24 * 60 * 60 * 1000;
  }

  function matches(card) {
    var text = (q && q.value || '').trim().toLowerCase();
    if (text && (card.getAttribute('data-text') || '').indexOf(text) === -1) return false;
    if (filters.format.value && card.getAttribute('data-format') !== filters.format.value) return false;
    if (filters.intent.value && card.getAttribute('data-intent') !== filters.intent.value) return false;
    if (filters.country.value && card.getAttribute('data-country') !== filters.country.value) return false;
    if (filters.price.value && card.getAttribute('data-price') !== filters.price.value) return false;
    if (filters.level.value && card.getAttribute('data-level') !== filters.level.value) return false;
    if (filters.lang.value && card.getAttribute('data-lang') !== filters.lang.value) return false;
    var start = Date.parse(card.getAttribute('data-start') || '');
    if (filters.when.value === 'week' && !(start >= Date.now() - 12 * 60 * 60 * 1000 && start <= weekEnd())) return false;
    if (filters.when.value === 'later' && !(start > weekEnd())) return false;
    if (filters.when.value === 'saved' && savedIds().indexOf(card.getAttribute('data-id')) === -1) return false;
    return true;
  }

  function render() {
    var shown = [];
    cards.forEach(function (card) {
      var ok = matches(card);
      card.hidden = !ok;
      if (ok) shown.push(card);
    });
    var now = Date.now();
    var limit = weekEnd();
    var soonCount = 0;
    shown.forEach(function (card) {
      var start = Date.parse(card.getAttribute('data-start') || '');
      var isSoon = start <= limit;
      if (isSoon) {
        soon.appendChild(card);
        soonCount += 1;
      } else {
        list.appendChild(card);
      }
    });
    cards.forEach(function (card) {
      if (card.hidden && card.parentNode !== list) list.appendChild(card);
    });
    soonH.hidden = soonCount === 0;
    laterH.hidden = shown.length === soonCount;
    empty.hidden = shown.length !== 0;
    if (filters.level.value === 'beginner' && shown.length === 0) {
      empty.textContent = 'No listing states that it is for beginners.';
    } else if (shown.length === 0) {
      empty.textContent = 'Nothing in the published list matches. The queue holds listings whose date is not confirmed.';
    }
    count.textContent = shown.length + (shown.length === 1 ? ' event' : ' events');
    drawMonth();
  }

  document.getElementById('ev-chips').addEventListener('click', function (event) {
    var btn = event.target.closest('button');
    if (!btn) return;
    var key = btn.getAttribute('data-chip');
    if (key === 'near') { near(); return; }
    var map = { online: ['format', 'online'], week: ['when', 'week'], free: ['price', 'free'], beginner: ['level', 'beginner'] };
    var pair = map[key];
    if (!pair) return;
    var el = filters[pair[0]];
    var on = btn.getAttribute('aria-pressed') === 'true';
    el.value = on ? '' : pair[1];
    document.querySelectorAll('#ev-chips button').forEach(function (b) { b.setAttribute('aria-pressed', 'false'); });
    btn.setAttribute('aria-pressed', on ? 'false' : 'true');
    render();
  });

  Object.keys(filters).forEach(function (key) {
    filters[key].addEventListener('change', function () {
      document.querySelectorAll('#ev-chips button').forEach(function (b) { b.setAttribute('aria-pressed', 'false'); });
      render();
    });
  });
  q.addEventListener('input', render);

  function near() {
    var note = document.getElementById('ev-near-note');
    if (!navigator.geolocation) {
      note.textContent = 'This browser has no location service. The list stays in time order.';
      return;
    }
    note.textContent = 'Asking for a location. Only venues the source published can be measured.';
    navigator.geolocation.getCurrentPosition(function (pos) {
      var lat = pos.coords.latitude, lng = pos.coords.longitude;
      cards.forEach(function (card) {
        var clat = parseFloat(card.getAttribute('data-lat'));
        var clng = parseFloat(card.getAttribute('data-lng'));
        var slot = card.querySelector('.ev-distance');
        if (!slot) return;
        if (Number.isNaN(clat) || Number.isNaN(clng)) {
          card.dataset.km = '99999';
          slot.textContent = 'Distance not available. The source did not publish a venue coordinate.';
        } else {
          var km = haversine(lat, lng, clat, clng);
          card.dataset.km = String(km);
          slot.textContent = km.toFixed(km < 10 ? 1 : 0) + ' km from you to the public venue, not a city centre.';
        }
      });
      cards.sort(function (a, b) { return parseFloat(a.dataset.km) - parseFloat(b.dataset.km); });
      cards.forEach(function (card) { list.appendChild(card); });
      note.textContent = 'Sorted by distance to a public venue. Events without one stay at the end.';
      render();
    }, function () {
      note.textContent = 'Location was not shared. The list stays in time order.';
    }, { maximumAge: 600000, timeout: 8000 });
  }

  function haversine(a, b, c, d) {
    var r = 6371, p = Math.PI / 180;
    var h = Math.sin((c - a) * p / 2) ** 2 + Math.cos(a * p) * Math.cos(c * p) * Math.sin((d - b) * p / 2) ** 2;
    return 2 * r * Math.asin(Math.min(1, Math.sqrt(h)));
  }

  var monthCursor = new Date();
  monthCursor.setDate(1);
  var monthLabel = document.getElementById('ev-month-label');
  var monthBody = document.getElementById('ev-month');

  function drawMonth() {
    if (!monthBody) return;
    var year = monthCursor.getFullYear(), month = monthCursor.getMonth();
    monthLabel.textContent = monthCursor.toLocaleString('en-GB', { month: 'long', year: 'numeric' });
    var first = new Date(year, month, 1);
    var startPad = (first.getDay() + 6) % 7;
    var days = new Date(year, month + 1, 0).getDate();
    var cells = [];
    for (var i = 0; i < startPad; i += 1) cells.push('<td class="muted"></td>');
    for (var day = 1; day <= days; day += 1) {
      var key = year + '-' + String(month + 1).padStart(2, '0') + '-' + String(day).padStart(2, '0');
      var links = cards.filter(function (card) {
        return !card.hidden && (card.getAttribute('data-days') || '').split(' ').indexOf(key) !== -1;
      }).map(function (card) {
        var a = card.querySelector('h3 a');
        return '<a href="' + esc(a.getAttribute('href')) + '">' + esc(a.textContent) + '</a>';
      }).join('');
      cells.push('<td><span>' + day + '</span>' + links + '</td>');
    }
    while (cells.length % 7) cells.push('<td class="muted"></td>');
    var html = '';
    for (var c = 0; c < cells.length; c += 7) html += '<tr>' + cells.slice(c, c + 7).join('') + '</tr>';
    monthBody.innerHTML = html;
  }

  document.getElementById('ev-prev').addEventListener('click', function () {
    monthCursor.setMonth(monthCursor.getMonth() - 1); drawMonth();
  });
  document.getElementById('ev-next').addEventListener('click', function () {
    monthCursor.setMonth(monthCursor.getMonth() + 1); drawMonth();
  });

  document.getElementById('ev-views').addEventListener('click', function (event) {
    var btn = event.target.closest('button');
    if (!btn) return;
    var id = btn.getAttribute('data-view');
    document.querySelectorAll('#ev-views button').forEach(function (b) {
      var on = b === btn;
      b.setAttribute('aria-selected', on ? 'true' : 'false');
    });
    document.querySelectorAll('.ev-panel').forEach(function (panel) {
      panel.hidden = panel.id !== 'panel-' + id;
    });
  });

  var params = new URLSearchParams(location.search);
  if (params.get('intent')) filters.intent.value = params.get('intent');
  if (params.get('format')) filters.format.value = params.get('format');
  if (params.get('country')) filters.country.value = params.get('country');
  if (params.get('q')) q.value = params.get('q');

  applyTimes();
  applySaved();
  render();
})();
