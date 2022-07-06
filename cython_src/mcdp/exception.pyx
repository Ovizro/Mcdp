cdef class McdpError(Exception):
    pass


cdef class McdpValueError(McdpError):
    pass


cdef class McdpTypeError(McdpError):
    pass


cdef class McdpIndexError(McdpError):
    pass