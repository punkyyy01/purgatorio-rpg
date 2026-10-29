#!/usr/bin/env python3
"""Prueba sin red de fuente_cf.py: simula respuestas de la API oficial (forma documentada en
docs.curseforge.com) y comprueba la normalización, la elección de fuente y el manejo de la clave.
Uso: python3 -I probar_fuente_cf.py"""
import importlib.util, json, os, stat, tempfile
from pathlib import Path

spec = importlib.util.spec_from_file_location('fuente_cf', Path(__file__).with_name('fuente_cf.py'))
fc = importlib.util.module_from_spec(spec); spec.loader.exec_module(fc)
CLAVE = 'clave-de-prueba-no-real'
llamadas = []


def falso_http(url, cabeceras=None, cuerpo=None, intentos=4):
    llamadas.append((url, dict(cabeceras or {}), cuerpo))
    assert (cabeceras or {}).get('x-api-key') == CLAVE and CLAVE not in url
    if '/v1/mods/search' in url:
        return {'data': [{'id': 686836, 'name': 'Tectonic', 'slug': 'tectonic', 'downloadCount': 10,
                          'authors': [{'id': 1, 'name': 'Apollo', 'url': ''}], 'allowModDistribution': True,
                          'links': {'websiteUrl': 'https://www.curseforge.com/minecraft/mc-mods/tectonic'}}]}
    if '/files' in url and 'index=0' in url:
        return {'data': [{'id': 8855043, 'fileName': 'tectonic-3.0.28-neoforge-21.1.jar', 'displayName': 'x', 'releaseType': 1,
                          'fileDate': '2026-09-11T00:00:00Z', 'fileLength': 451757, 'gameVersions': ['1.21.1', 'NeoForge'],
                          'hashes': [{'value': 'db15156eec4320c2997c4dd4948119472de01224', 'algo': 1}, {'value': 'm', 'algo': 2}],
                          'downloadUrl': None, 'isAvailable': True, 'dependencies': [{'modId': 1, 'relationType': 3}]}],
                'pagination': {'index': 0, 'pageSize': 50, 'resultCount': 1, 'totalCount': 2}}
    if '/files' in url and 'index=1' in url:
        return {'data': [{'id': 1, 'fileName': 'tectonic-beta.jar', 'releaseType': 2, 'fileDate': '2026-09-12T00:00:00Z',
                          'fileLength': 1, 'gameVersions': ['1.21.1', 'NeoForge'], 'hashes': [], 'dependencies': []}],
                'pagination': {'index': 1, 'pageSize': 50, 'resultCount': 1, 'totalCount': 2}}
    raise AssertionError('URL inesperada ' + url)


with tempfile.TemporaryDirectory() as t:
    os.environ.pop('CURSEFORGE_API_KEY', None)
    fc.ARCHIVO_CLAVE = Path(t) / 'no-existe'
    fc.ARCHIVO_CIFRADO = Path(t) / 'no-existe.cred'   # aislar de la clave real del equipo
    assert fc.fuente(t).nombre == 'cfwidget', 'sin clave debe usarse cfwidget'
    os.environ['PURGATORIO_FUENTE_CF'] = 'oficial'
    try:
        fc.fuente(t); raise AssertionError('oficial sin clave debe fallar')
    except SystemExit:
        pass
    # archivo de clave con permisos abiertos: se rechaza sin leerla
    fc.ARCHIVO_CLAVE = Path(t) / 'clave'; fc.ARCHIVO_CLAVE.write_text(CLAVE + '\n'); fc.ARCHIVO_CLAVE.chmod(0o644)
    try:
        fc.leer_clave(); raise AssertionError('permisos 644 deben rechazarse')
    except SystemExit as e:
        assert CLAVE not in str(e)
    fc.ARCHIVO_CLAVE.chmod(0o600)
    f = fc.fuente(t); assert f.nombre == 'oficial'
    fc._http = falso_http
    d = f.proyecto('tectonic')
    assert d['id'] == 686836 and d['title'] == 'Tectonic' and d['members'] == [{'username': 'Apollo'}]
    assert len(d['files']) == 2, 'debe recorrer todas las páginas'
    a = d['files'][0]
    assert a['type'] == 'release' and a['sha1'] == 'db15156eec4320c2997c4dd4948119472de01224' and a['filesize'] == 451757
    assert a['dependencias_cf'] == [{'modId': 1, 'tipo': 'obligatoria'}] and d['distribucion_permitida'] is True
    # sin caché en disco (condiciones de la API, sección 3.1) y la clave no se escribe en ningún archivo
    assert not list(Path(t).rglob('*.json')), 'la fuente oficial no debe guardar respuestas en disco'
    n = len(llamadas); f.proyecto('tectonic'); assert len(llamadas) == n, 'en la misma ejecución se reutiliza la respuesta en memoria'
    # misma elección de archivo que con CFWidget (release más reciente antes que beta)
    spec2 = importlib.util.spec_from_file_location('resolver', Path(__file__).with_name('resolver.py'))
    rs = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(rs)
    assert rs.elegir_archivo(d)['id'] == 8855043
    os.environ.pop('PURGATORIO_FUENTE_CF')
print('fuente_cf: todas las comprobaciones pasan (', len(llamadas), 'llamadas simuladas )')
