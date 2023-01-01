from ..objects cimport McdpObject, BaseNamespace
from ..exception cimport McdpUnboundError, McdpTypeError
from ..cpython_interface cimport Py_TYPE_NAME, Py_TYPE_MRO, PyUnicode_FromFormat


cdef class NamePool:
    cdef:
        set cache
        bytes _format
    cdef readonly Py_ssize_t used_size
    cpdef str fetch(self)
    cpdef void release(self, str name) except *


cdef class BaseFrame(McdpObject):
    cdef dict __dict__
    cdef:
        BaseNamespace namespace
        tuple name_pools


cdef class FrameVariable(McdpObject):
    cdef:
        bint special_name
        str name
    cdef readonly:
        BaseFrame frame
        Py_ssize_t channel_id
    cpdef void bind(self, BaseFrame frame) except *


cdef api object DpVar_FromObject(object obj)
cdef api int DpVar_RegisterBuilder(type t, object func) except -1
cdef int DpFrame_SetSpecialVar(object frame, object name, object attr) except -1