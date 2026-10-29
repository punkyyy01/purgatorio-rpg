#!/usr/bin/env python3
"""Genera overrides/config/crittersandcompanions-common.json5 a partir de la configuración por defecto del mod.

Uso: generar_critters.py <dir_overrides> <dir_configs_por_defecto>

El archivo original es de Critters and Companions (todos los derechos reservados), así que no se versiona: se toma
el que escribe el propio mod (obtener_config_por_defecto.py) y solo se cambian los pesos de abajo.
"""
import os, re, sys

OVR, DEF = sys.argv[1], sys.argv[2]
NOMBRE = 'crittersandcompanions-common.json5'
CABECERA = ('// Purgatorio RPG: pesos de aparición ajustados (insectos de bosque más raros, sin caracol duplicado,\n'
            '// más nutrias y koi en ríos). Resto = valores por defecto de Critters and Companions 2.7.0.\n')
# (especie, biome_spec): peso nuevo. Comentario: valor del mod.
PESOS = {
    ('leaf_insect', '#c:is_jungle'): 4,      # 14
    ('leaf_insect', '#c:is_forest'): 2,      # 6
    ('jumping_spider', '#c:is_jungle'): 1,   # 2
    ('jumping_spider', '#c:is_forest'): 1,   # 2
    ('jumping_spider', '#c:is_lush'): 2,     # 4
    ('otter', '#c:is_river'): 6,             # 1
    ('koi_fish', '#c:is_river'): 6,          # 2
    ('ladybug', '#c:is_forest'): 2,          # 6
    ('ladybug', '#c:is_lush'): 4,            # 10
    ('ladybug', '#c:is_floral'): 4,          # 12
    ('stag_beetle', '#c:is_forest'): 1,      # 4
    ('stag_beetle', '#c:is_lush'): 3,        # 10
    ('roly_poly', '#c:is_forest'): 1,        # 5
    ('roly_poly', '#c:is_lush'): 3,          # 10
    ('roly_poly', '#c:is_swamp'): 2,         # 10
    ('snail', '#c:is_forest'): 0,            # 5 (Naturalist ya trae caracol)
    ('snail', '#c:is_lush'): 0,              # 8
    ('snail', '#c:is_swamp'): 0,             # 10
    ('stick_bug', '#c:is_forest'): 1,        # 4
    ('stick_bug', '#c:is_lush'): 3,          # 10
    ('weevil', '#c:is_forest'): 1,           # 4
    ('weevil', '#c:is_lush'): 3,             # 10
}

especie = bioma = None
hechos = set()
salida = []
for linea in open(os.path.join(DEF, NOMBRE)):
    m = re.match(r'^\t\t([a-z_]+): \[', linea)
    if m:
        especie = m.group(1)
    m = re.search(r'biome_spec: "([^"]+)"', linea)
    if m:
        bioma = m.group(1)
    if (especie, bioma) in PESOS and re.search(r'weight: \d+,', linea):
        linea = re.sub(r'weight: \d+,', f'weight: {PESOS[(especie, bioma)]},', linea)
        hechos.add((especie, bioma))
    salida.append(linea)
falta = set(PESOS) - hechos
assert not falta, f'entradas no encontradas en el archivo del mod: {falta}'
destino = os.path.join(OVR, 'config', NOMBRE)
os.makedirs(os.path.dirname(destino), exist_ok=True)
open(destino, 'w').write(CABECERA + ''.join(salida))
print('ok', destino)
