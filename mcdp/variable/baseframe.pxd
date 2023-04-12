from libc.stdint cimport uint8_t
from ..objects cimport McdpObject, BaseNamespace
from ..exception cimport McdpUnboundError, McdpTypeError
from ..cpython_interface cimport Py_TYPE_GetName, Py_TYPE_NAME, Py_TYPE_MRO, PyUnicode_FromFormat, Py_VaBuildValue, va_list, va_start, va_end
from .selector cimport Selector


cdef enum Mcdp_Feature:
    IS_READY        = 0b0001
    IS_DISABLED     = 0b0010
    IS_REFERENCE    = 0b0100
    IS_VALID        = 0b1000
    CHECK_MASK      = 0b1010

cdef enum DpFrame_Feature:
    FORCE_BUILD_VALUE = 0b00010000
    FORCE_SPECIAL_NAME = 0b00100000
    SPECIAL_NAME_RENAME = 0b01000000


cdef class NamePool:
    cdef:
        set cache
        bytes _format
    cdef readonly Py_ssize_t used_size
    cpdef str fetch(self)
    cpdef void release(self, str name) except *


cdef api class BaseFrame(McdpObject) [object DpFrameObject, type DpFrame_Type]:
    cdef:
        dict __dict__
        Selector frame_selector
        BaseNamespace namespace
        tuple name_pools
        uint8_t flag
    cdef void set_special(self, str name, FrameVariable var) except *


cdef api class FrameVariable(McdpObject) [object DpVariableObject, type DpVariable_Type]:
    cdef:
        bint special_name
        str name
    cdef readonly:
        BaseFrame frame
        Py_ssize_t channel_id
    cpdef void bind(self, BaseFrame frame) except *
    cdef void ensure_bound(self) except *


cdef api object DpVar_FromObject(object obj)
cdef api int DpVar_RegisterBuilder(type t, object func) except -1
cdef api int DpVar_Bind(object var, object frame) except -1
cdef api object Dp_VaBuildValue(const char* format, va_list ap)
cdef api object Dp_BuildValue(const char* format, ...)
cdef api int DpFrame_SetSpecialVar(object frame, object name, object attr) except -1
cdef api object DpFrame_GetNamePool(object frame, Py_ssize_t channel_id)