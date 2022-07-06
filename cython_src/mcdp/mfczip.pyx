from libc.stdio cimport fopen, FILE
from libc.stdlib cimport free, atoi

cdef:
    char* mfc_cur_filename = NULL
    extern FILE* yyin

cdef extern from *:
    void __Pyx_AddTraceback(const char *funcname, int c_line, int py_line, const char *filename)


cdef public void mfczip_err(int lineno, const char* msg) except *:
    if mfc_cur_filename:
        __Pyx_AddTraceback("<mfczip>", 0, lineno, mfc_cur_filename)
    else:
        __Pyx_AddTraceback("<mfczip>", 0, lineno, "<string>")
    raise MFCzipError(msg.decode())


cdef public void mfczip_c_version(char* yyval):
    cdef int v = atoi(yyval)
    if v < 30:
        raise McdpVersionError("%d is not a invalid mfczip version." % v)


cdef public void mfczip_c_pragma(char* yyval):
    ...


cdef class 


cdef class MFCzipError(McdpError):
    pass