import warnings
from collections import defaultdict
from functools import wraps

from .typing cimport McdpVar, McdpError
from .typing import McdpVar, McdpError
from .stream cimport Stream
from .stream import Stream
from .config import get_config, get_version


cdef:
    int MAX_OPEN = 8
    str CONTEXT_PATH


cdef class StackCache(list):
    cdef int _capacity

    def __init__(self, int capacity = 12):
        if not (1 < capacity <= 128):
            raise ValueError(
                    f"expect the capacity ranging from 2 to 128, but get {capacity}"
            )
        self._capacity = capacity
        super().__init__()
    
    cpdef void append(self, Context env):
        super().append(env)
        env.activate()
        overflow = len(self) - self._capacity
        if overflow > 0:
            for e in self[:overflow]:
                e.deactivate()
    
    cpdef Context pop(self):
        cdef Context last = super().pop()
        last.deactivate()
        if self and not self[-1].writable():
            self[-1].activate(True)
        return last

    cpdef void clear(self):
        cdef Context e
        for e in self:
            e.deactivate()
        super().clear()


cdef class EnvMethod:
    """
    Use the class as a decorator to
    announce a environment method.
    
    When called from the instance, the method works 
    as a normal method. And when it is called from the 
    class, the param 'self' will input <class>.current as 
    the instance.
    """

    cdef __func__

    def __init__(self, func: Callable):
        self.__func__ = func

    def __get__(self, instance, owner) -> Callable:
        if instance is None:
            instance = owner.top
            if not instance:
                raise McdpContextError("invalid current context")

        @wraps(self.__func__)
        def wrapper(*args, **kw):
            return self.__func__(instance, *args, **kw)

        return wrapper


cdef class EnvProperty(EnvMethod):

    def __get__(self, instance, owner) -> Any:
        return self.__func__(owner)


cdef class ContextEnv(McdpVar):
    cdef readonly:
        str env_type
    
    env_counter = defaultdict(lambda: 0)

    def __init__(self, str env_type):
        self.env_type = env_type
    
    cpdef void init(self):
        config = get_config()
        comment(
            "Datapack %s built by Mcdp." % config.name,
            "Supported Minecraft version: %s(%s)" % (config.version, get_version(config.version)),
        )
        newline()
    
    cpdef str decorate_command(self, str cmd):
        return cmd
    
    cpdef Context creat_stream(self):
        cdef str file_name = self.env_type + hex(self.env_counter[self.env_type])
        self.env_counter[self.env_type] += 1
        return Context(file_name, root_path=CONTEXT_PATH, envs=self)


cdef StackCache _stack = StackCache(MAX_OPEN)


cdef class Context(McdpVar):
    cdef readonly:
        str name
        Stream stream
        list environments
    
    stack = _stack
    file_suffix = ".mcfunction"