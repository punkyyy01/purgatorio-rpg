#!/bin/bash
set -e; cd "$(dirname "$0")"
export PATH="$HOME/dev/tools/jdk-21.0.12.1+1/bin:$PATH"
V=$(sed -n 's/^version="\(.*\)"/\1/p' res/META-INF/neoforge.mods.toml | head -1)
rm -rf build; mkdir -p build/cls
javac -proc:none --release 21 -nowarn -d build/cls -cp "/home/umbrel/dev/lab-p0/dev/libs/mixinextras-neoforge-0.5.5.jar:/home/umbrel/dev/purg4tory-identidad/cliente/mc/libraries/net/neoforged/neoforge/21.1.259/neoforge-21.1.259-client.jar:/home/umbrel/dev/purg4tory-identidad/cliente/mc/libraries/net/minecraft/client/1.21.1-20240808.144430/client-1.21.1-20240808.144430-srg.jar:$(cat ../dev/purg4tory_cauces/classpath.txt | tr ':' '\n' | grep -v neoforge-21.1.259-server.jar | paste -sd:)" $(find src -name '*.java')
cp -r res/* build/cls/
(cd build/cls && jar --create --file ../purg4tory_diagtick-$V.jar .)
ls -la build/*.jar
