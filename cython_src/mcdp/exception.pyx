from ._typing import McdpError
from .version import __version__


cdef class McdpVersionError(McdpError):

    def __init__(self, str msg = None):
        if msg:
            super().__init__(msg.format(mcdp_ver=__version__))
        else:
            super().__init__()


cdef class McdpValueError(McdpError):
    pass


cdef class McdpTypeError(McdpError):
    pass


cdef class McdpIndexError(McdpError):
    pass