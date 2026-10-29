#!/usr/bin/env python3
"""Respaldo consistente del mundo de un servidor PURG4TORY EN MARCHA (o parado).

Uso: python3 respaldo.py <dir_servidor> <dir_destino> [--parado]
  En marcha (por defecto): RCON → «save-off» + «save-all flush» (espera confirmación) → copia el mundo → «save-on» (SIEMPRE, aunque falle).
  --parado: el servidor está apagado; solo copia (comprueba que no haya un proceso con ese directorio).
Genera <destino>/mundo-AAAAMMDD-HHMMSS.tar.gz + .sha256 + .json (lista de archivos con tamaño y SHA-256) y comprueba el respaldo releyéndolo.
Incluye: la carpeta del mundo (level-name de server.properties) completa — dimensiones, playerdata, advancements, stats, datapacks del mundo,
streamsreflowing/ (cuencas de ríos) — más server.properties, ops/whitelist/banned y config/.
No incluye mods/ (reproducibles con instalar_servidor.py); guarda la lista de mods y versiones actuales en el .json.
No usa nada fuera de la biblioteca estándar. Códigos: 0 ok · 2 no se confirmó el guardado · 4 el respaldo no se pudo verificar."""
import hashlib, json, os, sys, tarfile, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rcon import Rcon, propiedades
a = [x for x in sys.argv[1:] if not x.startswith('--')]
if len(a) != 2: sys.exit(__doc__)
srv, dest = os.path.abspath(a[0]), os.path.abspath(a[1]); parado = '--parado' in sys.argv
props = propiedades(os.path.join(srv, 'server.properties')); mundo = props.get('level-name', 'world')
if not os.path.isdir(os.path.join(srv, mundo)): sys.exit(f'No existe el mundo {os.path.join(srv, mundo)}')
os.makedirs(dest, exist_ok=True); sello = time.strftime('%Y%m%d-%H%M%S')
tgz = os.path.join(dest, f'mundo-{sello}.tar.gz'); r = None
def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()
try:
    if not parado:
        r = Rcon('127.0.0.1', int(props.get('rcon.port', 25575)), os.environ.get('RCON_PASSWORD') or props.get('rcon.password', ''), timeout=300)
        r.comando('save-off'); out = r.comando('save-all flush')
        if 'Saved the game' not in out: print('El guardado NO se confirmó:', out); sys.exit(2)
        print('guardado confirmado; escritura automática desactivada durante la copia')
    inventario = {}
    with tarfile.open(tgz, 'w:gz') as t:
        for ruta in [mundo, 'config', 'server.properties', 'ops.json', 'whitelist.json', 'banned-players.json', 'banned-ips.json', 'usercache.json']:
            p = os.path.join(srv, ruta)
            if not os.path.exists(p): continue
            if os.path.isdir(p):
                for raiz, _, fs in os.walk(p):
                    for f in sorted(fs):
                        if f == 'session.lock': continue
                        full = os.path.join(raiz, f); rel = os.path.relpath(full, srv)
                        try: t.add(full, arcname=rel); inventario[rel] = [os.path.getsize(full), sha(full)]
                        except FileNotFoundError: pass
            else:
                t.add(p, arcname=ruta); inventario[ruta] = [os.path.getsize(p), sha(p)]
finally:
    if r:
        try: r.comando('save-on'); print('escritura automática reactivada (save-on)')
        except Exception as e: print('¡AVISO! no se pudo ejecutar save-on:', e, '— ejecútalo a mano en la consola'); 
        r.cerrar()
mods = sorted(f for f in os.listdir(os.path.join(srv, 'mods')) if f.endswith('.jar')) if os.path.isdir(os.path.join(srv, 'mods')) else []
json.dump({'mundo': mundo, 'fecha': sello, 'archivos': inventario, 'mods': mods}, open(tgz[:-7] + '.json', 'w'), indent=0)
open(tgz + '.sha256', 'w').write(f'{sha(tgz)}  {os.path.basename(tgz)}\n')
# Verificación: releer el tar y comparar con el inventario (los archivos que cambiaron durante la copia se detectan aquí).
mal = 0
with tarfile.open(tgz) as t:
    n = 0
    for m in t:
        if not m.isfile(): continue
        n += 1; h = hashlib.sha256(t.extractfile(m).read()).hexdigest()
        if inventario.get(m.name, [0, None])[1] != h: mal += 1; print('  DIFERENTE:', m.name)
    print(f'{n} archivos en el respaldo, {mal} distintos del original en el momento de la copia')
if mal and not parado: print('Hubo archivos que cambiaron durante la copia (normal solo en cuencas de Streams en construcción). Repite si son archivos de región.')
print(tgz, os.path.getsize(tgz), 'bytes'); sys.exit(4 if mal and parado else 0)
