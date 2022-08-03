cdef extern from "Python.h":
    """
    __inline const char* PyType_GetNameStr(PyTypeObject* type) {
        return type->tp_name;
    }
    """

    const char* PyType_GetNameStr(type cls)
    const char* PyEval_GetFuncName(object func)