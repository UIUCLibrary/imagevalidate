#if(BUILD_TESTING)
    include(FetchContent)

    FetchContent_Declare(
        libcatch2
        URL https://github.com/catchorg/Catch2/archive/v2.4.0.tar.gz
#        GIT_REPOSITORY https://github.com/catchorg/Catch2.git
#        GIT_TAG 15cf3ca
    )

    FetchContent_GetProperties(libcatch2)
    if(NOT libcatch2_POPULATED)
        FetchContent_Populate(libcatch2)
        add_library(Catch2 INTERFACE)
        list(APPEND CMAKE_MODULE_PATH ${libcatch2_SOURCE_DIR}/contrib/)
    endif()

    target_include_directories(Catch2 INTERFACE ${libcatch2_SOURCE_DIR}/single_include)
    include(Catch)
# Get sample images
    if(NOT EXISTS ${PROJECT_BINARY_DIR}/metadata_test_images.tar.gz)
        file(DOWNLOAD https://jenkins.library.illinois.edu/userContent/metadata_test_images.tar.gz ${PROJECT_BINARY_DIR}/metadata_test_images.tar.gz SHOW_PROGRESS)
    endif()
    FetchContent_Declare(
            test_images
            URL ${PROJECT_BINARY_DIR}/metadata_test_images.tar.gz
    )
        if(NOT test_images_POPULATED)
            FetchContent_Populate(test_images)
        endif()

    add_executable(tester test-main.cpp test-basic.cpp)
    target_include_directories(tester PRIVATE ${PROJECT_SOURCE_DIR}/uiucprescon/imagevalidate)

    target_compile_definitions(tester PRIVATE TEST_IMAGE_PATH="${test_images_SOURCE_DIR}")

    set_target_properties(tester PROPERTIES
            CXX_STANDARD 11
            RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
            )

    target_link_libraries(tester PRIVATE Catch2 imagevalidate::glue)
    catch_discover_tests(tester
            TEST_PREFIX imagevalidate.
            )

    #############

    add_executable(tester-internal test-main.cpp tester-internal.cpp)

    target_compile_definitions(tester-internal
            PRIVATE TEST_IMAGE_PATH="${test_images_SOURCE_DIR}")

    set_target_properties(tester-internal PROPERTIES
            CXX_STANDARD 11
            RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
            )

    target_link_libraries(tester-internal
            PRIVATE
                Catch2
                glue
            )
    catch_discover_tests(tester-internal
            TEST_PREFIX imagevalidate.
            )

#endif()

