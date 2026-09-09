/* ============================================================
   scroll.js — motor de animación scroll-driven estilo Apple
   Landing "Caja de ingeniería PICO 2 Ultra".

   Sin listeners de scroll. Todo va por IntersectionObserver +
   requestAnimationFrame. Cada loop se enciende/apaga con un
   observer para no gastar batería cuando la sección no se ve.

   Alternativa nativa: CSS animation-timeline: scroll()/view().
   Se usa JS por fiabilidad cross-browser y porque data-reveal-delay
   (ms) no mapea limpio a timelines de scroll.
   ============================================================ */

(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var isMobile = window.matchMedia('(max-width: 767px)').matches;

  /* Marca el documento: sin JS, [data-reveal] queda visible (no se oculta). */
  document.documentElement.classList.add('js-anim');

  function clamp(v, min, max) { return Math.min(max, Math.max(min, v)); }

  /* Loop rAF encendido/apagado por IntersectionObserver.
     onFrame corre cada frame SOLO mientras el elemento intersecta. */
  function gatedLoop(el, onFrame) {
    var visible = false;
    var running = false;
    var io = new IntersectionObserver(function (entries) {
      visible = entries[0].isIntersecting;
      if (visible) start(); else stop();
    }, { threshold: 0 });
    io.observe(el);

    function tick() {
      running = false;
      if (!visible) return;
      onFrame();
      if (visible) { running = true; requestAnimationFrame(tick); }
    }
    function start() { if (!running) { running = true; requestAnimationFrame(tick); } }
    function stop() { running = false; }

    return { disconnect: function () { io.disconnect(); stop(); } };
  }

  /* ---------- 1. Hero: parallax sutil de la imagen ----------
     El parallax va en una variable CSS sobre el WRAPPER, no en
     .hero-img: esa imagen tiene la animación de entrada (hero-in)
     y escribirle transform inline la mataría. */
  var hero = document.querySelector('.hero');
  var heroMedia = document.querySelector('.hero-media');
  if (hero && heroMedia && !reduceMotion) {
    gatedLoop(hero, function () {
      var y = hero.getBoundingClientRect().top * -0.15;
      if (isMobile) y *= 0.4; /* móvil: parallax reducido */
      heroMedia.style.setProperty('--parallax', y.toFixed(2) + 'px');
    });
  }

  /* ---------- 2. Cinema dropscroll: crossfade 0 -> 1 -> 2 ---------- */
  var cinema = document.querySelector('.cinema');
  var stage = document.querySelector('.cinema-stage');
  var frames = document.querySelectorAll('.cinema-frame');
  var captions = document.querySelectorAll('.cinema-caption');
  if (cinema && frames.length && !reduceMotion) {
    gatedLoop(cinema, function () {
      var rect = cinema.getBoundingClientRect();
      var stageH = stage ? stage.offsetHeight : window.innerHeight;
      var total = rect.height - stageH; /* recorrido scrolleable del pin */
      if (total <= 0) return;

      var p = clamp(-rect.top / total, 0, 1); /* 0..1 a lo largo del pin */

      /* crossfade triangular: cada frame i tiene una ventana centrada
         en c = i/(n-1) y ancho w = 1/(n-1). opacity = 1 - |p-c|/w. */
      var n = frames.length;
      for (var i = 0; i < n; i++) {
        var c = n === 1 ? 0 : i / (n - 1);
        var w = n === 1 ? 1 : 1 / (n - 1);
        var o = clamp(1 - Math.abs(p - c) / w, 0, 1);
        frames[i].style.opacity = o;
        if (captions[i]) captions[i].style.opacity = o;
      }
    });
  }

  /* ---------- 3. Reveal escalonado ---------- */
  var reveals = document.querySelectorAll('[data-reveal]');
  if (reveals.length) {
    var rio = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        var delay = parseInt(el.dataset.revealDelay, 10) || 0;
        if (delay) el.style.transitionDelay = delay + 'ms';
        el.classList.add('is-revealed');
        rio.unobserve(el);
      });
    }, { threshold: 0.15, rootMargin: '0px 0px -10% 0px' });
    reveals.forEach(function (r) { rio.observe(r); });
  }

  /* ---------- 4. Count-up ---------- */
  var counters = document.querySelectorAll('[data-countup]');
  if (counters.length) {
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        cio.unobserve(el); /* una sola vez */
        var target = parseInt(el.dataset.countup, 10);
        if (isNaN(target)) return;
        if (reduceMotion) { el.textContent = String(target); return; }
        animateCount(el, target);
      });
    }, { threshold: 0.5 });
    counters.forEach(function (c) { cio.observe(c); });
  }

  function animateCount(el, target) {
    var dur = 800; /* ms */
    var start = null;
    function step(ts) {
      if (start === null) start = ts;
      var t = clamp((ts - start) / dur, 0, 1);
      var eased = 1 - Math.pow(1 - t, 3); /* easeOutCubic */
      el.textContent = String(Math.round(target * eased));
      if (t < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
})();
