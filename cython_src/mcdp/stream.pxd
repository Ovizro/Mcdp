from libc.stdio cimport FILE
from .exception cimport McdpValueError
from .path cimport *


cdef struct StreamCounter:
    int dirs
    int files
    int commands
    int chars


cdef StreamCounter get_counter() nogil
cdef void print_counter()

cpdef void mkdir(const char* dir_path) nogil except *


cdef class Stream:
    cdef FILE* _file
    cdef readonly:
        char* path
        bint closed

    cpdef void open(self, str mod = *) except *
    cpdef int fwrite(self, const char* _s) except -1
    cpdef int write(self, str _s) except -1
    cpdef int dump(self, data) except -1
    cpdef void close(self)
    cpdef bint writable(self)