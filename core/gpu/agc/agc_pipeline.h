/**
 * anyPS - Universal Translation Wrapper
 * File: core/gpu/agc/agc_pipeline.h
 * Purpose: PS5 AGC (Oberon / RDNA 2) Shader Recompiler & Command Pipeline Interface
 */

#ifndef ANYPS_AGC_PIPELINE_H
#define ANYPS_AGC_PIPELINE_H

#include "../include/gpu_interface.h"

#ifdef __cplusplus
extern "C" {
#endif

int agc_recompile_shader(const void *rdna2_bytecode, 
                         size_t byte_length, 
                         anyps_shader_stage_t stage, 
                         anyps_spirv_output_t *out_spirv);

void agc_free_shader(anyps_spirv_output_t *out_spirv);

extern const anyps_shader_translator_t g_agc_translator;

#ifdef __cplusplus
}
#endif

#endif /* ANYPS_AGC_PIPELINE_H */
