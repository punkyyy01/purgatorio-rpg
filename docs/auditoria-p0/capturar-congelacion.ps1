# PURG4TORY - captura DURANTE una congelación del mundo (un jugador). Solo lee: no toca el juego ni el mundo.
# Uso (PowerShell, con el juego congelado y SIN salir del mundo):
#   powershell -ExecutionPolicy Bypass -File capturar-congelacion.ps1 -Jdk "C:\jdk-21" -Instancia "C:\...\Instances\PURG4TORY..."
param(
  [Parameter(Mandatory=$true)][string]$Jdk,         # carpeta de un JDK 21 (Temurin zip); necesita bin\jcmd.exe
  [Parameter(Mandatory=$true)][string]$Instancia,   # carpeta de la instancia de CurseForge (la que contiene mods\ y logs\)
  [int]$Volcados = 12, [int]$Intervalo = 5
)
$ErrorActionPreference = 'Continue'
$jcmd = Join-Path $Jdk 'bin\jcmd.exe'
if (-not (Test-Path $jcmd)) { Write-Host "No encuentro $jcmd"; exit 1 }
$fecha = Get-Date -Format 'yyyyMMdd-HHmmss'
$dest = Join-Path ([Environment]::GetFolderPath('Desktop')) "purg4tory-captura-$fecha"
New-Item -ItemType Directory -Force -Path $dest | Out-Null
# El proceso del juego: javaw/java con NeoForge en la línea de órdenes
$p = Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^javaw?\.exe$' -and $_.CommandLine -match 'neoforge' } | Select-Object -First 1
if (-not $p) { Write-Host 'No encuentro el proceso de Minecraft (javaw.exe con neoforge)'; exit 1 }
$procId = $p.ProcessId
Write-Host "Minecraft PID $procId; guardando en $dest"
$p.CommandLine | Out-File -Encoding utf8 (Join-Path $dest 'linea-de-ordenes.txt')
for ($i = 1; $i -le $Volcados; $i++) {
  $f = Join-Path $dest ("hilos-{0:D2}-{1}.txt" -f $i, (Get-Date -Format 'HHmmss'))
  & $jcmd $procId Thread.print -l 2>&1 | Out-File -Encoding utf8 $f
  Write-Host "volcado $i/$Volcados"
  if ($i -eq 1) { & $jcmd $procId GC.heap_info 2>&1 | Out-File -Encoding utf8 (Join-Path $dest 'memoria.txt') }
  Start-Sleep -Seconds $Intervalo
}
# Registros tal y como están AHORA (latest.log se sobrescribe al volver a abrir el juego)
foreach ($r in 'logs\latest.log','logs\debug.log') { $o = Join-Path $Instancia $r; if (Test-Path $o) { Copy-Item $o $dest } }
Get-ChildItem $Instancia -Filter 'streamsreflowing-stall-*.txt' -ErrorAction SilentlyContinue | Copy-Item -Destination $dest
Get-ChildItem $Instancia -Filter 'purg4tory-congelacion-*.txt' -ErrorAction SilentlyContinue | Copy-Item -Destination $dest
Get-ChildItem (Join-Path $Instancia 'crash-reports') -ErrorAction SilentlyContinue | Copy-Item -Destination $dest
Compress-Archive -Path "$dest\*" -DestinationPath "$dest.zip" -Force
Write-Host "Listo: $dest.zip  (ahora ya puedes salir del mundo; apunta cuánto tarda «Guardando el mundo»)"
