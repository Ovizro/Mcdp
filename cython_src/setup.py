import os
from setuptools import setup, Extension
from Cython.Build import cythonize, build_ext

ext = [
    Extension("mcdp.counter", ["mcdp/counter.pyx"]),
    Extension("mcdp.version", ["mcdp/version.pyx"]),
    Extension("mcdp.stream", ["mcdp/stream.pyx"]),
    Extension("mcdp._typing", ["mcdp/_typing.pyx"])
]

path = os.getcwd()
if os.path.split(path)[1] != "cython_src":
    os.chdir("cython_src")

setup(
    name="mcdp",
    ext_modules=cythonize(ext),
    zip_safe=False,
    cmdclass={"build_ext": build_ext}
)