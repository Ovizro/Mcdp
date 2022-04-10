cimport cython
from libc.stdio cimport sprintf
from libc.stdlib cimport malloc, free
from libc.string cimport strlen, strcat
from cpython cimport PyObject, PyTuple_New, PyTuple_SET_ITEM, Py_INCREF
from .context import insert, comment


"""
POSITION OBJECT PART:
    Provide position component object, position object which is 
    a static version of dp_pos object and some constants.
"""

POS_LOCAL = Local
POS_RELATIVE = Relative
POS_ABSOLUTE = Absolute


cdef class PosComponent(McdpVar):
    def __init__(self, str value not None, PosType type = Empty):
        self.value = value
        if value[0] == '^':
            int(value[1:])
            self.type = Local
        elif value[0] == '~':
            int(value[1:])
            self.type = Relative
        else:
            int(value)
            self.type = Absolute
        if type and type != self.type:
            raise McdpValueError("unsuit position value.")
    
    def __repr__(self):
        return "PosComponent(%s)" % self.value

    def __str__(self):
        return self.value


cdef inline void _set_pos(list posXYZ, const int index, value, PosType typecheck) except *:
    cdef PosComponent c_pos
    if not isinstance(value, PosComponent):
        c_pos = PosComponent(value)
    else:
        c_pos = value
    if (c_pos.type == Local) ^ (typecheck == Local):
        raise McdpTypeError("Invalid position.")
    posXYZ[index] = c_pos


cdef class Position(McdpVar):
    def __init__(self, str pos not None):
        cdef list l = pos.split()
        if len(l) != 3:
            raise ValueError("Incorrect position length.")
        
        cdef:
            int i
            PosComponent c_pos
        self.type = Empty
        for i in range(3):
            c_pos = PosComponent(l[i])
            if c_pos.type == Absolute:
                if self.type == Local:
                    raise McdpTypeError("Invalid position.")
                self.type = Absolute
            elif c_pos.type == Relative:
                if self.type == Local:
                    raise McdpTypeError("Invalid position.")
                self.type = Relative
            else:
                if self.type <= Local:
                    raise McdpTypeError("Invalid position.")
                self.type = Local
            l[i] = c_pos

        self._posXYZ = l
    
    cpdef void teleport(self, slt) except *:
        cdef Selector s = Selector.validate_argument(slt, "slt")
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
        
    @staticmethod
    cdef Position validate_argument(val, str arg):
        if isinstance(val, Position):
            return <Position>val
        elif isinstance(val, str):
            return Position(<str>val)
        else:
            raise TypeError(f"argument {arg} must be Postion-like, not {type(val)}")
    
    def __repr__(self) -> str:
        return "Position(%s,%s,%s)" % tuple(self._posXYZ)

    def __str__(self) -> str:
        return "%s %s %s" % tuple(self._posXYZ)


"""
SELECTOR PART:
    Provide selector object or a multidict used in selector object.
"""

cdef class MultiDictItem(object):
    cdef size_t _iter_flag
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
    
    def remove_tag(self, str tag not None):
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

    @staticmethod
    cdef Selector validate_argument(val, str arg):
        if isinstance(val, str):
            return Selector(<str>val)
        elif isinstance(val, Selector):
            return <Selector>val
        elif hasattr(type(val), "__selector__"):
            return val.__selector__()
        else:
            raise TypeError(f"argument {arg} must be Selector-like, not {type(val)}")
    
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


def selector(t_slt not None, _iter = None, **kwds):
    if isinstance(t_slt, str):
        return Selector(t_slt, _iter, **kwds)
    elif isinstance(t_slt, Selector):
        return <Selector>t_slt
    elif hasattr(type(t_slt), "__selector__"):
        return t_slt.__selector__()
    else:
        raise McdpTypeError("'%s' object is not a selector" % type(t_slt))


"""
DATA PART:
    Provide NBT path object.
"""

cdef class NBTPath(McdpVar):
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
    
    @staticmethod
    cdef NBTPath validate_argument(val, str arg):
        if isinstance(val, NBTPath):
            return <NBTPath>val
        elif isinstance(val, (tuple, list)):
            return NBTPath(*val)
        elif isinstance(val, str):
            return NBTPath(val)
        else:
            raise TypeError(f"argument {arg} must be NBTPath-like, not {type(val)}")
    
    def __repr__(self) -> str:
        return "NBTPath(%s)" % self

    def __str__(self) -> str:
        return '.'.join(self.path)


"""
TELLING PART:
    Provide telling object to show text on the screen.
"""

cdef class TellingObject(McdpVar):
    def __init__(self, list data = None, *, bint base = False):
        if data is None:
            data = []
        self.data = data
        self.base = base
    
    def __getitem__(self, value: Any):
        if self.base:
            self = self.copy()

        self.data.append(value)
        return self
    
    cpdef TellingObject copy(self):
        return type(self)(self.data.copy())


cdef class Printer(TellingObject):
    def __init__(self, list data = None, *, bint base = False):
        super().__init__(data, base=base)
        self.input = []

    def __lshift__(self, other: Any) -> "Printer":
        if isinstance(other, PrinterEOF):
            other(self)
        else:
            if not isinstance(other, MCString):
                other = fsmcstr(other)

            self.input.append(<MCString>other)
        return self


cdef class PrinterEOF(TellingObject):
    def __call__(self, Printer stream) -> None:
        if len(stream.input) < 1:
            raise McdpCommandError(
                    "tellraw", ValueError(
                            "No string griven."
                    ))
        elif len(stream.input) == 1:
            input = stream.input[0]
        else:
            input = "[{0}]".format(','.join((str(i) for i in stream.input)))

        if not stream.data:
            self.__apply_printer__("tellraw {targets} {input}", input=input)
        elif len(stream.data) == 1:
            self.__apply_printer__("title {targets} {subcmd} {input}", input=input, subcmd=stream.data[0])
        else:
            raise McdpCommandError(
                "tellraw/title", ValueError(
                        "Invalid printer data."
                ))

        stream.input.clear()

    def __apply_printer__(self, str cmd not None, **kw) -> None:
        if len(self.data) == 0:
            targets = "@a"
        elif len(self.data) == 1:
            targets = self.data[0]
        else:
            raise McdpCommandError(
                    "tellraw/title", ValueError(
                            "Invalid EOF data."
                    ))
        insert(cmd.format(targets=targets, **kw))


cout = Printer(base=True)
endl = PrinterEOF(base=True)


"""
INSTRUCTION PART:
    Include all instruction used in 'execute' command.
"""

cdef int instruction_counter = 0


cdef class InstructionEnvironment(Context):
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
    
    def inline(self):
        cdef Execute _exec = Execute(self)
        return _exec.inline()
    
    cdef InstructionEnvironment enter(self):
        cdef InstructionEnvironment cxt = InstructionEnvironment(self)
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
    def __init__(self, str axes not None) -> None:
        cdef Py_ssize_t x, y, z
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
    def __init__(self, str anchor not None) -> None:
        if not anchor in ["eyes", "feet"]:
            raise ValueError("anchor must be 'eye' or 'feet'.")
        self.anchor = anchor

    def __str__(self) -> str:
        return f"anchored {self.anchor}"


cdef class AsInstruction(Instruction):
    def __init__(self, targets: Union[Selector, str]) -> None:
        if isinstance(targets, Selector):
            self.targets = <Selector>targets
        else:
            self.targets = selector(targets)

    def __str__(self) -> str:
        return f"as {self.targets}"


cdef class AtInstruction(Instruction):
    def __init__(self, targets) -> None:
        if isinstance(targets, Selector):
            self.targets = <Selector>targets
        else:
            self.targets = selector(targets)

    def __str__(self) -> str:
        return f"at {self.targets}"


cdef class FacingInstruction(Instruction):
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
            self.targets = Selector.validate_argument(pos_or_targets, "targets")
            self.anchor = anchor
            self.entity = True
        else:
            if anchor:
                raise ValueError("Invalid argument 'anchor'.")
            self.pos = Position.validate_argument(pos_or_targets, "pos")
            self.entity = entity

    def __str__(self) -> str:
        if self.entity:
            return f"facing entity {self.targets} {self.anchor}"
        else:
            return f"facing {self.pos}"


cdef class InInstruction(Instruction):
    def __init__(self, str dimension not None) -> None:
        self.dimension = dimension

    def __str__(self) -> str:
        return f"in {self.dimension}"


cdef class PositionedInstruction(Instruction):
    def __init__(self, pos_or_targets: Union[str, Position, Selector], *, bint entity = False) -> None:
        self.entity = entity
        if entity:
            self.targets = Selector.validate_argument(pos_or_targets, "targets")
        else:
            self.pos = Position.validate_argument(pos_or_targets, "pos")

    def __str__(self) -> str:
        if self.entity:
            return f"positioned as {self.targets}"
        else:
            return f"positioned {self.pos}"


cdef class RotatedInstruction(Instruction):
    def __init__(self, rot_or_targets: Union[str, Position, Selector], *, bint entity = False) -> None:
        self.entity = entity
        if entity:
            self.targets = Selector.validate_argument(rot_or_targets, "targets")
        else:
            self.rot = rot_or_targets

    def __str__(self) -> str:
        if self.entity:
            return f"rotated as {self.targets}"
        else:
            return f"rotated {self.rot[0]} {self.rot[1]}"


"""
CONDITION INSTRUCTION PART:
    Include cases used in condition instruction.
"""


cdef class Case(McdpVar):
    def __repr__(self):
        return f"{type(self).__name__}({self})"
    
    def __str__(self) -> str:
        """This part should be overridden by the subclass"""
        raise NotImplementedError


cdef class BlockCase(Case):
    def __init__(self, pos not None, str block not None):
        self.block = block
        if isinstance(pos, Position):
            self.pos = <Position>pos
        else:
            self.pos = Position(pos)
    
    def __str__(self) -> str:
        return f"block {self.pos} {self.block}"


cdef class BlocksCase(Case):
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
            self.pos = Position.validate_argument(pos_or_targets, "pos")
        else:
            self.targets = Selector.validate_argument(pos_or_targets, "targets")
    
    def __str__(self) -> str:
        if self.type == "block":
            return f"data block {self.pos} {self.path}"
        else:
            return f"data {self.type} {self.targets} {self.path}"


cdef class EntityCase(Case):
    def __init__(self, targets):
        self.targets = Selector.validate_argument(targets, "targets")
            
    def __str__(self) -> str:
        return f"entity {self.targets}"


cdef class PredicateCase(Case):
    def __init__(self, str predicate not None):
        self.predicate = predicate

    def __str__(self) -> str:
        return f"predicate {self.predicate}"


cdef class ScoreCase(Case):
    def __init__(
            self,
            target: Union[str, Selector],
            str target_obj not None,
            str ops not None,
            source_or_range: Union[str, Selector],
            str source_obj = None
    ) -> None:
        self.target = Selector.validate_argument(target, "target")
        self.target_obj = target_obj

        self.ops = ops
        if ops == "matches":
            if not source_obj is None:
                raise ValueError("Invalid source objective.")
            self.range = source_or_range
        elif ops in ["<", "<=", "=", ">=", ">"]:
            self.source = Selector.validate_argument(source_or_range, "source")
            if source_obj is None:
                raise TypeError(
                    "mcdp.command.ScoreCase.__init__ missing 1 required positional argument: 'source_obj'")
            self.source_obj = source_obj
        else:
            raise ValueError("ops must be '<', '<=', '=', '>=', '>' or 'matches'.")

    def __str__(self) -> str:
        if self.ops == "matches":
            return f"score {self.target} {self.target_obj} " +\
                f"matches {self.range}"
        else:
            return f"score {self.target} {self.target_obj} " +\
                f"{self.ops} {self.source} {self.source_obj}"


cdef class ConditionInstruction(Instruction):
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
    Include store modes used in store instruction.
"""


cdef class StoreMode(McdpVar):
    """Base class of store mode."""

    def __repr__(self):
        return f"{type(self).__name__}({self})"
    
    def __str__(self) -> str:
        """This part should be overridden by the subclass"""
        raise NotImplementedError


cdef class BlockStore(StoreMode):
    def __init__(
            self,
            target_pos: Union[str, Position],
            path: Union[str, NBTPath],
            str type not None,
            float scale
    ) -> None:
        self.target_pos = Position.validate_argument(target_pos, "target_pos")
        self.path = NBTPath.validate_argument(path, "path")
        if not type in ["byte", "short", "int", "long", "float", "double"]:
            raise ValueError("type must be 'byte', 'short', 'int', 'long', 'float' or 'double'.")
        self.type = type
        self.scale = scale

    def __str__(self) -> str:
        return f"block {self.target_pos} {self.path} {self.type} {self.scale}"


cdef class BossbarStore(StoreMode):
    def __init__(self, str id not None, str value not None):
        if not value in ["value", "max"]:
            raise ValueError("value must be 'value' or 'max'.")
        self.id = id
        self.value = value
    
    def __str__(self) -> str:
        return f"bossbar {self.id} {self.value}"


cdef class EntityStore(StoreMode):
    def __init__(
            self,
            target: Union[str, Selector],
            path: Union[str, NBTPath],
            str type not None,
            float scale
    ):
        self.target = Selector.validate_argument(target, "target")
        self.path = NBTPath.validate_argument(path, "path")
        if not type in ["byte", "short", "int", "long", "float", "double"]:
            raise ValueError("type must be 'byte', 'short', 'int', 'long', 'float' or 'double'.")
        self.type = type
        self.scale = scale

    def __str__(self) -> str:
        return f"entity {self.target} {self.path} {self.type} {self.scale}"


cdef class ScoreStore(StoreMode):
    def __init__(self, targets: Union[str, Selector], str objective not None) -> None:
        self.target = Selector.validate_argument(targets, "targets")
        self.objective = objective

    def __str__(self) -> str:
        return f"score {self.targets} {self.objective}"


cdef class StorageStore(StoreMode):
    def __init__(
            self,
            str target not None,
            path: Union[str, NBTPath],
            str type not None,
            float scale
    ) -> None:
        self.target = target
        self.path = NBTPath.validate_argument(path, "path")
        if not type in ["byte", "short", "int", "long", "float", "double"]:
            raise ValueError("type must be 'byte', 'short', 'int', 'long', 'float' or 'double'.")
        self.type = type
        self.scale = scale

    def __str__(self) -> str:
        return f"storage {self.target} {self.path} {self.type} {self.scale}"


cdef class StoreInstruction(Instruction):
    def __init__(self, mode: StoreMode, *, store_success: bool = False) -> None:
        self.mode = mode
        self.store_success = store_success

    def __str__(self) -> str:
        if self.store_success:
            return f"store success {self.mode}"
        else:
            return f"store result {self.mode}"


cdef dict _store_register = {"block": BlockStore, "bossbar": BossbarStore, "entity": EntityStore, "score": ScoreStore, "storage": StorageStore}


cdef class ExecuteEnvironment(Context):
    def __init__(self, Execute exec, *, bint inline = False) -> None:
        self.exec = exec
        self.inline = inline
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
    
    def inline(self):
        self.inline_handler = True
        return self
    
    def __call__(self, command = None) -> None:
        exc = "execute " + " ".join([str(i) for i in self.instructions])
        if not command is None:
            insert(f"{exc} run {command}")

        elif not isinstance(self.instructions[-1], ConditionInstruction):
            raise McdpCommandError(
                    "execute", TypeError(
                            "Final instruction should be a conditon instruction."
                    ))
        else:
            insert(exc)
    
    cpdef str command_prefix(self):
        return "execute {0} run ".format(" ".join([str(i) for i in self.instructions]))
    
    cdef ExecuteEnvironment enter(self):
        cdef ExecuteEnvironment hdl = ExecuteEnvironment(self, inline=self.inline_handler)
        if self.inline_handler:
            Context.add_hdl(hdl)
        else:
            hdl.enter()
        return hdl
    
    cdef void exit(self) except *:
        if self.inline_handler:
            Context.pop_hdl()
        else:
            _envs.pop()
    
    def __enter__(self):
        return self.enter()
    
    def __exit__(self, exc_type, exc_ins, traceback) -> None:
        self.exit()
    
    def __str__(self) -> str:
        return f"Execute{tuple(self.instructions)}"

    __repr__ = __str__

cpdef Execute inline(AnyExecutor instruction):
    cdef Execute _exec
    if AnyExecutor is Instruction:
        _exec = Execute(instruction)
    else:
        _exec = instruction
    _exec.inline_handler = True
    return _exec


cdef extern from *:
    ctypedef class __builtins__.BaseException [object PyBaseExceptionObject]:
        cdef:
            dict __dict__ "dict"
            list args
            PyObject* note
            PyObject* traceback
            PyObject* context
            PyObject* cause
            char suppress_context


cdef class McdpCommandError(McdpError):
    def __init__(self, str command not None, *args: BaseException) -> None:
        self.command = command

        cdef:
            str msg
            BaseException err
            size_t i = 1
            tuple lm= PyTuple_New(len(args) + 1)
        if not args:
            msg = f"Fail to handle command {command}."
        else:
            tmp = f"During handle command {command}, {len(args)} error(s) occur:"
            Py_INCREF(tmp)
            PyTuple_SET_ITEM(lm, 0, tmp)

            for err in args:
                tmp = f"    {type(err).__qualname__}: {' '.join(err.args)}"
                Py_INCREF(tmp)
                PyTuple_SET_ITEM(lm, i, tmp)
                i += 1

            msg = '\n'.join(lm)
        super().__init__(msg)