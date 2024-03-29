import re
from typing import Dict, Optional, Type
from typing_extensions import Self


__author__ = "HyperCol"
__author_email__ = "HyperCol@hypercol.com"
__maintainer__ = "Ovizro"
__maintainer_email__ = "Ovizro@hypercol.com"


_pack: Optional["Mcdatapack"] = None


class Mcdatapack(object):
    __slots__ = ["builder", "namespaces"]

    def __init__(
            self,
            name: str,
            version: "T_version",
            description: str,
            *,
            icon_path: Optional[str] = None,
            builderclass: Optional[Type["AbstractBuilder"]]  = None,
            **kwds
    ) -> None:
        if builderclass is None:
            builderclass = get_defaultbuilder()
        self.builder = builderclass(name, version, description, 
            icon_path=icon_path, **kwds)
        self.namespaces: Dict[str, Namespace] = {}
        self.active()
    
    @property
    def pack_info(self) -> "PackageInformation":
        return self.builder.pack_info

    @property
    def actived(self) -> bool:
        return _pack is self
    
    def active(self) -> None:
        global _pack
        _pack = self
    
    def create_namespace(self, name: str) -> "Namespace":
        if name in self.namespaces:
            raise ValueError(
                f"namespace '{name}' has been already created,",
                "using get_namespace() instead"
            )
        namespace = Namespace(name)
        self.namespaces[name] = namespace
        return namespace
    
    def get_namespace(self, name: str) -> "Namespace":
        return self.namespaces[name]
    
    def build(self) -> None:
        self.active()
        with self.builder:
            for i in self.namespaces.values():
                i.build()


def get_pack() -> Mcdatapack:
    if _pack is None:
        raise McdpInitalizeError("Mcdatapack has not been instantiated.")
    return _pack


from .exception import *
from .version import __version__, T_version
from .config import check_mc_version, check_mcdp_version, get_config
from .objects import BaseNamespace
from .context import Context, finalize_context, get_context, McdpContextError, init_context
from .variable import *
from .build import PackageInformation, AbstractBuilder, get_defaultbuilder
from .include import get_include

config = get_config()


P_name = re.compile(r"^[A-Za-z0-9\\-_]+$")


class Namespace(BaseNamespace):
    __slots__ = []

    def __init__(self, name: str) -> None:
        if P_name.fullmatch(name) is None:
            raise McdpValueError("invalid namespace")
        super().__init__(name)
    
    def build(self) -> None:
        with self:
            ...
    
    def __enter__(self) -> Self:
        init_context(self).activate()
        return self
    
    def __exit__(self, *args) -> None:
        finalize_context()


__all__ = [
    # core
    "Mcdatapack",
    "Namespace",
    # config
    "config",
    # context
    "Context",
    "get_context",
    # exception
    "McdpError",
    "McdpInitalizeError",
    "McdpRuntimeError",
    "McdpValueError",
    "McdpContextError",
]
