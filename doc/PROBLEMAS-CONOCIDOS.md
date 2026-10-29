# Problemas conocidos de {{NOMBRE}} {{VERSION_VISIBLE}}

Ordenados por importancia para quien juega o administra. «Medido» = visto en las pruebas de `PRUEBAS-BETA1.md`.

## Servidor y guardado
0. **Congelación del mundo al explorar (P0 de Beta 1): corregida en Beta 1.1** (Cauces 0.4.1, `PRUEBAS-BETA1.md` §Beta 1.1).
   Riesgos residuales: (a) si el servidor se para justo cuando una cadena de terreno nuevo está esperando a un chunk, esa
   reanudación se pierde y quedan unas pocas fuentes de lava bajo agua sin convertir (como hace Minecraft con las que nada
   actualiza; se convierten en cuanto un jugador las toca); (b) Streams Reflowing, sin C2ME, puede bloquear la generación hasta
   45 s por estructura mientras planifica sus ríos (no observado en las pruebas); (c) la causa se reprodujo en el laboratorio,
   **falta confirmarla en un PC con Windows**.
1. **Parada con una generación de chunks que no termina:** corregida en el peor caso reproducible (el servidor termina en ≈60 s y hace el guardado final; ver `SEGURIDAD-GUARDADO.md`). **Riesgo residual:** un `kill -9`, un corte de luz o un fallo de memoria pierden lo ocurrido desde el último guardado; en el caso estrecho de una generación retenida >30–60 s con cambios en un chunk ya descargado, esos cambios podrían perderse. Mitiga: `parar.py` para parar y `respaldo.py` a diario.
2. **Tirones al buscar estructuras (P1, medido):** `/locate`, los mapas de explorador de los cartógrafos y los ojos de ender buscan en el hilo principal. En terreno sin generar cada búsqueda lo bloquea **1–21 s**. Mitiga: pregenerar el entorno del spawn y no encadenar búsquedas. No se ha cambiado el comportamiento de los objetos.
3. **Primera entrada al End (P1, medido):** al llegar un jugador al End, End's Phantasm calcula la salida de las puertas del End y obliga a generar terreno lejano de forma síncrona: **un tirón de hasta ≈25 s una sola vez por mundo** (visto con el servidor compartiendo CPU con un cliente de software). Mitiga: que el administrador entre una vez al End antes que los jugadores (o pregenerar la dimensión). No se modificó End's Phantasm.
4. **Teletransportes:** Cauces aplaza `ServerPlayer.teleportTo` (`/tp`, la mayoría de mods) a terreno sin cargar. **No cubre** portales ni reaparición; esos destinos son terreno ya generado, pero un portal del Nether a terreno nuevo del Nether puede costar unos segundos (ver `PRUEBAS-BETA1.md`). Waystones no se ha verificado con terreno frío.
5. **Coste de generación:** el terreno nuevo cuesta ≈+40 % de CPU frente a la 0.8.0 (≈300 biomas más) y se notan «Can't keep up» al explorar deprisa (hasta ≈15 s de retraso acumulado en una sesión de pruebas con generación pesada y un cliente de software compartiendo CPU). Se recomienda pregenerar en servidores.
6. **Streams Reflowing, Minecraft y NeoForge no deben actualizarse** sin repetir las pruebas (Cauces depende de métodos internos).
7. **Cuatro mods requieren descarga manual en el servidor** (Alex's Mobs Continued, Hybrid API [HAPI], ServerCore, Structory): sus autores lo exigen. Sin ellos, el servidor no arranca o faltan criaturas/estructuras.

## Cliente
8. **Importación en CurseForge:** avisará de dos archivos externos (`reglas.mcfunction`, `crittersandcompanions-common.json5`). Son nuestros; seguros.
9. **Every Compat registra ≈16 600 bloques (57 % del total):** coste de arranque y de memoria **no medido** en un PC real; el propio mod lo avisa con dos `ERROR` en el registro (inofensivos). Cliente y servidor deben tener la misma versión.
10. **Variantes de las maderas de Promenade de Every Compat** (sakura, maple, palm, dark_amaranth) **no existen** en Beta 1 (sus texturas no se encuentran); Promenade conserva sus bloques. Un mundo de la candidata 0.9.0-alfa.2 perdería esos bloques (ver `COMPATIBILIDAD.md`).
11. **Registro del cliente con «ERROR» benignos:** ≈45 al abrir el título (cursor X11/GL del cliente de pruebas, «Invalid path in pack: …README», etc.); ninguno de módulos opcionales.
12. **FPS y rendimiento gráfico no medidos** (el cliente de pruebas es de software). El tiempo hasta el menú en el cliente de software fue ≈80 s.
13. Handcrafted lleva >18 meses sin actualizar (sigue funcionando en 1.21.1).

## Jugabilidad
14. **Balance:** solo se tocó el botín de 49 cofres. Armas, jefes, clases y magia están con los valores de cada mod: **balance no definitivo**. Cataclysm (≈1,3–1,4 objetos premium) y los jefes entregan sus recompensas propias.
15. **Combate y magia verificados con clics reales** en un cliente de software, **no** con una partida larga: no se probó el rendimiento de combates grandes ni la sensación de juego.
16. **Dos clientes de prueba no son un playtest multijugador real.** Falta el protocolo humano de `PRUEBAS-BETA1.md`.
17. Mecánica de **Alma**: no existe (pospuesta).
18. Mundos de Alphas anteriores: no soportados (`COMPATIBILIDAD.md`).

## Ruido conocido del registro del servidor (≈37 `ERROR` al arrancar, no ocultos a propósito)
- ≈34 `RuntimeDistCleaner`: clases de cliente que mixins de varios mods intentan cargar en servidor (inofensivo).
- 2 de Every Compat (aviso del número de bloques) y 1 de logros de When Dungeons Arise (`find_thornborn_towers`, `find_fishing_hut`).
- Durante la generación pueden aparecer algunos «entidad en posición inválida» (sin efecto visible comprobado).
