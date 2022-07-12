import os
from pydantic import BaseModel

from .exception import *
from .version import __version__, VersionChecker, McdpVersionError


class Config(BaseModel):
    check_stack: bool = True

    # function option
    overload_enable: bool = True
    add_comments: bool = True
    
    # Vmcl option
    disable_macro: bool = False


_config = Config()


def get_config() -> Config:
    return _config


check_mcdp_version = __version__.check
check_mc_version = VersionChecker(lambda: get_pack().pack_info.support_version).decorator


from . import get_pack


class MinecraftVersionError(McdpVersionError):
    pass