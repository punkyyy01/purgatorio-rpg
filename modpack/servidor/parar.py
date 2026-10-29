#!/usr/bin/env python3
"""Parada segura de un servidor PURG4TORY: guardado completo verificado + stop + espera acotada.

Uso: python3 parar.py <dir_servidor> [--pid N] [--espera 120] [--aviso 30]
Requiere enable-rcon=true y rcon.password en server.properties (rcon.port solo en 127.0.0.1 o red privada).

1) avisa a los jugadores (--aviso segundos) y ejecuta «save-all flush»; solo continúa si el servidor responde «Saved the game».
2) ejecuta «stop» y espera hasta --espera segundos a que el proceso termine (con --pid; sin él, a que el puerto RCON se cierre).
3) si NO termina: NO mata nada por su cuenta. Imprime qué hacer. El guardado del paso 1 ya está en disco: matar el proceso solo pierde
   lo ocurrido después de ese guardado (con el servidor vacío, nada). Nunca uses `kill -9` ANTES de que el paso 1 haya confirmado.
Códigos de salida: 0 parado limpio · 2 el guardado no se confirmó (NO parar a la fuerza) · 3 guardado OK pero el proceso no terminó."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rcon import Rcon, propiedades
args = sys.argv[1:]
if not args or args[0].startswith('--'): sys.exit(__doc__)
dir_srv = args[0]; opt = lambda n, d: int(args[args.index(n) + 1]) if n in args else d
pid, espera, aviso = opt('--pid', 0), opt('--espera', 120), opt('--aviso', 30)
p = propiedades(os.path.join(dir_srv, 'server.properties'))
try: r = Rcon('127.0.0.1', int(p.get('rcon.port', 25575)), os.environ.get('RCON_PASSWORD') or p.get('rcon.password', ''), timeout=300)
except Exception as e: sys.exit(f'No se pudo conectar por RCON ({e}). Activa enable-rcon=true y rcon.password en server.properties.')
if aviso:
    r.comando(f'say El servidor se detendrá en {aviso} s'); time.sleep(aviso)
t0 = time.time(); out = r.comando('save-all flush'); dt = time.time() - t0
print(f'save-all flush ({dt:.0f} s): {out}')
if 'Saved the game' not in out:
    print('El guardado NO se confirmó. No pares el servidor a la fuerza. Revisa logs/latest.log y repite.'); sys.exit(2)
try: r.comando('stop')
except Exception: pass
r.cerrar()
def vivo():
    if pid: return os.path.exists(f'/proc/{pid}') if os.path.exists('/proc') else True
    import socket
    try: socket.create_connection(('127.0.0.1', int(p.get('rcon.port', 25575))), timeout=1).close(); return True
    except OSError: return False
t1 = time.time()
while time.time() - t1 < espera:
    if not vivo(): print(f'Servidor parado limpio ({time.time() - t1:.0f} s tras «stop»).'); sys.exit(0)
    time.sleep(1)
print(f'''El servidor NO terminó en {espera} s, pero el guardado anterior SÍ está confirmado.
Qué hacer:
  1. Espera 1-2 minutos más: tras «stop» Minecraft aún cierra dimensiones (con Streams Reflowing, la parada acota a 60 s las generaciones en curso).
  2. Si sigue, guarda un diagnóstico:  jstack <pid> > parada-colgada.txt   (opcional)
  3. Cierra el proceso: primero «kill <pid>» (SIGTERM) y, si a los 30 s sigue, «kill -9 <pid>». Se pierde solo lo ocurrido desde el guardado confirmado.
  4. Antes de volver a arrancar: haz una copia del mundo con respaldo.py y verifícala con verificar_mundo.py.''')
sys.exit(3)
