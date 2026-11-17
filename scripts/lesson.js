(function () {
  var PROGRESS = 'sc-lesson-progress';
  var LAST = 'sc-lesson-last';
  function ready(fn) {
    if (document.readyState !== 'loading') fn();
    else document.addEventListener('DOMContentLoaded', fn);
  }
  function load(key) {
    try { return JSON.parse(localStorage.getItem(key) || 'null'); }
    catch (e) { return null; }
  }
  function save(key, value) {
    try { localStorage.setItem(key, JSON.stringify(value)); }
    catch (e) {}
  }
  function esc(s) {
    return String(s || '').replace(/[&<>"']/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c];
    });
  }
  ready(function () {
    var progress = load(PROGRESS) || {};
    var article = document.querySelector('article.lesson');
    var bar = document.querySelector('.readbar > span');
    if (bar && article) {
      var onscroll = function () {
        var top = article.getBoundingClientRect().top;
        var h = article.offsetHeight - window.innerHeight;
        var p = h > 0 ? Math.min(1, Math.max(0, -top / h)) : 0;
        bar.style.width = (p * 100) + '%';
      };
      document.addEventListener('scroll', onscroll, { passive: true });
      onscroll();
    }

    var railLinks = [].slice.call(document.querySelectorAll('.rail a'));
    if (railLinks.length && 'IntersectionObserver' in window) {
      var map = {};
      railLinks.forEach(function (a) {
        var id = (a.getAttribute('href') || '').slice(1);
        if (id) map[id] = a;
      });
      var obs = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (!en.isIntersecting) return;
          railLinks.forEach(function (a) { a.removeAttribute('aria-current'); });
          var hit = map[en.target.id];
          if (hit) hit.setAttribute('aria-current', 'true');
        });
      }, { rootMargin: '-20% 0px -65% 0px', threshold: 0.01 });
      Object.keys(map).forEach(function (id) {
        var el = document.getElementById(id);
        if (el) obs.observe(el);
      });
    }

    var slug = article && article.getAttribute('data-slug');
    if (slug && slug.indexOf('guide-') !== 0) {
      var h1 = document.querySelector('h1');
      save(LAST, { href: location.pathname, title: h1 ? h1.textContent : slug, at: Date.now(), slug: slug });
      var rec = progress[slug] || { done: [] };
      var boxes = [].slice.call(document.querySelectorAll('[data-step]'));
      function paint() {
        var n = 0;
        boxes.forEach(function (box) {
          var on = rec.done.indexOf(box.getAttribute('data-step')) >= 0;
          box.checked = on;
          var li = box.closest('.step');
          if (li) li.classList.toggle('done', on);
          if (on) n++;
        });
        var status = document.getElementById('step-status');
        if (status) status.textContent = boxes.length ? (n + ' of ' + boxes.length + ' steps checked on this device') : '';
      }
      boxes.forEach(function (box) {
        box.addEventListener('change', function () {
          var i = box.getAttribute('data-step');
          rec.done = rec.done.filter(function (x) { return x !== i; });
          if (box.checked) rec.done.push(i);
          rec.href = location.pathname;
          rec.title = h1 ? h1.textContent : slug;
          progress[slug] = rec;
          save(PROGRESS, progress);
          paint();
        });
      });
      paint();
    }

    document.addEventListener('click', function (ev) {
      var jump = ev.target.closest && ev.target.closest('[data-jump]');
      if (!jump) return;
      var heads = [].slice.call(document.querySelectorAll('.lesson-main h2'));
      var y = window.scrollY + 96;
      var nxt = null;
      for (var i = 0; i < heads.length; i++) {
        if (heads[i].getBoundingClientRect().top + window.scrollY > y + 8) { nxt = heads[i]; break; }
      }
      if (nxt) nxt.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    var flowDock = document.querySelector('article.lesson .dock');
    if (flowDock) {
      var pin = flowDock.cloneNode(true);
      pin.className = 'dock dock-pin';
      pin.setAttribute('aria-hidden', 'true');
      pin.hidden = true;
      document.body.appendChild(pin);
      var placePin = function () {
        var r = flowDock.getBoundingClientRect();
        pin.hidden = r.bottom > 8;
      };
      document.addEventListener('scroll', placePin, { passive: true });
      placePin();
    }

    document.querySelectorAll('pre.diagram, pre.sh').forEach(function (pre) {
      if (pre.querySelector('.copy')) return;
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'copy';
      b.textContent = 'Copy';
      b.addEventListener('click', function () {
        var clone = pre.cloneNode(true);
        var btn = clone.querySelector('.copy');
        if (btn) btn.remove();
        var text = (clone.querySelector('code') || clone).innerText;
        var done = function () { b.textContent = 'Copied'; setTimeout(function () { b.textContent = 'Copy'; }, 1200); };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(done, function () { b.textContent = 'Select the text'; });
        } else b.textContent = 'Select the text';
      });
      pre.appendChild(b);
    });

    var resume = document.getElementById('resume');
    if (resume) {
      var last = load(LAST);
      if (last && last.href && last.title && location.pathname !== last.href) {
        resume.hidden = false;
        resume.innerHTML = 'Pick up where you left off: <a href="' + esc(last.href) + '">' + esc(last.title) + '</a>';
      }
    }

    var q = document.getElementById('lesson-q');
    var cards = [].slice.call(document.querySelectorAll('[data-lesson]'));
    if (q && cards.length) {
      var buttons = [].slice.call(document.querySelectorAll('.finder-diff [data-diff]'));
      var formats = [].slice.call(document.querySelectorAll('.finder-format [data-format]'));
      var empty = document.getElementById('lesson-empty');
      var count = document.getElementById('lesson-count');
      function apply() {
        var s = (q.value || '').toLowerCase().trim();
        var pressed = document.querySelector('.finder-diff [data-diff][aria-pressed="true"]');
        var diff = pressed ? (pressed.getAttribute('data-diff') || '') : '';
        var fpressed = document.querySelector('.finder-format [data-format][aria-pressed="true"]');
        var format = fpressed ? (fpressed.getAttribute('data-format') || '') : '';
        var n = 0;
        cards.forEach(function (c) {
          var ok = (!s || (c.getAttribute('data-text') || '').indexOf(s) >= 0) && (!diff || c.getAttribute('data-diff') === diff) && (!format || c.getAttribute('data-format') === format);
          c.hidden = !ok;
          if (ok) n++;
        });
        document.querySelectorAll('section.path-stage').forEach(function (sec) {
          var own = sec.querySelectorAll('[data-lesson]');
          if (!own.length) return;
          var any = false;
          for (var i = 0; i < own.length; i++) if (!own[i].hidden) any = true;
          sec.hidden = !any;
        });
        if (count) count.textContent = n + (n === 1 ? ' lesson' : ' lessons');
        if (empty) empty.hidden = n !== 0;
        var filtering = !!(s || diff || format);
        document.querySelectorAll('.index-intro').forEach(function (el) { el.hidden = filtering; });
      }
      q.addEventListener('input', apply);
      function bind(group) {
        group.forEach(function (btn) {
          btn.addEventListener('click', function () {
            group.forEach(function (b) { b.setAttribute('aria-pressed', b === btn ? 'true' : 'false'); });
            apply();
          });
        });
      }
      bind(buttons);
      bind(formats);
      cards.forEach(function (card) {
        var rec = progress[card.getAttribute('data-slug')];
        if (rec && rec.done && rec.done.length) {
          var p = document.createElement('p');
          p.className = 'meta';
          p.textContent = rec.done.length + (rec.done.length === 1 ? ' step checked on this device' : ' steps checked on this device');
          card.insertBefore(p, card.firstChild);
        }
      });
      apply();
    }

    var gq = document.getElementById('gloss-q');
    if (gq) {
      gq.addEventListener('input', function () {
        var s = gq.value.toLowerCase().trim();
        document.querySelectorAll('dl.gloss dt').forEach(function (dt) {
          var dd = dt.nextElementSibling;
          var hay = (dt.getAttribute('data-term') || '') + ' ' + (dd ? dd.textContent.toLowerCase() : '');
          var ok = !s || hay.indexOf(s) >= 0;
          dt.hidden = !ok;
          if (dd && dd.tagName === 'DD') dd.hidden = !ok;
        });
      });
    }
  });
})();
