package es.purg4tory.cauces.mixin;

import com.llamalad7.mixinextras.injector.wrapmethod.WrapMethod;
import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import net.minecraft.core.BlockPos;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.SpawnPlacements;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.ServerLevelAccessor;
import es.purg4tory.cauces.SondeoSpawnUtil;
import org.spongepowered.asm.mixin.Mixin;

/** Comprobaciones de posición de spawn por tipo: si tocan un chunk no listo, fallan en vez de esperar (ver SondeoSpawn). */
@Mixin(SpawnPlacements.class)
public abstract class SpawnPlacementsSondeoMixin {
    @WrapMethod(method = "isSpawnPositionOk(Lnet/minecraft/world/entity/EntityType;Lnet/minecraft/world/level/LevelReader;Lnet/minecraft/core/BlockPos;)Z")
    private static boolean purg4tory$posicion(EntityType<?> tipo, LevelReader nivel, BlockPos pos, Operation<Boolean> original) {
        return SondeoSpawnUtil.envolver(() -> original.call(tipo, nivel, pos));
    }

    @WrapMethod(method = "checkSpawnRules(Lnet/minecraft/world/entity/EntityType;Lnet/minecraft/world/level/ServerLevelAccessor;Lnet/minecraft/world/entity/MobSpawnType;Lnet/minecraft/core/BlockPos;Lnet/minecraft/util/RandomSource;)Z")
    private static boolean purg4tory$reglas(EntityType<?> tipo, ServerLevelAccessor nivel, MobSpawnType st, BlockPos pos, RandomSource r, Operation<Boolean> original) {
        return SondeoSpawnUtil.envolver(() -> original.call(tipo, nivel, st, pos, r));
    }
}
