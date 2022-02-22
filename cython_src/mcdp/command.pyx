cimport cython
from libc.stdio cimport sprintf
from libc.stdlib cimport malloc, free
from libc.string cimport strlen, strcat

from .context import insert, comment


cdef class PosComponent(McdpVar):
    cdef readonly:
        str value
        str type

    def __init__(self, str value not None, str type = None):
        self.value = value
        if value[0] == '^':
            int(value[1:])
            self.type = "local"
        elif value[0] == '~':
            int(value[1:])
            self.type = "relative"
        else:
            int(value)
            self.type = "absolute"
        if type and type != self.type:
            raise McdpValueError("unsuit position value.")
    
    def __repr__(self):
        return "PosComponent(%s)" % self.value

    def __str__(self):
        return self.value


cdef inline void _set_pos(list posXYZ, const int index, value, str typecheck) except *:
    cdef PosComponent c_pos
    if not isinstance(value, PosComponent):
        c_pos = PosComponent(value)
    else:
        c_pos = value
    if (c_pos.type == "local") ^ (typecheck == "local"):
        raise McdpTypeError("Invalid position.")
    posXYZ[index] = c_pos


cdef class Position(McdpVar):
    cdef list _posXYZ
    cdef readonly:
        str type
    
    def __init__(self, str pos not None):
        cdef list l = pos.split()
        if len(l) != 3:
            raise McdpValueError("Incorrect position length.")
        
        cdef:
            int tid = 0
            int i
            PosComponent c_pos
        for i in range(3):
            c_pos = PosComponent(l[i])
            if c_pos.type == "absolute":
                if tid == 3:
                    raise McdpTypeError("Invalid position.")
                tid = 1
            elif c_pos.type == "relative":
                if tid == 3:
                    raise McdpTypeError("Invalid position.")
                tid = 2
            else:
                if tid < 3 and tid != 0:
                    raise McdpTypeError("Invalid position.")
                tid = 3
            l[i] = c_pos

        if tid == 1:
            self.type = "absolute"
        elif tid == 2:
            self.type = "relative"
        elif tid == 3:
            self.type = "local"
        self._posXYZ = l
    
    cpdef void teleport(self, slt) except *:
        cdef Selector s = selector(slt)
        insert("tp %s %s" % (self, slt))
    
    @property
    def x(self):
        return self._posXYZ[0]
    
    @x.setter
    def x(self, value):
        _set_pos(self._posXYZ, 0, value, self.type)
    
    @property
    def y(self):
        return self._posXYZ[1]
    
    @y.setter
    def y(self, value):
        _set_pos(self._posXYZ, 1, value, self.type)
    
    @property
    def z(self):
        return self._posXYZ[2]
    
    @z.setter
    def z(self, value):
        _set_pos(self._posXYZ, 1, value, self.type)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, val: Union[str, "Position"]):
        if isinstance(val, cls):
            return val
        else:
            return cls(val)
    
    def __repr__(self) -> str:
        return "Position(%s,%s,%s)" % tuple(self._posXYZ)

    def __str__(self) -> str:
        return "%s %s %s" % tuple(self._posXYZ)


cdef class MultiDictItem(object):
    cdef int _iter_flag
    cdef object __weakref__
    cdef readonly:
        key
        value
    
    def __init__(self, key, value):
        self.key = key
        if isinstance(value, dict) and not isinstance(value, MultiDict):
            value = MultiDict(**(<dict>value))
        self.value = value
        self._iter_flag = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self._iter_flag == 0:
            self._iter_flag += 1
            return self.key
        elif self._iter_flag == 1:
            self._iter_flag += 1
            return self.value
        else:
            self._iter_flag = 0
            raise StopIteration(0)
    
    def __getitem__(self, key):
        return (self.key, self.value)[key]
    
    def __setitem__(self, int key, value):
        if key == 0:
            self.key = value
        elif key == 1:
            self.value = value
        else:
            raise McdpIndexError("item index out of range")
    
    def __repr__(self):
        return "MultiDictItem(%s, %s)" % (self.key, self.value)

    def __str__(self):
        return "%s=%s" % (self.key, self.value)


cdef class MultiDict(dict):
    cdef object __weakref__
    
    def __init__(self, _iter = None, **kwds):
        super().__init__(**kwds)
        if isinstance(_iter, dict):
            for k, v in (<dict>_iter).items():
                self.add(k, v)
        else:
            if not _iter:
                return
            for i in _iter:
                if len(i) == 2:
                    self.add(i[0], i[1])
                else:
                    raise McdpTypeError("Invalid iter.")
    
    cpdef void add(self, key, value) except *:
        cdef:
            dict d_self = self
            set raw
            _raw
        if not key in d_self:
            self[key] = value if isinstance(value, set) else {value}
        _raw = d_self[key]
        if not isinstance(_raw, set):
            raw = {_raw}
        else:
            raw = <set>_raw
        if isinstance(value, set):
            raw.update(<set>value)
        else:
            raw.add(value)
        self[key] = raw
    
    cdef list _values(self):
        cdef list collections = []
        for v in (<dict>self).values():
            if isinstance(v, set) and v:
                collections.update(v)
            else:
                collections.append(v)
    
    def values(self):
        for v in (<dict>self).values():
            if isinstance(v, set) and v:
                for i in <set>v:
                    yield i
            else:
                yield v
    
    cdef list _items(self):
        cdef list collections = []
        for k, v in (<dict>self).items():
            if isinstance(v, set) and v:
                for i in <set>v:
                    collections.append(MultiDictItem(k, i))
            else:
                collections.append(MultiDictItem(k, v))
        return collections
    
    def items(self):
        for k, v in (<dict>self).items():
            if isinstance(v, set) and v:
                for i in <set>v:
                    yield MultiDictItem(k, i)
            else:
                yield MultiDictItem(k, v)
        
    def __repr__(self):
        cdef:
            str tmp
            list l_kv = []
        for i in self.items():
            l_kv.append(str(i))
        tmp = ','.join(l_kv)
        return "{%s}" % tmp


cdef class Selector(McdpVar):
    __accessible__ = {"name": 1, "args": 1}

    cdef readonly:
        str name
        MultiDict args
    
    def __init__(self, str name not None, _iterator = None, **kwds):
        cdef:
            str tmp = name[:2]
            list l_args
            list kv
            str k, v
        if not tmp in ["@p", "@a", "@r", "@e", "@s"]:
            raise McdpValueError("Invalid selector.")
        self.name = tmp
        self.args = MultiDict(_iterator, **kwds)
        with cython.nonecheck(False):
            if len(name) > 2:
                l_args = name[3:-1].split(',')
                for tmp in l_args:
                    kv = tmp.split('=')
                    k, v = kv
                    self.args.add(k.strip(), v.strip())
    
    cdef void _add_tag(self, const char* tag) except *:
        cdef:
            bytes b_self = (<str>str(self)).encode()
            Py_ssize_t p_len = len(b_self) + strlen(tag) + 10
            char* buffer = <char*>malloc(p_len * sizeof(char))
        if buffer == NULL:
            raise MemoryError
        sprintf(buffer, "tag %s add %s", <char*>b_self, tag)
        dp_insert(buffer)
        free(buffer)

    def add_tag(self, str tag not None):
        insert(f"tag {self} add {tag}")
    
    def __str__(self):
        cdef:
            str buffer
            list args
        if not self.args:
            return self.name
        else:
            args = self.args._items()
            for i in range(len(args)):
                args[i] = str(args[i])
            buffer = ','.join(args)
            return "%s[%s]" % (self.name, buffer)


cpdef Selector selector(t_slt):
    if isinstance(t_slt, Selector):
        return <Selector>t_slt
    elif hasattr(type(t_slt), "__selector__"):
        return t_slt.__selector__()
    else:
        raise McdpTypeError("'%s' object is not a selector" % type(t_slt))


cdef class NBTPath(McdpVar):
    cdef readonly tuple path

    def __init__(self, *args):
        cdef:
            list l_path = []
            str i
        if not args:
            raise McdpValueError("Invalid NBT path.")
        for i in args:
            if '.' in i:
                l_path.extend(i.split('.'))
            else:
                l_path.append(i)
        self.path = tuple(l_path)
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, val: Union[str, "NBTPath"]):
        if isinstance(val, cls):
            return val
        else:
            return cls(val)
    
    def __repr__(self) -> str:
        return "NBTPath(%s)" % self

    def __str__(self) -> str:
        return '.'.join(self.path)


cdef int instruction_counter = 0


cdef class InstructionEnvironment(Context):
    cdef Instruction instruction

    def __init__(self, instruction: Instruction) -> None:
        self.instruction = instruction
        super().__init__("instruction" + hex(instruction_counter), root_path=get_extra_path())
    
    cpdef void init(self):
        super().init()
        dp_comment("File ")
        dp_newline(2)


cdef class Instruction(McdpVar):
    ...