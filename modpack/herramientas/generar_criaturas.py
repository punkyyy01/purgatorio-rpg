#!/usr/bin/env python3
"""Hito 0.3.0 (propuesta en pruebas): datapack purgatorio_criaturas + ajustes de configuración de los mods de criaturas.
Uso: generar_criaturas.py <dir_overrides> <dir_configs_por_defecto>

<dir_configs_por_defecto> es la carpeta config/ de un servidor de laboratorio que ya arrancó una vez con los mods
(de ahí se leen los archivos completos que generan Alex's Mobs, Alex's Caves e IceAndFire, y solo se cambian las
claves de abajo; así el archivo que se distribuye es el del propio mod con nuestros valores).

Criterios (encargo 0.3.0): peligro según el entorno, zonas tranquilas sin monstruos nuevos, nada devastador junto
a jugadores nuevos, sin destrucción de bases ni eventos de invasión, sin duplicados entre mods de fauna.
"""
import json, os, re, sys
OVR, DEF = sys.argv[1], sys.argv[2]
DP = os.path.join(OVR, 'config', 'paxi', 'datapacks', 'purgatorio_criaturas')


def w(path, data, base=DP):
    p = os.path.join(base, path); os.makedirs(os.path.dirname(p), exist_ok=True)
    if isinstance(data, str):
        open(p, 'w').write(data)
    else:
        json.dump(data, open(p, 'w'), indent=2, ensure_ascii=False); open(p, 'a').write('\n')


w('pack.mcmeta', {'pack': {'pack_format': 48, 'description': 'Purgatorio: criaturas por entorno (Born in Chaos, IceAndFire, Mobs of Mythology)'}})

# ---------------------------------------------------------------------------------------------------------------
# 1) Born in Chaos: el mod añade casi todo a "neoforge:any" (todos los biomas, también el Nether) y solo filtra por
#    oscuridad y edad del mundo. Se sustituyen sus biome modifiers (mismo nombre de archivo) por listas por entorno.
#    Llanuras, praderas, playas tranquilas y biomas floridos quedan sin monstruos de Born in Chaos.
# ---------------------------------------------------------------------------------------------------------------
OSCURO = ['minecraft:dark_forest', '#c:is_spooky']
BIC = {
    # entidad: ([biomas], peso, min, max)   (peso de referencia: zombi vanilla = 95)
    'decrepit_skeleton': (['#c:is_forest', '#c:is_taiga', '#c:is_snowy', '#c:is_mountain', '#c:is_badlands'], 12, 1, 1),
    'zombie_lumberjack': (['#c:is_forest', '#c:is_taiga'], 12, 1, 1),
    'decaying_zombie':   (['#c:is_swamp', '#c:is_jungle'], 18, 1, 1),
    'zombie_fisherman':  (['#c:is_river', '#c:is_swamp', '#c:is_beach'], 10, 1, 1),
    'barrel_zombie':     (['#c:is_river', '#c:is_beach'], 5, 1, 1),
    'siamese_skeletons': (['#c:is_badlands', '#c:is_desert'], 12, 1, 1),
    'skeleton_thrasher': (OSCURO + ['#c:is_mountain'], 5, 1, 1),
    'zombie_bruiser':    (OSCURO + ['#c:is_taiga'], 5, 1, 1),
    'bonescaller':       (OSCURO + ['#c:is_snowy'], 5, 1, 1),
    'dread_hound':       (['#c:is_taiga', '#c:is_snowy'], 6, 2, 3),
    'baby_spider':       (['#c:is_jungle'] + OSCURO, 8, 2, 4),
    'mother_spider':     (['#c:is_jungle'] + OSCURO, 3, 1, 1),
    'restless_spirit':   (OSCURO + ['#c:is_swamp'], 8, 1, 1),
    'spirit_guide':      (OSCURO, 3, 1, 1),
    'spirit_guide_assistant': (OSCURO, 3, 1, 2),
    'corpse_fly':        (['#c:is_swamp'], 6, 1, 2),
    'bloody_gadfly':     (['#c:is_swamp', '#c:is_jungle'], 5, 1, 1),
    'door_knight':       (['#c:is_mountain'], 3, 1, 1),
    'thornshell_crab':   (['#c:is_beach', '#c:is_river'], 6, 1, 1),
    'corpse_fish':       (['#c:is_swamp', '#c:is_river'], 4, 2, 3),
    'glutton_fish':      (['#c:is_ocean'], 1, 1, 1),
    # Peligro excepcional: solo lejos del spawn (regla de In Control más abajo) y en su entorno.
    'fallen_chaos_knight': (OSCURO + ['#c:is_badlands'], 2, 1, 1),
    'lifestealer':       (OSCURO, 1, 1, 1),
    'nightmare_stalker': (OSCURO + ['#c:is_taiga'], 1, 1, 1),
    'dire_hound_leader': (['#c:is_taiga', '#c:is_snowy'], 1, 1, 1),
    'supreme_bonescaller': (['#c:is_snowy'], 1, 1, 1),
}
LEJOS_DEL_SPAWN = ['fallen_chaos_knight', 'lifestealer', 'nightmare_stalker', 'dire_hound_leader', 'supreme_bonescaller']
# Sin aparición natural: eventos, bromas fuera de tono, bombas que rompen bloques o invocadores de invasiones.
QUITAR = ['baby_skeleton', 'zombie_clown', 'dark_vortex', 'phantom_creeper', 'seared_spirit', 'missioner', 'swarmer',
          'spiritof_chaos', 'krampus', 'krampus_henchman', 'mr_pumpkin', 'mrs_pumpkin', 'senor_pumpkin', 'pumpkin_bruiser',
          'pumpkin_dunce', 'sir_pumpkinhead',
          # Skeleton Demoman: al recibir daño explota como TNT consultando la regla global mobGriefing (no el evento
          # de NeoForge), así que ni OPAC ni More MobGriefing Options pueden impedir que rompa construcciones (0.3.0-alfa.3).
          'skeleton_demoman']
for ent, (biomas, peso, mn, mx) in BIC.items():
    b = biomas[0] if len(biomas) == 1 else {'type': 'neoforge:or', 'values': biomas}
    w(f'data/born_in_chaos_v1/neoforge/biome_modifier/{ent}_biome_modifier.json',
      {'type': 'neoforge:add_spawns', 'biomes': b, 'spawners': [{'type': f'born_in_chaos_v1:{ent}', 'weight': peso, 'minCount': mn, 'maxCount': mx}]})
for ent in QUITAR:
    w(f'data/born_in_chaos_v1/neoforge/biome_modifier/{ent}_biome_modifier.json', {'type': 'neoforge:none'})
# bone_imp y firelight (Nether) se dejan como los trae el mod.

# ---------------------------------------------------------------------------------------------------------------
# 2) IceAndFire: "#c:is_hot" y "#c:is_cold" incluyen el Nether/End, así que el mod coloca nidos y esqueletos de dragón
#    en el Nether (visto en laboratorio sobre el techo de bedrock). Se limitan a la superficie y se quitan llanuras y
#    praderas (zonas tranquilas). Troll y anfíptero bajan de peso (60 y 50 en el mod).
# ---------------------------------------------------------------------------------------------------------------
w('data/iceandfire/tags/worldgen/biome/structure_gen/fire.json', {'replace': True, 'values': [
    'minecraft:desert', 'minecraft:jungle', 'minecraft:sparse_jungle', 'minecraft:stony_peaks', 'minecraft:windswept_savanna',
    'minecraft:eroded_badlands', 'minecraft:bamboo_jungle', 'minecraft:mangrove_swamp',
    {'id': '#c:is_hot/overworld', 'required': False}]})
w('data/iceandfire/tags/worldgen/biome/structure_gen/ice.json', {'replace': True, 'values': [
    'minecraft:frozen_ocean', 'minecraft:frozen_river', 'minecraft:snowy_plains', 'minecraft:snowy_beach', 'minecraft:snowy_taiga',
    'minecraft:old_growth_pine_taiga', 'minecraft:grove', 'minecraft:snowy_slopes', 'minecraft:jagged_peaks', 'minecraft:frozen_peaks',
    'minecraft:deep_frozen_ocean', 'minecraft:ice_spikes', {'id': '#c:is_cold/overworld', 'required': False},
    {'id': '#c:is_snowy', 'required': False}]})
w('data/iceandfire/neoforge/biome_modifier/troll.json', {'type': 'neoforge:add_spawns', 'biomes': '#iceandfire:entity_gen/troll',
  'spawners': [{'type': 'iceandfire:troll', 'weight': 12, 'minCount': 1, 'maxCount': 2}]})
w('data/iceandfire/neoforge/biome_modifier/amphithere.json', {'type': 'neoforge:add_spawns', 'biomes': '#iceandfire:entity_gen/amphithere',
  'spawners': [{'type': 'iceandfire:amphithere', 'weight': 15, 'minCount': 1, 'maxCount': 2}]})
# Cíclope errante: fuera de llanuras/praderas (zonas tranquilas); queda en colinas nevadas.
w('data/iceandfire/tags/worldgen/biome/entity_gen/wandering_cyclops.json', {'replace': True, 'values': ['minecraft:snowy_plains']})

# ---------------------------------------------------------------------------------------------------------------
# 3) Mobs of Mythology: el draco (peso 25) llenaba las badlands; se iguala al resto.
# ---------------------------------------------------------------------------------------------------------------
w('data/mobs_of_mythology/neoforge/biome_modifier/drakes_spawn.json', {'type': 'neoforge:add_spawns',
  'biomes': '#mobs_of_mythology:drakes_spawn_in', 'spawners': {'type': 'mobs_of_mythology:drake', 'weight': 8, 'minCount': 1, 'maxCount': 2}})

# El chupacabras usa "#c:is_temperate", que incluye llanuras y praderas (visto en el censo): se excluyen.
w('data/mobs_of_mythology/neoforge/biome_modifier/chupacabras_spawn.json', {'type': 'neoforge:add_spawns',
  'biomes': {'type': 'neoforge:and', 'values': ['#mobs_of_mythology:chupacabras_spawn_in',
             {'type': 'neoforge:not', 'value': {'type': 'neoforge:or', 'values': ['#c:is_plains', '#c:is_floral']}}]},
  'spawners': {'type': 'mobs_of_mythology:chupacabra', 'weight': 6, 'minCount': 1, 'maxCount': 2}})

# ---------------------------------------------------------------------------------------------------------------
# 4) Configuración de mods (archivo completo del mod con nuestras claves).
# ---------------------------------------------------------------------------------------------------------------
CFG = os.path.join(OVR, 'config')


def toml_set(nombre, cambios):
    txt = open(os.path.join(DEF, nombre)).read()
    for k, v in cambios.items():
        txt, n = re.subn(rf'(?m)^(\s*{re.escape(k)} = ).*$', lambda m: m.group(1) + v, txt)
        assert n == 1, (nombre, k, n)
    w(nombre, txt, CFG)


# Alex's Mobs Continued (2.x) no lee alexsmobs-common.toml: su configuración es config/amc.json (CodxLib).
# Hasta 0.3.0-alfa.3 se escribía el .toml y estas tres reglas no tenían efecto.
am = open(os.path.join(DEF, 'amc.json')).read()
for clave in ['cachalotDestruction',      # el cachalote rompe bloques de madera al embestir
              'raccoonStealFromChests',   # mapaches que vacían cofres de las bases
              'crowsStealCrops']:         # cuervos que arrasan cultivos
    am, n = re.subn(rf'("{clave}": )true', r'\g<1>false', am); assert n == 1, clave
w('amc.json', am, CFG)
toml_set('alexscaves-general.toml', {
    'tremorzilla_beam_breaks_blocks': 'false',
    'devastating_tremorzilla_beam': 'false',
    # La explosión nuclear (bomba fabricable y Nucleeper) ignora las zonas reclamadas de OPAC (probado):
    # 0 = no rompe ningún bloque; conserva el daño a criaturas y jugadores.
    'nuke_max_block_explosion_resistance': '0',
    # Pisotón del Atlatitan y del Luxtructosaurus (misma rutina, SauropodBaseEntity.crushBlocksInRing): rompe todo
    # bloque con resistencia <= este valor (10 = madera, piedra, ladrillo, cristal). 0 = no rompe bloques.
    'atlatitan_max_block_explosion_resistance': '0',
})
# Alex's Mobs: al buscar comida, el grizzly destruye colmenas (#minecraft:beehives) y el elefante come balas de heno
# y melones. Se acota a lo silvestre (nidos de abeja, hojas) para no dañar granjas ni almacenes de los jugadores.
w('data/alexsmobs/tags/block/grizzly_beehive.json', {'replace': True, 'values': ['minecraft:bee_nest']})
w('data/alexsmobs/tags/block/elephant_foodblocks.json', {'replace': True, 'values': ['#minecraft:leaves']})
iaf = json.load(open(os.path.join(DEF, 'iceandfire', 'iaf-common.json')))
iaf['dragon']['griefing'] = False          # dragones salvajes no rompen terreno ni construcciones
iaf['dragon']['tamedGriefing'] = False
iaf['cyclops']['griefing'] = False
iaf['seaSerpent']['griefing'] = False
iaf['troll']['spawnWeight'] = 12
iaf['amphithere']['spawnWeight'] = 15
# Equipo de dragón: medido en laboratorio, el acero de dragón daba 26-30 de daño y 34 de armadura (netherita: 8-10 y 20).
# Regla del hito: sin inflación de estadísticas. Se iguala a la netherita; conserva sus efectos de fuego/hielo/rayo.
A = iaf['armors']
A['dragonSteelBaseDamage'] = 5.0
A.update({'dragonsteelHelmetArmor': 3, 'dragonsteelChestplateArmor': 8, 'dragonsteelLeggingsArmor': 6, 'dragonsteelBootsArmor': 3,
          'dragonsteelArmorToughness': 3.0, 'dragonScaleProtection': [3, 6, 8, 3], 'dragonScaleToughness': 2.0})
w('iceandfire/iaf-common.json', iaf, CFG)
# IceAndFire: armas por encima de lo razonable (medido: daño por segundo ~2-2,6x la espada de netherita).
# Espada fantasma: sin receta (provisional). Espada del caballero del terror: no la sueltan (regla de botín de In Control).
w('data/iceandfire/recipe/ghost_sword.json', {'neoforge:conditions': [{'type': 'neoforge:false'}],
  'type': 'minecraft:crafting_shapeless', 'ingredients': [{'item': 'minecraft:stone'}], 'result': {'id': 'minecraft:stone'}})
w('incontrol/loot.json', [{'mob': 'iceandfire:dread_knight', 'remove': 'iceandfire:dread_knight_sword'}], CFG)
# Alex's Caves: bomba nuclear sin receta hasta decidir si encaja en el equilibrio (decisión del equipo, 0.3.0).
w('data/alexscaves/recipe/nuclear_bomb.json', {'neoforge:conditions': [{'type': 'neoforge:false'}],
  'type': 'minecraft:crafting_shapeless', 'ingredients': [{'item': 'minecraft:stone'}], 'result': {'id': 'minecraft:stone'}})
# Born in Chaos: armadura de metal oscuro (mejora por encima de la netherita) y darkwarblade (18 de daño): sin receta.
for r in ['armor_plate_from_dark_metal_k_2', 'armor_plate_from_dark_metal_k_3', 'armor_plate_from_dark_metal_k_4',
          'armor_plate_from_dark_metal_k_5', 'great_dark_crusher_k']:
    w(f'data/born_in_chaos_v1/recipe/{r}.json', {'neoforge:conditions': [{'type': 'neoforge:false'}],
      'type': 'minecraft:crafting_shapeless', 'ingredients': [{'item': 'minecraft:stone'}], 'result': {'id': 'minecraft:stone'}})
w('jupiter.json', {'general': {'loadForgeConfigs': False, 'loadClothConfigs': False,
                              'configButtonReplacement': 'UNAVAILABLE_ONLY', 'redirectAutoConfigScreen': False}}, CFG)
w('codxlib.json', {'updateNotifications': False}, CFG)

# Reglas de juego de Born in Chaos: sin eventos por fecha (Halloween empieza el 25 de octubre), sin Krampus.
GR = ['seasonalEvents false', 'halloweenEvent false', 'chillingHorrorEvent false', 'chaoticSpringEvent false',
      'naughtinessMechanics false', 'krampusSpawn false']
# Las reglas de juego (GR) se aplican desde purgatorio_reglas/reglas.mcfunction (un solo .mcfunction en el pack).
json.dump({'lejos_del_spawn': LEJOS_DEL_SPAWN}, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'criaturas_meta.json'), 'w'), indent=1)

# ---------------------------------------------------------------------------------------------------------------
# 5) ServerCore (rendimiento del servidor, 0.3.0). Perfil JFR: ~28-31 % del tick en aparición natural (consultas de
#    bioma ~10 %) y ~50 % en tick de entidades. Ajustes conservadores; ver hito-0.3.0/RENDIMIENTO.md.
# ---------------------------------------------------------------------------------------------------------------
sc_dir = os.path.join(DEF, 'servercore')
if os.path.isdir(sc_dir):
    opt = open(os.path.join(sc_dir, 'optimizations.yml')).read()
    opt, n = re.subn(r'(?m)^fast-biome-lookups: false$', 'fast-biome-lookups: true', opt); assert n == 1
    w('servercore/optimizations.yml', opt, CFG)
    cfg = open(os.path.join(sc_dir, 'config.yml')).read()
    # Tope de Glares (Friends & Foes): 90-105 cargadas costaban 6-8 % del tick.
    cfg, n = re.subn(r"(- category: 'FRIENDSANDFOES_GLARES'\n\s+mobcap: )15", r'\g<1>6', cfg); assert n == 1
    # Rango de activación: a más de 32 bloques de cualquier jugador, la IA se actualiza cada segundo en vez de cada tick.
    i = cfg.index('activation-range:')
    ar = cfg[i:]
    ar = ar.replace('  enabled: false', '  enabled: true', 1)
    # Excluidos del rango de activación: los del mod + dragones y jefes. ServerCore escribe su lista por defecto en un
    # orden que cambia entre arranques, así que se reescribe ordenada para que el resultado sea reproducible.
    m = re.search(r"(  excluded-entity-types:\n)((?:    - '[^']+'\n)+)", ar)
    lista = set(re.findall(r"'([^']+)'", m.group(2))) | {
        'minecraft:ender_dragon', 'minecraft:wither', 'iceandfire:fire_dragon', 'iceandfire:ice_dragon',
        'iceandfire:lightning_dragon', 'iceandfire:sea_serpent', 'alexsmobs:void_worm', 'alexscaves:tremorzilla',
        'alexscaves:luxtructosaurus'}
    ar = ar[:m.start(2)] + ''.join(f"    - '{e}'\n" for e in sorted(lista)) + ar[m.end(2):]
    ar = re.sub(r'(default-activation-type:\n\s+activation-range: )16', r'\g<1>32', ar, count=1)
    cfg = cfg[:i] + ar
    # «default-values» (ajustes dinámicos, desactivados) también sale en orden variable: se ordena.
    m = re.search(r"(  default-values:\n)((?:    [A-Z_]+: [^\n]*\n)+)", cfg)
    cfg = cfg[:m.start(2)] + ''.join(sorted(m.group(2).splitlines(keepends=True))) + cfg[m.end(2):]
    w('servercore/config.yml', cfg, CFG)

# ---------------------------------------------------------------------------------------------------------------
# 6) Sin destrucción de construcciones por criaturas, también fuera de terreno reclamado (0.3.0-alfa.3).
#    More MobGriefing Options responde al evento de NeoForge (EntityMobGriefingEvent) por tipo de criatura. Por ese
#    evento pasan las explosiones de criaturas (creepers), endermans, zombis contra puertas, ghasts, Alex's Caves,
#    Alex's Mobs, Cataclysm... FALSE para las hostiles; aldeanos, ovejas, conejos, zorros y demás animales siguen como
#    en vanilla (DEFAULT = regla mobGriefing, que se queda activada). Piglins fuera: necesitan recoger oro para trueques.
#    Categorías: herramientas/categorias_entidades.json (extraídas de los jars con categorias.py).
# ---------------------------------------------------------------------------------------------------------------
CAT = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'categorias_entidades.json')))
VANILLA_HOSTIL = {'blaze', 'bogged', 'breeze', 'cave_spider', 'creeper', 'drowned', 'elder_guardian', 'ender_dragon',
                  'enderman', 'endermite', 'evoker', 'ghast', 'giant', 'guardian', 'hoglin', 'husk', 'illusioner',
                  'magma_cube', 'phantom', 'pillager', 'ravager', 'shulker', 'silverfish', 'skeleton', 'slime', 'spider',
                  'stray', 'vex', 'vindicator', 'warden', 'witch', 'wither', 'wither_skeleton', 'zoglin', 'zombie',
                  'zombie_villager', 'zombified_piglin',
                  'wither_skull'}   # su explosión consulta el evento con el propio proyectil, no con el Wither
# Mods de monstruos: además de sus hostiles, sus proyectiles y entidades auxiliares (p. ej. alexscaves:tephra) y las
# que el extractor no clasificó. Sus animales (CREATURE, WATER_*, AMBIENT) siguen en DEFAULT.
MODS_HOSTILES = {'alexscaves', 'born_in_chaos_v1', 'cataclysm', 'iceandfire', 'mowziesmobs', 'bosses_of_mass_destruction',
                 'infernalexp', 'creeperoverhaul', 'endermanoverhaul', 'rottencreatures', 'mobs_of_mythology'}
PASIVAS = {'CREATURE', 'AMBIENT', 'WATER_CREATURE', 'WATER_AMBIENT', 'UNDERGROUND_WATER_CREATURE', 'AXOLOTLS'}
EXCEPCIONES = {'minecraft:piglin', 'minecraft:piglin_brute'}


def sin_romper(ent):
    ns, nombre = ent.split(':', 1)
    if ent in EXCEPCIONES:
        return False
    if ns == 'minecraft':
        return nombre in VANILLA_HOSTIL
    cat = CAT.get(ent)
    if cat == 'MONSTER':
        return True
    return ns in MODS_HOSTILES and cat not in PASIVAS


mm = open(os.path.join(DEF, 'moremobgriefingoptions-server.toml')).read()
falsos = []
def _f(m):
    if sin_romper(m.group(2)):
        falsos.append(m.group(2)); return m.group(1) + '"FALSE"'
    return m.group(0)
mm = re.sub(r'(?m)^(\s*"([a-z0-9_.-]+:[a-z0-9_./-]+)" = )"DEFAULT"$', _f, mm)
w('moremobgriefingoptions-server.toml', mm, CFG)
# Mods que consultan la regla directamente (no el evento) y tienen opción propia:
eo = open(os.path.join(DEF, 'endermanoverhaul.jsonc')).read()
eo, n = re.subn(r'"allowPickingUpBlocks": true', '"allowPickingUpBlocks": false', eo); assert n == 1
w('endermanoverhaul.jsonc', eo, CFG)
# Cataclysm: varios jefes ignoran mobGriefing ("ignore_mobgriefing = true") y rompen bloques siempre.
ca = open(os.path.join(DEF, 'cataclysm-common.toml')).read()
ca, n = re.subn(r'(?m)^(\s*ignore_mobgriefing = )true$', r'\g<1>false', ca); assert n >= 1
w('cataclysm-common.toml', ca, CFG)
# ---------------------------------------------------------------------------------------------------------------
# 7) Arranque: NeoForge construye los mods en paralelo y Architectury 13.0.11 guarda los registros de aparición en un
#    ArrayList sin sincronizar. Critters and Companions, Meadow y Mobs of Mythology lo usan a la vez al construirse:
#    fallo intermitente (ArrayIndexOutOfBoundsException en SpawnPlacementsRegistryImpl.register, 1 de 34 arranques).
#    Con maxThreads = 1 los mods se construyen de uno en uno.
# ---------------------------------------------------------------------------------------------------------------
fml = open(os.path.join(DEF, 'fml.toml')).read()
fml, n = re.subn(r'(?m)^maxThreads = -1$', 'maxThreads = 1', fml); assert n == 1
w('fml.toml', fml, CFG)
print('mobGriefing FALSE:', len(falsos), 'tipos de entidad')
print('ok', DP)
