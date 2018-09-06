#include "glue.h"

extern "C"{
#include <openjpeg.h>
}
int get_five(){

    return 5;
}

std::string open_jpeg_version(){
    return opj_version();
}