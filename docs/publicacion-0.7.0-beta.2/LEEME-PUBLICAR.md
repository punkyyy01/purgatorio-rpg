# Publicar PURG4TORY Cauces 0.5.0 y PURG4TORY: Souls Grimore 0.7.0-beta.2

Orden obligatorio: **1. Cauces → aprobación → 2. modpack.** El modpack referencia Cauces por su `fileID`, que solo existe
después de subirlo. Nada de esta carpeta está publicado ni comiteado.

## 1. Cauces 0.5.0 (proyecto 1763725) — súbelo ahora

| Campo en CurseForge | Valor |
|---|---|
| Archivo | `purg4tory_cauces-0.5.0.jar` (en `~/dev/publicar-purg4tory-0.7.0-beta.2/1-cauces-0.5.0/` o compilado con `modpack/mods-propios/purg4tory_cauces/construir.sh`) |
| Hashes | sha256 `83b00079624a17785f24d311eb515bd62c2b82e76e06c40b513b94f7f5b6d8ff` · sha1 en `SHA256SUMS.txt` |
| Display name | `PURG4TORY Cauces 0.5.0` |
| Release type | **Beta** |
| Game version | **1.21.1** (solo esa) · Mod loader **NeoForge** · Java 21 |
| Environment | **Client** y **Server** (en un jugador debe estar en el cliente) |
| Related projects | Streams Reflowing → **Optional Dependency** |
| Changelog | `modpack/mods-propios/purg4tory_cauces/publicacion/CHANGELOG-0.5.0.md` (pega la parte ES o EN) |
| Descripción del proyecto | Añade el párrafo de «Descripción del proyecto» de `CURSEFORGE-0.5.0.md` |

No subas 0.4.1 ni ninguna dev: 0.5.0 las contiene.
**Cuando CurseForge lo apruebe, anota el `fileID`** (número en la URL del archivo).

## 2. Modpack 0.7.0-beta.2 (proyecto 1755336) — tras aprobar Cauces

1. Desde el repositorio: `docs/publicacion-0.7.0-beta.2/completar_modpack.sh <fileID>` (escribe el fileID en `modpack/pack.toml`)
   (o pásame el fileID y lo hago yo; además puedo comprobar con la API que ese archivo es exactamente el jar de 0.5.0).
   Debe terminar en `RESULTADO: TODO CORRECTO`. Los zips quedan en `entrega/` (en la raíz del repo, ignorada por Git) y los hashes en `VERIFICACION.txt`.
2. Sube a CurseForge:

| Campo | Valor |
|---|---|
| Archivo principal | `entrega/PURG4TORY-Souls-Grimore-0.7.0-beta.2.zip` |
| Display name | **`0.7.0-beta.2`** (igual que el zip, el manifiesto y el menú del juego: «0.7.0 Beta 2») |
| Release type | **Beta** |
| Game version | **1.21.1** (¡no 1.21.11!) · NeoForge |
| Changelog | `docs/publicacion-0.7.0-beta.2/CHANGELOG-0.7.0-beta.2.md` |
| Archivo adicional (opcional) | `entrega/PURG4TORY-servidor-0.7.0-beta.2.zip` como server pack |

Qué contiene (verificado por el script): lo publicado en «0.7.0-beta.1» + Cauces 0.5.0 como **dependencia de CurseForge**
(no va jar suelto en el zip de cliente) + configuración de Cauces con las 5 opciones nuevas + nombre de versión unificado.
Ningún otro cambio.

## 3. Acciones tuyas en CurseForge

1. Subir Cauces 0.5.0 (Beta, 1.21.1, NeoForge, Cliente+Servidor, Streams Reflowing opcional) y actualizar su descripción.
2. Esperar la aprobación y anotar el `fileID`.
3. Subir el zip del modpack 0.7.0-beta.2 (Beta, **1.21.1**), con su changelog y, si quieres, el paquete de servidor.
4. Corregir la etiqueta **1.21.11 → 1.21.1** en los 7 archivos antiguos del modpack (Edit file → Game versions).
   Opcional, pero evita que aparezcan en filtros de otra versión.
5. Opcional: archivar u ocultar las Alphas antiguas para que nadie las instale por error.

## 4. Comprobar que se descarga lo nuevo

- Pásame los dos `fileID` cuando estén aprobados y lo compruebo con la API: el último archivo de cada proyecto, su versión
  de Minecraft y que los SHA-1 coinciden con los de `SHA256SUMS.txt` y `VERIFICACION.txt`.
- En un PC: instalar el modpack desde la app de CurseForge (instancia nueva o «Update») y comprobar:
  - en el menú del juego pone **«0.7.0 Beta 2»**;
  - en `mods\` está `purg4tory_cauces-0.5.0.jar` (y no 0.4.1);
  - al salir, `logs\latest.log` tiene una línea `al parar: …` que termina en `spawns cortados por terreno no listo: N`
    (esa parte solo existe en 0.5.0).
- Después, la prueba de 30 min: `~/dev/purg4tory-souls-grimore/docs/auditoria-p0/PRUEBA-WINDOWS.md`.
