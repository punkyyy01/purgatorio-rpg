#!/bin/bash
# Monta una instancia de cliente de pruebas (prueba/cli) desde bloqueo.json (153 mods) + overrides ya renderizados. Sin tocar nada fuera de prueba/.
set -e; cd "$(dirname "$0")"; M=../modpack; C=${1:-cli}
rm -rf $C; mkdir -p $C/mods $C/config
python3 -I - $M/bloqueo.json $C <<'PY'
import json, shutil, sys, os, hashlib
cache = os.path.expanduser('~/dev/modpack-cache/jars'); n = 0
for e in json.load(open(sys.argv[1]))['entradas']:
    f = f"{cache}/{e['fileID']}-{e['archivo']}"
    assert hashlib.sha1(open(f, 'rb').read()).hexdigest() == e['sha1'], f
    shutil.copy(f, f"{sys.argv[2]}/mods/{e['archivo']}"); n += 1
print(n, 'mods de cliente')
PY
python3 -I $M/herramientas/empaquetar.py $M /tmp/_x --materializar $C > /dev/null
rm -rf /tmp/_x; ls $C
cp ~/dev/purg4tory-090/cliente/inst2/options.txt $C/options.txt
