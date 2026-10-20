# anyPS4 Game Target Template

Template ini adalah titik awal standar (boilerplate) untuk mem-porting game PS4 baru menjadi aplikasi Native PC menggunakan kerangka kerja **anyPS4** dan protokol **REA (Reverse Engineer Anything)**.

---

## Langkah-Langkah Porting Target Baru

### Tahap 1: Persiapan & Triaging Binary (REA Protocol)
1. Letakkan file game mentah (`eboot.bin`, modul `sce_module/*.prx`, dan `sce_sys/param.sfo`) ke dalam folder `workspace/`.
2. Validasi magic bytes:
   - `7F 45 4C 46` -> Decrypted ELF (Siap diproses).
   - `4F 15 3D 1D` -> Encrypted SELF (Harus didekripsi terlebih dahulu dengan unself/fself dumper).
3. Salin folder `targets/template/` menjadi `targets/<nama_game>/`.

### Tahap 2: Konfigurasi Target (`target.ini`)
Isi file `target.ini` dengan informasi game:
- `TITLE_ID`: Misalnya `CUSAXXXXX`.
- `GAME_TITLE`: Nama resmi permainan.
- `DMEM_MB`: Kebutuhan memori direct PS4 (biasanya 4096 s.d. 5056 MiB).
- `TARGET_FPS`: Target frame rate (30 atau 60).
- `ENGINE_TYPE`: Unreal / Unity / MT Framework / Custom.

### Tahap 3: Pelacakan Delta Time & Frame Limiter (`patches.c`)
1. Cari XREF pemanggilan `sceVideoOutSetFlipRate` di dalam `eboot.bin` menggunakan `rea_analyzer.py` atau Ghidra/IDA.
2. Jika game terkunci di 30 FPS dan ingin di-unlock ke 60 FPS:
   - Periksa apakah game menggunakan *fixed timestep* atau *dynamic delta time*.
   - Jika pergerakan karakter menjadi 2x lipat lebih cepat (fast-forward), cari konstanta float `1/30.0f` (`0x3d088889` / `0.03333334f`) atau *animation tick counter* dan sesuaikan menjadi `1/60.0f` (`0x3c888889` / 0.5x scaling).
3. Tulis signature byte & hook di `patches.c`.

### Tahap 4: Build & Packaging
1. Jalankan build script target:
   ```bash
   ./build_target.sh
   ```
2. Jalankan `tools/make_portable.ps1` untuk mem-bundle seluruh DLL runtime dan aset game ke paket standalone portable.
