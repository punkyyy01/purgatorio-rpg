#!/bin/bash
# Confirmación con el jar definitivo de Cauces 0.5.0 (incluye M4 y freno de vehículos). Espera a la batería anterior.
cd $HOME/dev/lab-p0
until [ -e res2/bateria050.fin ]; do sleep 20; done
r(){ cp sp_vuelo.sh sp_vuelo_f.sh; env "$@" ./sp_vuelo_f.sh $E $J $T 32 > res2/$E.out 2>&1; }
E=fin050 J=purg4tory_cauces-0.5.0.jar T=900; r VUELO=cliente
E=fintp050 J=purg4tory_cauces-0.5.0.jar T=600; r VUELO=tp
./bordes050.sh fin050 $HOME/dev/lab-p0/jars/purg4tory_cauces-0.5.0.jar > res2/bordesfin050.out 2>&1
echo FIN > res2/bateria_final.fin
