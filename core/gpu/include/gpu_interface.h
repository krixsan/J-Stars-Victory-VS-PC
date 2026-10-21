/**
 * anyPS - Universal Translation Wrapper
 * File: core/gpu/include/gpu_interface.h
 * Purpose: Unified GPU Backend & Shader Translator Abstract Interface
 */

#ifndef ANYPS_GPU_INTERFACE_H
#define ANYPS_GPU_INTERFACE_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include "../../os/os_interface.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum anyps_gpu_api_type {
    GPU_API_GNM_PS4 = 0  /* Sony Liverpool GNM / GCN Generation */
} anyps_gpu_api_type_t;

typedef enum anyps_shader_stage {
    SHADER_STAGE_VERTEX                  = 0x01,
    SHADER_STAGE_FRAGMENT                = 0x02,
    SHADER_STAGE_COMPUTE                 = 0x04,
    SHADER_STAGE_GEOMETRY                = 0x08,
    SHADER_STAGE_TESS_CONTROL            = 0x10,
    SHADER_STAGE_TESS_EVAL               = 0x20
} anyps_shader_stage_t;

typedef struct anyps_spirv_output {
    const uint32_t *spirv_words;
    size_t word_count;
    const char *disassembly;
    bool has_errors;
    char error_message[256];
} anyps_spirv_output_t;

/**
 * Abstract Shader Translator Interface
 */
typedef struct anyps_shader_translator {
    const char *name;
    anyps_gpu_api_type_t api_type;

    /* Recompiles guest ISA bytecode into SPIR-V words for Vulkan */
    int (*recompile_to_spirv)(const void *guest_bytecode, 
                              size_t byte_length, 
                              anyps_shader_stage_t stage, 
                              anyps_spirv_output_t *out_spirv);

    void (*free_spirv)(anyps_spirv_output_t *spirv);
} anyps_shader_translator_t;

/**
 * Unified Vulkan Device & Presenter Interface
 */
typedef struct anyps_vk_renderer {
    int (*initialize)(int width, int height, bool vsync_60fps, bool hdr_enable);
    void (*shutdown)(void);

    /* Command submission from either GNM PM4 or AGC Command Stream */
    int (*submit_command_buffer)(const void *cmd_buffer, size_t dword_count);

    /* Presentation */
    void (*present_frame)(void);
    void (*set_target_fps)(uint32_t fps);
} anyps_vk_renderer_t;

/* Registry getters */
const anyps_shader_translator_t *anyps_get_gnm_translator(void);
const anyps_shader_translator_t *anyps_get_agc_translator(void);
const anyps_vk_renderer_t *anyps_get_vk_renderer(void);

#ifdef __cplusplus
}
#endif

#endif /* ANYPS_GPU_INTERFACE_H */
