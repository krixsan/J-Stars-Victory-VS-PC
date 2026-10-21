#ifndef JSTARS_PATCHES_H
#define JSTARS_PATCHES_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Initialize modular patches for J-Stars Victory VS+ (CUSA01593 / CUSA01661) */
void jstars_patches_init(uintptr_t image_base, size_t image_size);

/* Optional runtime hooks (e.g. 60 FPS, Resolution scale, Ultrawide) */
void jstars_apply_framerate_patch(uintptr_t image_base, int target_fps);
void jstars_apply_resolution_patch(uintptr_t image_base, int width, int height);

#ifdef __cplusplus
}
#endif

#endif /* JSTARS_PATCHES_H */
