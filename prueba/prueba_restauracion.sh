#!/bin/bash
# S5: restaurar el último respaldo en una instalación SEPARADA (prueba/srv_rest, puerto 25852), comprobar marcadores y estructura del mundo.
cd "$(dirname "$0")"; . ./lib.sh; S=srv_rest; F=$S/consola.fifo; c() { printf '%s\n' "$@" > $F; }
T=$(ls -t respaldos/mundo-*.tar.gz | head -1); log "S5 restauración de $(basename $T) en $S"
( cd respaldos && sha256sum -c $(basename $T).sha256 ) >/dev/null 2>&1 && log "S5 SHA-256 del respaldo: correcto" || log "S5 SHA-256 del respaldo: FALLA"
rm -rf $S; mkdir -p $S; tar xzf $T -C $S
for d in libraries mods; do ln -s $P/srv/$d $S/$d; done; cp srv/run.sh srv/user_jvm_args.txt srv/eula.txt $S/ 2>/dev/null
sed -i 's/^server-port=.*/server-port=25852/; s/^rcon.port=.*/rcon.port=25853/' $S/server.properties
python3 -I $S/../srv/verificar_mundo.py $S/aceptacion | tail -8 | tee -a $R
rm -f $F; mkfifo $F; : > $S/salida.log; ( cd $S; exec 3>&-; tail -f consola.fifo | nice -n 15 ./run.sh nogui > salida.log 2>&1; echo FIN >> salida.log ) > /dev/null 2>&1 < /dev/null &
for i in $(seq 1 300); do grep -qE 'Done \(|^FIN' $S/salida.log && break; sleep 1; done; grep -q 'Done (' $S/salida.log && log "S5 instalación restaurada arrancada ($(grep -o 'Done ([0-9.]*s)' $S/salida.log))" || { log "S5 NO ARRANCA"; exit 1; }
out() { local L=$(( $(wc -l < $S/salida.log) + 1 )); c "$1"; sleep 2; tail -n +$L $S/salida.log | sed -E 's/^\[[0-9:]+\] \[[^]]*\] //' | head -1 | cut -c1-70; }
c "forceload add 0 0"; sleep 5
log "S5 restaurado — cofre 7 diamantes: $(out 'execute if items block 2 200 2 container.0 minecraft:diamond') | bloque oro: $(out 'execute if block 6 200 6 minecraft:gold_block') | entidad: $(out 'execute if entity @e[type=minecraft:armor_stand,name=Persistente]')"
log "S5 restaurado — Nether: $(out 'execute in minecraft:the_nether if block 2 100 2 minecraft:gold_block') | End: $(out 'execute in minecraft:the_end if block 2 70 2 minecraft:gold_block')"
log "S5 restaurado — datos del jugador Pruebas (inventario): $(ls $S/aceptacion/playerdata | wc -l) archivos de jugador"
c "save-all flush"; sleep 4; c stop; for i in $(seq 1 120); do grep -q '^FIN' $S/salida.log && break; sleep 1; done; grep -q '^FIN' $S/salida.log && log "S5 parada limpia de la instalación restaurada" || log "S5 PARADA COLGADA"; pkill -x tail; true
