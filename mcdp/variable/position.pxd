from ..objects cimport McdpObject
from ..exception cimport McdpValueError
from ..cpython_interface cimport PyUnicode_FromFormat


cdef api enum MCPos_TypeFlag:
    NANTYPE = 0, LOCAL, ABSOLUTE, RELATIVE

ctypedef float (*fl_opt)(float, float)
ctypedef object (*ob_opt)(object, object)


cdef api class Component(McdpObject) [object DpComponentObject, type DpComponent_Type]:
    cdef:
        str raw_value
        MCPos_TypeFlag type_flag
    cdef readonly:
        float offset

    cdef object _calc(self, object other, fl_opt opt)


cdef api class Position(McdpObject) [object DpPositionObject, type DpPosition_Type]:
    cdef MCPos_TypeFlag type_flag
    cdef readonly:
        tuple components

    cdef void _validate_comp(self) except *
    cdef object _calc0(self, object other, ob_opt opt)
    cdef object _calc1(self, object other, ob_opt opt)


cdef api object DpPosition_New(float x, float y, float z, MCPos_TypeFlag flag)
cdef api object DpPosition_FromObject(object obj, MCPos_TypeFlag flag)
cdef api object DpPosition_FromString(const char* string)
cdef api object DpPosition_GetComponent(object pos, Py_ssize_t i)
cdef api object DpPosition_GetX(object pos)
cdef api object DpPosition_GetY(object pos)
cdef api object DpPosition_GetZ(object pos)
cdef api float DpPosComponent_GetOffset(object comp) except? -1.0
cdef api MCPos_TypeFlag DpPosComponent_GetFlag(object comp) except NANTYPE