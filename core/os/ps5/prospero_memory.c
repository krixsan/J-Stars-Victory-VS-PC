/**
 * anyPS - Universal Translation Wrapper
 * File: core/os/ps5/prospero_memory.c
 * Purpose: Unified GDDR6 Memory Subsystem for Prospero OS (PS5)
 */

#include "prospero_runtime.h"
#include <stdio.h>
#include <stdlib.h>

#ifdef _WIN32
#include <windows.h>
#endif

static void *s_prospero_base = NULL;
static size_t s_prospero_committed_bytes = 0;

int prospero_memory_init(void) {
    if (s_prospero_base) return 0;

    printf("[anyPS:ProsperoMemory] Reserving 16 GiB virtual address space for PS5 unified memory...\n");
#ifdef _WIN32
    /* Attempt to reserve 16 GiB in high address range */
    s_prospero_base = VirtualAlloc((void *)PROSPERO_ADDR_SPACE_START, 
                                   (size_t)16 * 1024 * 1024 * 1024ULL, 
                                   MEM_RESERVE, 
                                   PAGE_NOACCESS);
    if (!s_prospero_base) {
        /* Fallback: let system allocate reserve base */
        s_prospero_base = VirtualAlloc(NULL, 
                                       (size_t)16 * 1024 * 1024 * 1024ULL, 
                                       MEM_RESERVE, 
                                       PAGE_NOACCESS);
    }
#else
    s_prospero_base = malloc(1024 * 1024);
#endif

    if (!s_prospero_base) {
        printf("[anyPS:ProsperoMemory] Warning: 16 GiB continuous reserve failed; fallback to dynamic chunks.\n");
    } else {
        printf("[anyPS:ProsperoMemory] Unified memory reserved at %p.\n", s_prospero_base);
    }

    return 0;
}

void *prospero_direct_alloc(size_t size, uint32_t alignment, uint32_t flags) {
    (void)alignment;
    (void)flags;
#ifdef _WIN32
    void *ptr = VirtualAlloc(NULL, size, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    if (ptr) s_prospero_committed_bytes += size;
    return ptr;
#else
    return malloc(size);
#endif
}

void prospero_direct_free(void *ptr) {
#ifdef _WIN32
    if (ptr) VirtualFree(ptr, 0, MEM_RELEASE);
#else
    free(ptr);
#endif
}
