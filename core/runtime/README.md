# anyPS4 Core Runtime (HLE Operating System Subsystem)

`core/runtime/` mengimplementasikan High-Level Emulation (HLE) untuk antarmuka kernel dan sistem operasi PlayStation 4 (Orbis OS / FreeBSD derivatif) langsung di atas Windows x86-64.

---

## Arsitektur Subsystem

```
+-------------------------------------------------------------+
|                     Guest x86-64 Binary                     |
|           (eboot.bin, libc.prx, libSceFios2.prx)            |
+-------------------------------------------------------------+
                               |
                   [System V AMD64 ABI Bridge]
                               |
+-------------------------------------------------------------+
|                      anyPS4 Core Runtime                    |
|                                                             |
|  +--------------------+  +--------------------+             |
|  |   Virtual Memory   |  |   Thread & Sync    |             |
|  | - MapViewOfFile3   |  | - pthreads Win32   |             |
|  | - Direct Pool Map  |  | - Event Flags      |             |
|  | - Flexible Memory  |  | - TEB TLS Slot     |             |
|  +--------------------+  +--------------------+             |
|                                                             |
|  +--------------------+  +--------------------+             |
|  |   Virtual VFS      |  |   Audio & Input    |             |
|  | - /app0 Game Mount |  | - WASAPI 48kHz     |             |
|  | - /savedata VFS    |  | - XInput Gamepad   |             |
|  | - CRI File Access  |  | - SDL3 Key Remap   |             |
|  +--------------------+  +--------------------+             |
+-------------------------------------------------------------+
                               |
                     [Host Operating System]
           Windows 10/11 x64 (Win32 API / UCRT / NTDLL)
```

---

## Modul-Modul Utama

1. **Virtual Memory (`runtime_memory.c`):**
   - Mereservasi ruang alamat guest PS4 (`0x1000000000` s.d. `0xfc00000000`) sebelum DLL Windows dimuat.
   - Menggunakan Win32 `CreateFileMapping2` dan `MapViewOfFile3` dengan placeholder placeholders (`MEM_REPLACE_PLACEHOLDER`) untuk pemetaan direct memory (5056 MiB default) dan flexible memory (1024 MiB span).
   - Dilengkapi *automatic pagefile growth retry* dan *adaptive memory pool fallback* (4864 MiB) agar aman dari batas *commit charge* Windows (Error 1450).

2. **Threading & Synchronization (`runtime_thread.c`):**
   - Mengonversi pemanggilan pthread Orbis OS ke native Win32 threads.
   - Manajemen *Thread Control Block* (TCB) menggunakan slot TLS di dalam TEB Windows (`__readgsqword(0x58)`).
   - Sinkronisasi instan via `Kernel::EventFlag`, `Semaphore`, dan `Equeue` (kqueue emulation).

3. **Virtual File System (`runtime_file.c`):**
   - Mount layer untuk `/app0` (game assets) dan `/savedata` (user storage).
   - Path normalizer yang menangani perbedaan separator direktori POSIX `/` dan Windows `\`.
   - Thread-safe caching untuk pengaksesan file CRI Middleware CPK.

4. **Audio Engine (`runtime_audio.c`):**
   - Backend WASAPI (Windows Audio Session API) dengan latensi rendah.
   - Mendukung multi-channel 7.1 / 5.1 / stereo float 32-bit pada 48.000 Hz.

5. **Input / Gamepad (`runtime_pad.c`):**
   - Deteksi otomatis Controller Xbox (XInput Slot 1–4) dan DualShock/DualSense via SDL3.
   - Keyboard mapping responsif dengan konfigurasi default teruji.
