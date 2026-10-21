cmake_minimum_required(VERSION 3.24)
project(jstars_pc LANGUAGES C CXX)

message(STATUS "=======================================================")
message(STATUS "       J-Stars Victory VS+ PC Translation Wrapper      ")
message(STATUS "=======================================================")
message(STATUS " Target Game : J-Stars Victory VS+ (PS4 - CUSA01887)   ")
message(STATUS " Target OS   : Windows x86-64 (Vulkan + Direct ABI)    ")
message(STATUS "=======================================================")

# Forward build to modular GPU and runtime pipelines
add_subdirectory(gpu)
