from .version cimport Version
from .counter cimport Counter

cpdef int _get_mcdp_ef()
cpdef void _set_mcdp_ef(int ef)


cdef class McdpVar:
    cdef void check_gsattr(self, str key, int i) except *


cdef class _McdpBaseModel(McdpVar):
    cpdef dict to_dict(self)


cdef class Variable(McdpVar):
    cdef readonly:
        Counter counter
    cpdef void link(self, Variable var) except *
    cpdef bint used(self)
    

cdef class McdpError(Exception):
    cdef readonly:
        Version version