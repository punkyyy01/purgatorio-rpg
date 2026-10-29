#!/usr/bin/env python3
"""Elige un punto en el INTERIOR de cada familia de bioma (todos los chunks a <=2 chunks son de la
misma familia) a partir de un mundo ya generado con la misma semilla. Puntos separados >= 400 bloques.
Uso: elegir_puntos.py <tablas.json> <dir_dimension> <prefijo_dim>"""
import json, sys, glob, os
src = open(os.path.join(os.path.dirname(__file__), 'leer_censo.py')).read().split('dim, out = sys.argv')[0]
ns = {}; exec(compile(src, 'leer_censo', 'exec'), ns)
T = json.load(open(sys.argv[1])); tags = T['tags']
fam_ow = [('rio', ['minecraft:is_river']), ('oceano', ['minecraft:is_ocean']), ('pantano', ['c:is_swamp']), ('jungla', ['c:is_jungle']),
          ('desierto', ['c:is_desert']), ('badlands', ['c:is_badlands']), ('sabana', ['c:is_savanna']), ('cumbres', ['c:is_mountain/peak']),
          ('nieve', ['c:is_snowy']), ('taiga', ['c:is_taiga']), ('bosque', ['c:is_forest']), ('llanura', ['c:is_plains']),
          ('montana', ['c:is_mountain', 'c:is_hill'])]
def fam(b):
    if b and b.startswith('minecraft:') and b.split(':')[1] in ('nether_wastes', 'crimson_forest', 'warped_forest', 'soul_sand_valley', 'basalt_deltas'):
        return b.split(':')[1]
    for n, ts in fam_ow:
        if any(b in tags.get(t, []) for t in ts): return n
    return None
R = int(sys.argv[4]) if len(sys.argv) > 4 else 2
y = 70 if sys.argv[3] == 'ow' else 60
F = {}
for r in glob.glob(f'{sys.argv[2]}/region/*.mca'):
    for c in ns['chunks'](r):
        if c.get('Status') != 'minecraft:full': continue
        secs = {s['Y']: s['biomes'] for s in c.get('sections', []) if 'biomes' in s}
        F[(c['xPos'], c['zPos'])] = fam(ns['biome_at'](secs, c['xPos']*16+8, y, c['zPos']*16+8))
elegidos = {}
for (cx, cz), f in sorted(F.items()):
    if not f or f in elegidos or f == 'oceano': continue
    if all(F.get((cx+dx, cz+dz)) == f for dx in range(-R, R+1) for dz in range(-R, R+1)):
        x, z = cx*16+8, cz*16+8
        if all(abs(x-a) >= 400 or abs(z-b) >= 400 for a, b in elegidos.values()):
            elegidos[f] = (x, z)
for f, (x, z) in elegidos.items(): print(f, x, z)
