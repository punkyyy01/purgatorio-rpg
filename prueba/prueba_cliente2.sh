#!/bin/bash
# C2: dos clientes independientes (Pruebas en :87, Pruebas2 en :88) sobre el mundo de la batería. Combate cuerpo a cuerpo y magia con clic real (XTest),
# dos teletransportes en frío simultáneos, portal del Nether, muerte y reaparición, desconexión y reconexión. Cliente de software (sin GPU).
cd "$(dirname "$0")"; . ./lib.sh; xvfb; xvfb2; S=srv; F=$S/consola.fifo; T0=$(date +%s)
c() { printf '%s\n' "$@" > $F; }
q() { local L=$(( $(wc -l < $S/salida.log) + 1 )); c "$1"; sleep ${2:-2}; tail -n +$L $S/salida.log | grep -E "${3:-Test|has the following|No entity|Unknown|Could not}" | head -1 | sed -E 's/^\[[0-9:]+\] \[[^]]*\]: //' | cut -c1-110; }
joins() { grep -c "$1 joined the game" $S/salida.log; }
rm -f $F; mkfifo $F; : > $S/salida.log; ( cd $S; exec 3>&-; tail -f consola.fifo | nice -n 15 ./run.sh nogui > salida.log 2>&1; echo FIN >> salida.log ) > /dev/null 2>&1 < /dev/null &
for i in $(seq 1 300); do grep -q 'Done (' $S/salida.log && break; sleep 1; done; log "C2 servidor arrancado ($(grep -o 'Done ([0-9.]*s)' $S/salida.log))"; PID=$(for p in /proc/[0-9]*; do [ "$(readlink $p/cwd 2>/dev/null)" = "$P/$S" ] && grep -q java $p/comm 2>/dev/null && echo ${p#/proc/}; done | head -1)
cliente 127.0.0.1:25850 cli :87 Pruebas; sleep 20; cliente 127.0.0.1:25850 cli2 :88 Pruebas2
for i in $(seq 1 240); do [ $(joins Pruebas2) -ge 1 ] && [ $(joins "Pruebas") -ge 1 ] && break; sleep 3; done
log "C2 conectados: Pruebas=$(joins Pruebas) Pruebas2=$(joins Pruebas2) (jugadores en línea: $(q 'list' 2 'There are'))"; sleep 25
c "gamemode survival Pruebas" "gamemode survival Pruebas2" "effect give @a minecraft:resistance infinite 4 true" "effect give @a minecraft:saturation infinite 1 true" "forceload add 0 0 15 15"; sleep 3
# plataforma en el aire (chunks forzados): combate de Pruebas y magia de Pruebas2
c "fill 4 199 4 20 199 20 minecraft:stone" "tp Pruebas 8 200 8 facing 8 200 12" "tp Pruebas2 16 200 8 facing 16 200 12" "summon minecraft:zombie 8 200 11 {NoAI:1b,PersistenceRequired:1b}" "summon minecraft:zombie 16 200 11 {NoAI:1b,PersistenceRequired:1b}"; sleep 4
DSP=:87 x key 4 100; DSP=:88 x key 5 100; sleep 1
for i in 1 2 3 4; do DSP=:87 x click 1 120; sleep 0.7; done; DSP=:88 x click 3 3000; sleep 1
DSP=:87 cap c2_01_combate_Pruebas; DSP=:88 cap c2_02_magia_Pruebas2
log "C2 combate (espada, 4 golpes): zombi de Pruebas $(q 'data get entity @e[type=minecraft:zombie,x=8,y=200,z=11,distance=..3,limit=1] Health')"
log "C2 magia (varita arcana, clic derecho mantenido): zombi de Pruebas2 $(q 'data get entity @e[type=minecraft:zombie,x=16,y=200,z=11,distance=..3,limit=1] Health')"
# dos tp en frío simultáneos
L=$(( $(wc -l < $S/salida.log) + 1 )); c "tp Pruebas 7000 220 7000" "tp Pruebas2 -7000 220 -7000"
for i in $(seq 1 120); do [ $(tail -n +$L $S/salida.log | grep -cE "teletransporte de Pruebas2? a") -ge 2 ] && break; sleep 1; done
tail -n +$L $S/salida.log | grep -E "teletransporte de Pruebas2? a" | sed -E 's/^.*Cauces\/\]: //' | cut -c1-110 | while read l; do log "C2 tp simultáneo: $l"; done
sleep 10; DSP=:87 cap c2_03_tp_Pruebas; DSP=:88 cap c2_04_tp_Pruebas2
log "C2 mientras tanto, «Can't keep up» acumulados: $(grep -c "Can't keep up" $S/salida.log)"
# portal del Nether (changeDimension; no cubierto por el aplazamiento de Cauces): marco 4x5 en la plataforma
c "tp Pruebas 8 200 8" "fill 6 200 18 9 204 18 minecraft:obsidian" "fill 7 201 18 8 203 18 minecraft:nether_portal[axis=x]"; sleep 3
L=$(( $(wc -l < $S/salida.log) + 1 )); c "tp Pruebas 8 201 18"; sleep 15
log "C2 portal: dimensión de Pruebas: $(q 'data get entity Pruebas Dimension' 2 'has the following')"; DSP=:87 cap c2_05_portal; log "C2 portal: «Can't keep up» nuevos: $(tail -n +$L $S/salida.log | grep -c "Can't keep up")"
# muerte y reaparición
c "kill Pruebas2"; sleep 4; DSP=:88 cap c2_06_muerte; DSP=:88 x moveto 640 400; sleep 1; DSP=:88 x click 1 100; sleep 6; DSP=:88 cap c2_07_reaparicion
log "C2 reaparición de Pruebas2: $(q 'data get entity Pruebas2 Health' 2 'has the following')"
# desconexión y reconexión de Pruebas
n=$(joins Pruebas); log "C2 desconexión de Pruebas"; parar_cliente cli; sleep 6
log "C2 jugadores tras la desconexión: $(q 'list' 2 'There are')"
cliente 127.0.0.1:25850 cli :87 Pruebas; for i in $(seq 1 120); do [ $(joins Pruebas) -gt $n ] && break; sleep 3; done; sleep 20
log "C2 reconexión: entradas de Pruebas $n → $(joins Pruebas); espada conservada: $(q 'execute if items entity Pruebas container.* minecraft:iron_sword' 2 'Test|No entity')"
DSP=:87 cap c2_08_reconexion
for I in cli cli2; do cp $P/$I/logs/latest.log $OUT/cliente_${I}_partida.log; log "C2 errores del registro de $I: $(grep -c '/ERROR\]' $OUT/cliente_${I}_partida.log)"; done
parar_cliente cli; parar_cliente cli2; sleep 3
python3 -I $S/parar.py $S --pid $PID --espera 150 --aviso 0 > $OUT/parar_c2.txt 2>&1; log "C2 parada: código $? en $(tail -1 $OUT/parar_c2.txt | cut -c1-90)"; pkill -x tail; pkill -x Xvfb
log "FIN_C2 ($(( $(date +%s)-T0 )) s)"
