from os import PathLike
from typing import Union, Optional, Tuple, TypeVar
from pydantic import Field, validator

from .typings import McdpConfig, McdpVersionError, __version__
from .version import Version, T_version

_dp_version_field = Field(default=6, const=True, ge=4)

class PydpConfig(McdpConfig):
    use_ast: bool = False

class VmclConfig(McdpConfig):
    enabled: bool = True
    enable_pywheel: bool = True
    
def get_version(mc_version: T_version) -> int:
    if not isinstance(mc_version, Version):
        mc_version = Version(mc_version)

    if mc_version[0] != 1:
        raise MinecraftVersionError("Minecraft version must start with '1.XX'.")
    elif mc_version[1] < 13:
        raise MinecraftVersionError("datapack is not enable for Minecraft below 1.13")
    elif mc_version[1] < 15:
        return 4
    elif mc_version <= "1.16.1":
        return 5
    elif mc_version[1] < 17:
        return 6
    elif mc_version[1] == 17:
        return 7
    else:
        raise ValueError(f"unknow Minecraft datapack version {version}")

class Config(McdpConfig):
    name: str
    version: Version
    description: str
    iron_path: Optional[Union[str, PathLike]] = None
    namespace: str
    
    pydp: PydpConfig
    vmcl: VmclConfig
    
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
        namespace = namespace or name
        super().__init__(
            name=name, version=version, description=description,
            namespace=namespace, iron_path=iron_path, **kw)
    
    @validator("version")
    def _version(cls, value: T_version) -> Version:
        return Version(value)

class MinecraftVersionError(McdpVersionError):
    pass