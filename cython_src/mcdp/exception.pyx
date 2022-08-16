cdef class McdpError(Exception):
    """
    Base exception for Mcdp

    This exception can be raised when mcdp compiler is running.
    """


cdef class McdpValueError(McdpError):
    pass


cdef class McdpTypeError(McdpError):
    pass


cdef class McdpIndexError(McdpError):
    pass


cdef class McdpUnboundError(McdpError):
    pass


cdef class McdpRuntimeError(McdpError):
    pass