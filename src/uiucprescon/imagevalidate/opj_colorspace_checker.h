//
// Created by Borchers, Henry Samuel on 9/7/18.
//

#ifndef OPENJPEGWRAPPER_OPJ_COLORSPACE_CHECKER_H
#define OPENJPEGWRAPPER_OPJ_COLORSPACE_CHECKER_H

extern "C"{
#include <openjpeg.h>
}

#include <string>
#include <memory>

class opj_colorspace_checker {
    std::string filename;
public:
    explicit opj_colorspace_checker(std::string filename) noexcept;
    static std::string convert_enum_to_string(COLOR_SPACE colorSpace);

private:
    std::shared_ptr<opj_codec_t> l_codec;
    std::shared_ptr<opj_stream_t> l_stream;

public:
    std::string read() const;
    void setup();

private:
    void setup_codec();
    void setup_stream();
};


#endif //OPENJPEGWRAPPER_OPJ_COLORSPACE_CHECKER_H
