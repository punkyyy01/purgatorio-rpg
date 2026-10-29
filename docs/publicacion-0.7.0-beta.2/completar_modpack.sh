#!/bin/bash
# Genera los zips definitivos de PURG4TORY: Souls Grimore 0.7.0-beta.2 cuando Cauces 0.5.0 ya está aprobado en CurseForge.
# Uso (desde cualquier sitio): docs/publicacion-0.7.0-beta.2/completar_modpack.sh <fileID de Cauces 0.5.0>   (no publica nada)
# Escribe el fileID en modpack/pack.toml y deja en <repo>/entrega/ el zip de cliente, el paquete de servidor y VERIFICACION.txt.
set -e
cd "$(dirname "$0")/../.."     # raíz del repositorio
FID="$1"; [[ "$FID" =~ ^[0-9]{6,10}$ ]] || { echo "Uso: $0 <fileID numérico de Cauces 0.5.0 en CurseForge>"; exit 1; }
SHA_CAUCES=83b00079624a17785f24d311eb515bd62c2b82e76e06c40b513b94f7f5b6d8ff
PUBLICADO=${PUBLICADO:-$HOME/dev/purg4tory-beta1/entrega_0.6.0-beta.1.1/PURG4TORY-Souls-Grimore-0.6.0-beta.1.1.zip}   # = CurseForge 9325709 (opcional, para comparar)
HERR=herramientas-int/crear_entrega.py

echo "$SHA_CAUCES  modpack/overrides/mods/purg4tory_cauces-0.5.0.jar" | sha256sum -c --quiet
sed -i -E "s/^#? ?cauces_cf = \{ projectID = 1763725, fileID = [^}]+\}.*/cauces_cf = { projectID = 1763725, fileID = $FID }   # Cauces 0.5.0 en CurseForge/" modpack/pack.toml
grep -q "^cauces_cf = { projectID = 1763725, fileID = $FID }" modpack/pack.toml || { echo "No pude escribir el fileID en modpack/pack.toml"; exit 1; }

python3 -I "$HERR" modpack doc entrega > entrega.log 2>&1 || { echo "crear_entrega.py falló: ver entrega.log"; exit 1; }

python3 -I - "$FID" "$SHA_CAUCES" "$PUBLICADO" <<'EOF' | tee VERIFICACION.txt
import hashlib, json, sys, zipfile, glob
fid, sha_c, publicado = int(sys.argv[1]), sys.argv[2], sys.argv[3]
cli = zipfile.ZipFile('entrega/PURG4TORY-Souls-Grimore-0.7.0-beta.2.zip')
srv = zipfile.ZipFile('entrega/PURG4TORY-servidor-0.7.0-beta.2.zip')
m = json.loads(cli.read('manifest.json')); ids = [f['projectID'] for f in m['files']]
fallos = []
def ok(c, txt): print(('OK   ' if c else 'FALLO') + ' ' + txt); c or fallos.append(txt)
ok(m['version'] == '0.7.0-beta.2', f"versión del manifiesto: {m['version']}")
ok(m['minecraft']['version'] == '1.21.1', f"Minecraft del manifiesto: {m['minecraft']['version']}")
ok(m['minecraft']['modLoaders'][0]['id'] == 'neoforge-21.1.259', f"loader: {m['minecraft']['modLoaders'][0]['id']}")
ok(len(ids) == 154 and len(ids) == len(set(ids)), f"{len(ids)} archivos de CurseForge, sin duplicados")
ok({'projectID': 1763725, 'fileID': fid, 'required': True} in m['files'], f"Cauces referenciado como proyecto 1763725, fileID {fid}")
ok(not [n for n in cli.namelist() if n.endswith('.jar')], "el zip de cliente no lleva ningún jar suelto")
sj = [n for n in srv.namelist() if n.endswith('mods/purg4tory_cauces-0.5.0.jar')]
ok(len(sj) == 1 and hashlib.sha256(srv.read(sj[0])).hexdigest() == sha_c, "el paquete de servidor lleva Cauces 0.5.0 (sha256 correcto)")
for f in ('overrides/config/fancymenu/customization/purg4tory_titulo.txt',
          'overrides/config/paxi/datapacks/purgatorio_bienvenida/data/purgatorio/loot_table/bienvenida/guia.json'):
    t = cli.read(f).decode('utf8', 'replace'); ok('0.7.0 Beta 2' in t and '0.6.0 Beta' not in t, f"«0.7.0 Beta 2» en {f.split('/')[-1]}")
p = cli.read('overrides/config/purg4tory_cauces.properties').decode()
ok(all(k + '=true' in p for k in ('consultasSinEsperar', 'cargadoEsListo', 'movimientoAListo', 'cadenasGlobales', 'spawnsSinEsperar')), "configuración de Cauces con las 5 opciones de 0.5.0")
import os
if not os.path.exists(publicado):
    print('AVISO no encuentro el zip publicado para comparar (variable PUBLICADO); se omite esa comprobación')
else:
    pub = zipfile.ZipFile(publicado)
    hp = {n: hashlib.sha1(pub.read(n)).hexdigest() for n in pub.namelist()}; hn = {n: hashlib.sha1(cli.read(n)).hexdigest() for n in cli.namelist()}
    esperado = {'manifest.json', 'overrides/config/fancymenu/customization/purg4tory_titulo.txt',
                'overrides/config/paxi/datapacks/purgatorio_bienvenida/data/purgatorio/loot_table/bienvenida/guia.json',
                'overrides/config/purg4tory_cauces.properties'}
    cambios = {n for n in hn if n in hp and hn[n] != hp[n]}; nuevos = set(hn) - set(hp); quitados = set(hp) - set(hn)
    ok(cambios <= esperado and not nuevos and quitados == {'overrides/mods/purg4tory_cauces-0.4.1.jar'},
       f"respecto a lo publicado (9325709) solo cambia lo previsto: cambiados {len(cambios)}, nuevos {len(nuevos)}, quitados {sorted(quitados)}")
print()
for z in sorted(glob.glob('entrega/*.zip')):
    print(hashlib.sha256(open(z, 'rb').read()).hexdigest(), 'sha1', hashlib.sha1(open(z, 'rb').read()).hexdigest(), z.split('/')[-1])
print('\nRESULTADO:', 'TODO CORRECTO: listo para subir' if not fallos else f'{len(fallos)} FALLOS: NO SUBIR')
sys.exit(1 if fallos else 0)
EOF
