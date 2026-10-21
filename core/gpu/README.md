# anyPS Core GPU: Modular Graphics Architecture (Vulkan Backend)

`core/gpu/` mengimplementasikan arsitektur grafis terpadu (*Unified Graphics Architecture*) yang mampu menerjemahkan command buffer dan shader dari PlayStation 4 (**Liverpool GNM**) maupun PlayStation 5 (**Oberon AGC**) langsung ke backend native **Vulkan 1.3+**.

---

## Arsitektur Dual-Pipeline GPU

```
+------------------------------------+  +------------------------------------+
|        PS4 Guest Draw Calls        |  |        PS5 Guest Draw Calls        |
|  (libSceGnmDriver, PM4 Packets)    |  |    (libSceAgc, Command Streams)    |
+------------------------------------+  +------------------------------------+
                  |                                        |
                  v                                        v
+------------------------------------+  +------------------------------------+
|      GNM Translator (`gnm/`)       |  |       AGC Pipeline (`agc/`)        |
|  - GCN Instruction Decoder         |  |  - RDNA 2 Wave32/64 Mode           |
|  - PM4 Type-3 Packet Parsing       |  |  - Mesh / Task Shader Translation  |
|  - GCN to SPIR-V JIT Recompiler    |  |  - Hardware Ray Tracing BVH Bridge |
+------------------------------------+  +------------------------------------+
                  \                                        /
                   \                                      /
                    v                                    v
+----------------------------------------------------------------------------+
|                  Unified Vulkan 1.3+ Renderer (`vulkan/`)                  |
|                                                                            |
|  - Pipeline Layouts & SPIR-V Pipeline State Caching                        |
|  - Asynchronous Compute & Multi-threaded Command Buffer Recording          |
|  - Deadlock-Free Swapchain (`VK_PRESENT_MODE_MAILBOX_KHR`)                 |
|  - Sub-millisecond Precision Multimedia Frame Rate Limiter (60 FPS / VSync)|
|  - FidelityFX (FSR 1.0 & FSR 3.1) Spatial / Temporal Upscaling             |
+----------------------------------------------------------------------------+
                                      |
                                      v
+----------------------------------------------------------------------------+
|                             Host Vulkan Device                             |
|                   NVIDIA GeForce / AMD Radeon / Intel Arc                  |
+----------------------------------------------------------------------------+
```

---

## Modul Direktori

1. **`include/gpu_interface.h`:**
   - Kontrak antarmuka abstrak `anyps_shader_translator_t` dan `anyps_vk_renderer_t`.
   - Enumerasi stage shader standar hingga fitur modern PS5 (Mesh Shader, Ray Tracing).

2. **`gnm/` (PlayStation 4 GNM Subsystem):**
   - Menerjemahkan instruksi ISA AMD GCN (Graphics Core Next) ke byte-code SPIR-V standar.
   - Mengurai paket Liverpool Type-3 PM4 untuk rendering 2D/3D.

3. **`agc/` (PlayStation 5 AGC Subsystem):**
   - Menangani pipeline RDNA 2 modern: Primitive Shaders, Mesh Shaders, dan Ray Tracing acceleration structures.

4. **`vulkan/` (Unified Vulkan Core):**
   - Renderer terpadu lintas-platform dengan dynamic resolution scaling, presenter anti-deadlock, dan manajemen swapchain optimal.
