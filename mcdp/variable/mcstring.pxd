from libc.stdint cimport uint8_t 
from ..cpython_interface cimport PyUnicode_FromFormat, Py_TYPE_NAME

from ..objects cimport McdpObject
from ..version cimport Version, McdpVersionError


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


cdef api class MCStringModel(McdpObject) [object DpStrModelObject, type DpStrModel_Type]:
    cpdef dict to_dict(self)
    cpdef str to_json(self)


cdef class Score(MCStringModel):
    cdef readonly:
        str name
        str objective
        str value
    cpdef dict to_dict(self)


cdef class ClickEvent(MCStringModel):
    cdef readonly:
        str action
        str value
    cpdef dict to_dict(self)


cdef class HoverEvent(MCStringModel):
    cdef readonly:
        str action
        str value
        contents
    cpdef dict to_dict(self)


cdef class HoverItem(MCStringModel):
    cdef readonly:
        str id
        uint8_t count
        str tag
    cpdef dict to_dict(self)


cdef class HoverEntity(MCStringModel):
    cdef readonly:
        MCString name
        str type
        str id
    cpdef dict to_dict(self)


cdef api class MCSS(MCStringModel) [object DpStrStyleObject, type DpStrStyle_Type]:
    cdef readonly:
        str color
        bint bold
        bint italic
        bint underlined
        bint strikethrough
        bint obfuscated
        str font
        object separator
        str insertion
        ClickEvent clickEvent
        HoverEvent hoverEvent

    cpdef dict to_dict(self)
        

cdef api class MCString(MCSS) [object DpStaticStrObject, type DpStaticStr_Type]:
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

    cpdef void extend(self, MCString other)
    cpdef dict to_dict(self)

        
cdef api object DpStaticStr_FromObject(object obj)
cdef api object DpStaticStr_FromString(const char* string)