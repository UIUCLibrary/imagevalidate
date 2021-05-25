#include "glue.h"

extern "C"{
#include <openjpeg.h>
}

#include "opj_colorspace_checker.h"
#include "exceptions.h"
#include <memory>

std::string open_jpeg_version(){
    return opj_version();
}


std::string color_space(const std::string &file_path) {
    opj_colorspace_checker checker(file_path);
    checker.setup();
    return checker.read();
}

int bitdepth(const std::string &file_path){
    std::shared_ptr<opj_codec_t> l_codec(
            opj_create_decompress(OPJ_CODEC_JP2),
            [](opj_codec_t *ptr){
                opj_destroy_codec(ptr);
            });

    std::shared_ptr<opj_stream_t> l_stream(
            opj_stream_create_default_file_stream(file_path.c_str(), 1),
            [](opj_stream_t *ptr){
                opj_stream_destroy(ptr);
            });

    opj_image_t* image = nullptr;
    opj_read_header(l_stream.get(), l_codec.get(), &image);
    if(image == nullptr){
        throw InvalidFileException(file_path);
    }
    const auto bitDepth = (int)image->comps->prec;
    opj_image_destroy(image);
    return bitDepth;
}