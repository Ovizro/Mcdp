from .file_output import FileOutput
from .file_struct import BuildDirs
from .file import comment, insert
from .exception import McdpError

__version__ = "Alpha 0.1.0"
__version_num__ = 100

__all__ = [
    "FileOutput",
    "BuildDirs",
    "comment",
    "insert",
    "McdpError"
]