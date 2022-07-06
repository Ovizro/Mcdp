cdef class McdpObject(object):
    pass


cdef class BaseNamespace(McdpObject):
    cdef readonly:
        bytes n_name "name"
        bytes n_path "path"
        str n_tag "tag"
        object n_selector "selector"