import io
import ujson
import os
from functools import partial
from collections import OrderedDict
from typing import (Any, Type, Callable, Dict, Optional, Tuple,
                    Union)

def file_open(path: str, mode: str = 'w', **kw) -> io.TextIOWrapper:
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
    
    def __getitem__(self, key: str) -> Any:
        if key in self:
            self.move_to_end(key)
        return super().__getitem__(key)

    def __setitem__(self, key: str, value: Any) -> None:
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
                f.close()
        return overflow
    
    def clear(self) -> None:
        while len(self) > 0:
            k,v = self.popitem()
            if hasattr(v, "clear"):
                v.clear()
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

    def __get__(self, instance: Any, owner: Type) -> Callable:
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
        for t in bases:
            NewAttrs["FileMethodList"].update(t.FileMethodList)

        NewAttrs.update(
            spacePath = {},
            spaceStack = [],
            spaceCache = cacheFile(3)
        )
        return type.__new__(cls, name, bases, NewAttrs)
    
    def __getattr__(self, key: str) -> Callable:
        if key in self.FileMethodList:
            return self.context._get_method(key)
        else:
            raise AttributeError(f"'{self.__name__}' object has no attribute '{key}'.")

    def __getitem__(self, key: Optional[str]) -> Any:
        if key:
            self.switch(key)
        return self

    def __setitem__(self, key: str, value: Any) -> None:
        if not isinstance(value, self):
            raise TypeError
        if key in self.spaceCache:
            self.spaceCache.pop(key).clear()
        self.spaceCache[key] = value

        if not key in self.spacePath:
            self.spacePath[key] = value.path
        self.context: self = value
        value.activate()
    
    def file_struct(
        self, 
        base: str = os.getcwd(),
        *,
        spacePath: Optional[Dict[str,str]] = None,
    ) -> None:
        if not os.path.isabs(base):
            if self.__class__.ACTIVATED:
                raise ValueError("set file structure after activate spaces.")
            self.base = os.path.abspath(base)
        else:
            self.base = base

        if spacePath:
            self.spacePath = {k: os.path.abspath(v) for k, v in spacePath.items()}

        self.spaceStack.clear()
        self.enter("__home__", path=base)

    def reset(self) -> None:
        if not hasattr(self, "correct"):
            return
        self.__class__.ACTIVATED = False
        os.chdir(self.base)
        self.clearAll()

    def abspath(self, path: str):
        if not hasattr(self, "base"):
            raise OSError("use path.join without initing base dir.")
        if os.path.isabs(path):
            return path
        return os.path.join(self.base, path)
    
    join_path = staticmethod(os.path.join)

    def enter(self, spaceName: str, path: Optional[str] = None) -> None:
        self.spaceStack.append(spaceName)

        if not hasattr(self, "context"):
            return self.switch(spaceName, path)

        if self.context.name == spaceName:
            return
        elif spaceName in self.spaceStack:
            raise ValueError("enter a space which has been opened in the stack.")

        nsp: self = self(spaceName, path, stack=True)
        self[spaceName] = nsp

    def exit(self) -> None:
        csp = self.spaceStack.pop()
        self.clear(csp)

        self.switch(self.spaceStack[-1])

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
        if spaceName != "__home__":
            self.context.activate()
    
    def clear(self, spaceName: Optional[str] = None) -> None:
        if spaceName and spaceName in self.spaceCache:
            self.spaceCache.get(spaceName).fileCache.clear()
        else:
            self.context._get_method("clear")
    
    def clearAll(self) -> None:
        del self.context
        for s in self.spaceCache.values():
            s._get_method("clear")()

class FileOutput(metaclass=FileOutputMata):

    __slots__ = ["name", "path", "fileCache", "correct"]

    def __init__(self, spaceName: str, path: Optional[str] = None, *, stack: bool = False):
        self.name = spaceName

        if not path:
            if spaceName in self.__class__.spacePath:
                path = self.__class__.spacePath[spaceName]
                if not os.path.isabs(path):
                    if self.__class__.__class__.ACTIVATED:
                        raise OSError("param path should be an absolute path")
            else:
                path = spaceName

        if stack:
            path = os.path.abspath(path)
        else:
            path = self.__class__.abspath(path)

        if not os.path.isdir(path):
            os.makedirs(path)
        self.path = path
        self.fileCache = cacheFile()

    def __getattr__(self, key: str) -> Callable:
        if key in self.__class__.FileMethodList:
            return self.__class__.context._get_method(key)
        elif key == "correct":
            raise AttributeError("fetch correct file without opening")
        elif hasattr(self.correct, key):
            return self.correct.__getattribute__(key)

        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{key}'")
    
    def _get_method(self, key: str) -> Callable:
        return self.__class__.__getattribute__(self, "f_" + key)

    @FileFunc
    def activate(self) -> None:
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
    def close(self) -> None:
        self.correct.close()
        del self.fileCache[self.correct.name]
    
    @FileFunc
    def clear(self) -> None:
        self.fileCache.clear()

class MCFunc(FileOutput):

    __slots__ = ["name", "path", "fileCache", "correct", "opened"]

    def __init__(self, spaceName: str, path: Optional[str] = None, *, stack: bool = True):
        self.opened = set()
        super().__init__(spaceName, path=path, stack=stack)
    
    def __enter__(self):
        if hasattr(self.__class__, "context"):
            if self == self.__class__.context:
                return self
        if self.name in self.__class__.spaceStack:
            raise ValueError("enter a space which has been opened in the stack.")

        self.__class__.spaceStack.append(self.name)
        self.__class__[self.name] = self

    def __exit__(self, exc_type: Type, exc_val: BaseException, exc_tb: Any):
        if self.__class__.context != self:
            raise IOError(f"fail to exit from space '{self.name}'")
        self.__class__.exit()

    @FileFunc
    def open(self, path: str, *, mode: str = "w") -> None:
        if not path.endswith(".mcfunction"):
            path += ".mcfunction"
        
        if path in self.opened:
            mode = "a"
        else:
            self.opened.add(path)

        super().f_open(path, mode=mode)

class MCJson(FileOutput):

    @FileFunc
    def write(self, contain: dict) -> int:
        contain = ujson.dumps(contain, indent=4)
        return super().f_write(contain)

if __name__ == "__main__":
    MCFunc.file_struct(
        ".",
        spacePath={"here":"testdatapack", "test1s": "testdatapack/test1"}
    )
    with MCFunc("here"):
        MCFunc.open("hhh")
        MCFunc.write("kill @s\n")
        MCFunc.open("Hello")
        MCFunc.write("say Hello!\n")
        with MCFunc("test"):
            MCFunc.open("h")
            MCFunc.write("say Nothing\n")
            try:
                with MCFunc("here"):
                    pass
            except ValueError:
                print("__enter__ func works well.")
            else:
                raise Exception("uncatch error.")