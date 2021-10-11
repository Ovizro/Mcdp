import asyncio
import ujson
from pathlib import Path
from collections import ChainMap, UserList, defaultdict
from typing import Any, Dict, List, Literal, Optional, Callable, Union, Type

from .typings import McdpVar, Variable, McdpError
from .config import get_config
from .aio_stream import Stream, T_Path, wraps
from .counter import get_counter


class ContextManager(McdpVar):
    
    __slots__ = ["name", ]
    __accessible__ = ["name", ]

    collection = {}

    def __init__(self, name: str) -> None:
        self.name = name

    @classmethod
    def _collect(cls, instance: "ContextManager") -> None:
        cls.collection[instance.name] = instance

    @classmethod
    def _remove_from_collection(cls, instance: "ContextManager") -> None:
        cls.collection.pop(instance.name)

    def collect(self) -> None:
        self._collect(self)

    def remove_from_collection(self) -> None:
        self._remove_from_collection(self)

    @staticmethod
    def get_namespace() -> str:
        return get_config().namespace


class Environment(ContextManager):

    __slots__ = ["name", "var_dict", "stream"]
    __accessible__ = ["name", "stream"]

    def __init__(self, name: str, *, root_path: Optional[Union[str, Path]] = None):
        self.name = name
        self.stream: Stream = Stream(name + ".mcfunction", root=root_path)

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
        if instance is None:
            instance = owner.current
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


class Context(ContextManager):

    __slots__ = ["name", "_lock", "stack", "path", "dynamic_stack"]
    __accessible__ = ["name", "stack", "@item"]

    MAX_OPENED: int = 8

    current: Optional["Context"] = None
    collection = {}

    def __init__(
            self,
            name: str,
            path: Union[Path, str],
    ) -> None:
        self.name = name
        self._lock = asyncio.Lock()

        self.collect()

        self.stack: StackCache \
            = StackCache(self.__class__.MAX_OPENED)
        self.dynamic_stack = 0

        self.path = Path(path).resolve()

    @CCmethod
    async def enter(self, env: Union[Environment, str], dir: T_Path = '.') -> None:
        if not isinstance(env, Environment):
            env = Environment(env, root_path=self.path / dir)

        await self.stack.append(env)

    @CCmethod
    async def exit(self, env: Optional[Union[Environment, str]] = None) -> None:
        if env:
            if isinstance(env, Environment):
                if env in self.stack:
                    if not env.name == self.top.name:
                        await self.exit()
                        await self.exit(env)
                else:
                    raise McdpContextError(f"cannot find environment {env} in stack.")
            else:
                if self.top.name != env:
                    raise McdpContextError(f"cannot exit from the environment {env}.")

        if self.stack:
            await self.stack.pop()

    @property
    def top(self) -> Environment:
        if not self.stack:
            raise RuntimeError("no environment in the stack.")
        return self.stack[-1]

    async def shutdown(self) -> None:
        await self.stack.clear()
        del self.stack

        del self.path

        self.remove_from_collection()
        if get_context() is self:
            self.__class__.current = None

    async def __aenter__(self) -> "Context":
        """
        init the datapack.
        """
        await self._lock.acquire()
        self.__class__.current = self

        default = Environment("__init__", root_path=self.path)
        await self.stack.append(default)
        self.insert(
                "function {0}:__init_score__".format(self.get_namespace()),
                "summon armor_stand ~ ~ ~ {0}".format(
                        ujson.dumps({
                            "Invulnerable": True, "Invisible": True, "Marker": True,
                            "NoGravity":    True,
                            "Tags":         ["mcdp_obj", "mcdp_stack_obj", "stack_top", "mcdp_home"]
                        })
                ),
                "scoreboard players set @e[tag=stack_top,limit=1] mcdpStackID 0"
        )
        self.dynamic_stack += 1
        return self

    async def __aexit__(self, *args) -> None:
        await self.stack.clear()
        self._lock.release()

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
            raise McdpContextError("fail to add comments.")
        com = []
        for c in content:
            if "\n" in c:
                lc = c.split("\n")
                com.extend(lc)
            else:
                com.append(c)

        self.stack[-1].write("#" + "\n#".join(com) + "\n")

    @CCmethod
    def dynamic_pull(self) -> None:
        self.insert(
                "tag @s remove stack_top",
                "summon armor_stand ~ ~ ~ {0}".format(
                        ujson.dumps({
                            "Invulnerable": True, "Invisible": True, "Marker": True,
                            "NoGravity":    True, "Tags": ["mcdp_obj", "mcdp_stack_obj", "stack_top"]
                        })
                ),
                "scoreboard players set @e[tag=stack_top,limit=1] mcdpStackID {0}".format(self.dynamic_stack)
        )
        self.dynamic_stack += 1

    @CCmethod
    def dynamic_pop(self) -> None:
        self.dynamic_stack -= 1
        self.insert(
                "tag @e[tag=mcdp_stack_obj,scores={mcdpStackID=%i}] add stack_top" % (self.dynamic_stack - 1),
                "kill @s"
        )

    @CCmethod
    def enter_space(self, name: str) -> None:
        self.path = self.path / name

    @CCmethod
    def exit_space(self) -> None:
        self.path = self.path.parent

    @CCmethod
    def get_relative_path(self) -> Path:
        return self.path.relative_to(Path(f'{self.get_namespace()}/functions').resolve())

    @CCmethod
    def get_stack_id(self) -> int:
        return self.dynamic_stack - 1


T_tag = Literal["blocks", "entity_types", "items", "fluids", "functions"]


class TagManager(ContextManager):
    __slots__ = ["name", "type", "replace", "root_path", "cache"]
    __accessible__ = ["type", "replace", "@item"]

    collection = {}

    def __init__(self, type: T_tag, *, namespace: Optional[str] = None, replace: bool = False) -> None:
        self.type = type
        self.replace = replace
        if not namespace:
            namespace = self.get_namespace()
        self.root_path = Path(namespace, "tags", type).resolve()
        self.cache = defaultdict(set)

        self.name = f"{namespace}:{type}"
        self.collect()

    def add(self, tag: str, item: str, *, namaspace: Optional[str] = None) -> None:
        if not ":" in item:
            if not namaspace:
                namaspace = self.get_namespace()
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

    @classmethod
    def apply_all(cls) -> None:
        for i in cls.collection.values():
            i: TagManager
            i.apply()

    def __del__(self) -> None:
        if self.cache:
            self.apply()


class McdpContextError(McdpError):
    __slots__ = ["context", ]

    def __init__(self, *arg: str) -> None:
        self.context = Context.current
        super(McdpError, self).__init__(*arg)


def get_context() -> "Context":
    if not Context.current:
        raise McdpContextError("no context activated.")
    return Context.current


def insert(*content: str) -> None:
    return Context.insert(*content)


def comment(*content: str) -> None:
    return Context.comment(*content)


def pull_stack(func: Callable) -> None:
    Context.dynamic_pull = CCmethod(func)


def pop_stack(func: Callable) -> None:
    Context.dynamic_pop = CCmethod(func)


get_stack_id = Context.get_stack_id


def add_tag(tag: str, value: Optional[str] = None, *, namespace: Optional[str] = None, type: T_tag = "functions") -> None:
    if not namespace:
        namespace = TagManager.get_namespace()
    if not value:
        if type == "functions":
            c = Context.current
            value = str(c.get_relative_path() / c.top.name)
        else:
            raise ValueError("no value input.")
    m_tag: TagManager = TagManager.collection[f"{namespace}:{type}"]
    m_tag.add(tag, value)
