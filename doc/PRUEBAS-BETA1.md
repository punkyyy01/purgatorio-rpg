# Pruebas de {{NOMBRE}} {{VERSION_VISIBLE}} — qué se comprobó y qué no

Entorno: servidor de Costa Rica (20 hilos, Java 21), **cliente de software sin GPU** (Xvfb 1280×720, llvmpipe) → **no hay FPS ni validación gráfica con GPU**. Servidor de pruebas instalado **desde cero con el paquete de servidor** (`instalar_servidor.py --instalar-neoforge`), mundo nuevo (semilla `purg4tory-beta1`), producción y mundos persistentes intactos. Un servidor o laboratorio a la vez (`flock`). Scripts en `prueba/` del repositorio.
**Presupuesto:** la batería final ocupó ≈46 min de reloj (aceptación 11 min, dos clientes 6 min, título 1,5 min, resoluciones 6 min, parada acotada 4 min, restauración 2 min, un jugador y capturas ≈15 min); además hubo ≈25 min de repeticiones de depuración de scripts de prueba (declaradas en cada fila). Sin esperas por bloqueos ni procesos huérfanos.

## Resultados
| # | Prueba | Resultado | Veredicto |
|---|---|---|---|
| 1 | Instalación limpia del servidor (zip → carpeta vacía) | 129 mods descargados con SHA-1 + Cauces + NeoForge 21.1.259 oficial verificado: **1 min 41 s**; 4 descargas manuales listadas con enlace y SHA-1; al colocarlas, «limpio». Reinstalación sobre una versión anterior: detecta OBSOLETO/DUPLICADO y los aparta; respalda `config/` | ✅ |
| 2 | Dependencias y duplicados (estático, 154 jars) | 462 dependencias obligatorias, **0 sin cubrir**; los únicos «duplicados» son bibliotecas jar-in-jar (Biolith en Promenade, Bundle API en Runes): NeoForge usa la más alta | ✅ |
| 3 | Reproducibilidad del empaquetado | Dos construcciones seguidas dan **zips idénticos byte a byte** (cliente y servidor) | ✅ |
| 4 | Arranque del servidor | 85 s (primer arranque, con generación del área de aparición); Cauces «ACTIVA», 49 tablas de botín, 5 datapacks propios; **0 errores de receta**; 37 `ERROR` (34 `RuntimeDistCleaner`, 2 avisos de Every Compat, 1 logros de WDA): ruido conocido | ✅ |
| 5 | **Cliente hasta la pantalla de título SIN QuickPlay** (perfil limpio, 153 mods + Cauces) | Llega al menú de PURG4TORY con **«{{VERSION_VISIBLE}}»** visible; Every Compat carga **10 módulos** (incluido `regions_unexplored`), **0 errores de módulo**, **0 errores de textura de Promenade** (antes 16); ≈80 s en cliente de software. Control: antes del arreglo había 16 errores de textura | ✅ |
| 6 | Título en 854×480, 1920×1080 (escala auto y 2) y 2560×1440 (escala 3) | Botones, logotipo y texto de versión se ven bien y no se solapan en las cuatro (capturas) | ✅ |
| 7 | Botín (`/loot` 200–500 veces por tabla) | `shiraz_palace_normal` 4,03 → **0,88** objetos de alto nivel por cofre; mezcla de 3 tablas 4,22 → **1,17**; el equipo de netherita desaparece de los cofres normales | ✅ |
| 8 | Dos clientes independientes conectados a la vez (Pruebas, Pruebas2) | Ambos entran y juegan; reciben el **libro de bienvenida** (una vez) y los libros de Alex's Mobs/Tide | ✅ |
| 9 | **Teletransporte en frío** (Cauces) | Un jugador: destino a 3000,3000 «preparado en 37,7 s sin bloquear»; a −6000,2500: 17,4 s. **Dos jugadores a la vez** (±7000): 26,4 s y 26,6 s, **0 «Can't keep up»** | ✅ |
| 10 | Portal del Nether (no cubierto por el aplazamiento) | El jugador cambió de dimensión; 0 «Can't keep up» nuevos (destino ya generado; **no** se probó un portal a terreno nuevo del Nether) | ⚠ parcial |
| 11 | Nether y End: generar y visitar | Ambos se generan y recorren (capturas); marcadores colocados en ambos persisten tras reiniciar. **Primera entrada al End: tirón de ≈25 s** (End's Phantasm); ver `PROBLEMAS-CONOCIDOS.md` §3 | ⚠ |
| 12 | `/locate` de 8 estructuras peligrosas desde el spawn | Todas a ≥1 218 bloques (≥1 520 las guaridas de dragón); cada búsqueda bloquea 1–21 s el hilo principal | ⚠ P1 documentado |
| 13 | **Guardado, parada y reinicio** | `save-all flush` → `parar.py`: **parada limpia en 2 s** (código 0); reinicio: cofre con 7 diamantes, bloque, entidad con nombre y marcadores del Nether y el End **intactos**; inventario del jugador (5 pilas) conservado; segunda parada 32 s | ✅ |
| 14 | **Parada con una generación retenida para siempre** (peor caso), con el jar final 0.4.0 | `stop` termina en **62 s**, hace el guardado final; marcadores guardados antes y después del flush **4/4 y 4/4**, 0 errores de lectura. (Control Alpha 9: exp1/exp2 se colgaban >200 s) | ✅ |
| 15 | Respaldo en caliente (`respaldo.py`) | `save-off` + `save-all flush` confirmado, 1 551 archivos, 46 MB, **0 archivos distintos** al releer, `save-on` restaurado | ✅ |
| 16 | **Restauración en una instalación separada** | SHA-256 correcto; `verificar_mundo.py`: CORRECTO (level.dat, jugador, 3 dimensiones); el servidor restaurado arranca y los marcadores (cofre, bloque, entidad, Nether, End) están; parada limpia. Nota: algunos `.mca` copiados en caliente no tienen el último sector rellenado (Minecraft los lee igual) | ✅ |
| 17 | Desconexión y reconexión | Desconexión limpia (0 jugadores); al volver entra de nuevo (2.ª entrada) con la espada de hierro en el inventario | ✅ |
| 18 | Un jugador (servidor integrado) con el mundo restaurado | Copia del mundo restaurado abierta con `--quickPlaySingleplayer`: el servidor integrado arranca, el área de aparición se prepara en 1,6 s, **Cauces «ACTIVA»** y 49 tablas de botín cargadas, 1 «Can't keep up», 0 líneas del vigía; el planificador de cuencas trabaja (74 pendientes). (El mensaje «joined the game» no aparece en el registro del cliente en un jugador; se comprobó el apretón de manos de FancyMenu del jugador.) No se jugó con ese mundo. | ✅ (carga) |
| 19 | Capturas reales del juego | 5 capturas reales en `capturas/` (menú, End, un bosque, inventario con la guía); **calidad limitada** por el cliente de software (sin sombras, distancia 8). 7 capturas de paisaje: solo se conserva la mejor; las demás eran ríos/océano sin interés o mal encuadradas | — |

## Lo que NO se pudo comprobar (no se declara superado)
- **Combate y magia con clics reales:** se intentó con entrada sintética (XTest) en Xvfb sin gestor de ventanas; el puntero no queda capturado y la cámara se mueve con cada evento, así que no se logró apuntar de forma fiable (daño medido = 0, atribuible al método, no al juego). **Queda como prueba manual obligatoria** (protocolo). Sí se comprobó por datos: el objeto de varita/espada se entrega y se conserva, Spell Engine carga con las cuatro clases y la receta de la mesa de vinculación existe.
- **Reaparición tras morir, Waystones, Alma, jefes, dungeons en profundidad, FPS:** no probados (la reaparición falló al expulsar el servidor al cliente de prueba por `allow-flight=false`).
- **Multijugador real entre personas**; **dos bots no son un playtest**.
- **Compatibilidad con mundos de Alphas anteriores**; **Windows/macOS**; **importación en la app de CurseForge** (la hará el usuario; el 0.9.0-alfa.2 ya importó y arrancó en Windows).
- **Rendimiento a largo plazo** (soak de horas) y con más de 2 jugadores.

## Protocolo manual de aceptación (tú y Renas; ≈40 min)
1. Importar el ZIP en la app de CurseForge (Windows), 6 GB. Menú: ¿logotipo y «{{VERSION_VISIBLE}}»? Sin pantalla roja. Mundo **nuevo**.
2. **Primeros 10 min:** ¿hay libro de bienvenida? ¿Algún monstruo imposible cerca del inicio? ¿FPS aceptables (F3)?
3. **Combate:** espada de hierro contra un zombi (¿animación y daño?), rodar (tecla en *Controles*); **magia:** fabricar/conseguir varita arcana (`/give @s wizards:wand_arcane`) y lanzar; una de cada clase (`staff_fire`, un arco, `paladins:acolyte_wand`, una daga).
4. **Exploración:** teletransportarse (`/tp`) a 5 000 bloques; ver ríos y montañas; abrir un cofre de mazmorra: ¿botín razonable?
5. **Multijugador (servidor del paquete):** los dos exploráis zonas distintas; viaje conjunto a terreno nuevo; matar una élite o un jefe pequeño juntos; Waystone de aldea (activar y viajar); desconectar y reconectar; **morir y reaparecer**; ir al Nether y al End (anotar tirones).
6. `parar.py` con ambos desconectados; reabrir; comprobar construcciones e inventarios; `respaldo.py` + restaurar en otra carpeta.
7. Anotar: cualquier crash, texturas rotas, tirón >5 s, objeto absurdo.

## Veredicto
Ver el informe final y `publicacion/PASOS-PUBLICACION.md`. Resumen: **BETA 1 PREPARADA, pero la publicación está bloqueada por pasos humanos obligatorios** (publicar Cauces como proyecto de CurseForge, exportar el zip desde la aplicación, playtest manual/multijugador). No hay un bloqueante técnico de pérdida de datos.

## Beta 1.1: congelación del mundo (P0) y Cauces 0.4.1

Laboratorio con el servidor de Beta 1 (mismos mods y configuración), `view-distance=32`, mundo nuevo por prueba con la misma
semilla. Resultados y scripts en `pruebas/p0/`. Sin baterías largas: cada prueba dura de 3 a 8 minutos.

| # | Prueba | Resultado | Veredicto |
|---|---|---|---|
| P1 | Causa (cliente real volando en creativo, mod de diagnóstico) | Un solo chunk nuevo desencadena la conversión lava→obsidiana en cadena y el hilo principal genera de forma síncrona hasta 25 chunks seguidos (31 s sin tick). Mecánica de Minecraft; Streams encarece cada chunk | causa demostrada |
| P2 | Vuelo de 240 s, generación natural, 0.4.0 frente a 0.4.1 | Pausas > 2 s: 8 (54 s, máx. 12,7 s) → **4 (10 s, máx. 2,8 s)**; «Can't keep up» 6 → 3; lava bajo agua sin convertir alrededor del jugador 422 → **394** (Minecraft también deja algunas); 11 226 cargas síncronas evitadas, 1 008 reanudadas, **0 perdidas** | ✅ |
| P3 | Cadena de lava de **jugador/comando** (`/setblock`) que cruza a chunks descargados | 0.4.0 y 0.4.1: **128/128** convertidas (Minecraft carga los chunks). La versión global de desarrollo (dev2) dejaba **80 sin convertir para siempre** → descartada | ✅ alcance correcto |
| P4 | Cadena de **terreno nuevo** que llega al borde de lo cargado, y carga posterior | 48 convertidas y corte en el borde → al cargar 1003–1006: 112 (nuevo corte en el siguiente borde) → al cargar 1007: **128/128**; 3 reanudaciones, 0 perdidas | ✅ se reanuda |
| P5 | Redstone hacia un chunk descargado; agua, pistón pegajoso (empuja y retrae) y granja de observador (trigo que crece → bombilla de cobre) cruzando un borde de chunk | **Idéntico en 0.4.0 y 0.4.1**; Cauces registra 0 cortes durante estas pruebas | ✅ |
| P6 | `save-all flush`, parada y reapertura | flush 1 s, parada 2 s, reapertura con los mismos bloques (filas de obsidiana, pistón, agua, lámpara) | ✅ |
| P7 | Un jugador (cliente real): mundo A → guardar y salir → mundo B en la misma sesión | Vigía: 1 hilo en A, 0 en el título, **1 en B** (0.4.0: ninguno en B). Planificador: anillo nuevo en B alrededor de su punto de aparición. Guardado de ambos mundos; 0 errores de Cauces | ✅ |
| P8 | Jar reproducible | Mismo SHA-256 compilando con `TZ=UTC` y `TZ=America/Costa_Rica` | ✅ |
| P9 | Candidata ensamblada | Jar de `overrides/mods` del zip = jar probado (SHA-256 915c7625…); P3–P6 repetidas con ese jar y su `purg4tory_cauces.properties`: todo igual, 0 errores; reensamblar da zips idénticos byte a byte | ✅ |

**No comprobado:** partida real en Windows con GPU y distancia 32 (pendiente del equipo, `PRUEBA-WINDOWS.md`), multijugador real con la corrección, partidas largas.
