
from functools import partial

from .frame import enter_stack, leave_stack
from .entities import McdpStack
from .variable import Scoreboard, dp_score, global_var, init_global
from .entities import McdpStack, get_tag


cdef list _func_collections = []


cdef inline str get_func_name(str func_name, str space):
    if not space or space == '.':
        return func_name
    else:
        return "%s.%s" % (space, func_name)


cdef class FunctionContext(Context):
    cdef BaseFunction func

    def __init__(self, BaseFunction func):
        self.func = func
        cdef str name = func.__qualname__.replace('.', '/')
        super().__init__(name)
    
    cpdef void mkhead(self) except *:
        Context.mkhead(self)

        cdef bytes tmp = self.name.encode()
        dp_commentline("Function: %s", <char*>tmp)
        dp_newline(2)



cdef class BaseFunction(McdpVar):
    """
    Base class of function in the mcfunction.

    Attribute:
        flag: Final[int] - Each bit of data is used as:
            0b000101    validation check
                   ^
            0b000101    whether need to apply
                  ^
            0b000101    whether can be called
                 ^
            0b000101    stack mod
               ^^
            0b000101    validation check
              ^
        __name__: str - name of function
        __qualname__: str - name of function with space
    """
    cdef readonly int flag
    cdef public:
        str __name__
        str __qualname__
        object __func__
    
    collections = _func_collections
    
    def __init__(self, str name not None, func, *, str space = None):
        if self.flag ^ VALID_FUNC or self.flag & INVALID_FUNC:
            raise McdpFunctionError("Invalid function flag.")
        self.flag = 0b000101
        
        self.__func__ = func
        self.__name__ = name
        self.__qualname__ = get_func_name(name, space)
        _func_collections.append(self)
    
    def __call__(self):
        if self.flag ^ VALID_FUNC:
            raise McdpFunctionError("Invalid function.")

        cdef:
            str namespace = get_namespace()
            str name = self.__qualname__
            bytes buffer
        if self.flag & 0b010000:
            enter_stack()
            buffer = b"execute as "
        else:
            buffer = f"function {namespace}:{name}".encode()
        dp_insert(buffer)
        if self.flag & USE_STACK and self.flag ^ 0b001000:
            leave_stack()
    
    cpdef void add_space(self, str space):
        self.__qualname__ = "%s.%s" % (space, self.__qualname__)
        
    cpdef void apply(self) except *:
        if self.flag ^ VALID_FUNC:
            raise McdpFunctionError("Invalid function.")
            
        cdef:
            str doc
            bytes buffer

        cdef FunctionContext cxt = FunctionContext(self)
        cxt.enter()

        try:
            doc = self.__func__.__doc__
            if not doc is None:
                buffer = doc.encode()
                dp_comment(buffer)
            if self.flag & USE_STACK and self.flag ^ 0b010000:
                enter_stack()
            self.__func__()
            if self.flag & 0b001000:
                leave_stack()
        finally:
            cxt.exit()
    
    @classmethod
    def apply_all(cls):
        cdef BaseFunction func
        for func in _func_collections:
            func.apply()

    @staticmethod
    cdef void _apply_all() except *:
        cdef BaseFunction func
        for func in _func_collections:
            func.apply()


cdef class LibFunction(BaseFunction):
    ...


def lib_func(str space = "Libs") -> Callable[[Callable[[], None ]], Function]:
    return partial(LibFunction, space=space)


@lib_func(None)
def __init_score__():
    """Init the scoreboard."""
    Scoreboard.apply_all()

cdef class McdpFunctionError(McdpError):
    ...