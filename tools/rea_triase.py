#!/usr/bin/env python
"""
tools/rea_triase.py - anyPS Universal Binary Triage & Target Analyzer
Analyzes PS4/PS5 eboot.bin (ELF/SELF/PRX) to detect:
- Target Platform: PlayStation 4 (Orbis OS) vs PlayStation 5 (Prospero OS)
- System Software & SDK Version (e.g., 05.050.001 vs 02.000.001)
- CPU ISA Architecture (AMD Jaguar vs AMD Zen 2)
- GPU Graphics Driver (Liverpool GNM vs Oberon AGC)
- Imported Dynamic Modules & System Calls
- Recommended anyPS Target Configuration (targets/<platform>_<game_id>)
"""

import sys
import os
import struct

SELF_MAGIC = b'\x4f\x15\x3d\x1d'  # 0x1D3D154F
ELF_MAGIC  = b'\x7f\x45\x4c\x46'  # 0x464C457F

PT_SCE_RELA         = 0x60000000
PT_SCE_DYNLIBDATA   = 0x61000000
PT_SCE_PROGLIB      = 0x61000001
PT_SCE_PROC_PARAM   = 0x61000001
PT_SCE_MODULE_PARAM = 0x61000002
PT_SCE_RELRO        = 0x61000010

SELF_TARGET_PS4 = 0x01
SELF_TARGET_PS5 = 0x12


def format_sdk(sdk_val):
    if not sdk_val:
        return "Unknown / Not found"
    major = (sdk_val >> 24) & 0xFF
    minor = (sdk_val >> 12) & 0xFFF
    build = sdk_val & 0xFFF
    return "{:02d}.{:03d}.{:03d} (0x{:08X})".format(major, minor, build, sdk_val)


def triase_binary(file_path):
    if not os.path.exists(file_path):
        print("[!] Error: File '{}' does not exist.".format(file_path))
        return None

    file_size = os.path.getsize(file_path)
    print("\n============================================================")
    print("             anyPS Universal REA Triage Report              ")
    print("============================================================")
    print(" Target File     : {}".format(os.path.abspath(file_path)))
    print(" File Size       : {:,} bytes ({:.2f} MiB)".format(file_size, file_size / (1024.0 * 1024.0)))

    with open(file_path, "rb") as f:
        magic = f.read(4)
        f.seek(0)

        platform = "Unknown"
        sdk_version = None
        target_id = None
        format_type = "Unknown"
        imported_libs = set()

        if magic == SELF_MAGIC:
            format_type = "Signed ELF (SELF / FPKG)"
            # Parse SELF Header
            hdr_data = f.read(32)
            if len(hdr_data) >= 32:
                _, version, mode, endian, attrs = struct.unpack('<4s4B', hdr_data[:8])
                content_type, key_type, hdr_sz, meta_sz, fsz, entry_count, flags = struct.unpack('<2B2x2HQ2H4x', hdr_data[8:32])
                target_id = content_type

                if target_id == SELF_TARGET_PS5:
                    platform = "PlayStation 5 (Prospero OS)"
                elif target_id == SELF_TARGET_PS4:
                    platform = "PlayStation 4 (Orbis OS)"
                else:
                    platform = "PlayStation Unknown (TargetID 0x{:02X})".format(target_id)

        elif magic == ELF_MAGIC:
            format_type = "Standard ELF64 Executable"
            ehdr_data = f.read(64)
            if len(ehdr_data) >= 64:
                e_type, e_machine, e_version, e_entry, e_phoff, e_shoff, e_flags, e_ehsize, e_phentsize, e_phnum, e_shentsize = struct.unpack(
                    '<HHIQQQIHHHH', ehdr_data[16:60]
                )

                if e_phoff > 0 and e_phnum > 0 and e_phoff < file_size:
                    f.seek(e_phoff)
                    for _ in range(min(e_phnum, 128)):
                        phdr_bytes = f.read(56)
                        if len(phdr_bytes) < 56:
                            break
                        p_type, p_flags, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align = struct.unpack(
                            '<IIQQQQQQ', phdr_bytes
                        )

                        if p_type in (PT_SCE_PROC_PARAM, PT_SCE_PROGLIB) and p_offset < file_size:
                            cur_pos = f.tell()
                            f.seek(p_offset)
                            param_head = f.read(min(p_filesz, 64))
                            if len(param_head) >= 16:
                                sz = struct.unpack('<Q', param_head[:8])[0]
                                if sz <= p_filesz and len(param_head) >= 16:
                                    sdk_cand = struct.unpack('<I', param_head[12:16])[0]
                                    if 0x01000000 <= sdk_cand <= 0x12000000:
                                        sdk_version = sdk_cand
                            f.seek(cur_pos)

        # Scan for imported libraries and symbols across entire binary
        f.seek(0)
        chunk = f.read(min(file_size, 64 * 1024 * 1024))

        lib_signatures = [
            b"libkernel", b"libSceGnmDriver", b"libSceAgc", b"libScePad",
            b"libSceAudioOut", b"libSceVideoOut", b"libSceFios2", b"libSceSaveData",
            b"libSceSysmodule", b"libSceNet", b"libSceRtc", b"libSceAjm",
            b"libSceUserService", b"libSceCamera", b"libSceNpScore"
        ]

        for sig in lib_signatures:
            if sig in chunk:
                imported_libs.add(sig.decode("ascii", errors="ignore"))

        # Look for adjacent param.sfo
        title_id = None
        system_ver = None
        search_dirs = [
            os.path.join(os.path.dirname(file_path), "sce_sys", "param.sfo"),
            os.path.join(os.path.dirname(os.path.dirname(file_path)), "sce_sys", "param.sfo"),
            "extracted_game/app0/sce_sys/param.sfo"
        ]
        for sfo_path in search_dirs:
            if os.path.exists(sfo_path):
                try:
                    with open(sfo_path, "rb") as sfo_f:
                        sfo_data = sfo_f.read()
                        # Extract TITLE_ID (e.g. CUSA01593 / PPSA01234)
                        for m in (b"CUSA", b"PPSA", b"CUSA"):
                            idx = sfo_data.find(m)
                            if idx != -1:
                                title_id = sfo_data[idx:idx+9].decode("ascii", errors="ignore")
                                break
                        # If PPSA found in sfo, platform is PS5
                        if title_id and title_id.startswith("PPSA"):
                            platform = "PlayStation 5 (Prospero OS)"
                        elif title_id and title_id.startswith("CUSA"):
                            platform = "PlayStation 4 (Orbis OS)"
                except Exception:
                    pass
                if title_id:
                    break

        if platform == "Unknown":
            if "libSceAgc" in imported_libs:
                platform = "PlayStation 5 (Prospero OS)"
            elif "libSceGnmDriver" in imported_libs or "libSceVideoOut" in imported_libs:
                platform = "PlayStation 4 (Orbis OS)"
            else:
                platform = "PlayStation 4 (Orbis OS / Fallback)"

        # CPU & GPU architecture characteristics
        if "PlayStation 5" in platform:
            cpu_isa = "AMD Zen 2 (8 Cores / 16 Threads, AVX2, FMA3, BMI2)"
            gpu_api = "Oberon AGC (RDNA 2, Mesh Shaders, Ray Tracing Acceleration)"
            platform_code = "ps5"
        else:
            cpu_isa = "AMD Jaguar (8 Cores, AVX, BMI1, MOVBE, POPCNT)"
            gpu_api = "Liverpool GNM (GCN, PM4 Type-3 Command Buffers)"
            platform_code = "ps4"

        print(" Binary Format   : {}".format(format_type))
        print(" Platform Target : {}".format(platform))
        print(" Title ID        : {}".format(title_id if title_id else 'Not specified / Embedded'))
        print(" SDK Version     : {}".format(format_sdk(sdk_version)))
        print(" CPU Subsystem   : {}".format(cpu_isa))
        print(" GPU Subsystem   : {}".format(gpu_api))
        print(" Key Modules     : {}".format(', '.join(sorted(imported_libs)) if imported_libs else 'None detected in head chunk'))
        print("------------------------------------------------------------")
        print(" Recommended anyPS Build Configuration:")
        print("   cmake -B build -DPLATFORM={} -DTARGET_GAME=<game_id>".format(platform_code))
        print("   cmake --build build")
        print(" Recommended Target Folder:")
        print("   targets/{}_<game_id>/".format(platform_code))
        print("============================================================\n")

        return {
            "platform": platform,
            "platform_code": platform_code,
            "format": format_type,
            "sdk_version": sdk_version,
            "imported_libs": list(imported_libs)
        }


def main():
    target = None
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        # Check standard default paths
        candidates = [
            "workspace/eboot.bin",
            "extracted_game/app0/eboot.bin",
            "extracted_game/eboot.bin",
            "eboot.bin"
        ]
        for c in candidates:
            if os.path.exists(c):
                target = c
                break

    if not target:
        print("[anyPS:Triage] Usage: python tools/rea_triase.py <path/to/eboot.bin>")
        print("[anyPS:Triage] No eboot.bin found in default locations (workspace/ or extracted_game/app0/).")
        sys.exit(0)

    triase_binary(target)


if __name__ == "__main__":
    main()
