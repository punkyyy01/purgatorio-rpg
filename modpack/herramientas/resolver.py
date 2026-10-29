#!/usr/bin/env python3
"""Resuelve la selección de mods contra CurseForge para Minecraft 1.21.1 + NeoForge.

Uso: python3 -I resolver.py <dir_modpack> <dir_cache>

- Lee <dir_modpack>/seleccion.toml (mods elegidos) y <dir_modpack>/dependencias.toml
  (modId -> slug de CurseForge para las dependencias).
- Busca cada proyecto en CurseForge mediante fuente_cf.py: la API oficial si hay clave
  (CURSEFORGE_API_KEY o ~/.config/purgatorio-rpg/curseforge-api-key) o, si no, CFWidget. Elige el archivo más reciente marcado 1.21.1 + NeoForge (release antes que beta),
  salvo que <dir_modpack>/fijados.toml fije un archivo concreto.
- Descarga ese archivo exacto del CDN de CurseForge a <dir_cache> (fuera del repo) y anota
  tamaño y SHA-1. Así el manifiesto apunta a los mismos bytes que se han verificado.
- Lee META-INF/neoforge.mods.toml de cada jar (y de los jars incluidos en META-INF/jarjar)
  y comprueba dependencias obligatorias, rangos de versión, incompatibilidades y modIds
  duplicados.
- Escribe <dir_modpack>/bloqueo.json y <dir_modpack>/informe-dependencias.md.
"""
import hashlib, importlib.util, io, json, re, sys, time, tomllib, urllib.parse, urllib.request, zipfile
from pathlib import Path

_spec = importlib.util.spec_from_file_location('fuente_cf', Path(__file__).with_name('fuente_cf.py'))
fuente_cf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fuente_cf)

GV, LOADER = '1.21.1', 'NeoForge'
UA = {'User-Agent': 'punkyyy01/purgatorio-rpg modpack build'}
IGNORAR = {'minecraft', 'neoforge', 'forge', 'java', 'fml', 'javafml', 'mixinextras'}


def http(url, binario=False, intentos=4):
    for i in range(intentos):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120)
            data = r.read()
            return data if binario else json.loads(data)
        except Exception:
            if i == intentos - 1:
                raise
            time.sleep(3 + 3 * i)


def elegir_archivo(d, fijado=None):
    fs = [x for x in d.get('files', []) if GV in x['versions'] and LOADER in x['versions']]
    if not fs:
        # Algunos autores (YUNG's, Paxi) etiquetan sus jars de 1.21.1 como "Forge" aunque son de NeoForge.
        # Se aceptan solo si el jar trae META-INF/neoforge.mods.toml (se comprueba después).
        fs = [x for x in d.get('files', []) if GV in x['versions'] and 'Forge' in x['versions']]
    if fijado:
        fs = [x for x in d.get('files', []) if x['id'] == fijado]
    if not fs:
        return None
    rel = [x for x in fs if x['type'] == 'release']
    return max(rel or fs, key=lambda x: x['uploaded_at'])


def url_cdn(f):
    i = f['id']
    return f"https://mediafilez.forgecdn.net/files/{i // 1000}/{i % 1000}/{urllib.parse.quote(f['name'])}"


def leer_toml_mods(z):
    """Devuelve la lista de mods declarados en un jar (incluidos los de jarjar)."""
    mods = []
    nombres = z.namelist()
    for nombre in ('META-INF/neoforge.mods.toml', 'META-INF/mods.toml'):
        if nombre in nombres:
            texto = z.read(nombre).decode('utf-8', 'replace')
            try:
                t = tomllib.loads(texto)
            except Exception as e:
                mods.append({'modId': '?', 'error': f'toml ilegible: {e}'})
                break
            version_jar = '?'
            mf = z.read('META-INF/MANIFEST.MF').decode('utf-8', 'replace') if 'META-INF/MANIFEST.MF' in nombres else ''
            m = re.search(r'Implementation-Version:\s*(\S+)', mf)
            if m:
                version_jar = m.group(1)
            for mod in t.get('mods', []):
                v = str(mod.get('version', '?'))
                if '${' in v:
                    v = version_jar
                deps = []
                for d in t.get('dependencies', {}).get(mod.get('modId'), []):
                    tipo = str(d.get('type', 'required' if d.get('mandatory', True) else 'optional')).lower()
                    deps.append({'modId': d.get('modId'), 'tipo': tipo, 'rango': d.get('versionRange', '*'),
                                 'lado': d.get('side', 'BOTH')})
                mods.append({'modId': mod.get('modId'), 'version': v, 'deps': deps})
            break
    anidados = [n for n in nombres if n.startswith('META-INF/jarjar/') and n.endswith('.jar')]
    if 'META-INF/jarjar/metadata.json' in nombres:
        try:
            meta = json.loads(z.read('META-INF/jarjar/metadata.json'))
            anidados += [j['path'] for j in meta.get('jars', []) if j.get('path') in nombres]
        except Exception:
            pass
    for nombre in dict.fromkeys(anidados):
        if True:
            try:
                with zipfile.ZipFile(io.BytesIO(z.read(nombre))) as zz:
                    for m in leer_toml_mods(zz):
                        m['incluido_en_jarjar'] = True
                        mods.append(m)
            except zipfile.BadZipFile:
                pass
    return mods


def partes(v):
    return [int(x) if x.isdigit() else x for x in re.split(r'[.\-+_]', str(v)) if x != '']


def cmp(a, b):
    pa, pb = partes(a), partes(b)
    for x, y in zip(pa, pb):
        if x == y:
            continue
        if isinstance(x, int) and isinstance(y, int):
            return -1 if x < y else 1
        return -1 if str(x) < str(y) else 1
    return (len(pa) > len(pb)) - (len(pa) < len(pb))


def en_rango(v, rango):
    """Rangos de Maven: [1.0,2.0), [1.0,), 1.0 (= mínimo), *. None si no se puede decidir."""
    rango = str(rango).strip()
    if rango in ('', '*') or v in ('?', None):
        return True if rango in ('', '*') else None
    try:
        for parte in re.findall(r'[\[\(][^\]\)]*[\]\)]', rango) or [rango]:
            if parte[0] not in '[(':
                if cmp(v, parte) >= 0:
                    return True
                continue
            inc_i, inc_d = parte[0] == '[', parte[-1] == ']'
            cuerpo = parte[1:-1]
            if ',' not in cuerpo:
                if cmp(v, cuerpo) == 0:
                    return True
                continue
            lo, hi = [x.strip() for x in cuerpo.split(',', 1)]
            ok = True
            if lo:
                c = cmp(v, lo)
                ok &= c > 0 or (c == 0 and inc_i)
            if hi:
                c = cmp(v, hi)
                ok &= c < 0 or (c == 0 and inc_d)
            if ok:
                return True
        return False
    except Exception:
        return None


def main():
    mp, cache = Path(sys.argv[1]), Path(sys.argv[2])
    (cache / 'jars').mkdir(parents=True, exist_ok=True)
    sel = tomllib.loads((mp / 'seleccion.toml').read_text())['mod']
    depmap = tomllib.loads((mp / 'dependencias.toml').read_text()) if (mp / 'dependencias.toml').exists() else {}
    fijados = tomllib.loads((mp / 'fijados.toml').read_text()) if (mp / 'fijados.toml').exists() else {}
    fuente = fuente_cf.fuente(cache)
    print('Fuente de metadatos de CurseForge:', fuente.nombre)
    comprobaciones_cf = []   # solo con la API oficial
    cola = [(m['slug'], m['pilar'], m.get('porque', '')) for m in sel]
    vistos, entradas, errores = set(), [], []
    while cola:
        slug, pilar, porque = cola.pop(0)
        if slug in vistos:
            continue
        vistos.add(slug)
        try:
            d = fuente.proyecto(slug)
        except Exception as e:
            errores.append(f'{slug}: no encontrado en CurseForge vía {fuente.nombre} ({str(e)[:60]})')
            continue
        f = elegir_archivo(d, fijados.get(slug))
        if not f:
            errores.append(f'{slug}: sin archivo {GV} {LOADER} en CurseForge')
            continue
        destino = cache / 'jars' / f"{f['id']}-{f['name']}"
        if not destino.exists() or destino.stat().st_size != f['filesize']:
            destino.write_bytes(http(f.get('url_descarga') or url_cdn(f), binario=True))
        datos = destino.read_bytes()
        with zipfile.ZipFile(io.BytesIO(datos)) as z:
            mods = leer_toml_mods(z)
            es_neoforge = 'META-INF/neoforge.mods.toml' in z.namelist()
        e = {'slug': slug, 'titulo': d['title'], 'projectID': d['id'], 'fileID': f['id'], 'archivo': f['name'],
             'tipo': f['type'], 'fecha': f['uploaded_at'][:10], 'bytes': len(datos),
             'sha1': hashlib.sha1(datos).hexdigest(), 'licencia': d.get('license'),
             'autores': [m.get('username') for m in d.get('members', [])],
             'url': d['urls']['curseforge'], 'pilar': pilar, 'porque': porque, 'mods': mods,
             'tamano_ok': len(datos) == f['filesize'], 'etiquetas_cf': f['versions'], 'es_neoforge': es_neoforge}
        entradas.append(e)
        if f.get('sha1') and f['sha1'] != e['sha1']:
            comprobaciones_cf.append(('problema', f'{slug}: el SHA-1 descargado no coincide con el que publica CurseForge'))
        if d.get('distribucion_permitida') is False:
            comprobaciones_cf.append(('aviso', f'{slug}: el autor no permite la distribución por terceros; el zip solo lo '
                                               'referencia en el manifiesto (correcto); no incluir nunca el jar en un paquete'))
        e['_deps_cf'] = [x['modId'] for x in f.get('dependencias_cf', []) if x['tipo'] == 'obligatoria']
        for m in mods:
            for dep in m['deps']:
                if dep['tipo'] == 'required' and dep['modId'] not in IGNORAR:
                    s = depmap.get(dep['modId'])
                    if s and s not in vistos:
                        cola.append((s, 'dependencia', f"requerido por {m['modId']}"))
        print(f"{slug:38} {f['type']:8} {f['name']}")
    # Comprobaciones estáticas
    provistos = {}
    for e in entradas:
        for m in e['mods']:
            provistos.setdefault(m['modId'], []).append((e['slug'], m['version'], m.get('incluido_en_jarjar', False)))
    problemas, avisos, neo_rangos = [], [], []
    for mid, fuentes in provistos.items():
        principales = [f for f in fuentes if not f[2]]
        if len(principales) > 1:
            problemas.append(f'modId duplicado `{mid}` en ' + ', '.join(f[0] for f in principales))
    for e in entradas:
        for m in e['mods']:
            if m.get('incluido_en_jarjar'):
                continue
            for dep in m['deps']:
                mid, tipo, rango = dep['modId'], dep['tipo'], dep['rango']
                if mid in ('neoforge', 'forge'):
                    neo_rangos.append((e['slug'], rango))
                    continue
                if mid in ('minecraft',):
                    if en_rango(GV, rango) is False:
                        # Varios jars de 1.21.1 declaran [1.21,1.21.1) y aun así se usan en packs grandes
                        # (ATM10, Better MC 5). Se deja como aviso: hay que confirmarlo al arrancar el cliente.
                        avisos.append(f'{e["slug"]} ({m["modId"]}) declara minecraft {rango}; confirmar en el arranque')
                    continue
                if mid in IGNORAR:
                    continue
                if tipo == 'required':
                    if mid not in provistos:
                        problemas.append(f'{e["slug"]} ({m["modId"]}) necesita `{mid}` {rango} y no está')
                        continue
                    vs = [f[1] for f in provistos[mid]]
                    r = [en_rango(v, rango) for v in vs]
                    if not any(x is True for x in r):
                        (problemas if False in r and None not in r else avisos).append(
                            f'{e["slug"]} ({m["modId"]}) pide `{mid}` {rango}; presente {", ".join(vs)}')
                elif tipo == 'incompatible' and mid in provistos:
                    vs = [f[1] for f in provistos[mid]]
                    if any(en_rango(v, rango) is not False for v in vs):
                        problemas.append(f'{e["slug"]} ({m["modId"]}) es incompatible con `{mid}` {rango} (presente {", ".join(vs)})')
                elif tipo == 'discouraged' and mid in provistos:
                    avisos.append(f'{e["slug"]} ({m["modId"]}) desaconseja `{mid}` {rango}')
        if not e['mods']:
            avisos.append(f'{e["slug"]}: el jar no declara mods de NeoForge (¿solo recursos o datapack?)')
        if not e['es_neoforge']:
            (avisos if not e['mods'] else problemas).append(f'{e["slug"]}: el jar no trae META-INF/neoforge.mods.toml')
        if not e['tamano_ok']:
            problemas.append(f'{e["slug"]}: el tamaño descargado no coincide con CurseForge')
    en_pack = {e['projectID'] for e in entradas}
    for e in entradas:
        for pid in e.pop('_deps_cf'):
            if pid not in en_pack:
                comprobaciones_cf.append(('aviso', f'{e["slug"]}: CurseForge declara obligatorio el proyecto {pid}, que no está '
                                                   'en el bloqueo (puede ser un falso positivo: comprobar)'))
    problemas += [t for k, t in comprobaciones_cf if k == 'problema']
    avisos += [t for k, t in comprobaciones_cf if k == 'aviso']
    json.dump({'minecraft': GV, 'loader': LOADER, 'entradas': entradas, 'rangos_neoforge': neo_rangos},
              open(mp / 'bloqueo.json', 'w'), indent=1, ensure_ascii=False)
    with open(mp / 'informe-dependencias.md', 'w') as o:
        o.write(f'# Comprobación estática de dependencias\n\n{len(entradas)} archivos, '
                f'{len(provistos)} modIds (incluidos los anidados).\n\n')
        o.write('## Errores de resolución\n\n' + ('\n'.join('- ' + x for x in errores) or 'Ninguno.') + '\n\n')
        o.write('## Problemas\n\n' + ('\n'.join('- ' + x for x in problemas) or 'Ninguno.') + '\n\n')
        o.write('## Avisos (sin decidir automáticamente)\n\n' + ('\n'.join('- ' + x for x in avisos) or 'Ninguno.') + '\n\n')
        o.write('## Rangos de NeoForge pedidos\n\n' + '\n'.join(f'- {s}: `{r}`' for s, r in sorted(set(neo_rangos))) + '\n')
    print(f'\n{len(entradas)} archivos | errores {len(errores)} | problemas {len(problemas)} | avisos {len(avisos)}')
    for x in errores + problemas:
        print('  !', x)


if __name__ == '__main__':
    main()
