from cpython cimport PyObject
from .objects cimport McdpObject, BaseNamespace, DpNamespace_Property, T_property
from .exception cimport McdpError, McdpValueError
from .stream cimport Stream, va_list, va_start, va_end


cdef extern from "Python.h":
    str PyUnicode_FromFormatV(const char* format, va_list vargs)
    str PyUnicode_FromFormat(const char* format, ...)


ctypedef api object (*T_handler)(object ctx, object code, object chain)
ctypedef api object (*T_connect)(object handler_self, object header)


cdef class Handler:
    cdef public Handler next

    cpdef object do_handler(self, Context ctx, object code)
    cpdef object next_handler(self, Context ctx, object code)
    cpdef void append(self, Handler nxt)
    cpdef Handler link_handler(self, Handler header)
    cpdef Handler pop_handler(self, Handler header)


cdef api class _CHandlerMeta(type) [object DpHandlerMetaObject, type DpHandlerMeta_Type]:
    cdef:
        object handler_func
        object link_func
        object pop_func
    cdef void set_handler(self, T_handler hdl_func)
    cdef void set_link(self, T_connect lk_func)
    cdef void set_pop(self, T_connect pop_func)


cdef class _CHandler(Handler):
    cpdef object do_handler(self, Context ctx, object code)
    cpdef Handler link_handler(self, Handler header)


cdef class CommentHandler(Handler):
    cdef Py_ssize_t link_count
    cpdef object do_handler(self, Context ctx, object code)
    cpdef Handler link_handler(self, Handler header)
    cpdef Handler pop_handler(self, Handler header)


cdef class HandlerIter:
    cdef readonly Handler cur


cdef api class Context(McdpObject) [object DpContextObject, type DpContext_Type]:
    cdef:
        Py_ssize_t length
        Handler handler_chain
    cdef readonly:
        str name
        Stream stream
        BaseNamespace namespace
        Context back
    
    cpdef void set_back(self, Context back) except *
    cdef void init_stream(self) except *
    cpdef void join(self) except *
    cpdef void activate(self) except *
    cpdef void deactivate(self) except *
    cpdef bint writable(self)
    cpdef void put(self, object code) except *
    cpdef list get_handler(self)
    cpdef void add_handler(self, Handler hdl) except *
    cpdef void pop_handler(self) except *


cdef class _CommentImpl:
    cdef CommentHandler cmt_hdl
    cdef public:
        __name__
        __qualname__
    
    cpdef bint ensure(self) except -1
    cdef void enter_comment(self) except *
    cdef void exit_comment(self) except *


cdef api _CHandlerMeta DpHandlerMeta_New(const char* name, T_handler handler_func)
cdef api object DpHandler_FromMeta(_CHandlerMeta cls, object next_hdl)
cdef api object DpHandler_NewSimple(const char* name, T_handler handler_func)
cdef api object DpHandler_DoHandler(object hdl, object ctx, object code)

cdef api PyObject* DpContext_Get() except NULL
cdef api object DpContext_New(const char* name)
cdef api int DpContext_Join(object ctx) except -1
cdef api int DpContext_AddHnadler(object ctx, object hdl) except -1
cdef api int DpContext_AddHandlerSimple(object ctx, T_handler handler_func) except -1
cdef api int DpContext_InsertV(const char* format, va_list ap) except -1
cdef api int DpContext_Insert(const char* format, ...) except -1
cdef api int DpContext_CommentV(const char* format, va_list ap) except -1
cdef api int DpContext_Comment(const char* format, ...) except -1
cdef api int DpContext_FastComment(const char* cmt) except -1
cdef api int DpContext_Newline(unsigned int n_line) except -1


cdef class McdpContextError(McdpError):
    cdef readonly:
        Context context
