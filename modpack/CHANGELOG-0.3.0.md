# Purgatorio RPG 0.3.0-alfa.4 (candidata para pruebas, no publicada)

Cambios respecto a 0.3.0-alfa.3:
- **Alex's Mobs:** las tres reglas de protección por fin tienen efecto. Este port (Alex's Mobs Continued 2.x) lee
  `config/amc.json`, no `alexsmobs-common.toml`, así que en las alfa anteriores se ignoraban:
  - los mapaches salvajes no sacan comida de los cofres;
  - los cuervos salvajes no estropean cultivos;
  - el cachalote enfadado no rompe bloques de madera ni lana.

  Los mapaches y los cuervos siguen comiendo, lavando objetos y volando en círculos como siempre. Los domesticados no
  cambian. El cachalote sigue rompiendo hielo y nenúfares, como la orca.
- **Construcción reproducible:** la configuración se genera desde las versiones exactas de los mods. Sin cambios de juego.

Cambios de 0.3.0-alfa.3 respecto a 0.3.0-alfa.2:
Cambios respecto a 0.3.0-alfa.2:
- Nuevo mod **More MobGriefing Options** (123 archivos): las criaturas hostiles (creepers, endermans, zombis contra
  puertas, ghasts, Alex's Caves, Cataclysm, Born in Chaos, Mowzie's...) ya no rompen bloques, también fuera de terreno
  reclamado. Siguen haciendo daño a los jugadores. Aldeanos, ovejas, zorros, piglins y demás animales funcionan como en
  vanilla (la regla `mobGriefing` sigue activada).
- Enderman Overhaul: los endermans no cogen bloques. Cataclysm: ningún jefe ignora la protección.
- Born in Chaos: el Skeleton Demoman ya no aparece (su explosión no se puede limitar sin romper bloques).
- Arranque: los mods se cargan de uno en uno (`fml.toml`, maxThreads = 1) para evitar un fallo intermitente entre
  Critters and Companions, Meadow, Mobs of Mythology y Architectury. Unos 3 s más de arranque.

Cambios de 0.3.0-alfa.2 respecto a 0.3.0-alfa:
Cambios respecto a la primera candidata 0.3.0-alfa:
- Alex's Caves: el pisotón del Atlatitan y del Luxtructosaurus ya no rompe bloques (antes rompía madera, piedra,
  ladrillo y cristal; resistencia máxima 10 -> 0).
- Alex's Mobs: el oso grizzly solo saquea nidos de abeja silvestres (no colmenas fabricadas) y el elefante solo come
  hojas (no balas de heno ni melones).

Minecraft 1.21.1 · NeoForge 21.1.259 · 122 archivos de CurseForge (antes 110).

## Criaturas nuevas, repartidas por entorno
- **Alex's Mobs** (port "Continued"): ~90 animales y monstruos ligados a su bioma, también en Nether y End.
- **Alex's Caves** (port "Continued"): seis biomas subterráneos raros con su fauna.
- **IceAndFire CE**: dragones y bestias míticas en guaridas a más de 1000 bloques del spawn.
- **Born in Chaos**: monstruos nocturnos solo en su entorno (pantano, jungla, bosque oscuro, taiga, nieve,
  montaña, badlands, ríos). Nada en llanuras, praderas, sabana ni desierto. Los cinco más duros solo a más de
  1500 bloques del spawn. Sin eventos por fecha (Halloween, Krampus).
- **Mobs of Mythology**: kobolds, dracos, basilisco, chupacabras (fuera de llanuras).
- **Infernal Expansion Redux**: cañón de piedra luminosa en el Nether con su fauna.
- Retirados de Naturalist los animales que Alex's Mobs ya trae (elefante, rinoceronte, komodo, tigre, oso
  pardo, aligátor, pez gota, bagre).

## Sin destrucción de bases ni inflación
- Dragones, cíclopes, serpientes marinas y el cachalote no rompen bloques; los mapaches no vacían cofres.
- Bomba nuclear de Alex's Caves: no rompe bloques y no tiene receta (provisional).
- Acero y escamas de dragón con valores de netherita; sin receta la armadura de metal oscuro, la darkwarblade y la
  espada fantasma; los caballeros del terror no sueltan su espada.

## Rendimiento
- **ServerCore**: consultas de bioma rápidas al hacer aparecer criaturas, IA a ritmo reducido para criaturas a
  más de 32 bloques de cualquier jugador (dragones y jefes excluidos) y tope menor de Glares.
  En laboratorio: prueba larga de 11 TPS (91 ms/tick) a 20 TPS estables (31 ms/tick).

## Conocido / pendiente
- Quedan fuera de la protección, en sus propias zonas: el Magnetron (cuevas magnéticas) puede llevarse bloques
  metálicos cercanos para formar su cuerpo y los jefes de Bosses of Mass Destruction pueden romper bloques en sus
  arenas. Los objetos explosivos que usan los jugadores siguen funcionando.
- La protección se aplica a mundos que usen esta configuración; un mundo de pruebas anterior necesita copiar
  `config/moremobgriefingoptions-server.toml` y reiniciar.
- Galosphere no genera sus biomas con Terralith (desde 0.1.0); se tratará en otro hito.
- Tres biomas de Alex's Caves salen algo menos con Tectonic (se mantienen así de momento).
