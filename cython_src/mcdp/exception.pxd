from ._typing cimport McdpError


cdef class McdpVersionError(McdpError):
    pass


cdef class McdpValueError(McdpError):
    pass


cdef class McdpTypeError(McdpError):
    pass
    
    
cdef class McdpIndexError(McdpError):
    pass