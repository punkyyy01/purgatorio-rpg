package es.purg4tory.cauces;

import com.mojang.brigadier.arguments.IntegerArgumentType;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.ModList;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.loading.FMLPaths;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.server.ServerStartedEvent;
import net.neoforged.neoforge.event.server.ServerStoppedEvent;
import net.neoforged.neoforge.event.server.ServerStoppingEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Prepara las cuencas («placas») de Streams Reflowing antes de que un jugador llegue a ellas.
 * No modifica Streams Reflowing: solo llama a métodos públicos suyos (ver PuenteSR). Solo servidor.
 */
@Mod("purg4tory_cauces")
public final class Cauces {
    static final Logger LOG = LoggerFactory.getLogger("PURG4TORY Cauces");
    /** Versiones de Streams Reflowing contra las que se comprobó la integración. */
    static final String SR_PROBADA = "2.15.2";

    private Planificador plan;
    private volatile Vigia vigia;

    public Cauces(IEventBus modBus, ModContainer contenedor) {
        // Modificador global de botín (ver LimitarBotin): se registra siempre; sin config/purg4tory_botin.json no hace nada.
        var gml = net.neoforged.neoforge.registries.DeferredRegister.create(
            net.neoforged.neoforge.registries.NeoForgeRegistries.Keys.GLOBAL_LOOT_MODIFIER_SERIALIZERS, "purg4tory_cauces");
        gml.register("limitar_botin", () -> LimitarBotin.CODEC);
        gml.register(modBus);
        Config cfg = Config.cargar(FMLPaths.CONFIGDIR.get().resolve("purg4tory_cauces.properties"));
        // La salvaguarda del guardado es un mixin sobre Minecraft: funciona con o sin Streams Reflowing.
        SalvaguardaGuardado.esperaMaxima = Math.max(1, cfg.esperaGuardadoS);
        NeoForge.EVENT_BUS.addListener(ServerStartedEvent.class, e -> LOG.info("salvaguarda del guardado completo: {}",
            e.getServer().overworld().getChunkSource().chunkMap instanceof SalvaguardaGuardado.Marca ? "ACTIVA" : "NO APLICADA"));
        SalvaguardaGuardado.esperaParada = cfg.esperaParadaS;
        NeoForge.EVENT_BUS.addListener(ServerStoppingEvent.class, e -> SalvaguardaGuardado.inicioParadaNs = System.nanoTime());
        NeoForge.EVENT_BUS.addListener(ServerStoppedEvent.class, e -> TeletransportePrevio.limpiar());
        CadenaSinCargar.activo = cfg.cadenaSinCargar;
        CadenaSinCargar.global = cfg.cadenasGlobales;
        SondeoSpawn.activo = cfg.spawnsSinEsperar;
        NeoForge.EVENT_BUS.addListener(net.neoforged.neoforge.event.server.ServerStartedEvent.class, e -> SondeoSpawn.hilo = Thread.currentThread());
        NeoForge.EVENT_BUS.addListener(ServerStoppedEvent.class, e -> { SondeoSpawn.hilo = null; SondeoSpawn.profundidad = 0; });
        SinEsperas.consultas = cfg.consultasSinEsperar; SinEsperas.cargado = cfg.cargadoEsListo; SinEsperas.movimiento = cfg.movimientoAListo;
        NeoForge.EVENT_BUS.addListener(ServerTickEvent.Pre.class, e -> CadenaSinCargar.reiniciar());
        NeoForge.EVENT_BUS.addListener(ServerTickEvent.Post.class, e -> {
            try { CadenaSinCargar.reanudar(e.getServer()); }
            catch (RuntimeException ex) { LOG.error("reanudación de cadenas de bloques: error inesperado; se descartan las pendientes", ex); CadenaSinCargar.limpiar(); }
        });
        NeoForge.EVENT_BUS.addListener(ServerStoppedEvent.class, e -> { LOG.info("al parar: {}; {}; spawns cortados por terreno no listo: {}", CadenaSinCargar.estado(), SinEsperas.estado(), SondeoSpawn.cortes); CadenaSinCargar.limpiar(); });
        NeoForge.EVENT_BUS.addListener(ServerStartedEvent.class, e -> LOG.info("cadenas de bloques sin cargar chunks: {}; consultas sin esperar: {}; cargado = listo: {}", cfg.cadenaSinCargar ? (cfg.cadenasGlobales ? "ACTIVO (todas)" : "ACTIVO (terreno nuevo)") : "desactivado", cfg.consultasSinEsperar, cfg.cargadoEsListo));
        TeletransportePrevio.activo = cfg.teletransportePrevio;
        TeletransportePrevio.esperaMaximaS = Math.max(5, cfg.esperaTeletransporteS);
        if (cfg.teletransportePrevio) {
            NeoForge.EVENT_BUS.addListener(ServerTickEvent.Post.class, e -> TeletransportePrevio.tick(e.getServer()));
            NeoForge.EVENT_BUS.addListener(RegisterCommandsEvent.class, e -> e.getDispatcher().register(
                Commands.literal("cauces_tp").requires(src -> src.hasPermission(3))
                    .executes(c -> responder(c.getSource(), TeletransportePrevio.estado() + "; " + SalvaguardaGuardado.estadoDiferidas() + "; " + CadenaSinCargar.estado() + "; " + SinEsperas.estado() + "; " + LimitarBotin.estado()))));
        }
        if (!cfg.activado) { LOG.info("planificador y vigía desactivados en la configuración"); return; }
        var sr = ModList.get().getModContainerById("streamsreflowing");
        if (sr.isEmpty()) { LOG.info("Streams Reflowing no está instalado: no hay nada que preparar"); return; }
        String v = sr.get().getModInfo().getVersion().toString();
        if (!v.equals(SR_PROBADA) && !cfg.permitirOtraVersionSR) {
            LOG.warn("Streams Reflowing {} no es la versión probada ({}); el planificador queda desactivado "
                + "(permitirOtraVersionSR=true para probarlo)", v, SR_PROBADA);
            return;
        }
        plan = new Planificador(cfg);
        // Un vigía nuevo por cada arranque de servidor: en un solo jugador el mismo proceso abre y cierra varios mundos
        // (0.4.0 reutilizaba uno ya terminado y a partir del segundo mundo no vigilaba nada).
        NeoForge.EVENT_BUS.addListener(ServerStartedEvent.class, e -> {
            plan.arrancar(e.getServer());
            if (cfg.vigiaS > 0) { vigia = new Vigia(cfg.vigiaS, true); vigia.arrancar(e.getServer()); }
        });
        NeoForge.EVENT_BUS.addListener(ServerStoppingEvent.class, e -> plan.detener());
        // El vigía sigue durante la parada (un guardado final colgado también se diagnostica) y termina al final.
        NeoForge.EVENT_BUS.addListener(ServerStoppedEvent.class, e -> { Vigia vg = vigia; vigia = null; if (vg != null) vg.terminar(); });
        NeoForge.EVENT_BUS.addListener(ServerTickEvent.Post.class, e -> {
            Vigia vg = vigia;
            if (vg != null) vg.tick();
            plan.tick(e.getServer());
        });
        NeoForge.EVENT_BUS.addListener(RegisterCommandsEvent.class, this::comandos);
    }

    private void comandos(RegisterCommandsEvent e) {
        e.getDispatcher().register(Commands.literal("cauces").requires(s -> s.hasPermission(3))
            .then(Commands.literal("estado").executes(c -> responder(c.getSource(), plan.estado())))
            .then(Commands.literal("colas").executes(c -> responder(c.getSource(), "colas SR: " + PuenteSR.colas())))
            .then(Commands.literal("pausa").executes(c -> responder(c.getSource(), plan.pausar(true))))
            .then(Commands.literal("reanudar").executes(c -> responder(c.getSource(), plan.pausar(false))))
            .then(Commands.literal("planificar").then(Commands.argument("radio", IntegerArgumentType.integer(0, 30000))
                .executes(c -> responder(c.getSource(), plan.planificar(IntegerArgumentType.getInteger(c, "radio")))))));
    }

    private static int responder(CommandSourceStack s, String texto) {
        s.sendSuccess(() -> Component.literal(texto), false);
        return 1;
    }
}
