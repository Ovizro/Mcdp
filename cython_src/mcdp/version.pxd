cdef fused T_Version:
    dict
    tuple
    str
    Version

cdef fused T_Key:
    int
    slice

cdef class Version:
    cdef readonly:
        int major
        int minor
        int patch
        str prerelease
        str build
        
    cdef void _init_from_tuple(self, tuple version) except *
    cdef void _check_valid(self) except *
    cpdef tuple to_tuple(self)
    cpdef to_dict(self)

cdef class VersionChecker:
    cdef readonly:
        list sentence
        dict collection
        bint checked
        __func__
    cdef public:
        version_factory
    cpdef void apply_check(self)

cdef class AioCompatVersionChecker(VersionChecker):
    pass

cdef class VersionError(Exception):
    cdef readonly version