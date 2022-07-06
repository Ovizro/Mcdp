from libc.stdio cimport FILE
from .exception cimport McdpValueError
from .path cimport *


cdef extern from "<stdarg.h>":
    ctypedef void* va_list
    int vfprintf(FILE*, const char*, ...) nogil
    void va_start(va_list ap, const char* last_arg) nogil
    void va_end(va_list ap) nogil


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
    cdef int fwrite(self, const char* _s) except -1
    cdef int format(self, const char* _s, ...) except -1
    cdef int vformat(self, const char* _s, va_list ap) except -1
    cpdef int write(self, str _s) except -1
    cpdef int dump(self, data) except -1
    cpdef void close(self)
    cpdef bint writable(self)