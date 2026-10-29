#!/usr/bin/env python3
"""Entrada sintética para el cliente de pruebas en Xvfb (XTest vía ctypes; sin dependencias).
Uso: x11in.py [-d :87] key <nombre_keysym> [ms] | click <1|2|3> [ms] | move <dx> <dy> | moveto <x> <y> | type <texto>
 key: pulsa y suelta (ms = tiempo pulsada, 80 por defecto). click: botón del ratón (1 izq, 3 der) pulsado ms. move: relativo."""
import ctypes, sys, time
args = sys.argv[1:]; disp = b':87'
if args[:1] == ['-d']: disp = args[1].encode(); args = args[2:]
x11 = ctypes.CDLL('libX11.so.6'); xtst = ctypes.CDLL('libXtst.so.6')
x11.XOpenDisplay.restype = ctypes.c_void_p; x11.XKeysymToKeycode.restype = ctypes.c_ubyte
x11.XStringToKeysym.restype = ctypes.c_ulong; x11.XStringToKeysym.argtypes = [ctypes.c_char_p]
x11.XKeysymToKeycode.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
xtst.XTestFakeKeyEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]
xtst.XTestFakeButtonEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]
xtst.XTestFakeRelativeMotionEvent.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_ulong]
xtst.XTestFakeMotionEvent.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_ulong]
x11.XFlush.argtypes = [ctypes.c_void_p]; x11.XSync.argtypes = [ctypes.c_void_p, ctypes.c_int]
d = x11.XOpenDisplay(disp)
if not d: sys.exit('no se pudo abrir ' + disp.decode())
def tecla(nombre, ms):
    k = x11.XKeysymToKeycode(d, x11.XStringToKeysym(nombre.encode()))
    xtst.XTestFakeKeyEvent(d, k, 1, 0); x11.XFlush(d); time.sleep(ms / 1000); xtst.XTestFakeKeyEvent(d, k, 0, 0); x11.XFlush(d)
cmd = args[0]
if cmd == 'key': tecla(args[1], int(args[2]) if len(args) > 2 else 80)
elif cmd == 'click':
    b = int(args[1]); xtst.XTestFakeButtonEvent(d, b, 1, 0); x11.XFlush(d); time.sleep((int(args[2]) if len(args) > 2 else 80) / 1000); xtst.XTestFakeButtonEvent(d, b, 0, 0); x11.XFlush(d)
elif cmd == 'move':
    dx, dy = int(args[1]), int(args[2]); paso = 10
    for _ in range(max(abs(dx), abs(dy)) // paso + 1):
        xtst.XTestFakeRelativeMotionEvent(d, max(-paso, min(paso, dx)), max(-paso, min(paso, dy)), 0); x11.XFlush(d); time.sleep(0.01)
        dx -= max(-paso, min(paso, dx)); dy -= max(-paso, min(paso, dy))
elif cmd == 'moveto': xtst.XTestFakeMotionEvent(d, 0, int(args[1]), int(args[2]), 0); x11.XFlush(d)
elif cmd == 'type':
    for ch in ' '.join(args[1:]):
        nombre = {' ': 'space', '/': 'slash', '.': 'period', '-': 'minus', '_': 'underscore', ':': 'colon'}.get(ch, ch)
        sh = ch.isupper() or ch in '_:'
        if sh: tecla('Shift_L', 1) if False else None
        tecla(nombre, 30); time.sleep(0.03)
x11.XSync(d, 0)
