from ..objects cimport McdpObject
from ..exception cimport McdpTypeError
from .mcstring cimport MCString


cdef class Selector(McdpObject):
    cdef readonly:
        str name
        dict args
    
    cpdef void add_args(self, str key, val) except *


cdef api object DpSelector_FromObject(object val)
cdef api object DpSelector_FromString(const char* string)
