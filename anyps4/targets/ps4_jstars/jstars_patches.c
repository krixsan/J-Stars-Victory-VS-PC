#include "jstars_patches.h"
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <stdlib.h>

#ifdef _WIN32
#include <windows.h>
#endif

/*
 * Modular REA binary patches for J-Stars Victory VS+ (CUSA01593 / CUSA01661)
 *
 * REA Analysis Findings:
 * 1. eboot.bin VirtAddr 0x43d8e6 .. 0x43d903:
 *    The engine selects flip rate based on game mode / match state:
 *      cmpl $3, %r15d ; jne +7 ; movl $2, %esi ; jmp ... ; xor %esi, %esi ; cmpl $2, %r15d ; jne ... ; movl $1, %esi
 *      callq sceVideoOutSetFlipRate
 *    During matches, %r15d = 2 causes movl $1, %esi (30 FPS flip rate lock).
 *    We patch the movl $1/%2, %esi instructions to xorl %esi, %esi (60 FPS flip rate).
 *
 * 2. eboot.bin VirtAddr 0x24630c:
 *    FPS engine configuration structure:
 *      movl $0x41f00000, 0x4(%rax)   ; 30.0f FPS
 *      movl $0x3d088889, 0x8(%rax)   ; 1.0f / 30.0f dt
 *      movl $0x3dcccccd, 0xc(%rax)   ; 0.1f max frame time
 *    We patch this to:
 *      60.0f FPS (0x42700000), 1.0f / 60.0f dt (0x3c888889), 0.05f max dt (0x3d4ccccd).
 *
 * 3. eboot.bin VirtAddr 0x585bc8:
 *    Global frame delta constant 1.0f / 30.0f (0x3d088889) used by motion/camera update at VirtAddr 0x2fa0ec.
 *    We patch this to 1.0f / 60.0f (0x3c888889).
 */

static void patch_memory(uint8_t *dest, const uint8_t *src, size_t size) {
#ifdef _WIN32
    DWORD old_protect;
    if (VirtualProtect(dest, size, PAGE_EXECUTE_READWRITE, &old_protect)) {
        memcpy(dest, src, size);
        VirtualProtect(dest, size, old_protect, &old_protect);
        FlushInstructionCache(GetCurrentProcess(), dest, size);
    } else {
        memcpy(dest, src, size);
    }
#else
    memcpy(dest, src, size);
#endif
}

void jstars_patches_init(uintptr_t image_base, size_t image_size) {
    if (!image_base || !image_size) return;

    printf("[J-STARS] Initializing REA 60 FPS & graphics patches on image base: 0x%llx (size: %zu)\n",
           (unsigned long long)image_base, image_size);

    uint8_t *base = (uint8_t *)image_base;

    // --- Patch 1: Flip Rate Selection (VirtAddr 0x43d8e6) ---
    // Must always run to ensure sceVideoOutSetFlipRate receives 0, preventing presenter stall / black screen.
    if (image_size > 0x43da00) {
        uint8_t *p_rate2 = base + 0x43d8ec;
        uint8_t *p_rate1 = base + 0x43d8fb;
        static const uint8_t expected2[5] = {0xbe, 0x02, 0x00, 0x00, 0x00};
        static const uint8_t expected1[5] = {0xbe, 0x01, 0x00, 0x00, 0x00};
        static const uint8_t xor_esi[5]   = {0x31, 0xf6, 0x90, 0x90, 0x90};

        if (memcmp(p_rate2, expected2, 5) == 0 && memcmp(p_rate1, expected1, 5) == 0) {
            patch_memory(p_rate2, xor_esi, 5);
            patch_memory(p_rate1, xor_esi, 5);
            printf("[J-STARS] [PATCH SUCCESS] eboot.bin 0x43d8e6 flip rate logic patched to force rate=0!\n");
        } else {
            printf("[J-STARS] [PATCH NOTICE] eboot.bin 0x43d8e6 flip rate logic already patched or signature mismatch.\n");
        }
    }

    // Check if user disabled 60 FPS binary patches or requested 30 FPS console mode
    const char *no_patch = getenv("JSTARS_NO_PATCH");
    const char *fps30 = getenv("JSTARS_30FPS");
    if ((no_patch && *no_patch == '1') || (fps30 && *fps30 == '1')) {
        printf("[J-STARS] 60 FPS binary patches skipped (30 FPS normal console mode).\n");
        fflush(stdout);
        return;
    }

    // --- Patch 2: Physics Step Delta Time (Havok Physics Engine) ---
    // All 4 physics world creation sites store 1.0f / 30.0f (0x3d088889) into offset 0x10c.
    // At 60 FPS, we scale dt to 1.0f / 60.0f (0x3c888889) so physics/gravity/knockback advances at 1.0x normal speed.
    // 1. 0x1817be: c7 83 0c 01 00 00 89 88 08 3d -> c7 83 0c 01 00 00 89 88 88 3c
    // 2. 0x18189c: c7 83 0c 01 00 00 89 88 08 3d -> c7 83 0c 01 00 00 89 88 88 3c
    // 3. 0x182cbb: 41 c7 85 0c 01 00 00 89 88 08 3d -> 41 c7 85 0c 01 00 00 89 88 88 3c
    // 4. 0x186c52: 41 c7 86 0c 01 00 00 89 88 08 3d -> 41 c7 86 0c 01 00 00 89 88 88 3c
    if (image_size > 0x186d00) {
        static const uint8_t exp_rbx[10] = {0xc7, 0x83, 0x0c, 0x01, 0x00, 0x00, 0x89, 0x88, 0x08, 0x3d};
        static const uint8_t pat_rbx[10] = {0xc7, 0x83, 0x0c, 0x01, 0x00, 0x00, 0x89, 0x88, 0x88, 0x3c};
        static const uint8_t exp_r13[11] = {0x41, 0xc7, 0x85, 0x0c, 0x01, 0x00, 0x00, 0x89, 0x88, 0x08, 0x3d};
        static const uint8_t pat_r13[11] = {0x41, 0xc7, 0x85, 0x0c, 0x01, 0x00, 0x00, 0x89, 0x88, 0x88, 0x3c};
        static const uint8_t exp_r14[11] = {0x41, 0xc7, 0x86, 0x0c, 0x01, 0x00, 0x00, 0x89, 0x88, 0x08, 0x3d};
        static const uint8_t pat_r14[11] = {0x41, 0xc7, 0x86, 0x0c, 0x01, 0x00, 0x00, 0x89, 0x88, 0x88, 0x3c};

        int phys_patched = 0;
        if (memcmp(base + 0x1817be, exp_rbx, 10) == 0) {
            patch_memory(base + 0x1817be, pat_rbx, 10);
            ++phys_patched;
        }
        if (memcmp(base + 0x18189c, exp_rbx, 10) == 0) {
            patch_memory(base + 0x18189c, pat_rbx, 10);
            ++phys_patched;
        }
        if (memcmp(base + 0x182cbb, exp_r13, 11) == 0) {
            patch_memory(base + 0x182cbb, pat_r13, 11);
            ++phys_patched;
        }
        if (memcmp(base + 0x186c52, exp_r14, 11) == 0) {
            patch_memory(base + 0x186c52, pat_r14, 11);
            ++phys_patched;
        }
        printf("[J-STARS] [PATCH SUCCESS] Havok physics timestep patched (%d/4 sites) to 1/60s (0.01667s)!\n",
               phys_patched);
    }

    // --- Patch 3: Engine FPS Config & Speed Multiplier (VirtAddr 0x24630c) ---
    // Original:
    //   movl $0x41f00000, 4(%rax)   ; 30.0f FPS / animation multiplier
    //   movl $0x3d088889, 8(%rax)   ; 1.0f / 30.0f delta time
    //   movl $0x3dcccccd, 12(%rax)  ; 0.1f speed scale / max dt clamp
    //
    // Fixed for 60 FPS normal speed (prevents 2x fast-forward):
    //   4(%rax)  = 15.0f (0x41700000): 60 ticks * 15.0f == 30 ticks * 30.0f == 900.0 (normal 1.0x animation speed)
    //   8(%rax)  = 1/60.0f (0x3c888889): 0.0166667s per-frame delta
    //   12(%rax) = 0.05f (0x3d4ccccd): scaled by 0.5 for 60 FPS tick rate
    if (image_size > 0x246400) {
        uint8_t *p_fps = base + 0x24630c;
        static const uint8_t expected_fps[21] = {
            0xc7, 0x40, 0x04, 0x00, 0x00, 0xf0, 0x41, // movl $0x41f00000, 4(%rax) (30.0f)
            0xc7, 0x40, 0x08, 0x89, 0x88, 0x08, 0x3d, // movl $0x3d088889, 8(%rax) (1/30.0f)
            0xc7, 0x40, 0x0c, 0xcd, 0xcc, 0xcc, 0x3d  // movl $0x3dcccccd, 12(%rax) (0.1f)
        };
        static const uint8_t patched_fps[21] = {
            0xc7, 0x40, 0x04, 0x00, 0x00, 0x70, 0x41, // movl $0x41700000, 4(%rax) (15.0f = 0.5x scale)
            0xc7, 0x40, 0x08, 0x89, 0x88, 0x88, 0x3c, // movl $0x3c888889, 8(%rax) (1/60.0f)
            0xc7, 0x40, 0x0c, 0xcd, 0xcc, 0x4c, 0x3d  // movl $0x3d4ccccd, 12(%rax) (0.05f = 0.5x scale)
        };

        if (memcmp(p_fps, expected_fps, 21) == 0) {
            patch_memory(p_fps, patched_fps, 21);
            printf("[J-STARS] [PATCH SUCCESS] eboot.bin 0x24630c engine speed scaled 0.5x (15.0f / dt=1/60s / 0.05f)!\n");
        } else {
            printf("[J-STARS] [PATCH NOTICE] eboot.bin 0x24630c already patched or signature mismatch.\n");
        }
    }

    // --- Patch 4: Frame delta time constant (VirtAddr 0x585bc8) ---
    // 89 88 08 3d (0.033333334f) -> 89 88 88 3c (0.016666668f)
    if (image_size > 0x585c00) {
        uint8_t *p_dt = base + 0x585bc8;
        static const uint8_t expected_dt[4] = {0x89, 0x88, 0x08, 0x3d};
        static const uint8_t patched_dt[4]  = {0x89, 0x88, 0x88, 0x3c};

        if (memcmp(p_dt, expected_dt, 4) == 0) {
            patch_memory(p_dt, patched_dt, 4);
            printf("[J-STARS] [PATCH SUCCESS] eboot.bin 0x585bc8 global delta time patched to 1/60s (0.016667s)!\n");
        } else {
            printf("[J-STARS] [PATCH NOTICE] eboot.bin 0x585bc8 already patched or signature mismatch.\n");
        }
    }

    // --- Patch 5: Timer Manager Global Speed Multiplier (VirtAddr 0x41f6c9) ---
    // 0x41f6c9: c7 43 0c 00 00 80 3f (movl $0x3f800000, 0xc(%rbx)) ; 1.0f speed scale
    // At 60 FPS, scale to 0.5f (0x3f000000) so timer advance is 1.0x normal speed.
    if (image_size > 0x41f700) {
        uint8_t *p_speed = base + 0x41f6c9;
        static const uint8_t exp_speed[7] = {0xc7, 0x43, 0x0c, 0x00, 0x00, 0x80, 0x3f};
        static const uint8_t pat_speed[7] = {0xc7, 0x43, 0x0c, 0x00, 0x00, 0x00, 0x3f}; // 0.5f

        if (memcmp(p_speed, exp_speed, 7) == 0) {
            patch_memory(p_speed, pat_speed, 7);
            printf("[J-STARS] [PATCH SUCCESS] eboot.bin 0x41f6c9 Timer Manager speed multiplier scaled 0.5x!\n");
        } else {
            printf("[J-STARS] [PATCH NOTICE] eboot.bin 0x41f6c9 already patched or signature mismatch.\n");
        }
    }

    // --- Patch 6: Character Animation Track Speed Multiplier (VirtAddr 0x228286 & 0x22844c) ---
    // 0x228286: movl $0x3f800000, 0xa4/0xa8/0xac(%rdi) ; 1.0f animation speed
    // 0x22844c: movl $0x3f800000, 0xa4/0xa8/0xac(%rbx) ; 1.0f animation speed
    if (image_size > 0x228500) {
        uint8_t *p_anim1 = base + 0x228286;
        static const uint8_t exp_anim1[30] = {
            0xc7, 0x87, 0xa4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x3f,
            0xc7, 0x87, 0xa8, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x3f,
            0xc7, 0x87, 0xac, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x3f
        };
        static const uint8_t pat_anim1[30] = {
            0xc7, 0x87, 0xa4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x3f, // 0.5f
            0xc7, 0x87, 0xa8, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x3f, // 0.5f
            0xc7, 0x87, 0xac, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x3f  // 0.5f
        };

        if (memcmp(p_anim1, exp_anim1, 30) == 0) {
            patch_memory(p_anim1, pat_anim1, 30);
            printf("[J-STARS] [PATCH SUCCESS] eboot.bin 0x228286 character animation track speed scaled 0.5x!\n");
        } else {
            printf("[J-STARS] [PATCH NOTICE] eboot.bin 0x228286 already patched or signature mismatch.\n");
        }

        uint8_t *p_anim2 = base + 0x22844c;
        static const uint8_t exp_anim2[30] = {
            0xc7, 0x83, 0xa4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x3f,
            0xc7, 0x83, 0xa8, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x3f,
            0xc7, 0x83, 0xac, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x3f
        };
        static const uint8_t pat_anim2[30] = {
            0xc7, 0x83, 0xa4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x3f, // 0.5f
            0xc7, 0x83, 0xa8, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x3f, // 0.5f
            0xc7, 0x83, 0xac, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x3f  // 0.5f
        };

        if (memcmp(p_anim2, exp_anim2, 30) == 0) {
            patch_memory(p_anim2, pat_anim2, 30);
            printf("[J-STARS] [PATCH SUCCESS] eboot.bin 0x22844c secondary animation track speed scaled 0.5x!\n");
        } else {
            printf("[J-STARS] [PATCH NOTICE] eboot.bin 0x22844c already patched or signature mismatch.\n");
        }
    }

    // --- Patch 7: Default Animation Evaluation Speed Constant (VirtAddr 0x578ec0) ---
    // 0x578ec0 is loaded at VirtAddr 0x2488de (vmovss 0x3305da(%rip), %xmm0) to scale animation evaluation.
    // 00 00 80 3f (1.0f) -> 00 00 00 3f (0.5f)
    if (image_size > 0x578f00) {
        uint8_t *p_speed_const = base + 0x578ec0;
        static const uint8_t exp_speed_const[4] = {0x00, 0x00, 0x80, 0x3f};
        static const uint8_t pat_speed_const[4] = {0x00, 0x00, 0x00, 0x3f}; // 0.5f

        if (memcmp(p_speed_const, exp_speed_const, 4) == 0) {
            patch_memory(p_speed_const, pat_speed_const, 4);
            printf("[J-STARS] [PATCH SUCCESS] eboot.bin 0x578ec0 animation evaluation constant scaled to 0.5f!\n");
        } else {
            printf("[J-STARS] [PATCH NOTICE] eboot.bin 0x578ec0 already patched or signature mismatch.\n");
        }
    }

    fflush(stdout);
}



void jstars_apply_framerate_patch(uintptr_t image_base, int target_fps) {
    (void)image_base;
    (void)target_fps;
}

void jstars_apply_resolution_patch(uintptr_t image_base, int width, int height) {
    (void)image_base;
    (void)width;
    (void)height;
}

