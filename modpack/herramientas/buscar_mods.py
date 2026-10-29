#!/usr/bin/env python3
"""Descubrimiento de mods para Minecraft 1.21.1 + NeoForge.
Uso: python3 -I buscar_mods.py "<texto>" [n]

- Modrinth (sin clave): nombre, descargas, licencia, si tiene versión 1.21.1 NeoForge.
- CurseForge: con la API oficial si hay clave (ver fuente_cf.py); sin clave se omite (CFWidget no busca).
Solo consulta metadatos públicos; no descarga jars."""
import importlib.util, json, sys, urllib.parse
from pathlib import Path

spec = importlib.util.spec_from_file_location('fuente_cf', Path(__file__).with_name('fuente_cf.py'))
fc = importlib.util.module_from_spec(spec); spec.loader.exec_module(fc)
texto = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 15

facetas = json.dumps([['project_type:mod'], ['versions:1.21.1'], ['categories:neoforge']])
r = fc._http('https://api.modrinth.com/v2/search?' + urllib.parse.urlencode(
    {'query': texto, 'facets': facetas, 'limit': n, 'index': 'relevance'}))
print(f'== Modrinth (1.21.1 NeoForge): {r["total_hits"]} resultados')
for h in r['hits']:
    print(f"{h['downloads']:>12,}  {h['slug']:36} {h.get('license', '?'):24} {', '.join(h['categories'][:4])}")

clave = fc.leer_clave()
if not clave:
    print('\n== CurseForge: omitido (sin clave; ver fuente_cf.py)')
    sys.exit()
of = fc.Oficial('/nonexistent', clave)
r = of._get('/v1/mods/search', gameId=fc.MINECRAFT, classId=fc.CLASE_MODS, searchFilter=texto,
            gameVersion='1.21.1', modLoaderType=6, sortField=2, sortOrder='desc', pageSize=n)
print(f'\n== CurseForge (1.21.1 NeoForge, por popularidad): {r["pagination"]["totalCount"]} resultados')
for m in r['data']:
    ult = max((x for x in m.get('latestFilesIndexes', []) if x.get('gameVersion') == '1.21.1'),
              key=lambda x: x['fileId'], default=None)
    print(f"{m['downloadCount']:>12,}  {m['slug']:36} id={m['id']:<8} dist={'sí' if m.get('allowModDistribution') else 'no':2} "
          f"{ult['filename'] if ult else '—'}")
