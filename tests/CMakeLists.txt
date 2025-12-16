if(BUILD_TESTING)
    include(FetchContent)

    FetchContent_Declare(
        libcatch2
        URL https://github.com/catchorg/Catch2/archive/v3.11.0.tar.gz
        URL_HASH SHA1=5f5a932acf6990764c33ed80ee04f1c696f4d5bc
        DOWNLOAD_EXTRACT_TIMESTAMP true
    )

    FetchContent_MakeAvailable(libcatch2)
    list(APPEND CMAKE_MODULE_PATH ${libcatch2_SOURCE_DIR}/contrib/)

    target_include_directories(Catch2 INTERFACE ${libcatch2_SOURCE_DIR}/single_include)
    include(Catch)
# Get sample images
    if(NOT EXISTS ${PROJECT_BINARY_DIR}/metadata_test_images.tar.gz)
        file(DOWNLOAD https://nexus.library.illinois.edu/repository/sample-data/images/metadata_test_images.tar.gz ${PROJECT_BINARY_DIR}/metadata_test_images.tar.gz SHOW_PROGRESS)
    endif()
    FetchContent_Declare(
            test_images
            URL ${PROJECT_BINARY_DIR}/metadata_test_images.tar.gz
    )
    FetchContent_MakeAvailable(test_images)
    add_executable(tester test-basic.cpp test_exceptions.cpp)
    target_include_directories(tester PRIVATE ${PROJECT_SOURCE_DIR}/uiucprescon/imagevalidate)

    target_compile_definitions(tester PRIVATE TEST_IMAGE_PATH="${test_images_SOURCE_DIR}")
    if(CMAKE_CXX_CPPCHECK)
        set_property(TARGET tester PROPERTY
                CXX_CPPCHECK ${CMAKE_CXX_CPPCHECK};--suppress=*:${libcatch2_SOURCE_DIR}/single_include/catch2/catch.hpp
            )
    endif()

    target_link_libraries(tester PRIVATE Catch2::Catch2WithMain imagevalidate::glue)
    catch_discover_tests(tester
            TEST_PREFIX imagevalidate.
            )

    #############

    add_executable(tester-internal tester-internal.cpp)
    target_compile_definitions(tester-internal
            PRIVATE TEST_IMAGE_PATH="${test_images_SOURCE_DIR}")


    target_link_libraries(tester-internal
            PRIVATE
                Catch2::Catch2WithMain
                glue
            )
    catch_discover_tests(tester-internal
            TEST_PREFIX imagevalidate.
            )

endif()

