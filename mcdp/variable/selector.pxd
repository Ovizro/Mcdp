from cpython cimport PyDictProxy_New

from ..cpython_interface cimport _PyType_Lookup
from ..objects cimport McdpObject, BaseNamespace, DpNamespace_Property
from ..exception cimport McdpTypeError
from .mcstring cimport EntityNameString


cdef api class Selector(McdpObject) [object DpSelectorObject, type DpSelector_Type]:
    cdef dict _args
    cdef readonly str name
    
    cpdef void add_args(self, str key, val) except *

    
cdef:
    Selector SL_S
    Selector SL_A
    Selector SL_E
    Selector SL_P

cdef api object DpSelector_FromObject(object val)
cdef api object DpSelector_FromString(const char* string)
cdef api object DpSelector_GetName(object slt)
cdef api object DpSelector_GetArgs(object slt)
cdef api object DpStaticStr_FromSelector(object slt)