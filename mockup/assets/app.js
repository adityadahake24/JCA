/* ==========================================================================
   JCA Platform mockup — shared client-side behavior
   Same show()/data-jump router pattern as jca-admin-mocukups.html, extended
   with segmented-tab switching, modals, and a ⌘K command palette.
   Static walkthrough only — nothing here talks to a server.
   ========================================================================== */

(function () {
  'use strict';

  var items = document.querySelectorAll('.nav-item[data-view]');
  var views = document.querySelectorAll('.view[id^="v-"]');
  var crumb = document.getElementById('crumb');
  var titles = window.VIEW_TITLES || {};
  var fallback = (document.body.dataset.fallbackView) || 'dashboard';

  function show(view) {
    if (!view) return;
    views.forEach(function (v) { v.classList.add('hide'); });
    var el = document.getElementById('v-' + view);
    if (el) { el.classList.remove('hide'); }
    else {
      var fb = document.getElementById('v-' + fallback);
      if (fb) fb.classList.remove('hide');
    }
    items.forEach(function (i) { i.classList.toggle('active', i.dataset.view === view); });
    if (crumb) crumb.textContent = titles[view] || titles[fallback] || view;
    var main = document.querySelector('.main');
    if (main) main.scrollTo(0, 0);
    window.scrollTo(0, 0);
    if (history.replaceState) history.replaceState(null, '', '#' + view);
  }
  window.showView = show;

  items.forEach(function (i) {
    i.addEventListener('click', function (e) {
      e.preventDefault();
      show(i.dataset.view);
    });
  });

  document.addEventListener('click', function (e) {
    var jumpEl = e.target.closest('[data-jump]');
    if (jumpEl) {
      e.preventDefault();
      show(jumpEl.dataset.jump);
      // optional deep-link into a specific subnav tab of the view just shown
      var target = jumpEl.dataset.subnavTarget;
      if (target) {
        var host = document.getElementById('v-' + jumpEl.dataset.jump);
        var subBtn = host && host.querySelector('.subnav button[data-subnav="' + target + '"]');
        if (subBtn) subBtn.click();
      }
    }
  });

  // Deep-link on load via #hash
  if (views.length) {
    var hash = window.location.hash.replace('#', '');
    show(hash || fallback);
  }

  /* ---------- segmented tabs (.seg button[data-seg-target]) ---------- */
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.seg button[data-seg]');
    if (!btn) return;
    var seg = btn.closest('.seg');
    var group = seg.dataset.segGroup;
    seg.querySelectorAll('button').forEach(function (b) { b.classList.remove('on'); });
    btn.classList.add('on');
    if (group) {
      document.querySelectorAll('[data-seg-panel="' + group + '"]').forEach(function (p) {
        p.classList.add('hide');
      });
      var target = document.querySelector('[data-seg-panel="' + group + '"][data-seg-val="' + btn.dataset.seg + '"]');
      if (target) target.classList.remove('hide');
    }
  });

  /* ---------- sub-nav tabs (.subnav button[data-subnav]) ---------- */
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.subnav button[data-subnav]');
    if (!btn) return;
    var nav = btn.closest('.subnav');
    var group = nav.dataset.subnavGroup;
    nav.querySelectorAll('button').forEach(function (b) { b.classList.remove('on'); });
    btn.classList.add('on');
    document.querySelectorAll('[data-subnav-panel="' + group + '"]').forEach(function (p) {
      p.classList.add('hide');
    });
    var target = document.querySelector('[data-subnav-panel="' + group + '"][data-subnav-val="' + btn.dataset.subnav + '"]');
    if (target) target.classList.remove('hide');
  });

  /* ---------- chip toggles (visual only, e.g. quick-give amounts) ---------- */
  document.addEventListener('click', function (e) {
    var chip = e.target.closest('.chip-amt, .chip[data-chip-group], .quiz-opt[data-quiz]');
    if (!chip) return;
    if (chip.classList.contains('quiz-opt')) {
      chip.closest('.quiz-opts').querySelectorAll('.quiz-opt').forEach(function (o) { o.classList.remove('correct'); });
      if (chip.dataset.quiz === 'correct') chip.classList.add('correct');
      return;
    }
    var group = chip.parentElement;
    group.querySelectorAll('.on').forEach(function (o) { o.classList.remove('on'); });
    chip.classList.add('on');
  });

  /* ---------- emoji reactions on announcements (client-side only) ---------- */
  document.addEventListener('click', function (e) {
    var r = e.target.closest('[data-react]');
    if (!r) return;
    var n = r.querySelector('b');
    if (!n) return;
    var v = parseInt(n.textContent.replace(/[^0-9]/g, ''), 10) || 0;
    var on = r.classList.toggle('on');
    n.textContent = String(on ? v + 1 : Math.max(0, v - 1));
  });

  /* ---------- modals: [data-modal-open="id"] / [data-modal-close] ---------- */
  document.addEventListener('click', function (e) {
    var opener = e.target.closest('[data-modal-open]');
    if (opener) {
      var m = document.getElementById(opener.dataset.modalOpen);
      if (m) m.classList.remove('hide');
      return;
    }
    var closer = e.target.closest('[data-modal-close]');
    if (closer) {
      var overlay = closer.closest('.overlay');
      if (overlay) overlay.classList.add('hide');
      return;
    }
    // click on the dim backdrop itself closes it
    if (e.target.classList.contains('overlay')) {
      e.target.classList.add('hide');
    }
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      document.querySelectorAll('.overlay:not(.hide)').forEach(function (o) { o.classList.add('hide'); });
      var cmdk = document.getElementById('cmdk-overlay');
      if (cmdk) cmdk.classList.add('hide');
    }
  });

  /* ---------- ⌘K command palette ---------- */
  var cmdkOverlay = document.getElementById('cmdk-overlay');
  var cmdkInput = document.getElementById('cmdk-input');
  if (cmdkOverlay && cmdkInput) {
    var openCmdk = function () {
      cmdkOverlay.classList.remove('hide');
      cmdkInput.value = '';
      filterCmdk('');
      setTimeout(function () { cmdkInput.focus(); }, 10);
    };
    document.addEventListener('keydown', function (e) {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        openCmdk();
      }
    });
    document.querySelectorAll('[data-cmdk-open]').forEach(function (b) {
      b.addEventListener('click', openCmdk);
    });
    var cmdkItems = document.querySelectorAll('.cmdk-item');
    function filterCmdk(q) {
      q = q.toLowerCase();
      cmdkItems.forEach(function (item) {
        var text = item.textContent.toLowerCase();
        item.style.display = text.indexOf(q) > -1 ? '' : 'none';
      });
    }
    cmdkInput.addEventListener('input', function () { filterCmdk(cmdkInput.value); });
    cmdkItems.forEach(function (item) {
      item.addEventListener('click', function () {
        cmdkOverlay.classList.add('hide');
        if (item.dataset.jump) show(item.dataset.jump);
        else if (item.dataset.href) window.location.href = item.dataset.href;
      });
    });
  }

  /* ---------- notification bell dropdown ---------- */
  document.addEventListener('click', function (e) {
    var bell = e.target.closest('[data-bell-toggle]');
    if (bell) {
      var panel = document.getElementById(bell.dataset.bellToggle);
      if (panel) panel.classList.toggle('hide');
      return;
    }
    // click outside the open dropdown closes it
    document.querySelectorAll('.bell-dropdown:not(.hide)').forEach(function (p) {
      if (!p.contains(e.target) && !e.target.closest('[data-bell-toggle]')) p.classList.add('hide');
    });
  });

  /* ---------- inline calendar event detail (reveal/hide within the same view) ---------- */
  document.addEventListener('click', function (e) {
    var r = e.target.closest('[data-cal-reveal]');
    if (r) {
      var t = document.getElementById(r.dataset.calReveal);
      if (t) { t.classList.remove('hide'); t.scrollIntoView({ behavior: 'smooth', block: 'nearest' }); }
    }
    var h = e.target.closest('[data-cal-hide]');
    if (h) {
      var t2 = document.getElementById(h.dataset.calHide);
      if (t2) t2.classList.add('hide');
    }
  });

  /* ---------- embedded Payload CMS shells: rail nav + document tabs ---------- */
  document.addEventListener('click', function (e) {
    var rail = e.target.closest('[data-cms-nav]');
    if (rail) {
      var shell = rail.closest('.cms-shell');
      if (!shell) return;
      shell.querySelectorAll('[data-cms-panel]').forEach(function (p) { p.classList.add('hide'); });
      var panel = shell.querySelector('[data-cms-panel="' + rail.dataset.cmsNav + '"]');
      if (panel) panel.classList.remove('hide');
      var activeKey = rail.dataset.cmsParent || rail.dataset.cmsNav;
      shell.querySelectorAll('.cms-rail-item').forEach(function (b) {
        b.classList.toggle('on', b.dataset.cmsNav === activeKey);
      });
      return;
    }
    var tab = e.target.closest('.cms-tabs button[data-cms-tab]');
    if (tab) {
      var tabs = tab.closest('.cms-tabs');
      tabs.querySelectorAll('button').forEach(function (b) { b.classList.remove('on'); });
      tab.classList.add('on');
      var scope = tab.closest('.cms-doc') || tab.closest('.cms-shell');
      scope.querySelectorAll('[data-cms-tabpanel]').forEach(function (p) { p.classList.add('hide'); });
      var target = scope.querySelector('[data-cms-tabpanel="' + tab.dataset.cmsTab + '"]');
      if (target) target.classList.remove('hide');
      return;
    }
    var arrowRow = e.target.closest('.cms-array-row[data-cms-array-toggle]');
    if (arrowRow) {
      var arr = arrowRow.closest('.cms-array');
      arr.querySelectorAll('.cms-array-open').forEach(function (o) { if (o !== arrowRow.nextElementSibling) o.classList.add('hide'); });
      var open = arrowRow.nextElementSibling;
      if (open && open.classList.contains('cms-array-open')) open.classList.toggle('hide');
      return;
    }
    var cmsToggle = e.target.closest('.cms-toggle');
    if (cmsToggle) { cmsToggle.classList.toggle('on'); return; }
    var mediaCard = e.target.closest('.cms-media-card[data-cms-select]');
    if (mediaCard) { mediaCard.classList.toggle('sel'); return; }
  });

  /* ---------- campaign composer live preview (admin.html only) ---------- */
  (function campaignPreview() {
    var title = document.getElementById('camp-title');
    var body = document.getElementById('camp-body');
    if (!title || !body) return;
    function set(id, v) { var el = document.getElementById(id); if (el) el.textContent = v; }
    function sync() {
      var t = title.value.trim() || 'Untitled announcement';
      var b = body.value.trim() || 'Message body will appear here.';
      set('prev-push-title', t); set('prev-mail-subject', t); set('prev-mail-title', t);
      set('prev-push-body', b); set('prev-mail-body', b);
    }
    function channels() {
      var p = document.getElementById('ch-push'), m = document.getElementById('ch-mail');
      var pc = document.getElementById('prev-push-card'), mc = document.getElementById('prev-mail-card');
      if (p && pc) pc.classList.toggle('hide', !p.checked);
      if (m && mc) mc.classList.toggle('hide', !m.checked);
    }
    title.addEventListener('input', sync);
    body.addEventListener('input', sync);
    ['ch-push', 'ch-mail'].forEach(function (id) {
      var el = document.getElementById(id);
      if (el) el.addEventListener('change', channels);
    });
    sync();
    channels();
  })();

  /* ---------- marketing site nav drawer (7 public pages only — element presence gates it) ---------- */
  (function siteNav() {
    var toggle = document.querySelector('[data-site-nav-toggle]');
    var drawer = document.querySelector('[data-site-drawer]');
    if (!toggle || !drawer) return;
    function close() {
      drawer.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
    }
    function toggleDrawer() {
      var open = drawer.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    }
    toggle.addEventListener('click', toggleDrawer);
    drawer.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', close);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') close();
    });
  })();

  /* ---------- floating chatbot widget (index.html only — element presence gates it) ---------- */
  (function chatWidget() {
    var toggle = document.getElementById('chat-toggle');
    var panel = document.getElementById('chat-panel');
    if (!toggle || !panel) return;
    toggle.addEventListener('click', function () { panel.classList.toggle('hide'); });
    panel.querySelectorAll('[data-chat-close]').forEach(function (b) {
      b.addEventListener('click', function () { panel.classList.add('hide'); });
    });
    var body = panel.querySelector('.chat-body');
    var answers = {
      'How do I become a member?': 'Registration takes a few minutes — tap Register above, and a committee member will follow up to complete your family record.',
      'Where are you located?': '43-11 Ithaca Street, Elmhurst, NY 11373 — open daily, 7:00 AM to 7:00 PM.'
    };
    panel.querySelectorAll('[data-chat-ask]').forEach(function (chip) {
      chip.addEventListener('click', function () {
        var q = chip.dataset.chatAsk;
        var a = answers[q];
        if (!a || !body) return;
        var u = document.createElement('div');
        u.className = 'chat-msg user';
        u.textContent = q;
        body.appendChild(u);
        var bmsg = document.createElement('div');
        bmsg.className = 'chat-msg bot';
        bmsg.innerHTML = '<span class="tag">Grounded · cited</span>' + a;
        body.appendChild(bmsg);
        chip.remove();
        body.scrollTop = body.scrollHeight;
      });
    });
  })();

  /* ---------- generic active-toggle for .seg / .chip-row groups with no wired panel ---------- */
  /* (groups that DO drive a panel are handled above by the .seg[data-seg] / .subnav handlers,
     which run first; this covers the remaining display-only tab rows, e.g. year pills.) */
  document.addEventListener('click', function (e) {
    var segBtn = e.target.closest('.seg button:not([data-seg])');
    if (segBtn) {
      segBtn.parentElement.querySelectorAll('button').forEach(function (b) { b.classList.remove('on'); });
      segBtn.classList.add('on');
    }
    var chip = e.target.closest('.chip-row .chip');
    if (chip) {
      chip.parentElement.querySelectorAll('.chip').forEach(function (c) { c.classList.remove('on'); });
      chip.classList.add('on');
    }
  });

  /* ---------- toast feedback ---------- */
  function showToast(msg) {
    var stack = document.getElementById('toast-stack');
    if (!stack) {
      stack = document.createElement('div');
      stack.id = 'toast-stack';
      stack.className = 'toast-stack';
      document.body.appendChild(stack);
    }
    var t = document.createElement('div');
    t.className = 'toast';
    t.textContent = msg;
    stack.appendChild(t);
    requestAnimationFrame(function () { t.classList.add('show'); });
    setTimeout(function () {
      t.classList.remove('show');
      setTimeout(function () { t.remove(); }, 250);
    }, 2200);
  }

  /* ---------- fallback: every remaining button/link confirms its action ---------- */
  /* This is a static walkthrough with no backend, so a click that isn't already wired to
     navigate, open a modal, or switch a tab still needs to visibly do something — never a
     silent dead click. */
  document.addEventListener('click', function (e) {
    var el = e.target.closest('button, a');
    if (!el) return;
    if (el.matches('[data-jump],[data-modal-open],[data-modal-close],[data-cmdk-open],' +
                    '[data-bell-toggle],[data-chat-close],[data-chat-ask],[data-site-nav-toggle],' +
                    '[data-cal-reveal],[data-cal-hide],[data-react],[data-cms-nav],[data-cms-tab],' +
                    '.cmdk-item,.nav-item[data-view],.chip-amt,.quiz-opt,.cms-toggle')) return;
    if (el.closest('.seg, .subnav, .chip-row, .overlay, .cmdk-overlay, .bell-dropdown, .chat-panel, .chat-toggle, .cms-rail, .cms-tabs, .cms-array-row, .cms-media-card')) return;
    if (el.tagName === 'A' && el.getAttribute('href') && el.getAttribute('href') !== '#') return; // real navigation
    if (el.disabled) return;
    var label = (el.getAttribute('title') || el.getAttribute('aria-label') || el.textContent || '')
      .trim().replace(/\s+/g, ' ').slice(0, 44);
    showToast('✓ ' + (label || 'Action noted'));
  });
})();
