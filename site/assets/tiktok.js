/* ============================================================
   tiktok.js — Carrusel de videos de TikTok (@imeiclick)

   Enfoque click-to-play: la pagina NO carga ningun iframe de TikTok
   hasta que el usuario toca un video. Motivo (2026-09-11): montar 9
   iframes a la vez disparaba el rate-limit de TikTok ("overload-protect"
   / "video no disponible"). Un iframe a la vez, a pedido, elimina el
   problema de raiz.

   - Poster local (assets/img/tiktok/<id>.jpg): cero peticiones a TikTok
     al cargar; cero layout shift (la caja 9/16 ya esta reservada en CSS).
   - Click en el poster -> se monta el iframe de ESE video y se desmonta
     cualquier otro. Solo uno vive a la vez.
   - Si el iframe no carga en 6s, el enlace real a TikTok se queda visible.
   - Sin window.addEventListener('scroll'): solo observers.
   ============================================================ */

(function () {
	"use strict";

	// IDs reales de @imeiclick. Verificados 2026-09-11 contra el
	// endpoint embed de TikTok (HTTP 200). No inventar ni sustituir.
	// Orden: mas reciente primero. Un id muerto (400) se descarta.
	var VIDEOS = [
		{ id: "7684054875650510100", title: "Nueva PICO 2 Ultra: sacar iOS a un dispositivo Apple" },
		{ id: "7683691176272104724", title: "PICO 2 Ultra en accion" },
		{ id: "7683630006991457557", title: "Ultimas unidades hasta agotar stock" },
		{ id: "7683252903385173269", title: "Bypass con UnlockTool usando la PICO 2 Ultra" },
		{ id: "7682581386271771924", title: "Demo real de la PICO 2 Ultra" },
		{ id: "7682430154504899860", title: "DFU en un click" },
		{ id: "7682134228284214548", title: "PICO 2 Ultra en Argentina" },
		{ id: "7682131762272570644", title: "Modo DFU y PWND en un solo click" },
	];

	var PROFILE = "https://www.tiktok.com/@imeiclick";
	var POSTERS = "assets/img/tiktok/";
	var LOAD_TIMEOUT_MS = 6000;

	var rail = document.getElementById("tiktok-rail");
	if (!rail) return;

	var reduce =
		window.matchMedia &&
		window.matchMedia("(prefers-reduced-motion: reduce)").matches;

	var active = null; // el unico video montado en iframe

	/* --- 1. Tarjetas con poster local y boton play --- */
	var cards = VIDEOS.map(function (v, i) {
		var url = PROFILE + "/video/" + v.id;

		var card = document.createElement("article");
		card.className = "tiktok-card";
		card.setAttribute("role", "group");
		card.setAttribute(
			"aria-label",
			"Video " + (i + 1) + " de " + VIDEOS.length + ": " + v.title
		);

		// Boton play: cubre el poster. Al tocar, monta el iframe.
		var play = document.createElement("button");
		play.type = "button";
		play.className = "tiktok-play";
		play.setAttribute("aria-label", "Reproducir: " + v.title);

		var img = document.createElement("img");
		img.className = "tiktok-poster";
		img.src = POSTERS + v.id + ".jpg";
		img.alt = "";
		img.width = 325;
		img.height = 578;
		img.loading = i < 3 ? "eager" : "lazy";
		img.decoding = "async";

		var badge = document.createElement("span");
		badge.className = "tiktok-play-badge";
		badge.setAttribute("aria-hidden", "true");
		badge.innerHTML =
			'<svg viewBox="0 0 24 24" width="26" height="26" fill="currentColor">' +
			'<path d="M8 5v14l11-7z"/></svg>';

		var cap = document.createElement("span");
		cap.className = "tiktok-play-title";
		cap.textContent = v.title;

		play.appendChild(img);
		play.appendChild(badge);
		play.appendChild(cap);
		card.appendChild(play);

		// Enlace real (respaldo + accesible): siempre presente, bajo el poster.
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

		var entry = { id: v.id, url: url, card: card, play: play, link: link, mounted: false };
		play.addEventListener("click", function () {
			toggle(entry);
		});
		return entry;
	});

	/* --- 2. Monta/desmonta el iframe (solo uno a la vez) --- */
	function unmount(entry) {
		if (!entry || !entry.mounted) return;
		var f = entry.card.querySelector(".tiktok-frame");
		if (f) f.remove();
		entry.mounted = false;
		entry.card.classList.remove("is-loaded", "is-timeout", "is-playing");
	}

	function mount(entry) {
		// Solo un iframe vivo: apaga el anterior antes de encender este.
		if (active && active !== entry) unmount(active);

		if (entry.mounted) {
			// Segundo click sobre el mismo: se cierra.
			unmount(entry);
			active = null;
			return;
		}
		entry.mounted = true;
		active = entry;

		var iframe = document.createElement("iframe");
		iframe.className = "tiktok-frame";
		iframe.src = "https://www.tiktok.com/embed/v2/" + entry.id;
		iframe.title = "Video de TikTok de @imeiclick";
		iframe.allow = "encrypted-media; picture-in-picture; fullscreen";
		iframe.referrerPolicy = "strict-origin-when-cross-origin";

		var timer = setTimeout(function () {
			entry.card.classList.add("is-timeout");
		}, LOAD_TIMEOUT_MS);

		iframe.addEventListener("load", function () {
			clearTimeout(timer);
			entry.card.classList.remove("is-timeout");
			entry.card.classList.add("is-loaded");
		});

		entry.card.classList.add("is-playing");
		entry.card.appendChild(iframe);
	}

	function toggle(entry) {
		mount(entry);
	}

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
