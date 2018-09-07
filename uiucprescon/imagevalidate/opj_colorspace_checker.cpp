//
// Created by Borchers, Henry Samuel on 9/7/18.
//

#include <iostream>
#include "opj_colorspace_checker.h"
#include "exceptions.h"

opj_colorspace_checker::opj_colorspace_checker(const std::string &filename):
    filename(filename),
    l_codec(nullptr),
    l_stream(nullptr){

    setup_codec();
    setup_stream();
}

std::string opj_colorspace_checker::convert_enum_to_string(COLOR_SPACE colorSpace) {
    switch(colorSpace){
        case OPJ_CLRSPC_SRGB:
            return "SRGB";
        case OPJ_CLRSPC_UNKNOWN:
            return "Unknown";
        case OPJ_CLRSPC_UNSPECIFIED:
            return "UNSPECIFIED";
        case OPJ_CLRSPC_GRAY:
            return "GRAY";
        case OPJ_CLRSPC_SYCC:
            return "SYCC";
        case OPJ_CLRSPC_EYCC:
            return "EYCC";
        case OPJ_CLRSPC_CMYK:
            return "CMYK";
    }
}

void opj_colorspace_checker::setup_codec() {
    l_codec = opj_create_decompress(OPJ_CODEC_JP2);

    if(!l_codec){
        throw std::bad_alloc();
    }
}


opj_colorspace_checker::~opj_colorspace_checker() {

    if(l_codec){
        opj_destroy_codec(l_codec);
    }
    if(l_stream){
        opj_stream_destroy(l_stream);

    }

}

void opj_colorspace_checker::setup_stream() {
    l_stream = opj_stream_create_default_file_stream(filename.c_str(), 1);
    if(!l_stream) {
        throw InvalidFileException(filename, "Unable to load file");
    }

}

std::string opj_colorspace_checker::read() {
    opj_image_t* image = nullptr;
    opj_read_header(l_stream, l_codec, &image);
    auto  j = opj_get_cstr_info(l_codec);
    opj_decode(l_codec,l_stream, image );
    return opj_colorspace_checker::convert_enum_to_string(image->color_space);
}
