# J-Stars Victory VS+ PC

[![Platform](https://img.shields.io/badge/Platform-Windows%20x64-blue.svg)](https://microsoft.com/windows)
[![Graphics](https://img.shields.io/badge/Renderer-Vulkan%201.3+-red.svg)](https://vulkan.org)
[![Framerate](https://img.shields.io/badge/Framerate-60%20FPS%20Native-success.svg)](https://github.com/Mank-Krisna/J-Stars-Victory-VS-PC)
[![Release](https://img.shields.io/badge/Version-v1.02%20Standalone-orange.svg)](https://github.com/Mank-Krisna/J-Stars-Victory-VS-PC/releases)
[![License](https://img.shields.io/badge/License-MIT%20%2F%20GPLv2-green.svg)](LICENSE)

> ### 🚀 **[Download Latest Portable Release (v1.0.0)](https://github.com/Mank-Krisna/J-Stars-Victory-VS-PC/releases/latest)**
> Unduh file zip portable (`J-Stars-Victory-VS-PC-portable-windows.zip`), ekstrak, lalu taruh dump game Anda ke `extracted_game/app0/` untuk langsung bermain tanpa perlu kompilasi!

---

Native translation wrapper dan PC loader mandiri (*standalone PC port*) khusus untuk **J-Stars Victory VS+** (PlayStation 4 - Title ID: `CUSA01887` / `CUSA01593`) pada Windows x86-64. 

Proyek ini mengeksekusi instruksi biner x86-64 PS4 langsung di CPU host tanpa overhead virtualisasi atau emulasi CPU penuh, dipadukan dengan subsystem High-Level Emulation (HLE) untuk kernel Orbis OS dan backend grafis native **Vulkan 1.3+**.

---

## Fitur Utama

- ⚡ **60 FPS Unlocked Gameplay:** Patch native loop render game yang membuka framerate dari batasan 30 FPS konsol ke 60 FPS mulus dengan pacing animasi yang sinkron.
- 🌋 **Native Vulkan 1.3+ Renderer:** Penerjemahan GNM draw calls dan GCN shaders langsung ke SPIR-V/Vulkan, mendukung resolusi native (1080p, 1440p, 4K Ultrawide), HDR, dan triple buffering bebas tearing.
- 🎮 **Multi-Controller Support (2-Player Local VS):** Pemisahan hardware controller secara fisik (Handle 0 & Handle 1) untuk mode pertarungan 2 Player Local Versus tanpa bentrok input.
- ⚡ **Zero-Lag Input Pipeline:** Pembacaan status controller instan (*direct polling*) dari hardware via SDL3 Gamepad API dengan penyaringan noise analog stick.
- 🖥️ **Modern Game Launcher UI:** Antarmuka launcher modern tanpa border (borderless window) dengan latar belakang official splash art, seleksi resolusi, mode layar (Windowed/Borderless Fullscreen), audio volume control, dan indikator status stik real-time.
- ⌨️ **Full Keyboard & Gamepad Compatibility:** Dukungan bawaan untuk berbagai controller (Xbox / XInput, DualShock 4, DualSense, Nintendo Switch Pro Controller, gamepad generik) serta kontrol keyboard penuh.

---

## Panduan Cepat (Quick Start / How to Play)

### 1. Prasyarat Sistem
- **Sistem Operasi:** Windows 10 atau Windows 11 (64-bit)
- **Prosesor:** CPU x86-64 dengan dukungan AVX/AVX2 (Intel Core i5 generasi ke-4+ / AMD Ryzen 3+)
- **Kartu Grafis:** GPU yang mendukung Vulkan 1.3+ (NVIDIA GeForce GTX 900+, AMD Radeon RX 400+, Intel Arc)
- **RAM:** Minimal 8 GB RAM (Direkomendasikan 16 GB)

### 2. Pemasangan File Game (Legitimate Game Dump)
Repositori ini **TIDAK** memuat file aset atau biner terenkripsi game. Anda harus mengekstrak salinan resmi game PS4 milik Anda:

1. Ekstrak dump game PS4 (*decrypted eboot.bin, PRX modules, and game archives*) ke dalam folder:
   ```text
   extracted_game/app0/
   ```
2. Pastikan struktur folder menyerupai susunan berikut:
   ```text
   extracted_game/app0/
   ├── eboot.bin
   ├── sce_module/
   │   ├── libc.prx
   │   └── libSceFios2.prx
   ├── sce_sys/
   │   ├── icon0.png
   │   ├── pic0.png
   │   └── param.sfo
   └── data/ (atau file arsip .cpk game)
   ```

### 3. Memulai Permainan
1. Jalankan **`Launcher.exe`**.
2. Pilih resolusi layar yang diinginkan (misal: 1920x1080 atau 2560x1440) dan pilih mode **Fullscreen** atau **Windowed**.
3. Pastikan controller Anda terdeteksi pada panel status (*Gamepad Connected*).
4. Klik tombol besar **"PLAY J-STARS"** untuk memulai pertarungan!

---

## Tabel Kontrol (Controls Table)

Game mendukung kendali stik analog ganda maupun keyboard:

| Aksi / Fungsi Game | Gamepad (Xbox Layout) | Gamepad (PlayStation Layout) | Keyboard (Default) |
| :--- | :--- | :--- | :--- |
| **Normal Attack (Kotak)** | `X` | `Square` | `J` |
| **Heavy Attack (Segitiga)** | `Y` | `Triangle` | `I` |
| **Jump (Silang)** | `A` | `Cross` | `K` |
| **Special Attack (Lingkaran)** | `B` | `Circle` | `L` |
| **Guard / Block (L1)** | `LB` | `L1` | `U` |
| **Target Lock-On (R1)** | `RB` | `R1` | `O` |
| **Dash / Sprint (R2)** | `RT` | `R2` | `Left Shift` |
| **Victory Burst (R3)** | `R3 (Right Stick Click)` | `R3` | `Space` |
| **Movement** | `Left Stick` / `D-Pad` | `Left Stick` / `D-Pad` | `W, A, S, D` |
| **Camera Control** | `Right Stick` | `Right Stick` | `Panah Atas, Bawah, Kiri, Kanan` |
| **Pause Menu (Options)** | `Menu / Start` | `Options` | `Enter / Esc` |

---

## Kompilasi dari Source (Build from Source)

Jika Anda ingin mengompilasi biner wrapper secara mandiri:

```bash
# 1. Buka MSYS2 Clang64 Environment
source ./msys2-env.sh

# 2. Konfigurasi CMake & Build dengan Ninja
cmake -B out/gpu -G Ninja -S .
ninja -C out/gpu sacredfire

# 3. Kompilasi Launcher C#
dotnet build -c Release tools/Launcher.cs
```

File executable hasil build akan diletakkan di `out/gpu/jstars_pc.exe`.

---

## Legal Disclaimer

Proyek **J-Stars Victory VS+ PC** adalah proyek riset rekayasa terbalik independen (*independent clean-room reverse engineering project*).

- Proyek ini **TIDAK berafiliasi, didukung, atau disponsori** oleh Bandai Namco Entertainment Inc., Spike Chunsoft Co., Ltd., Shueisha Inc., atau Sony Interactive Entertainment Inc.
- Repositori ini **TIDAK memuat, mendistribusikan, atau menyertakan file binary berhak cipta, firmware konsol, kunci enkripsi, audio, maupun materi aset game apa pun**.
- Seluruh merek dagang, judul game, dan karakter Shonen Jump adalah hak milik sah dari pemilik hak cipta masing-masing.
- Pengguna diwajibkan memiliki dan menggunakan salinan game resmi (*legally purchased copy*) dari PlayStation 4 untuk dapat memainkan port ini di PC.
