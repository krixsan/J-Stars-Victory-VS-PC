# anyPS Core OS: PlayStation 5 (Prospero OS HLE Subsystem)

Direktori `core/os/ps5/` menyediakan kerangka kerja High-Level Emulation (HLE) untuk sistem operasi Sony PlayStation 5 (Prospero OS / FreeBSD 12+ kernel derivatif) pada arsitektur target AMD Zen 2 x86-64.

---

## Karakteristik Arsitektur Prospero OS

1. **CPU & Instruksi Hardware:**
   - 8-Core / 16-Thread kustom AMD Zen 2 (hingga 3.5 GHz).
   - Dukungan penuh instruksi x86-64 kontemporer: AVX, AVX2, FMA3, BMI1, BMI2, SHA, RDSEED, RDRAND, dan CLFLUSHOPT (tanpa perlu ISA rewriting seperti AMD Jaguar pada PS4).

2. **Unified Memory Architecture (16 GB GDDR6):**
   - Ruang alamat guest yang diperluas hingga rentang 48-bit address space.
   - Alokasi memori unified GDDR6: ~13.5 GB untuk game payload dan ~2.5 GB direservasi untuk OS Prospero.
   - Peningkatan granularitas proteksi memori via paging 4 KiB dan 2 MiB / 1 GiB large pages.

3. **Subsystem Audio Tempest 3D:**
   - Unit DSP audio berbasis arsitektur AMD RDNA GPU compute unit.
   - Emulasi channel spatial 3D audio, HRTF (*Head-Related Transfer Function*), dan decoding streaming multichannel via host WASAPI / Spatial Sound.

4. **Kontroler DualSense:**
   - Emulasi fitur generasi baru: *Adaptive Triggers* (variabel resistansi R2/L2) dan *Haptic Feedback* via protokol DirectInput/SDL3 USB HID.

5. **Modul Dinamis Prospero (Prospero PRX / SPRX):**
   - Format ELF64 dengan ekstensi khusus Prospero (`PT_SCE_PROGLIB`, Prospero SDK 1.00 - 8.xx).
   - Modul kernel standar: `libkernel.prx`, `libSceAgc.prx`, `libScePad.prx`, `libSceAudioOut.prx`, `libSceSaveData.prx`.
