import os
from setuptools import setup, Extension
from Cython.Build import cythonize

ext = [
    Extension("mcdp.counter", ["mcdp/counter.pyx"]),
    Extension("mcdp.version", ["mcdp/version.pyx"]),
    Extension("mcdp.stream", ["mcdp/stream.pyx"]),
    Extension("mcdp.typing", ["mcdp/typing.pyx"])
]

path = os.getcwd()
if os.path.split(path)[1] != "cython_src":
    os.chdir("cython_src")

setup(
    name="mcdp",
    ext_modules=cythonize(ext),
    zip_safe=False
)