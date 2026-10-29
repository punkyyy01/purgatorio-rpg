package es.purg4tory.cauces.mixin;

import es.purg4tory.cauces.CadenaSinCargar;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Apunta el origen de cada actualización de vecinos (MultiNeighborUpdate); solo se usa al procesar terreno nuevo (ver CadenaSinCargar). */
@Mixin(targets = "net.minecraft.world.level.redstone.CollectingNeighborUpdater$MultiNeighborUpdate")
public abstract class FuenteMultiMixin {
    @Shadow @Final private BlockPos sourcePos; @Shadow @Final private Block sourceBlock;
    @Inject(method = "runNext(Lnet/minecraft/world/level/Level;)Z", at = @At("HEAD"))
    private void purg4tory$fuente(Level l, CallbackInfoReturnable<Boolean> cir) { CadenaSinCargar.fuente(sourcePos, sourceBlock, false); }
}
