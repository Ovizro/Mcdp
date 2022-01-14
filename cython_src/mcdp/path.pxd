cdef extern from "path.c":
    char* _fspath(const char* path) nogil
    char* _join_path(const char* base, const char* path) nogil
    char* join_path(const char* base, const char* path) nogil
    void split(const char* path, char** base, char** name) nogil
    char* dirname(const char* path) nogil
    char* basename(const char* path) nogil
    int isabs(const char* path) nogil
    int isexist(const char* path) nogil
    int isdir(const char* path) nogil
    int isfile(const char* path) nogil
    char* abspath(const char* path) nogil

    int _rmtree(const char* path) nogil
    int rmtree(const char* path) nogil
    int copyfile(const char* src, const char* dst) nogil

cdef extern from *:
    int cmkdir "_mkdir" (const char* path) nogil
    int chdir "_chdir" (const char* path) nogil
    
    void* PyMem_Malloc(Py_ssize_t) nogil
    void PyMem_Free(void* p) nogil