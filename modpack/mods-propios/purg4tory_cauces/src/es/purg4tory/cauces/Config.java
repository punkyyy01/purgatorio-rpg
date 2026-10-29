package es.purg4tory.cauces;

import java.io.IOException;
import java.io.Reader;
import java.io.Writer;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Properties;

/** Configuración en config/purg4tory_cauces.properties (se crea con valores por defecto si no existe). */
final class Config {
    boolean activado = true;
    boolean permitirOtraVersionSR = false;
    /** false = no pedir cuencas (solo queda el vigía de diagnóstico). */
    boolean planificar = true;
    /** Segundos por delante de cada jugador que se intentan tener preparados (mínimo 1,5 cuencas). */
    int horizonteS = 90;
    /** Segundos sin completar un tick del servidor tras los que el vigía vuelca un diagnóstico. 0 = sin vigía. */
    int vigiaS = 20;
    /** Guardado completo: segundos máximos para liberar chunks retenidos por generación en curso (salvaguarda). */
    int esperaGuardadoS = 30;
    /** Parada: segundos máximos que Minecraft espera a chunks en generación antes del guardado final. 0 = sin límite. */
    int esperaParadaS = 60;
    /** Aplazar teletransportes de jugadores a terreno sin cargar hasta que el destino esté listo (no bloquea el servidor). */
    boolean teletransportePrevio = true;
    /** Segundos máximos de espera del destino antes de cancelar el teletransporte. */
    int esperaTeletransporteS = 90;
    /** Las cadenas de actualizaciones de bloques (p. ej. lava que se vuelve obsidiana) no cargan ni generan chunks en el hilo principal. */
    boolean cadenaSinCargar = true;
    /** 0.5.0: el hilo principal no espera a la generación (consultas «si está cargado», cadenas de bloques del juego normal). */
    boolean consultasSinEsperar = true, cargadoEsListo = true, cadenasGlobales = true, movimientoAListo = true, spawnsSinEsperar = true;
    /** Radio (bloques) alrededor del punto de aparición que se prepara sin jugadores. 0 = nada. */
    int radioSinJugadores = 3072;
    /** Con jugadores conectados, preparar también la cuenca hacia la que se mueve cada uno. */
    boolean anticiparJugadores = true;
    /** Con jugadores conectados, seguir preparando el anillo alrededor del punto de aparición. */
    boolean anilloConJugadores = false;
    /** Tras cada cuenca, esperar este múltiplo de lo que tardó (1.0 = como máximo la mitad del tiempo trabajando). */
    double pausaRelativa = 1.0;
    /** No pedir nada si el tick medio supera estos milisegundos. */
    double msptMaximo = 40.0;
    /** No pedir nada si la carga de CPU de toda la máquina supera esta fracción (0-1). */
    double cargaMaquinaMaxima = 0.75;
    /** Segundos tras arrancar antes de empezar. */
    int esperaInicialS = 30;

    static Config cargar(Path ruta) {
        Config c = new Config();
        Properties p = new Properties();
        if (Files.exists(ruta)) {
            try (Reader r = Files.newBufferedReader(ruta)) { p.load(r); }
            catch (IOException e) { Cauces.LOG.warn("no se pudo leer {}: {}", ruta, e.toString()); }
        }
        c.activado = Boolean.parseBoolean(p.getProperty("activado", "" + c.activado));
        c.permitirOtraVersionSR = Boolean.parseBoolean(p.getProperty("permitirOtraVersionSR", "" + c.permitirOtraVersionSR));
        c.planificar = Boolean.parseBoolean(p.getProperty("planificar", "" + c.planificar));
        c.horizonteS = Integer.parseInt(p.getProperty("horizonteS", "" + c.horizonteS).trim());
        c.vigiaS = Integer.parseInt(p.getProperty("vigiaS", "" + c.vigiaS).trim());
        c.esperaGuardadoS = Integer.parseInt(p.getProperty("esperaGuardadoS", "" + c.esperaGuardadoS).trim());
        c.esperaParadaS = Integer.parseInt(p.getProperty("esperaParadaS", "" + c.esperaParadaS).trim());
        c.teletransportePrevio = Boolean.parseBoolean(p.getProperty("teletransportePrevio", "" + c.teletransportePrevio));
        c.esperaTeletransporteS = Integer.parseInt(p.getProperty("esperaTeletransporteS", "" + c.esperaTeletransporteS).trim());
        c.cadenaSinCargar = Boolean.parseBoolean(p.getProperty("cadenaSinCargar", "" + c.cadenaSinCargar));
        c.consultasSinEsperar = Boolean.parseBoolean(p.getProperty("consultasSinEsperar", "" + c.consultasSinEsperar));
        c.cargadoEsListo = Boolean.parseBoolean(p.getProperty("cargadoEsListo", "" + c.cargadoEsListo));
        c.movimientoAListo = Boolean.parseBoolean(p.getProperty("movimientoAListo", "" + c.movimientoAListo));
        c.spawnsSinEsperar = Boolean.parseBoolean(p.getProperty("spawnsSinEsperar", "" + c.spawnsSinEsperar));
        c.cadenasGlobales = Boolean.parseBoolean(p.getProperty("cadenasGlobales", "" + c.cadenasGlobales));
        c.radioSinJugadores = Integer.parseInt(p.getProperty("radioSinJugadores", "" + c.radioSinJugadores).trim());
        c.anticiparJugadores = Boolean.parseBoolean(p.getProperty("anticiparJugadores", "" + c.anticiparJugadores));
        c.anilloConJugadores = Boolean.parseBoolean(p.getProperty("anilloConJugadores", "" + c.anilloConJugadores));
        c.pausaRelativa = Double.parseDouble(p.getProperty("pausaRelativa", "" + c.pausaRelativa).trim());
        c.msptMaximo = Double.parseDouble(p.getProperty("msptMaximo", "" + c.msptMaximo).trim());
        c.cargaMaquinaMaxima = Double.parseDouble(p.getProperty("cargaMaquinaMaxima", "" + c.cargaMaquinaMaxima).trim());
        c.esperaInicialS = Integer.parseInt(p.getProperty("esperaInicialS", "" + c.esperaInicialS).trim());
        if (!Files.exists(ruta)) c.guardar(ruta);
        return c;
    }

    void guardar(Path ruta) {
        String t = """
            # PURG4TORY Cauces: prepara las cuencas de Streams Reflowing antes de que lleguen los jugadores.
            # Solo usa métodos públicos de Streams Reflowing; Streams guarda las cuencas en el mundo, así que el trabajo
            # se conserva entre reinicios y se reanuda donde se quedó.
            activado=%s
            # Solo funciona con la versión de Streams Reflowing probada (%s) salvo que esto sea true.
            permitirOtraVersionSR=%s
            # false = no pedir cuencas (queda solo el vigía de diagnóstico).
            planificar=%s
            # Segundos por delante de cada jugador que se intentan tener preparados (mínimo 1,5 cuencas).
            horizonteS=%d
            # Si el servidor pasa estos segundos sin completar un tick, se vuelca un diagnóstico al registro. 0 = nunca.
            vigiaS=%d
            # Guardado completo (save-all flush y parada): segundos máximos para liberar chunks retenidos por generación
            # en curso antes de seguir (los que queden se guardan al descargarse). Evita que el servidor se cuelgue.
            esperaGuardadoS=%d
            # Parada del servidor: segundos máximos esperando a chunks en generación antes del guardado final (0 = sin límite).
            esperaParadaS=%d
            # Teletransportes de jugadores (/tp y mods) a terreno sin cargar: se aplazan hasta que el destino esté listo, sin parar el servidor.
            teletransportePrevio=%s
            # Segundos máximos de espera del destino; pasado ese tiempo el teletransporte se cancela.
            esperaTeletransporteS=%d
            # Terreno recién generado: las cadenas de actualizaciones de bloques que empiezan en él (lava que se vuelve obsidiana)
            # no generan otros chunks de forma síncrona en el hilo principal; se reanudan al cargarse esos chunks. Evita
            # congelaciones largas del mundo al explorar. No afecta a redstone, agua o mecanismos del juego normal. false = Minecraft.
            cadenaSinCargar=%s
            # El hilo principal no espera a que se genere un chunk cuando solo pregunta «si está cargado» (colisiones, IA,
            # mods): responde «no está» hasta que esté listo. Evita congelaciones al explorar rápido. false = Minecraft.
            consultasSinEsperar=%s
            # «¿Está cargado?» en el hilo principal = «está listo» (generado), para que leerlo no acabe en una espera. false = Minecraft.
            cargadoEsListo=%s
            # Las cadenas de bloques (redstone, agua, lava) que llegan a un chunk aún no listo esperan a que esté listo y se
            # reanudan, en vez de generarlo de forma síncrona. Requiere cadenaSinCargar=true. false = solo terreno nuevo.
            cadenasGlobales=%s
            # Un jugador no entra en un chunk hasta que su entorno (3×3 chunks) está generado: en el borde de lo generado
            # se nota como un tope que desaparece cuando el terreno está listo, en vez de un mundo congelado. false = Minecraft.
            movimientoAListo=%s
            # Las comprobaciones de aparición de criaturas que tocan un chunk aún no generado fallan («ahí aún no hay terreno»)
            # en vez de dejar el mundo esperando a que se genere. false = Minecraft.
            spawnsSinEsperar=%s
            # Radio en bloques alrededor del punto de aparición que se prepara cuando no hay jugadores. 0 = nada.
            radioSinJugadores=%d
            # Con jugadores: preparar la cuenca siguiente en la dirección en que se mueve cada jugador.
            anticiparJugadores=%s
            # Con jugadores: seguir con el anillo alrededor del punto de aparición (normalmente false).
            anilloConJugadores=%s
            # Pausa tras cada cuenca, como múltiplo de lo que tardó (1.0 = trabaja como mucho la mitad del tiempo).
            pausaRelativa=%s
            # No pedir cuencas si el tick medio del servidor supera estos ms.
            msptMaximo=%s
            # No pedir cuencas si la CPU de toda la máquina está por encima de esta fracción (protege otros servicios).
            cargaMaquinaMaxima=%s
            # Segundos tras arrancar el servidor antes de empezar.
            esperaInicialS=%d
            """.formatted(activado, Cauces.SR_PROBADA, permitirOtraVersionSR, planificar, horizonteS, vigiaS, esperaGuardadoS, esperaParadaS, teletransportePrevio, esperaTeletransporteS, cadenaSinCargar, consultasSinEsperar, cargadoEsListo, cadenasGlobales, movimientoAListo, spawnsSinEsperar, radioSinJugadores, anticiparJugadores,
            anilloConJugadores, pausaRelativa, msptMaximo, cargaMaquinaMaxima, esperaInicialS);
        try (Writer w = Files.newBufferedWriter(ruta)) { w.write(t); }
        catch (IOException e) { Cauces.LOG.warn("no se pudo escribir {}: {}", ruta, e.toString()); }
    }
}
