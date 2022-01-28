from pathlib import Path
from typing import Union, Optional
from zipfile import ZipFile

from .config import Config, get_config
from .context import Context, TagManager, comment, insert, add_tag
from .variable import Scoreboard, dp_int, dp_score, global_var
from .mcstring import MCString, MCSS
from .command import cout, endl
from .mcfunc import mcfunc, mcfunc_main, MCFunction
from .typing import McdpError
from .version import __version__
from .stream import *


__author__ = "Ovizro"
__author_email__ = "Ovizro@hypercol.com"
__maintainer__ = ["Tatersic", "ExDragine"]
__maintainer_email__ = ["Tatersic@qq.com", "ExDragine@hypercol.com"]


class Mcdatapack:
    __slots__ = ["config", ]

    def __init__(
            self,
            path: Union[str, Path],
            *,
            config: Optional[Config] = None
    ) -> None:
        pass


__all__ = [
    # config
    "Config",
    "get_config",
    # context
    "Context",
    "comment",
    "insert",
    "TagManager",
    "add_tag",
    # variable
    "global_var",
    "Scoreboard",
    "dp_score",
    "dp_int",
    # command
    "cout",
    "endl",
    "MCString",
    "MCSS",
    # mcfunction
    "mcfunc",
    "mcfunc_main",
    "MCFunction",
    # exception
    "McdpError"
]
