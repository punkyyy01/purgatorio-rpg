package es.purg4tory.cauces;

import it.unimi.dsi.fastutil.longs.Long2ObjectOpenHashMap;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.Registries;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.biome.Biomes;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.chunk.EmptyLevelChunk;

import java.util.IdentityHashMap;
import java.util.Map;

/**
 * Las cadenas de actualizaciones de bloques que empiezan al procesar un chunk RECIÉN GENERADO no generan otros chunks
 * de forma síncrona en el hilo principal (ver mixin.CadenaVecinosMixin, mixin.ServerChunkCacheCadenaMixin, mixin.PostProcesoMixin).
 *
 * Problema (Beta 1, un jugador, distancia 32): al pasar a «ticking» un chunk nuevo, sus fluidos pendientes se procesan; una
 * superficie de lava en contacto con agua se convierte en obsidiana bloque a bloque y cada conversión actualiza al vecino.
 * Al llegar a un chunk sin generar, Minecraft lo genera de forma SÍNCRONA en el hilo principal (con Streams Reflowing,
 * ~1 s cada uno) y la cadena sigue: el servidor deja de procesar nada durante decenas de segundos o más.
 *
 * Alcance: solo mientras el hilo principal ejecuta LevelChunk.postProcessGeneration (o una reanudación de este mismo
 * mecanismo) Y vacía la cola de CollectingNeighborUpdater. Las actualizaciones del juego normal (redstone, agua, lava,
 * pistones, granjas, jugadores, comandos) no pasan por aquí y se comportan como en Minecraft.
 * Dentro de ese alcance, pedir un chunk completo que no está cargado devuelve un chunk vacío en vez de esperarlo, y se
 * apunta qué actualización se cortó (bloque de origen y su posición). Cuando ese chunk se carga, la actualización se
 * repite (con el mismo alcance: si la cadena llega a otro chunk sin cargar, vuelve a esperar a que se cargue).
 * Lo apuntado vive en memoria: si el servidor se para antes de que el chunk se cargue, esa reanudación se pierde y el
 * contacto lava/agua de ese borde queda como lo dejaría Minecraft sin actualizar (se resuelve en cuanto algo lo actualice).
 */
public final class CadenaSinCargar {
    static volatile boolean activo = true;
    /** 0.5.0: también las cadenas del juego normal (no solo terreno nuevo); el corte se reanuda al cargar el chunk. */
    static volatile boolean global = true;
    /** Profundidad de CollectingNeighborUpdater.runUpdates en el hilo principal (solo niveles del servidor). */
    public static int profundidad;
    /** Profundidad de postProcessGeneration / reanudación en el hilo principal. */
    public static int generacion;
    /** Origen de la actualización de vecinos que se está ejecutando (solo válido con generacion > 0). */
    private static long fuentePos; private static Block fuenteBloque; private static boolean fuenteForma;

    private static final int MAX_PENDIENTES = 200_000, POR_TICK = 1024;
    /** tipos: 1 = vecino cambió (neighborChanged), 2 = forma (updateShape); un mismo origen puede cortar ambos. */
    /** nuevo = el corte ocurrió procesando terreno nuevo (se reanuda con ese mismo alcance). */
    private record Fuente(Block bloque, int tipos, boolean nuevo) {}
    /** Por nivel: chunk cortado -> (posición de origen -> bloque de origen). */
    private static final Map<ServerLevel, Long2ObjectOpenHashMap<Long2ObjectOpenHashMap<Fuente>>> PENDIENTES = new IdentityHashMap<>();
    private static int pendientes;
    private static long cortes, reanudadas, perdidas, ultimoAviso;
    private static ServerLevel nivelBioma; private static Holder<Biome> bioma;
    private CadenaSinCargar() {}

    /** Se está procesando terreno nuevo (postProcessGeneration o una reanudación). */
    public static boolean terrenoNuevo() { return generacion > 0; }

    public static boolean aplica() { return activo && profundidad > 0 && (generacion > 0 || global); }

    /** Desde los runNext de CollectingNeighborUpdater: quién origina la actualización en curso (barato: solo con generacion > 0). */
    public static void fuente(BlockPos pos, Block bloque, boolean forma) {
        if (generacion <= 0 && !global) return;
        fuentePos = pos.asLong(); fuenteBloque = bloque; fuenteForma = forma;
    }

    /** Chunk sin cargar pedido dentro del alcance: se apunta la actualización cortada y se devuelve un chunk vacío. */
    public static EmptyLevelChunk cortar(ServerLevel nivel, int x, int z) {
        if (nivel != nivelBioma) { bioma = nivel.registryAccess().registryOrThrow(Registries.BIOME).getHolderOrThrow(Biomes.PLAINS); nivelBioma = nivel; }
        cortes++;
        if (fuenteBloque != null) {
            if (pendientes < MAX_PENDIENTES) {
                var porChunk = PENDIENTES.computeIfAbsent(nivel, k -> new Long2ObjectOpenHashMap<>())
                    .computeIfAbsent(ChunkPos.asLong(x, z), k -> new Long2ObjectOpenHashMap<>());
                int tipo = fuenteForma ? 2 : 1; Fuente antes = porChunk.get(fuentePos);
                if (antes == null) pendientes++;
                porChunk.put(fuentePos, new Fuente(antes != null && !fuenteForma ? fuenteBloque : (antes != null ? antes.bloque() : fuenteBloque), (antes != null ? antes.tipos() : 0) | tipo, (antes != null && antes.nuevo()) || generacion > 0));
            } else perdidas++;
        }
        long ahora = System.nanoTime();
        if (ahora - ultimoAviso > 60_000_000_000L) {
            ultimoAviso = ahora;
            Cauces.LOG.info("cadena de bloques de terreno nuevo detenida en el borde de lo cargado (chunk {},{}); {}", x, z, estado());
        }
        return new EmptyLevelChunk(nivel, new ChunkPos(x, z), bioma);
    }

    /**
     * Al final de cada tick: repite las actualizaciones cortadas cuyos chunks ya están cargados. Primero se sacan de la
     * lista (la propia reanudación puede apuntar cortes nuevos en otros chunks) y luego se repiten, como mucho POR_TICK.
     */
    public static void reanudar(MinecraftServer s) {
        if (pendientes == 0) return;
        int presupuesto = POR_TICK;
        for (var porNivel : PENDIENTES.entrySet()) {
            if (presupuesto <= 0) break;
            ServerLevel nivel = porNivel.getKey(); var cs = nivel.getChunkSource(); var mapa = porNivel.getValue();
            java.util.List<long[]> listas = new java.util.ArrayList<>();            // {posición de origen}
            java.util.List<Fuente> bloques = new java.util.ArrayList<>();
            for (long k : mapa.keySet().toLongArray()) {
                if (presupuesto <= 0) break;
                if (cs.getChunkNow(ChunkPos.getX(k), ChunkPos.getZ(k)) == null) continue;
                var fuentes = mapa.get(k);
                for (long p : fuentes.keySet().toLongArray()) {
                    if (presupuesto-- <= 0) break;
                    bloques.add(fuentes.remove(p)); listas.add(new long[] { p }); pendientes--;
                }
                if (fuentes.isEmpty()) mapa.remove(k);
            }
            for (int i = 0; i < listas.size(); i++) {
                BlockPos p = BlockPos.of(listas.get(i)[0]); Fuente f = bloques.get(i);
                if (cs.getChunkNow(p.getX() >> 4, p.getZ() >> 4) == null) { perdidas++; continue; }   // el origen ya no está cargado
                if (f.nuevo()) generacion++;
                try {
                    if ((f.tipos() & 2) != 0) nivel.getBlockState(p).updateNeighbourShapes(nivel, p, 2);
                    if ((f.tipos() & 1) != 0) nivel.updateNeighborsAt(p, f.bloque());
                    reanudadas++;
                } catch (RuntimeException ex) {
                    Cauces.LOG.warn("reanudación de una cadena de bloques en {} falló: {}", p.toShortString(), ex.toString());
                } finally { if (f.nuevo()) generacion--; }
            }
        }
    }

    /** Al empezar cada tick: por si una excepción dejó las profundidades descuadradas. */
    public static void reiniciar() { profundidad = 0; generacion = 0; fuenteBloque = null; }

    /** Al parar el servidor (también el integrado de un solo jugador). */
    public static void limpiar() {
        if (pendientes > 0) Cauces.LOG.info("parada: {} reanudaciones de cadenas de bloques sin hacer (sus chunks no llegaron a cargarse)", pendientes);
        PENDIENTES.clear(); pendientes = 0; nivelBioma = null; bioma = null; reiniciar();
    }

    /** Solo para pruebas de laboratorio: ejecuta la acción como si ocurriera al procesar un chunk recién generado. */
    public static void comoTerrenoNuevo(Runnable r) { generacion++; try { r.run(); } finally { generacion--; } }

    public static String estado() {
        return "cadenas de terreno nuevo: " + cortes + " cargas síncronas evitadas, " + reanudadas + " reanudadas, "
            + pendientes + " pendientes, " + perdidas + " perdidas";
    }
}
