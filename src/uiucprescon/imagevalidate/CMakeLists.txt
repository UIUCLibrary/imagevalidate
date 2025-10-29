#add_library(openjp2wrap MODULE openjp2wrap.cpp)

add_library(glue OBJECT
        glue.cpp
        opj_colorspace_checker.cpp
        )

target_include_directories(glue PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
set_target_properties(glue PROPERTIES
        CXX_STANDARD 11
        )


add_library(imagevalidate::glue ALIAS glue)

target_include_directories(glue PUBLIC
        ${libopenjpeg_SOURCE_DIR}/src/lib/openjp2
        ${libopenjpeg_BINARY_DIR}/src/lib/openjp2
        ${CMAKE_CURRENT_SOURCE_DIR}
        )

if(CONAN_OPENJPEG_ROOT)

        find_path(OPENJPEG_INCLUDE_DIRS
            NAMES openjpeg.h
            PATHS ${CONAN_OPENJPEG_ROOT}/include/
            PATH_SUFFIXES
                openjpeg-2.3
                openjpeg-2.4
            )
    target_include_directories(glue PUBLIC ${OPENJPEG_INCLUDE_DIRS})
    find_library(OPENJPEG_LIBRARIES
            NAMES
                openjpeg
                openjpeg.so
                libopenjp2
#                libopenjp2.a
                libopenjp2.so
                libopenjp2.dylib
            PATHS ${CONAN_OPENJPEG_ROOT}/lib
            )
    target_link_libraries(glue PUBLIC ${OPENJPEG_LIBRARIES})
else()
    target_include_directories(glue PUBLIC
            ${OPENJPEG_INCLUDE_DIRS}
            )
    target_link_libraries(glue PUBLIC ${OPENJPEG_LIBRARIES})
    if(UNIX)
        if(NOT APPLE)
            target_link_libraries(glue PUBLIC pthread)
        endif()
    endif()
endif()
Python3_add_library(openjp2wrap MODULE openjp2wrap.cpp)

target_link_libraries(openjp2wrap
    PRIVATE
        glue
        pybind11::module
    )

install(TARGETS
            openjp2wrap
        RUNTIME DESTINATION uiucprescon/imagevalidate
        LIBRARY DESTINATION uiucprescon/imagevalidate
        )
