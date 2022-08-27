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
    
    @cython.nonecheck(True)
    cpdef Handler pop_handler(self, Handler header):
        while header != self:
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
            return PyUnicode_FromFormat("<%s object at %p>", get_type_name(self), <void*>self)
        return PyUnicode_FromFormat("<%s object linked <%s object at %p> at %p>", get_type_name(self), get_type_name(self.next), <void*>self.next, <void*>self)


cdef class _CHandlerMeta(type):
    cdef void set_handler(self, T_handler hdl_func):
        self.handler_func = PyCapsule_New(hdl_func, "dp_handler", NULL)
    
    cdef void set_link(self, T_connect lk_func):
        self.link_func = PyCapsule_New(lk_func, "dp_link_handler", NULL)
    
    cdef void set_pop(self, T_connect pop_func):
        self.pop_func = PyCapsule_New(pop_func, "dp_pop_handler", NULL)
        
    @property
    def valid(self):
        return not self.handler_func is None


cdef class _CHandler(Handler):
    def __init__(self, Handler next_handler = None):
        raise NotImplementedError

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


cdef class CommentHandler(Handler):
    cpdef object do_handler(self, Context ctx, object code):
        if not _config.use_comments:
            return

        code = self.next_handler(ctx, code)

        cdef str s = str(code)
        if s.startswith('#'):
            return s
        else:
            return "# " + s
    
    cpdef Handler link_handler(self, Handler header):
        if header is None:
            PyErr_Format(ValueError, "argument 'header' should be Handler, not NoneType")
        nxt = self.next
        if not nxt is None:
            self.next = nxt.link_handler(header)
        else:
            self.next = header
        self.link_count += 1
        return self
    
    @cython.nonecheck(True)
    cpdef Handler pop_handler(self, Handler header):
        if not self == header:
            raise McdpContextError("invalid handler chain")
        if self.link_count > 0:
            self.next = self.next.pop_handler(header.next)
            self.link_count -= 1
            return self
        else:
            return self.next


cdef class HandlerIter:
    def __init__(self, Handler hdl):
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
    def __init__(
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
            self.set_back(back)
        elif not namespace is None:
            self.init_stream()
    
    @cython.nonecheck(True)
    cpdef void set_back(self, Context back) except *:
        self.back = back
        self.length = back.length + 1
        if self.length > _config.max_stack:
            raise McdpRuntimeError("stack overflow")
        if self.namespace is None:
            self.namespace = back.namespace
        if self.handler_chain is None:
            self.handler_chain = back.handler_chain
        elif not back.handler_chain is None:
            self.handler_chain = back.handler_chain.link_handler(self.handler_chain)
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
            raise McdpContextError(f"context {self.name} is not writable")
        if not self.handler_chain is None:
            code = self.handler_chain.do_handler(self, code)
        if not code is None:
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


cdef class _CommentImpl:
    """
    Magic method implement class for context.comment

    Usage:

        @namespace.mcfunc
        def test_comment(frame: Frame) -> None:

            # as function
            comment(
                "This is a test function.",
                "Use `comment()` to add comments."
            )

            # as context manager
            with comment:
                insert("In this case, use `insert()` instead of `comment()`.")
                frame.var_int = 5
                frame.var_int += 2      # This part of compiled mc command will turn into comments too.

    """
    
    def __init__(self):
        self.__name__ = "comment"
        self.__qualname__ = "mcdp.context.comment"
    
    cpdef bint ensure(self) except -1:
        cdef Context ctx = <Context>DpContext_Get()
        return ctx.handler_chain == self.cmt_hdl

    cdef void enter_comment(self) except *:
        cdef Context ctx = <Context>DpContext_Get()
        self.cmt_hdl = CommentHandler()
        ctx.add_handler(self.cmt_hdl)
    
    cdef void exit_comment(self) except *:
        cdef Context ctx = <Context>DpContext_Get()
        ctx.pop_handler(self.cmt_hdl)
    
    @property
    def handler(self):
        if not self.ensure():
            raise McdpContextError("not in comment environment")
        return self.cmt_hdl
    
    def __enter__(self):
        self.enter_comment()
        return self.cmt_hdl
    
    def __exit__(self, exc_type, exc_obj, traceback):
        self.exit_comment()
    
    def __call__(self, *comments):
        if not _config.use_comments:
            return
        elif self.ensure():
            return insert(*comments)

        cdef:
            Context ctx = <Context>DpContext_Get()
            CommentHandler cmt_hdl = CommentHandler()

        ctx.add_handler(cmt_hdl)
        try:
            insert(*comments)
        finally:
            ctx.pop_handler(cmt_hdl)


def init_context(BaseNamespace nsp):
    global _current
    _current = Context("__init__", namespace=nsp, hdl_chain=_default_handler)
    return _current


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
    _config.use_comments = kwds.pop("use_comments", _config.use_comments)
    _config.max_open = kwds.pop("max_open", _config.max_open)
    _config.max_stack = kwds.pop("max_stack", _config.max_stack)
    if kwds:
        raise TypeError(
            "_set_ctx_config() got an unexpected keyword argument '%s'" % kwds.popitem()[0]
        )


comment = _CommentImpl()


"""
Context C API
-----------------------------------
"""

# Handler API
cdef _CHandlerMeta DpHandlerMeta_New(const char* name, T_handler handler_func):
    cdef _CHandlerMeta hdl_cls = _CHandlerMeta(
        name.decode(), (_CHandler,), {"__init__": Handler.__init__})
    hdl_cls.set_handler(handler_func)

cdef void DpHandlerMeta_SetHandler(_CHandlerMeta cls, T_handler func):
    cls.set_handler(func)

cdef void DpHandlerMeta_SetLinkHandler(_CHandlerMeta cls, T_connect func):
    cls.set_link(func)

cdef void DpHandlerMeta_SetPopHandler(_CHandlerMeta cls, T_connect func):
    cls.set_pop(func)

cdef object DpHandler_FromMeta(_CHandlerMeta cls, object next_hdl):
    return cls(next_hdl)

cdef object DpHandler_NewSimple(const char* name, T_handler handler_func):
    return DpHandler_FromMeta(DpHandlerMeta_New(name, handler_func), None)

cdef object DpHandler_DoHandler(object hdl, object ctx, object code):
    if hdl is None:
        return code
    return (<Handler?>hdl).do_handler(ctx, code)


# Context API
cdef PyObject* DpContext_Get() except NULL:
    if _current is None:
        raise McdpContextError("fail to get context")
    return <PyObject*>_current

cdef PyObject* DpContext_Getback(object ctx) except NULL:
    return <PyObject*>(<Context?>ctx).back

cdef object DpContext_New(const char* name):
    return Context(name.decode())

cdef int DpContext_Join(object ctx) except -1:
    (<Context?>ctx).join()
    return 0

cdef int DpContext_AddHnadler(object ctx, object hdl) except -1:
    (<Context?>ctx).add_handler(hdl)
    return 0

cdef int DpContext_AddHandlerSimple(object ctx, T_handler handler_func) except -1:
    cdef Handler hdl = <Handler>DpHandler_NewSimple("mcdp.context.CHandler", handler_func)
    return DpContext_AddHnadler(ctx, hdl)

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

cdef int DpContext_CommentV(const char* format, va_list ap) except -1:
    if not _config.use_comments:
        return 0
    cdef Context ctx = <Context>DpContext_Get()
    cdef _CommentImpl cmt = <_CommentImpl>comment

    code = PyUnicode_FromFormatV(format, ap)
    cmt.enter_comment()
    try:
        ctx.put(code)
    finally:
        cmt.exit_comment()
    return 0

cdef int DpContext_Comment(const char* format, ...) except -1:
    cdef va_list ap
    va_start(ap, format)
    try:
        DpContext_CommentV(format, ap)
    finally:
        va_end(ap)
    return 0

cdef int DpContext_FastComment(const char* cmt) except -1:
    if not _config.use_comments:
        return 0

    cdef:
        Context top = <Context>DpContext_Get()
        char buffer[129]
        int i = 2
    strcpy(buffer, "# ")
    while cmt[0]:
        if cmt[0] == ord('\n'):
            if i > 123:
                top.stream.put(buffer)
                i = 0
            strcpy(buffer + i, "\n# ")
            i += 3
        else:
            if i > 126:
                top.stream.put(buffer)
                i = 0
            buffer[i] = cmt[0]
            i += 1
        cmt += 1
    buffer[i] = ord('\n')
    buffer[i+1] = ord('\0')
    top.stream.put(buffer)
    return 0

cdef int DpContext_Newline(unsigned int n_line) except -1:
    if not _config.use_comments:
        return 0
    cdef Context ctx = <Context>DpContext_Get()
    while n_line > MAX_NEWLINE:
        ctx.stream.put(buffer_newline)
        n_line -= MAX_NEWLINE
    ctx.stream.put(buffer_newline - n_line + MAX_NEWLINE)


cdef class McdpContextError(McdpError):
    def __init__(self, *arg: str) -> None:
        self.context = <Context>DpContext_Get()
        super().__init__(*arg)