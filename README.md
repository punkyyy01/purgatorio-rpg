# PURG4TORY - Souls Grimore
An open-world Minecraft RPG modpack focused on exploration, dungeons, diverse biomes, challenging encounters, and cozy survival. Built with NeoForge.

## Contenido del repositorio

| Carpeta | Qué es |
|---|---|
| `modpack/` | **Fuente del modpack** (versión 0.7.0-beta.2): `pack.toml` (identidad y versión), `bloqueo.json` (archivos exactos de CurseForge), `overrides/` (configuración, datapacks, menú), `servidor/`, `herramientas/` |
| `modpack/mods-propios/purg4tory_cauces/` | Código fuente de **PURG4TORY Cauces 0.5.0** (mod propio, MIT); `construir.sh` compila el jar de forma reproducible; textos de publicación en `publicacion/` |
| `doc/` | Documentación del pack (plantillas que se rellenan con la versión al generar la entrega) |
| `herramientas-int/` | `crear_entrega.py`: genera el zip de cliente, el paquete de servidor y la documentación desde `modpack/` + `doc/` |
| `prueba/` | Scripts de las pruebas automáticas del pack (cliente en Xvfb, servidor, aceptación) |
| `docs/` | Auditorías (versiones en CurseForge, congelación de ticks) y guía de publicación de 0.7.0-beta.2 |
| `laboratorio/p0-congelacion/` | Herramientas de laboratorio (solo pruebas, no distribuir) |

Generar la entrega: `python3 -I herramientas-int/crear_entrega.py modpack doc entrega`.
Los binarios (zips y jars de terceros) no se guardan en Git: se publican en CurseForge. La única excepción es el jar propio
de Cauces en `modpack/overrides/mods/`, que necesita el paquete de servidor.
