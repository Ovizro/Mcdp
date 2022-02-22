from libc.stdio cimport fopen, fclose, fread, FILE
cimport cython

from functools import partial

from ._typing cimport McdpVar, McdpError
from .version cimport Version
from .stream cimport Stream, mkdir, chdir, rmtree, copyfile, isdir
from .context cimport (set_context_path, get_version, _envs, Context, TagManager,
                dp_insert as insert, dp_comment as comment, dp_newline as newline, 
                dp_fastAddTag as add_tag, dp_fastEnter as enter_context)

from .config import get_config
from .variable import Scoreboard, dp_score, global_var, init_global
from .command import AsInstruction, Selector
from .entities import McdpStack, get_tag
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
        set_context_path(<str>config.namespace)
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
        
        cdef Context base = Context("__init__")
        _envs._append(base)
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


mcdp_stack_id = global_var(dp_score, "mcdpStackID", 0)


cdef class McdpFunctionError(McdpError):
    ...