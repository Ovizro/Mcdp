from libc.stdio cimport FILE
from libc.stdint cimport uint64_t
from cpython cimport PyObject


cdef extern from "<stdarg.h>":
    ctypedef void* va_list
    int vfprintf(FILE*, const char*, ...) nogil
    void va_start(va_list ap, const char* last_arg) nogil
    void va_end(va_list ap) nogil


cdef extern from "Python.h":
    """
    #define Py_TYPE_NAME(obj) (Py_TYPE(obj)->tp_name)
    #define Py_TYPE_MRO(obj) (Py_TYPE(obj)->tp_mro)
    """

    const char* Py_TYPE_NAME(object cls) nogil
    PyObject* Py_TYPE_MRO(object cls) nogil
    PyObject* _PyType_Lookup(type t, str name)
    const char* PyEval_GetFuncName(object func)

    char *PyOS_double_to_string(double val, char format_code, int precision, int flags, int *ptype) except NULL

    ctypedef uint64_t Py_UCS4

    str PyUnicode_FromFormatV(const char* format, va_list vargs)
    str PyUnicode_FromFormat(const char* format, ...)
    Py_UCS4 PyUnicode_ReadChar(str unicode, Py_ssize_t index)
    int PyUnicode_WriteChar(str unicode, Py_ssize_t index, Py_UCS4 character) except -1

    enum PyUnicode_Kind:
        PyUnicode_WCHAR_KIND = 0
        PyUnicode_1BYTE_KIND = 1
        PyUnicode_2BYTE_KIND = 2
        PyUnicode_4BYTE_KIND = 4

    ctypedef struct _PyUnicodeWriter:
        PyObject* buffer
        void* data
        PyUnicode_Kind kind
        Py_UCS4 maxchar
        Py_ssize_t size
        Py_ssize_t pos

        # minimum number of allocated characters (default: 0)
        Py_ssize_t min_length

        # minimum character (default: 127, ASCII)
        Py_UCS4 min_char

        # If non-zero, overallocate the buffer (default: 0).
        unsigned char overallocate

        # If readonly is 1, buffer is a shared string (cannot be modified)
        # and size is set to 0.
        unsigned char readonly_ "readonly"
    
    void _PyUnicodeWriter_Init(_PyUnicodeWriter *writer) nogil
    int _PyUnicodeWriter_Prepare(_PyUnicodeWriter *writer, Py_ssize_t length, Py_UCS4 maxchar) except -1
    int _PyUnicodeWriter_PrepareKind(_PyUnicodeWriter *writer, PyUnicode_Kind kind) except -1
    int _PyUnicodeWriter_WriteChar(_PyUnicodeWriter *writer, Py_UCS4 ch) except -1
    int _PyUnicodeWriter_WriteStr(_PyUnicodeWriter *writer, str string) except -1
    int _PyUnicodeWriter_WriteASCIIString(_PyUnicodeWriter *writer, const char* string, Py_ssize_t len) except -1
    str _PyUnicodeWriter_Finish(_PyUnicodeWriter *writer)
    void _PyUnicodeWriter_Dealloc(_PyUnicodeWriter *writer)