import os
from shutil import copy, copytree, rmtree, make_archive
from abc import abstractmethod
from typing import Any, ClassVar, Dict, List, Optional, Type, Union
from pydantic import BaseModel, PrivateAttr, validator

from .version import Version
from .config import MinecraftVersionError
from .stream import Stream

try:
    import ujson as json
except ImportError:
    import json


class PackageInformation(BaseModel):
    name: str
    support_version: Version
    description: str
    icon_path: Optional[str] = None

    @validator("icon_path")
    def validate_icon_path(cls, icon_path: Optional[Union[str, os.PathLike]]) -> Optional[str]:
        if icon_path:
            return os.path.abspath(icon_path)


class AbstractBuilder(PackageInformation):
    build_dir: ClassVar[str] = "build"

    remove_old_pack: bool = True
    output_dir: List[str] = ['.']

    _origin_dir: str = PrivateAttr('.')

    @abstractmethod
    def build(self) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def finalize(self) -> str:
        raise NotImplementedError
    
    def __enter__(self) -> "AbstractBuilder":
        os.makedirs(self.build_dir, exist_ok=True)

        self._origin_dir = os.getcwd()
        os.chdir(self.build_dir)
        self.build()
        return self
    
    def __exit__(self, *args) -> None:
        pack_path = self.finalize()
        os.chdir(self._origin_dir)

        is_dir = os.path.isdir(pack_path)

        for dst in self.output_dir:
            os.makedirs(dst, exist_ok=True)
            if is_dir:
                _dst = os.path.join(dst, self.name)
                if self.remove_old_pack and os.path.exists(_dst):
                    rmtree(_dst)
                copytree(pack_path, _dst, dirs_exist_ok=True)
            else:
                copy(pack_path, dst)


class PackBuilder(AbstractBuilder):
    src_dir: ClassVar[str]

    make_archive: bool = False

    def build(self, *argv: str) -> None:
        p_name = self.name
        if not os.path.isdir(p_name):
            os.mkdir(p_name)
        os.chdir(p_name)
        
        with Stream(b"pack.mcmeta") as f:
            json.dump(self.get_mcmeta(), f, indent=4)
        if self.icon_path:
            copy(self.icon_path, "pack.png")

        src_path = self.src_dir
        if not os.path.isdir(src_path):
            os.mkdir(src_path)
        os.chdir(src_path)
    
    def finalize(self) -> str:
        os.chdir("../..")
        if self.make_archive:
            return make_archive(self.name, "zip", root_dir=self.name)
        else:
            return os.path.abspath(self.name)

    def get_mcmeta(self) -> Dict[str, Any]:
        return {
            "pack": {
                "pack_format": self.get_version_num(),
                "description": self.description
            }
        }

    @abstractmethod
    def get_version_num(self) -> int:
        raise NotImplementedError


class DatapackBuilder(PackBuilder):
    src_dir: ClassVar[str] = "data"

    def get_version_num(self) -> int:
        mc_version = self.support_version
        
        if mc_version.major != 1:
            raise MinecraftVersionError("Minecraft version must start with '1.'.")
        elif mc_version.minor < 13:
            raise MinecraftVersionError("datapack is not enable for Minecraft below 1.13 .")
        elif mc_version.minor < 15:
            return 4
        elif mc_version <= "1.16.1":
            return 5
        elif mc_version.minor < 17:
            return 6
        elif mc_version.minor < 18:
            return 7
        elif mc_version <= "1.18.1":
            return 8
        elif mc_version.minor < 19:
            return 9
        elif mc_version.minor == 19:
            return 10
        else:
            raise ValueError(f"unknow Minecraft datapack version {mc_version}.")


_buildcls: Type[AbstractBuilder] = DatapackBuilder


def get_defaultbuilder() -> Type[AbstractBuilder]:
    return _buildcls


def set_defaultbuilder(builder: Type[AbstractBuilder]) -> None:
    global _buildcls
    _buildcls = builder