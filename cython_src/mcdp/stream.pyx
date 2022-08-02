# distutils: sources = mcdp/path.c

cimport cython
from libc.stdio cimport fopen, fputs, fputc, fclose, sprintf
from libc.stdlib cimport malloc, free
from libc.string cimport strlen, strcpy, strcmp
from cpython cimport PyErr_Format

try:
    import ujson as json
except ImportError:
    import json


cdef StreamCounter counter = StreamCounter(0, 0, 0, 0)


cdef inline StreamCounter get_counter() nogil:
    return counter

cdef inline void print_counter():
    cdef char buffer[256]
    sprintf(buffer, "%d dirs, %d files, %d commands, %d chars in total",
        counter.dirs, counter.files, counter.commands, counter.chars)
    print(buffer.decode())


cdef int _mkdir(const char* path, int* _c) nogil:
    cdef:
        char* pdir = dirname(path)
        int _sc
    if pdir == NULL:
        return -2
    elif strcmp(pdir, ".") == 0 or isdir(pdir):
        _sc = cmkdir(path, 777)
        if _sc != 0:
            free(pdir)
            return -1
    else:
        _mkdir(pdir, _c)
    free(pdir)
    _c[0] += 1
    return 0

cpdef void mkdir(const char* dir_path) except *:
    cdef:
        int _s, c = 0

    with nogil:
        if isdir(dir_path) == 1:
            return
        _s = _mkdir(dir_path, &c)

    if _s == -1:
        raise OSError("fail to create dir")
    elif _s == -2:
        raise MemoryError
    if c:
        counter.dirs += c

cpdef void rmtree(const char* path) except *:
    cdef int _s
    with nogil:
        _s = _rmtree(path)

    if _s == -1:
        raise OSError("dir not exist")
    elif _s == -2:
        raise OSError("fail to remove file")
    elif _s == -3:
        raise OSError("fail to remove dir")

cpdef void copyfile(const char* src, const char* dst) except *:
    cdef int _s
    with nogil:
        _s = _copyfile(src, dst)
    
    if _s == -1:
        raise OSError("fail to open file")
    elif _s == -2:
        raise MemoryError
    

cdef class Stream:
    def __cinit__(self, bytes path not None, *, bytes root = None):
        cdef:
            char* p = path
            Py_ssize_t l_str
        if not isabs(p):
            if not root:
                p = abspath(p)
            else:
                p = join(root, p)
            if p == NULL:
                raise MemoryError
            self.path = p
        else:
            l_str = len(path) + 1
            self.path = <char*>malloc(l_str * sizeof(char))
            if self.path == NULL:
                raise MemoryError
            strcpy(self.path, p)
        self._file = NULL
        self.closed = False
    
    def __dealloc__(self):
        if self.path != NULL:
            free(self.path)
        if self._file != NULL:
            fclose(self._file)
            self._file = NULL
    
    cpdef void open(self, str mod = "w") except *:
        if self._file != NULL:
            return

        cdef:
            const char* open_mod
            char* file_dir
        if mod == 'w':
            open_mod = 'w'
        elif mod == 'a':
            open_mod = 'a'
        else:
            raise ValueError("Invalid open mod.")
            
        with nogil:
            file_dir = dirname(self.path)
            if not isdir(file_dir) and _mkdir(file_dir, &(counter.dirs)):
                raise FileNotFoundError("No such file or directory")
            free(file_dir)
            self._file = fopen(self.path, open_mod)
            if self._file != NULL:
                self.closed = False
                return
        PyErr_Format(OSError, "fail to open %s", self.path)
    
    @cython.nonecheck(False)
    cdef int put(self, const char* _s) except -1:
        if self._file == NULL:
            raise OSError("not writable")

        cdef int c
        with nogil:
            c = fputs(_s, self._file)

            if c < 0:
                with gil:
                    PyErr_Format(OSError, "fail to write to file %s", self.path)
            c = strlen(_s)
            counter.chars += c
        return c
    
    @cython.nonecheck(False)
    cdef int putc(self, char ch) except -1:
        if self._file == NULL:
            raise OSError("not writable")
        
        cdef int c
        with nogil:
            c = fputc(ch, self._file)
            if c < 0:
                with gil:
                    PyErr_Format(OSError, "fail to write to file %s", self.path)
            counter.chars += 1
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
                with gil:
                    PyErr_Format(OSError, "fail to write to file %s", self.path)
            counter.chars += c
        return c
    
    @cython.nonecheck(False)
    cdef int format(self, const char* _s, ...) except -1:
        cdef:
            va_list ap
            int c
        va_start(ap, _s)
        c = self.vformat(_s, ap)
        va_end(ap)
        return c
    
    cpdef int write(self, str _s) except -1:
        self.put(_s.encode())

    cpdef int dump(self, object data) except -1:
        cdef str d = json.dumps(data, indent=4)
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