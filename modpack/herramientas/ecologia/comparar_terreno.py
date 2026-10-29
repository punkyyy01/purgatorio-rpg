#!/usr/bin/env python3
"""Compara dos mundos generados con la misma semilla: para cada chunk completo presente en ambos,
compara la paleta de biomas por sección y el heightmap WORLD_SURFACE. Uso: comparar_terreno.py <mundoA> <mundoB>"""
import sys, os, glob
src = open(os.path.join(os.path.dirname(__file__), 'leer_censo.py')).read().split('dim, out = sys.argv')[0]
ns = {}; exec(compile(src, 'leer_censo', 'exec'), ns)
def cargar(m):
    out = {}
    for r in glob.glob(f'{m}/region/*.mca'):
        for c in ns['chunks'](r):
            if c.get('Status') != 'minecraft:full': continue
            bio = tuple((s['Y'], tuple(s['biomes']['palette']), tuple(s['biomes'].get('data', ()))) for s in c.get('sections', []) if 'biomes' in s)
            hm = tuple(c.get('Heightmaps', {}).get('WORLD_SURFACE_WG', ()) or c.get('Heightmaps', {}).get('OCEAN_FLOOR', ()))
            out[(c['xPos'], c['zPos'])] = (bio, hm)
    return out
A, B = cargar(sys.argv[1]), cargar(sys.argv[2])
comun = set(A) & set(B)
bio_ig = sum(A[k][0] == B[k][0] for k in comun); hm_ig = sum(A[k][1] == B[k][1] for k in comun)
print(f'chunks comunes {len(comun)}: biomas idénticos {bio_ig} ({100*bio_ig/max(len(comun),1):.1f} %), suelo idéntico {hm_ig} ({100*hm_ig/max(len(comun),1):.1f} %)')
