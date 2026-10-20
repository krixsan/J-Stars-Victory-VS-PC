#!/usr/bin/env python3
import os
import sys
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLANG_BIN = Path(os.environ.get('MSYS2_ROOT', 'C:/msys64')) / 'clang64' / 'bin'

SYSTEM_DLLS = {
    'kernel32', 'user32', 'gdi32', 'advapi32', 'shell32', 'ole32', 'oleaut32', 'ws2_32',
    'msvcrt', 'ntdll', 'bcrypt', 'bcryptprimitives', 'crypt32', 'secur32', 'winmm',
    'imm32', 'setupapi', 'version', 'shlwapi', 'comdlg32', 'comctl32', 'rpcrt4',
    'dwmapi', 'd3d11', 'dxgi', 'd3d9', 'd3d12', 'dxva2', 'mf', 'mfplat', 'mfuuid',
    'mfreadwrite', 'uxtheme', 'cfgmgr32', 'hid', 'opengl32', 'vulkan-1', 'iphlpapi',
    'mswsock', 'dnsapi', 'ncrypt', 'usp10', 'shcore', 'cabinet', 'wldap32', 'normaliz',
    'avrt', 'msimg32', 'propsys', 'windowscodecs', 'mmdevapi', 'powrprof', 'userenv',
    'psapi', 'netapi32', 'wsock32', 'd3dcompiler_47', 'gdiplus', 'd2d1', 'dwrite',
    'dinput8', 'xinput1_4', 'ucrtbase', 'vcruntime140', 'msvcp140', 'winspool',
    'cryptbase', 'sspicli', 'wintrust', 'rtworkq', 'ksuser', 'wevtapi', 'ntmarta',
    'dsparse', 'gdi32full', 'combase', 'msvcp_win', 'onecore'
}

def get_pe_imports(path):
    objdump = CLANG_BIN / 'llvm-objdump.exe'
    out = subprocess.run([str(objdump), '-p', str(path)],
                         capture_output=True, text=True, errors='replace').stdout
    names = set()
    for m in re.finditer(r'DLL Name:\s*(\S+)', out, re.IGNORECASE):
        names.add(m.group(1))
    return names

def get_transitive_dlls(binaries):
    found = {}
    queue = list(binaries)
    visited = set()
    while queue:
        curr = queue.pop()
        if curr in visited:
            continue
        visited.add(curr)
        for dll_name in get_pe_imports(curr):
            dll_lower = dll_name.lower()
            stem = dll_lower[:-4] if dll_lower.endswith('.dll') else dll_lower
            if stem in SYSTEM_DLLS or dll_lower.startswith(('api-ms-', 'ext-ms-')):
                continue
            if dll_lower in found:
                continue
            src = CLANG_BIN / dll_name
            if not src.is_file():
                # Case-insensitive search in CLANG_BIN
                matches = list(CLANG_BIN.glob(f"*[iI][nN]*")) # fallback
                for f in CLANG_BIN.iterdir():
                    if f.name.lower() == dll_lower:
                        src = f
                        break
            if src.is_file():
                found[dll_lower] = src
                queue.append(src)
    return found

def bundle(target_dirs):
    exe = ROOT / 'out' / 'gpu' / 'jstars_pc.exe'
    if not exe.is_file():
        exe = ROOT / 'out' / 'gpu' / 'sacredfire.exe'
    if not exe.is_file():
        print(f"Error: {exe} not found", file=sys.stderr)
        return False

    dlls = get_transitive_dlls([exe])
    print(f"Found {len(dlls)} dependency DLLs from clang64/bin for {exe.name}:")
    for name in sorted(dlls.keys()):
        print(f"  - {name} ({dlls[name]})")

    for target_dir in target_dirs:
        target_dir = Path(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        # Also copy jstars_pc.exe if needed
        if target_dir != exe.parent and exe.is_file():
            shutil.copy2(exe, target_dir / 'jstars_pc.exe')
        copied = 0
        for dll_lower, src in dlls.items():
            dst = target_dir / src.name
            if not dst.is_file() or dst.stat().st_size != src.stat().st_size:
                shutil.copy2(src, dst)
                copied += 1
        print(f"Verified {len(dlls)} DLLs in {target_dir} ({copied} newly copied).")
    return True

if __name__ == '__main__':
    targets = [ROOT / 'out' / 'gpu', ROOT / 'out']
    if len(sys.argv) > 1:
        targets = [Path(p) for p in sys.argv[1:]]
    success = bundle(targets)
    sys.exit(0 if success else 1)
