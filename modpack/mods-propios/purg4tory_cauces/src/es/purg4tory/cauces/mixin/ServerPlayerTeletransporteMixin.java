package es.purg4tory.cauces.mixin;

import es.purg4tory.cauces.TeletransportePrevio;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.RelativeMovement;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.Set;

/** Aplaza los teletransportes de jugadores a chunks sin cargar hasta que el destino esté listo (ver TeletransportePrevio). */
@Mixin(ServerPlayer.class)
public abstract class ServerPlayerTeletransporteMixin {
    @Inject(method = "teleportTo(Lnet/minecraft/server/level/ServerLevel;DDDLjava/util/Set;FF)Z",
        at = @At("HEAD"), cancellable = true)
    private void purg4tory$aplazar(ServerLevel nivel, double x, double y, double z, Set<RelativeMovement> rel,
                                   float yaw, float pitch, CallbackInfoReturnable<Boolean> cir) {
        ServerPlayer yo = (ServerPlayer) (Object) this;
        if (TeletransportePrevio.interceptar(yo, nivel, x, z, () -> yo.teleportTo(nivel, x, y, z, rel, yaw, pitch))) {
            cir.setReturnValue(true);
        }
    }

    @Inject(method = "teleportTo(Lnet/minecraft/server/level/ServerLevel;DDDFF)V", at = @At("HEAD"), cancellable = true)
    private void purg4tory$aplazar2(ServerLevel nivel, double x, double y, double z, float yaw, float pitch, CallbackInfo ci) {
        ServerPlayer yo = (ServerPlayer) (Object) this;
        if (TeletransportePrevio.interceptar(yo, nivel, x, z, () -> yo.teleportTo(nivel, x, y, z, yaw, pitch))) ci.cancel();
    }
}
