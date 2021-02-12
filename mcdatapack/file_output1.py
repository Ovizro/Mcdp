import io
import os
import sys
from collections import OrderedDict, defaultdict
from functools import partial
from typing import IO, Any, Optional, TypeVar, Union

_is_stdio = lambda i: isinstance(i, io.TextIOWrapper) or isinstance(i, io.StringIO)
stdio = Union[io.TextIOWrapper, io.StringIO]

def file_open(path: str, mode: str = 'w', **kw):
    if not os.path.isfile(path):
        p = os.path.split(path)
        if not os.path.isdir(p[0]):
            os.makedirs(p[0])
    return open(path, mode, **kw)

class __get_fsk(property):
    
    def __init__(self, key: str):
        def fetch(instance) -> stdio:
            if key in instance.cache:
                return instance.cache[key]
            elif key in instance._storage_:
                path = instance._storage_[key]
                if _is_stdio(path):
                    return path
                else:
                    f = open(path, 'a')
                    instance.cache[key] = f
                    return f                    
            else:
                return sys.stdout
        def setter(instance, value: Any) -> None:
            instance.__class__._storage_[key] = value
        def deleter(instance):
            del instance.__class__._storage_[key]
        super().__init__(fetch, setter, deleter)
        
class __get_fp(property):
    
    def __init__(self, key: str):
        def fetch(instance) -> stdio:
            if key in instance.cache:
                return instance.cache[key]
            elif key in instance._storage_:
                path = instance._storage_[key]
                if _is_stdio(path):
                    return path
                else:
                    f = open(path, 'a')
                    instance.cache[key] = f
                    return f                    
            else:
                return sys.stdout
        def setter(instance, value: Any) -> None:
            instance.__class__._storage_[key] = value
        def deleter(instance):
            del instance.__class__._storage_[key]
        super().__init__(fetch, setter, deleter)

class cacheFile(OrderedDict):
    
    __slots__ = ['_capacity', ]
    
    def __init__(self, capacity: int = 7):
        self._capacity = capacity
        super().__init__()
    
    def __getitem__(self, key) -> Any:
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
                if callable(f.close):
                    f.close()
        return overflow
    
    def clear(self) -> None:
        while len(self) > 0:
            k,v = self.popitem()
            if hasattr(v, 'close'):
                if callable(v.close):
                    v.close()
        super().clear()

class OutputMetaclass(type):
    
    def __new__(cls, name: str, bases: tuple, attrs: dict):
        attrs.update(
            _cache_ = cacheFile(3),
            _storage_ = defaultdict(lambda: {'load':'load.mcfunction', 'prepare':'prepare.mcfunction'}),
            _path_ = defaultdict(lambda: '.')
        )
        return type.__new__(cls, name, bases, attrs)
    
    def __getitem__(self, space: str) -> Any:
        os.chdir(self._path_[space])
        if space in self._cache_:
            self.switchTo(space)
        else:
            self.newSpace(space)
        return self
        
    def __setitem__(self, space: str, value: str) -> None:
        self._storage_[space] = value
        
    def setting(self, path: dict, file_struct: dict) -> None:
        self._storage_.update(**file_struct)
        for k,v in path.items():
            p = os.path.abspath(v)
            os.makedirs(p, exist_ok=True)
            self._path_[k] = p
        
        self.main = self('__main__')
        
    def newSpace(self, space: str) -> None:
        ins = self(space)
        self.currentSpace = ins
        self._cache_[ins.name] = ins
    
    def switchTo(self, space: str) -> None:
        self.currentSpace = self._cache_[space]
    
    def open(self, path: str) -> None:
        self.currentSpace.fetchfile(path)
    
    def write(self, *args, **kwargs) -> int:
        return self.currentSpace.Write(**args, **kwargs)

    def clear(self) -> None:
        self._cache_.clear()

class output(object, metaclass=OutputMetaclass):
    
    __slots__ = ["name", "currentFile", 'file_struct', "cache"]
    
    def __init__(self, space: str, *, path: Optional[str] = None):
        self.name = space
        if path:
            os.chdir(path)
        self.file_struct = self.__class__._storage_[space]
        self.cache = cacheFile()
    
    def Write(
        self, 
        contains: str,
        *, 
        ftype: str = 'file',
        env: Optional[str] = None
    ) -> int:
        ...
            
    def newfile(self, path: str) -> None:
        f = file_open(path)
        self.currentFile = f
        self.cache[path] = f

    def fetchfile(self, path: str) -> None:
        if path in self.cache:
            self.currentFile = self.cache[path]
        else:
            self.newfile(path)
    
    def close(self) -> None:
        self.cache.clear()

def output(contain: str, *, files: Union[stdio, str]):
    print(contain)

def load(
    cmd: Optional[str] = None,
    *,
    scoreboard: Optional[str] = None,
    criteria: str = 'dummy',
    display: Union[dict, str] = ''
    ):
    if not cmd.endswith('\n'):
        cmd += '\n'
    if scoreboard:
        cmd += "scoreboard objectives add {0} {1} {2}\n".format(scoreboard, criteria, display)
