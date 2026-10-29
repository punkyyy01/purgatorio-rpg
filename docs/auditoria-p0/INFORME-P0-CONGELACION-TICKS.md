# P0 · Auditoría de la congelación de ticks del servidor integrado (un jugador)

Fecha: 2026-10-28. Pack: PURG4TORY: Souls Grimore 0.6.0-beta.1 (Minecraft 1.21.1, NeoForge 21.1.259, 155 mods).
Corrección: **PURG4TORY Cauces 0.5.0** (`modpack/mods-propios/purg4tory_cauces/`). Laboratorio y herramientas: `laboratorio/p0-congelacion/`.
Estado: **causa raíz demostrada y corregida en laboratorio; validación en Windows con GPU pendiente** (ver §7).

## 1. Resumen

El mundo no se «cuelga» por un interbloqueo. El **hilo principal del servidor integrado se queda esperando de forma
síncrona a que se genere un chunk**. En Minecraft 1.21.1 esa generación pasa por **un buzón en serie por dimensión**
(`ChunkMap.worldgenMailbox`) y, con distancia 32, ese buzón tiene miles de chunks en cola sin prioridad. La espera dura lo que
tarde la cola en llegar al chunk pedido: de segundos a minutos (medido: 172 s, y a continuación «Guardar y salir» no
terminó en 240 s). Mientras tanto el cliente sigue pintando y moviéndose, pero el servidor no procesa nada: no hay drops,
daño, muertes ni chunks nuevos. Es exactamente el síntoma descrito.

Hay **dos familias de disparadores**, y ninguna depende de Cauces:

| Disparador | Ejemplos medidos (pila real) | Corregido en |
|---|---|---|
| A. Cadenas de actualizaciones de bloques que llegan a un chunk no listo | lava→obsidiana en `postProcessGeneration`; `FluidInteractionRegistry` (NeoForge) en `LiquidBlock.neighborChanged` | 0.4.1 (solo terreno nuevo) y 0.5.0 (todas, acotado) |
| B. Consultas alrededor del jugador cuando este va más rápido que la generación | colisiones de Lithium (`getChunk(..., false)`, «solo si está cargado», que **también espera**); `Entity.setPosRaw` (parche de NeoForge que carga el chunk); Tide (`FishingInfoManager`, radio 6); Galosphere (`hasChunksAt` + lectura); `isInWall`; spawners (In Control `SpawnerSystem`, `CatSpawner`) | **solo 0.5.0** |

**La 0.4.1 solo corrige la familia A**, y por eso el problema siguió reproduciéndose. Además, **la 0.4.1 nunca se
publicó**: CurseForge sirve Cauces 0.4.0, que es lo que tienen los cuatro equipos.

Streams Reflowing **no causa la espera, pero la alarga**. Cada chunk cuesta más y, sin C2ME, cada inicio de estructura
cuyas cuencas no estén listas bloquea el buzón de generación hasta 45 s (`ChunkStepDefer` → `awaitStructurePlates`).
Durante la congelación final de 0.4.0, solo 1 de los 17 hilos de generación trabajaba.

## 2. Resultados (A/B, mismas condiciones)

Cliente real en Xvfb (servidor integrado), mundo nuevo desde la misma plantilla (misma semilla), distancia 32, creativo,
**vuelo real del cliente** (W + esprint, a y=330, por encima de cualquier montaña) durante 15 min. Instrumentado con
`purg4tory_diagtick` (solo laboratorio) y JFR. «En partida» excluye los primeros 45 s de carga del mundo (ahí hay una
espera fija de ~9 s por el `forceload add 0 0` de la función de carga de Incendium y ~4,5 s de arranque).

| Cauces | Pausas ≥ 0,5 s | ≥ 2 s | ≥ 10 s | Suma | Máx. | Distancia volada | Guardar y salir |
|---|---|---|---|---|---|---|---|
| 0.4.0 (publicada) | 77 | 40 | 20 | 1153 s | **172 s** | 19,1 km y congelado | **no terminó en 240 s** |
| 0.4.1 (candidata, sin publicar) | 277 | 48 | 17 | 791 s | **79 s** | — | limpio |
| **0.5.0-dev1** | **0** | **0** | **0** | **0 s** | — | 12,6 km | limpio, 2 s |
| **0.5.0 (jar definitivo, sha256 83b00079…)** | **0** | **0** | **0** | **0 s** | — | 13,7 km | limpio, 1 s |

Con 0.5.0 la exploración rápida queda limitada a lo que da la generación: el jugador se frenó 1297 veces en el borde de
lo generado y voló 12,6 km en lugar de 19,1. **El mundo no se para; lo que se para es el avance del jugador en la
frontera**, y el terreno lo alcanza en segundos.

Las únicas pausas que aparecen fuera de la carga del mundo caen justo en «Guardar y salir»: el propio script hace
`JFR.dump` y `jstack -l` sobre el proceso en ese instante (artefacto de medición, ~0,6 s).

Otras pruebas:
- **Teletransportes** (41 `/tp` de 3000 bloques a terreno sin generar, 10 min; repetido con el jar definitivo): todos
  aplazados hasta tener el destino listo (13–42 s) y **0 pausas en partida**. Con dev2 quedaba una espera de 1,0 s de
  In Control (`SpawnerSystem` → `Mob.checkSpawnObstruction`); con el jar definitivo (M4) se cortaron 4 spawns y no hubo espera.
- **Regresión de bordes** (servidor dedicado, misma batería que la Beta 1.1, `bordes050.sh`; con dev2 y con el jar definitivo): cadena de lava de jugador
  hacia chunks descargados 128/128 (igual que Minecraft, 0 cortes); cadena de terreno nuevo cortada y reanudada hasta
  128/128 con 0 perdidas; pistón pegajoso, granja con observador, agua y redstone cruzando bordes: **pasan**;
  `save-all flush` 1 s, parada 2 s, reapertura con todo igual. 0 errores.
- **Estrés largo e integridad**: ver §6.

## 3. Mecanismo, paso a paso (con el código de 1.21.1)

1. Con distancia 32, el servidor integrado da nivel de ticket a 65×65 chunks: están «cargados» (`hasChunk` = sí) mucho antes
   de estar «listos» (generados y convertidos en `LevelChunk`).
2. `ServerChunkCache.getChunk(x, z, estado, cargar)` en el hilo principal llama a `getChunkFutureMainThread` y luego a
   `managedBlock(future::isDone)`. **Con `cargar=false` también espera** si el chunk tiene nivel de ticket, porque
   `scheduleChunkGenerationTask` devuelve el futuro en curso. Para el hilo principal no existe «si está cargado, dámelo,
   y si no, nada».
3. La generación de cada paso corre en `ChunkMap.runGenerationTask` → `worldgenMailbox`, **un buzón en serie** con prioridad por
   nivel de ticket. Todos los chunks visibles tienen el mismo nivel, así que el chunk pedido espera su turno en cola.
4. Streams Reflowing sin C2ME bloquea ese buzón hasta 45 s por inicio de estructura cuyas cuencas no están listas.
5. Resultado: una consulta trivial (una colisión, un escaneo de 6 bloques, una comprobación de spawn) bloquea el tick durante
   la cola entera. Con distancia 32 y exploración rápida, la cola no se vacía nunca.

No hay interbloqueo (`findDeadlockedThreads` = ninguno en todos los volcados).

## 4. La corrección (Cauces 0.5.0)

Regla de diseño: **el hilo principal no espera a la generación de chunks en el juego normal**. Cada parte tiene su
interruptor en `config/purg4tory_cauces.properties` (por defecto activadas) y su contador en el registro al parar.

| Parte | Clave | Qué hace | Efecto en el juego |
|---|---|---|---|
| M1 | `consultasSinEsperar` | `getChunk(..., cargar=false)` en el hilo principal responde `null` si el chunk aún no está listo en ese estado (es lo que promete el método) | Ninguno visible: «no cargado» durante los segundos que tarda en generarse |
| M1b | `cargadoEsListo` | `hasChunk`/`isLoaded`/`hasChunkAt` en el hilo principal = «está listo» | Ídem; evita el patrón «si está cargado, léelo» |
| M2 | `movimientoAListo` | El jugador (y su vehículo) no entra en un chunk hasta que sus 3×3 están listos; si no, vuelve a su posición, como hace el cliente con su propio chunk | En la frontera de lo generado se nota un tope que desaparece en segundos |
| M3 | `cadenasGlobales` | Una cadena de bloques (redstone, agua, lava) que llega a un chunk **ya en el área cargada pero aún generándose o leyéndose del disco** se aplaza y se reanuda al estar listo. Un chunk descargado de verdad se carga como en Minecraft | Retraso de segundos solo en ese borde. Lo aplazado vive en memoria (igual que 0.4.1) |
| M4 | `spawnsSinEsperar` | Las comprobaciones de spawn (`Mob.checkSpawnObstruction`, `checkSpawnRules`, `SpawnPlacements.*`) que tocan un chunk no listo fallan («ahí aún no hay terreno») | Ese intento de spawn no ocurre; se reintenta en ticks siguientes |
| (0.4.1) | `cadenaSinCargar` | Cadenas que empiezan al procesar terreno nuevo | Ya validado en Beta 1.1 |

Se mantiene todo lo de 0.4.x (planificador de cuencas, guardado/parada acotados, teletransportes aplazados, vigía, botín).

**Qué no es la solución:** no hay timeouts nuevos, no se esconde nada, no se reinicia nada y no se quitan funciones. Las
esperas que quedan son las que pide el propio jugador de forma explícita: `/forceload` (carga síncrona por diseño) y la
carga inicial del mundo.

Detalles técnicos:
- Los mixins de `getChunk` tienen prioridad 1500 porque Lithium sobrescribe `getChunk` (`@Overwrite`, `getChunkBlocking`).
  Con la prioridad por defecto se perderían.
- M4 usa `@WrapMethod` (MixinExtras, incluido en NeoForge). El corte es una excepción de control sin pila que se captura
  dentro del propio método envuelto, así que nunca atraviesa código de otros mods. Solo actúa en el hilo principal (los
  spawns de los hilos de generación no se tocan).
- El jar es reproducible (mismo SHA-256 en UTC y en America/Costa_Rica).

## 5. Qué se descartó y por qué

- **Subir prioridad del chunk pedido** (estilo Paper): acorta la espera, pero no la elimina. Un chunk con Streams cuesta
  0,5–3 s y puede caer en una espera de 45 s por estructura.
- **Devolver chunks vacíos a todas las lecturas**: perdería escrituras en el mundo y cambiaría la integridad.
- **Cadenas globales sin reanudación** (dev2 de 0.4.1): ya se había descartado (80/128 perdidas para siempre).
- **Cadenas globales también hacia chunks descargados de verdad**: misma regresión tras reiniciar. 0.5.0 lo acota (M3).
- **`-Dstreamsreflowing.structurewait=0`**: no cambiado sin necesidad. Con 0.5.0 la espera de Streams ya no congela el mundo,
  solo retrasa la aparición del terreno. Queda como opción documentada.

## 6. Estrés largo, reapertura e integridad

- **Estrés de 45 min** (dev2: M1–M3 + M2 de jugador), vuelo real en círculo con giro de 24°/min: tres vueltas de ~3 km
  de radio, que repasan zonas ya guardadas y descargadas (carga desde disco) además de generar terreno nuevo. **0 pausas en
  partida**, guardado limpio en 3 s. Cauces: 54 472 cargas síncronas evitadas en cadenas, 3829 reanudadas, **0 perdidas**,
  909 pendientes al salir y 4704 frenos en la frontera.
- **Reapertura** de ese mundo y 10 min más de vuelo cruzando lo ya visitado: el mundo abre, **0 pausas en partida** y
  guardado limpio. Las únicas pausas son de los 5 primeros segundos (Streams inicializa su motor y el hilo principal espera
  ese bloqueo una vez, 0,56 s; `isInWall` al entrar, 0,3 s) y forman parte de la carga del mundo.
- **Integridad** (`integridad.py`, lee todos los chunks: cabecera, descompresión, NBT completo, `xPos/zPos` coherentes):
  **0 fallos en 268 237 chunks** de 7 mundos (A/B 0.4.0, 0.4.1 y 0.5.0, teletransportes, estrés largo reabierto y
  confirmación final). Detalle en `resultados/integridad.txt`.
- **Cadenas pendientes al salir**: lo que estaba aplazado en ese momento (909 en 45 min) no se guarda. Ese contacto
  lava/agua del borde queda como lo dejaría Minecraft sin actualizar y se resuelve en cuanto algo lo actualiza (mismo
  comportamiento ya aceptado en 0.4.1). No es corrupción: el NBT de esos chunks es válido.

## 7. Pendiente y riesgos

- **Validar en Windows con GPU** (los cuatro equipos): el laboratorio usa render por software (llvmpipe, 15–20 FPS).
  Protocolo de 30 min por PC: `PRUEBA-WINDOWS.md` (con `capturar-congelacion.ps1`); el registro al salir
  muestra la línea `al parar: …` con todos los contadores.
- **Multijugador real** (servidor dedicado + varios clientes): las partes son las mismas, pero no se ha probado con jugadores reales.
- **Vehículos**: el freno de vehículos (M2) está aplicado y carga, pero no se ha estresado (un barco sobre hielo continuo no es
  reproducible en el laboratorio).
- **Portales** (Nether/End): el cambio de dimensión por portal no pasa por `teleportTo` y no se ha medido; la búsqueda de
  portal de Minecraft es síncrona por diseño.
- **Publicar**: Cauces 0.5.0 debe subirse al proyecto de CurseForge y el pack debe apuntar a ese archivo. Hasta entonces,
  los jugadores siguen con 0.4.0.

## 8. Cómo integrarlo en el pack (no hecho: requiere tu decisión)

1. Compilar (`modpack/mods-propios/purg4tory_cauces/construir.sh`) o usar el jar probado. Debe dar sha256
   `83b00079624a17785f24d311eb515bd62c2b82e76e06c40b513b94f7f5b6d8ff` (reproducible).
2. Subir **Cauces 0.5.0** al proyecto de CurseForge (1763725) y apuntar el pack a ese archivo (en la Beta 1, `cauces_cf` en
   `pack.toml`).
3. `config/purg4tory_cauces.properties` de overrides: no hace falta tocarlo (las claves nuevas valen `true` si faltan), pero
   conviene regenerarlo para que muestre las opciones nuevas documentadas.
4. Pedir a los cuatro equipos la misma partida (vuelo en creativo a distancia 32) y el registro al salir (línea `al parar: …`).

## 9. Archivos de esta entrega

- `modpack/mods-propios/purg4tory_cauces/`: fuente completa de Cauces 0.5.0 (MIT). Nuevos: `SinEsperas`, `SondeoSpawn`, `SondeoSpawnUtil`,
  mixins `ServerChunkCacheSinEsperaMixin`, `MovimientoListoMixin`, `SondeoSpawnMixin`, `SpawnPlacementsSondeoMixin`.
  Cambiados: `CadenaSinCargar`, `ServerChunkCacheCadenaMixin`, `Config`, `Cauces`, `mixins.json`, `neoforge.mods.toml`.
- `laboratorio/p0-congelacion/`: mod `diagtick` y scripts de prueba (ver su `LEEME.md`).
- `docs/auditoria-p0/resultados/`: resumen y análisis de cada prueba, batería de bordes e integridad.
- Antecedentes (fuera del repo, en el servidor de pruebas): auditoría de 2026-10-24 en `~/dev/lab-p0/entrega/` y
  `~/dev/purg4tory-beta1/prueba/p0/`; JFR y volcados completos de cada prueba en `~/dev/lab-p0/res2/<prueba>/`.
