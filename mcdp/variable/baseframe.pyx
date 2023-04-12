from libc.stdio cimport sprintf
from cpython cimport PyObject, PyErr_Format, PyObject_GenericGetAttr,\
    PyObject_GenericSetAttr, PyTuple_New, PyTuple_SET_ITEM, PyDict_GetItem, Py_INCREF,\
    PyCapsule_New, PyCapsule_CheckExact, PyCapsule_GetPointer
from ..objects cimport DpNamespace_Property, T_property
from .selector cimport SL_S, DpSelector_FromObject


cdef Selector _nspp_stacktop(BaseNamespace nsp):
    return Selector("@e", limit=1, tag={PyUnicode_FromFormat("Mcdp_%U", <void*>nsp.n_name), "Mcdp_stackTop"})

cdef Selector _nspp_stacknxt(BaseNamespace nsp):
    return Selector("@e", limit=1, tag={PyUnicode_FromFormat("Mcdp_%U", <void*>nsp.n_name), "Mcdp_stackNext"})

DpNamespace_Property("stack_selector", <T_property>_nspp_stacktop)
DpNamespace_Property("next_stack_selector", <T_property>_nspp_stacknxt)


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
        if self.used_size != 0:
            raise ValueError("cannot change the format of a used name pool")
        self._format = format_str.encode()
    
    def __repr__(self):
        return PyUnicode_FromFormat("<name pool(%d) at %p>", self.used_size, <void*>self)


cdef class BaseFrame(McdpObject):
    def __init__(self, BaseNamespace namespace not None, *, Py_ssize_t channel = 2, frame_selector = None):
        self.flag = IS_VALID
        self.namespace = namespace
        self.name_pools = PyTuple_New(channel)
        if frame_selector is None:
            self.frame_selector = SL_S
        else:
            self.frame_selector = <Selector>DpSelector_FromObject(frame_selector)
        for i in range(channel):
            p = NamePool()
            Py_INCREF(p)
            PyTuple_SET_ITEM(self.name_pools, i, p)
        
    def __setattr__(self, str name not None, value):
        if self.flag & FORCE_BUILD_VALUE and not (name.startswith('__') and name.endswith('__')):
            value = DpVar_FromObject(value)
        if isinstance(value, FrameVariable):
            if self.flag & FORCE_SPECIAL_NAME:
                self.set_special(name, <FrameVariable>value)
                return
            (<FrameVariable>value).bind(self)
        PyObject_GenericSetAttr(self, name, value)
    
    cdef void set_special(self, str name, FrameVariable var) except *:
        if self.flag & SPECIAL_NAME_RENAME:
            name = PyUnicode_FromFormat("Mcdp_%U_%s_%U",
                <void*>self.namespace.n_name, Py_TYPE_GetName(var), <void*>name)
        var.name = name
        var.special_name = True
        var.bind(self)
        PyObject_GenericSetAttr(self, name, var)
    
    @property
    def __namespace__(self):
        return self.namespace
    
    def __selector__(self):
        return self.frame_selector
    
    def __repr__(self):
        return PyUnicode_FromFormat("<frame object in namespace %U at %p>", <void*>self.namespace.n_name, <void*>self)


cdef class FrameVariable(McdpObject):
    def __init__(self, str name = None, *, Py_ssize_t channel_id = 0, BaseFrame frame = None):
        self.name = name
        if not name is None:
            self.special_name = True
        self.channel_id = channel_id
        if not frame is None:
            self.bind(frame)
    
    def __dealloc__(self):
        if not self.name is None and not self.special_name:
            (<NamePool>(self.frame.name_pools[self.channel_id])).release(self.name)

    cpdef void bind(self, BaseFrame frame) except *:
        self.frame = frame
        if not self.special_name:
            self.name = (<NamePool>(frame.name_pools[self.channel_id])).fetch()
    
    cdef void ensure_bound(self) except *:
        if self.frame is None:
            raise McdpUnboundError("unbound variable")
    
    @property
    def __name__(self):
        if self.name is None:
            raise McdpUnboundError("unbound variable has no attribute '__name__'")
        return self.name
    
    @__name__.setter
    def __name__(self, str value not None):
        if not self.name is None and not self.special_name:
            (<NamePool>(self.frame.name_pools[self.channel_id])).release(self.name)
        self.name = value
        self.special_name = True

    @property
    def namespace(self):
        if self.frame is None:
            raise McdpUnboundError("unbound variable has no attribute '__namespace__'")
        return self.frame.namespace
    
    @property
    def valid(self):
        return not self.name is None and not self.frame is None
    
    def __repr__(self):
        cdef const char* name = Py_TYPE_GetName(self)
        if self.frame is None:
            if not self.name is None:
                return PyUnicode_FromFormat("<unbound %s variable at %p>", name, <void*>self)
            else:
                return PyUnicode_FromFormat("<unbound %s variable '%U' at %p>", name, <void*>self.name, <void*>self)
        else:
            return PyUnicode_FromFormat("<%s variable '%U' in namespace %U at %p>",
                name, <void*>self.name, <void*>self.frame.namespace.n_name, <void*>self)
    

cdef dict _var_builder = {}
    

def var_builder(type _t not None):
    def wrapper(func):
        _var_builder[_t] = func
        return func
    return wrapper


def set_special(frame not None, name not None, attr):
    DpFrame_SetSpecialVar(frame, name, attr)


def get_channel(frame not None, Py_ssize_t channel_id):
    return DpFrame_GetNamePool(frame, channel_id)


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

cdef int DpVar_Bind(object var, object frame) except -1:
    (<FrameVariable?>var).bind(frame)
    return 0


cdef object Dp_VaBuildValue(const char* format, va_list ap):
    obj = Py_VaBuildValue(format, ap)
    return DpVar_FromObject(obj)

cdef object Dp_BuildValue(const char* format, ...):
    cdef va_list ap
    va_start(ap, format)
    try:
        return Dp_VaBuildValue(format, ap)
    finally:
        va_end(ap)


cdef int DpFrame_SetVar(object frame, object name, object attr) except -1:
    cdef FrameVariable var = <FrameVariable>DpVar_FromObject(attr)
    var.bind(frame)
    PyObject_GenericSetAttr(frame, name, var)
    return 0

cdef int DpFrame_SetSpecialVar(object frame, object name, object attr) except -1:
    BaseFrame.set_special(frame, name, <FrameVariable>DpVar_FromObject(attr))
    return 0

cdef object DpFrame_GetNamePool(object frame, Py_ssize_t channel_id):
    return (<BaseFrame?>frame).name_pools[channel_id]