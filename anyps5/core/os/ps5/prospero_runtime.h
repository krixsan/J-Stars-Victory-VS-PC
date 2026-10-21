/**
 * anyPS - Universal Translation Wrapper
 * File: core/os/ps5/prospero_runtime.h
 * Purpose: Header for Prospero OS (PlayStation 5) HLE subsystem
 */

#ifndef ANYPS_PROSPERO_RUNTIME_H
#define ANYPS_PROSPERO_RUNTIME_H

#include "../os_interface.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Prospero Memory Limits */
#define PROSPERO_ADDR_SPACE_START  0x0000001000000000ULL
#define PROSPERO_ADDR_SPACE_END    0x00007FFFFFFFFFFFULL
#define PROSPERO_GAME_MEMORY_MB    13824ULL /* 13.5 GiB for game allocations */
#define PROSPERO_SYSTEM_MEMORY_MB  2560ULL  /* 2.5 GiB reserved for Prospero OS */

/* Prospero SDK Version Range */
#define PROSPERO_SDK_MIN           0x01000000U
#define PROSPERO_SDK_MAX           0x09000000U

/* Subsystem Initializers */
int prospero_runtime_init(const anyps_os_config_t *config);
void prospero_runtime_shutdown(void);

int prospero_memory_init(void);
void *prospero_direct_alloc(size_t size, uint32_t alignment, uint32_t flags);
void prospero_direct_free(void *ptr);

int prospero_kernel_init(void);
int prospero_kernel_attach_main(void);

int prospero_services_init(void);
const char *prospero_lookup_symbol(const char *nid_or_name);
void *prospero_resolve_function(const char *module_name, const char *symbol_name);

/* OS Operations Table instance */
extern const anyps_os_ops_t g_prospero_os_ops;

#ifdef __cplusplus
}
#endif

#endif /* ANYPS_PROSPERO_RUNTIME_H */
