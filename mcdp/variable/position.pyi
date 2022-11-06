from enum import Enum
from typing import Callable, Final, Generator, Iterable, Iterator, Tuple, Type, Union, overload
from typing_extensions import Self

from ..objects import McdpObject


class ComponentType(Enum):
    local = ...
    relative = ...
    absolute = ...

T_Component = Union[str, int, float, Component]


class Component(McdpObject):
    offset: Final[float]
    type: Final[ComponentType]

    def __new__(cls: Type[Self], value: Union[str, int, float], *, type: Union[ComponentType, int] = ...) -> Self: ...
    def __add__(self, other: Union[int, float, Component]) -> Self: ...
    def __radd__(self, other: Union[int, float, Component]) -> Self: ...
    def __sub__(self, other: Union[int, float, Component]) -> Self: ...
    def __rsub__(self, other: Union[int, float, Component]) -> Self: ...
    def __mul__(self, other: Union[int, float, Component]) -> Self: ...
    def __rmul__(self, other: Union[int, float, Component]) -> Self: ...
    def __truediv__(self, other: Union[int, float, Component]) -> Self: ...
    def __rtruediv__(self, other: Union[int, float, Component]) -> Self: ...
    def __pos__(self) -> Self: ...
    def __neg__(self) -> Self: ...
    def __abs__(self) -> Self: ...
    def __float__(self) -> float: ...


class Position(McdpObject):
    components: Final[Tuple[Component]]
    type: Final[ComponentType]

    def __new__(cls: Type[Self], val: Union[str, Iterable[T_Component], None] = ..., *, 
        x: T_Component = ..., y: T_Component = ..., z: T_Component = ..., type: Union[ComponentType, int] = ...) -> Self: ...
    @property
    def x(self) -> Component: ...
    @property
    def y(self) -> Component: ...
    @property
    def z(self) -> Component: ...
    @classmethod
    def __get_validators__(cls) -> Generator[Callable, None, None]: ...
    @classmethod
    def validate(cls, val: Union[str, "Position"]) -> Position: ...
    def __add__(self, other: Union[int, float, Position]) -> Self: ...
    def __radd__(self, other: Union[int, float, Position]) -> Self: ...
    def __sub__(self, other: Union[int, float, Position]) -> Self: ...
    def __rsub__(self, other: Union[int, float, Position]) -> Self: ...
    def __mul__(self, other: Union[int, float, Iterable[T_Component]]) -> Self: ...
    def __rmul__(self, other: Union[int, float, Iterable[T_Component]]) -> Self: ...
    def __truediv__(self, other: Union[int, float, Iterable[T_Component]]) -> Self: ...
    def __rtruediv__(self, other: Union[int, float, Iterable[T_Component]]) -> Self: ...
    def __pos__(self) -> Self: ...
    def __neg__(self) -> Self: ...
    def __abs__(self) -> Self: ...
    def __iter__(self) -> Iterator[Component]: ...


@overload
def position(string: Union[str, Iterable[T_Component]], *, type: Union[ComponentType, int] = ...) -> Position: ...
@overload
def position(x: T_Component, y: T_Component, z: T_Component, *, type: Union[ComponentType, int] = ...) -> Position: ...
