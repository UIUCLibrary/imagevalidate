Python3_add_library(openjp2wrap MODULE openjp2wrap.cpp)

add_library(glue OBJECT glue.cpp glue.h opj_colorspace_checker.cpp opj_colorspace_checker.h exceptions.h)

target_include_directories(glue PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
set_target_properties(glue PROPERTIES CXX_STANDARD 11)

target_link_libraries(glue PUBLIC openjp2)

target_include_directories(glue PRIVATE
        ${libopenjpeg_SOURCE_DIR}/src/lib/openjp2
        ${libopenjpeg_BINARY_DIR}/src/lib/openjp2
        )

if(PYTHON_EXTENSION_OUTPUT)
    message(STATUS "Changing to ${PYTHON_EXTENSION_OUTPUT}")
    set_target_properties(openjp2wrap PROPERTIES
        LIBRARY_OUTPUT_NAME ${PYTHON_EXTENSION_OUTPUT}
        RUNTIME_OUTPUT_NAME ${PYTHON_EXTENSION_OUTPUT}
    )
endif(PYTHON_EXTENSION_OUTPUT)

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
