package es.purg4tory.diagtick.mixin;

import com.llamalad7.mixinextras.injector.wrapmethod.WrapMethod;
import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import es.purg4tory.diagtick.Esperas;
import net.minecraft.server.level.ServerChunkCache;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.chunk.status.ChunkStatus;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;

/** Mide cada getChunk del hilo principal (envolviendo el método entero, también lo que otros mods inyecten); las lentas se registran con su origen. */
@Mixin(value = ServerChunkCache.class, priority = 2000)
public abstract class EsperaChunkMixin {
    @Shadow @Final Thread mainThread;
    @Shadow @Final public ServerLevel level;

    @WrapMethod(method = "getChunk(IILnet/minecraft/world/level/chunk/status/ChunkStatus;Z)Lnet/minecraft/world/level/chunk/ChunkAccess;")
    private ChunkAccess diagtick$medir(int x, int z, ChunkStatus st, boolean carga, Operation<ChunkAccess> original) {
        if (Thread.currentThread() != mainThread) return original.call(x, z, st, carga);
        Esperas.entrar();
        ChunkAccess r = null;
        try { r = original.call(x, z, st, carga); return r; }
        finally { Esperas.salir(level, x, z, st, carga, r); }
    }
}
