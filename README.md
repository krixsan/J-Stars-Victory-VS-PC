# J-Stars Victory VS+ PC

[![Platform](https://img.shields.io/badge/Platform-Windows%20x64-blue.svg)](https://microsoft.com/windows)
[![Renderer](https://img.shields.io/badge/Renderer-Vulkan%201.3-red.svg)](https://vulkan.org)
[![Framerate](https://img.shields.io/badge/Framerate-60%20FPS-success.svg)](https://github.com/Mank-Krisna/J-Stars-Victory-VS-PC/releases)
[![Version](https://img.shields.io/badge/Release-v1.0.0%20Portable-orange.svg)](https://github.com/Mank-Krisna/J-Stars-Victory-VS-PC/releases/tag/v1.0.0)
[![License](https://img.shields.io/badge/License-MIT%20%2F%20GPLv2-green.svg)](https://github.com/Mank-Krisna/J-Stars-Victory-VS-PC)

> **[Download Portable Release (v1.0.0)](https://github.com/Mank-Krisna/J-Stars-Victory-VS-PC/releases/latest)**  
> Grab `J-Stars-Victory-VS-PC-portable-windows.zip`, extract it anywhere, drop your game files into `extracted_game/app0/`, and open `Launcher.exe`. No build tools or compiler required.

A native translation wrapper and Windows x86-64 PC loader for **J-Stars Victory VS+** (PS4, Title IDs `CUSA01887` and `CUSA01593`).

This project runs PS4 machine code directly on your host CPU. Because the PS4 runs on an AMD Jaguar x86-64 processor, guest code executes without CPU virtualization or JIT recompilation penalties. Sony Orbis OS system calls and proprietary graphics APIs are intercepted at runtime and translated to native Windows APIs, SDL3, and Vulkan 1.3.

---

## Features

- **60 FPS Gameplay Patch:** Bypasses the original 30 FPS console frame limiter while adjusting game timer intervals so animations, gravity, and combat mechanics run at native speed rather than double speed.
- **Native Vulkan 1.3 Renderer:** Decodes Liverpool GNM packets and translates GCN shaders to SPIR-V in real time. Supports custom resolutions (1080p, 1440p, 4K, Ultrawide) and non-blocking mailbox swapchain presentation.
- **Independent 2-Player Local Versus:** True multi-controller separation. Controller slots are isolated into distinct handles (`Handle 0` and `Handle 1`), preventing inputs from merging into Player 1.
- **Zero-Latency Input Polling:** Direct hardware reads through SDL3 gamepad APIs with analog stick deadzone centering on frame one, bypassing background event queues to remove input delay.
- **Custom Game Launcher:** Borderless UI featuring official game artwork, resolution selector, display modes (Windowed / Fullscreen), master volume control, and live gamepad connection indicators.
- **Controller & Keyboard Support:** Works out of the box with Xbox, DualShock 4, DualSense, Switch Pro, generic USB controllers, and custom keyboard layouts.

---

## Quick Start (How to Play)

### System Requirements
- **OS:** Windows 10 or Windows 11 (64-bit)
- **CPU:** x86-64 processor with AVX/AVX2 support (Intel Haswell 4th Gen+ or AMD Ryzen)
- **GPU:** Vulkan 1.3 compatible graphics card (NVIDIA GTX 900 series+, AMD Radeon RX 400+, or Intel Arc)
- **Memory:** 8 GB RAM minimum (16 GB recommended)

### 1. Getting the Game Files (From PKG or PS4 Console)
This repository does not contain copyrighted game files or proprietary binaries. You need the decrypted files from your own copy of **J-Stars Victory VS+** (`CUSA01887` or `CUSA01593`). You can obtain them using either method below:

#### Method A: Direct Dump from a Jailbroken PS4 (Recommended)
1. Boot your PS4 with GoldHEN enabled.
2. Launch an app like **ItemzFlow** or the **Game Dumper** payload.
3. Plug an exFAT-formatted USB drive into the console and dump your installed game.
4. Once complete, copy the generated `app0` directory straight into `extracted_game/app0/` on your PC.

#### Method B: Extracting a `.pkg` File on PC
If you have a decrypted package file (FPKG or decrypted retail dump):
1. Download a PS4 package extraction tool such as **LibOrbisPkg** (GUI `PkgEditor`), **PS4 PKG Tool**, or `orbis-pub-cmd`.
2. Open the `.pkg` file inside the tool.
3. Extract the entire `Image0` or `app` filesystem.
4. Copy the extracted files into the `extracted_game/app0/` directory.

#### Verifying Your Folder Structure
Confirm that your `extracted_game/app0/` directory matches this layout:
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
└── data/ (or your .cpk archives)
```

> **Note on eboot.bin:** The binary must be a standard decrypted ELF executable. If you extract an encrypted retail package, the loader won't be able to run it without decrypting it (`unfself`) first.

### 2. Launching the Game
1. Open `Launcher.exe`.
2. Select your desired resolution and screen mode (Windowed or Fullscreen).
3. Check the gamepad indicator in the bottom status panel to confirm your controller is detected.
4. Click **PLAY J-STARS** to start.

---

## Controls

The game accepts input from both gamepads and keyboards simultaneously:

| In-Game Action | Xbox Controller | PlayStation Controller | Keyboard (Default) |
| :--- | :--- | :--- | :--- |
| **Normal Attack (Square)** | `X` | `Square` | `J` |
| **Heavy Attack (Triangle)** | `Y` | `Triangle` | `I` |
| **Jump (Cross)** | `A` | `Cross` | `K` |
| **Special Attack (Circle)** | `B` | `Circle` | `L` |
| **Guard / Block (L1)** | `LB` | `L1` | `U` |
| **Target Lock-On (R1)** | `RB` | `R1` | `O` |
| **Dash / Sprint (R2)** | `RT` | `R2` | `Left Shift` |
| **Victory Burst (R3)** | `R3 (Right Stick Click)` | `R3` | `Space` |
| **Movement** | `Left Stick` / `D-Pad` | `Left Stick` / `D-Pad` | `W, A, S, D` |
| **Camera** | `Right Stick` | `Right Stick` | `Arrow Keys` |
| **Pause / Menu** | `Menu / Start` | `Options` | `Enter / Esc` |

---

## Building from Source

If you want to build the translation binary yourself:

```bash
# 1. Open MSYS2 Clang64 environment
source ./msys2-env.sh

# 2. Configure CMake and compile with Ninja
cmake -B out/gpu -G Ninja -S .
ninja -C out/gpu sacredfire

# 3. Compile the C# Launcher
dotnet build -c Release tools/Launcher.cs
```

The compiled binary will be generated at `out/gpu/jstars_pc.exe`.

---

## Legal Disclaimer

This is an independent clean-room reverse engineering project for research and educational purposes.

- This project is not affiliated with, endorsed by, or sponsored by Bandai Namco Entertainment Inc., Spike Chunsoft Co., Ltd., Shueisha Inc., or Sony Interactive Entertainment Inc.
- No copyrighted game binaries, proprietary firmware, audio files, decryption keys, or original game assets are hosted in or distributed with this repository.
- All product names, logos, and Shonen Jump characters are trademarks or registered trademarks of their respective owners.
- Users must dump and provide their own legally purchased copy of the PlayStation 4 game to play.
