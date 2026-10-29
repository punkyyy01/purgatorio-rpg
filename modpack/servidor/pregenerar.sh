#!/bin/bash
# Pregenera el mundo del servidor dentro de un borde, con el comando integrado de NeoForge (sin mods extra).
# Uso (con el servidor arrancado y su consola en una FIFO o rcon): pregenerar.sh <radio_bloques> | <consola>
# Ejemplo: ./pregenerar.sh 3000 > ruta/a/consola.fifo
# Medido en el laboratorio (20 hilos, 0.5.0): ~19 chunks/s -> radio 3000 bloques ≈ 141 000 chunks ≈ 2 h.
R=${1:?radio en bloques}; C=$(( (R + 15) / 16 ))
echo "worldborder center 0 0"
echo "worldborder set $(( R * 2 ))"
echo "neoforge generate start 0 64 0 $C"
