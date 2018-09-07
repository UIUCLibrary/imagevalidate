#include "glue.h"
#include <pybind11/pybind11.h>

PYBIND11_MODULE(openjp2wrap, m){
    pybind11::options options;
    options.enable_function_signatures();
    m.def("open_jpeg_version", &open_jpeg_version, "Get the version of OpenJPEG built with");
}

