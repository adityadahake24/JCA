/* Hero 6 — "Sun Dial". One state variable `p` (0 = sunrise, 1 = sunset) drives the whole scene.
   Per frame we only write opacity / transform on ~20 pre-composited layers: no layout, no repaint. */
(function () {
  'use strict';
  var root = document.getElementById('h6'); if (!root) return;
  var $ = function (s) { return root.querySelector(s); };
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  function clamp(v, a, b) { return v < a ? a : v > b ? b : v; }
  function ss(a, b, x) { var t = clamp((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); }

  /* ---------- where on Earth? (no permission prompt) ---------- */
  var TEMPLE = { lat: 40.7434, lon: -73.8766 };
  var ZONES = { // rough city coordinates for common zones; fallback uses the zone's standard UTC offset
    'America/Chicago': [41.9, -87.6], 'America/Denver': [39.7, -105.0], 'America/Los_Angeles': [34.1, -118.2], 'America/Phoenix': [33.4, -112.1],
    'America/Toronto': [43.7, -79.4], 'America/Detroit': [42.3, -83.0], 'America/Mexico_City': [19.4, -99.1],
    'Europe/London': [51.5, -0.1], 'Europe/Paris': [48.9, 2.35], 'Europe/Berlin': [52.5, 13.4],
    'Asia/Kolkata': [19.1, 72.9], 'Asia/Calcutta': [19.1, 72.9], 'Asia/Dubai': [25.2, 55.3], 'Asia/Singapore': [1.35, 103.8], 'Asia/Tokyo': [35.7, 139.7],
    'Australia/Sydney': [-33.9, 151.2], 'Africa/Nairobi': [-1.3, 36.8], 'Africa/Johannesburg': [-26.2, 28.0]
  };
  var EASTERN = { 'America/New_York': 1, 'US/Eastern': 1, 'America/Toronto': 0 };
  function where(now) {
    var tz = ''; try { tz = Intl.DateTimeFormat().resolvedOptions().timeZone || ''; } catch (e) {}
    if (EASTERN[tz]) return TEMPLE;
    if (ZONES[tz]) return { lat: ZONES[tz][0], lon: ZONES[tz][1] };
    var jan = -new Date(now.getFullYear(), 0, 1).getTimezoneOffset(), jul = -new Date(now.getFullYear(), 6, 1).getTimezoneOffset();
    return { lat: 40.7, lon: Math.min(jan, jul) / 4 };   // standard offset -> central meridian
  }
  /* NOAA solar position: sunrise/sunset in local minutes-of-day */
  function sunTimes(now) {
    var L = where(now), rad = Math.PI / 180;
    var start = new Date(now.getFullYear(), 0, 0), N = Math.floor((now - start) / 864e5);
    var g = 2 * Math.PI / 365 * (N - 1);
    var eq = 229.18 * (0.000075 + 0.001868 * Math.cos(g) - 0.032077 * Math.sin(g) - 0.014615 * Math.cos(2 * g) - 0.040849 * Math.sin(2 * g));
    var dec = 0.006918 - 0.399912 * Math.cos(g) + 0.070257 * Math.sin(g) - 0.006758 * Math.cos(2 * g) + 0.000907 * Math.sin(2 * g) - 0.002697 * Math.cos(3 * g) + 0.00148 * Math.sin(3 * g);
    var c = Math.cos(90.833 * rad) / (Math.cos(L.lat * rad) * Math.cos(dec)) - Math.tan(L.lat * rad) * Math.tan(dec);
    var ha = Math.acos(clamp(c, -1, 1)) / rad, off = -now.getTimezoneOffset();
    return { sr: 720 - 4 * (L.lon + ha) - eq + off, ss: 720 - 4 * (L.lon - ha) - eq + off };
  }
  var now0 = new Date(), T = sunTimes(now0), DAY = T.ss - T.sr;
  function nowMin() {
    var d = new Date(); return d.getHours() * 60 + d.getMinutes() + d.getSeconds() / 60;
  }
  function fmt(min) {
    min = Math.round(((min % 1440) + 1440) % 1440); var h = Math.floor(min / 60), m = min % 60, ap = h >= 12 ? 'PM' : 'AM';
    return ((h + 11) % 12 + 1) + ':' + (m < 10 ? '0' : '') + m + ' ' + ap;
  }
  var SMIN = -0.3, SMAX = 1.3;                // scene range: the sun can be well below the horizon (night)
  var VMIN = -0.092, VMAX = 1.092;            // thumb range: the dotted overhang beyond sunrise / sunset (twilight)
  function pOf(min) { return clamp((min - T.sr) / DAY, SMIN, SMAX); }
  function minOf(p) { return T.sr + p * DAY; }
  function part(p) { return p < -0.02 ? 'before sunrise' : p < 0.2 ? 'early morning' : p < 0.45 ? 'morning' : p < 0.58 ? 'midday' : p < 0.8 ? 'afternoon' : p <= 1.02 ? 'evening' : 'after sunset'; }

  /* ---------- elements ---------- */
  var L = {
    day: $('.sky-day'), dawn: $('.sky-dawn'), dusk: $('.sky-dusk'), stars: $('.stars'), gWarm: $('.glow-warm'), gDay: $('.glow-day'),
    orb: $('.orb'), halo: $('.orb-halo'), core: $('.orb-core'), warmCore: $('.orb-warm'), moon: $('.moon'),
    shadow: $('.t-shadow'), gdim: $('.g-dim'), dim: $('.t-dim'), warm: $('.t-warm'), shL: $('.t-shl'), shR: $('.t-shr'), sunL: $('.t-sunl'), sunR: $('.t-sunr'), lights: $('.t-lights'), wrap: $('.temple-wrap')
  };
  var thumb = $('.h6-thumb'), rail = $('.h6-rail'), read = $('.h6-read-t'), nowBtn = $('.h6-now');
  $('[data-sr]').textContent = fmt(T.sr); $('[data-ss]').textContent = fmt(T.ss);

  /* ---------- geometry (measured only on resize) ---------- */
  var G = { W: 1, hz: 1, pk: 0, sceneH: 1, rw: 1, orb: 64 };
  function measure() {
    var r = root.getBoundingClientRect(), s = $('.h6-scene').getBoundingClientRect(), t = L.wrap.getBoundingClientRect(), tr = $('.h6-track').getBoundingClientRect();
    G.W = r.width; G.sceneH = s.height; G.rw = rail.getBoundingClientRect().width; G.orb = L.core.offsetWidth || 64;
    G.hz = t.bottom - r.top - t.height * 0.5;                // horizon: half-way up the temple; the sun rises/sets at the screen edges, behind the neighbours
    var trackBottom = tr.bottom - r.top, templeTop = t.top - r.top, band = templeTop - trackBottom;
    G.pk = trackBottom + Math.max(G.orb * 0.75, band / 2);   // noon: in the free sky between the slider and the spires
    G.pk = Math.min(G.pk, G.hz - G.orb);
    apply(P, true);
  }

  /* ---------- the scene: p -> layers ---------- */
  var P = 0.5, lastKey = '';
  function op(el, v) { el.style.opacity = v < 0.004 ? 0 : v > 0.996 ? 1 : v.toFixed(3); }
  function apply(p, force) {
    p = clamp(p, SMIN, SMAX); var key = p.toFixed(4) + '|' + G.W + '|' + G.hz; if (!force && key === lastKey) return; lastKey = key; P = p;
    var e = Math.sin(Math.PI * p), h = Math.max(0, e);
    var night = clamp(-e / 0.4, 0, 1), day = ss(0.12, 0.45, e), warm = Math.max(0, 1 - Math.abs(e - 0.03) / 0.42), side = ss(0.35, 0.65, p);
    var lit = ss(0.0, 0.3, e);                                // how strongly the sun lights the facade
    /* sky */
    op(L.day, day); op(L.dawn, warm * (1 - side)); op(L.dusk, warm * side);
    op(L.stars, night * 0.9 + warm * 0.18); op(L.gWarm, warm * 0.95); op(L.gDay, day * 0.5);
    /* sun + moon */
    var sx = G.W * (0.05 + 0.9 * clamp(p, 0, 1)), sy = e >= 0 ? G.hz - e * (G.hz - G.pk) : G.hz - e * G.sceneH * 0.9;
    L.orb.style.transform = 'translate3d(' + (sx - G.orb * 2).toFixed(1) + 'px,' + (sy - G.orb * 2).toFixed(1) + 'px,0)';
    var cool = ss(0.05, 0.5, e);
    op(L.orb, 1 - ss(-0.1, -0.32, e)); op(L.halo, 0.25 + 0.5 * day + 0.5 * warm); op(L.core, cool); op(L.warmCore, 1 - cool);
    L.moon.style.transform = 'translate3d(' + (G.W * (0.2 + 0.6 * (1 - side)) - 28).toFixed(1) + 'px,' + (G.pk + 20).toFixed(1) + 'px,0)'; op(L.moon, ss(0.15, 0.8, night));
    /* temple: shade, glow, night tint (all clipped to the temple outline by one CSS mask) */
    var dir = clamp((sx / G.W) * 2 - 1, -1, 1);                // -1 sun on the left … +1 sun on the right
    op(L.dim, 0.24 * (1 - lit) + 0.5 * night);
    op(L.warm, 0.3 * warm * (1 - night));
    var low = 1 + 0.35 * (1 - h);                              // a low sun rakes the facade harder
    op(L.shR, Math.min(1, Math.max(0, -dir) * 0.75 * low) * (1 - night)); op(L.shL, Math.min(1, Math.max(0, dir) * 0.75 * low) * (1 - night));
    op(L.sunL, Math.max(0, -dir) * (0.35 + 0.55 * lit) * (1 - night)); op(L.sunR, Math.max(0, dir) * (0.35 + 0.55 * lit) * (1 - night));
    op(L.lights, clamp((0.15 - e) / 0.3, 0, 1));
    op(L.gdim, clamp(0.78 * night + 0.4 * (1 - lit), 0, 0.85));
    /* cast shadow on the ground, falls away from the sun; length grows as the sun gets low */
    var k = 0.1 + 0.05 * h, s = -dir * Math.min(6, 1.4 / Math.max(h, 0.12));
    L.shadow.style.transform = 'matrix(1,0,' + (-s * k).toFixed(3) + ',' + (-k).toFixed(3) + ',0,0)';
    op(L.shadow, 0.55 * lit * (1 - night) * (0.5 + 0.5 * (1 - h)));
    /* slider */
    thumb.style.transform = 'translate3d(' + (G.rw * (0.12 + 0.76 * clamp(p, VMIN, VMAX))).toFixed(1) + 'px,0,0)';
    thumb.setAttribute('aria-valuenow', Math.round(minOf(p))); thumb.setAttribute('aria-valuetext', fmt(minOf(p)) + ', ' + part(p));
    root.setAttribute('data-phase', night > 0.6 ? 'night' : day > 0.6 ? 'day' : p < 0.5 ? 'dawn' : 'dusk');
    var lm = mode === 'now' ? nowMin() : minOf(p);
    read.textContent = (mode === 'now' ? 'Now · ' : 'Preview · ') + fmt(lm) + (night > 0.5 ? ' · night' : '');
  }

  /* ---------- modes: following real time, or previewing by dragging ---------- */
  var mode = 'now', raf = 0, target = 0;
  function tween(to, ms) {
    cancelAnimationFrame(raf); if (reduce || ms <= 0) { apply(to); return; }
    var from = P, t0 = performance.now();
    (function step(t) { var k = clamp((t - t0) / ms, 0, 1), e = 1 - Math.pow(1 - k, 3); apply(from + (to - from) * e); if (k < 1) raf = requestAnimationFrame(step); })(t0);
  }
  function goNow(animate) { mode = 'now'; nowBtn.hidden = true; apply(P, true); tween(pOf(nowMin()), animate ? 700 : 0); }
  function preview(p) { p = clamp(p, VMIN, VMAX); if (mode !== 'preview') { mode = 'preview'; nowBtn.hidden = false; } cancelAnimationFrame(raf); apply(p); }
  nowBtn.addEventListener('click', function () { goNow(true); });

  /* ---------- dragging (pointer events; the rail is touch-action: pan-y so the page still scrolls) ---------- */
  var dragging = false, pending = null, ticking = false;
  function pFromX(cx) { var r = rail.getBoundingClientRect(); return (((cx - r.left) / r.width) - 0.12) / 0.76; }
  function onMove(cx) { pending = pFromX(cx); if (!ticking) { ticking = true; requestAnimationFrame(function () { ticking = false; if (pending !== null) preview(pending); }); } }
  rail.addEventListener('pointerdown', function (ev) {
    if (ev.button > 0) return; dragging = true; thumb.classList.add('drag'); try { rail.setPointerCapture(ev.pointerId); } catch (e) {} thumb.focus({ preventScroll: true }); onMove(ev.clientX);
  });
  rail.addEventListener('pointermove', function (ev) { if (dragging) onMove(ev.clientX); });
  function end() { dragging = false; thumb.classList.remove('drag'); }
  rail.addEventListener('pointerup', end); rail.addEventListener('pointercancel', end); rail.addEventListener('lostpointercapture', end);
  thumb.addEventListener('keydown', function (ev) {
    var step = 5 / DAY, p = P, k = ev.key;
    if (k === 'ArrowRight' || k === 'ArrowUp') p += step; else if (k === 'ArrowLeft' || k === 'ArrowDown') p -= step;
    else if (k === 'PageUp') p += 30 / DAY; else if (k === 'PageDown') p -= 30 / DAY;
    else if (k === 'Home') p = 0; else if (k === 'End') p = 1; else if (k === 'Escape' || k === 'n' || k === 'N') { goNow(true); return; } else return;
    ev.preventDefault(); preview(p);
  });

  /* ---------- lifecycle: update every 30 s while visible and following real time ---------- */
  var timer = 0, visible = true;
  function schedule() { clearInterval(timer); if (visible && !document.hidden) timer = setInterval(function () { if (mode === 'now') apply(pOf(nowMin())); }, 30000); }
  if ('IntersectionObserver' in window) new IntersectionObserver(function (es) { visible = es[0].isIntersecting; schedule(); }).observe(root);
  document.addEventListener('visibilitychange', schedule);
  if ('ResizeObserver' in window) { var ro = new ResizeObserver(function () { measure(); }); ro.observe(root); ro.observe(rail); } else window.addEventListener('resize', measure);

  measure();
  // intro: the sun glides from sunrise to where it really is
  apply(VMIN * 0.6, true); goNow(true); schedule();
  window.__h6 = { apply: function (p) { preview(p); }, state: function () { return { p: P, T: T, mode: mode, sunrise: fmt(T.sr), sunset: fmt(T.ss), G: G }; }, now: goNow };
})();
