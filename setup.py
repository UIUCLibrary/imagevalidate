import json
import os
import platform
import re
import shutil
import sys
import tarfile
import urllib
import zipfile
import sysconfig
import tempfile
from functools import reduce
from typing import Iterable, Tuple, List, Optional, Dict, Any, Union
import abc
from distutils.sysconfig import customize_compiler
from urllib import request
try:
    from macholib import MachO, MachOStandalone
except ImportError:
    pass
import setuptools
from setuptools import setup
from setuptools.command.build_ext import build_ext
from setuptools.command.build_clib import build_clib
from setuptools import Command
from ctypes.util import find_library

try:
    from conans.client import conan_api
except ModuleNotFoundError:
    print("Conan not installed", file=sys.stderr)

CMAKE = shutil.which("cmake")
PACKAGE_NAME = "uiucprescon.imagevalidate"
PYBIND11_URL = "https://github.com/pybind/pybind11/archive/v2.2.4.tar.gz"


class CMakeException(RuntimeError):
    pass


class PackageClib(Command):
    description = "Package required clib deps"
    user_options = []

    def initialize_options(self):
        self.clib_lib_path = None
        self.destination = None

    def finalize_options(self):
        self.library_dirs = \
            self.get_finalized_command("build_ext").library_dirs

        self.clib_bin_path = os.path.join(
            self.get_finalized_command("build_clib").build_clib, "bin")

        self.toolchain = self.get_finalized_command("build_clib").toolchain

        if self.get_finalized_command("build_ext").inplace == 1:
            self.destination = os.path.join(
                os.path.dirname(__file__),
                *PACKAGE_NAME.split(".")  # For namespace and subpackages
            )
        else:
            self.destination = os.path.join(
                self.get_finalized_command("build").build_lib,
                *PACKAGE_NAME.split(".")  # For namespace and subpackages
            )

    def run(self):
        self.mkpath(self.destination)
        for lib in self._locate_shared_libraries(self.clib_bin_path):
            self.copy_file(lib, self.destination)

        for runtime, runtime_file in self.toolchain.runtime_file_deps():
            self.announce("Including {}".format(runtime))
            self.copy_file(runtime_file, self.destination)

    def _locate_shared_libraries(self, root):

        def filter_library_files(item: os.DirEntry):
            if not item.is_file():
                return False

            if not item.name.endswith(".dll"):
                return False
            return True

        for library_file in filter(filter_library_files, os.scandir(root)):
            yield library_file.path


class AbsCMakeToolchain(metaclass=abc.ABCMeta):

    def __init__(self, builder: build_ext) -> None:
        super().__init__()
        self.builder = builder

    @abc.abstractmethod
    def create_toolchain(self, output_cmake_file):
        """Generate a toolchain file"""

    def compiler_spawn(self, cmd):
        self.builder.compiler.spawn(cmd)

    @abc.abstractmethod
    def run_cmake_configure(self, ext):
        pass

    @abc.abstractmethod
    def run_cmake_build(self, ext):
        pass

    @abc.abstractmethod
    def run_cmake_install(self, ext):
        pass

    @abc.abstractmethod
    def get_linking_library_extension(self) -> str:
        pass

    @abc.abstractmethod
    def get_shared_library_filename(self, library_name):
        """What the file name should be called when it's compiled"""

    def runtime_file_deps(self) -> Iterable[Tuple[str, str]]:
        """files that need to be bundled along with the library built,

        Returns:
            Tuple. name of item, file name

        """
        for r in []:
            yield r

    def get_compiler(self):

        return self.builder.compiler


class MSVCToolChain(AbsCMakeToolchain):

    def get_compiler(self):
        self.builder.compiler = self.builder.shlib_compiler
        if not self.builder.compiler.initialized:
            self.builder.compiler.initialize()
        return self.builder.compiler

    def create_toolchain(self, output_cmake_file):
        if not self.builder.compiler.initialized:
            self.builder.compiler.initialize()

        # self.builder.mkpath(self.builder.build_temp)
        writer = CMakeToolchainWriter()
        writer.add_string(key="CMAKE_SYSTEM_NAME", value=platform.system())

        writer.add_string(
            key="CMAKE_SYSTEM_PROCESSOR", value=platform.machine())

        writer.add_string(
            key="CMAKE_HOST_SYSTEM_PROCESSOR", value=platform.machine())

        writer.add_path(key="CMAKE_C_COMPILER", value=self.builder.compiler.cc)
        writer.add_path(
            key="CMAKE_CXX_COMPILER", value=self.builder.compiler.cc)

        writer.add_path(key="CMAKE_LINKER", value=self.builder.compiler.linker)
        writer.add_path(
            key="CMAKE_RC_COMPILER", value=self.builder.compiler.rc)

        writer.add_path(
            key="CMAKE_MT_COMPILER", value=self.builder.compiler.mt)

        if platform.machine() == "AMD64":
            writer.add_string("CMAKE_LIBRARY_ARCHITECTURE", value="x64")
            writer.add_string("CMAKE_C_LIBRARY_ARCHTECTURE ", value="x64")
            writer.add_string("CMAKE_CXX_LIBRARY_ARCHTECTURE ", value="x64")

        writer.add_path(key="FETCHCONTENT_BASE_DIR",
                        value=os.path.abspath(
                            os.path.join(
                                self.builder.build_temp, "thirdparty")))

        if self.builder.nasm_exec:
            writer.add_path(key="CMAKE_ASM_NASM_COMPILER",
                            value=os.path.normcase(self.builder.nasm_exec))

        writer.write(output_cmake_file)
        with open(output_cmake_file, "a+") as wf:
            wf.write("\nset(ENV{PATH} \"")
            wf.write(os.path.dirname(
                self.builder.compiler.cc).replace("\\", "\\\\"))

            wf.write(";$ENV{PATH}\")\n")

    def compiler_spawn(self, cmd):
        old_env_vars = os.environ.copy()
        old_path = os.getenv("Path")
        try:
            os.environ["LIB"] = ";".join(self.builder.compiler.library_dirs)
            os.environ["INCLUDE"] = ";".join(
                self.builder.compiler.include_dirs)

            paths = []
            paths += old_path.split(";")
            if hasattr(self.builder.compiler, "_paths"):
                paths += self.builder.compiler._paths.split(";")
            new_value_path = ";".join(paths)
            os.environ["Path"] = new_value_path
            self.builder.compiler.spawn(cmd)
        finally:
            os.environ = old_env_vars
            os.environ["Path"] = old_path

    def run_cmake_configure(self, ext):
        install_prefix = os.path.abspath(ext.cmake_install_prefix)
        temp_output = os.path.abspath(self.builder.build_temp)

        configure_command = [
            self.builder.cmake_exec,
            f"-S{os.path.abspath(ext.cmake_source_dir)}",
            f"-B{os.path.abspath(ext.cmake_binary_dir)}",
            f"-DCMAKE_INSTALL_PREFIX={install_prefix}",
            # f"-DCMAKE_RUNTIME_OUTPUT_DIRECTORY={temp_output}",
        ]

        if self.builder.debug is not None:
            configure_command.append(
                f"-DCMAKE_RUNTIME_OUTPUT_DIRECTORY_DEBUG={temp_output}")
        else:
            configure_command.append(
                f"-DCMAKE_RUNTIME_OUTPUT_DIRECTORY_RELEASE={temp_output}")

        try:

            if self.builder.cmake_generator is not None:
                configure_command += ["-G", self.builder.cmake_generator]
            else:

                if 'MSC v.19' in platform.python_compiler():
                    configure_command += ["-T", "v140"]

            configure_command.insert(
                2, "-DCMAKE_TOOLCHAIN_FILE:FILEPATH=\"{}\"".format(
                    self.builder.toolchain_file))

        except KeyError as e:

            message = "No known build system generator for the current " \
                      "implementation of Python's compiler {}".format(e)

            raise CMakeException(message)

        for k, v in ext.cmake_args:
            # To delay any evaluation
            if callable(v):
                v = v()
            configure_command.append(f"{k}={v}")
        configure_command += [
            "-DCMAKE_BUILD_TYPE={}".format(self.builder.build_configuration),
        ]
        self.compiler_spawn(configure_command)

    def get_shared_library_filename(self, library_name):
        return f"{library_name}.dll"

    def runtime_file_deps(self) -> Iterable[Tuple[str, str]]:
        open_mp_library = find_library("VCOMP140")
        if open_mp_library is not None:
            yield "OpenMP runtime", open_mp_library

    def run_cmake_install(self, ext):
        install_command = [
            self.builder.cmake_exec,
            "--build", os.path.abspath(ext.cmake_binary_dir),
            "--config=", self.builder.build_configuration,
            "--target", "install"
        ]
        self.compiler_spawn(install_command)

    def run_cmake_build(self, ext):
        build_command = [
            self.builder.cmake_exec,
            "--build", os.path.abspath(ext.cmake_binary_dir),
            "--config", self.builder.build_configuration,
        ]
        if self.builder.parallel is not None:
            build_command += ["--parallel", str(self.builder.parallel)]

        self.compiler_spawn(build_command)

    def get_linking_library_extension(self) -> str:
        return ".lib"


class CMakeToolchainWriter:

    def __init__(self) -> None:
        super().__init__()
        self._cache_values = dict()

    def _generate_text(self) -> str:
        lines = []
        for k, v in self._cache_values.items():
            lines.append(f"set({k} \"{v}\")")
        return "\n".join(lines)

    def write(self, filename) -> None:
        with open(filename, "w") as wf:
            wf.write(self._generate_text())
            wf.write("\n")

    def add_path(self, key: str, value: str):
        self._cache_values[key] = value.replace("\\", "/")

    def add_string(self, key: str, value: str):
        self._cache_values[key] = value


class ClangToolChain(AbsCMakeToolchain):
    def create_toolchain(self, output_cmake_file):
        writer = CMakeToolchainWriter()
        writer.write(output_cmake_file)

    def run_cmake_configure(self, ext):
        pass

    def run_cmake_build(self, ext):
        pass

    def run_cmake_install(self, ext):
        pass

    def get_linking_library_extension(self) -> str:
        pass

    def get_shared_library_filename(self, library_name):
        return f"{library_name}.dylib"



class BuildCMakeClib(build_clib):
    user_options = [
        ("cmake-path=", None, "Path to CMake Executable"),
        ('nasm-exec=', None, "Location of the NASM executable. "
                             "Defaults of NASM located on path"),
        ('source-archive-path=', None, "Location to save archive deps"),
        ('cmake-generator=', None, "Build system CMake generates."),

    ]

    def find_dep_libs_from_cmake(self, target_json, remove_prefix):
        if target_json is not None:
            with open(target_json) as f:
                t = json.load(f)
                link = t.get("link")
                if link is not  None:
                    cf = link['commandFragments']
                    deps = map(lambda i: os.path.split(i)[-1],
                               map(lambda z: z['fragment'],
                                   filter(lambda fragment: fragment['role'] == "libraries", cf)
                                   )
                               )

                    splitted = []
                    for d in deps:
                        splitted += d.split(" ")
                    prefix_removed = []
                    for d in splitted:
                        if d.startswith("-l"):
                            prefix_removed.append(d.replace("-l", ""))
                        else:
                            prefix_removed.append(d)

                    deps = map(lambda i: os.path.splitext(i)[0], prefix_removed)

                    if remove_prefix:
                        return list(map(lambda i: i.replace("lib","") if i.startswith("lib") else i, deps))
                    return list(deps)
            return []
        return None
    def find_target(self, target_name: str, build_type=None) -> Optional[str]:
        libraries = self.get_finalized_command("build_clib").libraries
        for l in libraries:
            if l[0] == target_name:
                lib = l
                break
        else:
            raise AttributeError("{} Not found".format(target_name))
        cmake_api_dir = os.path.join(lib[1]['build path'],  ".cmake", "api", "v1")

        cmake_api_reply_dir = os.path.join(cmake_api_dir, "reply")
        if not os.path.exists(cmake_api_dir):
            return None

        for f in os.scandir(cmake_api_reply_dir):
            if f"target-{target_name}-" not in f.name:
                continue
            if build_type is not None:
                if build_type not in f.name:
                    continue
            return f.path
        return None

    def __init__(self, dist):
        super().__init__(dist)
        if "MSC" in platform.python_compiler():
            self.toolchain = MSVCToolChain(self)

        elif "Clang" in platform.python_compiler():
            self.toolchain = ClangToolChain(self)
        self.cmake_api_dir = None
        self.build_configuration = "release"

    def initialize_options(self):
        super().initialize_options()
        self.cmake_path = shutil.which("cmake")
        self.nasm_exec = shutil.which("nasm")
        self.source_archive_path = None
        self.source_path_root = None

        if shutil.which("ninja") is not None:
            self.cmake_generator = "Ninja"
        else:
            self.cmake_generator = None

    # def build_libraries(self, libraries):
    #     super().build_libraries(libraries)

    def finalize_options(self):
        super().finalize_options()
        if not os.path.exists(str(self.cmake_path)):
            self.warn( "CMake required to build clibs")

        self.source_archive_path = os.path.join(
                self.build_temp,
                "dependencies",
                "source",
                "archives"
            )

        self.source_path_root = os.path.join(
                self.build_temp,
                "dependencies",
                "source",
            )

        if self.libraries is None:
            return

        for lib_name, library in self.libraries:
            build_path = os.path.join(self.build_temp,
                                      "dependencies",
                                      "build",
                                      lib_name)

            library["build path"] = build_path
            library["install prefix"] = self.build_clib

    def finalize_library_options(self, libraries):
        for lib_name, library in libraries:
            assert os.path.exists(library['source path'])

    def write_toolchain_file(self, toolchain_file):
        self.mkpath(self.build_temp)
        # self.toolchain.create_toolchain(toolchain_file)
        # self.announce(
        #     "Generated CMake Toolchain file: {}".format(toolchain_file))

    def run(self):
        if not self.libraries:
            return

            # Yech -- this is cut 'n pasted from build_ext.py!
        from distutils.ccompiler import new_compiler
        self.compiler = new_compiler(compiler=self.compiler,
                                     dry_run=self.dry_run,
                                     force=self.force)
        customize_compiler(self.compiler)

        if self.include_dirs is not None:
            self.compiler.set_include_dirs(self.include_dirs)
        if self.define is not None:
            # 'define' option is a list of (name,value) tuples
            for (name, value) in self.define:
                self.compiler.define_macro(name, value)
        if self.undef is not None:
            for macro in self.undef:
                self.compiler.undefine_macro(macro)

        # for library in self.libraries:
        #     self.build_extension(library)

        self.get_deps_source(self.libraries)
        self.finalize_library_options(self.libraries)
        self.build_libraries(self.libraries)

        # build_ext_cmd = self.get_finalized_command("build_ext")
        # print("")


        # super().run()

    def download_source_archive(self, url, lib_name):
        source_archive_file_extension = \
            self._get_file_extension(url)

        # if url.endswith(source_archive_file_extension):
        src_archive_dst = \
            os.path.join(self.source_archive_path,
                         "".join([lib_name,
                                  source_archive_file_extension])
                         )

        if not os.path.exists(src_archive_dst):
            self.announce(
                "Fetching source code for {}".format(lib_name),
                level=4)

            self.download_file(url, src_archive_dst)
        return src_archive_dst

    @staticmethod
    def download_file(url, save_as):
        dir_name = os.path.dirname(save_as)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        with urllib.request.urlopen(url) as response:
            with open(save_as, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
                assert response.getcode() == 200

    def get_deps_source(self, libraries):

        self.mkpath(self.source_archive_path)

        for lib_name, lib in libraries:
            lib_source_url = lib['url']

            lib["source archive"] = self.download_source_archive(
                lib_source_url, lib_name)
            source_dest = os.path.join(self.source_path_root, lib_name)

            if not os.path.exists(source_dest):
                self.announce("Extracting {}".format(lib_name), level=4)
                self._extract_source(lib["source archive"], source_dest)

            lib["source path"] = os.path.dirname(
                self._find_root_cmake(source_dest))

    def _find_root_cmake(self, path):
        """Locate the first file name CMakeLists.txt in a directory"""

        for root, dirs, files in os.walk(path):
            for file_name in files:
                if file_name == "CMakeLists.txt":
                    return os.path.join(root, file_name)
        raise FileNotFoundError("No CMakeLists.txt located")

    def _extract_source(self, source_archive, dst):
        if source_archive.endswith(".tar.gz"):
            with tarfile.open(source_archive, "r:gz") as archive:
                for compressed_file in archive:
                    if not os.path.exists(
                            os.path.join(dst, compressed_file.name)):
                        self.announce(
                            "Extracting {}".format(compressed_file.name))

                        archive.extract(compressed_file, dst)
        elif source_archive.endswith(".zip"):
            with zipfile.ZipFile(source_archive) as archive:
                for compressed_file in archive.namelist():
                    self.announce("Extracting {}".format(compressed_file))
                    archive.extract(compressed_file, dst)
        else:
            raise Exception(
                "Unknown format to extract {}".format(source_archive))

    def _check_install_manifest(self, path):
        manifest_document = os.path.join(path, "install_manifest.txt")
        with open(manifest_document, "r") as f:
            for line in f.readlines():
                yield line.strip()

    @staticmethod
    def _get_file_extension(url) -> str:
        if url.endswith(".tar.gz"):
            return ".tar.gz"
        if url.endswith(".zip"):
            return ".zip"
        return os.path.splitext(url)[0]

    def _needs_to_build(self, library) -> bool:
        install_manifest = library.get('install manifest', [])
        if len(install_manifest) <= 0:
            return True

        located_all_files = True

        for install_file in install_manifest:
            if not os.path.exists(install_file):
                located_all_files = False

        if located_all_files is False:
            return True
        return False

    def build_libraries(self, libraries):
        super().build_libraries([])
        # self.initalize_cmake_toolchain()

        build_command = self.get_finalized_command("build")

        package_path = os.path.abspath(
            os.path.join(
                build_command.build_lib,
                *PACKAGE_NAME.split(".")  # For namespace and subpackages
            )
        )
        # if not self.compiler.initialized:
        #     self.compiler.initialize()
        if self.compiler.compiler_type == "msvc":
            if not self.compiler.initialized:
                self.compiler.initialize()

        for lib_name, lib in libraries:
            cmake_api_dir = os.path.join(lib['build path'], ".cmake", "api", "v1")
            self.mkpath(os.path.join(cmake_api_dir, "query"))
            with open(os.path.join(cmake_api_dir, "query", "codemodel-v2"), "w"):
                pass
            self._resolve_cmake_args(lib)

            build_path = os.path.abspath(lib['build path'])
            lib['install manifest'] = []
            try:
                for file_already_installed in \
                        self._check_install_manifest(lib['build path']):
                    lib['install manifest'].append(file_already_installed)
            except FileNotFoundError:
                pass

            self.build_library(lib, build_path, package_path)

            #  Build
            if not self._needs_to_build(lib):
                continue

            self.announce("Building {}".format(lib_name))
            build_path = os.path.abspath(lib["build path"])
            build_command = [
                        self.cmake_path,
                        "--build", build_path,
                        "--config", self.build_configuration,
                    ]
            build_cmd = self.get_finalized_command("build")

            if build_cmd.parallel is not None:
                build_command += ["--parallel", str(build_cmd.parallel)]

            # if not self.compiler.initialized:
            #     self.compiler.initialize()

            self.compiler.spawn(build_command)

            install_command = [
                self.cmake_path,
                "--build", build_path,
                "--config", self.build_configuration,
                "--target", "install"

            ]

            self.spawn(install_command)

    def build_library(self, lib, build_path, runtime_output_path):
        # super(BuildCMakeClib, self).build_library()

        if not os.path.exists(os.path.join(build_path, "CMakeCache.txt")):
            install_prefix = os.path.abspath(lib["install prefix"])

            configure_command = [
                self.cmake_path,
                "-S", lib["source path"],
                "-B", lib["build path"],
                # f"-DCMAKE_RUNTIME_OUTPUT_DIRECTORY:PATH={runtime_output_path}",
                # f"-DCMAKE_RUNTIME_OUTPUT_DIRECTORY_RELEASE:PATH={runtime_output_path}",
                f"-DCMAKE_INSTALL_PREFIX:PATH={os.path.abspath(self.build_clib)}",
                # f"-DCMAKE_TOOLCHAIN_FILE:FILEPATH={self.toolchain_file}",
                f"-DCMAKE_BUILD_TYPE={self.build_configuration}"
            ]

            for k, v in lib.get("cmake_args", []):
                configure_command.append(f"{k}={v}")

            if self.cmake_generator is not None:
                configure_command += ["-G", self.cmake_generator]

            # self.mkpath(os.path.join(self.cmake_api_dir, "query"))
            # with open(os.path.join(self.cmake_api_dir, "query", "codemodel-v2"), "w"):
            #     pass

            self.compiler.spawn(configure_command)
            # self.toolchain.compiler_spawn(configure_command)

    def initalize_cmake_toolchain(self):
        self.toolchain_file = os.path.abspath(
            os.path.join(self.build_temp, "toolchain.cmake"))
        if os.path.exists(self.toolchain_file):
            self.announce("Using CMake Toolchain file {}.".format(
                self.toolchain_file), 2)

        else:
            self.announce("Generating CMake Toolchain file {}.".format(
                self.toolchain_file))

            self.write_toolchain_file(self.toolchain_file)

    def _resolve_cmake_args(self, library):
        cmake_args = library.get("cmake_args", [])
        resolved = []
        for k, v in cmake_args:
            # To delay any evaluation
            if callable(v):
                v = v()
            resolved.append(
                (k, v)
            )
        library["cmake_args"] = resolved

class BuildOpenJpegClib(build_clib):
    user_options = [
        ("cmake-path=", None, "Path to CMake Executable"),
        ('nasm-exec=', None, "Location of the NASM executable. "
                             "Defaults of NASM located on path"),
        ('source-archive-path=', None, "Location to save archive deps"),
        ('cmake-generator=', None, "Build system CMake generates."),
    ]
    def __init__(self, dist):
        super().__init__(dist)
        self.extra_cmake_options = []


# class BuildPybind11Ext(build_ext):
#     DEPS_REGEX = \
#         r'(?<=(Image has the following dependencies:(\n){2}))((?<=\s).*\.dll\n)*'
#
#     def find_pybind11_include(self):
#         for root, dirs, files in os.walk(self.pybind11_source_path):
#             for dirname in dirs:
#                 if dirname == "include":
#                     return os.path.join(root, dirname)
#
#     def initialize_options(self):
#         super().initialize_options()
#         self.pybind11_source_path = None
#         self.pybind11_include_path = None
#
#     def find_openjpeg_lib_path(self):
#         matching_names = [
#             "libopenjp2.a",
#             "openjp2.lib",
#         ]
#         clib_cmd = self.get_finalized_command("build_clib")
#         for root, dirs, files in os.walk(clib_cmd.build_clib):
#             for f in files:
#                 if f in matching_names:
#                     return root
#         return None
#
#     def find_openjpeg_header_path(self):
#         clib_cmd = self.get_finalized_command("build_clib")
#         for root, dirs, files in os.walk(os.path.join(clib_cmd.build_clib, "include")):
#             for f in files:
#                 if f == "openjpeg.h":
#                     return root
#         return None
#
#     def build_extension(self, ext):
#         missing = self.find_missing_libraries(ext)
#         build_clib_cmd = self.get_finalized_command("build_clib")
#
#
#         if len(missing) > 0:
#             self.announce(f"missing required deps [{', '.join(missing)}]. "
#                           f"Trying to build them", 5)
#             self.run_command("build_clib")
#
#             ext.include_dirs.append(os.path.abspath(os.path.join(build_clib_cmd.build_clib, "include")))
#         opj2_include_dir = self.find_openjpeg_header_path()
#         if opj2_include_dir is not None:
#             ext.include_dirs.insert(0, opj2_include_dir)
#         opj2_lib_dir = self.find_openjpeg_lib_path()
#         if opj2_lib_dir is not None:
#             ext.library_dirs.insert(0, opj2_lib_dir)
#
#         if self.compiler.compiler_type == "unix":
#             ext.extra_compile_args.append("-std=c++14")
#         else:
#             ext.extra_compile_args.append("/std:c++14")
#         new_libs = []
#         for lib in ext.libraries:
#             if self.compiler.compiler_type != "unix":
#                 if self.debug is None:
#                     build_configuration = "Release"
#                 else:
#                     build_configuration = "Debug"
#             else:
#                 build_configuration = None
#             t = build_clib_cmd.find_target(lib, build_configuration)
#             if t is not None:
#                 deps = build_clib_cmd.find_dep_libs_from_cmake(t, remove_prefix=self.compiler.compiler_type == "unix")
#                 if deps is not None:
#                     if lib in deps:
#                         deps.remove(lib)
#                     new_libs += deps
#
#         ext.libraries += new_libs
#         super().build_extension(ext)
#
#     def find_missing_libraries(self, ext):
#         missing_libs = []
#         for lib in ext.libraries:
#             if self.compiler.find_library_file(self.library_dirs, lib) is None:
#                 missing_libs.append(lib)
#         return missing_libs
#
#     def find_deps(self, lib):
#
#         for path in os.environ['path'].split(";"):
#             for f in os.scandir(path):
#                 if f.name.lower() == lib.lower():
#                     return f.path
#     def run(self):
#         self.get_pybind11()
#         self.pybind11_include_path = self.find_pybind11_include()
#         self.include_dirs.append(os.path.abspath(self.pybind11_include_path))
#
#         clib_cmd = self.get_finalized_command("build_clib")
#
#
#         # for lib_name, library in clib_cmd.libraries:
#         #     install_prefix = library['install prefix']
#         #
#         #     lib_include = os.path.join(install_prefix, "include")
#         #     lib_libdir = os.path.join(install_prefix, "lib")
#         #
#         #     if lib_include not in self.include_dirs and os.path.exists(lib_include):
#         #         self.include_dirs.append(lib_include)
#         #
#         #     if lib_libdir not in self.library_dirs and os.path.exists(lib_libdir):
#         #         self.library_dirs.append(lib_libdir)
#
#
#         super().run()
#         for e in self.extensions:
#             dll_file = \
#                 os.path.abspath(os.path.join(self.build_lib, self.get_ext_filename(e.name)))
#             assert os.path.exists(dll_file), "Unable to located {}".format(dll_file)
#             assert os.path.exists(self.build_temp), "Unable to located {}".format(self.build_temp)
#             output_file = os.path.abspath(os.path.join(self.build_temp, f'{e.name}.dependents'))
#             if self.compiler.compiler_type != "unix":
#                 if not self.compiler.initialized:
#                     self.compiler.initialize()
#                 self.compiler.spawn(
#                     [
#                         'dumpbin',
#                         '/dependents',
#                         dll_file,
#                         f'/out:{output_file}'
#                     ]
#                 )
#                 deps = self.parse_dumpbin_deps(dump_file=output_file)
#                 deps = self.remove_system_dlls(deps)
#                 dest = os.path.dirname(dll_file)
#                 for dep in deps:
#                     dll = self.find_deps(dep)
#                     if dll is not None:
#                         shutil.copy(dll, dest)
#                     else:
#                         self.announce("Unable to locate deps for {}".format(dep), level=2)
#
#         # for ext in self.extensions:
#         #     if self.compiler.compiler_type == "unix":
#         #         ext.extra_compile_args.append("-std=c++14")
#         #     else:
#         #         ext.extra_compile_args.append("/std:c++14")
#             # self.compiler.
#         # if self.inplace:
#         #     self.run_command("package_clib")
#     @staticmethod
#     def remove_system_dlls(dlls):
#         non_system_dlls = []
#         for dll in dlls:
#             if dll.startswith("api-ms-win-crt"):
#                 continue
#
#             if dll.startswith("python"):
#                 continue
#
#             if dll == "KERNEL32.dll":
#                 continue
#             non_system_dlls.append(dll)
#         return non_system_dlls
#
#     @classmethod
#     def parse_dumpbin_deps(cls, dump_file) -> List[str]:
#
#         dlls = []
#         dep_regex = re.compile(cls.DEPS_REGEX)
#
#         with open(dump_file) as f:
#             d = dep_regex.search(f.read())
#             for x in d.group(0).split("\n"):
#                 if x.strip() == "":
#                     continue
#                 dll = x.strip()
#                 dlls.append(dll)
#         return dlls
#
#     def finalize_options(self):
#         super().finalize_options()
#         clib_command = self.get_finalized_command("build_clib")
#         self.archive_dest = clib_command.source_archive_path
#
#         self.pybind11_source_path = \
#             os.path.join(clib_command.source_path_root,
#                          "pybind11"
#                          )
#
#     def get_pybind11(self):
#
#         self.mkpath(self.archive_dest)
#         pybind11_archive_dest = os.path.join(self.archive_dest,
#                                              "pybind11.tar.gz")
#
#         if not os.path.exists(pybind11_archive_dest):
#             self.announce("Downloading pybind11", level=4)
#             request.urlretrieve(PYBIND11_URL, filename=pybind11_archive_dest)
#
#         self.mkpath(self.pybind11_source_path)
#
#         with tarfile.open(pybind11_archive_dest, "r") as pb_archive:
#             self.announce("Extracting pybind11 source")
#             for f in pb_archive:
#                 dest = os.path.join(self.pybind11_source_path, f.name)
#                 if os.path.exists(dest):
#                     continue
#                 pb_archive.extract(f, self.pybind11_source_path)
#                 self.announce("Extracted {}".format(f.name), level=3)

PYBIND11_DEFAULT_URL = \
    "https://github.com/pybind/pybind11/archive/v2.5.0.tar.gz"
class BuildPybind11Extension(build_ext):
    user_options = build_ext.user_options + [
        ('pybind11-url=', None,
         "Url to download Pybind11")
    ]
    DEPS_REGEX = \
        r'(?<=(Image has the following dependencies:(\n){2}))((?<=\s).*\.dll\n)*'

    @classmethod
    def parse_dumpbin_deps(cls, dump_file) -> List[str]:

        dlls = []
        dep_regex = re.compile(cls.DEPS_REGEX)

        with open(dump_file) as f:
            d = dep_regex.search(f.read())
            for x in d.group(0).split("\n"):
                if x.strip() == "":
                    continue
                dll = x.strip()
                dlls.append(dll)
        return dlls

    def initialize_options(self):
        super().initialize_options()
        self.pybind11_url = None

    def finalize_options(self):
        self.pybind11_url = self.pybind11_url or PYBIND11_DEFAULT_URL
        super().finalize_options()

    @staticmethod
    def remove_system_dlls(dlls):
        non_system_dlls = []
        for dll in dlls:
            if dll.startswith("api-ms-win-crt"):
                continue

            if dll.startswith("python"):
                continue

            if dll == "KERNEL32.dll":
                continue
            non_system_dlls.append(dll)
        return non_system_dlls

    def find_openjpeg_lib_path(self, starting_path):
        matching_names = [
            "libopenjp2.a",
            "openjp2.lib",
        ]
        # clib_cmd = self.get_finalized_command("build_clib")
        for root, dirs, files in os.walk(starting_path):
            for f in files:
                if f in matching_names:
                    return root
        return None

    def find_openjpeg_header_path(self, starting_path):
        # clib_cmd = self.get_finalized_command("build_clib")
        for root, dirs, files in os.walk(starting_path):
            for f in files:
                if f == "openjpeg.h":
                    return root
        return None

    def run(self):
        # self.include_dirs.insert(0, os.path.abspath(os.path.join(self.build_temp, "include")))
        # self.library_dirs.insert(0, os.path.abspath(os.path.join(self.build_temp, "lib")))
        pybind11_include_path = self.get_pybind11_include_path()
        if pybind11_include_path is not None:
            self.include_dirs.insert(0, pybind11_include_path)
        self.run_command("build_conan")
        # build_conan_cmd = self.get_finalized_command("build_conan")
        # print("he")
        # build_clib_cmd = self.get_finalized_command("build_clib")
        # openjpeg_include_path = self.find_openjpeg_header_path(os.path.abspath(os.path.join(build_clib_cmd.build_clib, "include")))
        # if openjpeg_include_path is not None:
        #     self.include_dirs.insert(0, openjpeg_include_path)

        #     m = self.find_missing_libraries(e)
        #     pass
        super().run()

        for e in self.extensions:
            dll_name = \
                os.path.join(self.build_lib, self.get_ext_filename(e.name))
            search_dirs = self.get_library_paths()
            self.resolve_shared_library(dll_name, search_dirs)
            # dll_name = \
            #     os.path.join(self.build_lib, self.get_ext_filename(e.name))
            #
            # output_file = os.path.join(self.build_temp, f'{os.path.splitext(e.name)[0].replace(".", "-")}.dependents')
            # if self.compiler.compiler_type != "unix":
            #     if not self.compiler.initialized:
            #         self.compiler.initialize()
            #     dll_file = \
            #         os.path.abspath(os.path.join(self.build_lib, self.get_ext_filename(e.name)))
            #
            #     assert os.path.exists(dll_file), "Unable to located {}".format(dll_file)
            #     assert os.path.exists(self.build_temp), "Unable to located {}".format(self.build_temp)
            #     self.compiler.spawn(
            #         [
            #             'dumpbin',
            #             '/DEPENDENTS',
            #             f'/OUT:{output_file}',
            #             dll_name,
            #         ]
            #     )
            #     deps = self.parse_dumpbin_deps(dump_file=output_file)
            #     deps = self.remove_system_dlls(deps)
            #     dest = os.path.dirname(dll_name)
            #     self.announce("Copying dependencies to {}".format(dest))
            #     for dep in deps:
            #         dll = self.find_deps(dep)
            #         if dll is not None:
            #             self.copy_file(dll, dest)
            #             if self.inplace:
            #                 self.copy_file(dll, os.path.dirname(self.get_ext_filename(e.name)))
            #         else:
            #             print("Unable to locate deps for {}".format(dep), file=sys.stderr)

    def resolve_shared_library(self, dll_name, search_paths=None):
        dll_dumper = get_so_handler(dll_name, self)
        dll_dumper.set_compiler(self.compiler)
        try:
            dll_dumper.resolve(search_paths)
        except FileNotFoundError:
            if search_paths is not None:
                self.announce(
                    "Error: Not all required shared libraries were resolved. "
                    "Searched:\n{}".format('\n'.join(search_paths)), 5
                )
            raise
    def get_library_paths(self):
        search_paths = []
        library_search_paths = \
            self.compiler.library_dirs + \
            self.compiler.runtime_library_dirs + \
            self.library_dirs + \
            self._get_path_dirs()
        search_paths.append(self.build_temp)

        for lib_path in library_search_paths:
            if not os.path.exists(lib_path):
                continue
            if lib_path in search_paths:
                continue
            search_paths.append(lib_path)

        return search_paths

    def find_deps(self, lib,  search_paths=None):
        search_paths = search_paths or os.environ['path'].split(";")

        for path in search_paths:
            if not os.path.exists(path):
                self.announce(f"Skipping invalid path: {path}", 5)
                continue
            for f in os.scandir(path):
                if f.name.lower() == lib.lower():
                    return f.path

    # def find_deps(self, lib):
    #     build_clib_cmd = self.get_finalized_command("build_clib")
    #     paths = os.environ['path'].split(";")
    #     paths.insert(0, os.path.join(build_clib_cmd.build_clib, "bin"))
    #
    #     for path in paths:
    #         if not os.path.exists(path):
    #             continue
    #         for f in os.scandir(path):
    #             if f.name.lower() == lib.lower():
    #                 return f.path
    #
    #     return None
    def find_header_file_path(self, include_dirs: List[str], headers:List[str]) -> Optional[str]:
        for include_dir in include_dirs:
            for h in headers:
                if not os.path.exists(os.path.join(include_dir, h)):
                    continue
                return include_dir
        return None
            # for i in os.scandir(include_dir):


    def find_missing_libraries(self, ext):
        system_lib_dirs = [
            "/usr/local/lib",
            os.path.join(sys.base_prefix, "libs")
        ]
        missing_libs = []

        library_search_paths = \
            self.library_dirs + ext.library_dirs + system_lib_dirs

        for lib in ext.libraries:
            if self.compiler.find_library_file(library_search_paths, lib) \
                    is None:

                missing_libs.append(lib)
        return missing_libs
    # def find_missing_libraries(self, ext):
    #     missing_libs = []
    #     build_clib_cmd = self.get_finalized_command("build_clib")
    #
    #     for lib in ext.libraries:
    #         expected_header_files = []
    #         for libname, lib_data in build_clib_cmd.libraries:
    #             if libname == lib:
    #                 expected_header_files += lib_data['expected_headers']
    #         if self.compiler.find_library_file(self.library_dirs, lib) is None:
    #             missing_libs.append(lib)
    #             continue
    #
    #         if self.find_header_file_path(self.include_dirs, expected_header_files) is None:
    #             missing_libs.append(lib)
    #
    #     return missing_libs

    def build_extension(self, ext):
        missing = self.find_missing_libraries(ext)
        if self.compiler.compiler_type == "unix":
            ext.extra_compile_args.append("-std=c++14")
        else:
            ext.extra_compile_args.append("/std:c++14")

            # self.compiler.add_library("shell32")

            ext.libraries.append("shell32")

        if len(missing) > 0:
            self.announce(f"missing required deps [{', '.join(missing)}]. "
                          f"Trying to build them", 5)
            self.run_command("build_conan")
            missing = self.find_missing_libraries(ext)
            if len(missing) > 0:
                raise FileNotFoundError(
                    "Still Missing missing required deps [{}]".format(
                        ', '.join(missing)))

        new_libs = []
        ext.libraries += new_libs

        super().build_extension(ext)
        # if len(missing) > 0:
        #     self.announce(f"missing required deps [{', '.join(missing)}]. "
        #                   f"Trying to build them", 5)
        #     self.run_command("build_conan")
        #     missing = self.find_missing_libraries(ext)
        #     if len(missing) > 0:
        #         raise FileNotFoundError(
        #             "Still Missing missing required deps [{}]".format(
        #                 ', '.join(missing)))
        #     # self.run_command("build_clib")
        #     # build_clib_cmd = self.get_finalized_command("build_clib")
        #     # open_jpeg_include_path = self.find_openjpeg_header_path(os.path.join(build_clib_cmd.build_clib, "include"))
        #     build_conan_cmd = self.get_finalized_command("build_conan")
        #     #
        #     # if open_jpeg_include_path is not None:
        #     #     ext.include_dirs.append(os.path.abspath(open_jpeg_include_path))
        #     #
        #     # open_jpeg_library_path = self.find_openjpeg_lib_path(os.path.abspath(os.path.join(build_clib_cmd.build_clib, "lib")))
        #     # if open_jpeg_library_path is not None:
        #     #     ext.library_dirs.append(os.path.abspath(open_jpeg_library_path))

        # super().build_extension(ext)
    def _get_path_dirs(self):
        if platform.system() == "Windows":
            paths = os.environ['path'].split(";")
        else:
            paths = os.environ['PATH'].split(":")
        return [path for path in paths if os.path.exists(path)]

    def get_pybind11_include_path(self):
        pybind11_archive_filename = os.path.split(self.pybind11_url)[1]

        pybind11_archive_downloaded = os.path.join(self.build_temp,
                                                   pybind11_archive_filename)

        pybind11_source = os.path.join(self.build_temp, "pybind11")
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)

        if not os.path.exists(pybind11_source):
            if not os.path.exists(pybind11_archive_downloaded):
                self.announce("Downloading pybind11", level=5)
                request.urlretrieve(
                    self.pybind11_url, filename=pybind11_archive_downloaded)
                self.announce("pybind11 Downloaded", level=5)
            with tarfile.open(pybind11_archive_downloaded, "r") as tf:
                for f in tf:
                    if "pybind11.h" in f.name:
                        self.announce("Extract pybind11.h to include path")

                    tf.extract(f, pybind11_source)
        for root, dirs, files in os.walk(pybind11_source):
            for f in files:
                if f == "pybind11.h":
                    return os.path.abspath(os.path.relpath(
                        os.path.join(root, ".."),
                        os.path.dirname(__file__)
                    ))


# class BuildOpenJp2Extension(BuildPybind11Ext):
#
#     def links_to_dynamic(self, ext):
#         return super().links_to_dynamic(ext)
#
#     def run(self):
#         clib_command = self.get_finalized_command("build_clib")
#
#         self.include_dirs.insert(
#             0, os.path.join(
#                 clib_command.build_clib,
#                 "include",
#                 "openjpeg-2.3"
#                 )
#         )
#         self.library_dirs.insert(
#             0, os.path.join(clib_command.build_clib, "lib"))
#
#         super().run()
#         extension = os.path.join(self.build_lib, self.get_ext_filename(self.extensions[0].name))
#         bin_dir = os.path.join(clib_command.build_temp, "bin")
#         fixup_command = [
#             clib_command.cmake_path,
#             f'-DPYTHON_CEXTENSION={extension}',
#             f'-DDIRECTORIES={bin_dir}',
#             "-P",
#             "cmake/fixup.cmake",
#         ]
#         # if not self.compiler.initialized:
#         #     self.compiler.initialize()
#         self.compiler.spawn(fixup_command)
#



class AbsSoHandler(abc.ABC):
    def __init__(self, library_file, context):
        self.library_file = library_file
        self._compiler = None
        self.context = context

    def set_compiler(self, compiler):
        self._compiler = compiler

    @classmethod
    def is_system_file(cls, filename) -> bool:
        return False

    @abc.abstractmethod
    def get_deps(self) -> List[str]:
        pass

    def resolve(self, search_paths=None) -> None:
        dest = os.path.dirname(self.library_file)
        for dep in filter(lambda x: not self.is_system_file(x),
                          self.get_deps()):

            if os.path.exists(os.path.join(dest, dep)):
                continue
            if search_paths is None:
                if platform.system() == "Windows":
                    search_paths = self.context.compiler.library_dirs + \
                                   os.environ['path'].split(";")
                else:
                    search_paths = self.context.compiler.library_dirs + \
                                   os.environ['PATH'].split(":")

            dll = self.context.find_deps(dep, search_paths)
            if dll is None:
                raise FileNotFoundError(f"Unable to locate {dep} for "
                                        f"{self.library_file}")
            if not self.is_system_file(dll):
                type(self)(dll, self.context).resolve(search_paths)


class DllHandlerStrategy(AbsSoHandler):
    def __init__(self, library_file, context):
        super().__init__(library_file, context)
        self._compiler = None

    def resolve(self, search_paths=None) -> None:
        dest = os.path.dirname(self.library_file)
        for dep_name in self.get_deps():
            if self.is_system_file(dep_name):
                continue
            dep = self.find_lib(dep_name, search_paths=search_paths)
            if not dep:
                raise FileNotFoundError(
                    f"Unable to locate {dep_name} required by "
                    f"{self.library_file}")

            new_dll = os.path.join(dest, os.path.split(dep)[-1])
            if os.path.exists(new_dll):
                continue
            self.context.copy_file(dep, new_dll)
            DllHandlerStrategy(new_dll, self.context).resolve(search_paths)

    def find_lib(self, lib, search_paths=None):
        if search_paths is None:
            search_paths = os.environ['path'].split(";")

        for path in search_paths:
            if not os.path.exists(path):
                self.context.announce(f"Skipping invalid path: {path}", 5)
                continue
            for f in os.scandir(path):
                if f.name.lower() == lib.lower():
                    return f.path

    @classmethod
    def is_system_file(cls, filename: str) -> bool:
        system_libs = [
            i for i in os.listdir(r"c:\Windows\System32") if i.endswith(".dll")
        ]

        if filename in system_libs:
            return True

        if "api-ms-win-crt" in filename:
            return True

        if filename.startswith("python"):
            return True
        if filename == "KERNEL32.dll":
            return True
        return False

    def get_deps(self) -> List[str]:
        if not self.context.compiler.initialized:
            self.context.compiler.initialize()
        so_name = os.path.split(self.library_file)[-1]
        with tempfile.TemporaryDirectory() as td:
            output_file = os.path.join(td, f'{so_name}.dependents')
            dumpbin = \
                shutil.which("dumpbin",
                             path=os.path.dirname(self.context.compiler.cc))

            self.context.compiler.spawn(
                [
                    dumpbin,
                    '/dependents',
                    os.path.abspath(self.library_file),
                    f'/out:{output_file}'
                ]
            )
            return BuildPybind11Extension.parse_dumpbin_deps(dump_file=output_file)

class ConanBuildInfoParser:
    def __init__(self, fp):
        self._fp = fp

    def parse(self) -> Dict[str, List[str]]:
        data = dict()
        for subject_chunk in self.iter_subject_chunk():
            subject_title = subject_chunk[0][1:-1]

            data[subject_title] = subject_chunk[1:]
        return data

    def iter_subject_chunk(self) -> Iterable[Any]:
        buffer = []
        for line in self._fp:
            line = line.strip()
            if len(line) == 0:
                continue
            if line.startswith("[") and line.endswith("]") and len(buffer) > 0:
                yield buffer
                buffer.clear()
            buffer.append(line)
        yield buffer
        buffer.clear()
class ConanImportManifestParser:
    def __init__(self, fp):
        self._fp = fp

    def parse(self) -> List[str]:
        libs = set()
        for line in self._fp:
            t = line.split()[0].strip(":\n")
            if os.path.exists(t):
                libs.add(t)
        return list(libs)

class AbsSoHandler(abc.ABC):
    def __init__(self, library_file, context):
        self.library_file = library_file
        self._compiler = None
        self.context = context

    def set_compiler(self, compiler):
        self._compiler = compiler

    @classmethod
    def is_system_file(cls, filename) -> bool:
        return False

    @abc.abstractmethod
    def get_deps(self) -> List[str]:
        pass

    def resolve(self, search_paths=None) -> None:
        dest = os.path.dirname(self.library_file)
        for dep in filter(lambda x: not self.is_system_file(x),
                          self.get_deps()):

            if os.path.exists(os.path.join(dest, dep)):
                continue
            if search_paths is None:
                if platform.system() == "Windows":
                    search_paths = self.context.compiler.library_dirs + \
                                   os.environ['path'].split(";")
                else:
                    search_paths = self.context.compiler.library_dirs + \
                                   os.environ['PATH'].split(":")

            dll = self.context.find_deps(dep, search_paths)
            if dll is None:
                raise FileNotFoundError(f"Unable to locate {dep} for "
                                        f"{self.library_file}")
            if not self.is_system_file(dll):
                type(self)(dll, self.context).resolve(search_paths)


class NullHandlerStrategy(AbsSoHandler):

    def get_deps(self) -> List[str]:
        return []


class MacholibStrategy(AbsSoHandler):
    _system_files = []

    @classmethod
    def get_system_files(cls):
        if len(cls._system_files) == 0:
            cls._system_files = os.listdir("/usr/lib")
        return cls._system_files

    def get_deps(self) -> List[str]:

        libs = set()
        for header in MachO.MachO(self.library_file).headers:
            for _idx, _name, other in header.walkRelocatables():
                libs.add(os.path.split(other)[-1])
        return list(libs)

    @classmethod
    def is_system_file(cls, filename) -> bool:
        if filename in [
            "libsystem_malloc.dylib"
        ]:
            return True

        if filename in cls.get_system_files():
            return True
        return False

    def resolve(self, search_path=None) -> None:
        if self.is_system_file(os.path.split(self.library_file)[1]):
            return

        d = MachOStandalone.MachOStandalone(
            os.path.abspath(os.path.dirname(self.library_file)))

        d.dest = os.path.abspath(os.path.dirname(self.library_file))
        libraries = []
        for dep in self.get_deps():
            if self.is_system_file(dep):
                continue
            found_dep = self.context.find_deps(dep, search_path)
            c_dep = d.copy_dylib(found_dep)
            dep_file = d.mm.locate(c_dep)
            if dep_file is None:
                raise FileNotFoundError(f"Unable to locate {dep}, "
                                        f"required by {self.library_file}")

            self.context.announce(f"Fixing up {dep}")

            libraries.append(dep_file)
            type(self)(dep_file, self.context).resolve(search_path)
        libraries.append(self.library_file)
        d.run(platfiles=libraries, contents="@rpath/..")



class AudidWheelsHandlerStrategy(AbsSoHandler):

    def get_deps(self) -> List[str]:
        return []

def get_so_handler(shared_library: str, context,
                   system_name: str = None) -> AbsSoHandler:

    system_name = system_name or platform.system()
    strategies = {
        # "Darwin": NullHandlerStrategy,
        "Darwin": MacholibStrategy,
        "Linux": AudidWheelsHandlerStrategy,
        "Windows": DllHandlerStrategy,
    }
    strat = strategies.get(
        system_name, NullHandlerStrategy)
    return strat(shared_library, context)

class BuildConan(setuptools.Command):
    user_options = [
        ('conan-exec=', "c", 'conan executable')
    ]

    description = "Get the required dependencies from a Conan package manager"

    def get_from_txt(self, conanbuildinfo_file):
        definitions = []
        include_paths = []
        lib_paths = []
        libs = []

        with open(conanbuildinfo_file, "r") as f:
            parser = ConanBuildInfoParser(f)
            data = parser.parse()
            definitions = data['defines']
            include_paths = data['includedirs']
            lib_paths = data['libdirs']
            libs = data['libs']

        return {
            "definitions": definitions,
            "include_paths": list(include_paths),
            "lib_paths": list(lib_paths),
            "libs": list(libs)
        }

    def initialize_options(self):
        pass
        self.conan_exec = None

    def finalize_options(self):
        pass
        # if self.conan_exec is None:
        #     self.conan_exec = shutil.which("conan")
        #     if self.conan_exec is None:
        #         self.conan_exec = \
        #             shutil.which("conan", path=sysconfig.get_path('scripts'))
        #
        #         if self.conan_exec is None:
        #             raise FileNotFoundError("missing conan_exec")

    def getConanBuildInfo(self, root_dir):
        for root, dirs, files in os.walk(root_dir):
            for f in files:
                if f == "conanbuildinfo.json":
                    return os.path.join(root, f)
        return None

    def run(self):
        build_ext_cmd = self.get_finalized_command("build_ext")
        build_dir = build_ext_cmd.build_temp

        build_dir_full_path = os.path.abspath(build_dir)
        conan_cache = os.path.join(build_dir, "conan_cache")
        self.mkpath(conan_cache)
        self.mkpath(build_dir_full_path)
        self.mkpath(os.path.join(build_dir_full_path, "lib"))

        conan = conan_api.Conan(cache_folder=os.path.abspath(conan_cache))
        conan_options = []
        if platform.system() == "Windows":
            conan_options.append("*:shared=True")
        conan.install(
            options=conan_options,
            cwd=build_dir,
            path=os.path.abspath(os.path.dirname(__file__)),
            install_folder=build_dir_full_path
        )

        conanbuildinfotext = os.path.join(build_dir, "conanbuildinfo.txt")
        assert os.path.exists(conanbuildinfotext)
        text_md = self.get_from_txt(conanbuildinfotext)
        build_ext_cmd.include_dirs = list(
            set(text_md['include_paths']) | set(build_ext_cmd.include_dirs))

        build_ext_cmd.library_dirs = list(
            set(text_md['lib_paths']) | set(build_ext_cmd.library_dirs))

        build_ext_cmd.libraries = list(
            set(text_md['libs']) | set(build_ext_cmd.libraries))

        conanbuildinfo_file = self.getConanBuildInfo(build_dir_full_path)
        if conanbuildinfo_file is None:
            raise FileNotFoundError("Unable to locate conanbuildinfo.json")

        with open(conanbuildinfo_file) as f:
            conan_build_info = json.loads(f.read())
        for extension in build_ext_cmd.extensions:
            for dep in conan_build_info['dependencies']:
                extension.include_dirs += dep['include_paths']
                extension.library_dirs += dep['lib_paths']
                extension.libraries += dep['libs']
                extension.define_macros += [(d,) for d in dep['defines']]

    def get_import_paths_from_import_manifest(self, manifest_file) -> \
            List[str]:

        lib_dirs = set()
        for lib in self.get_libraries_from_import_manifest(manifest_file):
            lib_dirs.add(os.path.dirname(lib))
        return list(lib_dirs)

    def get_libraries_from_import_manifest(self, manifest_file) -> List[str]:
        with open(manifest_file, "r") as f:
            parser = ConanImportManifestParser(f)
            return parser.parse()

    def get_from_json(self, conanbuildinfo_file) -> \
            Dict[str, List[Union[str, Tuple[str, Optional[str]]]]]:

        if conanbuildinfo_file is None:
            raise FileNotFoundError("Unable to locate conanbuildinfo.json")
        self.announce(f"Reading from {conanbuildinfo_file}", 5)
        with open(conanbuildinfo_file) as f:
            conan_build_info = json.loads(f.read())

        def reduce_dups(a, b, key):

            if isinstance(a, set):
                collection = a
            else:
                collection = set(a[key])
            collection = collection.union(b[key])
            return collection

        libs = reduce(lambda a, b: reduce_dups(a, b, key="libs"),
                      conan_build_info['dependencies'])
        include_paths = reduce(
            lambda a, b: reduce_dups(a, b, key="include_paths"),
            conan_build_info['dependencies'])
        self.announce(f"Adding [{','.join(include_paths)}] to include path", 4)
        lib_paths = reduce(lambda a, b: reduce_dups(a, b, key="lib_paths"),
                           conan_build_info['dependencies'])
        self.announce(
            f"Adding [{', '.join(lib_paths)}] to library search path", 4)

        definitions = list()
        for dep in conan_build_info['dependencies']:
            definitions += [(d,) for d in dep['defines']]

        return {
            "definitions": definitions,
            "include_paths": list(include_paths),
            "lib_paths": list(lib_paths),
            "libs": list(libs)
        }



open_jpeg_extension = setuptools.Extension(
    "uiucprescon.imagevalidate.openjp2wrap",
    sources=[
        "uiucprescon/imagevalidate/glue.cpp",
        "uiucprescon/imagevalidate/openjp2wrap.cpp",
        "uiucprescon/imagevalidate/opj_colorspace_checker.cpp"
    ],
    language="c++",
    libraries=["openjp2"],
    # extra_compile_args=['-std=c++14'],
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
    packages=[
        'uiucprescon.imagevalidate',
        "uiucprescon.imagevalidate.profiles"],
    test_suite="tests",
    namespace_packages=["uiucprescon"],
    setup_requires=['pytest-runner'],
    install_requires=['py3exiv2bind>=0.1.5b3'],
    tests_require=['pytest'],
    zip_safe=False,
    ext_modules=[open_jpeg_extension],
    libraries=[],
    # libraries=[openjpeg_library],
    cmdclass={
        "build_ext": BuildPybind11Extension,
        # "build_openjpeg": BuildCMakeClib,
        "build_clib": BuildCMakeClib,
        "build_conan": BuildConan
        # "build_openjpeg": BuildOpenJpegClib,
        # "package_clib": PackageClib,
    }
)

# TODO extension should try to find the include and librarys and if not try looking at the one clib version
