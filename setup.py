import os
import shutil
import sys
from pathlib import Path
try:
    from macholib import MachO, MachOStandalone
except ImportError:
    pass
from setuptools import setup
try:
    from pybind11.setup_helpers import Pybind11Extension
except ImportError:
    from setuptools import Extension as Pybind11Extension

PACKAGE_NAME = "uiucprescon.imagevalidate"

cmd_class = {}
try:
    from uiucprescon.build import conan_libs
    cmd_class["build_conan"] = conan_libs.BuildConan
except ImportError:
    pass
try:
    from uiucprescon.build.pybind11_builder import BuildPybind11Extension, UseSetuptoolsCompilerFileLibrary

    class BuildPybind11Extensions(BuildPybind11Extension):

        def run(self):
            super().run()
            from uiucprescon.build.deps import get_win_deps

            for e in self.extensions:
                dll_name = \
                    os.path.join(self.build_lib, self.get_ext_filename(e.name))

                output_file = os.path.join(self.build_temp, f'{e.name}.dependents')
                if self.compiler.compiler_type != "unix":
                    if not self.compiler.initialized:
                        self.compiler.initialize()
                    deps = get_win_deps(dll_name, output_file,
                                        compiler=self.compiler)
                    dest = os.path.dirname(dll_name)

                    for dep in deps:
                        if os.path.exists(os.path.join(dest, dep)):
                            print(f"Package already has {dep}")
                            continue
                        paths = os.environ['path'].split(";")
                        dll = self.find_deps(dep, paths)
                        if dll is None:
                            for i in os.scandir(dest):
                                print(i.path)
                            raise FileNotFoundError(
                                f"Missing {dep}. Searched {paths}")
                        shutil.copy(dll, dest)

        def build_extension(self, ext: Pybind11Extension):
            from uiucprescon.build import conan_libs
            missing = self.find_missing_libraries(ext, strategies=[
                UseSetuptoolsCompilerFileLibrary(
                    compiler=self.compiler,
                    dirs=self.library_dirs + ext.library_dirs
                ),
            ])
            build_conan = self.get_finalized_command("build_conan")
            if len(missing) > 0:
                self.announce(f"missing required deps [{', '.join(missing)}]. "
                              f"Trying to get them with conan", 5)
                build_conan.build_libs = ['outdated']
            else:
                build_conan.build_libs = []
            build_conan.run()
            conanfileinfo_locations = [
                self.build_temp,
                os.path.join(self.build_temp, "Release"),
            ]
            conan_info_dir = os.environ.get('CONAN_BUILD_INFO_DIR')
            if conan_info_dir is not None:
                conanfileinfo_locations.insert(0, conan_info_dir)
            super().build_extension(ext)
            tester = {
                'darwin': conan_libs.MacResultTester,
                'linux': conan_libs.LinuxResultTester,
                'win32': conan_libs.WindowsResultTester
            }.get(sys.platform)
            dll_name = \
                os.path.join(self.build_lib, self.get_ext_filename(ext.name))
            tester().test_binary_dependents(Path(dll_name))


    cmd_class["build_ext"] = BuildPybind11Extensions
except ImportError as e:
    pass

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
    packages=[
        'uiucprescon.imagevalidate',
        "uiucprescon.imagevalidate.profiles"],
    test_suite="tests",
    setup_requires=['pytest-runner'],
    install_requires=['py3exiv2bind>=0.1.9b7'],
    tests_require=['pytest'],
    zip_safe=False,
    ext_modules=[open_jpeg_extension],
    libraries=[],
    package_data={"uiucprescon.imagevalidate": ["py.typed"]},
    cmdclass=cmd_class
)
