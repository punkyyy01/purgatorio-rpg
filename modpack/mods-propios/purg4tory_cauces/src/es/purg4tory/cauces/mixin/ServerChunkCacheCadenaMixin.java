package es.purg4tory.cauces.mixin;

import es.purg4tory.cauces.CadenaSinCargar;
import net.minecraft.server.level.ChunkHolder;
import net.minecraft.server.level.ChunkLevel;
import net.minecraft.server.level.ServerChunkCache;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.chunk.status.ChunkStatus;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Dentro de una cadena de actualizaciones de vecinos del hilo principal, un chunk completo que no está listo no se espera
 * (ver CadenaSinCargar):
 *  - al procesar terreno nuevo (postProcessGeneration o su reanudación): ningún chunk no listo (0.4.1);
 *  - en el juego normal (0.5.0, cadenasGlobales): solo los chunks que YA están en el área cargada pero aún se generan o
 *    leen del disco (llegarán solos en breve y la cadena se reanuda). Un chunk descargado de verdad se carga como en Minecraft.
 */
@Mixin(value = ServerChunkCache.class, priority = 1500)
public abstract class ServerChunkCacheCadenaMixin {
    @Shadow @Final Thread mainThread;
    @Shadow @Final public ServerLevel level;
    @Shadow public abstract net.minecraft.world.level.chunk.LevelChunk getChunkNow(int x, int z);
    @Shadow private ChunkHolder getVisibleChunkIfPresent(long pos) { throw new AssertionError(); }

    private static final int NIVEL_COMPLETO = ChunkLevel.byStatus(net.minecraft.server.level.FullChunkStatus.FULL);

    @Inject(method = "getChunk(IILnet/minecraft/world/level/chunk/status/ChunkStatus;Z)Lnet/minecraft/world/level/chunk/ChunkAccess;",
        at = @At("HEAD"), cancellable = true)
    private void purg4tory$noEsperar(int x, int z, ChunkStatus estado, boolean cargar, CallbackInfoReturnable<ChunkAccess> cir) {
        if (!cargar || estado != ChunkStatus.FULL || !CadenaSinCargar.aplica() || Thread.currentThread() != mainThread) return;
        if (getChunkNow(x, z) != null) return;
        if (!CadenaSinCargar.terrenoNuevo()) {
            ChunkHolder h = getVisibleChunkIfPresent(ChunkPos.asLong(x, z));
            if (h == null || h.getTicketLevel() > NIVEL_COMPLETO) return;   // descargado de verdad: como Minecraft
        }
        cir.setReturnValue(CadenaSinCargar.cortar(level, x, z));
    }
}
