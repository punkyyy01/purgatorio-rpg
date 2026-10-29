# {{NOMBRE}} {{VERSION_VISIBLE}} — cambios desde la última Alpha pública (Alpha 5)

*Versión técnica `{{VERSION}}` · canal {{CANAL}} · procede de la candidata interna `{{CANDIDATA}}` (se conserva intacta como punto de retorno). Las «Alphas 6–9» fueron etapas internas de desarrollo y **nunca se publicaron**: este registro las resume porque, para quien venga de la Alpha 5, forman parte de lo que cambia.*

## 0.7.0 Beta 2 (2026-10-28) — fin de las congelaciones del mundo al explorar
- **PURG4TORY Cauces 0.4.1 → 0.5.0.** La corrección de la Beta 1.1 solo cubría las cadenas de lava del terreno nuevo; el
  mundo seguía congelándose al explorar rápido. Causa de fondo: el servidor se quedaba esperando a que se generase un
  chunk por una simple colisión, un escaneo de bloques o una comprobación de spawn. Con 0.5.0 nunca espera: en el borde de
  lo generado notarás un tope de unos segundos mientras aparece el terreno, pero el mundo sigue funcionando (drops, daño,
  criaturas). Medido en vuelo de 15 min a distancia 32: Beta 1.1 tuvo 48 pausas de 2 s o más (máx. 79 s); 0.7.0 Beta 2, ninguna.
- Cauces pasa a descargarse como proyecto de CurseForge (antes iba dentro del zip). Opciones nuevas en
  `config/purg4tory_cauces.properties` (todas activadas; `false` = Minecraft).
- Nombre de versión unificado: CurseForge, archivo, menú del juego y libro de bienvenida dicen «0.7.0 Beta 2».
- El resto del pack no cambia respecto a la versión publicada «0.7.0-beta.1» (= 0.6.0 Beta 1.1).

## Beta 1.1 (candidata, 2026-10-24) — corrección de la congelación del mundo
- **P0 corregido: el mundo dejaba de responder al explorar** (sobre todo en un jugador con distancia de renderizado alta).
  Al procesar un chunk recién generado, una capa de lava en contacto con agua se convertía en obsidiana en cadena y obligaba
  al servidor a generar chunks nuevos de forma síncrona, uno tras otro (decenas de segundos sin procesar nada; en un jugador,
  sin límite). **PURG4TORY Cauces 0.4.1** detiene esa cadena en el borde de lo cargado y la **reanuda** cuando esos chunks se
  cargan. Solo actúa sobre el terreno recién generado: redstone, agua, lava, pistones, observadores y granjas funcionan como
  en Minecraft (comprobado). Medido en vuelo a distancia 32: pausas del servidor de más de 2 s, 54 s → 10 s (máx. 12,7 s → 2,8 s).
- **Vigía de Cauces en un jugador:** ahora vigila todos los mundos que abras en la sesión (antes solo el primero) y guarda un
  volcado `purg4tory-congelacion-<fecha>.txt` si el servidor se congela. El planificador ya no reutiliza datos del mundo anterior.
- Opción nueva `cadenaSinCargar` en `config/purg4tory_cauces.properties` (`true`; `false` = comportamiento de Minecraft).
- Sin otros cambios: mismos 153 mods y configuraciones que Beta 1.

## ⚠️ Importante
- **Mundo nuevo obligatorio** (generación del mundo distinta; ver `COMPATIBILIDAD.md`).
- Es una Beta: lee `PROBLEMAS-CONOCIDOS.md`; haz respaldos.

## Novedades de jugabilidad (acumuladas desde Alpha 5)
- **Ríos de verdad:** Streams Reflowing 2.15.2 (arroyos, ríos, lagos y cascadas con corriente).
- **Biodiversidad ampliada:** +18 mods de generación (Nature's Spirit, Regions Unexplored, [Let's Do] BloomingNature, Biomes O' Plenty, Promenade, Nyctophobia, Ecologics, Oh The Biomes We've Gone, Oh The Trees You'll Grow, Incendium, Hybrid Aquatic, End's Phantasm y bibliotecas): de ≈60 a **≈166 de diversidad efectiva** (≈307 biomas de tierra generados), Nether de 24 biomas, End de 8 con las nuevas zonas de End's Phantasm. Tectonic mantiene sus cordilleras monumentales.
- **Fauna:** 121 reglas de reposición (In Control), 98 % de la tierra generada cubierta (antes 84 %).
- **Menú principal** con la identidad de PURG4TORY y **la versión visible correcta (`{{VERSION_VISIBLE}}`)** — antes mostraba «0.5.0-alfa.2». La versión sale ahora de una única fuente (`pack.toml`).
- **Libro de bienvenida opcional** (5 páginas, una sola vez; sin quests ni tutoriales).

## Equilibrio (nuevo en Beta 1)
- **Botín de mazmorras recortado en 49 cofres** (When Dungeons Arise, Seven Seas, YUNG's, Deeper and Darker, Alex's Caves): antes entregaban 2–4 objetos de alto nivel por cofre (armadura de netherita incluida) en estructuras comunes; ahora ≈0,8 en cofres normales y ≈1,3 en cofres de tesoro/jefe, y sin equipo de netherita fuera de los de tesoro. Detalle y mediciones: `AUDITORIA-SISTEMAS.md` §4.

## Estabilidad y rendimiento
- **PURG4TORY Cauces 0.4.1** (mod propio, MIT; 0.4.0 en Beta 1): prepara las cuencas de ríos por delante de los jugadores; **aplaza los teletransportes a terreno nuevo** (`/tp` y mods que usan `teleportTo`; medido: 166 s de bloqueo → ≤ 1 s); **acota el guardado y la parada** (`save-all flush` ≤ 30 s, parada ≤ 60 s) para que el servidor no se cuelgue con chunks retenidos; vigía de diagnóstico. Análisis completo en `SEGURIDAD-GUARDADO.md`.
- Herramientas de administración nuevas en el paquete de servidor: `parar.py` (parada segura verificada), `respaldo.py` (respaldo consistente con verificación), `verificar_mundo.py`, `rcon.py`.
- El instalador del servidor descarga NeoForge (`--instalar-neoforge`), verifica SHA-1, avisa de jars obsoletos/duplicados, hace copia de `config/` antes de actualizar y aparta (sin borrar) datapacks propios que ya no existen.

## Correcciones
- **Every Compat 2.11.55** (corrige el error «Every Compat encountered an Error» al abrir el menú con Regions Unexplored 0.6.3).
- **Texturas rotas de Every Compat con Promenade:** 16 errores por arranque → 0 (se excluyen de Every Compat las 4 maderas y las hojas de arce de Promenade).
- **Recetas rotas Create ↔ Galosphere** (Galosphere 1.5.5 pasó de plata a paladio): desactivadas; 0 errores de receta al arrancar.

## Sin cambios (deliberadamente)
Minecraft 1.21.1, NeoForge 21.1.259, los **153** archivos de mods y sus versiones, Tectonic 3.0.28, Terralith 2.6.2, Streams Reflowing 2.15.2 (LOW, cuencas de 768, concurrencia 1). Hay 10 actualizaciones de mods disponibles que no se aplicaron por no corregir ningún problema detectado.

## Fuera de la Beta
Mecánica de **Alma**, quests, nuevas dimensiones, más mods.
