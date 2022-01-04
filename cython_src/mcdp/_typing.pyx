cimport cython
import ujson

from .version import __version__
from .counter import Counter


cdef int mcdp_env_flag = 0 # 0: pydp, 1: vmcl

cpdef int _get_mcdp_ef():
    return mcdp_env_flag

cpdef void _set_mcdp_ef(int ef):
    global mcdp_env_flag
    mcdp_env_flag  = ef


cdef class McdpVar:

    __accessible__ = {}

    def __getattribute__(self, str key):
        self.check_gsattr(key, 1)
        return object.__getattribute__(self, key)
    
    def __setattr__(self, str key, value):
        self.check_gsattr(key, 2)
        object.__setattr__(self, key, value)

    cdef void check_gsattr(self, str key, int i) except *:
        if mcdp_env_flag == 0:
            return
        cdef:
            int mod
            dict accessible = type(self).__accessible__

        if "@all" in accessible:
            mod =  accessible["@all"]
            if mod | i:
                return

        if key == "@item":
            if key in accessible:
                mod = accessible["@item"]
                if mod | i:
                    return

        if "@all.attr" in accessible:
            mod =  accessible["@all.attr"]
            if mod | i:
                return
        else:
            if key in accessible:
                mod = accessible[key]
                if mod | i:
                    return
        raise AttributeError("'%s' object has no attribute %s"
                % (type(self).__qualname__, key))


cdef class _McdpBaseModel(McdpVar):

    __accessible__ = {"@all.attr": 3}

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, val: Union[dict, _McdpBaseModel]):
        if isinstance(val, dict):
            return cls(**val)
        elif not isinstance(val, cls):
            raise TypeError("%s is not a instance of %s." % (val, cls.__qualname__))
        else:
            return val

    cpdef dict to_dict(self):
        return {}
    
    def json(self, **kwds) -> str:
        return ujson.dumps(self.to_dict(), **kwds)


cdef class Variable(McdpVar):
    
    def __init__(self, Counter counter = None):
        if counter:
            self.counter = counter
        else:
            self.counter = Counter()

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, Variable val):
        return val

    cpdef void link(self, Variable var) except *:
        self.counter.link_to(var.counter)
    
    cpdef bint used(self):
        return bool(self.counter)
    
    def __repr__(self):
        return str(self)

cdef class McdpError(Exception):

    def __init__(self, *args):
        self.version = __version__
        super().__init__(*args)