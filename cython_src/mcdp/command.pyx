cimport cython
from libc.stdio cimport sprintf
from libc.stdlib cimport malloc, free
from libc.string cimport strlen, strcat

from .context import insert, comment


cdef class PosComponent(McdpVar):
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
    def __init__(self, str pos not None):
        cdef list l = pos.split()
        if len(l) != 3:
            raise ValueError("Incorrect position length.")
        
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
                    raise TypeError("Invalid iter.")
    
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

    def __init__(self, str name not None, _iterator = None, **kwds):
        cdef:
            str tmp = name[:2]
            list l_args
            list kv
            str k, v
        if not tmp in ["@p", "@a", "@r", "@e", "@s"]:
            raise ValueError("Invalid selector.")
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
    
    cdef void _remove_tag(self, const char* tag) except *:
        cdef:
            bytes b_self = (<str>str(self)).encode()
            Py_ssize_t p_len = len(b_self) + strlen(tag) + 13
            char* buffer = <char*>malloc(p_len * sizeof(char))
        if buffer == NULL:
            raise MemoryError
        sprintf(buffer, "tag %s remove %s", <char*>b_self, tag)
        dp_insert(buffer)
        free(buffer)

    def add_tag(self, str tag not None):
        insert(f"tag {self} add {tag}")
    
    def remove_tag(self, tag: str) -> None:
        insert(f"tag {self} remove {tag}")
    
    cpdef void remove(self) except *:
        insert(f"kill {self}")

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, val: Any):
        if isinstance(val, cls):
            return val
        else:
            return val.__selector__()

    def __mcstr__(self) -> MCString:
        return MCString(selector=str(self))

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


cdef Selector _selector(t_slt):
    if isinstance(t_slt, Selector):
        return <Selector>t_slt
    elif hasattr(type(t_slt), "__selector__"):
        return t_slt.__selector__()
    else:
        raise McdpTypeError("'%s' object is not a selector" % type(t_slt))


def selector(t_slt not None, _iter = None, **kwds):
    if isinstance(t_slt, str):
        return Selector(t_slt, _iter, **kwds)
    else:
        return _selector(t_slt)


cdef class NBTPath(McdpVar):
    cdef readonly tuple path

    def __init__(self, *args):
        cdef:
            list l_path = []
            str i
        if not args:
            raise ValueError("Invalid NBT path.")
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


cdef class InstructionContext(Context):
    cdef readonly Instruction instruction

    def __init__(self, instruction: Instruction) -> None:
        self.instruction = instruction
        super().__init__("instruction" + hex(instruction_counter), root_path=get_extra_path())
    
    cpdef void mkhead(self):
        Context.mkhead(self)

        cdef:
            Context cxt
            bytes tmp
            const char* src_name
        if len(_envs) > 2:
            cxt = _envs[-2]
            tmp = cxt.name.encode()
            src_name = <char*>tmp
        else:
            src_name = "<__init__>"
        dp_commentline("Extra file from context '%s'", src_name)
        dp_newline(2)


cdef class Instruction(McdpVar):
    """
    Base class of all instructions of 'execute' command.
    """
    
    def __bool__(self) -> NoReturn:
        raise NotImplementedError("Maybe you want to use 'if'? Use 'with' instead.")
    
    cpdef Execute inline(self):
        cdef Execute _exec = Execute(self)
        return _exec.inline()
    
    cdef InstructionContext enter(self):
        cdef InstructionContext cxt = InstructionContext(self)
        cxt.enter()
        return cxt
    
    cdef void exit(self) except *:
        _envs.pop()
    
    def __enter__(self):
        return self.enter()
    
    def __exit__(self, *args):
        self.exit()
    
    def __str__(self) -> str:
        """This part should be overridden by the subclass"""
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self})"


cdef class AlignInstruction(Instruction):
    cdef readonly:
        str axes

    def __init__(self, str axes not None) -> None:
        cdef int x, y, z
        x = axes.count('x')
        y = axes.count('y')
        z = axes.count('z')
        if x > 1 or y > 1 or z > 1 or x + y + z != len(axes):
            raise ValueError(
                    "Axes should be any non-repeating combination of the characters 'x', 'y', and 'z'.")
        self.axes = axes

    def __str__(self) -> str:
        return f"align {self.axes}"


cdef class AnchoredInstruction(Instruction):
    cdef readonly:
        str anchor

    def __init__(self, str anchor not None) -> None:
        if not anchor in ["eyes", "feet"]:
            raise ValueError("anchor must be 'eye' or 'feet'.")
        self.anchor = anchor

    def __str__(self) -> str:
        return f"anchored {self.anchor}"


cdef class AsInstruction(Instruction):
    cdef readonly:
        Selector targets

    def __init__(self, targets: Union[Selector, str]) -> None:
        if isinstance(targets, Selector):
            self.targets = <Selector>targets
        else:
            self.targets = selector(targets)

    def __str__(self) -> str:
        return f"as {self.targets}"


cdef class AtInstruction(Instruction):
    cdef readonly:
        Selector targets

    def __init__(self, targets) -> None:
        if isinstance(targets, Selector):
            self.targets = <Selector>targets
        else:
            self.targets = selector(targets)

    def __str__(self) -> str:
        return f"at {self.targets}"


cdef class FacingInstruction(Instruction):
    cdef readonly:
        bint entity
        Position pos
        Selector targets
        str anchor

    def __init__(
            self,
            pos_or_targets: Union[str, Position, Selector],
            str anchor = None,
            *,
            bint entity = False
    ) -> None:
        if entity:
            if not anchor in ["eyes", "feet"]:
                raise ValueError("Miss a argument 'anchor'.'")
            if isinstance(pos_or_targets, str):
                self.targets = Selector(pos_or_targets)
            else:
                self.targets = _selector(pos_or_targets)
            self.anchor = anchor
            self.entity = True
        else:
            if anchor:
                raise ValueError("Invalid argument 'anchor'.")
            if isinstance(pos_or_targets, str):
                self.pos = Position(pos_or_targets)
            else:
                self.pos = pos_or_targets
            self.entity = entity

    def __str__(self) -> str:
        if self.entity:
            return f"facing entity {self.targets} {self.anchor}"
        else:
            return f"facing {self.pos}"


cdef class InInstruction(Instruction):
    cdef readonly:
        str dimension

    def __init__(self, str dimension not None) -> None:
        self.dimension = dimension

    def __str__(self) -> str:
        return f"in {self.dimension}"


cdef class PositionedInstruction(Instruction):
    cdef readonly:
        bint entity
        Position pos
        Selector targets

    def __init__(self, pos_or_targets: Union[str, Position, Selector], *, bint entity = False) -> None:
        self.entity = entity
        if entity:
            if isinstance(pos_or_targets, str):
                self.targets = Selector(pos_or_targets)
            else:
                self.targets = _selector(pos_or_targets)
        else:
            if isinstance(pos_or_targets, Position):
                self.pos = <Position>pos_or_targets
            else:
                self.pos = Position(pos_or_targets)

    def __str__(self) -> str:
        if self.entity:
            return f"positioned as {self.targets}"
        else:
            return f"positioned {self.pos}"


cdef class RotatedInstruction(Instruction):
    cdef readonly:
        bint entity
        (float, float) rot
        Selector targets

    def __init__(self, rot_or_targets: Union[str, Position, Selector], *, bint entity = False) -> None:
        self.entity = entity
        if entity:
            if isinstance(rot_or_targets, str):
                self.targets = Selector(rot_or_targets)
            else:
                self.targets = _selector(rot_or_targets)
        else:
            self.rot = rot_or_targets

    def __str__(self) -> str:
        if self.entity:
            return f"rotated as {self.targets}"
        else:
            return f"rotated {self.rot[0]} {self.rot[1]}"


"""
CONDITION INSTRUCTION PART:
    Include cases used in condition instruction
"""


cdef class Case(McdpVar):
    def __repr__(self):
        return f"{type(self).__name__}({self})"
    
    def __str__(self) -> str:
        """This part should be overridden by the subclass"""
        raise NotImplementedError


cdef class BlockCase(Case):
    cdef readonly:
        Position pos
        str block
    
    def __init__(self, pos not None, str block not None):
        self.block = block
        if isinstance(pos, Position):
            self.pos = <Position>pos
        else:
            self.pos = Position(pos)
    
    def __str__(self) -> str:
        return f"block {self.pos} {self.block}"


cdef class BlocksCase(Case):
    cdef readonly:
        Position start
        Position end
        Position destination
        str scan_mode

    def __init__(
            self,
            start: Union[str, Position],
            end: Union[str, Position],
            destination: Union[str, Position],
            *,
            str scan_mode not None = "all"
    ) -> None:
        if isinstance(start, Position):
            self.start = <Position>start
        else:
            self.start = Position(start)
        if isinstance(end, Position):
            self.end = <Position>end
        else:
            self.end = Position(end)
        if isinstance(destination, Position):
            self.destination = <Position>destination
        else:
            self.destination = Position(destination)
        
        if not scan_mode in ["all", "marked"]:
            raise ValueError("scan mod must be 'all' or 'marked'.")
        self.scan_mode = scan_mode

    def __str__(self) -> str:
        return f"blocks {self.start} {self.end} {self.destination} {self.scan_mode}"


cdef class DataCase(Case):
    cdef readonly:
        str type
        Position pos
        Selector targets
        NBTPath path

    def __init__(
            self,
            str type not None,
            pos_or_targets: Union[Position, str, Selector],
            path: Union[str, NBTPath]
    ) -> None:
        self.type = type
        if isinstance(path, NBTPath):
            self.path = path
        else:
            self.path = NBTPath(path)
        if type == "block":
            if isinstance(pos_or_targets, Position):
                self.pos_or_targets = <Position>pos_or_targets
            else:
                self.pos_or_targets = Position(pos_or_targets)
        else:
            if isinstance(pos_or_targets, str):
                self.targets = Selector(pos_or_targets)
            else:
                self.targets = _selector(pos_or_targets)
    
    def __str__(self) -> str:
        if self.type == "block":
            return f"data block {self.pos} {self.path}"
        else:
            return f"data {self.type} {self.targets} {self.path}"


cdef class EntityCase(Case):
    cdef readonly:
        Selector targets
    
    def __init__(self, targets):
        if isinstance(targets, str):
            self.targets = Selector(targets)
        else:
            self.targets = _selector(targets)
            
    def __str__(self) -> str:
        return f"entity {self.targets}"


cdef class PredicateCase(Case):
    cdef readonly:
        str predicate

    def __init__(self, str predicate not None):
        self.predicate = predicate

    def __str__(self) -> str:
        return f"predicate {self.predicate}"


cdef class ScoreCase(Case):
    cdef readonly:
        Selector target
        str target_obj 
        str ops
        Selector source
        str source_obj
        str range
    
    def __init__(
            self,
            target: Union[str, Selector],
            str target_obj not None,
            str ops not None,
            source_or_range: Union[str, Selector],
            str source_obj = None
    ) -> None:
        if isinstance(target, str):
            self.target = Selector(target)
        else:
            self.target = _selector(target)
        self.target_obj = target_obj

        self.ops = ops
        if ops == "matches":
            if not source_obj is None:
                raise ValueError("Invalid source objective.")
            self.range = source_or_range
        elif ops in ["<", "<=", "=", ">=", ">"]:
            if isinstance(source_or_range, str):
                self.source = Selector(source_or_range)
            else:
                self.source = _selector(source_or_range)
            if source_obj is None:
                raise TypeError(
                    "mcdp.command.ScoreCase.__init__ missing 1 required positional argument: 'source_obj'")
            self.source_obj = source_obj
        else:
            raise ValueError("ops must be '<', '<=', '=', '>=', '>' or 'matches'.")

    def __str__(self) -> str:
        if self.ops == "matches":
            return f"score {self.target} {self.target_obj} " +\
                f"{self.ops} {self.range}"
        else:
            return f"score {self.target} {self.target_obj} " +\
                f"{self.ops} {self.source} {self.source_obj}"


cdef class ConditionInstruction(Instruction):
    cdef readonly:
        bint unless
        Case case
    
    def __init__(self, Case case not None, *, bint unless = False) -> None:
        self.unless = unless
        self.case = case
    
    def __str__(self) -> str:
        if self.unless:
            return f"unless {self.case}"
        else:
            return f"if {self.case}"


cdef dict _case_class = {"block": BlockCase, "blocks": BlocksCase, "data": DataCase}


def case(str type not None, *args, **kwds):
    return _case_class[type](*args, **kwds)


"""
STORE INSTRUCTION PART:
    Include store modes used in store instruction
"""


cdef class StoreMode(McdpVar):
    """Base class of store mode."""

    def __repr__(self):
        return f"{type(self).__name__}({self})"
    
    def __str__(self) -> str:
        """This part should be overridden by the subclass"""
        raise NotImplementedError


cdef class Execute(McdpVar):
    def __init__(self, instruction_or_execobj: Union[Instruction, "Execute"], *instructions: Union[Instruction, "Execute"]) -> None:
        if isinstance(instruction_or_execobj, Instruction):
            self.instructions = [instruction_or_execobj]
        else:
            self.instructions = instruction_or_execobj.instructions
        for i in instructions:
            if isinstance(i, Instruction):
                self.instructions.append(i)
            else:
                self.instructions.extend(i.instructions)
        self.inline_handler = False