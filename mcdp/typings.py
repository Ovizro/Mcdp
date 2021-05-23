""""
All base classes of Mcdp variable.
""""

import sys
from abc import ABCMeta, abstractmethod
from pydantic import BaseModel
from typing import Any, Union, Tuple, Dict, Type

__version__ = "Alpha 0.1.0"
__version_num__ = 100

from .counter import Counter

class McdpVar:
    
    __accessible__: list = []
    

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
        return any(self.linked.values())

"""
==============================
Mcdp config
==============================
"""

class McdpConfig(McdpVar, BaseModel):
    
    __slots__ = ["name", ]
    
    def __init__(self, name: str) -> None:
        self.name = name

"""
==============================
Mcdp Context Manager
==============================
"""

class ContextManager(McdpVar):
    
    __slots__ = ["name"]
    
    collection = {}
    
    def __init__(self, name: str) -> None:
        self.name = name
    
    @classmethod
    def collect(cls, instance: "ContextManager") -> None:
        cls.collection[instance.name] = instance

    @classmethod
    def get_namespace(cls):
        pass

"""
==============================
Mcdp Exceptions
==============================
"""

class McdpError(Exception, McdpVar):
    
    __slots__ = ["mcdp_version", "python_version"]
    
    def __init__(self, *arg: str) -> None:
        self.mcdp_version = __version__
        self.python_version = sys.version
        super().__init__(*arg)
        
class McdpVersionError(McdpError):

    def __init__(self, msg: str) -> None:
        super().__init__(msg.format(mcdp_version=__version__))

class MinecraftVersionError(McdpVersionError):
    pass
