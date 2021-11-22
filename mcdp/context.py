import asyncio
import warnings
from pathlib import Path
from collections import ChainMap, UserList, defaultdict
from typing import Any, ClassVar, DefaultDict, Dict, List, Literal, Optional, Callable, Union, Type

from .typings import McdpBaseModel, McdpVar
from .config import get_config, get_version
from .aio_stream import Stream, T_Path, wraps
from .counter import get_counter
from .exceptions import McdpError, McdpValueError


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


class ContextEnv(McdpVar):

    __slots__ = ["env_type"]

    path: ClassVar[Path]
    env_counter: DefaultDict[str, int] = defaultdict(lambda:0)

    def __init__(self, env_type: str) -> None:
        self.env_type = env_type
    
    def init(self) -> None:
        config = get_config()
        comment(
            f"Datapack {config.name} built by Mcdp.",
            f"Supported Minecraft version: {config.version}({get_version(config.version)})",

        )
        newline()
    
    def decorate_command(self, cmd: str) -> str:
        return cmd
    
    def creat_stream(self) -> "Context":
        file_name = self.env_type + hex(self.env_counter[self.env_type])
        self.env_counter[self.env_type] += 1
        return Context(file_name, root_path=self.path, envs=self)
    

class ContextMeta(type):
    """
    Metaclass of Context. 
    Support for the sentence of 'with' and the initialization
    of Context.
    """

    MAX_OPENED: int = 8

    stack: StackCache
    environments: list
    enter: staticmethod
    leave: staticmethod

    def init(self, path: T_Path) -> None:
        self.path = Path(path, "functions").resolve()
        ContextEnv.path = self.path / "envs"

    @property
    def top(self) -> "Context":
        if len(self.stack) < 1:
            raise McdpContextError("Class 'Context' should be inited before used.")
        return self.stack[-1]

    async def __aenter__(self) -> "ContextMeta":
        """
        Init the datapack.
        """
        default_env = self("__init__", root_path=self.path, envs=ContextEnv("__init__"))
        await self.stack.append(default_env)
        comment("This is the initize function.")
        newline(2)

        self.enter()
        insert("tag @e[tag=Mcdp_stack] add Mcdp_home")
        TagManager("functions", namespace="minecraft")
        TagManager("functions", namespace=get_namespace())
        insert(f"function {get_namespace()}:__init_score__")
        return self
    
    async def __aexit__(self, exc_type, exc_ins, traceback) -> None:
        await self.stack.clear()
        del self.path
    
    def __str__(self) -> str:
        return f"<{self.__name__} with env {self.top.name}"

class Context(McdpVar, metaclass=ContextMeta):
    """
    Set for async file IO.
    """

    __slots__ = ["name", "stream", "environments"]

    stack = StackCache(ContextMeta.MAX_OPENED)
    file_suffix = ".mcfunction"

    path: Path
    top: "Context"
    enter: ClassVar[staticmethod]
    leave: ClassVar[staticmethod]

    def __init__(
            self,
            name: str, 
            *, 
            root_path: Optional[T_Path] = None, 
            envs: Union[ContextEnv, List[ContextEnv]] = []
    ) -> None:
        self.name = name
        self.stream: Stream = Stream(name + self.file_suffix, root=root_path or self.path)
        if not isinstance(envs, list):
            envs = [envs,]
        self.environments = envs

    def write(self, content: str) -> None:
        self.stream.write(content)

    def writable(self) -> bool:
        return self.stream.writable()

    async def activate(self, append: bool = False) -> None:
        if not append:
            await self.stream.open()
        else:
            await self.stream.open("a")
        for env in self.environments:
            env.init()

    async def deactivate(self) -> None:
        await self.stream.close()

    async def __aenter__(self) -> "Context":
        await self.__class__.stack.append(self)
        return self
    
    async def __aexit__(self, exc_type, exc_ins, traceback) -> None:
        if (await self.__class__.stack.pop()).name == "__init__":
            raise McdpContextError("Cannot leave the static stack '__init__'.")

    @EnvMethod
    def insert(self, *content: str) -> None:
        if not self.writable():
            raise McdpContextError("fail to insert command.")
        counter = get_counter().commands
        for command in content:
            +counter

            if not command.endswith('\n'):
                command += '\n'
            
            if command.count('\n') > 1:
                l_cmd = command.split('\n')[:-1]
                for c in l_cmd:
                    for env in self.environments:
                        c = env.decorate_command(c)
                    self.write(c + '\n')
            else:
                for env in self.environments:
                    command = env.decorate_command(command)
                self.write(command)

    @EnvMethod
    def comment(self, *content: str) -> None:
        if not self.writable():
            raise McdpContextError("fail to add comments.")
        com = []
        for c in content:
            if '\n' in c:
                lc = c.split('\n')
                com.extend(lc)
            else:
                com.append(c)

        self.write("# " + "\n# ".join(com) + '\n')
    
    @EnvMethod
    def newline(self, line: int = 1) -> None:
        self.write('\n' * line)
    
    @EnvMethod
    def add_env(self, env: ContextEnv) -> None:
        self.environments.append(env)
    
    @EnvMethod
    def pop_env(self) -> ContextEnv:
        return self.environments.pop()

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


T_tag = Literal["blocks", "entity_types", "items", "fluids", "functions"]


class TagManager(McdpVar):
    __slots__ = ["name", "type", "replace", "root_path", "cache"]
    __accessible__ = ["type", "replace", "@item"]

    collection: Dict[str, "TagManager"] = {}

    def __init__(self, type: T_tag, *, namespace: Optional[str] = None, replace: bool = False) -> None:
        self.type = type
        self.replace = replace
        if not namespace:
            namespace = get_namespace()
        self.root_path = Path(namespace, "tags", type).resolve()
        self.cache = defaultdict(list)

        self.name = f"{namespace}:{type}"
        self.collect()

    def add(self, tag: str, item: str, *, namaspace: Optional[str] = None) -> None:
        if not ":" in item:
            if not namaspace:
                namaspace = get_namespace()
            item = f"{namaspace}:{item}"

        if item in self.cache[tag]:
            warnings.warn(f"Try to add the tag '{tag}' twice.")
        else:
            self.cache[tag].append(item)

    def __getitem__(self, key: str) -> List[str]:
        return self.cache[key]

    def __setitem__(self, key: str, item: str) -> None:
        self.add(key, item)

    def get_tag_data(self, tag: str, replace: bool = False) -> dict:
        if not tag in self.cache:
            raise McdpContextError(f"Cannot find tag {tag} in the cache.")

        values = self.cache[tag]
        if not replace:
            replace = self.replace
        return {"replace": replace, "values": values}

    async def apply_tag(self, tag: str, *, replace: bool = False) -> None:
        if not tag in self.cache:
            raise McdpContextError(f"Tag {tag} did not defined.")

        async with Stream(tag + ".json", root=self.root_path) as stream:
            await stream.adump(self.get_tag_data(tag, replace))

        del self.cache[tag]

    def apply(self) -> List[asyncio.Task]:
        tl = []
        for tag in self.cache:
            tl.append(asyncio.ensure_future(self.apply_tag(tag)))
        return tl
    
    def collect(self) -> None:
        self.collection[self.name] = self

    @classmethod
    def apply_all(cls) -> asyncio.Future:
        tl = []
        for i in cls.collection.values():
            tl.extend(i.apply())
        return asyncio.gather(*tl)

    def __del__(self) -> None:
        if self.cache:
            self.apply()


def insert(*content: str) -> None:
    Context.insert(*content)


def comment(*content: str) -> None:
    if get_config().pydp.add_comments:
        Context.comment(*content)

def newline(line: int = 1) -> None:
    if get_config().pydp.add_comments:
        Context.newline(line)

def add_tag(
        tag: str, 
        value: Optional[str] = None, 
        *, 
        namespace: Optional[str] = None, 
        type: T_tag = "functions"
) -> None:
    if ':' in tag:
        nt = tag.split(':', 2)
        namespace = nt[0]
        tag = nt[1]
    elif not namespace:
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


def enter_stack_ops(func: Callable[[],None]) -> Callable:
    Context.enter = staticmethod(func)
    return func


def leave_stack_ops(func: Callable[[], None]) -> Callable:
    Context.leave = staticmethod(func)
    return func


class McdpContextError(McdpError):
    __slots__ = ["context", ]

    def __init__(self, *arg: str) -> None:
        self.context = Context
        super(McdpError, self).__init__(*arg)