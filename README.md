# J-Stars Victory VS+ PC

[![Platform](https://img.shields.io/badge/Platform-Windows%20x64-blue.svg)](https://microsoft.com/windows)
[![Renderer](https://img.shields.io/badge/Renderer-Vulkan%201.3%2B-red.svg)](https://vulkan.org)
[![Framerate](https://img.shields.io/badge/Framerate-30%20FPS%20Console%20%7C%20FSR3%20FrameGen-success.svg)](https://github.com/krixsan/J-Stars-Victory-VS-PC/releases)
[![Latency](https://img.shields.io/badge/Low%20Latency-NVIDIA%20Reflex%20%2B%20Anti--Lag%202-76b900.svg)](https://github.com/krixsan/J-Stars-Victory-VS-PC/releases)
[![Version](https://img.shields.io/badge/Release-v1.5.0%20Portable-orange.svg)](https://github.com/krixsan/J-Stars-Victory-VS-PC/releases/tag/v1.5.0)
[![License](https://img.shields.io/badge/License-MIT%20%2F%20GPLv2-green.svg)](https://github.com/krixsan/J-Stars-Victory-VS-PC)

> **[Download Portable Release (v1.5.0)](https://github.com/krixsan/J-Stars-Victory-VS-PC/releases/latest)** | **[Changelog](CHANGELOG.md)**  
> Extract `J-Stars-Victory-VS-PC-portable-windows.zip`, copy your decrypted PS4 game dump into `extracted_game/app0/`, and open `Launcher.exe`. You don't need Python, MSYS2, or external SDKs installed.

Standalone Windows x86-64 PC port and native loader for **J-Stars Victory VS+** (PS4 Title IDs `CUSA01593` US, `CUSA01887` EU, and `CUSA01661` JP).

Because the PlayStation 4 runs on an AMD Jaguar x86-64 processor, your PC executes the game's compiled machine code directly on host cores without CPU emulation or JIT overhead. System calls, threading primitives, and GPU command buffers are translated on the fly to Win32 APIs, WASAPI audio, SDL3/raw HID input, and Vulkan 1.3+.

---

## What's New in v1.5.0

- **30 FPS Console Timing + NVIDIA Reflex / AMD Anti-Lag 2:** Defaults to unmodified **30 FPS console timing (`1.0x` normal speed)** so menus, hitstop, battle timers, and baked 30 Hz character animations play at their intended pace. **NVIDIA Reflex + Boost** (`VK_NV_low_latency2`) and **AMD Anti-Lag 2** (`VK_AMD_anti_lag`) shave 20 to 40 ms of swapchain presentation latency off that 30 Hz clock, while **60 FPS Smooth (AMD FSR 3.1 FrameGen)** stays available in `Launcher.exe` for optical-flow frame interpolation.
- **16x Anisotropic Filtering, RCAS Sharpening & Crash-Proof Async Shaders:** Forces up to `16x` anisotropic filtering on 3D arena surfaces while excluding depth/shadow maps and clamping shadow cascade borders cleanly. Background shader worker threads compile new pipelines without pausing combat; if a GPU driver rejects an edge-case shader, that single draw is skipped instead of crashing the match.
- **Hor+ Ultrawide FOV (21:9 & 32:9):** Widens horizontal camera FOV proportionally at `2560x1080`, `3440x1440`, and `5120x1440` without clipping top/bottom framing or distorting UI shadows.
- **Save Manager (`Import`, `Backup Restore` & `Unlock All`):** Built straight into `Launcher.exe` for `SAVE-DATA.DAT` (`200,000` bytes). Checks the save checksum, warns if a retail PS4 save is still encrypted, writes timestamped backups to `user/save-backups/`, imports existing saves, and unlocks all 52 playable/boss characters, 13 support characters, and `999,999` J-Points in one click.
- **Loose-File Mod Loader (`user/mods/`):** Drop modded audio, textures, or data files under `user/mods/` mirroring `/app0/` paths (for example `user/mods/data/sound/...`) without modifying your clean PS4 dump.
- **Upgraded `Launcher.exe` (`Auto-Optimize`, `Safe Mode`, 7 Languages & Practice Trainer):** Reads dedicated GPU VRAM, system RAM, and monitor aspect ratio to pick graphics settings automatically. Includes a 720p windowed **Safe Mode**, pre-launch dump checks, custom player name, subtitle language, `Cross` vs `Circle` confirm button, master audio volume, an optional **Infinite Match Timer** trainer, and 7-language localization (`EN`, `ID`, `JA`, `ZH`, `ES`, `PT`, `RU`) shared with the `Insert` / `L3 + R3` in-game overlay.
- **Raw Sony HID + DualSense Haptics, `F12` Screenshots & Instant First-Boot Linker:** Pairs SDL3 and XInput with direct USB/Bluetooth DualSense and DualShock 4 polling (Bluetooth rumble, trigger resistance, per-player RGB LEDs, and sub-frame tap latching). Press `F12` in-game to save clean PNG screenshots to `user/screenshots/`; `jstars_prepare.exe` prepares the boot image in under 0.2 seconds on first launch.

---

## Framerate & Latency Modes

| Launcher Mode | Simulation Clock | Display Output | Latency Path |
| :--- | :--- | :--- | :--- |
| **30 FPS - Original Console Mode (Default)** | 30 Hz (`1.0x`) | 30 FPS | NVIDIA Reflex + Boost / AMD Anti-Lag 2 |
| **60 FPS Smooth (AMD FSR 3.1 FrameGen)** | 30 Hz (`1.0x`) | 60 FPS (Interpolated) | Optical-flow GPU interpolation + Low Latency |

---

## Quick Start

### System Requirements
- **OS:** Windows 10 (1809+) or Windows 11 (64-bit)
- **CPU:** x86-64 processor with AVX support (Intel 2nd Gen+ or AMD Ryzen)
- **GPU:** Vulkan 1.3+ graphics card (NVIDIA GTX 1060 / RTX series, AMD Radeon RX 580 / RX 6000+, or Intel Arc)
- **Memory:** 8 GB RAM minimum (16 GB recommended)

### 1. Supplying Your Decrypted PS4 Game Dump
No copyrighted PS4 binaries or game archives are included in this repository or portable archive. Copy decrypted files from your own copy of **J-Stars Victory VS+** (`CUSA01593`, `CUSA01887`, or `CUSA01661`):

1. **From a Jailbroken PS4 (GoldHEN):** Dump your installed game to an exFAT USB drive using **ItemzFlow** or **Game Dumper**, then copy the `app0` contents into `extracted_game/app0/`.
2. **From a Decrypted `.pkg` (FPKG) on PC:** Open your package in **PkgEditor (LibOrbisPkg)**, **PS4 PKG Tool**, or `orbis-pub-cmd`, and extract `Image0` into `extracted_game/app0/`.

Expected directory structure:
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
└── data/ (or .cpk archives)
```

> **Note:** `Launcher.exe` inspects `extracted_game/app0/` before booting and warns if `eboot.bin` is nested inside an extra subfolder, missing `sce_module/*.prx`, or still retail-encrypted (`unfself` required).

### 2. Playing, Modding & Managing Saves
1. Open `Launcher.exe` and click **Auto-Optimize** (or pick your resolution, `16x` AF, player name, subtitle language, and volume manually).
2. Click **PLAY J-STARS**. On first launch, `jstars_prepare.exe` prepares the boot image automatically before starting the game.
3. Open **Saves & Mods** in `Launcher.exe` to import a decrypted `SAVE-DATA.DAT`, restore a timestamped backup from `user/save-backups/`, drop loose-file mods into `user/mods/`, or browse `F12` captures in `user/screenshots/`.
4. Click **Unlock All** after creating an initial in-game save to unlock all 52 playable/boss characters, 13 support characters, and `999,999` J-Points.

---

## Controls

Up to 4 local controllers (DualSense, DualShock 4, Xbox, Switch Pro) and keyboard run simultaneously with hot-plug detection:

| In-Game Action | PlayStation Pad | Xbox Controller | Keyboard (Default) |
| :--- | :--- | :--- | :--- |
| **Normal Attack** | `Square` | `X` | `U` / `C` |
| **Heavy Attack** | `Triangle` | `Y` | `I` / `V` |
| **Jump / Confirm** | `Cross` | `A` | `J` / `Z` / `Space` |
| **Special Attack** | `Circle` | `B` | `K` / `X` / `Left Shift` |
| **Guard / Block** | `L1` | `LB` | `Q` / `1` |
| **Target Lock-On** | `R1` | `RB` | `E` / `3` |
| **Dash / Support** | `L2` / `R2` | `LT` / `RT` | `R` / `F` |
| **Victory Burst** | `L3` / `R3` | `LS` / `RS` | `B` / `N` |
| **Movement** | `Left Stick` / `D-Pad` | `Left Stick` / `D-Pad` | `W, A, S, D` |
| **Camera** | `Right Stick` | `Right Stick` | `Arrow Keys` |
| **Pause / Options** | `Options` | `Menu / Start` | `Enter` / `Esc` |
| **PNG Screenshot** | `-` | `-` | `F12` (`user/screenshots/`) |
| **In-Game Overlay** | `L3 + R3` | `LS + RS` | `Insert` |

---

## Portable Directories

All user data stays self-contained inside the portable folder without writing to `%APPDATA%` or the Windows Registry:

| Path | Purpose |
| :--- | :--- |
| `bbport.ini` | Live renderer, upscaler, anisotropy, controller port, and overlay language settings |
| `user/savedata/` | Active `SAVE-DATA.DAT` save directories |
| `user/save-backups/` | Automatic timestamped backups created before save imports, restores, or unlocks |
| `user/mods/` | Loose-file mod overrides mirroring `/app0/` paths |
| `user/screenshots/` | Clean `F12` PNG frame captures |
| `user/trophies/` | Persistent unlock log for all 50 in-game trophies |
| `user/logs/` & `user/crashes/` | Session logs and crash minidumps |

---

## Legal Disclaimer

Independent clean-room compatibility project. Not affiliated with, endorsed by, or sponsored by Bandai Namco Entertainment Inc., Spike Chunsoft Co., Ltd., Shueisha Inc., or Sony Interactive Entertainment Inc. No copyrighted PS4 binaries, firmware modules, decryption keys, or game assets are hosted or distributed here; supply files dumped from your own legally owned copy of the game.
