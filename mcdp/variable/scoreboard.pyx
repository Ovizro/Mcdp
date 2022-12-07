from cpython cimport PyErr_Format


cdef class Scoreboard(McdpObject):
    def __cinit__(self, str name not None, *, str criteria not None = "dummy", display = None):
        self.name = name
        self.criteria = criteria
        if not display is None:
            self.display_name = DpStaticStr_FromObject(display)
    
    cpdef void add(self) except *:
        if not self.display_name is None:
            DpContext_Insert("scoreboard objectives add %U %U %S",
                <void*>self.name, <void*>self.criteria, <void*>self.display_name
            )
        else:
            DpContext_Insert("scoreboard objectives add %U %U",
                <void*>self.name, <void*>self.criteria
            )
    
    cpdef void remove(self) except *:
        DpContext_Insert("scoreboard objectives remove %U", <void*>self.name)
    
    cpdef void display(self, str pos) except *:
        if pos in ["list", "sidebar", "belowName"] or pos.startswith("sidebar.team."):
            DpContext_Insert("scoreboard objectives setdisplay %U %U", <void*>pos, <void*>self.name)
        else:
            PyErr_Format(ValueError, "invalid scoreboard display position '%U'", <void*>pos)


cdef int DpScoreboard_Add(object scb) except -1:
    Scoreboard.add(scb)
    return 0

cdef int DpScoreboard_Remove(object scb) except -1:
    Scoreboard.remove(scb)
    return 0

cdef int DpScoreboard_Display(object scb, object pos) except -1:
    Scoreboard.display(scb, pos)
    return 0