package es.purg4tory.cauces;

import net.minecraft.server.MinecraftServer;

import java.lang.management.ManagementFactory;
import java.lang.management.ThreadInfo;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/**
 * Hilo de diagnóstico: si el servidor pasa vigiaS segundos sin completar un tick (guardado colgado, parada que no
 * termina, bucle, espera de un chunk), vuelca al registro la pila del hilo principal y el estado de las colas de
 * Streams Reflowing, y escribe un volcado completo de hilos en purg4tory-congelacion-<fecha>.txt (carpeta del juego o
 * del servidor). Cuando el servidor vuelve a completar un tick, registra cuánto duró la congelación.
 * No intenta arreglar nada ni toca el estado del juego; solo lee. Sigue vigilando durante la parada del servidor.
 *
 * Una instancia por arranque de servidor: en un solo jugador el mismo proceso abre y cierra varios mundos.
 */
final class Vigia implements Runnable {
    /** Como máximo tantos volcados a archivo por mundo abierto (cada uno ocupa ~0,5–2 MB). */
    private static final int MAX_ARCHIVOS = 4;
    private final int umbralS;
    private volatile long ultimoTick = System.nanoTime();
    private volatile boolean fin;
    private volatile MinecraftServer server;
    private final boolean conSR;

    Vigia(int umbralS, boolean conSR) { this.umbralS = umbralS; this.conSR = conSR; }

    void tick() { ultimoTick = System.nanoTime(); }

    void arrancar(MinecraftServer s) {
        server = s;
        ultimoTick = System.nanoTime();
        Thread t = new Thread(this, "purg4tory-cauces-vigia");
        t.setDaemon(true);
        t.setPriority(Thread.MIN_PRIORITY);
        t.start();
    }

    void terminar() { fin = true; server = null; }

    @Override public void run() {
        long informado = 0; int informes = 0, archivos = 0; long inicioCongelacion = 0; long peor = 0;
        while (!fin) {
            try { Thread.sleep(2000); } catch (InterruptedException e) { return; }
            try {
                long ahora = System.nanoTime();
                long parado = (ahora - ultimoTick) / 1_000_000_000L;
                if (parado < umbralS) {
                    if (inicioCongelacion != 0) {
                        Cauces.LOG.warn("VIGÍA: fin de la congelación; el servidor estuvo unos {} s sin completar un tick", peor);
                        inicioCongelacion = 0; peor = 0;
                    }
                    informado = 0; informes = 0;
                    continue;
                }
                if (inicioCongelacion == 0) inicioCongelacion = ahora;
                peor = Math.max(peor, parado);
                if (informes >= 10 || (informado != 0 && parado - informado < 60)) continue;
                informado = parado; informes++;
                String sr = conSR ? estadoSR() : "";
                StringBuilder b = new StringBuilder();
                b.append("VIGÍA: el servidor lleva ").append(parado).append(" s sin completar un tick").append(sr);
                Thread principal = server != null ? server.getRunningThread() : null;
                if (principal != null) {
                    b.append("\n  pila del hilo principal (").append(principal.getState()).append("):");
                    StackTraceElement[] pila = principal.getStackTrace();
                    for (int i = 0; i < Math.min(60, pila.length); i++) b.append("\n    at ").append(pila[i]);
                }
                if (archivos < MAX_ARCHIVOS) {
                    Path f = volcar(parado, sr);
                    if (f != null) { archivos++; b.append("\n  volcado completo de hilos: ").append(f.toAbsolutePath()); }
                }
                Cauces.LOG.warn(b.toString());
            } catch (Throwable e) {
                Cauces.LOG.warn("vigía: {}", e.toString());
            }
        }
    }

    private static String estadoSR() {
        try {
            return "; colas SR: " + PuenteSR.colas() + "; cuencas en construcción: " + PuenteSR.construyendo()
                + "; esperas de estructuras: " + PuenteSR.esperasEstructura() + "; hilos de generación retenidos: " + PuenteSR.retenidos();
        } catch (Throwable e) { return "; colas SR no disponibles (" + e + ")"; }
    }

    /** Volcado de todos los hilos (con bloqueos y monitores) a un archivo en el directorio de trabajo del proceso. */
    private Path volcar(long parado, String sr) {
        try {
            String fecha = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd-HHmmss"));
            Path f = Path.of("purg4tory-congelacion-" + fecha + ".txt");
            StringBuilder b = new StringBuilder(1 << 16);
            b.append("PURG4TORY Cauces: volcado de hilos durante una congelación del servidor\n")
                .append("fecha ").append(fecha).append(" | sin completar un tick desde hace ").append(parado).append(" s").append(sr).append('\n');
            MinecraftServer s = server;
            if (s != null) {
                b.append("jugadores ").append(s.getPlayerCount()).append(" | distancia de visión ").append(s.getPlayerList().getViewDistance())
                    .append(" | un jugador ").append(!s.isDedicatedServer()).append('\n');
            }
            Runtime rt = Runtime.getRuntime();
            b.append("memoria ").append((rt.totalMemory() - rt.freeMemory()) >> 20).append('/').append(rt.maxMemory() >> 20).append(" MB\n\n");
            for (ThreadInfo t : ManagementFactory.getThreadMXBean().dumpAllThreads(true, true)) {
                b.append('"').append(t.getThreadName()).append("\" ").append(t.getThreadState());
                if (t.getLockName() != null) b.append(" esperando ").append(t.getLockName());
                if (t.getLockOwnerName() != null) b.append(" (lo tiene \"").append(t.getLockOwnerName()).append("\")");
                b.append('\n');
                for (StackTraceElement e : t.getStackTrace()) b.append("    at ").append(e).append('\n');
                for (var m : t.getLockedMonitors()) b.append("    - bloquea ").append(m).append('\n');
                for (var l : t.getLockedSynchronizers()) b.append("    - posee ").append(l).append('\n');
                b.append('\n');
            }
            Files.writeString(f, b.toString(), StandardCharsets.UTF_8);
            return f;
        } catch (Throwable e) {
            Cauces.LOG.warn("vigía: no se pudo escribir el volcado de hilos ({})", e.toString());
            return null;
        }
    }
}
