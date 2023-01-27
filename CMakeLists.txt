cmake_minimum_required(VERSION 3.12)
project(OpenJpegWrapper)
cmake_policy(SET CMP0135 OLD)
include(FetchContent)
find_package(Python3 REQUIRED COMPONENTS Development)

if(NOT CONAN_OPENJPEG_ROOT)
    find_package(OpenJPEG)
endif()

FetchContent_Declare(libpybind11
        URL https://github.com/pybind/pybind11/archive/v2.5.0.tar.gz
        URL_HASH SHA1=8caf0bde85813f9eac55e516d4afcb925806aa5e
        )

FetchContent_GetProperties(libpybind11)
if (NOT libpybind11_POPULATED)
    FetchContent_Populate(libpybind11)
    add_subdirectory(${libpybind11_SOURCE_DIR} ${libpybind11_BINARY_DIR})
endif ()

add_subdirectory(uiucprescon/imagevalidate)
include(CTest)
add_subdirectory(tests)
