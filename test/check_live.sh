#!/usr/bin/env bash
# F1.4 — verificacion contra el sitio EN VIVO. Evidencia real, no auto-reporte.
# Uso: test/check_live.sh [host]
set -u
HOST="${1:-pico2ultra.imeiclick.com}"
BASE="https://${HOST}"
pass=0; fail=0
ok(){ echo "  ok   $1"; pass=$((pass+1)); }
no(){ echo "  FAIL $1"; fail=$((fail+1)); }

echo "== check_live: ${BASE} =="

# 1. DNS
ip=$(dig +short "$HOST" A | head -1)
[ -n "$ip" ] && ok "DNS resuelve ($ip)" || no "DNS no resuelve"

# 2. HTTPS 200
code=$(curl -s -o /tmp/pico_live.html -w '%{http_code}' --max-time 20 "$BASE/")
[ "$code" = "200" ] && ok "HTTPS 200" || no "HTTPS devolvio $code"

# 3. cert valido para el host
san=$(echo | openssl s_client -servername "$HOST" -connect "$HOST:443" 2>/dev/null \
      | openssl x509 -noout -ext subjectAltName 2>/dev/null)
echo "$san" | grep -q "$HOST" && ok "cert cubre $HOST" || no "cert NO cubre $HOST"

# 4. los videos de TikTok (viven en tiktok.js, no en el HTML)
curl -s --max-time 20 "$BASE/assets/tiktok.js" -o /tmp/pico_tiktok.js
for v in 7684054875650510100 7683691176272104724 7683630006991457557 \
         7683252903385173269 7682581386271771924 7682430154504899860 \
         7682134228284214548 7682131762272570644; do
  grep -q "$v" /tmp/pico_tiktok.js && ok "video $v servido" || no "falta video $v"
done

# 4b. posters locales servidos (click-to-play: nada se pide a TikTok al cargar)
for v in 7684054875650510100 7683630006991457557 7682131762272570644; do
  c=$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 \
       "$BASE/assets/img/tiktok/$v.jpg")
  [ "$c" = "200" ] && ok "poster $v" || no "poster $v devolvio $c"
done

# 5. click-to-play: no debe quedar montaje automatico de iframes
grep -q "IntersectionObserver" /tmp/pico_tiktok.js \
  && no "tiktok.js aun monta iframes automaticamente" \
  || ok "tiktok.js es click-to-play"
grep -q "tiktok.com/embed/v2/" /tmp/pico_tiktok.js \
  && ok "embed iframe /embed/v2/ presente" || no "sin endpoint de embed"

# 5b. el endpoint de TikTok sigue vivo para un video real (no asumir)
tc=$(curl -s -o /dev/null -w '%{http_code}' --max-time 20 \
     -H 'User-Agent: Mozilla/5.0' \
     "https://www.tiktok.com/embed/v2/7682430154504899860")
[ "$tc" = "200" ] && ok "TikTok embed responde 200" || no "TikTok embed devolvio $tc"

# 6. assets responden
for a in assets/base.css assets/motion.css assets/scroll.js assets/tiktok.js \
         assets/tiktok.css assets/img/pico2.webp assets/img/pico2_1.webp; do
  c=$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 "$BASE/$a")
  [ "$c" = "200" ] && ok "asset $a" || no "asset $a devolvio $c"
done

# 7. HTTP redirige a HTTPS
rc=$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 "http://${HOST}/")
case "$rc" in 301|302|308) ok "HTTP redirige ($rc)";; 200) no "HTTP sirve sin redirigir";; *) no "HTTP devolvio $rc";; esac

# 8. el dominio principal sigue intacto (regla de oro 1)
mc=$(curl -s -o /dev/null -w '%{http_code}' --max-time 20 "https://imeiclick.com/")
[ "$mc" = "200" ] && ok "imeiclick.com intacto (200)" || no "imeiclick.com devolvio $mc"

echo
echo "$pass pass / $fail fail"
[ "$fail" -eq 0 ]
