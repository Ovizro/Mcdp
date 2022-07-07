import re
from typing import Dict, Optional


__author__ = "Ovizro"
__author_email__ = "Ovizro@hypercol.com"
__maintainer__ = ["Tatersic", "ExDragine"]
__maintainer_email__ = ["Tatersic@qq.com", "ExDragine@hypercol.com"]


_pack: Optional["Mcdatapack"] = None


class Mcdatapack(object):
    __slots__ = ["pack_info", "namespaces"]

    def __init__(
            self,
            name: str,
            version: "T_version",
            description: str,
            *,
            icon_path: Optional[str] = None,
            **kwds
    ) -> None:
        self.pack_info = PackageImformation(
            name=name, support_version=version, description=description, icon_path=icon_path)
        self.namespaces: Dict[str, Namespace] = {}
        
        for k, v in kwds.items():
            setattr(config, k, v)
        self.active()
    
    @property
    def actived(self) -> bool:
        return _pack is self
    
    def active(self) -> None:
        global _pack
        _pack = self
    
    def create_namespace(self, name: str) -> "Namespace":
        namespace = Namespace(name)
        self.namespaces[name] = namespace
        return namespace
    
    def get_namespace(self, name: str) -> "Namespace":
        return self.namespaces[name]


def get_pack() -> Mcdatapack:
    if _pack is None:
        raise McdpValueError("Mcdatapack has not been instantiated.")
    return _pack


from .exception import *
from .version import __version__
from .config import PackageImformation, check_mc_version, check_mcdp_version, get_config, T_version
from .objects import BaseNamespace
from .stream import Stream

config_module = config
config = get_config()
P_name = re.compile("^[a-z0-9\\-_]+$")


class Namespace(BaseNamespace):
    __slots__ = []

    def __init__(self, name: str) -> None:
        if P_name.match(name) is None:
            raise McdpValueError("invalid namespace")
        super().__init__(name)


__all__ = [
    "Mcdatapack",
    "Namespace",
    # config
    "config",
    
]
