cdef class Counter:
    cdef readonly:
        int value
        str name
    cdef list link

    cpdef void link_to(self, Counter other) except*

cdef class ContextCounter(object):

    cdef public:
        Counter dirs
        Counter files
        Counter commands
        Counter chars

cpdef ContextCounter get_counter()