#!/usr/bin/env python3
"""Genera el datapack prototipo purgatorio_fauna (biome modifiers de NeoForge, sin código).
Uso: generar_fauna.py <dir_salida>
1) Excluye de Naturalist (sus etiquetas blacklist) las especies que se reponderan.
2) Las vuelve a añadir con pesos nuevos en los mismos biomas (#naturalist:has_*), respetando
   la exclusión original de nieve/hielo de Naturalist.
3) Añade fauna de montaña (cabras en cumbres, wooly cows de Meadow en colinas/montañas)."""
import json, os, sys
out = sys.argv[1]
def w(path, data):
    p = os.path.join(out, path); os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(data, open(p, 'w'), indent=2, ensure_ascii=False); open(p, 'a').write('\n')
w('pack.mcmeta', {'pack': {'pack_format': 48, 'description': 'Purgatorio: ecología (pesos de fauna por bioma)'}})
FRIO = [{'type': 'neoforge:not', 'value': '#c:is_snowy'}, {'type': 'neoforge:not', 'value': '#c:is_icy'}]
# especie: (etiquetas has_ de Naturalist, entidad, peso, min, max, respetar exclusión de frío)
REPONDERA = {
    'pajaros':    (['bluejay', 'canary', 'cardinal', 'finch', 'robin', 'sparrow'], 'naturalist:bird', 5, 2, 3, False),
    'caracol':    (['snail'], 'naturalist:snail', 3, 1, 2, True),
    'rata':       (['rat'], 'naturalist:rat', 3, 1, 2, False),
    'topo':       (['mole'], 'naturalist:mole', 3, 1, 1, True),
    'lagarto':    (['lizard'], 'naturalist:lizard', 4, 1, 1, True),
    'serpiente':  (['snake', 'rattlesnake', 'coral_snake'], 'naturalist:snake', 4, 1, 1, True),
    'luciernaga': (['firefly'], 'naturalist:firefly', 6, 2, 3, True),
    'escorpion_desierto': (['desert_scorpion'], 'naturalist:desert_scorpion', 8, 1, 2, False),
    'escorpion_jungla':   (['jungle_scorpion'], 'naturalist:jungle_scorpion', 8, 1, 2, False),
    'avestruz':   (['ostrich'], 'naturalist:ostrich', 10, 1, 3, False),
    'pavo':       (['turkey'], 'naturalist:turkey', 10, 2, 3, False),
    'cebra':      (['zebra'], 'naturalist:zebra', 10, 2, 5, True),
    'jirafa':     (['giraffe'], 'naturalist:giraffe', 8, 1, 3, True),
    'leon':       (['lion'], 'naturalist:lion', 4, 2, 4, True),
}
for nombre, (tags, ent, peso, mn, mx, frio) in REPONDERA.items():
    for t in tags:
        w(f'data/naturalist/tags/worldgen/biome/blacklist/blacklist_{t}.json', {'replace': False, 'values': ['#minecraft:is_overworld']})
    base = [f'#naturalist:has_{t}' for t in tags]
    biomes = {'type': 'neoforge:and', 'values': [{'type': 'neoforge:or', 'values': base}] + FRIO} if frio else ({'type': 'neoforge:or', 'values': base} if len(base) > 1 else base[0])
    w(f'data/purgatorio/neoforge/biome_modifier/fauna/{nombre}.json',
      {'type': 'neoforge:add_spawns', 'biomes': biomes, 'spawners': {'type': ent, 'weight': peso, 'minCount': mn, 'maxCount': mx}})
# Hito 0.3.0: especies que Naturalist y Alex's Mobs tienen por duplicado; se deja la versión de Alex's Mobs
# (más comportamiento: carga, doma, interacción con su entorno) y se quita la de Naturalist.
for t in ('elephant', 'rhino', 'komodo_dragon', 'tiger', 'bear', 'alligator', 'blobfish', 'catfish'):
    w(f'data/naturalist/tags/worldgen/biome/blacklist/blacklist_{t}.json', {'replace': False, 'values': ['#minecraft:is_overworld']})
# Naturalist trae una libélula ambiental y Critters and Companions otra domesticable (necesaria para
# domar la araña saltarina): se deja solo la de Critters.
w('data/naturalist/tags/worldgen/biome/blacklist/blacklist_dragonfly.json', {'replace': False, 'values': ['#minecraft:is_overworld']})
w('data/purgatorio/neoforge/biome_modifier/fauna/cabras_cumbres.json',
  {'type': 'neoforge:add_spawns', 'biomes': '#c:is_mountain/peak', 'spawners': {'type': 'minecraft:goat', 'weight': 10, 'minCount': 2, 'maxCount': 3}})
w('data/purgatorio/neoforge/biome_modifier/fauna/vacas_lanudas_montana.json',
  {'type': 'neoforge:add_spawns', 'biomes': '#meadow:spawns_highland_cow', 'spawners': {'type': 'meadow:wooly_cow', 'weight': 8, 'minCount': 2, 'maxCount': 4}})
print('ok', out)
