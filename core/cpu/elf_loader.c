/**
 * anyPS - Universal Translation Wrapper
 * File: core/cpu/elf_loader.c
 * Purpose: Universal ELF/SELF binary reader & automatic platform detector (PS4 vs PS5)
 */

#include "elf_loader.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Standard ELF64 Structures */
typedef struct {
    uint8_t  e_ident[16];
    uint16_t e_type;
    uint16_t e_machine;
    uint32_t e_version;
    uint64_t e_entry;
    uint64_t e_phoff;
    uint64_t e_shoff;
    uint32_t e_flags;
    uint16_t e_ehsize;
    uint16_t e_phentsize;
    uint16_t e_phnum;
    uint16_t e_shentsize;
    uint16_t e_shnum;
    uint16_t e_shstrndx;
} Elf64_Ehdr;

typedef struct {
    uint32_t p_type;
    uint32_t p_flags;
    uint64_t p_offset;
    uint64_t p_vaddr;
    uint64_t p_paddr;
    uint64_t p_filesz;
    uint64_t p_memsz;
    uint64_t p_align;
} Elf64_Phdr;

/* SELF Header format */
typedef struct {
    uint32_t magic;
    uint8_t  version;
    uint8_t  mode;
    uint8_t  endian;
    uint8_t  attributes;
    uint8_t  content_type;
    uint8_t  key_type;
    uint16_t header_size;
    uint16_t meta_size;
    uint64_t file_size;
    uint16_t entry_count;
    uint16_t flags;
} __attribute__((packed)) SelfHeader;

/* Format SDK Version integer (e.g., 0x05058000 -> "05.050.001") */
static void format_sdk_version(uint32_t sdk, char *out, size_t max_len) {
    if (sdk == 0) {
        snprintf(out, max_len, "Unknown / Unspecified");
        return;
    }
    uint32_t major = (sdk >> 24) & 0xFF;
    uint32_t minor = (sdk >> 12) & 0xFFF;
    uint32_t build = sdk & 0xFFF;
    snprintf(out, max_len, "%02u.%03u.%03u (0x%08X)", major, minor, build, sdk);
}

anyps_platform_id_t anyps_detect_platform_from_memory(const void *data, size_t size) {
    if (!data || size < sizeof(Elf64_Ehdr)) return ANYPS_PLATFORM_UNKNOWN;

    const uint8_t *bytes = (const uint8_t *)data;
    uint32_t magic = *(const uint32_t *)bytes;

    /* 1. Check SELF Header */
    if (magic == ANYPS_SELF_MAGIC && size >= sizeof(SelfHeader)) {
        const SelfHeader *self_hdr = (const SelfHeader *)bytes;
        uint8_t target_id = self_hdr->content_type;
        if (target_id == SELF_TARGET_PS5) {
            return ANYPS_PLATFORM_PS5;
        } else if (target_id == SELF_TARGET_PS4) {
            return ANYPS_PLATFORM_PS4;
        }
    }

    /* 2. Check Standard ELF64 */
    if (magic == ANYPS_ELF_MAGIC) {
        const Elf64_Ehdr *ehdr = (const Elf64_Ehdr *)bytes;
        if (ehdr->e_phoff > 0 && ehdr->e_phoff + (ehdr->e_phnum * sizeof(Elf64_Phdr)) <= size) {
            const Elf64_Phdr *phdrs = (const Elf64_Phdr *)(bytes + ehdr->e_phoff);
            for (uint16_t i = 0; i < ehdr->e_phnum; ++i) {
                /* Inspect SCE Process Param segment */
                if (phdrs[i].p_type == PT_SCE_PROC_PARAM && phdrs[i].p_offset + phdrs[i].p_filesz <= size) {
                    const uint32_t *params = (const uint32_t *)(bytes + phdrs[i].p_offset);
                    /* Process param struct often starts with size, then SDK version */
                    if (phdrs[i].p_filesz >= 16) {
                        uint32_t sdk = params[2]; /* typical offset for sdk_version */
                        uint32_t major = (sdk >> 24) & 0xFF;
                        if (major >= 1 && major <= 9 && ((bytes[phdrs[i].p_offset + 4] & 0x80) != 0)) {
                            /* Heuristic match for Prospero / Orbis */
                        }
                    }
                }
            }
        }
    }

    /* Scan imports for platform indicators in data strings */
    const char *str_data = (const char *)bytes;
    size_t scan_len = size > (1024 * 1024) ? (1024 * 1024) : size;
    for (size_t i = 0; i + 12 < scan_len; ++i) {
        if (!memcmp(str_data + i, "libSceAgc", 9) || !memcmp(str_data + i, "Prospero", 8)) {
            return ANYPS_PLATFORM_PS5;
        }
        if (!memcmp(str_data + i, "libSceGnmDriver", 15) || !memcmp(str_data + i, "Orbis", 5)) {
            return ANYPS_PLATFORM_PS4;
        }
    }

    /* Default fallback for PS4 backward-compatible games */
    return ANYPS_PLATFORM_PS4;
}

int anyps_inspect_binary_file(const char *filepath, anyps_binary_info_t *out_info) {
    if (!filepath || !out_info) return -1;
    memset(out_info, 0, sizeof(*out_info));

    FILE *f = fopen(filepath, "rb");
    if (!f) {
        fprintf(stderr, "[anyPS:Loader] Cannot open file: %s\n", filepath);
        return -1;
    }

    fseek(f, 0, SEEK_END);
    long file_size = ftell(f);
    fseek(f, 0, SEEK_SET);

    if (file_size < (long)sizeof(Elf64_Ehdr)) {
        fclose(f);
        return -2;
    }

    /* Read header chunk */
    size_t read_bytes = file_size > (64 * 1024) ? (64 * 1024) : (size_t)file_size;
    uint8_t *header_buf = (uint8_t *)malloc(read_bytes);
    if (!header_buf) {
        fclose(f);
        return -3;
    }

    if (fread(header_buf, 1, read_bytes, f) != read_bytes) {
        free(header_buf);
        fclose(f);
        return -4;
    }

    uint32_t magic = *(uint32_t *)header_buf;
    if (magic == ANYPS_SELF_MAGIC) {
        out_info->format = BINARY_FORMAT_SELF;
        const SelfHeader *sh = (const SelfHeader *)header_buf;
        if (sh->content_type == SELF_TARGET_PS5) {
            out_info->platform = ANYPS_PLATFORM_PS5;
        } else {
            out_info->platform = ANYPS_PLATFORM_PS4;
        }
    } else if (magic == ANYPS_ELF_MAGIC) {
        out_info->format = BINARY_FORMAT_RAW_ELF;
        out_info->platform = anyps_detect_platform_from_memory(header_buf, read_bytes);
        Elf64_Ehdr *ehdr = (Elf64_Ehdr *)header_buf;
        out_info->entry_point = ehdr->e_entry;
        out_info->segment_count = ehdr->e_phnum;
    } else if (!memcmp(header_buf, "BBPROBE", 7)) {
        out_info->format = BINARY_FORMAT_BBPROBE;
        out_info->platform = ANYPS_PLATFORM_PS4;
    } else {
        out_info->format = BINARY_FORMAT_UNKNOWN;
        out_info->platform = ANYPS_PLATFORM_UNKNOWN;
    }

    /* Fill descriptive labels */
    if (out_info->platform == ANYPS_PLATFORM_PS5) {
        strncpy(out_info->platform_name, "PlayStation 5 (Prospero OS)", sizeof(out_info->platform_name)-1);
        strncpy(out_info->target_cpu_isa, "AMD Zen 2 (x86-64 AVX2)", sizeof(out_info->target_cpu_isa)-1);
        strncpy(out_info->target_gpu_api, "Oberon / AGC (Vulkan Backend)", sizeof(out_info->target_gpu_api)-1);
    } else {
        strncpy(out_info->platform_name, "PlayStation 4 (Orbis OS)", sizeof(out_info->platform_name)-1);
        strncpy(out_info->target_cpu_isa, "AMD Jaguar (x86-64 / Rewrite)", sizeof(out_info->target_cpu_isa)-1);
        strncpy(out_info->target_gpu_api, "Liverpool / GNM (Vulkan Backend)", sizeof(out_info->target_gpu_api)-1);
    }

    format_sdk_version(out_info->sdk_version, out_info->sdk_version_str, sizeof(out_info->sdk_version_str));

    free(header_buf);
    fclose(f);
    return 0;
}

void anyps_print_binary_info(const anyps_binary_info_t *info) {
    if (!info) return;
    printf("============================================================\n");
    printf("           anyPS Universal Binary Inspection Report         \n");
    printf("============================================================\n");
    printf(" Target Platform : %s\n", info->platform_name);
    printf(" Target CPU ISA  : %s\n", info->target_cpu_isa);
    printf(" Target GPU API  : %s\n", info->target_gpu_api);
    printf(" Binary Format   : %s\n", 
           info->format == BINARY_FORMAT_SELF ? "Signed ELF (SELF / FPKG)" :
           info->format == BINARY_FORMAT_RAW_ELF ? "Standard ELF64 Executable" :
           info->format == BINARY_FORMAT_BBPROBE ? "anyPS Prepared Probe Image" : "Unknown");
    printf(" Entry Point     : 0x%016llX\n", (unsigned long long)info->entry_point);
    printf(" SDK Version     : %s\n", info->sdk_version_str);
    printf(" Program Headers : %u segments\n", info->segment_count);
    printf("============================================================\n");
}
