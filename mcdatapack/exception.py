import sys
from typing import Union

#from . import __version__ as VERSION
VERSION = "Alpha 0.1.0"
class McdpError(Exception):
    
    def __init__(self, arg: str) -> None:
        self.mcdp_version = VERSION
        self.python_version = sys.version
        super().__init__(arg)

class MinecraftVersionError(McdpError):
    pass

class McdpVersionError(MinecraftVersionError):

    def __init__(self, msg: str) -> None:
        super().__init__(msg.format(mcdp_version=VERSION))

class MinecraftVersionError(MinecraftVersionError):
    pass

if __name__ == "__main__":
    raise McdpError("test error")