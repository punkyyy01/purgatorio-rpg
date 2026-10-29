package es.purg4tory.cauces.mixin;

import com.llamalad7.mixinextras.injector.wrapmethod.WrapMethod;
import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.LevelReader;
import es.purg4tory.cauces.SondeoSpawnUtil;
import org.spongepowered.asm.mixin.Mixin;

/** Comprobaciones de spawn de una criatura: si tocan un chunk no listo, fallan en vez de esperar (ver SondeoSpawn). */
@Mixin(Mob.class)
public abstract class SondeoSpawnMixin {
    @WrapMethod(method = "checkSpawnObstruction(Lnet/minecraft/world/level/LevelReader;)Z")
    private boolean purg4tory$obstruccion(LevelReader nivel, Operation<Boolean> original) {
        return SondeoSpawnUtil.envolver(() -> original.call(nivel));
    }

    @WrapMethod(method = "checkSpawnRules(Lnet/minecraft/world/level/LevelAccessor;Lnet/minecraft/world/entity/MobSpawnType;)Z")
    private boolean purg4tory$reglas(LevelAccessor nivel, MobSpawnType tipo, Operation<Boolean> original) {
        return SondeoSpawnUtil.envolver(() -> original.call(nivel, tipo));
    }
}
