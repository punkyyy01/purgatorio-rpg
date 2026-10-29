#!/usr/bin/env python3
"""Compara el manifest.json de dos zips de modpack (el generado en Costa Rica y el exportado por la app de CurseForge):
mismos projectID/fileID, misma versión de Minecraft y de NeoForge, y mismo contenido de config/ (por SHA-256 de cada archivo de overrides).
Uso: python3 -I comparar_manifiestos.py <zip_costa_rica> <zip_exportado_app>     Salida 0 = sin diferencias de mods/config."""
import hashlib, json, sys, zipfile
def cargar(p):
    z = zipfile.ZipFile(p); m = json.loads(z.read('manifest.json'))
    ov = m.get('overrides', 'overrides').rstrip('/') + '/'
    arch = {n[len(ov):]: hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith(ov) and not n.endswith('/')}
    return m, {(f['projectID'], f['fileID']) for f in m['files']}, arch
a, fa, oa = cargar(sys.argv[1]); b, fb, ob = cargar(sys.argv[2]); mal = 0
print('Minecraft:', a['minecraft']['version'], '|', b['minecraft']['version'], '· loader:', a['minecraft']['modLoaders'][0]['id'], '|', b['minecraft']['modLoaders'][0]['id'])
if a['minecraft']['version'] != b['minecraft']['version'] or a['minecraft']['modLoaders'][0]['id'] != b['minecraft']['modLoaders'][0]['id']: mal += 1; print('  DIFERENTE versión de Minecraft/loader')
for x in sorted(fa - fb): mal += 1; print('  SOLO en Costa Rica (mod):', x)
for x in sorted(fb - fa): mal += 1; print('  SOLO en el export (mod):', x)
for k in sorted(set(oa) | set(ob)):
    if k.startswith(('logs/', 'crash-reports/', 'saves/')): print('  AVISO: el export incluye', k); continue
    if oa.get(k) != ob.get(k): mal += 1; print('  overrides distinto:', k, '(falta en un lado)' if k not in oa or k not in ob else '')
print(f'mods: {len(fa)} vs {len(fb)}; archivos de overrides: {len(oa)} vs {len(ob)}; RESULTADO:', 'SIN DIFERENCIAS' if not mal else f'{mal} DIFERENCIAS')
sys.exit(1 if mal else 0)
