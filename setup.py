import warnings
from setuptools import setup

try:
    with open("README.md", encoding='utf-8') as f:
        description = f.read()
except OSError:
    warnings.warn("Miss file 'README.md', using default description.")
    description = "A python wheel helps to build a Minecraft datapack."

setup(
    name="Mcdp",
    version="0.1.3",
    description="A python wheel helps to build a Minecraft datapack.\nThe name 'Mcdp' is short for 'Minecraft datapack'.",
    long_description=description,
    long_description_content_type='text/markdown',

    author="Ovizro",
    author_email="Ovizro@hypercol.com",
    license="Apache 2.0",

    url="https://github.com/Ovizro/Mcdp",
    packages=["mcdp"],
    install_requires=["ujson", "pydantic", "aiofiles"]
)