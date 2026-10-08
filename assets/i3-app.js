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
    if (window.__accSync) window.__accSync(view);
    document.body.classList.toggle('on-hero', view === 'home' && !!document.getElementById('h6'));
    if (window.__topbarSync) window.__topbarSync();
    document.querySelectorAll('[data-acct-tab]').forEach(function (t) { t.classList.toggle('on', t.dataset.acctTab === view); });
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

  /* "All" tab of the Community Feed shows every panel */
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.seg[data-seg-group="ann-tab"] button[data-seg="all"]');
    if (!btn) return;
    document.querySelectorAll('[data-seg-panel="ann-tab"]').forEach(function (p) { p.classList.remove('hide'); });
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

  /* ---------- transparent nav over the home hero photo (index.html only) ---------- */
  (function siteHeroNav() {
    var nav = document.querySelector('.site-nav');
    var hero = document.querySelector('.site-hero-home');
    if (!nav || !hero) return;
    if (!('IntersectionObserver' in window)) return;
    nav.classList.add('site-nav--on-hero');
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        nav.classList.toggle('site-nav--on-hero', entry.isIntersecting);
      });
    });
    io.observe(hero);
  })();

  /* ---------- home hero logo shrinks into the nav logo as you scroll (index.html only) ---------- */
  (function siteHeroLogo() {
    var hero = document.querySelector('.site-hero-home');
    var heroLogo = document.querySelector('.site-hero-logo');
    if (!hero || !heroLogo) return;
    var root = document.documentElement;
    var ticking = false;
    function update() {
      ticking = false;
      var end = hero.offsetHeight * 0.55;
      var p = end > 0 ? Math.min(1, Math.max(0, window.scrollY / end)) : 0;
      root.style.setProperty('--hlp', p.toFixed(3));
    }
    function onScroll() {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(update);
    }
    update();
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll);
  })();

  /* ---------- marketing announcement ticker (index.html only) ---------- */
  (function siteTicker() {
    var items = document.querySelectorAll('.site-ticker-item');
    var dots = document.querySelectorAll('.site-ticker-dots span');
    if (!items.length) return;
    var i = 0;
    var viewport = document.querySelector('.site-ticker-viewport');
    /* size the viewport to the active message so the dots sit right after the text */
    function fit() {
      if (viewport) viewport.style.width = items[i].offsetWidth + 'px';
    }
    var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    function go(n) {
      items[i].classList.remove('on');
      if (dots[i]) dots[i].classList.remove('on');
      i = ((n % items.length) + items.length) % items.length;
      items[i].classList.add('on');
      if (dots[i]) dots[i].classList.add('on');
      fit();
    }
    var timer;
    function restart() {
      clearInterval(timer);
      if (reduced) return;
      timer = setInterval(function () { go(i + 1); }, 6000);
    }
    dots.forEach(function (d, n) {
      d.addEventListener('click', function () { go(n); restart(); });
    });
    fit();
    window.addEventListener('resize', fit);
    window.addEventListener('load', fit);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(fit);
    restart();
  })();

  /* ---------- scrollytelling journey: dotted arc + crossfading photos (index.html only) ---------- */
  (function journeyScrolly() {
    var section = document.querySelector('.journey');
    if (!section) return; // 4 steps / 4 photos / 4 dots
    var steps = section.querySelectorAll('.journey-step');
    var photos = section.querySelectorAll('.journey-photo');
    var dots = section.querySelectorAll('.journey-dot');
    var clipRect = section.querySelector('.journey-arc-clip-rect');
    var arcViewboxHeight = 780; // matches the arc <svg viewBox="0 0 800 780"> in index.html
    function setActive(i) {
      photos.forEach(function (p, idx) { p.classList.toggle('active', idx === i); });
      dots.forEach(function (d, idx) {
        d.classList.toggle('active', idx <= i);
        d.classList.toggle('current', idx === i);
      });
      if (clipRect && steps.length > 1) {
        var progress = i / (steps.length - 1);
        clipRect.setAttribute('height', String(arcViewboxHeight * progress));
      }
    }
    if (!steps.length) return;
    // active step = the card whose centre is nearest the viewport centre (the card sitting beside the sticky photo)
    var current = -1;
    function update() {
      var mid = window.innerHeight / 2, best = 0, bestD = Infinity;
      steps.forEach(function (s, idx) {
        var card = s.querySelector('.journey-step-card') || s;
        var r = card.getBoundingClientRect();
        var d = Math.abs(r.top + r.height / 2 - mid);
        if (d < bestD) { bestD = d; best = idx; }
      });
      if (best !== current) { current = best; setActive(best); }
    }
    window.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    update();

    // phone: photos are a swipeable row, so the pager dots follow its scroll position
    var frame = section.querySelector('.journey-frame');
    var pager = section.querySelectorAll('.journey-pager i');
    if (frame && pager.length) {
      frame.addEventListener('scroll', function () {
        var first = photos[0], stride = first.offsetWidth + 14;
        var idx = Math.max(0, Math.min(photos.length - 1, Math.round(frame.scrollLeft / stride)));
        pager.forEach(function (d, n) { d.classList.toggle('on', n === idx); });
      }, { passive: true });
    }
  })();

  /* ---------- reveal-on-scroll (elements opted in with .reveal, once each) ---------- */
  (function revealOnScroll() {
    var els = document.querySelectorAll('.reveal');
    if (!els.length) return;
    if (!('IntersectionObserver' in window)) {
      els.forEach(function (e) { e.classList.add('in'); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
      });
    }, { threshold: 0.16 });
    els.forEach(function (e) { io.observe(e); });
  })();

  /* ---------- count-up figures (index.html/visit.html stat strips, [data-count-to]) ---------- */
  (function countUpFigures() {
    var els = document.querySelectorAll('[data-count-to]');
    if (!els.length) return;
    var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    function animate(el) {
      var to = parseInt(el.dataset.countTo, 10) || 0;
      var suffix = el.dataset.suffix || '';
      if (reduced) { el.textContent = to.toLocaleString() + suffix; return; }
      var start = null, dur = 1100;
      function step(ts) {
        if (!start) start = ts;
        var p = Math.min(1, (ts - start) / dur);
        var eased = 1 - Math.pow(1 - p, 3);
        el.textContent = Math.round(to * eased).toLocaleString() + suffix;
        if (p < 1) requestAnimationFrame(step);
      }
      requestAnimationFrame(step);
    }
    if (!('IntersectionObserver' in window)) { els.forEach(animate); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { animate(en.target); io.unobserve(en.target); }
      });
    }, { threshold: 0.5 });
    els.forEach(function (e) { io.observe(e); });
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
  /* ---------- collapsible sidebar (state remembered per browser) ---------- */
  (function () {
    var btn = document.getElementById('sb-toggle'), app = document.querySelector('.app'); if (!btn || !app) return;
    function set(c, save) {
      app.classList.toggle('sb-collapsed', c);
      btn.setAttribute('aria-expanded', String(!c));
      var t = c ? 'Expand menu' : 'Collapse menu'; btn.setAttribute('aria-label', t); btn.title = t;
      if (save) { try { localStorage.setItem('jca-sb', c ? '1' : '0'); } catch (e) {} }
    }
    var saved = null; try { saved = localStorage.getItem('jca-sb'); } catch (e) {}
    if (saved === '1') set(true, false);
    var animT = 0;
    btn.addEventListener('click', function () {
      app.classList.add('sb-anim'); clearTimeout(animT);
      animT = setTimeout(function () { app.classList.remove('sb-anim'); if (window.__h6) window.__h6.measure(); }, 300);   // one hero re-measure after the slide
      set(!app.classList.contains('sb-collapsed'), true);
    });
  })();
  /* ---------- top bar: transparent over the Home hero, solid once it scrolls away ---------- */
  (function () {
    var bar = document.querySelector('.topbar'), hero = document.getElementById('h6'), tick = false; if (!bar) return;
    function sync() {
      tick = false;
      var onHero = document.body.classList.contains('on-hero') && hero;
      bar.classList.toggle('solid', !onHero || hero.getBoundingClientRect().bottom < 90);
    }
    function req() { if (!tick) { tick = true; requestAnimationFrame(sync); } }
    window.__topbarSync = sync;
    window.addEventListener('scroll', req, { passive: true }); window.addEventListener('resize', req);
    sync();
  })();

  /* ---------- sidebar accordion: umbrella groups, one open at a time ---------- */
  (function () {
    var groups = [].slice.call(document.querySelectorAll('.nav-acc'));
    if (!groups.length) return;
    var app = document.querySelector('.app');
    function setOpen(g, open) {
      g.classList.toggle('open', open);
      var b = g.querySelector('.nav-acc-btn'); if (b) b.setAttribute('aria-expanded', open ? 'true' : 'false');
    }
    function openOnly(g) { groups.forEach(function (o) { setOpen(o, o === g); }); }
    groups.forEach(function (g) {
      g.querySelector('.nav-acc-btn').addEventListener('click', function () {
        if (app && app.classList.contains('sb-collapsed')) {   // icon rail: widen first, then open this group
          var t = document.getElementById('sb-toggle'); if (t) t.click();
          openOnly(g); return;
        }
        if (g.classList.contains('open')) setOpen(g, false); else openOnly(g);
      });
    });
    window.__accSync = function (view) {
      var hit = null;
      groups.forEach(function (g) {
        var has = !!g.querySelector('.nav-item[data-view="' + view + '"]');
        g.classList.toggle('has-active', has); if (has) hit = g;
      });
      if (hit) openOnly(hit);
      else if (view === 'home') groups.forEach(function (o) { setOpen(o, false); });
    };
    var cur = document.querySelector('.nav-item.active[data-view]');   // show() ran before this block existed
    if (cur) window.__accSync(cur.dataset.view);
  })();

  /* ---------- 360° tour viewer (Gallery → 360° Tour) ---------- */
  (function () {
    var list = document.querySelector('.tour-list'); if (!list) return;
    var img = document.querySelector('.tour-view img'), badge = document.querySelector('.tour-view .badge span'), open = document.querySelector('.tour-view .open');
    [].slice.call(list.querySelectorAll('button')).forEach(function (b) {
      b.addEventListener('click', function () {
        [].slice.call(list.querySelectorAll('button')).forEach(function (o) { o.setAttribute('aria-pressed', o === b); });
        if (img) { img.style.opacity = 0; setTimeout(function () { img.src = b.getAttribute('data-img'); img.alt = b.getAttribute('data-name'); img.style.opacity = 1; }, 160); }
        if (badge) badge.textContent = b.getAttribute('data-name') + ' · 360°';
        if (open) open.href = b.getAttribute('data-url');
      });
    });
  })();
})();
