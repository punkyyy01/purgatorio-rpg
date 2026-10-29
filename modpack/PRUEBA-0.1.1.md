# Prueba manual de Purgatorio RPG 0.1.1-alfa

Importa el zip como **perfil nuevo** (no actualices el de 0.1.0). Crea un **mundo nuevo**.

1. **Aviso de CurseForge.** Apunta qué archivos marca. Deberían ser solo los overrides del README, sección 1.
   Elige «todos los archivos».
2. **Arranque.** Llega al menú y crea el mundo. Si falla, guarda `logs/latest.log` y `crash-reports/`.
3. **Reglas.** `/gamerule disableRaids` debe devolver `true`.
4. **Waystones.** Explora unos 1000 bloques: no debe haber waystones sueltas. Entra en una aldea, vanilla o de CTOV,
   y busca su waystone.
   Comprueba que `config/waystones-common.toml` del perfil conserva `chunksBetweenWildWaystones = 0`.
5. **Mochilas.**
   - En EMI, busca «backpack»: deben salir las de cuero, cobre, hierro, oro, diamante y netherita.
   - No deben tener receta: inception, «auto smelting», «feeding» ni la pila omega.
6. **Hostiles.**
   - De noche, en desierto, nieve y pantano: endermen y creepers con aspecto del bioma; mineros no-muertos bajo tierra.
   - En el Nether: endermen de carmesí y de valle de almas, y Burned en los yermos.
   - Si no aparece ninguno, apunta el bioma (F3) y la hora.
7. **Lootr.**
   - Busca una aldea CTOV con cofre doble: deben verse dos cofres Lootr y cada uno debe abrirse por separado.
   - Si ves un cofre con textura vanilla, rómpelo **sin abrirlo** y apunta si suelta botín. Es el caso que no se ha
     podido comprobar.
8. **Rendimiento.** Apunta los FPS habituales y cualquier tirón al generar terreno.
