#ifndef ANYPS_PS5_PATCHES_H
#define ANYPS_PS5_PATCHES_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

void ps5_patches_init(uintptr_t image_base, size_t image_size);
void ps5_patches_apply_frame_limit(uint32_t fps);

#ifdef __cplusplus
}
#endif

#endif /* ANYPS_PS5_PATCHES_H */
