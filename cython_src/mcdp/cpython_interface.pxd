from libc.stdio cimport FILE


cdef extern from "<stdarg.h>":
    ctypedef void* va_list
    int vfprintf(FILE*, const char*, ...) nogil
    void va_start(va_list ap, const char* last_arg) nogil
    void va_end(va_list ap) nogil


cdef extern from "Python.h":
    """
    #define get_type_name(obj) (Py_TYPE(obj)->tp_name)
    """

    const char* get_type_name(object cls)
    const char* PyEval_GetFuncName(object func)
    str PyUnicode_FromFormatV(const char* format, va_list vargs)
    str PyUnicode_FromFormat(const char* format, ...)