#!/bin/bash
# T3: un jugador (servidor integrado) con una copia del mundo restaurado: comprueba que Cauces y el resto cargan en el cliente y que el mundo se abre sin pasar por el servidor dedicado.
cd "$(dirname "$0")"; . ./lib.sh; xvfb; log "== T3 un jugador (servidor integrado)"
rm -rf cli/saves/aceptacion; mkdir -p cli/saves; cp -a srv_rest/aceptacion cli/saves/aceptacion; rm -f cli/saves/aceptacion/session.lock; rm -f cli/logs/latest.log
t0=$(date +%s); ( cd $P; DISPLAY=:87 MC_NOMBRE=Pruebas MC_QUICKPLAY_SP=aceptacion LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe MC_XMX=6G MC_ANCHO=1280 MC_ALTO=720 nice -n 10 setsid python3 -I lanzar.py $HOME/dev/purg4tory-identidad/cliente/mc "$P/cli" > "$P/cli/salida.log" 2>&1 < /dev/null 3>&- & )
for i in $(seq 1 200); do grep -q "Pruebas joined the game" cli/logs/latest.log 2>/dev/null && break; sleep 3; done; sleep 20
grep -q "Pruebas joined the game" cli/logs/latest.log && log "T3 mundo abierto en un jugador en $(( $(date +%s)-t0 )) s" || log "T3 NO ENTRÓ al mundo"
log "T3 Cauces en el servidor integrado: $(grep -o 'salvaguarda del guardado completo: [A-Z ]*' cli/logs/latest.log | head -1); $(grep -o 'botín: [0-9]* tablas' cli/logs/latest.log | head -1)"
log "T3 «Can't keep up»: $(grep -c "Can't keep up" cli/logs/latest.log); VIGÍA: $(grep -c VIGÍA cli/logs/latest.log)"; cap t3_un_jugador; cp cli/logs/latest.log $OUT/cliente_unjugador.log
parar_cliente cli; pkill -x Xvfb; log FIN_T3
