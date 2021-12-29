import os
from setuptools import setup, Extension
from Cython.Build import cythonize

ext = [
    Extension("cython_src.counter", ["cython_src/counter.pyx"]),
    Extension("cython_src.version", ["cython_src/version.pyx"]),
    Extension("cython_src.stream", ["cython_src/stream.pyx"])
]

# os.chdir("cython_src")

setup(
    name="cython_src",
    ext_modules=cythonize(ext)
)