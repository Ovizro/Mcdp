from cpython cimport Py_LT, Py_LE, Py_GT, Py_GE, Py_EQ, Py_NE

from functools import wraps
from asyncio import iscoroutinefunction
from typing import Union, Tuple


T_version = Union[Tuple[int, ...], str, "Version"]

cdef bint _version_cmp(Version v0, Version v1, int op) except -1:
    if op == Py_EQ:
        return v0.vs_num == v1.vs_num
    elif op == Py_NE:
        return v0.vs_num != v1.vs_num
    
    cdef bint eq_ok = op == Py_LE | op == Py_GE
    cdef int m = max(len(v0), len(v1))

    cdef:
        int i
        int j
    cdef tuple vln0 = v0._extend(m)
    cdef tuple vln1 = v1._extend(m)
    for k in range(m):
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

    def __init__(self, version: T_version):
        cdef:
            list num
            int n
        if isinstance(version, tuple):
            self.vs_num = version
        elif isinstance(version, str):
            try:
                num = version.split('.')
                for i in range(len(num)):
                    num[i] = int(num[i])
                if len(num) <= 1:
                    raise ValueError
                for n in num:
                    if n < 0:
                        raise ValueError
                self.vs_num = tuple(num)
                return

            except Exception:
                pass
            raise ValueError("Incorrect version form.")
        else:
            self.vs_num = (<Version?>version).vs_num

    def __getitem__(self, key: T_version):
        try:
            return self.vs_num[key]
        except IndexError:
            if isinstance(key, slice):
                raise IndexError("Index out of range.")
            else:
                return 0

    def __iter__(self):
        return self.vs_num
    
    def __richcmp__(self, _other, int op):
        cdef Version other
        if not isinstance(_other, Version):
            try:
                other = Version(_other)
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
        return len(self.vs_num)

    cdef tuple _extend(self, int max):
        cdef int l = len(self.vs_num)
        if max <= l:
            return self.vs_num[:max]
        else:
            return self.vs_num + (0,) * (max - l)

    def _generator(self, max: Optional[int] = None):
        cdef int l = len(self.vs_num)
        cdef int i = 0
        while True:
            if i < l:
                yield self.vs_num[i]
            else:
                yield 0

            i += 1
            if not max is None:
                if i >= max:
                    return
            elif i > 32:
                raise RuntimeError
    
    def get_number(self, index: Optional[int] = None, *, extend: Optional[int] = None) -> Union[Tuple[int, ...], int]:
        if index:
            try:
                return self.vs_num[index]
            except IndexError:
                return 0
        else:
            if not extend:
                return self.vs_num
            else:
                return self._extend(extend)
    
    def check(self, *args: str, **kw: Union[Tuple[int, ...], str, "Version"]):
        return version_check(self, *args, **kw)

    def __repr__(self) -> str:
        return f"Version{self.vs_num}"

    def __str__(self) -> str:
        return '.'.join([str(i) for i in self.vs_num])


cdef class PhaseVersion(Version):

    def __init__(self, version: T_version, *, phase: Optional[str] = None) -> None:
        if isinstance(version, self.__class__):
            self.phase = version.phase
            super().__init__(version)
        elif isinstance(version, Version):
            self.phase = phase
            super().__init__(version)
        else:
            try:
                if isinstance(version, tuple):
                    if isinstance(version[0], str):
                        self.phase = phase or version[0]
                        version = version[1:]
                    else:
                        self.phase = phase
                else:
                    l = version.split()
                    if len(l) == 1:
                        self.phase = phase
                    elif len(l) > 2 or (not isinstance(l[0], str)):
                        raise ValueError
                    else:
                        self.phase = phase or l[0]
                        version = l[1]
                super().__init__(version)
                return
            except Exception:
                pass
            raise ValueError("Incorrect version form.")
    
    def __richcmp__(self, _other, int op):
        cdef PhaseVersion other
        if not isinstance(_other, PhaseVersion):
            try:
                other = PhaseVersion(_other)
            except ValueError:
                return NotImplemented
        else:
            other = _other
        
        if self.phase and other.phase:
            if op == Py_EQ:
                return self.vs_num == other.vs_num and self.phase == other.phase
            elif op == Py_NE:
                return self.vs_num != other.vs_num or self.phase != other.phase
        
        return _version_cmp(self, other, op)

    def __repr__(self) -> str:
        if not self.phase:
            return super().__repr__()
        return f"PhaseVersion({self.phase}, {self.get_number()})"

    def __str__(self) -> str:
        num = super().__str__()
        if not self.phase:
            return num
        return f"{self.phase} {num}"


__version__ = PhaseVersion("Alpha 0.2.1")

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
        eq: Union[List[T_version], T_version] = [],
        ne: Union[List[T_version], T_version] = [],
        gt: Optional[T_version] = None,
        ge: Optional[T_version] = None,
        lt: Optional[T_version] = None,
        le: Optional[T_version] = None
) -> Dict[str, Union[List[T_version], T_version, None]]:
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
        eq: Union[List[T_version], T_version] = [],
        ne: Union[List[T_version], T_version] = [],
        gt: Optional[T_version] = None,
        ge: Optional[T_version] = None,
        lt: Optional[T_version] = None,
        le: Optional[T_version] = None
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


cdef class AioCompatVersionChecker(VersionChecker):
    @property
    def decorator(self):
        def version_check_decorator(*args, **kwds):
            def get_func(func: Callable) -> Callable:
                name = func.__qualname__
                self.register(func, *args, **kwds)

                if not iscoroutinefunction(func):
                    @wraps(func)
                    def wrapper(*arg, **kw) -> Any:
                        self.apply_check()
                        if name in self.collection:
                            return self.collection[name](*arg, **kw)
                        else:
                            raise VersionError(
                                    f"The function '{name}' fails to pass the version check.", version=self.version_factory())

                    return wrapper
                else:
                    @wraps(func)
                    async def aio_wrapper(*arg, **kw) -> Any:
                        self.apply_check()
                        if name in self.collection:
                            return await self.collection[name](*arg, **kw)
                        else:
                            raise VersionError(
                                    f"The function '{name}' fails to pass the version check.", version=self.version_factory())

                    return aio_wrapper

            return get_func

        return version_check_decorator

    async def __call__(self, *args: Any, **kwds: Any) -> Any:
        self.apply_check()
        return await self.__func__(*args, **kwds)


cdef class VersionError(Exception):

    def __init__(self, *msg, version: Optional[Version] = None) -> None:
        self.version = version
        super().__init__(*msg)