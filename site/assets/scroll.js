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
  /* Si el navegador soporta animation-timeline: view(), el crossfade lo corre
     el compositor desde CSS y este loop sobra: se salta por completo. */
  var nativeCinema = window.CSS && CSS.supports && CSS.supports('animation-timeline: view()');
  if (cinema && frames.length && !reduceMotion && !nativeCinema) {
    gatedLoop(cinema, function () {
      var rect = cinema.getBoundingClientRect();
      var stageH = stage ? stage.offsetHeight : window.innerHeight;
      var total = rect.height - stageH; /* recorrido scrolleable del pin */
      if (total <= 0) return;

      var p = clamp(-rect.top / total, 0, 1); /* 0..1 a lo largo del pin */

      /* smoothstep sobre todo el recorrido: entrada y salida sin escalon, que
         es lo que hace que el cruce se sienta suave. La velocidad la da la
         altura del wrapper (.cinema), no esta curva. */
      var n = frames.length;
      for (var i = 0; i < n; i++) {
        var c = n === 1 ? 0 : i / (n - 1);
        var w = n === 1 ? 1 : 1 / (n - 1);
        var t = clamp(1 - Math.abs(p - c) / w, 0, 1);
        var o = t * t * (3 - 2 * t); /* smoothstep */
        frames[i].style.opacity = o.toFixed(3);
        /* parallax minimo: el frame entrante se asienta, no salta. */
        frames[i].style.transform = "scale(" + (1.035 - 0.035 * o).toFixed(4) + ")";
        if (captions[i]) {
          captions[i].style.opacity = o.toFixed(3);
          captions[i].style.transform = "translateY(" + ((1 - o) * 10).toFixed(1) + "px)";
        }
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

/* ---------- 6. Aviso legal: al abrir, traer el contenido a la vista ---------- */
/* El <details> esta en el footer: al desplegarlo el texto nace por debajo del
   borde inferior y parece que "no funciona". Al abrir, se ancla la cabecera
   arriba y se hace scroll para que las primeras lineas queden a la vista. */
(function () {
  var legal = document.querySelector('details.legal');
  if (!legal) return;
  legal.addEventListener('toggle', function () {
    if (!legal.open) return;
    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var top = legal.getBoundingClientRect().top + window.scrollY - 16;
    window.scrollTo({ top: top, behavior: reduce ? 'auto' : 'smooth' });
  });
})();
