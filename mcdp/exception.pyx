cdef class McdpError(Exception):
    """
    Base exception for Mcdp

    This exception can be raised when mcdp compiler is running.
    """


cdef class McdpInitalizeError(McdpError):
    pass


cdef class McdpRuntimeError(McdpError):
    pass


cdef class McdpCompileError(McdpError):
    pass

    
cdef class McdpValueError(McdpRuntimeError):
    pass


cdef class McdpTypeError(McdpRuntimeError):
    pass


cdef class McdpIndexError(McdpValueError):
    pass


cdef class McdpUnboundError(McdpRuntimeError):
    pass

