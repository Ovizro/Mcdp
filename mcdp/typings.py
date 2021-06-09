""""
All base classes of Mcdp variable.
"""

import sys
import ujson
from abc import ABCMeta, abstractmethod
from pydantic import BaseModel, BaseConfig
from typing import Any, Union, Optional

from .version import VersionError, __version__
from .counter import Counter

class McdpVar:
    
    __accessible__: list = []
    
    def get_attr(self, key: str) -> Any:
        if not key in self.__class__.__accessible__:
            raise McdpError
        return self.__getattribute__(key)

"""
==============================
Mcdp Variables
==============================
"""

class Variable(McdpVar, metaclass=ABCMeta):

    __slots__ = ["counter", "linked"]

    @abstractmethod
    def __init__(self) -> None:
        self.counter = Counter()
        self.linked = set()
        
    @abstractmethod
    def apply(self) -> None:
        raise NotImplementedError

    def link(self, var: Union["Variable", Counter]) -> None:
        if isinstance(var, self.__class__):
            var = var.counter
        if var == self.counter:
            raise RuntimeError("try linking a var to itself.")
        elif var in self.linked:
            return
        
        self.linked.add(var)

    def unlink(self, var: Union["Variable", Counter]) -> None:
        if isinstance(var, self.__class__):
            var = var.counter
        if var == self.counter:
            raise RuntimeError("try unlinking a var from itself.")
        elif not var in self.linked:
            raise RuntimeError("has not linked with the variabvle yet.")
        
        self.linked.remove(var)
        
    def used(self) -> bool:
        return any(self.linked)

"""
==============================
Mcdp config
==============================
"""

class McdpConfig(McdpVar, BaseModel):
    __accessible__ = ["@all.attr",]
    
    class Config(BaseConfig):
        arbitrary_types_allowed = True
        json_loads = ujson.loads
        json_dumps = ujson.dumps

"""
==============================
Mcdp Exceptions
==============================
"""

class McdpError(VersionError, McdpVar):
    
    __slots__ = ["version", "python_version"]
    
    def __init__(self, *arg: str, **kw) -> None:
        self.python_version = sys.version
        super().__init__(*arg, version=__version__)
        
class McdpVersionError(McdpError):

    def __init__(self, msg: Optional[str] = None) -> None:
        if msg:
            super().__init__(
                msg.format(mcdp_version=__version__))
        else:
            super().__init__()