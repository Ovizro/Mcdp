from libc.stdio cimport FILE
from .cpython_interface cimport va_list, vfprintf, va_start, va_end


cdef class Stream:
    cdef FILE* _file
    cdef readonly:
        object path
        bint closed

    cdef int put(self, const char* _s) except -1
    cdef int putc(self, char ch) except -1
    cdef int putln(self, const char* _s) except -1
    cdef int format(self, const char* _s, ...) except -1
    cdef int vformat(self, const char* _s, va_list ap) except -1
    
    cpdef void open(self, str mod = *) except *
    cpdef int write(self, str _s) except -1
    cpdef int dump(self, object data) except -1
    cpdef void close(self)
    cpdef bint writable(self)