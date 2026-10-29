package es.purg4tory.cauces;

/**
 * Comprobaciones de aparición de criaturas (spawns) del hilo principal sin esperar a la generación (ver SinEsperas).
 *
 * Los spawners (vanilla: gatos, patrullas…; mods como In Control) comprueban un punto con «¿está cargado?» y después
 * leen la caja entera de la criatura, que puede caer en el chunk vecino aún en generación: el hilo principal se quedaba
 * esperando (medido: 1 s tras un teletransporte; con la cola de generación llena, el mismo mecanismo da decenas de s).
 * Dentro de esas comprobaciones, pedir un chunk que no está listo hace fallar la comprobación («ahí aún no hay terreno»)
 * en vez de esperar. El corte se recoge en el propio método envuelto (mixin.SondeoSpawnMixin): no atraviesa código ajeno.
 */
public final class SondeoSpawn {
    public static volatile boolean activo = true;
    public static int profundidad;       // solo hilo principal
    /** Hilo principal del servidor en marcha (lo fija Cauces al arrancar; null sin servidor). */
    public static volatile Thread hilo;
    public static long cortes;
    /** Sin pila: es un corte de control, no un error. */
    public static final RuntimeException CORTE = new RuntimeException("purg4tory: chunk no listo en una comprobación de spawn", null, false, false) {};
    private SondeoSpawn() {}
}
