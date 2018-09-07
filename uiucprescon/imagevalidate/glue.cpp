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
    return checker.read();

    opj_stream_t *l_stream = NULL;
    opj_codec_t* l_codec = NULL;
    opj_image_t* image = NULL;

    std::string color_space_value;

    l_codec = opj_create_decompress(OPJ_CODEC_JP2);

    if(!l_codec){
        opj_destroy_codec(l_codec);
        return "Failed opj_destroy_codec";
    }

    l_stream = opj_stream_create_default_file_stream(file_path.c_str(), 1);
    if(!l_stream){
        opj_stream_destroy(l_stream);
        return "Failed opj_stream_create_default_file_stream";
    }

    opj_read_header(l_stream, l_codec, &image);
    auto  j = opj_get_cstr_info(l_codec);
    opj_decode(l_codec,l_stream, image );

    ////////
    color_space_value = opj_colorspace_checker::convert_enum_to_string(image->color_space);
//    color_space_value = to_string(image->color_space);
    ///////
    opj_stream_destroy(l_stream);
    opj_destroy_codec(l_codec);
    opj_image_destroy(image);
//    return 0;
    return color_space_value;
}
