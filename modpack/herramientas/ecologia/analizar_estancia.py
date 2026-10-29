#!/usr/bin/env python3
"""Analiza una prueba de estancia: entidades a <=80 bloques (horizontal) de cada bot en t0, t1, t2.
Uso: analizar_estancia.py <tablas.json> <dir_resultados> [<dir_resultados_2>]  -> tabla comparativa"""
import json, sys, glob, os, re, math
from collections import Counter, defaultdict
src = open(os.path.join(os.path.dirname(__file__), 'leer_censo.py')).read().split('dim, out = sys.argv')[0]
ns = {}; exec(compile(src, 'leer_censo', 'exec'), ns)
T = json.load(open(sys.argv[1]))
cat = defaultdict(set)
for cats in T['tab'].values():
    for c, l in cats.items():
        for e in l: cat[e['type']].add(c)
GANADO = {'minecraft:cow', 'minecraft:sheep', 'minecraft:pig', 'minecraft:chicken', 'meadow:wooly_cow', 'meadow:water_buffalo',
          'minecraft:mooshroom', 'friendsandfoes:moobloom'}
GRANDE = {'naturalist:' + x for x in ('deer', 'bear', 'black_bear', 'boar', 'zebra', 'giraffe', 'elephant', 'rhino', 'lion', 'hippo',
          'mammoth', 'tiger', 'alligator', 'komodo_dragon', 'ostrich', 'capybara')} | {'minecraft:' + x for x in
          ('horse', 'donkey', 'mule', 'llama', 'camel', 'polar_bear', 'panda', 'goat', 'wolf', 'sniffer')} | {'crittersandcompanions:red_panda'}
HOSTIL_NS = ('creeperoverhaul', 'endermanoverhaul', 'rottencreatures', 'cataclysm', 'mowziesmobs', 'bosses_of_mass_destruction', 'deeperdarker')
HOSTIL_EXTRA = {'netherexp:' + x for x in ('apparition', 'vessel', 'stampede', 'ecto_slab', 'banshee', 'carcass')} | {
    'artifacts:mimic', 'friendsandfoes:mauler', 'friendsandfoes:illusioner', 'friendsandfoes:iceologer', 'minecraft:hoglin', 'minecraft:piglin'}
def clase(e):
    c = cat.get(e, set())
    if e in GANADO: return 'ganado'
    if e in GRANDE: return 'grande'
    if 'monster' in c or e.split(':')[0] in HOSTIL_NS or e in HOSTIL_EXTRA: return 'hostil'
    if e.startswith('tide:') or c & {'water_creature', 'water_ambient', 'underground_water_creature'} or e in (
            'crittersandcompanions:otter', 'crittersandcompanions:koi_fish', 'crittersandcompanions:sea_bunny', 'crittersandcompanions:dumbo_octopus'):
        return 'agua'
    if c & {'creature', 'ambient'} or e.split(':')[0] in ('naturalist', 'crittersandcompanions', 'meadow') or e in (
            'minecraft:rabbit', 'minecraft:fox', 'minecraft:frog', 'minecraft:parrot', 'minecraft:bee', 'minecraft:armadillo',
            'minecraft:ocelot', 'minecraft:bat', 'minecraft:turtle', 'minecraft:strider', 'netherexp:wisp', 'netherexp:warphopper'):
        return 'pequeña'
    return None
def analizar(d):
    pts = {l.split()[0]: (int(l.split()[1]), int(l.split()[2]), l.split()[3]) for l in open(f'{d}/puntos.txt')}
    pos = {}
    for l in open(f'{d}/posiciones.log'):
        m = re.search(r'b_(\S+) has the following entity data: \[(-?[\d.]+)d, (-?[\d.]+)d, (-?[\d.]+)d\]', l)
        if m: pos[m.group(1)] = (float(m.group(2)), float(m.group(4)), float(m.group(3)))   # x, z, y (última conocida)
    res = {}
    for t in ('t0', 't1', 't2'):
        ents = {'ow': [], 'nether': []}
        for dimdir in ents:
            for r in glob.glob(f'{d}/{t}/{dimdir}/*.mca'):
                for c in ns['chunks'](r): ents[dimdir] += [(e['id'], e['Pos'][0], e['Pos'][2], e['Pos'][1]) for e in c.get('Entities', [])]
        for n, (x, z, dim) in pts.items():
            key = n[:14]; bx, bz, by = pos.get(key, (x, z, 64))
            lst = ents['nether' if 'nether' in dim else 'ow']
            cnt = Counter(); esp = Counter()
            for i, ex, ez, ey in lst:
                # SUPERFICIE: misma capa que el bot (de 12 bloques por debajo hacia arriba); 'sub' = cuevas
                if (ex-bx)**2 + (ez-bz)**2 <= 80*80 and (ey >= by - 12 or 'nether' in dim):
                    k = clase(i)
                    if k: cnt[k] += 1; esp[i] += 1
            res[(n, t)] = (cnt, esp)
    return pts, res
dirs = sys.argv[2:]
datos = [analizar(d) for d in dirs]
K = ['ganado', 'grande', 'pequeña', 'agua', 'hostil']
for (pts, res), d in zip(datos, dirs):
    print('\n##', os.path.basename(d.rstrip('/')))
    print(f"{'bioma':16} {'momento':7} " + ' '.join(f'{k:>8}' for k in K) + '  especies')
    for n in pts:
        for t in ('t0', 't1', 't2'):
            cnt, esp = res[(n, t)]
            print(f"{n:16} {t:7} " + ' '.join(f'{cnt[k]:8}' for k in K) + f"  {len([e for e in esp if clase(e)!='hostil'])}p/{len([e for e in esp if clase(e)=='hostil'])}h")
for (pts, res), d in zip(datos, dirs):
    tot = {t: Counter() for t in ('t0', 't1', 't2')}; especies = {t: set() for t in ('t0', 't1', 't2')}
    for (n, t), (cnt, esp) in res.items():
        tot[t].update(cnt); especies[t] |= {e for e in esp if clase(e) != 'hostil'}
    print(os.path.basename(d.rstrip('/')), 'TOTALES:', {t: dict(tot[t]) for t in tot}, 'especies no hostiles:', {t: len(especies[t]) for t in especies})
json.dump({os.path.basename(d.rstrip('/')): {f'{n}|{t}': [dict(c), dict(e)] for (n, t), (c, e) in r.items()} for (p, r), d in zip(datos, dirs)},
          open('resultados/estancia_resumen.json', 'w'), indent=1, ensure_ascii=False)
