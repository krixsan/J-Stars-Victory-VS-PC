# anyPS4 Core GPU (Vulkan Graphics Backend)

`core/gpu/` mengimplementasikan emulasi arsitektur grafis PlayStation 4 ("Liverpool" AMD GCN GPU) yang diterjemahkan langsung ke Vulkan 1.3+ pada PC host berbasis arsitektur **shadPS4 Video Core**.

---

## Alur Pipeline Grafis

```
+-------------------------------------------------------------+
|                     Guest GNM Draw Calls                    |
|           (libSceGnmDriver, PM4 Command Buffers)            |
+-------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                    anyPS4 Liverpool Core                    |
|                                                             |
|  [PM4 Packet Decoder] ---> [Shader Recompiler (GCN->SPIR-V)]|
|          |                                                  |
|          v                                                  |
|  [Vulkan Command Recorders] (Multi-threaded chunks 64 KiB)   |
|          |                                                  |
|          v                                                  |
|  [Vulkan Render Passes & Compute Pipelines]                 |
|          |                                                  |
|          v                                                  |
|  [FSR 1.0 / 3.1 Post-Processing & Temporal Upscaling]       |
|          |                                                  |
|          v                                                  |
|  [Deadlock-Free Presenter]                                  |
|  - VK_PRESENT_MODE_MAILBOX_KHR                              |
|  - Precise 1ms High-Resolution Multimedia Frame Limiter     |
+-------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                       Host Vulkan 1.3                       |
|           NVIDIA / AMD / Intel GPU Native Driver            |
+-------------------------------------------------------------+
```

---

## Karakteristik Utama Backend GPU

1. **PM4 Packet Decoding:**
   - Menerjemahkan paket Liverpool Type-3 (Draw index, Set context registers, Surface sync, EOS fences).
   - Melindungi command buffer yang disubmit dari *clobbering dword race condition* (SacredFire issue #2 mitigasi).

2. **Shader Translation (GCN ke SPIR-V):**
   - Mengompilasi instruksi ISA shader PS4 secara JIT menjadi byte-code SPIR-V standar yang dieksekusi native oleh Vulkan hardware pipelines.

3. **Frame Pacing & Swapchain Deadlock Prevention:**
   - Secara default menggunakan `VK_PRESENT_MODE_MAILBOX_KHR` (triple buffering non-blocking) untuk mencegah *thread hang* saat pemanggilan `acquireNextImageKHR` pada laptop hybrid (NVIDIA Optimus).
   - Penguncian framerate (60 FPS / 30 FPS) dikendalikan secara mutlak dan presisi oleh timer multimedia 1ms di `driver.cpp`, menjaga game speed tepat 1.0x.

4. **Upscaling & FidelityFX:**
   - Terintegrasi dengan AMD FidelityFX Super Resolution (FSR) untuk resolusi dinamis tinggi (1080p, 1440p, 4K) dengan performa optimal.
