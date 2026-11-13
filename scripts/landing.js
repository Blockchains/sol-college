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
})();
