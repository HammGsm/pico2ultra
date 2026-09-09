# PLAN — pico2ultra.imeiclick.com

Landing de infoproducto, presentación estilo Apple de **un solo producto**: Caja de ingeniería PICO 2 Ultra (versión mejorada).

Ciclo obligatorio: `plan -> test -> implement -> review -> verify -> remember -> improve`.
Marcar cada casilla al completarla. No saltar fases.

---

## 0. Reglas de oro (no negociables)

1. **Producción ajena intacta.** Solo se crea el vhost `pico2ultra.imeiclick.com`. NO se toca `imeiclick.com` (SaaS Sassidru en `/home/imeiclick/web/imeiclick.com/sassidru`), ni su BD, ni su vhost, ni su cert.
2. **Sitio estático.** Sin Laravel, sin BD, sin PHP con estado. HTML+CSS+JS servido por nginx. Menos superficie, menos riesgo, deploy trivial.
3. **Fotos reales del producto.** Las 3 adjuntas son la única fuente visual del hardware. No inventar renders ni fotos de stock del producto.
4. **Los 6 videos de TikTok son los reales de @imeiclick.** IDs verificados por el endpoint embed (ver §3). No inventar IDs ni incrustar videos de otras cuentas.
5. **Sin em-dash (—) en ningún texto visible.** Regla dura de `design-taste-frontend` §9.G.
6. **Un tema, un acento, un radio.** Lock de tema/color/forma en toda la página.
7. **`prefers-reduced-motion` respetado** en cada animación. Toda la narrativa debe leerse sin movimiento.
8. **Copy en español (es-PE).** Público objetivo: técnicos de reparación de celulares en LATAM.
9. **Nada se declara "listo" sin evidencia de ejecución real** (curl, HTTP code, screenshot, byte count). Auto-reporte de agente no es verificación.
10. **Archivos .md entregados con BOM UTF-8.**

---

## 1. Design Read (obligatorio antes de código)

> **Reading this as:** landing de producto único (infoproducto hardware) para técnicos de reparación de móviles en LATAM, con lenguaje **premium-consumer estilo Apple product page**, apoyado en scroll-driven storytelling y fotografía real de producto sobre fondo oscuro.

**Dials** (`design-taste-frontend` §1):

| Dial | Valor | Razón |
|---|---|---|
| `DESIGN_VARIANCE` | **7** | Premium consumer. Composición asimétrica, pero legible; no experimental. |
| `MOTION_INTENSITY` | **8** | La petición es explícita: "transiciones para dropscroll, como Apple". El movimiento ES el producto aquí. |
| `VISUAL_DENSITY` | **3** | Product page Apple: aire, una idea por pantalla. |

**Paleta** (medida de las fotos reales, no inventada):

Las 3 fotos comparten un mundo frío gris-azulado (`#c0c0d8`, `#a8c0c0`, `#d8d8d8`) con negro profundo en `pico1`. Esto **prohíbe** el default beige+brass de premium-consumer (§4.2 ban) y da la paleta natural:

- Fondo: `#08090c` (off-black frío, nunca `#000000`)
- Superficie elevada: `#111318`
- Texto primario: `#f2f4f8`
- Texto secundario: `#9aa3b2`
- Acento único: **cian frío `#4fd6e8`** (deriva del `#a8c0c0` de las fotos; encaja con "chip", "señal", "diagnóstico")
- Sin segundo acento. Sin gradiente morado IA.

**Tipografía**: sans display, NO serif (§4.1 serif discipline). `Geist` o system-ui como fallback. Tracking negativo en display (`-0.02em`), leading `1.05`. Body cerca de `0` tracking.

**Radio de forma**: lock en `16px` para superficies, `999px` (pill) para botones. Un solo sistema.

---

## 2. Arquitectura de la página (secciones y familia de layout)

Regla §4.7: ninguna familia de layout se repite; mínimo 4 familias distintas. Máximo `ceil(9/3) = 3` eyebrows en toda la página.

| # | Sección | Familia de layout | Eyebrow | Movimiento |
|---|---|---|---|---|
| 1 | Hero | Producto centrado sobre fondo negro, headline 2 líneas | Sí (1/3) | Fade+scale de entrada, imagen con parallax sutil |
| 2 | Scroll-cinema DCSD | Sticky pinned, imagen fija + texto que avanza | No | **Dropscroll principal**: pin + crossfade entre las 3 fotos |
| 3 | Un click: DFU / PWND | Split 50/50 asimétrico | No | Reveal escalonado, contador de "1 click" |
| 4 | Chip RP2354A | Full-bleed oscuro, dato grande | Sí (2/3) | Number count-up al entrar en viewport |
| 5 | Protecciones + Type-C | Bento 4 celdas (exacto 4 items, sin celda vacía) | No | Stagger de entrada |
| 6 | Compatibilidad | Grid de dispositivos, 7 iPhone + 4 iPad = 11 celdas | Sí (3/3) | Stagger, sin marquee |
| 7 | TikTok | Carrusel horizontal scroll-snap con 6 embeds | No | Scroll-snap nativo, sin hijack |
| 8 | Cierre / CTA | Manifiesto centrado (única sección centrada) | No | Fade final |
| 9 | Footer | Fila simple | No | Ninguno |

**CTA intent único**: un solo intent de conversión en toda la página (§4.5 no duplicate CTA intent). Label único: **"Pedir por WhatsApp"**. Aparece en hero, en cierre y en la barra sticky. Mismo texto en los tres.

**Prohibido explícitamente en esta página** (tells de §9.F):
- Nada de `V2.0` / `BETA` en el hero
- Nada de `01 / INDEX` ni numeración de secciones
- Nada de `Scroll ↓`
- Nada de strip decorativo `DCSD · DFU · PWND` al pie del hero
- Nada de dots de estado decorativos
- Nada de captions de crédito fotográfico inventadas
- Máximo 1 marquee en la página (decisión: **cero** marquees)

---

## 3. Videos TikTok (@imeiclick) — datos verificados

Extraídos de `https://www.tiktok.com/embed/@imeiclick` (HTTP 200, 304 KB) el 2026-09-08. **6 IDs**:

```
7683252903385173269
7682581386271771924
7682430154504899860   <- desc: "Bypass con UnlockTool utilizando la nueva Raspberry Pi Pico 2 Ultra (RP2350) de forma auto..."
7682134228284214548
7682131762272570644
7682127178368992263
```

**Método de incrustación**: `blockquote.tiktok-embed` + `https://www.tiktok.com/embed.js` (oficial, el mismo que devuelve el oembed de TikTok).

**Problema conocido a resolver en la fase de test** (§ por qué esta sección tiene su propio test): el embed oficial de TikTok reserva un alto fijo y con 6 embeds en fila produce saltos de layout (CLS) y videos que se solapan o quedan fuera de flujo. La petición del usuario es literal: *"que todos los videos se muestren de forma correcta y ubicación correcta"*.

Estrategia: contenedor con **aspect-ratio reservado** (`aspect-ratio: 9/16`, `max-width: 325px`) por tarjeta, carrusel `scroll-snap-type: x mandatory`, y **lazy-mount**: el `embed.js` solo se carga cuando la sección entra en viewport (IntersectionObserver), no al cargar la página. Fallback si el embed no monta en 3 s: tarjeta con thumbnail + link directo al video.

---

## 4. Fotos

| Archivo | Contenido | Uso |
|---|---|---|
| `pico1.jpeg` | Fondo oscuro, producto iluminado | Hero + frame final del scroll-cinema |
| `pico2.jpeg` | Fondo claro frío, vista producto | Frame 1 del scroll-cinema |
| `pico2_1.jpeg` | Fondo claro frío, vista alterna | Frame 2 del scroll-cinema |

Pipeline: convertir a **WebP** (calidad 82) + mantener JPEG como fallback `<picture>`. Ancho servido: 896px nativo, más variante 448px para móvil. `loading="lazy"` en todas menos la del hero (`fetchpriority="high"`).

---

## 5. Fases

### F0 — Preparación y assets
- [x] F0.1 Crear estructura `/root/pico2ultra/site/`
- [x] F0.2 Copiar las 3 fotos, generar WebP + variantes 448px, medir pesos — hero 776 KB JPEG a 137 KB WebP
- [x] F0.3 Verificar que ImageMagick/cwebp existen; si no, usar PIL — usado PIL 10.2.0
- [x] F0.4 Definir tokens CSS (color, tipo, radio, spacing) en un solo `:root` — `site/assets/base.css`

### F1 — Test primero (harness antes del código)
> Regla del usuario: `plan -> test -> implement`. Los checks se escriben ANTES del HTML.
- [x] F1.1 `test/check_site.py`: valida los 11 modelos compatibles, las características, los 6 IDs de TikTok
- [x] F1.2 mismo fichero: falla con em-dash visible, >3 eyebrows, `h-screen`, `100vh`, `#000000`, listener de scroll, acento duplicado
- [x] F1.3 mismo fichero: contraste WCAG AA calculado sobre los tokens, alt en toda `<img>`, un solo `<h1>`, lang es
- [x] F1.4 `test/check_live.sh`: DNS, HTTPS 200, cert SAN, 6 IDs servidos, assets 200, HTTP→301, `imeiclick.com` intacto
- [x] F1.5 Correr y confirmar RED — `0 pass / 1 fail` (no existe index.html todavía)

### F4 — Deploy a papuserver
- [x] F4.1 `v-add-web-domain imeiclick pico2ultra.imeiclick.com` — rc=0, docroot creado
- [ ] F4.2 Subir sitio a `/home/imeiclick/web/pico2ultra.imeiclick.com/public_html/`
- [x] F4.3 `v-add-letsencrypt-domain` — rc=0, cert CN=pico2ultra.imeiclick.com, vence 2026-12-07
- [x] F4.4 `v-add-web-domain-ssl-force` — rc=0, HTTP devuelve 301
- [x] F4.5 `imeiclick.com` verificado 200 antes y después de tocar el server

### F2 — Implementación (agentes en paralelo)
Los agentes NO comparten fichero. Cada uno entrega su parcial; yo cableo el `index.html`.
- [x] F2.1 **Agente A — Motion/Scroll**: `assets/scroll.js` + `assets/motion.css` entregados
- [x] F2.2 **Agente B — Copy/Marketing**: `content/copy.json` entregado
- [x] F2.3 **Agente C — TikTok**: reescrito por el orquestador (ver F3.3)
- [x] F2.4 **Yo — Estructura**: `build.py` genera `index.html` desde `copy.json` + `assets/base.css`

### F3 — Review
- [x] F3.1 Tests de F1 en verde: **53 pass / 0 fail**
- [x] F3.2 Pre-Flight Check aplicado (ver §9)
- [x] F3.3 Diff de cada agente revisado. **3 bugs reales encontrados en su código, no en sus resúmenes**:
  1. `copy.json` traía 4 frames de cinema y solo había 3 fotos (ahora 2 por decisión del cliente)
  2. `scroll.js` escribía `transform` inline sobre `.hero-img`, el mismo elemento con `animation: hero-in`: el inline ganaba y mataba el fade de entrada. Fix: el parallax va como variable CSS sobre `.hero-media`
  3. `tiktok.js` era destructivo y frágil: a los 3 s hacía `card.innerHTML=''` en TODAS las tarjetas (si TikTok tardaba 4 s borraba embeds que sí iban a montar) y dependía de `window.tiktokEmbed.render()`, API no documentada. **Reescrito**: `<iframe>` directo a `/embed/v2/<id>` (verificado HTTP 200, sin `X-Frame-Options` ni `frame-ancestors`), fallback no destructivo por capas

### F5 — Verify (evidencia real, no auto-reporte)
- [x] F5.1 `check_live.sh`: **20 pass / 0 fail**
- [x] F5.2 Cert válido: `CN=pico2ultra.imeiclick.com`, vence 2026-12-07
- [x] F5.3 **Los 6 videos montan en navegador real**: `cargados: 6, timeout: 0`, mismo alto y mismo top en las 6 tarjetas (cero layout shift). IDs verificados uno a uno
- [x] F5.4 Dropscroll medido: crossfade `[0.98, 0.02]` al inicio y `[0.02, 0.98]` al final, `stage_top: 0` (pin sticky correcto)
- [x] F5.5 `prefers-reduced-motion: reduce`: `frames:[0,1]` una sola visible, 0 reveals ocultos, página legible sin movimiento
- [x] F5.6 Móvil 390px: hero **689px en viewport de 844 (cabe)**, CTA visible sin scroll, cero overflow horizontal, flechas ocultas

### F6 — Remember
- [ ] F6.1 Persistir en skill: embed de TikTok por iframe directo, bug de `height` en `<picture>`, especificidad en reduced-motion
- [ ] F6.2 Persistir en el vault lo reutilizable

### F7 — Improve
- [ ] F7.1 Lighthouse: LCP < 2.5 s, CLS < 0.1, INP < 200 ms
- [ ] F7.2 Ajustes de pulido

### F4 — Deploy a papuserver
- [ ] F4.1 `v-add-web-domain imeiclick pico2ultra.imeiclick.com` (usuario `imeiclick`, ya existe)
- [ ] F4.2 Subir sitio a `/home/imeiclick/web/pico2ultra.imeiclick.com/public_html/`
- [ ] F4.3 `v-add-letsencrypt-domain imeiclick pico2ultra.imeiclick.com` (DNS ya resuelve a 161.132.47.111, HTTP-01 viable)
- [ ] F4.4 `v-add-web-domain-ssl-force imeiclick pico2ultra.imeiclick.com`
- [ ] F4.5 Confirmar que `imeiclick.com` sigue intacto (curl 200 + login del SaaS responde)

### F5 — Verify (evidencia real, no auto-reporte)
- [ ] F5.1 `check_live.sh` verde contra `https://pico2ultra.imeiclick.com`
- [ ] F5.2 Cert válido: `openssl s_client` con CN/SAN correcto
- [ ] F5.3 Los 6 embeds de TikTok montan y se ven en su sitio (verificación en navegador real, no solo HTTP 200)
- [ ] F5.4 Sin errores en consola del navegador
- [ ] F5.5 Prueba con `prefers-reduced-motion: reduce`: la página se lee completa sin movimiento
- [ ] F5.6 Móvil (viewport 390px): sin overflow horizontal, hero cabe, carrusel funciona

### F6 — Remember
- [ ] F6.1 Actualizar skill `imei-check-saas` o crear skill nueva con lo aprendido (embed de TikTok sin CLS, dropscroll Apple, subdominio Hestia)
- [ ] F6.2 Persistir en el vault lo que sea reutilizable

### F7 — Improve
- [ ] F7.1 Lighthouse: LCP < 2.5 s, CLS < 0.1, INP < 200 ms
- [ ] F7.2 Ajustes de pulido según lo que salga de F5/F7.1

---

## 6. Riesgos conocidos

| Riesgo | Mitigación |
|---|---|
| Romper `imeiclick.com` (SaaS en producción, cobra dinero) | Vhost separado, usuario Hestia existente, cero cambios en el vhost/cert/BD del dominio principal. Verificación explícita en F4.5. |
| Embed de TikTok causa CLS o no monta | Aspect-ratio reservado + lazy-mount + fallback a link. Test dedicado en F1.4/F5.3. |
| TikTok cambia/borra un video | Fallback degradado a link; la página no depende de que monte para ser legible. |
| Let's Encrypt falla | DNS ya verificado resolviendo a la IP correcta. Si falla, el sitio queda en HTTP y se reintenta; no bloquea el resto. |
| Agentes en paralelo pisándose | Cada uno escribe ficheros disjuntos; el cableado del `index.html` lo hago yo. |
| Motion pesado en móvil | Solo `transform`/`opacity`, sin librería externa, IntersectionObserver nativo. |

---

## 7. Stack decidido

- HTML5 + CSS nativo (custom properties, `position: sticky`, `scroll-snap`, `animation-timeline` donde haya soporte con fallback IntersectionObserver)
- JS vanilla, cero dependencias, cero build step
- `embed.js` de TikTok, cargado bajo demanda
- Servido por nginx (Hestia), estático puro

Razón (ladder): no necesita framework. Es una landing de una página. Añadir React/Vite sería construir un pipeline de build para servir HTML estático.

---

## 8. Bitácora

| Fecha | Fase | Resultado |
|---|---|---|
| 2026-09-08 | Recon | 6 IDs de TikTok extraídos y verificados; DNS `pico2ultra` ya resuelve a 161.132.47.111; papuserver con nginx+PHP 8.3, usuario `imeiclick` existente; paleta medida de las 3 fotos |
| | | |
