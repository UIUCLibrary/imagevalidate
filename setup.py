from setuptools import setup


setup(
    packages=['uiucprescon.imagevalidate'],
    test_suite="tests",
    namespace_packages=["uiucprescon"],
    setup_requires=['pytest-runner'],
    # install_requires=['aiohttp', 'importlib_resources'],
    tests_require=['pytest'],
    zip_safe=False,
)
