from glob import glob
import os
from setuptools import setup, Extension
from Cython.Build import cythonize

path = os.getcwd()
if os.path.split(path)[1] != "cython_src":
    os.chdir("cython_src")

ext = [
    Extension("mcdp.counter", ["mcdp\\counter.pyx"]),
    Extension("mcdp.version", ["mcdp\\version.pyx"]),
    Extension("mcdp.stream", ["mcdp\\stream.pyx"]),
    Extension("mcdp._typing", ["mcdp\\_typing.pyx"]),
    Extension("mcdp.exception", ["mcdp\\exception.pyx"]),
    Extension("mcdp.context", ["mcdp\\context.pyx"]),
    Extension("mcdp.mcstring", ["mcdp\\mcstring.pyx"]),
    Extension("mcdp.command", ["mcdp\\command.pyx"]),
    Extension("mcdp.compiler", ["mcdp\\compiler.pyx"])
]

setup(
    name="mcdp",
    ext_modules=cythonize(ext, annotate=True, compiler_directives={"language_level": "3str"}),
    zip_safe=False,
)