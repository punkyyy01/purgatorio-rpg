# PURG4TORY Cauces 0.5.0

## Español

**Corrige las congelaciones del mundo al explorar (un jugador y servidor).** El hilo principal del servidor ya no se
queda esperando a que se genere un chunk:

- Las consultas «solo si está cargado» (colisiones, IA, mods) responden al momento si el chunk aún se está generando.
- «¿Está cargado?» en el hilo principal significa «está generado».
- El jugador y su vehículo no entran en un chunk hasta que sus 3×3 chunks están generados (en el borde de lo generado se
  nota un tope de unos segundos).
- Las cadenas de bloques (redstone, agua, lava) que llegan a terreno que aún se está generando se aplazan y se reanudan
  solas. Hacia chunks descargados de verdad se comportan como en Minecraft.
- Las comprobaciones de aparición de criaturas sobre terreno sin generar fallan en vez de esperar.
- Incluye las correcciones de 0.4.1, que no llegó a publicarse: las cadenas lava→obsidiana del terreno recién generado ya
  no generan chunks de forma síncrona; el vigía funciona en todos los mundos de una sesión (antes solo en el primero) y
  vuelca los hilos si el servidor se para; el planificador se reinicia bien al cambiar de mundo.
- Opciones nuevas (todas activadas por defecto; `false` = Minecraft): `consultasSinEsperar`, `cargadoEsListo`,
  `movimientoAListo`, `cadenasGlobales`, `spawnsSinEsperar`. No hace falta tocar la configuración al actualizar.
- Al parar el servidor, el registro muestra una línea `al parar: …` con los contadores de cada parte.

Medido (15 min de vuelo a distancia 32, mismo mundo): 0.4.0 tuvo 40 pausas de 2 s o más (máx. 172 s); 0.5.0, ninguna.

## English

**Fixes world freezes while exploring (single-player and servers).** The server main thread no longer blocks waiting
for chunk generation:

- "Only if loaded" chunk lookups (collisions, AI, mods) return immediately while a chunk is still generating.
- "Is it loaded?" on the main thread now means "is it generated".
- Players and their vehicles don't enter a chunk until its 3×3 area is generated (a few-seconds stop at the edge).
- Block-update chains (redstone, water, lava) reaching terrain still being generated are deferred and resume by
  themselves; towards truly unloaded chunks they behave as in vanilla.
- Mob spawn checks on ungenerated terrain fail instead of waiting.
- Includes the unreleased 0.4.1 fixes: lava→obsidian chains in freshly generated terrain no longer generate chunks
  synchronously; the watchdog works in every world of a session (it used to only work in the first one) and dumps threads
  on a stall; the planner resets properly when switching worlds.
- New options (all on by default; `false` = vanilla): `consultasSinEsperar`, `cargadoEsListo`, `movimientoAListo`,
  `cadenasGlobales`, `spawnsSinEsperar`. No config changes needed when updating.
- On server stop, the log prints an `al parar: …` line with per-feature counters.

Measured (15 min flight at view distance 32, same world): 0.4.0 had 40 stalls of 2 s or more (max 172 s); 0.5.0 had none.
