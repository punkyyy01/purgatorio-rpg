package es.purg4tory.diagtick;

import java.util.*;

/** Hilo vigía: detecta pausas del hilo principal, muestrea su pila y registra la posición del jugador en el cliente. */
final class Vigia {
    static final long UMBRAL = 250_000_000L, MIN_INFORME = 500_000_000L;
    static final String[] CLAVES = {
        "getChunkBlocking", "postProcessGeneration", "CollectingNeighborUpdater", "teleport", "saveAllChunks", "processUnloads",
        "streamsreflowing", "purg4tory", "managedBlock", "LockSupport.park", "Object.wait", "Thread.sleep", "Unsafe.park",
        "ChunkMap", "DistanceManager", "tickChunks", "tickEntities", "EntityTickList", "PoiManager", "StructureManager",
        "LevelChunk.runPostLoad", "ServerLevel.tick", "BlockEntity", "ChunkSerializer", "RegionFile", "IOWorker",
        "net.minecraft.world.entity.ai", "PathFinder", "NaturalSpawner", "Explosion", "FlowingFluid", "LiquidBlock",
        "ServerGamePacketListenerImpl", "GameTestServer", "Commands", "ChunkGenerator", "NoiseBasedChunkGenerator", "Feature"
    };

    static void bucle() {
        boolean enPausa = false; long inicio = 0, siguienteVolcado = 0; int muestras = 0;
        Map<String, Integer> firmas = new HashMap<>(); Map<String, Integer> clases = new TreeMap<>(); Map<Thread.State, Integer> estados = new EnumMap<>(Thread.State.class);
        long ultimaPos = 0;
        while (DiagTick.vivo) {
            try { Thread.sleep(10); } catch (InterruptedException e) { return; }
            long ahora = System.nanoTime(), fin = DiagTick.finUltimoTick, gap = ahora - fin;
            Thread h = DiagTick.hiloPrincipal;
            if (ahora - ultimaPos > 1_000_000_000L) { ultimaPos = ahora; posicionCliente(gap); }
            if (gap > UMBRAL && h != null) {
                if (!enPausa) { enPausa = true; inicio = fin; muestras = 0; firmas.clear(); clases.clear(); estados.clear(); siguienteVolcado = fin + 3_000_000_000L; }
                StackTraceElement[] st = h.getStackTrace(); muestras++;
                estados.merge(h.getState(), 1, Integer::sum);
                StringBuilder f = new StringBuilder(); Set<String> vistas = new HashSet<>();
                for (int i = 0; i < Math.min(st.length, 45); i++) {
                    String e = st[i].toString(); f.append("\n      ").append(e);
                    for (String k : CLAVES) if (e.contains(k) && vistas.add(k)) clases.merge(k, 1, Integer::sum);
                }
                firmas.merge(f.toString(), 1, Integer::sum);
                if (ahora > siguienteVolcado) { siguienteVolcado = ahora + 20_000_000_000L; DiagTick.volcado(String.format("pausa en curso de %.1f s", gap / 1e9)); }
            } else if (enPausa) {
                enPausa = false;
                long dur = fin - inicio;
                if (dur >= MIN_INFORME && muestras > 0) informe(dur, muestras, firmas, clases, estados);
            }
        }
    }

    static void informe(long dur, int muestras, Map<String, Integer> firmas, Map<String, Integer> clases, Map<Thread.State, Integer> estados) {
        StringBuilder b = new StringBuilder(String.format("PAUSA %.2f s, %d muestras, estados %s\n  claves:", dur / 1e9, muestras, estados));
        clases.entrySet().stream().sorted((a, c) -> c.getValue() - a.getValue())
            .forEach(e -> b.append(String.format(" %s=%d%%", e.getKey(), 100 * e.getValue() / muestras)));
        firmas.entrySet().stream().sorted((a, c) -> c.getValue() - a.getValue()).limit(4)
            .forEach(e -> b.append(String.format("\n  pila (%d%%):", 100 * e.getValue() / muestras)).append(e.getKey()));
        DiagTick.escribir(DiagTick.pausas, b.toString());
    }

    static java.lang.reflect.Method getInstance; static java.lang.reflect.Field campoJugador, campoFps;
    static boolean sinCliente;
    /** Si hay cliente en este proceso (un jugador), su posición: compararla con la del servidor detecta desincronización. */
    static void posicionCliente(long gap) {
        if (sinCliente) return;
        try {
            if (getInstance == null) {
                Class<?> mc = Class.forName("net.minecraft.client.Minecraft");
                getInstance = mc.getMethod("getInstance"); campoJugador = mc.getField("player");
                campoFps = mc.getDeclaredField("fps"); campoFps.setAccessible(true);
            }
            Object m = getInstance.invoke(null); if (m == null) return;
            Object p = campoJugador.get(m);
            int fps = campoFps.getInt(m);
            if (p instanceof net.minecraft.world.entity.Entity e)
                DiagTick.escribir(DiagTick.posiciones, String.format("CLI %.1f %.1f %.1f fps=%d ms_desde_ultimo_tick=%d", e.getX(), e.getY(), e.getZ(), fps, gap / 1_000_000));
        } catch (ClassNotFoundException ex) { sinCliente = true; }
        catch (Throwable t) { DiagTick.escribir(DiagTick.posiciones, "CLI error " + t); sinCliente = true; }
    }
}
