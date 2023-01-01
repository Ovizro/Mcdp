from typing import Any, Callable, Final, Optional, TypeVar, Union
from typing_extensions import Self

from ..objects import BaseNamespace, McdpObject


class NamePool:
    format: str
    used_size: Final[int]

    def __new__(cls: type[Self], format: Union[str, bytes, None] = ...) -> Self: ...
    def fetch(self) -> str: ...
    def release(self, name: str) -> None: ...


class BaseFrame(McdpObject):
    __namespace__: Final[BaseNamespace]

    def __init__(self, namespace: Optional[BaseNamespace], *, channel: int = 2) -> None: ...
    def __getattribute__(self, __name: str) -> Any: ...
    def __setattr__(self, __name: str, __value: Any) -> None: ...


class FrameVariable(McdpObject):
    __name__: str
    frame: Final[BaseFrame]
    channel_id: Final[int]

    def __init__(self, name: Optional[str] = ..., *, channel: int = 0) -> None: ...
    @property
    def namespace(self) -> BaseNamespace: ...
    @property
    def valid(self) -> bool: ...


class FrameVariableWrapper(FrameVariable):
    def __init_subclass__(cls, *, as_type: Optional[type] = ...) -> None: ...


_T = TypeVar("_T")
def var_builder(_t: type) -> Callable[[_T], _T]: ...
def set_special(frame: BaseFrame, name: str, attr: Any) -> None: ...
