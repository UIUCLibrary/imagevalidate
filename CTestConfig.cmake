set(CTEST_PROJECT_NAME imagevalidate)

if (NOT CTEST_DROP_LOCATION)
    set(CTEST_DROP_LOCATION  "${CMAKE_CURRENT_LIST_DIR}/testresults")

endif ()

if(NOT CTEST_DROP_METHOD)
    set(CTEST_DROP_METHOD cp)
endif()

#set(CTEST_DROP_SITE_USER me)
