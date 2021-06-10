from os import PathLike
from asyncio import iscoroutinefunction
from functools import partial, lru_cache
from typing import Union, Optional, Callable
from pydantic import validator

from .typings import McdpBaseModel, McdpError, McdpVersionError
from .version import (Version, T_version, __version__, version_check, VersionChecker, AioVersionChecker)

class PydpConfig(McdpBaseModel):
    use_ast: bool = False

class VmclConfig(McdpBaseModel):
    enabled: bool = True
    enable_pywheel: bool = True
    
def get_version(mc_version: T_version) -> int:
    if not isinstance(mc_version, Version):
        mc_version = Version(mc_version)

    if mc_version[0] != 1:
        raise MinecraftVersionError("Minecraft version must start with '1.'.")
    elif mc_version[1] < 13:
        raise MinecraftVersionError("datapack is not enable for Minecraft below 1.13 .")
    elif mc_version[1] < 15:
        return 4
    elif mc_version <= "1.16.1":
        return 5
    elif mc_version[1] < 17:
        return 6
    elif mc_version[1] == 17:
        return 7
    else:
        raise ValueError(f"unknow Minecraft datapack version {mc_version}.")

_current_cfg: Optional["Config"] = None

class Config(McdpBaseModel):
    name: str
    version: Version
    description: str
    iron_path: Optional[Union[str, PathLike]] = None
    namespace: str
    
    pydp: PydpConfig = PydpConfig()
    vmcl: VmclConfig = VmclConfig()
    
    def __init__(
        self,
        name: str,
        version: T_version,
        description: str,
        *,
        namespace: Optional[str] = None,
        iron_path: Optional[Union[str, PathLike]] = None,
        **kw
    ) -> None:
        global _current_cfg
        namespace = namespace or name
        version = Version(version)
        super().__init__(
            name=name, version=version, description=description,
            namespace=namespace, iron_path=iron_path, **kw)
        _current_cfg = self
    
    @validator("version")
    def _version(cls, value: T_version) -> Version:
        return Version(value)

def get_config() -> Config:
    if not _current_cfg:
        raise McdpError("fail to get the config.")
    return _current_cfg

check_mcdp_version = partial(version_check, __version__)

@lru_cache()
def get_mc_version_checker(name: str):
    return VersionChecker(name, lambda: get_config().version)

@lru_cache()
def get_mc_version_aiochecker(name: str):
    return AioVersionChecker(name, lambda: get_config().version)

def check_mc_version(*args, **kw) -> Callable[[Callable], VersionChecker]:
    def MCheker(func: Callable) -> VersionChecker:
        if not iscoroutinefunction(func):
            mcv_checker = get_mc_version_checker(func.__qualname__)
        else:
            mcv_checker = get_mc_version_aiochecker(func.__qualname__)
        mcv_checker.register(func, *args, **kw)
        return mcv_checker
    return MCheker

class MinecraftVersionError(McdpVersionError):
    pass