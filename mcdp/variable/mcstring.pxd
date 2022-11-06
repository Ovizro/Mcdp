from libc.stdint cimport uint8_t 
from cpython cimport PyObject
from ..cpython_interface cimport PyUnicode_FromFormat, Py_TYPE_NAME, _PyType_Lookup

from ..objects cimport McdpObject
from ..exception cimport McdpValueError
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

cdef enum MCStr_RenderStyle:
    BOLD = 1 << 0
    ITALIC = 1 << 1
    UNDERLINED = 1 << 2
    STRIKETHROUGH = 1 << 3
    OBFUSCATED = 1 << 4


cdef api class StringModel(McdpObject) [object DpStrModelObject, type DpStrModel_Type]:
    cpdef dict to_dict(self)
    cpdef str to_json(self)


cdef class Score(StringModel):
    cdef readonly:
        str name
        str objective
        str value
    cpdef dict to_dict(self)


cdef class ClickEvent(StringModel):
    cdef readonly:
        str action
        str value
    cpdef dict to_dict(self)


cdef class HoverEvent(StringModel):
    cdef readonly:
        str action
        str value
        contents
    cpdef dict to_dict(self)


cdef class HoverItem(StringModel):
    cdef readonly:
        str id
        uint8_t count
        str tag
    cpdef dict to_dict(self)


cdef class HoverEntity(StringModel):
    cdef readonly:
        BaseString name
        str type
        str id
    cpdef dict to_dict(self)


cdef api class MCSS(StringModel) [object DpStrStyleObject, type DpStrStyle_Type]:
    cdef int render_flag
    cdef public:
        str color
        str font

    cpdef dict to_dict(self)


cdef api class BaseString(StringModel) [object DpStaticStrObject, type DpStaticStr_Type]:
    cdef readonly:
        MCSS style
        list extra
    cdef public:
        str insertion
        ClickEvent clickEvent
        HoverEvent hoverEvent

    cpdef void append(self, mcstr) except *
    cpdef void set_interactivity(self, str type, value) except *
    cpdef dict to_dict(self)


cdef class PlainString(BaseString):
    cdef readonly:
        str text
    cpdef dict to_dict(self)


cdef class TranslatedString(BaseString):
    cdef readonly:
        str translate
        tuple with_
    cpdef dict to_dict(self)


cdef class ScoreString(BaseString):
    cdef readonly:
        Score score
    cpdef dict to_dict(self)


cdef class EntityNameString(BaseString):
    cdef readonly:
        str selector
        PlainString separator
    cpdef dict to_dict(self)


cdef class KeybindString(BaseString):
    cdef readonly:
        str keybind
    cpdef dict to_dict(self)


cdef class NBTValueString(BaseString):
    cdef readonly:
        str nbt
        bint interpret
        PlainString separator
        str block
        str entity
        str storage
    cpdef dict to_dict(self)


cdef api object DpStrStyle_New(MCStr_Color color, int render, const char* font)
cdef api object DpStaticStr_FromObject(object obj)
cdef api object DpStaticStr_FromString(const char* string)
cdef api object DpStaticStr_FromDict(dict data)
cdef api object DpStaticStr_FromStyle(object style, object text)
cdef api object DpStaticStr_FromStyleString(object style, const char* text)
cdef api object DpStaticStr_Copy(object mcstr)
cdef api dict DpStaticStr_ToDict(object mcstr)