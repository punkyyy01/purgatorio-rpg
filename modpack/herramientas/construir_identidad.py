#!/usr/bin/env python3
"""Integra la identidad visual de PURG4TORY: Souls Grimore en overrides/ (solo cliente).

Uso: python3 construir_identidad.py <dir_modpack> <dir_originales> [--afma-jar <fancymenu.jar>] [--libs <dir_libraries>]
  <dir_originales>: carpeta PURG4TORY_Identidad extraída del ZIP de identidad (solo lectura).
Necesita Pillow + numpy (PYTHONPATH) y ffmpeg con libvpx (para extraer los fotogramas con alfa).

Qué genera (todo bajo overrides/config/):
- fancymenu/assets/purg4tory/: fondo del menú, fondo desenfocado para menús y cargas, animación AFMA de la
  composición (presentación de 4 s + reposo en bucle de 12 s), texturas de botón nine-slice, iconos de ventana y logo.
- fancymenu/customization/: layouts de la pantalla de título, de las pantallas fuera del mundo y de la carga (Drippy).
- Ajustes de cliente de otros mods para que el menú propio funcione: IceAndFire sin su menú principal, y los
  botones de configuración de Create y Supplementaries fuera del menú (sus opciones siguen accesibles desde «Mods»).
Las opciones globales de FancyMenu y Drippy (formato de Konkrete) las aplica parchear_opciones.py sobre los archivos
que generan los propios mods.

La animación AFMA se codifica con el codificador oficial de FancyMenu (AfmaEncodeStandaloneTool, dentro del jar de
FancyMenu) y se guarda en caché por hash de sus fuentes: si las fuentes no cambian, no se vuelve a codificar.
"""
import hashlib, json, os, shutil, subprocess, sys, tempfile, tomllib
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

MP, ORIG = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
def arg(n, d=None):
    return sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d
CACHE = Path(arg('--cache', Path.home() / 'dev/modpack-cache/identidad'))
LIBS = Path(arg('--libs', Path.home() / 'dev/purg4tory-identidad/cliente/mc/libraries'))
JAVA = arg('--java', str(Path.home() / 'dev/tools/jdk-21.0.12.1+1/bin/java'))
pack = tomllib.loads((MP / 'pack.toml').read_text())
VERSION, NOMBRE = pack['version'], pack['nombre']

CONF = MP / 'overrides' / 'config'
FM = CONF / 'fancymenu'
ASSETS = FM / 'assets' / 'purg4tory'
LAYOUTS = FM / 'customization'
REL = '/config/fancymenu/assets/purg4tory/'          # rutas tal como las ve el juego (relativas al directorio del juego)
for d in (ASSETS, LAYOUTS):
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)

KIT = ORIG / '06_minecraft_menu' / 'kit_capas'
ANIM = ORIG / '04_animaciones' / 'menu_composicion'
fuentes = {}

def fuente(p):
    p = Path(p)
    fuentes[str(p.relative_to(ORIG))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return p

# ---------- 1. Fondos ----------
# Fondo del menú principal: paisaje limpio del PSD con viñeta suave y la franja inferior algo más oscura
# (legibilidad de botones y textos). Es un derivado de nuestro propio recurso.
pais = Image.open(fuente(KIT / '00_fondo_paisaje.png')).convert('RGB')
a = np.asarray(pais).astype(np.float32) / 255
h, w = a.shape[:2]
yy, xx = np.mgrid[0:h, 0:w]
r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h * 0.45) / (h / 2)) ** 2)
vin = 1 - 0.38 * np.clip((r - 0.55) / 0.75, 0, 1) ** 1.6
baja = 1 - 0.30 * np.clip((yy / h - 0.62) / 0.38, 0, 1) ** 1.4
a = a * (vin * baja)[..., None]
Image.fromarray((a * 255).clip(0, 255).astype(np.uint8)).save(ASSETS / 'fondo_menu_principal.jpg', quality=90, optimize=True)

# Fondo para menús fuera del mundo y pantallas de carga: desenfocado y oscurecido, 1280×720.
bl = pais.resize((1280, 720), Image.LANCZOS).filter(ImageFilter.GaussianBlur(10))
b = np.asarray(bl).astype(np.float32) * 0.42
Image.fromarray(b.clip(0, 255).astype(np.uint8)).save(ASSETS / 'fondo_menus.jpg', quality=88, optimize=True)

# ---------- 2. Logo, iconos ----------
shutil.copy(fuente(ORIG / '02_logos' / 'PURG4TORY_logo_transparente_1024w.png'), ASSETS / 'logo_1024.png')
for n in (16, 32):
    shutil.copy(fuente(ORIG / '01_iconos' / f'souls_grimore_icon_{n}.png'), ASSETS / f'icono_{n}.png')

# ---------- 3. Texturas de botón (nine-slice, arte propio con la paleta de la marca) ----------
def boton(relleno_sup, relleno_inf, borde, brillo, nombre):
    W, H = 64, 20
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    px = im.load()
    for y in range(H):
        t = y / (H - 1)
        c = tuple(int(relleno_sup[i] * (1 - t) + relleno_inf[i] * t) for i in range(4))
        for x in range(W):
            px[x, y] = c
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, H - 1], outline=(4, 10, 9, 255))          # contorno exterior oscuro
    d.rectangle([1, 1, W - 2, H - 2], outline=borde)                     # marco de energía
    d.line([2, 2, W - 3, 2], fill=brillo)                                # luz superior
    d.line([2, H - 3, W - 3, H - 3], fill=(0, 0, 0, 90))                 # sombra inferior
    for (x, y) in ((0, 0), (W - 1, 0), (0, H - 1), (W - 1, H - 1)):      # esquinas achaflanadas
        px[x, y] = (0, 0, 0, 0)
    im.save(ASSETS / nombre, optimize=True)

boton((10, 28, 24, 214), (5, 14, 12, 228), (47, 143, 120, 255), (95, 209, 176, 120), 'boton_normal.png')
boton((22, 74, 61, 232), (11, 40, 34, 240), (143, 255, 224, 255), (190, 255, 236, 170), 'boton_hover.png')
boton((24, 28, 27, 190), (16, 19, 18, 205), (70, 84, 80, 255), (110, 120, 116, 70), 'boton_inactivo.png')

# ---------- 4. Animación AFMA (presentación + reposo) ----------
def afma():
    srcs = [fuente(ANIM / 'menu_intro_alfa.webm'), fuente(ANIM / 'menu_reposo_loop_alfa.webm')]
    jar = Path(arg('--afma-jar', Path.home() / 'dev/modpack-cache/identidad/fancymenu_neoforge_3.9.14_MC_1.21.1.jar'))
    # 960×540 a 15 fps: 26 MiB (a 1920×1080 y 30 fps pesaba 128 MiB). El título nítido va aparte, encima.
    preset, ft, vf = 'balanced', '67', 'fps=15,scale=960:540:flags=lanczos'
    clave = hashlib.sha256(b''.join(hashlib.sha256(p.read_bytes()).digest() for p in srcs)
                           + hashlib.sha256(jar.read_bytes()).digest() + f'{preset}{ft}{vf}'.encode()).hexdigest()[:16]
    cache = CACHE / 'afma' / f'composicion_{clave}.afma'
    if not cache.exists():
        cache.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=str(CACHE)) as t:
            t = Path(t)
            for nombre, src in (('intro', srcs[0]), ('main', srcs[1])):
                (t / nombre).mkdir()
                subprocess.run(['ffmpeg', '-v', 'error', '-c:v', 'libvpx-vp9', '-i', str(src), '-vf', vf, '-pix_fmt', 'rgba',
                                str(t / nombre / 'frame_%04d.png')], check=True)
            cp = [str(jar)] + [str(p) for g in ('com/google/code/gson/gson/2.10.1', 'commons-io/commons-io/2.15.1',
                  'org/apache/commons/commons-compress/1.26.0', 'org/apache/logging/log4j/log4j-api/2.22.1',
                  'org/apache/logging/log4j/log4j-core/2.22.1', 'org/lwjgl/lwjgl/3.3.3', 'org/lwjgl/lwjgl-stb/3.3.3')
                  for p in sorted((LIBS / g).glob('*.jar'))]
            (t / 'tmp').mkdir()
            subprocess.run([JAVA, '-Xmx6G', '-cp', ':'.join(cp),
                            'de.keksuccino.fancymenu.util.resource.resources.texture.afma.creator.AfmaEncodeStandaloneTool',
                            '--intro', str(t / 'intro'), '--main', str(t / 'main'), '--output', str(t / 'out.afma'),
                            '--preset', preset, '--frame-time', ft, '--intro-frame-time', ft, '--temp-dir', str(t / 'tmp')],
                           check=True, stdout=subprocess.DEVNULL)
            shutil.move(str(t / 'out.afma'), cache)
    shutil.copy(cache, ASSETS / 'composicion_menu.afma')
    return cache
CLAVE_AFMA = afma()

# Título nítido a resolución completa (sombra + título del kit, mismo lienzo 1920×1080 que la animación).
tit = Image.open(fuente(KIT / '40_titulo_sombra.png')).convert('RGBA')
tit.alpha_composite(Image.open(fuente(KIT / '50_titulo.png')).convert('RGBA'))
tit.save(ASSETS / 'titulo_nitido.png', optimize=True)

# ---------- 5. Layouts de FancyMenu ----------
GW, GH = '{"placeholder":"guiwidth"}', '{"placeholder":"guiheight"}'
def calc(expr):
    return '{"placeholder":"calc","values":{"expression":"%s","decimal":"false"}}' % expr
def mn(a, b):
    return f'(({a})+({b})-abs(({a})-({b})))/2'

def contenedor(tipo, props):
    return tipo + ' {\n' + ''.join(f'  {k} = {v}\n' for k, v in props.items()) + '}\n\n'

def meta(identificador, extra=None):
    p = {'identifier': identificador, 'render_custom_elements_behind_vanilla': 'false', 'last_edited_time': '0',
         'is_enabled': 'true', 'randommode': 'false', 'randomgroup': '1', 'randomonlyfirsttime': 'false', 'layout_index': '0'}
    p.update(extra or {})
    return contenedor('layout-meta', p)

def base_elem(tipo, ident, anchor, x, y, w, h, extra):
    p = {'element_type': tipo, 'instance_identifier': ident, 'appearance_delay': 'no_delay', 'disappearance_delay': 'no_delay',
         'fade_in_v2': 'no_fading', 'fade_out': 'no_fading', 'anchor_point': anchor, 'sticky_anchor': 'true',
         'x': x, 'y': y, 'width': w, 'height': h, 'stay_on_screen': 'false', 'enable_parallax': 'false',
         'load_once_per_session': 'false'}
    p.update(extra)
    return p

# Geometría (unidades GUI): la composición ocupa la parte superior y deja abajo 92 unidades para tres filas de
# botones (3×20 + 2×4) con márgenes. El título acaba al 88,4 % de la altura de la composición (955/1080).
ALTO_COMP = mn(mn(f'0.80*{GH}', f'({GH}-92)/0.884'), f'{GW}*9/16')
ANCHO_COMP = f'({ALTO_COMP})*16/9'

def boton_vanilla(ident, x, y, w, extra=None):
    p = base_elem('vanilla_button', ident, 'bottom-centered', str(x), str(y), str(w), '20', {
        'is_hidden': 'false', 'backgroundnormal': '[source:local]' + REL + 'boton_normal.png',
        'backgroundhovered': '[source:local]' + REL + 'boton_hover.png',
        'background_texture_inactive': '[source:local]' + REL + 'boton_inactivo.png',
        'nine_slice_custom_background': 'true', 'nine_slice_border_x': '3', 'nine_slice_border_y': '3',
        'label_base_color': '#E8FFF7', 'label_hover_color': '#FFFFFF', 'label_shadow': 'true',
        'fade_in_v2': 'first_time', 'fade_in_speed': '3', 'appearance_delay': 'first_time',
        'appearance_delay_seconds': '0.8'})
    p.update(extra or {})
    return contenedor('vanilla_button', p)

def oculto(ident):
    return contenedor('vanilla_button', {'element_type': 'vanilla_button', 'instance_identifier': ident, 'is_hidden': 'true'})

t = 'type = fancymenu_layout\n\n' + meta('title_screen')
t += contenedor('menu_background', {'background_type': 'image', 'instance_identifier': 'purg4tory_fondo_titulo',
                                     'image_path': '[source:local]' + REL + 'fondo_menu_principal.jpg', 'slide': 'false',
                                     'repeat_texture': 'false', 'parallax': 'true', 'parallax_intensity_x': '0.012',
                                     'parallax_intensity_y': '0.008', 'invert_parallax': 'false',
                                     'restart_animated_on_menu_load': 'false'})
t += contenedor('customization', {'action': 'backgroundoptions', 'keepaspectratio': 'true'})
t += contenedor('element', base_elem('image', 'purg4tory_composicion', 'top-centered', '0', '2', '100', '100', {
    'source': '[source:local]' + REL + 'composicion_menu.afma', 'advanced_width': calc(ANCHO_COMP),
    'advanced_height': calc(ALTO_COMP), 'restart_animated_on_menu_load': 'false', 'repeat_texture': 'false',
    'nine_slice_texture': 'false', 'image_tint': '#FFFFFF', 'enable_parallax': 'true', 'parallax_intensity_x': '0.25',
    'parallax_intensity_y': '0.10', 'invert_parallax': 'true'}))
# Título nítido encima, con la misma geometría y paralaje. En la presentación el título aparece entre 2,1 y 2,7 s:
# esta capa entra a los 2,1 s con un fundido de ~0,6 s (opacidad += 0,4·velocidad por segundo).
t += contenedor('element', base_elem('image', 'purg4tory_titulo_nitido', 'top-centered', '0', '2', '100', '100', {
    'source': '[source:local]' + REL + 'titulo_nitido.png', 'advanced_width': calc(ANCHO_COMP),
    'advanced_height': calc(ALTO_COMP), 'restart_animated_on_menu_load': 'false', 'repeat_texture': 'false',
    'nine_slice_texture': 'false', 'image_tint': '#FFFFFF', 'enable_parallax': 'true', 'parallax_intensity_x': '0.25',
    'parallax_intensity_y': '0.10', 'invert_parallax': 'true', 'appearance_delay': 'first_time',
    'appearance_delay_seconds': '2.1', 'fade_in_v2': 'first_time', 'fade_in_speed': '4.2'}))
# Versión del pack (sustituye a las líneas de marca, que varios mods escriben encima unas de otras).
t += contenedor('element', base_elem('text_v2', 'purg4tory_version', 'top-left', '3', '3', '220', '20', {
    'source': f'**{NOMBRE}** {VERSION}%n%Minecraft {{"placeholder":"mcversion"}} · NeoForge {{"placeholder":"loaderver"}} · {{"placeholder":"loadedmods"}} mods',
    'source_mode': 'direct', 'shadow': 'true', 'scale': '0.75', 'base_color': '#CFEFE6', 'interactable': 'false',
    'auto_line_wrapping': 'false', 'enable_scrolling': 'false'}))
for ident in ('minecraft_logo_widget', 'minecraft_splash_widget', 'minecraft_realms_notification_icons_widget',
              'minecraft_branding_widget', 'mc_titlescreen_realms_button'):
    t += oculto(ident)
# Botones: tres filas centradas abajo (bloque de 200 de ancho). Fila 1: Un jugador | Multijugador.
t += boton_vanilla('mc_titlescreen_singleplayer_button', -51, -66, 98)
t += boton_vanilla('mc_titlescreen_multiplayer_button', 51, -66, 98)
t += boton_vanilla('forge_titlescreen_mods_button', -51, -42, 98)
t += boton_vanilla('mc_titlescreen_options_button', 51, -42, 98)
# Idioma y accesibilidad: en 1.21.1 sus textos usan options.language/options.accessibility, que FancyMenu 3.9.14 no
# reconoce; su identificador es entonces la posición «x»+«y» en la pantalla de referencia de 1000×1000 de FancyMenu
# (TitleScreen con NeoForge: x = ancho/2-124 o ancho/2+104, y = alto/4+138).
t += boton_vanilla('376388', -90, -18, 20)
t += boton_vanilla('604388', -68, -18, 20)
t += boton_vanilla('mc_titlescreen_quit_button', 23, -18, 154)
(LAYOUTS / 'purg4tory_titulo.txt').write_text(t)

# Pantallas que solo existen fuera del mundo: mismo fondo desenfocado (no se tocan listas ni botones).
FUERA = ['select_world_screen', 'create_world_screen', 'join_multiplayer_screen', 'connect_screen', 'direct_join_server_screen',
         'edit_server_screen', 'level_loading_screen', 'receiving_level_screen', 'generic_dirt_message_screen',
         'progress_screen', 'disconnected_screen', 'net.neoforged.neoforge.client.gui.ModListScreen']
for i, s in enumerate(FUERA):
    t = 'type = fancymenu_layout\n\n' + meta(s)
    t += contenedor('menu_background', {'background_type': 'image', 'instance_identifier': f'purg4tory_fondo_{i}',
                                         'image_path': '[source:local]' + REL + 'fondo_menus.jpg', 'slide': 'false',
                                         'repeat_texture': 'false', 'parallax': 'false', 'restart_animated_on_menu_load': 'false'})
    t += contenedor('customization', {'action': 'backgroundoptions', 'keepaspectratio': 'true'})
    (LAYOUTS / f'purg4tory_fondo_{s.split(".")[-1].lower()}.txt').write_text(t)

# Carga de recursos (Drippy): fondo desenfocado, logo y barra con el color de la marca.
LOGO_W = calc(mn(f'{GW}*0.42', f'{GH}*0.42*1024/418'))
LOGO_H = calc(f'({mn(f"{GW}*0.42", f"{GH}*0.42*1024/418")})*418/1024')
t = 'type = fancymenu_layout\n\n' + meta('drippy_loading_overlay')
t += contenedor('menu_background', {'background_type': 'image', 'instance_identifier': 'purg4tory_fondo_carga',
                                     'image_path': '[source:local]' + REL + 'fondo_menus.jpg', 'slide': 'false',
                                     'repeat_texture': 'false', 'parallax': 'false', 'restart_animated_on_menu_load': 'false'})
t += contenedor('customization', {'action': 'backgroundoptions', 'keepaspectratio': 'true'})
t += contenedor('element', base_elem('image', 'purg4tory_logo_carga', 'mid-centered', '0', '-14', '100', '40', {
    'source': '[source:local]' + REL + 'logo_1024.png', 'advanced_width': LOGO_W, 'advanced_height': LOGO_H,
    'restart_animated_on_menu_load': 'false', 'repeat_texture': 'false', 'nine_slice_texture': 'false', 'image_tint': '#FFFFFF'}))
t += contenedor('element', base_elem('drippy_vanilla_bar', 'purg4tory_barra_carga', 'mid-centered', '0',
                                     calc(f'({mn(f"{GW}*0.42", f"{GH}*0.42*1024/418")})*418/1024/2+4'), '160', '6',
                                     {'color': '#5FD1B0'}))
t += oculto('mojang_logo') + oculto('progress_bar')
(LAYOUTS / 'purg4tory_carga.txt').write_text(t)

# Pantallas en las que FancyMenu aplica layouts (clave = ruta de clase de la pantalla, nunca el identificador universal).
CLASES = ['net.minecraft.client.gui.screens.TitleScreen', 'net.minecraft.client.gui.screens.worldselection.SelectWorldScreen',
          'net.minecraft.client.gui.screens.worldselection.CreateWorldScreen',
          'net.minecraft.client.gui.screens.multiplayer.JoinMultiplayerScreen', 'net.minecraft.client.gui.screens.ConnectScreen',
          'net.minecraft.client.gui.screens.DirectJoinServerScreen', 'net.minecraft.client.gui.screens.EditServerScreen',
          'net.minecraft.client.gui.screens.LevelLoadingScreen', 'net.minecraft.client.gui.screens.ReceivingLevelScreen',
          'net.minecraft.client.gui.screens.GenericMessageScreen', 'net.minecraft.client.gui.screens.ProgressScreen',
          'net.minecraft.client.gui.screens.DisconnectedScreen', 'net.neoforged.neoforge.client.gui.ModListScreen',
          'de.keksuccino.drippyloadingscreen.customization.DrippyOverlayScreen']
(FM / 'customizablemenus.txt').write_text('type = customizablemenus\n\n' + ''.join(f'{c} {{\n}}\n\n' for c in CLASES))

# Opciones globales (formato de Konkrete: T:clave = 'valor';). Solo las claves que cambiamos; el mod completa el resto.
def opciones(secciones):
    return ''.join(f'##[{s}]\n\n' + ''.join(f"{k} = '{v}';\n" for k, v in kv.items()) + '\n\n' for s, kv in secciones.items())
(FM / 'options.txt').write_text(opciones({
    'customization': {'B:modpack_mode': 'true', 'B:show_customization_overlay': 'false'},
    'window': {'B:show_custom_window_icon': 'true', 'S:custom_window_icon_16': REL + 'icono_16.png',
               'S:custom_window_icon_32': REL + 'icono_32.png', 'S:custom_window_title': NOMBRE}}))
# La carga temprana de NeoForge NO se personaliza: el jar de Drippy 3.1.5 publicado para 1.21.1 no incluye su módulo
# de ventana temprana (sin ImmediateWindowProvider), así que esas opciones no tendrían efecto.

# ---------- 6. Ajustes de cliente de otros mods ----------
(CONF / 'iceandfire').mkdir(parents=True, exist_ok=True)
(CONF / 'iceandfire' / 'iaf-client.json').write_text(json.dumps(
    {'client': {'customMainMenu': False, 'dragonAuto3rdPerson': False, 'siren.shader': True}}, indent=2) + '\n')
(CONF / 'create-client.toml').write_text('# PURG4TORY: el botón de configuración de Create sale del menú principal (sigue en Mods > Create > Config).\n'
                                         '[client]\n\tmainMenuConfigButtonRow = 0\n')
(CONF / 'supplementaries-client.toml').write_text('# PURG4TORY: sin botón de configuración en el menú principal (sigue en Mods).\n'
                                                  '[general]\n\tconfigs_button = false\n')

# ---------- 7. Registro de fuentes ----------
(MP / 'identidad').mkdir(exist_ok=True)
(MP / 'identidad' / 'fuentes_usadas.json').write_text(json.dumps(dict(sorted(fuentes.items())), indent=1) + '\n')
tam = sum(p.stat().st_size for p in ASSETS.rglob('*') if p.is_file())
print(f'identidad: {len(list(ASSETS.iterdir()))} recursos ({tam / 2**20:.1f} MB), {len(list(LAYOUTS.iterdir()))} layouts')
