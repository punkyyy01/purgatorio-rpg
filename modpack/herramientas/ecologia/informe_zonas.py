#!/usr/bin/env python3
"""Fauna por zona (cuadro de 256x256 bloques centrado en cada zona de zonas.txt).
Uso: informe_zonas.py <tablas.json> <zonas.txt> <mundo> [<mundo_b>]
Cuenta entidades de categoría creature/ambient (según tablas.json) guardadas en entities/*.mca."""
import json, sys, glob, math, os
from collections import Counter
src = open(os.path.join(os.path.dirname(__file__), 'leer_censo.py')).read().split('dim, out = sys.argv')[0]
ns = {}; exec(compile(src, 'leer_censo', 'exec'), ns); chunks = ns['chunks']
T = json.load(open(sys.argv[1]))
fauna = {e['type'] for cats in T['tab'].values() for c in ('creature', 'ambient') for e in cats.get(c, [])}
fauna |= {'minecraft:bee', 'minecraft:polar_bear'}
zonas = [(n, int(x), int(z)) for n, x, z in (l.split() for l in open(sys.argv[2]) if l.strip())]
def censo(mundo):
    res = {n: [0, Counter()] for n, _, _ in zonas}
    def zona(x, z):
        for n, cx, cz in zonas:
            if cx - 128 <= x < cx + 128 and cz - 128 <= z < cz + 128: return n
    for r in glob.glob(f'{mundo}/region/*.mca'):
        for c in chunks(r):
            if c.get('Status') == 'minecraft:full':
                n = zona(c['xPos'] * 16 + 8, c['zPos'] * 16 + 8)
                if n: res[n][0] += 1
    for r in glob.glob(f'{mundo}/entities/*.mca'):
        for c in chunks(r):
            for e in c.get('Entities', []):
                if e['id'] in fauna:
                    n = zona(math.floor(e['Pos'][0]), math.floor(e['Pos'][2]))
                    if n: res[n][1][e['id']] += 1
    return res
A = censo(sys.argv[3]); B = censo(sys.argv[4]) if len(sys.argv) > 4 else None
ta = tb = ca = cb = 0
for n, _, _ in zonas:
    ch, cnt = A[n]; t = sum(cnt.values()); ta += t; ca += ch
    lin = f"{n:26} {ch:4}ch {t:4} ({100*t/max(ch,1):5.1f}/100)"
    if B:
        chb, cntb = B[n]; tb2 = sum(cntb.values()); tb += tb2; cb += chb
        lin += f" | B {chb:4}ch {tb2:4} ({100*tb2/max(chb,1):5.1f}/100)"
    print(lin + '  ' + ', '.join(f"{k.split(':')[1]}:{v}" for k, v in cnt.most_common(7)))
print(f"TOTAL A {ta} en {ca} chunks ({100*ta/max(ca,1):.1f}/100)" + (f" | B {tb} en {cb} chunks ({100*tb/max(cb,1):.1f}/100)" if B else ''))
