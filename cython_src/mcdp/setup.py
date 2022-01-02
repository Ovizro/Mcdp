import os
from setuptools import setup, Extension
from Cython.Build import cythonize

ext = [
    Extension("mcdp.counter", ["cython_src/mcdp/counter.pyx"]),
    Extension("mcdp.version", ["cython_src/mcdp/version.pyx"]),
    Extension("mcdp.stream", ["cython_src/mcdp/stream.pyx"])
]

# path = os.getcwd()
# if os.path.split(path)[1] != "cython_src":
#     os.chdir("cython_src")

setup(
    name="mcdp",
    ext_modules=cythonize(ext),
    zip_safe=False
)