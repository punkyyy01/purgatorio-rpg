#!/usr/bin/env python3
"""Instala los mods del servidor PURG4TORY desde el CDN de CurseForge y verifica el SHA-1 de cada archivo.
Uso: python3 instalar_servidor.py <dir_servidor> [--instalar-neoforge] [--mover-obsoletos]
     --instalar-neoforge: descarga el instalador oficial de NeoForge (maven.neoforged.net), comprueba su SHA-1 contra el publicado por
     NeoForged y ejecuta «java -jar ... --installServer» en <dir_servidor>. Sin esta opción NeoForge ya debe estar instalado (ver SERVIDOR.md).

- No descarga los proyectos cuyo autor no permite la distribución por terceros: los lista para bajarlos a mano.
- Después de instalar REVISA mods/: avisa de jars que no figuran en la lista de esta versión. Para cada uno lee su modId:
    * OBSOLETO: mismo modId que un mod de la lista pero otro archivo (p. ej. una versión anterior). Dos versiones del mismo mod
      hacen que NeoForge no arranque o cargue la equivocada.
    * DESCONOCIDO: modId que no está en la lista (otro mod o una versión que no es de este pack). No se toca.
    * DUPLICADO: dos jars con el mismo modId.
- NUNCA borra nada. Con --mover-obsoletos solo mueve los OBSOLETOS (procedencia comprobada por modId) a <dir_servidor>/mods-obsoletos/,
  de donde se pueden recuperar. Sin esa opción solo avisa e imprime los comandos. Código de salida 3 si queda algún obsoleto o duplicado; 4 si faltan descargas manuales."""
import hashlib, io, json, shutil, sys, tomllib, urllib.parse, urllib.request, zipfile
from pathlib import Path
aqui = Path(__file__).resolve().parent; args = [a for a in sys.argv[1:] if not a.startswith('--')]
dest = Path(args[0]).resolve(); mods = dest/'mods'; mods.mkdir(parents=True, exist_ok=True); mover = '--mover-obsoletos' in sys.argv
datos = json.load(open(aqui/'mods-servidor.json')); manual = []; fallos = []

if '--instalar-neoforge' in sys.argv:
    import subprocess
    v = datos['neoforge']; base = f'https://maven.neoforged.net/releases/net/neoforged/neoforge/{v}/neoforge-{v}-installer.jar'
    try:
        jar = urllib.request.urlopen(urllib.request.Request(base, headers={'User-Agent': 'purg4tory-servidor-instalador'}), timeout=120).read()
        sha = urllib.request.urlopen(base + '.sha1', timeout=60).read().decode().split()[0].strip()
        assert hashlib.sha1(jar).hexdigest() == sha, 'el SHA-1 del instalador de NeoForge no coincide con el publicado'
    except Exception as ex:
        sys.exit(f'No se pudo obtener el instalador de NeoForge {v}: {ex}\nDescárgalo a mano de https://neoforged.net y ejecuta: java -jar neoforge-{v}-installer.jar --installServer')
    (dest/'neoforge-installer.jar').write_bytes(jar)
    if subprocess.run(['java', '-jar', 'neoforge-installer.jar', '--installServer'], cwd=dest).returncode != 0:
        sys.exit('La instalación de NeoForge falló (¿Java 21 en el PATH? comprueba «java -version»).')
    print('NeoForge', v, 'instalado en', dest)


def ids_de_jar(p):
    """modIds propios del jar (no los de jarjar), leídos de neoforge.mods.toml."""
    try:
        with zipfile.ZipFile(p) as z:
            t = tomllib.loads(z.read('META-INF/neoforge.mods.toml').decode('utf8'))
            return [m['modId'] for m in t.get('mods', [])]
    except Exception:
        return []


for m in datos['mods']:
    f = mods/m['archivo']
    if f.exists() and hashlib.sha1(f.read_bytes()).hexdigest() == m['sha1']: continue
    if not m['descarga_automatica']: manual.append(m); continue
    i = m['fileID']; url = f"https://mediafilez.forgecdn.net/files/{i // 1000}/{i % 1000}/{urllib.parse.quote(m['archivo'])}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'purg4tory-servidor-instalador'})
        b = urllib.request.urlopen(req, timeout=60).read()
        assert hashlib.sha1(b).hexdigest() == m['sha1'], 'SHA-1 distinto'
        f.write_bytes(b); print('ok', m['archivo'])
    except Exception as ex: fallos.append((m, str(ex)))
# Actualizaciones: antes de sobrescribir config/ se guarda una copia, y los datapacks propios (purgatorio_*) que ya no existen en esta
# versión se APARTAN (no se borran) para que no sigan cargándose.
import tarfile, time
if (dest/'config').exists() and any((dest/'config').iterdir()):
    (dest/'respaldos-config').mkdir(exist_ok=True)
    with tarfile.open(dest/'respaldos-config'/f"config-{time.strftime('%Y%m%d-%H%M%S')}.tar.gz", 'w:gz') as t: t.add(dest/'config', arcname='config')
    print('copia de config/ guardada en respaldos-config/ (se sobrescribirá con la de esta versión)')
nuevos = (aqui/'overrides'/'config'/'paxi'/'datapacks'); viejos = dest/'config'/'paxi'/'datapacks'
if viejos.exists():
    for d in sorted(viejos.glob('purgatorio_*')):
        if not (nuevos/d.name).exists():
            (dest/'config-obsoleta').mkdir(exist_ok=True); shutil.move(str(d), str(dest/'config-obsoleta'/d.name)); print('datapack obsoleto apartado a config-obsoleta/:', d.name)
for d in ('config', 'defaultconfigs', 'mods'):
    if (aqui/'overrides'/d).exists(): shutil.copytree(aqui/'overrides'/d, dest/d, dirs_exist_ok=True)

# Revisión de mods/: jars que no son de esta versión.
conocidos = {m['archivo']: m['modIds'] for m in datos['mods']}
for j in (aqui/'overrides'/'mods').glob('*.jar'): conocidos[j.name] = ids_de_jar(j)
por_id = {i: a for a, ids in conocidos.items() for i in ids}
presentes = {j.name: ids_de_jar(j) for j in sorted(mods.glob('*.jar'))}
sobrantes = [(n, ids) for n, ids in presentes.items() if n not in conocidos]
obsoletos = [(n, ids, por_id[i]) for n, ids in sobrantes for i in ids if i in por_id][:]
vistos = {}; duplicados = []
for n, ids in presentes.items():
    for i in ids:
        if i in vistos: duplicados.append((i, vistos[i], n))
        vistos[i] = n
print('\nREVISIÓN DE mods/')
nombres_obs = {n for n, _, _ in obsoletos}
for n, ids, nuevo in obsoletos:
    print(f"  OBSOLETO  {n}  (modId {ids[0]}; esta versión lleva {nuevo})")
for n, ids in sobrantes:
    if n not in nombres_obs: print(f"  DESCONOCIDO  {n}  (modId {', '.join(ids) or 'ilegible'}); no figura en esta versión, no se toca")
for i, a, b in duplicados: print(f"  DUPLICADO  modId {i}: {a} y {b}")
if mover and obsoletos:
    (dest/'mods-obsoletos').mkdir(exist_ok=True)
    for n, _, _ in obsoletos: shutil.move(str(mods/n), str(dest/'mods-obsoletos'/n)); print('  movido a mods-obsoletos/:', n)
elif obsoletos:
    print('  Para retirarlos (no se ha borrado nada):  mkdir -p mods-obsoletos && ' + ' && '.join(f'mv "mods/{n}" mods-obsoletos/' for n, _, _ in obsoletos)
          + '\n  o vuelve a ejecutar este instalador con --mover-obsoletos')
if not (obsoletos or sobrantes or duplicados): print('  limpio: mods/ coincide con la lista de esta versión')
if manual: print('\nDESCARGA MANUAL (el autor no permite la distribución por terceros): bájalos de CurseForge y ponlos en mods/')
for m in manual: print(f"  {m['titulo']}: {m['url']}/files/{m['fileID']}  ({m['archivo']}, sha1 {m['sha1']})")
if fallos:
    print('\nFALLOS:'); [print(' ', m['archivo'], e) for m, e in fallos]; sys.exit(1)
if mover: duplicados = [d for d in duplicados if d[1] not in nombres_obs and d[2] not in nombres_obs]
if manual: print(f'\nFALTAN {len(manual)} DESCARGAS MANUALES: el servidor no arrancará (o le faltarán mods) hasta ponerlos en mods/. Vuelve a ejecutar este instalador para comprobarlos.')
sys.exit(3 if ((obsoletos and not mover) or duplicados) else (4 if manual else 0))
