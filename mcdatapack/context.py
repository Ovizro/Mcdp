import asyncio
from pathlib import PurePath
from collections import ChainMap
from abc import ABCMeta, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Union

from .variable import Variable
from .aio_stream import Stream, wraps
from .exception import McdpContextError

class Environment:

    __slots__ = ["name", "var_list", "stream", "active", "closed"]

    def __init__(self, name: str, *, root_path: Optional[Union[str, PurePath]] = None):
        self.name = name
        self.var_list: Dict[str, Variable] = {}
        self.stream: Stream = Stream(name, root=root_path)
        self.active = True
        self.closed = False

    def __getitem__(self, key: str) -> Variable:
        if not key in self.var_list:
            raise AttributeError(f"unfound var {key} in env {self.name}")
        return self.var_list[key]

    def __setitem__(self, name: str, instance: Variable) -> None:
        if not self.active:
            raise McdpContextError
        if name in self.var_list:
            if self.var_list[name] == instance:
                return
        self.var_list[name] = instance

    def write(self, content: str) -> None:
        self.stream.write(content)
        
    def writable(self) -> bool:
        return self.active and not self.closed

    async def activate(self) -> None:
        self.closed = False
        await self.stream.open()
        self.active = True
    
    async def exit(self) -> None:
        self.active = False
        await self.stream.close()
        self.closed = True
        
    async def __aenter__(self) -> "Environment":
        await self.activate()
        return self
        
    async def __aexit__(self, *args)  -> None:
        await self.exit()

    def __str__(self) -> str:
        return f"<env {self.name} in the context {get_context().name}>"

class StackCache(list):
    
    __slots__ = "_capacity", 
    
    def __init__(self, capacity: int = 12):
        if not (1 < capacity <= 128):
            raise ValueError(
                f"expect the capacity ranging from 2 to 128, but get {capacity}"
            )
        self._capacity = capacity
        super().__init__()
        
    async def append(self, env: Environment) -> None:
        super().append(env)
        overflow = len(self) - self._capacity
        if overflow > 0:
            for e in self[:overflow]:
                await e.exit()

    async def pop(self) -> Environment:
        ans: Environment = super().pop()
        await ans.exit()
        if self:
            if not self[-1].writable():
                await self[-1].activate()
        return ans

class CCmethod:
    """
    Use the class as a decorator to
    announce a current context method.
    
    When called from the instance, the method works 
    as a normal method. And when it is called from the 
    class, the param 'self' will input <class>.current as 
    the instance.
    """
    
    __slots__ = ["__func__", "use_async"]
    
    def __init__(self, func: Callable):
        self.__func__ = func
        self.use_async = asyncio.iscoroutinefunction(func)
    
    def __get__(self, instance: Any, owner: type) -> Callable:
        if instance is None:
            instance = owner.current
            
        if self.use_async:
            @wraps(self.__func__)
            async def wrapper(*args, **kw):
                return await self.__func__(instance, *args, **kw)
        else:
            @wraps(self.__func__)
            def wrapper(*args, **kw):
                return self.__func__(*args, **kw)
        
        return wrapper

class AbstractContext(metaclass=ABCMeta):
    
    __slots__ = ["name", "_lock"]
    
    current: Optional["AbstractContext"] = None
    collection: Dict[str, "AbstractContext"] = {}
    
    @abstractmethod
    def __init__(self, name: str, *args, **kwargs) -> None:
        self.name = name
        self._lock = asyncio.Lock()
    
    @abstractmethod
    def enter(self, env: Union[Environment, str], *args, **kwargs) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def exit(self, env: Optional[Union[Environment, str]] = None, *args, **kwargs) -> None:
        raise NotImplementedError
    
    async def __aenter__(self) -> "AbstractContext":
        await self._lock.acquire()
        return self
    
    def __aexit__(self, *args) -> None:
        self._lock.release()

    @classmethod
    def collect_context(cls, instance: "AbstractContext") -> None:
        cls.collection[instance.name] = instance

    @classmethod
    def get_context(cls) -> "AbstractContext":
        if not cls.current:
            raise McdpContextError
        return cls.current
        
class Context(AbstractContext):

    __slots__ = ["name", "stack", "path", "var_map"]
    
    MAX_OPENED: int = 8

    def __init__(
        self, 
        name: str, 
        path: Union[PurePath, str],
    ) -> None:
        super().__init__(name)
        
        self.collect_context(self)
        
        if not self.__class__.current:
            self.__class__.current = self
        
        self.stack: Union[List[Environment], StackCache] \
            = StackCache(self.__class__.MAX_OPENED)
        self.var_map = ChainMap()
        
        if not Stream.pathtools.isabs(path):
            path = Stream.pathtools.abspath(path)
        if not isinstance(path, PurePath):
            self.path = PurePath(path)
        else:
            self.path: PurePath = path
            
    def enter(self, env: Union[Environment, str]) -> None:
        if not isinstance(env, Environment):
            env = Environment(env, root_path=self.path)
            
        self.stack.append(env)
        self.var_map.new_child(env.var_list)
        self.path.joinpath(env.name)
    
    def exit(self, env: Optional[Union[Environment, str]] = None) -> None:
        if env:
            if isinstance(env, Environment):
                if env in self.stack:
                    if not env.name == self.stack[-1].name:
                        self.exit()
                        self.exit(env)
                else:
                    raise McdpContextError
            else:
                if self.stack[-1].name != env:
                    raise McdpContextError
        
        self.stack.pop()
        self.var_map = self.var_map.parents
        self.path = self.path.parent
        
    @CCmethod
    def insert(self, *content: str) -> None:
        if not self.stack[-1].writable():
            raise McdpContextError
            
    @CCmethod
    def comment(self, content: str) -> None:
        pass

get_context = Context.get_context
insert = Context.insert
comment = Context.comment
'''
from io import StringIO
from .file_struct import BuildDirs

def insert(*contents: str) -> None:
    """
    Insert commends into correct context.
    When context is not writeable, throw OSError.
    """
    if not MCFunc.writable():
        raise OSError("cannot insert command.")
    
    content: str = '\n'.join(contents)
    if not content.endswith("\n"): 
        content += "\n"
    MCFunc.write(content)

_textCache = StringIO()
    
def comment(content: str) -> None:
    """
    Make a comment in correct file.
    """
    if not MCFunc.writable():
        raise OSError("cannot comment.")

    if '\n' in content:
        l = content.split("\n")
        MCFunc.write("#" + "\n#".join(l)+"\n")
    else:
        MCFunc.write('#'+content+"\n")
'''