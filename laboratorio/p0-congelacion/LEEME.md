# Laboratorio P0: congelación de ticks del servidor integrado (SOLO PRUEBAS, no distribuir)

Herramientas usadas en `docs/auditoria-p0/INFORME-P0-CONGELACION-TICKS.md`. Rutas pensadas para el servidor de
pruebas (`~/dev/lab-p0`): cliente NeoForge en Xvfb (`cli/`), servidor dedicado de bordes (`srv/`), plantilla de mundo
`plantillas/p0` (misma semilla en todas las pruebas).

| Archivo | Para qué |
|---|---|
| `diagtick/` | Mod de diagnóstico (cliente y servidor). Vigía de ticks: si el hilo principal pasa >250 ms sin terminar un tick, muestrea su pila cada 10 ms y vuelca todos los hilos con locks y detección de interbloqueos (a los 3 s y cada 20 s). Mide cada `getChunk` del hilo principal (`@WrapMethod`) y registra las >50 ms con su origen. Posición del jugador en servidor y cliente. Órdenes de laboratorio en `<juego>/diagtick-comandos.txt`: `!vuelo_cliente <s> [giro°/min] [rumbo]` (W + esprint reales en el cliente, altitud 330), `!vuelo …` (vuelo programado desde el servidor), `!parar_vuelo`, `!salir` (= «Guardar y salir»). |
| `sp_vuelo.sh` | Una prueba: mundo nuevo desde la plantilla (o `REUSAR=<mundo>`), distancia 32, creativo, vuelo (`VUELO=cliente\|servidor\|tp`, `GIRO`, `YAW`), JFR continuo, comprobación de vida, salida limpia y resumen. |
| `bateria050.sh` | Batería larga del informe (0.4.1, bordes, teletransportes, estrés 45 min con giro, reapertura). |
| `bordes050.sh` | Regresión funcional en servidor dedicado: cadenas de lava de jugador y de terreno nuevo hacia chunks descargados, pistón pegajoso, granja con observador, agua, redstone, `save-all flush`, parada y reapertura. Necesita el mod `purg4tory_diagp0` de la auditoría anterior. |
| `analizar.py <dir diagtick>` | Pausas por causa y esperas síncronas agrupadas por llamador. |
| `integridad.py <mundo>` | Lee TODOS los chunks de todas las regiones: cabecera, descompresión, NBT, `xPos/zPos` coherentes, estados. |
| `doble.py` | Doble pulsación de espacio por XTest (versiones antiguas; el vuelo actual no lo necesita). |

Trampas: el vuelo por XTest no mueve al jugador en Xvfb; un script bash editado mientras corre se rompe (por eso las
baterías copian `sp_vuelo.sh` antes de cada prueba); cerrar el cliente con SIGTERM no garantiza un guardado limpio (usar
`!salir`); volar por debajo de y=320 choca con montañas de Tectonic.
