/**
 * anyPS - Universal Translation Wrapper
 * File: core/cpu/elf_loader.h
 * Purpose: Universal ELF/SELF binary reader & automatic platform detector (PS4 vs PS5)
 */

#ifndef ANYPS_ELF_LOADER_H
#define ANYPS_ELF_LOADER_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include "../os/os_interface.h"

#ifdef __cplusplus
extern "C" {
#endif

#define ANYPS_ELF_MAGIC   0x464C457FU /* "\x7FELF" in little-endian */
#define ANYPS_SELF_MAGIC  0x1D3D154FU /* PS4/PS5 Signed ELF */

/* SCE Program Header Types */
#define PT_SCE_RELA         0x60000000U
#define PT_SCE_DYNLIBDATA   0x61000000U
#define PT_SCE_PROGLIB      0x61000001U
#define PT_SCE_PROC_PARAM   0x61000001U
#define PT_SCE_MODULE_PARAM 0x61000002U
#define PT_SCE_RELRO        0x61000010U

/* SELF Target Platform IDs */
#define SELF_TARGET_PS4       0x01U
#define SELF_TARGET_PS5       0x12U

typedef enum anyps_binary_format {
    BINARY_FORMAT_UNKNOWN = 0,
    BINARY_FORMAT_RAW_ELF,
    BINARY_FORMAT_SELF,
    BINARY_FORMAT_PRX,
    BINARY_FORMAT_BBPROBE
} anyps_binary_format_t;

typedef struct anyps_binary_info {
    anyps_platform_id_t platform;
    anyps_binary_format_t format;
    char platform_name[32];
    char target_cpu_isa[32];
    char target_gpu_api[32];
    
    uint64_t entry_point;
    uint64_t mapped_size;
    uint32_t sdk_version;
    char sdk_version_str[32];
    
    char title_id[16];
    char content_id[48];
    uint16_t segment_count;
    bool is_encrypted;
} anyps_binary_info_t;

/**
 * Detects whether buffer represents PS4 or PS5 binary.
 */
anyps_platform_id_t anyps_detect_platform_from_memory(const void *data, size_t size);

/**
 * Inspects a binary file path and populates complete metadata report.
 */
int anyps_inspect_binary_file(const char *filepath, anyps_binary_info_t *out_info);

/**
 * Pretty prints binary inspection summary to stdout.
 */
void anyps_print_binary_info(const anyps_binary_info_t *info);

#ifdef __cplusplus
}
#endif

#endif /* ANYPS_ELF_LOADER_H */
