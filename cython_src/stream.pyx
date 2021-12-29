from libc.stdio cimport fopen, fputs, fclose
from .counter cimport ContextCounter, get_counter

import os
import ujson
import shutil
from functools import partial, wraps
from typing import List, Literal, Optional, Union

from .counter import get_counter


cdef ContextCounter counter = get_counter()

cpdef void mkdir(str dir_path) except *:
    +counter.dirs
    cdef str base = os.path.split(dir_path)[0]
    if os.path.isdir(base):
        os.mkdir(dir_path)
    else:
        mkdir(base)
    

cdef class Stream:

    def __init__(self, str path, *, root: Optional[str] = None):
        if not os.path.isabs(path):
            if not root:
                p = os.path.abspath(path)
            else:
                p = os.path.join(root, path)

        self.path = p
        self._file = NULL
        self.closed = False
    
    cpdef void open(self, str mod = "w") except *:
        if self._file != NULL:
            return

        cdef char* open_mod
        mkdir(self.path)
        if mod == 'w':
            open_mod = 'w'
        elif mod == 'a':
            open_mod = 'a'
        else:
            raise ValueError("invalid open mod")
        self._file = fopen(self.path.encode(), open_mod)
        if self._file == NULL:
            raise OSError("fail to open %s." % self.path)
        self.closed = False
    
    cpdef int write(self, AnyStr data) except -1:
        if not self._file == NULL:
            raise OSError("not writable")

        if data is None:
            raise ValueError("argument must be a string or bytes, not 'NoneType'")
        cdef int c
        if AnyStr is str:
            c = fputs(data.encode(), self._file)
        else:
            c = fputs(data, self._file)

        if c < 0:
            raise OSError("fail to write to file %s" % self.path)
        c = len(data)
        counter.chars += c
        return c

    cpdef int dump(self, data) except -1:
        cdef str d = ujson.dumps(data)
        return self.write(d)
    
    cpdef void close(self):
        if self._file == NULL:
            return
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