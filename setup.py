import os
import pathlib
import platform
import shutil
import subprocess
import sys

import sysconfig

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext

# TODO Add CMake location option


CMAKE = shutil.which("cmake")


# Idea comes from https://stackoverflow.com/questions/42585210/extending-setuptools-extension-to-use-cmake-in-setup-py

class CMakeExtension(Extension):
    def __init__(self, name, sources=None):
        # don't invoke the original build_ext for this special extension
        super().__init__(name, sources=sources if sources is not None else [])


class BuildCMakeExt(build_ext):

    user_options = build_ext.user_options + [
        ('cmake-exec=', None,
         "Location of CMake. Defaults of CMake located on path")
    ]

    def initialize_options(self):
        super().initialize_options()
        self.cmake_exec = shutil.which("cmake")
        pass

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
            'MSC v.1915 64 bit (AMD64)': "Visual Studio 14 2015 Win64",
            'MSC v.1915 32 bit (Intel)': "Visual Studio 14 2015",
            'GCC': "Unix Makefiles",
            'Clang': "Unix Makefiles",

        }

        return cmake_build_systems_lut[python_compiler]

    def run(self):
        for extension in self.extensions:
            self.configure_cmake(extension)
            self.build_cmake(extension)
            self.build_install_cmake(extension)
            self.bundle_shared_library_deps(extension)

    def bundle_shared_library_deps(self, extension: Extension):
        print("bundling")
        pass

    def configure_cmake(self, extension: Extension):
        source_dir = os.path.abspath(os.path.dirname(__file__))

        if self.debug:
            build_configuration_name = 'Debug'
        else:
            build_configuration_name = 'Release'


        self.announce("Configuring cmake project", level=3)
        os.makedirs(self.build_temp, exist_ok=True)


            # install_prefix = os.path.abspath(os.path.dirname(__file__))
        # else:
        #     install_prefix = self.build_lib

        # install_prefix = os.path.abspath(self.build_lib)
        # print(self.get_ext_fullpath(extension.name))
        # print()

        # dll_library_dest = os.path.abspath(
        #     os.path.join(install_prefix, "uiucprescon", "imagevalidate")
        # )
        #
        package_source = os.path.join(source_dir, "uiucprescon", "imagevalidate")

        configure_command = [
                CMAKE,
                f'-H{source_dir}',
                # f'-DCMAKE_INSTALL_PREFIX={package_source}',
                f'-B{self.build_temp}',

                # f'-DCMAKE_RUNTIME_OUTPUT_DIRECTORY_RELEASE={package_source}',
                # f'-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_RELEASE={package_source}',
                # f'-DBUILD_STATIC_LIBS:BOOL=OFF',
                # '-DBUILD_THIRDPARTY:BOOL=ON',
                # f'-DCMAKE_INSTALL_INCLUDEDIR={self.build_temp}/include',
                # f'-DCMAKE_INSTALL_LIBDIR={self.build_temp}/lib',
                f'-G{self.get_build_generator_name()}',
                # f'-DPYTHON_EXTENSION_OUTPUT={os.path.splitext(self.get_ext_filename(extension.name))[0]}',
            ]
        if self.inplace == 1:

            configure_command.append(
                f'-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{build_configuration_name.upper()}={package_source}')

            configure_command.append(
                f'-DCMAKE_RUNTIME_OUTPUT_DIRECTORY_{build_configuration_name.upper()}={package_source}')

            configure_command.append(
                f'-DOPENJPEG_INSTALL_BIN_DIR={package_source}')
        else:
            configure_command.append(
                f'-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{build_configuration_name.upper()}={os.path.abspath(os.path.join(self.build_lib, "uiucprescon", "imagevalidate"))}')

            configure_command.append(
                f'-DCMAKE_RUNTIME_OUTPUT_DIRECTORY_{build_configuration_name.upper()}={os.path.abspath(os.path.join(self.build_lib, "uiucprescon", "imagevalidate"))}')

        configure_command.append(
            f'-DCMAKE_BUILD_TYPE={build_configuration_name}')

        configure_command.append(f'-DPYTHON_EXECUTABLE:FILEPATH={sys.executable}')
        configure_command.append(f'-DCMAKE_INSTALL_PREFIX={self.build_lib}')
        # configure_command.append(f'-DPYTHON_LIBRARY={os.path.join(sys.exec_prefix, "Scripts")}')
        configure_command.append(f'-DPYTHON_INCLUDE_DIR={sysconfig.get_path("include")}')
        configure_command.append(f'-DPython_ADDITIONAL_VERSIONS={sys.version_info.major}.{sys.version_info.minor}')
        self.spawn(configure_command)

    def build_cmake(self, extension: Extension):
        build_command = [
            self.cmake_exec,
            "--build", self.build_temp
        ]

        self.announce("Building binaries", level=3)

        build_command.append("--config")
        if self.debug:
            build_command.append("Debug")
        else:
            build_command.append("Release")

        if self.parallel:
            build_command.extend(["-j", str(self.parallel)])

        if "Visual Studio" in self.get_build_generator_name():
            build_command += ["--", "/NOLOGO", "/verbosity:minimal"]

        if sys.gettrace():
            subprocess.check_call(build_command)
        else:
            self.spawn(build_command)
        # if self.parallel:
        #     build_command.extend(["-j", str(self.parallel)])
        #
        # self.spawn(build_command)

    def build_install_cmake(self, extension: Extension):

        install_command = [
            self.cmake_exec,
            "--build", self.build_temp
        ]

        self.announce("Adding binaries to Python build path", level=3)

        install_command.append("--config")
        if self.debug:
            install_command.append("Debug")
        else:
            install_command.append("Release")

        install_command += ["--target", "install"]

        if self.parallel:
            install_command.extend(["-j", str(self.parallel)])

        if "Visual Studio" in self.get_build_generator_name():
            install_command += ["--", "/NOLOGO", "/verbosity:quiet"]

        if sys.gettrace():
            print("Running as a debug", file=sys.stderr)
            subprocess.check_call(install_command)
        else:
            self.spawn(install_command)


open_jpeg_extension = CMakeExtension("openjp2wrapper")

setup(
    packages=[
        'uiucprescon.imagevalidate',
        "uiucprescon.imagevalidate.profiles"],
    test_suite="tests",
    namespace_packages=["uiucprescon"],
    setup_requires=['pytest-runner'],
    install_requires=['py3exiv2bind>=0.1.1'],
    tests_require=['pytest'],
    zip_safe=False,
    ext_modules=[open_jpeg_extension],
    cmdclass={
        "build_ext": BuildCMakeExt,
    }
)
