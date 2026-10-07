/* JCA · Iteration 1 — behaviour. Plain JS, no dependencies. Every block is gated on element presence. */
(function () {
  'use strict';
  var d = document, root = d.documentElement;
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  function $(s, c) { return (c || d).querySelector(s); }
  function $$(s, c) { return [].slice.call((c || d).querySelectorAll(s)); }
  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) {} return null; }

  /* ---------- header: solid after scroll, parallax var ---------- */
  var hdr = $('.hdr'), ticking = false;
  function onScroll() {
    if (ticking) return; ticking = true;
    requestAnimationFrame(function () {
      ticking = false;
      var y = window.scrollY || 0;
      if (hdr) hdr.classList.toggle('solid', y > 40 || d.body.classList.contains('menu-open') || !!$('.nav-item.open'));
      if (!reduce) root.style.setProperty('--sy', Math.min(y, 1400));
    });
  }
  window.addEventListener('scroll', onScroll, { passive: true }); onScroll();

  /* ---------- mock sign-in state: login link keeps you on this page; signed in -> profile menu ---------- */
  (function () {
    var sc = $$('script[src*="assets/i1.js"]')[0]; if (!sc) return;
    var root = new URL('../', new URL(sc.getAttribute('src'), location.href).href.split('?')[0]).href;   // site root (…/assets/i1.js -> …/)
    var rel = location.pathname.slice(new URL(root).pathname.length) || 'iteration1/';
    var authed = store('jca-auth') === '1';
    var loginHref = root + 'login.html?next=' + encodeURIComponent(rel);
    $$('a[href$="login.html"]').forEach(function (a) { a.setAttribute('href', loginHref); });
    if (!authed) return;
    var tools = $('.hdr-tools'), signin = $('.hdr-signin'); if (!tools) return;
    var app = root + 'iteration2/';
    var LINKS = [['Profile', 'Your details and household', '#profile'], ['Family & Dues', 'Members, passes and what is due', '#family'], ['Settings', 'Notifications and preferences', '#settings'], ['Donation History', 'Receipts and tax statements', '#history'], ['Recurring Seva', 'Your monthly offerings', '#recurring']];
    var prof = d.createElement('div'); prof.className = 'nav-item prof';
    prof.innerHTML = '<button type="button" class="prof-btn nav-link" aria-expanded="false" aria-controls="prof-menu" aria-label="Account menu"><span class="prof-av">MS</span><svg class="chev" viewBox="0 0 10 10" aria-hidden="true"><use href="#chev"/></svg></button>' +
      '<div class="mega prof-menu" id="prof-menu" role="region" aria-label="Account menu"><div class="prof-head"><span class="prof-av lg">MS</span><div><b>Manan Shah</b><span>Patron · ID 04812</span></div></div><div class="mega-links">' +
      LINKS.map(function (l) { return '<a href="' + app + l[2] + '"><i class="dot"></i><div><b>' + l[0].replace('&', '&amp;') + '</b><span>' + l[1] + '</span></div></a>'; }).join('') +
      '</div><button type="button" class="prof-out">Sign out</button></div>';
    if (signin) signin.remove();
    tools.insertBefore(prof, tools.firstChild);
    function out() { try { localStorage.removeItem('jca-auth'); } catch (e) {} location.reload(); }
    $('.prof-out', prof).addEventListener('click', out);
    var cta = $('.drawer-cta'), dsign = cta && $('a[href*="login.html"]', cta);
    if (cta && dsign) {
      var dt = d.createElement('details');
      dt.innerHTML = '<summary>Manan Shah</summary><div class="sub">' + LINKS.map(function (l) { return '<a href="' + app + l[2] + '">' + l[0].replace('&', '&amp;') + '<span>' + l[1] + '</span></a>'; }).join('') + '</div>';
      cta.parentNode.insertBefore(dt, cta);
      dsign.textContent = 'Sign out'; dsign.setAttribute('href', '#'); dsign.addEventListener('click', function (e) { e.preventDefault(); out(); });
    }
  })();

  /* ---------- mega menu ---------- */
  var items = $$('.nav-item'), closeT;
  function closeAll(except) {
    items.forEach(function (it) {
      if (it === except) return;
      it.classList.remove('open'); var b = $('.nav-link', it); if (b) b.setAttribute('aria-expanded', 'false');
    });
    onScroll();
  }
  function openItem(it) {
    clearTimeout(closeT); closeAll(it);
    it.classList.add('open'); $('.nav-link', it).setAttribute('aria-expanded', 'true'); onScroll();
  }
  items.forEach(function (it, idx) {
    var btn = $('.nav-link', it), panel = $('.mega', it);
    if (!panel) return;
    $$('.mega-links a', it).forEach(function (a, i) { a.style.setProperty('--i', i); });
    it.addEventListener('pointerenter', function (e) { if (e.pointerType === 'mouse') openItem(it); });
    it.addEventListener('pointerleave', function (e) { if (e.pointerType === 'mouse') { closeT = setTimeout(function () { closeAll(); }, 160); } });
    btn.addEventListener('click', function (e) {
      if (it.classList.contains('open')) { closeAll(); } else { openItem(it); }
    });
    it.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { closeAll(); btn.focus(); }
      else if (e.key === 'ArrowDown' && e.target === btn) { e.preventDefault(); openItem(it); var f = $('.mega a', it); if (f) f.focus(); }
      else if (e.key === 'ArrowRight' && e.target === btn) { var n = items[(idx + 1) % items.length]; $('.nav-link', n).focus(); }
      else if (e.key === 'ArrowLeft' && e.target === btn) { var p = items[(idx - 1 + items.length) % items.length]; $('.nav-link', p).focus(); }
    });
    it.addEventListener('focusout', function (e) { if (!it.contains(e.relatedTarget)) { closeT = setTimeout(function () { if (!it.contains(d.activeElement)) { it.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); onScroll(); } }, 60); } });
  });
  d.addEventListener('click', function (e) { if (!e.target.closest('.nav-item')) closeAll(); });

  /* ---------- mobile drawer ---------- */
  var burger = $('.burger'), drawer = $('.drawer');
  if (burger && drawer) {
    $$('details, .drawer-cta', drawer).forEach(function (el, i) { el.style.setProperty('--i', i); });
    function drawerSet(open) {
      drawer.classList.toggle('open', open); d.body.classList.toggle('menu-open', open);
      burger.setAttribute('aria-expanded', open); burger.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
      if (hdr) hdr.classList.toggle('drawer-open', open); onScroll();
    }
    burger.addEventListener('click', function () { drawerSet(!drawer.classList.contains('open')); });
    drawer.addEventListener('click', function (e) { if (e.target.closest('a')) drawerSet(false); });
    d.addEventListener('keydown', function (e) { if (e.key === 'Escape' && drawer.classList.contains('open')) { drawerSet(false); burger.focus(); } });
    window.addEventListener('resize', function () { if (window.innerWidth >= 1100) drawerSet(false); });
    // accordion: opening one closes the others
    $$('details', drawer).forEach(function (dt) { dt.addEventListener('toggle', function () { if (dt.open) $$('details', drawer).forEach(function (o) { if (o !== dt) o.open = false; }); }); });
  }

  /* ---------- announcement ticker ---------- */
  (function () {
    var its = $$('.ticker-item'); if (its.length < 2) return;
    var i = 0; setInterval(function () { its[i].classList.remove('on'); i = (i + 1) % its.length; its[i].classList.add('on'); }, 5200);
  })();

  /* ---------- reveal on scroll ---------- */
  var revealEls = $$('.rv, .timeline, .shrine-media, .bar');
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        var el = e.target; el.classList.add('in'); io.unobserve(el);
        // once revealed, hand the element back to its normal hover/transform rules
        if (el.classList.contains('rv')) setTimeout(function () { el.classList.remove('rv', 'in', 'rv-left', 'rv-right'); el.style.removeProperty('--d'); }, 1500);
      });
    }, { threshold: .12, rootMargin: '0px 0px -6% 0px' });
    revealEls.forEach(function (el) { io.observe(el); });
  } else { revealEls.forEach(function (el) { el.classList.add('in'); }); }

  /* ---------- count-up ---------- */
  (function () {
    var els = $$('[data-count-to]'); if (!els.length) return;
    function run(el) {
      var to = +el.getAttribute('data-count-to'), suf = el.getAttribute('data-suffix') || '';
      if (reduce) { el.textContent = to.toLocaleString('en-US') + suf; return; }
      var t0 = null, dur = 1600;
      (function step(t) { if (!t0) t0 = t; var p = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - p, 4);
        el.textContent = Math.round(to * e).toLocaleString('en-US') + suf; if (p < 1) requestAnimationFrame(step); })(performance.now());
    }
    if (!('IntersectionObserver' in window)) { els.forEach(run); return; }
    var o = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { run(e.target); o.unobserve(e.target); } }); }, { threshold: .6 });
    els.forEach(function (el) { o.observe(el); });
  })();

  /* ---------- building explorer (home) ---------- */
  (function () {
    var rootEl = $('#tower'); if (!rootEl) return;
    var fl = $$('.floor', rootEl), cur = 0, t;
    function show(i) { cur = i; fl.forEach(function (f, k) { var on = k === i; f.classList.toggle('active', on); $('.floor-head', f).setAttribute('aria-expanded', on); }); }
    function auto() { clearInterval(t); if (!reduce) t = setInterval(function () { show((cur + 1) % fl.length); }, 5200); }
    fl.forEach(function (f, i) { $('.floor-head', f).addEventListener('click', function () { show(i); clearInterval(t); }); });
    rootEl.addEventListener('mouseenter', function () { clearInterval(t); }); rootEl.addEventListener('mouseleave', auto);
    rootEl.addEventListener('focusin', function () { clearInterval(t); }); auto();
  })();

  /* ---------- scroll-spy for sticky sub-navigation ---------- */
  (function () {
    var links = $$('.subnav a[href^="#"]'); if (!links.length || !('IntersectionObserver' in window)) return;
    var map = {}; links.forEach(function (a) { var s = $(a.getAttribute('href')); if (s) map[s.id] = a; });
    var ids = Object.keys(map); if (!ids.length) return;
    var so = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        links.forEach(function (a) { a.classList.remove('on'); }); var a = map[e.target.id]; a.classList.add('on');
        var bar = a.parentNode; if (bar.scrollWidth > bar.clientWidth) bar.scrollTo({ left: a.offsetLeft - 24, behavior: reduce ? 'auto' : 'smooth' });
      });
    }, { rootMargin: '-35% 0px -60% 0px' });
    ids.forEach(function (id) { so.observe(d.getElementById(id)); });
  })();

  /* ---------- collapsible long reads ---------- */
  $$('.collapse[data-collapse]').forEach(function (el) {
    var body = $('.collapse-body', el), ch = +el.getAttribute('data-collapse') || 260;
    if (!body || body.scrollHeight < ch + 140) return;
    el.style.setProperty('--ch', ch + 'px'); el.classList.add('is-collapsed');
    var btn = d.createElement('button'); btn.type = 'button'; btn.className = 'collapse-toggle'; btn.setAttribute('aria-expanded', 'false');
    var label = el.getAttribute('data-label') || 'Continue reading';
    btn.innerHTML = '<span>' + label + '</span><svg viewBox="0 0 12 12"><path d="M2 4l4 4 4-4"/></svg>'; el.appendChild(btn);
    btn.addEventListener('click', function () {
      var collapsed = el.classList.contains('is-collapsed');
      if (collapsed) {
        body.style.maxHeight = body.scrollHeight + 'px'; el.classList.remove('is-collapsed');
        setTimeout(function () { body.style.maxHeight = ''; }, 850); btn.firstChild.textContent = 'Show less'; btn.setAttribute('aria-expanded', 'true');
      } else {
        body.style.maxHeight = body.scrollHeight + 'px'; void body.offsetHeight; el.classList.add('is-collapsed'); body.style.maxHeight = '';
        btn.firstChild.textContent = label; btn.setAttribute('aria-expanded', 'false');
        var top = el.getBoundingClientRect().top; if (top < 80) window.scrollBy({ top: top - 120, behavior: reduce ? 'auto' : 'smooth' });
      }
    });
  });

  /* ---------- idols: floor filter + per-card details ---------- */
  (function () {
    var grid = $('.idol-grid'); if (!grid) return;
    var cards = $$('.idol', grid), floors = {}, order = [];
    function floorOf(c) {
      var dts = $$('dt', c), v = '';
      dts.forEach(function (dt) { if (/^floor$/i.test(dt.textContent.trim())) v = dt.nextElementSibling.textContent; });
      v = v.toLowerCase();
      if (/cellar/.test(v)) return 'Cellar'; if (/first|1st/.test(v)) return 'First floor'; if (/second|2nd/.test(v)) return 'Second floor';
      if (/third|3rd/.test(v)) return 'Third floor'; if (/fourth|4th/.test(v)) return 'Fourth floor'; return 'Guardians & devotees';
    }
    cards.forEach(function (c) {
      var f = floorOf(c); c.setAttribute('data-floor', f); if (!floors[f]) { floors[f] = 0; order.push(f); } floors[f]++;
      var dl = $('dl', c);
      if (dl && dl.children.length > 8) {
        c.classList.add('is-collapsed');
        var b = d.createElement('button'); b.type = 'button'; b.className = 'idol-toggle'; b.textContent = 'All details'; $('.info', c).appendChild(b);
        b.addEventListener('click', function () { var on = c.classList.toggle('is-collapsed'); b.textContent = on ? 'All details' : 'Fewer details'; });
      }
    });
    var rank = ['Cellar', 'First floor', 'Second floor', 'Third floor', 'Fourth floor', 'Guardians & devotees'];
    order.sort(function (a, b) { return rank.indexOf(a) - rank.indexOf(b); });
    var bar = d.createElement('div'); bar.className = 'chips'; bar.setAttribute('role', 'group'); bar.setAttribute('aria-label', 'Filter idols by floor');
    var count = d.createElement('p'); count.className = 'idol-count'; count.setAttribute('aria-live', 'polite');
    function apply(f) {
      var n = 0; cards.forEach(function (c) { var show = f === 'All' || c.getAttribute('data-floor') === f; c.classList.toggle('is-hidden', !show); if (show) n++; });
      $$('.chip', bar).forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-f') === f); });
      count.textContent = 'Showing ' + n + ' of ' + cards.length + ' pratimas';
    }
    ['All'].concat(order).forEach(function (f) {
      var b = d.createElement('button'); b.type = 'button'; b.className = 'chip'; b.setAttribute('data-f', f);
      b.textContent = f === 'All' ? 'All (' + cards.length + ')' : f + ' (' + floors[f] + ')'; b.addEventListener('click', function () { apply(f); }); bar.appendChild(b);
    });
    grid.parentNode.insertBefore(bar, grid); grid.parentNode.insertBefore(count, grid); apply('All');
  })();

  /* ---------- gallery: tabs ---------- */
  (function () {
    var tabs = $$('.tab[data-tab]'); if (!tabs.length) return;
    function sel(name) {
      tabs.forEach(function (t) { t.setAttribute('aria-selected', t.getAttribute('data-tab') === name); });
      $$('.tabpanel').forEach(function (p) { p.classList.toggle('hide', p.getAttribute('data-panel') !== name); });
    }
    tabs.forEach(function (t) { t.addEventListener('click', function () { sel(t.getAttribute('data-tab')); }); });
    var h = location.hash.replace('#', ''); if (h && $('[data-tab="' + h + '"]')) sel(h);
    window.addEventListener('hashchange', function () { var n = location.hash.replace('#', ''); if ($('[data-tab="' + n + '"]')) sel(n); });
  })();

  /* ---------- gallery: 360 tour viewer ---------- */
  (function () {
    var list = $('.tour-list'); if (!list) return;
    var img = $('.tour-view img'), badge = $('.tour-view .badge span'), open = $('.tour-view .open');
    $$('button', list).forEach(function (b) {
      b.addEventListener('click', function () {
        $$('button', list).forEach(function (o) { o.setAttribute('aria-pressed', o === b); });
        img.style.opacity = 0; setTimeout(function () { img.src = b.getAttribute('data-img'); img.alt = b.getAttribute('data-name'); img.style.opacity = 1; }, 180);
        badge.textContent = b.getAttribute('data-name') + ' · 360°'; open.href = b.getAttribute('data-url');
      });
    });
  })();

  /* ---------- lightbox ---------- */
  (function () {
    var figs = $$('[data-lb]'); if (!figs.length) return;
    var lb = d.createElement('div'); lb.className = 'lb'; lb.setAttribute('role', 'dialog'); lb.setAttribute('aria-modal', 'true'); lb.setAttribute('aria-label', 'Photo viewer');
    lb.innerHTML = '<button class="x" aria-label="Close">&times;</button><button class="p" aria-label="Previous">&#8249;</button><figure><img alt=""><figcaption></figcaption></figure><button class="n" aria-label="Next">&#8250;</button>';
    d.body.appendChild(lb); var im = $('img', lb), cap = $('figcaption', lb), i = 0, last = null;
    function show(n) { i = (n + figs.length) % figs.length; var f = figs[i], s = $('img', f); im.src = s.currentSrc || s.src; im.alt = s.alt; var c = $('figcaption', f); cap.textContent = c ? c.textContent : s.alt; }
    function openAt(n) { last = d.activeElement; show(n); lb.classList.add('open'); d.body.style.overflow = 'hidden'; $('.x', lb).focus(); }
    function close() { lb.classList.remove('open'); d.body.style.overflow = ''; if (last) last.focus(); }
    figs.forEach(function (f, n) { f.tabIndex = 0; f.setAttribute('role', 'button'); f.addEventListener('click', function () { openAt(n); }); f.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openAt(n); } }); });
    $('.x', lb).onclick = close; $('.p', lb).onclick = function () { show(i - 1); }; $('.n', lb).onclick = function () { show(i + 1); };
    lb.addEventListener('click', function (e) { if (e.target === lb) close(); });
    d.addEventListener('keydown', function (e) { if (!lb.classList.contains('open')) return; if (e.key === 'Escape') close(); if (e.key === 'ArrowLeft') show(i - 1); if (e.key === 'ArrowRight') show(i + 1); });
    var x0 = null; lb.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener('touchend', function (e) { if (x0 === null) return; var dx = e.changedTouches[0].clientX - x0; if (Math.abs(dx) > 50) show(i + (dx < 0 ? 1 : -1)); x0 = null; });
  })();

  /* ---------- donation amount chips, forms (static mock) ---------- */
  $$('.chip-amounts').forEach(function (g) { g.addEventListener('click', function (e) { var b = e.target.closest('.chip-amt'); if (!b) return; $$('.chip-amt', g).forEach(function (o) { o.classList.toggle('on', o === b); }); }); });
  $$('form[data-mock]').forEach(function (f) {
    f.addEventListener('submit', function (e) {
      e.preventDefault(); var ok = $('.form-ok', f.parentNode) || d.createElement('p');
      ok.className = 'form-ok note'; ok.setAttribute('role', 'status'); ok.textContent = f.getAttribute('data-mock') || 'Thank you — this is a static preview, nothing was sent.';
      if (!ok.parentNode) f.parentNode.appendChild(ok); f.reset();
    });
  });

  /* ---------- chat widget ---------- */
  (function () {
    var tg = $('#chat-toggle'), pn = $('#chat-panel'); if (!tg || !pn) return;
    tg.addEventListener('click', function () { var hidden = pn.classList.toggle('hide'); tg.setAttribute('aria-expanded', !hidden); });
    $$('[data-chat-close]', pn).forEach(function (b) { b.addEventListener('click', function () { pn.classList.add('hide'); tg.setAttribute('aria-expanded', 'false'); tg.focus(); }); });
    var body = $('.chat-body', pn);
    var answers = {
      'How do I become a member?': 'Registration takes a few minutes — tap Register above, and a committee member will follow up to complete your family record.',
      'Where are you located?': '43-11 Ithaca Street, Elmhurst, NY 11373 — open daily, 7:00 AM to 7:00 PM.'
    };
    $$('[data-chat-ask]', pn).forEach(function (chip) {
      chip.addEventListener('click', function () {
        var q = chip.getAttribute('data-chat-ask'), a = answers[q]; if (!a) return;
        var u = d.createElement('div'); u.className = 'chat-msg user'; u.textContent = q; body.appendChild(u);
        var m = d.createElement('div'); m.className = 'chat-msg bot'; m.innerHTML = '<span class="tag">Grounded · cited</span>' + a; body.appendChild(m);
        chip.remove(); body.scrollTop = body.scrollHeight;
      });
    });
  })();
  /* ---------- daily quiz: mark the pick, reveal the right answer ---------- */
  d.addEventListener('click', function (e) {
    var o = e.target.closest && e.target.closest('.quiz-opt[data-quiz]'); if (!o) return;
    var box = o.closest('.quiz'); if (!box || box.dataset.done) return; box.dataset.done = '1';
    var ok = o.dataset.quiz === 'correct';
    $$('.quiz-opt', box).forEach(function (b) { b.disabled = true; if (b.dataset.quiz === 'correct') b.classList.add('correct'); });
    if (!ok) o.classList.add('wrong');
    var r = $('.quiz-res', box); if (r) r.textContent = ok ? 'Correct — Ahimsa is non-violence. Jai Jinendra!' : 'Not quite — Ahimsa is non-violence, the first great vow.';
  });
})();
