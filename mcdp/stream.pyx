cimport cython
from libc.stdio cimport fopen, fputs, fputc, fclose, sprintf
from libc.stdlib cimport malloc, free
from libc.string cimport strlen, strcpy, strcmp
from cpython cimport PyErr_Format
from kola._cutil cimport kola_open

import os
from os import path as os_path

try:
    import ujson as json
except ImportError:
    import json


cdef class Stream:
    def __cinit__(self, path not None, *, root = None):
        if not os_path.isabs(path):
            if not root:
                self.path = os_path.abspath(path)
            else:
                self.path = os_path.join(root, path)
        self._file = NULL
        self.closed = False
    
    def __dealloc__(self):
        self.close()
    
    cpdef void open(self, str mod = "w") except *:
        if self._file != NULL:
            return

        cdef bytes open_mod = mod.encode()
        file_dir = os_path.dirname(self.path)
        os.makedirs(file_dir, exist_ok=True)
        self._file = kola_open(self.path, NULL, open_mod)
        self.closed = False
    
    @cython.nonecheck(False)
    cdef int put(self, const char* _s) except -1:
        if self._file == NULL:
            raise OSError("not writable")

        cdef int c
        with nogil:
            c = fputs(_s, self._file)

        if c < 0:
            PyErr_Format(OSError, "fail to write to file %S", <void*>self.path)
        return c
    
    @cython.nonecheck(False)
    cdef int putc(self, char ch) except -1:
        if self._file == NULL:
            raise OSError("not writable")
        
        cdef int c
        with nogil:
            c = fputc(ch, self._file)
        if c < 0:
            PyErr_Format(OSError, "fail to write to file %S", <void*>self.path)
        return 1
    
    @cython.nonecheck(False)
    cdef int putln(self, const char* _s) except -1:
        cdef int c = self.put(_s)
        fputc(ord('\n'), self._file)
        return c + 1
    
    @cython.nonecheck(False)
    cdef int vformat(self, const char* _s, va_list ap) except -1:
        if self._file == NULL:
            raise OSError("not writable")

        cdef int c
        with nogil:
            c = vfprintf(self._file, _s, ap)
        if c < 0:
            PyErr_Format(OSError, "fail to write to file %S", <void*>self.path)
        return c
    
    @cython.nonecheck(False)
    cdef int format(self, const char* _s, ...) except -1:
        cdef:
            va_list ap
            int c
        va_start(ap, _s)
        try:
            c = self.vformat(_s, ap)
        finally:
            va_end(ap)
        return c
    
    cpdef int write(self, str _s) except -1:
        self.put(_s.encode())

    cpdef int dump(self, object data) except -1:
        cdef str d = json.dumps(data, indent=4)
        return self.write(d)
    
    cpdef void close(self):
        if self._file == NULL:
            return
        with nogil:
            fclose(self._file)
            self._file = NULL
            self.closed = True
    
    cpdef bint writable(self):
        return self._file != NULL

    def __enter__(self):
        self.open()
        return self
    
    def __exit__(self, *args):
        self.close()