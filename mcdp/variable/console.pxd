from ..objects cimport McdpObject
from ..context cimport DpContext_Insert
from .selector cimport DpSelector_FromObject, SL_A
from .mcstring cimport BaseString, PlainString, DpStaticStr_FromObject, DpStaticStr_FromString


cdef enum MCTitle_Position:
    TITLE
    SUBTITLE
    ACTIONBAR


cdef class _Console(McdpObject):
    @staticmethod
    cdef void _title(tuple texts, sep, MCTitle_Position pos, target) except *


cdef api int DpConsole_Tell(object selector, object message) except -1
cdef api int DpConsole_TellString(object selector, const char* message) except -1
cdef api int DpConsole_Print(object message) except -1
cdef api int DpConsole_PrintString(const char* message) except -1
cdef api int DpConsole_Title(object selector, MCTitle_Position pos, object message) except -1
cdef api int DpConsole_Show(MCTitle_Position pos, object message) except -1
cdef api int DpConsole_ShowString(MCTitle_Position pos, const char* message) except -1
cdef api int DpConsole_TitleReset(object selector) except -1
cdef api int DpConsole_TitleClear(object selector) except -1
cdef api int DpConsole_TitleSetTime(object selector, int fadeIn, int stay, int fadeOut) except -1