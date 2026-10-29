package es.purg4tory.cauces;

/** Configuración y registro de la salvaguarda del guardado completo (ver mixin.ChunkMapGuardadoMixin). */
public final class SalvaguardaGuardado {
    /** Implementada por ChunkMap cuando el mixin se ha aplicado (para comprobarlo al arrancar). */
    public interface Marca {}

    static volatile int esperaMaxima = 30;
    /** Segundos máximos que el bucle de parada de Minecraft espera a que no quede trabajo de chunks. 0 = sin límite. */
    static volatile int esperaParada = 60;
    /** Instante (System.nanoTime) en que empezó la parada del servidor; 0 = no se está parando. */
    static volatile long inicioParadaNs = 0;
    private static boolean paradaAvisada;
    private SalvaguardaGuardado() {}

    public static int esperaMaximaS() { return esperaMaxima; }

    /**
     * Llamado desde ChunkMap.hasWork() durante la parada: tras esperaParada segundos se da el trabajo por terminado para
     * que el servidor pase al guardado final (sin esto, un chunk que no termina de generarse impide guardar y parar).
     */
    private static long diferidasTotal, diferidasMax;
    /** Estadística (hilo principal): reintentos de descargas retenidas por generación. */
    public static void contarDiferidas(int n) { diferidasTotal += n; if (n > diferidasMax) diferidasMax = n; }
    public static String estadoDiferidas() { return "descargas diferidas por generación: " + diferidasTotal + " reintentos, máx. " + diferidasMax + " a la vez"; }

    public static boolean paradaVencida() {
        long i = inicioParadaNs;
        if (i == 0 || esperaParada <= 0 || System.nanoTime() - i < esperaParada * 1_000_000_000L) return false;
        if (!paradaAvisada) {
            paradaAvisada = true;
            Cauces.LOG.warn("parada: aún hay chunks en generación tras {} s; se continúa con el guardado final "
                + "(esos chunks a medio generar no se guardan y se regenerarán)", esperaParada);
        }
        return true;
    }

    public static void informar(int apartados, int liberados, double segundos) {
        if (liberados == apartados) {
            Cauces.LOG.info("guardado completo: {} chunks retenidos por generación en curso; liberados y guardados en {} s",
                apartados, String.format("%.1f", segundos));
        } else {
            Cauces.LOG.warn("guardado completo: {} chunks retenidos por generación en curso; {} liberados en {} s, {} quedan "
                + "para los ticks siguientes (se guardarán al descargarse; sin este arreglo el servidor se habría colgado)",
                apartados, liberados, String.format("%.1f", segundos), apartados - liberados);
        }
    }
}
