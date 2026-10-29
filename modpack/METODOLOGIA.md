# Metodología de desarrollo de Purgatorio RPG

Vigente desde el hito 0.4.0. Sustituye la forma anterior de trabajar, mod por mod, por un trabajo por
**sistemas completos** que aprovecha primero lo que ya existe y está probado.

## 1. Principios

1. **Sistemas, no mods.** Cada hito trabaja necesidades de juego completas. Los sistemas son:
   ecosistemas y fauna, cuevas y exploración, combate, magia, guía del jugador, interfaz, progresión,
   botín y multijugador. Un mod es una pieza de un sistema, no un objetivo.
2. **Primero lo existente.** Antes de diseñar o programar algo propio se busca una solución completa y
   probada. El orden de preferencia es:
   1. configuración o datapack sobre mods que ya están en el pack;
   2. un mod o una compatibilidad existente y mantenida;
   3. adaptar un recurso de terceros cuya licencia lo permita, citando la autoría y conservando sus avisos;
   4. desarrollo propio, mínimo y solo para lo que no existe.
3. **Comparar pocas alternativas y en la práctica.** Para cada necesidad se comparan de 2 a 4 candidatos
   prometedores, no el catálogo entero. Se elige el que mejor encaja con la visión, aunque no sea el más
   popular.
4. **El conjunto es lo que se prueba.** No se vuelve a demostrar que cada mod funciona solo. Se comprueba
   que el sistema produce una experiencia coherente y divertida junto con el resto del pack.
5. **Un conflicto no se resuelve quitando el mod.** Ante un conflicto entre mods importantes (Terralith,
   Tectonic…), primero se buscan compatibilidades existentes y combinaciones que ya funcionan en
   proyectos reales. Retirar o sustituir un mod importante se consulta siempre antes.
6. **Investigación con límite.** Cada pregunta tiene un tiempo acotado. Lo aprendido se anota en el
   documento del hito para no repetirlo. Se distingue siempre entre causa demostrada e hipótesis.

## 2. Visión que guía las elecciones

RPG de mundo abierto; libertad de progresión; exploración interesante en superficie y bajo tierra;
actividades pacíficas con peso propio; dificultad por regiones; sin grindeo excesivo ni inflación de botín.
Mods ligeros en rendimiento y mantenidos para Minecraft 1.21.1 + NeoForge.

## 3. Ficha de cada sistema

Cada sistema se documenta en el hito con esta ficha breve:

| Apartado | Contenido |
|---|---|
| Necesidad | Qué debe sentir o poder hacer el jugador, en una o dos frases |
| Diagnóstico | Qué falla hoy, con datos (demostrado o hipótesis) |
| Candidatos | De 2 a 4: qué aporta cada uno, mantenimiento (último archivo 1.21.1 NeoForge), descargas, licencia, lado (cliente o servidor) y dependencias |
| Uso real | En qué modpacks públicos aparece ya junto a nuestros mods clave (`coocurrencia_modpacks.py`) |
| Riesgo | Rendimiento, generación del mundo (¿exige mundo nuevo?) y conflictos conocidos |
| Prueba | La mínima que responde la duda: estática, laboratorio con semilla fija o partida manual |
| Decisión | Qué se adopta, qué se aplaza y qué hay que desarrollar nosotros |

## 4. Dónde buscar

- **CurseForge**: la API oficial cuando haya clave (ver el apartado 6) y, sin clave, CFWidget.
- **Modrinth**: su API pública no necesita clave. Sirve para buscar mods y leer los manifiestos de modpacks.
- **GitHub y la documentación de los autores**: wikis, incidencias abiertas y notas de compatibilidad.
- **Modpacks de referencia** (Prominence II, Craftoria, ATM10, BMC5 y packs de exploración de 1.21.1):
  sirven para ver qué combinaciones funcionan y cómo integran los sistemas. Son una referencia de diseño;
  sus archivos (configuraciones, misiones, scripts, traducciones o recursos) no se copian.

## 5. Licencias: referenciar frente a redistribuir

| Acción | Regla |
|---|---|
| Referenciar un mod en el manifiesto (projectID/fileID) | Permitido para cualquier mod publicado en CurseForge; CurseForge lo descarga al instalar |
| Incluir el jar de un tercero en el zip | No se hace nunca |
| Configuraciones de terceros en `overrides/` | Solo cambios propios y necesarios. El resto se regenera desde las versiones exactas (`regenerar.sh`) |
| Datapacks y scripts propios que solo nombran IDs y valores numéricos de otros mods | Son obra nuestra (MIT); no copian código ni recursos de otros autores |
| Adaptar archivos de terceros | Solo si su licencia lo permite. Se conserva el aviso de copyright y se anota el origen en `LICENSES/` |
| Mods con licencia restrictiva (por ejemplo, la Stardust Labs License de Terralith, Nullscape, Structory e Incendium) | Se usan sin modificar. No se distribuyen versiones modificadas ni archivos derivados de ellos |
| Material gráfico, logos y marca de Purgatorio | Todos los derechos reservados |

Antes de adoptar un recurso se anota su licencia en la ficha. Si no está clara, se pregunta al autor o se descarta.

## 6. Herramientas

| Herramienta | Uso |
|---|---|
| `herramientas/resolver.py` | Resuelve la selección contra CurseForge y escribe `bloqueo.json` |
| `herramientas/fuente_cf.py` | Fuente de metadatos de CurseForge: la API oficial si hay clave y, si no, CFWidget |
| `herramientas/buscar_mods.py "<texto>"` | Descubrimiento en Modrinth (siempre) y en CurseForge (con clave) |
| `herramientas/coocurrencia_modpacks.py <caché> <slug>…` | Qué mods acompañan a una combinación en los modpacks de 1.21.1 NeoForge de Modrinth |
| `herramientas/verificar_modrinth.py` | Segunda fuente: busca cada jar del bloqueo por su SHA-1 en Modrinth |
| `herramientas/empaquetar.py` | Construye el zip **solo** desde `bloqueo.json` y `overrides/`, sin red ni clave |

### API oficial de CurseForge

- Es opcional. Construir el zip nunca la necesita y, sin clave, todo funciona como antes: el bloqueo
  resultante es idéntico byte a byte.
- Activación: una clave de la consola de CurseForge for Studios, guardada en
  `~/.config/purgatorio-rpg/curseforge-api-key` con permisos `600`, o en la variable `CURSEFORGE_API_KEY`.
  Nunca va en el repositorio, en argumentos de la línea de órdenes ni en los registros. El programa
  rechaza el archivo si otros usuarios pueden leerlo.
- Elección de la fuente con la variable `PURGATORIO_FUENTE_CF`: `auto` (por defecto), `oficial` o `cfwidget`.
- Lo que añade:
  - comprueba el SHA-1 que publica CurseForge contra el jar descargado;
  - compara las dependencias que declara CurseForge con el bloqueo;
  - avisa si el autor no permite la distribución por terceros;
  - permite buscar por versión y cargador, y mantener actualizado el bloqueo.
- `herramientas/probar_fuente_cf.py` comprueba sin red la normalización y el manejo de la clave.

## 7. Pruebas

Se mantienen los tres niveles: rápidas, manuales e intensivas. Además:

- **Pruebas de conjunto**: laboratorio con semilla fija (`purgatorio-ecologia-1`) y rutas reproducibles,
  con bots que se mueven y perfiles comparables (pack actual, alternativa y Vanilla).
- **Proporcionalidad**: el tamaño de la prueba depende del riesgo. Un datapack pequeño se valida con
  `/locate` y un censo; un cambio de generación del mundo pide una ruta completa; las pruebas multijugador
  intensivas solo se hacen cuando el cambio afecta al rendimiento.
- **Nada se da por bueno en el cliente** si solo se ha validado por consola. Lo que necesita pantalla
  (sonido, interfaz, sensación) va a la lista de pruebas manuales.
