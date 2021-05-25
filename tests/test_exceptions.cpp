//
// Created by Borchers, Henry Samuel on 5/25/21.
//

#include "catch2/catch.hpp"
#include "exceptions.h"

TEST_CASE("InvalidFileException filename only"){
    REQUIRE_THROWS_WITH(throw InvalidFileException("myfile.txt"), Catch::Equals( "myfile.txt" ));
}
TEST_CASE("InvalidFileException filename with message"){
    REQUIRE_THROWS_WITH(throw InvalidFileException("myfile.txt", "did something stupid"), Catch::Equals( "myfile.txt: did something stupid" ));
}