import asyncio
from pathlib import PurePath
from collections import ChainMap, UserList
from abc import ABCMeta, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Union, Type

from .variable import Variable
from .aio_stream import Stream, wraps
from .counter import get_counter
from .exception import McdpContextError

class AbstractEnvironment(metaclass=ABCMeta):
    
    __slots__ = ["name", "stream"]
    
    def __init__(self, name: str, *, root_path: Optional[Union[str, PurePath]] = None): 
        self.name = name
        self.stream = Stream(name, root=root_path)

class Environment(AbstractEnvironment):

    __slots__ = ["name", "var_dict", "stream"]

    def __init__(self, name: str, *, root_path: Optional[Union[str, PurePath]] = None):
        self.name = name
        self.var_dict: Dict[str, Variable] = {}
        self.stream: Stream = Stream(name, root=root_path)

    def __getitem__(self, key: str) -> Variable:
        if not key in self.var_dict:
            raise AttributeError(f"unfound var {key} in env {self.name}")
        return self.var_dict[key]

    def __setitem__(self, name: str, instance: Variable) -> None:
        if not self.writable():
            raise McdpContextError
        if name in self.var_dict:
            if self.var_dict[name] == instance:
                return
        self.var_dict[name] = instance

    def write(self, content: str) -> None:
        self.stream.write(content)
        
    def writable(self) -> bool:
        return self.stream.writable()

    async def activate(self) -> None:
        await self.stream.open()
    
    async def deactivate(self) -> None:
        await self.stream.close()
        
    def __str__(self) -> str:
        return f"<env {self.name} in the context {get_context().name}>"

class StackCache(UserList):
    
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
        await env.activate()
        overflow = len(self) - self._capacity
        if overflow > 0:
            for e in self[:overflow]:
                await e.deactivate()

    async def pop(self) -> Environment:
        ans: Environment = super().pop()
        await ans.deactivate()
        if self:
            if not self[-1].writable():
                await self[-1].activate()
        return ans
        
    async def clear(self) -> None:
        for e in self:
            e: Environment
            await e.deactivate()
        super().clear()

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
    
    def __get__(self, instance: Any, owner: Type) -> Callable:
        if self.use_async:
            @wraps(self.__func__)
            async def wrapper(*args, **kw):
                if instance is None:
                    instance = owner.current
                    if not instance:
                        raise McdpContextError("invalid current context")
                        
                return await self.__func__(instance, *args, **kw)
        else:
            @wraps(self.__func__)
            def wrapper(*args, **kw):
                if instance is None:
                    instance = owner.current
                    if not instance:
                        raise McdpContextError("invalid current context")
                        
                return self.__func__(instance, *args, **kw)
                
        return wrapper

class AbstractContext(metaclass=ABCMeta):
    
    __slots__ = ["name", "_lock", "root_path"]
    
    current: Optional["AbstractContext"] = None
    collection: Dict[str, "AbstractContext"] = {}
    root_path: Optional[PurePath] = None
    
    @abstractmethod
    def __init__(self, name: str, *args, **kwargs) -> None:
        self.name = name
        self._lock = asyncio.Lock()
    
    @abstractmethod
    async def enter(self, env: Union[Environment, Stream, str], *args, **kwargs) -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def exit(self, env: Optional[Union[Environment, Stream, str]] = None, *args, **kwargs) -> None:
        raise NotImplementedError
        
    @abstractmethod
    async def shutdown(self) -> None:
        raise NotImplementedError
    
    async def __aenter__(self) -> "AbstractContext":
        await self._lock.acquire()
        self.__class__.current = self
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
        
        self.stack: StackCache \
            = StackCache(self.__class__.MAX_OPENED)
        self.var_map = ChainMap()
        
        if not Stream.pathtools.isabs(path):
            path = Stream.pathtools.abspath(path)
        if not isinstance(path, PurePath):
            self.path = PurePath(path)
        else:
            self.path: PurePath = path
            
    async def enter(self, env: Union[Environment, str]) -> None:
        if not isinstance(env, Environment):
            env = Environment(env, root_path=self.path)
            
        await self.stack.append(env)
        self.var_map.new_child(env.var_dict)
        self.path.joinpath(env.name)
    
    async def exit(self, env: Optional[Union[Environment, str]] = None) -> None:
        if env:
            if isinstance(env, Environment):
                if env in self.stack:
                    if not env.name == self.stack[-1].name:
                        await self.exit()
                        await self.exit(env)
                else:
                    raise McdpContextError
            else:
                if self.stack[-1].name != env:
                    raise McdpContextError
        
        await self.stack.pop()
        self.var_map = self.var_map.parents
        self.path = self.path.parent
    
    def __getitem__(self, key: str) -> Variable:
        return self.var_map[key]
    
    def __setitem__(self, key: str, value: Variable) -> None:
        self.var_map[key] = value
    
    async def shutdown(self) -> None:
        await self.stack.clear()
        del self.stack
        
        self.var_map.clear()
        del self.path
        
        self.__class__.collection.pop(self.name)
        if self.get_context() is self:
            self.__class__.current = None
    
    @CCmethod
    def insert(self, *content: str) -> None:
        if not self.stack[-1].writable():
            raise McdpContextError("fail to insert command.")
        counter = get_counter().commands
        for command in content:
            +counter
            if not command.endswith("\n"):
                command += "\n"
            self.stack[-1].write(command)
            
    @CCmethod
    def comment(self, *content: str) -> None:
        if not self.stack[-1].writable():
            raise McdpContextError("fail to add the comment.")
        com = []
        for c in content:
            if "\n" in c:
                lc = c.split("\n")
                com.extend(lc)
            else:
                com.append(c)
        
        self.stack[-1].write("#" + "\n#".join(com) + "\n")

class JsonContext(AbstractContext):
    
    __slots__ = ["name", ]
    

get_context = Context.get_context
insert = Context.insert
comment = Context.comment