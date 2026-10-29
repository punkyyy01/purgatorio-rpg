#!/bin/bash
# Pruebas funcionales de bordes de chunk (sin cliente). Uso: bordes.sh <etiqueta> <jar de Cauces> [fases: LNGS]
L=$HOME/dev/lab-p0; E=$1; JAR=$2; FASES=${3:-LNGS}; O=$L/res/bordes_$E; rm -rf $O; mkdir -p $O; S=$L/srv; F=$S/consola.fifo
export PATH="$HOME/dev/tools/jdk-21.0.12.1+1/bin:$PATH"
log(){ echo "$(date +%H:%M:%S) $*" | tee -a $O/resumen.txt; }
c(){ printf '%s\n' "$@" > $F; }
q(){ local n=$(wc -l < $S/salida.log); c "$1"; sleep ${2:-2}; tail -n +$((n+1)) $S/salida.log | grep -E "${3:-\[P0\]|Unknown|Incorrect|error}" | sed -E 's/^\[[0-9:]+\] \[[^]]*\]: //' | head -3 | tr '\n' ' '; }
esperar_descarga(){ for i in $(seq 1 60); do q "p0 cargado $1 $2" 1 | grep -q "cargado=false" && return 0; done; return 1; }
arrancar(){ rm -f $F; mkfifo $F; : > $S/salida.log
  ( cd $S; exec 3>&-; tail -f consola.fifo | nice -n 5 ./run.sh nogui > salida.log 2>&1; echo FIN >> salida.log ) > /dev/null 2>&1 < /dev/null &
  for i in $(seq 1 400); do grep -qE 'Done \(|^FIN' $S/salida.log && break; sleep 1; done
  SP=$(for p in /proc/[0-9]*; do [ "$(readlink $p/cwd 2>/dev/null)" = "$S" ] && grep -q java $p/comm 2>/dev/null && echo ${p#/proc/}; done | head -1); }
parar(){ local t0=$(date +%s); c "stop"; for i in $(seq 1 240); do kill -0 $SP 2>/dev/null || break; sleep 1; done
  if kill -0 $SP 2>/dev/null; then jstack $SP > $O/jstack_parada.txt; kill -9 $SP; log "PARADA COLGADA (>240 s), proceso matado"; else log "parada en $(( $(date +%s)-t0 )) s"; fi
  for p in $(pgrep -f "tail -f consola.fifo"); do [ "$(readlink /proc/$p/cwd)" = "$S" ] && kill $p; done; }
rm -rf $S/p0 $S/purg4tory-congelacion-*.txt; rm -f $S/mods/purg4tory_cauces-*.jar $S/mods/purg4tory_diagp0-*.jar
cp $JAR $L/jars/purg4tory_diagp0-0.0.3.jar $S/mods/; log "Cauces: $(basename $JAR)"
arrancar; log "servidor: $(grep -o 'Done ([^)]*)' $S/salida.log)"
X=16000
cnt(){ q "p0 contar $X 100 $1 128" 2 | grep -oE 'lava [0-9]+ obsidiana [0-9]+ \|.*\)' | sed 's/  (?=no cargado u otro)//'; }
cargado(){ q "p0 cargado $1 $2" 1 | grep -oE 'cargado=[a-z]+'; }
if [[ $FASES == *L* ]]; then
  q "forceload add 15984 0 16127 31" 25 >/dev/null
  q "p0 armar $X 100 8 128" 4 >/dev/null; q "p0 armar $X 100 24 128" 4 >/dev/null
  log "L armadas (todo cargado): fila1 $(cnt 8) || fila2 $(cnt 24)"
  q "forceload remove all" 2 >/dev/null; q "forceload add $X 0" 3 >/dev/null     # solo el chunk 1000,0: cargados 998-1002, descargados 1003+
  esperar_descarga 1003 0 && esperar_descarga 1003 1 && log "L borde: 1002=$(cargado 1002 0) 1003=$(cargado 1003 0) (fila2: 1002=$(cargado 1002 1) 1003=$(cargado 1003 1))" || log "L AVISO: 1003 no se descargó"
  log "L antes del disparo (parte cargada): fila1 $(cnt 8)"
  log "L1 disparo normal con /setblock (como un jugador) en $X: $(q "setblock $X 100 8 minecraft:obsidian" 8 'Changed|Could not')"
  log "L1 justo después: $(cnt 8)   [1003=$(cargado 1003 0) 1007=$(cargado 1007 0)]"
  q "forceload add 16048 0 16127 15" 20 >/dev/null; log "L1 con 1003-1007 cargados: $(cnt 8)"
  log "L1 Cauces: $(q 'cauces_tp' 2 'cadenas' | grep -oE 'cadenas de terreno nuevo: [^;]*')"
  q "forceload remove 16048 0 16127 15" 2 >/dev/null
  if [[ $(basename $JAR) == *dev3* || $(basename $JAR) == *0.4.1.jar || $(basename $JAR) == *0.5.0* ]]; then
    esperar_descarga 1003 1 && log "L2 borde: 1002=$(cargado 1002 1) 1003=$(cargado 1003 1)" || log "L2 AVISO: 1003 no se descargó"
    log "L2 disparo en modo terreno nuevo en $X z=24: $(q "p0 disparar $X 100 24" 6 | grep -oE 'cadenas de terreno nuevo: .*')"
    log "L2 justo después: $(cnt 24)   [1003=$(cargado 1003 1)]"
    q "forceload add 16064 16" 15 >/dev/null; log "L2 tras cargar 1002-1006 (forzar 1004,1): $(cnt 24)"
    q "forceload add 16112 16" 15 >/dev/null; log "L2 tras cargar 1007: $(cnt 24)"
    log "L2 Cauces: $(q 'cauces_tp' 2 'cadenas' | grep -oE 'cadenas de terreno nuevo: [^;]*')"
  fi
  q "forceload remove all" 2 >/dev/null
fi
if [[ $FASES == *N* ]]; then
  q "forceload add 31984 0 32079 15" 25 >/dev/null
  q "fill 31990 99 0 32075 99 15 minecraft:stone" 3 >/dev/null
  q "setblock 32014 100 5 minecraft:sticky_piston[facing=east]" 1 >/dev/null; q "setblock 32015 100 5 minecraft:stone_bricks" 1 >/dev/null
  q "setblock 32016 99 9 minecraft:farmland" 1 >/dev/null; q "setblock 32016 100 9 minecraft:wheat[age=3]" 1 >/dev/null; q "setblock 32017 99 9 minecraft:water" 1 >/dev/null
  q "setblock 32014 100 9 minecraft:copper_bulb" 1 >/dev/null; q "setblock 32015 100 9 minecraft:observer[facing=east]" 3 >/dev/null
  q "fill 32008 100 11 32030 101 11 minecraft:glass" 1 >/dev/null; q "fill 32008 100 13 32030 101 13 minecraft:glass" 1 >/dev/null
  q "fill 32056 100 2 32067 100 2 minecraft:redstone_wire" 2 >/dev/null; q "setblock 32068 100 2 minecraft:redstone_lamp" 1 >/dev/null
  q "forceload remove all" 2 >/dev/null; q "forceload add 32000 0 32031 15" 3 >/dev/null   # 2000-2001 forzados; 2003 borde; 2004+ descargado
  esperar_descarga 2004 0 && log "N borde: 2003=$(cargado 2003 0) 2004=$(cargado 2004 0)" || log "N AVISO: 2004 no se descargó"
  q "setblock 32013 100 5 minecraft:redstone_block" 5 >/dev/null
  log "N pistón pegajoso (cruza 2000->2001): empujado a 32016 $(q 'execute if block 32016 100 5 minecraft:stone_bricks' 2 'Test passed|Test failed' | grep -oE 'Test [a-z]+')"
  q "setblock 32013 100 5 minecraft:air" 5 >/dev/null
  log "N pistón pegajoso: retraído a 32015 $(q 'execute if block 32015 100 5 minecraft:stone_bricks' 2 'Test passed|Test failed' | grep -oE 'Test [a-z]+')"
  g="$(q 'execute if block 32014 100 9 minecraft:copper_bulb[lit=true]' 2 'Test passed|Test failed' | grep -oE 'passed|failed')"
  for k in 4 5 7; do q "setblock 32016 100 9 minecraft:wheat[age=$k]" 3 >/dev/null; g="$g>$(q 'execute if block 32014 100 9 minecraft:copper_bulb[lit=true]' 2 'Test passed|Test failed' | grep -oE 'passed|failed')"; done
  [[ $g == passed\>failed\>passed\>failed || $g == failed\>passed\>failed\>passed ]] && r="Test passed" || r="Test failed"
  log "N granja (observador en 2000 ve crecer el trigo en 2001, la bombilla de cobre alterna en cada paso): $r ($g)"
  q "setblock 32010 100 12 minecraft:water" 8 >/dev/null
  log "N agua (cruza 2000->2001): 32016 $(q 'execute if block 32016 100 12 minecraft:water' 2 'Test passed|Test failed' | grep -oE 'Test [a-z]+'), 32017 $(q 'execute if block 32017 100 12 minecraft:water' 2 'Test passed|Test failed' | grep -oE 'Test [a-z]+'), 32018 vacío $(q 'execute if block 32018 100 12 minecraft:air' 2 'Test passed|Test failed' | grep -oE 'Test [a-z]+')"
  log "N redstone: bloque en 32055 (cable 32056-32067 cruza 2003->2004 descargado): $(q 'setblock 32055 100 2 minecraft:redstone_block' 3 'Changed' | grep -oE 'Changed')   [2004=$(cargado 2004 0)]"
  q "forceload add 32064 0" 15 >/dev/null
  log "N redstone con 2004 cargado: lámpara encendida $(q 'execute if block 32068 100 2 minecraft:redstone_lamp[lit=true]' 2 'Test passed|Test failed' | grep -oE 'Test [a-z]+'), cable 32066 con potencia $(q 'execute unless block 32066 100 2 minecraft:redstone_wire[power=0]' 2 'Test passed|Test failed' | grep -oE 'Test [a-z]+')"
  q "setblock 32055 100 2 minecraft:air" 3 >/dev/null
  log "N redstone apagado: cable 32066 sin potencia $(q 'execute if block 32066 100 2 minecraft:redstone_wire[power=0]' 2 'Test passed|Test failed' | grep -oE 'Test [a-z]+')"
  log "N Cauces: $(q 'cauces_tp' 2 'cadenas' | grep -oE 'cadenas de terreno nuevo: [^;]*')"
  q "forceload remove all" 2 >/dev/null
fi
if [[ $FASES == *S* ]]; then
  t0=$(date +%s); r=$(q 'save-all flush' 1 'xx'); for i in $(seq 1 120); do grep -q "Saved the game" $S/salida.log && break; sleep 1; done; log "S save-all flush: $(grep -c 'Saved the game' $S/salida.log) confirmado en $(( $(date +%s)-t0 )) s"
  parar; grep -E "parada:|guardado completo|Cauces/\]: .*(WARN|ERROR)" $S/logs/latest.log | sed -E 's/^\[[^]]*\] //' | cut -c1-160 | head -5 >> $O/resumen.txt
  cp $S/logs/latest.log $O/latest_1.log
  arrancar; log "S reabierto: $(grep -o 'Done ([^)]*)' $S/salida.log)"
  [[ $FASES == *L* ]] && { q "forceload add 15984 0 16127 31" 20 >/dev/null; log "S fila1 tras reabrir: $(cnt 8) || fila2 $(cnt 24)"; }
  [[ $FASES == *N* ]] && log "S pistón/agua/lámpara tras reabrir: $(q 'forceload add 32000 0 32079 15' 15 >/dev/null; q 'execute if block 32015 100 5 minecraft:stone_bricks' 2 'Test' | grep -oE 'Test [a-z]+') $(q 'execute if block 32017 100 12 minecraft:water' 2 'Test' | grep -oE 'Test [a-z]+') $(q 'execute if block 32068 100 2 minecraft:redstone_lamp' 2 'Test' | grep -oE 'Test [a-z]+')"
fi
parar; cp $S/logs/latest.log $O/latest.log
log "errores de Cauces: $(grep -E 'PURG4TORY Cauces' $O/latest*.log | grep -ciE 'ERROR|falló|exception'); excepciones del hilo principal: $(grep -c 'Server thread/ERROR' $O/latest.log)"
log FIN
