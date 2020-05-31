cmake_minimum_required(VERSION 3.12)
project(OpenJpegWrapper)
include(FetchContent)

#find_package(Python3 REQUIRED COMPONENTS Development)
find_package(PythonInterp 3)
find_package(PythonLibs)

FetchContent_Declare(libpybind11
        URL https://github.com/pybind/pybind11/archive/v2.2.3.tar.gz
        URL_HASH SHA1=0acaeb967f09dbef53a1e2a4366780548597beba
        )

FetchContent_GetProperties(libpybind11)
if (NOT libpybind11_POPULATED)
    FetchContent_Populate(libpybind11)
    add_subdirectory(${libpybind11_SOURCE_DIR} ${libpybind11_BINARY_DIR})
endif ()

FetchContent_Declare(libopenjpeg
        URL https://github.com/uclouvain/openjpeg/archive/v2.3.1.tar.gz
#        URL_HASH SHA1=0acaeb967f09dbef53a1e2a4366780548597beba
        )

FetchContent_GetProperties(libopenjpeg)
if (NOT libopenjpeg_POPULATED)
    FetchContent_Populate(libopenjpeg)
#    set(BUILD_SHARED_LIBS OFF CACHE BOOL "")
    set(BUILD_CODEC OFF CACHE BOOL "")
#    set(BUILD_SHARED_LIBS OFF)
#        -DBUILD_SHARED_LIBS:bool
    add_subdirectory(${libopenjpeg_SOURCE_DIR} ${libopenjpeg_BINARY_DIR})
endif ()
#add_subdirectory(uiucprescon/imagevalidate)
#set_target_properties(openjp2 PROPERTIES
#    RUNTIME_OUTPUT_DIRECTORY_RELEASE ${CMAKE_RUNTIME_OUTPUT_DIRECTORY_RELEASE}
#    LIBRARY_OUTPUT_DIRECTORY_RELEASE ${CMAKE_LIBRARY_OUTPUT_DIRECTORY_RELEASE}
#    RUNTIME_OUTPUT_DIRECTORY_DEBUG ${CMAKE_RUNTIME_OUTPUT_DIRECTORY_DEBUG}
#    LIBRARY_OUTPUT_DIRECTORY_DEBUG ${CMAKE_LIBRARY_OUTPUT_DIRECTORY_DEBUG}
#
#    )
include(CTest)
add_subdirectory(tests)
