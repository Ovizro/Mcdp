from typing import List, Tuple, Iterable, Callable, Union, Optional, TypeVar

from .typings import McdpError, __version__

T_version = TypeVar("version", Tuple[int], str, "Version")

class Version:
    
    __slots__ = ["__num_list",]
    
    def __init__(self, version: T_version) -> None:
        if isinstance(version, self.__class__):
            self.__num_list = version.get_number()
        elif isinstance(version, tuple):
            self.__num_list = version
        else:
            try:
                num = [int(i) for i in version.split('.')]
                if len(num) <= 1:
                    raise ValueError
                elif any([i < 0 for i in num]):
                    raise ValueError
                self.__num_list = tuple(num)
                return
            
            except (TypeError, ValueError):
                pass
            raise ValueError("incorrect version form.")
    
    def __getitem__(self, key: Union[int, slice]) -> Union[int, Tuple[int]]:
        try:
            return self.__num_list[key]
        except IndexError:
            if isinstance(key, slice):
                raise
            else:
                return 0
        
    def __iter__(self) -> Tuple[int]:
        return self.__num_list
                
    def _compare(self, ops: Callable[[int, int], bool], other: T_version) -> bool:
        if not isinstance(other, self.__class__):
            try:
                other = self.__class__(other)
            except (McdpVersionError, ValidationError):
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
    def _D_compare(ops: Callable[[int,int], bool]) -> Callable[["Version", T_version], bool]:
        def __compare__(self, other: T_version) -> bool:
            return self._compare(ops, other)
        return __compare__
        
    def __eq__(self, other: T_version) -> bool:
        if not isinstance(other, self.__class__):
            other = self.__class__(other)
        return self.__num_list == other.get_number()
        
    def __ne__(self, other: T_version) -> bool:
        if not isinstance(other, self.__class__):
            other = self.__class__(other)
        return self.__num_list != other.get_number()
    
    __gt__ = _D_compare.__func__(lambda x, y: x > y)
    __ge__ = _D_compare.__func__(lambda x, y: x >= y)
    __lt__ = _D_compare.__func__(lambda x, y: x < y)
    __le__ = _D_compare.__func__(lambda x, y: x <= y)
    
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
    
    def get_number(self, index: Optional[int] = None, *, extend: Optional[int] = None) -> Union[Tuple[int], int]:
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
            
    def __repr__(self) -> str:
        return f"Version{self.__num_list}"
    
    def __str__(self) -> str:
        return '.'.join(self.__num_list)

def get_version(mc_version: T_version) -> int:
    if not isinstance(mc_version, Version):
        mc_version = Version(mc_version)

    if mc_version[0] != 1:
        raise MinecraftVersionError
    elif mc_version[1] < 14:
        raise MinecraftVersionError
    elif mc_version[1] < 15:
        return 4
    elif mc_version <= "1.16.1":
        return 5
    elif mc_version[1] < 17:
        return 6
    elif mc_version[1] == 17:
        return 7
    else:
        raise ValueError(f"unknow Minecraft datapack version {version}")

_version_func: dict = {}

def version_check(
    version: Version,
    *args: str,
    eq: List[T_version] = [],
    ne: List[T_version] = [],
    gt: Optional[T_version] = None,
    ge: Optional[T_version] = None,
    lt: Optional[T_version] = None,
    le: Optional[T_version] = None
) -> Callable[[Callable], Callable]:
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

class McdpVersionError(McdpError):

    def __init__(self, msg: str) -> None:
        super().__init__(msg.format(mcdp_version=__version__))

class MinecraftVersionError(McdpVersionError):
    pass
