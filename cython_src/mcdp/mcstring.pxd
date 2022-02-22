from libc.stdint cimport uint8_t
from ._typing cimport McdpVar, _McdpBaseModel
from .version cimport Version, VersionError
from .exception cimport McdpValueError, McdpTypeError


cdef enum MCStr_Color:
    BLACK       = 0
    DARK_BLUE   = 1
    DARK_GREEN  = 2
    DARK_AQUA   = 3
    DARK_RED    = 4
    DARK_PURPLE = 5
    GOLD        = 6
    GRAY        = 7
    DARK_GRAY   = 8
    BLUE        = 9
    GREEN       = 10
    AQUA        = 11
    RED         = 12
    LIGHT_PURPLE= 13
    YELLOW      = 14
    WHITE       = 15
