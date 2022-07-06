import os
from setuptools import setup, Extension
from Cython.Build import cythonize

ext = [
    Extension("mcdp.version", ["mcdp\\version.pyx"]),
    Extension("mcdp.stream", ["mcdp\\stream.pyx"]),
    Extension("mcdp.objects", ["mcdp\\objects.pyx"]),
    Extension("mcdp.exception", ["mcdp\\exception.pyx"])
]

path = os.getcwd()
if os.path.split(path)[1] != "cython_src":
    os.chdir("cython_src")

setup(
    name="mcdp",
    ext_modules=cythonize(ext, annotate=True, compiler_directives={"language_level": "3str"}),
    zip_safe=False,
)