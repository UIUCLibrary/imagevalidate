from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension
from uiucprescon.build.pybind11_builder import BuildPybind11Extension

PACKAGE_NAME = "uiucprescon.imagevalidate"

class BuildPybind11Extensions(BuildPybind11Extension):

    def run(self):
        conan_cmd = self.get_finalized_command("build_conan")
        conan_cmd.run()
        super().run()

    def build_extension(self, ext: Pybind11Extension):
        build_conan = self.get_finalized_command("build_conan")
        build_conan.build_libs = ['missing']
        build_conan.run()
        super().build_extension(ext)


open_jpeg_extension = Pybind11Extension(
    "uiucprescon.imagevalidate.openjp2wrap",
    sources=[
        "uiucprescon/imagevalidate/glue.cpp",
        "uiucprescon/imagevalidate/openjp2wrap.cpp",
        "uiucprescon/imagevalidate/opj_colorspace_checker.cpp"
    ],
    language="c++",
    libraries=["openjp2"],
)
openjpeg_library = \
    ("openjp2",
     {
        "url": "https://github.com/uclouvain/openjpeg/archive/v2.3.1.tar.gz",
        "cmake_args": [
            ("-DBUILD_CODEC:BOOL", "OFF"),
            ("-DBUILD_SHARED_LIBS:BOOL", "ON"),
        ],
        "sources": [],
        "expected_headers": ["openjpeg.h"]
     }
     )
setup(
    ext_modules=[open_jpeg_extension],
    libraries=[],
    cmdclass={
        "build_ext": BuildPybind11Extensions
    }
)
