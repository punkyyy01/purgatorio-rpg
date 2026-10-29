package es.purg4tory.cauces;

import net.minecraft.core.BlockPos;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.storage.LevelResource;

import java.lang.management.ManagementFactory;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;

/**
 * Decide qué cuenca pedir y cuándo. Corre en el hilo del servidor cada 10 ticks y solo hace cuentas baratas;
 * el trabajo pesado lo hacen los hilos de Streams Reflowing. Nunca bloquea un hilo ni retiene chunks: solo consulta
 * si el futuro de su petición ha terminado. Nunca hay más de una petición propia en curso.
 *
 * Cuándo pide:
 *  - anillo (sin jugadores): solo con Streams ocioso, servidor y máquina holgados, y con pausa tras cada cuenca;
 *  - por delante de un jugador: además vale con que la cola de Streams esté vacía aunque esté construyendo una cuenca
 *    (Streams las construye de una en una: la nuestra va justo detrás y no pasa por delante de nada en espera).
 */
final class Planificador {
    private static final long S = 1_000_000_000L;
    private final Config cfg;
    private MinecraftServer server;
    private ServerLevel nivel;
    private Object motor;
    private double escala;
    private Path dirCuencas;
    private volatile boolean activo;
    private boolean pausado, anilloAnunciado;
    private long inicioPermitido, siguientePermitido, ultimoInforme;
    private int ticks, erroresSeguidos, turnoJugador;

    private final ArrayDeque<int[]> anillo = new ArrayDeque<>();
    private int radioAnillo;
    private int[] enCurso;
    private String motivoEnCurso;
    private boolean enCursoEsJugador;
    private CompletableFuture<Void> futuro;
    private long t0;
    private int completadas, yaHechas, abandonadas, porJugador;
    private double segundosTotales;
    private final Map<UUID, double[]> rastro = new HashMap<>();
    private final Map<Long, Integer> fallos = new HashMap<>();
    private final com.sun.management.OperatingSystemMXBean so =
        (com.sun.management.OperatingSystemMXBean) ManagementFactory.getOperatingSystemMXBean();

    Planificador(Config cfg) { this.cfg = cfg; this.radioAnillo = cfg.radioSinJugadores; }

    void arrancar(MinecraftServer s) {
        // En un solo jugador este objeto sobrevive al mundo anterior: nada de su estado vale para el nuevo
        // (0.4.0 conservaba el motor de Streams del mundo cerrado y seguía pidiéndole cuencas).
        motor = null; futuro = null; enCurso = null; motivoEnCurso = null; enCursoEsJugador = false;
        anillo.clear(); rastro.clear(); fallos.clear();
        radioAnillo = cfg.radioSinJugadores; pausado = false; anilloAnunciado = false;
        siguientePermitido = 0; ultimoInforme = 0; ticks = 0; erroresSeguidos = 0; turnoJugador = 0;
        completadas = 0; yaHechas = 0; abandonadas = 0; porJugador = 0; segundosTotales = 0;
        server = s;
        nivel = s.overworld();
        dirCuencas = s.getWorldPath(LevelResource.ROOT).resolve("streamsreflowing").resolve("minecraft_overworld");
        inicioPermitido = System.nanoTime() + cfg.esperaInicialS * S;
        activo = cfg.planificar;
        Cauces.LOG.info("planificador {}: radio sin jugadores {} bloques, anticipar jugadores {} ({} s por delante), pausa x{}",
            activo ? "listo" : "DESACTIVADO (solo vigía)", radioAnillo, cfg.anticiparJugadores, cfg.horizonteS, cfg.pausaRelativa);
    }

    void detener() { activo = false; motor = null; futuro = null; enCurso = null; server = null; nivel = null; }

    void tick(MinecraftServer s) {
        if (!activo || pausado || ++ticks % 10 != 0) return;
        try {
            paso();
            erroresSeguidos = 0;
        } catch (LinkageError e) {
            activo = false;
            Cauces.LOG.error("Streams Reflowing ya no ofrece los métodos esperados ({}); planificador desactivado", e.toString());
        } catch (RuntimeException e) {
            // Nunca dejar que un fallo propio llegue al tick del servidor.
            enCurso = null;
            if (++erroresSeguidos >= 3) {
                activo = false;
                Cauces.LOG.error("planificador desactivado tras 3 errores seguidos", e);
            } else {
                Cauces.LOG.warn("error en el planificador ({}); reintento", e.toString());
            }
        }
    }

    private void paso() {
        long ahora = System.nanoTime();
        if (motor == null) {
            if (ahora < inicioPermitido) return;
            motor = PuenteSR.motor(nivel);
            if (motor == null) return;
            escala = PuenteSR.escala(motor);
            rehacerAnillo();
        }
        List<ServerPlayer> jugadores = new ArrayList<>(nivel.players());
        actualizarRastro(jugadores);

        if (enCurso != null) {
            double seg = (ahora - t0) / 1e9;
            if (futuro.isDone()) {
                boolean ok = !futuro.isCompletedExceptionally();
                if (ok) { completadas++; segundosTotales += seg; }
                else { abandonadas++; fallos.merge(clave(enCurso), 1, Integer::sum); }
                Cauces.LOG.info("cuenca ({},{}) {} en {} s [{}]; quedan {} en el anillo", enCurso[0], enCurso[1],
                    ok ? "lista" : "FALLÓ", String.format("%.1f", seg), motivoEnCurso, anillo.size());
                // La pausa solo se aplica al anillo: por delante de un jugador importa la latencia.
                siguientePermitido = enCursoEsJugador ? ahora : ahora + (long) (seg * cfg.pausaRelativa * S);
                enCurso = null;
            } else if (seg > 300) {
                abandonadas++;
                fallos.merge(clave(enCurso), 1, Integer::sum);
                Cauces.LOG.warn("cuenca ({},{}) sigue sin terminar tras 300 s; dejo de esperarla", enCurso[0], enCurso[1]);
                enCurso = null;
            }
            return;
        }
        if (ahora - ultimoInforme > 60 * S && !anillo.isEmpty()) {
            ultimoInforme = ahora;
            Cauces.LOG.info("progreso: {} cuencas preparadas ({} s), {} ya estaban hechas, quedan {}; colas SR: {}",
                completadas, String.format("%.0f", segundosTotales), yaHechas, anillo.size(), PuenteSR.colas());
        }
        if (server.getAverageTickTimeNanos() / 1e6 > cfg.msptMaximo) return;
        double carga = so.getCpuLoad();
        if (carga >= 0 && carga > cfg.cargaMaquinaMaxima) return;      // otros servicios de la máquina primero

        int[] k = null; String motivo = null; boolean deJugador = false;
        if (!jugadores.isEmpty() && cfg.anticiparJugadores && PuenteSR.colaVacia()) {
            Object[] mejor = elegirPorDelante(jugadores);
            if (mejor != null) { k = (int[]) mejor[0]; motivo = (String) mejor[1]; deJugador = true; }
        }
        if (k == null && (jugadores.isEmpty() || cfg.anilloConJugadores)
                && ahora >= siguientePermitido && PuenteSR.construyendo() == 0) {
            while (!anillo.isEmpty()) {
                int[] c = anillo.poll();
                if (hecha(c) || descartada(c)) { yaHechas++; continue; }
                k = c; motivo = "anillo"; break;
            }
        }
        if (k == null) {
            if (anillo.isEmpty() && !anilloAnunciado && radioAnillo > 0 && jugadores.isEmpty()) {
                anilloAnunciado = true;
                Cauces.LOG.info("anillo terminado: {} cuencas preparadas, {} ya estaban hechas", completadas, yaHechas);
            }
            return;
        }
        if (deJugador) porJugador++;
        enCurso = k; motivoEnCurso = motivo; enCursoEsJugador = deJugador; t0 = ahora;
        futuro = PuenteSR.pedir(motor, k[0], k[1]);
    }

    private static long clave(int[] c) { return ((long) c[0] << 32) ^ (c[1] & 0xffffffffL); }

    /** Tras dos fallos (o 300 s sin terminar) una cuenca no se vuelve a pedir en esta sesión: Streams la hará al llegar. */
    private boolean descartada(int[] c) { return fallos.getOrDefault(clave(c), 0) >= 2; }

    /** Ya preparada: en memoria o guardada en el mundo por Streams. */
    private boolean hecha(int[] c) {
        return PuenteSR.lista(motor, c[0], c[1]) || Files.exists(dirCuencas.resolve("r." + c[0] + "." + c[1] + ".srn"));
    }

    private void actualizarRastro(List<ServerPlayer> jugadores) {
        long ahora = System.nanoTime();
        for (ServerPlayer p : jugadores) {
            double[] r = rastro.get(p.getUUID());
            if (r == null) { rastro.put(p.getUUID(), new double[] { p.getX(), p.getZ(), 0, 0, ahora }); continue; }
            double dt = Math.max(0.05, (ahora - r[4]) / 1e9);
            double dx = p.getX() - r[0], dz = p.getZ() - r[1];
            if (dx * dx + dz * dz > 256 * 256) { dx = 0; dz = 0; }       // teletransporte: no es movimiento
            r[2] = r[2] * 0.7 + dx / dt * 0.3; r[3] = r[3] * 0.7 + dz / dt * 0.3;  // velocidad media en bloques/s
            r[0] = p.getX(); r[1] = p.getZ(); r[4] = ahora;
        }
        if (rastro.size() > jugadores.size() + 8) rastro.keySet().retainAll(jugadores.stream().map(ServerPlayer::getUUID).toList());
    }

    /**
     * Entre todos los jugadores que se mueven, la cuenca no preparada a la que llegará antes alguno de ellos.
     * Mira por delante hasta horizonteS segundos (mínimo 1,5 cuencas), en el eje del camino y a ambos lados
     * (distancia de visión + margen), porque los chunks de los lados también necesitan su cuenca.
     */
    private Object[] elegirPorDelante(List<ServerPlayer> jugadores) {
        int vision = server.getPlayerList().getViewDistance() * 16 + 64;
        int[] mejor = null; String quien = null; double mejorEta = Double.MAX_VALUE;
        int n = jugadores.size();
        for (int i = 0; i < n; i++) {
            ServerPlayer p = jugadores.get((i + turnoJugador) % n);
            double[] r = rastro.get(p.getUUID());
            if (r == null) continue;
            double v = Math.hypot(r[2], r[3]);
            if (v < 1.0) continue;                                         // casi quieto: no anticipar
            double ux = r[2] / v, uz = r[3] / v;
            double alcance = Math.max(1.5 * escala, v * cfg.horizonteS);
            for (double d = 0.25 * escala; d <= alcance; d += 0.25 * escala) {
                double eta = d / v;
                if (eta >= mejorEta) break;
                for (int lado = 0; lado < 3; lado++) {
                    double o = lado == 0 ? 0 : (lado == 1 ? vision : -vision);
                    int[] k = PuenteSR.placaEn(motor, p.getX() + ux * d - uz * o, p.getZ() + uz * d + ux * o);
                    if (!hecha(k) && !descartada(k)) { mejor = k; mejorEta = eta; quien = p.getGameProfile().getName(); break; }
                }
                if (mejor != null && mejorEta == eta) break;
            }
        }
        turnoJugador++;
        return mejor == null ? null : new Object[] { mejor, String.format("por delante de %s, llega en ~%.0f s", quien, mejorEta) };
    }

    private void rehacerAnillo() {
        anillo.clear();
        anilloAnunciado = false;
        if (radioAnillo <= 0 || motor == null) return;
        BlockPos o = nivel.getSharedSpawnPos();
        double alcance = radioAnillo + 0.75 * escala;                     // cuencas cuya celda puede tocar el círculo
        int n = (int) Math.ceil(alcance / escala) + 1;
        int bx = (int) Math.floor(o.getX() / escala), bz = (int) Math.floor(o.getZ() / escala);
        List<double[]> c = new ArrayList<>();
        for (int cx = bx - n; cx <= bx + n; cx++) for (int cz = bz - n; cz <= bz + n; cz++) {
            double d = Math.hypot(PuenteSR.semillaX(motor, cx, cz) - o.getX(), PuenteSR.semillaZ(motor, cx, cz) - o.getZ());
            if (d <= alcance) c.add(new double[] { cx, cz, d });
        }
        c.sort(Comparator.comparingDouble(a -> a[2]));                    // de dentro hacia fuera: reanudable y determinista
        for (double[] a : c) anillo.add(new int[] { (int) a[0], (int) a[1] });
        Cauces.LOG.info("anillo: {} cuencas de {} bloques en {} bloques alrededor de ({}, {})", anillo.size(),
            (int) escala, radioAnillo, o.getX(), o.getZ());
    }

    String estado() {
        if (!cfg.planificar) return "Cauces: planificador desactivado en la configuración (vigía activo)";
        if (motor == null) return "Cauces: esperando al motor de Streams Reflowing";
        return String.format("Cauces: %s; %d cuencas preparadas (%.0f s, media %.1f s), %d por delante de jugadores, "
                + "%d ya estaban hechas, %d fallidas; quedan %d en el anillo (radio %d)%s",
            !activo ? "DETENIDO" : pausado ? "EN PAUSA" : "activo", completadas, segundosTotales,
            completadas > 0 ? segundosTotales / completadas : 0, porJugador, yaHechas, abandonadas, anillo.size(), radioAnillo,
            enCurso != null ? String.format("; preparando (%d,%d)", enCurso[0], enCurso[1]) : "");
    }

    String pausar(boolean p) { pausado = p; return p ? "Cauces en pausa" : "Cauces reanudado"; }

    String planificar(int radio) {
        radioAnillo = radio;
        rehacerAnillo();
        pausado = false;
        return "Cauces: " + anillo.size() + " cuencas en el anillo de " + radio + " bloques (las ya hechas se saltan)";
    }
}
