#!/bin/bash
# Compila PURG4TORY Cauces sin Gradle (javac contra las librerías de un servidor NeoForge 21.1.259 ya instalado, ver classpath.txt).
# -proc:none: el procesador de anotaciones de Mixin no resuelve los destinos sin mapeos; los mixins se aplican en ejecución.
# Uso: construir.sh   -> build/purg4tory_cauces-<versión>.jar
set -e; cd "$(dirname "$0")"
export PATH="$HOME/dev/tools/jdk-21.0.12.1+1/bin:$PATH"
V=$(sed -n 's/^version="\(.*\)"/\1/p' res/META-INF/neoforge.mods.toml | head -1)
rm -rf build; mkdir -p build/cls
javac -proc:none --release 21 -d build/cls -cp "$(cat classpath.txt):${MIXINEXTRAS:-$HOME/dev/lab-p0/dev/libs/mixinextras-neoforge-0.5.5.jar}" $(find src -name '*.java')
cp -r res/* build/cls/
find build/cls -exec touch -d '2026-01-01 00:00:00' {} +
(cd build/cls && jar --create --date=2026-01-01T00:00:00Z --file ../purg4tory_cauces-$V.jar .)
sha256sum build/purg4tory_cauces-$V.jar
