package es.purg4tory.cauces.mixin;

import es.purg4tory.cauces.SalvaguardaGuardado;
import net.minecraft.server.level.ChunkHolder;
import net.minecraft.server.level.ChunkMap;
import net.minecraft.util.thread.BlockableEventLoop;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import java.util.ArrayList;
import java.util.List;
import java.util.function.BooleanSupplier;

/**
 * Salvaguarda del guardado completo («save-all flush» y parada del servidor) en Minecraft 1.21.1.
 *
 * Problema (vanilla, muy agravado por Streams Reflowing, que retiene pasos de generación esperando cuencas):
 * saveAllChunks(true) vacía la cola de descargas con processUnloads(() -> true). Un chunk retenido por una tarea de
 * generación (contador > 0) cuyo futuro de guardado ya ha terminado se vuelve a encolar al instante para siempre, y
 * esas tareas solo avanzan si el hilo principal atiende su trabajo pendiente: bucle sin fin en el hilo principal.
 *
 * Arreglo: durante el guardado completo, esos chunks se apartan en vez de reencolarse. Al terminar la cola, el hilo
 * principal atiende trabajo pendiente (managedBlock, igual que hace el propio saveAllChunks antes) un tiempo
 * acotado; los que quedan libres se descargan y guardan normalmente; los que sigan retenidos se devuelven a la
 * cola normal y se descargan en los ticks siguientes. Los chunks modificados por jugadores ya los guarda la primera
 * parte de saveAllChunks (no se toca).
 */
@Mixin(ChunkMap.class)
public abstract class ChunkMapGuardadoMixin implements SalvaguardaGuardado.Marca {
    @Shadow @Final private BlockableEventLoop<Runnable> mainThreadExecutor;
    @Shadow private void scheduleUnload(long pos, ChunkHolder holder) {}
    @Shadow private void processUnloads(BooleanSupplier hasMoreTime) {}

    @Unique private boolean purg4tory$guardadoCompleto;
    @Unique private final List<Object[]> purg4tory$apartados = new ArrayList<>();
    /** Fuera del guardado completo: descargas retenidas por generación, que se reintentan una vez por tick. */
    @Unique private final List<Object[]> purg4tory$diferidos = new ArrayList<>();

    @Inject(method = "saveAllChunks(Z)V", at = @At("HEAD"))
    private void purg4tory$inicio(boolean flush, CallbackInfo ci) {
        if (flush) { purg4tory$guardadoCompleto = true; purg4tory$apartados.clear(); }
    }

    @Inject(method = "scheduleUnload(JLnet/minecraft/server/level/ChunkHolder;)V", at = @At("HEAD"), cancellable = true)
    private void purg4tory$apartar(long pos, ChunkHolder holder, CallbackInfo ci) {
        if (holder.getGenerationRefCount() != 0 && holder.getSaveSyncFuture().isDone()) {
            // Vanilla lo reencola al instante; mientras la generación lo retenga eso es un bucle que consume todo el
            // presupuesto del tick en processUnloads (visto con generación pesada: 95 % del hilo principal).
            (purg4tory$guardadoCompleto ? purg4tory$apartados : purg4tory$diferidos).add(new Object[] { pos, holder });
            ci.cancel();
        }
    }

    @Inject(method = "saveAllChunks(Z)V", at = @At(value = "INVOKE",
        target = "Lnet/minecraft/server/level/ChunkMap;flushWorker()V"))
    private void purg4tory$resolverApartados(boolean flush, CallbackInfo ci) {
        if (!flush) return;
        try {
            if (purg4tory$apartados.isEmpty()) return;
            int total = purg4tory$apartados.size();
            long limite = System.nanoTime() + SalvaguardaGuardado.esperaMaximaS() * 1_000_000_000L;
            long t0 = System.nanoTime();
            // Dejar que avancen las tareas de generación que los retienen (trabajo del hilo principal y luz).
            mainThreadExecutor.managedBlock(() -> System.nanoTime() > limite
                || purg4tory$apartados.stream().allMatch(a -> ((ChunkHolder) a[1]).getGenerationRefCount() == 0));
            int libres = 0;
            purg4tory$guardadoCompleto = false;           // a partir de aquí, comportamiento normal de Minecraft
            for (Object[] a : purg4tory$apartados) {
                if (((ChunkHolder) a[1]).getGenerationRefCount() == 0) libres++;
                scheduleUnload((Long) a[0], (ChunkHolder) a[1]);
            }
            if (libres > 0) {
                long fin = System.nanoTime() + 10_000_000_000L;   // descargar y guardar los liberados (acotado)
                processUnloads(() -> System.nanoTime() < fin);
            }
            SalvaguardaGuardado.informar(total, libres, (System.nanoTime() - t0) / 1e9);
        } finally {
            purg4tory$guardadoCompleto = false;
            purg4tory$apartados.clear();
        }
    }

    /** Una vez por tick: reintenta las descargas diferidas (las que sigan retenidas vuelven a diferirse). */
    @Inject(method = "tick(Ljava/util/function/BooleanSupplier;)V", at = @At("HEAD"))
    private void purg4tory$reintentar(BooleanSupplier hasMoreTime, CallbackInfo ci) {
        if (purg4tory$diferidos.isEmpty() || purg4tory$guardadoCompleto) return;
        Object[][] copia = purg4tory$diferidos.toArray(new Object[0][]);
        purg4tory$diferidos.clear();
        SalvaguardaGuardado.contarDiferidas(copia.length);
        for (Object[] a : copia) scheduleUnload((Long) a[0], (ChunkHolder) a[1]);
    }

    /** Bucle de parada de Minecraft (while hasWork): acotado en el tiempo para poder llegar al guardado final. */
    @Inject(method = "hasWork()Z", at = @At("RETURN"), cancellable = true)
    private void purg4tory$limitarParada(org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable<Boolean> cir) {
        if (cir.getReturnValueZ() && SalvaguardaGuardado.paradaVencida()) cir.setReturnValue(false);
    }

    @Inject(method = "saveAllChunks(Z)V", at = @At("RETURN"))
    private void purg4tory$fin(boolean flush, CallbackInfo ci) {
        if (flush) { purg4tory$guardadoCompleto = false; purg4tory$apartados.clear(); }
    }
}
