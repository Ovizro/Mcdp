""""
All base classes of Mcdp variable.
"""

import sys
import ujson
from abc import ABCMeta, abstractmethod
from pydantic import BaseModel, BaseConfig
from typing import Any, Dict, Union, Optional

from .version import __version__
from .counter import Counter

class McdpVar:
    
    __accessible__: list = []
    
    def get_attr(self, key: str) -> Any:
        if not key in self.__class__.__accessible__:
            raise McdpError
        return self.__getattribute__(key)
    
"""
==============================
Mcdp Functions
==============================
"""

class BaseMcfunc(McdpVar):
    
    __slots__ = []
    __accessible__ = ["name",]

"""
==============================
Mcdp Variables
==============================
"""

class VariableMeta(ABCMeta):
    
    def __new__(cls, name: str, bases: tuple, attrs: Dict[str, Any]) -> ABCMeta:
        if not attrs.get('__accessible__', None):
            attrs['__accessible__'] = []
        elif not isinstance(attrs['__accessible__'], list):
            attrs['__accessible__'] = list(attrs['__accessible__'])
            
        for k,v in attrs.items():
            if isinstance(v, BaseMcfunc):
                attrs['__accessible__'].append(k)
        return ABCMeta.__new__(cls, name, bases, attrs)
    
    def __instancecheck__(self, instance: Any) -> bool:
        if instance.__class__ is self:
            return True
        else:
            return self.__subclasscheck__(instance.__class__)

class Variable(McdpVar, metaclass=VariableMeta):

    __slots__ = ["counter", "applied"]

    counter: Counter

    @abstractmethod
    def __init__(self) -> None:
        self.applied = False
        self.counter = Counter()
        
    @abstractmethod
    def apply(self) -> None:
        raise NotImplementedError

    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, val: "Variable"):
        if not isinstance(val, cls):
            raise TypeError(f"{val} is not a instance of {cls}.")
        else:
            return val

    def link(self, var: Union["Variable", Counter]) -> None:
        if not isinstance(var, Counter):
            var = var.counter
        self.counter.link_to(var)
        
    def used(self) -> bool:
        return bool(self.counter)

"""
==============================
Mcdp BaseModel
==============================
"""

class McdpBaseModel(McdpVar, BaseModel):
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

class McdpError(Exception, McdpVar):
    
    __slots__ = ["version", "python_version"]
    
    def __init__(self, *arg: str, **kw) -> None:
        self.python_version = sys.version
        self.version = __version__
        super().__init__(*arg)
        
class McdpVersionError(McdpError):

    def __init__(self, msg: Optional[str] = None, type=None) -> None:
        if msg:
            super().__init__(
                msg.format(mcdp_version=__version__))
        else:
            super().__init__()