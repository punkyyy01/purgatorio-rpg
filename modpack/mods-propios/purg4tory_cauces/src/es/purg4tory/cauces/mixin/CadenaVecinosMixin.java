package es.purg4tory.cauces.mixin;

import es.purg4tory.cauces.CadenaSinCargar;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.redstone.CollectingNeighborUpdater;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Marca cuándo el hilo principal está vaciando una cola de actualizaciones de vecinos (ver CadenaSinCargar). */
@Mixin(CollectingNeighborUpdater.class)
public abstract class CadenaVecinosMixin {
    @Shadow @Final private Level level;

    @Inject(method = "runUpdates()V", at = @At("HEAD"))
    private void purg4tory$entrar(CallbackInfo ci) {
        if (level instanceof ServerLevel s && s.getServer().isSameThread()) CadenaSinCargar.profundidad++;
    }

    @Inject(method = "runUpdates()V", at = @At("RETURN"))
    private void purg4tory$salir(CallbackInfo ci) {
        if (level instanceof ServerLevel s && s.getServer().isSameThread() && CadenaSinCargar.profundidad > 0) CadenaSinCargar.profundidad--;
    }
}
