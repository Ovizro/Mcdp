from typing import Optional

from .typing import McdpError, __version__


class McdpVersionError(McdpError):

    __slots__ = []

    def __init__(self, msg: Optional[str] = None) -> None:
        if msg:
            super().__init__(
                    msg.format(mcdp_version=__version__))
        else:
            super().__init__()

class McdpValueError(McdpError):
    __slots__ = []

class McdpTypeError(McdpError):
    __slots__ = []

class McdpIndexError(McdpError):
    __slots__ = []