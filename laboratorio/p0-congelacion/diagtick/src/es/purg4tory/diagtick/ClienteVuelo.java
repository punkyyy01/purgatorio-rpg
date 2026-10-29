package es.purg4tory.diagtick;

import net.minecraft.client.Minecraft;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import net.neoforged.neoforge.common.NeoForge;

/** SOLO LABORATORIO. Vuelo real del cliente: mantiene W + esprint en vuelo creativo mirando a +X (como un jugador). */
final class ClienteVuelo {
    static final double ALTURA = 330;   // por encima del límite de construcción (320): sin montañas en la ruta
    static volatile long finMs, inicioMs; static volatile boolean activo; static volatile double giroPorMin, rumbo = -90;
    static void registrar() {
        NeoForge.EVENT_BUS.addListener(ClientTickEvent.Post.class, e -> tick());
    }
    static void empezar(long segundos, double giro, double rumboIni) { rumbo = rumboIni; inicioMs = System.currentTimeMillis(); finMs = inicioMs + segundos * 1000; giroPorMin = giro; activo = true; }
    static void parar() { finMs = 0; }
    /** Como «Guardar y salir» del menú de pausa: desconecta y el servidor integrado guarda y se para. */
    static void salir() {
        Minecraft mc = Minecraft.getInstance();
        mc.execute(() -> {
            if (mc.level != null) mc.level.disconnect();
            mc.disconnect(new net.minecraft.client.gui.screens.GenericMessageScreen(net.minecraft.network.chat.Component.literal("Guardando (diagtick)")));
            mc.setScreen(new net.minecraft.client.gui.screens.TitleScreen());
        });
    }
    static void tick() {
        if (!activo) return;
        Minecraft mc = Minecraft.getInstance(); var p = mc.player;
        boolean seguir = System.currentTimeMillis() < finMs;
        mc.options.keyUp.setDown(seguir); mc.options.keySprint.setDown(seguir);
        mc.options.keyJump.setDown(seguir && p != null && p.getY() < ALTURA);
        if (!seguir) { activo = false; DiagTick.escribir(DiagTick.resumen, "vuelo terminado"); return; }
        if (p == null) return;
        if (mc.screen != null) mc.setScreen(null);
        if (p.getAbilities().mayfly && !p.getAbilities().flying) { p.getAbilities().flying = true; p.onUpdateAbilities(); }
        p.setYRot((float) (rumbo + giroPorMin * (System.currentTimeMillis() - inicioMs) / 60000.0)); p.setXRot(0f); p.setSprinting(true);
    }
}
