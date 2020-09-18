import os

from conans import ConanFile, CMake

class ImageValidate(ConanFile):
    requires = [
        "openjpeg/2.3.1",
    ]
    settings = "os", "arch", "compiler", "build_type"

    generators = ["json", "cmake_paths"]
    default_options = {
        "openjpeg:shared": True
    }
    #
    # def imports(self):
    #     self.copy("*.dll", dst="bin", src="bin")  # From bin to bin
    #     self.copy("*.dylib", dst="lib", src="lib")  # From bin to bin
    #     self.copy("*.so", dst="lib", src="lib")  # From bin to bin
