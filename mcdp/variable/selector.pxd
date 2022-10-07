from ..objects cimport McdpObject
from ..exception cimport McdpTypeError
from .mcstring cimport MCString


cdef api class Selector(McdpObject) [object DpSelectorObject, type DpSelector_Type]:
    cdef readonly:
        str name
        dict args
    
    cpdef void add_args(self, str key, val) except *


cdef api object DpSelector_FromObject(object val)
cdef api object DpSelector_FromString(const char* string)
cdef api object DpSelector_GetName(object slt)