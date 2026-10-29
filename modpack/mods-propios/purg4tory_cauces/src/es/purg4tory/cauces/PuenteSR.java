package es.purg4tory.cauces;

import dev.streamsreflowing.core.RiverEngine;
import dev.streamsreflowing.core.plate.PlateKey;
import dev.streamsreflowing.core.plate.PlateLattice;
import dev.streamsreflowing.worldgen.StreamPrefetcher;
import dev.streamsreflowing.worldgen.StreamsWorldgen;
import net.minecraft.server.level.ServerLevel;

import java.util.concurrent.CompletableFuture;

/**
 * Único punto de contacto con Streams Reflowing (licencia All Rights Reserved: no se copia ni se modifica nada suyo).
 * Solo métodos públicos de la 2.15.2, los mismos que usa su propia generación de chunks:
 *  - StreamsWorldgen.engineIfPresent(nivel)       motor de ríos del nivel (null si aún no existe)
 *  - RiverEngine.lattice().seedX/seedZ/plateAt/scale   geometría de las cuencas (Voronoi con semillas desplazadas)
 *  - RiverEngine.isPlateReady(placa)              ¿ya está en memoria?
 *  - RiverEngine.whenPlatesReady(placas)          pide la cuenca por la vía de demanda normal y devuelve un futuro
 *  - RiverEngine.activeBuildCount()               cuencas construyéndose ahora mismo
 *  - RiverEngine.DEMAND_REASON                    etiqueta de quién pide (aparece en sus registros de diagnóstico)
 *  - StreamPrefetcher.laneDiag()                  estado de sus colas (registro, vigía y «¿cola vacía?»)
 * Si una versión futura cambia algo de esto, la llamada falla con LinkageError y el planificador se desactiva.
 */
final class PuenteSR {
    private PuenteSR() {}

    static Object motor(ServerLevel nivel) { return StreamsWorldgen.engineIfPresent(nivel); }

    static double escala(Object motor) { return ((RiverEngine) motor).lattice().scale(); }

    static double semillaX(Object motor, int cx, int cz) { return ((RiverEngine) motor).lattice().seedX(cx, cz); }

    static double semillaZ(Object motor, int cx, int cz) { return ((RiverEngine) motor).lattice().seedZ(cx, cz); }

    /** Cuenca que contiene el punto (x, z) en bloques. */
    static int[] placaEn(Object motor, double x, double z) {
        PlateKey k = ((RiverEngine) motor).lattice().plateAt(x, z);
        return new int[] { k.cx(), k.cz() };
    }

    static boolean lista(Object motor, int cx, int cz) { return ((RiverEngine) motor).isPlateReady(new PlateKey(cx, cz)); }

    static CompletableFuture<Void> pedir(Object motor, int cx, int cz) {
        RiverEngine.DEMAND_REASON.set("purg4tory_cauces");
        try { return ((RiverEngine) motor).whenPlatesReady(new PlateKey[] { new PlateKey(cx, cz) }); }
        finally { RiverEngine.DEMAND_REASON.remove(); }
    }

    static int construyendo() { return RiverEngine.activeBuildCount(); }

    static String colas() { return StreamPrefetcher.laneDiag(); }

    /** Pasos de estructura que esperan ahora mismo a que se planifique su cuenca (bloquean el hilo que genera). */
    static int esperasEstructura() { return StreamsWorldgen.structureWaiters(); }

    /** Hilos de generación retenidos esperando la planificación de ríos. */
    static int retenidos() { return dev.streamsreflowing.core.cache.PlateRiverCache.foreignHeld(); }

    /**
     * ¿No hay ninguna cuenca esperando en la cola de Streams? Se lee del texto de diagnóstico de Streams
     * («exec=1/1 queue=0 activeBuilds=0 urgentWaiters=0»). Si el formato cambia, se responde como si Streams
     * estuviera ocupado salvo que no construya nada (comportamiento prudente de la versión 0.1.0).
     */
    static boolean colaVacia() {
        String d = StreamPrefetcher.laneDiag();
        java.util.regex.Matcher q = COLA.matcher(d), u = URGENTES.matcher(d);
        if (q.find() && u.find()) return Integer.parseInt(q.group(1)) == 0 && Integer.parseInt(u.group(1)) == 0;
        return construyendo() == 0;
    }
    private static final java.util.regex.Pattern COLA = java.util.regex.Pattern.compile("queue=(\\d+)");
    private static final java.util.regex.Pattern URGENTES = java.util.regex.Pattern.compile("urgentWaiters=(\\d+)");
}
