#!/usr/bin/env python3
"""Escribe doc/LICENCIAS-Y-CREDITOS.md desde informes/licencias.json (generar_licencias.py). Uso: generar_doc_licencias.py <licencias.json> <salida.md>"""
import json, sys
f = json.load(open(sys.argv[1]))
filas = '\n'.join(f"| [{x['titulo']}]({x['url']}) | {x['autores'] or '—'} | {x['licencia'][:70] or '?'} | {'sí' if x['redistribuible_por_terceros'] else '**NO**'} |" for x in f)
restr = [x for x in f if any(k in x['licencia'].lower() for k in ('all rights', 'arr', 'custom', 'nc', 'polyform', 'read attached', 'protective', 'terrarium', 'stardust', 'dsmsl', 'supplementaries team', 'unlicensed')) or x['licencia'] in ('?', '${mod_license}')]
res = '\n'.join(f"- **{x['titulo']}** — {x['licencia'][:110]}" for x in restr)
open(sys.argv[2], 'w').write(f"""# Licencias y créditos de {{{{NOMBRE}}}} {{{{VERSION_VISIBLE}}}}

## Qué distribuye realmente este modpack
| Qué | Cómo |
|---|---|
| **Mods de terceros ({len(f)} archivos)** | **Solo por referencia** (`manifest.json`: projectID/fileID de CurseForge). El zip de cliente **no contiene ningún jar de terceros**: el launcher de CurseForge los descarga de CurseForge, como hace cualquier modpack. |
| **Paquete de servidor** | Sin jars de terceros. Trae `mods-servidor.json` (lista exacta con SHA-1) y un instalador que descarga cada mod **desde el CDN oficial de CurseForge** y verifica su SHA-1. Los 4 proyectos cuyo autor desactiva la distribución por terceros se descargan a mano desde su página de CurseForge. |
| **Archivos propios** | Configuraciones (`config/`), datapacks de Paxi (`purgatorio_*`: reglas del mundo, fauna, desactivación de recetas, guía de bienvenida, arreglos), textos e imágenes de la identidad visual, `purg4tory_botin.json` y el mod **PURG4TORY Cauces** (licencia **MIT**, código en `mods-propios/purg4tory_cauces`). |
| **Datos de terceros copiados** | **Ninguno.** Los datapacks propios solo *desactivan* recetas ajenas con una condición `neoforge:false` o ajustan etiquetas con archivos nuevos; el equilibrio de botín (`purg4tory_botin.json`) no copia tablas: guarda identificadores y probabilidades, y lo aplica el código de Cauces sobre el resultado generado. |

Una licencia «All Rights Reserved» no impide referenciar un mod desde un modpack mediante CurseForge: CurseForge lo permite expresamente mientras el proyecto exista y esté aprobado; lo que **no** se hace aquí es copiar sus jars o sus archivos.

## Mods cuyo autor no permite la distribución por terceros
Se cargan en el launcher de CurseForge sin problema. **No** pueden descargarse automáticamente ni copiarse a un paquete de servidor: hay que bajarlos de su página (el instalador del servidor da el enlace exacto y el SHA-1): Alex's Mobs Continued, Hybrid API [HAPI], ServerCore, Structory, Entity Culling (este último es solo de cliente).
**Excluido del pack por esta razón:** Mystic's Biomes (prohíbe la distribución por terceros).

## Licencias con condiciones especiales (revisadas por el nombre declarado en el jar)
{res}

## Tabla completa (licencia tal y como la declara cada jar en `neoforge.mods.toml`)
| Mod | Autores | Licencia declarada | ¿Descarga por terceros permitida en CurseForge? |
|---|---|---|---|
{filas}

Los créditos de cada mod corresponden a sus autores; se enlazan arriba a su página de CurseForge. Minecraft es © Mojang Studios/Microsoft; este proyecto no está afiliado a ellos ni a CurseForge.
El campo «licencia declarada» procede del jar; si una página de CurseForge indica algo distinto, manda lo que diga el autor. Última revisión: generada automáticamente desde `bloqueo.json`.
""")
