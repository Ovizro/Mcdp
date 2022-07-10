from .cpython_interface cimport FunctionType

ctypedef object (*T_property)(BaseNamespace nsp)


cdef class McdpObject(object):
    pass


cdef class BaseNamespace(McdpObject):
    cdef dict __dict__
    cdef readonly:
        str n_name "name"
        bytes n_path "path"


cdef void register_factory(const char* name, T_property factory) except *