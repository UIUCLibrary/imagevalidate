//
// Created by Borchers, Henry Samuel on 9/7/18.
//

#include <utility>
#include "opj_colorspace_checker.h"
#include "exceptions.h"

opj_colorspace_checker::opj_colorspace_checker(std::string filename) noexcept:
    filename(std::move(filename)){
}

std::string opj_colorspace_checker::convert_enum_to_string(COLOR_SPACE colorSpace) {
    switch(colorSpace){
        case OPJ_CLRSPC_SRGB:
            return "sRGB";
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
        default:
            return "invalid";
    }
}

void opj_colorspace_checker::setup_codec() {
    l_codec = std::shared_ptr<opj_codec_t>(
            opj_create_decompress(OPJ_CODEC_JP2),
            [](opj_codec_t *ptr){
                if(ptr != nullptr){
                    opj_destroy_codec(ptr);
                }
            });
    if(!l_codec){
        throw std::bad_alloc();
    }
}


void opj_colorspace_checker::setup_stream() {
     l_stream = std::shared_ptr<opj_stream_t>(
            opj_stream_create_default_file_stream(filename.c_str(), 1),
            [](opj_stream_t *ptr){
                opj_stream_destroy(ptr);
            });

    if(!l_stream) {
        throw InvalidFileException(filename, "Unable to load file");
    }

}

std::string opj_colorspace_checker::read() const{
    opj_image_t* image = nullptr;

    opj_read_header(l_stream.get(), l_codec.get(), &image);

    opj_codestream_info_v2_t *info = opj_get_cstr_info(l_codec.get());

    opj_decode(l_codec.get(), l_stream.get(), image );
    std::string result = opj_colorspace_checker::convert_enum_to_string(image->color_space);
    opj_image_destroy(image);
    opj_destroy_cstr_info(&info);
    return result;
}

void opj_colorspace_checker::setup() {

    setup_codec();
    setup_stream();
}
