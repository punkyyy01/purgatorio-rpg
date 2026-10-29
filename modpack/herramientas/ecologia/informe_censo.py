#!/usr/bin/env python3
"""Resume un censo por familia de biomas: chunks, fauna (categoría creature/ambient) por 100 chunks, especies.
Uso: informe_censo.py <tablas.json> <censo.json> [<censo_base.json>]"""
import json, sys
from collections import Counter, defaultdict
T = json.load(open(sys.argv[1])); C = json.load(open(sys.argv[2]))
tags = T['tags']; tab = T['tab']
fauna = set()
for b, cats in tab.items():
    for cat in ('creature', 'ambient'):
        for e in cats.get(cat, []): fauna.add(e['type'])
fauna |= {'minecraft:bee', 'minecraft:polar_bear'}
fam = [('Océano', ['c:is_ocean', 'minecraft:is_ocean']), ('Playa/costa', ['c:is_beach', 'minecraft:is_beach']), ('Río', ['minecraft:is_river']),
       ('Pantano', ['c:is_swamp']), ('Jungla', ['c:is_jungle']), ('Desierto', ['c:is_desert']), ('Badlands', ['c:is_badlands']),
       ('Sabana', ['c:is_savanna']), ('Cumbres/picos', ['c:is_mountain/peak', 'minecraft:is_mountain']),
       ('Nieve', ['c:is_snowy']), ('Taiga', ['c:is_taiga']), ('Bosque', ['c:is_forest']), ('Llanura/pradera', ['c:is_plains']), ('Colinas', ['c:is_hill'])]
def familia(b):
    for n, ts in fam:
        if any(b in tags.get(t, []) for t in ts): return n
    return 'Otros'
chunks = Counter(); anim = defaultdict(Counter)
for b, n in C['chunks_por_bioma'].items(): chunks[familia(b)] += n
for b, ents in C['por_bioma'].items():
    for e, n in ents.items():
        if e in fauna: anim[familia(b)][e] += n
print(f"{'Familia':16} {'chunks':>7} {'fauna':>6} {'/100ch':>7}  especies principales")
for f, n in chunks.most_common():
    a = anim[f]; tot = sum(a.values())
    top = ', '.join(f"{k.split(':')[1]}:{v}" for k, v in a.most_common(9))
    print(f"{f:16} {n:7} {tot:6} {100*tot/max(n,1):7.1f}  {top}")
tot = Counter()
for f in anim: tot.update(anim[f])
mods = Counter(); 
for e, n in tot.items(): mods[e.split(':')[0]] += n
print('\nFauna total', sum(tot.values()), 'por mod:', dict(mods.most_common()))
otros = Counter()
for b, ents in C['por_bioma'].items():
    for e, n in ents.items():
        if e not in fauna: otros[e] += n
print('No fauna (estructuras/hostiles):', otros.most_common(25))
