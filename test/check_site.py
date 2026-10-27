#!/usr/bin/env python3
"""F1.1 + F1.2 + F1.3 — checks estaticos del landing pico2ultra.

Se ejecutan ANTES de que exista el HTML (deben fallar en RED) y luego
hasta verde. Sin frameworks: assert + salida legible.

Uso: python3 test/check_site.py [ruta_index.html]
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "site", "index.html")
SITE = os.path.dirname(INDEX)


def strip_comments(src):
    """Quita comentarios /* */ y // para no dar falsos positivos:
    un comentario que dice 'sin #000000' no es un uso de #000000."""
    src = re.sub(r"/\*.*?\*/", " ", src, flags=re.S)
    src = re.sub(r"^\s*//.*$", " ", src, flags=re.M)
    return src


def read(*parts):
    """Lee un asset del sitio; '' si no existe."""
    p = os.path.join(SITE, *parts)
    return open(p, encoding="utf-8").read() if os.path.exists(p) else ""

# --- datos de verdad (del brief del usuario, no inventados) -----------------
TIKTOK_IDS = [
    "7684054875650510100",
    "7683691176272104724",
    "7683630006991457557",
    "7683252903385173269",
    "7682581386271771924",
    "7682430154504899860",
    "7682134228284214548",
    "7682131762272570644",
]

IPHONES = [
    "iPhone XR", "iPhone XS", "iPhone XS Max", "iPhone 11",
    "iPhone 11 Pro", "iPhone 11 Pro Max", "iPhone SE 2",
]
IPADS = ["iPad mini 5", "iPad Air 3", "iPad (8", "iPad (9"]

FEATURES = ["DCSD", "DFU", "PWND", "Type", "RP2354A"]

# tokens de color esperados (paleta medida de las fotos, ver PLAN.md §1)
BG = "#08090c"
ACCENT = "#4fd6e8"

failures = []
passes = []


def check(name, cond, detail=""):
    if cond:
        passes.append(name)
    else:
        failures.append(f"{name}{(' :: ' + detail) if detail else ''}")


def visible_text(html):
    """Texto que ve el usuario: sin <script>, <style> ni comentarios."""
    h = re.sub(r"<script\b.*?</script>", " ", html, flags=re.S | re.I)
    h = re.sub(r"<style\b.*?</style>", " ", h, flags=re.S | re.I)
    h = re.sub(r"<!--.*?-->", " ", h, flags=re.S)
    return h


def srgb_lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hexcolor):
    hexcolor = hexcolor.lstrip("#")
    if len(hexcolor) == 3:
        hexcolor = "".join(ch * 2 for ch in hexcolor)
    r, g, b = (int(hexcolor[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * srgb_lin(r) + 0.7152 * srgb_lin(g) + 0.0722 * srgb_lin(b)


def contrast(fg, bg):
    a, b = luminance(fg), luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


# --- F1.1 contenido --------------------------------------------------------
def test_content(html, text, bundle):
    for vid in TIKTOK_IDS:
        check(f"[content] video TikTok {vid} presente", vid in bundle)
    check("[content] exactamente 8 IDs de TikTok",
          len({v for v in TIKTOK_IDS if v in bundle}) == len(TIKTOK_IDS))
    check("[content] ningun ID de TikTok ajeno",
          not [i for i in set(re.findall(r"tiktok\.com/@[\w.]+/video/(\d{15,})", bundle))
               if i not in TIKTOK_IDS],
          "hay IDs que no son de @imeiclick")
    check("[content] cuenta @imeiclick referenciada", "@imeiclick" in bundle)
    # click-to-play: no se monta ningun iframe hasta que el usuario toca.
    # Se comprueba SOLO tiktok.js (scroll.js usa IntersectionObserver para
    # las animaciones de reveal, no para iframes).
    tiktok_js = strip_comments(read("assets", "tiktok.js"))
    check("[content] tiktok.js es click-to-play (sin autoplay de iframes)",
          "IntersectionObserver" not in tiktok_js and "tiktok-play" in tiktok_js,
          "vuelve a montar iframes automaticamente")
    check("[content] posters locales referenciados",
          "assets/img/tiktok/" in tiktok_js)

    for m in IPHONES:
        check(f"[content] modelo {m}", m in text)
    for m in IPADS:
        check(f"[content] modelo {m}...", m in text)
    for f in FEATURES:
        check(f"[content] caracteristica {f}", f in text)
    check("[content] nombre del producto", "PICO 2 Ultra" in text)
    check("[content] CTA unico WhatsApp", text.count("Más información por WhatsApp") >= 1)
    # numero real del vendedor (+54 9 11 6665-8740). Un numero equivocado
    # manda los pedidos a la nada: se verifica literal.
    was = set(re.findall(r"wa\.me/(\d+)", bundle))
    check("[content] WhatsApp apunta al numero real",
          was == {"5491166658740"},
          f"encontrados: {was or 'ninguno'}")
    # branding cruzado: la landing lleva a imeiclick.com (header y footer)
    check("[content] enlace a imeiclick.com en header",
          re.search(r'<header[\s\S]*?imeiclick\.com', html) is not None)
    check("[content] enlace a imeiclick.com en footer",
          re.search(r'<footer[\s\S]*?imeiclick\.com', html) is not None)
    check("[content] nav-imei es pill con punto",
          re.search(r'nav-imei[\s\S]*?nav-imei-dot[\s\S]*?imeiclick\.com', html) is not None)
    check("[content] favicon referenciado", "favicon.ico" in html)
    # badge iOS: el gancho comercial. from tachado -> flecha -> to destacado.
    check("[content] badge iOS 26 -> 27 en hero",
          re.search(r'ios-badge[\s\S]*?ios-badge-old[\s\S]*?ios-badge-arrow[\s\S]*?ios-badge-new', html)
          is not None)
    check("[content] badge dice iOS 27 soportado", "iOS 27" in html)
    # aviso legal: 3 secciones + lista de 3 + bloque IMPORTANTE, cerrado
    check("[content] aviso legal en footer",
          re.search(r'<footer[\s\S]*?class="legal"[\s\S]*?legal-summary', html) is not None)
    check("[content] aviso legal tiene las 3 secciones",
          html.count('class="legal-h"') == 3)
    check("[content] aviso legal cita la Ley 25.891", "25.891" in html)
    check("[content] aviso legal lista los 3 puntos",
          len(re.search(r'class="legal-list">([\s\S]*?)</ul>', html).group(1).split("<li>")) - 1 == 3)
    check("[content] aviso legal bloque IMPORTANTE", 'class="legal-warn"' in html)
    check("[content] aviso legal cerrado por defecto",
          not re.search(r'<details[^>]*\sopen', html))
    # compatibilidad iOS 27: seccion propia y el badge del hero lleva a ella
    check("[content] seccion compatibilidad con id", 'id="compatibilidad"' in html)
    check("[content] badge iOS enlaza a compatibilidad",
          re.search(r'<a[^>]*class="ios-badge"[^>]*href="#compatibilidad"', html) is not None)
    check("[content] compatibilidad tiene 3 tarjetas", html.count('class="compat-card"') == 3)
    check("[content] compatibilidad lista iPhone e iPad",
          ">iPhone<" in html and ">iPad<" in html)
    check("[content] logo Apple es el path oficial (814x1000)",
          'viewBox="0 0 814 1000"' in html)
    # novedades: tarjetas que llevan a WhatsApp
    check("[content] seccion novedades con id", 'id="novedades"' in html)
    check("[content] novedades tiene 2 tarjetas",
          html.count('class="novedad-card"') == 2)
    check("[content] tarjetas de novedades abren WhatsApp",
          html.count('class="novedad-card" href="https://wa.me/') == 2)
    check("[content] novedades usa los dos banners",
          "novedad-wide.webp" in html and "novedad-tall.webp" in html)
    # cross-promo: bloque con los colores de imeiclick.com y CTA a /free
    # (el href imeiclick.com/free va antes del texto del CTA en la misma linea)
    check("[content] cross-promo imeiclick",
          re.search(r'<section[\s\S]*?imei-promo[\s\S]*?imeiclick\.com/free"[\s\S]*?Verificar gratis ahora', html) is not None)
    check("[content] cross-promo no rompe CTA principal",
          text.count('Más información por WhatsApp') >= 1)


# --- F1.2 reglas de diseno (design-taste-frontend) -------------------------
def test_design(html, text, bundle):
    check("[design] cero em-dash visible", "\u2014" not in text,
          "em-dash prohibido (§9.G)")
    check("[design] cero en-dash como separador", "\u2013" not in text)

    eyebrows = len(re.findall(r"class=\"[^\"]*\beyebrow\b", html))
    sections = len(re.findall(r"<section\b", html, re.I))
    cap = max(1, -(-sections // 3))
    check(f"[design] eyebrows {eyebrows} <= ceil({sections}/3)={cap}",
          eyebrows <= cap)

    check("[design] sin h-screen (usar 100dvh)", "h-screen" not in bundle)
    check("[design] sin 100vh en alturas (usar dvh)",
          not re.search(r"(min-)?height:\s*100vh", bundle),
          "iOS Safari salta con 100vh")
    check("[design] sin negro puro #000000",
          not re.search(r"#000000\b", bundle, re.I))
    check("[design] sin listener de scroll",
          "addEventListener('scroll'" not in bundle
          and 'addEventListener("scroll"' not in bundle,
          "usar IntersectionObserver / scroll-driven CSS")
    check("[design] fondo base es el token de la paleta", BG in bundle.lower())
    check("[design] acento unico presente", ACCENT in bundle.lower())

    # un solo acento: no debe haber otro color saturado compitiendo
    banned_accents = ["#8b5cf6", "#a855f7", "#7c3aed", "#6366f1"]
    for c in banned_accents:
        check(f"[design] sin morado IA {c}", c not in bundle.lower())

    check("[design] prefers-reduced-motion contemplado",
          "prefers-reduced-motion" in bundle)
    check("[design] sin scroll cue",
          not re.search(r"\bscroll\s*(↓|abajo|para explorar)", text, re.I))
    check("[design] sin numeracion de seccion tipo 01 /",
          not re.search(r">\s*0\d\s*/\s*\w", text))


# --- F1.3 accesibilidad ----------------------------------------------------
def test_a11y(html, text):
    imgs = re.findall(r"<img\b[^>]*>", html, re.I)
    check("[a11y] hay imagenes", len(imgs) > 0)
    sin_alt = [i for i in imgs if not re.search(r"\balt\s*=", i, re.I)]
    check("[a11y] toda <img> con alt", not sin_alt,
          f"{len(sin_alt)} sin alt")

    check("[a11y] lang del documento",
          re.search(r"<html[^>]+lang\s*=\s*\"es", html, re.I) is not None)
    check("[a11y] tiene <h1>", "<h1" in html.lower())
    check("[a11y] un solo <h1>", html.lower().count("<h1") == 1)

    # contraste de los pares declarados en el plan
    pairs = [
        ("#f2f4f8", BG, 4.5, "texto primario sobre fondo"),
        ("#9aa3b2", BG, 4.5, "texto secundario sobre fondo"),
        (ACCENT, BG, 3.0, "acento sobre fondo"),
        (BG, ACCENT, 4.5, "texto del boton sobre acento"),
    ]
    for fg, bg, minimo, label in pairs:
        ratio = contrast(fg, bg)
        check(f"[a11y] contraste {label} {ratio:.2f} >= {minimo}",
              ratio >= minimo)

    # el CTA no puede quedar sin texto legible
    check("[a11y] CTA con texto", "Más información por WhatsApp" in text)

    # iframes/embeds necesitan title
    for tag in re.findall(r"<iframe\b[^>]*>", html, re.I):
        check("[a11y] iframe con title", "title=" in tag.lower())


def test_images(html):
    """Los atributos width/height deben coincidir con el fichero real:
    si no, el navegador reserva una caja con otro ratio y la foto se ve
    alargada o aplastada."""
    try:
        from PIL import Image
    except ImportError:
        check("[img] PIL disponible para medir ratios", False, "pip install pillow")
        return

    for tag in re.findall(r"<img\b[^>]*>", html, re.I):
        m = re.search(r'src="assets/img/([^"]+)"', tag)
        w = re.search(r'width="(\d+)"', tag)
        h = re.search(r'height="(\d+)"', tag)
        if not (m and w and h):
            continue
        path = os.path.join(SITE, "assets", "img", m.group(1))
        if not os.path.exists(path):
            check(f"[img] {m.group(1)} existe", False)
            continue
        iw, ih = Image.open(path).size
        declared = int(w.group(1)) / int(h.group(1))
        real = iw / ih
        check(f"[img] {m.group(1)} ratio declarado {declared:.3f} == real {real:.3f}",
              abs(declared - real) < 0.01,
              "width/height del HTML no cuadran con el fichero")
        # una foto de producto muy vertical se ve alargada
        check(f"[img] {m.group(1)} no es excesivamente vertical ({real:.2f})",
              real >= 0.8, "ratio < 0.8: recortar el aire muerto")
        # el cliente pidio producto sin fondo: alpha real, no un rectangulo
        img = Image.open(path)
        if img.mode in ("RGBA", "LA"):
            alpha = img.convert("RGBA").getchannel("A")
            lo, _ = alpha.getextrema()
            check(f"[img] {m.group(1)} tiene fondo transparente", lo < 250,
                  "el alpha es opaco: la foto lleva fondo")
        else:
            check(f"[img] {m.group(1)} tiene canal alpha", False,
                  f"modo {img.mode}: sin transparencia")


def main():
    if not os.path.exists(INDEX):
        print(f"RED: no existe {INDEX} (esperado antes de F2)")
        print("0 pass / 1 fail")
        return 1

    html = open(INDEX, encoding="utf-8").read()
    text = visible_text(html)
    # bundle = HTML + todos los assets: los IDs viven en tiktok.js y
    # los tokens de color en base.css, no en el HTML.
    bundle = html + "".join(
        strip_comments(read("assets", f)) for f in
        ("base.css", "motion.css", "tiktok.css", "scroll.js", "tiktok.js")
    )

    test_content(html, text, bundle)
    test_design(html, text, bundle)
    test_a11y(html, text)
    test_images(html)

    for f in failures:
        print("FAIL", f)
    print(f"\n{len(passes)} pass / {len(failures)} fail")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
