package es.purg4tory.cauces;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import it.unimi.dsi.fastutil.objects.ObjectArrayList;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.storage.loot.LootContext;
import net.minecraft.world.level.storage.loot.predicates.LootItemCondition;
import net.neoforged.fml.loading.FMLPaths;
import net.neoforged.neoforge.common.loot.IGlobalLootModifier;
import net.neoforged.neoforge.common.loot.LootModifier;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;
import java.util.regex.Pattern;

/**
 * Modificador global de botín: recorta, en cofres concretos, la cantidad de objetos de alto nivel (diamante, netherita, tótems…).
 *
 * No copia ni modifica las tablas de botín de otros mods: actúa sobre el resultado ya generado, con una probabilidad de
 * conservar cada objeto de alto nivel por tabla (config/purg4tory_botin.json, generado por herramientas/equilibrar_botin.py a
 * partir de una auditoría de los jars). Una tabla que no figura en el archivo no se toca. Los cofres de Lootr pasan por aquí
 * igualmente (Lootr genera su botín con LootTable#getRandomItems).
 */
public final class LimitarBotin extends LootModifier {
    public static final MapCodec<LimitarBotin> CODEC = RecordCodecBuilder.mapCodec(inst -> codecStart(inst).apply(inst, LimitarBotin::new));
    private LimitarBotin(LootItemCondition[] c) { super(c); }
    static final Pattern PREMIUM = Pattern.compile("(netherite|diamond|enchanted_golden_apple|elytra|totem|nether_star|heart_of_the_sea|trident|mace|echo_shard|beacon|dragon|wither|ancient_debris|emerald_block|golden_apple)");
    static final Pattern EQUIPO_NETHERITA = Pattern.compile("netherite_(helmet|chestplate|leggings|boots|sword|axe|pickaxe|shovel|hoe)$");

    record Regla(double conservar, boolean sinEquipoNetherita) {}
    private static volatile Map<ResourceLocation, Regla> reglas;
    static long cofres, premiumAntes, premiumDespues;

    static Map<ResourceLocation, Regla> reglas() {
        Map<ResourceLocation, Regla> r = reglas;
        if (r != null) return r;
        synchronized (LimitarBotin.class) {
            if (reglas != null) return reglas;
            Map<ResourceLocation, Regla> m = new HashMap<>();
            Path p = FMLPaths.CONFIGDIR.get().resolve("purg4tory_botin.json");
            try {
                if (Files.exists(p)) {
                    JsonObject o = new Gson().fromJson(Files.readString(p), JsonObject.class).getAsJsonObject("tablas");
                    for (var e : o.entrySet()) {
                        JsonObject t = e.getValue().getAsJsonObject();
                        m.put(ResourceLocation.parse(e.getKey()), new Regla(t.get("conservar").getAsDouble(),
                            t.has("sinEquipoNetherita") && t.get("sinEquipoNetherita").getAsBoolean()));
                    }
                    Cauces.LOG.info("botín: {} tablas con límite de objetos de alto nivel (config/purg4tory_botin.json)", m.size());
                } else Cauces.LOG.info("botín: no existe config/purg4tory_botin.json; no se limita ningún cofre");
            } catch (Exception ex) { Cauces.LOG.warn("botín: config/purg4tory_botin.json ilegible ({}); no se limita ningún cofre", ex.toString()); m.clear(); }
            return reglas = Map.copyOf(m);
        }
    }

    @Override
    protected ObjectArrayList<ItemStack> doApply(ObjectArrayList<ItemStack> loot, LootContext ctx) {
        ResourceLocation id = ctx.getQueriedLootTableId();
        Regla r = id == null ? null : reglas().get(id);
        if (r == null) return loot;
        cofres++;
        for (int i = loot.size() - 1; i >= 0; i--) {
            String nombre = BuiltInRegistries.ITEM.getKey(loot.get(i).getItem()).getPath();
            boolean premium = PREMIUM.matcher(nombre).find();
            if (premium) premiumAntes++;
            boolean quitar = (r.sinEquipoNetherita() && EQUIPO_NETHERITA.matcher(nombre).find())
                || (premium && ctx.getRandom().nextDouble() >= r.conservar());
            if (quitar) loot.remove(i); else if (premium) premiumDespues++;
        }
        return loot;
    }

    @Override public MapCodec<? extends IGlobalLootModifier> codec() { return CODEC; }
    static String estado() {
        return "botín: " + cofres + " cofres con límite generados; objetos de alto nivel por cofre " + String.format("%.2f", cofres == 0 ? 0 : (double) premiumAntes / cofres)
            + " antes del límite, " + String.format("%.2f", cofres == 0 ? 0 : (double) premiumDespues / cofres) + " después";
    }
}
