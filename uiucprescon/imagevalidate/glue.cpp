#include "glue.h"

extern "C"{
#include <openjpeg.h>
}

#include "opj_colorspace_checker.h"
#include <iostream>

std::string open_jpeg_version(){
    return opj_version();
}


std::string color_space(const std::string &file_path) {
    auto checker = opj_colorspace_checker(file_path);
    checker.setup();
    return checker.read();
}

int bitdepth(const std::string &file_path){
    opj_codec_t* l_codec = opj_create_decompress(OPJ_CODEC_JP2);

    opj_stream_t *l_stream = opj_stream_create_default_file_stream(file_path.c_str(), 1);
    opj_image_t* image = nullptr;

    opj_read_header(l_stream, l_codec, &image);
//    TODO error check
// TODO: manage memory
    long int *j = new long;
    *j  = 8;
    (*j)++;
    std::cout << j << "\n";
    int bitDepth = image->comps->prec;
    return bitDepth;
}