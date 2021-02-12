import io
import json
import os
from shutil import copyfile
from functools import partial
from collections import OrderedDict, defaultdict
from typing import (Any, Callable, Dict, Literal, NoReturn, Optional, Tuple,
                    Union)

try:
    from .exception import VersionError
except ImportError:
    from exception import VersionError

def file_open(path: str, mode: str = 'w', **kw):
    if not os.path.isfile(path):
        p = os.path.split(path)
        if not os.path.isdir(p[0]):
            os.makedirs(p[0])
    return open(path, mode, **kw)

class cacheFile(OrderedDict):
    
    __slots__ = ['_capacity',]
    
    def __init__(self, capacity: int = 7):
        self._capacity = capacity
        super().__init__()
    
    def __getitem__(self, key) -> io.TextIOWrapper:
        self.move_to_end(key)
        return super().__getitem__(key)

    def __setitem__(self, key: str, value: io.TextIOWrapper) -> None:
        super().__setitem__(key, value)
        self.check()
    
    def update(self, *args, **kw) -> None:
        super().update(*args, **kw)
        self.check()

    def check(self) -> int:
        overflow = len(self) - self._capacity
        if overflow <= 0:
            return 0
        for i in range(overflow):
            k,f = self.popitem(last=False)
            if hasattr(f, "close"):
                if callable(f.close):
                    f.close()
        return overflow
    
    def clear(self) -> None:
        while len(self) > 0:
            k,v = self.popitem()
            if hasattr(v, "close"):
                v.close()
        super().clear()

class FileFunc:

    __slots__ = ['__func__', '__name__']

    def __init__(self, func: Callable) -> None:
        self.__func__ = func
        self.__name__ = func.__name__

    def __get__(self, instance: Any, owner: type) -> Callable:
        if instance == None:
            return self.__func__
        else:
            def FileMethod(*args, **kwargs):
                return self.__func__(instance, *args, **kwargs)
            FileMethod.__name__ = self.__name__
            return FileMethod

    def __call__(self, *args, **kwds) -> Any:
        return self.__func__(*args, **kwds)

class FileOutputMata(type):

    DIR_CHANGED = False

    def __new__(cls, name: str, bases: Tuple[type], attrs: dict) -> type:
        NewAttrs = {
            "FileMethodList": set()
        }
        for k,v in attrs.items():
            if isinstance(v, FileFunc):
                NewAttrs["f_" + k] = v
                NewAttrs["FileMethodList"].add(k)
            else:
                NewAttrs[k] = v

        NewAttrs.update(
            spaceCathe = cacheFile(3),
            spacePath = defaultdict(lambda: '.')
        )
        return type.__new__(cls, name, bases, NewAttrs)
    
    def __getattr__(self, key: str) -> Callable:
        if key in self.FileMethodList:
            return self.context.__getattribute__("f_" + key)
        else:
            raise AttributeError(f"'{self.__name__}' object has no attribute '{key}'")

    def __getitem__(self, key: str) -> Any:
        self.switch(key)
        return self

    def file_struct(
        self, 
        base: str,
        *,
        spacePath: Optional[Dict[str,str]] = None,
        filePath: Optional[Dict[str,str]] = None
    ) -> None:
        if not os.path.isabs(base):
            if self.__class__.DIR_CHANGED:
                raise OSError("set file structure after activate spaces")
            self.base = os.path.abspath(base)
        else:
            self.base = base

        for k,v in filePath.items():
            if k in self.ReserveFile:
                self.ReserveFile[k] = v
        self.spacePath.update(spacePath)

    def switch(self, spaceName: str, path: Optional[str] = None) -> None:
        if hasattr(self, "context"):
            if self.context.name == spaceName:
                return
        if spaceName in self.spaceCathe:
            self.context = self.spaceCathe[spaceName]
        else:
            NewSpace = self(spaceName, path)
            self.spaceCathe[spaceName] = NewSpace
            self.context = NewSpace

        self.context.activate()
    
    def clear(self, spaceName: Optional[str] = None) -> NoReturn:
        if spaceName:
            self.spaceCathe.get(spaceName).fileCathe.clear()
        else:
            self.__getattr__("clear")()

class MCFile(metaclass=FileOutputMata):
    
    ReserveFile = {}

    def __init__(self, spaceName: str, path: Optional[str] = None) -> NoReturn:
        self.name = spaceName

        if not path:
            path = self.__class__.spacePath[spaceName]
        if not os.path.isabs(path):
            if self.__class__.__class__.DIR_CHANGED == True:
                raise OSError("param path should be an absolute path")
            path = os.path.abspath(path)

        if not os.path.isdir(path):
            os.makedirs(path)
        self.path = path
        self.fileCathe = cacheFile()
    
    def __getattr__(self, key: str) -> Callable:
        if key in self.__class__.FileMethodList:
            return self.context.__getattribute__("f_" + key)
        else:
            raise AttributeError(f"'{self.__name__}' object has no attribute '{key}'")

    @FileFunc
    def activate(self) -> NoReturn:
        self.__class__.__class__.DIR_CHANGED = True
        os.chdir(self.path)

    @FileFunc
    def open(self, path: str,  *, mode: str = "w") -> None:
        name = os.path.split(path)[-1]
        if hasattr(self, "correct"):
            if self.correct.__name__ == name:
                return
        elif name in self.fileCache:
            self.correct = self.fileCache[name]
        else:
            f = file_open(path)
            self.fileCathe[name] = f
            self.correct = f

    @FileFunc
    def get_correct_file(self) -> io.TextIOWrapper:
        return self.correct

    @FileFunc
    def write(self, contains: str) -> int:
        return self.correct.write(contains)

    @FileFunc
    def seek(self, cookie: int, whence: int = 0) -> None:
        self.correct.seek(cookie, whence)

    @FileFunc
    def close(self) -> NoReturn:
        self.correct.close()
        self.fileCathe.popitem(last=True)
    
    @FileFunc
    def clear(self) -> NoReturn:
        self.fileCathe.clear()

class MCFunc(MCFile):
    ReserveFile = {
        "load"      : "load.mcfunction",
        "preapare"  : "prepare.mcfunction",
        "main"      : "main.mcfunction",
    }

class MCJson(MCFile):

    @FileFunc
    def write(self, contain: dict) -> int:
        contain = json.dumps(contain, indent=4)
        return super(self, MCFile).write(contain)

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
            json.dump(contain, f, indent=4)

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

if __name__ == "__main__":
    MCFile["here"].open("test.txt")
    MCFile.write("Hello World!")
    MCFile.close()