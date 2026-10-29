# PURG4TORY Cauces 0.5.0

Mod auxiliar de servidor (también actúa en el servidor integrado de un jugador) para NeoForge 1.21.1. Licencia MIT.

**Novedad de 0.5.0: el hilo principal del servidor no se queda esperando a la generación de chunks** (P0, congelación del
mundo al explorar: ver `docs/auditoria-p0/INFORME-P0-CONGELACION-TICKS.md`). Opciones nuevas en
`config/purg4tory_cauces.properties`, todas activadas por defecto y con `false` = comportamiento de Minecraft:
`consultasSinEsperar`, `cargadoEsListo`, `movimientoAListo`, `cadenasGlobales`, `spawnsSinEsperar`.
Al parar el servidor se escribe en el registro una línea `al parar: …` con los contadores de cada parte.

Compilar: `./construir.sh` (javac contra las librerías de un servidor NeoForge 21.1.259 listadas en `classpath.txt`, más
MixinExtras 0.5.5, que está dentro del jar `neoforge-21.1.259-universal.jar` en `META-INF/jarjar/`; ruta en la variable
`MIXINEXTRAS`). `classpath.ejemplo.txt` es el del laboratorio. El jar sale reproducible (fechas fijas).

---

## Historia (README de 0.1.0, Alpha 7)

# PURG4TORY Cauces 0.1.0 (experimental, Alpha 7)

Mod auxiliar de servidor para NeoForge 1.21.1 que **prepara de antemano las cuencas de Streams Reflowing** (las
«placas» de ~768×768 bloques en las que Streams planifica sus ríos) sin generar chunks. Cuando un jugador llega a
terreno nuevo, la cuenca ya está calculada y el chunk solo paga el tallado (+7–11 % de CPU frente a no tener Streams,
medido en Alpha 6), en lugar de esperar a que se calcule (4,8× de CPU en Alpha 6).

No modifica ni redistribuye Streams Reflowing (licencia All Rights Reserved). No usa mixins ni reflexión: llama a
métodos públicos de la 2.15.2 (lista completa en `PuenteSR.java`). Con otra versión de Streams se desactiva solo,
salvo `permitirOtraVersionSR=true`. Si Streams no está instalado, no hace nada. Los clientes no lo necesitan.

## Qué hace

- **Sin jugadores**: recorre un anillo de cuencas alrededor del punto de aparición, de dentro hacia fuera
  (`radioSinJugadores`, por defecto 3072 bloques), y pide cada una a Streams por la misma vía que usa su generación de
  chunks (`RiverEngine.whenPlatesReady`).
- **Con jugadores**: pide la siguiente cuenca no preparada en la dirección en que se mueve cada jugador (a 0,5, 1 y
  1,5 cuencas por delante). El anillo se detiene salvo `anilloConJugadores=true`.
- **Una petición a la vez**, y solo si Streams no está construyendo nada, el tick medio está por debajo de `msptMaximo`
  y la CPU de toda la máquina por debajo de `cargaMaquinaMaxima`. Tras cada cuenca espera `pausaRelativa` veces lo
  que tardó (1,0 = trabaja como mucho la mitad del tiempo). Una cuenca ya pedida no se puede cancelar: el retraso máximo
  que puede causar a un jugador es una cuenca (0,5–6 s medidos a LOW).
- **Persistencia**: Streams guarda cada cuenca en `<mundo>/streamsreflowing/minecraft_overworld/r.<cx>.<cz>.srn`. El mod
  salta las que existen, así que tras un reinicio sigue donde lo dejó. Las cuencas guardadas se conservan aunque cambie
  la configuración de Streams (Streams avisa y mantiene las existentes).

## Comandos (permiso 3)

`/cauces estado` · `/cauces planificar <radio>` (rehace el anillo y reanuda) · `/cauces pausa` · `/cauces reanudar`

## Configuración

`config/purg4tory_cauces.properties` (se crea al primer arranque, comentada).

## Compilar

Sin Gradle: `javac` contra las librerías del servidor de laboratorio y el jar de Streams (solo para compilar; no se
incluye nada de Streams en el jar):

```sh
javac --release 21 -d build/cls -cp "$(cat classpath.txt)" src/es/purg4tory/cauces/*.java
cp -r res/META-INF build/cls/ && (cd build/cls && jar --create --file ../purg4tory_cauces-0.1.0.jar .)
```

## Límites conocidos

- Depende de métodos públicos pero no documentados de Streams: cada versión nueva de Streams exige comprobarlo.
- El orden en que se calculan las cuencas puede cambiar el sentido de un río en la frontera entre dos cuencas
  (`riverSeamAgreement` de Streams: «depende de qué lado se exploró antes»). Preparar en anillo hace ese orden
  determinista; explorar sin el mod lo deja en manos de los jugadores. No crea discontinuidades.
- No acelera el cálculo de una cuenca: lo adelanta. Explorar más allá del anillo preparado sigue costando lo mismo.
