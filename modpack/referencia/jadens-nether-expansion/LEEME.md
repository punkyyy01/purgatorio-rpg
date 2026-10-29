# Jaden's Nether Expansion: probado en el hito 0.2.0 y retirado

No se incluye en el candidato. Motivos medidos en el laboratorio (2.4.1 con Elysium API 2.0.1 y Lodestone 1.8.2):

- **Rompe los peces de lava de Tide en el Nether**: con JNE, 0 entidades de Tide en el Nether cargado (dos
  pruebas); sin JNE, 65 en las mismas coordenadas. No es su modificador de niebla (anularlo no cambia nada).
- Cambia la distribución de biomas del Nether (el valle de almas cambia de sitio con la misma semilla).
- Contenido a medio hacer: recetas que apuntan a objetos que no existen (`warphopper_fur`, `iron_scrap`,
  `igneous_reeds`); el propio autor dice que es "1/8" del mod.
- Sus criaturas naturales son hostiles del valle de almas (Apparition y Vessel con peso 30), no fauna.
- Añade escopetas (Shotgun-Fist, Pump-Charge Shotgun), cofres de brasero que se rellenan y opciones globales
  (pociones apilables, quitar Soul Speed) que había que desactivar.

Aquí quedan los ajustes que se usaron en la prueba, por si se reconsidera: configs (`netherexp-*.toml`) y
las dos recetas de armas desactivadas (`recetas_desactivadas/`, iban en el datapack `purgatorio_reglas`).
