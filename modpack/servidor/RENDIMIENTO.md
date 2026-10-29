# PURG4TORY — ajustes recomendados de rendimiento (mediciones del laboratorio 0.5.0; vigentes en {{VERSION_VISIBLE}}, que añade ≈+40 % de coste de generación por la biodiversidad)

Todos los números de este documento salen del laboratorio 0.5.0 (servidor dedicado, 20 hilos, Java 21, un jugador, semilla
fija) salvo donde dice «estimación». El cliente de pruebas no tiene GPU: no hay datos de FPS.

## Servidor (server.properties y JVM)
| Ajuste | Recomendado | Por qué (medido) |
|---|---|---|
| view-distance | **12** (máx. 16) | Por jugador, ya generado: 10/6 → 9,0 ms/tick, 16/8 → 12,6, 32/10 → 17,2. A 32 el coste es la distancia de visión, no la simulación (32/6 → 15,5). |
| simulation-distance | **6** (8 si hay granjas grandes) | La simulación solo baja ~1,5 ms a 32 de visión; a 6 mobs y cultivos cerca del jugador siguen activos. |
| Memoria | **-Xms6G -Xmx6G**, G1 por defecto de Java 21, sin más opciones | Memoria viva con 1 jugador: 1,0 GB (visión 10) – 1,65 GB (visión 32). 6 GB da margen para 4–6 jugadores (estimación: +0,3–0,6 GB por jugador). Más heap no acelera nada. |
| Pregeneración | **Sí**, con borde (servidor/pregenerar.sh) | Generar terreno es el 85 % de la CPU del servidor al explorar; cargar chunks ya generados es barato. ~19 chunks/s: radio 3000 ≈ 2 h, radio 5000 ≈ 5,5 h (estimación por extrapolación). Hacerlo fuera de horas de juego: comparte máquina con producción. |
| fml.toml maxThreads=1 | Mantener | Evita una carrera de arranque (Architectury); solo cuesta ~3 s al iniciar. |

## Cliente (CurseForge)
- Memoria asignada: **6 GB** (el ZIP la recomienda). Con la carga de modelos bajo demanda de ModernFix, la memoria viva a distancia 12 es ~1,1 GB (antes 2,1 GB).
- Perfil **equilibrado**: distancia de renderizado 12, simulación 6, partículas «Todas» (Particular y Particle Rain incluidos).
- Perfil **alto**: renderizado 16–20 (en multijugador nunca verás más allá del view-distance del servidor).
- **32 chunks no debe ser el mínimo.** Cuesta en el servidor (+6–7 ms/tick por jugador) y en la GPU. Si se quieren vistas lejanas de verdad, la vía
  habitual es un mod de LOD (Distant Horizons): pendiente de evaluar en un PC con GPU.
- FancyMenu: la animación del menú se detiene sola a los 10 s de dejar de verse (comprobado en su código fuente); no gasta nada en partida.
