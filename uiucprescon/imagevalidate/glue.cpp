#include "glue.h"

extern "C"{
#include <openjpeg.h>
}

std::string open_jpeg_version(){
    return opj_version();
}