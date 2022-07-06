from ._typing cimport McdpVar, McdpError
from .stream cimport Stream, StreamCounter, get_counter, va_list, va_start, va_end
from .version cimport get_version, Version
from .exception cimport McdpValueError

cdef EnvCache _envs

cdef class EnvCache(list):
    cdef int _capacity

    cdef void _append(self, Context env)
    cdef Context _pop(self)
    cdef void _clear(self)


cdef class EnvMethod:
    cdef __func__


cdef class Context(McdpVar):
    cdef readonly:
        str name
        Stream stream
        list handlers
    
    cpdef void mkhead(self) except *
    cpdef void write(self, str content) except *
    cpdef bint writable(self)
    cpdef void activate(self, bint append = *) except *
    cpdef void deactivate(self)
    cdef void enter(self) except *
    cdef void exit(self) except *


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
cdef api void dp_commentline(const char* cmt, ...) except *
cdef api void dp_newline(int line) except *
cdef api void dp_fastAddTag(const char* _tag) except *
cdef api void dp_addTag(str tag, str value, str m_name) except *
cdef api void dp_enter(str name, str root, list hdls) except *
cdef api void dp_fastEnter(const char* name) except *
cdef api void dp_exit() except *
cdef str get_namespace()
cdef str get_library_path()
cdef str get_extra_path()
cdef void init_namespace(str nsp)


cdef class McdpContextError(McdpError):
    cdef readonly:
        Context context