#!/bin/bash
# T2: pantalla de título en distintas resoluciones y escalas de interfaz (FancyMenu): 854x480, 1920x1080 (guiScale auto y 2), 2560x1440 (guiScale 3).
cd "$(dirname "$0")"; . ./lib.sh
for cfg in "854 480 0" "1920 1080 0" "1920 1080 2" "2560 1440 3"; do set -- $cfg; W=$1; H=$2; G=$3
  pkill -x Xvfb 2>/dev/null; sleep 2; rm -f /tmp/.X11-unix/X87; setsid $HOME/dev/tools/xvfb/xvfb-aislado.sh :87 ${W}x${H}x24 > $OUT/xvfb.log 2>&1 < /dev/null 3>&- & sleep 5
  sed -i "s/^guiScale:.*/guiScale:$G/" cli/options.txt
  log "T2 ${W}x${H} guiScale=$G"; ( cd $P; DISPLAY=:87 LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe MC_XMX=6G MC_ANCHO=$W MC_ALTO=$H nice -n 10 \
    setsid python3 -I lanzar.py $HOME/dev/purg4tory-identidad/cliente/mc "$P/cli" > "$P/cli/salida.log" 2>&1 < /dev/null 3>&- & )
  rm -f cli/logs/latest.log; sleep 8
  for i in $(seq 1 200); do grep -q "Every Compat has loaded" cli/logs/latest.log 2>/dev/null && break; sleep 3; done; sleep 40
  cap titulo_${W}x${H}_gui$G; parar_cliente
done; pkill -x Xvfb; log FIN_T2
