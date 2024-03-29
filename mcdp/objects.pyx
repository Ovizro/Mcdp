cimport cython
from cpython cimport (PyObject, PyCapsule_New, PyCapsule_CheckExact, PyCapsule_GetPointer,
    Py_INCREF, Py_DECREF, PyDict_SetItemString, PyErr_Format, PyObject_GenericSetAttr)

from os.path import join

cdef class McdpObject(object):
    pass


cdef dict _namespace_property = {}


cdef class BaseNamespace(McdpObject):
    def __init__(self, name not None, bytes path = None):
        self.n_name = name
        if not path is None:
            self.n_path = join(path, name)
        else:
            self.n_path = name
        
    def __getattr__(self, str name not None):
        cdef:
            str _name
            T_property cfactory
        if name.startswith("n_"):
            _name = name[2:]
            if _name in _namespace_property:
                f_attr = _namespace_property[_name]
                if PyCapsule_CheckExact(f_attr):
                    cfactory = <T_property>PyCapsule_GetPointer(f_attr, "dp_nspProperty")
                    ret = cfactory(self)
                else:
                    ret = f_attr(self)
                PyObject_GenericSetAttr(self, name, ret)
                return ret
        PyErr_Format(AttributeError, "'%s' object has no attribute '%U'", Py_TYPE_NAME(self), <PyObject*>name)
    
    @staticmethod
    def property(attr not None):
        if not isinstance(attr, str):
            PyDict_SetItemString(_namespace_property, PyEval_GetFuncName(attr), attr)
            return attr
        def wrapper(func):
            _namespace_property[attr] = func
            return func
        return wrapper
    
    def __repr__(self):
        return PyUnicode_FromFormat("<namespace %U at %p>", <void*>self.n_name, <void*>self)


cdef api int DpNamespace_Property(const char* name, T_property factory) except -1:
    cdef object fac = PyCapsule_New(factory, "dp_nspProperty", NULL)

    _namespace_property[name.decode()] = fac
    return 0