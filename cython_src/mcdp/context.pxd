from .objects cimport McdpObject, BaseNamespace, DpNamespace_Property, T_property
from .exception cimport McdpError, McdpValueError
from .stream cimport Stream, va_list, va_start, va_end


cdef extern from "Python.h":
    str PyUnicode_FromFormatV(const char* format, va_list vargs)
    str PyUnicode_FromFormat(const char* format, ...)


ctypedef api object (*T_handler)(object ctx, object code, object chain)
ctypedef api object (*T_link)(object handler_self, object new_head)


cdef class Handler(McdpObject):
    cdef public Handler next

    cpdef object do_handler(self, Context ctx, object code)
    cpdef object next_handler(self, Context ctx, object code)
    cpdef void append(self, Handler hdl)
    cpdef Handler link_to(self, Handler new_head)


cdef api class _CHandlerMeta(type) [object DpHandlerMetaObject, type DpHandlerMeta_Type]:
    cdef:
        object handler_func
        object linked_func
    cdef void set_handler(self, T_handler hdl_func)
    cdef void set_link(self, T_link lk_func)


cdef class _CHandler(Handler):
    cpdef object do_handler(self, Context ctx, object code)
    cpdef Handler link_to(self, Handler new_head)


cdef class CommentHandler(Handler):
    cpdef object do_handler(self, Context ctx, object code)
    cpdef Handler link_to(self, Handler new_head)


cdef class HandlerIter:
    cdef readonly Handler cur


cdef api class Context(McdpObject) [object DpContextObject, type DpContext_Type]:
    cdef Handler handler_chain
    cdef readonly:
        str name
        Stream stream
        BaseNamespace namespace
        Context back
    
    cpdef void set_back(self, Context back) except *
    cpdef void join(self) except *
    cpdef bint writable(self)
    cpdef void put(self, object code) except *
    cpdef void newline(self, unsigned int n_line = *) except *
    cpdef void add_handler(self, Handler hdl) except *
    cpdef void pop_handler(self, Handler hdl = *) except *


cdef class _CommentImpl:
    cdef CommentHandler cmt_hdl
    cdef public:
        __name__
        __qualname__
    
    cpdef bint ensure(self) except -1
    cdef void enter_comment(self) except *
    cdef void exit_comment(self) except *


cdef _CHandlerMeta DpHandler_NewMeta(const char* name, T_handler handler_func)
cdef object DpHandler_New(_CHandlerMeta cls, object next_hdl)
cdef object DpHandler_NewSimple(const char* name, T_handler handler_func)
cdef api object DpHandler_DoHandler(object hdl, object ctx, object code)

cdef api object DpContext_Get()
cdef api object DpContext_New(const char* name)
cdef int DpContext_Join(object ctx) except -1
cdef api int DpContext_AddHnadler(object ctx, object hdl) except -1
cdef int DpContext_AddHandlerSimple(object ctx, T_handler handler_func) except -1
cdef int DpContext_InsertV(const char* format, va_list ap) except -1
cdef int DpContext_Insert(const char* format, ...) except -1
cdef int DpContext_CommentV(const char* format, va_list ap) except -1
cdef int DpContext_Comment(const char* format, ...) except -1
cdef int DpContext_FastComment(const char* cmt) except -1


cdef class McdpContextError(McdpError):
    cdef readonly:
        Context context