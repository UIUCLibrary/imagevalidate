cmake_minimum_required(VERSION 3.12)
project(OpenJpegWrapper)
cmake_policy(SET CMP0135 OLD)
include(FetchContent)
find_package(Python3 REQUIRED COMPONENTS Development)

if(NOT CONAN_OPENJPEG_ROOT)
    find_package(OpenJPEG)
endif()

FetchContent_Declare(libpybind11
        URL https://github.com/pybind/pybind11/archive/v2.13.6.tar.gz
        URL_HASH SHA1=8c7e3e8fec829ced31a495dec281153511f33c63
        )

FetchContent_MakeAvailable(libpybind11)

add_subdirectory(src/uiucprescon/imagevalidate)
include(CTest)
add_subdirectory(tests)
