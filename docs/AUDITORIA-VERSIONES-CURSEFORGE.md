# Auditoría de versiones: CurseForge frente a desarrollo (2026-10-28)

Fuente: CurseForge Core API (consultada el 28-10) y zips locales comparados por SHA-1. **Los 7 archivos del modpack y el
de Cauces coinciden byte a byte con archivos locales.** Además, la fuente actual del modpack (`~/dev/purg4tory-beta1/modpack`)
regenera exactamente el último zip publicado (mismo SHA-1 `1d2fee99…`).

## Resumen

| Proyecto | Última publicada | Última desarrollada | Diferencias importantes | Actualización recomendada |
|---|---|---|---|---|
| **PURG4TORY - Souls Grimore** (modpack, 1755336) | «0.7.0-beta.1», fileID **9325709**, 25-10, Beta. Contenido real = **0.6.0-beta.1.1** | 0.6.0-beta.1.1, idéntica a lo publicado (no hay cambios posteriores en el pack) | Ninguna en el pack. Solo cambia el mod propio que lleva dentro (Cauces 0.4.1 → 0.5.0) | **0.7.0-beta.2** = lo publicado + Cauces 0.5.0 (jar y `purg4tory_cauces.properties`), referenciando Cauces como proyecto (`cauces_cf`). Corregir la versión de Minecraft a **1.21.1** |
| **PURG4TORY Cauces** (mod, 1763725) | **0.4.0**, fileID 9311855, 24-10, Release (único archivo). **Pero el modpack no la usa**: lleva 0.4.1 en `overrides` | **0.5.0** (sha256 `83b00079…`), sin publicar | Corrección de fondo de las congelaciones (el hilo principal no espera a la generación) + las correcciones de 0.4.1 (cadenas lava→obsidiana, vigía en todos los mundos, planificador al cambiar de mundo) | Publicar **0.5.0** directamente (Beta). **No** publicar 0.4.1 ni ninguna dev |

## Qué descarga cada jugador

- **Quien instala el modpack actual** (9325709): pack 0.6.0-beta.1.1, que en el juego se ve como «0.6.0 Beta 1.1», con
  **Cauces 0.4.1** dentro. Ese 0.4.1 se congela al explorar rápido (laboratorio: 791 s de pausas en 15 min, máximo 79 s).
  Probablemente es lo que tienen los cuatro PCs de las pruebas manuales.
- **Quien instaló versiones anteriores del modpack** y no actualizó: Alphas con Cauces 0.3.0-exp1 o sin Cauces (ver tabla).
- **Quien baja Cauces suelto**: 0.4.0.
- Descargas totales del modpack: 67. La API no da el reparto por archivo.

## Archivos del modpack en CurseForge

| fileID | Nombre en CurseForge | Zip (= versión interna) | Fecha | Canal | Cauces dentro |
|---|---|---|---|---|---|
| 9325709 | 0.7.0-beta.1 | PURG4TORY-Souls-Grimore-**0.6.0-beta.1.1** | 25-10 | Beta | 0.4.1 (overrides) |
| 9303519 | 0.6.0-alpha.1.5 | **0.9.0-alfa.2** | 23-10 | Alpha | 0.3.0-exp1 |
| 9293690 | 0.5.0-alpha.1.4 | **0.5.0-alfa.2** | 23-10 | Alpha | — |
| 9291920 | 0.4.0-alpha.1.3 | **0.4.0-alfa.identidad.1** | 22-10 | Alpha | — |
| 9281011 | 0.4.0-alpha.1.2 | Purgatorio-RPG-**0.3.0-alfa.4** | 21-10 | Alpha | — |
| 9278476 | 0.2.0-alpha.1.1 | Purgatorio-RPG-**0.3.0-alfa.3** | 21-10 | Alpha | — |
| 9272644 | 0.1.0-alpha.1 | Purgatorio-RPG-**0.2.0-alfa** | 21-10 | Alpha | — |

Nunca publicadas (superadas, no hace falta publicarlas): 0.1.0/0.1.1/0.1.2-alfa, 0.3.0-alfa(.2), 0.5.0-alfa.1, 0.6.0 a 0.9.0-alfa.1
y 0.6.0-beta.1 (con Cauces 0.4.0; se publicó directamente la 1.1).

## Problemas de distribución encontrados

1. **Versión de Minecraft mal etiquetada en los 7 archivos: 1.21.11 en vez de 1.21.1.** El manifiesto dentro del zip dice
   1.21.1, así que la app instala bien, pero el archivo aparece en los filtros de una versión de Minecraft que no es. Se
   puede corregir editando cada archivo en CurseForge.
2. **Nombres que no coinciden.** El nombre en CurseForge («0.7.0-beta.1») no es el del zip ni el del juego («0.6.0 Beta 1.1»).
   Por eso, en las pruebas manuales no se sabe a simple vista qué versión se está usando. Propuesta: la próxima se llama
   **0.7.0-beta.2** en `pack.toml`, de modo que zip, manifiesto, título del menú y nombre en CurseForge digan lo mismo.
3. **Cauces va como jar suelto en `overrides/mods`** y no como proyecto, aunque el proyecto existe. CurseForge lo aprobó,
   pero así la versión de Cauces del modpack y la del proyecto se separan sin que nadie lo note (0.4.1 frente a 0.4.0). El
   empaquetador ya admite `cauces_cf`.
4. **Ningún aviso de versiones nuevas de mods propios.** Desde ahora se avisará explícitamente en cada entrega.

## Comprobación de paquetes (generados en una copia temporal; no se tocó la fuente)

Candidata **0.7.0-beta.2** = fuente publicada + Cauces 0.5.0 + `purg4tory_cauces.properties` nuevo:

| Modo | Zip de cliente | Paquete de servidor |
|---|---|---|
| `cauces_cf` (recomendado; fileID de prueba) | Manifiesto: 154 archivos sin duplicados (153 + Cauces 1763725); `overrides/mods` sin el jar; Minecraft 1.21.1, NeoForge 21.1.259 | Lleva `purg4tory_cauces-0.5.0.jar` en `overrides/mods` (un servidor no lee el manifiesto); 133 mods en `mods-servidor.json` |
| jar en `overrides` (como hasta ahora) | 153 archivos + `overrides/mods/purg4tory_cauces-0.5.0.jar` | Igual |

Respecto a lo publicado solo cambian el jar de Cauces, su `.properties` y los textos de versión (manifiesto, título del menú
y libro de bienvenida, que ya muestran «0.7.0 Beta 2»).

## Propuesta para ponerlo todo al día (sin versiones intermedias)

1. Revisar y publicar **Cauces 0.5.0** en el proyecto 1763725 como Beta (paquete en `~/dev/lab-p0/publicar-cauces-0.5.0/`).
   No publicar 0.4.1.
2. Cuando CurseForge apruebe el archivo, poner su fileID en `cauces_cf` de `pack.toml`, cambiar el jar y el `.properties` de
   `overrides`, subir la versión a **0.7.0-beta.2** y generar la entrega (`crear_entrega.py`, ya comprobado que genera bien).
3. Publicar el modpack **0.7.0-beta.2** con la versión de Minecraft **1.21.1** y, si se quiere, corregir la etiqueta de los
   archivos anteriores.
4. Que las pruebas manuales usen 0.7.0-beta.2 (en el menú del juego debe verse «0.7.0 Beta 2») con la guía de 30 min
   (`docs/auditoria-p0/PRUEBA-WINDOWS.md`).

Pendiente de desarrollo, no resuelto en ninguna versión (documentado en la Beta 1): tirón de ~25 s al entrar al End
(End's Phantasm) y `/locate`, que bloquea de 1 a 21 s.
