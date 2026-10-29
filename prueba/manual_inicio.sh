#!/bin/bash
# Arranque manual (depuración de pruebas): servidor + un cliente Pruebas. Parar con manual_fin.sh
cd "$(dirname "$0")"; . ./lib.sh; xvfb; S=srv; F=$S/consola.fifo
rm -f $F; mkfifo $F; : > $S/salida.log; ( cd $S; exec 3>&-; tail -f consola.fifo | nice -n 15 ./run.sh nogui > salida.log 2>&1; echo FIN >> salida.log ) > /dev/null 2>&1 < /dev/null &
for i in $(seq 1 300); do grep -q 'Done (' $S/salida.log && break; sleep 1; done
cliente 127.0.0.1:25850 cli :87 Pruebas
for i in $(seq 1 240); do grep -q "Pruebas joined the game" $S/salida.log && break; sleep 3; done; sleep 25; echo listo
