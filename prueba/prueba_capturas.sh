#!/bin/bash
# Capturas REALES del juego (cliente de software 1280x720, sin GPU, sin sombras ni shaders) para la página del proyecto: varios paisajes del mundo de pruebas.
cd "$(dirname "$0")"; . ./lib.sh; xvfb; S=srv; F=$S/consola.fifo; c() { printf '%s\n' "$@" > $F; }
rm -f $F; mkfifo $F; : > $S/salida.log; ( cd $S; exec 3>&-; tail -f consola.fifo | nice -n 15 ./run.sh nogui > salida.log 2>&1; echo FIN >> salida.log ) > /dev/null 2>&1 < /dev/null &
for i in $(seq 1 300); do grep -q 'Done (' $S/salida.log && break; sleep 1; done; PID=$(for p in /proc/[0-9]*; do [ "$(readlink $p/cwd 2>/dev/null)" = "$P/$S" ] && grep -q java $p/comm 2>/dev/null && echo ${p#/proc/}; done | head -1)
cliente 127.0.0.1:25850 cli :87 Pruebas; for i in $(seq 1 240); do grep -q "Pruebas joined the game" $S/salida.log && break; sleep 3; done; sleep 20
c "gamemode spectator Pruebas" "time set 6000" "weather clear"; sleep 2
i=0; for sp in "0 0 45 18" "3000 3000 200 20" "-6000 2500 120 22" "7000 7000 300 18" "-7000 -7000 20 20" "1500 -1500 250 22" "-3000 -3000 90 20"; do set -- $sp; i=$((i+1)); X=$1; Z=$2
  c "forceload add $X $Z" ; sleep 25; c "execute in minecraft:overworld positioned $X 0 $Z positioned over motion_blocking_no_leaves run tp Pruebas ~ ~28 ~ $3 $4"; sleep 22; cap paisaje_0$i
  c "data get entity Pruebas Pos"; c "forceload remove $X $Z"; done
parar_cliente cli; sleep 3; python3 -I $S/parar.py $S --pid $PID --espera 150 --aviso 0 > $OUT/parar_cap.txt 2>&1; pkill -x tail; pkill -x Xvfb; log FIN_CAP
