""""
All base classes of Mcdp variable.
"""

import ujson
from pydantic import BaseModel, BaseConfig
from typing import ClassVar, Dict

from .version import __version__
from ._typing import McdpVar, Variable, McdpError


"""
==============================
Mcdp BaseModel
==============================
"""


class McdpBaseModel(BaseModel):

    __accessible__: ClassVar[Dict[str, int]] = {"@all.attr": 3}

    class Config(BaseConfig):
        arbitrary_types_allowed = True
        json_loads = ujson.loads
        json_dumps = ujson.dumps