from functools import wraps
from asyncio import iscoroutinefunction
from typing import Any, Dict, List, NoReturn, Tuple, Callable, Union, Optional, TypeVar, overload

T_version = Union[Tuple[int, ...], str, "Version"]
TS_version = Union[Tuple[Union[str, int], ...], str, "PhaseVersion"]


class Version:
    """
    The base class in model 'version'.
    Support boolean operations between version numbers like '1.0.2'.
    """

    __slots__ = ["__num_list", ]

    def __init__(self, version: T_version) -> None:
        if isinstance(version, tuple):
            self.__num_list: Tuple[int, ...] = version
        elif isinstance(version, self.__class__):
            self.__num_list = version.get_number()
        else:
            try:
                num = [int(i) for i in version.split('.')]
                if len(num) <= 1:
                    raise ValueError
                elif any([i < 0 for i in num]):
                    raise ValueError
                self.__num_list = tuple(num)
                return

            except Exception:
                pass
            raise ValueError("Incorrect version form.")

    @overload
    def __getitem__(self, key: int) -> int:
        ...
    @overload
    def __getitem__(self, key: slice) -> Tuple[int, ...]:
        ...
    def __getitem__(self, key: Union[int, slice]) -> Union[int, Tuple[int, ...]]:
        try:
            return self.__num_list[key]
        except IndexError:
            if isinstance(key, slice):
                raise
            else:
                return 0

    def __iter__(self) -> Tuple[int, ...]:
        return self.__num_list

    def _compare(self, ops: Callable[[int, int], bool], other: T_version) -> bool:
        if not isinstance(other, self.__class__):
            try:
                other = self.__class__(other)
            except ValueError:
                return NotImplemented

        m = max(len(self), len(other))
        e = ops(1, 1)
        for i, j in zip(self._generator(m), other.get_number(extend=m)):
            if i == j:
                continue
            else:
                return ops(i, j)
        else:
            return e

    @staticmethod
    def compare_decorator(ops: Callable[[int, int], bool]) -> Callable[["Version", T_version], bool]:
        """
        Be used to create a operator to compare two Version instance. 
        The argument 'ops' will be used to compare every number of
        the version list.
        
        Use as: 
            ```
            @Version.compare_decorator
            def around(v1: int, v2: int) -> bool:
                if abs(v1 - v2) < 5:
                    return True
                else:
                    return False
            print(around(Version("1.12"), Version("1.13")))
            # output: True
            ```
        """

        def __compare__(self, other: T_version) -> bool:
            return self._compare(ops, other)

        return __compare__

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, val: Union[str, "Version"]):
        if isinstance(val, cls):
            return val
        else:
            return cls(val)

    def __eq__(self, other: T_version) -> bool:
        if not isinstance(other, self.__class__):
            try:
                other = self.__class__(other)
            except ValueError:
                return NotImplemented
        return self.__num_list == other.get_number()

    def __ne__(self, other: T_version) -> bool:
        if not isinstance(other, self.__class__):
            try:
                other = self.__class__(other)
            except ValueError:
                return NotImplemented
        return self.__num_list != other.get_number()

    __gt__ = compare_decorator.__func__(lambda x, y: x > y)
    __ge__ = compare_decorator.__func__(lambda x, y: x >= y)
    __lt__ = compare_decorator.__func__(lambda x, y: x < y)
    __le__ = compare_decorator.__func__(lambda x, y: x <= y)

    def __len__(self) -> int:
        return len(self.__num_list)

    def _generator(self, max: Optional[int] = None):
        l = len(self)
        i = 0
        while True:
            if i < l:
                yield self.__num_list[i]
            else:
                yield 0

            i += 1
            if not max is None:
                if i >= max:
                    return
            elif i > 32:
                raise RuntimeError

    @overload
    def get_number(self, *, extend: Optional[int] = None) -> Tuple[int, ...]:
        ...
    @overload
    def get_number(self, index: int , *, extend: Optional[int] = None) -> int:
        ...
    def get_number(self, index: Optional[int] = None, *, extend: Optional[int] = None) -> Union[Tuple[int, ...], int]:
        if index:
            try:
                return self.__num_list[index]
            except IndexError:
                return 0
        else:
            if not extend:
                return self.__num_list
            else:
                return tuple(self._generator(extend))

    def check(self, *args, **kw):
        return version_check(self, *args, **kw)

    def __repr__(self) -> str:
        return f"Version{self.__num_list}"

    def __str__(self) -> str:
        return '.'.join([str(i) for i in self.__num_list])


class PhaseVersion(Version):
    """
    Just add a version phase like 'Alpha' or 'Beta'. 
    (In fact, 'Python 3.8.3' is valid, too.)
    
    The phase mark only used in '==' and '!=' when both sides have a phase mark.
    That is to say:
        ```
        v = PhaseVersion('Beta 1.5.2')
        v == '1.5.2'        #True
        v == 'Alpha 1.5.2'  #False
        v >= 'Alpha 1.4'    #True
        ```
    """

    __slots__ = ["phase"]

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
                return super().__init__(version)
            except Exception:
                pass
            raise ValueError("Incorrect version form.")

    def __eq__(self, other: T_version) -> bool:
        if not isinstance(other, self.__class__):
            try:
                other = self.__class__(other)
            except ValueError:
                return NotImplemented
        if self.phase and other.phase:
            if self.phase != other.phase:
                return False
        return super().__eq__(other)

    def __ne__(self, other: T_version) -> bool:
        if not isinstance(other, self.__class__):
            try:
                other = self.__class__(other)
            except ValueError:
                return NotImplemented
        if self.phase and other.phase:
            if self.phase == other.phase:
                return False
        return super().__ne__(other)

    def __repr__(self) -> str:
        if not self.phase:
            return super().__repr__()
        return f"PhaseVersion({self.phase}, {self.get_number()})"

    def __str__(self) -> str:
        num = super().__str__()
        if not self.phase:
            return num
        return f"{self.phase} {num}"


__version__ = PhaseVersion("Alpha 0.1.0")

_version_func: Dict[str, Callable] = {}


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


def pass_version_check(func: Callable, *, collection: Dict[str, Callable] = _version_func) -> Any:
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
    ans: Dict[str, Union[List[T_version], T_version, None]] = {}
    if not isinstance(eq, List):
        ans['eq'] = [eq, ]
    else:
        ans['eq'] = eq
    if not isinstance(ne, List):
        ans['ne'] = [ne, ]
    else:
        ans['ne'] = ne

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
        version: Version,
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
    if not isinstance(eq, List):
        eq = [eq, ]
    if not isinstance(ne, List):
        ne = [ne, ]
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
                eq.append(i[2:])
            elif i.startswith('!='):
                ne.append(i[2:])
            else:
                raise ValueError(f"Cannot analyze the argument {i}")
    check = True
    if gt:
        check = check and (version > gt)
    if ge:
        check = check and (version >= ge)
    if lt:
        check = check and (version < lt)
    if le:
        check = check and (version <= le)
    if eq:
        check = check or (version in [Version(i) for i in eq])
        eq.clear()
    if ne:
        check = check and not (version in [Version(i) for i in ne])
        ne.clear()

    if not check:
        return fail_version_check
    else:
        return pass_version_check


class VersionChecker:
    """
    The helper of version checker.
    
    Sometimes the version cannot be fetched when inited, so class VersionChecker is created.
    The final function will be insure when the function is first called.
    
    In the same time, the class supports the multiple version check.
    """

    __slots__ = ["collection", "version_factory", "checked", "__func__", "sentence", "__qualname__"]

    def __init__(self, version_factory: Callable[[], Version]) -> None:
        self.collection: Dict[str, Callable] = {}
        self.version_factory = version_factory
        self.checked = False
        self.__func__: Union[List[Callable], Callable, None] = []
        self.sentence: List[dict] = []

    def register(self, func: Callable, *args: str, **kwds) -> None:
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

    def apply_check(self) -> None:
        if not self.checked:
            l: list = self.__func__
            for i in range(len(l)):
                ans = version_check(self.version_factory(), **self.sentence[i])
                self.__func__ = ans(l[i], collection=self.collection)
            self.checked = True

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        self.apply_check()
        return self.__func__(*args, **kwds)


class AioCompatVersionChecker(VersionChecker):
    """
    The async compat version of class VersionCheck.
    """

    __slots__ = []

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


class VersionError(Exception):
    __slots__ = ["version"]

    def __init__(self, *msg, version: Optional[Version] = None) -> None:
        self.version = version
        super().__init__(*msg)
