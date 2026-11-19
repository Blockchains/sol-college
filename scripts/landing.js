/* Sol.College landing interactions. Respects prefers-reduced-motion. */
(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Mobile nav */
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.textContent = open ? 'Close' : 'Menu';
    });
    nav.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        if (window.matchMedia('(max-width: 760px)').matches) {
          nav.classList.remove('is-open');
          toggle.setAttribute('aria-expanded', 'false');
          toggle.textContent = 'Menu';
        }
      });
    });
  }

  /* Audience tabs: I want to learn / I build a dApp */
  var tabs = Array.prototype.slice.call(document.querySelectorAll('.audience [role="tab"]'));
  var learn = document.getElementById('hero-learn');
  var teams = document.getElementById('hero-teams');

  function selectAudience(which, pushHash) {
    var isTeams = which === 'teams';
    tabs.forEach(function (t) {
      var on = t.getAttribute('aria-controls') === (isTeams ? 'hero-teams' : 'hero-learn');
      t.setAttribute('aria-selected', on ? 'true' : 'false');
      t.tabIndex = on ? 0 : -1;
    });
    if (learn) learn.hidden = isTeams;
    if (teams) teams.hidden = !isTeams;
    document.documentElement.setAttribute('data-audience', isTeams ? 'teams' : 'learn');
    if (pushHash) {
      var hash = isTeams ? '#build' : '#learn';
      if (history.replaceState) history.replaceState(null, '', hash);
    }
  }

  tabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      selectAudience(tab.getAttribute('aria-controls') === 'hero-teams' ? 'teams' : 'learn', true);
    });
    tab.addEventListener('keydown', function (e) {
      if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
      e.preventDefault();
      var i = tabs.indexOf(tab);
      var next = tabs[(i + (e.key === 'ArrowRight' ? 1 : tabs.length - 1)) % tabs.length];
      next.focus();
      next.click();
    });
  });

  function fromLocation() {
    var h = (location.hash || '').toLowerCase();
    var q = new URLSearchParams(location.search).get('for') || '';
    if (h === '#build' || h === '#teams' || h === '#for-teams' || q === 'teams' || q === 'dapp') {
      selectAudience('teams', false);
      if (h === '#for-teams') {
        var el = document.getElementById('for-teams');
        if (el && !reduce) el.scrollIntoView({ block: 'start' });
      }
    } else {
      selectAudience('learn', false);
    }
  }
  fromLocation();
  window.addEventListener('hashchange', fromLocation);

  /* Nav "For teams" should reveal the teams hero as well when staying near the top */
  document.querySelectorAll('a[href="#for-teams"]').forEach(function (a) {
    a.addEventListener('click', function () {
      selectAudience('teams', false);
    });
  });
  document.querySelectorAll('a[href="#loop"], a[href="#build"]').forEach(function (a) {
    a.addEventListener('click', function () {
      if (a.getAttribute('href') === '#build') selectAudience('teams', true);
    });
  });

  /* Homepage resume from device-local last lesson (Release E.5) */
  function esc(s) {
    return String(s || '').replace(/[&<>"']/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c];
    });
  }
  var startResume = document.getElementById('start-resume');
  if (startResume) {
    try {
      var lastLesson = JSON.parse(localStorage.getItem('sc-lesson-last') || 'null');
      if (lastLesson && lastLesson.href) {
        var body = document.getElementById('start-resume-body');
        var goResume = document.getElementById('start-resume-go');
        if (body) {
          body.innerHTML = 'Pick up where you left off: <a href="' + esc(lastLesson.href) + '"><strong>' +
            esc(lastLesson.title || 'your last lesson') + '</strong></a>';
        }
        if (goResume) {
          goResume.href = lastLesson.href;
          goResume.textContent = 'Continue';
        }
        startResume.hidden = false;
      }
    } catch (err) {}
  }

  /* Front-door recommender (#start) */
  var form = document.getElementById('start-form');
  var result = document.getElementById('start-result');
  if (form && result) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var d = new FormData(form);
      var q1 = d.get('q1');
      var q2 = d.get('q2');
      var q3 = d.get('q3');
      var q4 = d.get('q4');
      var href = '/lessons/first-transaction/';
      var title = 'Foundations 1 — Your First Transaction';
      var why = 'You want a guided introduction and have not yet inspected a transaction result.';
      if (q4 === 'challenge') {
        href = '/lessons/#challenges';
        title = 'Debug laboratory';
        why = 'You asked for an independent challenge. Start from the debug catalogue — not a patch requirement.';
      } else if (q1 === 'yes' && q2 === 'yes' && q3 === 'yes') {
        href = '/lessons/picassol-hackathon/';
        title = 'Picassol application lab';
        why = 'You already know transactions and accounts, and you want guided practice on a live app.';
      } else if (q1 === 'yes' && q2 === 'no') {
        href = '/lessons/accounts-ownership/';
        title = 'Foundations 2 — Accounts & authority';
        why = 'You have sent a transaction; next is ownership and authority before application labs.';
      }
      document.getElementById('start-result-title').textContent = title;
      document.getElementById('start-result-why').textContent = 'Why: ' + why;
      var go = document.getElementById('start-result-go');
      go.href = href;
      result.hidden = false;
      try {
        localStorage.setItem('sc-start-route', JSON.stringify({ href: href, title: title, at: Date.now() }));
      } catch (err) {}
      result.scrollIntoView({ block: 'nearest', behavior: reduce ? 'auto' : 'smooth' });
    });
    form.addEventListener('reset', function () {
      result.hidden = true;
    });
  }
})();
