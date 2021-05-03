import sys
from typing import Union

from . import __version__ as VERSION
from . import get_context

class McdpError(Exception):
    
    __slots__ = ["mcdp_version", "python_version"]
    
    def __init__(self, *arg: str) -> None:
        self.mcdp_version = VERSION
        self.python_version = sys.version
        super().__init__(*arg)

class McdpContextError(McdpError, OSError):
	
	__slots__ = ["context", ]
	
	def __init__(self, *arg: str) -> None:
		self.context = get_context()
		super().__init__(*arg)

class MinecraftVersionError(McdpError):
    pass

class McdpVersionError(MinecraftVersionError):

    def __init__(self, msg: str) -> None:
        super().__init__(msg.format(mcdp_version=VERSION))

if __name__ == "__main__":
    raise McdpError("test error")