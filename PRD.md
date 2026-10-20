# Product Requirements Document (PRD)

## Project: anyPS4 — Modular PlayStation 4 to PC Translation Wrapper Template
**Version:** 1.0.0  
**Author:** anyPS4 Core Team & Autonomous REA Agent  
**Status:** Approved / Active Development  

---

## 1. Executive Summary & Objective

Tujuan dari proyek **anyPS4** adalah menciptakan kerangka kerja (*framework*) berbasis repositori template modular yang memungkinkan game PlayStation 4 (berbasis prosesor x86-64) dijalankan secara *native* pada PC Windows modern. 

Alih-alih menggunakan emulator sistem penuh yang membutuhkan virtualisasi CPU berat, **anyPS4** menggunakan pendekatan *translation wrapper* (mirip dengan Proton/Wine untuk DirectX-ke-Vulkan, dan arsitektur bbport/CTR-NitroFueled):
- CPU guest mengeksekusi instruksi x86-64 langsung di prosesor host.
- Syscall kernel Orbis OS FreeBSD di-jembatani oleh runtime HLE berkinerja tinggi.
- Perintah grafis AMD Liverpool GNM diterjemahkan secara real-time ke Vulkan 1.3+.
- Frame timer & delta time dinormalisasi menggunakan metodologi **REA (Reverse Engineer Anything)** agar game dapat berjalan pada 60 FPS tanpa efek *fast-forward*.

---

## 2. Target Games & Roadmap

### Milestone 1: J-Stars Victory VS+ (`targets/jstars/`) — **COMPLETED & VERIFIED**
- **Title ID:** `CUSA01593` (US) / `CUSA01661` (EU)
- **Engine:** Custom Spike Chunsoft Fighting Engine + Havok Physics 2013
- **Fitur Kritis yang Telah Diselesaikan:**
  - [x] Ekstraksi PKG otomatis dan linking dynamic modules (`libc.prx`, `libSceFios2.prx`).
  - [x] Booting dan rendering Vulkan 1080p/1440p dengan FSR 1.0.
  - [x] Perbaikan 2x fast-forward pada 60 FPS via patch Havok physics timestep (`1/60s`) dan animation multiplier scaling (`0.5x`).
  - [x] Swapchain non-blocking `VK_PRESENT_MODE_MAILBOX_KHR` untuk mencegah hang pada GPU NVIDIA RTX 3050 Laptop.
  - [x] Adaptive memory pool (`4864 MiB`) untuk mengatasi limit Windows commit charge (Error 1450).
  - [x] Standalone interactive GUI Launcher (`Launcher.exe`) dengan live XInput gamepad polling.
  - [x] Script otomatisasi bundling portable (`make_portable.ps1`) dengan seluruh 99 runtime DLL.

### Milestone 2: Sengoku Basara 4: Sumeragi (`targets/basara4/`) — **PLANNED / IN PROGRESS**
- **Title ID:** `CUSA02057` (Japan) / `CUSA01134` (Asia)
- **Engine:** Capcom MT Framework (PS4 Native 64-bit Edition)
- **Rencana Kerja:**
  - [ ] Binary triaging `eboot.bin` dan dekompilasi Dynamic Symbol Table menggunakan `rea_analyzer.py`.
  - [ ] Pemetaan sistem file archive Capcom `.arc` ke Virtual File System (`runtime_file.c`).
  - [ ] Verifikasi native 60 FPS pacing pada pipeline rendering MT Framework.
  - [ ] Pembuatan target profile dan pengemasan portabel.

---

## 3. Arsitektur Core HLE & Spesifikasi Sistem

### 3.1 Core Runtime (`core/runtime/`)
1. **Memory Management:**
   - Reservasi virtual address range PS4 (`0x1000000000` s.d. `0xfc00000000`) sebelum DLL Windows dialokasikan.
   - Pemanfaatan `CreateFileMapping2` dan `MapViewOfFile3` dengan `MEM_REPLACE_PLACEHOLDER`.
   - Mekanisme *auto-retry* dan *adaptive memory fallback* untuk stabilitas alokasi di PC dengan RAM terbatas.
2. **Multi-threading & Synchronizations:**
   - Konversi thread POSIX/FreeBSD ke Windows Threads.
   - Slot TCB guest dialokasikan pada TEB TLS slot Windows (`__readgsqword(0x58)`).
   - Implementasi lengkap primitif sinkronisasi: `SceKernelEventFlag`, `SceKernelSemaphore`, dan `Equeue`.
3. **Virtual File System (VFS):**
   - Mount layer modular: `/app0` (read-only game assets), `/savedata` (user writable), `/hostapp`.
   - Dukungan akses thread-safe untuk sistem file archive game (CRI Middleware CPK, Capcom ARC).
4. **Audio Subsystem:**
   - Output audio multi-channel WASAPI (float 32-bit, 48.000 Hz, 8-channel surround / stereo).
5. **Controller & Input:**
   - XInput plug-and-play dengan deteksi otomatis stik Xbox.
   - Mapping keyboard default untuk kontrol darurat tanpa gamepad.

### 3.2 Core GPU (`core/gpu/`)
1. **Liverpool GNM to Vulkan 1.3:**
   - PM4 packet processor yang memecah command buffer menjadi thread perekaman Vulkan paralel (chunk size 64 KiB).
2. **Shader JIT:**
   - Recompiler ISA AMD GCN PS4 ke SPIR-V binary code standar.
3. **Presenter & Frame Pacing:**
   - Default present mode: `VK_PRESENT_MODE_MAILBOX_KHR` (bebas deadlock DWM).
   - Precision timer 1ms (`timeSetEvent` / multimedia clock) di `driver.cpp` untuk mengunci interval flip tepat 16.666 ms (60 FPS) atau 33.333 ms (30 FPS).
4. **Upscaling:**
   - AMD FidelityFX Super Resolution (FSR) 1.0 & 3.1 terintegrasi.

---

## 4. Pipeline REA (Reverse Engineer Anything)

Setiap game baru yang di-porting ke **anyPS4** wajib melalui 5 fase protokol REA:
1. **Triage:** Validasi format binary (`ELF` vs `SELF`), ekstraksi SFO metadata (`param.sfo`), dan pemetaan dependency library.
2. **Analysis:** Penelusuran fungsi frame rate (`sceVideoOutSetFlipRate`), deteksi engine physics (Havok, PhysX, Bullet), dan pencarian konstanta delta-time (`0.033333f` / `0.016667f`).
3. **Patching:** Pembuatan patch biner aman (*signature-checked memory patching*) di dalam folder target.
4. **Wrapping:** Penghubungan entry point guest dengan runtime `anyPS4` dan resolver symbol HLE.
5. **Validation:** Pengujian stabilitas gameplay minimal 1 sesi match/stage penuh dengan FPS stabil dan audio sinkron.

---

## 5. Sistem Portable Packaging & Launcher

Paket distribusi yang dihasilkan oleh `tools/make_portable.ps1` harus memenuhi standar kualitas berikut:
1. **Zero External Dependency:** Paket dapat langsung dimainkan di Windows 10/11 x64 tanpa perlu menginstal MSYS2, Python, Visual C++ Redistributable terpisah, atau DirectX runtime tambahan.
2. **Auto-Bundled Runtime DLLs:** Menyertakan seluruh 99 library pendukung (`SDL3.dll`, `libc++.dll`, `libwinpthread-1.dll`, `avcodec*.dll`, `libxxhash.dll`, dll.).
3. **Interactive GUI Launcher:**
   - Tombol "PLAY" yang responsif dan tidak membekukan antarmuka Windows (*non-blocking asynchronous execution*).
   - Indikator status controller real-time (hijau saat terhubung, kuning saat keyboard mode).
   - Opsi resolusi layar (720p, 1080p, 1440p, 4K), toggle Fullscreen, dan mode FPS (30 FPS vs 60 FPS).
4. **Direct Fallback:** Menyediakan script batch `Play_Direct.bat` untuk eksekusi langsung via terminal bagi pengguna tingkat lanjut.

---

## 6. Kepatuhan Hukum & Clean-Room Implementation

1. Repositori **anyPS4** adalah proyek *clean-room reverse engineering*.
2. Dilarang keras melakukan commit atau menyertakan file binary komersial berhak cipta (`eboot.bin` asli, `param.sfo`, data game CPK/ARC, dan firmware modules).
3. File `.gitignore` wajib menjaga direktori kerja lokal (`workspace/`, `extracted_game/`, `JStars_PC_Portable/`) agar tidak pernah terunggah ke repositori Git publik.
