from cpython cimport Py_LT, Py_LE, Py_GT, Py_GE, Py_EQ, Py_NE
cimport cython

import re
from functools import wraps
from collections import OrderedDict
from typing import Union, Tuple, Dict


T_version = Union[Tuple[Union[str, int], ...], Dict[str, Union[str, int]], str, "Version"]


cdef SEMVER_REGEX = re.compile(
    r"""
        ^
        (0|[1-9]\d*)
        \.
        (0|[1-9]\d*)
        (?:\.
        (0|[1-9]\d*))?
        (?:-(
            (?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)
            (?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*
        ))?
        (?:\+(
            [0-9a-zA-Z-]+
            (?:\.[0-9a-zA-Z-]+)*
        ))?
        $
    """,
    re.VERBOSE,
)

'''
cpdef int get_version(_version) except -1:
    cdef Version mc_version 
    if not isinstance(_version, Version):
        mc_version = Version(_version)
    else:
        mc_version = _version

    if mc_version.major != 1:
        raise McdpVersionError("Minecraft version must start with '1.'.")
    elif mc_version.minor < 13:
        raise McdpVersionError("datapack is not enable for Minecraft below 1.13 .")
    elif mc_version.minor < 15:
        return 4
    elif mc_version <= "1.16.1":
        return 5
    elif mc_version.minor < 17:
        return 6
    elif mc_version.minor == 17:
        return 7
    else:
        raise ValueError(f"unknow Minecraft datapack version {mc_version}.")
'''

cdef inline bint _version_cmp(Version v0, Version v1, int op) except -1:
    cdef:
        tuple v0_num = v0.to_tuple()
        tuple v1_num = v1.to_tuple()
    if op == Py_EQ:
        return v0_num == v1_num
    elif op == Py_NE:
        return v0_num != v1_num
    
    cdef bint eq_ok = op == Py_LE or op == Py_GE

    cdef:
        int i
        int j
    cdef tuple vln0 = v0_num[:3]
    cdef tuple vln1 = v1_num[:3]
    for k in range(3):
        i = vln0[k]
        j = vln1[k]
        if i == j:
            continue
        else:
            if op == Py_LT or op == Py_LE:
                return i < j
            else:
                return i > j
    else:
        return eq_ok


cdef class Version:
    @cython.nonecheck(False)
    def __init__(self, version):
        cdef:
            tuple num
            int n
        if isinstance(version, tuple):
            self._init_from_tuple(<tuple>version)
            self._check_valid()
        elif isinstance(version, str):
            m = SEMVER_REGEX.match(version)
            if m is None:
                raise ValueError("Incorrect version form.")
            self._init_from_tuple(m.groups())
        elif isinstance(version, dict):
            try:
                self.major = int(version["major"])
                self.minor = int(version["minor"])
                self.patch = int(version["patch"])
                if "prerelease" in (<dict>version) and version["prerelease"]:
                    self.prerelease = str(version["prerelease"])
                if "build" in (<dict>version) and version["build"]:
                    self.build = str(version["build"])
                self._check_valid()
            except:
                pass
            else:
                return
            raise ValueError("Incorrect version form.")
        elif isinstance(version, Version):
            self._init_from_tuple((<Version>version).to_tuple())
        else:
            raise TypeError("Invalid version type '%s'" % type(version))
    
    cdef inline void _init_from_tuple(self, tuple version) except *:
        if len(version) != 5:
            raise ValueError("Incorrect version tuple.")
        self.major = int(version[0])
        self.minor = int(version[1])
        if version[2] is None:
            self.patch = 0
        else:
            self.patch = int(version[2])
        if version[3]:
            self.prerelease = str(version[3])
        if version[4]:
            self.build = str(version[4])
    
    cdef inline void _check_valid(self) except *:
        if self.major < 0 or self.minor < 0 or self.patch < 0:
            raise ValueError("A version can only be positive.")
    
    cpdef tuple to_tuple(self):
        return (self.major, self.minor, self.patch, self.prerelease, self.build)
    
    cpdef to_dict(self):
        return OrderedDict(
            (
                ("major", self.major),
                ("minor", self.minor),
                ("patch", self.patch),
                ("prerelease", self.prerelease),
                ("build", self.build),
            )
        )
    
    cpdef int to_int(self):
        return (self.major * 10 + self.minor) * 10 + self.patch

    @cython.nonecheck(False)
    def __getitem__(self, index):
        cdef slice _index
        if isinstance(index, int):
            if (<int>index < 0):
                raise IndexError("Version index cannot be negative")
            return self.to_tuple()[index]
        else:
            _index = index
            if (
                (_index.start is not None and _index.start < 0)
                or (_index.stop is not None and _index.stop < 0)
            ):
                raise IndexError("Version index cannot be negative")

            part = []
            for i in <tuple>(self.to_tuple()[_index]):
                if not i is None:
                    part.append(i)
            part = tuple(<list>part)
            if not part:
                raise IndexError("Version part undefined")
            return part

    def __iter__(self):
        return self.to_tuple()
    
    def __hash__(self):
        return hash(self.to_tuple[:4])
    
    def __int__(self):
        return self.to_int()
    
    def __index__(self):
        return self.to_int()
    
    def __richcmp__(self, _other, int op):
        cdef Version other
        if not isinstance(_other, Version):
            try:
                other = type(self)(_other)
            except ValueError:
                return NotImplemented
        else:
            other = _other

        return _version_cmp(self, other, op)
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, val: Union[str, "Version"]):
        if isinstance(val, cls):
            return val
        else:
            return cls(val)
    
    def __len__(self) -> int:
        cdef int n = 0
        for i in self.to_tuple():
            if i != None:
                n += 1
        return n
    
    cdef bint _ensure(
            self, list eq = None, list ne = None,
            object gt = None, object ge = None,
            object lt = None, object le = None
    ) except -1:
        cdef bint check = True
        if not gt is None:
            check = check and (self> gt)
        if not ge is None:
            check = check and (self >= ge)
        if not lt is None:
            check = check and (self < lt)
        if not le is None:
            check = check and (self <= le)
        if eq:
            for v in eq:
                if self == Version(v):
                    check = True
        if ne:
            for v in ne:
                if self == Version(v):
                    check = False
        return check
    
    
    def ensure(
            self,
            *args,
            object eq = None, object ne = None,
            object gt = None, object ge = None,
            object lt = None, object le = None
    ) -> bool:
        """
        The core function of the version check.
        """
        cdef str i
        cdef list _eq, _ne
        if not (eq is None or isinstance(eq, list)):
            _eq = [eq, ]
        else:
            _eq = eq
        if not (ne is None or isinstance(ne, list)):
            _ne = [ne, ]
        else:
            _ne = ne
        if args:
            for i in args:
                if i.startswith('>='):
                    ge = ge or i[2:]
                elif i.startswith('<='):
                    le = le or i[2:]
                elif i.startswith('>'):
                    gt = gt or i[1:]
                elif i.startswith('<'):
                    lt = lt or i[1:]
                elif i.startswith('=='):
                    _eq.append(i[2:])
                elif i.startswith('!='):
                    _ne.append(i[2:])
                else:
                    raise ValueError(f"Cannot analyze the argument {i}")
        return self._ensure(_eq, _ne, ge, gt, le, lt)


    def check(self, *args, **kwds):
        cdef bint check = self.ensure(*args, **kwds)
        if not check:
            return fail_version_check
        else:
            return pass_version_check

    def __repr__(self) -> str:
        return "Version%s" % (self.to_tuple(),)

    def __str__(self):
        cdef str version = "%d.%d.%d" % (self.major, self.minor, self.patch)
        if self.prerelease != None:
            version += "-%s" % self.prerelease
        if self.build != None:
            version += "+%s" % self.build
        return version


__version__ = Version("0.2.3-Alpha")

cdef dict _version_func = {}


def fail_version_check(func: Callable, *, collection: Dict[str, Callable] = _version_func) -> Callable:
    name = func.__qualname__
    if name in collection:
        return collection[name]
    @wraps(func)
    def nope(*args, **kwargs) -> NoReturn:
        raise McdpVersionError(f"The function '{name}' fails to pass the version check.")

    return nope


def pass_version_check(func: Callable, *, collection: Dict[str, Callable] = _version_func) -> Callable:
    name = func.__qualname__
    if name in collection:
        raise McdpVersionError(f"The function '{name}' has a version conflict.")
    collection[name] = func
    return func


def analyse_check_sentences(
        *args,
        eq: Union[List[T_Version], T_Version] = [],
        ne: Union[List[T_Version], T_Version] = [],
        gt: Optional[T_Version] = None,
        ge: Optional[T_Version] = None,
        lt: Optional[T_Version] = None,
        le: Optional[T_Version] = None
) -> Dict[str, Union[List[T_Version], T_Version, None]]:
    cdef dict ans = {}
    if not isinstance(eq, list):
        ans['eq'] = [eq, ]
    else:
        ans['eq'] = eq
    if not isinstance(ne, list):
        ans['ne'] = [ne, ]
    else:
        ans['ne'] = ne

    cdef str i
    for i in args:
        if i.startswith('>='):
            ans['ge'] = ge or i[2:]
        elif i.startswith('<='):
            ans['le'] = le or i[2:]
        elif i.startswith('>'):
            ans['gt'] = gt or i[1:]
        elif i.startswith('<'):
            ans['lt'] = lt or i[1:]
        elif i.startswith('=='):
            ans['eq'].append(i[2:])
        elif i.startswith('!='):
            ans['ne'].append(i[2:])
        else:
            raise ValueError(f"Cannot analyze the argument {i}")
    return ans


version_check = Version.check


cdef class VersionChecker:
    def __init__(self, version_factory: Callable[[], Version], bint save_check = False) -> None:
        self.version_factory = version_factory
        self.checked = False
        self.save_check = save_check

        self.functions = []
        self.sentences = []
        self.collection = {}

    def register(self, func: Callable, *args: str, **kwds) -> None:
        cdef Version version
        if not self.checked:
            c = analyse_check_sentences(*args, **kwds)
            self.functions.append(func)
            self.sentences.append(c)
        else:
            version = self.version_factory()
            check_ans = version.CHECK(*args, **kwds)
            self.__func__ = check_ans(func, collection=self.collection)

    @property
    def decorator(self):
        def version_check_decorator(*args, **kwds):
            def get_func(func: Callable) -> Callable:
                name = func.__qualname__
                self.register(func, *args, **kwds)

                @wraps(func)
                def wrapper(*arg, **kw) -> Any:
                    self.apply_check()
                    if name in self.collection:
                        return self.collection[name](*arg, **kw)
                    else:
                        raise McdpVersionError(
                                f"The function '{name}' fails to pass the version check.",
                                version=self.version_factory()
                            )

                return wrapper
            return get_func
        return version_check_decorator

    cpdef void apply_check(self):
        if self.checked:
            return

        cdef Version ver = self.version_factory()
        for i in range(len(self.functions)):
            ans = version_check(ver, **self.sentences[i])
            self.__func__ = ans(self.functions[i], collection=self.collection)
        if self.save_check:
            self.checked = True

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        self.apply_check()
        return self.__func__(*args, **kwds)


cdef class McdpVersionError(McdpError):
    def __init__(self, *msg, version = None) -> None:
        if version is None:
            self.version = __version__
        else:
            self.version = version
        super().__init__(*msg)