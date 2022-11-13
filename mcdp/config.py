import os
from pydantic import BaseModel

from .exception import *
from .version import __version__, VersionChecker, McdpVersionError


class Config(BaseModel):
    check_stack: bool = True

    # function option
    overload_enable: bool = True
    
    # context option
    @property
    def use_annotates(self) -> bool:
        return _get_ctx_config()["use_annotates"]
    
    @use_annotates.setter
    def use_annotates(self, val: bool) -> None:
        _set_ctx_config(use_annotates=val)
    
    @property
    def max_stack(self) -> int:
        return _get_ctx_config()["max_stack"]
    
    @max_stack.setter
    def max_stack(self, val: int) -> None:
        _set_ctx_config(max_stack=val)
    
    @property
    def max_open(self) -> int:
        return _get_ctx_config()["max_open"]
    
    @max_open.setter
    def max_open(self, val: int) -> None:
        _set_ctx_config(max_open=val)

    # Vmcl option
    disable_macro: bool = False


_config = Config()


def get_config() -> Config:
    return _config


check_mcdp_version = __version__.check
check_mc_version = VersionChecker(lambda: get_pack().pack_info.support_version).decorator


from . import get_pack
from .context import _get_ctx_config, _set_ctx_config


class MinecraftVersionError(McdpVersionError):
    pass