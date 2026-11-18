# Changelog

All notable changes to **J-Stars Victory VS+ PC** are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v1.5.0] - 2026-11-18

### Added
- **Official RecompLauncher Integration:** Added `recomplauncher.json` supporting Level 1 (one-click setup and direct play), Level 2 (launcher settings mapping for display resolution, ultrawide aspect ratios, frame pacing, upscaling/DLSS, anisotropic filtering, async shaders, and 7 menu languages), and Level 3 (automated headless asset/module preparation via `jstars_prepare.exe` and save/log folder actions).
- **NVIDIA Reflex (`VK_NV_low_latency2`) & AMD Anti-Lag 2 (`VK_AMD_anti_lag`):** Hardware swapchain pacing cuts 20 to 40 ms of input-to-photon latency in default 30 FPS console mode without altering the game's 30 Hz simulation clock.
- **Configurable 16x Anisotropic Filtering & Shadow Border Clamp Fix:** Added live `Off / 2x / 4x / 8x / 16x` anisotropic filtering (default `16x`) in `Launcher.exe` and the in-game `Picture` tab, automatically excluding depth/shadow targets and 2D point-sampled UI while clamping shadow cascade borders cleanly.
- **Background Async Shader Compilation & Crash-Proof Pipeline Skip:** Enabled background graphics pipeline worker threads by default and replaced fatal shader compilation aborts with safe per-draw skipping.
- **AMD FSR 3.1 Optical-Flow Frame Generation:** Optional **60 FPS Smooth** mode in `Launcher.exe` that keeps game simulation at 30 Hz while interpolating intermediate frames on Vulkan.
- **Hor+ Ultrawide 21:9 & 32:9 Support:** Added proportional horizontal FOV scaling paired with dynamic swapchain aspect handling for `2560x1080`, `3440x1440`, and `5120x1440`.
- **Save Manager (`Import`, `Backup Restore` & `Unlock All`):** Added `SAVE-DATA.DAT` (`200,000` bytes) checksum validation, encrypted retail save detection, one-click import, backup restoration from `user/save-backups/`, and an **Unlock All** tool (52 playable/boss characters, 13 support characters, and `999,999` J-Points) inside `Launcher.exe`.
- **Loose-File VFS Mod Loader (`user/mods/`):** Redirects `/app0/*` file opens to matching loose files under `user/mods/*` without modifying the original game dump.
- **7-Language UI Localization (`en`, `id`, `ja`, `zh`, `es`, `pt`, `ru`):** Added localized dictionaries and Windows CJK font merging across both `Launcher.exe` and the `Insert` / `L3 + R3` in-game overlay.
- **Hardware `Auto-Optimize`, `Safe Mode` & Pre-Launch Dump Validator:** `Launcher.exe` now reads GPU VRAM, system RAM, and monitor dimensions to apply tailored presets, offers a one-click 720p windowed Safe Mode, and checks `extracted_game/app0/` for nested folders, missing `sce_module/*.prx`, or encrypted SELFs before launch.
- **Player Name, Game Language, Confirm Button, Master Volume & Practice Trainer:** Added `Launcher.exe` controls for profile name, subtitle language, `Cross` vs `Circle` confirm button, WASAPI master volume, and an optional **Infinite Match Timer** toggle.
- **Raw Win32 HID DualSense / DualShock 4 Reader + Haptics:** Added direct USB & Bluetooth Sony controller polling with Bluetooth rumble, DualSense trigger resistance, per-player RGB lightbar colors, and sub-frame button tap latching.
- **`F12` PNG Screenshots, 50 Offline Trophies, Discord RPC & Crash Minidumps:** Added `F12` screenshot capture to `user/screenshots/` with on-screen notifications, clean window-close shutdown handling, 50 built-in trophies, standalone `jstars_prepare.exe` first-boot linker, Discord Rich Presence, cutscene stall recovery, and automatic minidumps (`user/crashes/`).

### Changed
- **Authentic 30 FPS Console Timing by Default:** Configured `Launcher.exe`, `bbport.ini`, and `Play_Direct.bat` to run unmodified 30 FPS console timing (`1.0x` normal speed) by default while preserving controller port bindings across launches.

### Fixed
- **Fixed 2x Speed-Up Issue from `v1.0.0`:** Removed forced flip-rate overrides in default 30 FPS mode that previously caused double-speed menus and character state ticks.
- **Fixed Unconditional Anisotropy on Shadow & UI Samplers:** Stopped forcing `16x` anisotropy onto depth-compare shadow maps and 2D point-sampled UI textures.
- **Fixed Overlay Default Language & Title:** Changed overlay default language to `English` (with system locale auto-detection) and updated the in-game overlay header to `J-Stars Victory VS+`.
- **Fixed Guest Thread Synchronization Heap Corruption:** Added trailing allocation padding to guest synchronization objects so runtime writes no longer corrupt host heap metadata during stage transitions.
- **Fixed Frame Pacing & Audio Clipping:** Switched frame pacing to high-resolution waitable timers and registered WASAPI audio threads with Windows MMCSS `"Pro Audio"` plus soft-knee peak limiting.

---

## [v1.0.0] - 2026-10-21

### Added
- Initial standalone Windows x86-64 native wrapper release for **J-Stars Victory VS+** (`CUSA01887` / `CUSA01593`).
- Direct x86-64 guest execution with HLE system runtime and Vulkan 1.3 renderer.
- 2-player local versus controller handle separation (`Handle 0` and `Handle 1`) via SDL3.
- Custom borderless WinForms `Launcher.exe` with resolution selector and gamepad indicator.
