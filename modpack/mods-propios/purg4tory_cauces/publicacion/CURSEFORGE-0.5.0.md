# Publicar PURG4TORY Cauces 0.5.0 en CurseForge (proyecto 1763725) — NO publicado todavía

## Estado real de las versiones (2026-10-28)

| Versión | Dónde ha estado | Estado |
|---|---|---|
| 0.1.0, 0.2.0 (+ variante `-sinmixin`) | Alphas 7 y 8 del pack (jar en `overrides/mods`) | Obsoletas, solo internas |
| 0.3.0-exp1 / exp2 / exp3 | Laboratorio de rendimiento y Alpha 0.9.0 | Experimentales; exp3 se convirtió en 0.4.0 |
| **0.4.0** | **Proyecto Cauces en CurseForge** (único archivo, fileID 9311855, sha1 `c317c354…`, idéntico al jar local) | Lo que baja quien instala Cauces suelto; el modpack **no** lo usa |
| 0.4.1-dev1 / dev2 / dev3 | Laboratorio P0 (24-10) | Experimentales, descartadas o absorbidas |
| **0.4.1** (sha256 `915c7625…`) | **Dentro del modpack publicado** («0.7.0-beta.1», fileID 9325709) en `overrides/mods`; nunca como archivo del proyecto Cauces | **Lo que tienen los jugadores del modpack**; superada por 0.5.0 |
| 0.5.0-dev1 / dev2 / dev3 | Laboratorio P0 (28-10) | Experimentales, absorbidas |
| **0.5.0** (sha256 `83b00079…`) | `~/dev/lab-p0/publicar-cauces-0.5.0/` | **Lista para publicar** tras tu revisión |

0.5.0 contiene todo lo válido anterior: código de 0.4.1 completo (13 líneas ampliadas, ninguna corrección retirada) y 0.4.1
contiene todo 0.4.0 (que a su vez es exp3 + límite de botín + limpieza de teletransportes al parar).
**Recomendación: publicar 0.5.0 directamente y no publicar 0.4.1** (0.5.0 es 0.4.1 + la corrección de fondo).

## Ficha del archivo

| Campo | Valor |
|---|---|
| Archivo | `purg4tory_cauces-0.5.0.jar` (en `~/dev/lab-p0/publicar-cauces-0.5.0/`) |
| SHA-256 | `83b00079624a17785f24d311eb515bd62c2b82e76e06c40b513b94f7f5b6d8ff` (reproducible con `construir.sh`) |
| Nombre visible | PURG4TORY Cauces 0.5.0 |
| Tipo de publicación | **Beta** (sugerido: falta la prueba en Windows con GPU; 0.4.0 se subió como Release) |
| Versión de Minecraft | 1.21.1 (solo; `versionRange [1.21.1,1.21.2)`) |
| Loader | NeoForge (≥ 21.1; probado con 21.1.259) |
| Java | 21 |
| Entorno | **Cliente y servidor** (en un jugador actúa dentro del servidor integrado: tiene que estar en el cliente). En multijugador basta con el servidor; en los clientes no molesta |
| Relación con otros proyectos | Streams Reflowing: **dependencia opcional** (sin él no hay planificador de cuencas; el resto funciona) |
| Changelog | Texto de `CHANGELOG-0.5.0.md` (ES y EN) |

## Compatibilidad comprobada

- Pack PURG4TORY 0.6.0-beta.1 completo (155 mods), un jugador y servidor dedicado.
- Lithium 0.15.4 sobrescribe `ServerChunkCache.getChunk`: los mixins de Cauces que actúan ahí tienen prioridad 1500 para
  aplicarse después (comprobado en ejecución).
- Usa MixinExtras (`@WrapMethod`), que ya viene dentro de NeoForge 21.1 (0.5.5): no añade dependencias.
- Streams Reflowing 2.15.2 (se desactiva solo con otra versión salvo `permitirOtraVersionSR=true`).
- No probado con C2ME (no está en el pack) ni con otros mods que intercepten `getChunk` del hilo principal.

## Descripción del proyecto: párrafo nuevo a añadir

ES: **Desde 0.5.0, el mundo no se congela al explorar rápido.** En Minecraft 1.21.1, el hilo principal del servidor
(también el integrado de un jugador) puede quedarse esperando a que se genere un chunk por una simple colisión o una
cadena de lava; con distancia de visión alta eso son decenas de segundos sin ticks. Cauces hace que esas consultas no
esperen: el jugador no entra en terreno hasta que está generado (se nota un tope de segundos en el borde), las cadenas de
bloques se reanudan cuando el chunk está listo y los intentos de spawn sobre terreno sin generar fallan. Todo desactivable.

EN: **Since 0.5.0, the world no longer freezes while exploring fast.** In Minecraft 1.21.1 the server main thread (including
the single-player integrated server) can block waiting for a chunk to generate because of a simple collision check or a lava
chain; at high view distance that means tens of seconds without ticks. Cauces makes those lookups non-blocking: players don't
enter terrain until it is generated (a few-seconds stop at the edge), block-update chains resume once the chunk is ready, and
spawn attempts on ungenerated terrain fail. Everything is configurable.

## Después de publicar

1. Esperar la aprobación del archivo y anotar su `fileID`.
2. Modpack: ver `MODPACK-0.5.0.md`.
