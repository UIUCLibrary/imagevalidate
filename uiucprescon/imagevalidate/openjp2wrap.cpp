#include "glue.h"
#include "exceptions.h"

#include <pybind11/pybind11.h>

//NOLINTNEXTLINE
PYBIND11_MODULE(openjp2wrap, m){ //  cppcheck-suppress unusedFunction
    pybind11::options options;
    options.enable_function_signatures();
    m.def("open_jpeg_version", &open_jpeg_version, "Get the version of OpenJPEG built with");
    m.def("get_colorspace", &color_space, "get color space value from an image");
    m.def("get_bit_depth", &bitdepth, "get color bit depth from an image");
    pybind11::register_exception<InvalidFileException>(m, "InvalidFileException");

}

