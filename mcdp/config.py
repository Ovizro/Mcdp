from os import PathLike
from typing import Union, Optional, Tuple, TypeVar
from pydantic import Field, validator

from .typings import McdpConfig, __version__
from .version import Version, MinecraftVersionError

_dp_version_field = Field(default=6, const=True, ge=4)
T_version = TypeVar("version", Tuple[int], str, Version)

class PydpConfig(McdpConfig):
    use_ast: bool = False

class VmclConfig(McdpConfig):
    enabled: bool = True
    enable_pywheel: bool = True

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
    def _version(cls, value: T_version) -> int:
        return Version(value)