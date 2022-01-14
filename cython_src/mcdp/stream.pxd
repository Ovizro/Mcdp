from libc.stdio cimport FILE
from .path cimport *


cpdef void mkdir(const char* dir_path) nogil except *


cdef class Stream:
    cdef FILE* _file
    cdef readonly:
        bytes path
        bint closed

    cpdef void open(self, str mod = *) except *
    cpdef int _bwrite(self, const char* _s) except -1
    cpdef int write(self, str _s) except -1
    cpdef int dump(self, data) except -1
    cpdef void close(self)
    cpdef bint writable(self)