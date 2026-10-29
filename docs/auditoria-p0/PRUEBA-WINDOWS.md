# Prueba en los PCs reales (Windows, un jugador): Cauces 0.5.0

Es la validación que falta y no se puede hacer en el laboratorio (allí no hay GPU). Lleva unos 30 min por PC; no hace falta
más. **Hazla sobre una copia de la instancia y no toques la original.**

## Preparación (5 min)

1. En la app de CurseForge, crea una copia de la instancia de la Beta 1 (clic derecho → «Abrir carpeta» para verla).
2. En `mods\` de la copia, cambia `purg4tory_cauces-0.4.0.jar` por `purg4tory_cauces-0.5.0.jar`
   (sha256 `83b00079624a17785f24d311eb515bd62c2b82e76e06c40b513b94f7f5b6d8ff`).
3. No hace falta tocar `config\purg4tory_cauces.properties`: las opciones nuevas se activan solas.

## Partida (25 min, mundo nuevo)

1. Crea un mundo nuevo, en creativo, con distancia de renderizado 32.
2. Vuela en línea recta con esprint durante **15 min** (el mismo escenario que con 0.4.0 congelaba). Es normal notar un tope en
   el borde de lo generado que dura unos segundos; lo que **no** debe pasar es que dejen de romperse bloques, de caer drops o
   de recibir daño las criaturas.
3. Haz **5 `/tp` lejanos** (por ejemplo `/tp @s 20000 200 0`, luego 40000…). Debe aparecer «Preparando el destino…» y
   llevarte a los pocos segundos, sin congelarse.
4. Juega 5 min normal (romper bloques, pelear, abrir cofres).
5. Sal con «Guardar y salir» y cierra el juego.

## Qué enviar

De `logs\latest.log` de la copia:

- la línea que contiene `al parar:` (contadores de Cauces);
- cuántas líneas `Can't keep up!` hay y sus milisegundos (`Running NNNNms behind`);
- si aparece `VIGÍA:` y cualquier `purg4tory-congelacion-*.txt` o `streamsreflowing-stall-*.txt` de la carpeta de la instancia.

**Si el mundo se congela** (más de 10 s sin drops ni daño), **no cierres el juego**. Ejecuta en PowerShell
`capturar-congelacion.ps1 -Jdk <carpeta de un JDK 21> -Instancia <carpeta de la instancia>`. El script vuelca los hilos tres
veces mientras sigue congelado; envía la carpeta que genera junto con lo anterior.

Criterio: ninguna congelación de más de 2 s en partida (sin contar los primeros segundos al abrir el mundo) y
`Can't keep up!` como mucho aislado.
