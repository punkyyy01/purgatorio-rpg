package es.purg4tory.cauces.mixin;

import es.purg4tory.cauces.SinEsperas;
import net.minecraft.server.level.ChunkHolder;
import net.minecraft.server.level.ServerChunkCache;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.level.chunk.status.ChunkStatus;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Consultas «solo si está cargado» del hilo principal sin esperar a la generación (ver SinEsperas). */
@Mixin(value = ServerChunkCache.class, priority = 1500)
public abstract class ServerChunkCacheSinEsperaMixin {
    @Shadow @Final Thread mainThread;
    @Shadow private ChunkHolder getVisibleChunkIfPresent(long pos) { throw new AssertionError(); }
    @Shadow public abstract LevelChunk getChunkNow(int x, int z);

    @Inject(method = "getChunk(IILnet/minecraft/world/level/chunk/status/ChunkStatus;Z)Lnet/minecraft/world/level/chunk/ChunkAccess;",
        at = @At("HEAD"), cancellable = true)
    private void purg4tory$sinEsperar(int x, int z, ChunkStatus estado, boolean cargar, CallbackInfoReturnable<ChunkAccess> cir) {
        if (cargar) {
            // dentro de una comprobación de spawn (SondeoSpawn): un chunk que no está listo hace fallar la comprobación
            if (es.purg4tory.cauces.SondeoSpawn.profundidad > 0 && Thread.currentThread() == mainThread && !listo(x, z, estado))
                throw es.purg4tory.cauces.SondeoSpawn.CORTE;
            return;
        }
        if (!SinEsperas.consultas || Thread.currentThread() != mainThread) return;
        ChunkHolder h = getVisibleChunkIfPresent(ChunkPos.asLong(x, z));
        if (h == null || h.currentlyLoading != null) return;          // Minecraft responde al momento
        if (h.getChunkIfPresent(estado) != null) return;              // listo: Minecraft lo devuelve al momento
        SinEsperas.evitadas++;
        cir.setReturnValue(null);                                     // en generación: «no está», sin esperar
    }

    private boolean listo(int x, int z, ChunkStatus estado) {
        ChunkHolder h = getVisibleChunkIfPresent(ChunkPos.asLong(x, z));
        if (h == null) return false;
        if (h.currentlyLoading != null) return true;
        return h.getChunkIfPresent(estado) != null;
    }

    @Inject(method = "hasChunk(II)Z", at = @At("HEAD"), cancellable = true)
    private void purg4tory$cargadoEsListo(int x, int z, CallbackInfoReturnable<Boolean> cir) {
        if (!SinEsperas.cargado || Thread.currentThread() != mainThread) return;
        if (getChunkNow(x, z) == null) { SinEsperas.cargadoNo++; cir.setReturnValue(false); }
    }
}
