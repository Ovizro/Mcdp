from libc.stdio cimport fopen, fputs, fclose
from .counter cimport ContextCounter, get_counter

import os
import ujson

from .counter import get_counter

cdef _path_tool = os.path
cdef ContextCounter counter = get_counter()

cpdef void mkdir(str dir_path) except *:
    +counter.dirs
    cdef str base = _path_tool.split(dir_path)[0]
    if _path_tool.isdir(base):
        os.mkdir(dir_path)
    else:
        mkdir(base)
    

cdef class Stream:

    def __init__(self, str path, *, root: Optional[str] = None):
        if not _path_tool.isabs(path):
            if not root:
                p = _path_tool.abspath(path)
            else:
                p = _path_tool.join(root, path)

        self.path = p
        self._file = NULL
        self.closed = False
    
    cpdef void open(self, str mod = "w") except *:
        if self._file != NULL:
            return

        cdef:
            tmp_path = self.path.encode()
            char* _path = <char*>tmp_path
            char* open_mod
        file_dir = _path_tool.split(self.path)[0]
        if not _path_tool.isdir(file_dir):
            mkdir(file_dir)
        if mod == 'w':
            open_mod = 'w'
        elif mod == 'a':
            open_mod = 'a'
        else:
            raise ValueError("Invalid open mod.")

        with nogil:
            self._file = fopen(_path, open_mod)
            if self._file != NULL:
                self.closed = False
                return
        raise OSError("fail to open %s" % self.path)
    
    cpdef int _bwrite(self, bytes _s) except -1:
        if self._file == NULL:
            raise OSError("not writable")

        if _s is None:
            raise ValueError("argument must be a string or bytes, not 'NoneType'")
        cdef:
            int c
            char* string = _s

        with nogil:
            c = fputs(string, self._file)

        if c < 0:
            raise OSError("fail to write to file %s" % self.path)
        c = len(_s)
        counter.chars += c
        return c
    
    cpdef int write(self, str _s) except -1:
        self._bwrite(_s.encode())

    cpdef int dump(self, data) except -1:
        cdef str d = ujson.dumps(data)
        return self.write(d)
    
    cpdef void close(self):
        with nogil:
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