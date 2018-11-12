add_library(openjp2wrap MODULE openjp2wrap.cpp)

add_library(glue OBJECT
        glue.cpp
        opj_colorspace_checker.cpp
        )

target_include_directories(glue PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
set_target_properties(glue PROPERTIES CXX_STANDARD 11)

target_link_libraries(glue PUBLIC openjp2)

target_include_directories(glue PUBLIC
        ${libopenjpeg_SOURCE_DIR}/src/lib/openjp2
        ${libopenjpeg_BINARY_DIR}/src/lib/openjp2
        )

set_target_properties(openjp2wrap PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/uiucprescon/imagevalidate
    RUNTIME_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/uiucprescon/imagevalidate
    PREFIX "${PYTHON_MODULE_PREFIX}"
    SUFFIX "${PYTHON_MODULE_EXTENSION}"
    )

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
