from os import PathLike
from typing import Dict, Literal, Tuple, Union, Optional, List, Set

from .typing import McdpBaseModel
from .version import Version, __version__, AioCompatVersionChecker
from .exception import *

T_version = Union[Version, Tuple[Union[str, int], ...], Dict[str, Union[str, int]], str]

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
