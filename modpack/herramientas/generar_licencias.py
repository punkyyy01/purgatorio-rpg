#!/usr/bin/env python3
"""Tabla de licencias y créditos de TODOS los archivos del pack, leída de los metadatos de cada jar (neoforge.mods.toml: license, authors).
Uso: python3 -I generar_licencias.py <bloqueo.json> <cache_jars> <salida.json>   (solo lectura; la licencia es la que DECLARA el jar)"""
import json, os, sys, tomllib, zipfile
b = json.load(open(sys.argv[1])); cache = sys.argv[2]; filas = []
SIN_REDIST = {636540, 448233, 1635121, 550579, 883374}
for e in sorted(b['entradas'], key=lambda e: e['titulo'].lower()):
    f = f"{cache}/{e['fileID']}-{e['archivo']}"; lic = '?'; aut = ', '.join(e.get('autores', []))
    try:
        z = zipfile.ZipFile(f); t = tomllib.loads(z.read('META-INF/neoforge.mods.toml').decode('utf8'))
        lic = (t.get('license') or '?').strip()
        if not aut:
            m = t.get('mods', [{}])[0]; aut = str(m.get('authors') or t.get('authors') or '')
    except Exception as ex: lic = f'?({type(ex).__name__})'
    filas.append({'titulo': e['titulo'], 'projectID': e['projectID'], 'licencia': lic, 'autores': aut, 'url': e['url'], 'archivo': e['archivo'],
                  'pilar': e['pilar'], 'redistribuible_por_terceros': e['projectID'] not in SIN_REDIST})
json.dump(filas, open(sys.argv[3], 'w'), indent=1, ensure_ascii=False)
from collections import Counter
print(Counter(f['licencia'] for f in filas).most_common())
