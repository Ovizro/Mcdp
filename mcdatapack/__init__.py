from .file_struct import BuildDirs
from .context import get_context, comment, insert
from .exception import McdpError

__version__ = "Alpha 0.1.0"
__version_num__ = 100

__all__ = [
    "get_context",
    "BuildDirs",
    "comment",
    "insert",
    "McdpError"
]