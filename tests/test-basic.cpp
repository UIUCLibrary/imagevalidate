#include "catch2/catch.hpp"
#include "glue.h"

#include <iostream>

TEST_CASE("dummy"){
    REQUIRE(get_five() == 5);
    std::cout << open_jpeg_version() << std::endl;
}