#!/usr/bin/env python3
"""Busca cofres dobles en los planos de estructura (.nbt) de los jars del pack.

Uso: python3 -I cofres_dobles.py <dir_jars> [salida.json]

Un cofre doble son dos bloques chest/trapped_chest con propiedad type=left/right.
Lootr los convierte en dos cofres individuales (issue LootrMinecraft/Lootr#886).
Solo cuenta los que tienen tabla de botín en el plano o pueden recibirla de un
procesador; marca 'con_botin' cuando el NBT del bloque trae LootTable.
"""
import gzip, io, json, struct, sys, zipfile
from pathlib import Path

def leer(f, t):
    if t == 1: return struct.unpack('>b', f.read(1))[0]
    if t == 2: return struct.unpack('>h', f.read(2))[0]
    if t == 3: return struct.unpack('>i', f.read(4))[0]
    if t == 4: return struct.unpack('>q', f.read(8))[0]
    if t == 5: return struct.unpack('>f', f.read(4))[0]
    if t == 6: return struct.unpack('>d', f.read(8))[0]
    if t == 7: n = leer(f, 3); return f.read(n)
    if t == 8: n = struct.unpack('>H', f.read(2))[0]; return f.read(n).decode('utf-8', 'replace')
    if t == 9:
        tt = leer(f, 1); n = leer(f, 3); return [leer(f, tt) for _ in range(n)]
    if t == 10:
        d = {}
        while True:
            tt = leer(f, 1)
            if tt == 0: return d
            k = leer(f, 8); d[k] = leer(f, tt)
    if t == 11: n = leer(f, 3); return struct.unpack(f'>{n}i', f.read(4 * n))
    if t == 12: n = leer(f, 3); return struct.unpack(f'>{n}q', f.read(8 * n))
    raise ValueError(t)

def raiz(data):
    if data[:2] == b'\x1f\x8b': data = gzip.decompress(data)
    f = io.BytesIO(data)
    if leer(f, 1) != 10: return {}
    leer(f, 8)
    return leer(f, 10)

res = {}
for jar in sorted(Path(sys.argv[1]).glob('*.jar')):
    try: z = zipfile.ZipFile(jar)
    except zipfile.BadZipFile: continue
    for n in z.namelist():
        if not (n.endswith('.nbt') and '/structure' in n and n.startswith('data/')): continue
        try: r = raiz(z.read(n))
        except Exception: continue
        pal = r.get('palette') or (r.get('palettes') or [[]])[0]
        idx = {i for i, p in enumerate(pal)
               if p.get('Name', '').endswith(('chest',)) and 'ender' not in p.get('Name', '')
               and p.get('Properties', {}).get('type') in ('left', 'right')}
        if not idx: continue
        mitades = [b for b in r.get('blocks', []) if b.get('state') in idx]
        botin = sum(1 for b in mitades if isinstance(b.get('nbt'), dict) and 'LootTable' in b['nbt'])
        res.setdefault(jar.name.split('-', 1)[1], []).append(
            {'plano': n, 'mitades': len(mitades), 'con_botin': botin})

resumen = {k: {'planos': len(v), 'mitades': sum(x['mitades'] for x in v),
               'mitades_con_botin': sum(x['con_botin'] for x in v)} for k, v in res.items()}
for k, v in sorted(resumen.items(), key=lambda kv: -kv[1]['mitades']):
    print(f"{v['planos']:4d} planos {v['mitades']:5d} mitades {v['mitades_con_botin']:5d} con LootTable  {k}")
if len(sys.argv) > 2:
    Path(sys.argv[2]).write_text(json.dumps({'resumen': resumen, 'detalle': res}, indent=1, ensure_ascii=False))
