# J-Stars Victory VS+ | Portable Distribution Packager
# Assembles a standalone portable package ready to play on any Windows 10/11 x64 PC.

param(
    [string]$OutputDir = "JStars_PC_Portable",
    [switch]$IncludeGameData = $true
)

$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$target = Join-Path $root $OutputDir

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  J-STARS VICTORY VS+ PC | PORTABLE PACKAGER" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Output Directory: $target" -ForegroundColor Gray

# 1. Prepare target directory
if (Test-Path $target) {
    Write-Host "[1/6] Cleaning existing portable directory..." -ForegroundColor Yellow
    Remove-Item -Path $target -Recurse -Force
}
New-Item -ItemType Directory -Path $target | Out-Null
New-Item -ItemType Directory -Path (Join-Path $target "extracted_game\app0\savedata") | Out-Null

# 2. Build / Compile Launcher.exe if not already compiled
$launcherExe = Join-Path $root "out\Launcher.exe"
if (-not (Test-Path $launcherExe)) {
    Write-Host "[2/6] Compiling Launcher.exe via .NET csc.exe..." -ForegroundColor Yellow
    $csc = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
    $launcherSrc = Join-Path $root "tools\Launcher.cs"
    & $csc /target:winexe /optimize+ /platform:x64 /out:$launcherExe $launcherSrc | Out-Null
}

Write-Host "[3/6] Copying executables and core boot image..." -ForegroundColor Green
Copy-Item (Join-Path $root "out\Launcher.exe") -Destination $target
Copy-Item (Join-Path $root "out\jstars_pc.exe") -Destination $target
Copy-Item (Join-Path $root "out\boot-linked.bin") -Destination $target
Copy-Item (Join-Path $root "out\import_names.txt") -Destination $target

# 3. Copy all 99 runtime DLLs from out/
Write-Host "[4/6] Bundling all 99 standalone runtime DLLs..." -ForegroundColor Green
$dlls = Get-ChildItem -Path (Join-Path $root "out") -Filter "*.dll"
$copiedDllCount = 0
foreach ($dll in $dlls) {
    Copy-Item $dll.FullName -Destination $target
    $copiedDllCount++
}
Write-Host "  -> Successfully copied $copiedDllCount DLLs into portable folder." -ForegroundColor Gray

# 4. Copy extracted game data
if ($IncludeGameData -and (Test-Path (Join-Path $root "extracted_game\app0"))) {
    Write-Host "[5/6] Copying game data assets (extracted_game\app0)..." -ForegroundColor Green
    $destApp0 = Join-Path $target "extracted_game\app0"
    
    # Use robocopy for fast, reliable copy of game files excluding temp savedata
    $srcApp0 = Join-Path $root "extracted_game\app0"
    robocopy $srcApp0 $destApp0 /E /NFL /NDL /NJH /NJS /nc /ns /np /XD "$srcApp0\savedata" | Out-Null
    
    # Ensure savedata folder exists
    $destSavedata = Join-Path $destApp0 "savedata"
    if (-not (Test-Path $destSavedata)) {
        New-Item -ItemType Directory -Path $destSavedata | Out-Null
    }
    Write-Host "  -> Game assets copied successfully." -ForegroundColor Gray
} else {
    Write-Host "[5/6] Notice: extracted_game\app0 skipped or not present." -ForegroundColor Yellow
}

# 5. Create README and Launch Shortcut
Write-Host "[6/6] Generating documentation & quick-launch script..." -ForegroundColor Green

$readmeContent = @"
====================================================================
  J-STARS VICTORY VS+ (PS4 NATIVE PC PORT) - PORTABLE EDITION
====================================================================

CARA MEMAINKAN:
1. Cukup klik dua kali `Launcher.exe` untuk membuka menu pengaturan & bermain.
2. Anda juga dapat langsung menjalankan `Play_Game.bat` atau `jstars_pc.exe`.

FITUR UTAMA PORTING:
- 60 FPS Mode: Animasi & pergerakan berjalan mulus 60 FPS dengan kecepatan waktu normal (Delta Time Fixed).
- 30 FPS Mode: Mode asli konsol PS4 dapat dipilih lewat Launcher jika diinginkan.
- Vulkan Renderer: Menggunakan arsitektur shadPS4 Vulkan core dengan VSync FIFO locked.
- AMD FSR Upscaling: Meningkatkan ketajaman grafis secara real-time.
- Standalone: Seluruh 99 runtime DLL sudah dibundle langsung. Tidak memerlukan MSYS2, Python, atau software eksternal.

KONTROL DEFAULT:
- Gamepad: Stik Xbox One / Xbox Series / DualShock 4 / DualSense (XInput plug-and-play).
- Keyboard:
    W, A, S, D       : Gerakan Karakter
    J, K, L, I       : Kotak, Segitiga, Bulat, Silang (Attack / Jump / Special)
    U, O             : L1 / R1 (Guard / Lock-on)
    Q, E             : L2 / R2 (Charge / Burst Tag)
    Enter / Space    : Start / Pause
    Insert / F1      : Buka Menu In-Game Overlay

LOKASI SAVE DATA:
- extracted_game\app0\savedata\

Selamat bermain!
====================================================================
"@
Set-Content -Path (Join-Path $target "README_PORTABLE.txt") -Value $readmeContent -Encoding UTF8

$batContent = @"
@echo off
cd /d "%~dp0"
start "" "Launcher.exe"
"@
Set-Content -Path (Join-Path $target "Play_Game.bat") -Value $batContent -Encoding ASCII

$directContent = @"
@echo off
cd /d "%~dp0"
start "" "jstars_pc.exe" boot-linked.bin --app0 extracted_game/app0 --import-names import_names.txt
"@
Set-Content -Path (Join-Path $target "Play_Direct.bat") -Value $directContent -Encoding ASCII

# Summary
$sizeBytes = (Get-ChildItem -Path $target -Recurse | Measure-Object -Property Length -Sum).Sum
$sizeMB = [math]::Round($sizeBytes / 1MB, 2)
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  PORTABLE PACKAGE READY: $target" -ForegroundColor Green
Write-Host "  Total Size: $sizeMB MB" -ForegroundColor Yellow
Write-Host "  Double-click Launcher.exe to play!" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
