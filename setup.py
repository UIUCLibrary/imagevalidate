import os
import pathlib
import platform
import shutil

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext

# TODO remove fixed location
# TODO Add CMake location option
SOURCE_DIR = r"C:\Users\hborcher\PycharmProjects\imagevalidate"
CMAKE = shutil.which("cmake")

# Idea comes from https://stackoverflow.com/questions/42585210/extending-setuptools-extension-to-use-cmake-in-setup-py

class CMakeExtension(Extension):
    def __init__(self, name, sources=None):
        # don't invoke the original build_ext for this special extension
        super().__init__(name, sources=sources if sources is not None else [])


class BuildCMakeExt(build_ext):
    @staticmethod
    def get_build_generator_name():
        python_compiler = platform.python_compiler()

        if "GCC" in python_compiler:
            python_compiler = "GCC"

        if "Clang" in python_compiler:
            python_compiler = "Clang"

        cmake_build_systems_lut = {
            'MSC v.1900 64 bit (AMD64)': "Visual Studio 14 2015 Win64",
            'MSC v.1900 32 bit (Intel)': "Visual Studio 14 2015",
            'GCC': "Unix Makefiles",
            'Clang': "Unix Makefiles",
        }

        return cmake_build_systems_lut[python_compiler]

    def run(self):
        for extension in self.extensions:
            self.configure_cmake(extension)
            self.build_cmake(extension)


    def configure_cmake(self, extension: Extension):

        self.announce("Configuring cmake project", level=3)
        os.makedirs(self.build_temp, exist_ok=True)

        if self.inplace == 1:
            install_prefix = os.path.abspath(os.path.dirname(__file__))
        else:
            install_prefix = self.build_lib

        # install_prefix = os.path.abspath(self.build_lib)
        # print(self.get_ext_fullpath(extension.name))
        # print()

        configure_command = [
            CMAKE,
            f'-H{SOURCE_DIR}',
            f'-DCMAKE_INSTALL_PREFIX={install_prefix}',
            f'-B{self.build_temp}',
            f'-DOPENJPEG_INSTALL_BIN_DIR={install_prefix}/uiucprescon/imagevalidate',
            f'-G{self.get_build_generator_name()}',
            # f'-DPYTHON_EXTENSION_OUTPUT={os.path.splitext(self.get_ext_filename(extension.name))[0]}',
        ]
        self.spawn(configure_command)

    def build_cmake(self, extension: Extension):
        self.announce("Building binaries", level=3)

        self.spawn(["cmake", "--build", self.build_temp, "--target", "INSTALL",
                    "--config", "Release"])




open_jpeg_extension = CMakeExtension("openjp2wrapper")

setup(
    packages=[
        'uiucprescon.imagevalidate',
        "uiucprescon.imagevalidate.profiles"],
    test_suite="tests",
    namespace_packages=["uiucprescon"],
    setup_requires=['pytest-runner'],
    install_requires=['py3exiv2bind==0.1.0'],
    tests_require=['pytest'],
    zip_safe=False,
    ext_modules=[open_jpeg_extension],
    cmdclass={
        "build_ext": BuildCMakeExt,
    }
)
