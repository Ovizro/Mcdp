cdef api class McdpError(Exception) [object McdpErrorObject, type DpExc_BaseError, check_size ignore]:
    pass


cdef api class McdpInitalizeError(McdpError) [object McdpInitalizeErrorObject, type DpExc_InitalizeError, check_size ignore]:
    pass


cdef api class McdpRuntimeError(McdpError) [object McdpRuntimeErrorObject, type DpExc_RuntimeError, check_size ignore]:
    pass
    

cdef api class McdpCompileError(McdpError) [object McdpCompileErrorObject, type DpExc_CompileError, check_size ignore]:
    pass


cdef api class McdpValueError(McdpRuntimeError) [object McdpValueErrorObjet, type DpExc_ValueError, check_size ignore]:
    pass


cdef api class McdpTypeError(McdpRuntimeError) [object McdpTypeErrorObject, type DpExc_TypeError, check_size ignore]:
    pass
    
    
cdef api class McdpIndexError(McdpValueError) [object McdpIndexErrorObject, type DpExc_IndexError, check_size ignore]:
    pass


cdef api class McdpUnboundError(McdpRuntimeError) [object McdpUnboundErrorObject, type DpExc_UnboundError, check_size ignore]:
    pass

