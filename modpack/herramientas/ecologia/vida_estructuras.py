#!/usr/bin/env python3
"""Busca en plantillas .nbt de estructuras (spawners/entidades) vidas máximas personalizadas.
Uso: vida_estructuras.py <jar>..."""
import zipfile, gzip, sys, struct, importlib.util
spec = importlib.util.spec_from_file_location('lc', __file__.replace('vida_estructuras.py', 'leer_censo.py'))
src = open(spec.origin).read().split('dim, out = sys.argv')[0]
ns = {}; exec(compile(src, 'leer_censo', 'exec'), ns); nbt = ns['nbt']
res = []
def walk(o, path, ent):
    if isinstance(o, dict):
        e = o.get('id') if isinstance(o.get('id'), str) and ':' in o.get('id', '') and 'generic' not in o.get('id','') else ent
        attrs = o.get('Attributes') or o.get('attributes')
        if isinstance(attrs, list):
            for a in attrs:
                if isinstance(a, dict) and 'max_health' in str(a.get('Name', a.get('id', ''))):
                    res.append((a.get('Base', a.get('base')), e, path, o.get('CustomName')))
        for k, v in o.items(): walk(v, path, e)
    elif isinstance(o, list):
        for v in o: walk(v, path, ent)
for j in sys.argv[1:]:
    z = zipfile.ZipFile(j)
    for n in z.namelist():
        if not n.endswith('.nbt'): continue
        b = z.read(n)
        if b'max_health' not in (d := (gzip.decompress(b) if b[:2] == b'\x1f\x8b' else b)): continue
        try: walk(nbt(d), j.split('-')[0] + ' ' + n, None)
        except Exception as ex: print('ERR', n, ex)
res.sort(key=lambda r: -(r[0] or 0))
for r in res[:25]: print(r[0], r[1], r[2][-80:], str(r[3] or '')[:60])
print(len(res), 'entidades con vida personalizada')
