#!/usr/bin/env python3
"""build.py — genera site/index.html desde content/copy.json.

Una sola fuente de verdad para el texto: si cambia copy.json, se
regenera el HTML. Sin motor de plantillas (no hace falta para una
pagina): f-strings de stdlib.

Uso: python3 build.py
"""
import html
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, "site")

with open(os.path.join(SITE, "content", "copy.json"), encoding="utf-8") as fh:
    C = json.load(fh)

# Contacto real del vendedor. WhatsApp de imeiclick.
# WhatsApp real de imeiclick: +54 9 11 6665-8740 (mismo de imeiclick.com).
WA = "https://wa.me/5491166658740?text=" \
     "Hola%2C%20quiero%20m%C3%A1s%20informaci%C3%B3n%20sobre%20la%20PICO%202%20Ultra"
TIKTOK = "https://www.tiktok.com/@imeiclick"
IMEICLICK = "https://imeiclick.com/"
SVC_COUNT = "210"

IPHONES = ["iPhone XR", "iPhone XS", "iPhone XS Max", "iPhone 11",
           "iPhone 11 Pro", "iPhone 11 Pro Max", "iPhone SE 2"]
IPADS = ["iPad mini 5", "iPad Air 3", "iPad (8.ª generación)",
         "iPad (9.ª generación)"]

# Solo 2 fotos del producto (decision del cliente 2026-09-08): pico2 y pico2_1.
FRAME_IMG = [
    ("pico2", "Caja de ingeniería PICO 2 Ultra conectada por su puerto Type-C"),
    ("pico2_1", "Vista de la placa y los conectores de la PICO 2 Ultra"),
]


def e(s):
    return html.escape(str(s), quote=True)


def picture(base, alt, cls="", eager=False, sizes="(max-width: 900px) 92vw, 520px"):
    """<picture> con WebP + JPEG y variante pequeña. Espacio reservado.

    Las fotos van recortadas a 4:3 (1200x900): el original 3:4 traia el
    tercio superior vacio y el producto se veia alargado.
    """
    loading = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    return f"""<picture>
					<source type="image/webp" srcset="assets/img/{base}-448.webp 600w, assets/img/{base}.webp 1200w" sizes="{sizes}">
					<img src="assets/img/{base}.png" srcset="assets/img/{base}-448.png 600w, assets/img/{base}.png 800w" sizes="{sizes}" alt="{e(alt)}" class="{cls}" width="1200" height="900" {loading}>
				</picture>"""


# Aviso legal: una seccion por item, con lista opcional. Escapado estricto.
def _legal_section(s):
    items = "".join(f"<li>{e(i)}</li>" for i in s.get("list") or [])
    ul = f"\n\t\t\t\t\t\t<ul class=\"legal-list\">{items}</ul>" if items else ""
    return (f"\t\t\t\t\t<h3 class=\"legal-h\">{e(s['h'])}</h3>\n"
            f"\t\t\t\t\t<p>{e(s['p'])}</p>{ul}")

legal_sections = "\n".join(_legal_section(s) for s in C["legal"]["sections"])


frames = "\n".join(
    f"""				<div class="cinema-frame" data-frame="{i}">{picture(img, alt)}</div>"""
    for i, (img, alt) in enumerate(FRAME_IMG)
)

captions = "\n".join(
    f"""				<div class="cinema-caption" data-frame="{i}">
					<h3 class="h2">{e(f['title'])}</h3>
					<p class="body">{e(f['body'])}</p>
				</div>"""
    for i, f in enumerate(C["cinema"]["frames"])
)

# 4 celdas para 4 items: la primera lleva imagen (variacion visual real)
gi = C["grid"]["items"]
cells = []
for i, item in enumerate(gi):
    if i == 0:
        cells.append(f"""				<div class="cell cell-media" data-reveal>
					{picture('pico2_1', 'Placa y conectores de la caja PICO 2 Ultra')}
					<h3 class="h3">{e(item['title'])}</h3>
					<p class="body-tight">{e(item['body'])}</p>
				</div>""")
    else:
        tint = " cell-tint" if i == 1 else ""
        cells.append(f"""				<div class="cell{tint}" data-reveal data-reveal-delay="{i * 70}">
					<h3 class="h3">{e(item['title'])}</h3>
					<p class="body-tight">{e(item['body'])}</p>
				</div>""")
cells = "\n".join(cells)

iphone_chips = "\n".join(f"						<li>{e(m)}</li>" for m in IPHONES)
ipad_chips = "\n".join(f"						<li>{e(m)}</li>" for m in IPADS)

DOC = f"""<!doctype html>
<html lang="es">
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<title>{e(C['meta']['title'])}</title>
	<meta name="description" content="{e(C['meta']['description'])}">
	<meta name="theme-color" content="#08090c">
	<link rel="icon" href="favicon.ico" sizes="32x32">
	<link rel="canonical" href="https://pico2ultra.imeiclick.com/">

	<meta property="og:type" content="product">
	<meta property="og:url" content="https://pico2ultra.imeiclick.com/">
	<meta property="og:title" content="{e(C['meta']['og_title'])}">
	<meta property="og:description" content="{e(C['meta']['og_description'])}">
	<meta property="og:image" content="https://pico2ultra.imeiclick.com/assets/img/pico2.png">
	<meta property="og:locale" content="es_PE">
	<meta name="twitter:card" content="summary_large_image">

	<link rel="preload" as="image" href="assets/img/pico2.webp" type="image/webp">
	<link rel="preload" as="font" type="font/woff2" href="assets/fonts/Geist-Variable.woff2" crossorigin>
	<link rel="stylesheet" href="assets/base.css">
	<link rel="stylesheet" href="assets/motion.css">
	<link rel="stylesheet" href="assets/tiktok.css">

	<script type="application/ld+json">
	{{
		"@context": "https://schema.org",
		"@type": "Product",
		"name": "Caja de ingeniería PICO 2 Ultra",
		"description": {json.dumps(C['meta']['description'], ensure_ascii=False)},
		"image": "https://pico2ultra.imeiclick.com/assets/img/pico2.png",
		"brand": {{"@type": "Brand", "name": "PICO"}},
		"category": "Herramientas de reparación de móviles"
	}}
	</script>
</head>
<body>
	<a class="skip" href="#main">Saltar al contenido</a>

	<header class="nav">
		<div class="wrap nav-inner">
			<a class="nav-brand" href="#main">PICO 2 <span>Ultra</span></a>
			<div class="nav-right">
				<a class="nav-imei" href="https://imeiclick.com/" target="_blank" rel="noopener">
					<span class="nav-imei-dot" aria-hidden="true">
						<span class="nav-imei-dot-ping"></span>
						<span class="nav-imei-dot-core"></span>
					</span>
					imeiclick.com
				</a>
				<a class="cta" href="{WA}" target="_blank" rel="noopener">{e(C['hero']['cta'])}</a>
			</div>
		</div>
	</header>

	<main id="main">

		<!-- 1. Hero -->
		<section class="hero">
			<div class="wrap hero-grid">
				<div class="hero-copy">
					<p class="eyebrow">{e(C['hero']['eyebrow'])}</p>
					<div class="ios-badge" data-ios-badge role="note">
						<span class="ios-badge-old">{e(C['hero']['ios_badge']['from'])}</span>
						<svg class="ios-badge-arrow" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M5 12h14M13 6l6 6-6 6"/></svg>
						<span class="ios-badge-new">{e(C['hero']['ios_badge']['to'])}</span>
					</div>
					<h1 class="display">{e(C['hero']['h1'])}</h1>
					<p class="body">{e(C['hero']['sub'])}</p>
					<div class="cta-row">
						<a class="cta" href="{WA}" target="_blank" rel="noopener">{e(C['hero']['cta'])}</a>
						<span class="cta-note">{e(C['hero']['cta_note'])}</span>
					</div>
				</div>
				<div class="hero-media">
					{picture('pico2', 'Caja de ingeniería PICO 2 Ultra vista de frente', cls='hero-img', eager=True)}
				</div>
			</div>
		</section>

		<!-- 2. Cinema: dropscroll, el efecto principal -->
		<section class="cinema" aria-label="Cómo trabaja la PICO 2 Ultra">
			<div class="cinema-stage">
				<div class="cinema-media">
{frames}
				</div>
				<div class="wrap cinema-text">
{captions}
				</div>
			</div>
		</section>

		<!-- 3. Un click: DFU / PWND -->
		<section class="pad-y hairline-top">
			<div class="wrap oneclick-grid">
				<div>
					<div class="click-stat">
						<span class="click-num" data-countup="1">1</span>
						<span class="click-word">click, no más</span>
					</div>
					<h2 class="h2" data-reveal>{e(C['oneclick']['title'])}</h2>
					<p class="body" data-reveal data-reveal-delay="60" style="margin-top:1rem">{e(C['oneclick']['body'])}</p>
				</div>
				<div class="mode-pair">
					<div class="mode" data-reveal>
						<span class="mode-label">{e(C['oneclick']['dfu']['label'])}</span>
						<p class="body-tight">{e(C['oneclick']['dfu']['body'])}</p>
					</div>
					<div class="mode" data-reveal data-reveal-delay="90">
						<span class="mode-label">{e(C['oneclick']['pwnd']['label'])}</span>
						<p class="body-tight">{e(C['oneclick']['pwnd']['body'])}</p>
					</div>
				</div>
			</div>
		</section>

		<!-- 4. Chip -->
		<section class="chip pad-y">
			<div class="wrap">
				<p class="eyebrow">{e(C['chip']['eyebrow'])}</p>
				<p class="chip-stat"><span data-countup="2354">2354</span>A</p>
				<p class="chip-stat-label">{e(C['chip']['stat_label'])}</p>
				<p class="body" data-reveal>{e(C['chip']['body'])}</p>
			</div>
		</section>

		<!-- 5. Bento: 4 items, 4 celdas -->
		<section class="pad-y">
			<div class="wrap">
				<h2 class="h2" data-reveal>{e(C['grid']['title'])}</h2>
				<div class="bento">
{cells}
				</div>
			</div>
		</section>

		<!-- 6. Compatibilidad -->
		<section class="pad-y hairline-top">
			<div class="wrap">
				<p class="eyebrow">{e(C['compat']['eyebrow'])}</p>
				<h2 class="h2" data-reveal>{e(C['compat']['title'])}</h2>
				<div class="compat-cols">
					<div class="compat-group" data-reveal>
						<h3>iPhone</h3>
						<ul class="chips">
{iphone_chips}
						</ul>
					</div>
					<div class="compat-group" data-reveal data-reveal-delay="80">
						<h3>iPad</h3>
						<ul class="chips">
{ipad_chips}
						</ul>
					</div>
				</div>
				<p class="compat-note">{e(C['compat']['note'])}</p>
			</div>
		</section>

		<!-- 7. TikTok: los 6 videos reales de @imeiclick -->
		<section class="tiktok pad-y hairline-top" aria-label="Videos de @imeiclick en TikTok">
			<div class="wrap">
				<h2 class="h2" data-reveal>{e(C['tiktok']['title'])}</h2>
				<p class="body" data-reveal data-reveal-delay="60" style="margin-top:1rem">{e(C['tiktok']['body'])}</p>
			</div>
			<div class="wrap">
				<div class="tiktok-rail" id="tiktok-rail"></div>
			</div>
		</section>

		<!-- 8. Cierre -->
		<section class="close pad-y hairline-top">
			<div class="wrap">
				<h2 class="h2" data-reveal>{e(C['close']['title'])}</h2>
				<p class="body" data-reveal data-reveal-delay="60">{e(C['close']['body'])}</p>
				<div class="cta-row">
					<a class="cta" href="{WA}" target="_blank" rel="noopener">{e(C['close']['cta'])}</a>
					<a class="cta cta-ghost" href="{TIKTOK}" target="_blank" rel="noopener">Ver @imeiclick en TikTok</a>
				</div>
			</div>
		</section>

		<!-- 9. Cross-promo imeiclick: los colores de la pagina principal
		     de imeiclick.com (cyan->emerald), enlace a la verificacion gratis.
		     Sutil: mismo fondo oscuro de pico2ultra, solo el bloque destaca. -->
		<section class="pad-y">
			<div class="wrap">
				<div class="imei-promo" data-reveal>
					<div class="imei-promo-grid">
						<div>
							<span class="imei-promo-badge">
								<svg class="h-3.5 w-3.5" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>
								Del mismo equipo de imeiclick
							</span>
							<h2 class="h2">Verifica cualquier IMEI,<br><span class="imei-promo-grad">sin pagar nada</span></h2>
							<p class="body">¿Compraste el equipo o lo vas a comprar? Consulta su estado real antes de cerrar trato.</p>
							<a class="cta imei-promo-cta" href="https://imeiclick.com/free" target="_blank" rel="noopener">Verificar gratis ahora</a>
						</div>
						<ul class="imei-promo-list">
							<li>Modelo y marca al instante, sin coste</li>
							<li>Sin registro ni tarjeta, solo el IMEI</li>
							<li>Más de {SVC_COUNT}+ servicios premium al crear cuenta</li>
						</ul>
					</div>
				</div>
			</div>
		</section>
	</main>

	<footer>
		<div class="wrap foot">
			<span>Bypass iCloud con un click, sin cambiar cables.</span>
			<div class="foot-links">
				<a href="https://imeiclick.com/" target="_blank" rel="noopener">imeiclick.com</a>
				<a href="https://www.tiktok.com/@imeiclick" target="_blank" rel="noopener">@imeiclick</a>
			</div>
		</div>
		<div class="wrap">
			<details class="legal">
				<summary class="legal-summary">{e(C['legal']['title'])}</summary>
				<div class="legal-body">
					<p class="legal-sub">{e(C['legal']['subtitle'])}</p>
{legal_sections}
					<p class="legal-warn">{e(C['legal']['warning'])}</p>
				</div>
			</details>
		</div>
	</footer>

	<script src="assets/scroll.js" defer></script>
	<script src="assets/tiktok.js" defer></script>
</body>
</html>
"""

out = os.path.join(SITE, "index.html")
with open(out, "w", encoding="utf-8") as fh:
    fh.write(DOC)
print(f"escrito {out} ({len(DOC.encode('utf-8'))} bytes)")
