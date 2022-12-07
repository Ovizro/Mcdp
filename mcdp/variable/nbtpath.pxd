from ..objects cimport McdpObject
from ..exception cimport McdpIndexError


cdef class PathNode:
    cdef readonly:
        str name
        PathNode next
    cpdef PathNode copy(self, Py_ssize_t depth = *)


cdef api class NBTPath(McdpObject) [object DpNBTPathObject, type DpNBTPath_Type]:
    cdef:
        Py_ssize_t size
        PathNode node
    

cdef api object DpNBTPath_FromObject(object obj)
cdef api object DpNBTPath_FromString(const char* string)