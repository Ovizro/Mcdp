from os import PathLike
from typing import Dict, Literal, Tuple, Union, Optional, List, Set

from caio import version

from .typing import McdpBaseModel
from .version import Version, __version__, VersionChecker
from .exception import *


T_version = Union[Version, Tuple[Union[str, int], ...], Dict[str, Union[str, int]], str]


UPWARD_COMPAT   = 1
DOWNWARD_COMPAT = 2

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
    # base model information
    name: str
    support_version: Version
    description: str
    icon_path: Optional[str] = None
    namespace: str

    # build option
    build_zip: bool = False
    build_dir: List[str] = ["."]
    remove_old_pack: bool = True

    # version option
    version_flag: int = 0
    version_check: int = 0

    pydp: PydpConfig = PydpConfig()
    vmcl: VmclConfig = VmclConfig()

    def __init__(
            self,
            name: str,
            version: T_version,
            description: str,
            *,
            namespace: Optional[str] = None,
            icon_path: Optional[str] = None,
            **kw
    ) -> None:
        global _current_cfg
        namespace = namespace or name
        version = Version(version)
        super().__init__(
                name=name, version=version, description=description,
                namespace=namespace, icon_path=icon_path, **kw)
        _current_cfg = self


def get_config() -> Config:
    if not _current_cfg:
        raise McdpValueError("fail to get the config.")
    return _current_cfg


check_mcdp_version = __version__.check
check_mc_version = VersionChecker(lambda: get_config().support_version).decorator


class MinecraftVersionError(McdpVersionError):
    pass
