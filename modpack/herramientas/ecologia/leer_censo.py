#!/usr/bin/env python3
"""Cuenta las entidades guardadas en entities/*.mca por bioma (bioma de la celda 4x4x4 donde están).
Uso: leer_censo.py <dir_dimension> <salida.json>"""
import struct, zlib, os, sys, json, glob, math
from collections import Counter, defaultdict
def nbt(b):
    i = 0
    def rd(t):
        nonlocal i
        if t == 1: v = struct.unpack_from('>b', b, i)[0]; i += 1; return v
        if t == 2: v = struct.unpack_from('>h', b, i)[0]; i += 2; return v
        if t == 3: v = struct.unpack_from('>i', b, i)[0]; i += 4; return v
        if t == 4: v = struct.unpack_from('>q', b, i)[0]; i += 8; return v
        if t == 5: v = struct.unpack_from('>f', b, i)[0]; i += 4; return v
        if t == 6: v = struct.unpack_from('>d', b, i)[0]; i += 8; return v
        if t == 7: n = rd(3); v = b[i:i+n]; i += n; return v
        if t == 8: n = struct.unpack_from('>H', b, i)[0]; i += 2; v = b[i:i+n].decode('utf-8', 'replace'); i += n; return v
        if t == 9: et = b[i]; i += 1; n = rd(3); return [rd(et) for _ in range(n)]
        if t == 10:
            d = {}
            while True:
                tt = b[i]; i += 1
                if tt == 0: return d
                k = rd(8); d[k] = rd(tt)
        if t == 11: n = rd(3); v = struct.unpack_from(f'>{n}i', b, i); i += 4*n; return v
        if t == 12: n = rd(3); v = struct.unpack_from(f'>{n}q', b, i); i += 8*n; return v
        raise ValueError(t)
    t = b[0]; i = 1; rd(8); return rd(t)
def chunks(path):
    with open(path, 'rb') as f: data = f.read()
    for k in range(1024):
        off = int.from_bytes(data[k*4:k*4+3], 'big'); 
        if not off: continue
        p = off * 4096; ln = struct.unpack_from('>i', data, p)[0]; comp = data[p+4]
        raw = data[p+5:p+4+ln]
        yield nbt(zlib.decompress(raw) if comp == 2 else raw)
def biome_at(sec_by_y, x, y, z):
    s = sec_by_y.get(y >> 4)
    if not s: return None
    pal = s['palette']
    if len(pal) == 1: return pal[0]
    bits = max(1, math.ceil(math.log2(len(pal)))); per = 64 // bits
    idx = (((y & 15) >> 2) << 4) | (((z & 15) >> 2) << 2) | ((x & 15) >> 2)
    v = (s['data'][idx // per] >> ((idx % per) * bits)) & ((1 << bits) - 1)
    return pal[v]
dim, out = sys.argv[1:3]
biomas = {}  # (cx,cz) -> {secY: biomes}
chunk_biomas = Counter()
for r in glob.glob(f'{dim}/region/*.mca'):
    for c in chunks(r):
        if c.get('Status') != 'minecraft:full': continue
        secs = {s['Y']: s['biomes'] for s in c.get('sections', []) if 'biomes' in s}
        biomas[(c['xPos'], c['zPos'])] = secs
        hm = secs  # bioma de superficie aproximado: sección y=64
        b = biome_at(secs, c['xPos']*16+8, 70, c['zPos']*16+8); chunk_biomas[b] += 1
por_bioma = defaultdict(Counter); total = Counter()
for r in glob.glob(f'{dim}/entities/*.mca'):
    for c in chunks(r):
        for e in c.get('Entities', []):
            x, y, z = (math.floor(v) for v in e['Pos'])
            secs = biomas.get((x >> 4, z >> 4))
            b = biome_at(secs, x, y, z) if secs else '?'
            por_bioma[b][e['id']] += 1; total[e['id']] += 1
json.dump({'chunks_por_bioma': chunk_biomas, 'total': total, 'por_bioma': por_bioma}, open(out, 'w'), indent=1)
print(sum(chunk_biomas.values()), 'chunks completos;', sum(total.values()), 'entidades')
