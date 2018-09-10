#include "catch2/catch.hpp"
#include "glue.h"
#include "exceptions.h"

#include <iostream>

TEST_CASE("utils"){
    open_jpeg_version();
}
SCENARIO("Color space"){
    GIVEN("I need to know the color space of an image"){
        WHEN("a valid jp2 file encoded in SRGB"){
            std::string valid_srgb_jp2 = TEST_IMAGE_PATH "/colorspace/0000001.jp2";
            THEN("I get the value SRGB"){
                REQUIRE(color_space(valid_srgb_jp2) == "SRGB");
            }
        }
        WHEN("the file is valid"){
            std::string invalid_image = TEST_IMAGE_PATH "/colorspace/nosuchfile.jp2";
            THEN("I get an error"){
                REQUIRE_THROWS_AS(color_space(invalid_image), InvalidFileException);

            }
        }
    }

}