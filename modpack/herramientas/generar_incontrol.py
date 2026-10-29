#!/usr/bin/env python3
"""Genera las reglas de In Control! (1.21-10.3.0) del pack.
Uso: generar_incontrol.py <dir_overrides>

spawner.json (Fase A): reposición suave de fauna cerca de cada jugador. In Control! la evalúa una vez
por segundo por regla; cada especie de la lista se intenta con probabilidad persecond * peso/peso_máx.
Topes: `maxlocal` cuenta esa especie en una caja de ±(maxdist+1) bloques alrededor del jugador
(incluye la fauna que generó el mundo), y `maxpeaceful` es un freno global de animales cargados en la
dimensión (si hay granjas enormes, la reposición se detiene en vez de saturar).
No se usa `mobsfrombiome`: con él `maxlocal` no funciona y las granjas de los jugadores bloquearían la
reposición.

spawn.json (Fase B): solo afecta a apariciones naturales (`spawntype: natural`); no toca spawners,
estructuras, jefes ni la generación del mundo.
"""
import json, os, sys

out = os.path.join(sys.argv[1], 'config', 'incontrol')
os.makedirs(out, exist_ok=True)

# familia: (etiquetas de bioma, [(entidad, peso relativo, máximo cerca del jugador)])
FAMILIAS = {
    'llanura':  (['c:is_plains'], [('minecraft:cow', 1.0, 3), ('minecraft:sheep', 1.0, 3), ('minecraft:pig', 0.8, 3),
                                   ('minecraft:chicken', 0.8, 3), ('minecraft:horse', 0.4, 2),
                                   ('naturalist:hedgehog', 0.3, 1), ('crittersandcompanions:ferret', 0.3, 2)]),
    'bosque':   (['c:is_forest'], [('naturalist:deer', 1.0, 3), ('naturalist:boar', 0.7, 3), ('minecraft:sheep', 0.6, 3),
                                   ('minecraft:chicken', 0.6, 3), ('minecraft:rabbit', 0.5, 2), ('naturalist:turkey', 0.4, 2),
                                   ('naturalist:black_bear', 0.25, 1), ('alexsmobs:raccoon', 0.3, 2)]),
    'taiga':    (['c:is_taiga'], [('naturalist:deer', 0.8, 3), ('minecraft:wolf', 0.6, 3), ('minecraft:fox', 0.6, 2),
                                  ('minecraft:rabbit', 0.6, 3), ('minecraft:sheep', 0.5, 3), ('alexsmobs:grizzly_bear', 0.25, 1),
                                  ('alexsmobs:moose', 0.2, 1)]),
    'sabana':   (['c:is_savanna'], [('naturalist:zebra', 1.0, 4), ('naturalist:giraffe', 0.6, 2), ('naturalist:ostrich', 0.6, 2),
                                    ('alexsmobs:elephant', 0.4, 2), ('minecraft:horse', 0.4, 2), ('alexsmobs:rhinoceros', 0.2, 1),
                                    ('alexsmobs:gazelle', 0.6, 3),
                                    ('naturalist:lion', 0.15, 1)]),
    'pantano':  (['c:is_swamp'], [('minecraft:frog', 1.0, 4), ('naturalist:duck', 0.8, 3), ('naturalist:capybara', 0.6, 3),
                                  ('naturalist:tortoise', 0.4, 2), ('alexsmobs:shoebill', 0.2, 1),
                                  ('alexsmobs:crocodile', 0.15, 1)]),
    'jungla':   (['c:is_jungle'], [('minecraft:parrot', 1.0, 3), ('crittersandcompanions:red_panda', 0.5, 2),
                                   ('naturalist:capybara', 0.4, 2), ('minecraft:chicken', 0.4, 2), ('minecraft:ocelot', 0.2, 1),
                                   ('alexsmobs:toucan', 0.5, 2), ('alexsmobs:gorilla', 0.3, 2), ('alexsmobs:capuchin_monkey', 0.3, 2)]),
    'nieve':    (['c:is_snowy'], [('minecraft:rabbit', 1.0, 3), ('minecraft:fox', 0.6, 2),
                                  ('crittersandcompanions:shima_enaga', 0.6, 3), ('minecraft:polar_bear', 0.15, 1),
                                  ('naturalist:mammoth', 0.15, 1)]),
    'montana':  (['c:is_mountain'], [('minecraft:goat', 1.0, 3), ('meadow:wooly_cow', 0.6, 3), ('minecraft:llama', 0.5, 2),
                                     ('minecraft:sheep', 0.5, 3)]),
    'desierto': (['c:is_desert'], [('minecraft:rabbit', 1.0, 2), ('minecraft:camel', 0.3, 1), ('naturalist:lizard', 0.3, 1),
                                   ('naturalist:tortoise', 0.2, 1), ('alexsmobs:roadrunner', 0.3, 1)]),
    'badlands': (['c:is_badlands'], [('minecraft:armadillo', 1.0, 2), ('minecraft:rabbit', 0.5, 2)]),
    'rio':      (['c:is_river'], [('crittersandcompanions:otter', 1.0, 3), ('naturalist:duck', 0.6, 2)]),
}
# Hito 0.4.0: biomas terrestres sin ninguna etiqueta de FAMILIAS (sobre todo de Terralith y los «windswept» de
# vanilla) se quedaban sin reposición. Se cubren por nombre, con especies de su propia lista natural de aparición.
# Se dejan sin reposición a propósito los biomas inhóspitos sin fauna propia: acantilados de basalto, granito y
# creta, mesa deformada y costa pedregosa.
FAMILIAS_BIOMAS = {
    'matorral': (['terralith:shrubland', 'terralith:hot_shrubland'],
                 [('minecraft:sheep', 1.0, 3), ('minecraft:cow', 0.7, 3), ('minecraft:horse', 0.5, 2),
                  ('naturalist:boar', 0.6, 2), ('minecraft:armadillo', 0.3, 1), ('naturalist:lizard', 0.3, 1)]),
    'colinas':  (['minecraft:windswept_hills', 'minecraft:windswept_forest', 'minecraft:windswept_gravelly_hills',
                  'terralith:haze_mountain', 'terralith:windswept_spires'],
                 [('minecraft:sheep', 1.0, 3), ('minecraft:cow', 0.6, 3), ('minecraft:pig', 0.5, 2),
                  ('minecraft:llama', 0.5, 2), ('minecraft:chicken', 0.4, 2)]),
    'valle':    (['terralith:lush_valley', 'terralith:valley_clearing', 'terralith:shield_clearing',
                  'terralith:yosemite_cliffs', 'terralith:yellowstone', 'terralith:blooming_plateau'],
                 [('minecraft:cow', 1.0, 3), ('minecraft:sheep', 0.8, 3), ('minecraft:pig', 0.6, 2),
                  ('minecraft:horse', 0.4, 2), ('minecraft:fox', 0.4, 2), ('minecraft:rabbit', 0.4, 2),
                  ('minecraft:wolf', 0.3, 2), ('naturalist:deer', 0.5, 3)]),
    'islas':    (['terralith:alpha_islands', 'terralith:alpha_islands_winter', 'terralith:mirage_isles'],
                 [('minecraft:sheep', 1.0, 3), ('minecraft:cow', 0.7, 3), ('minecraft:pig', 0.6, 2), ('minecraft:chicken', 0.5, 2)]),
    'agujas':   (['terralith:stony_spires'], [('minecraft:goat', 1.0, 3), ('minecraft:sheep', 0.5, 2)]),
    'hongos':   (['minecraft:mushroom_fields'], [('minecraft:mooshroom', 1.0, 3)]),
}
# Hito 2 (0.9.0): fauna para biomas nuevos (Nature's Spirit, Regions Unexplored, OTBWG, BloomingNature, Promenade, Nyctophobia, Terralith skylands) sin etiqueta c:is_*.
# Cobertura medida con la malla del sondeo: 85 % -> 98 %. Se dejan sin regla los acantilados, baldíos y la barrera de basalto.
FAMILIAS_BIOMAS.update({
    'sabana_h2': (['natures_spirit:oak_savanna', 'natures_spirit:xeric_plains', 'natures_spirit:golden_wilds',
                   'natures_spirit:chaparral', 'natures_spirit:wooded_drylands'],
                  [('minecraft:horse', 0.6, 2), ('alexsmobs:gazelle', 0.6, 3), ('naturalist:zebra', 0.5, 3),
                   ('minecraft:rabbit', 0.6, 2), ('naturalist:lizard', 0.3, 1)]),
    'altiplano_h2': (['natures_spirit:woody_highlands', 'natures_spirit:shrubby_highlands', 'natures_spirit:arid_highlands',
                      'biomeswevegone:lush_stacks'],
                     [('minecraft:goat', 1.0, 3), ('minecraft:sheep', 0.7, 3), ('minecraft:llama', 0.4, 2),
                      ('minecraft:rabbit', 0.5, 2)]),
    'pradera_h2': (['windswept:lavender_fields', 'regions_unexplored:hyacinth_deeps', 'natures_spirit:flowering_shrubland',
                    'natures_spirit:marigold_meadows', 'natures_spirit:carnation_fields', 'natures_spirit:heather_fields'],
                   [('minecraft:sheep', 1.0, 3), ('minecraft:cow', 0.7, 3), ('minecraft:rabbit', 0.6, 2),
                    ('minecraft:horse', 0.4, 2), ('naturalist:hedgehog', 0.3, 1)]),
    'bosque_h2': (['atmospheric:aspen_parkland', 'bloomingnature:cypress_fields', 'natures_spirit:cypress_fields',
                   'biomesoplenty:old_growth_woodland'],
                  [('naturalist:deer', 1.0, 3), ('naturalist:boar', 0.6, 3), ('minecraft:rabbit', 0.5, 2),
                   ('naturalist:turkey', 0.4, 2), ('minecraft:fox', 0.4, 2), ('alexsmobs:raccoon', 0.3, 2)]),
    'taiga_h2': (['natures_spirit:snowy_redwood_forest', 'regions_unexplored:tundra'],
                 [('naturalist:deer', 0.8, 3), ('minecraft:wolf', 0.5, 3), ('minecraft:fox', 0.6, 2), ('minecraft:rabbit', 0.6, 3)]),
    'jungla_h2': (['atmospheric:kousa_jungle', 'natures_spirit:tropical_woods', 'natures_spirit:sparse_tropical_woods', 'nyctophobia:haunted_forest'],
                  [('minecraft:parrot', 1.0, 3), ('alexsmobs:toucan', 0.5, 2), ('alexsmobs:capuchin_monkey', 0.3, 2),
                   ('naturalist:capybara', 0.4, 2), ('minecraft:ocelot', 0.2, 1)]),
    'islas_h2': (['terralith:skylands_autumn', 'terralith:skylands_spring', 'terralith:skylands_summer', 'terralith:skylands_winter'],
                 [('minecraft:sheep', 1.0, 3), ('minecraft:cow', 0.7, 3), ('minecraft:pig', 0.6, 2), ('minecraft:chicken', 0.5, 2)]),
})

COMUN = {
    'dimension': 'minecraft:overworld',
    # 0.4.0: un poco más lejos (40-96) para que la fauna esté ya ahí al llegar y no aparezca a la vista
    'mindist': 40, 'maxdist': 96,
    'validspawn': True, 'sturdy': True,
    'maxpeaceful': 800,               # freno de seguridad por dimensión (animales cargados, granjas incluidas)
}
# 0.4.0: en terreno nuevo solo había animales en el 62 % de los pasos (83 % al volver) y en grupos de 1,3.
# Se repone el doble de rápido y en grupos de tamaño natural: rebaños de 2-4 (tope local +3), parejas de
# 1-3 y solitarios de uno en uno. El freno global maxpeaceful no cambia.
def regla(ent, peso, maximo, cond):
    grupo = {1: (1, 1), 2: (1, 3)}.get(maximo, (2, 4))
    return {'mob': ent, 'persecond': round(0.5 * peso, 4), 'attempts': 10,
            'amount': {'minimum': grupo[0], 'maximum': grupo[1], 'groupdistance': 6},
            'conditions': dict(COMUN, maxlocal=maximo + 3 if maximo >= 3 else maximo, **{'and': cond})}

spawner = []
for nombre, (tags, mobs) in FAMILIAS.items():
    # una regla por especie: así cada una tiene su propio maxlocal
    for ent, peso, maximo in mobs:
        # al aire libre, en el bioma, y lejos de luz artificial (bases, aldeas iluminadas)
        spawner.append(regla(ent, peso, maximo, {'biometags': tags, 'seesky': True, 'maxlight': 3}))
for nombre, (biomas, mobs) in FAMILIAS_BIOMAS.items():
    for ent, peso, maximo in mobs:
        spawner.append(regla(ent, peso, maximo, {'biome': biomas, 'seesky': True, 'maxlight': 3}))
json.dump(spawner, open(os.path.join(out, 'spawner.json'), 'w'), indent=2)

TRANQUILOS = ['c:is_plains', 'c:is_floral']
spawn = [
    # Aldeas (vanilla y CTOV): sin hostiles naturales en superficie.
    {'dimension': 'minecraft:overworld', 'spawntype': 'natural', 'hostile': True, 'seesky': True,
     'structuretags': 'minecraft:village', 'result': 'deny'},
    # (Probado y retirado en 0.2.0: denegar al azar el 50 % de hostiles en llanuras/praderas no reduce su
    #  número, porque el juego reintenta hasta llenar su tope; esos biomas quedan con peligro vanilla.)
    # Minijefe de Cataclysm (200 de vida) fuera de zonas tranquilas.
    {'mob': 'cataclysm:amethyst_crab', 'spawntype': 'natural', 'biometags': TRANQUILOS, 'result': 'deny'},
]
# Hito 0.3.0: enemigos excepcionales de Born in Chaos solo lejos del spawn del mundo (nunca junto a jugadores nuevos).
META = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'criaturas_meta.json')
if os.path.exists(META):
    lejos = ['born_in_chaos_v1:' + e for e in json.load(open(META))['lejos_del_spawn']]
    spawn.append({'mob': lejos, 'spawntype': 'natural', 'maxspawndist': 1500, 'result': 'deny'})
json.dump(spawn, open(os.path.join(out, 'spawn.json'), 'w'), indent=2)
print(len(spawner), 'reglas spawner,', len(spawn), 'reglas spawn ->', out)
