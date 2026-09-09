/* ============================================================
   tiktok.js — Carrusel de 6 videos de TikTok (@imeiclick)

   Enfoque: <iframe> directo a https://www.tiktok.com/embed/v2/<id>
   (verificado: HTTP 200, sin X-Frame-Options ni frame-ancestors).
   Evita embed.js de TikTok, que reemplaza el <blockquote> por un
   iframe de alto impredecible (layout shift) y obliga a una API no
   documentada (tiktokEmbed.render) mas un timeout de rescate.

   - Cero layout shift: la tarjeta reserva 9/16 en CSS, el iframe
     rellena esa caja. El alto no depende de terceros.
   - Lazy: el iframe se crea al acercarse al viewport
     (IntersectionObserver + rootMargin), no al cargar la pagina.
   - Fallback NO destructivo: si el iframe no dispara load en 6s,
     se muestra un enlace real por encima; si carga despues, el
     enlace se retira. Nunca se borra un embed que iba a montar.
   - Sin window.addEventListener('scroll'): solo observers.
   ============================================================ */

(function () {
	"use strict";

	// IDs reales de @imeiclick (verificados 2026-09-08 contra el
	// endpoint embed de TikTok). No inventar ni sustituir.
	var VIDEO_IDS = [
		"7683252903385173269",
		"7682581386271771924",
		"7682430154504899860",
		"7682134228284214548",
		"7682131762272570644",
		"7682127178368992263",
	];

	var PROFILE = "https://www.tiktok.com/@imeiclick";
	var LOAD_TIMEOUT_MS = 6000;

	var rail = document.getElementById("tiktok-rail");
	if (!rail) return;

	var reduce =
		window.matchMedia &&
		window.matchMedia("(prefers-reduced-motion: reduce)").matches;

	/* --- 1. Tarjetas: reservan su espacio desde el primer pintado --- */
	var cards = VIDEO_IDS.map(function (id, i) {
		var url = PROFILE + "/video/" + id;

		var card = document.createElement("article");
		card.className = "tiktok-card";
		card.setAttribute("role", "group");
		card.setAttribute(
			"aria-label",
			"Video " + (i + 1) + " de " + VIDEO_IDS.length + " de @imeiclick"
		);

		// Enlace de respaldo: existe desde el inicio (sirve sin JS de
		// terceros y para lectores de pantalla). Se oculta si el iframe carga.
		var link = document.createElement("a");
		link.className = "tiktok-link";
		link.href = url;
		link.target = "_blank";
		link.rel = "noopener noreferrer";
		link.innerHTML =
			'<span class="tiktok-link-mark" aria-hidden="true">&#9835;</span>' +
			'<span class="tiktok-link-name">@imeiclick</span>' +
			'<span class="tiktok-link-cta">Ver en TikTok</span>';

		card.appendChild(link);
		rail.appendChild(card);

		return { id: id, url: url, card: card, link: link, mounted: false };
	});

	/* --- 2. Monta el iframe cuando la tarjeta se acerca al viewport --- */
	function mount(entry) {
		if (entry.mounted) return;
		entry.mounted = true;

		var iframe = document.createElement("iframe");
		iframe.className = "tiktok-frame";
		iframe.src = "https://www.tiktok.com/embed/v2/" + entry.id;
		iframe.title = "Video de TikTok de @imeiclick";
		iframe.loading = "lazy";
		iframe.allow = "encrypted-media; picture-in-picture; fullscreen";
		// Sin setAttribute('allowfullscreen'): Edge avisa que 'allow'
		// tiene prioridad y el atributo legacy sobra.
		iframe.referrerPolicy = "strict-origin-when-cross-origin";

		var timer = setTimeout(function () {
			// No cargo a tiempo: el enlace de respaldo se queda visible.
			entry.card.classList.add("is-timeout");
		}, LOAD_TIMEOUT_MS);

		iframe.addEventListener("load", function () {
			clearTimeout(timer);
			// Solo aqui se oculta el respaldo: nunca se destruye nada.
			entry.card.classList.remove("is-timeout");
			entry.card.classList.add("is-loaded");
		});

		entry.card.appendChild(iframe);
	}

	var io = new IntersectionObserver(
		function (entries) {
			entries.forEach(function (e) {
				if (!e.isIntersecting) return;
				var entry = cards.filter(function (c) {
					return c.card === e.target;
				})[0];
				if (entry) mount(entry);
				io.unobserve(e.target);
			});
		},
		{ root: null, rootMargin: "300px 0px" }
	);

	cards.forEach(function (c) {
		io.observe(c.card);
	});

	/* --- 3. Flechas: solo si el carril desborda --- */
	var section = rail.closest(".tiktok");
	if (!section) return;

	function makeArrow(dir, label, glyph) {
		var b = document.createElement("button");
		b.type = "button";
		b.className = "tiktok-arrow tiktok-arrow--" + dir;
		b.setAttribute("aria-label", label);
		b.setAttribute("aria-controls", "tiktok-rail");
		b.innerHTML = '<span aria-hidden="true">' + glyph + "</span>";
		b.addEventListener("click", function () {
			var step = cards[0].card.offsetWidth + 16; // ancho + gap
			rail.scrollBy({
				left: (dir === "prev" ? -1 : 1) * step,
				behavior: reduce ? "auto" : "smooth",
			});
		});
		return b;
	}

	section.appendChild(makeArrow("prev", "Ver video anterior", "&#8249;"));
	section.appendChild(makeArrow("next", "Ver video siguiente", "&#8250;"));
})();
