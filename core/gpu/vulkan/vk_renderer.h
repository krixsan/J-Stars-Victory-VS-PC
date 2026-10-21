/**
 * anyPS - Universal Translation Wrapper
 * File: core/gpu/vulkan/vk_renderer.h
 * Purpose: Unified Vulkan 1.3+ Renderer & Presentation Backend
 */

#ifndef ANYPS_VK_RENDERER_H
#define ANYPS_VK_RENDERER_H

#include "../include/gpu_interface.h"

#ifdef __cplusplus
extern "C" {
#endif

int vk_renderer_init(int width, int height, bool vsync_60fps, bool hdr_enable);
void vk_renderer_shutdown(void);
int vk_renderer_submit(const void *cmd_buffer, size_t dword_count);
void vk_renderer_present(void);
void vk_renderer_set_fps(uint32_t fps);

extern const anyps_vk_renderer_t g_vk_renderer;

#ifdef __cplusplus
}
#endif

#endif /* ANYPS_VK_RENDERER_H */
