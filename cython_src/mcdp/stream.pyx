from libc.stdio cimport fopen, fputs, fclose
from .counter cimport ContextCounter, get_counter

import ujson

from .path cimport (join_path, dirname, cmkdir,
    isdir, isfile, isabs, abspath, PyMem_Free)
from .counter import get_counter

cdef ContextCounter counter = get_counter()


cdef void _mkdir(const char* path, int* counter) nogil except *:
    counter[0] += 1

    cdef:
        char* pdir = dirname(path)
        int _sc
    if pdir == NULL:
        raise MemoryError
    if isdir(pdir) == 1:
        _sc = cmkdir(path)
        if _sc != 0:
            with gil:
                raise OSError("fail to create dir")
    else:
        _mkdir(pdir, counter)
    PyMem_Free(pdir)
    

cpdef void mkdir(const char* dir_path) nogil except *:
    if isdir(dir_path) == 1:
        return

    cdef int c = 0
    _mkdir(dir_path, &c)
    if c:
        with gil:
            counter.dirs += c
    

cdef class Stream:

    def __init__(self, str path, *, root: Optional[str] = None):
        self.path = path.encode()
        cdef:
            bytes _root
            char* p = <char*>self.path
            char* r
        if not isabs(p):
            if not root:
                p = abspath(p)
                if p == NULL:
                    raise MemoryError
            else:
                _root = root.encode()
                r = <char*>_root
                p = join_path(r, p)

        self.path = p
        self._file = NULL
        self.closed = False
    
    cpdef void open(self, str mod = "w") except *:
        if self._file != NULL:
            return

        cdef:
            char* _path = <char*>self.path
            char* open_mod
            char* file_dir = dirname(self.path)
        if mod == 'w':
            open_mod = 'w'
        elif mod == 'a':
            open_mod = 'a'
        else:
            raise ValueError("Invalid open mod.")
            
        with nogil:
            if not isdir(file_dir):
                mkdir(file_dir)
            self._file = fopen(_path, open_mod)
            if self._file != NULL:
                self.closed = False
                return
            PyMem_Free(file_dir)
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