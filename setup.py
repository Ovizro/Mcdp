from setuptools import setup

setup(
    name="Mcdp",
    version="0.1.0",
    description="A python wheel helps to build a Minecraft datapack.\nThe name 'Mcdp' is short for 'Minecraft datapack'.",

    author="Ovizro",
    author_email="Ovizro@hypercol.com",
    license="Apache 2.0",

    url="https:https://github.com/Ovizro/Mcdp",
    packages=["mcdp"],
    install_requires=["ujson", "pydantic", "aiofiles"]
)