from typing import Any, ClassVar, Dict, Final, Optional

from .version import Version, __version__
from .counter import Counter


class McdpVar:
    __accessible__: ClassVar[Dict[str, int]]


class _McdpBaseModel(McdpVar):
    def to_dict(self) -> Dict[str, Any]: ...
    def json(self) -> str: ...


class Variable(McdpVar):
    counter: Final[Counter]

    def __init__(self, counter: Optional[Counter] = None) -> None: ...
    def link(self, other: "Variable") -> None: ...
    def used(self) -> bool: ...
    def __repr__(self) -> str: ...


class McdpError(Exception):
    version: Final[Version]

    def __init__(self, *args: object) -> None: ...