from types import MappingProxyType
from typing import Any, Callable, Dict, Final, Generator, Generic, Iterable, Type, TypeVar, Union, Literal, Protocol, overload, runtime_checkable
from typing_extensions import Self

from ..objects import McdpObject
from .mcstring import EntityNameString


_T_SLN = Literal["@p", "@a", "@r", "@e", "@s"]
@runtime_checkable
class SelectorLike(Protocol):
    def __selector__(self) -> Selector:
        pass

T_Selector = Union[str, Selector, SelectorLike]


class Selector(McdpObject):
    name: _T_SLN

    def __new__(cls: Type[Self], name: _T_SLN, _iter: Union[Dict[str, Any], Iterable] = ..., **kwds: Any) -> Self: ...
    def add_args(self, key: str, value: Any) -> None: ...
    @classmethod
    def __get_validators__(cls) -> Generator[Callable, None, None]: ...
    @classmethod
    def validate(cls, val: T_Selector) -> Selector: ...
    @property
    def args(self) -> MappingProxyType[str, Any]: ...
    def __selector__(self) -> Selector: ...
    def __mcstr__(self) -> EntityNameString: ...


@overload
def selector(t_slt: T_Selector) -> Selector: ...
@overload
def selector(t_slt: _T_SLN, _iter: Union[Dict[str, Any], Iterable] = ..., **kwds: Any) -> Selector: ...


s_all: Selector     = Selector("@a")
s_nearest: Selector = Selector("@p")
s_entity: Selector  = Selector("@e")
s_current: Selector = Selector("@s")