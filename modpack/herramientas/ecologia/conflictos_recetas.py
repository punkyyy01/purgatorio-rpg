#!/usr/bin/env python3
"""Detecta recetas de crafteo con la misma entrada y distinto resultado entre mods.
Uso: conflictos_recetas.py <bloqueo.json> <dir_jars> [datapack_dir...]
Normaliza recetas shaped (patrón + claves) y shapeless (multiconjunto). Ignora recetas con
condiciones neoforge (pueden no cargarse) y las anuladas por datapacks indicados."""
import zipfile, json, glob, sys, os
from collections import defaultdict
bloq = json.load(open(sys.argv[1])); jars = sys.argv[2]; packs = sys.argv[3:]
anuladas = set()
for p in packs:
    for f in glob.glob(f'{p}/data/*/recipe/**/*.json', recursive=True):
        d = json.load(open(f))
        if any(c.get('type') == 'neoforge:false' for c in d.get('neoforge:conditions', [])):
            ns = f.split('/data/')[1].split('/')[0]; anuladas.add(ns + ':' + f.split('/recipe/')[1][:-5])
def ing(x):
    if isinstance(x, list): return '|'.join(sorted(ing(i) for i in x))
    if isinstance(x, dict): return x.get('item') or ('#' + x['tag']) if ('item' in x or 'tag' in x) else json.dumps(x, sort_keys=True)
    return str(x)
firmas = defaultdict(list)
for e in bloq['entradas']:
    j = glob.glob(f"{jars}/{e['fileID']}-*")[0]
    z = zipfile.ZipFile(j)
    for n in z.namelist():
        if '/recipe/' not in n or not n.endswith('.json') or not n.startswith('data/'): continue
        rid = n.split('/')[1] + ':' + n.split('/recipe/')[1][:-5]
        if rid in anuladas: continue
        try: d = json.loads(z.read(n))
        except Exception: continue
        if 'neoforge:conditions' in d or 'conditions' in d: continue
        t = d.get('type'); res = d.get('result')
        res = (res.get('id') or res.get('item')) if isinstance(res, dict) else res
        if t == 'minecraft:crafting_shaped':
            pat = d.get('pattern', []); key = {k: ing(v) for k, v in d.get('key', {}).items()}
            firma = 'S:' + '/'.join(''.join(key.get(ch, '_') + ',' for ch in fila) for fila in pat)
        elif t == 'minecraft:crafting_shapeless':
            firma = 'L:' + ','.join(sorted(ing(i) for i in d.get('ingredients', [])))
        else: continue
        firmas[firma].append((rid, res, e['titulo']))
n = 0
for f, l in firmas.items():
    if len({r for _, r, _ in l}) > 1 and len({m for _, _, m in l}) > 1:
        n += 1; print(f[:110]); [print('   ', x) for x in l]
print(n, 'conflictos entre mods distintos')
