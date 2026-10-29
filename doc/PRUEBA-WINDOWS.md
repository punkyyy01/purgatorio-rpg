# {{NOMBRE}} {{VERSION_VISIBLE}} — prueba en Windows de la corrección de congelación

Objetivo: confirmar en un PC real que el mundo ya no se congela al explorar (P0 de Beta 1).

1. Importa `PURG4TORY-Souls-Grimore-{{VERSION}}.zip` en CurseForge como **perfil nuevo** (no sobrescribas el de Beta 1).
   Comprueba en `mods\` que está `purg4tory_cauces-0.4.1.jar`.
2. Mundo nuevo, creativo, distancia de renderizado 32. Explora deprisa en línea recta 10–15 minutos, mejor también bajo tierra
   o cerca de lagos de lava. Rompe bloques y golpea criaturas de vez en cuando para ver que el mundo responde.
3. Al terminar, en la carpeta de la instancia (`logs\latest.log`):
   - `cadena de bloques de terreno nuevo detenida en el borde de lo cargado` → la corrección actuó;
   - `VIGÍA:` y `Can't keep up!` → pausas del servidor (anota su duración).
4. Si vuelve a congelarse: **no salgas**, espera 30 s. Cauces guarda `purg4tory-congelacion-<fecha>.txt` en la carpeta de la
   instancia. Envía ese archivo, `logs\latest.log` y `logs\debug.log`.
5. Para comparar con el comportamiento de Minecraft: `config\purg4tory_cauces.properties` → `cadenaSinCargar=false`.
