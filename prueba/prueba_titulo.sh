#!/bin/bash
# T1: cliente desde un perfil limpio hasta la PANTALLA DE TÍTULO, SIN QuickPlay; captura y revisión de errores de módulos opcionales.
cd "$(dirname "$0")"; . ./lib.sh; xvfb; log "== T1 título sin QuickPlay"; t0=$(date +%s); cliente ""
for i in $(seq 1 200); do grep -q "Every Compat has loaded" cli/logs/latest.log 2>/dev/null && break; sleep 3; done
sleep 50; cap titulo; L=cli/logs/latest.log; cp $L $OUT/cliente_titulo.log
log "tiempo hasta el título: $(( $(date +%s)-t0 )) s"
log "Every Compat: $(grep -o 'Every Compat has loaded [0-9]* modules: .*' $L | head -1 | cut -c1-220)"
log "errores de módulo (encountered/ERRORED/NoClassDef): $(grep -ciE 'encountered an error|ERRORED|NoClassDefFound' $L)"
log "errores de textura de Every Compat (Promenade): $(grep -c 'Every Compat/\].*promenade' $L)"
log "ERROR totales en el registro del cliente: $(grep -c '/ERROR\]' $L)"
grep '/ERROR\]' $L | sed -E 's/^\[[^]]*\] //' | cut -c1-200 | sort | uniq -c | sort -rn | head -12 >> $R
parar_cliente; log FIN_T1
