package es.purg4tory.cauces.mixin;

import es.purg4tory.cauces.SinEsperas;
import net.minecraft.network.protocol.game.ClientboundMoveVehiclePacket;
import net.minecraft.network.protocol.game.ServerboundMovePlayerPacket;
import net.minecraft.network.protocol.game.ServerboundMoveVehiclePacket;
import net.minecraft.world.entity.Entity;
import net.minecraft.server.level.ServerChunkCache;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.network.ServerGamePacketListenerImpl;
import net.minecraft.world.phys.Vec3;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Un jugador no entra en un chunk cuyo entorno 3×3 aún no está listo (ver SinEsperas.movimiento): el servidor lo devuelve a
 * su posición, como hace el propio cliente con su chunk. Así lo que se mira alrededor del jugador cada tick (colisiones,
 * asfixia, mods que escanean bloques cercanos) nunca pide un chunk en generación.
 */
@Mixin(ServerGamePacketListenerImpl.class)
public abstract class MovimientoListoMixin {
    @Shadow public ServerPlayer player;
    @Shadow private Vec3 awaitingPositionFromClient;
    @Shadow public abstract void teleport(double x, double y, double z, float yaw, float pitch);

    @Inject(method = "handleMovePlayer", at = @At(value = "INVOKE", shift = At.Shift.AFTER,
        target = "Lnet/minecraft/network/protocol/PacketUtils;ensureRunningOnSameThread(Lnet/minecraft/network/protocol/Packet;Lnet/minecraft/network/PacketListener;Lnet/minecraft/server/level/ServerLevel;)V"),
        cancellable = true)
    private void purg4tory$soloAListo(ServerboundMovePlayerPacket p, CallbackInfo ci) {
        if (!SinEsperas.movimiento || awaitingPositionFromClient != null || player.isPassenger() || !p.hasPosition()) return;
        double x = p.getX(player.getX()), z = p.getZ(player.getZ());
        if (Double.isNaN(x) || Double.isNaN(z) || Math.abs(x) > 3.0E7 || Math.abs(z) > 3.0E7) return;   // Minecraft lo trata
        if (listo(player, x, z)) return;
        SinEsperas.movimientosFrenados++;
        teleport(player.getX(), player.getY(), player.getZ(), player.getYRot(), player.getXRot());
        ci.cancel();
    }

    /** Lo mismo para vehículos que controla el jugador (caballo, barco, etc.): se le devuelve a su posición como hace Minecraft. */
    @Inject(method = "handleMoveVehicle", at = @At(value = "INVOKE", shift = At.Shift.AFTER,
        target = "Lnet/minecraft/network/protocol/PacketUtils;ensureRunningOnSameThread(Lnet/minecraft/network/protocol/Packet;Lnet/minecraft/network/PacketListener;Lnet/minecraft/server/level/ServerLevel;)V"),
        cancellable = true)
    private void purg4tory$vehiculoAListo(ServerboundMoveVehiclePacket p, CallbackInfo ci) {
        if (!SinEsperas.movimiento || awaitingPositionFromClient != null) return;
        Entity v = player.getRootVehicle();
        if (v == player || v.getControllingPassenger() != player) return;
        double x = p.getX(), z = p.getZ();
        if (Double.isNaN(x) || Double.isNaN(z) || Math.abs(x) > 3.0E7 || Math.abs(z) > 3.0E7) return;
        if (listo(v, x, z)) return;
        SinEsperas.movimientosFrenados++;
        ((ServerGamePacketListenerImpl) (Object) this).send(new ClientboundMoveVehiclePacket(v));
        ci.cancel();
    }

    /** Destino en el mismo chunk, o chunk de destino con su entorno 3×3 listo. */
    private static boolean listo(Entity e, double x, double z) {
        int cx = (int) Math.floor(x) >> 4, cz = (int) Math.floor(z) >> 4;
        if (cx == e.chunkPosition().x && cz == e.chunkPosition().z) return true;
        ServerChunkCache cs = ((net.minecraft.server.level.ServerLevel) e.level()).getChunkSource();
        for (int dx = -1; dx <= 1; dx++) for (int dz = -1; dz <= 1; dz++)
            if (cs.getChunkNow(cx + dx, cz + dz) == null) return false;
        return true;
    }
}
