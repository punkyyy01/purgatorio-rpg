#!/usr/bin/env python3
"""Segunda fuente: busca el SHA-1 de cada jar de bloqueo.json en Modrinth.
Si Modrinth tiene un archivo idéntico, anota proyecto y versión. Uso: verificar_modrinth.py <dir_modpack>"""
import json, sys, urllib.parse, urllib.request
from pathlib import Path
mp = Path(sys.argv[1]); b = json.load(open(mp / 'bloqueo.json'))
hashes = [e['sha1'] for e in b['entradas']]
req = urllib.request.Request('https://api.modrinth.com/v2/version_files', method='POST',
      data=json.dumps({'hashes': hashes, 'algorithm': 'sha1'}).encode(),
      headers={'User-Agent': 'punkyyy01/purgatorio-rpg modpack build', 'Content-Type': 'application/json'})
r = json.load(urllib.request.urlopen(req, timeout=60))
n = 0
for e in b['entradas']:
    v = r.get(e['sha1'])
    e['modrinth'] = {'project_id': v['project_id'], 'version': v['version_number']} if v else None
    n += bool(v)
json.dump(b, open(mp / 'bloqueo.json', 'w'), indent=1, ensure_ascii=False)
print(f'{n}/{len(hashes)} jars idénticos en Modrinth')

# Licencias según Modrinth (CFWidget no las da) para los jars que coinciden
ids = sorted({e['modrinth']['project_id'] for e in b['entradas'] if e.get('modrinth')})
req = urllib.request.Request('https://api.modrinth.com/v2/projects?ids=' + urllib.parse.quote(json.dumps(ids)),
      headers={'User-Agent': 'punkyyy01/purgatorio-rpg modpack build'})
lic = {p['id']: p['license']['id'] for p in json.load(urllib.request.urlopen(req, timeout=60))}
for e in b['entradas']:
    if e.get('modrinth'):
        e['licencia'] = lic.get(e['modrinth']['project_id'])
json.dump(b, open(mp / 'bloqueo.json', 'w'), indent=1, ensure_ascii=False)
