#!/usr/bin/env python3
"""Fuentes de metadatos de CurseForge para las herramientas del modpack.

Dos fuentes que devuelven los proyectos con la misma forma (la de CFWidget, que ya usa resolver.py):
- `oficial`: API oficial de CurseForge (api.curseforge.com). Necesita una clave de la consola de
  CurseForge for Studios. Da además SHA-1, dependencias declaradas en CurseForge y si el autor
  permite la distribución por terceros.
- `cfwidget`: api.cfwidget.com, no oficial y sin clave. Es la fuente por defecto si no hay clave.

Elección (variable PURGATORIO_FUENTE_CF): `auto` (por defecto: oficial si hay clave, si no cfwidget),
`oficial` (falla si no hay clave) o `cfwidget`.

La clave NUNCA va en el repositorio, en argumentos de la línea de órdenes ni en los registros:
- variable de entorno CURSEFORGE_API_KEY, o
- archivo ~/.config/purgatorio-rpg/curseforge-api-key (solo legible por su dueño: chmod 600).
Construir el zip no necesita clave ni red: empaquetar.py solo lee bloqueo.json y overrides/.
"""
import json, os, stat, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path

UA = {'User-Agent': 'punkyyy01/purgatorio-rpg modpack build'}
API = 'https://api.curseforge.com'
MINECRAFT, CLASE_MODS = 432, 6
TIPO_ARCHIVO = {1: 'release', 2: 'beta', 3: 'alpha'}
RELACION = {1: 'embebida', 2: 'opcional', 3: 'obligatoria', 4: 'herramienta', 5: 'incompatible', 6: 'incluida'}
ARCHIVO_CLAVE = Path.home() / '.config' / 'purgatorio-rpg' / 'curseforge-api-key'
# Clave cifrada con `systemd-creds --user` (la misma que usa el servidor MCP ~/dev/purg4tory-curseforge-mcp).
ARCHIVO_CIFRADO = ARCHIVO_CLAVE.with_name('curseforge-api-key.cred')


class SinClave(Exception):
    pass


def leer_clave():
    """Devuelve la clave o None. No la imprime nunca."""
    c = os.environ.get('CURSEFORGE_API_KEY', '').strip()
    if c:
        return c
    if ARCHIVO_CIFRADO.exists():
        st = ARCHIVO_CIFRADO.stat()
        if st.st_mode & (stat.S_IRWXG | stat.S_IRWXO) or st.st_uid != os.getuid():
            raise SystemExit(f'{ARCHIVO_CIFRADO}: permisos demasiado abiertos; usa chmod 600 (no se ha leído la clave)')
        import subprocess
        r = subprocess.run(['systemd-creds', '--user', 'decrypt', '--name=curseforge-api-key', str(ARCHIVO_CIFRADO), '-'],
                           capture_output=True, text=True, timeout=15)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
        raise SystemExit(f'no se pudo descifrar {ARCHIVO_CIFRADO} (systemd-creds terminó con código {r.returncode})')
    if ARCHIVO_CLAVE.exists():
        st = ARCHIVO_CLAVE.stat()
        if st.st_mode & (stat.S_IRWXG | stat.S_IRWXO) or st.st_uid != os.getuid():
            raise SystemExit(f'{ARCHIVO_CLAVE}: permisos demasiado abiertos; usa chmod 600 (no se ha leído la clave)')
        return ARCHIVO_CLAVE.read_text().strip() or None
    return None


def _http(url, cabeceras=None, cuerpo=None, intentos=4):
    h = dict(UA, **(cabeceras or {}))
    if cuerpo is not None:
        h['Content-Type'] = 'application/json'
        cuerpo = json.dumps(cuerpo).encode()
    for i in range(intentos):
        try:
            return json.loads(urllib.request.urlopen(urllib.request.Request(url, data=cuerpo, headers=h), timeout=120).read())
        except urllib.error.HTTPError as e:
            # 403 con clave = clave rechazada; no se reintenta ni se muestra la petición (lleva la clave en la cabecera).
            if e.code in (401, 403, 404) or i == intentos - 1:
                raise RuntimeError(f'HTTP {e.code} en {url.split("?")[0]}') from None
        except Exception:
            if i == intentos - 1:
                raise
        time.sleep(3 + 3 * i)


class CFWidget:
    nombre = 'cfwidget'

    def __init__(self, cache):
        self.cache = Path(cache) / 'cfwidget'

    def proyecto(self, slug):
        f = self.cache / f'{slug}.json'
        if f.exists() and time.time() - f.stat().st_mtime < 6 * 3600:
            return json.loads(f.read_text())
        ruta = slug if str(slug).isdigit() else 'minecraft/mc-mods/' + slug
        d = _http('https://api.cfwidget.com/' + ruta)
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(d))
        time.sleep(0.5)
        return d


class Oficial:
    """API oficial. Normaliza a la forma de CFWidget y añade a cada archivo `sha1`, `dependencias_cf`
    y `url_descarga`, y al proyecto `distribucion_permitida`."""
    nombre = 'oficial'

    def __init__(self, cache, clave):
        # Sin caché en disco: las condiciones de la API de terceros (sección 3.1) prohíben guardar o cachear sus datos.
        self._memoria = {}
        self._h = {'x-api-key': clave, 'Accept': 'application/json'}

    def _get(self, ruta, **params):
        q = ('?' + urllib.parse.urlencode(params)) if params else ''
        return _http(API + ruta + q, self._h)

    def _post(self, ruta, cuerpo):
        return _http(API + ruta, self._h, cuerpo)

    def buscar_slug(self, slug):
        r = self._get('/v1/mods/search', gameId=MINECRAFT, classId=CLASE_MODS, slug=slug)['data']
        if not r:
            raise RuntimeError(f'{slug}: no existe en CurseForge')
        return r[0]

    def archivos(self, mod_id, version='1.21.1'):
        fs, i = [], 0
        while True:
            r = self._get(f'/v1/mods/{mod_id}/files', gameVersion=version, index=i, pageSize=50)
            fs += r['data']
            p = r['pagination']
            i += p['resultCount']
            if not p['resultCount'] or i >= p['totalCount']:
                return fs

    @staticmethod
    def normalizar(m, archivos):
        fs = []
        for f in archivos:
            sha1 = next((h['value'] for h in f.get('hashes', []) if h.get('algo') == 1), None)
            fs.append({'id': f['id'], 'name': f['fileName'], 'display': f.get('displayName'),
                       'type': TIPO_ARCHIVO.get(f.get('releaseType'), 'alpha'), 'uploaded_at': f['fileDate'],
                       'filesize': f['fileLength'], 'versions': f.get('gameVersions', []),
                       'sha1': sha1, 'url_descarga': f.get('downloadUrl'), 'disponible': f.get('isAvailable', True),
                       'dependencias_cf': [{'modId': d['modId'], 'tipo': RELACION.get(d['relationType'], str(d['relationType']))}
                                           for d in f.get('dependencies', [])]})
        return {'id': m['id'], 'title': m['name'], 'slug': m.get('slug'), 'license': '',
                'downloads': {'total': m.get('downloadCount', 0)},
                'members': [{'username': a['name']} for a in m.get('authors', [])],
                'urls': {'curseforge': (m.get('links') or {}).get('websiteUrl', '')},
                'distribucion_permitida': m.get('allowModDistribution'),
                'files': fs}

    def proyecto(self, slug):
        if slug not in self._memoria:   # solo durante esta ejecución
            m = self._get(f'/v1/mods/{slug}')['data'] if str(slug).isdigit() else self.buscar_slug(slug)
            self._memoria[slug] = self.normalizar(m, self.archivos(m['id']))
        return self._memoria[slug]

    def archivos_por_id(self, ids):
        """Comprobación del bloqueo: metadatos de una lista de fileID en una sola petición."""
        return {f['id']: f for f in self._post('/v1/mods/files', {'fileIds': list(ids)})['data']}


def fuente(cache):
    modo = os.environ.get('PURGATORIO_FUENTE_CF', 'auto')
    if modo not in ('auto', 'oficial', 'cfwidget'):
        raise SystemExit(f'PURGATORIO_FUENTE_CF={modo}: usa auto, oficial o cfwidget')
    clave = None if modo == 'cfwidget' else leer_clave()
    if modo == 'oficial' and not clave:
        raise SystemExit('Fuente oficial pedida pero no hay clave (CURSEFORGE_API_KEY, ' + str(ARCHIVO_CIFRADO) + ' o ' + str(ARCHIVO_CLAVE) + ')')
    return Oficial(cache, clave) if clave else CFWidget(cache)

