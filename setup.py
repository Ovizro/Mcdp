"""
Copyright 2022 Ovizro

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import re
from typing import List, Optional
import warnings
from setuptools import setup, find_packages, Extension


try:
    with open("README.md", encoding='utf-8') as f:
        description = f.read()
except OSError:
    warnings.warn("Miss file 'README.md', using default description.", ResourceWarning)
    description = "A python wheel helps to build a Minecraft datapack."

try:
    with open("mcdp/include/version.h") as f:
        version = re.search(r"#define DP_VERSION \"(.*)\"\n", f.read()).group(1) # type: ignore
except Exception as e:
    raise ValueError("fail to read mcdp version") from e


USE_CYTHON = "USE_CYTHON" in os.environ
FILE_SUFFIX = ".pyx" if USE_CYTHON else ".c"
HOME_PATH = os.path.join(os.path.dirname(__file__), "mcdp")

ext = [
    Extension("mcdp.stream", ["mcdp/stream" + FILE_SUFFIX],
        include_dirs=[HOME_PATH, os.path.join(HOME_PATH, "include")]),
    # Extension("mcdp.variable", ["mcdp/variable/{}{}".format(i, FILE_SUFFIX) for i in ("mcstring", "selector", "position", "console", "nbtpath")], include_dirs=[HOME_PATH]),
    Extension("mcdp.control_flow.execute", ["mcdp/control_flow/execute" + FILE_SUFFIX], include_dirs=[HOME_PATH]),
    Extension("mcdp.control_flow.branch", ["mcdp/control_flow/branch" + FILE_SUFFIX], include_dirs=[HOME_PATH])
]


def add_ext(name: str, include: Optional[List[str]] = None) -> None:
    include_dirs = [HOME_PATH]
    if include:
        include_dirs.extend(include)
    ext.append(
        Extension(
            name, [name.replace('.', '/') + FILE_SUFFIX],
            include_dirs=include_dirs
        )
    )


for i in ["version", "objects", "exception", "context"]:
    add_ext(f"mcdp.{i}")
for i in ["mcstring", "selector", "position", "console", "nbtpath", "baseframe", "scoreboard"]:
    add_ext(f"mcdp.variable.{i}")


if USE_CYTHON:
    from Cython.Build import cythonize
    from Cython.Compiler import Options
    
    Options.fast_fail = True
    extensions = cythonize(ext, annotate=True, compiler_directives={"language_level": "3"})


setup(
    name="Mcdp",
    version=version,
    description="A python wheel helps to build a Minecraft datapack.\nThe name 'Mcdp' is short for 'Minecraft datapack'.",
    long_description=description,
    long_description_content_type='text/markdown',

    author="HyperCol",
    author_email="HyperCol@hypercol.com",
    maintainer="Ovizro",
    maintainer_email="Ovizro@hypercol.com",
    license="Apache 2.0",

    url="https://github.com/Ovizro/Mcdp",
    packages=find_packages(exclude=["tests"]),
    python_requires=">=3.6",
    # package_data={'':["*.pyi", "*.pxd"]},
    ext_modules=ext,
    install_requires=["pydantic>=1.7.0", "typing_extensions>=4.0.0", "KoiLang>=1.0.0"],

    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Cython",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Compilers"
    ]
)