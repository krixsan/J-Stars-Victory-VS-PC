# anyPS5: Modular PlayStation 5 to PC Translation Wrapper

**anyPS5** is a high-performance native translation wrapper framework for running PlayStation 5 (x86-64 Prospero OS / AMD Zen 2) titles on Windows PCs without full-system emulation overhead.

## Architecture Highlights
- **CPU:** Native AMD Zen 2 x86-64 execution with direct AVX2 / FMA acceleration.
- **Kernel:** Prospero OS HLE implementation based on FreeBSD 12+ kernel derivatives.
- **GPU Interface:** AGC (Accelerated Graphics Core) command translator to Vulkan 1.3+ backend with hardware ray-tracing abstraction.
- **Target Profiles:** Modular game profiling in \	argets/ps5_<game_id>\.

## Prerequisites
- Windows 10/11 x64
- MSYS2 Clang64 toolchain (LLVM Clang 18+, Ninja, CMake 3.25+)
- Vulkan 1.3 capable GPU (NVIDIA RTX / AMD RDNA2 / Intel Arc)
