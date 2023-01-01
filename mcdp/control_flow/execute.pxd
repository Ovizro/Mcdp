from cpython cimport PyObject

from ..objects cimport McdpObject
from ..exception cimport McdpTypeError
from ..variable.selector cimport Selector, DpSelector_FromObject
from ..variable.position cimport Position, DpPosition_FromObject
from ..variable.nbtpath cimport NBTPath, DpNBTPath_FromObject


cdef class BaseInstruction(McdpObject):
    pass

cdef class AlignInstruction(BaseInstruction):
    cdef readonly:
        str axes

cdef class AnchoredInstruction(BaseInstruction):
    cdef readonly:
        str anchor

cdef class AsInstruction(BaseInstruction):
    cdef readonly:
        Selector targets

cdef class AtInstruction(BaseInstruction):
    cdef readonly:
        Selector targets

cdef class FacingInstruction(BaseInstruction):
    cdef readonly:
        bint entity
        Position pos
        Selector targets
        str anchor

cdef class InInstruction(BaseInstruction):
    cdef readonly:
        str dimension

cdef class PositionedInstruction(BaseInstruction):
    cdef readonly:
        bint entity
        Position pos
        Selector targets

cdef class RotatedInstruction(BaseInstruction):
    cdef readonly:
        bint entity
        (float, float) rot
        Selector targets


cdef class Case(McdpObject):
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
    cdef object data
    cdef readonly:
        str type
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


cdef class ConditionInstruction(BaseInstruction):
    cdef readonly:
        bint unless
        Case case "condition"


cdef class StoreMode(McdpObject):
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


cdef class StoreInstruction(BaseInstruction):
    cdef readonly:
        bint store_success
        StoreMode mode


cdef class Execute(McdpObject):
    cdef list _instructions

    cpdef str as_prefix(self, bint run_cmd = *)


cdef api object DpExecute_FromObject(object _case)