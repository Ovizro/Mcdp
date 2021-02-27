import os
import ujson
from shutil import copyfile
from typing import Any, Callable, Dict, Optional, Set, Union

try:
    from .exception import MinecraftVersionError
    from .file_output import FileOutput, MCJson, MCFunc, MCTag
except ImportError:
    from exception import MinecraftVersionError
    from file_output import FileOutput, MCJson, MCFunc, MCTag

USE_AIO: bool = False

def get_version(version: str) -> int:
    vlist = [int(v) for v in version.split(".")]

    if vlist[0] != 1 or vlist[1] < 13:
        raise MinecraftVersionError("Only Minecraft version >= 1.13 can use datapack.")

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

def init_mcmeta(desc: str, version: Union[int, str]) -> None:
    with open("pack.mcmeta", "w") as f:
        if isinstance(version, str):
            version = get_version(version)
        contain = {
            "pack":{
                "pack_format": version,
                "description": desc
            }
        }
        ujson.dump(contain, f, indent=4)

def init_name_space(name: str, *, used: Optional[Set[str]] = None) -> None:
    dirs = {
        "advancements", 
        "functions", 
        "loot_tables", 
        "predicates", 
        "structures", 
        "recipes", 
        "item_modifiers", 
        "dimension_type", 
        "dimension", 
        "worldgen"
    }
    for d in dirs:
        if used:
            if not d in used:
                continue
        path = os.path.join(name, d)
        os.makedirs(path, exist_ok=True)
    
    dirs = {
        "blocks",
        "entity_types",
        "items",
        "fluids",
        "functions"
    }
    tag_path = os.path.join(name, "tags")
    for d in dirs:
        path = os.path.join(tag_path, d)
        os.makedirs(path, exist_ok=True)

def analyse_file_struct(
    struct: Union[dict, str], 
    base: Optional[os.PathLike] = None
) -> Dict[str, os.PathLike]:

    if isinstance(struct, str):
        struct = ujson.loads(struct)
    ans = {}
    for k,v in struct.items():
        if not base:
            path = k
        else:
            path = os.path.join(base, k)
        
        if isinstance(v, str):
            ans[v] = path
        else:
            ans.update(analyse_file_struct(v, path))
    
    return ans


class BuildDirs:

    __slots__ = ["progress", "namespace", "space_list"]

    def __init__(
        self,
        name: str,
        description: str,
        version: Union[int, str] = 4,
        *,
        iron_path: Optional[os.PathLike] = None,
        namespace: Optional[str] = None
    ) -> None:
        """
        :param name: the package name
        :param description: the description of the package
        :param version: Minecraft version such as '1.16.2' or a datapack version number
        :param iron_path: be packed into the package as pack.png
        :param namespace: the name space in package, and will use name instead without it
        """
        if not namespace:
            namespace = name
        self.namespace = namespace
        os.makedirs(os.path.join(name, "data", namespace), exist_ok=True)
        os.chdir(name)

        init_mcmeta(description, version)

        if iron_path:
            iron_path = os.path.abspath(iron_path)
            copyfile(iron_path, "pack.png")
        
        os.chdir("data")
        init_name_space("minecraft", used={"advancements",})

        if not namespace:
            namespace = name
        init_name_space(namespace)

        self.progress: int = 1

    def init_output(self, file_struct: Union[dict, str], *, analyse_struct: bool = True) -> None:
        if self.progress != 1:
            raise OSError("cannot init FileOutput class.")

        FileOutput.file_struct()
        MCJson.file_struct()

        MCTag.init_minecraft_space("minecraft/tags")

        self.progress = 2
        os.chdir(self.namespace)
        MCTag.file_struct("tags")

        if analyse_struct:
            self.space_list = analyse_file_struct(file_struct)
        else:
            self.space_list = file_struct

        MCFunc.file_struct(
            "functions",
            spacePath=self.space_list
        )

if __name__ == "__main__":
    s = {
        "here": {
            "test": {
                "test": "test",
                "test2": "test3"
            },
            "there": "there"
        },
        "test": "test2"
    }
    BuildDirs("testdatapack", description="Hello world").init_output(s)
    MCFunc["test2"].open("hello")
    MCFunc.write("say Hello!")
    MCTag.tick("testdatapack:test/hello", flush=True)
    MCTag.add_tag("test", "testdatapack:test/hello")
    MCTag.clearAll()
    