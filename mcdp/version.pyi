from typing import Any, Dict, Final, List, OrderedDict, Tuple, Callable, Union, Optional, overload


T_version = Union[Tuple[Union[str, int], ...], Dict[str, Union[str, int]], str, "Version"]

from .exception import McdpError

class Version:
    """
    Support boolean operations between version numbers like '1.0.2'.
    """

    major: Final[int]
    minor: Final[int]
    patch: Final[int]
    prerelease: Final[Optional[str]]
    build: Final[Optional[str]]

    def __init__(self, version: T_version) -> None:...
    @overload
    def __getitem__(self, key: int) -> int:...
    @overload
    def __getitem__(self, key: slice) -> Tuple[int, ...]:...
    def __getitem__(self, key: Union[int, slice]) -> Union[int, Tuple[int, ...]]:...
    def __iter__(self) -> Tuple[int, int, int, Optional[str], Optional[str]]:...
    @classmethod
    def __get_validators__(cls):...
    @classmethod
    def validate(cls, val: T_version):...
    def __eq__(self, other: T_version) -> bool:...
    def __ne__(self, other: T_version) -> bool:...
    def __gt__(self, other: T_version) -> bool:...
    def __ge__(self, other: T_version) -> bool:...
    def __lt__(self, other: T_version) -> bool:...
    def __le__(self, other: T_version) -> bool:...
    def __len__(self) -> int:...
    def to_tuple(self) -> Tuple[int, int, int, Optional[str], Optional[str]]:...
    def to_dict(self) -> OrderedDict[str, Union[int, str]]:...
    def check(self,
        *args: str,
        eq: Union[List[T_version], T_version] = [],
        ne: Union[List[T_version], T_version] = [],
        gt: Optional[T_version] = None,
        ge: Optional[T_version] = None,
        lt: Optional[T_version] = None,
        le: Optional[T_version] = None
    ) -> Callable[[Callable], Callable]:...
    def __repr__(self) -> str:...
    def __str__(self) -> str:...


__version__: Version

def fail_version_check(func: Callable, *, collection: Dict[str, Callable] = ...) -> Callable:...
def pass_version_check(func: Callable, *, collection: Dict[str, Callable] = ...) -> Callable:...
def analyse_check_sentences(
        *args: str,
        eq: Union[List[T_version], T_version] = [],
        ne: Union[List[T_version], T_version] = [],
        gt: Optional[T_version] = None,
        ge: Optional[T_version] = None,
        lt: Optional[T_version] = None,
        le: Optional[T_version] = None
) -> Dict[str, Union[List[T_version], T_version, None]]:...
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

class VersionChecker:
    """
    The helper of version checker.
    
    Sometimes the version cannot be fetched when inited, so class VersionChecker is created.
    The final function will be insure when the function is first called.
    
    In the same time, the class supports the multiple version check.
    """

    def __init__(self, version_factory: Callable[[], Version]) -> None:...
    def register(self, func: Callable, *args: str, **kwds) -> None:...
    
    @property
    def decorator(self) -> Callable[..., Callable[[Callable], Callable]]:...
    def apply_check(self) -> None:...
    def __call__(self, *args: Any, **kwds: Any) -> Any:...


class McdpVersionError(McdpError):
    version: Any
    def __init__(self, *msg, version: Optional[Version] = None) -> None:...