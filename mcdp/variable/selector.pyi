from types import MappingProxyType
from typing import Any, Callable, Dict, Final, Generator, Iterable, Union, Literal, Protocol

from ..objects import McdpObject
from .mcstring import String


class SelectorLike(Protocol):
    def __selector__(self) -> Selector:
        pass

T_Selector = Union[str, Selector, SelectorLike]


class Selector(McdpObject):
    name: Final[Literal["@p", "@a", "@r", "@e", "@s"]]
    args: Final[MappingProxyType[str, Any]]

    def __init__(self, name: str, _iter: Union[Dict[str, Any], Iterable] = ..., **kwds: Any) -> None: ...
    def add_args(self, key: str, value: Any) -> None: ...
    @classmethod
    def __get_validators__(cls) -> Generator[Callable, None, None]: ...
    @classmethod
    def validate(cls, val: T_Selector) -> Selector: ...
    def __selector__(self) -> Selector: ...
    def __mcstr__(self) -> String: ...


def selector(t_slt: T_Selector, _iter: Union[Dict[str, Any], Iterable] = ..., /, **kwds: Any) -> Selector: ...

s_all: Selector     = Selector("@a")
s_nearest: Selector = Selector("@p")
s_entity: Selector  = Selector("@e")
s_current: Selector = Selector("@s")