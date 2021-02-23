import os
import ujson
from shutil import copyfile
from typing import (Any, Callable, Dict, NoReturn, Optional, Tuple,
                    Union)

try:
    from .exception import VersionError
except ImportError:
    from exception import VersionError

class DatapackType:
    pass
class DatapackFile(DatapackType):
    pass
class DatapackDir(DatapackType):
    pass

class PackageDirs:

    def __init__(
        self,
        name: str,
        version: Union[int, str] = 1,
        description: Optional[str] = None,
        iron_path: Optional[str] =None,
        *,
        namespace: Optional[str] = None
    ) -> None:
        iron_path = os.path.abspath(iron_path)
        if not namespace:
            namespace = name
        os.makedirs(os.path.join(name, "data", namespace), exist_ok=True)
        os.chdir(name)

        with open("pack.mcmeta", "w") as f:
            if isinstance(version, str):
                version = self.get_version(version)
            contain = {
                "pack":{
                    "pack_format": version,
                    "description": description
                }
            }
            ujson.dump(contain, f, indent=4)

        if iron_path:
            copyfile(iron_path, "pack.png")
        
        os.chdir("data")

    @staticmethod
    def get_version(version: str) -> int:
        vlist = [int(v) for v in version.split(".")]

        if vlist[0] != 1 or vlist[1] < 13:
            raise VersionError(">= 1.13", version, "Minecraft")

        if vlist[1] == 13 or vlist[1] == 14:
            return 4
        if vlist[1] == 15:
            return 5
        if vlist[1] == 16:
            if len(vlist) <= 2:
                return 5
            if vlist[2] <= 1:
                return 5
            else:
                return 6
        if vlist[1] == 17:
            return 7