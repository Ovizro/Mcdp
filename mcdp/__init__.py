from pathlib import Path
from typing import Union, Optional

from .config import Config
from .file_struct import build_dirs
from .context import get_context, comment, insert
from .typings import McdpError
from .version import __version__

class Mcdatapack:
    
    __slots__ = ["config"]
    
    def __init__(
        self,
        path: Union[str, Path],
        *,
        config: Optional[Config] = None
    ) -> None:
        pass

__all__ = [
    "get_context",
    "build_dirs",
    "comment",
    "insert",
    "McdpError"
]