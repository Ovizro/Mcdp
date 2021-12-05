cdef class Version:
    cdef tuple vs_num
    cdef tuple _extend(self, int max)

cdef class PhaseVersion(Version):
    cdef readonly str phase

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