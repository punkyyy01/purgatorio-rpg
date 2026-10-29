#!/usr/bin/env python3
"""Actualiza UNA entrada de bloqueo.json a otro archivo de CurseForge sin tocar el resto (no ejecuta el resolver completo).
Uso: actualizar_entrada.py <dir_modpack> <projectID> <fileID_nuevo> <jar_descargado> <fecha AAAA-MM-DD> <SHA-1 esperado de CurseForge>
Verifica el SHA-1 del jar, lo copia a la caché de jars, reescribe los metadatos (modId, versión, dependencias) leídos del jar y
comprueba las dependencias obligatorias de todo el conjunto."""
import hashlib, io, json, shutil, sys, tomllib, zipfile
from pathlib import Path
mp, pid, fid, jar, fecha, sha_cf = Path(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), Path(sys.argv[4]), sys.argv[5], sys.argv[6]
CACHE = Path.home()/'dev/modpack-cache/jars'
def mods_de(z, ruta=''):
    out = []; n = 'META-INF/neoforge.mods.toml'
    if n in z.namelist():
        t = tomllib.loads(z.read(n).decode('utf8')); deps = t.get('dependencies', {})
        for m in t.get('mods', []):
            d = [{'modId': x['modId'], 'tipo': x.get('type', 'required' if x.get('mandatory') else 'optional'),
                  'rango': x.get('versionRange', ''), 'lado': x.get('side', 'BOTH')} for x in deps.get(m['modId'], [])]
            out.append({'modId': m['modId'], 'version': str(m.get('version', '')), 'deps': d, **({'incluido_en_jarjar': True} if ruta else {})})
    for j in [x for x in z.namelist() if x.startswith('META-INF/jarjar/') and x.endswith('.jar')]:
        with zipfile.ZipFile(io.BytesIO(z.read(j))) as zz: out += mods_de(zz, j)
    return out
datos = jar.read_bytes(); sha1 = hashlib.sha1(datos).hexdigest()
assert sha1 == sha_cf, f'SHA-1 {sha1} != CurseForge {sha_cf}'
b = json.load(open(mp/'bloqueo.json'))
e = next(x for x in b['entradas'] if x['projectID'] == pid)
antes = (e['fileID'], e['archivo'], e['sha1'], [(m['modId'], m['version']) for m in e['mods']])
with zipfile.ZipFile(jar) as z: mods = mods_de(z)
dest = CACHE/f'{fid}-{jar.name}'
if not dest.exists(): shutil.copy(jar, dest)
e.update({'fileID': fid, 'archivo': jar.name, 'fecha': fecha, 'bytes': len(datos), 'sha1': sha1, 'mods': mods})
ids = {m['modId'] for x in b['entradas'] for m in x['mods']} | {'minecraft', 'neoforge', 'java'}
fallos = [(x['slug'], m['modId'], d['modId']) for x in b['entradas'] for m in x['mods'] for d in m['deps'] if d['tipo'] == 'required' and d['modId'] not in ids]
print('antes:', antes); print('ahora:', (fid, jar.name, sha1, [(m['modId'], m['version']) for m in mods]))
print('dependencias obligatorias sin cubrir:', fallos or 'ninguna')
if fallos: sys.exit(1)
json.dump(b, open(mp/'bloqueo.json', 'w'), indent=1, ensure_ascii=False)
