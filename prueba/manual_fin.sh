#!/bin/bash
cd "$(dirname "$0")"; . ./lib.sh; parar_cliente cli; parar_cliente cli2; PID=$(for p in /proc/[0-9]*; do [ "$(readlink $p/cwd 2>/dev/null)" = "$P/srv" ] && grep -q java $p/comm 2>/dev/null && echo ${p#/proc/}; done | head -1)
python3 -I srv/parar.py srv --pid $PID --espera 150 --aviso 0 | tail -2; pkill -x tail; pkill -x Xvfb; true
