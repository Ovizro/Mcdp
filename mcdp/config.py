import re
import sys
from pydantic import BaseModel, validator, Field
from typing import Any, Dict, Tuple, Union, Optional, List, Set
from types import ModuleType

from .exception import *
from .version import Version, __version__, VersionChecker, McdpVersionError


T_version = Union[Version, Tuple[Union[str, int], ...], Dict[str, Union[str, int]], str]
P_dpfile = re.compile("[a-z0-9\\-_]+")

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

    @validator("namespace")
    def valid_namespace(cls, value: str) -> str:
        if P_dpfile.match(value):
            return value
        else:
            raise McdpValueError("Invalid namespace.")


_current_cfg: Optional["Config"] = None


class Config(BaseModel):
    package: PackageImformation

    # build option
    build_zip: bool = False
    build_dir: List[str] = ["."]
    remove_old_pack: bool = True

    # function option
    enable_overload: bool = True
    add_comments: bool = True
    
    # Vmcl option
    vmcl_cfg: VmclConfig = VmclConfig()


def set_config(config: Config) -> None:
    global _current_cfg
    _current_cfg = config


def get_config() -> Config:
    if not _current_cfg:
        raise McdpValueError("fail to get the config.")
    return _current_cfg


check_mcdp_version = __version__.check
check_mc_version = VersionChecker(lambda: get_config().package.support_version).decorator


class MinecraftVersionError(McdpVersionError):
    pass