from .version cimport Version
from .counter cimport Counter


cdef class McdpVar:
    cdef v_getattr(self, str key)
    cdef void v_setattr(self, str key, value) except*
    cdef void check_gsattr(self, str key, int i) except *


cdef class _McdpBaseModel(McdpVar):
    cpdef dict to_dict(self)
    cdef str _json(self)


cdef class Variable(McdpVar):
    cdef readonly:
        Counter counter
    cpdef void link(self, Variable var) except *
    cpdef bint used(self)
    

cdef class McdpError(Exception):
    cdef readonly:
        Version version