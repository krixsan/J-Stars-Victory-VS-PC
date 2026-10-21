#ifndef BASARA4_PATCHES_H
#define BASARA4_PATCHES_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Initialize binary patches & hooks for Sengoku Basara 4: Sumeragi (CUSA02057 / CUSA01134).
 * 
 * @param image_base Virtual memory address where eboot.bin is loaded.
 * @param image_size Total mapped image size in bytes.
 */
void basara4_patches_init(uintptr_t image_base, size_t image_size);

#ifdef __cplusplus
}
#endif

#endif /* BASARA4_PATCHES_H */
