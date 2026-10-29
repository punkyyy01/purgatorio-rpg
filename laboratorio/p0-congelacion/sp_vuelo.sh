#!/bin/bash
# Auditoría P0 (2026-10-28): UN JUGADOR real (servidor integrado), mundo nuevo desde plantilla, distancia 32,
# creativo volando a y=310 hacia +X durante <segundos>. Instrumentado: purg4tory_diagtick + JFR continuo.
# Uso: sp_vuelo.sh <etiqueta> <jar_cauces|ninguno> <segundos> [distancia] [mods_extra_dir]
L=$HOME/dev/lab-p0; P=$HOME/dev/purg4tory-beta1/prueba; E=$1; JAR=$2; DUR=${3:-900}; RD=${4:-32}; EXTRA=$5
O=$L/res2/$E; mkdir -p $O; C=$L/cli
. $HOME/dev/tools/xvfb/entorno.sh; export PATH="$HOME/dev/tools/jdk-21.0.12.1+1/bin:$PATH"
log(){ echo "$(date +%H:%M:%S) $*" | tee -a $O/resumen.txt; }
x(){ DISPLAY=:89 python3 -I $P/x11in.py -d :89 "$@"; }
# mods: Cauces elegido + diagtick; nada más de laboratorio
mkdir -p $L/mods-fuera-cli; for f in $C/mods/purg4tory_cauces-*.jar $C/mods/purg4tory_diag*.jar $C/mods/extra-*.jar; do [ -e "$f" ] && mv "$f" $L/mods-fuera-cli/; done
[ "$JAR" != ninguno ] && cp $L/jars/$JAR $C/mods/purg4tory_cauces-prueba.jar
cp $L/diagtick/build/purg4tory_diagtick-0.1.0.jar $C/mods/
[ -n "$EXTRA" ] && for f in $EXTRA/*.jar; do cp $f $C/mods/extra-$(basename $f); done
log "mods de prueba: $(ls $C/mods | grep -E 'purg4tory|extra-' | tr '\n' ' ') (sha cauces: $(sha256sum $C/mods/purg4tory_cauces-prueba.jar 2>/dev/null | cut -c1-12))"
sed -i "s/^renderDistance:.*/renderDistance:$RD/; s/^simulationDistance:.*/simulationDistance:12/" $C/options.txt
if [ -n "$REUSAR" ]; then W=$REUSAR; [ -d $C/saves/$W ] || { log "no existe el mundo $W"; exit 1; }; log "reabriendo mundo existente $W"
else W=p0v_$E; [ -e $C/saves/$W ] && mv $C/saves/$W $L/res2/basura_${W}_$(date +%s); cp -a $L/plantillas/p0 $C/saves/$W; fi
sed -i 's/^vigiaS=.*/vigiaS=20/' $C/config/purg4tory_cauces.properties 2>/dev/null
pgrep -f "[X]vfb :89" >/dev/null || { rm -f /tmp/.X11-unix/X89; setsid $HOME/dev/tools/xvfb/xvfb-aislado.sh :89 1280x720x24 > $O/xvfb.log 2>&1 < /dev/null 3>&- & sleep 5; }
rm -f $C/logs/latest.log $C/diagtick-comandos.txt
JFR="-XX:StartFlightRecording=name=p0,disk=true,maxsize=800m,dumponexit=true,filename=$O/vuelo.jfr"
( cd $P; DISPLAY=:89 MC_NOMBRE=Pruebas LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe LP_NUM_THREADS=4 MC_XMX=7G MC_QUICKPLAY_SP=$W MC_ANCHO=1280 MC_ALTO=720 \
  nice -n 5 setsid python3 -I lanzar.py $HOME/dev/purg4tory-identidad/cliente/mc "$C" -- -Dstreamsreflowing.stalltrace=1 $JFR > "$C/salida.log" 2>&1 < /dev/null 3>&- & )
for i in $(seq 1 300); do grep -q "se ha unido a la partida\|joined the game" $C/logs/latest.log 2>/dev/null && break; sleep 2; done
grep -q "se ha unido a la partida\|joined the game" $C/logs/latest.log || { log "NO ENTRÓ"; exit 1; }
sleep 20; CP=$(pgrep -f "bin/java.*lab-p0/cli" | head -1); echo $CP > $O/pid
D=$(ls -td $C/diagtick/*/ | head -1); echo $D > $O/diagdir; log "mundo abierto; pid $CP; diag $D"
printf '%s\n' "gamemode creative Pruebas" "time set noon" "gamerule doDaylightCycle false" "weather clear" "gamerule doWeatherCycle false" "tp Pruebas ~ 330 ~ ${YAW:--90} 0" > $C/diagtick-comandos.txt
for i in $(seq 1 60); do grep -q "orden: tp Pruebas" $D/resumen.log && break; sleep 1; done; grep -q "orden: tp Pruebas" $D/resumen.log || log "AVISO: órdenes iniciales sin ejecutar"; sleep 2
cap(){ DISPLAY=:89 import -window root "$O/$1.png" 2>/dev/null; }
cap 1_entrada
# muestreo externo: CPU y memoria del proceso cada 10 s
( while kill -0 $CP 2>/dev/null; do echo "$(date +%H:%M:%S) $(ps -o %cpu=,rss= -p $CP) carga=$(cut -d' ' -f1 /proc/loadavg)"; sleep 10; done > $O/cpu.txt ) &
log "vuelo ${VUELO:-cliente} +X (servidor: 21.6 b/s fijo; cliente: W+esprint creativo), y=310, $DUR s, distancia $RD"
if [ "${VUELO:-cliente}" = tp ]; then :; elif [ "${VUELO:-cliente}" = servidor ]; then echo "!vuelo 21.6 0 310 $DUR" > $C/diagtick-comandos.txt; else echo "!vuelo_cliente $DUR ${GIRO:-0} ${YAW:--90}" > $C/diagtick-comandos.txt; fi
( sleep 60; cap 3_vuelo60s ) &
# espera activa; corta si el servidor deja de escribir posiciones (congelación) más de 300 s
T0=$(date +%s); NTP=0; while [ $(( $(date +%s) - T0 )) -lt $((DUR+10)) ]; do sleep 15
  if [ "${VUELO:-cliente}" = tp ]; then NTP=$((NTP+1)); echo "tp Pruebas $((NTP*3000)) 200 $(( (NTP%2)*3000 ))" > $C/diagtick-comandos.txt; fi
  grep -q "vuelo terminado" $D/resumen.log && break
  U=$(stat -c %Y $D/posiciones.log); [ $(( $(date +%s) - U )) -gt 300 ] && { log "CONGELACIÓN: sin posiciones de servidor desde hace >300 s"; jstack -l $CP > $O/jstack_congelado.txt 2>&1; break; }
done
log "fin del vuelo; últimas posiciones SRV/CLI:"; grep -E " (SRV|CLI) " $D/posiciones.log | tail -2 | tee -a $O/resumen.txt
# prueba de vida final: ¿el servidor responde a una orden?
echo "say fin-de-prueba-$E" > $C/diagtick-comandos.txt; sleep 8
grep -q "fin-de-prueba-$E" $C/logs/latest.log && log "servidor responde" || log "SERVIDOR NO RESPONDE a los 8 s"
jcmd $CP JFR.dump name=p0 filename=$O/vuelo.jfr > /dev/null 2>&1
jstack -l $CP > $O/jstack_final.txt 2>&1
# salida limpia, como «Guardar y salir»: se espera a que el servidor integrado termine de guardar
TS=$(date +%s); echo "!salir" > $C/diagtick-comandos.txt
for i in $(seq 1 240); do grep -q "parada (servidor detenido" $D/resumen.log && break; sleep 1; done
grep -q "parada (servidor detenido" $D/resumen.log && log "guardar y salir: limpio en $(( $(date +%s) - TS )) s" || log "guardar y salir: NO terminó en 240 s"
sleep 3; kill $CP; for i in $(seq 1 60); do kill -0 $CP 2>/dev/null || break; sleep 1; done; kill -0 $CP 2>/dev/null && { log "cliente no salió: kill -9"; kill -9 $CP; }
cp $C/logs/latest.log $O/cliente.log; cp -r $D $O/diag
log "resumen diag:"; cat $D/resumen.log | tee -a $O/resumen.txt
log "pausas >=0.5 s: $(grep -c '^.* PAUSA' $D/pausas.log); >=2 s: $(grep -oE 'PAUSA [0-9.]+' $D/pausas.log | awk '$2>=2' | wc -l); suma: $(grep -oE 'PAUSA [0-9.]+' $D/pausas.log | awk '{s+=$2} END{print s+0}') s; máx: $(grep -oE 'PAUSA [0-9.]+' $D/pausas.log | awk '$2>m{m=$2} END{print m+0}') s"
log "esperas síncronas >50 ms: $(grep -c ESPERA $D/esperas.log); Can't keep up: $(grep -c "Can't keep up" $O/cliente.log); VIGÍA: $(grep -c 'VIGÍA: el servidor' $O/cliente.log)"
log FIN
