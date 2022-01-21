from libc.stdio cimport fopen, fclose, fread, FILE
cimport cython

from functools import partial

from ._typing cimport McdpVar
from .version cimport Version
from .stream cimport Stream, mkdir, chdir, rmtree, copyfile, isdir
from .context cimport set_context_path, get_namespace, get_version
from .context cimport dp_insert as insert, dp_comment as comment, dp_newline as newline, dp_addTag as add_tag
from .context cimport StackCache, _stack, Context, Handler, TagManager

from .config import get_config
from .variable import Scoreboard
from .entities import Entity


cdef:
    dict _func_collections = {}
    BaseCompilter compilter


cdef void init_mcmeta(str desc, Version version) except *:
    cdef dict content
    cdef Stream s = Stream("path.mcmeta")
    s.open()
    try:
        content = {
            "pack": {
                "pack_format": get_version(version),
                "description": desc
            }
        }
        s.dump(content)
    finally:
        s.close()

cdef void create_iron(str path) except *:
    cdef:
        bytes p = path.encode()
        int _sc
    _sc = copyfile(p, "pack.png")
    if _sc == -2:
        raise MemoryError
    if _sc == -1:
        raise OSError("fail to copy file")

cdef str get_func_name(str func_name, str space):
    if not space or space == '.':
        return func_name
    else:
        return "%s.%s" % (space, func_name)

cpdef void pull() except *:
    compilter.pull()

cpdef void push() except *:
    compilter.push()


cdef class FunctionHandler(Handler):
    cdef bytes __name__
    cdef readonly:
        __func__

    def __init__(self, func):
        self.__func__ = func
        self.__name__ = (<str>(func.__name__)).encode()
        super().__init__("Function")
    
    cpdef void init(self):
        cdef bytes buffer = b"Library function %S of Mcdp." % self.__name__
        comment(buffer)
        newline(1)


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

        _stack._append(cnt)
        try:
            doc = self.__func__.__doc__
            if doc:
                buffer = doc.encode()
                comment(buffer)
            self.__func__()
            if self.create_frame:
                compilter.push()
        finally:
            _stack._pop()
    
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


def lib_func(str space = "Libs") -> Callable[[Callable[[], None ]], Function]:
    return partial(Function, space=space)


cdef class BaseCompilter:
    cdef readonly:
        config

    def __init__(self, config = None):
        global compilter
        if not config:
            config = get_config()
        self.config = config
        set_context_path(<str>config.namespace)
        compilter = self
    
    cpdef void build_dirs(self) except *:
        cdef:
            config = self.config
            bytes btmp
            char* tmp
            int _sc
        btmp = (<str>(config.name)).encode()
        tmp = <char*>btmp
        if isdir(tmp):
            if config.remove_old_pack:
                _sc = rmtree(tmp)
                if _sc == -1:
                    raise OSError("invalid path")
                elif _sc == -2:
                    raise MemoryError
                elif _sc == -3:
                    raise OSError("fail to remove old package")
        else:
            mkdir(tmp)
        _sc = chdir(tmp)
        if _sc != 0:
            raise OSError("fail to chdir")

        init_mcmeta(<str>config.description, config.version)
        if config.iron_path:
            create_iron(config.iron_path)
        mkdir("data")
        _sc = chdir("data")
        if _sc != 0:
            raise OSError("fail to chdir")

        btmp = (<str>config.namespace).encode()
        mkdir("minecraft")
        mkdir(btmp)
    
    cdef void enter(self) except *:
        self.build_dirs()
        
        cdef Context base = Context("__init__", hdls=Handler("__init__"))
        _stack._append(base)
        comment("This is the initize function.")
        newline(2)
        add_tag("minecraft:load")
        __init_score__()
    
    cdef void exit(self):
        Function.apply_all()
        TagManager.apply_all()
        _stack._clear()

    @staticmethod
    def pull():
        raise NotImplementedError

    @staticmethod
    def push():
        raise NotImplementedError
    
    def __enter__(self):
        self.enter()
        return self

    def __exit__(self, *args):
        self.exit()


@lib_func(None)
def __init_score__():
    """Init the scoreboard."""
    Scoreboard.apply_all()