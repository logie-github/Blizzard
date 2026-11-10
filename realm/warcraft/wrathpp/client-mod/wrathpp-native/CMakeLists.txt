cmake_minimum_required(VERSION 3.21)
# Wrath++'s native mod: 32-bit only (it reads the stock client's own memory at its fixed addresses).
project(wrathpp-native VERSION 0.1.0 LANGUAGES NONE)
set(WXL_SDK_DIR "" CACHE PATH "Path to the WarcraftXL SDK (wrathpp.env's SDK_COMMIT)")
include("${WXL_SDK_DIR}/cmake/wxl_add_mod.cmake")
wxl_add_mod(wrathpp-native
    SOURCES src/Native.cpp
    MANIFEST mod.json
    TARGETS win-x86)
