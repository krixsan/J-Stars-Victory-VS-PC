/**
 * @file patches.c
 * @brief anyPS4 Target Binary Patching Template (REA Protocol)
 */

#include "patches.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
#include <windows.h>
static void patch_memory(void *addr, const void *data, size_t size) {
    DWORD old_protect;
    if (VirtualProtect(addr, size, PAGE_EXECUTE_READWRITE, &old_protect)) {
        memcpy(addr, data, size);
        VirtualProtect(addr, size, old_protect, &old_protect);
        FlushInstructionCache(GetCurrentProcess(), addr, size);
    }
}
#else
#include <sys/mman.h>
#include <unistd.h>
static void patch_memory(void *addr, const void *data, size_t size) {
    uintptr_t page_start = (uintptr_t)addr & ~(4095);
    size_t page_size = ((uintptr_t)addr + size - page_start + 4095) & ~(4095);
    mprotect((void *)page_start, page_size, PROT_READ | PROT_WRITE | PROT_EXEC);
    memcpy(addr, data, size);
    mprotect((void *)page_start, page_size, PROT_READ | PROT_EXEC);
}
#endif

void target_apply_patches(uintptr_t image_base, size_t image_size) {
    if (!image_base || !image_size) return;

    printf("[anyPS4-TARGET] Initializing patches on base: %p (size: %zu)\n", (void *)image_base, image_size);

    const char *no_patch = getenv("ANYPS4_NO_PATCH");
    if (no_patch && *no_patch == '1') {
        printf("[anyPS4-TARGET] Patches skipped (ANYPS4_NO_PATCH=1).\n");
        return;
    }

    // TODO: Tambahkan signature byte matching dan patch memory di sini:
    // Contoh:
    // uint8_t *base = (uint8_t *)image_base;
    // uint8_t *target_addr = base + 0x123456;
    // static const uint8_t expected[] = { 0x90, 0x90 };
    // static const uint8_t replacement[] = { 0x31, 0xc0 };
    // if (memcmp(target_addr, expected, sizeof(expected)) == 0) {
    //     patch_memory(target_addr, replacement, sizeof(replacement));
    //     printf("[anyPS4-TARGET] [SUCCESS] Patched function at 0x123456\n");
    // }
}
