import re
import sys
from pydantic import validator, Field
from typing import Any, Dict, Literal, Tuple, Union, Optional, List, Set
from types import ModuleType

from .typing import McdpBaseModel
from .version import Version, __version__, VersionChecker
from .exception import *


T_version = Union[Version, Tuple[Union[str, int], ...], Dict[str, Union[str, int]], str]
P_dpfile = re.compile("[a-z0-9\\-_]+")

UPWARD_COMPAT   = 1
DOWNWARD_COMPAT = 2


class VmclConfig(McdpBaseModel):
    enabled: bool = True
    enable_pywheel: bool = True


class MCFuncConfig(McdpBaseModel):
    type: Literal["sfunction", "normal"] = "normal"
    allow_overload: bool = True
    tag: Set[str] = set()


class PackageImformation(McdpBaseModel):
    name: str
    support_version: Version
    description: str
    icon_path: Optional[str] = None
    namespace: str

    @validator("namespace")
    def valid_namespace(cls, value: str) -> str:
        if P_dpfile.match(value):
            return value
        else:
            raise McdpValueError("Invalid namespace.")


_current_cfg: Optional["Config"] = None


class Config(McdpBaseModel):
    package: PackageImformation = Field(alias="pack")

    # build option
    build_zip: bool = False
    build_dir: List[str] = ["."]
    remove_old_pack: bool = True

    # version option
    version_flag: int = 0
    version_check: int = 0

    # function option
    use_ast: bool = False
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
check_mc_version = VersionChecker(lambda: get_config().packaage.support_version).decorator


class MinecraftVersionError(McdpVersionError):
    pass


if sys.version_info >= (3, 7):
    # declaretion for type check

    packaage: PackageImformation
    build_zip: bool
    build_dir: List[str]
    remove_old_pack: bool
    version_flag: int
    version_check: int
    use_ast: bool
    add_comments: bool
    vmcl_cfg: VmclConfig

    class McdpConfigModel(ModuleType):
        """Help to get and set config value without using 'get_config'"""

        def __getattr__(self, name: str) -> Any:
            return getattr(get_config(), name)
        
        def __setattr__(self, __name: str, __value: Any) -> None:
            if _current_cfg and hasattr(_current_cfg, __name):
                setattr(_current_cfg, __name, __value)
            else:
                super().__setattr__(__name, __value)

                
    sys.modules[__name__].__class__ = McdpConfigModel