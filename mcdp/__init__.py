from pathlib import Path
from typing import Union, Optional

from .config import Config, get_config
from .file_struct import build_dirs, build_dirs_from_config, init_context, init_mcmeta
from .context import get_context, Context, TagManager, comment, insert, add_tag
from .variable import Scoreboard, dp_int, dp_score
from .mcfunc import mcfunc, MCFunction
from .typings import McdpError
from .version import __version__

class Mcdatapack:
    
    __slots__ = ["config",]
    
    def __init__(
        self,
        path: Union[str, Path],
        *,
        config: Optional[Config] = None
    ) -> None:
        pass

__all__ = [
    #config
    "Config",
    "get_config",
    #file
    "build_dirs",
    "build_dirs_from_config",
    #context
    "init_context",
    "Context",
    "get_context",
    "comment",
    "insert",
    "TagManager",
    "add_tag",
    #variable
    "Scoreboard",
    "dp_score",
    "dp_int",
    #mcfunction
    "mcfunc",
    "MCFunction",
    #exception
    "McdpError"
]