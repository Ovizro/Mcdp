import sys
import ujson

from .version import __version__
from .counter cimport Counter
from .counter import Counter


cdef class McdpVar:

    cdef set __accessible__

    cdef get_attr(self, str key):
        if not key in self.__accessible__:
            raise McdpError("%s has no attribute %s" % (self, key))
        return self.__getattribute__(key)
    

cdef class Variable(McdpVar):
    pass