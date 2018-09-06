if(BUILD_TESTING)
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
    add_executable(tester test-main.cpp test-basic.cpp)
    target_link_libraries(tester PRIVATE Catch2 glue)
    catch_discover_tests(tester)

endif()

