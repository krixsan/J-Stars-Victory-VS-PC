# Product Requirements Document (PRD): J-Stars Victory VS+ Native PC Port (x86-64 Wrapper)

## 1. Project Overview
- **Project Name:** J-Stars Victory VS+ PC (`jstars-pc`)
- **Target Game:** J-Stars Victory VS+ (PS4 - Title ID: `CUSA01593` / `CUSA01661`)
- **Base Architecture:** `bbport` / `CTR-NitroFueled-PC` (Native x86-64 execution + Win32/SDL3 HLE Runtime + `shadPS4` Vulkan Video Core)
- **Target Platform:** Windows 10/11 (64-bit), Clang/LLVM Compiler (`sysv_abi` calling convention support)

## 2. Core Objectives
1. **Sanitize Base Repository:** Strip all hardcoded memory offsets, instruction hooks, and binary hash checks specific to *CTR: Nitro-Fueled* (`CUSA13795`) or *Bloodborne* (`CUSA03173`).
2. **Offline ELF-to-Image Pipeline:** Adapt the image builder tool to parse and relocate J-Stars Victory VS+'s decrypted `eboot.bin`, `sce_module/libc.prx`, and `sce_module/libSceFios2.prx` into a valid flat memory image.
3. **HLE Runtime & NID Resolution:** Intercept PS4 Orbis OS system calls (`sysv_abi`) made by J-Stars and translate them to native Windows API / SDL3 calls. Log any unimplemented NIDs (hashed symbol names) clearly instead of silently crashing.
4. **Graphics & Audio Initialization:** Route `libSceGnmDriver` and `libSceVideoOut` calls to the embedded `shadPS4` Vulkan backend, and route `libSceAudioOut` / CRIWARE audio calls to SDL3 Audio.

## 3. Technical Architecture & Constraints
- **ABI Bridging:** PS4 guest code executes natively on the host CPU using the System V AMD64 ABI (`__attribute__((sysv_abi))`), while Windows host libraries use the Microsoft x64 ABI (`__attribute__((ms_abi))`). Every HLE runtime function in `src/runtime_*.c` MUST explicitly declare `SYSV_ABI`.
- **Filesystem Redirection:** All guest paths starting with `/app0/` must be transparently redirected to the user-specified local game dump directory on Windows.
- **No Blind Memory Patching:** Do NOT write hardcoded hex offsets into guest memory during Phase 1. All game-specific patches must be isolated in a modular `src/jstars_patches.c` file and disabled by default until the game reaches the Title Screen.

## 4. Phased Milestones
- **Milestone 1 (Clean Loader):** Successfully generate the flat memory image for J-Stars `eboot.bin` and load it into host memory without segmentation faults during static initialization (`_init`).
- **Milestone 2 (Symbol & NID Stubbing):** Identify all imported Sony PRX modules and NIDs required by J-Stars. Implement stubs/HLE functions for missing symbols until the main game loop initializes.
- **Milestone 3 (Boot to Title Screen):** Initialize the Vulkan swapchain via `shadPS4` video core, mount CRIWARE `.cpk` archives via `libSceFios2` / `KernelOpen`, and render the 2D/3D Title Screen with SDL3 controller input.
- **Milestone 4 (Enhancements):** Analyze guest memory to create optional hooks for 60+ FPS unlock, resolution scaling, and aspect ratio support.
