import os
import warnings
from collections import defaultdict
from functools import wraps

from libc.stdio cimport fputs
from libc.string cimport strcpy

from .config import get_config
from .exceptions import McdpValueError

cdef extern from *:
    void* PyMem_Malloc(Py_ssize_t size) nogil
    void PyMem_Free(void* p) nogil


cdef:
    int MAX_OPEN = 8
    str CONTEXT_PATH
    str CONTEXT_ENV_PATH


cdef class StackCache(list):

    def __init__(self, int capacity = 12):
        if not (1 < capacity <= 128):
            raise ValueError(
                    "except the capacity ranging from 2 to 128, but get %d" % capacity
            )
        self._capacity = capacity
        super().__init__()
    
    cdef void _append(self, Context env):
        super().append(env)
        env.activate()
        cdef:
            int overflow = len(self) - self._capacity
            Context e
        if overflow > 0:
            for e in (<list>self)[:overflow]:
                e.deactivate()
    
    def append(self, Context env not None):
        self._append(env)
    
    cdef Context _pop(self):
        cdef:
            Context last = super().pop()
            Context next = (<list>self)[-1]
        last.deactivate()
        if self and not next.writable():
            next.activate(True)
        return last
    
    def pop(self):
        return self._pop()

    cdef void _clear(self):
        cdef Context e
        for e in (<list>self):
            e.deactivate()
        super().clear()
    
    def clear(self):
        self._clear()


cdef class EnvMethod:
    """
    Use the class as a decorator to
    announce a environment method.
    
    When called from the instance, the method works 
    as a normal method. And when it is called from the 
    class, the param 'self' will input <class>.current as 
    the instance.
    """

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


cdef class Handler(McdpVar):
    
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
    
    cpdef str command(self, str cmd):
        return cmd
    
    cpdef Context stream(self):
        cdef str file_name = self.env_type + hex(self.env_counter[self.env_type])
        self.env_counter[self.env_type] += 1
        return Context(file_name, root_path=CONTEXT_ENV_PATH, envs=self)


cdef StackCache _stack = StackCache(MAX_OPEN)

cdef str get_func_path():
    CONTEXT_PATH.replace('/', '\\')
    cdef list l = CONTEXT_PATH.split('\\', 2)
    if len(l) > 2:
        return l[2]
    else:
        return ''

cdef class Context(McdpVar):
    
    file_suffix = ".mcfunction"

    def __init__(
            self,
            str name not None,
            *,
            root_path = None,
            hdls = []
    ):
        self.name = name
        self.stream = Stream(name + self.file_suffix, root=root_path or CONTEXT_PATH)
        if not isinstance(hdls, list):
            hdlss = [hdls,]
        self.handlers = hdls
    
    cpdef void write(self, str content) except *:
        self.stream.write(content)
    
    cpdef bint writable(self):
        return self.stream.writable()
    
    cpdef void activate(self, bint append = False) except *:
        cdef Handler hdl
        if not append:
            self.stream.open("w")
            for hdl in self.handlers:
                hdl.init()
        else:
            self.stream.open("a")
    
    cpdef void deactivate(self):
        self.stream.close()
    
    def __enter__(self) -> Context:
        _stack._append(self)
        return self
    
    def __exit__(self, *args) -> None:
        if _stack._pop().name == "__init__":
            raise McdpContextError("Cannot leave the static stack '__init__'.")
    
    @EnvProperty
    def top(cls):
        if len(_stack) < 1:
            raise McdpContextError("Class 'Context' should be inited before used.")
        return _stack[-1]
    
    @EnvProperty
    def stacks(cls):
        return _stack

    @EnvMethod
    def insert(self, *content: str) -> None:
        if not self.writable():
            raise McdpContextError("fail to insert command.")

        cdef:
            str command
            list l_cmd
            str c
            Handler hdl
            Counter counter = get_counter().commands
            
        for command in content:
            +counter

            if not command.endswith('\n'):
                command += '\n'
            
            if command.count('\n') > 1:
                l_cmd = command.split('\n')[:-1]
                for c in l_cmd:
                    for hdl in self.handlers:
                        c = hdl.command(c)
                    self.write(c + '\n')
            else:
                for hdl in self.handlers:
                    command = hdl.command(command)
                self.write(command)

    @EnvMethod
    def comment(self, *content: str) -> None:
        if not self.writable():
            raise McdpContextError("fail to add comments.")
        cdef:
            list com = []
            str c
            list lc
        for c in content:
            if '\n' in c:
                lc = c.split('\n')
                com.extend(lc)
            else:
                com.append(c)

        self.write("# " + "\n# ".join(com) + '\n')
    
    @EnvMethod
    def newline(self, int line = 1) -> None:
        self.write('\n' * line)
    
    @EnvMethod
    def add_hdl(self, Handler hdl) -> None:
        self.handlers.append(hdl)
    
    @EnvMethod
    def pop_hdl(self) -> Handler:
        return self.handlers.pop()

    @staticmethod
    def enter_space(str name) -> None:
        global CONTEXT_PATH
        CONTEXT_PATH = os.path.join(CONTEXT_PATH, name)

    @staticmethod
    def exit_space() -> None:
        global CONTEXT_PATH
        CONTEXT_PATH = os.path.dirname(CONTEXT_PATH)

    @staticmethod
    def get_relative_path():
        return get_func_path()

    def __repr__(self) -> str:
        return "<env %s in the context>" % self.name


cdef dict _tag_collections = {}


cdef class TagManager(McdpVar):
    __accessible__ = {"type": 3, "replace": 3, "@item": 3}

    collections = _tag_collections

    def __init__(
            self, 
            str type not None, 
            *, 
            str namespace = None, 
            bint replace = False
    ):
        if not type in ["blocks", "entity_types", "items", "fluids", "functions"]:
            raise McdpValueError("Invalid tag type '%s'" % type)
        self.type = type
        self.replace = replace
        if not namespace:
            namespace = get_namespace()
        self.root_path = namespace + "\\tags\\" + type
        self.cache = {}

        self.name = "%s:%s" % (namespace, type)
        self.collect()
    
    cpdef void add(self, str tag, str item, namespace = None) except *:
        if not ":" in item:
            if not namespace:
                namespace = get_namespace()
            item = "%s:%s" % (namespace, item)

        cdef list litem = self[tag]
        if item in litem:
            warnings.warn("Try to add the tag '%s' twice." % tag)
        else:
            litem.append(item)

    def __getitem__(self, str key not None) -> List[str]:
        if not key in self.cache:
            self.cache[key] = []
        return self.cache[key]

    def __setitem__(self, str key not None, str item not None) -> None:
        self.add(key, item)

    cpdef dict get_tag_data(self, str tag, bint replace = False):
        if not tag in self.cache:
            raise McdpContextError("Cannot find tag '%s' in the cache." % tag)

        values = self.cache[tag]
        if not replace:
            replace = self.replace
        return {"replace": replace, "values": values}

    cpdef void apply_tag(self, str tag, bint replace = False) except *:
        if not tag in self.cache:
            raise McdpContextError("Tag '%s' did not defined." % tag)

        with Stream(tag + ".json", root=self.root_path) as stream:
            stream.dump(self.get_tag_data(tag, replace))

        del self.cache[tag]

    cpdef void apply(self):
        for tag in self.cache:
            self.apply_tag(tag)
    
    cdef void collect(self):
        _tag_collections[self.name] = self

    @classmethod
    def apply_all(cls):
        for i in _tag_collections.values():
            i.apply()
    
    def __del__(self) -> None:
        if self.cache:
            self.apply()


cdef api void dp_insert(const char* cmd) except *:
    cdef:
        Context top = _stack[-1]
        Handler hdl
        str tmp = cmd.decode()
    if not top.writable():
        raise McdpContextError("fail to insert command.")
    for hdl in top.handlers:
        tmp = hdl.command(tmp)
    top.stream._bwrite(tmp.encode())

cdef api void dp_comment(const char* cmt) except *:
    if not get_config().pydp.add_comments:
        return
    cdef Context top = _stack[-1]
    if not top.writable():
        raise McdpContextError("fail to add comments.")

    cdef:
        char buffer[129]
        int i = 2
    strcpy(buffer, "# ")
    while cmt[0]:
        if cmt[0] == ord('\n'):
            if i > 123:
                top.stream._bwrite(buffer)
                i = 0
            strcpy(buffer+i, "\n# ")
            i += 3
            cmt += 1
        else:
            if i > 126:
                top.stream._bwrite(buffer)
                i = 0
            buffer[i] = cmt[0]
            i += 1
            cmt += 1
    buffer[i] = ord('\n')
    buffer[i+1] = ord('\0')
    top.stream._bwrite(buffer)

cdef api void dp_newline(int line) except *:
    if not get_config().pydp.add_comments:
        return
    cdef Context top = _stack[-1]
    if not top.writable():
        raise McdpContextError("fail to add comments.")

    cdef char* buffer = <char*>PyMem_Malloc((line + 1) * sizeof(char))
    if buffer == NULL:
        raise MemoryError
    cdef int i
    for i in range(line):
        buffer[i] = ord('\n')
    buffer[i] = ord('\0')
    top.stream._bwrite(buffer)
    PyMem_Free(buffer)

cdef api void dp_addTag(const char* _tag) except *:
    cdef:
        str tag = _tag.decode()
        str namespace = get_namespace()
        str value = get_func_path()
        TagManager m_tag = _tag_collections[namespace + ":functions"]
    m_tag.add(tag, value)


def insert(*content: str) -> None:
    Context.insert(*content)

def comment(*content: str) -> None:
    if get_config().pydp.add_comments:
        Context.comment(*content)

def newline(line: int = 1) -> None:
    if get_config().pydp.add_comments:
        Context.newline(line)

def add_tag(
        str tag not None, 
        str value = None, 
        *, 
        str namespace = None, 
        str type = "functions"
) -> None:
    cdef:
        list nt
        TagManager m_tag
        Context c
    if ':' in tag:
        nt = tag.split(':', 2)
        namespace = nt[0]
        tag = nt[1]
    elif not namespace:
        namespace = get_namespace()

    if not value:
        if type == "functions":
            c = Context.top
            value = get_func_path() + '\\' + c.name
        else:
            raise McdpValueError("no value input.")
    m_tag = _tag_collections[f"{namespace}:{type}"]
    m_tag.add(tag, value)

cpdef str get_namespace():
    return get_config().namespace

cdef void set_context_path(str path):
    global CONTEXT_PATH, CONTEXT_ENV_PATH
    CONTEXT_PATH = path
    CONTEXT_ENV_PATH = path + "\\Envs"


cdef class McdpContextError(McdpError):

    def __init__(self, *arg: str) -> None:
        if _stack:
            self.context = _stack[-1]
        super(McdpError, self).__init__(*arg)