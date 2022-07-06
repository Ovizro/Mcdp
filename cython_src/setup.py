from glob import glob
import os
from setuptools import setup, Extension
from Cython.Build import cythonize

path = os.getcwd()
if os.path.split(path)[1] != "cython_src":
    os.chdir("cython_src")

ext = [
    Extension("mcdp.version", ["mcdp\\version.pyx"]),
    Extension("mcdp.stream", ["mcdp\\stream.pyx"]),
    Extension("mcdp.objects", ["mcdp\\objects.pyx"]),
    Extension("mcdp.exception", ["mcdp\\exception.pyx"])
]

setup(
    name="mcdp",
    ext_modules=cythonize(ext, annotate=True, compiler_directives={"language_level": "3"}),
    zip_safe=False,
)