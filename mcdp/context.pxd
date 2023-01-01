from cpython cimport PyObject
from .cpython_interface cimport *
from .objects cimport McdpObject, BaseNamespace, DpNamespace_Property, T_property
from .exception cimport McdpInitalizeError, McdpRuntimeError, McdpUnboundError
from .stream cimport Stream


ctypedef api void (*T_hook)(object nsp) except *
ctypedef api object (*T_handler)(object ctx, object code, object chain)
ctypedef api object (*T_connect)(object handler_self, object header)

ctypedef struct ContextConfig:
    Py_ssize_t max_open
    Py_ssize_t max_stack
    bint use_annotates
    

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


cdef class AnnotateHandler(Handler):
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
    cpdef void reactivate(self) except *
    cpdef void deactivate(self) except *
    cpdef bint writable(self)
    cpdef void put(self, object code) except *
    cpdef list get_handler(self)
    cpdef void add_handler(self, Handler hdl) except *
    cpdef void pop_handler(self, Handler hdl = *) except *


cdef class _AnnotateImpl:
    cdef AnnotateHandler cmt_hdl
    cdef public:
        __name__
        __qualname__
    
    cpdef bint ensure(self) except -1
    cdef void enter_annotate(self) except *
    cdef void exit_annotate(self) except *


cdef api _CHandlerMeta DpHandlerMeta_New(const char* name, T_handler handler_func)
cdef api void DpHandlerMeta_SetHandler(_CHandlerMeta cls, T_handler func)
cdef api void DpHandlerMeta_SetLinkHandler(_CHandlerMeta cls, T_connect func)
cdef api void DpHandlerMeta_SetPopHandler(_CHandlerMeta cls, T_connect func)
cdef api object DpHandler_FromMeta(_CHandlerMeta cls, object next_hdl)
cdef api object DpHandler_NewSimple(const char* name, T_handler handler_func)
cdef api PyObject* DpHandler_GetNext(object hdl) except NULL
cdef api object DpHandler_DoHandler(object hdl, object ctx, object code)

cdef api PyObject* DpContext_Initalize(object nsp) except NULL
cdef api PyObject* DpContext_Get() except NULL
cdef api object DpContext_New(const char* name)
cdef api PyObject* DpContext_GetBack(object ctx) except NULL
cdef api int DpContext_SetBack(object ctx, object back) except -1
cdef api int DpContext_Join(object ctx) except -1
cdef api bint DpContext_Writable(object ctx) except -1
cdef api int DpContext_Activate(object ctx) except -1
cdef api int DpContext_Reactivate(object ctx) except -1
cdef api int DpContext_Deactivate(object ctx) except -1
cdef api int DpContext_Finalize() except -1
cdef api int DpContext_AddHnadler(object ctx, object hdl) except -1
cdef api int DpContext_AddHandlerSimple(object ctx, T_handler handler_func) except -1
cdef api int DpContext_PopHnadler(object ctx, object hdl) except -1
cdef api int DpContext_InsertV(const char* format, va_list ap) except -1
cdef api int DpContext_Insert(const char* format, ...) except -1
cdef api int DpContext_AnnotateV(const char* format, va_list ap) except -1
cdef api int DpContext_StartAnnotate() except -1
cdef api int DpContext_EndAnnotate() except -1
cdef api int DpContext_Annotate(const char* format, ...) except -1
cdef api int DpContext_FastAnnotate(const char* cmt) except -1
cdef api int DpContext_Newline(unsigned int n_line) except -1


cdef class McdpContextError(McdpRuntimeError):
    cdef readonly:
        Context context
