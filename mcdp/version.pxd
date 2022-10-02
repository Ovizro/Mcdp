from .exception cimport McdpError


cdef extern from "include/version.h":
    const unsigned int DP_RELEASE_LEVEL_ALPHA, DP_RELEASE_LEVEL_BETA, DP_RELEASE_LEVEL_GAMMA, DP_RELEASE_LEVEL_FINAL
    const unsigned int DP_MAJOR_VERSION, DP_MINOR_VERSION, DP_MICRO_VERSION
    const unsigned int DP_RELEASE_LEVEL, DP_RELEASE_SERIAL
    const char* DP_VERSION
    const unsigned int DP_VERSION_HEX


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