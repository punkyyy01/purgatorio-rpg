#!/bin/bash
# Ayudante de pruebas: srv.sh start|cmd "<comando>"|stop   (servidor en prueba/srv, consola por FIFO)
cd "$(dirname "$0")/srv"; export PATH="$HOME/dev/tools/jdk-21.0.12.1+1/bin:$PATH"
case $1 in
start) rm -f consola.fifo; mkfifo consola.fifo; : > salida.log
  ( exec 3>&-; tail -f consola.fifo | nice -n 15 ./run.sh nogui > salida.log 2>&1; echo FIN >> salida.log ) > /dev/null 2>&1 < /dev/null &
  for i in $(seq 1 ${2:-300}); do grep -qE 'Done \(|^FIN' salida.log && break; sleep 1; done; grep -E 'Done \(' salida.log | tail -1;;
cmd) shift; printf '%s\n' "$@" > consola.fifo;;
esac
