from typing import Final, Literal, Optional, Union
from typing_extensions import Self

from ..objects import McdpObject
from .mcstring import T_MCString, BaseString


class Scoreboard(McdpObject):
    name: Final[str]
    criteria: Final[str]
    display_name: Final[Optional[BaseString]]

    def __new__(cls: type[Self], name: str, *, criteria: str = ..., display: Optional[T_MCString] = ...) -> Self: ...
    def add(self) -> None: ...
    def remove(self) -> None: ...
    def display(self, pos: Union[Literal["list", "sidebar", "belowName"], str]) -> None: ...
