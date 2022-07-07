from pydantic import BaseModel
from typing import Dict, Tuple, Union, Optional, List

from .exception import *
from .version import Version, __version__, VersionChecker, McdpVersionError


T_version = Union[Version, Tuple[Union[str, int], ...], Dict[str, Union[str, int]], str]


UPWARD_COMPAT   = 1
DOWNWARD_COMPAT = 2


class VmclConfig(BaseModel):
    enabled: bool = True
    enable_pywheel: bool = True


class PackageImformation(BaseModel):
    name: str
    support_version: Version
    description: str
    icon_path: Optional[str] = None


class Config(BaseModel):
    # build option
    build_zip: bool = False
    build_dir: List[str] = ["."]
    remove_old_pack: bool = True

    # function option
    enable_overload: bool = True
    add_comments: bool = True
    
    # Vmcl option
    vmcl_cfg: VmclConfig = VmclConfig()


_config = Config()


def get_config() -> Config:
    return _config

def set_config(config: Config) -> None:
    global _config
    _config = config


check_mcdp_version = __version__.check
check_mc_version = VersionChecker(lambda: get_pack().pack_info.support_version).decorator


from . import get_pack


class MinecraftVersionError(McdpVersionError):
    pass