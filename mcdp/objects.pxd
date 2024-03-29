from .cpython_interface cimport Py_TYPE_NAME, PyEval_GetFuncName, PyUnicode_FromFormat


ctypedef api object (*T_property)(object nsp)


cdef api class McdpObject(object) [object DpBaseObject, type DpBaseObject_Type]:
    pass


cdef class BaseNamespace(McdpObject):
    cdef dict __dict__
    cdef readonly:
        str n_name "name"
        object n_path "path"


cdef api int DpNamespace_Property(const char* name, T_property factory) except -1