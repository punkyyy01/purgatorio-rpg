#!/usr/bin/env python3
"""Fauna por 100 chunks de TIERRA, por familia de bioma, para varios mundos.
Uso: informe_familias.py <tablas.json> <etiqueta>=<mundo> ...
Bioma del chunk: el de (x+8, 100, z+8). Fauna = tipos de las listas creature/ambient de tablas.json."""
import json, sys, glob, math, os
from collections import Counter, defaultdict
src = open(os.path.join(os.path.dirname(__file__), 'leer_censo.py')).read().split('dim, out = sys.argv')[0]
ns = {}; exec(compile(src, 'leer_censo', 'exec'), ns); chunks, biome_at = ns['chunks'], ns['biome_at']
T = json.load(open(sys.argv[1])); tags = T['tags']
fauna = {e['type'] for cats in T['tab'].values() for c in ('creature', 'ambient') for e in cats.get(c, [])} | {'minecraft:bee'}
fam = [('agua', ['c:is_ocean', 'minecraft:is_ocean', 'minecraft:is_river', 'c:is_river']), ('costa', ['c:is_beach', 'minecraft:is_beach']),
       ('pantano', ['c:is_swamp']), ('jungla', ['c:is_jungle']), ('desierto', ['c:is_desert']), ('badlands', ['c:is_badlands']),
       ('sabana', ['c:is_savanna']), ('cumbres', ['c:is_mountain/peak']), ('nieve', ['c:is_snowy']), ('taiga', ['c:is_taiga']),
       ('bosque', ['c:is_forest']), ('llanura', ['c:is_plains']), ('montaña/colinas', ['c:is_mountain', 'c:is_hill', 'minecraft:is_mountain'])]
def familia(b):
    for n, ts in fam:
        if any(b in tags.get(t, []) for t in ts): return n
    return 'otros'
res = {}
for arg in sys.argv[2:]:
    et, mundo = arg.split('=', 1)
    ch = Counter(); fa = defaultdict(Counter); secs_by = {}
    for r in glob.glob(f'{mundo}/region/*.mca'):
        for c in chunks(r):
            if c.get('Status') != 'minecraft:full': continue
            secs = {s['Y']: s['biomes'] for s in c.get('sections', []) if 'biomes' in s}
            secs_by[(c['xPos'], c['zPos'])] = secs
            ch[familia(biome_at(secs, c['xPos']*16+8, 100, c['zPos']*16+8))] += 1
    for r in glob.glob(f'{mundo}/entities/*.mca'):
        for c in chunks(r):
            for e in c.get('Entities', []):
                if e['id'] not in fauna: continue
                x, y, z = (math.floor(v) for v in e['Pos'])
                s = secs_by.get((x >> 4, z >> 4))
                if s: fa[familia(biome_at(s, x, 100, z))][e['id']] += 1
    res[et] = (ch, fa)
ets = list(res)
print(f"{'familia':16}" + ''.join(f"{e:>22}" for e in ets))
tot = {e: [0, 0] for e in ets}
for f, _ in fam + [('otros', 0)]:
    row = f"{f:16}"
    for e in ets:
        ch, fa = res[e]; n = sum(fa[f].values()); row += f"{n:6}/{ch[f]:5}ch {100*n/max(ch[f],1):6.1f}"
        if f not in ('agua', 'costa'): tot[e][0] += n; tot[e][1] += ch[f]
    print(row)
print(f"{'TIERRA':16}" + ''.join(f"{t[0]:6}/{t[1]:5}ch {100*t[0]/max(t[1],1):6.1f}" for t in tot.values()))
for e in ets:
    c = Counter()
    for f in res[e][1]:
        if f not in ('agua', 'costa'): c.update(res[e][1][f])
    print(e, 'top:', ', '.join(f"{k}:{v}" for k, v in c.most_common(14)))
