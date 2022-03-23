from libc.stdint cimport uint8_t
from cpython cimport PyObject, PyTuple_New, PyTuple_SetItem, PyTuple_GetItem
from ._typing cimport McdpVar, _McdpBaseModel
from .version cimport Version, VersionError
from .exception cimport McdpValueError, McdpTypeError


cdef enum MCStr_Color:
    BLACK       = 0
    DARK_BLUE   = 1
    DARK_GREEN  = 2
    DARK_AQUA   = 3
    DARK_RED    = 4
    DARK_PURPLE = 5
    GOLD        = 6
    GRAY        = 7
    DARK_GRAY   = 8
    BLUE        = 9
    GREEN       = 10
    AQUA        = 11
    RED         = 12
    LIGHT_PURPLE= 13
    YELLOW      = 14
    WHITE       = 15


cdef class MCStringObject(_McdpBaseModel):
    pass


cdef class Score(MCStringObject):
    cdef readonly:
        str name
        str objective
        str value


cdef class ClickEvent(MCStringObject):
    cdef readonly:
        str action
        str value


cdef class HoverEvent(MCStringObject):
    cdef readonly:
        str action
        str value
        contents


cdef class HoverItem(MCStringObject):
    cdef readonly:
        str id
        uint8_t count
        str tag


cdef class HoverEntity(MCStringObject):
    cdef readonly:
        MCString name
        str type
        str id


cdef class MCSS(MCStringObject):
    cdef readonly:
        str color
        bint bold
        bint italic
        bint underlined
        bint strikethrough
        bint obfuscated
        str font
        separator
        str insertion
        ClickEvent clickEvent
        HoverEvent hoverEvent


cdef class MCString(MCSS):
    cdef readonly:
        str text
        str translate
        list with_
        Score score
        str selector
        str keybind
        str nbt
        str block
        str entity
        str storage
        list extra


cpdef MCString fsmcstr(object t_mcstring)