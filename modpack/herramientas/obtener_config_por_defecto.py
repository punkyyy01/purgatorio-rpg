#!/usr/bin/env python3
"""Obtiene la configuración por defecto de los mods a partir de las versiones exactas de bloqueo.json.

Uso: python3 -I herramientas/obtener_config_por_defecto.py <dir_modpack> <dir_trabajo> --acepto-eula

Las configuraciones originales de los mods no se versionan (son de sus autores). Este script las genera:
1. Descarga cada jar de bloqueo.json del CDN de CurseForge y comprueba su SHA-1. Usa <dir_trabajo>/jars como caché.
2. Instala el servidor oficial de NeoForge (versión de pack.toml) desde maven.neoforged.net.
3. Arranca el servidor en local, sin red: primero sin EULA (FML solo escribe su fml.toml original), y después con
   maxThreads = 1 para que los mods carguen siempre en el mismo orden y cada uno escriba su config por defecto con
   un orden de claves reproducible.
4. Copia los archivos que necesita generar_criaturas.py a <dir_trabajo>/config_por_defecto.

Arrancar el servidor exige aceptar el EULA de Minecraft (https://aka.ms/MinecraftEULA): pasa --acepto-eula
solo si lo aceptas. Requiere Java 21 (variable JAVA o `java` en el PATH).
"""
import hashlib, json, os, shutil, socket, subprocess, sys, tomllib, urllib.parse, urllib.request
from pathlib import Path

UA = {'User-Agent': 'purgatorio-rpg build'}
# Mods solo de cliente: no se cargan en el servidor (no generan configuración necesaria).
SOLO_CLIENTE = {'Sodium', 'ImmediatelyFast', 'Entity Culling Fabric/Forge', 'Mouse Tweaks', 'Controlling', 'Searchables',
                'Enchantment Descriptions', 'AmbientSounds 6', 'Sound Physics Remastered', 'FancyMenu', 'Drippy Loading Screen', 'Konkrete', 'Melody', "Countered's Smooth Steps", 'Particular ✨ Reforged', 'Particle Rain', "Xaero's Minimap", "Xaero's World Map", 'EMI', 'AppleSkin'}
# Archivos que lee generar_criaturas.py (rutas relativas a config/).
NECESARIOS = ['amc.json', 'alexscaves-general.toml', 'iceandfire/iaf-common.json',
              'servercore/config.yml', 'servercore/optimizations.yml', 'cataclysm-common.toml',
              'endermanoverhaul.jsonc', 'moremobgriefingoptions-server.toml', 'fml.toml',
              'crittersandcompanions-common.json5']


def bajar(url, destino):
    tmp = destino.with_suffix(destino.suffix + '.part')
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as r, open(tmp, 'wb') as f:
        shutil.copyfileobj(r, f)
    tmp.rename(destino)


def sha1(p):
    h = hashlib.sha1()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    mp, trabajo = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    if '--acepto-eula' not in sys.argv:
        sys.exit('Hace falta --acepto-eula (EULA de Minecraft: https://aka.ms/MinecraftEULA).')
    neo = tomllib.loads((mp / 'pack.toml').read_text())['neoforge']
    entradas = json.loads((mp / 'bloqueo.json').read_text())['entradas']
    java = os.environ.get('JAVA', 'java')

    cache = trabajo / 'jars'; cache.mkdir(parents=True, exist_ok=True)
    srv = trabajo / 'servidor'
    if srv.exists():
        shutil.rmtree(srv)
    (srv / 'mods').mkdir(parents=True)

    # 1) Jars exactos del bloqueo, verificados por SHA-1.
    for e in entradas:
        if e['titulo'] in SOLO_CLIENTE:
            continue
        jar = cache / f"{e['fileID']}-{e['archivo']}"
        if not jar.exists() or sha1(jar) != e['sha1']:
            i = e['fileID']
            bajar(f"https://mediafilez.forgecdn.net/files/{i // 1000}/{i % 1000}/{urllib.parse.quote(e['archivo'])}", jar)
        if sha1(jar) != e['sha1']:
            sys.exit(f"SHA-1 distinto: {e['archivo']}")
        shutil.copy(jar, srv / 'mods' / e['archivo'])
    print(len(list((srv / 'mods').glob('*.jar'))), 'jars de servidor verificados')

    # 2) Servidor NeoForge oficial.
    inst = cache / f'neoforge-{neo}-installer.jar'
    if not inst.exists():
        bajar(f'https://maven.neoforged.net/releases/net/neoforged/neoforge/{neo}/neoforge-{neo}-installer.jar', inst)
    subprocess.run([java, '-jar', str(inst), '--installServer', str(srv)], check=True, stdout=subprocess.DEVNULL, cwd=trabajo)

    # 3) Arranques locales.
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0)); puerto = s.getsockname()[1]
    (srv / 'server.properties').write_text(f'server-ip=127.0.0.1\nserver-port={puerto}\nonline-mode=false\n'
                                           'level-name=mundo\nenable-rcon=false\nenable-query=false\n')
    (srv / 'user_jvm_args.txt').write_text('-Xmx4G\n')
    args = 'win_args.txt' if os.name == 'nt' else 'unix_args.txt'
    cmd = [java, '@user_jvm_args.txt', f'@libraries/net/neoforged/neoforge/{neo}/{args}', 'nogui']
    # 3a) Sin eula.txt el servidor se detiene enseguida; FML ya ha escrito su fml.toml original.
    subprocess.run(cmd, cwd=srv, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, timeout=600)
    fml_original = (srv / 'config' / 'fml.toml').read_text()
    fml = srv / 'config' / 'fml.toml'
    fml.write_text(fml_original.replace('maxThreads = -1', 'maxThreads = 1'))
    # 3b) Arranque completo, con carga de mods en un solo hilo.
    (srv / 'eula.txt').write_text('eula=true\n')
    p = subprocess.Popen(cmd, cwd=srv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    listo = False
    for linea in p.stdout:
        if 'Done (' in linea and not listo:
            listo = True
            p.stdin.write('stop\n'); p.stdin.flush()
    p.wait(timeout=600)
    if not listo:
        sys.exit('El servidor no llegó a arrancar; revisa ' + str(srv / 'logs' / 'latest.log'))
    fml.write_text(fml_original)   # se copia el original, no el modificado

    # 4) Copiar solo los archivos necesarios.
    dest = trabajo / 'config_por_defecto'
    if dest.exists():
        shutil.rmtree(dest)
    for rel in NECESARIOS:
        (dest / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(srv / 'config' / rel, dest / rel)
    print('config por defecto en', dest)


if __name__ == '__main__':
    main()
