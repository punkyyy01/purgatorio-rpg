# PURG4TORY: Souls Grimore 0.7.0 Beta 2

## 0.7.0 Beta 2 (2026-10-28) — fin de las congelaciones del mundo al explorar
- **PURG4TORY Cauces 0.4.1 → 0.5.0.** La corrección de la Beta 1.1 solo cubría las cadenas de lava del terreno nuevo; el
  mundo seguía congelándose al explorar rápido. Causa de fondo: el servidor se quedaba esperando a que se generase un
  chunk por una simple colisión, un escaneo de bloques o una comprobación de spawn. Con 0.5.0 nunca espera: en el borde de
  lo generado notarás un tope de unos segundos mientras aparece el terreno, pero el mundo sigue funcionando (drops, daño,
  criaturas). Medido en vuelo de 15 min a distancia 32: Beta 1.1 tuvo 48 pausas de 2 s o más (máx. 79 s); 0.7.0 Beta 2, ninguna.
- Cauces pasa a descargarse como proyecto de CurseForge (antes iba dentro del zip). Opciones nuevas en
  `config/purg4tory_cauces.properties` (todas activadas; `false` = Minecraft).
- Nombre de versión unificado: CurseForge, archivo, menú del juego y libro de bienvenida dicen «0.7.0 Beta 2».
- El resto del pack no cambia respecto a la versión publicada «0.7.0-beta.1» (= 0.6.0 Beta 1.1).

## English
- **PURG4TORY Cauces 0.4.1 → 0.5.0: world freezes while exploring are fixed.** The server no longer blocks waiting for chunk
  generation (collision checks, block scans, spawn checks). At the edge of generated terrain you may hit a few-seconds stop
  while terrain appears, but the world keeps running. Measured (15 min flight, view distance 32): Beta 1.1 had 48 stalls of
  2 s or more (max 79 s); 0.7.0 Beta 2 had none.
- Cauces is now downloaded as a CurseForge project dependency instead of being bundled in the zip.
- Unified version name across CurseForge, file, title screen and welcome book: "0.7.0 Beta 2".
- Everything else is unchanged from the published "0.7.0-beta.1" (= 0.6.0 Beta 1.1).
