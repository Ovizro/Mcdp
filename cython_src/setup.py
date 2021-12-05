from setuptools import setup
from Cython.Build import cythonize

setup(
    name="cmcdp",
    ext_modules=cythonize("cython_src/*.pyx"),
    package_data={
        "cmcdp": ["cython_src/**.pxd"]
    }
)