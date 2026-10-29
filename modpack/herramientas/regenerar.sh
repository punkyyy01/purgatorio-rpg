#!/bin/sh
# Regenera overrides/ (y, opcionalmente, el zip) desde el repositorio y las versiones exactas de bloqueo.json.
# Uso: sh herramientas/regenerar.sh <dir_trabajo> --acepto-eula [dir_salida_zip]
#   <dir_trabajo>: carpeta fuera del repositorio para la caché de jars, el servidor temporal y la config por defecto.
#   --acepto-eula: necesario para arrancar el servidor temporal (EULA de Minecraft: https://aka.ms/MinecraftEULA).
set -eu
RAIZ=$(cd "$(dirname "$0")/.." && pwd)
TRABAJO=${1:?falta <dir_trabajo>}
[ "${2:-}" = "--acepto-eula" ] || { echo "Hace falta --acepto-eula"; exit 1; }
SALIDA=${3:-}

python3 -I "$RAIZ/herramientas/obtener_config_por_defecto.py" "$RAIZ" "$TRABAJO" --acepto-eula
python3 -I "$RAIZ/herramientas/generar_fauna.py" "$RAIZ/overrides/config/paxi/datapacks/purgatorio_fauna"
python3 -I "$RAIZ/herramientas/generar_criaturas.py" "$RAIZ/overrides" "$TRABAJO/config_por_defecto"
python3 -I "$RAIZ/herramientas/generar_critters.py" "$RAIZ/overrides" "$TRABAJO/config_por_defecto"
python3 -I "$RAIZ/herramientas/generar_incontrol.py" "$RAIZ/overrides"
python3 -I "$RAIZ/herramientas/empaquetar.py" "$RAIZ" --solo-lista
[ -n "$SALIDA" ] && python3 -I "$RAIZ/herramientas/empaquetar.py" "$RAIZ" "$SALIDA"
echo "Listo. Revisa los cambios con: git status && git diff --stat"
