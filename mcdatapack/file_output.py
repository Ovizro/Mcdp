import io
import ujson
import os
from functools import partial
from collections import OrderedDict
from typing import (Any, Callable, Dict, NoReturn, Optional, Tuple,
                    Union)

ALLOW_NOT_SETTING_SPACE_PATH: bool = True

def file_open(path: str, mode: str = 'w', **kw):
    if not os.path.isfile(path):
        p = os.path.split(path)
        if not os.path.isdir(p[0]) and p[0]:
            os.makedirs(p[0])
    return open(path, mode, **kw)

class cacheFile(OrderedDict):
    
    __slots__ = ['_capacity',]
    
    def __init__(self, capacity: int = 7):
        self._capacity = capacity
        super().__init__()
    
    def __getitem__(self, key) -> io.TextIOWrapper:
        if key in self:
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
    
    def popitem(self, last: bool = True) -> Tuple[str, io.TextIOWrapper]:
        if last:
            ite = self.items().__reversed__()
        else:
            ite = self.items()
        for ans in ite:
            del self[ans[0]]
            return ans

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

    ACTIVATED = False

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
            spacePath = {},
            spaceStack = [],
            spaceCache = cacheFile(3)
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

    def __setitem__(self, key: str, value: Any) -> NoReturn:
        if not isinstance(value, self):
            raise TypeError
        self.spaceCache[key] = value
        if not key in self.spacePath:
            self.spacePath[key] = value.path
    
    def file_struct(
        self, 
        base: str = os.getcwd(),
        *,
        spacePath: Optional[Dict[str,str]] = None,
        filePath: Optional[Dict[str,str]] = None
    ) -> None:
        if hasattr(self, "context"):
            self.clearAll()

        if not os.path.isabs(base):
            if self.__class__.ACTIVATED:
                raise OSError("set file structure after activate spaces")
            self.base = os.path.abspath(base)
        else:
            self.base = base

        if filePath:
            for k,v in filePath.items():
                if k in self.ReserveFile:
                    self.ReserveFile[k] = v
        if spacePath:
            self.spacePath = {k: os.path.abspath(v) for k, v in spacePath.items()}

        self.file = {}
        for k, v in self.ReserveFile.items():
            self.file[k] = file_open(v)

        self.spaceStack.clear()
        self.spaceStack.append("__base__")

    def abspath(self, path: str):
        if not hasattr(self, "base"):
            raise OSError("use path.join without initing base dir")
        return os.path.join(self.base, path)
    
    join_path = staticmethod(os.path.join)

    def enter(self, name: str, path: Optional[str] = None) -> NoReturn:...


    def switch(self, spaceName: str, path: Optional[str] = None) -> None:
        if hasattr(self, "context"):
            if self.context.name == spaceName:
                return
        if spaceName in self.spaceCache:
            self.context = self.spaceCache[spaceName]
        else:
            NewSpace = self(spaceName, path)
            self.spaceCache[spaceName] = NewSpace
            self.context = NewSpace

        self.context.activate()
    
    def clear(self, spaceName: Optional[str] = None) -> NoReturn:
        if spaceName:
            self.spaceCache.get(spaceName).fileCache.clear()
        else:
            self.__class__.__getattr__(self, "clear")()
    
    def clearAll(self) -> NoReturn:
        del self.context
        for s in self.spaceCache.values():
            s.get_method("clear")()

class FileOutput(metaclass=FileOutputMata):

    __slots__ = ["name", "path", "fileCache", "correct"]
    
    ReserveFile = {}

    def __init__(self, spaceName: str, path: Optional[str] = None) -> NoReturn:
        self.name = spaceName

        if not path:
            if spaceName in self.__class__.spacePath:
                path = self.__class__.spacePath[spaceName]
                if not os.path.isabs(path):
                    if self.__class__.__class__.ACTIVATED and (not ALLOW_NOT_SETTING_SPACE_PATH):
                        raise OSError("param path should be an absolute path")
                    path = os.path.abspath(path)
            else:
                path = self.__class__.abspath(spaceName)

        if not os.path.isdir(path):
            os.makedirs(path)
        self.path = path
        self.fileCache = cacheFile()

    def __getattr__(self, key: str) -> Callable:
        if key in self.__class__.FileMethodList:
            return self.__class__.context.__getattribute__("f_" + key)
        elif key == "correct":
            raise AttributeError("fetch correct file without opening")
        elif hasattr(self.correct, key):
            return self.correct.__getattribute__(key)

        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{key}'")
    
    def get_method(self, key: str) -> Callable:
        return self.__class__.__getattribute__(self, "f_" + key)

    @FileFunc
    def activate(self) -> NoReturn:
        self.__class__.__class__.ACTIVATED = True
        os.chdir(self.path)

    @FileFunc
    def open(self, path: str, *, mode: str = "w") -> None:
        name = os.path.split(path)[-1]
        if hasattr(self, "correct"):
            if self.correct.name == name:
                return
        if name in self.fileCache:
            self.correct = self.fileCache[name]
        else:
            f = file_open(path, mode=mode)
            self.fileCache[name] = f
            self.correct = f

    @FileFunc
    def get_correct_file(self) -> io.TextIOWrapper:
        return self.correct

    @FileFunc
    def write(self, contains: str) -> int:
        return self.correct.write(contains)

    @FileFunc
    def writeable(self) -> bool:
        if not hasattr(self, "correct"):
            return False
        elif self.correct.closed:
            return False
        else:
            return self.correct.writable()
    
    @FileFunc
    def seek(self, cookie: int, whence: int = 0) -> None:
        self.correct.seek(cookie, whence)

    @FileFunc
    def flush(self) -> None:
        self.correct.flush()

    @FileFunc
    def close(self) -> NoReturn:
        self.correct.close()
        del self.fileCache[self.correct.name]
    
    @FileFunc
    def clear(self) -> NoReturn:
        self.fileCache.clear()

class MCFunc(FileOutput):
    ReserveFile = {
        "load"      : "load.mcfunction",
        "preapare"  : "prepare.mcfunction",
        "main"      : "main.mcfunction",
    }

class MCJson(FileOutput):

    @FileFunc
    def write(self, contain: dict) -> int:
        contain = ujson.dumps(contain, indent=4)
        return super(self, FileOutput).write(contain)

if __name__ == "__main__":
    FileOutput.file_struct(
        ".",
        spacePath={"here":"testdatapack/test", "test": "testdatapack/test1"}
    )
    FileOutput["here"].open("test.txt")
    FileOutput.write("Hello World!")
    FileOutput["test"].open("Hello_world.txt")
    FileOutput.write("Hey! Look, I do work!")
    FileOutput.open("hhhh.txt")
    FileOutput.write("hhh\n"*10)
    FileOutput["here"].open("test.txt")
    FileOutput.write("\nhhh")
    FileOutput.clearAll()
    FileOutput["test1"].open("hhh.txt")
    FileOutput.write("ok!\n")
    FileOutput.context.flush()
    try:      
        FileOutput.write("closed?\n")
    except:
        print("successful closed")