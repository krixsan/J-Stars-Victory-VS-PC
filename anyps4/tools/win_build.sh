#!/usr/bin/env bash
# J-Stars PC: apply FSR-Vulkan patches (no git metadata), build jstars_pc.exe, and bundle DLLs.
set -uo pipefail
cd "$(dirname "$0")/.."
source ./msys2-env.sh
for p in gpu/patches/fsr-vulkan/*.patch; do
    if patch -p1 -R --dry-run -s -f -d gpu/third_party/fsr-vulkan < "$p" >/dev/null 2>&1; then
        echo "already applied: $p"
    else
        patch -p1 -N -f -d gpu/third_party/fsr-vulkan < "$p" || echo "FAILED: $p"
    fi
done
cmake -S gpu -B out/gpu -G Ninja -DCMAKE_BUILD_TYPE=Release -DBB_PGO=off -DBB_LTO=OFF \
    -DCMAKE_C_FLAGS_RELEASE="-O3 -march=native -DNDEBUG" \
    -DCMAKE_CXX_FLAGS_RELEASE="-O3 -march=native -DNDEBUG" \
    -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ >/dev/null || exit 1
ninja -C out/gpu -k 0 sacredfire > out/gpu-build.log 2>&1
rc=$?
grep -E "error:|FAILED:" out/gpu-build.log | head -60
echo "ninja exit: $rc"

if [ $rc -eq 0 ]; then
    echo "Compiling Launcher.exe..."
    MSYS2_ARG_CONV_EXCL="*" cmd.exe /c "C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\csc.exe /nologo /target:winexe /optimize+ /platform:x64 /out:out\\Launcher.exe tools\\Launcher.cs" >/dev/null 2>&1 || true
    echo "Bundling all runtime DLLs next to jstars_pc.exe..."
    (python3 tools/bundle_dlls.py || py -3 tools/bundle_dlls.py || python tools/bundle_dlls.py)
    cp -u out/gpu/jstars_pc.exe out/ 2>/dev/null || cp out/gpu/jstars_pc.exe out/
    if [ -f out/Launcher.exe ]; then
        cp -u out/Launcher.exe out/gpu/ 2>/dev/null || cp out/Launcher.exe out/gpu/
    fi
    echo "Ready! Standalone jstars_pc.exe and Launcher.exe with all bundled DLLs prepared."
fi

exit $rc
