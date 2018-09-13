#include "glue.h"

extern "C"{
#include <openjpeg.h>
}

#include "opj_colorspace_checker.h"

std::string open_jpeg_version(){
    return opj_version();
}


std::string color_space(const std::string &file_path) {
    auto checker = opj_colorspace_checker(file_path);
    checker.setup();
    return checker.read();
}
