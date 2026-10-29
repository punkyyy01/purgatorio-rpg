package es.purg4tory.diagtick;

import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.chunk.status.ChunkStatus;

/** Esperas síncronas de chunks en el hilo principal (solo se llama desde él). */
public final class Esperas {
    static final long[] INICIO = new long[128]; static int prof;
    static final long UMBRAL = 50_000_000L;
    static long total, lentas;

    public static void entrar() { if (prof < INICIO.length) INICIO[prof] = System.nanoTime(); prof++; }

    public static void salir(ServerLevel nivel, int x, int z, ChunkStatus st, boolean carga, ChunkAccess r) {
        if (prof == 0) return;
        prof--; if (prof >= INICIO.length) return;
        long ns = System.nanoTime() - INICIO[prof]; total++;
        if (ns < UMBRAL) return;
        lentas++;
        int dmin = Integer.MAX_VALUE;
        for (var p : nivel.players()) dmin = Math.min(dmin, Math.max(Math.abs(p.chunkPosition().x - x), Math.abs(p.chunkPosition().z - z)));
        StringBuilder b = new StringBuilder(String.format("ESPERA %.0f ms chunk (%d,%d) %s %s carga=%s prof=%d resultado=%s dist_jugador=%d #%d",
            ns / 1e6, x, z, nivel.dimension().location(), st, carga, prof, r == null ? "null" : r.getClass().getSimpleName(), dmin, lentas));
        StackTraceElement[] pila = Thread.currentThread().getStackTrace(); boolean tras = false; int n = 0;
        for (StackTraceElement e : pila) {
            String s = e.toString();
            if (!tras) { if (s.contains("ServerChunkCache.getChunk")) tras = true; continue; }
            if (s.contains("ServerChunkCache.getChunk") || s.contains("diagtick")) continue;
            b.append("\n      ").append(s); if (++n >= 30) break;
        }
        DiagTick.escribir(DiagTick.esperas, b.toString());
    }
}
