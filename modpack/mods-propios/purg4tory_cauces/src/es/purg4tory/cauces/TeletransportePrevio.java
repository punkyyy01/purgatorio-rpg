package es.purg4tory.cauces;

import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.level.TicketType;
import net.minecraft.world.level.ChunkPos;

import java.util.Comparator;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;

/**
 * Teletransporte de jugadores a terreno sin cargar sin congelar el servidor (ver mixin.ServerPlayerTeletransporteMixin).
 *
 * Problema: un teletransporte (/tp, otros mods) a un chunk sin generar obliga al hilo principal a esperar su
 * generación; con Streams Reflowing en frío eso son 20–60 s de servidor parado para todos.
 * Solución: el teletransporte se aplaza. Se pide la carga del destino con un ticket (asíncrona, en los hilos de
 * generación) y el jugador se mueve cuando los chunks de alrededor ya están listos. El hilo principal sigue
 * atendiendo a todos mientras tanto. Si el destino no está listo tras {@code esperaMaximaS}, se avisa al jugador y se
 * cancela (no se bloquea el servidor). Un jugador solo puede tener un teletransporte pendiente.
 */
public final class TeletransportePrevio {
    /** Ticket propio, de 60 s de vida, que mantiene cargado el destino mientras se prepara. */
    private static final TicketType<Integer> TICKET = TicketType.create("purg4tory_tp", Integer::compare, 1200);
    private static final int RADIO_TICKET = 2;

    static volatile boolean activo = true;
    static volatile int esperaMaximaS = 90;

    private static final ThreadLocal<Boolean> REENTRADA = ThreadLocal.withInitial(() -> false);
    private static final Map<UUID, Pendiente> PENDIENTES = new LinkedHashMap<>();
    private static long preparados, cancelados, inmediatos;

    private TeletransportePrevio() {}

    private record Pendiente(ServerLevel nivel, ChunkPos centro, long limiteTick, Runnable repetir, long inicioNs) {}

    /** true = se aplaza (el mixin cancela la llamada); false = seguir con el teletransporte normal. */
    public static boolean interceptar(ServerPlayer jugador, ServerLevel nivel, double x, double z, Runnable repetir) {
        if (!activo || REENTRADA.get() || jugador.getServer() == null || !jugador.getServer().isSameThread()) return false;
        ChunkPos c = new ChunkPos(net.minecraft.core.BlockPos.containing(x, 64, z));
        if (listo(nivel, c)) { inmediatos++; return false; }
        if (PENDIENTES.containsKey(jugador.getUUID())) {
            jugador.displayClientMessage(Component.literal("Ya hay un teletransporte en preparación"), true);
            return true;
        }
        long limite = jugador.getServer().getTickCount() + esperaMaximaS * 20L;
        PENDIENTES.put(jugador.getUUID(), new Pendiente(nivel, c, limite, repetir, System.nanoTime()));
        ticket(nivel, c, jugador);
        jugador.displayClientMessage(Component.literal("Preparando el destino…"), true);
        return true;
    }

    private static void ticket(ServerLevel nivel, ChunkPos c, ServerPlayer j) {
        nivel.getChunkSource().addRegionTicket(TICKET, c, RADIO_TICKET, j.getId());
    }

    /** El chunk de destino y su entorno inmediato están completos. */
    private static boolean listo(ServerLevel nivel, ChunkPos c) {
        var cs = nivel.getChunkSource();
        for (int dx = -1; dx <= 1; dx++) for (int dz = -1; dz <= 1; dz++)
            if (cs.getChunkNow(c.x + dx, c.z + dz) == null) return false;
        return true;
    }

    /** Una vez por tick del servidor (hilo principal). */
    public static void tick(MinecraftServer s) {
        if (PENDIENTES.isEmpty()) return;
        long ahora = s.getTickCount();
        for (Iterator<Map.Entry<UUID, Pendiente>> it = PENDIENTES.entrySet().iterator(); it.hasNext();) {
            var e = it.next(); Pendiente p = e.getValue();
            ServerPlayer j = s.getPlayerList().getPlayer(e.getKey());
            if (j == null || j.hasDisconnected() || !j.isAlive()) { it.remove(); cancelados++; continue; }
            if (listo(p.nivel(), p.centro())) {
                it.remove(); preparados++;
                REENTRADA.set(true);
                try { p.repetir().run(); }
                catch (RuntimeException ex) { Cauces.LOG.warn("teletransporte aplazado de {} falló: {}", j.getGameProfile().getName(), ex.toString()); }
                finally { REENTRADA.set(false); }
                Cauces.LOG.info("teletransporte de {} a {},{}: destino preparado en {} s sin bloquear el servidor",
                    j.getGameProfile().getName(), p.centro().x * 16, p.centro().z * 16,
                    String.format("%.1f", (System.nanoTime() - p.inicioNs()) / 1e9));
            } else if (ahora >= p.limiteTick()) {
                it.remove(); cancelados++;
                j.displayClientMessage(Component.literal("El destino aún no está listo; teletransporte cancelado. Inténtalo de nuevo en un minuto."), false);
                Cauces.LOG.warn("teletransporte de {} a {},{} cancelado tras {} s (destino sin preparar)",
                    j.getGameProfile().getName(), p.centro().x * 16, p.centro().z * 16, esperaMaximaS);
            } else if (ahora % 400 == 0) {
                ticket(p.nivel(), p.centro(), j);
            }
        }
    }

    /** Al parar el servidor (también el integrado de un solo jugador): ningún teletransporte pendiente sobrevive al mundo. */
    public static void limpiar() {
        if (!PENDIENTES.isEmpty()) Cauces.LOG.info("parada: {} teletransportes pendientes descartados", PENDIENTES.size());
        PENDIENTES.clear();
    }

    public static String estado() {
        return "teletransportes: " + PENDIENTES.size() + " pendientes, " + preparados + " aplazados y completados, "
            + inmediatos + " inmediatos, " + cancelados + " cancelados";
    }
}
