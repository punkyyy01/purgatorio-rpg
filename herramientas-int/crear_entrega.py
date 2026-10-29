#!/usr/bin/env python3
"""Genera la entrega de PURG4TORY (zip de cliente, paquete de servidor, documentación, SHA-256) desde pack.toml + bloqueo.json.
Uso: python3 -I crear_entrega.py <dir_modpack> <dir_doc> <dir_entrega>      (no publica nada)
Toda la identidad (nombre, versión, canal) sale de pack.toml; los documentos pueden usar {{VERSION}}, {{VERSION_VISIBLE}}, {{NOMBRE}}, {{CANAL}}, {{CANDIDATA}}."""
import ast, hashlib, json, re, shutil, subprocess, sys, tomllib, zipfile
from pathlib import Path
mp, doc, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
shutil.rmtree(out, ignore_errors=True); out.mkdir(parents=True)
meta = tomllib.loads((mp/'pack.toml').read_text()); v = meta['version']
SUST = {'{{VERSION}}': v, '{{VERSION_VISIBLE}}': meta['version_visible'], '{{NOMBRE}}': meta['nombre'], '{{CANAL}}': meta['canal'], '{{CANDIDATA}}': meta['candidata_interna']}
def plantilla(t):
    for k, x in SUST.items(): t = t.replace(k, x)
    return t
subprocess.run([sys.executable, '-I', str(mp/'herramientas/empaquetar.py'), str(mp), str(out)], check=True)
b = json.load(open(mp/'bloqueo.json'))
solo_cliente = ast.literal_eval(re.search(r'SOLO_CLIENTE = (\{.*?\})', (mp/'herramientas/obtener_config_por_defecto.py').read_text(), re.S).group(1))
SIN_REDISTRIBUCION = {636540: 'Structory', 448233: 'Entity Culling', 1635121: "Alex's Mobs Continued", 550579: 'ServerCore', 883374: 'Hybrid API [HAPI]'}
lista = []
for e in sorted(b['entradas'], key=lambda e: e['titulo'].lower()):
    if e['titulo'] in solo_cliente: continue
    lista.append({'titulo': e['titulo'], 'archivo': e['archivo'], 'projectID': e['projectID'], 'fileID': e['fileID'], 'sha1': e['sha1'], 'bytes': e['bytes'],
                  'modIds': [m['modId'] for m in e['mods'] if not m.get('incluido_en_jarjar')], 'url': e['url'], 'descarga_automatica': e['projectID'] not in SIN_REDISTRIBUCION})
srv = out/f'PURG4TORY-servidor-{v}'; (srv/'overrides').mkdir(parents=True)
(srv/'mods-servidor.json').write_text(json.dumps({'version': v, 'minecraft': b['minecraft'], 'neoforge': meta['neoforge'], 'mods': lista}, indent=1, ensure_ascii=False))
tmp = out/'_ov'; subprocess.run([sys.executable, '-I', str(mp/'herramientas/empaquetar.py'), str(mp), str(out/'_x'), '--materializar', str(tmp)], check=True)
for d in ('config', 'defaultconfigs', 'mods'):
    if (tmp/d).exists(): shutil.copytree(tmp/d, srv/'overrides'/d)
shutil.rmtree(tmp); shutil.rmtree(out/'_x', ignore_errors=True)
for f in ('pregenerar.sh', 'RENDIMIENTO.md', 'rcon.py', 'parar.py', 'respaldo.py', 'verificar_mundo.py'):
    (srv/f).write_text(plantilla((mp/'servidor'/f).read_text()), encoding='utf-8') if f.endswith('.md') else shutil.copy(mp/'servidor'/f, srv/f)
shutil.copy(Path(__file__).with_name('instalar_servidor.py'), srv)
(srv/'LEEME.md').write_text(plantilla((doc/'SERVIDOR.md').read_text()))
zserv = out/f'PURG4TORY-servidor-{v}.zip'
with zipfile.ZipFile(zserv, 'w', zipfile.ZIP_DEFLATED) as z:
    for f in sorted(srv.rglob('*')):
        if f.is_file():
            zi = zipfile.ZipInfo(f.relative_to(out).as_posix(), date_time=(1980, 1, 1, 0, 0, 0)); zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = (0o755 if f.suffix in ('.sh', '.py') else 0o644) << 16; z.writestr(zi, f.read_bytes())
shutil.rmtree(srv)
shutil.copy(mp/'LISTA-MODS.md', out/'LISTA-MODS.md')
for f in sorted(doc.glob('*.md')):
    (out/f.name).write_text(plantilla(f.read_text()))
if (doc/'publicacion').exists():
    (out/'publicacion').mkdir()
    for f in sorted((doc/'publicacion').glob('*')): (out/'publicacion'/f.name).write_text(plantilla(f.read_text())) if f.suffix == '.md' else shutil.copy(f, out/'publicacion'/f.name)
if (doc/'capturas').exists(): shutil.copytree(doc/'capturas', out/'capturas')
sumas = [f'{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.relative_to(out).as_posix()}' for f in sorted(out.rglob('*')) if f.is_file() and f.name != 'SHA256SUMS.txt']
(out/'SHA256SUMS.txt').write_text('\n'.join(sumas) + '\n'); print('\n'.join(sumas))
