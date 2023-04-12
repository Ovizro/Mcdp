from libc.stdint cimport uint32_t
from libc.stdio cimport sprintf


cdef class CommandExecuter:
    cdef readonly:
        Execute execobj
        object command
    
    def __cinit__(self, execobj not None, command not None):
        self.execobj = <Execute>DpExecute_FromObject(execobj)
        self.command = command
    
    def __iter__(self):
        return iter((self.execobj, self.command))
    
    def __str__(self):
        return self.execobj.as_prefix(True) + <str>str(self.command)


cdef class ExecuteHandler(Handler):
    def __init__(self, Execute execobj not None, Handler next_hdl = None):
        self.execobj = execobj
        self.next = next_hdl

    cpdef object do_handler(self, Context ctx, object code):
        code = CommandExecuter(self.execobj, code)
        return self.next_handler(ctx, code)


cdef class BranchEnvironment:
    def __cinit__(self, execobj not None):
        self.execobj = <Execute>DpExecute_FromObject(execobj)

    cdef void enter(self) except *:
        pass

    cdef void exit(self) except *:
        pass
    
    def __enter__(self):
        self.enter()
        return self
    
    def __exit__(self, *args):
        self.exit()


cdef class condition(BranchEnvironment):
    cdef void enter(self) except *:
        cdef Context ctx = <Context>DpContext_Get()
        self.ctx = <Context>DpControlFlowBranch_New()
        self.ctx.set_back(ctx)
        prefix = self.execobj.as_prefix(True)
        DpContext_Insert("%Ufunction %U:%U", <void*>prefix, <void*>self.ctx.namespace.n_name, <void*>self.ctx.name)
        self.ctx.activate()
        DpContext_StartAnnotate()
        try:
            DpContext_Insert("control flow branch of 'Case Environment'")
            DpContext_Insert("from %U", <void*>ctx.name)
            DpContext_Newline(1)
        finally:
            DpContext_EndAnnotate()

    cdef void exit(self) except *:
        self.ctx.deactivate()


cdef class inline_condition(BranchEnvironment):
    cdef void enter(self) except *:
        cdef Context ctx = <Context>DpContext_Get()
        self.hdl = ExecuteHandler(self.execobj)
        ctx.add_handler(self.hdl)
    
    cdef void exit(self) except *:
        cdef Context ctx = <Context>DpContext_Get()
        ctx.pop_handler(self.hdl)


cdef class while_loop(BranchEnvironment):
    cdef void enter(self) except *:
        cdef Context ctx = <Context>DpContext_Get()
        self.ctx = <Context>DpControlFlowBranch_New()
        self.ctx.set_back(ctx)
        prefix = self.execobj.as_prefix(True)
        DpContext_Insert("%Ufunction %U:%U", <void*>prefix, <void*>self.ctx.namespace.n_name, <void*>self.ctx.name)
        self.ctx.activate()
        DpContext_StartAnnotate()
        try:
            DpContext_Insert("control flow branch of 'Case Environment'")
            DpContext_Insert("from %U", <void*>ctx.name)
            DpContext_Newline(1)
        finally:
            DpContext_EndAnnotate()

    cdef void exit(self) except *:
        prefix = self.execobj.as_prefix(True)
        DpContext_Insert("%Ufunction %U:%U", <void*>prefix, <void*>self.ctx.namespace.n_name, <void*>self.ctx.name)
        self.ctx.deactivate()

    
cdef uint32_t cfb_counter = 0

cdef object DpControlFlowBranch_New():
    global cfb_counter
    cdef:
        char name[15]
        Context ctx
    if cfb_counter > 0xFFFFFF:
        raise McdpRuntimeError("control flow branch size overflow")
    sprintf(name, "__cfb__/%04X", cfb_counter)
    ctx = Context(name.decode())
    cfb_counter += 1
    return ctx

cdef object Dp_If(object case):
    return condition(case)

cdef object Dp_InlineIf(object case):
    return inline_condition(case)

cdef object Dp_While(object case):
    return while_loop(case)