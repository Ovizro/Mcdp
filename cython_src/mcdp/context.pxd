from ._typing cimport McdpVar, McdpError
from .stream cimport Stream
from .counter cimport Counter, get_counter
from .version cimport get_version
from .exception cimport McdpValueError


cdef StackCache _stack

cdef class StackCache(list):
    cdef int _capacity

    cdef void _append(self, Context env)
    cdef Context _pop(self)
    cdef void _clear(self)


cdef class EnvMethod:
    cdef __func__


cdef class Handler(McdpVar):
    cdef readonly:
        str env_type

    cpdef void init(self)
    cpdef str command(self, str cmd)
    cpdef Context stream(self)


cdef class Context(McdpVar):
    cdef readonly:
        str name
        Stream stream
        list handlers
    
    cpdef void write(self, str content) except *
    cpdef bint writable(self)
    cpdef void activate(self, bint append = *) except *
    cpdef void deactivate(self)


cdef class TagManager(McdpVar):
    cdef:
        str name
        str type
        bint replace
        str root_path
        dict cache
    
    cpdef void add(self, str tag, str item, str namespace = *) except *
    cpdef dict get_tag_data(self, str tag, bint replace = *)
    cpdef void apply_tag(self, str tag, bint replace = *) except *
    cpdef void apply(self)
    cdef void collect(self)

cdef api void dp_insert(const char* cmd) except *
cdef api void dp_comment(const char* cmt) except *
cdef api void dp_newline(int line) except *
cdef api void dp_addTag(const char* _tag) except *
cdef void set_context_path(str path)
cpdef str get_namespace()


cdef class McdpContextError(McdpError):
    cdef readonly:
        Context context