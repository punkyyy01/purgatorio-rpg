# PURG4TORY: Souls Grimore 0.7.0-alfa.1 (experimental, no publicada)

## Añadido
- **PURG4TORY Cauces 0.1.0** (mod propio, solo servidor; va en `overrides/mods/`): prepara de antemano los ríos de
  Streams Reflowing en los ratos sin jugadores (3072 bloques alrededor del punto de aparición) y por delante de cada
  jugador. Explorando a pie, el terreno a 64 bloques por delante está listo el 97 % del tiempo (47 % sin el mod) con
  un 69 % menos de CPU. Comandos `/cauces estado|planificar <radio>|pausa|reanudar` (operadores).

## Sin cambios
- Streams Reflowing 2.15.2 con la misma configuración que 0.6.0-alfa.1 (LOW, cuencas de 768, sin rebioma).

## Avisos
- Requiere mundo nuevo (igual que 0.6.0).
- El mod no figura en `bloqueo.json` ni en CurseForge: la app de CurseForge puede avisar de «archivos externos».
- No usar `save-all flush` en copias de seguridad mientras se pruebe esta versión (ver `hito-0.7.0/INFORME-ALFA7.md` §6).
