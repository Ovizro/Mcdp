import os
from setuptools import setup, Extension
from Cython.Build import cythonize

ext = [
    Extension("mcdp.counter", ["mcdp\\counter.pyx"]),
    Extension("mcdp.version", ["mcdp\\version.pyx"]),
    Extension("mcdp.stream", ["mcdp\\stream.pyx"]),
    Extension("mcdp._typing", ["mcdp\\_typing.pyx"]),
    Extension("mcdp.context", ["mcdp\\context.pyx"]),
    Extension("mcdp.compiler", ["mcdp\\compiler.pyx"])
]

path = os.getcwd()
if os.path.split(path)[1] != "cython_src":
    os.chdir("cython_src")

setup(
    name="mcdp",
    ext_modules=cythonize(ext, annotate=True, compiler_directives={"language_level": "3str"}),
    zip_safe=False,
)