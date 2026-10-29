#!/usr/bin/env python3
"""Cliente RCON mínimo (solo biblioteca estándar) para las herramientas de administración de PURG4TORY.
Uso:  python3 rcon.py [--host 127.0.0.1] [--puerto 25575] [--clave-env RCON_PASSWORD] <comando...>
La clave NO se pasa por línea de comandos (se vería en `ps`): variable de entorno RCON_PASSWORD, o se lee de server.properties
con --propiedades <ruta/server.properties>."""
import os, socket, struct, sys, time

class Rcon:
    def __init__(self, host='127.0.0.1', puerto=25575, clave='', timeout=30):
        self.s = socket.create_connection((host, puerto), timeout=timeout); self.n = 0
        r = self._enviar(3, clave)
        if r[0] == -1: raise PermissionError('RCON: clave incorrecta')
    def _enviar(self, tipo, cuerpo):
        self.n += 1; b = cuerpo.encode('utf-8')
        self.s.sendall(struct.pack('<iii', 10 + len(b), self.n, tipo) + b + b'\0\0')
        return self._leer()
    def _leer(self):
        cab = self._exacto(4); (largo,) = struct.unpack('<i', cab); d = self._exacto(largo)
        ident, tipo = struct.unpack('<ii', d[:8]); return ident, tipo, d[8:-2].decode('utf-8', 'replace')
    def _exacto(self, n):
        b = b''
        while len(b) < n:
            c = self.s.recv(n - len(b))
            if not c: raise ConnectionError('RCON cerrado')
            b += c
        return b
    def comando(self, texto): return self._enviar(2, texto)[2]
    def cerrar(self):
        try: self.s.close()
        except OSError: pass

def propiedades(ruta):
    p = {}
    for l in open(ruta, encoding='utf-8'):
        if '=' in l and not l.startswith('#'): k, v = l.split('=', 1); p[k.strip()] = v.strip()
    return p

def conectar(args):
    host, puerto, clave, props = '127.0.0.1', None, os.environ.get('RCON_PASSWORD', ''), None
    i = 0
    while i < len(args):
        if args[i] == '--host': host = args[i + 1]; i += 2
        elif args[i] == '--puerto': puerto = int(args[i + 1]); i += 2
        elif args[i] == '--propiedades': props = propiedades(args[i + 1]); i += 2
        else: break
    if props:
        puerto = puerto or int(props.get('rcon.port', 25575)); clave = clave or props.get('rcon.password', '')
    return Rcon(host, puerto or 25575, clave), args[i:]

if __name__ == '__main__':
    r, resto = conectar(sys.argv[1:])
    if not resto: sys.exit(__doc__)
    print(r.comando(' '.join(resto))); r.cerrar()
