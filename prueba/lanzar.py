#!/usr/bin/env python3
"""Lanzador mínimo del cliente de pruebas (sin cuenta, modo offline) para NeoForge 1.21.1.

Uso: lanzar.py <dir_mc> <dir_instancia> [--preparar] [-- args extra de java]
- Lee versions/neoforge-*/<id>.json y el vanilla del que hereda.
- Descarga y verifica (SHA-1) las librerías y el índice de recursos de Mojang que falten.
  Los sonidos se omiten (no hay audio en el entorno de pruebas); el juego avisa y sigue.
- --preparar: solo descarga, no arranca.
Variables: MC_JAVA (java 21), MC_XMX (por defecto 6G), MC_ANCHO/MC_ALTO (tamaño de ventana).
"""
import hashlib, json, os, subprocess, sys, urllib.request
from pathlib import Path

UA = {'User-Agent': 'purg4tory test client'}
MC, INST = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
SOLO_PREPARAR = '--preparar' in sys.argv
EXTRA = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []


def bajar(url, destino, sha1=None):
    destino = Path(destino)
    if destino.exists() and (sha1 is None or hashlib.sha1(destino.read_bytes()).hexdigest() == sha1):
        return
    destino.parent.mkdir(parents=True, exist_ok=True)
    datos = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()
    if sha1 and hashlib.sha1(datos).hexdigest() != sha1:
        raise SystemExit(f'SHA-1 incorrecto: {url}')
    destino.write_bytes(datos)


def permitido(reglas):
    if not reglas:
        return True
    ok = False
    for r in reglas:
        cumple = all(r.get('os', {}).get(k) in (None, v) for k, v in (('name', 'linux'), ('arch', 'x86_64')))
        if 'features' in r:
            cumple = False
        if cumple:
            ok = r['action'] == 'allow'
    return ok


neo = next(p for p in (MC / 'versions').iterdir() if p.name.startswith('neoforge-'))
vn = json.loads((neo / f'{neo.name}.json').read_text())
base_id = vn['inheritsFrom']
vb_path = MC / 'versions' / base_id / f'{base_id}.json'
if not vb_path.exists():
    manifest = json.load(urllib.request.urlopen('https://piston-meta.mojang.com/mc/game/version_manifest_v2.json'))
    e = next(v for v in manifest['versions'] if v['id'] == base_id)
    bajar(e['url'], vb_path, e['sha1'])
vb = json.loads(vb_path.read_text())
bajar(vb['downloads']['client']['url'], MC / 'versions' / base_id / f'{base_id}.jar', vb['downloads']['client']['sha1'])

cp, vistos = [], set()
for lib in vn['libraries'] + vb['libraries']:
    if not permitido(lib.get('rules')):
        continue
    art = lib.get('downloads', {}).get('artifact')
    if not art:
        continue
    clave = lib['name'].rsplit(':', 1)[0] if lib['name'].count(':') == 2 else lib['name']
    if clave in vistos:
        continue
    vistos.add(clave)
    destino = MC / 'libraries' / art['path']
    if art.get('url'):
        bajar(art['url'], destino, art.get('sha1'))
    cp.append(str(destino))
# Como el launcher oficial: el jar vanilla va con el nombre de la versión hija (NeoForge lo ignora por ese nombre).
jar_hijo = neo / f'{neo.name}.jar'
if not jar_hijo.exists():
    jar_hijo.write_bytes((MC / 'versions' / base_id / f'{base_id}.jar').read_bytes())
cp.append(str(jar_hijo))

ai = vb['assetIndex']
idx_path = MC / 'assets' / 'indexes' / f"{ai['id']}.json"
bajar(ai['url'], idx_path, ai['sha1'])
objetos = json.loads(idx_path.read_text())['objects']
faltan = [(n, o) for n, o in objetos.items() if not n.startswith('minecraft/sounds/')
          and not (MC / 'assets' / 'objects' / o['hash'][:2] / o['hash']).exists()]
for i, (n, o) in enumerate(faltan):
    h = o['hash']
    bajar(f'https://resources.download.minecraft.net/{h[:2]}/{h}', MC / 'assets' / 'objects' / h[:2] / h, h)
if faltan:
    print(f'{len(faltan)} recursos descargados')
if SOLO_PREPARAR:
    print('preparado'); sys.exit()

INST.mkdir(parents=True, exist_ok=True)
vars_ = {
    '${library_directory}': str(MC / 'libraries'), '${classpath_separator}': ':', '${version_name}': neo.name,
    '${natives_directory}': str(INST / 'natives'), '${launcher_name}': 'purg4tory-pruebas', '${launcher_version}': '1',
    '${classpath}': ':'.join(cp), '${auth_player_name}': os.environ.get('MC_NOMBRE', 'Pruebas'), '${game_directory}': str(INST),
    '${assets_root}': str(MC / 'assets'), '${assets_index_name}': ai['id'], '${auth_uuid}': '00000000-0000-0000-0000-000000000000',
    '${auth_access_token}': '0', '${clientid}': '0', '${auth_xuid}': '0', '${user_type}': 'legacy',
    '${version_type}': 'release', '${resolution_width}': os.environ.get('MC_ANCHO', '1920'),
    '${resolution_height}': os.environ.get('MC_ALTO', '1080'), '${quickPlayPath}': '', '${quickPlaySingleplayer}': '',
    '${quickPlayMultiplayer}': '', '${quickPlayRealms}': '',
}


def args(lista):
    out = []
    for a in lista:
        if isinstance(a, dict):
            if not permitido(a.get('rules')):
                continue
            a = a['value']
        for x in (a if isinstance(a, list) else [a]):
            for k, v in vars_.items():
                x = x.replace(k, v)
            out.append(x)
    return out


jvm = args(vb['arguments']['jvm']) + args(vn['arguments'].get('jvm', []))
juego = args(vb['arguments']['game']) + args(vn['arguments'].get('game', []))
juego += (['--quickPlayMultiplayer', os.environ['MC_QUICKPLAY']] if os.environ.get('MC_QUICKPLAY') else [])
juego += (['--quickPlaySingleplayer', os.environ['MC_QUICKPLAY_SP']] if os.environ.get('MC_QUICKPLAY_SP') else [])
juego += ['--width', vars_['${resolution_width}'], '--height', vars_['${resolution_height}']]
java = os.environ.get('MC_JAVA', str(Path.home() / 'dev/tools/jdk-21.0.12.1+1/bin/java'))
cmd = [java, f"-Xmx{os.environ.get('MC_XMX', '6G')}", '-Xms1G'] + EXTRA + jvm + [vn['mainClass']] + juego
(INST / 'comando.txt').write_text('\n'.join(cmd))
os.chdir(INST)
os.execv(java, cmd)
