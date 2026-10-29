# PURG4TORY: Souls Grimore 0.9.0-alfa.2 (candidata jugable, NO publicada)

## Cambios de alfa.1 a alfa.2 (corrección de arranque)
- **Every Compat 2.11.54 → 2.11.55** (archivo CurseForge 9219760 → 9263267). Es el único mod que cambia. Con Regions Unexplored 0.6.3 la 2.11.54
  fallaba al abrir el menú con «Every Compat encountered an Error» (`net/regions_unexplored/world/level/block/plant/tall/ShrubBlock`,
  clase que Regions Unexplored ya no tiene). La 2.11.55 corrige el módulo (#1343).
- **Efecto**: ahora Every Compat carga de verdad su módulo de Regions Unexplored y registra bloques nuevos (variantes de sus maderas en Handcrafted,
  Farmer's Delight, Storage Drawers, Rechiseled, etc.). Ver «Mundos existentes» en `PROBLEMAS-CONOCIDOS.md`.
- Instalador del servidor: revisa `mods/` y avisa de jars obsoletos (p. ej. Every Compat 2.11.54), desconocidos o duplicados; nunca borra.
- Las pruebas de integración pasan ahora siempre por la pantalla de título y revisan los errores de módulos opcionales (ver `PRUEBAS-0.9.0.md`).

## Contenido de la serie 0.9.0 (igual en alfa.1 y alfa.2; alfa.1 se conserva reproducible en `versiones/0.9.0-alfa.1/`)

Integra los hitos de biodiversidad (hito 2) y de rendimiento (Alpha 9). Requiere **mundo nuevo** (cambia la generación del mundo).

## Añadido: biodiversidad
- **18 mods nuevos** (12 de contenido + 6 bibliotecas), sin ningún mod de Blueprint:
  Nature's Spirit 2.3.1, Regions Unexplored 0.6.3, [Let's Do] BloomingNature 1.1.11, Biomes O' Plenty 21.1.0.14, Promenade 6.0.1,
  Nyctophobia 2.0.0, Ecologics 2.3.7, Oh The Biomes We've Gone 2.6.3, Oh The Trees You'll Grow 5.3.5, Incendium 5.4.4,
  Hybrid Aquatic 1.7.4, End's Phantasm 1.0.3; bibliotecas: CorgiLib, Hybrid API [HAPI], Kotlin for Forge, Biolith, TerraBlender, GlitchCore.
- Medido en el sondeo del servidor de integración (mismos parámetros que el hito 2): ≈ 500 biomas registrados, ≈ 307 biomas de tierra que aparecen,
  diversidad efectiva ≈ 166 (0.8.0: unas 60), Nether de 24 biomas, End de 8 biomas con las nuevas zonas de End's Phantasm
  (diversidad del End 3,5 → 5,7). Tectonic y sus paisajes monumentales no cambian (tierra por encima de Y 160: 11,1 %).
- Configuración de generación: `terrablender.toml`, `natures_spirit-common.toml`, `biomesoplenty/generation.toml` (pesos equilibrados del hito 1).
- **Fauna de In Control**: 121 reglas de reposición (antes 62). Cobertura de la tierra generada: 84 % → 98 %.

## Cambiado
- **PURG4TORY Cauces 0.3.0-exp1** (experimental, sustituye a 0.2.0): los teletransportes (`/tp` y mods que usan `ServerPlayer.teleportTo`)
  a terreno sin generar se aplazan con tickets en vez de bloquear el servidor (en la prueba: 166 s de bloqueo → ≤ 1 s). Opciones nuevas:
  `teletransportePrevio`, `esperaTeletransporteS`.
- `pack.toml`: versión 0.9.0-alfa.1.

## Sin cambios
- Tectonic 3.0.28, Terralith 2.6.2, Streams Reflowing 2.15.2 (LOW, cuencas de 768, concurrencia 1), Nullscape y el resto de la identidad.

## Excluidos a propósito
- Mods de Blueprint (Atmospheric, Autumnity, Windswept, Environmental, Upgrade Aquatic, Unusual End): la generación completa con ellos supera los
  600 s en la zona de prueba y no se ha validado la corrección.
- Mystic's Biomes (prohíbe la distribución por terceros), Traveler's Titles (sin probar en cliente), Polar's Exploration Additions, Nether Descent,
  Hearths, The Beyond, Astrological (no aportan o empeoran).
- Cauces 0.3.0-exp2 y -exp3.

## Avisos
- Problemas abiertos (parada con chunk retenido, portales, coste de CPU +40 %): ver `PROBLEMAS-CONOCIDOS.md`.
