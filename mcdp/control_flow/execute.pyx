from cpython cimport PyObject, PyErr_Format, PyTuple_New, PyTuple_SET_ITEM, Py_INCREF, PyMem_Free

from ..version cimport Version
from ..context cimport Context, DpContext_Get, DpContext_Insert
from ..cpython_interface cimport Py_TYPE_GetName, PyUnicode_FromFormat, PyOS_double_to_string

from .. import get_pack


cdef inline Version get_support_version():
    return get_pack().pack_info.support_version


cdef class BaseInstruction(McdpObject):
    """
    Base class of all instructions of 'execute' command.
    """

    def __bool__(self):
        raise NotImplementedError("unknown result '__bool__'\n\tMaybe you want to use 'if'? Use 'with' instead.")
    
    def __str__(self):
        """This part should be overridden by the subclass"""
        raise NotImplementedError
    
    def __repr__(self):
        cdef const char* name = Py_TYPE_GetName(self)
        return PyUnicode_FromFormat("%s(%S)", name, <PyObject*>self)


cdef class AlignInstruction(BaseInstruction):
    def __init__(self, str axes not None) -> None:
        cdef Py_ssize_t x, y, z
        x = axes.count('x')
        y = axes.count('y')
        z = axes.count('z')
        if x > 1 or y > 1 or z > 1 or x + y + z != len(axes):
            raise ValueError(
                    "axes should be any non-repeating combination of the characters 'x', 'y', and 'z'")
        self.axes = axes

    def __str__(self) -> str:
        return PyUnicode_FromFormat("align %U", <void*>self.axes)


cdef class AnchoredInstruction(BaseInstruction):
    def __init__(self, str anchor not None) -> None:
        if not anchor in ["eyes", "feet"]:
            raise ValueError("anchor must be 'eye' or 'feet'")
        self.anchor = anchor

    def __str__(self) -> str:
        return PyUnicode_FromFormat("anchored %U", <void*>self.anchor)


cdef class AsInstruction(BaseInstruction):
    def __init__(self, targets: Union[Selector, str]) -> None:
        self.targets = <Selector>DpSelector_FromObject(targets)

    def __str__(self) -> str:
        return PyUnicode_FromFormat("as %S", <void*>self.targets)


cdef class AtInstruction(BaseInstruction):
    def __init__(self, targets: Union[Selector, str]) -> None:
        self.targets = <Selector>DpSelector_FromObject(targets)

    def __str__(self) -> str:
        return PyUnicode_FromFormat("at %S", <void*>self.targets)


cdef class FacingInstruction(BaseInstruction):
    def __init__(
            self,
            pos_or_targets not None,
            str anchor = None,
            *,
            bint entity = False
    ) -> None:
        if entity:
            if not anchor in ["eyes", "feet"]:
                raise ValueError("miss a argument 'anchor'")
            self.targets = <Selector>DpSelector_FromObject(pos_or_targets)
            self.anchor = anchor
            self.entity = True
        else:
            if anchor:
                raise ValueError("invalid argument 'anchor'.")
            self.pos = <Position>DpPosition_FromObject(pos_or_targets)
            self.entity = entity

    def __str__(self) -> str:
        if self.entity:
            return PyUnicode_FromFormat("facing entity %S %U", <void*>self.targets, <void*>self.anchor)
        else:
            return PyUnicode_FromFormat("facing %S", <void*>self.pos)


cdef class InInstruction(BaseInstruction):
    def __init__(self, str dimension not None) -> None:
        self.dimension = dimension

    def __str__(self) -> str:
        return PyUnicode_FromFormat("in %U", <void*>self.dimension)


cdef class PositionedInstruction(BaseInstruction):
    def __init__(self, pos_or_targets: Union[str, Position, Selector], *, bint entity = False) -> None:
        self.entity = entity
        if entity:
            self.targets = <Selector>DpSelector_FromObject(pos_or_targets)
        else:
            self.pos = <Position>DpPosition_FromObject(pos_or_targets)

    def __str__(self) -> str:
        if self.entity:
            return PyUnicode_FromFormat("positioned as %S", <void*>self.targets)
        else:
            return PyUnicode_FromFormat("positioned %S", <void*>self.pos)


cdef class RotatedInstruction(BaseInstruction):
    def __init__(self, rot_or_targets not None, *, bint entity = False) -> None:
        self.entity = entity
        if entity:
            self.targets = <Selector>DpSelector_FromObject(rot_or_targets)
        else:
            self.rot = rot_or_targets

    def __str__(self) -> str:
        cdef:
            char* buff0
            char* buff1
        if self.entity:
            return PyUnicode_FromFormat("rotated as %S", <void*>self.targets)
        else:
            buff0 = PyOS_double_to_string(self.rot[0], ord("f"), 0, 0, NULL)
            buff1 = PyOS_double_to_string(self.rot[1], ord("f"), 0, 0, NULL)
            try:
                return PyUnicode_FromFormat("rotated %s %s", buff0, buff1)
            finally:
                PyMem_Free(buff0)
                PyMem_Free(buff1)


cdef class Case(McdpObject):
    """Base class for case instruction"""

    def __str__(self) -> str:
        """This part should be overridden by the subclass"""
        raise NotImplementedError

    def __repr__(self):
        cdef const char* name = Py_TYPE_GetName(self)
        return PyUnicode_FromFormat("%s(%S)", name, <PyObject*>self)


cdef class BlockCase(Case):
    def __init__(self, pos not None, str block not None):
        self.block = block
        self.pos = DpPosition_FromObject(pos)

    def __str__(self) -> str:
        return PyUnicode_FromFormat("block %S %U", <void*>self.pos, <void*>self.block)


cdef class BlocksCase(Case):
    def __init__(
            self,
            start not None,
            end not None,
            destination not None,
            *,
            str scan_mode not None = "all"
    ) -> None:
        self.start = <Position>DpPosition_FromObject(start)
        self.end = <Position>DpPosition_FromObject(end)
        self.destination = <Position>DpPosition_FromObject(destination)
        if not scan_mode in ["all", "marked"]:
            PyErr_Format(ValueError, "scan mod must be 'all' or 'marked', not '%U'", <void*>scan_mode)
        self.scan_mode = scan_mode

    def __str__(self) -> str:
        return PyUnicode_FromFormat(
            "blocks %S %S %S %U",
            <void*>self.start, <void*>self.end, <void*>self.destination, <void*>self.scan_mode
        )


cdef class DataCase(Case):
    def __init__(
            self,
            str type not None,
            pos_or_targets not None,
            path not None
    ) -> None:
        self.type = type
        self.path = <NBTPath>DpNBTPath_FromObject(path)
        if type == "block":
            self.data = <Position>DpPosition_FromObject(pos_or_targets)
        elif type == "entity":
            self.data = <Selector>DpSelector_FromObject(pos_or_targets)
        elif type == "storage":
            self.data = <str?>pos_or_targets
        else:
            PyErr_Format(ValueError, "data type must be 'block', 'entity' or 'storage', not '%U'", <void*>type)
    
    @property
    def pos(self):
        if self.type != "block":
            raise AttributeError("DataCase object has no attribute 'pos'")
        return self.data
        
    @property
    def target(self):
        if self.type != "entity":
            raise AttributeError("DataCase object has no attribute 'target'")
        return self.data
        
    @property
    def source(self):
        if self.type != "storage":
            raise AttributeError("DataCase object has no attribute 'source'")
        return self.data

    def __str__(self) -> str:
        if self.type == "block":
            return PyUnicode_FromFormat("data block %S %S", <void*>self.data, <void*>self.path)
        else:
            return PyUnicode_FromFormat("data %U %S %S", <void*>self.type, <void*>self.data, <void*>self.path)


cdef class EntityCase(Case):
    def __init__(self, targets):
        self.targets = <Selector>DpSelector_FromObject(targets)

    def __str__(self) -> str:
        return PyUnicode_FromFormat("entity %S", <void*>self.targets)


cdef class PredicateCase(Case):
    def __init__(self, str predicate not None):
        self.predicate = predicate

    def __str__(self) -> str:
        return PyUnicode_FromFormat("predicate %U", <void*>self.predicate)


cdef class ScoreCase(Case):
    def __init__(
            self,
            target,
            str target_obj not None,
            str ops not None,
            source_or_range,
            str source_obj = None
    ) -> None:
        self.target = <Selector>DpSelector_FromObject(target)
        self.target_obj = target_obj

        self.ops = ops
        if ops == "matches":
            if not source_obj is None:
                raise ValueError("invalid source objective")
            self.range = source_or_range
        elif ops in ["<", "<=", "=", ">=", ">"]:
            self.source = <Selector>DpSelector_FromObject(source_or_range)
            if source_obj is None:
                raise TypeError(
                    "mcdp.control_flow.ScoreCase.__init__ missing 1 required positional argument: 'source_obj'")
            self.source_obj = source_obj
        else:
            raise ValueError("ops must be '<', '<=', '=', '>=', '>' or 'matches'")

    def __str__(self) -> str:
        if self.ops == "matches":
            return PyUnicode_FromFormat("score %S %U matches %U", <void*>self.target, <void*>self.target_obj, <void*>self.range)
        else:
            return PyUnicode_FromFormat("score %S %U %U %S %U", <void*>self.target, <void*>self.target_obj, 
                <void*>self.ops, <void*>self.source, <void*>self.source_obj)


cdef class ConditionInstruction(BaseInstruction):
    def __init__(self, Case case not None, *, bint unless = False) -> None:
        self.unless = unless
        self.case = case

    def __str__(self) -> str:
        if self.unless:
            return PyUnicode_FromFormat("unless %S", <void*>self.case)
        else:
            return PyUnicode_FromFormat("if %S", <void*>self.case)


cdef class StoreMode(McdpObject):
    """Base class for store instruction"""

    def __str__(self) -> str:
        """This part should be overridden by the subclass"""
        raise NotImplementedError

    def __repr__(self):
        cdef const char* name = Py_TYPE_GetName(self)
        return PyUnicode_FromFormat("%s(%S)", name, <PyObject*>self)


cdef class BlockStore(StoreMode):
    def __init__(
            self,
            target_pos not None,
            path not None,
            str type not None,
            float scale
    ) -> None:
        self.target_pos = <Position>DpPosition_FromObject(target_pos)
        self.path = <NBTPath>DpNBTPath_FromObject(path)
        if not type in ["byte", "short", "int", "long", "float", "double"]:
            PyErr_Format(
                ValueError,
                "type must be 'byte', 'short', 'int', 'long', 'float' or 'double', not '%U'",
                <PyObject*>type
            )
        self.type = type
        self.scale = scale

    def __str__(self) -> str:
        cdef char* buff = PyOS_double_to_string(self.scale, ord("f"), 0, 0, NULL)
        try:
            return PyUnicode_FromFormat("block %S %S %U %s", <void*>self.target_pos, <void*>self.path, <void*>self.type, buff)
        finally:
            PyMem_Free(buff)


cdef class BossbarStore(StoreMode):
    def __init__(self, str id not None, str value not None):
        if not value in ["value", "max"]:
            PyErr_Format(ValueError, "value must be 'value' or 'max', not '%U'", <PyObject*>value)
        self.id = id
        self.value = value

    def __str__(self) -> str:
        return PyUnicode_FromFormat("bossbar %U %U", <void*>self.id, <void*>self.value)


cdef class EntityStore(StoreMode):
    def __init__(
            self,
            target not None,
            path not None,
            str type not None,
            float scale
    ):
        self.target = <Selector>DpSelector_FromObject(target)
        self.path = <NBTPath>DpNBTPath_FromObject(path)
        if not type in ["byte", "short", "int", "long", "float", "double"]:
            PyErr_Format(
                ValueError,
                "type must be 'byte', 'short', 'int', 'long', 'float' or 'double', not '%U'",
                <PyObject*>type
            )
        self.type = type
        self.scale = scale

    def __str__(self) -> str:
        cdef char* buff = PyOS_double_to_string(self.scale, ord("f"), 0, 0, NULL)
        try:
            return PyUnicode_FromFormat("entity %S %S %U %s", <void*>self.target, <void*>self.path, <void*>self.type, buff)
        finally:
            PyMem_Free(buff)


cdef class ScoreStore(StoreMode):
    def __init__(self, targets not None, str objective not None) -> None:
        self.target = <Selector>DpSelector_FromObject(targets)
        self.objective = objective

    def __str__(self) -> str:
        return PyUnicode_FromFormat("score %S %U", <void*>self.targets, <void*>self.objective)


cdef class StorageStore(StoreMode):
    def __init__(
            self,
            str target not None,
            path: Union[str, NBTPath],
            str type not None,
            float scale
    ) -> None:
        self.target = target
        self.path = <NBTPath>DpNBTPath_FromObject(path)
        if not type in ["byte", "short", "int", "long", "float", "double"]:
            PyErr_Format(
                ValueError,
                "type must be 'byte', 'short', 'int', 'long', 'float' or 'double', not '%U'",
                <PyObject*>type
            )
        self.type = type
        self.scale = scale

    def __str__(self) -> str:
        cdef char* buff = PyOS_double_to_string(self.scale, ord("f"), 0, 0, NULL)
        try:
            return PyUnicode_FromFormat("storage %S %S %U %s", <void*>self.target, <void*>self.path, <void*>self.type, buff)
        finally:
            PyMem_Free(buff)


cdef class StoreInstruction(BaseInstruction):
    def __init__(self, StoreMode mode not None, *, bint store_success = False) -> None:
        self.mode = mode
        self.store_success = store_success

    def __str__(self) -> str:
        cdef const char* store_str = "store success %S" if self.store_success else "store result %S"
        return PyUnicode_FromFormat(store_str, <void*>self.mode)


cdef class Execute(McdpObject):
    def __cinit__(self, execobj not None, *instructions) -> None:
        if isinstance(execobj, BaseInstruction):
            self._instructions = [execobj]
        else:
            self._instructions = (<Execute?>execobj)._instructions
        for i in instructions:
            if isinstance(i, BaseInstruction):
                self._instructions.append(i)
            else:
                self._instructions.extend((<Execute?>execobj)._instructions)
    
    cpdef str as_prefix(self, bint run_cmd = False):
        cdef:
            Py_ssize_t size = len(self._instructions)
            tuple instruction_str = PyTuple_New(size)
        for i in range(size):
            tmp = str(self._instructions[i])
            Py_INCREF(tmp)
            PyTuple_SET_ITEM(instruction_str, i, tmp)
        s = ' '.join(instruction_str)
        return PyUnicode_FromFormat("execute %U run " if run_cmd else "execute %U ", <PyObject*>s)
    
    def __call__(self, command = None):
        if not command is None:
            prefix = self.as_prefix(True)
            DpContext_Insert("%U%S", <PyObject*>prefix, <PyObject*>command)
        elif not isinstance(self._instructions[-1], ConditionInstruction):
            raise McdpTypeError(
                    "final instruction should be a conditon instruction"
                )
        else:
            (<Context>DpContext_Get()).put(self.as_prefix(False))

    @property
    def instructions(self):
        return list(self._instructions)
    
    def __repr__(self):
        tmp = tuple(self._instructions)
        return PyUnicode_FromFormat("Execute%S", <void*>tmp)


cdef object DpExecute_FromObject(object _case):
    if isinstance(_case, BaseInstruction):
        return Execute(_case)
    else:
        return <Execute?>_case
    