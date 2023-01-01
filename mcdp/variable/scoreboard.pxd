from ..objects cimport McdpObject
from ..context cimport DpContext_Insert
from .mcstring cimport BaseString, DpStaticStr_FromObject


cdef api class Scoreboard(McdpObject) [object DpScoreboardObject, type DpScoreboard_Type]:
    cdef readonly:
        str name
        str criteria
        BaseString display_name
    cpdef void add(self) except *
    cpdef void remove(self) except *
    cpdef void display(self, str pos) except *


cdef api int DpScoreboard_Add(object scb) except -1
cdef api int DpScoreboard_Remove(object scb) except -1
cdef api int DpScoreboard_Display(object scb, object pos) except -1