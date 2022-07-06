from ._typing cimport McdpVar, McdpError
from .context cimport get_namespace, Context, dp_insert, dp_newline, dp_comment, dp_commentline
from .command cimport Selector


cdef list _func_collections

cdef enum FunctionFlag:
    VALID_FUNC      = 0b000001
    NEED_APPLY      = 0b000010
    CALLABLE        = 0b000100
    USE_STACK       = 0b011000
    INVALID_FUNC    = 0b100000