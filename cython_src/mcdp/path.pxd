cdef extern from *:
    """
    #ifdef _WIN32
    #define PATH_PUBLIC __declspec(dllexport)
    #endif
    """

cdef extern from "path.h":
    char* _fspath(const char* path, int* len) nogil
    char* _fsdir(const char* path, int* len) nogil
    char* fspath(const char* path) nogil
    char* fsdir(const char* path) nogil
    char* join(const char* base, const char* path) nogil
    void split(const char* path, char** base, char** name) nogil
    char* dirname(const char* path) nogil
    char* basename(const char* path) nogil
    int isabs(const char* path) nogil
    int isexist(const char* path) nogil
    int isdir(const char* path) nogil
    int isfile(const char* path) nogil
    char* abspath(const char* path) nogil

    int rmtree(const char* path) nogil
    int copyfile(const char* src, const char* dst) nogil

    int cmkdir "MKDIR" (const char* path, int mod) nogil
    int cchdir "CHDIR" (const char* path) nogil
    int cgetcwd "GETCWD" (const char* path) nogil