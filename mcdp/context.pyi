import os
from typing import Any, Callable, ClassVar, DefaultDict, Dict, Final, List, Literal, Optional, Type
import warnings
from collections import defaultdict
from functools import wraps

from .typing import McdpVar
from .config import get_config
from .exceptions import McdpValueError


T_tag = Literal["blocks", "entity_types", "items", "fluids", "functions"]


class StackCache(list):

    def __init__(self, capacity: int = ...) -> None: ...
    def append(self, __object: "Context") -> None: ...
    def pop(self) -> "Context": ...
    def clear(self) -> None: ...


class EnvMethod:
    """
    Use the class as a decorator to
    announce a environment method.
    
    When called from the instance, the method works 
    as a normal method. And when it is called from the 
    class, the param 'self' will input <class>.current as 
    the instance.
    """

    def __init__(self, func: Callable): ...
    def __get__(self, instance: "Context", owner: Type["Context"]) -> Callable: ...


class EnvProperty(EnvMethod):
    def __get__(self, instance: "Context", owner: Type["Context"]) -> Any: ...


class Handler(McdpVar):
    env_counter: ClassVar[DefaultDict[str, int]] = ...
    env_type: str

    def __init__(self, env_type: str) -> None: ...
    def init(self) -> None: ...
    def command(self, cmd: str) -> str: ...
    def stream(self) -> "Context": ...


class Context(McdpVar):

    file_suffix: ClassVar[str] = ...

    def __init__(
        self, name: str, 
        *, root_path: Optional[str] = None, hdls = ...) -> None: ...
    def write(self, content: str) -> None: ...
    def writable(self) -> bool: ...
    def activate(self, append: bool = False) -> None: ...
    def deactivate(self) -> None: ...
    def __enter__(self) -> "Context": ...
    def __exit__(self, exc_type, exc_ins, traceback) -> None: ...

    @EnvProperty
    def top(cls) -> "Context": ...
    @EnvProperty
    def stacks(cls) -> StackCache: ...
    @EnvMethod
    def insert(self, *content: str) -> None: ...
    @EnvMethod
    def comment(self, *content: str) -> None: ...
    @EnvMethod
    def newline(self, line: int = ...) -> None: ...
    @EnvMethod
    def add_env(self, hdl: Handler) -> None: ...
    @EnvMethod
    def pop_env(self) -> Handler: ...

    @staticmethod
    def enter_space(name: str) -> None: ...
    @staticmethod
    def exit_space() -> None: ...
    @staticmethod
    def get_relative_path(): ...


class TagManager(McdpVar):
    __accessible__: ClassVar[Dict[str, int]] = ...
    collections: ClassVar[Dict[str, "TagManager"]] = ...

    def __init__(
        self, type: T_tag, 
        *, namespace: Optional[str] = None, replace: bool = False) -> None: ...
    def add(self, tag: str, item: str, namespace: Optional[str] = None) -> None: ...
    def __getitem__(self, key: str) -> List[str]: ...
    def __setitem__(self, key: str, item: str) -> None: ...
    def get_tag_data(self, tag: str, replace: bool = False) -> Dict[str, Any]: ...
    def apply_tag(self, tag: str, replace: bool = False) -> None: ...
    def apply(self) -> None: ...
    @classmethod
    def apply_all(cls) -> None: ...
    def __del__(self) -> None: ...

def insert(*content: str) -> None: ...
def comment(*content: str) -> None: ...
def newline(line: int = 1) -> None: ...
def add_tag(
        tag: str, 
        value: Optional[str] = None, 
        *, 
        namespace: Optional[str] = None, 
        type: T_tag = ...
) -> None: ...