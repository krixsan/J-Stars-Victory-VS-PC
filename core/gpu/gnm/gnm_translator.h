/**
 * anyPS - Universal Translation Wrapper
 * File: core/gpu/gnm/gnm_translator.h
 * Purpose: PS4 GNM (Liverpool / GCN) Shader Recompiler & Command Processor
 */

#ifndef ANYPS_GNM_TRANSLATOR_H
#define ANYPS_GNM_TRANSLATOR_H

#include "../include/gpu_interface.h"

#ifdef __cplusplus
extern "C" {
#endif

int gnm_recompile_shader(const void *gcn_bytecode, 
                         size_t byte_length, 
                         anyps_shader_stage_t stage, 
                         anyps_spirv_output_t *out_spirv);

void gnm_free_shader(anyps_spirv_output_t *out_spirv);

extern const anyps_shader_translator_t g_gnm_translator;

#ifdef __cplusplus
}
#endif

#endif /* ANYPS_GNM_TRANSLATOR_H */
