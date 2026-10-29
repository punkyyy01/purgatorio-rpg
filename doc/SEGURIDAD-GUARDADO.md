# Seguridad del guardado y de la parada ({{NOMBRE}} {{VERSION_VISIBLE}})

Revisión técnica de seguridad (no una investigación abierta). Alcance: ¿puede perderse o corromperse un mundo por el guardado o la parada?

## 1. Qué pasaba (causa demostrada en Alpha 9, confirmada en esta revisión)
En Minecraft 1.21.1 el guardado completo (`save-all flush`) y la parada vacían la cola de descargas de chunks con `ChunkMap.processUnloads`. Un chunk **retenido por una tarea de generación** (contador de referencias > 0) cuyo guardado ya terminó **se vuelve a encolar al instante, sin fin**, dentro de una sola llamada. Las tareas que lo retienen solo avanzan si el hilo principal atiende su trabajo pendiente, y ese hilo está atrapado en el bucle. Resultado: `save-all flush` o `stop` no terminan (bucle vanilla, muy agravado por Streams Reflowing, que retiene pasos de generación mientras espera cuencas de ríos). Además, en `stop` este bucle ocurre **antes** del guardado final: si se mata el proceso, no hay guardado final.

## 2. Qué hace ahora PURG4TORY Cauces 0.4.0 (mixin sobre `ChunkMap`; no toca Streams Reflowing)

*Beta 1.1 lleva Cauces 0.4.1: esta parte del código no cambia (la salvaguarda del guardado es idéntica); el guardado y la parada se volvieron a comprobar (flush 1 s, parada 2 s, reapertura con los mismos bloques).*
| Situación | Comportamiento |
|---|---|
| `save-all flush` | Los chunks retenidos se **apartan** en vez de reencolarse; el hilo principal atiende trabajo pendiente hasta `esperaGuardadoS` (30 s); los que quedan libres se descargan y **guardan**; los que no, vuelven a la cola normal y se guardan cuando se descarguen. Lo informa en el registro (`guardado completo: N chunks retenidos…`). |
| Funcionamiento normal | Las descargas retenidas se **difieren y reintentan una vez por tick** en lugar de girar en bucle (antes: hasta ≈95 % del hilo principal en `processUnloads` con generación pesada). |
| `stop` | El bucle de parada espera como máximo `esperaParadaS` (60 s) a las generaciones en curso; después continúa con el **guardado final**. Los chunks a medio generar no se guardan y se regeneran (terreno determinista por semilla). |
| Teletransportes | Aplazados con tickets de 60 s (ver `TeletransportePrevio`): no bloquean el hilo principal; se cancelan a los 90 s con mensaje; si el jugador se desconecta o muere se descartan; al parar el servidor se vacía la lista. |

## 3. Evidencia
| Prueba | Resultado |
|---|---|
| Alpha 9 E4 (exp1 + chunks retenidos, 3 modos) | 12/12 marcadores presentes tras reabrir; 0 errores de lectura; `save-all flush` con un chunk retenido para siempre tarda 30 s (acotado) y lo informa; no declara éxito en falso. |
| Alpha 9 E5 (parada con un chunk retenido **para siempre**): exp1 y exp2 | **Se cuelga >200 s** (cierre forzado). exp2 (solo limitar entre iteraciones) no corrige: el bucle está dentro de una única llamada. |
| **Beta 1, E5 repetida con el código de el jar final de Cauces 0.4.0 (código de exp3 + limpieza + límite de botín)** — esta revisión | **`stop` terminó en 62 s** (60 s de espera acotada + cierre); registro: `parada: aún hay chunks en generación tras 60 s; se continúa con el guardado final`. Marcadores guardados antes del flush **4/4**; marcadores colocados **después** del flush (solo pueden persistir por el guardado final) **4/4**; **0 errores de lectura** al reabrir. Duración total de la prueba: 242 s (el mismo resultado con el jar exp3 en una primera ejecución: parada en 62 s, 4/4, 4/4). |
| Batería de aceptación Beta 1 | Ver `PRUEBAS-BETA1.md` (parada con `parar.py`, reinicio, persistencia, respaldo y restauración). |

## 4. Respuestas a las preguntas de la revisión
- **¿Puede ocurrir en juego normal o solo con retención artificial?** El bucle exige una generación que no termina nunca. En juego normal las cuencas de Streams se calculan en segundos y la retención se libera; el fallo se reproduce con retención permanente (artificial) o con cargas de generación extremas. Con la configuración vanilla+Streams sin Cauces, la parada **sí** se retrasaba bajo generación pesada; con Cauces esa espera está acotada.
- **¿Qué implica `save-all flush` con operaciones pendientes?** Guarda todos los chunks cargados y modificados (primera parte, sin cambios), y luego resuelve los retenidos como arriba. Los chunks ya **descargados** de la vista y aún **retenidos** por una generación son los únicos que pueden quedar sin guardar tras el límite de 30 s; Cauces lo escribe como `WARN` (`quedan para los ticks siguientes`).
- **¿Puede anunciar «Saved the game» sin persistirlo todo?** Sí, en un único caso acotado: chunks retenidos por una generación que dura más de 30 s *y* con cambios *y* ya descargados. Es un caso estrecho (no demostrado en ninguna prueba) y siempre queda constancia en el registro. `parar.py` y `respaldo.py` lo tienen en cuenta: leen la confirmación de `save-all flush` y no fuerzan nada si no llega.
- **¿Se puede quedar bloqueado indefinidamente?** Ya no por este bucle: `stop` está acotado a 60 s + guardado final, y `save-all flush` a 30 s. Sigue siendo posible un bloqueo por otras causas (disco lleno, otro mod); por eso hay un vigía de diagnóstico (`VIGÍA` en el registro tras 20 s sin tick) y un procedimiento de recuperación (`SERVIDOR.md`).
- **¿Hay alternativas más seguras con APIs soportadas?** No hay API de NeoForge para acotar la descarga de chunks en la parada; la causa está en código de Minecraft. La opción menos invasiva es la actual (mixin local, 6 inyecciones, sin reflexión, sin tocar escritura de regiones ni NBT). Se descartaron: limitar `maxThreads`/concurrencia (no afecta al bucle), `exp2` (no corrige) y cualquier reescritura de `ChunkMap`.
- **¿Se modifica Streams Reflowing?** No (licencia «All Rights Reserved»). Cauces solo llama a métodos públicos y, si Streams no es la versión probada (2.15.2), el planificador se desactiva solo.

## 5. Riesgo residual (qué NO está garantizado)
1. Un proceso terminado a la fuerza (`kill -9`, corte de luz, OOM) pierde lo ocurrido desde el último guardado (automático cada 5 min o `save-all flush`). Es igual en vanilla.
2. En el caso estrecho de §4 (retención >30 s/60 s + cambios + chunk ya descargado) esos cambios pueden perderse. Mitigación: `save-all flush` con los jugadores desconectados antes de `stop` (lo hace `parar.py`) y respaldos.
3. No se ha hecho una prueba de resistencia larga (horas) ni con más de un jugador real simultáneo; ver `PRUEBAS-BETA1.md`.
4. El código de Cauces depende de métodos internos de Minecraft 1.21.1 (`ChunkMap`) y públicos pero no documentados de Streams 2.15.2: **no actualizar Streams, NeoForge ni Minecraft sin repetir `prueba_parada.sh`**.

## 6. Decisión
Opción **B** (riesgo acotado + medidas operativas) con la parada colgada **corregida y validada en el peor caso reproducible**. No es un riesgo reproducible de pérdida o corrupción sin mitigación, así que **no bloquea** una Beta pública, siempre que se publique con `PROBLEMAS-CONOCIDOS.md` y la guía de respaldos de `SERVIDOR.md`.
