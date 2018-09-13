//
// Created by Borchers, Henry Samuel on 9/13/18.
//

#include "catch2/catch.hpp"
#include "opj_colorspace_checker.h"

SCENARIO("opj_colorspace_checker"){
    GIVEN("A opj_colorspace_checker object initialized with a image"){
        auto checker = opj_colorspace_checker(TEST_IMAGE_PATH "/colorspace/0000001.jp2");
        checker.setup();
        WHEN("it calls the read method"){
            auto s = checker.read();
        }
    }
}
