from cpython cimport Py_LT, Py_LE, Py_GT, Py_GE, Py_EQ, Py_NE
cimport cython

import re
from functools import wraps
from collections import OrderedDict
from asyncio import iscoroutinefunction
from typing import Union, Tuple


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


cpdef int get_version(_version) except -1:
    cdef Version mc_version 
    if not isinstance(_version, Version):
        mc_version = Version(_version)
    else:
        mc_version = _version

    if mc_version.major != 1:
        raise VersionError("Minecraft version must start with '1.'.")
    elif mc_version.minor < 13:
        raise VersionError("datapack is not enable for Minecraft below 1.13 .")
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

cdef bint _version_cmp(Version v0, Version v1, int op) except -1:
    cdef:
        tuple v0_num = v0.to_tuple()
        tuple v1_num = v1.to_tuple()
    if op == Py_EQ:
        return v0_num == v1_num
    elif op == Py_NE:
        return v0_num != v1_num
    
    cdef bint eq_ok = op == Py_LE | op == Py_GE

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

@cython.binding(False)
@cython.unraisable_tracebacks(False)
def _init_packed(Version version_self, T_Version version):
    cdef:
        tuple num
        int n
    if T_Version is tuple:
        version_self._init_from_tuple(version)
        version_self._check_valid()
    elif T_Version is str:
        m = SEMVER_REGEX.match(version)
        if m is None:
            raise ValueError("Incorrect version form.")
        version_self._init_from_tuple(m.groups())
    elif T_Version is dict:
        try:
            version_self.major = int(version["major"])
            version_self.minor = int(version["minor"])
            version_self.patch = int(version["patch"])
            if "prerelease" in version and version["prerelease"]:
                version_self.prerelease = str(version["prerelease"])
            if "build" in version and version["build"]:
                version_self.build = str(version["build"])
            version_self._check_valid()
        except:
            pass
        else:
            return
        raise ValueError("Incorrect version form.")
    else:
        version_self._init_from_tuple(version.to_tuple())

@cython.binding(False)
@cython.unraisable_tracebacks(False)
def _version_getitem(Version version_self, T_Key index):
    if T_Key is int:
        if (index < 0):
            raise IndexError("Version index cannot be negative")
        return version_self.to_tuple()[index]
    else:
        if (
            (index.start is not None and index.start < 0)
            or (index.stop is not None and index.stop < 0)
        ):
            raise IndexError("Version index cannot be negative")

        part = tuple(i for i in version_self.to_tuple()[index] if i != None)
        if not part:
            raise IndexError("Version part undefined")
        return part


cdef class Version:

    def __init__(self, version):
        _init_packed(self, version)
    
    cdef void _init_from_tuple(self, tuple version) except *:
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
    
    cdef void _check_valid(self) except *:
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

    def __getitem__(self, index):
        return _version_getitem(self, index)

    def __iter__(self):
        return self.to_tuple()
    
    def __hash__(self):
        return hash(self.to_tuple[:4])
    
    def __richcmp__(self, _other, int op):
        cdef Version other
        if not isinstance(_other, Version):
            try:
                other = self.__class__(_other)
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
    
    def check(self, *args: str, **kw: Union[Tuple[int, ...], str, "Version"]):
        return version_check(self, *args, **kw)

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
    if not iscoroutinefunction(func):
        @wraps(func)
        def nope(*args, **kwargs) -> NoReturn:
            raise VersionError(f"The function '{name}' fails to pass the version check.")

        return nope
    else:
        @wraps(func)
        async def aio_nope(*args, **kwargs) -> NoReturn:
            raise VersionError(f"The function '{name}' fails to pass the version check.")

        return aio_nope


def pass_version_check(func: Callable, *, collection: Dict[str, Callable] = _version_func) -> Callable:
    name = func.__qualname__
    if name in collection:
        raise VersionError(f"The function '{name}' has a version conflict.")
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


def version_check(
        Version version,
        *args: str,
        eq: Union[List[T_Version], T_Version] = [],
        ne: Union[List[T_Version], T_Version] = [],
        gt: Optional[T_Version] = None,
        ge: Optional[T_Version] = None,
        lt: Optional[T_Version] = None,
        le: Optional[T_Version] = None
) -> Callable[[Callable], Callable]:
    """
    The core function of the version check.
    """
    cdef str i
    cdef list _eq, _ne
    if not isinstance(eq, list):
        _eq = [eq, ]
    else:
        _eq = eq
    if not isinstance(ne, list):
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

    cdef bint check = True
    if gt:
        check = check and (version > gt)
    if ge:
        check = check and (version >= ge)
    if lt:
        check = check and (version < lt)
    if le:
        check = check and (version <= le)
    if _eq:
        for v in _eq:
            if version == Version(v):
                check = True
        _eq.clear()
    if _ne:
        for v in _ne:
            if version == Version(v):
                check = False
        _ne.clear()

    if not check:
        return fail_version_check
    else:
        return pass_version_check

cdef class VersionChecker:

    def __init__(self, version_factory: Callable[[], Version]) -> None:
        self.collection: Dict[str, Callable] = {}
        self.version_factory = version_factory
        self.checked = False
        self.__func__: Union[List[Callable], Callable, None] = []
        self.sentence: List[dict] = []

    def register(self, func: Callable, *args: str, **kwds) -> None:
        cdef Version version
        if not self.checked:
            c = analyse_check_sentences(*args, **kwds)
            self.__func__.append(func)
            self.sentence.append(c)
        else:
            version = self.version_factory()
            check_ans = version_check(version, *args, **kwds)
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
                        raise VersionError(
                                f"The function '{name}' fails to pass the version check.",
                                version=self.version_factory()
                            )

                return wrapper

            return get_func

        return version_check_decorator

    cpdef void apply_check(self):
        cdef list l
        if not self.checked:
            l = self.__func__
            for i in range(len(l)):
                ans = version_check(self.version_factory(), **self.sentence[i])
                self.__func__ = ans(l[i], collection=self.collection)
            self.checked = True

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        self.apply_check()
        return self.__func__(*args, **kwds)


cdef class VersionError(Exception):

    def __init__(self, *msg, version: Optional[Version] = None) -> None:
        self.version = version
        super().__init__(*msg)