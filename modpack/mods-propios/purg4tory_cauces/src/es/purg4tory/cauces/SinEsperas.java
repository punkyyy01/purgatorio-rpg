package es.purg4tory.cauces;

/**
 * El hilo principal del servidor no espera a la generación de chunks en las consultas «solo si está cargado».
 *
 * Problema (P0, un jugador, distancia 32): en Minecraft 1.21.1 un chunk está «cargado» (tiene nivel de ticket) mucho antes de
 * estar «listo» (generado y convertido en LevelChunk). Las consultas que solo quieren el chunk si ya existe
 * ({@code ServerChunkCache.getChunk(x, z, estado, false)}, que usan colisiones, Lithium, la IA, fluidos y muchos mods) esperan
 * igualmente a que termine su generación si el chunk está dentro de la distancia de visión. Con distancia 32 eso es un área
 * de 65×65 chunks; la generación es un buzón serie por dimensión (y Streams Reflowing la bloquea hasta 45 s por estructura),
 * así que una consulta así puede dejar el mundo parado decenas de segundos (medido: 31 s por una colisión del jugador).
 *
 * Cambio: en el hilo principal, esas consultas responden «no está» (null) si el chunk aún no está listo en ese estado,
 * que es lo que el propio contrato del método promete. {@code hasChunk} (Level.isLoaded/hasChunkAt) en el hilo principal
 * solo dice «sí» si el chunk está listo, para que los «si está cargado, léelo» no acaben en una espera.
 * Las peticiones que SÍ quieren cargar (cargar=true) no cambian aquí.
 */
public final class SinEsperas {
    public static volatile boolean consultas = true;   // getChunk(cargar=false)
    public static volatile boolean cargado = true;     // hasChunk
    public static volatile boolean movimiento = true;  // jugador solo entra en chunks con entorno 3×3 listo
    public static long evitadas, cargadoNo, movimientosFrenados;
    private SinEsperas() {}

    public static String estado() {
        return "consultas sin esperar: " + (consultas ? evitadas + " esperas evitadas" : "NO") + ", «cargado» = listo: " + (cargado ? cargadoNo + " respuestas no" : "NO")
            + ", movimiento a terreno listo: " + (movimiento ? movimientosFrenados + " frenados" : "NO");
    }
}
