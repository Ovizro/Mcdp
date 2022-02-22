cimport cython
from libc.stdio cimport fopen, fputs, fclose, sprintf
from libc.stdlib cimport malloc, free
from libc.string cimport strlen, strcpy

import ujson


cdef StreamCounter counter = StreamCounter(0, 0, 0, 0)


cdef inline StreamCounter get_counter() nogil:
    return counter

cdef inline void print_counter():
    cdef char buffer[128]
    sprintf(buffer, "%d dirs, %d files, %d commands, %d chars in total",
        counter.dirs, counter.files, counter.commands, counter.chars)
    print(buffer.decode())


cdef void _mkdir(const char* path, int* _c) nogil except *:
    cdef:
        char* pdir = dirname(path)
        int _sc
    if pdir == NULL:
        with gil:
            raise MemoryError
    if isdir(pdir) == 1:
        _sc = cmkdir(path)
        if _sc != 0:
            free(pdir)
            with gil:
                raise OSError("fail to create dir")
    else:
        _mkdir(pdir, _c)
    free(pdir)
    _c[0] += 1
    

cpdef void mkdir(const char* dir_path) nogil except *:
    if isdir(dir_path) == 1:
        return

    cdef int c = 0
    _mkdir(dir_path, &c)
    if c:
        counter.dirs += c
    

cdef class Stream:

    def __cinit__(self, str path, *, str root = None):
        cdef:
            bytes _tmp = path.encode()
            char* p = _tmp
            Py_ssize_t l_str
        if not isabs(p):
            if not root:
                p = abspath(p)
            else:
                _tmp = root.encode()
                p = join_path(_tmp, p)
            if p == NULL:
                raise MemoryError
            self.path = p
        else:
            l_str = len(_tmp) + 1
            self.path = <char*>malloc(l_str * sizeof(char))
            if self.path == NULL:
                raise MemoryError
            strcpy(self.path, p)
        self._file = NULL
        self.closed = False
    
    def __dealloc__(self):
        if self._file != NULL:
            fclose(self._file)
            self._file = NULL
    
    cpdef void open(self, str mod = "w") except *:
        if self._file != NULL:
            return

        cdef:
            const char* open_mod
            char* file_dir = dirname(self.path)
        if mod == 'w':
            open_mod = 'w'
        elif mod == 'a':
            open_mod = 'a'
        else:
            raise ValueError("Invalid open mod.")
            
        with nogil:
            mkdir(file_dir)
            free(file_dir)
            self._file = fopen(self.path, open_mod)
            if self._file != NULL:
                self.closed = False
                return
        raise OSError("fail to open %s" % self.path)
    
    @cython.nonecheck(False)
    cpdef int fwrite(self, const char* _s) except -1:
        if self._file == NULL:
            raise OSError("not writable")

        cdef:
            int c

        with nogil:
            c = fputs(_s, self._file)

            if c < 0:
                raise OSError("fail to write to file %s" % self.path)
            c = strlen(_s)
            counter.chars += c
        return c
    
    cpdef int write(self, str _s) except -1:
        self.fwrite(_s.encode())

    cpdef int dump(self, data) except -1:
        cdef str d = ujson.dumps(data, indent=4)
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