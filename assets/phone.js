/* ==========================================================================
   JCA Platform — phone prototype behavior
   Independent of app.js: a tab bar with a per-tab navigation stack instead
   of a flat sidebar router. Same defensive style (delegated document click
   listeners, closest(), early return) as the desktop app.js.
   Static walkthrough only — nothing here talks to a server.
   ========================================================================== */

(function () {
  'use strict';

  var TABS = ['home', 'calendar', 'give', 'community', 'me'];
  var titles = window.SCREEN_TITLES || {};

  // Each tab keeps its own stack of screen keys; the first entry is the root.
  var stacks = {
    home: ['home'],
    calendar: ['calendar'],
    give: ['give'],
    community: ['community'],
    me: ['me']
  };
  var activeTab = 'home';

  var screensEl = document.querySelector('.p-screens');
  var tabBtns = document.querySelectorAll('.p-tab[data-tab]');
  var tabBar = document.querySelector('.p-tabbar');

  function screenEl(key) { return document.getElementById('s-' + key); }

  function currentKey() { return stacks[activeTab][stacks[activeTab].length - 1]; }

  function render(prevKey, direction) {
    var key = currentKey();
    document.querySelectorAll('.p-screen.on').forEach(function (s) {
      if (s.id !== 's-' + key) { s.classList.remove('on'); }
    });
    var el = screenEl(key);
    if (!el) return;
    el.classList.toggle('pushed', stacks[activeTab].length > 1);
    el.classList.add('on');

    // header title + back-button visibility
    var h1 = el.querySelector('.p-header h1');
    if (h1) h1.textContent = titles[key] || h1.textContent;
    var back = el.querySelector('.p-header .p-back');
    if (back) back.style.visibility = stacks[activeTab].length > 1 ? 'visible' : 'hidden';

    tabBtns.forEach(function (b) { b.classList.toggle('on', b.dataset.tab === activeTab); });

    var scroller = el.querySelector('.p-scroll');
    if (scroller) scroller.scrollTop = 0;
  }

  function switchTab(tab) {
    if (!TABS.indexOf) {} // no-op, keeps older engines from choking on Array#indexOf absence
    if (activeTab === tab) {
      // Re-tapping the active tab pops its stack back to root (iOS convention).
      if (stacks[tab].length > 1) {
        stacks[tab] = [stacks[tab][0]];
        pushHistory();
        render();
      }
      return;
    }
    activeTab = tab;
    pushHistory();
    render();
  }

  function push(key) {
    if (!screenEl(key)) return;
    stacks[activeTab].push(key);
    pushHistory();
    render();
  }

  function pop() {
    if (stacks[activeTab].length <= 1) return;
    stacks[activeTab].pop();
    render();
  }

  function pushHistory() {
    if (history.pushState) {
      history.pushState({ tab: activeTab, depth: stacks[activeTab].length }, '', '#' + activeTab + '/' + currentKey());
    }
  }

  window.addEventListener('popstate', function () {
    pop();
  });

  // ---- tab bar -------------------------------------------------------
  document.addEventListener('click', function (e) {
    var t = e.target.closest('[data-tab]');
    if (t) { switchTab(t.dataset.tab); }
  });

  // ---- push / back -----------------------------------------------------
  document.addEventListener('click', function (e) {
    var p = e.target.closest('[data-push]');
    if (p) { e.preventDefault(); push(p.dataset.push); return; }
    var b = e.target.closest('[data-back]');
    if (b) { e.preventDefault(); pop(); }
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { pop(); }
  });

  // ---- segmented rail (.p-seg) — same contract shape as app.js .seg -----
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.p-seg button[data-seg]');
    if (!btn) return;
    var group = btn.closest('.p-seg').dataset.segGroup;
    var host = btn.closest('.p-screen') || document;
    host.querySelectorAll('.p-seg[data-seg-group="' + group + '"] button').forEach(function (b) { b.classList.remove('on'); });
    btn.classList.add('on');
    host.querySelectorAll('[data-seg-panel="' + group + '"]').forEach(function (p) { p.classList.remove('on'); });
    var panel = host.querySelector('[data-seg-panel="' + group + '"][data-seg-val="' + btn.dataset.seg + '"]');
    if (panel) panel.classList.add('on');
    var scroller = btn.closest('.p-scroll');
    if (scroller) scroller.scrollTop = 0;
  });

  // ---- decorative seg rail (no data-seg-panel wired, e.g. year/category
  // filters that are visual-only on desktop too) — single-select highlight
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.p-seg button:not([data-seg])');
    if (!btn) return;
    var rail = btn.closest('.p-seg');
    rail.querySelectorAll('button').forEach(function (b) { b.classList.remove('on'); });
    btn.classList.add('on');
  });

  // ---- accordion (.p-acc) ------------------------------------------------
  document.addEventListener('click', function (e) {
    var h = e.target.closest('.p-acc-h');
    if (!h) return;
    var acc = h.closest('.p-acc');
    var body = acc.querySelector('.p-acc-b');
    var open = acc.classList.toggle('open');
    if (body) body.style.maxHeight = open ? body.scrollHeight + 'px' : '';
  });

  // ---- bottom sheet --------------------------------------------------
  function openSheet(id) {
    var wrap = document.getElementById(id);
    if (wrap) wrap.classList.add('on');
  }
  function closeSheet(el) {
    var wrap = el.closest('.p-sheet-wrap');
    if (wrap) wrap.classList.remove('on');
  }
  document.addEventListener('click', function (e) {
    var open = e.target.closest('[data-sheet]');
    if (open) { openSheet(open.dataset.sheet); return; }
    var close = e.target.closest('[data-sheet-close]');
    if (close) { closeSheet(close); return; }
    var bg = e.target.closest('.p-sheet-bg');
    if (bg) { closeSheet(bg); }
  });

  // ---- quiz single-select (ported from app.js) ------------------------
  document.addEventListener('click', function (e) {
    var opt = e.target.closest('.p-quiz-opt[data-quiz]');
    if (!opt) return;
    var group = opt.closest('.p-quiz-opts');
    if (group) group.querySelectorAll('.p-quiz-opt').forEach(function (o) { o.classList.remove('correct'); });
    if (opt.dataset.quiz === 'correct') opt.classList.add('correct');
  });

  // ---- chip single-select ------------------------------------------------
  document.addEventListener('click', function (e) {
    var chip = e.target.closest('.p-chip[data-chip-group]');
    if (!chip) return;
    var group = chip.dataset.chipGroup;
    document.querySelectorAll('.p-chip[data-chip-group="' + group + '"]').forEach(function (c) { c.classList.remove('on'); });
    chip.classList.add('on');
  });

  // ---- toggle switches -------------------------------------------------
  document.addEventListener('click', function (e) {
    var tg = e.target.closest('.p-toggle');
    if (!tg) return;
    tg.classList.toggle('on');
  });

  // ---- emoji reactions on announcements (client-side only) ---------------
  document.addEventListener('click', function (e) {
    var r = e.target.closest('[data-react]');
    if (!r) return;
    var n = r.querySelector('b');
    if (!n) return;
    var v = parseInt(n.textContent.replace(/[^0-9]/g, ''), 10) || 0;
    var on = r.classList.toggle('active');
    n.textContent = String(on ? v + 1 : Math.max(0, v - 1));
  });

  // ---- push notification demo -------------------------------------------
  var demoNotifs = {
    birthday: {
      title: 'Happy Birthday, Manan! 🎂',
      message: 'The whole sangha wishes you a joyful year ahead. Tap to share a birthday seva today.',
      cta: 'Tap to open ›'
    },
    mjk: {
      title: 'Mahavir Janma Kalyanak — 3 days away',
      message: 'RSVP by Apr 22 so we can plan the thali count for the swamivatsalya lunch.',
      cta: 'Tap to RSVP ›'
    }
  };
  window.showPhoneNotification = function (key) {
    var data = demoNotifs[key];
    if (!data) return;
    var banner = document.getElementById('p-push-banner');
    if (!banner) return;
    banner.querySelector('.ttl').textContent = data.title;
    banner.querySelector('.msg').textContent = data.message;
    banner.querySelector('.cta').textContent = data.cta;
    banner.classList.add('show');
    clearTimeout(window.__pPushTimer);
    window.__pPushTimer = setTimeout(function () { banner.classList.remove('show'); }, 4200);
  };
  document.addEventListener('click', function (e) {
    if (e.target.closest('#p-push-banner')) {
      document.getElementById('p-push-banner').classList.remove('show');
    }
  });

  // ---- toast fallback: guarantee no dead taps anywhere in the phone ------
  function showToast(msg) {
    var stack = document.querySelector('.p-screen.on .p-toast-stack');
    if (!stack) return;
    var t = document.createElement('div');
    t.className = 'p-toast';
    t.textContent = msg;
    stack.appendChild(t);
    requestAnimationFrame(function () { t.classList.add('show'); });
    setTimeout(function () {
      t.classList.remove('show');
      setTimeout(function () { t.remove(); }, 250);
    }, 2000);
  }

  document.addEventListener('click', function (e) {
    var el = e.target.closest('button, a');
    if (!el) return;
    var wired = el.matches([
      '[data-tab]', '[data-push]', '[data-back]', '[data-sheet]', '[data-sheet-close]',
      '[data-chip-group]', '[data-quiz]', '[data-react]', '.p-toggle',
      '.p-seg button', '.p-acc-h *'
    ].join(','));
    if (wired) return;
    if (el.closest('.p-seg, .p-acc-h, .p-tabbar, .p-sheet-wrap, #p-push-banner')) return;
    if (el.tagName === 'A' && el.getAttribute('href') && el.getAttribute('href') !== '#') return;
    if (el.disabled) return;
    var label = (el.getAttribute('title') || el.getAttribute('aria-label') || el.textContent || '').replace(/\s+/g, ' ').trim();
    showToast('✓ ' + (label ? label.slice(0, 40) : 'Action noted'));
  });

  // ---- fit the device frame to the viewport ------------------------------
  // At 100% browser zoom the stage (top bar + device + hint) is taller than
  // most viewports, which forced scrolling the whole page just to see the
  // bottom of the phone outline, on top of the phone's own internal scroll.
  // Below 720px wide the device already goes full-bleed (see phone.css) and
  // this is skipped entirely — it only applies to the desktop "stage" view.
  (function fitDevice() {
    var scaleWrap = document.getElementById('p-device-scale');
    var device = document.getElementById('p-device');
    var bar = document.querySelector('.p-stage-bar');
    var hint = document.querySelector('.p-stage-hint');
    if (!scaleWrap || !device) return;
    var NATURAL_W = 390, NATURAL_H = 844;
    function apply() {
      if (window.innerWidth <= 720) {
        // real-phone mode — no scaling, let it fill the viewport
        device.style.transform = '';
        scaleWrap.style.width = '';
        scaleWrap.style.height = '';
        return;
      }
      // +20px safety buffer so rounding/font-metric differences never leave a
      // few px of unavoidable page scroll — a slightly smaller device beats that.
      var reserved = (bar ? bar.offsetHeight : 0) + (hint ? hint.offsetHeight : 0) + 48 + 40 + 26 + 26 + 20;
      var available = window.innerHeight - reserved;
      var scale = Math.min(1, Math.max(0.5, available / NATURAL_H));
      device.style.transform = 'scale(' + scale + ')';
      scaleWrap.style.width = Math.round(NATURAL_W * scale) + 'px';
      scaleWrap.style.height = Math.round(NATURAL_H * scale) + 'px';
    }
    apply();
    window.addEventListener('resize', apply);
    // re-measure once the webfont swaps in — Playfair vs. the fallback serif
    // can reflow the hint text onto a different number of lines, changing
    // its height after the first paint.
    if (document.fonts && document.fonts.ready) { document.fonts.ready.then(apply); }
    setTimeout(apply, 400);
  })();

  // ---- boot -------------------------------------------------------------
  render();
})();
