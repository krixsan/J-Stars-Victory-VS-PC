cmake_minimum_required(VERSION 3.24)
project(anyPS LANGUAGES C CXX)

# anyPS Universal Platform and Target Game Options
set(PLATFORM "ps4" CACHE STRING "Target platform: ps4 or ps5")
set(TARGET_GAME "jstars" CACHE STRING "Target game profile: jstars, basara4, template, etc.")

message(STATUS "=======================================================")
message(STATUS "     anyPS - Universal Translation Wrapper (PS4/PS5)   ")
message(STATUS "=======================================================")
message(STATUS " Target Platform : ${PLATFORM}")
message(STATUS " Target Game     : ${TARGET_GAME}")
message(STATUS " Target Profile  : targets/${PLATFORM}_${TARGET_GAME}")
message(STATUS "=======================================================")

# Forward build to modular GPU and runtime pipelines
add_subdirectory(gpu)
