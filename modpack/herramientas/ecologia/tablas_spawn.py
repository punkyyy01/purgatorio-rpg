#!/usr/bin/env python3
"""Tabla efectiva de spawns por bioma (estática): biomas vanilla/mods + modificadores JSON
+ Naturalist, Friends&Foes y Meadow (registrados por código, valores por defecto).
Uso: tablas_spawn.py <dir_extraido> <naturalist.tsv> <salida.json>
El orden de carga aproxima el de NeoForge: vanilla, neoforge, mods."""
import json, os, sys, glob
X, NAT, OUT = sys.argv[1:4]
fuentes = ['vanilla', 'neoforge'] + sorted(d for d in os.listdir(X) if d.isdigit())
def rid(path, kind):  # data/<ns>/<kind>/<rest>.json -> ns:rest
    p = path.split('/data/', 1)[1].split('/'); ns = p[0]
    k = kind.split('/'); rest = p[1 + len(k):]
    return ns + ':' + '/'.join(rest)[:-5]
biomes, tags = {}, {}
for f in fuentes:
    for p in glob.glob(f'{X}/{f}/data/*/worldgen/biome/**/*.json', recursive=True):
        try: biomes[rid(p, 'worldgen/biome')] = json.load(open(p))
        except Exception: pass
    for p in glob.glob(f'{X}/{f}/data/*/tags/worldgen/biome/**/*.json', recursive=True):
        try: d = json.load(open(p))
        except Exception: continue
        k = rid(p, 'tags/worldgen/biome')
        vals = [v['id'] if isinstance(v, dict) else v for v in d.get('values', [])]
        tags[k] = vals if d.get('replace') else tags.get(k, []) + vals
def resolve(ref, seen=()):
    if isinstance(ref, list): return set().union(*(resolve(r, seen) for r in ref)) if ref else set()
    if ref.startswith('#'):
        t = ref[1:]
        if t in seen: return set()
        return set().union(set(), *(resolve(v, seen + (t,)) for v in tags.get(t, [])))
    return {ref} if ref in biomes else set()
tab = {b: {cat: [dict(e, fuente='base') for e in lst] for cat, lst in d.get('spawners', {}).items()} for b, d in biomes.items()}
def add(bs, cat, ent, w, mn, mx, fuente):
    for b in bs: tab[b].setdefault(cat, []).append({'type': ent, 'weight': w, 'minCount': mn, 'maxCount': mx, 'fuente': fuente})
removes = []
for f in fuentes:
    for p in glob.glob(f'{X}/{f}/data/*/neoforge/biome_modifier/**/*.json', recursive=True):
        try: d = json.load(open(p))
        except Exception: continue
        t = d.get('type'); mod = p.split('/data/')[1].split('/')[0]
        if t == 'neoforge:add_spawns':
            sp = d['spawners']; sp = sp if isinstance(sp, list) else [sp]
            for s in sp:
                cat = 'monster'  # categoría real = la del tipo de entidad; se corrige abajo
                add(resolve(d['biomes']), '?', s['type'], s['weight'], s['minCount'], s['maxCount'], mod)
        elif t == 'neoforge:remove_spawns':
            ents = d['entity_types']; removes.append((resolve(d['biomes']), set(resolve_e for resolve_e in ([ents] if isinstance(ents, str) else ents)), mod))
# Naturalist
for l in open(NAT):
    tag, cat, ent, w, mn, mx = l.split('\t'); t = tag[4:].lower()
    bs = resolve('#naturalist:has_' + t) - resolve('#naturalist:blacklist/blacklist_' + t)
    add(bs, cat.lower(), 'naturalist:' + ent.lower(), int(w), int(mn), int(mx), 'naturalist')
# Friends & Foes (valores por defecto de friendsandfoes.json)
for t, cat, ent, w, mn, mx in [('has_barnacle','monster','barnacle',4,1,1),('has_crab','creature','crab',14,2,4),('has_glare','glare','glare',4,1,1),
        ('has_badlands_mauler','creature','mauler',16,1,1),('has_desert_mauler','creature','mauler',8,1,1),('has_savanna_mauler','creature','mauler',32,1,1),
        ('has_mooblooms','creature','moobloom',4,2,4),('has_penguin','creature','penguin',4,4,8),('has_rascal','rascal','rascal',4,1,1)]:
    add(resolve('#friendsandfoes:' + t), cat, 'friendsandfoes:' + ent, w, mn, mx, 'friendsandfoes')
# Meadow (config por defecto)
add(resolve('#meadow:is_meadow') | resolve('#meadow:spawns_umbra_cow'), 'creature', 'meadow:wooly_cow', 14, 3, 6, 'meadow')
add(resolve('#meadow:spawns_buffalo'), 'creature', 'meadow:water_buffalo', 8, 2, 3, 'meadow')
for bs, ents, mod in removes:
    for b in bs:
        for cat in tab[b]: tab[b][cat] = [e for e in tab[b][cat] if e['type'] not in ents]
json.dump({'tab': tab, 'prob': {b: d.get('creature_spawn_probability', 0.1) for b, d in biomes.items()},
           'tags': {k: sorted(resolve('#' + k)) for k in tags}}, open(OUT, 'w'), indent=0)
print(len(biomes), 'biomas', len(tags), 'etiquetas')
