# anyPS

> **Universal PlayStation 4 & PlayStation 5 to PC Translation Wrapper Template**  
> *Execute PS4 (Orbis OS) and PS5 (Prospero OS) x86-64 binaries directly on Windows PC with modular HLE and native Vulkan graphics.*

[![Platform](https://img.shields.io/badge/Platform-Windows%20x64-blue.svg)](https://microsoft.com/windows)
[![Graphics](https://img.shields.io/badge/Renderer-Vulkan%201.3+-red.svg)](https://vulkan.org)
[![Compiler](https://img.shields.io/badge/Toolchain-MSYS2%20Clang64-success.svg)](https://www.msys2.org/)
[![License](https://img.shields.io/badge/License-MIT%20%2F%20GPLv2-orange.svg)](LICENSE)

---

## Ikhtisar (Overview)

**anyPS** adalah kerangka kerja terpadu (*Universal Translation Wrapper*) modular untuk menjalankan biner game konsol **PlayStation 4** dan **PlayStation 5** langsung pada arsitektur Windows PC x86-64 tanpa overhead emulasi CPU penuh.

Karena kedua konsol menggunakan arsitektur x86-64 (AMD Jaguar pada PS4 dan AMD Zen 2 pada PS5), game dieksekusi secara native langsung di CPU host. Lapisan HLE modular menangani panggilan kernel Orbis OS maupun Prospero OS, dan pipeline grafis (Liverpool GNM & Oberon AGC) bermuara ke backend native **Vulkan 1.3+**.

---

## Fitur Utama

- ⚡ **Universal Multi-Platform HLE (`core/os/`):**
  - **PS4 (Orbis OS):** FreeBSD 9.0 kernel HLE, direct memory mapping (5056 MiB/4864 MiB), pthreads via TEB TLS.
  - **PS5 (Prospero OS):** FreeBSD 12+ kernel HLE, 16 GiB unified GDDR6 memory mapping, Zen 2 AVX2/FMA3 dispatch.
- 🔍 **Universal ELF/SELF Loader (`core/cpu/`):**
  - Deteksi otomatis biner PS4 vs PS5 dari header ELF64/SELF/PRX dan ekstensi SCE.
  - Pembaca versi SDK, Program Headers (`PT_SCE_PROGLIB`), dan relokasi dynamic linking.
- 🎮 **Modular Vulkan 1.3+ GPU Backend (`core/gpu/`):**
  - **PS4 GNM:** Dekoder paket PM4 Liverpool dan translator shader GCN ke SPIR-V.
  - **PS5 AGC:** Pipeline RDNA 2 modern, Primitive/Mesh Shaders, dan Ray Tracing acceleration abstraction.
  - **Unified Presenter:** Triple buffering bebas deadlock (`VK_PRESENT_MODE_MAILBOX_KHR`) dan pembatas framerate multimedia 1ms presisi.
- 🎯 **Target Modular (`targets/<platform>_<game_id>`):**
  - Konfigurasi game terpisah per platform: `ps4_jstars`, `ps4_basara4`, `ps5_template`.
  - Dukungan parameter build fleksibel: `-DPLATFORM=ps4 -DTARGET_GAME=jstars`.
- 🛠️ **REA Automated Triage (`tools/rea_triase.py`):**
  - Script analisis biner instan untuk memverifikasi format file, platform target, versi SDK, dan modul impor.

---

## Struktur Repositori

```
anyPS/
├── CMakeLists.txt            # Root build script (-DPLATFORM=... -DTARGET_GAME=...)
├── core/
│   ├── os/
│   │   ├── os_interface.h    # Kontrak antarmuka OS universal
│   │   ├── ps4/              # HLE Orbis OS: Virtual Memory, Threading, VFS, WASAPI
│   │   └── ps5/              # HLE Prospero OS: 16GB GDDR6, Zen 2, Tempest 3D
│   ├── cpu/
│   │   ├── elf_loader.h      # Universal ELF/SELF header reader & validator
│   │   └── elf_loader.c      # Detektor platform otomatis (PS4 vs PS5)
│   └── gpu/
│       ├── include/          # Kontrak GPU backend & shader translator
│       ├── gnm/              # PS4 Liverpool GNM (GCN -> SPIR-V)
│       ├── agc/              # PS5 Oberon AGC (RDNA 2 -> SPIR-V)
│       └── vulkan/           # Unified Vulkan 1.3+ Renderer & Presenter
├── targets/
│   ├── ps4_jstars/           # Profil referensi terverifikasi: J-Stars Victory VS+ (60 FPS Fix)
│   ├── ps4_basara4/          # Profil target berikutnya: Sengoku Basara 4: Sumeragi
│   ├── ps5_template/         # Kerangka boilerplate untuk target game PS5
│   └── template/             # Template target umum
├── tools/
│   ├── rea_triase.py         # Universal REA binary & SDK triage tool
│   ├── Launcher.cs           # Source launcher GUI C# WinForms asinkron
│   ├── win_build.sh          # Pipeline kompilasi otomatis MSYS2 Clang64
│   └── make_portable.ps1     # Script bundling 99 DLL runtime standalone
└── workspace/                # Direktori kerja lokal untuk dump game (dikecualikan Git)
```

---

## Panduan Cepat (Quick Start)

### 1. Prasyarat Sistem
- **Windows 10 / 11 64-bit**
- **MSYS2 Clang64 Environment:**
  ```bash
  pacman -S mingw-w64-clang-x86_64-clang mingw-w64-clang-x86_64-ninja mingw-w64-clang-x86_64-cmake
  pacman -S mingw-w64-clang-x86_64-vulkan-devel mingw-w64-clang-x86_64-sdl3 mingw-w64-clang-x86_64-ffmpeg
  ```
- **GPU:** Kompatibel Vulkan 1.3+ (NVIDIA Driver 550+, AMD Adrenalin 24+, Intel Arc)

### 2. Analisis Biner Game (Triage)
Jalankan script triage REA untuk mendeteksi platform dan konfigurasi target:
```bash
python tools/rea_triase.py path/to/eboot.bin
```

### 3. Kompilasi Target Spesifik

Gunakan parameter `PLATFORM` dan `TARGET_GAME`:

```bash
# Kompilasi J-Stars Victory VS+ (PS4)
cmake -B build -DPLATFORM=ps4 -DTARGET_GAME=jstars
cmake --build build

# Kompilasi Sengoku Basara 4 (PS4)
cmake -B build -DPLATFORM=ps4 -DTARGET_GAME=basara4
cmake --build build

# Kompilasi Target PS5
cmake -B build -DPLATFORM=ps5 -DTARGET_GAME=template
cmake --build build
```

---

## Status Target Game

| Platform | Game Profile | Title ID | Status | Catatan Teknis |
| :--- | :--- | :--- | :--- | :--- |
| **PS4** | `ps4_jstars` | CUSA01593 | **Playable (60 FPS)** | Havok timestep fix, delta-time 0.5x scale, VSync mailbox |
| **PS4** | `ps4_basara4` | CUSA02057 | **In-Triaging** | Capcom MT Framework engine, 60 FPS native |
| **PS5** | `ps5_template`| PPSA00000 | **Skeleton** | Template arsitektur Prospero OS & AGC pipeline |

---

## Legal & Clean-Room Disclaimer

Proyek **anyPS** dikembangkan semata-mata untuk tujuan penelitian interoperabilitas perangkat lunak (*clean-room reverse engineering*) dan preservasi game. 

- Repositori ini **TIDAK** menyertakan, mendistribusikan, maupun membagikan file game berhak cipta, dump file `eboot.bin`, ROM, file `.pkg`, file audio/grafis komersial, maupun file enkripsi/dekripsi milik Sony Interactive Entertainment atau penerbit game terkait.
- Pengguna wajib menyediakan dan mengekstrak file game legal milik sendiri dari konsol yang sah ke dalam direktori lokal `workspace/`.
