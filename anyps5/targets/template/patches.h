#ifndef ANYPS4_TARGET_PATCHES_H
#define ANYPS4_TARGET_PATCHES_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Initialize game-specific binary patches and delta-time hooks.
 * 
 * @param image_base Virtual memory address where eboot.bin is loaded (typically 0x800000000).
 * @param image_size Total mapped image size in bytes.
 */
void target_apply_patches(uintptr_t image_base, size_t image_size);

#ifdef __cplusplus
}
#endif

#endif // ANYPS4_TARGET_PATCHES_H
