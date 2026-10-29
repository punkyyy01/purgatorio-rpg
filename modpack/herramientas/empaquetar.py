#!/usr/bin/env python3
"""Genera el zip importable en CurseForge a partir de bloqueo.json y overrides/.

Uso: python3 -I empaquetar.py <dir_modpack> <dir_salida>
     python3 -I empaquetar.py <dir_modpack> --solo-lista   (regenera LISTA-MODS.md sin crear el zip)

El zip contiene solo manifest.json, modlist.html y overrides/ (archivos propios).
Los mods NO van dentro: el manifiesto los referencia por projectID/fileID y el
launcher de CurseForge los descarga de CurseForge.
"""
import html, json, re, sys, tomllib, zipfile
from pathlib import Path

# Plantillas: los archivos de overrides pueden contener {{VERSION}}, {{VERSION_VISIBLE}}, {{NOMBRE}}, {{CANAL}}; se sustituyen al
# empaquetar a partir de pack.toml (fuente única). Si queda un {{...}} sin resolver o una versión «literal» antigua, el build falla.
VERSION_LITERAL = re.compile(r'\b\d+\.\d+\.\d+-(?:alfa|alpha|beta|rc)\.\d+\b')
TEXTO = {'.txt', '.toml', '.json', '.json5', '.jsonc', '.properties', '.mcmeta', '.mcfunction', '.cfg', '.md'}

def renderizar(mp, meta):
    sust = {'{{VERSION}}': meta['version'], '{{VERSION_VISIBLE}}': meta.get('version_visible', meta['version']),
            '{{NOMBRE}}': meta['nombre'], '{{CANAL}}': meta.get('canal', '')}
    salida = {}
    for f in sorted((mp / 'overrides').rglob('*')):
        if not f.is_file(): continue
        rel = f.relative_to(mp / 'overrides').as_posix(); datos = f.read_bytes()
        if f.suffix.lower() in TEXTO:
            try: t = datos.decode('utf-8')
            except UnicodeDecodeError: t = None
            if t is not None:
                for k, v in sust.items(): t = t.replace(k, v)
                if '{{' in t and re.search(r'\{\{[A-Z_]+\}\}', t): raise SystemExit(f'plantilla sin resolver en overrides/{rel}')
                if rel.startswith('config/fancymenu/') and VERSION_LITERAL.search(t):
                    raise SystemExit(f'versión literal en overrides/{rel}: usar {{{{VERSION_VISIBLE}}}}')
                datos = t.encode('utf-8')
        salida[rel] = datos
    return salida

mp = Path(sys.argv[1]); solo_lista = sys.argv[2] == "--solo-lista"; salida = None if solo_lista else Path(sys.argv[2])
meta = tomllib.loads((mp / 'pack.toml').read_text())
b = json.load(open(mp / 'bloqueo.json'))
entradas = sorted(b['entradas'], key=lambda e: (e['pilar'] == 'dependencia', e['pilar'], e['titulo'].lower()))

manifest = {
    'minecraft': {'version': b['minecraft'],
                  'modLoaders': [{'id': f"neoforge-{meta['neoforge']}", 'primary': True}],
                  'recommendedRam': meta['ram_mb']},
    'manifestType': 'minecraftModpack', 'manifestVersion': 1,
    'name': meta['nombre'], 'version': meta['version'], 'author': meta['autor'],
    'files': [{'projectID': e['projectID'], 'fileID': e['fileID'], 'required': True} for e in entradas]
             + ([{'projectID': meta['cauces_cf']['projectID'], 'fileID': meta['cauces_cf']['fileID'], 'required': True}] if meta.get('cauces_cf') else []),
    'overrides': 'overrides',
}
modlist = '<ul>\n' + ''.join(
    f'<li><a href="{html.escape(e["url"])}">{html.escape(e["titulo"])}</a> ({html.escape(", ".join(e["autores"]))})</li>\n'
    for e in entradas) + '</ul>\n'

# Extensiones de overrides que la app de CurseForge marcó como «no de CurseForge» al importar
# el zip 0.1.1 (prueba manual 2026-10-20). .toml, .json y .mcmeta no se marcaron.
MARCADAS = {'.mcfunction', '.json5'}
for f in sorted((mp / 'overrides').rglob('*')):
    if f.is_file() and f.suffix in MARCADAS:
        print('AVISO CurseForge:', f.relative_to(mp / 'overrides'), 'disparará la advertencia de archivos externos')

if not solo_lista:
  salida.mkdir(parents=True, exist_ok=True)
zpath = None
if not solo_lista:
  if len(sys.argv) > 3 and sys.argv[3] == '--materializar':   # vuelca los overrides ya renderizados (para pruebas y servidor)
      for rel, datos in renderizar(mp, meta).items():
          d = Path(sys.argv[4]) / rel; d.parent.mkdir(parents=True, exist_ok=True); d.write_bytes(datos)
      sys.exit(0)
  # Nombre de archivo válido en Windows (sin «:» ni otros caracteres reservados).
  zpath = salida / (re.sub(r'[^A-Za-z0-9._-]+', '-', meta['nombre']).strip('-') + f"-{meta['version']}.zip")
if not solo_lista:
  # Fecha y permisos fijos en cada entrada: dos construcciones del mismo commit dan el mismo zip byte a byte.
  def entrada(nombre):
      zi = zipfile.ZipInfo(nombre, date_time=(1980, 1, 1, 0, 0, 0))
      zi.compress_type = zipfile.ZIP_DEFLATED
      zi.external_attr = 0o644 << 16
      return zi
  with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr(entrada('manifest.json'), json.dumps(manifest, indent=2, ensure_ascii=False))
    z.writestr(entrada('modlist.html'), modlist)
    for rel, datos in renderizar(mp, meta).items():
        # Con cauces_cf (pack.toml) Cauces va como proyecto de CurseForge y su jar NO va en overrides/mods (política de CurseForge).
        if meta.get('cauces_cf') and rel.startswith('mods/purg4tory_cauces'): continue
        z.writestr(entrada('overrides/' + rel), datos)

# Lista legible versionada en el repo
filas = ['| Mod | Pilar | Archivo exacto | Tipo | Licencia | CurseForge (proyecto/archivo) |', '|---|---|---|---|---|---|']
for e in entradas:
    filas.append(f"| [{e['titulo']}]({e['url']}) | {e['pilar']} | `{e['archivo']}` | {e['tipo']} | "
                 f"{e.get('licencia') or '?'} | {e['projectID']}/{e['fileID']} |")
(mp / 'LISTA-MODS.md').write_text(
    f"# Mods de {meta['nombre']} {meta.get('version_visible', meta['version'])}\n\nMinecraft {b['minecraft']}, NeoForge {meta['neoforge']}. "
    f"{len(entradas)} archivos ({sum(e['pilar'] != 'dependencia' for e in entradas)} elegidos y "
    f"{sum(e['pilar'] == 'dependencia' for e in entradas)} dependencias). Generado por `herramientas/empaquetar.py`.\n\n"
    + '\n'.join(filas) + '\n')
print('LISTA-MODS.md actualizada' if solo_lista else f'{zpath} {zpath.stat().st_size} bytes,', len(entradas), 'mods')
