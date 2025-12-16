#include "glue.h"
#include "exceptions.h"
#include <catch2/catch_test_macros.hpp>


TEST_CASE("utils"){
    open_jpeg_version();
}
SCENARIO("Color space"){ // NOLINT
    GIVEN("I need to know the color space of an image"){
        WHEN("a valid jp2 file encoded in SRGB"){
            std::string valid_srgb_jp2 = TEST_IMAGE_PATH "/colorspace/0000001.jp2";
            THEN("I get the value sRGB"){
                REQUIRE(color_space(valid_srgb_jp2) == "sRGB");
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

SCENARIO("Bitdepth")
{
    GIVEN("A jp2 file with 8 bit color depth") {
        const std::string valid_srgb_jp2 = TEST_IMAGE_PATH "/colorspace/0000001.jp2";
        WHEN("bit depth information is requested") {
            int bit_depth = bitdepth(valid_srgb_jp2);
            THEN("The value returned is 8"){
                REQUIRE(bit_depth == 8);

            }
        }
    }


}