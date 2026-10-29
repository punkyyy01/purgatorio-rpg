# Pasos humanos para publicar {{NOMBRE}} {{VERSION_VISIBLE}} en CurseForge

**Nada de esto se ha hecho ni se hará automáticamente.** Orden estricto. Reglas de CurseForge consultadas el 2026-10-24 en `support.curseforge.com` (Moderation Policies; Exporting a modpack for project submission):
- «Los modpacks deben crearse con la aplicación de CurseForge, con el formato correcto»; **«no se permiten ediciones del manifiesto que genera la aplicación»**.
- Los mods alojados en CurseForge se **referencian** en el manifiesto; **no** se pueden poner jars de mods de CurseForge en `overrides/mods`.
- Un jar de un mod **no alojado en CurseForge** (aquí: PURG4TORY Cauces) solo puede ir en el pack si está en la lista de mods externos aprobados. **→ Cauces debe publicarse como proyecto de CurseForge** y añadirse al pack como cualquier otro mod.
- El **paquete de servidor** se sube como **«Additional File»** del archivo principal del modpack.

## Paso 0 — Antes de nada (bloqueantes si no se hacen)
1. **Revisar** esta carpeta: `PRUEBAS-BETA1.md` (qué se probó y qué no), `PROBLEMAS-CONOCIDOS.md`, `SEGURIDAD-GUARDADO.md`. Decidir si la Beta se publica (veredicto en `PRUEBAS-BETA1.md`).
2. **Jugar 30 min** con el ZIP importado en tu Windows (protocolo manual abajo): el cliente sin GPU de las pruebas no mide FPS ni valida combate «real».
3. **Protocolo con Renas (multijugador real):** ver `PRUEBAS-BETA1.md` §«Protocolo manual». Las pruebas automáticas no sustituyen una partida entre dos personas.

## Paso 1 — Publicar PURG4TORY Cauces como proyecto de CurseForge
Datos listos en `CAUCES-PROYECTO.md` (nombre, resumen, descripción, licencia MIT, categoría, archivo `purg4tory_cauces-0.4.0.jar`, SHA-256). Esperar su **aprobación** (los archivos de proyectos nuevos pasan moderación). Anotar el `projectID` y el `fileID` del archivo aprobado.

## Paso 2 — Construir el pack final desde Costa Rica (única fuente de verdad)
En el servidor de Costa Rica: añadir en `modpack/pack.toml` `cauces_cf = { projectID = <id>, fileID = <id> }` y volver a ejecutar `crear_entrega.py`. Con esa línea el zip **no lleva el jar de Cauces en `overrides/mods`** y lo referencia en el manifiesto. Volver a pasar la batería corta (`prueba_titulo.sh`).

## Paso 3 — Exportar desde la aplicación de CurseForge (obligatorio)
1. Importar el ZIP resultante en la app de CurseForge (Windows) y comprobar que abre (menú «{{VERSION_VISIBLE}}»).
2. En el perfil: **Share profile → Export Profile → .zip**. En el cuadro, nombre **{{NOMBRE}}**, versión **{{VERSION}}**, y marca para exportar solo `config`, `defaultconfigs` y lo imprescindible (nunca la carpeta `saves`, `logs` ni `crash-reports`).
3. **Este zip exportado por la app es el que se sube.** No subir el zip generado por `empaquetar.py` ni editar su `manifest.json`.
4. **Regla anti-divergencia:** la exportación desde Windows es solo un *envoltorio*. No se cambia ningún mod ni configuración allí. Si hace falta cambiar algo: se cambia en Costa Rica, se regenera y se repite este paso. Comprobar después que `manifest.json` (mods y fileIDs) del export coincide con `SHA256`/`LISTA-MODS.md` de la entrega: `python3 herramientas-int/comparar_manifiestos.py <entrega>/…zip <export>.zip` (en el repositorio de Costa Rica, `herramientas-int/`; «SIN DIFERENCIAS» = OK).

## Paso 4 — Subir a CurseForge
1. Proyecto **{{NOMBRE}}** → *Upload file*: el zip exportado. **Release type: {{CANAL}}**. Versión de Minecraft 1.21.1; loader NeoForge. Changelog: `CHANGELOG-PUBLICO.md`.
2. Tras subirlo, en ese archivo: **Additional File → `PURG4TORY-servidor-{{VERSION}}.zip`** (paquete de servidor).
3. Página del proyecto: descripción `DESCRIPCION-ES.md` (y `DESCRIPTION-EN.md` si se desea), resumen de una línea (primera frase de la descripción), avatar `identidad/curseforge/avatar_proyecto_512_fondo_oscuro.png` (≥400×400), cabecera y galería con capturas **reales** de `capturas/` (cada una indica con qué cliente se tomó). Categoría: *Adventure and RPG* (+ *Exploration*, *Magic*, *Combat / PvE* si procede).
4. **Mods externos de la descripción:** ninguno (todos los mods están en CurseForge; el único propio, Cauces, se publica en el Paso 1).
5. Enviar a revisión. Si la moderación rechaza algo, **no borres el proyecto ni lo subas de nuevo**: responde en el hilo del rechazo.

## Paso 5 — Después
Anuncio con la descripción y los **problemas conocidos**; abrir un canal de reporte de fallos; hacer copia del zip final y de `SHA256SUMS.txt` fuera de la máquina.
