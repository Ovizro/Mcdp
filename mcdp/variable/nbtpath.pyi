from typing import Final, Optional, Tuple, Union
from typing_extensions import Self

from ..objects import McdpObject


class PathNode:
    name: Final[str]
    next: Final[Optional[PathNode]]

    def __new__(cls: type[Self], name: str, next: Optional[PathNode] = None) -> Self: ...
    def copy(self, depth: int = ...) -> Self: ...


class NBTPath(McdpObject):
    named_tags: Final[Tuple[str, ...]]

    def __new__(cls: type[Self], path: Union[str, PathNode, None]) -> Self: ...
    def __getitem__(self, key: int) -> NBTPath: ...
    def __len__(self) -> int: ...



def nbtpath(path: Union[str, PathNode, None] = ...) -> NBTPath: ...