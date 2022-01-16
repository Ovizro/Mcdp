from libc.stdio cimport fopen, fclose, fread, FILE

from functools import partial

from ._typing cimport McdpVar
from .version cimport Version
from .stream cimport Stream, mkdir, chdir, rmtree, copyfile, isdir
from .context cimport set_context_path, get_namespace, get_version
from .context cimport dp_insert as insert, dp_comment as comment, dp_newline as newline, dp_addTag as add_tag
from .context cimport StackCache, _stack, Context, Handler
from .config import get_config


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
        return space + '/' + func_name


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
    cdef readonly:
        __func__
        str __name__
    
    collections = _func_collections
    
    def __init__(self, func not None, *, str space = None):
        self.__func__ = func
        self.__name__ = get_func_name(<str>func.__name__, space)
        _func_collections[self.__name__] = self
    
    def __call__(self, str namespace = None):
        namespace = namespace or get_namespace()

        cdef str name = self.__name__
        cdef bytes buffer = f"function {namespace}:{name}".encode()
        insert(buffer)
        
    cpdef void apply(self, bint create_frame = False) except *:
        cdef Context cnt = Context(
                self.func.__name__, hdls=FunctionHandler(self.__func__))

        cdef:
            str doc
            bytes buffer
        _stack._append(cnt)
        try:
            if create_frame:
                compilter.pull()
            doc = self.__func__.__doc__
            if doc:
                buffer = doc.encode()
                comment(buffer)
            self.__func__()
            if create_frame:
                compilter.push()
        finally:
            _stack._pop()
    
    @staticmethod
    def apply_all(bint create_frame = False):
        cdef Function func
        for func in _func_collections.values():
            func.apply(create_frame)

    @staticmethod
    cdef void _apply_all(bint create_frame = False) except *:
        cdef Function func
        for func in _func_collections.values():
            func.apply(create_frame)


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
        btmp = (<str>(config.name)).encode()
        tmp = <char*>btmp
        if isdir(tmp):
            if config.remove_old_pack:
                rmtree(tmp)
        else:
            mkdir(tmp)
        cdef int _sc = chdir(tmp)
        if _sc != 0:
            raise OSError("fail to chdir")

        init_mcmeta(<str>config.description, <Version>config.version)
        if config.iron_path:
            create_iron(config.iron_path)
        mkdir("data")
        chdir("data")

        btmp = (<str>config.namespace).encode()
        mkdir("minecraft")
        mkdir(btmp)
    
    cdef void enter(self) except *:
        self.build_dirs()
        
        cdef Context base = Context("__init__", hdls=Handler("__init__"))
        _stack._append(base)
        comment("This is the initize function.")
        newline(2)
    
    cdef void exit(self):
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
    raise NotImplementedError