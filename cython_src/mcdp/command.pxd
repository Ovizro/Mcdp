from ._typing cimport McdpVar, McdpError
from .context cimport Context, _envs, dp_insert, dp_comment, dp_commentline, dp_newline, get_extra_path 
from .exception cimport McdpValueError, McdpTypeError, McdpIndexError
from .mcstring cimport MCString, fsmcstr


cdef enum PosType:
    Empty = 0, Local, Relative, Absolute


cdef class PosComponent(McdpVar):
    cdef readonly:
        str value
        PosType type


cdef class Position(McdpVar):
    cdef list _posXYZ
    cdef readonly:
        PosType type
        
    cpdef void teleport(self, slt) except *
    @staticmethod
    cdef Position validate_argument(val, str arg)


cdef class MultiDict(dict):
    cdef object __weakref__

    cpdef void add(self, key, value) except *
    cdef list _values(self)
    cdef list _items(self)


cdef class Selector(McdpVar):
    cdef readonly:
        str name
        MultiDict args

    cdef void _add_tag(self, const char* tag) except *
    cdef void _remove_tag(self, const char* tag) except *
    cpdef void remove(self) except *
    @staticmethod
    cdef Selector validate_argument(val, str arg)


cdef class NBTPath(McdpVar):
    cdef readonly tuple path
    
    @staticmethod
    cdef NBTPath validate_argument(val, str arg)


cdef class TellingObject(McdpVar):
    cdef readonly list data
    cdef public bint base
    
    cpdef TellingObject copy(self)

cdef class Printer(TellingObject):
    cdef readonly list input

cdef class PrinterEOF(TellingObject):
    pass


cdef class InstructionEnvironment(Context):
    cdef readonly Instruction instruction

    cpdef void mkhead(self)

cdef class ExecuteEnvironment(Context):
    cdef readonly:
        Execute exec
        bint inline "inline_handler"

    cpdef void mkhead(self)

cdef class Instruction(McdpVar):
    cdef InstructionEnvironment enter(self)
    cdef void exit(self) except *

cdef class AlignInstruction(Instruction):
    cdef readonly:
        str axes

cdef class AnchoredInstruction(Instruction):
    cdef readonly:
        str anchor

cdef class AsInstruction(Instruction):
    cdef readonly:
        Selector targets

cdef class AtInstruction(Instruction):
    cdef readonly:
        Selector targets

cdef class FacingInstruction(Instruction):
    cdef readonly:
        bint entity
        Position pos
        Selector targets
        str anchor

cdef class InInstruction(Instruction):
    cdef readonly:
        str dimension

cdef class PositionedInstruction(Instruction):
    cdef readonly:
        bint entity
        Position pos
        Selector targets

cdef class RotatedInstruction(Instruction):
    cdef readonly:
        bint entity
        (float, float) rot
        Selector targets


cdef class Case(McdpVar):
    pass

cdef class BlockCase(Case):
    cdef readonly:
        Position pos
        str block
        
cdef class BlocksCase(Case):
    cdef readonly:
        Position start
        Position end
        Position destination
        str scan_mode

cdef class DataCase(Case):
    cdef readonly:
        str type
        Position pos
        Selector targets
        NBTPath path

cdef class EntityCase(Case):
    cdef readonly:
        Selector targets
    
cdef class PredicateCase(Case):
    cdef readonly:
        str predicate

cdef class ScoreCase(Case):
    cdef readonly:
        Selector target
        str target_obj 
        str ops
        Selector source
        str source_obj
        str range
    

cdef class ConditionInstruction(Instruction):
    cdef readonly:
        bint unless
        Case case "condition"


cdef class StoreMode(McdpVar):
    pass
    
cdef class BlockStore(StoreMode):
    cdef readonly:
        Position target_pos
        NBTPath path
        str type
        float scale

cdef class BossbarStore(StoreMode):
    cdef readonly:
        str id
        str value
    
cdef class EntityStore(StoreMode):
    cdef readonly:
        Selector target
        NBTPath path
        str type
        float scale
    
cdef class ScoreStore(StoreMode):
    cdef readonly:
        Selector targets
        str objective

cdef class StorageStore(StoreMode):
    cdef readonly:
        str target
        NBTPath path
        str type
        float scale 


cdef class StoreInstruction(Instruction):
    cdef readonly:
        bint store_success
        StoreMode mode

cdef class Execute(McdpVar):
    cdef readonly list instructions
    cdef public bint inline_handler

    cpdef str command_prefix(self)
    cdef ExecuteEnvironment enter(self)
    cdef void exit(self) except *
    

ctypedef fused AnyExecutor:
    Instruction
    Execute


cpdef Execute inline(AnyExecutor instruction)

cdef class McdpCommandError(McdpError):
    cdef readonly str command