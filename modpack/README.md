# Purgatorio RPG — modpack de cliente (0.2.0-alfa candidata para pruebas)

Minecraft **1.21.1**, **NeoForge 21.1.259**. Modpack propio (no usa Prominence II como base).
Estado: 0.1.0-alfa probado a mano (importa, arranca, se juega). 0.1.1-alfa comprobado solo de forma estática.

La 0.1.0-alfa queda como referencia en `versiones/0.1.0-alfa/` y en la etiqueta git local `modpack-0.1.0-alfa`.

## Archivos

| Archivo | Qué es |
|---|---|
| `seleccion.toml` | Mods elegidos, con pilar y motivo |
| `dependencias.toml` | modId → proyecto de CurseForge para las dependencias |
| `fijados.toml` | Archivos fijados a mano (con el motivo) |
| `pack.toml` | Nombre, versión, NeoForge y RAM recomendada |
| `bloqueo.json` | Resultado exacto: projectID/fileID, nombre del jar, SHA-1, modIds y versiones |
| `LISTA-MODS.md` | Lista legible de los 106 archivos |
| `informe-dependencias.md` | Resultado de la comprobación estática |
| `overrides/` | Archivos propios que van dentro del zip |
| `herramientas/` | `resolver.py`, `verificar_modrinth.py`, `empaquetar.py`, `cofres_dobles.py` |
| `versiones/` | Copia de la selección y del bloqueo de versiones anteriores |

Reconstruir (los jars se descargan a una caché fuera del repo):

```sh
python3 -I herramientas/resolver.py . ~/dev/modpack-cache
python3 -I herramientas/verificar_modrinth.py .
python3 -I herramientas/empaquetar.py . ~/dev/modpack-dist
```

## 0.2.0-alfa (candidata para pruebas, no publicada)

Fauna por bioma (pesos de Naturalist, Critters and Companions, reposición con In Control!), zonas tranquilas,
Create opcional, Champions 2.1.11.3 con lista blanca y campamentos de Artifacts al 25 %. Cambios: `CHANGELOG-0.2.0.md`; comprobaciones en partida: `PRUEBA-0.2.0.md`; detalle y pruebas de laboratorio:
`hito-0.2.0/INTEGRACION.md`; diagnóstico previo: `hito-0.2.0/FASE-A-DIAGNOSTICO.md`; prueba a pie:
`hito-0.2.0/PRUEBA-ECOLOGIA.md`.

## Cambios de 0.1.2-alfa

Solo empaquetado: los mismos 106 mods y overrides que 0.1.1, salvo `sparsestructures.json5`, que sale del zip
sin cambiar el juego (ver sección 1).

## Cambios de 0.1.1-alfa

| Cambio | Detalle |
|---|---|
| Fuera Traveler's Backpack | Decisión del equipo. Proyecto 321117 retirado del manifiesto |
| Sophisticated Backpacks + Sophisticated Core | Oficiales de P3pp3rF1y, 1.21.1 NeoForge |
| Enderman Overhaul | Hostiles por bioma, incluidos 4 del Nether |
| Rotten Creatures + Platform | Hostiles por bioma. Platform fijado a 1.2.10.2: ver `fijados.toml` |
| Waystones | Sin waystones salvajes; quedan las de aldea y las fabricadas |
| Mochilas | Mejoras automáticas recortadas y sin mochilas en el botín de cofres |

## 1. Aviso de CurseForge al importar

**Resultado de la prueba de 0.1.1.** CurseForge marcó exactamente dos archivos:
- `config/paxi/datapacks/purgatorio_reglas/data/purgatorio/function/reglas.mcfunction`
- `config/sparsestructures.json5`

No marcó ningún `.toml`, `.json` ni `.mcmeta`.

**Causa.** CurseForge no publica qué tipos de archivo marca. Su soporte y su blog solo dicen que la app señala los
archivos de overrides de los zip importados que no estén alojados en CurseForge
([soporte](https://support.curseforge.com/support/solutions/articles/9000197912-sharing-modpacks-custom-profiles),
[blog](https://blog.curseforge.com/stay-safe-how-to-spot-suspicious-modpacks-and-files/)). El patrón observado
indica una lista de extensiones de configuración aceptadas en la que no están `.mcfunction` ni `.json5`.
Es una deducción de la prueba, no una regla documentada.

**Corrección en 0.1.2:**

| Archivo | Qué se hizo y por qué |
|---|---|
| `sparsestructures.json5` | **Fuera del zip, sin cambiar el comportamiento.** El mod solo lee ese nombre exacto (`Constants.CONFIG_FILENAME`), así que no se puede cambiar el formato. Pero si no existe, copia su `sparse-structures-default-config.json5` (`Files.copy`), y esos valores son idénticos a los nuestros: `spreadFactor` 2, `idBasedSalt` true, mansión ×2. La copia queda en `referencia/` |
| `reglas.mcfunction` | **Se mantiene.** Ver abajo |

Por qué `reglas.mcfunction` no tiene alternativa compatible:
- `disableRaids` es una regla de juego (gamerule). Solo una función de datapack (siempre `.mcfunction`) o un mod
  pueden fijarla al crear el mundo.
- Las raids no dependen de ningún archivo de datos que se pueda sustituir por JSON.
- Las patrullas sí se podrían quitar con la etiqueta JSON `minecraft:without_patrol_spawns`, pero eso no evita
  el `.mcfunction`.
- Los mods que fijan reglas desde un `.toml` son pequeños y de terceros: Gamerule Defaults (~200 descargas),
  Global Gamerules NeoForge (~2,6 mil) y World Start Commands (~84 mil, sin cambios desde 2025-04).
- Añadir uno solo para cambiar el aviso por más código ajeno no compensa.

Queda, por tanto, un único archivo marcado, que es propio y de dos líneas. Es una limitación de la importación
manual de zips. `herramientas/empaquetar.py` avisa si algún override nuevo usa una extensión marcada.

**Si se publica en CurseForge.** Los overrides propios (configs, scripts, datapacks) son el contenido previsto,
según la [guía de envío](https://support.curseforge.com/support/solutions/articles/9000197908-exporting-a-modpack-for-curseforge-project-submission).
Su moderación los revisa. Que la instalación desde la página oficial no muestre el aviso es probable, pero no
está documentado.

**Pendiente antes de publicar.** Confirmar en cada proyecto que permite la distribución por terceros.

| Override (en el zip) | Tipo | Para qué |
|---|---|---|
| `config/paxi/datapacks/purgatorio_reglas/` (3 archivos) | datapack propio | `disableRaids`, sin patrullas |
| `config/waystones-common.toml` | config | sin waystones salvajes |
| `config/sophisticatedcore-common.toml` | config | mejoras de mochila desactivadas |
| `config/sophisticatedbackpacks-common.toml` | config | sin mochilas en cofres de botín |
| `defaultconfigs/champions-server.toml` | config | élites al 2 % |
| `defaultconfigs/sophisticatedbackpacks-server.toml` | config | mejoras activas solo en la mochila puesta |

**Prueba de 0.1.2:**
1. El aviso solo debe marcar `reglas.mcfunction`.
2. Tras el primer arranque, el perfil debe tener `config/sparsestructures.json5`, creado por el mod, con
   `"spreadFactor": 2`.

## 2. Lootr y los cofres

- **Cofres dobles partidos en dos.** Es una limitación documentada de Lootr
  ([#886](https://github.com/LootrMinecraft/Lootr/issues/886)), abierta y sin opción de configuración. Cada mitad
  de un cofre doble es un bloque con su propia tabla de botín, y Lootr las convierte por separado.
  - El botín total no cambia: es el mismo que darían las dos mitades.
  - No se duplica y sigue siendo por jugador.
  - El efecto es visual: dos cofres en lugar de uno.
- **Estructuras afectadas** (`herramientas/cofres_dobles.py`, mitades de cofre doble en los planos):

  | Mod | Planos | Mitades |
  |---|---|---|
  | CTOV | 235 | 504 |
  | Moog's Voyager | 47 | 200 |
  | Explorify | 28 | 56 |
  | Dungeons Arise | 9 | 36 |
  | Terralith | 11 | 32 |
  | Cataclysm | 9 | 32 |
  | Galosphere | 5 | 12 |
  | Structory | 5 | 12 |
  | Mowzie's | 1 | 2 |
  | Better Archeology | 1 | 2 |

  YUNG's, Seven Seas y vanilla no traen cofres dobles en sus planos.
- **Decisión: no se excluye nada.**
  - La alternativa sería `loot_modid_blacklist = ["ctov"]` en `lootr-common.toml`. Las aldeas volverían a tener
    cofres dobles, pero su botín sería compartido: el primero que llega se lo lleva todo.
  - Eso choca con la prioridad de mantener el botín individual, así que no se aplica.
- **Cofres con textura vanilla hasta abrirlos.** Lootr solo convierte un cofre cuando su zona de chunks está
  registrada como cargada del todo; los chunks del borde de la vista pueden quedarse fuera.
  - Al abrir el cofre, Lootr intercepta el reparto del botín (`MixinRandomizableContainer` cancela
    `unpackLootTable`) y lo convierte antes.
  - Así, el botín sigue siendo por jugador; el fallo es visual.
- **Lootr Conversion Fix no se instala.** Es de un solo autor y tiene 7 días y unas 70 descargas. Ataca justo
  este fallo: vuelve a registrar los chunks cercanos cada 2 segundos. Se reevaluará si el fallo visual molesta
  en partida.
- **Riesgo que hay que probar.** Romper un cofre que aún no se ha convertido, sin abrirlo antes.

## 3. Mochilas: Sophisticated Backpacks

- **Progresión.**
  - Cuero (cofre, cuero e hilo) → cobre → hierro (también directo desde cuero) → oro → diamante.
  - La de netherita se hace en la mesa de herrería, con plantilla y lingote.
  - Las capacidades y ranuras son las de serie del mod. Se ajustan en
    `sophisticatedbackpacks-server.toml`, sección `[server.<material>Backpack]`.
- **Desactivadas** (sin receta, `sophisticatedcore-common.toml`):
  - Inception (mochilas dentro de mochilas);
  - pila omega;
  - fundido, ahumado y alto horno automáticos;
  - alimentación básica y avanzada.

  Las versiones manuales de fundido, ahumado y alto horno siguen activas.
- **Siguen activas:**
  - imán y recogida;
  - filtro, depósito, recarga y reabastecer;
  - vacío;
  - cambio de herramienta;
  - compactado;
  - tanque, bomba y batería;
  - mesa de trabajo y cortapiedras;
  - pilas hasta el nivel 4;
  - alquimia, captura de mobs y «everlasting».
- **Pendiente del equipo.** Revisar si alquimia y captura de mobs encajan; no se han tocado.
- **Mejoras activas** (imán, recogida, cocina…) solo funcionan en la mochila puesta.
- **Mochilas fuera del botín de cofres.**
- **Mundos de 0.1.0 con Traveler's Backpack.**
  - Al abrirlos con 0.1.1, las mochilas de Traveler's y lo que contengan **desaparecen**.
  - Antes de cambiar, vacíalas en cofres con el perfil 0.1.0, o usa un mundo nuevo.
  - Importa 0.1.1 como perfil nuevo: no sobrescribas el de 0.1.0.

## 4. Criaturas hostiles

**Diagnóstico.** No hay ningún bloqueo: el pack simplemente casi no tenía hostiles de aparición natural.
- Terralith etiqueta sus 84 biomas en `c:` y `minecraft:`, así que los modificadores de bioma de Creeper Overhaul,
  Mowzie's y los demás sí los alcanzan.
- En 0.1.0 no había nada nuevo en el Nether salvo peces de Tide.

**Qué aporta cada mod:**

| Mod | Hostiles de aparición natural | Ligado a estructura, jefe o dimensión |
|---|---|---|
| Creeper Overhaul | Creeper propio en 14 tipos de bioma y en cuevas; sustituye al vanilla | — |
| Mowzie's | Foliaath (jungla), Naga (costa y montaña), Lantern (bosque mágico), cazadores Umvuthana (sabana) | Wroughtnaut, Frostmaw, Umvuthi, Sculptor |
| Cataclysm | Deeplings (océano profundo), Koboleton, Ignited Berserker, Coral Golem; pesos en su config | Todos los jefes |
| Galosphere | Preserved (cuevas de sal rosa) | — |
| Deeper and Darker | Mobs del sculk | Otherside, Ancient City |
| Friends & Foes | Barnacle (océano); Iceologer e Illusioner desactivables | Casi todo es pasivo o neutral |
| Naturalist, Tide | Fauna y peces (no hostiles) | — |
| **Enderman Overhaul** (nuevo) | Enderman por bioma: 12 del Overworld, 2 del End y 4 del Nether (yermos, carmesí, distorsionado, valle de almas) | — |
| **Rotten Creatures** (nuevo) | Ver detalle abajo | Dead Beard: biomas de naufragio en playa |

Detalle de Rotten Creatures:
- Mineros no-muertos bajo tierra en todo el Overworld.
- Frostbitten y Glacial Hunter en biomas de iglú y en picos de hielo.
- Momias en biomas de pirámide.
- Swampy en pantano.
- Burned en los yermos del Nether.
- Immortal, raro.

**Explosiones.**
- Ninguno de los dos mods nuevos tiene enemigos que asedien bases.
- Rotten Creatures incluye un barril de TNT con su propio cálculo de explosión; está ligado a Dead Beard.
- Las bases reclamadas con Open Parties and Claims están protegidas de explosiones.

**Descartados por ahora:**

| Mod | Por qué |
|---|---|
| Mutant Monsters | Ataques que destruyen bloques |
| Born in Chaos | Muchas criaturas a la vez, estética de terror; candidato para revisar con calma |
| Mobs of Mythology | Candidato; sin revisar a fondo |
| Illager Invasion | Ligado a illagers y raids, que están desactivadas |
| Bygone Nether, Whisperwoods | Sin versión para 1.21.1 NeoForge |
| Incendium | Su único archivo para 1.21.1 es la 5.4.4, de 2024-12. CurseForge la marca como release, Modrinth como **alpha**, y las versiones posteriores ya no incluyen 1.21.1. Además no añade criaturas nuevas: solo biomas y estructuras del Nether |

El Nether sigue siendo la zona más pobre en hostiles nuevos.

## 5. Waystones

- **Ajuste.** `chunksBetweenWildWaystones = 0` desactiva las waystones salvajes, que eran las que aparecían sueltas
  en el terreno.
- **Siguen apareciendo:**
  - en aldeas vanilla (`spawnInVillages = "REGULAR"`);
  - en cada aldea de CTOV, que incluye una waystone garantizada mediante Lithostitched;
  - las que fabriquen los jugadores.
- **Mundos existentes.** Solo cambian los chunks nuevos. No se toca ninguna waystone ya generada o colocada.

## Cómo se verifica

- Cada mod es un proyecto de CurseForge. El archivo se elige entre los marcados 1.21.1 + NeoForge (release antes
  que beta), salvo los fijados a mano.
- Se descarga **ese mismo archivo** del CDN de CurseForge y se comprueba su tamaño.
- 101 de los 106 jars son idénticos (SHA-1) a un archivo de Modrinth. Los otros cinco solo se publican en CurseForge:
  - Spell Engine;
  - Paladins & Priests;
  - Storage Drawers;
  - Sophisticated Backpacks y Sophisticated Core.
- Se leen los `neoforge.mods.toml`, incluidos los anidados, para comprobar:
  - dependencias y rangos de versión;
  - incompatibilidades;
  - modIds duplicados;
  - el rango de NeoForge.
- Resultado: 0 problemas y 1 aviso. Dungeons Arise declara `minecraft [1.21,1.21.1)`, pero ATM10 y Better MC 5 usan
  ese mismo archivo en 1.21.1.

## Distribución y licencias

- El zip **no contiene ningún jar de terceros**: el manifiesto los referencia y el launcher los descarga de
  CurseForge.
- Hay licencias ARR (entre ellas Sophisticated, Enderman Overhaul y Rotten Creatures), NC-ND y personalizadas.
  Referenciarlas desde un modpack de CurseForge es el uso previsto.
- Antes de **publicar**, hay que releer cada licencia personalizada y confirmar en la página de cada proyecto que
  permite la distribución por terceros.
- **Créditos exigidos por la Stardust Labs License:** Terralith
  (<https://www.curseforge.com/minecraft/mc-mods/terralith>), Nullscape
  (<https://www.curseforge.com/minecraft/mc-mods/nullscape>) y Structory
  (<https://www.curseforge.com/minecraft/mc-mods/structory>) son obra de **Stardust Labs**. Se usan sin
  modificar y completos, como permite su licencia. El pack no incluye ni modifica archivos suyos.

## Configuración (conservadora)

- Sin raids ni patrullas: datapack global `purgatorio_reglas`, cargado por Paxi.
- Élites de Champions: probabilidad 0,02 en lugar de 0,1.
- Estructuras: Sparse Structures con factor 2 (valores por defecto del mod; copia en `referencia/`).
- Botín: Lootr da botín por jugador; sin Loot Integrations ni mochilas en cofres.
- Waystones y mochilas: ver secciones 3 y 5.

## Excluidos

| Excluido | Por qué |
|---|---|
| Traveler's Backpack | Decisión del equipo (0.1.1); sustituido por Sophisticated Backpacks |
| Aquamirae | No se localizó su proyecto NeoForge en CurseForge |
| Dungeons and Taverns | En CurseForge está dividido en módulos; pendiente de elegir |
| JEI | Pide una librería nueva y declara `minecraft [1.21,1.21.1)`; se usa EMI |
| Create y tecnología | Fuera del núcleo inicial |
| Simply Swords, Soulslike, Jewelry, Immersive Armors | Se solapan con la serie RPG |
| In Control! | Solo existe en beta |
| Incendium | Ver sección 4 |
| Lootr Conversion Fix | Ver sección 2 |
| Shaders, menús propios, Alma y traducción | Etapas posteriores |
