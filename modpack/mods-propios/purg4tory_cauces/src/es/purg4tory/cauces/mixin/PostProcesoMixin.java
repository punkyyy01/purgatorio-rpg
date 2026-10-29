package es.purg4tory.cauces.mixin;

import es.purg4tory.cauces.CadenaSinCargar;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.chunk.LevelChunk;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Marca el procesado de un chunk recién generado (fluidos y bloques pendientes de la generación); ver CadenaSinCargar. */
@Mixin(LevelChunk.class)
public abstract class PostProcesoMixin {
    @Inject(method = "postProcessGeneration()V", at = @At("HEAD"))
    private void purg4tory$entrar(CallbackInfo ci) {
        if (((LevelChunk) (Object) this).getLevel() instanceof ServerLevel s && s.getServer().isSameThread()) CadenaSinCargar.generacion++;
    }

    @Inject(method = "postProcessGeneration()V", at = @At("RETURN"))
    private void purg4tory$salir(CallbackInfo ci) {
        if (((LevelChunk) (Object) this).getLevel() instanceof ServerLevel s && s.getServer().isSameThread() && CadenaSinCargar.generacion > 0) CadenaSinCargar.generacion--;
    }
}
