from libc.stdio cimport FILE
from libc.stdint cimport uint8_t
from ._typing cimport McdpVar
from .exception cimport McdpError, McdpVersionError, McdpTypeError
from .compliter cimport Comliter


cdef extern from "lex.yy.c":
    pass