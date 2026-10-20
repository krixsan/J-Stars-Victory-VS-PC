# anyPS4 Next Target Profile: Sengoku Basara 4: Sumeragi

- **Title ID:** `CUSA02057` (Japan) / `CUSA01134` (Asia)
- **Engine:** Capcom MT Framework (PlayStation 4 64-bit Edition)
- **Target Status:** **Planned / In-Progress Analysis**
- **Native Frame Rate:** 60 FPS Native on PS4

---

## Roadmap Analisis & Reverse Engineering (REA Protocol)

1. **Fase 1: Triaging Binary & Ekstraksi ELF:**
   - Ekstraksi `eboot.bin`, `sce_module/*.prx`, dan `sce_sys/param.sfo` ke dalam `workspace/basara4/`.
   - Menggunakan `tools/rea_analyzer.py` untuk mengidentifikasi Dynamic Symbol Table, GOT entries, dan TLS initializers.

2. **Fase 2: Identifikasi Engine Subsystems (MT Framework):**
   - MT Framework menggunakan format archive proprietary `.arc` yang diakses via `libSceFios2` dan libc `open`/`read`.
   - Mapping syscall IO filesystem ke `core/runtime/runtime_file.c`.
   - Memeriksa pemanggilan rendering Vulkan GNM driver untuk vertex buffer layouts Capcom.

3. **Fase 3: Input & Gamepad Remapping:**
   - Memastikan mapping input 60 FPS cocok dengan kontroler PC (XInput/DirectInput/Keyboard).

4. **Fase 4: Testing & Packaging:**
   - Memverifikasi stability loop match dan audio playback BGM/SE via WASAPI.
