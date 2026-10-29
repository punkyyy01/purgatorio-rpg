# Llevar Cauces 0.5.0 al modpack (no hecho: requiere publicar antes en CurseForge)

## Situación actual

| Paquete | Cómo lleva Cauces | Versión |
|---|---|---|
| Zip de cliente 0.6.0-beta.1 (`entrega_0.6.0-beta.1`) | jar en `overrides/mods` (sin `cauces_cf`) | 0.4.0 |
| 0.6.0-beta.1.1 = **publicada en CurseForge como «0.7.0-beta.1»** (fileID 9325709, 25-10) | jar en `overrides/mods` | 0.4.1 |
| Fuente del modpack (`~/dev/purg4tory-beta1/modpack`) | `overrides/mods/purg4tory_cauces-0.4.1.jar`, sin `cauces_cf` en `pack.toml` | 0.4.1 |

**CurseForge:** el archivo 9325709 se aprobó con el jar de Cauces en `overrides/mods`, pero lo correcto (y lo que pide la
política de proyectos externos) es referenciarlo como proyecto, ya que existe. El empaquetador ya lo soporta: con `cauces_cf` en `pack.toml`, el **zip de cliente** quita el
jar de `overrides/mods` y lo pone en el manifiesto, y el **paquete de servidor** sigue llevando el jar en `overrides/mods`
(un servidor no lee el manifiesto de CurseForge).

## Pasos (después de que CurseForge apruebe el archivo 0.5.0)

En `~/dev/purg4tory-beta1/modpack/`:

1. `overrides/mods/`: cambiar `purg4tory_cauces-0.4.1.jar` por `purg4tory_cauces-0.5.0.jar` (sha256 `83b00079…`).
2. `overrides/config/purg4tory_cauces.properties`: sustituir por el de esta carpeta (añade las 5 opciones nuevas
   documentadas y corrige el comentario de `cadenaSinCargar`; sin él, las opciones valen igualmente `true`).
3. `pack.toml`: añadir `cauces_cf = { projectID = 1763725, fileID = <fileID del archivo 0.5.0> }` y subir la versión del pack
   (**`0.7.0-beta.2` / «0.7.0 Beta 2»**: la última publicada se llama «0.7.0-beta.1» en CurseForge; así el nombre del archivo, el manifiesto y el título del juego vuelven a coincidir).
4. Changelog del pack: «PURG4TORY Cauces 0.4.0 → 0.5.0: corrige las congelaciones del mundo al explorar» (ver `CHANGELOG-0.5.0.md`).
5. `herramientas-int/crear_entrega.py` y la batería corta (`prueba_titulo.sh`). Comprobar en el zip de cliente que el
   manifiesto lleva `projectID 1763725` y que `overrides/mods` no lleva el jar; en el de servidor, que sí lo lleva.
6. Exportar desde la app de CurseForge como siempre (paso humano de la Beta 1).

Si prefieres no esperar a la moderación, se puede dejar el jar en `overrides/mods` para pruebas privadas, pero **no para
publicar** el modpack.
