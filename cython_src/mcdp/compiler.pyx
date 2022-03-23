from libc.stdio cimport fopen, fclose, fread, FILE
cimport cython

from ._typing cimport McdpVar, McdpError
from .version cimport Version
from .stream cimport Stream, mkdir, chdir, rmtree, copyfile, isdir
from .context cimport (init_namespace, get_version, _envs, Context, TagManager,
                dp_insert as insert, dp_comment as comment, dp_commentline as commentline, dp_newline as newline, 
                dp_fastAddTag as add_tag, dp_fastEnter as enter_context)

from .config import get_config
from .mcfunc import Function, __init_score__


cdef Compilter compilter


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

cdef void create_icon(str path) except *:
    cdef:
        bytes p = path.encode()
        int _sc
    _sc = copyfile(p, "pack.png")
    if _sc == -2:
        raise MemoryError
    if _sc == -1:
        raise OSError("fail to copy file")


cdef class Compilter:
    cdef readonly:
        config

    def __init__(self, config = None):
        global compilter
        if not config:
            config = get_config()
        self.config = config
        init_namespace(<str>config.namespace)
        compilter = self
    
    cpdef void build_dirs(self) except *:
        cdef:
            pack = self.config.package
            bytes btmp
            char* tmp
            int _sc
        btmp = (<str>(pack.name)).encode()
        tmp = <char*>btmp
        if isdir(tmp):
            if pack.remove_old_pack:
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

        init_mcmeta(<str>pack.description, pack.support_version)
        if pack.icon_path:
            create_icon(pack.icon_path)
        mkdir("data")
        _sc = chdir("data")
        if _sc != 0:
            raise OSError("fail to chdir")

        btmp = (<str>pack.namespace).encode()
        mkdir("minecraft")
        mkdir(btmp)
    
    cdef void enter(self) except *:
        self.build_dirs()
        
        enter_context("__init__")
        comment("This is the initize function.")
        newline(2)
        add_tag("minecraft:load")
        __init_score__()
    
    cdef void exit(self):
        Function.apply_all()
        TagManager.apply_all()
        _envs._clear()

    def __enter__(self):
        self.enter()
        return self

    def __exit__(self, *args):
        self.exit()


cdef list _init_list = []


cpdef inline mcdp_init(func):
    _init_list.append(func)
    return func