# Instalación del cliente — {{NOMBRE}} {{VERSION_VISIBLE}}

## Requisitos
| | |
|---|---|
| Minecraft | **1.21.1** con **NeoForge 21.1.259** (el launcher de CurseForge lo instala solo) |
| Java | **21** (la aplicación de CurseForge descarga el runtime correcto; no instales otro) |
| Memoria asignada | **6 GB** (el pack lo recomienda: 6144 MB). Tu PC debe tener al menos 12 GB de RAM libres para el sistema y el juego. **No asignes más de 8 GB**: no acelera nada y empeora las pausas de Java |
| Disco | ≈ 3 GB para el perfil (los 153 archivos de mods pesan ≈ 714 MB) más tus mundos |
| Gráficos | GPU con OpenGL 3.3 o superior (Sodium). |
| Internet | Solo para la descarga inicial desde CurseForge |

## Instalar desde CurseForge (cuando esté publicada)
Busca **PURG4TORY: Souls Grimore** en la aplicación de CurseForge → *Instalar*. El launcher crea el perfil, descarga los 153 archivos y NeoForge.

## Instalar desde el ZIP
1. Aplicación de CurseForge → *Minecraft* → *Crear perfil personalizado* → **Importar** → elige `PURG4TORY-Souls-Grimore-{{VERSION}}.zip`.
2. Al importar, la aplicación avisará de **archivos externos** (`reglas.mcfunction`, `crittersandcompanions-common.json5`): son configuraciones propias de este pack, **es seguro continuar**.
3. En los ajustes del perfil comprueba la memoria (6 GB) y pulsa *Jugar*.
4. **Primera partida:** crea un **mundo nuevo** (ver `COMPATIBILIDAD.md`). Recomendado: distancia de renderizado 12, simulación 6. Si el PC es modesto, 8–10.

## Comprobación rápida de que está bien instalado
En el menú principal debe verse el logotipo de **PURG4TORY: Souls Grimore** y, arriba a la izquierda, **«{{VERSION_VISIBLE}}»** con la versión de Minecraft y NeoForge. Si aparece una pantalla roja «Every Compat encountered an Error», alguna versión no coincide: cierra el juego y reimporta el ZIP en un perfil nuevo.

## Jugar en un servidor
El servidor debe ser de **la misma versión** del pack (cliente y servidor deben coincidir en todos los mods, sobre todo Every Compat). Para montar uno: `SERVIDOR.md`.

## Qué hacer al empezar
Dentro del mundo recibirás un **libro opcional** «Guía de PURG4TORY» (puedes tirarlo). Lo básico: mapa Xaero (minimapa), Jade (qué estás mirando), EMI (recetas: tecla **R** sobre un objeto; usos: **U**), clases y magia por equipo (`README.md`).

## Problemas frecuentes
- *Se queda en la barra de carga mucho tiempo:* es normal 1–2 min con ~150 mods. Si pasan 10 min, cierra y mira `logs/latest.log` del perfil.
- *Texturas rotas (morado/negro) en un bloque:* anota qué bloque es y mira `PROBLEMAS-CONOCIDOS.md`.
- *Un ladrillo/madera de Promenade «desaparece» de un menú de creativo:* en {{VERSION_VISIBLE}} Every Compat ya no genera variantes de las maderas de Promenade (sus texturas no existen); Promenade conserva sus propios bloques.
