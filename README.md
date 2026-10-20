# anyPS4

> **Modular PlayStation 4 to PC Native Translation Wrapper Template**  
> *Execute PS4 x86-64 games directly on Windows without full-system emulation overhead.*

[![Platform](https://img.shields.io/badge/Platform-Windows%20x64-blue.svg)](https://microsoft.com/windows)
[![Graphics](https://img.shields.io/badge/Renderer-Vulkan%201.3+-red.svg)](https://vulkan.org)
[![Compiler](https://img.shields.io/badge/Toolchain-MSYS2%20Clang64-success.svg)](https://www.msys2.org/)
[![License](https://img.shields.io/badge/License-MIT%20%2F%20GPLv2-orange.svg)](LICENSE)

---

## Ikhtisar (Overview)

**anyPS4** adalah kerangka kerja modular berbasis template untuk mengubah game konsol PlayStation 4 (Orbis OS x86-64) menjadi game Native Windows PC. 

Dengan memanfaatkan arsitektur prosesor PS4 yang sudah berbasis x86-64, game dijalankan langsung pada CPU komputer tanpa emulasi instruksi CPU. Panggilan sistem operasi (*syscalls*) dan library native ditangani melalui lapisan HLE (*High-Level Emulation*), dan perintah grafis AMD Liverpool GNM diterjemahkan secara real-time ke **Vulkan 1.3+**.

---

## Fitur Utama

- ⚡ **Native x86-64 Execution:** Performa CPU maksimal tanpa kompilasi ulang JIT dinamis.
- 🎮 **Vulkan 1.3+ Graphics Backend:** Renderer Vulkan berkemampuan tinggi dengan dukungan multi-threading command recording dan FSR upscaling.
- ⏱️ **60 FPS & Delta-Time Fixed:** Protokol REA terintegrasi untuk menormalkan kecepatan permainan (mencegah *fast-forward* 2x lipat saat 60 FPS dibuka).
- 🕹️ **Controller Ready (XInput & SDL3):** Dukungan penuh plug-and-play untuk stik Xbox Series/One, DualShock 4, DualSense, serta Keyboard.
- 📦 **1-Click Standalone Bundling:** Otomatisasi pembuatan paket game portabel lengkap dengan seluruh 99 runtime DLL tanpa membutuhkan instalasi software eksternal di komputer pengguna.
- 🖥️ **Custom GUI Launcher:** Launcher interaktif dengan status koneksi stik real-time, pengatur resolusi, dan pemilih FPS.

---

## Struktur Repositori

```
anyPS4/
├── core/
│   ├── runtime/       # HLE Kernel PS4: Memory, Threads, VFS, Audio WASAPI, Gamepad
│   └── gpu/           # Liverpool GNM to Vulkan 1.3 translation backend
├── targets/
│   ├── template/      # Kerangka boilerplate untuk target game baru
│   ├── jstars/        # Profil referensi terverifikasi: J-Stars Victory VS+ (60 FPS)
│   └── basara4/       # Profil target berikutnya: Sengoku Basara 4: Sumeragi
├── tools/             # Script build, analisis binary ELF, dan packaging portable
├── workspace/         # Area kerja lokal untuk file game (dikecualikan dari Git)
├── anyPS4.md          # Dokumen arsitektur lengkap
└── PRD.md             # Product Requirements Document
```

---

## Panduan Cepat (Quick Start)

### 1. Prasyarat Sistem
- **Windows 10 / 11 64-bit**
- **MSYS2 Clang64 Toolchain:**
  ```bash
  pacman -S mingw-w64-clang-x86_64-clang mingw-w64-clang-x86_64-ninja mingw-w64-clang-x86_64-cmake
  ```
- **GPU:** Mendukung Vulkan 1.3+ (NVIDIA Driver 550+, AMD Adrenalin 24+, Intel Arc)

### 2. Membangun Proyek (Build)
Buka terminal MSYS2 Clang64 di direktori repositori:
```bash
./tools/win_build.sh
```

### 3. Membuat Paket Portable Standalone
Buka PowerShell dan jalankan:
```powershell
.\tools\make_portable.ps1
```
Hasil paket portabel siap dimainkan akan berada di direktori `JStars_PC_Portable/`.

---

## Status Target Game

| Target Game | Engine | Status | Framerate |
| :--- | :--- | :---: | :---: |
| **J-Stars Victory VS+** (`CUSA01593` / `CUSA01661`) | Custom + Havok | **Playable (100%)** | 60 FPS (Speed Fixed) |
| **Sengoku Basara 4: Sumeragi** (`CUSA02057`) | MT Framework | Planned / In Triage | 60 FPS Target |
| **Custom Target Template** | Any | Ready to Use | Configurable |

---

## Pernyataan Hukum & Hak Cipta (Disclaimer)

> Repositori **anyPS4** tidak mendistribusikan, menyertakan, atau membagikan file game berhak cipta, ROM, dump ISO/PKG, file sistem PlayStation 4 resmi, atau kunci kriptografi apa pun milik Sony Interactive Entertainment atau pengembang game terkait.
> 
> Pengguna bertanggung jawab penuh untuk menyediakan salinan game resmi (*clean game dump*) yang diperoleh dari media fisik atau digital milik pribadi secara sah.
