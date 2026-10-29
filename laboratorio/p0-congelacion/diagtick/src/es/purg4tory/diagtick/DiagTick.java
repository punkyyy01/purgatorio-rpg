package es.purg4tory.diagtick;

import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.loading.FMLPaths;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.server.ServerStartedEvent;
import net.neoforged.neoforge.event.server.ServerStoppedEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;

import java.io.BufferedWriter;
import java.io.IOException;
import java.lang.management.ManagementFactory;
import java.lang.management.ThreadInfo;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

/**
 * SOLO LABORATORIO. Mide la vida del hilo principal del servidor (dedicado o integrado):
 *  - pausas: tiempo desde el último fin de tick > 250 ms; durante la pausa muestrea la pila del hilo principal cada 10 ms,
 *    y a los 3 s (y cada 20 s después) vuelca todos los hilos con locks y busca deadlocks;
 *  - esperas síncronas de chunks en el hilo principal (mixin EsperaChunkMixin) con su origen;
 *  - posición del jugador en el servidor y en el cliente (si hay cliente en el proceso), y teletransportes sin confirmar.
 * Salida: <juego>/diagtick/<fecha>/{pausas,esperas,posiciones,resumen}.log y volcado-*.txt
 */
@Mod("purg4tory_diagtick")
public final class DiagTick {
    static final DateTimeFormatter F = DateTimeFormatter.ofPattern("HH:mm:ss.SSS");
    static volatile MinecraftServer servidor;
    static volatile Thread hiloPrincipal;
    static volatile long finUltimoTick = System.nanoTime();
    static volatile long ticks;
    static Path dir;
    static BufferedWriter pausas, esperas, posiciones, resumen;
    static Thread vigia;
    static volatile boolean vivo;

    // estadística de ticks (solo hilo principal)
    static long inicioTick, minutoIni = System.nanoTime(), nTicks, sumaNs, maxNs; static int b50, b250, b1000, b5000;

    public DiagTick() {
        NeoForge.EVENT_BUS.addListener(ServerStartedEvent.class, e -> arrancar(e.getServer()));
        NeoForge.EVENT_BUS.addListener(ServerStoppedEvent.class, e -> parar());
        NeoForge.EVENT_BUS.addListener(ServerTickEvent.Pre.class, e -> inicioTick = System.nanoTime());
        NeoForge.EVENT_BUS.addListener(ServerTickEvent.Post.class, e -> finTick(e.getServer()));
        if (net.neoforged.fml.loading.FMLEnvironment.dist.isClient()) ClienteVuelo.registrar();
    }

    static synchronized void escribir(BufferedWriter w, String s) {
        if (w == null) return;
        try { w.write(LocalDateTime.now().format(F)); w.write(' '); w.write(s); w.newLine(); w.flush(); } catch (IOException ignored) {}
    }

    static void arrancar(MinecraftServer s) {
        try {
            dir = FMLPaths.GAMEDIR.get().resolve("diagtick").resolve(LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd-HHmmss")));
            Files.createDirectories(dir);
            pausas = Files.newBufferedWriter(dir.resolve("pausas.log"));
            esperas = Files.newBufferedWriter(dir.resolve("esperas.log"));
            posiciones = Files.newBufferedWriter(dir.resolve("posiciones.log"));
            resumen = Files.newBufferedWriter(dir.resolve("resumen.log"));
        } catch (IOException ex) { throw new RuntimeException(ex); }
        servidor = s; hiloPrincipal = Thread.currentThread(); finUltimoTick = System.nanoTime(); vivo = true;
        escribir(resumen, "inicio; dedicado=" + s.isDedicatedServer() + " hilo=" + hiloPrincipal.getName());
        vigia = new Thread(Vigia::bucle, "diagtick-vigia"); vigia.setDaemon(true); vigia.start();
    }

    static void parar() {
        vivo = false;
        escribir(resumen, "parada (servidor detenido; guardado terminado)");
        servidor = null;
    }

    static void finTick(MinecraftServer s) {
        long ahora = System.nanoTime(), d = ahora - inicioTick;
        finUltimoTick = ahora; ticks++;
        nTicks++; sumaNs += d; if (d > maxNs) maxNs = d;
        if (d > 50_000_000L) b50++; if (d > 250_000_000L) b250++; if (d > 1_000_000_000L) b1000++; if (d > 5_000_000_000L) b5000++;
        if (ahora - minutoIni > 60_000_000_000L) {
            escribir(resumen, String.format("minuto: ticks=%d mspt_medio=%.1f max=%.0fms >50ms=%d >250ms=%d >1s=%d >5s=%d chunks_cargados=%d",
                nTicks, sumaNs / 1e6 / Math.max(1, nTicks), maxNs / 1e6, b50, b250, b1000, b5000, cargados(s)));
            minutoIni = ahora; nTicks = 0; sumaNs = 0; maxNs = 0; b50 = b250 = b1000 = b5000 = 0;
        }
        if (vueloTicks > 0) vuelo(s);
        if (ticks % 20 == 0) { posicionesServidor(s); comandos(s); }
    }

    // Vuelo programado (determinista): cada tick mueve a todos los jugadores (vx,vz) bloques a altura fija,
    // con teleport de conexión (mismo camino que un movimiento: absMoveTo; no carga chunks de forma síncrona).
    static double vueloVx, vueloVz, vueloY; static long vueloTicks, vueloEsperando;
    static void vuelo(MinecraftServer s) {
        vueloTicks--;
        for (ServerPlayer p : s.getPlayerList().getPlayers()) {
            if (!p.getAbilities().flying && p.getAbilities().mayfly) { p.getAbilities().flying = true; p.onUpdateAbilities(); }
            double nx = p.getX() + vueloVx, nz = p.getZ() + vueloVz;
            // como el cliente real: no avanza hacia un chunk que aún no está listo (el cliente no lo tendría)
            if (p.serverLevel().getChunkSource().getChunkNow((int) Math.floor(nx) >> 4, (int) Math.floor(nz) >> 4) == null) { vueloEsperando++; continue; }
            p.connection.teleport(nx, vueloY, nz, p.getYRot(), p.getXRot());
        }
        if (vueloTicks % 1200 == 0 && vueloEsperando > 0) { escribir(resumen, "vuelo: ticks frenado por chunk no listo=" + vueloEsperando); vueloEsperando = 0; }
        if (vueloTicks == 0) escribir(resumen, "vuelo terminado");
    }

    static boolean ordenPropia(MinecraftServer s, String c) {
        String[] a = c.split("\\s+");
        if (a[0].equals("!vuelo")) { // !vuelo <bloques_por_s_x> <bloques_por_s_z> <y> <segundos>
            vueloVx = Double.parseDouble(a[1]) / 20; vueloVz = Double.parseDouble(a[2]) / 20; vueloY = Double.parseDouble(a[3]);
            vueloTicks = Long.parseLong(a[4]) * 20; return true;
        }
        if (a[0].equals("!parar_vuelo")) { vueloTicks = 1; ClienteVuelo.parar(); return true; }
        if (a[0].equals("!salir")) { ClienteVuelo.salir(); return true; }
        if (a[0].equals("!vuelo_cliente")) { ClienteVuelo.empezar(Long.parseLong(a[1]), a.length > 2 ? Double.parseDouble(a[2]) : 0, a.length > 3 ? Double.parseDouble(a[3]) : -90); return true; }   // !vuelo_cliente <segundos> [grados de giro por minuto]
        return false;
    }

    /** Órdenes de laboratorio: <juego>/diagtick-comandos.txt se ejecuta como consola y se borra. */
    static void comandos(MinecraftServer s) {
        Path f = FMLPaths.GAMEDIR.get().resolve("diagtick-comandos.txt");
        if (!Files.exists(f)) return;
        try {
            List<String> l = Files.readAllLines(f); Files.delete(f);
            for (String c : l) { c = c.strip(); if (c.isEmpty()) continue;
                escribir(resumen, "orden: " + c);
                if (c.startsWith("!")) { try { ordenPropia(s, c); } catch (RuntimeException ex) { escribir(resumen, "orden mal: " + ex); } continue; }
                s.getCommands().performPrefixedCommand(s.createCommandSourceStack(), c); }
        } catch (IOException ex) { escribir(resumen, "órdenes: " + ex); }
    }

    static int cargados(MinecraftServer s) {
        int n = 0; for (ServerLevel l : s.getAllLevels()) n += l.getChunkSource().getLoadedChunksCount(); return n;
    }

    static java.lang.reflect.Field campoEspera;
    static void posicionesServidor(MinecraftServer s) {
        for (ServerPlayer p : s.getPlayerList().getPlayers()) {
            boolean cargado = p.serverLevel().getChunkSource().getChunkNow(p.chunkPosition().x, p.chunkPosition().z) != null;
            Object espera = null;
            try {
                if (campoEspera == null) { campoEspera = p.connection.getClass().getDeclaredField("awaitingPositionFromClient"); campoEspera.setAccessible(true); }
                espera = campoEspera.get(p.connection);
            } catch (ReflectiveOperationException | RuntimeException ignored) {}
            escribir(posiciones, String.format("SRV tick=%d %s %.1f %.1f %.1f chunk_cargado=%s tp_sin_confirmar=%s",
                ticks, p.getGameProfile().getName(), p.getX(), p.getY(), p.getZ(), cargado, espera == null ? "no" : espera));
        }
    }

    /** Volcado completo de hilos con locks; devuelve los ids en deadlock (o null). */
    static void volcado(String motivo) {
        try {
            var mx = ManagementFactory.getThreadMXBean();
            long[] dl = mx.findDeadlockedThreads();
            StringBuilder b = new StringBuilder("# " + motivo + "\n# deadlock: " + (dl == null ? "ninguno" : Arrays.toString(dl)) + "\n");
            for (ThreadInfo ti : mx.dumpAllThreads(true, true)) {
                b.append('"').append(ti.getThreadName()).append("\" ").append(ti.getThreadState());
                if (ti.getLockName() != null) b.append(" en ").append(ti.getLockName());
                if (ti.getLockOwnerName() != null) b.append(" (dueño ").append(ti.getLockOwnerName()).append(')');
                b.append('\n');
                StackTraceElement[] st = ti.getStackTrace();
                for (int i = 0; i < Math.min(st.length, 80); i++) b.append("    at ").append(st[i]).append('\n');
                for (var m : ti.getLockedMonitors()) b.append("    - monitor ").append(m).append('\n');
                for (var l : ti.getLockedSynchronizers()) b.append("    - sincronizador ").append(l).append('\n');
                b.append('\n');
            }
            Path f = dir.resolve("volcado-" + LocalDateTime.now().format(DateTimeFormatter.ofPattern("HHmmss-SSS")) + ".txt");
            Files.writeString(f, b.toString());
            escribir(pausas, "  volcado " + f.getFileName() + " deadlock=" + (dl == null ? "no" : "SI " + dl.length));
        } catch (Throwable t) { escribir(pausas, "  volcado falló: " + t); }
    }
}
