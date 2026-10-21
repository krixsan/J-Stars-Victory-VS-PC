# J-Stars Victory VS+ PC - Graphics Architecture (Vulkan Backend)

`core/gpu/` mengimplementasikan arsitektur grafis yang menerjemahkan command buffer dan shader dari PlayStation 4 (**Liverpool GNM**) langsung ke backend native **Vulkan 1.3+**.

---

## Arsitektur Pipeline GPU

```
+------------------------------------+
|        PS4 Guest Draw Calls        |
|  (libSceGnmDriver, PM4 Packets)    |
+------------------------------------+
                  |
                  v
+------------------------------------+
|      GNM Translator (`gnm/`)       |
|  - GCN Instruction Decoder         |
|  - PM4 Type-3 Packet Parsing       |
|  - GCN to SPIR-V JIT Recompiler    |
+------------------------------------+
                  |
                  v
+------------------------------------+
|     Vulkan 1.3+ Renderer           |
|  - Pipeline State Caching          |
|  - Multi-threaded Draw Recording   |
|  - Triple-Buffering Mailbox Mode   |
+------------------------------------+
```
