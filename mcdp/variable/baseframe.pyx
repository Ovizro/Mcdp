from libc.stdio cimport sprintf
from cpython cimport PyObject, PyErr_Format, PyObject_GenericGetAttr,\
    PyObject_GenericSetAttr, PyTuple_New, PyTuple_SET_ITEM, PyDict_GetItem, Py_INCREF,\
    PyCapsule_New, PyCapsule_CheckExact, PyCapsule_GetPointer


cdef class NamePool:
    def __cinit__(self, format = None):
        self.used_size = 0
        self.cache = set()
        if isinstance(format, str):
            self._format = (<str>format).encode()
        else:
            self._format = format
    
    cpdef str fetch(self):
        cdef:
            char buffer[4 + 8 + 1]
            const char* f = "dpc_%04X"
        if self.cache:
            return self.cache.pop()
        if not self._format is None:
            f = <const char*>self._format
        sprintf(buffer, f, self.used_size)
        self.used_size += 1
        return buffer.decode()
    
    cpdef void release(self, str name) except *:
        if name is None:
            raise ValueError("expect str, not NoneType")
        self.cache.add(name)
    
    @property
    def format(self):
        if self._format is None:
            return "dpc_%04X"
        return self._format.decode()
    
    @format.setter
    def format(self, str format_str not None):
        self._format = format_str.encode()
    
    def __repr__(self):
        return PyUnicode_FromFormat("<name pool(%d) at %p>", self.used_size, <void*>self)


cdef class BaseFrame(McdpObject):
    def __init__(self, BaseNamespace namespace, *, Py_ssize_t channel = 2):
        self.namespace = namespace
        self.name_pools = PyTuple_New(channel)
        for i in range(channel):
            p = NamePool()
            Py_INCREF(p)
            PyTuple_SET_ITEM(self.name_pools, i, p)
        
    def __bool__(self):
        return not self.namespace is None
    
    def __setattr__(self, str name not None, value):
        if not name.startswith('__') or not name.endswith('__'):
            value = DpVar_FromObject(value)
            (<FrameVariable>value).bind(self)
        PyObject_GenericSetAttr(self, name, value)
    
    @property
    def __namespace__(self):
        if self.namespace is None:
            raise AttributeError("unbound frame has no attribute '__namespace__'")
        return self.namespace
    
    def __repr__(self):
        if self.namespace is None:
            return PyUnicode_FromFormat("<unbound frame object at %p>", <void*>self)
        else:
            return PyUnicode_FromFormat("<frame object in %S at %p", <void*>self.namespace, <void*>self)


cdef class FrameVariable(McdpObject):
    def __init__(self, str name = None, *, Py_ssize_t channel_id = 0):
        self.name = name
        if not name is None:
            self.special_name = True
        self.channel_id = channel_id
    
    def __dealloc__(self):
        if not self.name is None and not self.special_name:
            (<NamePool>(self.frame.name_pools[self.channel_id])).release(self.name)

    cpdef void bind(self, BaseFrame frame) except *:
        self.frame = frame
        if not self.special_name:
            self.name = (<NamePool>(frame.name_pools[self.channel_id])).fetch()
    
    @property
    def __name__(self):
        if self.name is None:
            raise McdpUnboundError("unbound variable has no attribute '__name__'")
        return self.name
    
    @__name__.setter
    def __name__(self, str value not None):
        self.name = value
        self.special_name = True

    @property
    def namespace(self):
        if not self.frame:
            raise McdpUnboundError("unbound variable has no attribute '__namespace__'")
        return self.frame.namespace
    
    @property
    def valid(self):
        return not self.name is None
    

cdef dict _var_builder = {}
    

def var_builder(type _t not None):
    def wrapper(func):
        _var_builder[_t] = func
        return func
    return wrapper


def set_special(frame not None, name not None, attr):
    DpFrame_SetSpecialVar(frame, name, attr)


class FrameVariableWrapper(FrameVariable):
    def __init_subclass__(cls, *, type as_type = None):
        if not as_type is None:
            _var_builder[as_type] = cls


cdef object DpVar_FromObject(object obj):
    if isinstance(obj, FrameVariable):
        return obj

    cdef:
        PyObject* o
        tuple mro = <tuple>Py_TYPE_MRO(obj)
    for i in mro:
        o = PyDict_GetItem(_var_builder, i)
        if o != NULL:
            var = (<object>o)(obj)
            if not var is NotImplemented:
                return <FrameVariable?>var
    PyErr_Format(McdpTypeError, "unsupport type '%s'", Py_TYPE_NAME(obj))


cdef int DpVar_RegisterBuilder(type t, object func) except -1:
    _var_builder[t] = func
    return 0


cdef int DpFrame_SetVar(object frame, object name, object attr) except -1:
    cdef FrameVariable var = <FrameVariable>DpVar_FromObject(attr)
    var.bind(frame)
    PyObject_GenericSetAttr(frame, name, var)


cdef int DpFrame_SetSpecialVar(object frame, object name, object attr) except -1:
    cdef FrameVariable var = <FrameVariable>DpVar_FromObject(attr)
    var.name = name
    var.special_name = True
    var.bind(frame)
    PyObject_GenericSetAttr(frame, name, var)
    return 0