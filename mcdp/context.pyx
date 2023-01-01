cimport cython
from cpython cimport PyCapsule_New, PyCapsule_CheckExact, PyCapsule_GetPointer, PyErr_Format
from libc.string cimport strcpy


cdef extern from *:
    """
    #define MAX_NEWLINE 5
    const char buffer_newline[MAX_NEWLINE + 1] = "\\n\\n\\n\\n\\n";
    """
    const int MAX_NEWLINE
    const char* buffer_newline


cdef:
    bytes file_suffix = b".mcfunction"
    Context _current = None
    Handler _default_handler = None
    ContextConfig _config = ContextConfig(8, 128, True)


cdef bytes _nspp_funcpath(BaseNamespace nsp):
    return nsp.n_path + b"/functions"

DpNamespace_Property("funcpath", <T_property>_nspp_funcpath)


cdef class Handler:
    def __init__(self, Handler next_hdl = None):
        self.next = next_hdl
    
    cpdef object do_handler(self, Context ctx, object code):
        return self.next_handler(ctx, code)
    
    cpdef object next_handler(self, Context ctx, object code):
        if self.next is None:
            return code
        return self.next.do_handler(ctx, code)
    
    cpdef void append(self, Handler nxt):
        while not self.next is None:
            self = self.next
        self.next = nxt
    
    @cython.nonecheck(True)
    cpdef Handler link_handler(self, Handler header):
        header.append(self)
        return header

    cpdef Handler pop_handler(self, Handler header):
        while header != self:
            if header is None:
                raise TypeError("argument 'header' should be Handler, not NoneType")
            header = header.pop_handler(header)
            if not self in header:
                return header
        return self.next
    
    def __contains__(self, hdl):
        while self:
            if self == hdl:
                return True
            self = self.next
        return False
    
    def __call__(self, code, *, Context ctx = None):
        if ctx is None:
            ctx = <Context>DpContext_Get()
        return self.do_handler(ctx, code)

    def __iter__(self):
        return HandlerIter(self)
    
    def __repr__(self):
        if self.next is None:
            return PyUnicode_FromFormat("<%s object at %p>", Py_TYPE_NAME(self), <void*>self)
        return PyUnicode_FromFormat("<%s object linked <%s object at %p> at %p>", Py_TYPE_NAME(self), Py_TYPE_NAME(self.next), <void*>self.next, <void*>self)


cdef class _CHandlerMeta(type):
    """
    Meta class for handlers with C functions

    DO NOT DIRECTLY USE THIS CLASS IN PYTHON!
    """
    cdef void set_handler(self, T_handler hdl_func):
        DpHandlerMeta_SetHandler(self, hdl_func)
    
    cdef void set_link(self, T_connect lk_func):
        DpHandlerMeta_SetLinkHandler(self, lk_func)
    
    cdef void set_pop(self, T_connect pop_func):
        DpHandlerMeta_SetPopHandler(self, pop_func)
        
    @property
    def valid(self):
        return not self.handler_func is None


cdef class _CHandler(Handler):
    """
    Base class for handlers with C functions

    DO NOT DIRECTLY USE THIS CLASS IN PYTHON!
    """

    cpdef object do_handler(self, Context ctx, object code):
        cdef _CHandlerMeta cls = type(self)
        if cls.handler_func is None:
            raise ValueError("C function of the handler is unset")
        cdef T_handler f_hdl = <T_handler>PyCapsule_GetPointer(self.handler_func, "dp_handler")
        return f_hdl(ctx, code, self.next)
    
    cpdef Handler link_handler(self, Handler header):
        cdef _CHandlerMeta cls = type(self)
        if cls.link_func is None:
            header.append(self)
            return header
        cdef T_connect f_lnk = <T_connect>PyCapsule_GetPointer(self.link_func, "dp_link_handler")
        return f_lnk(self, header)
        
    cpdef Handler pop_handler(self, Handler header):
        cdef _CHandlerMeta cls = type(self)
        if cls.pop_func is None:
            return Handler.pop_handler(self, header)
        cdef T_connect f_pop = <T_connect>PyCapsule_GetPointer(self.pop_func, "dp_pop_handler")
        return f_pop(self, header)


cdef class AnnotateHandler(Handler):
    cpdef object do_handler(self, Context ctx, object code):
        if not _config.use_annotates:
            return

        code = self.next_handler(ctx, code)

        cdef str s = str(code)
        if s.startswith('#'):
            return s
        else:
            return "# " + s
    
    cpdef Handler link_handler(self, Handler header):
        if header is None:
            raise TypeError("argument 'header' should be Handler, not NoneType")
        nxt = self.next
        if not nxt is None:
            self.next = nxt.link_handler(header)
        else:
            self.next = header
        self.link_count += 1
        return self
    
    cpdef Handler pop_handler(self, Handler header):
        if not self == header:
            raise McdpContextError("invalid handler chain")
        if self.link_count > 0:
            if self.next is None:
                raise TypeError("link counter unmatch")
            self.next = self.next.pop_handler(header.next)
            self.link_count -= 1
            return self
        else:
            return self.next


cdef class HandlerIter:
    def __cinit__(self, Handler hdl):
        self.cur = hdl
    
    def __iter__(self):
        return self
    
    def __next__(self):
        hdl = self.cur
        if hdl is None:
            raise StopIteration
        self.cur = hdl.next
        return hdl
            

cdef class Context(McdpObject):
    def __cinit__(
            self,
            str name not None,
            Context back = None,
            *,
            BaseNamespace namespace = None,
            Handler hdl_chain = None
        ):
        self.name = name
        self.namespace = namespace
        self.length = 1
        self.handler_chain = hdl_chain
        if not back is None:
            DpContext_SetBack(self, back)
        elif not namespace is None:
            self.init_stream()
    
    cpdef void set_back(self, Context back) except *:
        if back is None:
            raise TypeError("argument 'back' should be Handler, not NoneType")
        self.back = back
        self.length = back.length + 1
        if self.length > _config.max_stack:
            raise McdpRuntimeError("stack overflow")
        if self.namespace is None:
            self.namespace = back.namespace
        # if self.handler_chain is None:
        #     self.handler_chain = back.handler_chain
        # elif not back.handler_chain is None:
        #     self.handler_chain = back.handler_chain.link_handler(self.handler_chain)
        self.init_stream()
    
    cdef void init_stream(self) except *:
        if not self.stream is None:
            self.stream.close()
        self.stream = Stream(
            self.name.encode() + file_suffix, root=self.namespace.n_funcpath)

    cpdef void join(self) except *:
        self.set_back(<Context>DpContext_Get())
    
    cpdef void activate(self) except *:
        global _current
        if self.stream is None:
            raise McdpUnboundError("context '%s' is activated before init" % self.name)
        self.stream.open()
        _current = self

        for _ in range(_config.max_open):
            self = self.back
            if self is None:
                break
        else:
            self.stream.close()
    
    cpdef void reactivate(self) except *:
        global _current
        if self.stream is None:
            raise McdpUnboundError("context '%s' is activated before init" % self.name)
        self.stream.open("a")
        _current = self
    
    cpdef void deactivate(self) except *:
        if not _current is self:
            raise McdpContextError("incurrect context stat detected")
        self.stream.close()
        if not self.back is None:
            self.back.reactivate()
    
    cpdef bint writable(self):
        if self.stream is None:
            return False
        return self.stream.writable()
    
    cpdef void put(self, object code) except *:
        if not self.writable():
            PyErr_Format(McdpContextError, "context %U is not writable", <PyObject*>self.name)
        if not self.handler_chain is None:
            code = self.handler_chain.do_handler(self, code)
        self.stream.putln((<str>str(code)).encode())
    
    cpdef list get_handler(self):
        if self.handler_chain is None:
            return []
        return list(self.handler_chain)
    
    cpdef void add_handler(self, Handler hdl) except *:
        if self.handler_chain is None:
            self.handler_chain = hdl
        else:
            self.handler_chain = self.handler_chain.link_handler(hdl)
    
    cpdef void pop_handler(self, Handler hdl = None) except *:
        if self.handler_chain is None:
            raise McdpContextError("no handler has been set")
        if hdl is None:
            hdl = self.handler_chain
        self.handler_chain = hdl.pop_handler(self.handler_chain)
    
    def __len__(self):
        return self.length
    
    def __enter__(self):
        if self.stream is None:
            self.join()
        self.activate()
        return self
    
    def __exit__(self, exc_type, exc_obj, traceback):
        self.deactivate()
    
    def __repr__(self):
        if self.namespace is None:
            return PyUnicode_FromFormat("<context %U unbound at %p>", <void*>self.name, <void*>self)
        return PyUnicode_FromFormat("<context %U in namespace %U at %p>", <void*>self.name, <void*>self.namespace.n_name, <void*>self)


cdef class _AnnotateImpl:
    """
    Magic method implement class for context.annotate

    Usage:

        @namespace.mcfunc
        def test_annotate(frame: Frame) -> None:

            # as function
            annotate(
                "This is a test function.",
                "Use `annotate()` to add annotates."
            )

            # as context manager
            with annotate:
                insert("In this case, use `insert()` instead of `annotate()`.")
                frame.var_int = 5
                frame.var_int += 2      # This part of compiled mc command will turn into annotates too.

    """
    
    def __cinit__(self):
        self.__name__ = "annotate"
        self.__qualname__ = "mcdp.context.annotate"
    
    cpdef bint ensure(self) except -1:
        cdef Context ctx = <Context>DpContext_Get()
        return ctx.handler_chain == self.cmt_hdl

    cdef void enter_annotate(self) except *:
        cdef Context ctx = <Context>DpContext_Get()
        self.cmt_hdl = AnnotateHandler()
        ctx.add_handler(self.cmt_hdl)
    
    cdef void exit_annotate(self) except *:
        cdef Context ctx = <Context>DpContext_Get()
        ctx.pop_handler(self.cmt_hdl)
    
    @property
    def handler(self):
        if not self.ensure():
            raise McdpContextError("not in annotate environment")
        return self.cmt_hdl
    
    def __enter__(self):
        self.enter_annotate()
        return self.cmt_hdl
    
    def __exit__(self, exc_type, exc_obj, traceback):
        self.exit_annotate()
    
    def __call__(self, *annotates):
        if not _config.use_annotates:
            return
        elif self.ensure():
            return insert(*annotates)

        cdef:
            Context ctx = <Context>DpContext_Get()
            AnnotateHandler cmt_hdl = AnnotateHandler()

        ctx.add_handler(cmt_hdl)
        try:
            insert(*annotates)
        finally:
            ctx.pop_handler(cmt_hdl)
    
    def __repr__(self):
        return PyUnicode_FromFormat("annotate environment at %p", <void*>self)


def init_context(BaseNamespace nsp):
    return <object>DpContext_Initalize(nsp)

def finalize_context():
    DpContext_Finalize()


def get_context():
    return <Context>DpContext_Get()


def insert(*codes):
    cdef Context ctx = <Context>DpContext_Get()
    for i in codes:
        if isinstance(i, str):
            for j in (<str>i).split('\n'):
                ctx.put(j)
        else:
            ctx.put(i)


def newline(unsigned int n_line = 1):
    DpContext_Newline(n_line)


def _get_ctx_config():
    return <dict>_config


def _set_ctx_config(**kwds):
    _config.use_annotates = kwds.pop("use_annotates", _config.use_annotates)
    _config.max_open = kwds.pop("max_open", _config.max_open)
    _config.max_stack = kwds.pop("max_stack", _config.max_stack)
    for k in kwds:
        PyErr_Format(
            TypeError,
            "_set_ctx_config() got an unexpected keyword argument '%U'",
            <PyObject*>k
        )


cdef _AnnotateImpl _annotate = _AnnotateImpl()
annotate = _annotate


"""
Context C API
-----------------------------------
"""

# Handler API
cdef _CHandlerMeta DpHandlerMeta_New(const char* name, T_handler handler_func):
    cdef _CHandlerMeta hdl_cls = _CHandlerMeta(name.decode(), (_CHandler,), {})
    DpHandlerMeta_SetHandler(hdl_cls, handler_func)

cdef void DpHandlerMeta_SetHandler(_CHandlerMeta cls, T_handler func):
    cls.handler_func = PyCapsule_New(func, "dp_handler", NULL)

cdef void DpHandlerMeta_SetLinkHandler(_CHandlerMeta cls, T_connect func):
    cls.link_func = PyCapsule_New(func, "dp_link_handler", NULL)

cdef void DpHandlerMeta_SetPopHandler(_CHandlerMeta cls, T_connect func):
    cls.pop_func = PyCapsule_New(func, "dp_pop_handler", NULL)

cdef object DpHandler_FromMeta(_CHandlerMeta cls, object next_hdl):
    return cls(next_hdl)

cdef object DpHandler_NewSimple(const char* name, T_handler handler_func):
    return DpHandler_FromMeta(DpHandlerMeta_New(name, handler_func), None)

cdef PyObject* DpHandler_GetNext(object hdl) except NULL:
    return <PyObject*>(<Handler?>hdl).next

cdef object DpHandler_DoHandler(object hdl, object ctx, object code):
    if hdl is None:
        return code
    return (<Handler?>hdl).do_handler(ctx, code)


# Context API
cdef PyObject* DpContext_Initalize(object nsp) except NULL:
    global _current
    if not _current is None:
        raise McdpContextError("cannot reinitalize the context")
    _current = Context("__init__", namespace=nsp, hdl_chain=_default_handler)
    return <PyObject*>_current

cdef PyObject* DpContext_Get() except NULL:
    if _current is None:
        raise McdpInitalizeError("the context has not been initalized")
    return <PyObject*>_current

cdef object DpContext_New(const char* name):
    return Context(name.decode())

cdef PyObject* DpContext_GetBack(object ctx) except NULL:
    return <PyObject*>(<Context?>ctx).back

cdef int DpContext_SetBack(object ctx, object back) except -1:
    Context.set_back(ctx, back)
    return 0

cdef int DpContext_Join(object ctx) except -1:
    Context.join(ctx)
    return 0

cdef bint DpContext_Writable(object ctx) except -1:
    return (<Context?>ctx).writable()

cdef int DpContext_Activate(object ctx) except -1:
    Context.activate(ctx)
    return 0
    
cdef int DpContext_Reactivate(object ctx) except -1:
    Context.reactivate(ctx)
    return 0
    
cdef int DpContext_Deactivate(object ctx) except -1:
    Context.deactivate(ctx)
    return 0

cdef int DpContext_Finalize() except -1:
    global _current
    if _current is None:
        raise McdpContextError("cannot finalized the context before its initalization")
    elif _current.name != "__init__":
        PyErr_Format(McdpContextError, "context finalized on incurrect context %U", <void*>_current.name)
    _current.deactivate()
    _current = None
    return 0

cdef int DpContext_AddHnadler(object ctx, object hdl) except -1:
    Context.add_handler(ctx, hdl)
    return 0

cdef int DpContext_AddHandlerSimple(object ctx, T_handler handler_func) except -1:
    cdef Handler hdl = <Handler>DpHandler_NewSimple("mcdp.context.CHandler", handler_func)
    return DpContext_AddHnadler(ctx, hdl)

cdef int DpContext_PopHnadler(object ctx, object hdl) except -1:
    Context.pop_handler(ctx, hdl)
    return 0

cdef int DpContext_InsertV(const char* format, va_list ap) except -1:
    cdef Context ctx = <Context>DpContext_Get()
    code = PyUnicode_FromFormatV(format, ap)
    ctx.put(code)
    return 0

cdef int DpContext_Insert(const char* format, ...) except -1:
    cdef va_list ap
    va_start(ap, format)
    try:
        DpContext_InsertV(format, ap)
    finally:
        va_end(ap)
    return 0

cdef int DpContext_StartAnnotate() except -1:
    _annotate.enter_annotate()
    return 0

cdef int DpContext_EndAnnotate() except -1:
    _annotate.exit_annotate()
    return 0

cdef int DpContext_AnnotateV(const char* format, va_list ap) except -1:
    if not _config.use_annotates:
        return 0
    cdef Context ctx = <Context>DpContext_Get()

    code = PyUnicode_FromFormatV(format, ap)
    _annotate.enter_annotate()
    try:
        ctx.put(code)
    finally:
        _annotate.exit_annotate()
    return 0

cdef int DpContext_Annotate(const char* format, ...) except -1:
    cdef va_list ap
    va_start(ap, format)
    try:
        DpContext_AnnotateV(format, ap)
    finally:
        va_end(ap)
    return 0

cdef int DpContext_FastAnnotate(const char* cmt) except -1:
    if not _config.use_annotates:
        return 0

    cdef:
        Context top = <Context>DpContext_Get()
        char buffer[129]
        int i = 2
    strcpy(buffer, "# ")
    while cmt[0]:
        if cmt[0] == ord('\n'):
            if i > 123:
                buffer[i] = 0
                top.stream.put(buffer)
                i = 0
            strcpy(buffer + i, "\n# ")
            i += 3
        else:
            if i > 126:
                buffer[i] = 0
                top.stream.put(buffer)
                i = 0
            buffer[i] = cmt[0]
            i += 1
        cmt += 1
    buffer[i] = ord('\n')
    buffer[i+1] = 0
    top.stream.put(buffer)
    return 0

cdef int DpContext_Newline(unsigned int n_line) except -1:
    if not _config.use_annotates:
        return 0
    cdef Context ctx = <Context>DpContext_Get()
    while n_line > MAX_NEWLINE:
        ctx.stream.put(buffer_newline)
        n_line -= MAX_NEWLINE
    ctx.stream.put(buffer_newline - n_line + MAX_NEWLINE)


cdef class McdpContextError(McdpRuntimeError):
    def __init__(self, *arg: str) -> None:
        self.context = <Context>DpContext_Get()
        super().__init__(*arg)
