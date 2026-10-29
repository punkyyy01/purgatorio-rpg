#!/usr/bin/env python3
"""Comprobación estructural de un mundo (restaurado o vivo) SIN arrancar Minecraft. Solo lectura.

Uso: python3 verificar_mundo.py <dir_mundo>
Comprueba: level.dat legible (nombre, versión, semilla, hora), playerdata/*.dat legibles (posición, dimensión, nº de objetos del inventario),
y para cada dimensión (region/, DIM-1/region, DIM1/region, dimensions/*/*/region) que cada archivo .mca tenga cabecera coherente y
chunks leíbles (descomprime una muestra y comprueba la etiqueta NBT). Lo que NO sustituye: arrancar el servidor restaurado y mirar
vuestras construcciones (ver SERVIDOR.md, «Restaurar»)."""
import gzip, io, os, struct, sys, zlib

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
def mal(msg):
    global fallos; fallos += 1; print('  FALLO:', msg)
try:
    ld = nbt(gzip.decompress(open(os.path.join(mundo, 'level.dat'), 'rb').read()))['Data']
    print(f"level.dat: «{ld.get('LevelName')}», versión {ld.get('Version', {}).get('Name')}, hora {ld.get('DayTime')}, aparición {ld.get('SpawnX')},{ld.get('SpawnY')},{ld.get('SpawnZ')}")
except Exception as e: mal(f'level.dat ilegible: {e}')
pd = os.path.join(mundo, 'playerdata')
for f in sorted(os.listdir(pd)) if os.path.isdir(pd) else []:
    if not f.endswith('.dat'): continue
    try:
        d = nbt(gzip.decompress(open(os.path.join(pd, f), 'rb').read()))
        print(f"  jugador {f[:8]}…: dimensión {d.get('Dimension')}, pos {[round(x) for x in d.get('Pos', [])]}, {len(d.get('Inventory', []))} pilas de objetos, vida {d.get('Health')}")
    except Exception as e: mal(f'{f}: {e}')
dims = {'Overworld': 'region', 'Nether': 'DIM-1/region', 'End': 'DIM1/region'}
dd = os.path.join(mundo, 'dimensions')
if os.path.isdir(dd):
    for ns in os.listdir(dd):
        for nm in os.listdir(os.path.join(dd, ns)): dims[f'{ns}:{nm}'] = f'dimensions/{ns}/{nm}/region'
for nombre, rel in dims.items():
    p = os.path.join(mundo, rel)
    if not os.path.isdir(p): print(f'  {nombre}: sin región (no visitada)'); continue
    mcas = [x for x in os.listdir(p) if x.endswith('.mca')]; chunks = 0; leidos = 0; vacias = 0; sin_relleno = 0
    for x in mcas:
        b = open(os.path.join(p, x), 'rb').read()
        if len(b) == 0: vacias += 1; continue          # Minecraft crea regiones vacías (0 bytes) al explorar: normal
        if len(b) < 8192: mal(f'{rel}/{x}: tamaño {len(b)} menor que la cabecera'); continue
        if len(b) % 4096: sin_relleno += 1             # copia de un servidor en marcha: el último sector puede no estar rellenado; Minecraft lo lee igual
        entradas = [struct.unpack('>I', b'\0' + b[i * 4:i * 4 + 3])[0] for i in range(1024) if b[i * 4:i * 4 + 4] != b'\0\0\0\0']
        chunks += len(entradas)
        for off in entradas[:8]:
            try:
                n = struct.unpack('>I', b[off * 4096:off * 4096 + 4])[0]; c = b[off * 4096 + 4]
                datos = zlib.decompress(b[off * 4096 + 5:off * 4096 + 4 + n]) if c == 2 else gzip.decompress(b[off * 4096 + 5:off * 4096 + 4 + n]) if c == 1 else None
                if datos is not None: nbt(datos); leidos += 1
            except Exception as e: mal(f'{rel}/{x}: chunk ilegible ({e})')
    print(f'  {nombre}: {len(mcas)} regiones ({vacias} vacías, {sin_relleno} sin relleno final: aviso, no fallo), {chunks} chunks, {leidos} muestras leídas')
print('RESULTADO:', 'CORRECTO' if not fallos else f'{fallos} FALLOS'); sys.exit(1 if fallos else 0)
