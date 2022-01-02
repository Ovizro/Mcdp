from libc.stdio cimport FILE


cdef fused AnyStr:
    str
    bytes

cpdef void mkdir(str dir_path) except *


cdef class Stream:
    cdef FILE* _file
    cdef readonly:
        str path
        bint closed

    cpdef void open(self, str mod = *) except *
    cpdef int write(self, AnyStr data) except -1
    cpdef int dump(self, data) except -1
    cpdef void close(self)
    cpdef bint writable(self)