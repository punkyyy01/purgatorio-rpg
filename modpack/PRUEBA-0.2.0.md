# Comprobaciones en partida · Purgatorio RPG 0.2.0-alfa

Importad el zip como **perfil nuevo** (la 0.1.1 sigue intacta). Mundo nuevo, dificultad normal,
supervivencia. Anotad cada punto como OK / FALLO con una captura si falla.

## 1. Instalación
- [ ] El zip importa; el aviso de archivos externos, si sale, lista solo `crittersandcompanions-common.json5`
      y `reglas.mcfunction`. Elegid "todos los archivos".
- [ ] El juego arranca sin pantallas de error; FPS similares a 0.1.1 en el mismo sitio.

## 2. Paisaje (no debe haber cambiado)
- [ ] Montañas, valles y biomas con la misma escala que en 0.1.1 (Tectonic + Terralith).

## 3. Fauna (a pie, de día; quedarse ~10 min en cada sitio)
- [ ] Llanura: vacas, ovejas, cerdos o gallinas a la vista en 2 min; aparece algo nuevo en 10 min.
- [ ] Bosque: ciervos, jabalíes u ovejas; algún insecto de Critters, sin plaga de insectos.
- [ ] Sabana: cebras, jirafas, avestruces o elefantes (sin vacas: es intencionado).
- [ ] Río: nutrias, patos o koi.
- [ ] Nieve: zorros, conejos, shima enaga.
- [ ] Montaña: cabras, vacas lanudas o llamas.
- [ ] Ningún animal fuera de su hábitat; ningún animal apareciendo "de golpe" a la vista.
- [ ] Junto a una base iluminada no aparecen animales nuevos.

## 4. Peligro
- [ ] De noche, en una aldea al aire libre no aparecen monstruos (pueden llegar desde fuera).
- [ ] De noche en llanura hay monstruos, pero un peligro normal (no inmunidad ni saturación).
- [ ] Sin raids ni patrullas de saqueadores.
- [ ] Élites de Champions: solo en monstruos hostiles (zombis, esqueletos, arañas...). Si veis un animal,
      pez o murciélago con barra de élite, es FALLO. Con Jade apuntando a la élite se ve su nivel (máx. 3).
- [ ] Base reclamada con Open Parties and Claims (mapa de Xaero → reclamar): un creeper no rompe bloques.
- [ ] Si aparece el enemigo de "≈1024 corazones": captura de Jade (nombre y mod en azul) y
      `/data get entity @e[type=!player,sort=nearest,limit=1] id`.

## 5. Botín
- [ ] Un campamento subterráneo de Artifacts (cofre o mímico) es raro, pero existe.
- [ ] Cofres de estructuras con Lootr: cada jugador tiene su botín.
- [ ] Una élite de Champions suelta como mucho un objeto moderado (hierro, oro, libro, esmeralda; diamante raro).

## 6. Jefes de Cataclysm (en creativo vale)
- [ ] Tras matar un jefe aparece un Boss Respawner donde estaba.
- [ ] Usarlo con el ojo de ese jefe (p. ej. Mech Eye para el Harbinger) consume el ojo y vuelve a
      invocar al jefe; sin el ojo no hace nada.

## 7. Create
- [ ] Un molino de agua con una prensa o un mezclador funciona; no baja mucho el rendimiento.
- [ ] Las masas de trigo de Create y Farmer's Delight sirven en las recetas de la otra.
