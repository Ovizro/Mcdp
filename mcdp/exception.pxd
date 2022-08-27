cdef api class McdpError(Exception) [object McdpErrorObject, type DpExc_BaseError, check_size ignore]:
    pass


cdef api class McdpValueError(McdpError) [object McdpValueErrorObjet, type DpExc_ValueError, check_size ignore]:
    pass


cdef api class McdpTypeError(McdpError) [object McdpTypeErrorObject, type DpExc_TypeError, check_size ignore]:
    pass
    
    
cdef api class McdpIndexError(McdpError) [object McdpIndexErrorObject, type DpExc_IndexError, check_size ignore]:
    pass


cdef api class McdpUnboundError(McdpError) [object McdpUnboundErrorObject, type DpExc_UnboundError, check_size ignore]:
    pass


cdef api class McdpRuntimeError(McdpError) [object McdpRuntimeErrorObject, type DpExc_RuntimeError, check_size ignore]:
    pass