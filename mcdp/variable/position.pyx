from libc.stdio cimport sprintf
from libc.string cimport memset
from cpython cimport PyTuple_New, PyTuple_SET_ITEM, Py_INCREF,\
    PyIter_Check, PyNumber_Add, PyNumber_Subtract, PyNumber_Multiply, PyNumber_TrueDivide

from enum import Enum


class ComponentType(Enum):
    local = LOCAL
    relative = RELATIVE
    absolute = ABSOLUTE


cdef float fl_add(float a, float b):
    return a + b

cdef float fl_sub(float a, float b):
    return a - b

cdef float fl_rsub(float b, float a):
    return a - b

cdef float fl_mul(float a, float b):
    return a * b

cdef float fl_div(float a, float b):
    return a / b

cdef float fl_rdiv(float b, float a):
    return a / b

cdef object ob_rsub(object b, object a):
    return PyNumber_Subtract(a, b)

cdef object ob_rdiv(object b, object a):
    return PyNumber_TrueDivide(a, b)

cdef MCPos_TypeFlag get_type_flag(object type) except *:
    cdef MCPos_TypeFlag _type = NANTYPE
    if type is None:
        pass
    elif isinstance(type, int):
        _type = <MCPos_TypeFlag>(<int>type)
    else:
        _type = <MCPos_TypeFlag?>type.value
    return _type

cdef tuple get_component_str(str stringobj, object type):
    cdef:
        str s = stringobj
        list lc = s.split()
    for i in range(len(lc)):
        lc[i] = Component(lc[i], type=type)
    return tuple(lc)


cdef class Component(McdpObject):
    def __cinit__(self, value not None, *, type = None):
        cdef:
            MCPos_TypeFlag _type = get_type_flag(type)
            str _value
            Py_ssize_t length
            char buffer[18]

        if isinstance(value, (int, float)):
            self.offset = <float>value
            if self.offset > 30000000:
                raise McdpValueError("position offset should not be more than 3e7")
            self.type_flag = _type or ABSOLUTE
            memset(buffer, 0, 18 * sizeof(char))
            if _type == RELATIVE:
                sprintf(buffer, "~%f", self.offset)
            elif _type == LOCAL:
                sprintf(buffer, "^%f", self.offset)
            else:
                sprintf(buffer, "%f", self.offset)
            for i in range(17, 0, -1):
                if buffer[i] == ord('0'):
                    buffer[i] = 0
                elif buffer[i] == ord('.'):
                    buffer[i] = 0
                    break
                elif buffer[i] != 0:
                    break
            self.raw_value = buffer.decode()
            return

        _value = value
        self.raw_value = _value
        if _value[0] == '^':
            _value = _value[1:]
            self.type_flag = LOCAL
        elif value[0] == '~':
            _value = _value[1:]
            self.type_flag = RELATIVE
        else:
            self.type_flag = ABSOLUTE
        
        if _value:
            self.offset = float(_value)
            if self.offset > 30000000:
                raise McdpValueError("position offset should not be more than 3e7")
        else:
            self.offset = 0.0
        if _type and _type != self.type_flag:
            raise McdpValueError("unmatch position value")
    
    @property
    def type(self):
        return ComponentType(self.type_flag)
        
    def __eq__(self, other):
        if not isinstance(other, Component):
            return NotImplemented
        cdef Component o = <Component>other
        if self.type_flag != o.type_flag:
            return False
        return abs(self.offset - o.offset) <= 1e-6
    
    cdef object _calc(self, object other, fl_opt opt):
        cdef type cls = <type>type(self)
        if isinstance(other, (int, float)):
            return cls(opt(self.offset, <float>other), type=self.type_flag)
        elif isinstance(other, Component) and (<Component>other).type_flag == self.type_flag:
            return cls(opt(self.offset, (<Component>other).offset), type=self.type_flag)
        return NotImplemented
    
    def __add__(self, other):
        return self._calc(other, fl_add)
    
    def __radd__(self, other):
        return self._calc(other, fl_add)

    def __sub__(self, other):
        return self._calc(other, fl_sub)

    def __rsub__(self, other):
        return self._calc(other, fl_rsub)
    
    def __mul__(self, other):
        return self._calc(other, fl_mul)

    def __rmul__(self, other):
        return self._calc(other, fl_mul)
        
    def __truediv__(self, other):
        return (<Component>self)._calc(other, fl_div)
        
    def __rtruediv__(self, other):
        return (<Component>self)._calc(other, fl_rdiv)
    
    def __pos__(self):
        return self
    
    def __neg__(self):
        cdef type cls = <type>type(self)
        return cls(-self.offset, type=self.type_flag)
    
    def __abs__(self):
        cdef type cls = <type>type(self)
        return cls(abs(self.offset), type=self.type_flag)
    
    def __float__(self):
        return self.offset

    def __repr__(self):
        return "Component(%s)" % self.raw_value

    def __str__(self):
        return self.raw_value


cdef class Position(McdpObject):
    def __cinit__(self, val = None, *, x = None, y = None, z = None, type = None):
        if isinstance(val, str):
            self.components = get_component_str(val, type)
        else:
            if not val is None:
                x, y, z = val
            
            if not isinstance(x, Component):
                x = Component(x, type=type)
            if not isinstance(y, Component):
                y = Component(y, type=type)
            if not isinstance(z, Component):
                z = Component(z, type=type)
            self.components = (x, y, z)
        self._validate_comp()

    cdef void _validate_comp(self) except *:
        cdef:
            Component i
            MCPos_TypeFlag t = NANTYPE
        for i in self.components:
            if i.type_flag == LOCAL:
                if t > LOCAL:
                    raise McdpValueError("incurrect position component type")
                t = LOCAL
            else:
                if t == LOCAL:
                    raise McdpValueError("incurrect position component type")
                t = max(t, i.type_flag)
        self.type_flag = t

    @property
    def type(self):
        return ComponentType(self.type_flag)

    @property
    def x(self):
        return self.components[0]

    @property
    def y(self):
        return self.components[1]

    @property
    def z(self):
        return self.components[2]

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, val: Union[str, "Position"]):
        if isinstance(val, cls):
            return val
        else:
            return cls(val)
    
    def __eq__(self, other):
        if not isinstance(other, Position):
            return NotImplemented
        return self.components == (<Position>other).components
    
    cdef object _calc0(self, object other, ob_opt opt):
        cdef:
            type cls = type(self)
            tuple comp
            object tmp
        if isinstance(other, (int, float)):
            comp = PyTuple_New(3)
            for i in range(3):
                tmp = opt(self.components[i], other)
                Py_INCREF(tmp)
                PyTuple_SET_ITEM(comp, i, tmp)
            return cls(comp)
        elif isinstance(other, Position):
            comp = PyTuple_New(3)
            for i in range(3):
                tmp = opt(self.components[i], (<Position>other).components[i])
                Py_INCREF(tmp)
                PyTuple_SET_ITEM(comp, i, tmp)
            return cls(comp)
        return NotImplemented
    
    cdef object _calc1(self, object other, ob_opt opt):
        cdef:
            type cls = type(self)
            Position o
            Component x = self.components[0]
            Component y = self.components[1]
            Component z = self.components[2]

        if isinstance(other, Position):
            o = <Position>other
            scale_x = o.components[0]
            scale_y = o.components[1]
            scale_z = o.components[2]
        elif isinstance(other, (int, float)):
            scale_x = scale_y = scale_z = other
        else:
            try:
                scale_x, scale_y, scale_z = other
            except Exception:
                return NotImplemented
                
        cdef tuple c = PyTuple_New(3)
        tmp = opt(x, scale_x)
        Py_INCREF(tmp)
        PyTuple_SET_ITEM(c, 0, tmp)
        tmp = opt(y, scale_y)
        Py_INCREF(tmp)
        PyTuple_SET_ITEM(c, 1, tmp)
        tmp = opt(z, scale_z)
        Py_INCREF(tmp)
        PyTuple_SET_ITEM(c, 2, tmp)
        return cls(c)
    
    def __add__(self, other):
        return self._calc0(other, PyNumber_Add)
    
    def __radd__(self, other):
        return self._calc0(other, PyNumber_Add)

    def __sub__(self, other):
        return self._calc0(other, PyNumber_Subtract)
    
    def __rsub__(self, other):
        return self._calc0(other, ob_rsub)
    
    def __mul__(self, other):
        return self._calc1(other, PyNumber_Multiply)
    
    def __rmul__(self, other):
        return self._calc1(other, PyNumber_Multiply)

    def __truediv__(self, other):
        return (<Position>self)._calc1(other, PyNumber_TrueDivide)

    def __rtruediv__(self, other):
        return (<Position>self)._calc1(other, ob_rdiv)
    
    def __pos__(self):
        return self
    
    def __neg__(self):
        cdef:
            type cls = type(self)
            tuple c = PyTuple_New(3)
        for i in range(3):
            tmp = -self.components[i]
            Py_INCREF(tmp)
            PyTuple_SET_ITEM(c, i, tmp)
        return cls(c, type=self.type_flag)

    def __abs__(self):
        cdef:
            type cls = type(self)
            tuple c = PyTuple_New(3)
        for i in range(3):
            tmp = abs(self.components[i])
            Py_INCREF(tmp)
            PyTuple_SET_ITEM(c, i, tmp)
        return cls(c, type=self.type_flag)
    
    def __iter__(self):
        return iter(self.components)
    
    def __repr__(self):
        return "Position(%s)" % self
    
    def __str__(self):
        return "%s %s %s" % self.components


cdef object DpPosition_New(float x, float y, float z, MCPos_TypeFlag flag):
    return Position(x=x, y=y, z=z, type=flag)

cdef object DpPosition_FromObject(object obj, MCPos_TypeFlag flag):
    return Position(obj, type=flag)

cdef object DpPosition_FromString(const char* string):
    return Position(string.decode())

cdef object DpPosition_GetComponent(object pos, Py_ssize_t i):
    return (<Position?>pos).components[i]

cdef object DpPosition_GetX(object pos):
    return DpPosition_GetComponent(pos, 0)

cdef object DpPosition_GetY(object pos):
    return DpPosition_GetComponent(pos, 1)

cdef object DpPosition_GetZ(object pos):
    return DpPosition_GetComponent(pos, 2)

cdef float DpPosComponent_GetOffset(object comp) except? -1.0:
    return (<Component?>comp).offset

cdef MCPos_TypeFlag DpPosComponent_GetFlag(object comp) except NANTYPE:
    return (<Component?>comp).type_flag