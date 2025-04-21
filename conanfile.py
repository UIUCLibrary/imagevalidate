import os

from conan import ConanFile

class ImageValidate(ConanFile):
    requires = [
        "openjpeg/2.3.1",
    ]
    settings = "os", "arch", "compiler", "build_type"

    generators = ["CMakeToolchain", "CMakeDeps"]
    default_options = {
        # "openjpeg:shared": True
    }
    #
    def imports(self):
        self.copy("*.dll", dst=".", src="bin")  # From bin to bin
        self.copy("*.dylib", dst=".", src="lib")  # From bin to bin
    #     self.copy("*.so", dst="lib", src="lib")  # From bin to bin
