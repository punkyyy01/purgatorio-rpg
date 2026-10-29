#!/bin/bash
# Batería de aceptación de 0.6.0-beta.1 (corta, funcional; NO es un benchmark). Presupuesto: ≈ 40 min. Servidor en prueba/srv (instalado con el instalador del paquete de servidor).
# Fases: S0 arranque · S1 marcadores · S2 localizar estructuras peligrosas desde el spawn · C cliente (conexión, guía, combate, magia, tp en frío, Nether/End, reconexión)
#        · S3 parada segura (parar.py) · S4 reinicio y persistencia · S5 respaldo → restauración en instalación separada → verificación.
cd "$(dirname "$0")"; . ./lib.sh; xvfb; S=srv; F=$S/consola.fifo; T0=$(date +%s)
c() { printf '%s\n' "$@" > $F; }
esp() { local pat=$1 max=${2:-60} ini=${3:-1}; for i in $(seq 1 $max); do tail -n +$ini $S/salida.log | grep -qE "$pat" && return 0; sleep 1; done; return 1; }
cmdout() { local L=$(( $(wc -l < $S/salida.log) + 1 )); c "$1"; sleep ${2:-2}; tail -n +$L $S/salida.log | sed -E 's/^\[[0-9:]+\] \[[^]]*\] //' | head -${3:-3}; }
arrancar() { rm -f $F; mkfifo $F; : > $S/salida.log; ( cd $S; exec 3>&-; tail -f consola.fifo | nice -n 15 ./run.sh nogui > salida.log 2>&1; echo FIN >> salida.log ) > /dev/null 2>&1 < /dev/null &
  for i in $(seq 1 400); do grep -qE 'Done \(|^FIN' $S/salida.log && break; sleep 1; done; grep -q 'Done (' $S/salida.log; }
pidsrv() { for p in /proc/[0-9]*; do [ "$(readlink $p/cwd 2>/dev/null)" = "$P/$S" ] && grep -q java $p/comm 2>/dev/null && echo ${p#/proc/} && return; done; }
log "=== ACEPTACIÓN 0.6.0-beta.1 ($(date -u +%FT%TZ))"
rm -rf $S/aceptacion $S/logs; sed -i 's/^level-name=.*/level-name=aceptacion/' $S/server.properties; : > $R
# ---- S0
t=$(date +%s); arrancar && log "S0 servidor arrancado en $(( $(date +%s)-t )) s ($(grep -o 'Done ([0-9.]*s)' $S/salida.log))" || { log "S0 FALLO: no arranca"; exit 1; }
cp $S/logs/latest.log $OUT/servidor_arranque.log; PID=$(pidsrv)
log "S0 ERROR en el registro de arranque: $(grep -c '/ERROR\]' $S/logs/latest.log) (no-DISTXFORM: $(grep '/ERROR\]' $S/logs/latest.log | grep -vc DISTXFORM))"
grep '/ERROR\]' $S/logs/latest.log | grep -v DISTXFORM | sed -E 's/^\[[^]]*\] //' | cut -c1-170 >> $R
log "S0 Cauces: $(grep -o 'salvaguarda del guardado completo: [A-Z ]*' $S/logs/latest.log | head -1); $(grep -o 'botín: [0-9]* tablas' $S/logs/latest.log | head -1); datapacks propios: $(grep -c 'Found new data pack purgatorio_' $S/logs/latest.log)"
log "S0 errores de receta (Create/Galosphere): $(grep -c 'RecipeManager.*Parsing error' $S/logs/latest.log)"
# ---- S1 marcadores (sin jugadores)
c "forceload add 0 0 15 15" "execute in minecraft:the_nether run forceload add 0 0" "execute in minecraft:the_end run forceload add 0 0"; sleep 30
c 'setblock 2 200 2 minecraft:chest{Items:[{Slot:0,id:"minecraft:diamond",count:7}]}' "setblock 6 200 6 minecraft:gold_block" \
  "summon minecraft:armor_stand 4 200 4 {CustomName:'\"Persistente\"',NoGravity:1b,Invulnerable:1b}" \
  "execute in minecraft:the_nether run setblock 2 100 2 minecraft:gold_block" "execute in minecraft:the_end run setblock 2 70 2 minecraft:gold_block"; sleep 3
log "S1 marcadores colocados (Overworld cofre+bloque+entidad, Nether, End)"
# ---- S2 estructuras peligrosas desde el spawn (tope 70 s cada una)
: > $OUT/locate.txt
for e in bosses_of_mass_destruction:lich_tower bosses_of_mass_destruction:void_blossom cataclysm:cursed_pyramid cataclysm:frosted_prison iceandfire:fire_dragon_roost iceandfire:hydra_cave mowziesmobs:monastery dungeons_arise:shiraz_palace minecraft:stronghold; do
  L=$(( $(wc -l < $S/salida.log) + 1 )); c "execute in minecraft:overworld positioned 0 64 0 run locate structure $e"; r=""
  for i in $(seq 1 70); do r=$(tail -n +$L $S/salida.log | grep -E "nearest|Could not find|Unknown|not exist|Invalid" | head -1); [ -n "$r" ] && break; sleep 1; done
  echo "$e | $(echo "$r" | sed -E 's/^\[[^]]*\] \[[^]]*\]: //' | cut -c1-140)" | tee -a $OUT/locate.txt >> $R
done
# ---- C cliente
log "C: cliente Pruebas por QuickPlay"; cliente 127.0.0.1:25850; L0=1
esp "Pruebas joined the game" 300 || log "C: el cliente NO entró en 5 min"
if grep -q "Pruebas joined the game" $S/salida.log; then
  log "C conectado ($(( $(date +%s)-T0 )) s desde el inicio)"; sleep 20
  c "gamemode survival Pruebas" "effect give Pruebas minecraft:resistance infinite 4 true" "effect give Pruebas minecraft:saturation infinite 1 true"; sleep 2
  log "C guía de bienvenida en el inventario: $(cmdout 'execute if items entity Pruebas container.* minecraft:written_book' 2 1 | tr '\n' ' ' | cut -c1-120)"
  c "advancement grant Pruebas only purgatorio:bienvenida" ; sleep 1
  x key e 100; sleep 3; cap c01_inventario; x key Escape 100; sleep 1
  # combate cuerpo a cuerpo (Better Combat): espada de hierro, zombi delante
  c "tp Pruebas 8 201 8 facing 8 201 12" "give Pruebas minecraft:iron_sword" "summon minecraft:zombie 8 201 11 {NoAI:1b,PersistenceRequired:1b,Health:20f}"; sleep 3
  x key 1 100; sleep 1; for i in 1 2 3 4; do x click 1 120; sleep 0.7; done; sleep 1; cap c02_combate
  log "C combate: zombi tras 4 golpes -> $(cmdout 'data get entity @e[type=minecraft:zombie,limit=1,sort=nearest] Health' 2 1 | cut -c1-110)"
  # magia (Spell Engine): varita arcana en la mano, clic derecho mantenido
  c "kill @e[type=minecraft:zombie]" "give Pruebas wizards:wand_arcane" "summon minecraft:zombie 8 201 11 {NoAI:1b,PersistenceRequired:1b,Health:20f}"; sleep 3
  x key 2 100; sleep 1; x click 3 2500; sleep 1; cap c03_magia
  log "C magia (wand_arcane): zombi -> $(cmdout 'data get entity @e[type=minecraft:zombie,limit=1,sort=nearest] Health' 2 1 | cut -c1-110)"
  # tp en frío (Cauces): dos destinos lejanos, verificando que el servidor sigue respondiendo
  c "gamemode creative Pruebas"; sleep 1
  for d in "3000 3000" "-6000 2500"; do set -- $d; L=$(( $(wc -l < $S/salida.log) + 1 )); c "tp Pruebas $1 220 $2"; 
    esp "teletransporte de Pruebas a|cancelado" 100 $L && log "C tp frío a $d: $(tail -n +$L $S/salida.log | grep -E 'teletransporte de Pruebas' | head -1 | sed -E 's/^.*Cauces\/\]: //' | cut -c1-110)" || log "C tp frío a $d: SIN RESPUESTA en 100 s"
    sleep 12; cap c04_tp_$1; done
  # Nether y End
  c "execute in minecraft:the_nether run tp Pruebas 0 110 0"; sleep 40; cap c05_nether
  c "execute in minecraft:the_end run tp Pruebas 100 75 0"; sleep 40; cap c06_end
  c "execute in minecraft:overworld run tp Pruebas 4 202 4"; sleep 15
  log "C ping de tick: $(grep -c "Can't keep up" $S/salida.log) avisos «Can't keep up» en toda la sesión"
  # desconexión y reconexión
  log "C desconexión del cliente"; parar_cliente; sleep 8; c "list"; sleep 2
  cliente 127.0.0.1:25850; esp "Pruebas joined the game" 240 3 >/dev/null; sleep 30
  log "C reconexión: entradas de Pruebas en el registro = $(grep -c 'Pruebas joined the game' $S/salida.log); espada de hierro conservada: $(cmdout 'execute if items entity Pruebas container.* minecraft:iron_sword' 2 1 | tr '\n' ' ' | cut -c1-80)"
  cap c07_reconexion; cp $P/cli/logs/latest.log $OUT/cliente_partida.log
  log "C errores del cliente en partida: $(grep -c '/ERROR\]' $OUT/cliente_partida.log)"
  parar_cliente
fi
# ---- S3 parada segura
c "save-all flush"; esp "Saved the game" 90 >/dev/null; ti=$(date +%s)
python3 -I $S/parar.py $S --pid $PID --espera 150 --aviso 0 > $OUT/parar.txt 2>&1; rc=$?; log "S3 parar.py -> código $rc en $(( $(date +%s)-ti )) s: $(tail -1 $OUT/parar.txt | cut -c1-120)"
cp $S/logs/latest.log $OUT/servidor_sesion.log; pkill -x tail 2>/dev/null
log "S3 avisos de guardado de Cauces: $(grep -cE 'guardado completo|parada:' $OUT/servidor_sesion.log); líneas VIGÍA: $(grep -c VIGÍA $OUT/servidor_sesion.log)"
[ $rc != 0 ] && { log "S3 PARADA NO LIMPIA"; kill -9 $PID 2>/dev/null; }
# ---- S4 reinicio y persistencia
arrancar && { sleep 5; PID=$(pidsrv)
  log "S4 reabierto; cofre con 7 diamantes: $(cmdout 'execute if items block 2 200 2 container.0 minecraft:diamond' 2 1 | cut -c1-60 | tr '\n' ' ')"
  log "S4 bloque de oro: $(cmdout 'execute if block 6 200 6 minecraft:gold_block' 2 1 | cut -c1-60 | tr '\n' ' ')"
  log "S4 entidad «Persistente»: $(cmdout 'execute if entity @e[type=minecraft:armor_stand,name=Persistente]' 2 1 | cut -c1-60 | tr '\n' ' ')"
  log "S4 Nether: $(cmdout 'execute in minecraft:the_nether if block 2 100 2 minecraft:gold_block' 2 1 | cut -c1-50 | tr '\n' ' ') End: $(cmdout 'execute in minecraft:the_end if block 2 70 2 minecraft:gold_block' 2 1 | cut -c1-50 | tr '\n' ' ')"
  c "save-all flush"; esp "Saved the game" 60 >/dev/null; python3 -I $S/respaldo.py $S $P/respaldos > $OUT/respaldo.txt 2>&1; log "S5 respaldo en caliente: $(tail -2 $OUT/respaldo.txt | head -1 | cut -c1-100)"
  python3 -I $S/parar.py $S --pid $PID --espera 120 --aviso 0 > $OUT/parar2.txt 2>&1; log "S4 segunda parada: código $? ($(tail -1 $OUT/parar2.txt | cut -c1-80))"; pkill -x tail 2>/dev/null
} || log "S4 el servidor no reabrió"
log "S4 verificar_mundo (tras la parada): $(python3 -I $S/verificar_mundo.py $S/aceptacion 2>&1 | grep -E 'RESULTADO|jugador|Overworld|Nether|End' | tr '\n' '|' | cut -c1-300)"
log "FIN ($(( $(date +%s)-T0 )) s de reloj)"
