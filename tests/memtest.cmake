set(CTEST_SOURCE_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}/..)
set(CTEST_BINARY_DIRECTORY "${CMAKE_CURRENT_LIST_DIR}/../build_ci")
set(CTEST_BUILD_NAME "memtest")
set(CTEST_CMAKE_GENERATOR "Unix Makefiles")
ctest_start("Experimental")
list(APPEND config_options -DBUILD_TESTING:BOOL=ON)
list(APPEND config_options -DBUILD_UNIT_TESTS:BOOL=OFF)
list(APPEND config_options -DBUILD_CODEC:BOOL=ON)
list(APPEND config_options -DCMAKE_BUILD_TYPE=Debug)
#list(APPEND options -DBUILD_TESTING:BOOL=ON)
#list(APPEND options -DBUILD_TESTING:BOOL=ON)

ctest_configure(
        OPTIONS "${config_options}"
        )

ctest_build(TARGET tester)
ctest_test(INCLUDE imagevalidate)
ctest_memcheck(INCLUDE imagevalidate)
ctest_submit()
ctest_empty_binary_directory(${CTEST_BINARY_DIRECTORY})
