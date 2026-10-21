/**
 * J-Stars Victory VS+ PC - Translation Wrapper
 * File: core/os/os_interface.h
 * Purpose: OS abstraction interface for Orbis OS (PS4) subsystem
 */

#ifndef JSTARS_OS_INTERFACE_H
#define JSTARS_OS_INTERFACE_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum anyps_platform_id {
    ANYPS_PLATFORM_UNKNOWN = 0,
    ANYPS_PLATFORM_PS4     = 1  /* Orbis OS / FreeBSD 9.0 kernel deriv / AMD Jaguar */
} anyps_platform_id_t;


typedef struct anyps_os_config {
    anyps_platform_id_t platform;
    const char *app0_path;
    const char *user_path;
    const char *title_id;
    uint32_t sdk_version;
    uint64_t direct_memory_mb;
    uint64_t flexible_memory_mb;
    bool enable_gpu;
    bool strict_imports;
    bool enable_audio;
} anyps_os_config_t;

/**
 * Universal OS Subsystem Operations Table
 */
typedef struct anyps_os_ops {
    const char *name;
    anyps_platform_id_t platform;

    /* Lifecycle */
    int (*init)(const anyps_os_config_t *config);
    void (*shutdown)(void);

    /* Memory Management */
    int (*memory_reserve)(void);
    void *(*direct_memory_alloc)(size_t size, uint32_t alignment, uint32_t flags);
    void (*direct_memory_free)(void *ptr);

    /* Threading & Sync */
    int (*thread_attach_main)(void);
    uint32_t (*thread_tcb_offset)(void);

    /* File System */
    int (*vfs_mount)(const char *virtual_path, const char *host_path);

    /* Symbol & Syscall Dispatch */
    const char *(*lookup_symbol)(const char *nid_or_name);
    void *(*resolve_function)(const char *module_name, const char *symbol_name);

    /* Hardware/Device Control */
    void (*pad_update)(void);
    void (*audio_pump)(void);
} anyps_os_ops_t;

/* Registry functions */
const anyps_os_ops_t *anyps_get_os_ops(anyps_platform_id_t platform);
int anyps_init_os(const anyps_os_config_t *config);

#ifdef __cplusplus
}
#endif

#endif /* ANYPS_OS_INTERFACE_H */
