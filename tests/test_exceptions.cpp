//
// Created by Borchers, Henry Samuel on 5/25/21.
//

#include "exceptions.h"

#include <catch2/catch_test_macros.hpp>
#include <catch2/matchers/catch_matchers_string.hpp>
#include <catch2/matchers/catch_matchers_exception.hpp>

TEST_CASE("InvalidFileException filename only"){
    REQUIRE_THROWS_WITH(throw InvalidFileException("myfile.txt"), Catch::Matchers::Equals( "myfile.txt" ));
}
TEST_CASE("InvalidFileException filename with message"){
    REQUIRE_THROWS_WITH(throw InvalidFileException("myfile.txt", "did something stupid"), Catch::Matchers::Equals( "myfile.txt: did something stupid" ));
}