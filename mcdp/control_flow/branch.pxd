from ..context cimport Context, Handler, DpContext_Get, DpContext_Insert, DpContext_StartAnnotate, DpContext_EndAnnotate, DpContext_Newline
from ..exception cimport McdpRuntimeError
from .execute cimport Execute, DpExecute_FromObject


cdef class ExecuteHandler(Handler):
    cdef readonly:
        str execobj


cdef class BranchEnvironment:
    cdef readonly:
        Execute execobj
    cdef void enter(self) except *
    cdef void exit(self) except *


cdef class condition(BranchEnvironment):
    cdef readonly:
        Context ctx
    cdef void enter(self) except *
    cdef void exit(self) except *


cdef class inline_condition(BranchEnvironment):
    cdef readonly:
        ExecuteHandler hdl
    cdef void enter(self) except *
    cdef void exit(self) except *


cdef class while_loop(BranchEnvironment):
    cdef readonly:
        Context ctx
    cdef void enter(self) except *
    cdef void exit(self) except *


cdef api object Dp_If(object case)
cdef api object Dp_InlineIf(object case)
cdef api object Dp_While(object case)