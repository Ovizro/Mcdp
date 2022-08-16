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

import re
import warnings
from setuptools import setup

try:
    with open("README.md", encoding='utf-8') as f:
        description = f.read()
except OSError:
    warnings.warn("Miss file 'README.md', using default description.", ResourceWarning)
    description = "A python wheel helps to build a Minecraft datapack."

try:
    with open("mcdp/include/version.h") as f:
        version = re.search(r"#define DP_VERSION \"(.*)\"\n", f.read()).group(1)
except Exception as e:
    raise ValueError("fail to read mcdp version") from e


setup(
    name="Mcdp",
    version=version,
    description="A python wheel helps to build a Minecraft datapack.\nThe name 'Mcdp' is short for 'Minecraft datapack'.",
    long_description=description,
    long_description_content_type='text/markdown',

    author="Ovizro",
    author_email="Ovizro@hypercol.com",
    maintainer="Tatersic, ExDragine",
    maintainer_email="Tatersic@qq.com, ExDragine@hypercol.com",
    license="Apache 2.0",

    url="https://github.com/Ovizro/Mcdp",
    packages=["mcdp"],
    python_requires="3.7",
    package_data={'':["*.pyi", "include/*.h", "*.pxd"]},
    install_requires=["ujson", "pydantic"],

    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Cython",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Compilers"
    ]
)