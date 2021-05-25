//
// Created by Borchers, Henry Samuel on 9/7/18.
//

#ifndef OPENJPEGWRAPPER_OPJ_COLORSPACE_CHECKER_H
#define OPENJPEGWRAPPER_OPJ_COLORSPACE_CHECKER_H

#include <string>
extern "C"{
#include <openjpeg.h>
}


class opj_colorspace_checker {
    const std::string filename;
public:
    explicit opj_colorspace_checker(const std::string &filename);
    static std::string convert_enum_to_string(COLOR_SPACE colorSpace);

private:
    opj_codec_t* l_codec = nullptr;
    opj_stream_t *l_stream = nullptr;

public:
    virtual ~opj_colorspace_checker();
    std::string read();
    void setup();

private:
    void setup_codec();
    void setup_stream();
};


#endif //OPENJPEGWRAPPER_OPJ_COLORSPACE_CHECKER_H
