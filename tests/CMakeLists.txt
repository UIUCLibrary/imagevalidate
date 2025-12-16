if (BUILD_TESTING AND Catch2_FOUND)
    include(FetchContent)
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

