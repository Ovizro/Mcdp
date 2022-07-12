from .exception cimport McdpError


cdef class Version:
    cdef readonly:
        int major
        int minor
        int patch
        str prerelease
        str build
        
    cdef void _init_from_tuple(self, tuple version) except *
    cdef void _check_valid(self) except *
    cdef bint _ensure(
        self, list eq =*, list ne =*, object gt =*, object ge =*, object lt =*, object le =*) except -1
    cpdef tuple to_tuple(self)
    cpdef to_dict(self)
    cpdef int to_int(self)

cdef class VersionChecker:
    cdef dict collection
    cdef readonly:
        list sentences
        list functions
        bint checked
        bint save_check
    cdef public:
        version_factory
        __func__
    cpdef void apply_check(self)


cdef class McdpVersionError(McdpError):
    cdef readonly version