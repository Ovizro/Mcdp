from ._typing cimport McdpVar, McdpError
from .context cimport Context, _envs, dp_insert, dp_comment, dp_commentline, dp_newline, get_extra_path 
from .exception cimport McdpValueError, McdpTypeError, McdpIndexError
from .mcstring cimport MCString


cdef class PosComponent(McdpVar):
    cdef readonly:
        str value
        str type


cdef class Position(McdpVar):
    cdef list _posXYZ
    cdef readonly:
        str type
        
    cpdef void teleport(self, slt) except *


cdef class MultiDict(dict):
    cdef object __weakref__

    cpdef void add(self, key, value) except *
    cdef list _values(self)
    cdef list _items(self)

cdef class Selector(McdpVar):
    cdef readonly:
        str name
        MultiDict args

    cdef void _add_tag(self, const char* tag) except *
    cdef void _remove_tag(self, const char* tag) except *
    cpdef void remove(self) except *

cdef Selector _selector(t_slt)


cdef class Execute(McdpVar):
    cdef readonly:
        bint inline_handler
        list instructions