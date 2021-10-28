import asyncio
import ujson
from pathlib import Path
from collections import ChainMap, UserList, defaultdict
from typing import Any, Dict, List, Literal, Optional, Callable, Union, Type

from .typings import McdpVar, Variable, McdpError
from .config import get_config
from .aio_stream import Stream, T_Path, wraps
from .counter import get_counter


class StackCache(UserList):

    __slots__ = "_capacity",

    def __init__(self, capacity: int = 12):
        if not (1 < capacity <= 128):
            raise ValueError(
                    f"expect the capacity ranging from 2 to 128, but get {capacity}"
            )
        self._capacity = capacity
        super().__init__()

    async def append(self, env: "Context") -> None:
        super().append(env)
        await env.activate()
        overflow = len(self) - self._capacity
        if overflow > 0:
            for e in self[:overflow]:
                await e.deactivate()

    async def pop(self) -> "Context":
        ans: "Context" = super().pop()
        await ans.deactivate()
        if self:
            if not self[-1].writable():
                await self[-1].activate(True)
        return ans

    async def clear(self) -> None:
        for e in self:
            e: "Context"
            await e.deactivate()
        super().clear()


class EnvMethod:
    """
    Use the class as a decorator to
    announce a environment method.
    
    When called from the instance, the method works 
    as a normal method. And when it is called from the 
    class, the param 'self' will input <class>.current as 
    the instance.
    """

    __slots__ = ["__func__", "use_async"]

    def __init__(self, func: Callable):
        self.__func__ = func
        self.use_async = asyncio.iscoroutinefunction(func)

    def __get__(self, instance: Any, owner: "Context") -> Callable:
        if instance is None:
            instance = owner.top
            if not instance:
                raise McdpContextError("invalid current context")

        if self.use_async:
            @wraps(self.__func__)
            async def wrapper(*args, **kw):
                return await self.__func__(instance, *args, **kw)
        else:
            @wraps(self.__func__)
            def wrapper(*args, **kw):
                return self.__func__(instance, *args, **kw)

        return wrapper


class ContextMeta(type):
    """
    Metaclass of Context. 
    Support for the sentence of 'with' and the initialization
    of Context.
    """

    MAX_OPENED: int = 8

    stack: list
    environments: StackCache
    get_stack_id: EnvMethod
    enter: EnvMethod
    leave: EnvMethod

    def init(self, path: T_Path) -> None:
        self.path = Path(path, "functions").resolve()

    @property
    def top(self) -> "Context":
        return self.environments[-1]

    async def __aenter__(self) -> "ContextMeta":
        """
        Init the datapack.
        """
        default_env = self("__init__", root_path=self.path)
        await self.environments.append(default_env)
        TagManager("functions", namespace="minecraft")
        TagManager("functions", namespace=get_namespace())
        insert(f"function {get_namespace()}:__init_score__")
        self.enter()
        return self
    
    async def __aexit__(self, exc_type, exc_ins, traceback) -> None:
        await self.environments.clear()
        del self.path
    
    def __str__(self) -> str:
        return f"<{self.__name__} with env {self.top.name} in stack {self.get_stack_id()}"

class Context(McdpVar, metaclass=ContextMeta):
    """
    Set for async file IO.
    """

    __slots__ = ["name", "stream"]

    stack = []
    environments = StackCache(ContextMeta.MAX_OPENED)

    path: Path
    top: "Context"
    enter: EnvMethod
    leave: EnvMethod

    def __init__(self, name: str, *, root_path: Optional[T_Path] = None):
        self.name = name
        self.stream: Stream = Stream(name + ".mcfunction", root=root_path or self.path)

    def write(self, content: str) -> None:
        self.stream.write(content)

    def writable(self) -> bool:
        return self.stream.writable()

    async def activate(self, append: bool = False) -> None:
        if not append:
            await self.stream.open()
        else:
            await self.stream.open("a")

    async def deactivate(self) -> None:
        await self.stream.close()

    async def __aenter__(self) -> ContextMeta:
        await self.__class__.environments.append(self)
        return self.__class__
    
    async def __aexit__(self, exc_type, exc_ins, traceback) -> None:
        if (await self.__class__.environments.pop()).name == "__init__":
            raise McdpContextError("Cannot leave the static stack '__init__'.")

    @EnvMethod
    def insert(self, *content: str) -> None:
        if not self.writable():
            raise McdpContextError("fail to insert command.")
        counter = get_counter().commands
        for command in content:
            +counter
            if not command.endswith("\n"):
                command += "\n"
            self.write(command)

    @EnvMethod
    def comment(self, *content: str) -> None:
        if not self.writable():
            raise McdpContextError("fail to add comments.")
        com = []
        for c in content:
            if "\n" in c:
                lc = c.split("\n")
                com.extend(lc)
            else:
                com.append(c)

        self.write("#" + "\n#".join(com) + "\n")

    @EnvMethod
    def get_stack_id(self) -> int:
        return self.stack.index(self)

    @classmethod
    def enter_space(cls, name: str) -> None:
        cls.path = cls.path / name

    @classmethod
    def exit_space(cls) -> None:
        cls.path = cls.path.parent

    @classmethod
    def get_relative_path(cls) -> Path:
        return cls.path.relative_to(Path(get_namespace(), "functions").resolve())

    def __str__(self) -> str:
        return f"<env {self.name} in the context>"


_tagType = Literal["blocks", "entity_types", "items", "fluids", "functions"]


class TagManager(McdpVar):
    __slots__ = ["name", "type", "replace", "root_path", "cache"]
    __accessible__ = ["type", "replace", "@item"]

    collection = {}

    def __init__(self, type: _tagType, *, namespace: Optional[str] = None, replace: bool = False) -> None:
        self.type = type
        self.replace = replace
        if not namespace:
            namespace = get_namespace()
        self.root_path = Path(namespace, "tags", type).resolve()
        self.cache = defaultdict(set)

        self.name = f"{namespace}:{type}"
        self.collect()

    def add(self, tag: str, item: str, *, namaspace: Optional[str] = None) -> None:
        if not ":" in item:
            if not namaspace:
                namaspace = get_namespace()
            item = f"{namaspace}:{item}"

        self.cache[tag].add(item)

    def __getitem__(self, key: str) -> set:
        return self.cache[key]

    def __setitem__(self, key: str, item: str) -> None:
        self.add(key, item)

    def get_tag_data(self, tag: str, replace: bool = False) -> dict:
        if not tag in self.cache:
            raise McdpContextError

        values = list(self.cache[tag])
        if not replace:
            replace = self.replace
        return {"replace": replace, "values": values}

    async def apply_tag(self, tag: str, *, replace: bool = False) -> None:
        if not tag in self.cache:
            raise McdpContextError

        async with Stream(tag + ".json", root=self.root_path) as stream:
            await stream.adump(self.get_tag_data(tag, replace))

        del self.cache[tag]

    def apply(self) -> None:
        for tag in self.cache:
            asyncio.ensure_future(self.apply_tag(tag))
    
    def collect(self) -> None:
        self.collection[self.name] = self

    @classmethod
    def apply_all(cls) -> None:
        for i in cls.collection.values():
            i: TagManager
            i.apply()

    def __del__(self) -> None:
        if self.cache:
            self.apply()


def insert(*content: str) -> None:
    return Context.insert(*content)


def comment(*content: str) -> None:
    return Context.comment(*content)


def get_stack_id() -> int:
    return len(Context.stack) - 1


def add_tag(tag: str, value: Optional[str] = None, *, namespace: Optional[str] = None, type: _tagType = "functions") -> None:
    if not namespace:
        namespace = get_namespace()
    if not value:
        if type == "functions":
            c = Context.top
            value = str(c.get_relative_path() / c.name)
        else:
            raise McdpError("no value input.")
    m_tag: TagManager = TagManager.collection[f"{namespace}:{type}"]
    m_tag.add(tag, value)


def get_namespace() -> str:
    return get_config().namespace


def enter_stack_ops(func: Callable[[Context],None]) -> Callable:
    Context.enter = EnvMethod(func)
    return func


def leave_stack_ops(func: Callable[[Context], None]) -> Callable:
    Context.leave = EnvMethod(func)
    return func


class McdpContextError(McdpError):
    __slots__ = ["context", ]

    def __init__(self, *arg: str) -> None:
        self.context = Context
        super(McdpError, self).__init__(*arg)