#!/bin/bash
# C3: combate cuerpo a cuerpo (Better Combat, espada de hierro) y magia (Spell Engine, varita arcana) con CLIC REAL (XTest) en dos clientes, contra vacas sin IA a ras de suelo.
cd "$(dirname "$0")"; . ./lib.sh; xvfb; xvfb2; S=srv; F=$S/consola.fifo; T0=$(date +%s)
c() { printf '%s\n' "$@" > $F; }
q() { local L=$(( $(wc -l < $S/salida.log) + 1 )); c "$1"; sleep ${2:-2}; tail -n +$L $S/salida.log | grep -E "${3:-has the following|No entity|Unknown}" | head -1 | sed -E 's/^\[[0-9:]+\] \[[^]]*\]: //' | cut -c1-110; }
joins() { grep -c "$1 joined the game" $S/salida.log; }
rm -f $F; mkfifo $F; : > $S/salida.log; ( cd $S; exec 3>&-; tail -f consola.fifo | nice -n 15 ./run.sh nogui > salida.log 2>&1; echo FIN >> salida.log ) > /dev/null 2>&1 < /dev/null &
for i in $(seq 1 300); do grep -q 'Done (' $S/salida.log && break; sleep 1; done
PID=$(for p in /proc/[0-9]*; do [ "$(readlink $p/cwd 2>/dev/null)" = "$P/$S" ] && grep -q java $p/comm 2>/dev/null && echo ${p#/proc/}; done | head -1)
cliente 127.0.0.1:25850 cli :87 Pruebas; sleep 20; cliente 127.0.0.1:25850 cli2 :88 Pruebas2
for i in $(seq 1 240); do [ $(joins Pruebas2) -ge 1 ] && [ $(joins Pruebas) -ge 1 ] && break; sleep 3; done; sleep 30
c "time set noon" "gamemode survival Pruebas" "gamemode survival Pruebas2" "effect give @a minecraft:resistance infinite 4 true" "effect give @a minecraft:saturation infinite 1 true"; sleep 5
# separar a los jugadores y colocar una vaca sin IA a 2 bloques de cada uno, mirándola a los ojos
c "execute in minecraft:overworld positioned 8 0 8 positioned over motion_blocking_no_leaves run tp Pruebas ~ ~1 ~" "execute in minecraft:overworld positioned 12 0 8 positioned over motion_blocking_no_leaves run tp Pruebas2 ~ ~1 ~"; sleep 15
for n in Pruebas Pruebas2; do c "execute at $n run summon minecraft:cow ^ ^ ^2 {NoAI:1b,PersistenceRequired:1b,Tags:[\"v_$n\"]}"; done; sleep 3
for n in Pruebas Pruebas2; do c "execute as $n at @s facing entity @e[type=minecraft:cow,tag=v_$n,limit=1] eyes run tp @s ~ ~ ~ ~ ~"; done; sleep 2
DSP=:87 x key 4 100; DSP=:88 x key 5 100; sleep 1
log "C3 antes: vaca de Pruebas $(q 'data get entity @e[type=minecraft:cow,tag=v_Pruebas,limit=1] Health'); vaca de Pruebas2 $(q 'data get entity @e[type=minecraft:cow,tag=v_Pruebas2,limit=1] Health')"
DSP=:87 x click 1 120; sleep 0.7; DSP=:87 x click 1 120; sleep 1; DSP=:88 x click 3 1800; sleep 1.5
DSP=:87 cap c3_01_espada_Pruebas; DSP=:88 cap c3_02_varita_Pruebas2
log "C3 tras 2 golpes de espada, vaca de Pruebas: $(q 'data get entity @e[type=minecraft:cow,tag=v_Pruebas,limit=1] Health')"
log "C3 tras 1 hechizo mantenido 1,8 s, vaca de Pruebas2: $(q 'data get entity @e[type=minecraft:cow,tag=v_Pruebas2,limit=1] Health')"
log "C3 «No entity» = la vaca murió"; c "kill @e[type=minecraft:cow,tag=v_Pruebas]" "kill @e[type=minecraft:cow,tag=v_Pruebas2]"
parar_cliente cli; parar_cliente cli2; sleep 3
python3 -I $S/parar.py $S --pid $PID --espera 150 --aviso 0 > $OUT/parar_c3.txt 2>&1; log "C3 parada: código $?"; pkill -x tail; pkill -x Xvfb; log "FIN_C3 ($(( $(date +%s)-T0 )) s)"
