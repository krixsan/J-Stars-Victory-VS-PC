# Product Requirements Document (PRD)

## Project: anyPS — Universal PlayStation 4 & PlayStation 5 to PC Translation Wrapper
**Version:** 2.0.0 (Universal Architecture)  
**Author:** anyPS Core Architecture Team & Autonomous REA Agent  
**Status:** Approved / Active Modular Development  

---

## 1. Executive Summary & Objective

Tujuan dari proyek **anyPS** adalah menghadirkan kerangka kerja (*framework*) terpadu dan modular untuk menjalankan biner game konsol **PlayStation 4 (Orbis OS)** dan **PlayStation 5 (Prospero OS)** secara native di atas sistem operasi PC Windows modern x86-64.

Pendekatan *Universal Translation Wrapper* (HLE + Direct ISA Execution) dipilih untuk memberikan performa maksimal tanpa latensi emulasi CPU penuh:
- **Direct CPU Execution:** CPU AMD Jaguar (PS4) dan AMD Zen 2 (PS5) dieksekusi langsung pada CPU host x86-64.
- **Universal OS Abstraction (`core/os/`):**
  - **PS4 Module (`core/os/ps4/`):** Menjembatani panggilan kernel FreeBSD 9.0 Orbis OS (direct memory mapping 5056 MiB/4864 MiB, pthreads via TEB TLS).
  - **PS5 Module (`core/os/ps5/`):** Menjembatani panggilan kernel FreeBSD 12+ Prospero OS (16 GiB unified GDDR6 memory mapping, Zen 2 ISA features, Tempest 3D Audio).
- **Universal Binary & CPU Loader (`core/cpu/`):** Mendeteksi format ELF/SELF/PRX dan platform target (PS4 vs PS5) secara otomatis dari header dan metadata SCE.
- **Unified GPU Backend (`core/gpu/`):** Menerjemahkan paket grafis AMD Liverpool GNM (PS4) maupun AMD Oberon AGC (PS5) ke Vulkan 1.3+ dengan presenter triple-buffering non-blocking.
- **REA Binary Pacing:** Protokol Reverse Engineer Anything untuk mengidentifikasi frame limiter, timer structs, dan patch delta-time normalizer (60 FPS stabil).

---

## 2. Target Games & Roadmap

### Milestone 1: J-Stars Victory VS+ (`targets/ps4_jstars/`) — **COMPLETED & VERIFIED**
- **Platform:** PlayStation 4 (Orbis OS)
- **Title ID:** `CUSA01593` (US) / `CUSA01661` (EU)
- **Engine:** Custom Spike Chunsoft Fighting Engine + Havok Physics 2013
- **Fitur Kritis yang Telah Diselesaikan:**
  - [x] Ekstraksi PKG otomatis dan dynamic linking (`libc.prx`, `libSceFios2.prx`).
  - [x] Booting dan rendering Vulkan 1080p/1440p dengan FSR 1.0.
  - [x] Perbaikan 2x fast-forward pada 60 FPS via patch Havok physics timestep (`1/60s`) dan animation multiplier scaling (`0.5x`).
  - [x] Swapchain non-blocking `VK_PRESENT_MODE_MAILBOX_KHR` untuk mencegah hang pada GPU NVIDIA RTX 3050 Laptop.
  - [x] Adaptive memory pool (`4864 MiB`) untuk mengatasi limit Windows commit charge (Error 1450).
  - [x] Standalone interactive GUI Launcher (`Launcher.exe`) dengan live XInput gamepad polling.
  - [x] Script otomatisasi bundling portable (`make_portable.ps1`) dengan seluruh 99 runtime DLL.

### Milestone 2: Sengoku Basara 4: Sumeragi (`targets/ps4_basara4/`) — **IN PROGRESS**
- **Platform:** PlayStation 4 (Orbis OS)
- **Title ID:** `CUSA02057` (Japan) / `CUSA01134` (Asia)
- **Engine:** Capcom MT Framework (PS4 Native 64-bit Edition)
- **Rencana Kerja:**
  - [x] Profil target `targets/ps4_basara4/` disiapkan dengan hook stubs dan `target.ini`.
  - [x] Tooling `rea_triase.py` terintegrasi untuk analisis binary MT Framework.
  - [ ] Pemetaan file archive `.arc` ke Virtual File System (`runtime_file.c`).
  - [ ] Validasi native 60 FPS frame timing pada Capcom MT Framework engine loop.

### Milestone 3: PlayStation 5 Target Architecture (`targets/ps5_template/`) — **STAGING**
- **Platform:** PlayStation 5 (Prospero OS)
- **Title ID:** `PPSA00000` (Template)
- **Tujuan:**
  - [x] Abstraksi `core/os/ps5/` (Prospero runtime, kernel primitives, GDDR6 memory mapping).
  - [x] Abstraksi `core/gpu/agc/` untuk pipeline RDNA 2 dan primitive/mesh shaders.
  - [x] Deteksi otomatis biner Prospero via `core/cpu/elf_loader.c`.

---

## 3. Arsitektur Teknis anyPS

### 3.1 Sub-sistem OS Terpadu (`core/os/`)
1. **Antarmuka Universal (`core/os/os_interface.h`):**
   - Kontrak fungsi `anyps_os_ops_t` untuk inisialisasi lifecycle, alokasi memori direct, VFS mount, dan syscall dispatching.
2. **PS4 Orbis Subsystem (`core/os/ps4/`):**
   - HLE kernel lengkap dengan support Direct Memory 5056 MiB / 4864 MiB fallback, EventFlags, Semaphores, pthreads via TEB TLS slot (`__readgsqword(0x58)`), WASAPI audio, dan DualShock 4 mapping.
3. **PS5 Prospero Subsystem (`core/os/ps5/`):**
   - Ruang alamat guest 48-bit, 16 GiB virtual unified memory mapping, Zen 2 thread dispatch, Tempest 3D audio, dan DualSense adaptive trigger stubs.

### 3.2 Universal Loader (`core/cpu/`)
- Menganalisis file biner guest (ELF64, SELF, PRX, atau BBPROBE).
- Deteksi otomatis target ID (0x01 untuk PS4 vs 0x12 untuk PS5) dan ekstraksi versi SDK (`0xMMmmbbbb`).

### 3.3 Modular GPU Backend (`core/gpu/`)
- **GNM Translator (`core/gpu/gnm/`):** Mengurai PM4 command packets Liverpool dan menerjemahkan GCN ISA ke SPIR-V.
- **AGC Pipeline (`core/gpu/agc/`):** Mengurai command stream Oberon dan menangani fitur grafis RDNA 2 (Mesh Shaders, BVH Ray Tracing).
- **Vulkan Core (`core/gpu/vulkan/`):** Renderer terpadu dengan swapchain `VK_PRESENT_MODE_MAILBOX_KHR`, temporal upscaling (FSR 1.0 & FSR 3.1), serta frame pacing multimedia sub-millisecond.

### 3.4 Target Management & Build System
- Pengelompokan direktori target: `targets/<platform>_<game_id>/`.
- CMake modular menerima parameter:
  ```bash
  cmake -B build -DPLATFORM=<ps4|ps5> -DTARGET_GAME=<game_id>
  cmake --build build
  ```

---

## 4. Keamanan & Kepatuhan Hukum

- Proyek ini sepenuhnya beroperasi di bawah prinsip *clean-room reverse engineering*.
- Tidak ada file game berhak cipta (`.pkg`, `.prx`, `.bin`, `.cpk`) atau data proprietary Sony Interactive Entertainment yang didistribusikan dalam repositori ini.
- Semua dump game pengguna diisolasi di direktori lokal `workspace/` yang secara ketat dikecualikan dari Git melalui `.gitignore`.
