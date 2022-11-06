cimport cython
from cpython cimport PyErr_Format, PyObject_Str, PyDict_Next
from ..cpython_interface cimport *

from typing import Union
from typing_extensions import Protocol


class SelectorLike(Protocol):
    def __selector__(self) -> Selector:
        pass

T_Selector = Union[str, Selector, SelectorLike]


cdef str args2str(dict d):
    cdef:
        str k, ret
        object v
        _PyUnicodeWriter writer

    if not d:
        return "{}"
        
    _PyUnicodeWriter_Init(&writer)
    writer.overallocate = 1
    try:
        _PyUnicodeWriter_WriteChar(&writer, ord('{'))
        for k, v in d.items():
            write_args(&writer, k, v)
        ret = _PyUnicodeWriter_Finish(&writer)
        PyUnicode_WriteChar(ret, len(ret) - 1, ord('}'))
        return ret
    except:
        _PyUnicodeWriter_Dealloc(&writer)
        raise

cdef void write_args(_PyUnicodeWriter* writer, str key, object val) except *:
    cdef:
        object i
        str v
    if isinstance(val, set):
        for i in <set>val:
            write_args(writer, key, i)
        return
        
    _PyUnicodeWriter_WriteStr(writer, key)
    _PyUnicodeWriter_WriteChar(writer, ord('='))
    if isinstance(val, str):
        v = val
    if isinstance(val, dict):
        v = args2str(<dict>val)
    else:
        v = <str>PyObject_Str(val)
    _PyUnicodeWriter_WriteStr(writer, v)
    _PyUnicodeWriter_WriteChar(writer, ord(','))


cdef class Selector(McdpObject):
    def __cinit__(self, str name not None, _iter = None, **kwds):
        cdef:
            str tmp = name[:2]
            list l_args
            list kv
            str k
            object v
        if not tmp in ["@p", "@a", "@r", "@e", "@s"]:
            raise ValueError("Invalid selector.")
        self.name = tmp
        self._args = kwds
        if _iter:
            if isinstance(_iter, dict):
                for k, v in (<dict>_iter).items():
                    self.add_args(k, v)
            elif hasattr(type(_iter), "items"):
                for k, v in _iter.items():
                    self.add_args(k, v)
            else:
                for i in _iter:
                    if len(i) == 2:
                        self.add_args(i[0], i[1])
                    else:
                        raise TypeError("invalid iteration")

        if len(name) <= 2:
            return

        if (PyUnicode_ReadChar(name, 2) != ord('[') or
                PyUnicode_ReadChar(name, len(name) - 1) != ord(']')):
            raise ValueError("selector string should be like @a[arg=xxx], not %s" % name)
        l_args = name[3:-1].split(',')
        for tmp in l_args:
            kv = tmp.split('=', 2)
            k, v = kv
            self.add_args(k, v)
        
    cpdef void add_args(self, str key, value) except *:
        cdef:
            dict attrs = self._args
            set raw
        if not key in attrs:
            attrs[key] = value if isinstance(value, set) else {value}
            return

        _raw = attrs[key]
        if not isinstance(_raw, set):
            raw = {_raw}
        else:
            raw = <set>_raw
        if isinstance(value, set):
            raw.update(<set>value)
        else:
            raw.add(value)
        attrs[key] = raw
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, val: Any):
        if isinstance(val, cls):
            return val
        else:
            return DpSelector_FromObject(val)
    
    @property
    def args(self):
        return PyDictProxy_New(self._args)
    
    def __eq__(self, other):
        if not isinstance(other, Selector):
            return NotImplemented
        
        cdef Selector slt = <Selector>other
        if slt.name != self.name:
            return False
        return slt._args == self._args
    
    def __selector__(self) -> Selector:
        return self
    
    def __mcstr__(self) -> String:
        return EntityNameString(str(self))
    
    def __repr__(self):
        return "Selector(%s)" % self

    def __str__(self):
        cdef str ret
        if not self._args:
            return self.name

        ret = args2str(self._args)
        PyUnicode_WriteChar(ret, 0, ord('['))
        PyUnicode_WriteChar(ret, len(ret) - 1, ord(']'))
        return self.name + ret


def selector(t_slt not None, _iter = None, **kwds):
    if isinstance(t_slt, str):
        return Selector(t_slt, _iter, **kwds)
    return DpSelector_FromObject(t_slt)


SL_S = Selector("@s")
SL_A = Selector("@a")
SL_E = Selector("@e")
SL_P = Selector("@p")

s_current = SL_S
s_all     = SL_A
s_entity  = SL_E
s_nearest = SL_P

cdef object _nspp_top(object nsp):
    cdef:
        BaseNamespace n = <BaseNamespace>nsp
        str name = n.n_name
    return Selector("@e", tag={"McdpName_" + name, "Mcdp_Top"})

DpNamespace_Property("top", _nspp_top)


cdef object DpSelector_FromObject(object obj):
    if isinstance(obj, str):
        return Selector(obj)
    elif isinstance(obj, Selector):
        return <Selector>obj
    elif hasattr(type(obj), "__selector__"):
        return obj.__selector__()
    else:
        PyErr_Format(McdpTypeError, "'%s' object is not a selector", Py_TYPE_NAME(obj))

cdef object DpSelector_FromString(const char* string):
    return Selector(string.decode())

cdef object DpSelector_GetName(object slt):
    return (<Selector?>slt).name

cdef object DpSelector_GetArgs(object slt):
    return PyDictProxy_New((<Selector?>slt)._args)

cdef object DpStaticStr_FromSelector(object slt):
    return EntityNameString(str(<Selector?>slt))
