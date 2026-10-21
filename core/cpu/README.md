# anyPS Core CPU: Universal Loader & Architecture Dispatcher

Direktori `core/cpu/` menyediakan loader universal untuk mem-parsing, memvalidasi, dan mendispatch biner guest (ELF, SELF, PRX) secara otomatis mendeteksi platform target: **PlayStation 4 (Orbis OS)** vs **PlayStation 5 (Prospero OS)**.

---

## Logika Deteksi Platform Universal

```
+-------------------------------------------------------------+
|                 Guest Binary (eboot.bin / PRX)              |
+-------------------------------------------------------------+
                               |
                               v
                     [Signature Detection]
          /                                          \
    [SELF 0x1D3D154F]                           [ELF 0x7F454C46]
          |                                           |
  (Read Target ID)                            (Read Phdr / Shdr)
  - 0x01 -> PS4                               - PT_SCE_PROC_PARAM
  - 0x12 -> PS5                               - SDK Version Analysis
          \                                           /
           +-----------------------------------------+
                               |
                               v
                      [Platform Identified]
             /                                   \
   [anyPS PS4 Profile]                    [anyPS PS5 Profile]
   - OS: Orbis OS                         - OS: Prospero OS
   - CPU: AMD Jaguar (ISA Rewrite)        - CPU: AMD Zen 2 (Native AVX2)
   - GPU: Liverpool (GNM -> Vulkan)       - GPU: Oberon (AGC -> Vulkan)
```

---

## Komponen Utama

1. **`elf_loader.h` & `elf_loader.c`:**
   - Reader ELF64 spesifikasi System V AMD64 + ekstensi Sony SCE.
   - Detektor SDK Version otomatis (misal: `05.050.001` vs `02.000.001`).
   - Ekstraktor metadata Game ID (`TITLE_ID`), Program Headers (`PT_LOAD`, `PT_SCE_PROGLIB`), dan relokasi runtime.
