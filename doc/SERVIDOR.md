# Servidor de {{NOMBRE}} {{VERSION_VISIBLE}} — instalación y administración

Minecraft 1.21.1 · NeoForge 21.1.259 · **Java 21** · **Linux (probado)**. Los scripts son Python 3.11+ sin dependencias y deberían funcionar igual en Windows, pero **no se ha probado**; los `.sh` son solo para Linux.
Memoria: `-Xms6G -Xmx6G` (G1 por defecto de Java 21, sin más opciones). Ver `RENDIMIENTO.md` para `server.properties`.

Este paquete **no contiene jars de terceros** (ver `LICENCIAS-Y-CREDITOS.md`): trae la lista exacta de mods con SHA-1 (`mods-servidor.json`), un instalador que los baja del CDN de CurseForge y los verifica, las configuraciones y **PURG4TORY Cauces** (código propio, MIT).

## 1. Instalación desde cero
```sh
mkdir mi-servidor && cd mi-servidor
unzip ../PURG4TORY-servidor-{{VERSION}}.zip && cd PURG4TORY-servidor-{{VERSION}}
python3 instalar_servidor.py ~/servidor --instalar-neoforge
```
- `--instalar-neoforge` descarga el instalador oficial de NeoForge 21.1.259 de `maven.neoforged.net`, comprueba su SHA-1 contra el publicado y ejecuta `--installServer` (necesita `java` 21 en el PATH). Sin esa opción, instala NeoForge tú.
- El instalador baja cada mod, **comprueba su SHA-1**, copia `config/`, `defaultconfigs/` y el jar de Cauces, y revisa `mods/`: avisa de jars **OBSOLETOS** (mismo modId que uno de la lista pero otro archivo), **DESCONOCIDOS** (otros mods; no se tocan) y **DUPLICADOS**. **Nunca borra nada**: con `--mover-obsoletos` los mueve a `mods-obsoletos/`.
- **Descarga manual (4 mods)**: Alex's Mobs Continued, Hybrid API [HAPI], ServerCore y Structory; sus autores **no permiten la distribución por terceros**. El instalador imprime el enlace exacto y el SHA-1 de cada archivo: bájalos de la página de CurseForge (botón «Download») y déjalos en `mods/`. Vuelve a ejecutar el instalador: los verifica. Hybrid API es obligatorio (lo necesita Hybrid Aquatic); sin los cuatro, el servidor no arranca o le faltan criaturas/estructuras. El instalador sale con código **4** mientras falten.
- Códigos de salida: 0 todo bien · 1 fallo de descarga · 3 obsoletos/duplicados · 4 faltan descargas manuales.

## 2. Primer arranque
1. `eula.txt` → `eula=true`.
2. `server.properties`: `view-distance=12`, `simulation-distance=6`, **`allow-flight=true`** (recomendado: con `false`, el servidor expulsa con «Flying is not enabled on this server» a quien «flota» sin estar en creativo; en las pruebas expulsó a un jugador que había sido teletransportado en el aire, y hechizos como *Levitate* de los paladines o élitros y mecanismos de Create lo harían más probable — no se probó con esos) y, para los scripts de administración `enable-rcon=true`, `rcon.port=25575`, `rcon.password=<clave larga>` (RCON **solo** en 127.0.0.1 o red privada; no lo abras a Internet).
3. `user_jvm_args.txt`: `-Xms6G -Xmx6G`. Mantén `config/fml.toml` con `maxThreads=1` (ya viene).
4. `./run.sh nogui`. El primer arranque tarda ~1 min; **el terreno nuevo cuesta más de generar** (ríos de Streams Reflowing y ~300 biomas): ver §5 (pregeneración).
5. **Mundo nuevo obligatorio** para disfrutar la generación actual; ver `COMPATIBILIDAD.md`.

## 3. Parada segura (hazlo siempre así)
```sh
RCON_PASSWORD=<clave> python3 parar.py ~/servidor --pid <pid_de_java> [--aviso 30] [--espera 120]
```
`parar.py` avisa a los jugadores, ejecuta `save-all flush` y **solo si el servidor responde «Saved the game»** ejecuta `stop`; espera hasta `--espera` s a que el proceso termine. Códigos: **0** parado limpio · **2** el guardado no se confirmó (**no** pares a la fuerza; mira `logs/latest.log` y repite) · **3** guardado confirmado pero el proceso no termina.

**Si el servidor no termina de apagarse** (código 3): (1) espera 1–2 min más (con Streams, la parada acota a 60 s las generaciones en curso y luego hace el guardado final); (2) opcional: `jstack <pid> > parada-colgada.txt` para diagnóstico; (3) `kill <pid>` (SIGTERM) y, si a los 30 s sigue, `kill -9 <pid>`. Con el guardado del paso previo confirmado y sin jugadores, no se pierde nada; (4) haz un respaldo (§4) y verifica el mundo antes de volver a arrancar. **No hagas del cierre forzado tu procedimiento normal.** Ver `SEGURIDAD-GUARDADO.md`.

## 4. Respaldos y recuperación
Todo con la biblioteca estándar de Python; no hace falta instalar nada.
- **Respaldo consistente (servidor en marcha):** `RCON_PASSWORD=… python3 respaldo.py ~/servidor ~/respaldos` → `save-off` + `save-all flush` (confirmado) → copia del mundo → `save-on` **siempre** → releé el `.tar.gz` y compara cada archivo con su SHA-256. Genera `mundo-AAAAMMDD-HHMMSS.tar.gz`, `.sha256` y `.json` (inventario + lista de mods y versiones). Incluye el mundo completo (Overworld, Nether, End, `playerdata`, `advancements`, `stats`, datapacks del mundo, **`streamsreflowing/`**), `config/`, `server.properties` y listas de ops/baneos. No incluye `mods/` (se reconstruyen con el instalador; el `.json` guarda cuáles eran).
- **Nunca copies a mano la carpeta del mundo con el servidor activo** (copia inconsistente). Con el servidor parado, usa `respaldo.py … --parado`.
- **Antes de actualizar mods o el paquete:** respaldo + conserva el `.zip` del servidor de la versión anterior. El instalador ya guarda `respaldos-config/` y aparta los datapacks propios que desaparecen a `config-obsoleta/`.
- **Comprobar un respaldo sin arrancar nada:** `python3 verificar_mundo.py <carpeta_del_mundo>` (lee `level.dat`, cada `playerdata/*.dat` y muestras de chunks de todas las dimensiones; devuelve `CORRECTO` o los fallos).
- **Restaurar en una instalación separada:** (1) `sha256sum -c mundo-….tar.gz.sha256`; (2) `mkdir restaurado && tar xzf mundo-….tar.gz -C restaurado`; (3) instala un servidor con el instalador en otra carpeta y copia dentro `restaurado/<mundo>/`, `server.properties` y `config/` (cambia los puertos); (4) `verificar_mundo.py`; (5) arráncalo y comprueba **lo que os importa**: vuestras construcciones, un cofre con objetos, el inventario de un jugador al entrar, cada dimensión (Nether y End). Esa comprobación humana es la que cuenta.
- **Frecuencia recomendada:** un respaldo diario y otro antes de cualquier actualización; conserva al menos 7. Copia los respaldos **fuera** de la máquina del servidor.

## 5. Rendimiento y pregeneración (opcional)
Medido (ver `RENDIMIENTO.md`): generar terreno es ≈85 % de la CPU del servidor al explorar, y los biomas ampliados cuestan ≈+40 % frente a la 0.8.0. **PURG4TORY Cauces** prepara las cuencas de ríos alrededor del punto de aparición cuando no hay jugadores (radio 3072) y por delante de cada jugador cuando exploran.
Pregenerar es **opcional** y solo para servidores con borde: `./pregenerar.sh <radio>` imprime los comandos (`worldborder` + `/neoforge generate`); ≈19 chunks/s en el laboratorio (radio 3000 ≈ 2 h). Hazlo fuera de horas de juego. Quien juega en su mundo local no necesita nada de esto.

## 6. Administración de Cauces (permiso 3)
`/cauces estado` · `/cauces colas` · `/cauces pausa|reanudar` · `/cauces planificar <radio>` · `/cauces_tp` (teletransportes aplazados, descargas diferidas y recortes de botín). Configuración: `config/purg4tory_cauces.properties`. **No cambies `-Dstreamsreflowing.concurrentplates`** (se deja en 1). Los límites de botín de mazmorras están en `config/purg4tory_botin.json` (se pueden quitar tablas; se regenera con `herramientas/equilibrar_botin.py`).

## 7. Reglas del mundo que ya vienen configuradas
Sin raids ni patrullas (`disableRaids`, `doPatrolSpawning`), sin eventos por fecha de Born in Chaos, criaturas hostiles que **no rompen bloques** (More MobGriefing Options), sin Waystones salvajes (solo aldeas y las fabricadas), élites (Champions) ≈2 % y solo de nivel ≤3, jefes lejos del inicio. Protección de bases: Open Parties and Claims (los jugadores reclaman chunks; configuración propia del mod).

## 8. Actualizar desde otra versión
1. Respaldo (§4). 2. Para el servidor y descomprime el paquete nuevo. 3. `instalar_servidor.py <carpeta> --mover-obsoletos`. 4. Revisa `COMPATIBILIDAD.md` (¿mundo nuevo? ¿bloques que desaparecen?). 5. Arranca y mira `logs/latest.log` (`PURG4TORY Cauces`, errores). **Cliente y servidor deben tener las mismas versiones** (Every Compat lo verifica al conectar).
