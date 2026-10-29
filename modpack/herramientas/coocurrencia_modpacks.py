#!/usr/bin/env python3
"""¿Qué combinaciones de mods usan ya modpacks reales? (Modrinth, sin clave.)
Uso: python3 -I coocurrencia_modpacks.py <dir_cache> <slug> [<slug> ...] [--packs N]

Toma los N modpacks de 1.21.1 + NeoForge más descargados de Modrinth (por defecto 200), lee las
dependencias de su versión más reciente y cuenta, entre los packs que contienen TODOS los slugs pedidos,
qué otros mods de mundo y criaturas los acompañan. Limitación: Modrinth no aloja todo (por ejemplo,
Alex's Caves); los packs que solo están en CurseForge necesitarían la API oficial con clave."""
import collections, concurrent.futures as cf, importlib.util, json, sys, time, urllib.parse
from pathlib import Path

spec = importlib.util.spec_from_file_location('fuente_cf', Path(__file__).with_name('fuente_cf.py'))
fc = importlib.util.module_from_spec(spec); spec.loader.exec_module(fc)
args = sys.argv[1:]; npacks = 200
if '--packs' in args:
    i = args.index('--packs'); npacks = int(args[i + 1]); del args[i:i + 2]
cache, pedidos = Path(args[0]) / 'modrinth', set(args[1:])
cache.mkdir(parents=True, exist_ok=True)
M = 'https://api.modrinth.com/v2'


def cacheado(nombre, f):
    p = cache / nombre
    if p.exists() and time.time() - p.stat().st_mtime < 24 * 3600:
        return json.loads(p.read_text())
    d = f(); p.write_text(json.dumps(d)); return d


def packs():
    fac = json.dumps([['project_type:modpack'], ['versions:1.21.1'], ['categories:neoforge']])
    out = []
    for off in range(0, npacks, 100):
        out += fc._http(f'{M}/search?' + urllib.parse.urlencode(
            {'facets': fac, 'limit': min(100, npacks - off), 'offset': off, 'index': 'downloads'}))['hits']
    return out


def deps(p):
    vs = fc._http(f"{M}/project/{p['project_id']}/version?" + urllib.parse.urlencode(
        {'game_versions': '["1.21.1"]', 'loaders': '["neoforge"]'}))
    return [p['slug'], [d['project_id'] for d in vs[0].get('dependencies', []) if d.get('project_id')] if vs else []]


lista = cacheado(f'packs-{npacks}.json', packs)
with cf.ThreadPoolExecutor(6) as ex:
    res = cacheado(f'deps-{npacks}.json', lambda: list(ex.map(deps, lista)))
ids = sorted({i for _, d in res for i in d})


def proyectos():
    info = {}
    for k in range(0, len(ids), 400):
        for p in fc._http(f'{M}/projects?ids=' + urllib.parse.quote(json.dumps(ids[k:k + 400]))):
            info[p['id']] = {'slug': p['slug'], 'cats': p['categories'], 'lic': p['license']['id']}
    return info


info = cacheado(f'proyectos-{npacks}.json', proyectos)
total, junto = collections.Counter(), collections.Counter(); n = 0; nombres = []
for slug, d in res:
    s = {info[i]['slug'] for i in d if i in info}
    total.update(s)
    if pedidos <= s:
        n += 1; nombres.append(slug); junto.update(s)
print(f'{len(res)} modpacks 1.21.1 NeoForge; con {" + ".join(sorted(pedidos))}: {n}')
print('  ', ', '.join(nombres[:20]))
por_slug = {v['slug']: v for v in info.values()}
print('\nmods de mundo/criaturas que los acompañan (packs con la combinación / packs totales, licencia):')
for x, k in junto.most_common():
    v = por_slug.get(x)
    if v and x not in pedidos and k >= 2 and {'worldgen', 'mobs'} & set(v['cats']):
        print(f'{k:4} / {total[x]:<4} {x:40} {v["lic"]}')
