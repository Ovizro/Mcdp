from os import PathLike
from typing import Literal, Union, Optional, List, Set

from .typings import McdpBaseModel
from .version import Version, T_version, __version__, AioCompatVersionChecker
from .exceptions import *

class PydpConfig(McdpBaseModel):
    use_ast: bool = False
    add_comments: bool = True


class VmclConfig(McdpBaseModel):
    enabled: bool = True
    enable_pywheel: bool = True


class MCFuncConfig(McdpBaseModel):
    type: Literal["sfunction", "normal"] = "normal"
    allow_overload: bool = True
    tag: Set[str] = set()


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

    remove_old_pack: bool = True

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


def get_config() -> Config:
    if not _current_cfg:
        raise McdpValueError("fail to get the config.")
    return _current_cfg


check_mcdp_version = __version__.check
check_mc_version = AioCompatVersionChecker(lambda: get_config().version).decorator


class MinecraftVersionError(McdpVersionError):
    pass
