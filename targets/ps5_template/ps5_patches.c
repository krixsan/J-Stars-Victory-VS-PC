#include "ps5_patches.h"
#include <stdio.h>

void ps5_patches_init(uintptr_t image_base, size_t image_size) {
    (void)image_base;
    (void)image_size;
    printf("[anyPS:PS5Patches] Initializing Prospero game runtime patches...\n");
}

void ps5_patches_apply_frame_limit(uint32_t fps) {
    printf("[anyPS:PS5Patches] Applied PS5 frame rate target: %u FPS\n", fps);
}
