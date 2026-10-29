# Funciones comunes de las pruebas (se carga con «. lib.sh»). Cliente de software en Xvfb :87, sin GPU.
export PATH="$HOME/dev/tools/jdk-21.0.12.1+1/bin:$PATH"; . $HOME/dev/tools/xvfb/entorno.sh
P=$HOME/dev/purg4tory-beta1/prueba; OUT=${OUT:-$P/resultados}; mkdir -p $OUT/capturas; R=$OUT/resumen.txt
log() { echo "$(date +%H:%M:%S) $*" | tee -a $R; }
xvfb() { pgrep -x Xvfb >/dev/null && [ -S /tmp/.X11-unix/X87 ] && return; rm -f /tmp/.X11-unix/X87; setsid $HOME/dev/tools/xvfb/xvfb-aislado.sh :87 1280x720x24 > $OUT/xvfb.log 2>&1 < /dev/null 3>&- & sleep 5; }
cap() { DISPLAY=${DSP:-:87} import -window root "$OUT/capturas/$1.png" 2>/dev/null && log "captura $1"; }
cliente() { # $1 = quickplay host:puerto (vacío = pantalla de título) · $2 = instancia (cli) · $3 = display (:87) · $4 = nombre (Pruebas)
  local I=$P/${2:-cli}; rm -f $I/logs/latest.log; ( cd $P; DISPLAY=${3:-:87} MC_NOMBRE=${4:-Pruebas} LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe MC_XMX=6G MC_QUICKPLAY=$1 MC_ANCHO=1280 MC_ALTO=720 nice -n 10 \
    setsid python3 -I lanzar.py $HOME/dev/purg4tory-identidad/cliente/mc "$I" > "$I/salida.log" 2>&1 < /dev/null 3>&- & ); }
parar_cliente() { local I=${1:-cli}; for q in $(pgrep -f "purg4tory-beta1/prueba/$I\$|purg4tory-beta1/prueba/$I "); do [ "$q" != "$$" ] && kill $q 2>/dev/null; done; sleep 4; pkill -9 -f "purg4tory-beta1/prueba/$I\$|purg4tory-beta1/prueba/$I " 2>/dev/null; true; }
x() { DISPLAY=${DSP:-:87} python3 -I $P/x11in.py "$@"; }
xvfb2() { pgrep -f "Xvfb :88" >/dev/null && [ -S /tmp/.X11-unix/X88 ] && return; rm -f /tmp/.X11-unix/X88; setsid $HOME/dev/tools/xvfb/xvfb-aislado.sh :88 1280x720x24 > $OUT/xvfb2.log 2>&1 < /dev/null 3>&- & sleep 5; }
