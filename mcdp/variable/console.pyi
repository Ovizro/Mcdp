from ..objects import McdpObject
from .mcstring import T_MCString
from .selector import T_Selector


class _Console(McdpObject):
    @staticmethod
    def print(*texts: T_MCString, sep: T_MCString = ..., target: T_Selector = ...) -> None: ...
    @staticmethod
    def title(*texts: T_MCString, sep: T_MCString = ..., target: T_Selector = ...) -> None: ...
    @staticmethod
    def subtitle(*texts: T_MCString, sep: T_MCString = ..., target: T_Selector = ...) -> None: ...
    @staticmethod
    def actionbar(*texts: T_MCString, sep: T_MCString = ..., target: T_Selector = ...) -> None: ...
    @staticmethod
    def reset_title(target: T_Selector = ...) -> None: ...
    @staticmethod
    def set_time(fadeIn: int, stay: int, fadOut: int, target: T_Selector = ...) -> None: ...


console: _Console