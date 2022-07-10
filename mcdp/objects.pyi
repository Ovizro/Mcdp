import types
from typing import Any, Callable, Final, overload


T_Nspp_F = Callable[[BaseNamespace], Any]

class McdpObject(object):
    pass


class BaseNamespace(McdpObject):
    n_name: Final[str]
    n_path: Final[bytes]

    def __init__(self, name: str) -> None: ...
    def __getattr__(self, name: str) -> Any: ...
    @staticmethod
    @overload
    def property(attr: str) -> Callable[[T_Nspp_F], T_Nspp_F]: ...
    @staticmethod
    @overload
    def property(attr: T_Nspp_F) -> T_Nspp_F: ...