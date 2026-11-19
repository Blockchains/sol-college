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

    var pathProgress = document.getElementById('path-progress');
    var pathProgressData = document.getElementById('path-progress-data');
    var pathProgressBody = document.getElementById('path-progress-body');
    if (pathProgress && pathProgressData && pathProgressBody) {
      try {
        var catalog = JSON.parse(pathProgressData.textContent || '{}');
        var loops = load('sc-lesson-loop') || {};
        var sectionProgress = load(PROGRESS) || {};
        function isTouched(id) {
          var loop = loops[id];
          var sec = sectionProgress[id];
          var marked = 0;
          if (loop && loop.marked && typeof loop.marked === 'object') {
            Object.keys(loop.marked).forEach(function (k) { if (loop.marked[k]) marked++; });
          }
          var loopTouched = loop && (
            (loop.visited && loop.visited.length) ||
            marked ||
            loop.predictLocked ||
            loop.predict
          );
          var secTouched = sec && sec.done && sec.done.length;
          return !!(loopTouched || secTouched);
        }
        function countTouched(items) {
          var touched = 0;
          (items || []).forEach(function (item) {
            if (isTouched(item.id)) touched++;
          });
          return touched;
        }
        var fItems = catalog.foundations || [];
        var cItems = catalog.core || [];
        var fN = countTouched(fItems);
        var cN = countTouched(cItems);
        pathProgress.hidden = false;
        var html = '';
        html += '<p><b>Foundations:</b> ' + fN + ' of ' + fItems.length + ' lessons touched on this device</p>';
        html += '<p><b>Core staged path:</b> ' + cN + ' of ' + cItems.length + ' lessons touched on this device</p>';
        function firstUntouched(items) {
          for (var i = 0; i < items.length; i++) {
            if (!isTouched(items[i].id)) return items[i];
          }
          return null;
        }
        var nextItem = firstUntouched(fItems) || firstUntouched(cItems);
        if (nextItem) {
          var label = (fN + cN) ? 'Continue with ' : 'Start with ';
          html += '<p class="cta-row"><a class="btn" href="' + esc(nextItem.href) + '">' + label + esc(nextItem.title) + '</a></p>';
        } else if (fN + cN > 0) {
          html += '<p class="note">Every listed foundations and core path lesson has local activity on this device. Rubrics still decide mastery.</p>';
        }
        pathProgressBody.innerHTML = html;
      } catch (err) {
        pathProgress.hidden = true;
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

    /* Learning-layer vertical slice: preflight, workspace loop, stuck help */
    var LOOP = 'sc-lesson-loop';
    var workspace = document.getElementById('workspace');
    if (workspace && slug) {
      var loops = load(LOOP) || {};
      var pageVersion = workspace.getAttribute('data-content-version') || '';
      var state = loops[slug] || {
        version: 1,
        content_version: pageVersion,
        mode: '',
        step: 'prepare',
        predict: '',
        predictLocked: false,
        inspect: {},
        route: '',
        explain: '',
        outcome: '',
        observedAt: '',
        attempt: null,
        marked: {},
        visited: ['prepare']
      };

      var ATTEMPT_GUIDE = {
        wallet_rejected: 'No chain effect from this attempt. Review the wallet request, then you may try again with a corrected request. Do not reuse a partially built transaction blindly.',
        submitted_unknown: 'Preserve the signature if you have one. Check Explorer before sending again — missing UI status is not proof of failure. Do not replace the transaction until you reconcile.',
        pending: 'Wait and reconcile on Explorer. Do not automatically resubmit. A second send can create a duplicate if the first still lands.',
        failed: 'Read the program logs for the failed signature. Fix the cause, then send a new approved transaction. Do not claim a simulated fee was paid.',
        confirmed: 'Record the signature as your attempt evidence. Refresh account state before the next action — do not overwrite observation with the draft you intended.'
      };

      function routeTag(route) {
        return ({
          observe: 'Captured / observation',
          live: 'My attempt (live)',
          local: 'Local test',
          guided: 'Guided investigation'
        })[route] || 'Unspecified';
      }

      function persist() {
        state.href = location.pathname;
        state.at = Date.now();
        if (pageVersion) state.content_version = pageVersion;
        loops[slug] = state;
        save(LOOP, loops);
        var saveEl = document.getElementById('lab-save');
        if (saveEl) {
          saveEl.textContent = 'Saved on this device · step: ' + state.step +
            (state.outcome ? ' · outcome: ' + state.outcome : '');
        }
        var mode = document.getElementById('ev-mode');
        var pred = document.getElementById('ev-predict');
        var route = document.getElementById('ev-route');
        var out = document.getElementById('ev-outcome');
        var sig = document.getElementById('ev-sig');
        var observed = document.getElementById('ev-observed');
        var tag = document.getElementById('ev-route-tag');
        var att = document.getElementById('ev-attempt-status');
        if (mode) mode.textContent = state.mode || 'Not chosen';
        if (pred) pred.textContent = state.predict || '—';
        if (route) route.textContent = state.route || '—';
        if (out) out.textContent = state.outcome || '—';
        if (sig) {
          var fromAttempt = state.attempt && state.attempt.sig;
          sig.textContent = fromAttempt || (state.inspect && state.inspect.sig) || '—';
        }
        if (observed) observed.textContent = state.observedAt || '—';
        if (tag) tag.textContent = routeTag(state.route);
        if (att) {
          att.textContent = (state.attempt && state.attempt.status) || '—';
        }
      }

      function paintAttempt() {
        var a = state.attempt || {};
        var op = document.getElementById('attempt-op');
        var net = document.getElementById('attempt-network');
        var st = document.getElementById('attempt-status');
        var sig = document.getElementById('attempt-pending-sig');
        var guide = document.getElementById('attempt-guidance');
        var expl = document.getElementById('attempt-explorer');
        var saveSt = document.getElementById('attempt-save-status');
        if (op) op.value = a.op || '';
        if (net) net.value = a.network || 'devnet';
        if (st) st.value = a.status || '';
        if (sig) sig.value = a.sig || '';
        if (guide) {
          var text = ATTEMPT_GUIDE[a.status] || '';
          guide.hidden = !text;
          guide.textContent = text;
        }
        if (expl) {
          if (a.sig) {
            expl.href = 'https://explorer.solana.com/tx/' + encodeURIComponent(a.sig) + '?cluster=devnet';
            expl.textContent = 'Open this signature on Explorer';
          } else {
            expl.href = 'https://explorer.solana.com/?cluster=devnet';
            expl.textContent = 'Open Explorer (devnet)';
          }
        }
        if (saveSt && a.at) {
          saveSt.textContent = 'Attempt saved · ' + (a.status || 'status unset') + ' · ' + a.at;
        }
      }

      function showPredictLockedUi() {
        var fb = document.getElementById('predict-feedback');
        var why = document.getElementById('predict-why');
        var cont = document.getElementById('predict-continue');
        var answer = workspace.getAttribute('data-predict-answer') || '';
        if (fb) {
          fb.hidden = false;
          fb.textContent = state.predict === answer
            ? 'Your prediction matches the intended outcome. Continue to Act.'
            : 'Interesting choice. Compare it with the intended path, then continue — a wrong prediction is still useful learning.';
        }
        if (why) why.hidden = false;
        if (cont) cont.hidden = false;
      }

      function showStep(name) {
        state.step = name;
        if (state.visited.indexOf(name) < 0) state.visited.push(name);
        workspace.querySelectorAll('.loop-panel').forEach(function (p) {
          p.hidden = p.getAttribute('data-panel') !== name;
        });
        workspace.querySelectorAll('[data-loop-step]').forEach(function (b) {
          var stepName = b.getAttribute('data-loop-step');
          b.classList.toggle('is-current', stepName === name);
          if (state.visited.indexOf(stepName) >= 0) b.classList.add('is-visited');
        });
        persist();
      }

      workspace.querySelectorAll('[data-loop-step]').forEach(function (b) {
        b.addEventListener('click', function () {
          showStep(b.getAttribute('data-loop-step'));
        });
      });
      workspace.querySelectorAll('[data-loop-next]').forEach(function (b) {
        b.addEventListener('click', function () {
          showStep(b.getAttribute('data-loop-next'));
        });
      });

      var preflight = document.getElementById('preflight');
      if (preflight) {
        preflight.querySelectorAll('[data-mode]').forEach(function (btn) {
          btn.addEventListener('click', function () {
            var mode = btn.getAttribute('data-mode');
            state.mode = mode;
            var prac = document.getElementById('preflight-practical');
            if (prac) prac.hidden = mode !== 'practical';
            var st = document.getElementById('preflight-status');
            if (st) {
              st.textContent = mode === 'practical'
                ? 'Practical mode: complete wallet setup below, then continue in the workspace. Progress is saved before you leave for the faucet or app.'
                : 'Observation mode: read accounts and platform proof without sending a transaction. This is not equivalent to practical completion.';
            }
            persist();
          });
        });
      }

      var checkPredict = workspace.querySelector('[data-loop-check-predict]');
      if (checkPredict) {
        checkPredict.addEventListener('click', function () {
          var picked = workspace.querySelector('input[name="loop-predict"]:checked');
          var fb = document.getElementById('predict-feedback');
          var why = document.getElementById('predict-why');
          var cont = document.getElementById('predict-continue');
          if (!picked) {
            if (fb) { fb.hidden = false; fb.textContent = 'Choose a prediction first.'; }
            return;
          }
          state.predict = picked.value;
          state.predictLocked = true;
          var answer = workspace.getAttribute('data-predict-answer') || '';
          if (fb) {
            fb.hidden = false;
            fb.textContent = picked.value === answer
              ? 'Your prediction matches the intended outcome. Continue to Act.'
              : 'Interesting choice. Compare it with the intended path, then continue — a wrong prediction is still useful learning.';
          }
          if (why) why.hidden = false;
          if (cont) cont.hidden = false;
          persist();
        });
      }

      workspace.querySelectorAll('[data-loop-mark]').forEach(function (btn) {
        btn.addEventListener('click', function () {
          var which = btn.getAttribute('data-loop-mark');
          state.marked[which] = true;
          if (which === 'inspect') {
            var insp = {};
            workspace.querySelectorAll('[data-inspect]').forEach(function (inp) {
              insp[inp.getAttribute('data-inspect')] = inp.value;
            });
            state.inspect = insp;
            var er = document.getElementById('evidence-route');
            if (er) state.route = er.value;
            state.observedAt = new Date().toISOString();
            var stale = document.getElementById('inspect-stale');
            if (stale) stale.hidden = true;
          }
          if (which === 'explain') {
            var ta = document.getElementById('loop-explain');
            if (ta) state.explain = ta.value;
          }
          if (which === 'transfer') {
            var oc = document.getElementById('loop-outcome');
            if (oc) state.outcome = oc.value;
          }
          persist();
          btn.textContent = 'Saved';
          setTimeout(function () { btn.textContent = btn.getAttribute('data-label') || 'Saved'; }, 1200);
        });
      });

      // restore
      if (pageVersion && state.content_version && state.content_version !== pageVersion) {
        var banner = document.getElementById('lab-version-banner');
        if (banner) {
          banner.hidden = false;
          banner.innerHTML = '<p style="margin:0 0 8px">This lesson content changed since your last visit (saved <code>' +
            esc(state.content_version) + '</code>, now <code>' + esc(pageVersion) +
            '</code>). Historical evidence is kept; re-check predictions and observations before treating them as current.</p>' +
            '<button type="button" class="btn ghost" id="lab-version-keep">Keep saved progress</button> ' +
            '<button type="button" class="btn" id="lab-version-reset">Reset loop answers</button>';
          var keep = document.getElementById('lab-version-keep');
          var reset = document.getElementById('lab-version-reset');
          if (keep) keep.addEventListener('click', function () {
            state.content_version = pageVersion;
            persist();
            banner.hidden = true;
          });
          if (reset) reset.addEventListener('click', function () {
            state.predict = '';
            state.predictLocked = false;
            state.inspect = {};
            state.route = '';
            state.explain = '';
            state.outcome = '';
            state.observedAt = '';
            state.attempt = null;
            state.marked = {};
            state.content_version = pageVersion;
            state.step = 'prepare';
            persist();
            location.reload();
          });
        }
      } else if (pageVersion && !state.content_version) {
        state.content_version = pageVersion;
      }

      var attemptSave = document.getElementById('attempt-save');
      if (attemptSave) {
        attemptSave.addEventListener('click', function () {
          state.attempt = {
            op: (document.getElementById('attempt-op') || {}).value || '',
            network: (document.getElementById('attempt-network') || {}).value || 'devnet',
            status: (document.getElementById('attempt-status') || {}).value || '',
            sig: (document.getElementById('attempt-pending-sig') || {}).value || '',
            at: new Date().toISOString()
          };
          if (state.attempt.sig && state.inspect) {
            state.inspect.sig = state.attempt.sig;
          } else if (state.attempt.sig) {
            state.inspect = Object.assign({}, state.inspect || {}, { sig: state.attempt.sig });
          }
          persist();
          paintAttempt();
        });
        ['attempt-status', 'attempt-pending-sig'].forEach(function (id) {
          var el = document.getElementById(id);
          if (el) el.addEventListener('change', function () {
            // Live guidance while editing; persist on Save.
            var status = (document.getElementById('attempt-status') || {}).value || '';
            var guide = document.getElementById('attempt-guidance');
            if (guide) {
              var text = ATTEMPT_GUIDE[status] || '';
              guide.hidden = !text;
              guide.textContent = text;
            }
            var sig = (document.getElementById('attempt-pending-sig') || {}).value || '';
            var expl = document.getElementById('attempt-explorer');
            if (expl && sig) {
              expl.href = 'https://explorer.solana.com/tx/' + encodeURIComponent(sig) + '?cluster=devnet';
              expl.textContent = 'Open this signature on Explorer';
            }
          });
        });
      }
      paintAttempt();
      if (state.mode) {
        var st0 = document.getElementById('preflight-status');
        if (st0) st0.textContent = 'Restored mode: ' + state.mode;
        var prac0 = document.getElementById('preflight-practical');
        if (prac0) prac0.hidden = state.mode !== 'practical';
      }
      if (state.predict) {
        var radio = workspace.querySelector('input[name="loop-predict"][value="' + state.predict + '"]');
        if (radio) radio.checked = true;
      }
      if (state.predictLocked) showPredictLockedUi();
      Object.keys(state.inspect || {}).forEach(function (k) {
        var inp = workspace.querySelector('[data-inspect="' + k + '"]');
        if (inp) inp.value = state.inspect[k];
      });
      var er0 = document.getElementById('evidence-route');
      if (er0 && state.route) er0.value = state.route;
      var ta0 = document.getElementById('loop-explain');
      if (ta0 && state.explain) ta0.value = state.explain;
      var oc0 = document.getElementById('loop-outcome');
      if (oc0 && state.outcome) oc0.value = state.outcome;
      if (state.observedAt) {
        var staleNote = document.getElementById('inspect-stale');
        if (staleNote) staleNote.hidden = false;
      }
      workspace.querySelectorAll('[data-loop-step]').forEach(function (b) {
        var name = b.getAttribute('data-loop-step');
        if (state.visited && state.visited.indexOf(name) >= 0) b.classList.add('is-visited');
        if (state.marked && state.marked[name]) b.classList.add('is-marked');
      });
      showStep(state.step || 'prepare');
    }

    var stuck = document.getElementById('stuck');
    if (stuck) {
      var help = {
        concept: 'Restate the goal in one sentence, then open the Technical explanation layer for the key distinction. Hint ladder: (1) goal, (2) evidence drawer, (3) predict-why note, (4) worked Proof example.',
        wallet: 'Confirm Devnet, a practice wallet, and that “not connected” is not “unsupported.” Use observation mode if the faucet or wallet fails — do not buy tokens to bypass it. Your workspace progress is already saved on this device.',
        tx: 'Open Attempt recovery below. Preserve the original signature. Separate wallet rejection from submission, and execution from commitment. Do not send a second transaction until you know whether the first confirmed, failed, or is still pending.',
        ui: 'The hosted UI may differ from screenshots. Prefer account observation over appearance. Report a product defect if the documented control is missing — then use platform Proof as an alternative evidence route.',
        diff: 'Shared mutable state can change. A historical November colour may differ from today’s account. That is a teaching moment, not an automatic fail. Record both values and the time you observed them.',
        a11y: 'Use observation mode and keyboard-accessible Explorer links. Ask for an equivalent task if a control is inaccessible. Escalation: open a GitHub issue labelled accessibility.'
      };
      var panel = document.getElementById('stuck-panel');
      stuck.querySelectorAll('[data-stuck]').forEach(function (btn) {
        btn.addEventListener('click', function () {
          var key = btn.getAttribute('data-stuck');
          if (!panel) return;
          panel.hidden = false;
          panel.innerHTML = '<p><b>' + esc(btn.textContent) + '</b></p><p>' + esc(help[key] || '') + '</p><p class="note">Do not respond to every category with “try again.”</p>';
          if (key === 'tx') {
            var rec = document.getElementById('attempt-recovery');
            if (rec) rec.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
          }
        });
      });
    }
  });
})();
