package es.purg4tory.cauces;

import java.util.function.BooleanSupplier;

/** Envoltura común de SondeoSpawnMixin y SpawnPlacementsSondeoMixin. */
public final class SondeoSpawnUtil {
    private SondeoSpawnUtil() {}
    public static boolean envolver(BooleanSupplier comprobacion) {
        if (!SondeoSpawn.activo || Thread.currentThread() != SondeoSpawn.hilo) return comprobacion.getAsBoolean();
        SondeoSpawn.profundidad++;
        try { return comprobacion.getAsBoolean(); }
        catch (RuntimeException e) {
            if (e != SondeoSpawn.CORTE) throw e;
            SondeoSpawn.cortes++;
            return false;
        } finally { SondeoSpawn.profundidad--; }
    }
}
