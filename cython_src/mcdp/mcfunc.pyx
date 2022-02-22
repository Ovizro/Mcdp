cdef dict _func_collections = {}


cdef str get_func_name(str func_name, str space):
    if not space or space == '.':
        return func_name
    else:
        return "%s.%s" % (space, func_name)


cdef class Function(McdpVar):
    cdef int start
    cdef readonly:
        str __name__
        str __qualname__
        bint create_frame
        object __func__
    
    collections = _func_collections
    
    def __init__(self, func not None, *, str space = None, bint create_frame = False):
        self.__func__ = func
        self.__name__ = func.__name__
        self.__qualname__ = get_func_name(self.__name__, space)
        self.create_frame = create_frame
        _func_collections[self.__qualname__] = self
    
    def __call__(self):
        cdef:
            str namespace = get_namespace()
            str name = self.__qualname__
        if self.create_frame:
            pull()
        cdef bytes buffer = f"function {namespace}:{name}".encode()
        insert(buffer)
    
    cpdef void add_space(self, str space):
        self.__qualname__ = "%s.%s" % (space, self.__qualname__)
        
    cpdef void apply(self) except *:
        cdef:
            str path = self.__qualname__
            str doc
            bytes buffer

        path.replace('.', '/')
        cdef Context cnt = Context(
                path, hdls=FunctionHandler(self.__func__))

        _envs._append(cnt)
        try:
            doc = self.__func__.__doc__
            if doc:
                buffer = doc.encode()
                comment(buffer)
            self.__func__()
            if self.create_frame:
                compilter.push()
        finally:
            _envs._pop()
    
    @classmethod
    def apply_all(cls):
        cdef Function func
        for func in _func_collections.values():
            func.apply()

    @staticmethod
    cdef void _apply_all() except *:
        cdef Function func
        for func in _func_collections.values():
            func.apply()


cdef class LibFunction(Function):
    ...


def lib_func(str space = "Libs") -> Callable[[Callable[[], None ]], Function]:
    return partial(Function, space=space)


@lib_func(None)
def __init_score__():
    """Init the scoreboard."""
    Scoreboard.apply_all()


@lib_func()
def enter_stack() -> None:
    global mcdp_stack_id

    top = Selector("@e", "tag=stack_top", tag=get_tag(), limit=1)
    lower = Selector("@e", "tag=lower_stack", tag=get_tag(), limit=1)
    
    lower.remove_tag("lower_stack")
    top.add_tag("lower_stack")
    top.remove_tag("stack_top")

    stack = McdpStack()
    mcdp_stack_id += 1
    

@lib_func()
def leave_stack() -> None:
    global mcdp_stack_id

    top = Selector("@e", "tag=stack_top", tag=get_tag(), limit=1)
    lower = Selector("@e", "tag=lower_stack", tag=get_tag(), limit=1)

    top.remove()
    lower.add_tag("stack_top")
    lower.remove_tag("lower_stack")

    mcdp_stack_id -= 2
    s = dp_score("mcdpStackID", selector=Selector(McdpStack))
    with s == mcdp_stack_id:
        Selector("@s").add_tag("lower_stack")
    mcdp_stack_id += 1