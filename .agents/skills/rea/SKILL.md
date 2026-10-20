---
name: rea
description: Reverse Engineer Anything (REA) Protocol for PS4 Native PC Porting & Binary Analysis
---

# REA Protocol: PS4 Native PC Porting & Binary Analysis

## 1. Binary Triaging
- Selalu periksa 4 byte pertama (magic header) dari target binary (`eboot.bin`, `libc.prx`, `libSceFios2.prx`):
  - `7F 45 4C 46` (`\x7fELF`): Standard ELF64 executable/shared object. Siap dianalisis atau dipetakan ke flat memory image.
  - `4F 15 3D 1D` (`\x1d\x3d\x15\x4f`): PS4 Signed ELF (SELF / FPKG SELF). Harus di-unself terlebih dahulu menjadi file `.ELF` murni yang valid menggunakan extractor / script unfself.

## 2. Static Analysis & Decompilation
- Ekstraksi segmen program (`PT_LOAD`, `.text`, `.rodata`, `.data`, `.bss`), tabel simbol dinamis (`.dynsym`), dan tabel relokasi (`.rela.plt`, `.rela.dyn`).
- Gunakan tooling yang tersedia:
  - Analisis struktur ELF & disassembler via script Python (`pyelftools`, `capstone`).
  - Binary tooling: `llvm-readobj`, `llvm-objdump`, `dumpbin`, atau Ghidra headless jika tersedia.
- Lacak fungsi crash melalui `Caller RIP` dan dekompilasi instruksi x86-64 di sekitar offset tersebut.

## 3. PS4 NID Resolution
- Sony Orbis OS menggunakan 11-karakter Base64-encoded SHA-1 hash (NID) untuk mengekspor/mengimpor fungsi dan variabel pustaka sistem.
- Terjemahkan NID yang diimpor oleh game ke nama fungsi Orbis OS asli menggunakan database resmi/komunitas `ps4libdoc` / `OpenOrbis` / `shadPS4` NID database (unduh otomatis database JSON/TXT jika belum ada di lokal).
- Setiap NID yang belum memiliki implementasi native di-stub secara aman dengan konvensi pemanggilan `SYSV_ABI` (`__attribute__((sysv_abi))`) agar register guest tidak rusak.

## 4. Pattern & XREF Hunting
- Pindai konstanta spesifik di `.rodata` atau imm di `.text`:
  - `0.016666668` (`3C 88 88 3C` float): Delta time 60 FPS.
  - `0.033333335` (`3D 08 88 3D` float): Delta time 30 FPS.
  - `1.7777778` (`3F E3 8E 39` float): Aspect ratio 16:9.
  - String signature seperti `.cpk`, CRIWARE, `criFs*`, `GnmDriver`, `libScePad`, dll.
- Lacak XREF (Cross References) dari konstanta/string tersebut ke fungsi di segmen `.text` untuk membuat patch modular yang presisi.

## 5. ABI Bridging & Memory Redirection
- Host Windows menggunakan MS ABI (`RCX, RDX, R8, R9, ...`), sedangkan Guest PS4 menggunakan System V AMD64 ABI (`RDI, RSI, RDX, RCX, R8, R9, ...`).
- Seluruh fungsi HLE runtime wajib menggunakan atribut `__attribute__((sysv_abi))` (`SYSV_ABI`).
- Semua path `/app0/` dialihkan secara transparan ke path lokal `./extracted_game/app0/`.
