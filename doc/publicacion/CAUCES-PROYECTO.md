# Datos para publicar PURG4TORY Cauces en CurseForge (proyecto de mod)

| Campo | Valor |
|---|---|
| Nombre | **PURG4TORY Cauces** |
| Resumen (una línea) | Mod de servidor/mundo único para NeoForge 1.21.1: prepara los ríos de Streams Reflowing antes de llegar, aplaza teletransportes a terreno sin generar y acota el guardado y la parada. |
| Licencia | **MIT** (archivo `LICENSE` en el repositorio del mod) |
| Versión de Minecraft / loader | 1.21.1 / NeoForge ≥ 21.1 |
| Archivo | `purg4tory_cauces-0.5.0.jar` · versión **0.5.0** · canal Beta · sha256 `83b00079…` (reproducible con `construir.sh`). En CurseForge solo está la 0.4.0; la 0.4.1 solo se distribuyó dentro del modpack. Datos completos: `modpack/mods-propios/purg4tory_cauces/publicacion/CURSEFORGE-0.5.0.md` |
| Dependencias | NeoForge, Minecraft 1.21.1. **Opcional:** Streams Reflowing 2.15.2 (sin él, solo actúa la salvaguarda de guardado, los teletransportes y el botín) |
| Categoría | Utilidad de servidor / Rendimiento |
| Código fuente | `modpack/mods-propios/purg4tory_cauces/` del repositorio https://github.com/punkyyy01/purg4tory-souls-grimore |

## Descripción (ES)
**PURG4TORY Cauces** hace tres cosas, todas desactivables en `config/purg4tory_cauces.properties`: (1) **cuencas de ríos**: pide con antelación a Streams Reflowing 2.15.2 las cuencas alrededor del punto de aparición y por delante de cada jugador, usando solo métodos públicos del mod (no lo modifica ni lo redistribuye); (2) **guardado y parada**: evita que `save-all flush` y `stop` se cuelguen cuando una generación de chunks queda retenida, con esperas acotadas (30 s y 60 s) y avisos en el registro; (3) **teletransportes** (`/tp` y mods que usan `ServerPlayer.teleportTo`) a terreno sin generar: se aplazan con tickets en lugar de congelar el hilo principal (medido: 166 s de bloqueo → ≤ 1 s). Además incluye un modificador global de botín que recorta, **solo en las tablas listadas en `config/purg4tory_botin.json`**, el equipo de alto nivel de algunos cofres de mazmorra (no copia ni modifica tablas de otros mods). Comandos (permiso 3): `/cauces estado|colas|pausa|reanudar|planificar <radio>`, `/cauces_tp`.
**Límites:** depende de métodos internos de Minecraft 1.21.1 y de Streams 2.15.2: no actualizar sin repetir pruebas. Funciona también en el servidor integrado de un jugador.

## Description (EN)
**PURG4TORY Cauces** does three things, each configurable: (1) pre-plans Streams Reflowing 2.15.2 river basins around spawn and ahead of each player via its public methods only (it neither modifies nor redistributes it); (2) keeps `save-all flush` and `stop` from hanging when a chunk generation stays retained (bounded 30 s / 60 s waits, logged); (3) defers player teleports to ungenerated terrain with chunk tickets instead of freezing the main thread (166 s freeze → ≤ 1 s measured). It also ships a global loot modifier that trims high-tier gear in the chests listed in `config/purg4tory_botin.json` only. Source: MIT.
