# anyPS Core OS: PlayStation 4 (Orbis OS HLE Subsystem)

Direktori `core/os/ps4/` mengimplementasikan High-Level Emulation (HLE) untuk kernel dan userland subsystem Sony PlayStation 4 (Orbis OS / FreeBSD 9.0 kernel derivatif) pada sistem operasi host Windows x86-64.

---

## Modul-Modul Utama Orbis OS

1. **Virtual Memory Management (`runtime_memory.c`):**
   - Mereservasi ruang alamat guest PS4 (`0x1000000000` s.d. `0xfc00000000`) sebelum DLL Windows dialokasikan.
   - Menggunakan Win32 `CreateFileMapping2` dan `MapViewOfFile3` dengan placeholder (`MEM_REPLACE_PLACEHOLDER`) untuk pemetaan direct memory (5056 MiB default) dan flexible memory (1024 MiB span).
   - Dilengkapi *automatic pagefile growth retry loop* dan *adaptive memory pool fallback* (4864 MiB) untuk mitigasi commit error (Error 1450).

2. **Threading & Synchronization (`runtime_thread.c`, `runtime_kernel.c`):**
   - Mengonversi thread pthread Orbis OS ke native Win32 threads.
   - Manajemen Thread Control Block (TCB) menggunakan slot TLS di dalam Windows TEB (`__readgsqword(0x58)`).
   - Sinkronisasi instan melalui `Kernel::EventFlag`, `Semaphore`, `Mutex`, `RwLock`, dan `Equeue` (kqueue).

3. **Virtual File System (`runtime_file.c`, `runtime_savedata.c`):**
   - Mount layer untuk path sandboxing:
     - `/app0/` -> direktori game assets lokal.
     - `/savedata/` -> direktori user save data terisolasi.
     - `/temp0/` -> temporary cache scratch directory.
   - Thread-safe path normalizer menangani perbedaan separator POSIX `/` dan Windows `\`.

4. **Audio Engine (`runtime_audio.c`, `runtime_ajm.c`):**
   - Backend WASAPI (Windows Audio Session API) dengan latensi ultra-rendah.
   - Decoding audio ATRAC9 hardware menggunakan LibAtrac9 bridge.
   - Dukungan output stereo, 5.1 surround, dan 7.1 float 32-bit pada 48.000 Hz.

5. **Input & Pad Emulation (`runtime_pad.c`):**
   - Emulasi DualShock 4 Controller melalui XInput dan SDL3.
   - Mapping analog stick, tombol digital, touchpad click, dan rumble feedback.
