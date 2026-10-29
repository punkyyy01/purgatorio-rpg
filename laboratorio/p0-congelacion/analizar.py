#!/usr/bin/env python3
"""Resumen de un directorio diagtick: pausas por causa (marco más informativo de la pila dominante) y esperas síncronas."""
import re, sys, collections, os

d = sys.argv[1]
txt = open(os.path.join(d, 'pausas.log'), encoding='utf-8', errors='replace').read()
bloques = re.split(r'\n(?=\d\d:\d\d:\d\d\.\d{3} PAUSA)', txt)
INTERES = ['getChunkBlocking', 'postProcessGeneration', 'CollectingNeighborUpdater', 'awaitStructurePlates',
           'saveAllChunks', 'teleport', 'tickChunks', 'tickEntities', 'NaturalSpawner', 'runPostLoad',
           'processUnloads', 'DistanceManager', 'ChunkMap.tick', 'ServerGamePacketListenerImpl', 'streamsreflowing',
           'purg4tory', 'Commands', 'BlockEntity', 'IOWorker', 'RegionFile', 'saveChunk']
pausas = []
for b in bloques:
    m = re.search(r'(\d\d:\d\d:\d\d\.\d{3}) PAUSA ([\d.]+) s', b)
    if not m: continue
    dur = float(m.group(2))
    pila = re.search(r'pila \((\d+)%\):((?:\n      .*)+)', b)
    marcos = [l.strip() for l in pila.group(2).split('\n') if l.strip()] if pila else []
    causa = '?'
    for k in INTERES:
        if any(k in f for f in marcos): causa = k; break
    # marco mod/vanilla más alto que no sea de espera genérica
    alto = next((f for f in marcos if not re.search(r'LockSupport|Unsafe|Thread\.(sleep|yield)|managedBlock|waitForTasks|BlockableEventLoop|ForkJoin|CompletableFuture|Object\.wait|parkNanos|pollTask|MinecraftServer\.(waitUntil|haveTime)', f)), '?')
    pausas.append((m.group(1), dur, causa, alto[:150]))

print(f'pausas >=0.5 s: {len(pausas)}  suma {sum(p[1] for p in pausas):.1f} s  máx {max([p[1] for p in pausas], default=0):.2f} s')
por = collections.defaultdict(lambda: [0, 0.0, 0.0])
for _, dur, c, _ in pausas:
    x = por[c]; x[0] += 1; x[1] += dur; x[2] = max(x[2], dur)
for c, (n, s, mx) in sorted(por.items(), key=lambda e: -e[1][1]):
    print(f'  {c:30s} n={n:4d} suma={s:7.1f} s máx={mx:6.2f} s')
print('pausas >= 2 s:')
for t, dur, c, alto in pausas:
    if dur >= 2: print(f'  {t} {dur:6.2f} s  {c}  | {alto}')

e = os.path.join(d, 'esperas.log')
GEN = r'Level\.getChunk|getBlockState|LevelReader|getChunkAt|BlockGetter|getFluidState\(Level|ChunkSource\.getChunk|CollisionGetter\.getChunk'
def llamador(fr, n=4):
    fr = [f for f in fr if not re.search(GEN, f)]
    return ' <- '.join(re.sub(r'\(.*', '', f).split('.')[-2] + '.' + re.sub(r'\(.*', '', f).split('.')[-1] for f in fr[:n])
if os.path.exists(e):
    t = open(e, encoding='utf-8', errors='replace').read()
    es = []
    for b in re.split(r'\n(?=\d\d:\d\d:\d\d\.\d{3} ESPERA)', t):
        m = re.search(r'(\d\d:\d\d:\d\d\.\d{3}) ESPERA (\d+) ms chunk \((-?\d+),(-?\d+)\) \S+ (\S+) carga=(\S+) .*?dist_jugador=(\d+)', b)
        if not m: continue
        fr = [l.strip().replace('TRANSFORMER/minecraft@1.21.1/', '') for l in b.split('\n')[1:] if l.strip()]
        es.append((m.group(1), int(m.group(2)), m.group(5), m.group(6), int(m.group(7)), llamador(fr)))
    print(f'esperas síncronas >50 ms: {len(es)}  suma {sum(x[1] for x in es)/1000:.1f} s')
    c = collections.Counter(); sm = collections.Counter(); cg = collections.defaultdict(set)
    for x in es: c[x[5]] += 1; sm[x[5]] += x[1]; cg[x[5]].add(x[3])
    for k, n in sorted(c.items(), key=lambda kv: -sm[kv[0]])[:14]: print(f'  n={n:4d} {sm[k]/1000:7.1f} s carga={",".join(sorted(cg[k]))}  {k}')
    print('esperas >= 2 s:')
    for x in es:
        if x[1] >= 2000: print(f'  {x[0]} {x[1]/1000:6.1f} s {x[2]} carga={x[3]} dist={x[4]}  {x[5]}')
