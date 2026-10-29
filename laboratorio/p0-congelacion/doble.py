import ctypes, sys, time
x11 = ctypes.CDLL('libX11.so.6'); xt = ctypes.CDLL('libXtst.so.6')
x11.XOpenDisplay.restype = ctypes.c_void_p; x11.XKeysymToKeycode.restype = ctypes.c_ubyte
x11.XStringToKeysym.restype = ctypes.c_ulong; x11.XStringToKeysym.argtypes = [ctypes.c_char_p]
x11.XKeysymToKeycode.argtypes = [ctypes.c_void_p, ctypes.c_ulong]; x11.XFlush.argtypes = [ctypes.c_void_p]
xt.XTestFakeKeyEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]
d = x11.XOpenDisplay(sys.argv[1].encode()); k = x11.XKeysymToKeycode(d, x11.XStringToKeysym(b'space'))
for _ in range(2):
    xt.XTestFakeKeyEvent(d, k, 1, 0); x11.XFlush(d); time.sleep(0.06); xt.XTestFakeKeyEvent(d, k, 0, 0); x11.XFlush(d); time.sleep(0.09)
