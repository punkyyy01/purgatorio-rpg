#!/bin/bash
# Ensambla la carpeta de entrega completa (zips, documentación, Cauces, informes, pruebas) y calcula SHA256SUMS.txt. No publica nada.
set -e; cd "$(dirname "$0")/.."; V=$(sed -n 's/^version *= *"\(.*\)".*/\1/p' modpack/pack.toml | head -1); OUT=entrega_$V
chmod -R u+w $OUT 2>/dev/null || true
python3 -I herramientas-int/crear_entrega.py modpack doc $OUT > /dev/null
mkdir -p $OUT/cauces $OUT/informes $OUT/pruebas
J=$(ls modpack/mods-propios/purg4tory_cauces/build/purg4tory_cauces-*.jar | tail -1); cp $J modpack/mods-propios/purg4tory_cauces/LICENSE $OUT/cauces/
(cd modpack/mods-propios && python3 - ../../$OUT/cauces/$(basename ${J%.jar})-fuentes.zip <<'PY'
import zipfile,os,sys
z=zipfile.ZipFile(sys.argv[1],'w',zipfile.ZIP_DEFLATED)
for r,_,fs in sorted(os.walk('purg4tory_cauces')):
    if '/build' in r: continue
    for f in sorted(fs):
        p=os.path.join(r,f); zi=zipfile.ZipInfo(p,(1980,1,1,0,0,0)); zi.compress_type=8; zi.external_attr=0o644<<16; z.writestr(zi,open(p,'rb').read())
PY
)
cp informes/*.json $OUT/informes/
cp prueba/resultados/resumen.txt prueba/resultados/locate.txt prueba/resultados/parar.txt prueba/resultados/respaldo.txt prueba/aceptacion.out prueba/cliente2.out prueba/combate.out prueba/fin.out prueba/t3.out $OUT/pruebas/ 2>/dev/null || true
cp ~/dev/lab090-perf/resultados/e5_beta1/resumen.txt $OUT/pruebas/E5_parada_retenida_0.4.0.txt
cp prueba/*.sh prueba/x11in.py $OUT/pruebas/
[ -d prueba/p0 ] && cp -r prueba/p0 $OUT/pruebas/p0
cp herramientas/*.py modpack/herramientas/generar_licencias.py $OUT/informes/ 2>/dev/null || true
(cd $OUT && find . -type f ! -name SHA256SUMS.txt | sort | sed 's#^\./##' | xargs sha256sum > SHA256SUMS.txt)
chmod -R a-w $OUT; echo "$OUT listo: $(ls $OUT | wc -l) elementos"; ls -la $OUT/*.zip
