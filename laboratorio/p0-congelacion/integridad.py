#!/usr/bin/env python3
"""Integridad completa de un mundo (solo lectura, sin Minecraft): lee TODOS los chunks de todas las regiones.
Comprueba: cabecera .mca, descompresión, NBT completo, xPos/zPos == posición en el archivo, Status, DataVersion.
Uso: integridad.py <dir_mundo> [--json salida.json]"""
import collections, json, os, struct, sys, zlib, gzip, io

# lector NBT copiado de modpack/servidor/verificar_mundo.py (Beta 1)
def nbt(data):
    f = io.BytesIO(data)
    def leer(tipo):
        if tipo == 1: return struct.unpack('>b', f.read(1))[0]
        if tipo == 2: return struct.unpack('>h', f.read(2))[0]
        if tipo == 3: return struct.unpack('>i', f.read(4))[0]
        if tipo == 4: return struct.unpack('>q', f.read(8))[0]
        if tipo == 5: return struct.unpack('>f', f.read(4))[0]
        if tipo == 6: return struct.unpack('>d', f.read(8))[0]
        if tipo == 7: n = struct.unpack('>i', f.read(4))[0]; return f.read(n)
        if tipo == 8: n = struct.unpack('>H', f.read(2))[0]; return f.read(n).decode('utf-8', 'replace')
        if tipo == 9:
            t = f.read(1)[0]; n = struct.unpack('>i', f.read(4))[0]; return [leer(t) for _ in range(n)]
        if tipo == 10:
            d = {}
            while True:
                t = f.read(1)[0]
                if t == 0: return d
                n = struct.unpack('>H', f.read(2))[0]; k = f.read(n).decode(); d[k] = leer(t)
        if tipo == 11: n = struct.unpack('>i', f.read(4))[0]; return list(struct.unpack('>%di' % n, f.read(4 * n)))
        if tipo == 12: n = struct.unpack('>i', f.read(4))[0]; return list(struct.unpack('>%dq' % n, f.read(8 * n)))
        raise ValueError(f'tipo NBT {tipo}')
    t = f.read(1)[0]; n = struct.unpack('>H', f.read(2))[0]; f.read(n); return leer(t)

mundo = sys.argv[1] if len(sys.argv) > 1 else sys.exit(__doc__); fallos = 0

def regiones(mundo):
    for dim, rel in (('overworld', 'region'), ('nether', 'DIM-1/region'), ('end', 'DIM1/region')):
        d = os.path.join(mundo, rel)
        if os.path.isdir(d): yield dim, d
    base = os.path.join(mundo, 'dimensions')
    if os.path.isdir(base):
        for ns in os.listdir(base):
            for n in os.listdir(os.path.join(base, ns)):
                d = os.path.join(base, ns, n, 'region')
                if os.path.isdir(d): yield f'{ns}:{n}', d

def main():
    mundo = sys.argv[1]; fallos = []; total = collections.Counter(); estados = collections.defaultdict(collections.Counter)
    versiones = collections.Counter()
    for dim, d in regiones(mundo):
        for f in sorted(os.listdir(d)):
            if not f.endswith('.mca'): continue
            ruta = os.path.join(d, f)
            try: rx, rz = map(int, f.split('.')[1:3])
            except ValueError: fallos.append(f'{ruta}: nombre raro'); continue
            b = open(ruta, 'rb').read()
            if len(b) == 0: continue
            if len(b) < 8192: fallos.append(f'{ruta}: cabecera corta ({len(b)} B)'); continue
            for i in range(1024):
                off = struct.unpack('>I', b'\0' + b[i*4:i*4+3])[0]; n = b[i*4+3]
                if off == 0: continue
                p = off * 4096
                if p + 5 > len(b): fallos.append(f'{ruta} #{i}: sector fuera del archivo'); continue
                ln, comp = struct.unpack('>IB', b[p:p+5])
                cx, cz = rx * 32 + i % 32, rz * 32 + i // 32
                try:
                    if comp & 128:   # datos externos (.mcc)
                        raw = open(os.path.join(d, f'c.{cx}.{cz}.mcc'), 'rb').read(); comp &= 127
                    else:
                        raw = b[p+5:p+4+ln]
                    data = zlib.decompress(raw) if comp == 2 else gzip.decompress(raw) if comp == 1 else raw if comp == 3 else None
                    if data is None: raise ValueError(f'compresión {comp}')
                    if data[0] != 10: raise ValueError('no empieza por compuesto')
                    f2 = io.BytesIO(data); f2.read(1); nl = struct.unpack('>H', f2.read(2))[0]; f2.read(nl)
                    raiz = nbt(data)
                except Exception as e:
                    fallos.append(f'{dim} chunk ({cx},{cz}) en {f}: ilegible: {e}'); continue
                if not isinstance(raiz, dict): fallos.append(f'{dim} chunk ({cx},{cz}): raíz no es compuesto'); continue
                if raiz.get('xPos') != cx or raiz.get('zPos') != cz:
                    fallos.append(f'{dim} chunk ({cx},{cz}): xPos/zPos = {raiz.get("xPos")},{raiz.get("zPos")} (descolocado)')
                estados[dim][raiz.get('Status', '?')] += 1; versiones[raiz.get('DataVersion')] += 1; total[dim] += 1
    for dim in total:
        print(f'{dim}: {total[dim]} chunks; estados: ' + ', '.join(f'{k}={v}' for k, v in estados[dim].most_common()))
    print('DataVersion:', dict(versiones))
    print(f'RESULTADO: {len(fallos)} FALLOS' + ('' if not fallos else ':'))
    for x in fallos[:40]: print('  ' + x)
    if '--json' in sys.argv:
        json.dump({'total': total, 'estados': {k: dict(v) for k, v in estados.items()}, 'fallos': fallos}, open(sys.argv[sys.argv.index('--json') + 1], 'w'))
    sys.exit(1 if fallos else 0)

main()
