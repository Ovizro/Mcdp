cimport cython
from cpython cimport PyErr_Format
from ..cpython_interface cimport *

from typing_extensions import Protocol


class SelectorLike(Protocol):
    def __selector__(self) -> Selector:
        pass


cdef class Selector(McdpObject):
    def __init__(self, str name not None, _iter = None, **kwds):
        cdef:
            str tmp = name[:2]
            list l_args
            list kv
            str k
            object v
        if not tmp in ["@p", "@a", "@r", "@e", "@s"]:
            raise ValueError("Invalid selector.")
        self.name = tmp
        self.args = kwds
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

        with cython.nonecheck(False):
            if len(name) > 2:
                l_args = <list>name[3:-1].split(',')
                for tmp in l_args:
                    kv = <list>tmp.split('=')
                    k, v = kv
                    self.add_args(k, v)
        
    cpdef void add_args(self, str key, value) except *:
        cdef:
            dict attrs = self.args
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
    
    def __selector__(self) -> Selector:
        return self
    
    def __mcstr__(self) -> MCString:
        return MCString(selector=str(self))
    
    def __repr__(self):
        return "Selector(%s)" % self

    def __str__(self):
        cdef:
            object k, v, i
            str slt_string
            _PyUnicodeWriter writer
        if not self.args:
            return self.name

        _PyUnicodeWriter_Init(&writer)
        try:
            _PyUnicodeWriter_WriteStr(&writer, self.name)
            _PyUnicodeWriter_WriteChar(&writer, ord('['))
            for k, v in self.args.items():
                if isinstance(v, set):
                    for i in <set>v:
                        _PyUnicodeWriter_WriteStr(&writer, k)
                        _PyUnicodeWriter_WriteChar(&writer, ord('='))
                        _PyUnicodeWriter_WriteStr(&writer, <str>str(i))
                        _PyUnicodeWriter_WriteChar(&writer, ord(','))
                else:
                    _PyUnicodeWriter_WriteStr(&writer, k)
                    _PyUnicodeWriter_WriteChar(&writer, ord('='))
                    _PyUnicodeWriter_WriteStr(&writer, <str>str(v))
                    _PyUnicodeWriter_WriteChar(&writer, ord(','))

            slt_string = _PyUnicodeWriter_Finish(&writer)
            PyUnicode_WriteChar(slt_string, len(slt_string) - 1, ord(']'))
            return slt_string
        except:
            _PyUnicodeWriter_Dealloc(&writer)
            raise


def selector(t_slt not None, _iter = None, **kwds):
    if isinstance(t_slt, str):
        return Selector(t_slt, _iter, **kwds)
    return DpSelector_FromObject(t_slt)


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