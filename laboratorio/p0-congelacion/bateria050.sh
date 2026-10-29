#!/bin/bash
# Batería P0 (2026-10-28): se copia el script antes de cada prueba (editar un script en marcha lo rompe).
cd $HOME/dev/lab-p0
r(){ cp sp_vuelo.sh sp_vuelo_b.sh; env "$@" ./sp_vuelo_b.sh $E $J $T 32 > res2/$E.out 2>&1; }
E=ab041 J=purg4tory_cauces-0.4.1.jar T=900; r VUELO=cliente
./bordes050.sh dev2_050 $HOME/dev/lab-p0/jars/purg4tory_cauces-0.5.0-dev2.jar > res2/bordes050.out 2>&1
E=tp050 J=purg4tory_cauces-0.5.0-dev2.jar T=600; r VUELO=tp
E=largo050 J=purg4tory_cauces-0.5.0-dev2.jar T=2700; r VUELO=cliente GIRO=24
E=reabrir050 J=purg4tory_cauces-0.5.0-dev2.jar T=600; r VUELO=cliente REUSAR=p0v_largo050 YAW=90
echo BATERIA-FIN > res2/bateria050.fin
