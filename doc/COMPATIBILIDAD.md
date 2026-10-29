# Compatibilidad de mundos y actualizaciones — {{NOMBRE}} {{VERSION_VISIBLE}}

**Resumen: usa un mundo nuevo.** Esta versión cambia la generación del mundo (≈300 biomas más que la serie 0.8, Terralith + Tectonic + Streams Reflowing + Regions Unexplored, Biomes O' Plenty, etc.). No se ha comprobado —ni se promete— compatibilidad con mundos de las Alphas públicas.

| Caso | Qué esperar | Comprobado |
|---|---|---|
| **Cliente sin mundo → Beta 1** | Instalación limpia, sin riesgo. | Sí (importación y arranque hasta el menú desde un perfil nuevo). |
| **Mundo nuevo (cliente o servidor)** | Camino recomendado y el único probado de extremo a extremo. | Sí (batería de aceptación, `PRUEBAS-BETA1.md`). |
| **Mundo existente de una Alpha pública (≤ Alpha 5)** | Los chunks ya generados conservan su terreno; los nuevos se generan con los biomas y ríos actuales: **cortes bruscos de bioma y de río en los límites**. Faltarán bloques/objetos de mods que ya no estén (se convierten en aire al aceptar el aviso de NeoForge) y habrá registros nuevos. | **No probado.** No usarlo con un mundo que importe sin copia de seguridad. |
| **Mundo de la candidata interna 0.9.0-alfa.2** (no pública) | Igual de compatible salvo: Every Compat ya no genera variantes de las 4 maderas de Promenade (sakura, maple, palm, dark_amaranth) → esos bloques (solo los de Every Compat) desaparecen; Create ya no lleva dos recetas rotas de plata (sin efecto en el mundo). | Parcial: las pruebas 0.9.0-alfa.2 cargaron mundos de alfa.1; esta combinación no se probó. |
| **Servidor existente → Beta 1** | `instalar_servidor.py --mover-obsoletos` tras un respaldo (`SERVIDOR.md` §8). | El instalador sí (obsoletos y duplicados); el mundo no. |
| **Bajar de versión** | No soportado: se pierden bloques registrados por Every Compat y otros. | — |

## Qué cambia entre versiones que puede romper un mundo
- **Registros de bloques/objetos:** *añadir* es seguro; *quitar o renombrar* (típico en Every Compat al actualizar) rompe lo ya construido. Antes de cambiar la versión de un mod con módulos de compatibilidad, repite la prueba «mundo existente».
- **Worldgen/biomas/estructuras:** cualquier cambio altera solo chunks nuevos; los viejos no se regeneran.
- **Dimensiones:** Nether (24 biomas) y End (8) incluyen mods de generación (Incendium, Infernal Expansion, Nullscape, End's Phantasm).
- **Multijugador:** cliente y servidor deben ser de la misma versión de **todos** los mods.
- **Streams Reflowing:** guarda las cuencas de ríos en `<mundo>/streamsreflowing/`; hay que incluirlas en los respaldos. Cambiar la configuración de Streams no altera las ya guardadas.
- **PURG4TORY Cauces:** necesita Streams Reflowing 2.15.2 exacta para el planificador (si no, se desactiva solo; la salvaguarda de guardado sigue).

## Historial de versiones
La serie pública de CurseForge llega hasta **Alpha 5**. «Alpha 6–9» fueron etapas internas de desarrollo (nunca publicadas). Esta publicación, **{{VERSION_VISIBLE}}**, procede de la candidata interna **{{CANDIDATA}}**; la candidata se conserva intacta como punto de retorno.
