cdef class Counter:

    def __init__(self, str name = None, int init = 0):
        self.value = init
        self.name = name
        self.link = []
    
    cpdef void link_to(self, Counter other) except *:
        if other in self.linked:
            return
        if self in other.linked or other is self:
            raise ValueError("circular link counters.")
        self.link.append(other)

    @property
    def linked(self):
        cdef list l = self.link.copy()
        for c in self.link:
            l.extend(c.linked)
        return l

    def __pos__(self) -> int:
        cdef Counter c
        cdef l_link = self.linked
        if l_link:
            for c in l_link:
                c += 1
        self.value += 1
        return self.value

    def __neg__(self) -> int:
        cdef Counter c
        cdef l_link = self.linked
        if l_link:
            for c in l_link:
                c -= 1
        self.value -= 1
        return self.value

    def __invert__(self) -> int:
        self.value = 0
        return self.value

    def __add__(self, other):
        if isinstance(other, Counter):
            return self.value + other.value
        elif isinstance(other, int):
            return self.value + other
        else:
            return NotImplemented

    __radd__ = __add__

    def __iadd__(self, other) -> "Counter":
        if isinstance(other, Counter):
            self.value += other.value
            return self
        elif isinstance(other, int):
            self.value += other
            return self
        else:
            return NotImplemented

    def __sub__(self, other) -> int:
        if isinstance(other, Counter):
            return self.value - other.value
        elif isinstance(other, int):
            return self.value - other
        else:
            return NotImplemented

    def __rsub__(self, other) -> int:
        if isinstance(other, int):
            return other - self.value
        else:
            return NotImplemented

    def __isub__(self, other) -> "Counter":
        if isinstance(other, Counter):
            self.value -= other.value
            return self
        elif isinstance(other, int):
            self.value -= other
            return self
        else:
            return NotImplemented

    def __int__(self) -> int:
        return self.value

    __index__ = __int__

    def __bool__(self) -> bool:
        if self.value > 0:
            return True
        else:
            return any(self.linked)

    def __repr__(self) -> str:
        if self.name:
            return "<counter %s with value %d>" % (self.name, self.value)
        else:
            return "<counter %s>" % self.value

    def __str__(self) -> str:
        return str(self.value)

cdef class ContextCounter(object):
    
    def __init__(self):
        self.dirs = Counter("__dir__")
        self.files = Counter("__file__")
        self.commands = Counter("__command__")
        self.chars = Counter("__char__")

    def reset(self) -> None:
        ~self.dirs
        ~self.files
        ~self.commands
        ~self.chars

    def print_out(self) -> None:
        print(f"{self.dirs}+ dirs, {self.files} files, {self.commands} commands, {self.chars} chars in total")

cdef ContextCounter _current_counter = None

cpdef ContextCounter get_counter():
    global _current_counter
    if not _current_counter:
        _current_counter = ContextCounter()

    return _current_counter