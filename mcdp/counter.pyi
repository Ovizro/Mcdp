from typing import List, Optional, Union


class Counter:
    value: int
    name: Optional[str]

    def __init__(self, name: Optional[str] = None, init: int = 0) -> None: ...
    def link_to(self, other: "Counter") -> None:...
    @property
    def linked(self) -> List["Counter"]:...

    def __pos__(self):...
    def __neg__(self):...
    def __invert__(self):...
    def __add__(self, other: Union[int, "Counter"]) -> int:...
    __radd__ = __add__
    def __iadd__(self, other: Union[int, "Counter"]) -> "Counter":...
    def __sub__(self, other: Union[int, "Counter"]) -> int:...
    def __rsub__(self, other: int) -> int:...
    def __isub__(self, other: Union[int, "Counter"]) -> "Counter":...
    def __int__(self) -> int:...
    __index__ = __int__
    def __bool__(self) -> bool:...
    def __repr__(self) -> str:...
    def __str__(self) -> str:...


class ContextCounter(object):
    dirs: Counter
    files: Counter
    commands: Counter
    chars: Counter

    def __init__(self) -> None:...
    def reset(self) -> None:...
    def print_out(self) -> None:...


def get_counter() -> Counter:...