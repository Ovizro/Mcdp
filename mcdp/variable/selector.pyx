cimport cython
from cpython cimport PyErr_Format, PyObject_Str, PyDict_Next, PyDictProxy_New, PyObject
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
    if isinstance(val, dict) and key != "nbt":
        v = args2str(<dict>val)
    else:
        v = <str>PyObject_Str(val)
    _PyUnicodeWriter_WriteStr(writer, v)
    _PyUnicodeWriter_WriteChar(writer, ord(','))


cdef class Selector(McdpObject):
    def __cinit__(self, str name not None, _iter = None, **kwds):
        cdef:
            str k
            object v
        if len(name) != 2 or PyUnicode_ReadChar(name, 0) != ord('@')\
                or PyUnicode_ReadChar(name, 1) not in [ord('p'), ord('a'), ord('r'), ord('e'), ord('s')]:
            PyErr_Format(ValueError, "invalid selector %U", <void*>name)
        self.name = name
        self._args = kwds

        if _iter is None:
            return
        elif isinstance(_iter, dict):
            for k, v in (<dict>_iter).items():
                self.add_args(k, v)
        elif hasattr(type(_iter), "items"):
            for k, v in _iter.items():
                self.add_args(k, v)
        else:
            for k, v in _iter:
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
    if not _iter is None or kwds:
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


cdef Selector _DpSelector_DecodeSimple(str string):
    cdef:
        Py_UCS4 ch
        char state = 0
        int level = 0
        Py_ssize_t length = len(string)
        Py_ssize_t prev = 3
        str key
        Selector slt = Selector(string[:2])
    if length < 3:
        return slt
    if (PyUnicode_ReadChar(string, 2) != ord('[')
            or PyUnicode_ReadChar(string, length - 1) != ord(']')):
        PyErr_Format(ValueError, "selector string should be like @a[arg=xxx], not %U", <void*>string)
    for i in range(3, length - 1):
        ch = PyUnicode_ReadChar(string, i)
        if ch == ord('=') and state == 0b00:
            state = 1
            key = string[prev: i]
            prev = i + 1
        elif ch == ord('"'):
            if i == 0 or PyUnicode_ReadChar(string, i - 1) != ord('\\'):
                state ^= ~0b10
        elif state == 0b01:
            if ch == ord('{'):
                level += 1
            elif ch == ord('}'):
                level -= 1
            elif ch == ord(',') and not level:
                state = 0
                slt.add_args(key, string[prev: i])
                prev = i + 1
    if state != 1 or level:
        raise ValueError("invalid selector argument")
    slt.add_args(key, string[prev: i + 1])
    return slt


cdef object DpSelector_FromObject(object obj):
    cdef PyObject* fn_slt
    if isinstance(obj, str):
        return _DpSelector_DecodeSimple(<str>obj)
    elif isinstance(obj, Selector):
        return <Selector>obj
    else:
        fn_slt = _PyType_Lookup(type(obj), "__selector__")
        if fn_slt != NULL:
            return (<object>fn_slt)(obj)
        PyErr_Format(McdpTypeError, "unsupport type '%s'", Py_TYPE_NAME(obj))

cdef object DpSelector_FromString(const char* string):
    return _DpSelector_DecodeSimple(string.decode())

cdef object DpSelector_GetName(object slt):
    return (<Selector?>slt).name

cdef object DpSelector_GetArgs(object slt):
    return PyDictProxy_New((<Selector?>slt)._args)

cdef object DpStaticStr_FromSelector(object slt):
    return EntityNameString(str(<Selector?>slt))
