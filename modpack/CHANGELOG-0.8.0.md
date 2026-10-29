# PURG4TORY: Souls Grimore 0.8.0-alfa.1 (experimental, NO publicable)

## Corregido
- **El servidor podía quedarse colgado al guardar** (`save-all flush` o al detenerse) después de explorar terreno nuevo
  deprisa. Era un bucle de Minecraft 1.21.1 que Streams Reflowing hace mucho más probable. PURG4TORY Cauces 0.2.0 lo
  evita: el guardado espera como mucho 30 s a los chunks que aún se están generando y sigue.

## Cambiado
- **PURG4TORY Cauces 0.2.0** (sustituye a 0.1.0):
  - ningún fallo del mod puede llegar a detener el servidor;
  - con varios jugadores, anticipa para el que antes llegará a terreno sin preparar (antes, siempre el primero);
  - mira más lejos según la velocidad de cada jugador y también a los lados del camino;
  - **vigía**: si el servidor se queda sin avanzar 20 s, deja en el registro qué estaba haciendo;
  - comando nuevo `/cauces colas`; opciones nuevas `planificar`, `horizonteS`, `vigiaS`, `esperaGuardadoS`.

## Sin cambios
- Streams Reflowing 2.15.2: LOW, cuencas de 768 (pendiente de vuestra decisión entre 512 y 768), sin rebioma.

## Avisos
- Requiere mundo nuevo.
- Riesgos abiertos en `hito-0.8.0/INFORME-ALFA8.md` §7 (congelones al teletransportarse a terreno sin preparar; cliente
  gráfico sin validar).
